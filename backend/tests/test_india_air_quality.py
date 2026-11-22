from datetime import datetime, timezone

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api import india_air_quality
from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_normalizes_station_pollutants_and_freshness():
    now = datetime(2026, 11, 22, 12, 0, tzinfo=timezone.utc)
    records = [
        {"state":"Telangana","city":"Hyderabad","station":"Sanathnagar, Hyderabad - TSPCB",
         "latitude":"17.455","longitude":"78.448","pollutant_id":"PM2.5","pollutant_avg":"42","last_update":"22-11-2026 17:00:00"},
        {"state":"Telangana","city":"Hyderabad","station":"Sanathnagar, Hyderabad - TSPCB",
         "latitude":"17.455","longitude":"78.448","pollutant_id":"NO2","pollutant_avg":"18","last_update":"22-11-2026 17:00:00"},
    ]
    result = india_air_quality.normalize_station_records(records, now=now)
    assert len(result["stations"]) == 1
    station = result["stations"][0]
    assert station["freshness"] == "fresh"
    assert station["latitude"] == 17.455
    assert {p["key"] for p in station["pollutants"]} == {"PM2.5", "NO2"}


def test_rejects_invalid_and_unknown_pollutant_records():
    result = india_air_quality.normalize_station_records([
        {"state":"Telangana","city":"Hyderabad","station":"A","pollutant_id":"PM2.5","pollutant_avg":"-1","last_update":"22-11-2026 17:00:00"},
        {"state":"Telangana","city":"Hyderabad","station":"A","pollutant_id":"NOX","pollutant_avg":"12","last_update":"22-11-2026 17:00:00"},
        None,
    ])
    assert result["stations"] == []
    assert result["rejected_records"] == 3


def test_marks_old_station_records_stale():
    now = datetime(2026, 11, 22, 12, 0, tzinfo=timezone.utc)
    result = india_air_quality.normalize_station_records([{
        "state":"Telangana","city":"Hyderabad","station":"A","pollutant_id":"PM10",
        "pollutant_avg":"88","last_update":"22-11-2026 06:00:00",
    }], now=now)
    assert result["stations"][0]["freshness"] == "stale"


def test_india_station_route_requires_server_side_api_key(monkeypatch):
    monkeypatch.setattr(settings, "data_gov_in_api_key", None)
    response = client.get("/api/india/stations?city=Hyderabad")
    assert response.status_code == 503
    assert "DATA_GOV_IN_API_KEY" in response.json()["detail"]


def test_india_station_route_returns_explicit_no_aqi(monkeypatch):
    monkeypatch.setattr(settings, "data_gov_in_api_key", "test-secret")
    async def fake_fetch(city, api_key):
        assert city == "Hyderabad"
        assert api_key == "test-secret"
        return {"records":[{"state":"Telangana","city":"Hyderabad","station":"Test station",
            "pollutant_id":"PM2.5","pollutant_avg":"42","last_update":"22-11-2026 17:00:00"}]}
    monkeypatch.setattr(india_air_quality, "fetch_ogd_records", fake_fetch)
    response = client.get("/api/india/stations?city=Hyderabad")
    assert response.status_code == 200
    body = response.json()
    assert body["national_aqi"] is None
    assert len(body["stations"]) == 1
    assert "No National AQI" in body["national_aqi_note"]


def test_india_station_route_handles_provider_errors(monkeypatch):
    monkeypatch.setattr(settings, "data_gov_in_api_key", "test-secret")
    async def fake_fetch(city, api_key):
        raise HTTPException(status_code=502, detail="provider down")
    monkeypatch.setattr(india_air_quality, "fetch_ogd_records", fake_fetch)
    assert client.get("/api/india/stations?city=Hyderabad").status_code == 502


def test_future_dated_station_record_is_rejected():
    now = datetime(2026, 11, 22, 12, 0, tzinfo=timezone.utc)
    result = india_air_quality.normalize_station_records([{
        "state":"Telangana","city":"Hyderabad","station":"A","pollutant_id":"PM10",
        "pollutant_avg":"88","last_update":"22-11-2026 18:00:00",
    }], now=now)
    assert result["stations"] == []
    assert result["rejected_records"] == 1


def test_station_freshness_uses_oldest_included_pollutant():
    now = datetime(2026, 11, 22, 12, 0, tzinfo=timezone.utc)
    result = india_air_quality.normalize_station_records([
        {"state":"Telangana","city":"Hyderabad","station":"A","pollutant_id":"PM10",
         "pollutant_avg":"88","last_update":"22-11-2026 06:00:00"},
        {"state":"Telangana","city":"Hyderabad","station":"A","pollutant_id":"PM2.5",
         "pollutant_avg":"42","last_update":"22-11-2026 17:00:00"},
    ], now=now)
    station = result["stations"][0]
    assert station["freshness"] == "stale"
    assert station["age_hours"] == 6
    assert {p["freshness"] for p in station["pollutants"]} == {"fresh", "stale"}
