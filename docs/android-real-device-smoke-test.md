# Android Real-Device Smoke Test

Status: partially verified on 2026-09-17. Backend configuration and the live Gemini evaluation corpus passed locally, but the real-device Android smoke test is still blocked because no ADB-authorized Android device was connected. Do not describe the real-device smoke test as passed until the device checklist below is completed.

## Goal

Verify the narrow Android loop on a physical device:

```text
backend running -> device connected -> app installed -> record -> review -> upload audio -> feedback or honest provider error
```

## Attempted Receipt

Environment:

- Commit: `158a33a Prepare real-device Android smoke test` plus local verification changes for Gemini schema/model compatibility.
- Host OS: Windows 10.0.26200
- ADB path: `C:\Users\sehri\AppData\Local\Android\Sdk\platform-tools\adb.exe`
- ADB version: `1.0.41`, platform-tools `37.0.1-15733141`
- Backend Gemini key: configured locally in ignored `backend/.env`; secret value is not recorded.
- Live model: `gemini-3.6-flash`

Commands run:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" version
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" devices -l
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" reverse tcp:8000 tcp:8000
```

Observed output:

```text
Android Debug Bridge version 1.0.41
Version 37.0.1-15733141
Installed as C:\Users\sehri\AppData\Local\Android\Sdk\platform-tools\adb.exe
Running on Windows 10.0.26200
List of devices attached

adb.exe: no devices/emulators found
adb reverse exit code: 1
```

Result:

- No physical Android device was attached or authorized.
- `adb reverse tcp:8000 tcp:8000` could not run because ADB had no device target.
- The backend contract was verified with FastAPI `TestClient`: `/openapi.json` returned `200`, `POST /api/practice-sessions` returned `200`, and a numeric `session_id` was present.
- Live Gemini corpus passed after updating the provider schema sanitizer, model default and synthetic speech fixture: `2` total, `2` passed, `0` failed.
- The real-device record -> review -> upload -> feedback path did not run and must not be claimed as passed.

## Latest Device Check

Second ADB check on commit `fcf4ade Verify live Gemini path and update Android smoke receipt`:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" kill-server
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" start-server
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" devices -l
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" reverse tcp:8000 tcp:8000
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" get-state
```

Observed output:

```text
List of devices attached

adb.exe: no devices/emulators found
adb reverse exit code: 1
error: no devices/emulators found
get-state exit code: 1
```

Windows present-device scan showed USB controllers/hubs but no Android, ADB, MTP, Pixel, Samsung, Xiaomi, OnePlus, Huawei, Motorola, Oppo, Vivo or Realme device. The device-side USB debugging authorization step remains incomplete.

## USB Driver Check

The Android SDK Google USB Driver package was downloaded locally:

```text
C:\Users\sehri\AppData\Local\Android\Sdk\extras\google\usb_driver\android_winusb.inf
```

Attempting to add it to the Windows driver store from the current shell failed because the shell is not elevated:

```text
Microsoft PnP Utility
Adding driver package: android_winusb.inf
Failed to add driver package: Access is denied.
Total driver packages: 1
Added driver packages: 0
pnputil exit code: 5
```

If Windows still does not detect the phone after trying a data-capable cable and another USB port, run PowerShell as Administrator and install the driver manually:

```powershell
pnputil /add-driver "$env:LOCALAPPDATA\Android\Sdk\extras\google\usb_driver\android_winusb.inf" /install
```

For Samsung, Xiaomi, OnePlus, Huawei, Motorola, Oppo, Vivo or Realme devices, prefer the official OEM USB driver if the Google driver does not bind to the device.

## Live Gemini Receipt

Command shape:

```powershell
python backend\scripts\evaluate_agent.py
```

Equivalent local run loaded `backend/.env` explicitly and wrote the report to `%TEMP%\auracoach-live-eval-report.md`.

Observed summary:

```text
Live evaluation status: passed
Live evaluation total: 2
Live evaluation passed: 2
Live evaluation failed: 0
```

Notes:

- `bad_audio_abstain` passed as an abstention or explicitly allowed safe provider-unavailable outcome.
- `good_technical_pitch` passed using committed synthetic speech audio.
- The Google SDK emitted a non-blocking warning recommending the Interactions API instead of direct AFC through `generate_content`.

## Required Setup

1. Connect a physical Android device over USB.
2. Enable Developer options and USB debugging.
3. Accept the RSA debugging prompt on the device.
4. Create `backend/.env` from `backend/.env.example` and set a backend-only `GEMINI_API_KEY`.
5. Start the backend from `backend/`.
6. Reverse the device port to the host backend:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" reverse tcp:8000 tcp:8000
```

The mobile app uses `http://localhost:8000` in dev so `adb reverse` works on a real Android device.

## Verification Commands

Use these exact commands from the repository root unless stated otherwise:

```powershell
git status --short --branch
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" devices -l
Push-Location backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
Pop-Location
Push-Location mobile
npm run android
Pop-Location
```

During the manual run:

1. Confirm the app opens on the physical device.
2. Confirm camera and microphone permission prompts appear and are understandable.
3. Record at least five seconds.
4. Stop manually and confirm review playback works.
5. Submit for feedback.
6. Confirm backend terminal receives `POST /api/practice-sessions` and `POST /api/practice-sessions/{session_id}/attempts`.
7. Confirm the response is either validated AI feedback or an honest provider/backend error.
8. Confirm video remains local and only the audio file is submitted.

## Pass Criteria

The smoke test passes only when the receipt records:

- device model and Android version from ADB;
- app install/run command result;
- backend startup receipt;
- backend request logs for session creation and attempt upload;
- screenshot or written observation for record, review and feedback/error states;
- exact final status: passed, failed with defect, or blocked.
