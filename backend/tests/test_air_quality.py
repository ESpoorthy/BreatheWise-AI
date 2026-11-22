import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.api import air_quality
from app.main import app
from app.api.air_quality import classify_us_aqi

client = TestClient(app)


def test_us_aqi_categories() -> None:
    assert [classify_us_aqi(x) for x in (25, 75, 125, 175, 250, 350)] == [
        "Good", "Moderate", "Unhealthy for sensitive groups", "Unhealthy", "Very unhealthy", "Hazardous"
    ]


def test_air_quality_validates_and_filters_provider_values(monkeypatch) -> None:
    async def fake_provider(url, params):
        return {
            "latitude": 17.4, "longitude": 78.4, "timezone": "Asia/Kolkata",
            "current": {"time": "2026-11-22T10:00", "us_aqi": 87, "pm2_5": 22.4, "pm10": -3, "ozone": "bad", "nitrogen_dioxide": 10},
            "current_units": {"pm2_5": "µg/m³", "nitrogen_dioxide": "µg/m³"},
        }
    monkeypatch.setattr(air_quality, "get_provider_json", fake_provider)
    response = client.get("/api/air-quality?latitude=17.4&longitude=78.4")
    assert response.status_code == 200
    data = response.json()
    assert data["current"]["aqi"] == 87
    assert data["current"]["category"] == "Moderate"
    assert [p["key"] for p in data["current"]["pollutants"]] == ["pm2_5", "nitrogen_dioxide"]
    assert "not India's CPCB" in data["caveat"]


@pytest.mark.parametrize("bad_aqi", [None, "not-a-number", "nan", "inf", -1, 501])
def test_air_quality_rejects_invalid_provider_aqi(monkeypatch, bad_aqi) -> None:
    async def fake_provider(url, params):
        return {"current": {"us_aqi": bad_aqi}, "current_units": {}}
    monkeypatch.setattr(air_quality, "get_provider_json", fake_provider)
    response = client.get("/api/air-quality?latitude=17.4&longitude=78.4")
    assert response.status_code == 502


def test_air_quality_rejects_malformed_current_payload(monkeypatch) -> None:
    async def fake_provider(url, params):
        return {"current": [], "current_units": {}}
    monkeypatch.setattr(air_quality, "get_provider_json", fake_provider)
    assert client.get("/api/air-quality?latitude=17.4&longitude=78.4").status_code == 502


def test_location_search_filters_invalid_coordinates(monkeypatch) -> None:
    async def fake_provider(url, params):
        return {"results": [
            {"name": "Hyderabad", "latitude": 17.385, "longitude": 78.486, "country": "India"},
            {"name": "Bad place", "latitude": 999, "longitude": 78},
            {"name": "Missing coordinates"},
        ]}
    monkeypatch.setattr(air_quality, "get_provider_json", fake_provider)
    response = client.get("/api/locations/search?name=Hyderabad")
    assert response.status_code == 200
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["name"] == "Hyderabad"


def test_location_search_rejects_invalid_results_shape(monkeypatch) -> None:
    async def fake_provider(url, params):
        return {"results": "not-a-list"}
    monkeypatch.setattr(air_quality, "get_provider_json", fake_provider)
    assert client.get("/api/locations/search?name=Hyderabad").status_code == 502


def test_provider_http_failure_becomes_502(monkeypatch) -> None:
    async def fake_provider(url, params):
        raise HTTPException(status_code=502, detail="provider unavailable")
    monkeypatch.setattr(air_quality, "get_provider_json", fake_provider)
    assert client.get("/api/air-quality?latitude=17.4&longitude=78.4").status_code == 502
