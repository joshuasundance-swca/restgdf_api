from fastapi import FastAPI

from discovery import discovery_router
from retrieval import retrieval_router

__version__ = "3.2.1"

app = FastAPI(
    title="restgdf_api",
    description="A REST API for interacting with ArcGIS FeatureLayers, powered by restgdf.",
    version=__version__,
)

app.include_router(discovery_router)
app.include_router(retrieval_router)
