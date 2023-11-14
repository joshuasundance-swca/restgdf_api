import time

import numpy as np
import pandas as pd
from fastapi import Depends, APIRouter
from pydantic import BaseModel, Field

url = "https://mappingsupport.com/p/surf_gis/list-federal-state-county-city-GIS-servers.csv"
names = [
    "Line-number",
    "Type",
    "State",
    "County",
    "Town",
    "FIPS",
    "Server-owner",
    "ArcGIS-url",
    "https",
    "Show-contents",
    "SSL",
    "Open",
    "Comment",
    "Unnamed: 13",
    "Unnamed: 14",
]

data_cache = {
    "last_download_time": 0.0,
    "data": pd.DataFrame(),
}


def get_df() -> pd.DataFrame:
    return pd.read_csv(
        url,
        encoding="cp1252",
        skip_blank_lines=True,
        names=names,
    ).replace([np.inf, -np.inf, np.nan], None)


def get_df_depends() -> pd.DataFrame:
    global data_cache

    # Get the current time
    current_time = time.time()

    # Check if it's been more than a week (604800 seconds)
    if (
        current_time - data_cache["last_download_time"] > 604800
        or len(data_cache["data"]) == 0
    ):
        # Download the data and update the time
        data_cache["data"] = get_df()
        data_cache["last_download_time"] = current_time

    return data_cache["data"]


mappingsupport_router = APIRouter(
    prefix="/mappingsupport",
    tags=["mappingsupport"],
    on_startup=[get_df_depends],
)


class StateRequest(BaseModel):
    state_name: str = Field(
        ...,
        example="Florida",
        description="Full name of the state",
    )


class CountyRequest(StateRequest):
    county_name: str = Field(
        ...,
        example="Volusia",
        description="Full name of the county",
    )


class CityRequest(StateRequest):
    city_name: str = Field(
        ...,
        example="Daytona Beach",
        description="Full name of the city",
    )


class TownRequest(StateRequest):
    town_name: str = Field(
        ...,
        example="Daytona Beach Shores",
        description="Full name of the town",
    )


@mappingsupport_router.post(
    "/",
    description="This endpoint uses data from https://mappingsupport.com/p/surf_gis/list-federal-state-county-city-GIS-servers.csv",
)
async def mappingsupport(df: pd.DataFrame = Depends(get_df_depends)):
    """Return all data as json."""
    return df.to_dict(orient="records")


@mappingsupport_router.post(
    "/state/{state_name}",
    description="This endpoint uses data from https://mappingsupport.com/p/surf_gis/list-federal-state-county-city-GIS-servers.csv",
)
async def state(
    request: StateRequest,
    df: pd.DataFrame = Depends(get_df_depends),
):
    """Return data for a state as json."""
    return df.loc[df["State"] == request.state_name].to_dict(orient="records")


@mappingsupport_router.post(
    "/state/{state_name}/county/{county_name}",
    description="This endpoint uses data from https://mappingsupport.com/p/surf_gis/list-federal-state-county-city-GIS-servers.csv",
)
async def county(
    request: CountyRequest,
    df: pd.DataFrame = Depends(get_df_depends),
):
    """Return data for a county as json."""
    m1 = df["State"] == request.state_name
    m2 = df["County"] == request.county_name
    return df.loc[m1 & m2].to_dict(orient="records")


@mappingsupport_router.post(
    "/state/{state_name}/city/{city_name}",
    description="This endpoint uses data from https://mappingsupport.com/p/surf_gis/list-federal-state-county-city-GIS-servers.csv",
)
async def city(
    request: CityRequest,
    df: pd.DataFrame = Depends(get_df_depends),
):
    """Return data for a city as json."""
    m1 = df["State"] == request.state_name
    m2 = df["City"] == request.city_name
    return df.loc[m1 & m2].to_dict(orient="records")


@mappingsupport_router.post(
    "/state/{state_name}/town/{town_name}",
    description="This endpoint uses data from https://mappingsupport.com/p/surf_gis/list-federal-state-county-city-GIS-servers.csv",
)
async def town(
    request: TownRequest,
    df: pd.DataFrame = Depends(get_df_depends),
):
    """Return data for a town as json."""
    m1 = df["State"] == request.state_name
    m2 = df["Town"] == request.town_name
    return df.loc[m1 & m2].to_dict(orient="records")
