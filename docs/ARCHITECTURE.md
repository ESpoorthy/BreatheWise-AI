# Architecture Notes

## Initial system boundaries

- **Frontend:** presents source-aware AQI states, personalized guidance, and an explainable impact view.
- **FastAPI backend:** validates inputs, orchestrates provider calls, applies policy and safety checks, and returns typed response objects.
- **AQI adapters:** isolate provider-specific request/response handling. Every observation should carry pollutant, value, unit, station/location, observation time, provider, and quality metadata when available.
- **Recommendation service:** combines current observations with user-declared constraints. Recommendations state rationale and uncertainty.
- **Gemini service:** generates plain-language explanations from supplied, validated context. It must not invent AQI readings, claim diagnoses, or replace official emergency/public-health guidance.
- **Impact service:** uses documented calculation factors and user-visible assumptions. Avoid claiming an individual's routine changes ambient citywide AQI.

## Data contract principles

1. Preserve provider timestamps and units.
2. Distinguish observations from forecasts and derived values.
3. Represent unavailable data explicitly; never silently substitute fabricated values.
4. Include source attribution on API responses.
5. Validate geographic input and avoid retaining exact coordinates unless needed.
6. Keep secrets and provider credentials on the server.

## Planned request flow

1. Frontend requests air quality for a user-selected location.
2. Backend resolves the location through a supported provider or receives an approved location identifier.
3. AQI adapter fetches and normalizes source data.
4. Recommendation service evaluates normalized values and user-selected context.
5. Gemini explains the grounded recommendation using supplied context.
6. API returns recommendations, source metadata, limitations, and timestamp.
