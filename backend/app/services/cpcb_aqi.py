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
    "pm10": ((0, 50, 0, 50), (51, 100, 51, 100), (101, 250, 101, 200),
             (251, 350, 201, 300), (351, 430, 301, 400)),
    "pm2_5": ((0, 30, 0, 50), (31, 60, 51, 100), (61, 90, 101, 200),
              (91, 120, 201, 300), (121, 250, 301, 400)),
    "no2": ((0, 40, 0, 50), (41, 80, 51, 100), (81, 180, 101, 200),
            (181, 280, 201, 300), (281, 400, 301, 400)),
    "o3": ((0, 50, 0, 50), (51, 100, 51, 100), (101, 168, 101, 200),
           (169, 208, 201, 300), (209, 748, 301, 400)),
    "co": ((0, 1, 0, 50), (1.1, 2, 51, 100), (2.1, 10, 101, 200),
           (10.1, 17, 201, 300), (17.1, 34, 301, 400)),
    "so2": ((0, 40, 0, 50), (41, 80, 51, 100), (81, 380, 101, 200),
            (381, 800, 201, 300), (801, 1600, 301, 400)),
    "nh3": ((0, 200, 0, 50), (201, 400, 51, 100), (401, 800, 101, 200),
            (801, 1200, 201, 300), (1201, 1800, 301, 400)),
    "pb": ((0, 0.5, 0, 50), (0.6, 1, 51, 100), (1.1, 2, 101, 200),
           (2.1, 3, 201, 300), (3.1, 3.5, 301, 400)),
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
