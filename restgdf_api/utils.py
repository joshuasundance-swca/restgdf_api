"""Utility functions for restgdf_api."""
from aiohttp import ClientSession


async def get_session():
    """Return an aiohttp ClientSession."""
    async with ClientSession() as session:
        yield session


us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}

state_dict = {
    k.replace(" ", "").replace(".", "").upper(): v
    for k, v in us_state_to_abbrev.items()
}


def state_to_abbrev(state: str) -> str:
    """Convert a state name to its abbreviation."""
    return state_dict.get(state.replace(" ", "").replace(".", "").upper(), "NA")


def abbrev_to_state(abbrev: str) -> str:
    """Convert a state abbreviation to its name."""
    return us_state_to_abbrev.get(
        abbrev.replace(".", "").replace(" ", "").upper(),
        "NA",
    )


def filter_layers_by_type(
    layers_json: dict,
    typestr: str,
    keys: list[str] = ["name", "geometryType", "url"],
) -> dict:
    """Return a dict of layers filtered by type."""
    return {
        key: [
            {k: item[k] for k in keys if k in item}
            for item in value
            if isinstance(item, dict) and item.get("type") == typestr
        ]
        for key, value in layers_json.items()
        if isinstance(value, list)
        and any(
            isinstance(item, dict) and item.get("type") == typestr for item in value
        )
    }


def feature_layers_from_response(layers_json: dict) -> dict:
    """Return a dict of feature layers from a layers response."""
    return filter_layers_by_type(layers_json, "Feature Layer")


def rasters_from_response(layers_json: dict) -> dict:
    """Return a dict of rasters from a layers response."""
    return filter_layers_by_type(layers_json, "Raster Layer")


def relative_path(remote_url: str, root_url: str) -> str:
    """Return a relative path from a remote url and a root url."""
    _path = remote_url.strip("/ ").replace(root_url.strip("/ "), "").strip("/ ")
    return f"/{_path}/"
