import asyncio
import json
import os
from typing import Optional, Any

from aiohttp import ClientSession
from fastapi import FastAPI, HTTPException, Depends
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from pydantic import BaseModel
from restgdf import FeatureLayer, Directory

__version__ = "3.2.0"

app = FastAPI(
    title="restgdf_api",
    description="A REST API for interacting with ArcGIS FeatureLayers, powered by restgdf.",
    version=__version__,
)


class GeoDataFrameResponse(BaseModel):
    metadata: Optional[dict[str, Any]] = None
    data: Optional[str] = None  # JSON representation of GeoDataFrame
    error: Optional[str] = None


class MultiGeoDataFrameRequest(BaseModel):
    urls: list[str]
    token: Optional[str] = None


class MultiGeoDataFrameResponse(BaseModel):
    gdfs: Optional[dict[str, GeoDataFrameResponse]] = None
    error: Optional[str] = None


class SummarizedGeoDataFrameResponse(GeoDataFrameResponse):
    summarized_description: str
    summary: str


class LayersResponse(BaseModel):
    layers: Optional[dict[str, list[dict[str, Any]]]] = None
    error: Optional[str] = None


class MultiLayersRequest(BaseModel):
    urls: list[str]
    token: Optional[str] = None


class MultiLayersResponse(BaseModel):
    layers: dict[str, LayersResponse]


class SummarizedLayersResponse(LayersResponse):
    summary: str


class UniqueValuesResponse(BaseModel):
    values: list


async def get_session():
    async with ClientSession() as session:
        yield session


@app.post("/getlayers/", response_model=LayersResponse)
async def get_layers(
    url: str,
    token: Optional[str] = None,
    session: ClientSession = Depends(get_session),
):
    """Retrieve Layers from an ArcGIS Services Directory."""
    try:
        rest_obj = await Directory.from_url(
            url,
            session=session,
            token=token,
        )
        return LayersResponse(layers=rest_obj.data)
    except Exception as e:
        return LayersResponse(error=str(e))


@app.post("/getlayers/multiple/", response_model=MultiLayersResponse)
async def get_multiple_layers(
    request: MultiLayersRequest,
    session: ClientSession = Depends(get_session),
):
    """Retrieve Layers from multiple ArcGIS Services Directories."""

    async def get_layers_from_url(url: str):
        try:
            rest_obj = await Directory.from_url(
                url,
                session=session,
                token=request.token,
            )
            return LayersResponse(layers=rest_obj.data)
        except Exception as e:
            return LayersResponse(error=str(e))

    tasks = [get_layers_from_url(url) for url in request.urls]
    results = await asyncio.gather(*tasks)
    return MultiLayersResponse(layers=dict(zip(request.urls, results)))


summarize_server_prompt = ChatPromptTemplate.from_messages(
    (
        "user",
        """
This data was returned by a geospatial API. Characterize the server by summarizing the data:
API Data:
{data}
""".strip(),
    ),
)


@app.post("/getlayers/summarize/", response_model=SummarizedLayersResponse)
async def get_summarized_layers(
    url: str,
    token: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    session: ClientSession = Depends(get_session),
):
    """Retrieve Layers from an ArcGIS Services Directory, with summary."""
    openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY", None)
    if openai_api_key is None:
        raise HTTPException(
            status_code=501,
            detail="Summarization is not enabled.",
        )
    desc_chain = (
        RunnablePassthrough()
        | summarize_server_prompt
        | ChatOpenAI(openai_api_key=openai_api_key, model_name="gpt-4-1106-preview")
        | (lambda output: output.content.strip())
    )
    try:
        rest_obj = await Directory.from_url(
            url,
            session=session,
            token=token,
        )
        summarized_desc = await desc_chain.ainvoke(
            {"data": json.dumps(rest_obj.data)},
        )
        return SummarizedLayersResponse(
            layers=rest_obj.data,
            summary=summarized_desc,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving Layers: {str(e)}",
        )


@app.post("/getgdf/", response_model=GeoDataFrameResponse)
async def get_gdf(
    url: str,
    token: Optional[str] = None,
    where: str = "1=1",
    session: ClientSession = Depends(get_session),
):
    """Retrieve a GeoDataFrame from an ArcGIS FeatureLayer."""
    try:
        rest_obj = await FeatureLayer.from_url(
            url,
            token=token,
            where=where,
            session=session,
        )
        metadata = rest_obj.jsondict
        gdf = await rest_obj.getgdf()
        return GeoDataFrameResponse(
            metadata=metadata,
            data=gdf.to_json(),
        )  # Convert to JSON
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving GeoDataFrame: {str(e)}",
        )


@app.post("/getgdf/multiple/", response_model=MultiGeoDataFrameResponse)
async def get_multiple_gdfs(
    request: MultiGeoDataFrameRequest,
    session: ClientSession = Depends(get_session),
):
    """Retrieve GeoDataFrames from multiple ArcGIS FeatureLayers."""

    async def fetch_gdf(url: str) -> GeoDataFrameResponse:
        try:
            rest_obj = await FeatureLayer.from_url(
                url,
                token=request.token,
                session=session,
            )
            gdf = await rest_obj.getgdf()
            return GeoDataFrameResponse(
                metadata=rest_obj.jsondict,
                data=gdf.to_json(),  # Convert to JSON
            )
        except Exception as e:
            return GeoDataFrameResponse(error=str(e))

    tasks = [fetch_gdf(url) for url in request.urls]
    results = await asyncio.gather(*tasks)
    return MultiGeoDataFrameResponse(gdfs=dict(zip(request.urls, results)))


summarize_record_prompt = ChatPromptTemplate.from_messages(
    (
        "user",
        """
This data was returned by a geospatial API. We've dropped the geometry column, but summarize the data:
API Name: {name}
API Description: {description}
API Data:
{data}
""".strip(),
    ),
)

summarize_desc_prompt = ChatPromptTemplate.from_messages(
    (
        "user",
        """
Summarize this description to no more than three sentences:
{description}
""".strip(),
    ),
)
summarize_summaries_prompt = ChatPromptTemplate.from_messages(
    (
        "user",
        """
Combine these individual summaries of features into a single summary of the dataset:
{summaries}
""".strip(),
    ),
)


@app.post("/getgdf/summarize/", response_model=SummarizedGeoDataFrameResponse)
async def get_summarized_gdf(
    url: str,
    token: Optional[str] = None,
    where: str = "1=1",
    openai_api_key: Optional[str] = None,
    session: ClientSession = Depends(get_session),
):
    """Retrieve a GeoDataFrame from an ArcGIS FeatureLayer, with summary."""
    openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY", None)
    if openai_api_key is None:
        raise HTTPException(
            status_code=501,
            detail="Summarization is not enabled.",
        )
    try:
        rest_obj = await FeatureLayer.from_url(
            url,
            token=token,
            where=where,
            session=session,
        )
        metadata = rest_obj.jsondict
        name = metadata["name"]
        desc = metadata.get("description", "")
        # summarize desc if it's likely to be more than 3 sentences, based on len()
        if len(desc) > 300:
            desc_chain = (
                RunnablePassthrough()
                | summarize_desc_prompt
                | ChatOpenAI(
                    openai_api_key=openai_api_key,
                    model_name="gpt-4-1106-preview",
                )
                | (lambda output: output.content.strip())
            )
            summarized_desc = await desc_chain.ainvoke(desc)
        else:
            summarized_desc = desc
        gdf = await rest_obj.getgdf()
        dropcols = ["OBJECTID", "geometry"]
        final_summary_input = gdf.drop(columns=dropcols).to_json()
        final_summary_chain = (
            summarize_record_prompt
            | ChatOpenAI(
                openai_api_key=openai_api_key,
                model_name="gpt-4-1106-preview",
            )
            | (lambda output: output.content.strip())
        )
        final_summary = await final_summary_chain.ainvoke(
            dict(name=name, description=summarized_desc, data=final_summary_input),
        )
        return SummarizedGeoDataFrameResponse(
            metadata=metadata,
            data=gdf.to_json(),
            summary=final_summary,
            summarized_description=summarized_desc,
        )  # Convert to JSON
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving GeoDataFrame: {str(e)}",
        )


@app.post("/gethead/", response_model=GeoDataFrameResponse)
async def get_head(
    url: str,
    n: int = 10,
    token: Optional[str] = None,
    where: str = "1=1",
    session: ClientSession = Depends(get_session),
):
    """Retrieve a GeoDataFrame from an ArcGIS FeatureLayer."""
    try:
        rest_obj = await FeatureLayer.from_url(
            url,
            token=token,
            where=where,
            session=session,
        )
        metadata = rest_obj.jsondict
        gdf = await rest_obj.headgdf(n)
        return GeoDataFrameResponse(
            metadata=metadata,
            data=gdf.to_json(),
        )  # Convert to JSON
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving GeoDataFrame: {str(e)}",
        )


@app.post("/getsample/", response_model=GeoDataFrameResponse)
async def get_sample(
    url: str,
    n: int = 10,
    token: Optional[str] = None,
    where: str = "1=1",
    session: ClientSession = Depends(get_session),
):
    """Retrieve a GeoDataFrame from an ArcGIS FeatureLayer."""
    try:
        rest_obj = await FeatureLayer.from_url(
            url,
            token=token,
            where=where,
            session=session,
        )
        metadata = rest_obj.jsondict
        gdf = await rest_obj.samplegdf(n)
        return GeoDataFrameResponse(
            metadata=metadata,
            data=gdf.to_json(),
        )  # Convert to JSON
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving GeoDataFrame: {str(e)}",
        )


@app.post("/getuniquevalues/", response_model=UniqueValuesResponse)
async def get_unique_values(
    url: str,
    field: str,
    token: Optional[str] = None,
    session: ClientSession = Depends(get_session),
):
    """Get the unique values for a field in an ArcGIS FeatureLayer."""
    try:
        rest_obj = await FeatureLayer.from_url(url, token=token, session=session)
        unique_values = await rest_obj.getuniquevalues(field)
        return UniqueValuesResponse(values=unique_values)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving unique values: {str(e)}",
        )
