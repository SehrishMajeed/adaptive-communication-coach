# Android Real-Device Smoke Test

Status: blocked on 2026-09-17 because no Android device was connected to ADB and no backend Gemini key was configured. This file is the exact verification receipt for the attempted run; do not describe the real-device smoke test as passed until the checklist below is completed.

## Goal

Verify the narrow Android loop on a physical device:

```text
backend running -> device connected -> app installed -> record -> review -> upload audio -> feedback or honest provider error
```

## Attempted Receipt

Environment:

- Commit: `73790cd Align public docs with verified Android milestone`
- Host OS: Windows 10.0.26200
- ADB path: `C:\Users\sehri\AppData\Local\Android\Sdk\platform-tools\adb.exe`
- ADB version: `1.0.41`, platform-tools `37.0.1-15733141`

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
- `backend/.env` was missing, so live Gemini evaluation could not be verified.
- The smoke test did not run and must not be claimed as passed.

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
