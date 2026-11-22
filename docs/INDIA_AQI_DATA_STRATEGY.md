# India AQI data integration strategy

## Decision

BreatheWise currently uses Open-Meteo modeled current conditions and displays the provider's **US EPA AQI** estimate. It must not relabel that value as India's National AQI.

The next India-specific milestone is a separately versioned adapter for verified Indian monitoring data. Until a supported, documented machine-readable feed and its access conditions are confirmed, the app should link users to official monitoring resources rather than scrape undocumented browser endpoints or infer CPCB AQI.

## Verified official reference points

- **CPCB Air Quality Resources & Documents:** https://app.cpcbccr.com/ccr_docs
  - Includes the National AQI overview and calculation methodology, CAAQMS station list, and data-transmission protocol.
- **CPCB CAAQMS station list:** https://app.cpcbccr.com/ccr_docs/caaqms_list_All_India.pdf
  - Provides station names, cities, agencies, and station codes. The document describes station codes in the `site_NNN` form.
- **CPCB station data transmission protocol:** https://app.cpcbccr.com/ccr_docs/Protocol_CAAQM.pdf
  - Describes 15-minute average pollutant data transmission and standardized pollutant naming/units.
- **Open Government Data resource — Real time Air Quality Index from various locations:** https://www.data.gov.in/resource/real-time-air-quality-index-various-locations
  - The official catalogue describes an hourly, station-level dataset and warns that raw live instrument values may contain abnormal readings. Its current catalogue entry does not advertise a sourced webservice/API endpoint; a stable API contract must be confirmed before integration.
- **CPCB portal:** https://airquality.cpcb.gov.in/AQI_India/

## Integration gates

Do not enable a CPCB/India AQI badge until all of these are satisfied:

1. A documented, permitted, stable data access method is confirmed (official API, approved download, or an authorized data provider).
2. Station metadata can be resolved: station ID, name, city, state, coordinates, operating agency, and source attribution.
3. Each pollutant record retains measurement timestamp, averaging window, unit, validity flag, and original source value.
4. The National AQI calculation follows the CPCB method and breakpoint table for eligible pollutants. Do not derive it from a US AQI value or from arbitrary model output.
5. Missing, stale, invalid, or insufficient pollutant averages are surfaced as unavailable; never silently substitute zero or another AQI scale.
6. The UI labels a station observation separately from modeled grid estimates and includes distance/time context.
7. Provider failure, malformed records, stale readings, and station changes are covered by automated tests.

## Proposed user experience

- Keep the existing **Modeled estimate · US EPA AQI** card.
- Add a distinct **Official Indian station data** card only when a verified feed is configured.
- Show station name, agency, distance (if coordinates are available), timestamp, pollutant values, averaging period, National AQI category, and source link.
- If no suitable station data is available, say so and provide a link to CPCB's official portal. Do not blend model and station readings into one number.

## Current implementation status

- [x] US AQI model estimate explicitly labeled and caveated.
- [x] Provider payload validation rejects malformed AQI and invalid coordinates.
- [x] Official CPCB and OGD reference sources documented.
- [ ] Confirm a supported official machine-readable endpoint and terms.
- [ ] Implement the station adapter and CPCB National AQI calculation with methodology tests.
- [ ] Add freshness and station-distance indicators.
