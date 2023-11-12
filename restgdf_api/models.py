from typing import Optional, Any

from pydantic import BaseModel, Field


class GeoDataFrameResponse(BaseModel):
    metadata: Optional[dict[str, Any]] = Field(None, description="Layer metadata")
    data: Optional[str] = Field(None, description="gpd.GeoDataFrame.to_json")
    error: Optional[str] = Field(None, description="Error message")


class MultiGeoDataFrameRequest(BaseModel):
    urls: list[str] = Field(
        ...,
        example=["https://maps1.vcgov.org/arcgis/rest/services/VC_Public/MapServer/0"],
    )
    token: Optional[str] = Field(
        None,
        description="Token to send to the server with requests.",
    )


class MultiGeoDataFrameResponse(BaseModel):
    gdfs: Optional[dict[str, GeoDataFrameResponse]] = Field(
        None,
        description="List of GeoDataFrameResponses",
    )
    error: Optional[str] = Field(None, description="Error message")


class LayersResponse(BaseModel):
    layers: Optional[dict[str, list[dict[str, Any]]]] = Field(
        None,
        description="Layer JSON",
    )
    error: Optional[str] = Field(None, description="Error message")


class MultiLayersRequest(BaseModel):
    urls: list[str] = Field(
        ...,
        example=[
            "https://maps1.vcgov.org/arcgis/rest/services",
            "https://ocgis4.ocfl.net/arcgis/rest/services",
        ],
    )
    token: Optional[str] = Field(
        None,
        description="Token to send to the server with requests.",
    )


class MultiLayersResponse(BaseModel):
    layers: dict[str, LayersResponse] = Field(
        ...,
        description="List of LayersResponses",
    )


class UniqueValuesResponse(BaseModel):
    values: list = Field(..., description="List of unique values")
