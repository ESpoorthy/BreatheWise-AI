from fastapi.testclient import TestClient

from app.main import app
from app.schemas.guidance import HouseholdContext
from app.services.guidance import (
    aqi_category,
    build_daily_guidance,
    estimate_commute_impact,
)

client = TestClient(app)


def test_aqi_boundaries() -> None:
    assert aqi_category(50) == "Good"
    assert aqi_category(51) == "Moderate"
    assert aqi_category(101) == "Unhealthy for sensitive groups"
    assert aqi_category(151) == "Unhealthy"
    assert aqi_category(201) == "Very unhealthy"
    assert aqi_category(301) == "Hazardous"


def test_sensitive_household_gets_cautious_guidance() -> None:
    result = build_daily_guidance(130, HouseholdContext(household="children"))
    assert result["category"] == "Unhealthy for sensitive groups"
    assert any("cautious household" in item["title"].lower() for item in result["actions"])
    assert result["aqi_scale"] == "US EPA AQI"


def test_indoor_endpoint_returns_source_control_actions() -> None:
    response = client.post("/api/guidance/indoor", json={"aqi": 180})
    assert response.status_code == 200
    assert response.json()["recommendations"]
    assert response.json()["recommendations"][0]["when"] == "At home"


def test_impact_estimate_is_transparent_and_non_negative() -> None:
    result = estimate_commute_impact(10, 5, 4, "metro")
    assert result["estimated_kg_co2e_avoided"] > 0
    assert "Illustrative" in result["methodology"]
    assert result["estimated_alternative_kg_co2e"] < result["estimated_baseline_kg_co2e"]


def test_impact_endpoint_validates_distance() -> None:
    response = client.post("/api/impact/estimate", json={
        "distance_km": -1, "trips_per_week": 5, "weeks": 4, "alternative": "metro"
    })
    assert response.status_code == 422


def test_daily_guidance_rejects_out_of_range_aqi() -> None:
    response = client.post("/api/guidance/daily", json={"aqi": 900})
    assert response.status_code == 422


def test_chat_uses_fallback_without_api_key(monkeypatch) -> None:
    from app.api import guidance

    monkeypatch.setattr(guidance.settings, "gemini_api_key", None)
    response = client.post("/api/assistant/chat", json={"message": "How should I plan today?", "aqi": 120})
    assert response.status_code == 200
    assert response.json()["mode"] == "grounded_fallback"
    assert "US EPA AQI" in response.json()["answer"]
