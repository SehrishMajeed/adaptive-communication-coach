# Aura Coach Android Client

This React Native client implements the focused practice loop: setup, record locally, review privately, receive one evidence-backed target, retry and compare. It uses the same backend contract as the web prototype.

## Product Scope

The Android app is intentionally narrow:

- Practice one technical project explanation for a recruiter or nontechnical listener.
- Keep video replay local to the device.
- Upload only the extracted mono PCM16 WAV audio track to the backend.
- Show AI feedback only when the backend returns validated, evidence-grounded output.
- Keep retry comparison backend-owned instead of relying on frontend memory.

Do not present this client as Play Store production-ready until real-device recording, release signing, privacy disclosures and staged rollout are verified.

For the full internal-test release checklist, signed AAB receipt and Play Store draft copy, see [Release readiness pack](../docs/release-readiness-pack.md).

## Local Setup

Install the React Native Android environment from the official guide, including:

- Node.js compatible with the root CI configuration.
- JDK 17.
- Android Studio with Android SDK, platform tools and an Android API level supported by the project.

Then install dependencies from this directory:

```sh
npm ci
```

## Development

Start Metro:

```sh
npm start
```

Run on an Android emulator or connected Android device:

```sh
npm run android
```

Use the backend API configured for your local or staging environment. Do not put Gemini/provider secrets in the mobile app.

For a physical Android device, keep the backend on the host and reverse port `8000` before launching the app:

```sh
adb reverse tcp:8000 tcp:8000
```

The dev client uses `http://localhost:8000`, which works with `adb reverse` on a real device.

## Quality Checks

Run these before committing mobile changes:

```sh
npm run typecheck
npm run lint
npm test
```

These checks validate TypeScript, lint rules and React Native rendering/navigation boundaries. They do not replace real-device camera, microphone or upload testing.

## Android Audio Extraction

The review flow uses a small Android native bridge to decode the local recording's audio track and write a mono PCM16 WAV file in app cache before upload. The backend rejects video files and non-WAV audio, so the client must upload that extracted WAV rather than the local MP4/MOV recording.

Real-device verification must confirm the extracted file passes backend media validation and that the video file itself is not sent.

## Android Debug Build

React Native native modules can exceed Windows CMake path limits when this repo lives under a long OneDrive path. For local Android verification on Windows, use a short working path and build a focused ARM64 debug APK:

```sh
gradlew.bat :app:assembleDebug --no-daemon --max-workers=1 -PreactNativeArchitectures=arm64-v8a
```

The most recent verified receipt was produced from a fresh short-path checkout using the command above. Full multi-ABI and signed release builds remain separate release gates.

## Release Signing

Release signing is intentionally not configured with the debug keystore. A release build requires these environment variables, supplied by a secret manager or a secure local shell:

- `AURACOACH_RELEASE_STORE_FILE`
- `AURACOACH_RELEASE_STORE_PASSWORD`
- `AURACOACH_RELEASE_KEY_ALIAS`
- `AURACOACH_RELEASE_KEY_PASSWORD`

Never commit `.keystore` or `.jks` files. The root `.gitignore` blocks those files, but secret handling still depends on local and CI discipline.

Build a signed release AAB only after those variables are set:

```sh
cd android
./gradlew :app:bundleRelease --no-daemon --max-workers=1
```

## Unverified Release Gates

The following are not complete yet:

- Real-device record -> review -> upload -> feedback flow.
- Live Gemini behavior with approved backend credentials.
- Signed release APK/AAB.
- Play Console internal track setup.
- Privacy policy, Data safety form and staged rollout.
