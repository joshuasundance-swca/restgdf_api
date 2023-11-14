import asyncio
from typing import Optional

from aiohttp import ClientSession
from fastapi import Depends, APIRouter
from models import (
    GeoDataFrameResponse,
    MultiGeoDataFrameRequest,
    MultiGeoDataFrameResponse,
)
from utils import fetch_gdf, get_session

layer_router = APIRouter(prefix="/layer", tags=["layer"])


@layer_router.get("/", response_model=GeoDataFrameResponse)
async def layer(
    url: str,
    token: Optional[str] = None,
    where: str = "1=1",
    session: ClientSession = Depends(get_session),
):
    """Retrieve FeatureLayer."""
    return await fetch_gdf(url, session, token, where)


@layer_router.post("/multiple/", response_model=MultiGeoDataFrameResponse)
async def layers(
    request: MultiGeoDataFrameRequest,
    session: ClientSession = Depends(get_session),
):
    """Retrieve multiple FeatureLayers."""
    tasks = [fetch_gdf(url, session) for url in request.urls]
    results = await asyncio.gather(*tasks)
    return MultiGeoDataFrameResponse(gdfs=dict(zip(request.urls, results)))
