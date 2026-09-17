# Release readiness pack

Status: internal-test readiness plan and receipt template. This is not a public launch claim. Real-device Android proof, signed release artifacts, deployed web smoke tests, privacy operations and Play Console review remain gates until completed and recorded here.

## Highest-leverage gate

The release package is only credible after a physical Android device completes:

```text
backend running -> adb reverse -> app installed -> setup -> record -> review -> upload audio -> feedback or honest provider error
```

Store assets, listing copy and Play Console forms should not be treated as release proof until that loop is verified.

## Current verified baseline

- Android target SDK is `36` in `mobile/android/build.gradle`.
- Release signing requires explicit `AURACOACH_RELEASE_*` environment variables and does not reuse the debug signing config when those variables are present.
- `.gitignore` excludes `.keystore` and `.jks` files.
- The mobile client uses `http://localhost:8000` in development and requires `adb reverse tcp:8000 tcp:8000` for physical-device testing.
- Android manifest declares `INTERNET`, `CAMERA` and `RECORD_AUDIO`.
- The mobile camera records video with audio enabled, then an Android native bridge extracts the audio track to a mono PCM16 WAV file in app cache before upload. Real-device proof is still required.
- A fresh short-path working copy with clean `npm ci` produced `C:\acc-fresh-232459\mobile\android\app\build\outputs\apk\debug\app-debug.apk` on 2026-09-17. Installation remains blocked until ADB sees an authorized phone.
- Direct `alembic.exe` can be blocked by Windows App Control on this machine; use `python -m alembic upgrade head`.

Install command once a phone appears in `adb devices -l`:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install -r "C:\acc-fresh-232459\mobile\android\app\build\outputs\apk\debug\app-debug.apk"
```

## Real-device Android smoke receipt

Before starting:

1. Connect an Android phone by USB.
2. Enable Developer options and USB debugging.
3. Accept the RSA debugging prompt on the device.
4. Configure `backend/.env` with backend-only `GEMINI_API_KEY`; never add provider keys to the mobile app.
5. Start the backend from `backend/`.
6. Start Metro from `mobile/`.

Commands:

```powershell
git status --short --branch
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" devices -l
Push-Location backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
Pop-Location
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" reverse tcp:8000 tcp:8000
Push-Location mobile
npm run android
Pop-Location
```

Receipt fields to fill:

| Field | Value |
| --- | --- |
| Date/time | TODO |
| Git commit/status | TODO |
| Host OS | TODO |
| Device model | TODO |
| Android version/API | TODO |
| ADB device ID | TODO |
| Backend base URL | `http://localhost:8000` through `adb reverse` |
| Gemini model | TODO |
| Final result | TODO: passed / failed with defect / blocked |

Latest local ADB check:

```text
List of devices attached
```

Result: blocked because no physical Android device or emulator is attached/authorized.

Required observations:

- Permission prompts appear for camera and microphone.
- Setup screen captures scenario, audience and goal.
- Recording runs for at least 5 seconds and can stop manually.
- Review playback works locally.
- Backend logs show `POST /api/practice-sessions`.
- Backend logs show `POST /api/practice-sessions/{session_id}/attempts`.
- Feedback renders, or a provider/backend failure is shown honestly while preserving the local review.
- A retry in the same session produces a backend-owned comparison when evidence is sufficient.
- No video field or video payload is uploaded.
- Feedback upload must use the extracted mono PCM16 WAV file, not the local video file.

Screenshot set:

1. setup/context screen;
2. Android permission prompt;
3. recording screen with timer;
4. review screen;
5. feedback screen with evidence/provenance or honest error;
6. retry/comparison state;
7. backend log excerpt with request paths and timestamps.

## Signed Android internal-test artifact

Create the release keystore outside the repository, for example under a private credential directory. Do not commit the keystore, passwords or generated signing reports.

```powershell
keytool -genkeypair `
  -v `
  -storetype PKCS12 `
  -keystore "$env:USERPROFILE\.auracoach\release\auracoach-upload.jks" `
  -alias auracoach-upload `
  -keyalg RSA `
  -keysize 2048 `
  -validity 10000
```

Set release-signing variables in the shell or CI secret manager:

```powershell
$env:AURACOACH_RELEASE_STORE_FILE="$env:USERPROFILE\.auracoach\release\auracoach-upload.jks"
$env:AURACOACH_RELEASE_STORE_PASSWORD="<secret>"
$env:AURACOACH_RELEASE_KEY_ALIAS="auracoach-upload"
$env:AURACOACH_RELEASE_KEY_PASSWORD="<secret>"
```

Build the internal-test AAB from a short path if Windows native module paths are too long:

```powershell
Push-Location mobile\android
.\gradlew.bat :app:bundleRelease --no-daemon --max-workers=1
Pop-Location
```

Release artifact receipt:

| Field | Value |
| --- | --- |
| Date/time | TODO |
| Git commit/status | TODO |
| Artifact path | `mobile/android/app/build/outputs/bundle/release/app-release.aab` |
| versionCode/versionName | `1` / `1.0` unless changed before build |
| targetSdkVersion | `36` |
| Signing source | `AURACOACH_RELEASE_*` variables |
| Debug keystore used? | TODO: must be no |
| Play Console upload result | TODO |

## Play Store listing draft

App name: AuraCoach

Short description:

> Practice a technical explanation, review privately, and get one evidence-backed AI coaching target.

Full description draft:

> AuraCoach helps technical people practice explaining a project to a recruiter or nontechnical listener. Record a short explanation, review it privately, send audio for AI feedback, receive one focused improvement target, then retry and compare the same task.
>
> The product is intentionally narrow. It does not score body language, infer emotions or claim verified learning outcomes. Video replay stays on your device for self-review. Audio is uploaded only when you request AI feedback.
>
> Current internal-test focus: validate recording, local replay, audio upload, evidence-grounded feedback and retry comparison on real Android devices.

Category: Education or Productivity. Choose Education if positioning as practice/learning; choose Productivity if positioning as interview-preparation workflow. Default for internal test: Education.

Permission rationale:

- Camera: records the user's practice explanation for local self-review.
- Microphone: records audio for local replay and optional AI feedback upload.
- Internet: creates practice sessions and sends audio to the backend when the user requests feedback.

Reviewer notes draft:

> This is an internal-test prototype for practicing technical communication. The main flow is setup -> record -> review -> get feedback -> retry. The app requires camera and microphone permissions. Video remains local to the device; the feedback request sends audio to the backend. The backend requires configured provider credentials in the test environment.

Blocked before public release:

- production privacy policy URL;
- support email;
- data deletion request URL/process;
- real-device verification of native Android audio extraction to backend-accepted mono PCM16 WAV;
- managed production backend/database;
- deployed smoke test;
- rate/cost limits;
- Play Console internal-test upload receipt;
- real-device smoke receipt.

## Data safety draft

Use this draft as an input to the Play Console Data safety form. Re-check against the exact deployed build before submission.

| Data type | Collected? | Shared? | Purpose | Notes |
| --- | --- | --- | --- | --- |
| Audio recordings | Yes, when user requests feedback | Yes, to AI provider through backend | App functionality: transcription/evaluation | Do not claim audio never touches external systems. |
| Video recordings | No backend collection by design | No | Local self-review | Verify multipart request has no video field before submitting. |
| Transcripts | Yes | May be derived by provider/backend | App functionality, feedback history | Persisted with attempts; deletion process is not implemented. |
| App interactions | Minimal backend request metadata | No known third-party analytics currently | App functionality/debugging | Do not add analytics without updating this draft. |
| Device/user identifiers | Anonymous owner token/device-scoped placeholder | No known external sharing | Session ownership | Not a full account system. |
| Crash logs | Not integrated yet | N/A | Future diagnostics | Safe logger exists, but external crash reporting is not configured. |

Security/privacy declarations should remain conservative:

- Data is transmitted over HTTPS only in release environments.
- Raw media is not stored in database columns, but multipart handling may spool temporary files.
- Transcripts/evaluations are persisted.
- User deletion/export is not implemented yet; mark as blocked for public release.

## Privacy policy draft

This draft needs legal/product review before public use.

> AuraCoach helps users practice technical explanations. The app records video and audio on the user's device. Video is used for local self-review and is not intentionally uploaded to AuraCoach servers. When the user requests AI feedback, the app uploads an audio file and related practice metadata, such as duration, scenario, audience and goal, to the AuraCoach backend.
>
> The backend may send audio and prompt content to an AI provider to generate a transcript, evidence-backed rubric feedback and a suggested practice target. AuraCoach stores practice-session metadata, transcript text, evaluation results, deterministic measurements and retry comparisons. AuraCoach does not currently provide account-based deletion, export or retention controls.
>
> Users should not submit confidential, private or sensitive project information during this prototype stage. Provider retention and processing are governed by the configured provider's terms and settings. AuraCoach does not sell personal data and does not currently use third-party advertising SDKs.

Required before public release:

- production contact email;
- hosted privacy policy URL;
- retention policy;
- deletion/export request process;
- provider/subprocessor disclosure;
- analytics/crash-reporting disclosure if added.

## Web readiness on Vercel

Existing config:

- `frontend/vercel.json` rewrites all routes to `index.html`.
- `backend/vercel.json` routes all backend requests to `api/index.py`.

Required environment variables:

Backend:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `GEMINI_TEMPERATURE`
- `DATABASE_URL`
- `CORS_ORIGINS`
- `DB_AUTO_CREATE=false` for release-like environments
- `LANGSMITH_TRACING=false` unless privacy-reviewed tracing is deliberately enabled

Frontend:

- `VITE_API_BASE_URL` pointing to the deployed backend URL.

Release commands:

```powershell
python -m pytest tests/
python -m backend.scripts.evaluate_agent
python -m alembic upgrade head
Push-Location frontend
npm run typecheck
npm test
npm run build
Pop-Location
Push-Location mobile
npm run typecheck
npm run lint
npm test
Pop-Location
```

Deployment smoke:

- `GET /openapi.json` returns `200` on backend.
- `POST /api/practice-sessions` creates a session with an owner token.
- Frontend can create a practice session against deployed backend.
- Browser Network tab confirms feedback upload sends `audio`, `duration_seconds` and `idempotency_key`, not video.
- Provider failure renders a recoverable error.

Production blockers:

- no managed database migration/rollback rehearsal;
- no backup/restore receipt;
- no global rate limits or cost limits;
- no retention/deletion process;
- no deployed live-provider reliability report;
- no public privacy/support URLs.

## Figma-ready visual handoff

Create a Figma file or provide an existing Figma file URL/key before executing canvas work. Use this structure:

1. Android real-device flow: six frames in order from setup to retry comparison.
2. Web flow: setup, record, review, feedback/history.
3. Play Store screenshot storyboard: four factual screenshots with short captions.
4. Data safety summary: audio uploaded, video local, transcript persisted, deletion blocked.
5. UX audit notes: strengths, visible issues, accessibility risks and evidence limits.

Recommended screenshot captions:

- Practice a technical explanation.
- Video stays on your device.
- Audio is sent only when you request AI feedback.
- Retry the same task and compare.

Use Canva only after the Figma board is approved, mainly for polished feature graphics or presentation exports. Use Lovable or Replit only for separate prototype/demo experiments, not as the source of truth for this repository.

## Lovable transfer status

The Lovable connector was attempted for a product-design companion workspace, but the app connection currently requires reauthentication. Use [Product and AI engineering alignment](product-ai-engineering-alignment.md) as the transfer-ready brief once Lovable access is restored.
