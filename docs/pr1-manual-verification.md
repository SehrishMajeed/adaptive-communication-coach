# PR 1 manual verification log

Status: partially verified on 2026-09-14. This is not a completed manual acceptance because live Gemini credentials and controllable computer-use browser access were unavailable.

## Environment

- OS shell: Windows PowerShell
- Python: 3.14.4
- Node: 26.4.0
- npm: 11.17.0
- Backend: `uvicorn app.main:app` on `127.0.0.1:8000`
- Frontend: Vite dev server on `127.0.0.1:5173`

## Passed automated checks

- `python -m pytest tests/ -q`: 78 passed, 1 Google GenAI deprecation warning.
- `npm run typecheck`: passed.
- `npm test`: 5 files passed, 21 tests passed.
- `npm run build`: passed.

## Passed live local checks

- Backend OpenAPI responded at `http://127.0.0.1:8000/openapi.json`.
- Frontend dev server responded at `http://127.0.0.1:5173`.
- A real multipart request to `/api/sessions/latest/attempts` with fields `audio` as `audio/wav` and `duration_seconds=5` reached the backend.
- With no Gemini API key configured, the API returned safe error JSON:
  - HTTP status: `502`
  - code: `evaluation_failed`
  - message: `The audio could not be evaluated. You can retry this recording.`
- After that failed provider path, local SQLite contained zero `coaching_sessions`, zero `coaching_attempts`, and zero `user_profiles`.

## Blocked checks

- Live Gemini success path was not verified because `backend/.env` was absent and no `GEMINI_API_KEY` / `GOOGLE_API_KEY` was configured.
- Real camera/microphone browser recording was not verified because the computer-use browser interface was unavailable:
  - `iab` browser was not available.
  - Browser discovery repeatedly failed with `Unable to load browser request-header policy`.
- Browser Network-tab confirmation that no video payload is uploaded still requires manual browser verification.
- Real-device compatibility across Chrome/Safari/Firefox remains unverified.

## Remaining manual checklist

1. Create `backend/.env` from `.env.example` and set a valid backend-only Gemini key.
2. Start backend and frontend locally.
3. Open the frontend in a real browser at `http://localhost:5173` or `http://127.0.0.1:5173`, using one hostname consistently.
4. Allow camera and microphone permissions.
5. Record at least five seconds and stop manually.
6. Confirm full replay, muted replay, and audio-only playback work.
7. Click `Get AI Feedback`.
8. In browser Network tools, confirm multipart fields contain only:
   - `audio` with `Content-Type: audio/wav`
   - `duration_seconds`
9. Confirm no video field or video payload is uploaded.
10. Confirm transcript, four rubric labels, duration, and counts render with a valid key.
11. Record again and let automatic stop run at 60 seconds.
12. Confirm a single transition to review and released camera/microphone indicators.
13. Deny permissions and confirm recovery UI.
14. Stop backend, request feedback, and confirm the recording remains reviewable and retryable.
15. Check the database after successful submissions: each successful submission has its own storage session, attempt number `1`, and no learner profile mutation.

## Gate

Phase 2 implementation must not start until the remaining live browser/Gemini checklist is completed.

