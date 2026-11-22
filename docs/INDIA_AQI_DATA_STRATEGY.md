# India AQI data integration strategy

## Decision

BreatheWise currently uses Open-Meteo modeled current conditions and displays the provider's **US EPA AQI** estimate. It must not relabel that value as India's National AQI.

The codebase now contains an isolated, tested CPCB National AQI calculation module. It is a calculation component only: it does not fetch CPCB station readings, and it must not be connected to modeled Open-Meteo data. A station adapter remains blocked until a supported, documented machine-readable feed and its access conditions are confirmed.

## Verified official reference points

- **CPCB Air Quality Resources & Documents:** https://app.cpcbccr.com/ccr_docs
- **CPCB National AQI methodology:** https://www.cpcb.nic.in/displaypdf.php?id=bmF0aW9uYWwtYWlyLXF1YWxpdHktaW5kZXgvSG93X0FRSV9DYWxjdWxhdGVkLnBkZg%3D%3D
- **CPCB AQI breakpoints:** https://airquality.cpcb.gov.in/ccr_docs/About_AQI.pdf
- **CAAQMS station list and data-transmission protocol:** available from the CPCB resources portal above.
- **Open Government Data resource — Real time Air Quality Index from various locations:** https://www.data.gov.in/resource/real-time-air-quality-index-various-locations. Its catalogue describes hourly station-level data; confirm a supported API contract and access conditions before integration.
- **CPCB portal:** https://airquality.cpcb.gov.in/AQI_India/

## Calculation rules implemented

- Eight supported pollutants: PM10, PM2.5, NO2, SO2, CO, O3, NH3 and Pb.
- 24-hour averages for PM10, PM2.5, NO2, SO2, NH3 and Pb; 8-hour averages for CO and O3.
- At least 16 valid hours are required before a pollutant sub-index is calculated.
- Overall AQI requires at least three valid pollutant sub-indices, including PM2.5 or PM10.
- The overall AQI is the maximum valid pollutant sub-index.
- If requirements are not met, the result is explicitly `insufficient_data`; unavailable values are never replaced with zero.
- CO concentrations are accepted in mg/m³; other pollutant concentrations are accepted in µg/m³.

The helper is in `backend/app/services/cpcb_aqi.py`, with tests in `backend/tests/test_cpcb_aqi.py`. The helper expects pre-validated station averages; it does not calculate rolling averages from raw hourly readings.

## Integration gates

1. Confirm a documented, permitted, stable data access method (official API, approved download, or authorized provider).
2. Resolve station metadata: station ID, name, city, state, coordinates, operating agency, and source attribution.
3. Preserve timestamp, averaging window, unit, validity flag, and original source value for each pollutant.
4. Calculate rolling averages from quality-checked measurements according to the CPCB protocol; do not infer 24-hour averages from one hourly sample.
5. Apply the CPCB calculation only to eligible station observations. Do not derive it from a US AQI value or arbitrary model output.
6. Surface missing, stale, invalid, or insufficient pollutant averages as unavailable.
7. Label station observations separately from modeled grid estimates and include station/time context.
8. Test provider failures, malformed records, stale readings, station changes, and calculation edge cases.

## Proposed user experience

- Keep the existing **Modeled estimate · US EPA AQI** card.
- Add a distinct **Official Indian station data** card only when a verified feed is configured.
- Show station name, agency, distance (if coordinates are available), timestamp, pollutant values, averaging period, National AQI category, and source link.
- If no suitable station data is available, say so and link to CPCB's official portal. Do not blend model and station readings into one number.

## Current implementation status

- [x] US AQI model estimate explicitly labeled and caveated.
- [x] Provider payload validation rejects malformed AQI and invalid coordinates.
- [x] Official CPCB and OGD reference sources documented.
- [x] Isolated CPCB sub-index and overall AQI calculation helper.
- [x] Tests for breakpoints, averaging windows, minimum valid hours, pollutant eligibility, and worst-sub-index selection.
- [ ] Confirm a supported official machine-readable endpoint and terms.
- [ ] Implement station ingestion, quality checks, rolling averages, and station metadata.
- [ ] Add freshness and station-distance indicators.
