# Adaptive Communication Coach

**Prototype — not production-ready.** This project explores helping technical people explain complex ideas to different audiences through practice and review. The intended adaptive coaching loop is not implemented yet.

## Current implementation

React records camera and microphone and offers full, muted-video and audio-only replay. The frontend currently uploads the entire audiovisual recording to FastAPI. A small LangGraph workflow calls Gemini once for transcription and qualitative scores, calculates transcript metrics in Python, and optionally compares a previous attempt. SQLAlchemy stores attempts using SQLite by default or a configured PostgreSQL database.

The integration has known correctness failures:

- The feedback component expects fields the API does not return and can crash on a successful response.
- Duration is guessed from recording byte size, so WPM is unreliable.
- Filler counts are saved incorrectly, producing misleading comparisons.
- Every caller shares one demo user/session; profile updates are incomplete and do not drive personalized coaching.
- Recording automatic-stop and resource cleanup have lifecycle defects.
- The frontend production build and TypeScript check fail in the audited checkout.

There is no validated evidence-based diagnosis, verified improvement, automated body-language assessment, or reliable multi-user history. Muted video is a human self-review tool. See the [audit](docs/current-state-audit.md) for affected files, reproduced failures and the proposed first corrective PR.

## Intended direction

Practice a technical explanation for a specified audience and goal → review → measure → evaluate → choose one supported weakness → practice a targeted intervention → retry → compare → update eligible skill evidence.

This is a roadmap, not a claim about current behavior. The [documentation index](docs/README.md) links the product scope, target architecture, domain model, testing/evaluation strategies, roadmap and decision records.

## Local development

Use isolated local development only. The locked frontend tooling requires Node 20.19+ in the Node 20 series, or a compatible newer runtime. CI currently selects Python 3.10 and Node 20.x. Python dependencies are not locked, so setup is not yet fully reproducible.

Backend, from the repository root:

```sh
cd backend
python -m venv .venv
# Activate .venv with the command appropriate to your shell.
pip install -r requirements.txt
# Copy .env.example to .env and set GEMINI_API_KEY there.
uvicorn app.main:app --reload
```

Frontend, in another terminal from the repository root:

```sh
cd frontend
npm ci
npm run dev
```

The frontend uses `VITE_API_BASE_URL`, defaulting to `http://localhost:8000`. Keep `GEMINI_API_KEY` in the backend environment only. The backend accepts `DATABASE_URL` and `CORS_ORIGINS`; without a database URL it creates a local SQLite file. Starting these processes does not resolve the known recording, build or feedback failures.

## Verification status

The Phase 0 audit recorded **7 passing Python tests**: five database-configuration tests with mocked connections and two individual workflow-node tests. They do not cover the full HTTP/database/UI path or prove AI reliability. The frontend build failed on its Tailwind/PostCSS configuration; TypeScript reported JSX and Vite environment typing errors. No live model benchmark or deployed-system verification was performed.

Existing checks, from the repository root:

```sh
python -m pytest tests/
cd frontend
npx tsc --noEmit
npm run build
```

Pytest must be installed separately; CI currently installs it explicitly. The [testing strategy](docs/testing-strategy.md) describes the missing coverage. Future normal CI must remain free of paid model calls.

## Privacy and deployment limitations

Provider calls run on the backend, but currently receive the full audiovisual upload. Transcripts are persisted without a retention/deletion flow. There is no authentication or user isolation. Environment examples enable tracing; recording exclusion from traces and external provider retention have not been verified. Do not submit confidential recordings to this prototype.

Vercel configuration files exist for the frontend and backend. They are not proof of a successful deployment. Database migrations, production recovery procedures, ownership controls and release verification are not implemented. No production-readiness or guaranteed-latency claim is made.
