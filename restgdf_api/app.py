from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from restgdf import Rest

__version__ = "1.0.2"

app = FastAPI(
    title="restgdf_api",
    description="A REST API for interacting with ArcGIS FeatureLayers, powered by restgdf.",
    version=__version__,
)


class GeoDataFrameResponse(BaseModel):
    data: str  # JSON representation of GeoDataFrame


class UniqueValuesResponse(BaseModel):
    values: list


class ValueCountsResponse(BaseModel):
    counts: dict


class NestedCountResponse(BaseModel):
    nested_counts: dict


@app.post("/getgdf/", response_model=GeoDataFrameResponse)
async def get_gdf(url: str, token: Optional[str] = None, where: str = "1=1"):
    """Retrieve a GeoDataFrame from an ArcGIS FeatureLayer."""
    try:
        rest_obj = await Rest.from_url(url, token=token, where=where)
        gdf = await rest_obj.getgdf()
        return GeoDataFrameResponse(data=gdf.to_json())  # Convert to JSON
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving GeoDataFrame: {str(e)}",
        )


@app.post("/gethead/", response_model=GeoDataFrameResponse)
async def get_head(
    url: str,
    n: int = 10,
    token: Optional[str] = None,
    where: str = "1=1",
):
    """Retrieve a GeoDataFrame from an ArcGIS FeatureLayer."""
    try:
        rest_obj = await Rest.from_url(url, token=token, where=where)
        gdf = await rest_obj.headgdf(n)
        return GeoDataFrameResponse(data=gdf.to_json())  # Convert to JSON
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving GeoDataFrame: {str(e)}",
        )


@app.post("/getsample/", response_model=GeoDataFrameResponse)
async def get_sample(
    url: str,
    n: int = 10,
    token: Optional[str] = None,
    where: str = "1=1",
):
    """Retrieve a GeoDataFrame from an ArcGIS FeatureLayer."""
    try:
        rest_obj = await Rest.from_url(url, token=token, where=where)
        gdf = await rest_obj.samplegdf(n)
        return GeoDataFrameResponse(data=gdf.to_json())  # Convert to JSON
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving GeoDataFrame: {str(e)}",
        )


@app.post("/getuniquevalues/", response_model=UniqueValuesResponse)
async def get_unique_values(url: str, field: str, token: Optional[str] = None):
    """Get the unique values for a field in an ArcGIS FeatureLayer."""
    try:
        rest_obj = await Rest.from_url(url, token=token)
        unique_values = await rest_obj.getuniquevalues(field)
        return UniqueValuesResponse(values=unique_values)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving unique values: {str(e)}",
        )


# @app.post("/getvaluecounts/", response_model=ValueCountsResponse)
# async def get_value_counts(url: str, field: str, token: Optional[str] = None):
#     """
#     Get the value counts for a specific field in an ArcGIS FeatureLayer.
#
#     Args:
#     - url (str): URL of the ArcGIS FeatureLayer.
#     - field (str): Field name to get value counts from.
#     - token (str, optional): Authentication token, if required.
#
#     Returns:
#     - ValueCountsResponse: Dictionary of value counts.
#     """
#     try:
#         rest_obj = await Rest.from_url(url, token=token)
#         value_counts = await rest_obj.getvaluecounts(field)
#         return ValueCountsResponse(counts=value_counts)
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error retrieving value counts: {str(e)}",
#         )
#
#
# @app.post("/getnestedcount/", response_model=NestedCountResponse)
# async def get_nested_count(url: str, fields: list[str], token: Optional[str] = None):
#     """
#     Get nested value counts for a combination of fields in an ArcGIS FeatureLayer.
#
#     Args:
#     - url (str): URL of the ArcGIS FeatureLayer.
#     - fields (list[str]): List of fields to get nested counts.
#     - token (str, optional): Authentication token, if required.
#
#     Returns:
#     - NestedCountResponse: Dictionary of nested value counts.
#     """
#     try:
#         rest_obj = await Rest.from_url(url, token=token)
#         nested_counts = await rest_obj.getnestedcount(tuple(fields))
#         return NestedCountResponse(nested_counts=nested_counts)
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error retrieving nested counts: {str(e)}",
#         )
#
#
# @app.post("/customquery/", response_model=GeoDataFrameResponse)
# async def custom_query(
#     url: str,
#     where: str,
#     token: Optional[str] = None,
#     additional_params: dict[str, str] = Body(...),
# ):
#     """
#     Perform a custom query on an ArcGIS FeatureLayer with additional parameters.
#
#     Args:
#     - url (str): URL of the ArcGIS FeatureLayer.
#     - where (str): WHERE clause for filtering data.
#     - token (str, optional): Authentication token, if required.
#     - additional_params (dict, optional): Additional query parameters.
#
#     Returns:
#     - GeoDataFrameResponse: JSON representation of the GeoDataFrame.
#     """
#     try:
#         rest_obj = await Rest.from_url(
#             url,
#             token=token,
#             where=where,
#             **additional_params,
#         )
#         gdf = await rest_obj.getgdf()
#         return GeoDataFrameResponse(data=gdf.to_json())
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error performing custom query: {str(e)}",
#         )
