# BreatheWise AI 🌿

**Your intelligent companion for cleaner air and healthier everyday choices.**

BreatheWise AI is a GenAI-powered urban air-quality assistant designed to help families and communities understand local pollution, make safer day-to-day decisions, improve indoor air practices, and choose lower-emission alternatives.

> **Important:** BreatheWise AI provides general air-quality information and practical guidance. It is not a medical device, emergency service, or substitute for advice from a qualified healthcare professional or official public-health authority.

## Chosen challenge vertical

**Challenge 6 — Urban Air Quality Assistant.** The primary persona is a household member planning safer everyday routines during urban pollution and winter-smog episodes. The app asks the user to choose a city and optionally describe household needs; it does not silently collect device location or personal medical records.

## Working features

- **City search:** look up a city or town without granting device-location permission.
- **Current modeled air quality:** fetch an Open-Meteo current estimate for the selected coordinates.
- **Pollutant details:** view PM2.5, PM10, nitrogen dioxide, sulphur dioxide, ozone, and carbon monoxide where returned by the provider.
- **Source transparency:** show provider attribution, model timestamp, data type, and limitations.
- **Responsive frontend:** React + TypeScript interface with a mobile-friendly city search and air-quality panel.
- **Household-aware daily plan:** recommendations adapt to the selected AQI estimate, household profile (general, children, older adults, or respiratory-sensitive), and purifier availability.
- **Indoor-air guidance:** practical source-control, ventilation-timing, and filtration suggestions with a clear safety note.
- **GenAI assistant:** server-side Gemini integration grounded in the selected modeled AQI and supplied household context, with deterministic fallback if Gemini is not configured or unavailable.
- **Commute impact estimator:** compares a single-occupancy-car baseline with bus, metro, carpool, cycling, or walking using disclosed illustrative passenger-kilometre factors.
- **Community preparedness brief:** generates non-identifying shared-space actions from the selected AQI and household category.
- **On-screen AQI threshold:** lets users choose a threshold and shows a reminder when the currently loaded city estimate reaches it. This is not a background or push notification.
- **Input validation:** Pydantic request models constrain AQI, commute distance, travel frequency, and household options.

The displayed index is explicitly the **US EPA AQI scale**. It is **not India's CPCB National AQI** and is not a ground-monitor station reading. The Open-Meteo air-quality API serves modeled atmospheric composition data; local model coverage and resolution vary. Use official local monitoring and public-health advisories for high-stakes decisions. A nearby modeled grid cell is not a personal exposure monitor.

## Planned enhancements

- **Personalized daily planner:** recommendations shaped by outdoor conditions, commute, household needs, and preferences.
- **Indoor air guidance:** practical ventilation, cleaning, and filtration suggestions.
- **Cleaner commute choices:** compare practical travel alternatives and explain likely trade-offs.
- **Impact explorer:** transparent estimates of travel emissions avoided, with assumptions shown.
- **BreatheWise AI assistant:** conversational explanations grounded in available data and safety guidance.
- **Community view:** shareable, non-identifying local actions and preparedness tips.
- **Official Indian AQI adapter:** integrate validated CPCB station readings and calculate/report India AQI only when the data and averaging requirements are met.

## Product principles

1. Evidence before confidence: show the source, observation time, units, and whether a value is measured, forecast, or estimated.
2. Local and useful: recommendations reflect location and real-world constraints.
3. Explain the why: every recommendation explains its purpose, trade-offs, and limitations.
4. No fake impact numbers: emissions estimates disclose methodology and assumptions.
5. Privacy by default: avoid collecting precise location or personal health information unless necessary and explicitly provided.
6. Safety first: never imply an activity is completely safe based on AQI alone; defer to official advisories.

## Planned technology

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| Styling | Custom responsive CSS |
| Backend | Python, FastAPI |
| Current air-quality data | Open-Meteo Air Quality API |
| City lookup | Open-Meteo Geocoding API |
| GenAI | Google Gemini API (server-side; deterministic fallback) |
| Official Indian monitoring | CPCB station adapter (planned) |
| Maps | Leaflet / OpenStreetMap (planned) |
| Database | Supabase (planned; not required for local MVP) |
| Deployment | Vercel (frontend) + Render (backend) |

## Repository structure

```text
BreatheWise-AI/
├── frontend/                 # React + TypeScript + Vite
├── backend/
│   ├── app/
│   │   ├── api/               # HTTP routes
│   │   ├── core/              # Configuration and shared utilities
│   │   ├── schemas/            # Request/response models
│   │   └── services/           # Data, Gemini, recommendations, impact
│   └── tests/
├── docs/                      # Architecture and product notes
├── .env.example
├── .gitignore
└── README.md
```

## Getting started

### Prerequisites

- Node.js 20+
- Python 3.11+
- npm

### 1. Clone the repository

```bash
git clone https://github.com/ESpoorthy/BreatheWise-AI.git
cd BreatheWise-AI
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Add credentials locally only. **Never commit API keys.**

### 3. Run the backend

```bash
cd backend
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000 · Interactive docs: http://127.0.0.1:8000/docs

### 4. Run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite prints the local development URL in the terminal.

## Approach and decision logic

1. The user searches for a city; the app retrieves coordinates from Open-Meteo Geocoding. Precise device location is not requested.
2. The backend fetches modeled current pollutant data and the provider's US AQI estimate. It returns source, model, timestamp, units, and limitations.
3. The user selects household context. Deterministic rules use the supplied AQI band and household flags to suggest lower-exposure routines and indoor source-control steps.
4. The assistant receives only the user question and the context explicitly selected in the app. Gemini is called from the backend; if it is unavailable, the app returns a rule-based answer.
5. The commute estimator compares a car baseline with a selected alternative using published-in-code illustrative factors. The result is an estimate of transport CO₂e, not a claim that local ambient AQI will improve by that amount.

## Assumptions and limitations

- The current air-quality feed is a modeled Open-Meteo estimate using the **US EPA AQI scale**. It is not an official CPCB station observation, not an Indian National AQI calculation, and not a personal exposure reading.
- Household categories are planning preferences, not diagnoses. The application does not collect diagnoses or provide medical treatment advice.
- Commute factors are illustrative averages and do not account for the exact vehicle, occupancy, grid mix, route, or lifecycle emissions. They are shown for comparative education only.
- The Gemini key is optional for local fallback operation and must be configured only as a backend secret.
- Community features, push alerts, and official CPCB station integration remain future work; they are not represented as currently available.

## API endpoints

- `GET /api/india/stations?city=Hyderabad` — optional hourly station-level observations from the Government of India OGD/CPCB dataset. Requires the backend-only `DATA_GOV_IN_API_KEY`. Does not calculate National AQI from a single hourly snapshot.

- `GET /health` — service health check.
- `GET /api/locations/search?name=Hyderabad` — city/town lookup.
- `GET /api/air-quality?latitude=17.385&longitude=78.486` — current modeled conditions, US AQI category, pollutants, timestamp, and source metadata.
- `POST /api/guidance/daily` — household-aware daily recommendations.
- `POST /api/guidance/indoor` — indoor-air recommendations.
- `POST /api/assistant/chat` — Gemini-backed assistant with deterministic fallback.
- `POST /api/impact/estimate` — transparent illustrative commute-emissions estimate.
- `POST /api/community/brief` — non-identifying community preparedness actions.

The coordinates above are only an example query for Hyderabad; the application does not automatically infer or request a user's precise location.

## Environment variables

| Variable | Purpose | Required |
|---|---|---|
| `GEMINI_API_KEY` | Server-side Gemini API key | Only for AI responses |
| `GEMINI_MODEL` | Gemini model identifier | No; configured default |
| `AQI_PROVIDER` | Selected AQI provider adapter | No |
| `OPENAQ_API_KEY` | OpenAQ credential, if required by current API access | Provider-dependent |
| `DATA_GOV_IN_API_KEY` | Server-side data.gov.in API key for optional Indian station observations | Only for India station data |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins | No; local default |
| `VITE_API_BASE_URL` | Public backend base URL | No; local default |

Do not put secrets in frontend variables (for example, `VITE_*` variables), because browser-exposed values are public.

## Data sources and interpretation

- [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api) — modeled current air-quality variables and AQI indices.
- [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api) — city-name lookup.
- [CPCB Air Quality Resources](https://app.cpcbccr.com/ccr_docs) — official National AQI methodology, station list, and CAAQMS protocol.
- [Open Government Data: Real time AQI from various locations](https://www.data.gov.in/resource/real-time-air-quality-index-various-locations) — official catalogue for hourly station-level data; confirm a supported API before automated integration.

BreatheWise must not relabel a US or European AQI index as CPCB AQI. An official Indian AQI implementation requires compatible pollutant measurements, averaging periods, valid sub-indices, and source attribution.

## Development roadmap

- [x] Create public repository and starter monorepo.
- [x] Add FastAPI health endpoint and React/Vite application shell.
- [x] Add city search and Open-Meteo modeled air-quality API.
- [x] Show pollutant readings, timestamp, source, and AQI-scale caveat.
- [x] Document architecture, privacy, and safety boundaries.
- [x] Add tests for provider failures and API response validation.
- [x] Add isolated CPCB National AQI calculation helpers and methodology tests.
- [x] Add optional data.gov.in/CPCB station-observation adapter with server-side key, validation, and freshness labels.\n- [ ] Verify API access and terms with an active data.gov.in key; add CPCB National AQI only from compliant rolling averages.
- [x] Add Gemini assistant with grounded prompts, safety constraints, and graceful fallback.
- [x] Add household profile and personalized routine planner.
- [x] Add indoor-air guidance and clean-commute comparison.
- [x] Add transparent emissions-impact calculations.
- [x] Add backend tests and frontend build checks in CI.
- [ ] Complete accessibility audit and deployment configuration.
- [ ] Record a demo and document the deployed build.

## Contributing

Issues and pull requests are welcome. Keep changes focused, add tests for behavior changes, and never commit credentials or personal data.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
