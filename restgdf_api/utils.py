"""Utility functions for restgdf_api."""

from typing import Optional

from aiohttp import ClientSession
from fastapi import APIRouter, Depends
from restgdf import Directory, FeatureLayer

from models import GeoDataFrameResponse, LayersResponse


async def get_session():
    """Return an aiohttp ClientSession."""
    async with ClientSession() as session:
        yield session


us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}

state_dict = {
    k.replace(" ", "").replace(".", "").upper(): v
    for k, v in us_state_to_abbrev.items()
}

abbrev_dict = {v: k for k, v in state_dict.items()}


def state_to_abbrev(state: str) -> str:
    """Convert a state name to its abbreviation."""
    return state_dict.get(state.replace(" ", "").replace(".", "").upper(), "NA")


def abbrev_to_state(abbrev: str) -> str:
    """Convert a state abbreviation to its name."""
    return us_state_to_abbrev.get(
        abbrev.replace(".", "").replace(" ", "").upper(),
        "NA",
    )


async def get_directory(
    url: str,
    session: ClientSession,
    token: Optional[str] = None,
) -> Directory:
    rest_obj = await Directory.from_url(
        url,
        session=session,
        token=token,
    )
    _ = await rest_obj.crawl()
    return rest_obj


async def layers_from_directory(
    url: str,
    session: ClientSession,
    token: Optional[str] = None,
):
    """Discover content in an ArcGIS Services Directory."""
    try:
        rest_obj = await get_directory(url, session, token)
        return dict(layers=rest_obj.services)
    except Exception as e:
        return dict(error=str(e))


async def feature_layers_from_directory(
    url: str,
    session: ClientSession,
    token: Optional[str] = None,
) -> dict:
    """Discover content in an ArcGIS Services Directory."""
    try:
        rest_obj = await get_directory(url, session, token)
        return dict(layers=rest_obj.feature_layers())
    except Exception as e:
        return dict(error=str(e))


async def rasters_from_directory(
    url: str,
    session: ClientSession,
    token: Optional[str] = None,
):
    """Discover content in an ArcGIS Services Directory."""
    try:
        rest_obj = await get_directory(url, session, token)
        return dict(layers=rest_obj.rasters())
    except Exception as e:
        return dict(error=str(e))


def relative_path(remote_url: str, root_url: str) -> str:
    """Return a relative path from a remote url and a root url."""
    _path = remote_url.strip("/ ").replace(root_url.strip("/ "), "").strip("/ ")
    return f"/{_path}/"


async def fetch_gdf(
    url: str,
    session: ClientSession,
    token: Optional[str] = None,
    where: str = "1=1",
    **kwargs,
) -> GeoDataFrameResponse:
    try:
        rest_obj = await FeatureLayer.from_url(
            url,
            token=token,
            session=session,
            where=where,
            **kwargs,
        )
        gdf = await rest_obj.getgdf()
        return GeoDataFrameResponse(
            metadata=rest_obj.metadata,
            data=gdf.to_json(),  # Convert to JSON
        )
    except Exception as e:
        return GeoDataFrameResponse(error=str(e))


async def make_clone(
    session: ClientSession,
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
        return await layers_from_directory(cloned_url, session, token)

    @router.get("/featurelayers/", response_model=LayersResponse)
    async def featurelayers(
        token: Optional[str] = None,
        session: ClientSession = Depends(get_session),
    ):
        """Discover feature layers in an ArcGIS Services Directory."""
        return await feature_layers_from_directory(cloned_url, session, token)

    @router.get("/rasters/", response_model=LayersResponse)
    async def rasters(
        token: Optional[str] = None,
        session: ClientSession = Depends(get_session),
    ):
        """Discover rasters in an ArcGIS Services Directory."""
        return await rasters_from_directory(cloned_url, session, token)

    @router.get(
        "/{path:path}/",
        response_model=GeoDataFrameResponse,
    )
    async def layer(
        path: str,
        token: Optional[str] = None,
        where: str = "1=1",
        session: ClientSession = Depends(get_session),
    ):
        """Retrieve FeatureLayer."""
        return await fetch_gdf(
            f"{cloned_url.strip('/ ')}/{path.strip('/ ')}",
            session,
            token or default_token,
            where,
        )

    def create_layer_endpoint(rel_path: str):
        """Create a closure that captures the relative path."""

        async def endpoint_function(
            token: Optional[str] = None,
            where: str = "1=1",
            session: ClientSession = Depends(get_session),
        ):
            """Endpoint function using captured relative path."""
            full_url = f"{cloned_url.strip('/ ')}/{rel_path.strip('/ ')}"
            return await fetch_gdf(
                full_url,
                session,
                token or default_token,
                where,
            )

        return endpoint_function

    feature_layers = await feature_layers_from_directory(
        cloned_url,
        session,
        default_token,
    )
    if "error" in feature_layers:
        raise ValueError(feature_layers["error"])
    for _layer in feature_layers["layers"]:
        layer_name = _layer["metadata"]["name"]
        rel_path = relative_path(_layer["url"], root_url=cloned_url)
        layer_endpoint = create_layer_endpoint(rel_path)
        router.add_api_route(
            path=rel_path,
            endpoint=layer_endpoint,
            response_model=GeoDataFrameResponse,
            summary=layer_name,
        )

    return router
