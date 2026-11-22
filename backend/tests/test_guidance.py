from fastapi.testclient import TestClient
from app.main import app
from app.schemas.guidance import HouseholdContext
from app.services.guidance import aqi_category,build_community_brief,build_daily_guidance,estimate_commute_impact

client=TestClient(app)

def test_aqi_boundaries():
    assert [aqi_category(x) for x in (50,51,101,151,201,301)] == ["Good","Moderate","Unhealthy for sensitive groups","Unhealthy","Very unhealthy","Hazardous"]

def test_sensitive_household_guidance():
    result=build_daily_guidance(130,HouseholdContext(household="children"))
    assert any("cautious household" in x["title"].lower() for x in result["actions"])

def test_indoor_endpoint():
    response=client.post("/api/guidance/indoor",json={"aqi":180})
    assert response.status_code==200
    assert response.json()["recommendations"][0]["when"]=="At home"

def test_impact_estimate_transparent():
    result=estimate_commute_impact(10,5,4,"metro")
    assert result["estimated_kg_co2e_avoided"]>0
    assert "Illustrative" in result["methodology"]
    assert "ambient city AQI" in result["limitations"]

def test_impact_validation():
    assert client.post("/api/impact/estimate",json={"distance_km":-1,"alternative":"metro"}).status_code==422

def test_chat_fallback_without_key(monkeypatch):
    from app.api import guidance
    monkeypatch.setattr(guidance.settings,"gemini_api_key",None)
    response=client.post("/api/assistant/chat",json={"message":"How should I plan today?","aqi":120})
    assert response.status_code==200
    assert response.json()["mode"]=="grounded_fallback"

def test_community_brief_scales_with_aqi_and_household():
    routine=build_community_brief(35)
    sensitive=build_community_brief(160,"children")
    assert routine["response_level"]=="routine"
    assert sensitive["response_level"]=="high_pollution_response"
    assert sensitive["actions"][0]["title"]=="Use an inclusive communication plan"
    assert "does not collect names" in sensitive["privacy_note"]

def test_community_endpoint_validates_aqi():
    assert client.post("/api/community/brief",json={"aqi":800}).status_code==422

