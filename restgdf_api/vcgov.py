import asyncio

from make_clone import make_clone

vcgov_router = asyncio.run(
    make_clone(
        cloned_url="https://maps1.vcgov.org/arcgis/rest/services",
        prefix="/vcgov",
        tags=["vcgov"],
    ),
)
