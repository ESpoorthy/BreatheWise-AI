"""Optional station-level observations from India's OGD platform.

These are hourly pollutant observations, not precomputed CPCB National AQI.
No National AQI is calculated from a single hourly snapshot.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

import httpx
from fastapi import APIRouter, HTTPException, Query

from app.core.config import settings

router = APIRouter(prefix="/api/india", tags=["India station data"])
OGD_RESOURCE_URL = "https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
OGD_RESOURCE_ID = "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
OGD_RESOURCE_PAGE = "https://www.data.gov.in/resource/real-time-air-quality-index-various-locations"
INDIA_TZ = ZoneInfo("Asia/Kolkata")
MAX_RECORDS = 1000
FRESHNESS_HOURS = 3
POLLUTANTS = {
    "PM2.5": ("PM2.5", "µg/m³"), "PM10": ("PM10", "µg/m³"),
    "NO2": ("Nitrogen dioxide", "µg/m³"), "SO2": ("Sulphur dioxide", "µg/m³"),
    "CO": ("Carbon monoxide", "mg/m³"), "OZONE": ("Ozone", "µg/m³"),
    "O3": ("Ozone", "µg/m³"), "NH3": ("Ammonia", "µg/m³"), "PB": ("Lead", "µg/m³"),
}


def parse_ogd_timestamp(value: str) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value.strip(), "%d-%m-%Y %H:%M:%S").replace(tzinfo=INDIA_TZ)
    except ValueError:
        return None


def normalize_station_records(records: Any, *, now: datetime | None = None) -> dict[str, Any]:
    if not isinstance(records, list):
        raise ValueError("OGD records must be a list")
    now_utc = now or datetime.now(timezone.utc)
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    rejected = 0
    for row in records[:MAX_RECORDS]:
        if not isinstance(row, dict):
            rejected += 1
            continue
        city, station, state = row.get("city"), row.get("station"), row.get("state")
        pollutant_id = str(row.get("pollutant_id", "")).strip().upper()
        if not all(isinstance(v, str) and v.strip() for v in (city, station, state)):
            rejected += 1
            continue
        pollutant = POLLUTANTS.get(pollutant_id)
        if not pollutant:
            rejected += 1
            continue
        try:
            value = float(row.get("pollutant_avg"))
        except (TypeError, ValueError):
            rejected += 1
            continue
        if not math.isfinite(value) or value < 0:
            rejected += 1
            continue
        observed_at = parse_ogd_timestamp(row.get("last_update"))
        if observed_at is None:
            rejected += 1
            continue
        key = (state.strip(), city.strip(), station.strip())
        item = grouped.setdefault(key, {
            "state": state.strip(), "city": city.strip(), "station": station.strip(),
            "latitude": None, "longitude": None, "observed_at": observed_at.isoformat(),
            "pollutants": {},
        })
        try:
            lat, lon = float(row.get("latitude")), float(row.get("longitude"))
            if math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180:
                item["latitude"], item["longitude"] = lat, lon
        except (TypeError, ValueError):
            pass
        item["pollutants"][pollutant_id] = {
            "key": pollutant_id, "label": pollutant[0], "value": value, "unit": pollutant[1],
        }
        if observed_at.isoformat() > item["observed_at"]:
            item["observed_at"] = observed_at.isoformat()
    stations = []
    for item in grouped.values():
        observed = datetime.fromisoformat(item["observed_at"])
        age = max(0.0, (now_utc - observed.astimezone(timezone.utc)).total_seconds() / 3600)
        item["age_hours"] = round(age, 1)
        item["freshness"] = "fresh" if age <= FRESHNESS_HOURS else "stale"
        item["pollutants"] = list(item["pollutants"].values())
        stations.append(item)
    stations.sort(key=lambda item: (item["freshness"] != "fresh", item["station"].casefold()))
    return {"stations": stations, "rejected_records": rejected}


async def fetch_ogd_records(city: str, api_key: str) -> dict[str, Any]:
    params = {"api-key": api_key, "format": "json", "limit": MAX_RECORDS, "offset": 0, "filters[city]": city}
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(12.0, connect=4.0)) as client:
            response = await client.get(OGD_RESOURCE_URL, params=params)
            response.raise_for_status()
            payload = response.json()
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="India station data is temporarily unavailable. Please try again.") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
        raise HTTPException(status_code=502, detail="India station data returned an invalid response.")
    return payload


@router.get("/stations")
async def get_india_station_data(city: str = Query(min_length=2, max_length=80)) -> dict[str, Any]:
    """Return station-level hourly pollutant observations for one city."""
    api_key = settings.data_gov_in_api_key
    if not api_key or not api_key.strip():
        raise HTTPException(status_code=503, detail="Official Indian station data is not configured yet. Add DATA_GOV_IN_API_KEY to the backend environment.")
    payload = await fetch_ogd_records(city.strip(), api_key.strip())
    try:
        normalized = normalize_station_records(payload["records"])
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="India station data returned an invalid record set.") from exc
    return {
        "city": city.strip(), "resource": OGD_RESOURCE_ID,
        "source": "Government of India OGD Platform · CPCB", "source_url": OGD_RESOURCE_PAGE,
        "data_type": "Hourly station-level pollutant averages from monitoring instruments.",
        "national_aqi": None,
        "national_aqi_note": "No National AQI is calculated from this hourly snapshot. CPCB AQI requires compliant pollutant averaging windows and valid-data coverage.",
        **normalized,
    }
