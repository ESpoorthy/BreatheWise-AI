from app.api.air_quality import classify_us_aqi


def test_us_aqi_categories() -> None:
    assert classify_us_aqi(25) == "Good"
    assert classify_us_aqi(75) == "Moderate"
    assert classify_us_aqi(125) == "Unhealthy for sensitive groups"
    assert classify_us_aqi(175) == "Unhealthy"
    assert classify_us_aqi(250) == "Very unhealthy"
    assert classify_us_aqi(350) == "Hazardous"
