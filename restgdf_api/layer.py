import asyncio
import os
from typing import Optional

from aiohttp import ClientSession
from fastapi import Depends, HTTPException, APIRouter
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from restgdf import FeatureLayer

from utils import get_session
from models import (
    GeoDataFrameResponse,
    MultiGeoDataFrameRequest,
    MultiGeoDataFrameResponse,
    SummarizedGeoDataFrameResponse,
    UniqueValuesResponse,
)

layer_router = APIRouter(prefix="/layer", tags=["layer"])


@layer_router.post("/", response_model=GeoDataFrameResponse)
async def layer(
    url: str,
    token: Optional[str] = None,
    where: str = "1=1",
    session: ClientSession = Depends(get_session),
):
    """Retrieve FeatureLayer."""
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


@layer_router.post("/multiple/", response_model=MultiGeoDataFrameResponse)
async def layers(
    request: MultiGeoDataFrameRequest,
    session: ClientSession = Depends(get_session),
):
    """Retrieve multiple FeatureLayers."""

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


@layer_router.post("/summarized/", response_model=SummarizedGeoDataFrameResponse)
async def summarized_layer(
    url: str,
    token: Optional[str] = None,
    where: str = "1=1",
    openai_api_key: Optional[str] = None,
    session: ClientSession = Depends(get_session),
):
    """Retrieve and summarize FeatureLayer."""
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


@layer_router.post("/head/", response_model=GeoDataFrameResponse)
async def layer_head(
    url: str,
    n: int = 10,
    token: Optional[str] = None,
    where: str = "1=1",
    session: ClientSession = Depends(get_session),
):
    """Retrieve the first n features from a FeatureLayer."""
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


@layer_router.post("/sample/", response_model=GeoDataFrameResponse)
async def layer_sample(
    url: str,
    n: int = 10,
    token: Optional[str] = None,
    where: str = "1=1",
    session: ClientSession = Depends(get_session),
):
    """Retrieve n random features from a FeatureLayer."""
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


@layer_router.post("/unique/", response_model=UniqueValuesResponse)
async def unique_values(
    url: str,
    field: str,
    token: Optional[str] = None,
    session: ClientSession = Depends(get_session),
):
    """Get the unique values for a field in a FeatureLayer."""
    try:
        rest_obj = await FeatureLayer.from_url(url, token=token, session=session)
        unique_values = await rest_obj.getuniquevalues(field)
        return UniqueValuesResponse(values=unique_values)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving unique values: {str(e)}",
        )
