# Frontend

React/TypeScript and Vite provide recording, three local replay modes and feedback presentation. This remains a prototype with known recording, API-contract, build and type errors.

Use the [root setup instructions](../README.md#local-development). Run `npm ci` and `npm run dev` from this directory. `VITE_API_BASE_URL` points to FastAPI and defaults to `http://localhost:8000`; do not put a Gemini API key in frontend environment files.

The frontend currently uploads the complete audiovisual recording. Audio-only analysis with video kept local is planned, not implemented. See the [current-state audit](../docs/current-state-audit.md) for limitations and the first corrective PR.
