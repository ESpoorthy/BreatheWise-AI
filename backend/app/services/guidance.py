from typing import Any

from app.schemas.guidance import HouseholdContext

# Illustrative passenger-kilometre factors (kg CO2e). These are transparent
# planning assumptions, not measured emissions or a lifecycle assessment.
EMISSION_FACTORS = {
    "car": 0.192,
    "bus": 0.105,
    "metro": 0.041,
    "carpool": 0.096,
    "cycle": 0.0,
    "walk": 0.0,
}


def aqi_category(aqi: int) -> str:
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 150:
        return "Unhealthy for sensitive groups"
    if aqi <= 200:
        return "Unhealthy"
    if aqi <= 300:
        return "Very unhealthy"
    return "Hazardous"


def build_daily_guidance(aqi: int, context: HouseholdContext) -> dict[str, Any]:
    category = aqi_category(aqi)
    sensitive = context.household != "general"
    actions: list[dict[str, str]] = []

    if aqi <= 50:
        actions.append({
            "title": "Use the cleaner-air window",
            "when": "Outdoor time",
            "action": "Normal outdoor activity is generally reasonable; check local advisories and symptoms.",
            "why": "The selected US AQI estimate is in the Good band.",
        })
    elif aqi <= 100:
        actions.append({
            "title": "Plan outdoor activity thoughtfully",
            "when": "Outdoor time",
            "action": "Consider shorter or less strenuous outdoor sessions if you notice irritation.",
            "why": "Pollution may affect unusually sensitive people even in the Moderate band.",
        })
    else:
        actions.append({
            "title": "Reduce strenuous outdoor exposure",
            "when": "Outdoor time",
            "action": "Move exercise indoors, shorten time outside, and follow local public-health guidance.",
            "why": "Higher particle pollution can increase exposure during heavy breathing.",
        })

    if sensitive and aqi > 50:
        actions.append({
            "title": "Use a more cautious household plan",
            "when": "Family",
            "action": "For children, older adults, or people with respiratory sensitivity, prioritize lower-exposure options and follow their clinician's advice.",
            "why": "Some groups may be more affected by air pollution.",
        })

    if aqi > 100:
        actions.append({
            "title": "Choose a lower-exposure commute",
            "when": "Travel",
            "action": "Prefer a shorter route, public transport, or a cleaner-air indoor waiting area where practical; avoid high-traffic roadside waiting.",
            "why": "Traffic corridors can add exposure beyond the city-level estimate.",
        })
    else:
        actions.append({
            "title": "Keep the commute practical",
            "when": "Travel",
            "action": "Choose a route that avoids prolonged idling and congested roads where feasible.",
            "why": "Reducing time around concentrated traffic emissions can help limit exposure.",
        })

    indoor_action = (
        "If outdoor pollution is elevated, keep windows closed during peak pollution periods; ventilate when outdoor conditions improve. "
        "Avoid indoor smoking, incense, and unnecessary combustion."
    )
    if context.has_air_purifier:
        indoor_action += " Run a correctly sized particle filter in the room where people spend the most time and maintain it as directed."
    else:
        indoor_action += " If filtration is unavailable, prioritize source control and a cleaner room rather than relying on improvised filters."

    actions.append({
        "title": "Make one room your cleaner-air space",
        "when": "At home",
        "action": indoor_action,
        "why": "Reducing indoor particle sources and filtering air can lower indoor exposure; results depend on the building and device.",
    })

    if context.cooking_fuel == "biomass":
        actions.append({
            "title": "Reduce cooking smoke",
            "when": "Cooking",
            "action": "Use a cleaner fuel or electric cooking option when available, ensure safe exhaust ventilation, and keep children away from cooking smoke.",
            "why": "Solid-fuel cooking can be a significant source of household air pollution.",
        })

    return {
        "aqi": aqi,
        "aqi_scale": "US EPA AQI",
        "category": category,
        "summary": f"The selected location's modeled US AQI value is {aqi} ({category}). Use this as a planning signal, not a personal exposure measurement.",
        "actions": actions,
        "safety_note": "General information only, not medical advice. Follow official local advisories; seek medical care for severe or worsening symptoms.",
    }


def estimate_commute_impact(
    distance_km: float,
    trips_per_week: int,
    weeks: int,
    alternative: str,
) -> dict[str, Any]:
    baseline = distance_km * trips_per_week * weeks * EMISSION_FACTORS["car"]
    alternative_emissions = distance_km * trips_per_week * weeks * EMISSION_FACTORS[alternative]
    avoided = max(0.0, baseline - alternative_emissions)
    return {
        "distance_km_one_way": round(distance_km, 2),
        "trips_per_week": trips_per_week,
        "weeks": weeks,
        "alternative": alternative,
        "baseline_mode": "single-occupancy car",
        "estimated_baseline_kg_co2e": round(baseline, 2),
        "estimated_alternative_kg_co2e": round(alternative_emissions, 2),
        "estimated_kg_co2e_avoided": round(avoided, 2),
        "methodology": "Illustrative passenger-kilometre factors: car 0.192, bus 0.105, metro 0.041, carpool 0.096, cycle/walk 0 kg CO2e per passenger-km. One-way distance is multiplied by trips as entered; adjust trips to represent total one-way journeys.",
        "limitations": "Approximate operational planning estimate, not a verified lifecycle assessment. Actual emissions vary by vehicle, occupancy, grid mix, route, and service.",
    }


def deterministic_answer(message: str, aqi: int | None, context: HouseholdContext) -> str:
    if aqi is None:
        return (
            "I can help with daily routines, indoor air, commuting and pollution basics. "
            "Select a city and share its current air-quality estimate for location-aware guidance. "
            "For now: avoid indoor smoke, maintain cooking exhaust, and check official local air-quality advisories."
        )
    plan = build_daily_guidance(aqi, context)
    top_actions = " ".join(f"{item['title']}: {item['action']}" for item in plan["actions"][:3])
    return (
        f"For the supplied {plan['aqi_scale']} value of {aqi} ({plan['category']}): {top_actions} "
        f"{plan['safety_note']}"
    )
