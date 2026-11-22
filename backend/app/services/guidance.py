from typing import Any
from app.schemas.guidance import HouseholdContext

EMISSION_FACTORS = {"car": 0.192, "bus": 0.105, "metro": 0.041, "carpool": 0.096, "cycle": 0.0, "walk": 0.0}

def aqi_category(aqi: int) -> str:
    if aqi <= 50: return "Good"
    if aqi <= 100: return "Moderate"
    if aqi <= 150: return "Unhealthy for sensitive groups"
    if aqi <= 200: return "Unhealthy"
    if aqi <= 300: return "Very unhealthy"
    return "Hazardous"

def build_daily_guidance(aqi: int, context: HouseholdContext) -> dict[str, Any]:
    category=aqi_category(aqi)
    actions=[]
    if aqi <= 50:
        actions.append({"title":"Use the cleaner-air window","when":"Outdoor time","action":"Normal outdoor activity is generally reasonable; check local advisories and symptoms.","why":"The selected US AQI estimate is in the Good band."})
    elif aqi <= 100:
        actions.append({"title":"Plan outdoor activity thoughtfully","when":"Outdoor time","action":"Consider shorter or less strenuous outdoor sessions if you notice irritation.","why":"Unusually sensitive people may still notice effects in the Moderate band."})
    else:
        actions.append({"title":"Reduce strenuous outdoor exposure","when":"Outdoor time","action":"Move exercise indoors, shorten time outside, and follow local public-health guidance.","why":"Higher particle pollution can increase exposure during heavy breathing."})
    if context.household != "general" and aqi > 50:
        actions.append({"title":"Use a more cautious household plan","when":"Family","action":"For children, older adults, or people with respiratory sensitivity, prioritize lower-exposure options and follow their clinician's advice.","why":"Some groups may be more affected by air pollution."})
    actions.append({"title":"Choose a lower-exposure commute","when":"Travel","action":"Avoid prolonged roadside waiting and heavy-traffic corridors where practical; consider public transport or a shorter route.","why":"Traffic corridors can add exposure beyond a city-level model estimate."})
    indoor="When outdoor pollution is elevated, keep windows closed during peak periods and ventilate when conditions improve. Avoid indoor smoking, incense, and unnecessary combustion."
    indoor += (" Run a correctly sized particle filter in the room used most and maintain it as directed." if context.has_air_purifier else " Without filtration, prioritize source control and a cleaner room rather than improvised filters.")
    actions.append({"title":"Make one room your cleaner-air space","when":"At home","action":indoor,"why":"Reducing indoor particle sources and filtering air can lower indoor exposure; results vary by building and device."})
    if context.cooking_fuel == "biomass":
        actions.append({"title":"Reduce cooking smoke","when":"Cooking","action":"Use cleaner fuel or electric cooking when available, ensure safe exhaust ventilation, and keep children away from cooking smoke.","why":"Solid-fuel cooking can be a significant source of household air pollution."})
    return {"aqi":aqi,"aqi_scale":"US EPA AQI","category":category,"summary":f"The selected location's modeled US AQI value is {aqi} ({category}). Use this as a planning signal, not a personal exposure measurement.","actions":actions,"safety_note":"General information only, not medical advice. Follow official local advisories; seek medical care for severe or worsening symptoms."}

def estimate_commute_impact(distance_km: float, trips_per_week: int, weeks: int, alternative: str) -> dict[str, Any]:
    journeys=distance_km*trips_per_week*weeks
    baseline=journeys*EMISSION_FACTORS["car"]
    alternative_emissions=journeys*EMISSION_FACTORS[alternative]
    return {"distance_km_one_way":round(distance_km,2),"one_way_trips_per_week":trips_per_week,"weeks":weeks,"alternative":alternative,"baseline_mode":"single-occupancy car","estimated_baseline_kg_co2e":round(baseline,2),"estimated_alternative_kg_co2e":round(alternative_emissions,2),"estimated_kg_co2e_avoided":round(max(0,baseline-alternative_emissions),2),"methodology":"Illustrative passenger-kilometre factors (kg CO2e): car 0.192, bus 0.105, metro 0.041, carpool 0.096, cycle/walk 0. One-way distance is multiplied by one-way journeys entered.","limitations":"Approximate planning estimate, not a verified lifecycle assessment. Actual emissions vary by vehicle, occupancy, electricity mix, route, and service. This does not quantify changes in ambient city AQI."}

def deterministic_answer(message: str, aqi: int | None, context: HouseholdContext) -> str:
    if aqi is None:
        return "I can help with daily routines, indoor air, commuting and pollution basics. Select a city to add its modeled air-quality estimate. For now, avoid indoor smoke, maintain cooking exhaust, and check official local advisories."
    plan=build_daily_guidance(aqi,context)
    actions=" ".join(f"{x['title']}: {x['action']}" for x in plan["actions"][:3])
    return f"For the supplied {plan['aqi_scale']} value of {aqi} ({plan['category']}): {actions} {plan['safety_note']}"

def build_community_brief(aqi: int, household: str = "general") -> dict[str, Any]:
    """Return non-identifying, shareable preparedness actions for a community."""
    if aqi <= 50:
        level="routine"
        actions=[
            {"title":"Keep shared spaces low-emission","action":"Avoid unnecessary idling near gates, schools, and shared entrances."},
            {"title":"Prepare before pollution rises","action":"Share official monitoring links and agree on a simple communication plan."},
            {"title":"Protect green and shaded spaces","action":"Maintain trees and planted areas without burning garden waste."},
        ]
    elif aqi <= 100:
        level="heightened_awareness"
        actions=[
            {"title":"Reduce avoidable traffic emissions","action":"Encourage no-idling near school gates and building entrances; combine errands where practical."},
            {"title":"Share reliable local information","action":"Circulate official air-quality updates and clearly label modeled estimates as estimates."},
            {"title":"Plan flexible outdoor activities","action":"Offer an indoor or lower-exertion alternative for people who feel irritation."},
        ]
    else:
        level="high_pollution_response"
        actions=[
            {"title":"Coordinate lower-exposure schedules","action":"Consider moving strenuous group activities indoors and reducing time beside busy roads."},
            {"title":"Keep vulnerable neighbours informed","action":"Share official advisories with families who may need extra precautions, without collecting medical details."},
            {"title":"Reduce local smoke sources","action":"Avoid waste burning, generator idling where safe alternatives exist, and other unnecessary combustion."},
            {"title":"Make a cleaner-air room available","action":"Where feasible, identify a ventilated or filtered indoor community space and communicate access arrangements."},
        ]
    if household != "general":
        actions.insert(0,{"title":"Use an inclusive communication plan","action":"Provide updates in accessible formats and consider the needs of children, older adults, and people who may be more sensitive to pollution."})
    return {
        "aqi":aqi,"aqi_scale":"US EPA AQI","response_level":level,"actions":actions,
        "privacy_note":"This brief is generated from the selected modeled AQI and an optional household category. It does not collect names, addresses, diagnoses, or individual health records.",
        "source_note":"Community preparedness suggestions are general actions, not official emergency instructions. Follow local government and public-health advisories.",
    }
