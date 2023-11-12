import asyncio
import json
import os
from typing import Optional

from aiohttp import ClientSession
from fastapi import Depends, HTTPException, APIRouter
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from restgdf import Directory

from utils import get_session, feature_layers_from_response, rasters_from_response
from models import (
    LayersResponse,
    MultiLayersRequest,
    MultiLayersResponse,
    SummarizedLayersResponse,
)

directory_router = APIRouter(prefix="/directory", tags=["directory"])


@directory_router.get("/", response_model=LayersResponse)
async def directory(
    url: str,
    token: Optional[str] = None,
    session: ClientSession = Depends(get_session),
):
    """Discover content in an ArcGIS Services Directory."""
    try:
        rest_obj = await Directory.from_url(
            url,
            session=session,
            token=token,
        )
        return LayersResponse(layers=rest_obj.data)
    except Exception as e:
        return LayersResponse(error=str(e))


@directory_router.get("/featurelayers/", response_model=LayersResponse)
async def featurelayers(
    url: str,
    token: Optional[str] = None,
    session: ClientSession = Depends(get_session),
):
    """Discover feature layers in an ArcGIS Services Directory."""
    try:
        rest_obj = await Directory.from_url(
            url,
            session=session,
            token=token,
        )
        resp = LayersResponse(layers=rest_obj.data)
        if resp.error or not isinstance(resp.layers, dict):
            raise Exception(resp.error)
        return LayersResponse(layers=feature_layers_from_response(resp.layers))
    except Exception as e:
        return LayersResponse(error=str(e))


@directory_router.get("/rasters/", response_model=LayersResponse)
async def rasters(
    url: str,
    token: Optional[str] = None,
    session: ClientSession = Depends(get_session),
):
    """Discover rasters in an ArcGIS Services Directory."""
    try:
        rest_obj = await Directory.from_url(
            url,
            session=session,
            token=token,
        )
        resp = LayersResponse(layers=rest_obj.data)
        if resp.error or not isinstance(resp.layers, dict):
            raise Exception(resp.error)
        return LayersResponse(layers=rasters_from_response(resp.layers))
    except Exception as e:
        return LayersResponse(error=str(e))


@directory_router.get("/multiple/", response_model=MultiLayersResponse)
async def discoveries(
    request: MultiLayersRequest,
    session: ClientSession = Depends(get_session),
):
    """Discover content in multiple ArcGIS Services Directories."""

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


@directory_router.get("/summarized/", response_model=SummarizedLayersResponse)
async def summarized_directory(
    url: str,
    token: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    session: ClientSession = Depends(get_session),
):
    """Discover and summarize content in an ArcGIS Services Directory."""
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
