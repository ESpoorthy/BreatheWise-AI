"""CPCB National AQI calculation helpers.

This module deliberately accepts only validated station averages. It does not
fetch data or convert modeled US/EU AQI values into an Indian AQI.
"""
from __future__ import annotations

import math
from typing import Any, Mapping

# (concentration lower, concentration upper, AQI lower, AQI upper)
# Concentrations follow CPCB's published breakpoint table. CO is mg/m³;
# all other pollutants are µg/m³.
BREAKPOINTS: dict[str, tuple[tuple[float, float, int, int], ...]] = {
    "pm10": ((0, 50, 0, 50), (50, 100, 50, 100), (100, 250, 100, 200),
             (250, 350, 200, 300), (350, 430, 300, 400)),
    "pm2_5": ((0, 30, 0, 50), (30, 60, 50, 100), (60, 90, 100, 200),
              (90, 120, 200, 300), (120, 250, 300, 400)),
    "no2": ((0, 40, 0, 50), (40, 80, 50, 100), (80, 180, 100, 200),
            (180, 280, 200, 300), (280, 400, 300, 400)),
    "o3": ((0, 50, 0, 50), (50, 100, 50, 100), (100, 168, 100, 200),
           (168, 208, 200, 300), (208, 748, 300, 400)),
    "co": ((0, 1, 0, 50), (1, 2, 50, 100), (2, 10, 100, 200),
           (10, 17, 200, 300), (17, 34, 300, 400)),
    "so2": ((0, 40, 0, 50), (40, 80, 50, 100), (80, 380, 100, 200),
            (380, 800, 200, 300), (800, 1600, 300, 400)),
    "nh3": ((0, 200, 0, 50), (200, 400, 50, 100), (400, 800, 100, 200),
            (800, 1200, 200, 300), (1200, 1800, 300, 400)),
    "pb": ((0, 0.5, 0, 50), (0.5, 1, 50, 100), (1, 2, 100, 200),
           (2, 3, 200, 300), (3, 3.5, 300, 400)),
}
EXPECTED_AVERAGING_HOURS = {
    "pm10": 24, "pm2_5": 24, "no2": 24, "so2": 24,
    "nh3": 24, "pb": 24, "co": 8, "o3": 8,
}
PARTICULATE_KEYS = {"pm10", "pm2_5"}
CATEGORIES = (
    (50, "Good"),
    (100, "Satisfactory"),
    (200, "Moderate"),
    (300, "Poor"),
    (400, "Very Poor"),
    (500, "Severe"),
)


def calculate_sub_index(
    pollutant: str,
    concentration: float,
    *,
    averaging_hours: int,
    valid_hours: int,
) -> int:
    """Calculate one CPCB sub-index from a compliant pollutant average."""
    if pollutant not in BREAKPOINTS:
        raise ValueError(f"Unsupported CPCB AQI pollutant: {pollutant}")
    if isinstance(concentration, bool) or not isinstance(concentration, (int, float)):
        raise ValueError("Concentration must be a finite number")
    if not math.isfinite(concentration) or concentration < 0:
        raise ValueError("Concentration must be a finite non-negative number")
    if averaging_hours != EXPECTED_AVERAGING_HOURS[pollutant]:
        raise ValueError(f"{pollutant} requires a {EXPECTED_AVERAGING_HOURS[pollutant]}-hour average")
    if isinstance(valid_hours, bool) or not isinstance(valid_hours, int) or valid_hours < 16:
        raise ValueError("At least 16 valid hours are required for a pollutant sub-index")

    bands = BREAKPOINTS[pollutant]
    if concentration <= bands[0][0]:
        return bands[0][2]
    for low_c, high_c, low_i, high_i in bands:
        if low_c <= concentration <= high_c:
            if high_c == low_c:
                return high_i
            index = ((high_i - low_i) / (high_c - low_c)) * (concentration - low_c) + low_i
            return max(0, min(500, round(index)))
    # CPCB defines the final band as Severe (401–500); values above its
    # published upper breakpoint remain in that category and are capped.
    return 500


def calculate_national_aqi(
    observations: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    """Calculate National AQI only when CPCB minimum-data rules are met.

    Each observation must contain concentration, averaging_hours and
    valid_hours. Ineligible pollutant records are reported as unavailable.
    """
    if not isinstance(observations, Mapping):
        raise ValueError("Observations must be a pollutant mapping")

    sub_indices: dict[str, int] = {}
    unavailable: dict[str, str] = {}
    for pollutant, observation in observations.items():
        if pollutant not in BREAKPOINTS:
            unavailable[str(pollutant)] = "Unsupported pollutant"
            continue
        if not isinstance(observation, Mapping):
            unavailable[pollutant] = "Malformed observation"
            continue
        try:
            sub_indices[pollutant] = calculate_sub_index(
                pollutant,
                observation.get("concentration"),
                averaging_hours=observation.get("averaging_hours"),
                valid_hours=observation.get("valid_hours"),
            )
        except (TypeError, ValueError) as exc:
            unavailable[pollutant] = str(exc)

    has_particulate = any(key in sub_indices for key in PARTICULATE_KEYS)
    eligible = len(sub_indices) >= 3 and has_particulate
    if not eligible:
        return {
            "status": "insufficient_data",
            "aqi": None,
            "category": None,
            "sub_indices": sub_indices,
            "unavailable": unavailable,
            "requirements": {
                "minimum_valid_pollutants": 3,
                "requires_pm25_or_pm10": True,
                "minimum_valid_hours_per_pollutant": 16,
            },
        }

    aqi = max(sub_indices.values())
    category = next(label for upper, label in CATEGORIES if aqi <= upper)
    return {
        "status": "available",
        "aqi": aqi,
        "category": category,
        "dominant_pollutant": max(sub_indices, key=sub_indices.get),
        "sub_indices": sub_indices,
        "unavailable": unavailable,
    }
