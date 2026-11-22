from typing import Literal
from pydantic import BaseModel, Field

class HouseholdContext(BaseModel):
    household: Literal["general", "children", "older_adults", "respiratory_sensitive"] = "general"
    commute: Literal["walk", "cycle", "public_transport", "car", "work_from_home"] = "public_transport"
    outdoor_minutes: int = Field(default=30, ge=0, le=600)
    has_air_purifier: bool = False
    cooking_fuel: Literal["electric", "lpg", "biomass", "other"] = "lpg"

class GuidanceRequest(BaseModel):
    aqi: int = Field(ge=0, le=500)
    context: HouseholdContext = Field(default_factory=HouseholdContext)

class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1200)
    aqi: int | None = Field(default=None, ge=0, le=500)
    city: str | None = Field(default=None, max_length=100)
    context: HouseholdContext = Field(default_factory=HouseholdContext)

class ImpactRequest(BaseModel):
    distance_km: float = Field(gt=0, le=500)
    trips_per_week: int = Field(default=5, ge=1, le=21)
    weeks: int = Field(default=4, ge=1, le=52)
    alternative: Literal["bus", "metro", "cycle", "walk", "carpool"]
