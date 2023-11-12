from make_clone import make_clone

vcgov_router = make_clone(
    cloned_url="https://maps1.vcgov.org/arcgis/rest/services",
    prefix="/vcgov",
    tags=["vcgov"],
)
