from typing import Optional, Any

from pydantic import BaseModel


class GeoDataFrameResponse(BaseModel):
    metadata: Optional[dict[str, Any]] = None
    data: Optional[str] = None  # JSON representation of GeoDataFrame
    error: Optional[str] = None


class MultiGeoDataFrameRequest(BaseModel):
    urls: list[str]
    token: Optional[str] = None


class MultiGeoDataFrameResponse(BaseModel):
    gdfs: Optional[dict[str, GeoDataFrameResponse]] = None
    error: Optional[str] = None


class SummarizedGeoDataFrameResponse(GeoDataFrameResponse):
    summarized_description: str
    summary: str


class LayersResponse(BaseModel):
    layers: Optional[dict[str, list[dict[str, Any]]]] = None
    error: Optional[str] = None


class MultiLayersRequest(BaseModel):
    urls: list[str]
    token: Optional[str] = None


class MultiLayersResponse(BaseModel):
    layers: dict[str, LayersResponse]


class SummarizedLayersResponse(LayersResponse):
    summary: str


class UniqueValuesResponse(BaseModel):
    values: list
