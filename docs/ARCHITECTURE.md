# Architecture Notes

## Current request flow

1. The user searches for a city name; the browser does not request device location.
2. FastAPI calls the Open-Meteo Geocoding API and returns a small list of matching places.
3. The user selects a result. The frontend sends its latitude and longitude to the backend.
4. FastAPI requests current air-quality variables from Open-Meteo.
5. The API returns a US EPA AQI-scale model estimate, available pollutant values and units, the model timestamp, and source/limitation metadata.
6. The UI labels the estimate and does not claim it is an official CPCB station reading.

## Planned system boundaries

- **Frontend:** presents source-aware AQI states, personalized guidance, and an explainable impact view.
- **FastAPI backend:** validates inputs, orchestrates provider calls, applies policy and safety checks, and returns typed response objects.
- **AQI adapters:** isolate provider-specific request/response handling. Each observation should carry pollutant, value, unit, station/location, observation time, provider, and quality metadata when available.
- **Recommendation service:** combines current observations with user-declared constraints. Recommendations state rationale and uncertainty.
- **Gemini service:** generates plain-language explanations from supplied, validated context. It must not invent AQI readings, claim diagnoses, or replace official emergency/public-health guidance.
- **Impact service:** uses documented calculation factors and user-visible assumptions. Avoid claiming an individual's routine changes ambient citywide AQI.
- **CPCB adapter (planned):** should consume validated official monitoring data and preserve station metadata, averaging windows, units, and pollutant sub-index validity.

## Data contract principles

1. Preserve provider timestamps and units.
2. Distinguish station observations from modeled estimates and forecasts.
3. Represent unavailable data explicitly; never silently substitute fabricated values.
4. Include source attribution and interpretation notes on API responses.
5. Validate geographic input and avoid retaining exact coordinates unless needed.
6. Keep secrets and provider credentials on the server.
7. Never label a foreign AQI scale as India’s CPCB National AQI.

## Planned request flow for personalized guidance

1. Frontend requests air quality for a user-selected location.
2. Backend obtains source-validated observations and metadata.
3. Recommendation service evaluates normalized values and user-selected context.
4. Gemini explains the grounded recommendation using supplied context and safety constraints.
5. API returns recommendations, source metadata, assumptions, limitations, and timestamp.
