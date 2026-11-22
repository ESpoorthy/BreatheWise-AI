# BreatheWise AI 🌿

**Your intelligent companion for cleaner air and healthier everyday choices.**

BreatheWise AI is a GenAI-powered urban air-quality assistant designed to help families and communities understand local pollution, make safer day-to-day decisions, improve indoor air practices, and choose lower-emission alternatives.

> **Important:** BreatheWise AI provides general air-quality information and practical guidance. It is not a medical device, emergency service, or substitute for advice from a qualified healthcare professional or official public-health authority.

## What we're building

- **Air-quality intelligence:** location-aware AQI and pollutant readings with timestamps and source attribution.
- **Personalized daily planner:** recommendations shaped by outdoor conditions, commute, household needs, and preferences.
- **Indoor air guidance:** practical ventilation, cleaning, and filtration suggestions.
- **Cleaner commute choices:** compare practical travel alternatives and explain likely trade-offs.
- **Impact explorer:** transparent estimates of travel emissions avoided, with assumptions shown.
- **BreatheWise AI assistant:** conversational explanations grounded in available data and safety guidance.
- **Community view:** shareable, non-identifying local actions and preparedness tips.

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
| Styling | Custom responsive CSS; Tailwind may be introduced with the design system |
| Backend | Python, FastAPI |
| GenAI | Google Gemini API (server-side integration) |
| AQI data | Provider adapters; OpenAQ and official CPCB sources where available |
| Maps | Leaflet / OpenStreetMap (planned) |
| Database | Supabase (planned; not required for local MVP) |
| Deployment | Vercel (frontend) + Render (backend) |

Provider availability, API access, licensing, coverage, and rate limits will be verified before integration. This starter version does not claim a live data connection until an adapter is implemented and tested.

## Repository structure

```text
BreatheWise-AI/
├── frontend/                 # React + TypeScript + Vite
├── backend/
│   ├── app/
│   │   ├── api/               # HTTP routes
│   │   ├── core/              # Configuration and shared utilities
│   │   ├── schemas/            # Request/response models
│   │   └── services/           # AQI, Gemini, recommendations, impact
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

## API starter endpoints

- `GET /` — API identity and docs pointer.
- `GET /health` — service health check.

AQI, recommendations, impact, and chat endpoints will be added with validated data contracts and source metadata.

## Development roadmap

- [x] Create public repository and starter monorepo.
- [x] Add FastAPI health endpoint and React/Vite application shell.
- [x] Document architecture, privacy, and safety boundaries.
- [ ] Build the responsive dashboard and AQI data states.
- [ ] Implement and test AQI provider adapters with source attribution.
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
