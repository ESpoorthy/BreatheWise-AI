# BreatheWise AI 🌿

**Your intelligent companion for cleaner air and healthier everyday choices.**

BreatheWise AI is a GenAI-powered urban air-quality assistant designed to help families and communities understand local pollution, make safer day-to-day decisions, improve indoor air practices, and choose lower-emission alternatives.

> **Important:** BreatheWise AI provides general air-quality information and practical guidance. It is not a medical device, emergency service, or substitute for advice from a qualified healthcare professional or official public-health authority.

## Working in this starter build

- **City search:** look up a city or town without granting device-location permission.
- **Current modeled air quality:** fetch an Open-Meteo current estimate for the selected coordinates.
- **Pollutant details:** view PM2.5, PM10, nitrogen dioxide, sulphur dioxide, ozone, and carbon monoxide where returned by the provider.
- **Source transparency:** show provider attribution, model timestamp, data type, and limitations.
- **Responsive frontend:** React + TypeScript interface with a mobile-friendly city search and air-quality panel.

The displayed index is explicitly the **US EPA AQI scale**. It is **not India's CPCB National AQI** and is not a ground-monitor station reading. The Open-Meteo air-quality API serves modeled atmospheric composition data; local model coverage and resolution vary. Use official local monitoring and public-health advisories for high-stakes decisions. A nearby modeled grid cell is not a personal exposure monitor.

## What we're building next

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
| GenAI | Google Gemini API (planned; server-side integration) |
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

## API endpoints

- `GET /health` — service health check.
- `GET /api/locations/search?name=Hyderabad` — city/town lookup.
- `GET /api/air-quality?latitude=17.385&longitude=78.486` — current modeled conditions, US AQI category, pollutants, timestamp, and source metadata.

The coordinates above are only an example query for Hyderabad; the application does not automatically infer or request a user's precise location.

## Environment variables

| Variable | Purpose | Required |
|---|---|---|
| `GEMINI_API_KEY` | Server-side Gemini API key | Only for AI responses |
| `GEMINI_MODEL` | Gemini model identifier | No; configured default |
| `AQI_PROVIDER` | Selected AQI provider adapter | No |
| `OPENAQ_API_KEY` | OpenAQ credential, if required by current API access | Provider-dependent |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins | No; local default |
| `VITE_API_BASE_URL` | Public backend base URL | No; local default |

Do not put secrets in frontend variables (for example, `VITE_*` variables), because browser-exposed values are public.

## Data sources and interpretation

- [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api) — modeled current air-quality variables and AQI indices.
- [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api) — city-name lookup.
- [CPCB National AQI methodology](https://airquality.cpcb.gov.in/ccr_docs/About_AQI.pdf) — reference for India's AQI categories, pollutant breakpoints, and sub-index method.

BreatheWise must not relabel a US or European AQI index as CPCB AQI. An official Indian AQI implementation requires compatible pollutant measurements, averaging periods, valid sub-indices, and source attribution.

## Development roadmap

- [x] Create public repository and starter monorepo.
- [x] Add FastAPI health endpoint and React/Vite application shell.
- [x] Add city search and Open-Meteo modeled air-quality API.
- [x] Show pollutant readings, timestamp, source, and AQI-scale caveat.
- [x] Document architecture, privacy, and safety boundaries.
- [ ] Add tests for provider failures and API response validation.
- [ ] Integrate validated CPCB station measurements.
- [ ] Add Gemini assistant with grounded prompts, safety constraints, and graceful fallback.
- [ ] Add household profile and personalized routine planner.
- [ ] Add indoor-air guidance and clean-commute comparison.
- [ ] Add transparent emissions-impact calculations.
- [ ] Add tests, accessibility checks, and deployment configuration.
- [ ] Record a demo and document the deployed build.

## Contributing

Issues and pull requests are welcome. Keep changes focused, add tests for behavior changes, and never commit credentials or personal data.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
