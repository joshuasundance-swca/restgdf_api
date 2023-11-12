from typing import Optional

import aiohttp
from aiohttp import ClientSession
from fastapi import APIRouter, Depends, HTTPException
from restgdf import Directory, FeatureLayer

from models import GeoDataFrameResponse, LayersResponse
from utils import get_session, rasters_from_response, feature_layers_from_response
from utils import relative_path


async def make_clone(
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

    @router.get("/featurelayers/", response_model=LayersResponse)
    async def featurelayers(
        token: Optional[str] = None,
        session: ClientSession = Depends(get_session),
    ):
        """Discover feature layers in an ArcGIS Services Directory."""
        try:
            rest_obj = await Directory.from_url(
                cloned_url,
                session=session,
                token=token,
            )
            resp = LayersResponse(layers=rest_obj.data)
            if resp.error or not isinstance(resp.layers, dict):
                raise Exception(resp.error)
            return LayersResponse(layers=feature_layers_from_response(resp.layers))
        except Exception as e:
            return LayersResponse(error=str(e))

    @router.get("/rasters/", response_model=LayersResponse)
    async def rasters(
        token: Optional[str] = None,
        session: ClientSession = Depends(get_session),
    ):
        """Discover rasters in an ArcGIS Services Directory."""
        try:
            rest_obj = await Directory.from_url(
                cloned_url,
                session=session,
                token=token,
            )
            resp = LayersResponse(layers=rest_obj.data)
            if resp.error or not isinstance(resp.layers, dict):
                raise Exception(resp.error)
            return LayersResponse(layers=rasters_from_response(resp.layers))
        except Exception as e:
            return LayersResponse(error=str(e))

    @router.get(
        "/{path:path}",
        response_model=GeoDataFrameResponse,
    )
    async def layer(
        path: str,
        token: Optional[str] = None,
        where: str = "1=1",
        session: ClientSession = Depends(get_session),
    ):
        """Retrieve FeatureLayer."""
        try:
            rest_obj = await FeatureLayer.from_url(
                f"{cloned_url.strip('/ ')}/{path.strip('/ ')}",
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

    def create_layer_endpoint(rel_path: str):
        """Create a closure that captures the relative path."""

        async def endpoint_function(
            token: Optional[str] = None,
            where: str = "1=1",
            session: ClientSession = Depends(get_session),
        ):
            """Endpoint function using captured relative path."""
            try:
                full_url = f"{cloned_url.strip('/ ')}/{rel_path.strip('/ ')}"
                rest_obj = await FeatureLayer.from_url(
                    full_url,
                    token=token or default_token,
                    where=where,
                    session=session,
                )
                metadata = rest_obj.jsondict
                gdf = await rest_obj.getgdf()
                return GeoDataFrameResponse(
                    metadata=metadata,
                    data=gdf.to_json(),
                )
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error retrieving GeoDataFrame: {str(e)}",
                )

        return endpoint_function

    async with aiohttp.ClientSession() as session:
        rest_obj = await Directory.from_url(
            cloned_url,
            session=session,
            token=default_token,
        )
        layers_data = feature_layers_from_response(rest_obj.data)
        for service_name, layers in layers_data.items():
            for _layer in layers:
                rel_path = relative_path(_layer["url"], root_url=cloned_url)
                layer_endpoint = create_layer_endpoint(rel_path)
                router.add_api_route(
                    path=rel_path,
                    endpoint=layer_endpoint,
                    response_model=GeoDataFrameResponse,
                    summary=f"Retrieve FeatureLayer for {service_name}/{_layer['name']}",
                )

    return router
