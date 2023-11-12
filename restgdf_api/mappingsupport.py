import time

import numpy as np
import pandas as pd
from fastapi import Depends, APIRouter

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


def get_df():
    global data_cache

    # Get the current time
    current_time = time.time()

    # Check if it's been more than a week (604800 seconds)
    if (
        current_time - data_cache["last_download_time"] > 604800
        or len(data_cache["data"]) == 0
    ):
        # Download the data and update the time
        df = pd.read_csv(
            url,
            encoding="cp1252",
            skip_blank_lines=True,
            names=names,
        ).replace([np.inf, -np.inf, np.nan], None)

        data_cache["data"] = df
        data_cache["last_download_time"] = current_time

    return data_cache["data"]


mappingsupport_router = APIRouter(
    prefix="/mappingsupport",
    tags=["mappingsupport"],
    on_startup=[get_df],
)


@mappingsupport_router.get("/")
async def mappingsupport(df: pd.DataFrame = Depends(get_df)):
    """Return all data as json."""
    return df.to_dict(orient="records")


@mappingsupport_router.get("/state/{state_name}")
async def state(
    state_name: str,
    df: pd.DataFrame = Depends(get_df),
):
    """Return data for a state as json."""
    return df.loc[df["State"] == state_name].to_dict(orient="records")


@mappingsupport_router.get("/state/{state_name}/county/{county_name}")
async def county(
    state_name: str,
    county_name: str,
    df: pd.DataFrame = Depends(get_df),
):
    """Return data for a county as json."""
    m1 = df["State"] == state_name
    m2 = df["County"] == county_name
    return df.loc[m1 & m2].to_dict(orient="records")


@mappingsupport_router.get("/state/{state_name}/city/{city_name}")
async def city(
    state_name: str,
    city_name: str,
    df: pd.DataFrame = Depends(get_df),
):
    """Return data for a city as json."""
    m1 = df["State"] == state_name
    m2 = df["City"] == city_name
    return df.loc[m1 & m2].to_dict(orient="records")


@mappingsupport_router.get("/state/{state_name}/town/{town_name}")
async def town(
    state_name: str,
    town_name: str,
    df: pd.DataFrame = Depends(get_df),
):
    """Return data for a town as json."""
    m1 = df["State"] == state_name
    m2 = df["Town"] == town_name
    return df.loc[m1 & m2].to_dict(orient="records")


@mappingsupport_router.get("/fips/{fips_code}")
async def fips(
    fips_code: str,
    df: pd.DataFrame = Depends(get_df),
):
    """Return data for a FIPS code as json."""
    return df.loc[df["FIPS"].astype(str) == fips_code].to_dict(orient="records")
