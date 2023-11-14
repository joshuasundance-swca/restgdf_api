import asyncio
from typing import Optional

from aiohttp import ClientSession
from fastapi import Depends, APIRouter

from models import (
    LayersResponse,
    MultiLayersRequest,
    MultiLayersResponse,
)
from utils import (
    get_session,
    layers_from_directory,
    feature_layers_from_directory,
    rasters_from_directory,
)

directory_router = APIRouter(prefix="/directory", tags=["directory"])


@directory_router.get("/", response_model=LayersResponse)
async def directory(
    url: str,
    token: Optional[str] = None,
    session: ClientSession = Depends(get_session),
):
    """Discover content in an ArcGIS Services Directory."""
    return await layers_from_directory(url, session, token)


@directory_router.get("/featurelayers/", response_model=LayersResponse)
async def featurelayers(
    url: str,
    token: Optional[str] = None,
    session: ClientSession = Depends(get_session),
):
    """Discover feature layers in an ArcGIS Services Directory."""
    return await feature_layers_from_directory(url, session, token)


@directory_router.get("/rasters/", response_model=LayersResponse)
async def rasters(
    url: str,
    token: Optional[str] = None,
    session: ClientSession = Depends(get_session),
):
    """Discover rasters in an ArcGIS Services Directory."""
    return await rasters_from_directory(url, session, token)


@directory_router.post("/multiple/", response_model=MultiLayersResponse)
async def discoveries(
    request: MultiLayersRequest,
    session: ClientSession = Depends(get_session),
):
    """Discover content in multiple ArcGIS Services Directories."""
    tasks = [layers_from_directory(url, session) for url in request.urls]
    results = await asyncio.gather(*tasks)
    return MultiLayersResponse(layers=dict(zip(request.urls, results)))
