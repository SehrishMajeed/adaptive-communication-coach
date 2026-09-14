# Frontend

React/TypeScript and Vite provide capture, three local replay modes and validated feedback presentation. Use the [root setup instructions](../README.md#local-development).

Video stays local. A separate audio recording is converted to mono PCM16 WAV for analysis. Unsupported recording/decoding formats produce a recoverable error; the recording remains available for local review. The backend API URL is `VITE_API_BASE_URL` (default `http://localhost:8000`). Provider keys belong only in the backend environment.

Run `npm run typecheck`, `npm test` and `npm run build` from this directory. Tests use Vitest, Testing Library and jsdom; they do not replace real-device media checks. See the [manual checklist and limitations](../README.md#manual-verification).
