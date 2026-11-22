import math
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api", tags=["air quality"])

AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
POLLUTANT_KEYS = ("pm2_5", "pm10", "nitrogen_dioxide", "sulphur_dioxide", "ozone", "carbon_monoxide")
POLLUTANT_LABELS = {
    "pm2_5": "PM2.5",
    "pm10": "PM10",
    "nitrogen_dioxide": "Nitrogen dioxide",
    "sulphur_dioxide": "Sulphur dioxide",
    "ozone": "Ozone",
    "carbon_monoxide": "Carbon monoxide",
}


def classify_us_aqi(value: float) -> str:
    if value <= 50: return "Good"
    if value <= 100: return "Moderate"
    if value <= 150: return "Unhealthy for sensitive groups"
    if value <= 200: return "Unhealthy"
    if value <= 300: return "Very unhealthy"
    return "Hazardous"


def _provider_error() -> HTTPException:
    return HTTPException(status_code=502, detail="The air-quality data provider returned an invalid or unavailable response. Please try again.")


async def get_provider_json(url: str, params: dict[str, Any]) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(12.0, connect=4.0)) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
        raise _provider_error() from exc
    if not isinstance(payload, dict):
        raise _provider_error()
    return payload


@router.get("/locations/search")
async def search_locations(name: str = Query(min_length=2, max_length=80)) -> dict[str, list[dict[str, Any]]]:
    """Search city/town names without requesting a precise device location."""
    payload = await get_provider_json(GEOCODING_URL, {"name": name, "count": 6, "language": "en", "format": "json"})
    raw_results = payload.get("results")
    if raw_results is None:
        raw_results = []
    if not isinstance(raw_results, list):
        raise _provider_error()
    results = []
    for item in raw_results[:6]:
        if not isinstance(item, dict):
            continue
        latitude, longitude = item.get("latitude"), item.get("longitude")
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            continue
        if not math.isfinite(latitude) or not math.isfinite(longitude) or not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            continue
        if not isinstance(item.get("name"), str) or not item["name"].strip():
            continue
        results.append({
            "name": item["name"], "admin1": item.get("admin1"), "country": item.get("country"),
            "country_code": item.get("country_code"), "latitude": latitude, "longitude": longitude,
            "timezone": item.get("timezone"),
        })
    return {"results": results}


@router.get("/air-quality")
async def get_air_quality(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
) -> dict[str, Any]:
    """Return modeled current conditions, explicitly labeled as US AQI."""
    payload = await get_provider_json(AIR_QUALITY_URL, {
        "latitude": latitude, "longitude": longitude,
        "current": ",".join(("us_aqi", *POLLUTANT_KEYS)), "timezone": "auto",
    })
    current = payload.get("current")
    units = payload.get("current_units") or {}
    if not isinstance(current, dict) or not isinstance(units, dict):
        raise _provider_error()
    raw_aqi = current.get("us_aqi")
    try:
        aqi_numeric = float(raw_aqi)
    except (TypeError, ValueError):
        raise _provider_error()
    if not math.isfinite(aqi_numeric) or not 0 <= aqi_numeric <= 500:
        raise _provider_error()
    aqi_value = round(aqi_numeric)

    pollutants = []
    for key in POLLUTANT_KEYS:
        raw_value = current.get(key)
        if raw_value is None:
            continue
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(value) or value < 0:
            continue
        unit = units.get(key, "µg/m³")
        pollutants.append({"key": key, "label": POLLUTANT_LABELS[key], "value": value, "unit": unit if isinstance(unit, str) else "µg/m³"})

    return {
        "location": {"latitude": payload.get("latitude", latitude), "longitude": payload.get("longitude", longitude), "timezone": payload.get("timezone")},
        "current": {"observed_at": current.get("time"), "aqi": aqi_value, "aqi_scale": "US EPA AQI", "category": classify_us_aqi(aqi_value), "pollutants": pollutants},
        "source": {"name": "Open-Meteo Air Quality API", "url": "https://open-meteo.com/en/docs/air-quality-api", "model": "CAMS-based atmospheric composition model", "data_type": "Modeled current estimate; not a ground-monitor station measurement."},
        "caveat": "This is a US EPA AQI-scale model estimate, not India's CPCB National AQI or a personal exposure measurement. Use official local monitoring and public-health advisories for decisions during severe pollution.",
    }
