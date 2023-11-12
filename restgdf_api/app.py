from typing import Optional

from aiohttp import ClientSession
from fastapi import Depends, FastAPI

from directory import directory_router
from layer import layer_router
from mappingsupport import mappingsupport_router
from utils import get_session, make_clone

__version__ = "3.6.0"

app = FastAPI(
    title="restgdf_api",
    description="A REST API for interacting with ArcGIS FeatureLayers, powered by restgdf.",
    version=__version__,
)

app.include_router(mappingsupport_router)
app.include_router(directory_router)
app.include_router(layer_router)


@app.put("/server", tags=["server"], summary="Add server")
async def add_server(
    url: str,
    name: str,
    default_token: Optional[str] = None,
    session: ClientSession = Depends(get_session),
):
    try:
        router = await make_clone(
            session,
            url,
            default_token,
        )
        app.include_router(router)
        return {"result": "success"}
    except Exception as e:
        return {"result": "failure", "error": str(e)}
