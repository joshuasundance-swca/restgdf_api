from typing import Optional

from aiohttp import ClientSession
from fastapi import APIRouter, Depends, HTTPException
from restgdf import Directory, FeatureLayer

from models import GeoDataFrameResponse, LayersResponse
from utils import get_session


def make_clone(
    cloned_url: str,
    default_token: Optional[str] = None,
    prefix: str = "/clone",
    tags: list[str] = ["clone"],
    **kwargs,
) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=tags, **kwargs)

    @router.get("/", response_model=LayersResponse)
    async def directory(
        token: Optional[str] = None,
        session: ClientSession = Depends(get_session),
    ):
        """Discover content in an ArcGIS Services Directory."""
        try:
            rest_obj = await Directory.from_url(
                cloned_url,
                session=session,
                token=token or default_token,
            )
            return LayersResponse(layers=rest_obj.data)
        except Exception as e:
            return LayersResponse(error=str(e))

    @router.get(
        "/{path:path}/MapServer/{layer_id}",
        response_model=GeoDataFrameResponse,
    )
    async def layer(
        path: str,
        layer_id: int,
        token: Optional[str] = None,
        where: str = "1=1",
        session: ClientSession = Depends(get_session),
    ):
        """Retrieve FeatureLayer."""
        _ = layer_id
        try:
            rest_obj = await FeatureLayer.from_url(
                f"{cloned_url}/{path}/MapServer/{layer_id}",
                token=token or default_token,
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

    return router
