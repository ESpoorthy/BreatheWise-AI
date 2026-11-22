from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api", tags=["air quality"])

AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
POLLUTANT_KEYS = (
    "pm2_5",
    "pm10",
    "nitrogen_dioxide",
    "sulphur_dioxide",
    "ozone",
    "carbon_monoxide",
)


def classify_us_aqi(value: float) -> str:
    if value <= 50:
        return "Good"
    if value <= 100:
        return "Moderate"
    if value <= 150:
        return "Unhealthy for sensitive groups"
    if value <= 200:
        return "Unhealthy"
    if value <= 300:
        return "Very unhealthy"
    return "Hazardous"


async def get_provider_json(url: str, params: dict[str, Any]) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except (httpx.RequestError, httpx.HTTPStatusError) as exc:
        raise HTTPException(
            status_code=502,
            detail="The air-quality data provider is temporarily unavailable. Please try again.",
        ) from exc


@router.get("/locations/search")
async def search_locations(
    name: str = Query(min_length=2, max_length=80),
) -> dict[str, list[dict[str, Any]]]:
    """Search city/town names without requesting a precise device location."""
    payload = await get_provider_json(
        GEOCODING_URL,
        {"name": name, "count": 6, "language": "en", "format": "json"},
    )
    results = payload.get("results") or []
    return {
        "results": [
            {
                "name": item.get("name"),
                "admin1": item.get("admin1"),
                "country": item.get("country"),
                "country_code": item.get("country_code"),
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "timezone": item.get("timezone"),
            }
            for item in results
        ]
    }


@router.get("/air-quality")
async def get_air_quality(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
) -> dict[str, Any]:
    """Return modeled current conditions, explicitly labeled as US AQI."""
    payload = await get_provider_json(
        AIR_QUALITY_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join(("us_aqi", *POLLUTANT_KEYS)),
            "timezone": "auto",
        },
    )
    current = payload.get("current") or {}
    units = payload.get("current_units") or {}
    raw_aqi = current.get("us_aqi")
    if raw_aqi is None:
        raise HTTPException(
            status_code=502,
            detail="The provider did not return a current AQI estimate for this location.",
        )

    aqi_value = round(float(raw_aqi))
    pollutants = [
        {
            "key": key,
            "label": {
                "pm2_5": "PM2.5",
                "pm10": "PM10",
                "nitrogen_dioxide": "Nitrogen dioxide",
                "sulphur_dioxide": "Sulphur dioxide",
                "ozone": "Ozone",
                "carbon_monoxide": "Carbon monoxide",
            }[key],
            "value": current.get(key),
            "unit": units.get(key, "µg/m³"),
        }
        for key in POLLUTANT_KEYS
        if current.get(key) is not None
    ]

    return {
        "location": {
            "latitude": payload.get("latitude"),
            "longitude": payload.get("longitude"),
            "timezone": payload.get("timezone"),
        },
        "current": {
            "observed_at": current.get("time"),
            "aqi": aqi_value,
            "aqi_scale": "US EPA AQI",
            "category": classify_us_aqi(aqi_value),
            "pollutants": pollutants,
        },
        "source": {
            "name": "Open-Meteo Air Quality API",
            "url": "https://open-meteo.com/en/docs/air-quality-api",
            "model": "CAMS-based atmospheric composition model",
            "data_type": "Modeled current estimate; not a ground-monitor station measurement.",
        },
        "caveat": (
            "This is a US EPA AQI-scale model estimate, not India's CPCB National AQI "
            "or a personal exposure measurement. Use official local monitoring and "
            "public-health advisories for decisions during severe pollution."
        ),
    }
