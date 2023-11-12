from fastapi import FastAPI

from directory import directory_router
from layer import layer_router

__version__ = "3.2.1"

app = FastAPI(
    title="restgdf_api",
    description="A REST API for interacting with ArcGIS FeatureLayers, powered by restgdf.",
    version=__version__,
)

app.include_router(directory_router)
app.include_router(layer_router)
