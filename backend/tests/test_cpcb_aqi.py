import pytest

from app.services.cpcb_aqi import calculate_national_aqi, calculate_sub_index


@pytest.mark.parametrize(
    "pollutant,value,window,expected",
    [
        ("pm2_5", 30, 24, 50),
        ("pm2_5", 45, 24, 75),
        ("pm10", 75, 24, 75),
        ("no2", 60, 24, 75),
        ("o3", 75, 8, 75),
        ("co", 1.5, 8, 73),
        ("so2", 60, 24, 75),
        ("nh3", 300, 24, 75),
        ("pb", 0.75, 24, 69),
    ],
)
def test_cpcb_sub_index_interpolates_breakpoints(pollutant, value, window, expected):
    assert calculate_sub_index(pollutant, value, averaging_hours=window, valid_hours=24) == expected


def test_sub_index_rejects_wrong_averaging_window():
    with pytest.raises(ValueError, match="24-hour"):
        calculate_sub_index("pm2_5", 45, averaging_hours=1, valid_hours=24)
    with pytest.raises(ValueError, match="8-hour"):
        calculate_sub_index("co", 1.5, averaging_hours=24, valid_hours=24)


@pytest.mark.parametrize("valid_hours", [None, 0, 15, -1])
def test_sub_index_requires_at_least_16_valid_hours(valid_hours):
    with pytest.raises(ValueError, match="16 valid hours"):
        calculate_sub_index("pm2_5", 30, averaging_hours=24, valid_hours=valid_hours)


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), "bad", True])
def test_sub_index_rejects_invalid_concentrations(value):
    with pytest.raises(ValueError):
        calculate_sub_index("pm2_5", value, averaging_hours=24, valid_hours=24)


def test_overall_aqi_requires_three_pollutants_and_particulate():
    only_two = {
        "pm2_5": {"concentration": 45, "averaging_hours": 24, "valid_hours": 24},
        "no2": {"concentration": 60, "averaging_hours": 24, "valid_hours": 24},
    }
    result = calculate_national_aqi(only_two)
    assert result["status"] == "insufficient_data"
    assert result["aqi"] is None

    no_pm = {
        "no2": {"concentration": 60, "averaging_hours": 24, "valid_hours": 24},
        "so2": {"concentration": 60, "averaging_hours": 24, "valid_hours": 24},
        "co": {"concentration": 1.45, "averaging_hours": 8, "valid_hours": 24},
    }
    assert calculate_national_aqi(no_pm)["status"] == "insufficient_data"


def test_overall_aqi_uses_worst_valid_sub_index():
    observations = {
        "pm2_5": {"concentration": 45, "averaging_hours": 24, "valid_hours": 24},
        "no2": {"concentration": 60, "averaging_hours": 24, "valid_hours": 24},
        "co": {"concentration": 1.5, "averaging_hours": 8, "valid_hours": 24},
    }
    result = calculate_national_aqi(observations)
    assert result["status"] == "available"
    assert result["aqi"] == 75
    assert result["category"] == "Satisfactory"
    assert result["dominant_pollutant"] == "pm2_5"


def test_invalid_pollutant_is_excluded_without_becoming_zero():
    observations = {
        "pm2_5": {"concentration": 45, "averaging_hours": 24, "valid_hours": 24},
        "no2": {"concentration": 60, "averaging_hours": 24, "valid_hours": 24},
        "co": {"concentration": 1.5, "averaging_hours": 24, "valid_hours": 24},
    }
    result = calculate_national_aqi(observations)
    assert result["status"] == "insufficient_data"
    assert "co" in result["unavailable"]
