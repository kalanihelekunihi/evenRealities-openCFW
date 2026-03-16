# API Testing Plan For EvenG2Shortcuts

## Goal
Add repeatable automated tests for the cloud/API layer in `EvenG2Shortcuts`, starting with `G2FirmwareAPIClient` and its related models, without depending on live Even servers for the main test suite.

## Current State
- The app has a single application target in `project.yml`; there is no unit test target yet.
- API logic is concentrated in `Sources/EvenG2Shortcuts/G2FirmwareAPIClient.swift`.
- Model decoding for the cloud layer lives in `Sources/EvenG2Shortcuts/G2FirmwareModels.swift`.
- There is already an in-app manual/network test harness in `Sources/EvenG2Shortcuts/G2DebugLogger.swift`, but it is not suitable for CI because it depends on live network access, mutable server state, and sometimes a connected device.
- `G2FirmwareAPIClient` currently uses `URLSession.shared`, `UUID()`, `Date()`, and generated `common` headers directly, which makes request-level assertions harder than they need to be.

## Scope
- In scope:
  - Automated tests for request building, response decoding, error translation, auth-header behavior, and firmware download verification.
  - Project/test-target changes required to run those tests locally and in CI.
  - Small refactors that improve API testability without changing feature behavior.
- Out of scope for the first wave:
  - BLE protocol testing.
  - UI snapshot/UI flow testing.
  - Running mutating cloud calls against production by default.

## Test Strategy
1. Add a dedicated test target, preferably `EvenG2ShortcutsTests`, via `project.yml`, then regenerate/update the Xcode project.
2. Keep the default suite offline and deterministic by stubbing HTTP traffic.
3. Treat existing `G2DebugLogger` API checks as optional live smoke tests, not the primary verification path.
4. Cover pure request/model logic first, then transport/error behavior, then opt-in live validation.

## Phase 1: Build A Testable API Surface
- Extract a small transport seam from `G2FirmwareAPIClient`:
  - `G2HTTPClient` protocol or equivalent async wrapper for `data(for:)` and `bytes(for:)`.
  - Default implementation backed by `URLSession`.
- Isolate non-deterministic inputs:
  - `request-id` generation.
  - timestamp generation for `common`.
  - generated `openUdid`.
- Split request construction from request execution where it materially improves assertions:
  - request builders for login, latest firmware, settings, bind/unbind, update-set, and download.
- Keep public call sites stable where possible so the refactor does not ripple into UI code.

## Phase 2: Add Offline Unit Tests
- Create tests for request construction:
  - correct HTTP method, path, query items, headers, and JSON body.
  - authenticated vs unauthenticated routes.
  - `sn` vs `device_sn` field usage where the API is sensitive.
- Create tests for helper behavior:
  - `passwordValues(from:mode:)`.
  - `md5Base64(_:)`.
  - `buildCommonHeader(...)` field population and override rules.
  - `G2FirmwareVersionStatus.compare(device:latest:)`.
- Create tests for model decoding using stable fixtures:
  - `LatestFirmwareAPIResponse`.
  - `G2APIEnvelope<T>`.
  - `G2UserInfoData`, `G2UserPrefsRecord`, `G2UserSettingsRecord`.
  - `G2BindDeviceData` and update-set responses.

## Phase 3: Add Stubbed Integration Tests
- Use a custom `URLProtocol` or injected fake transport to simulate server responses.
- Verify end-to-end behavior for:
  - `checkLatestFirmwareFull`.
  - `loginAndCreateSession`, including raw-password then MD5+Base64 fallback on `code=1102`.
  - `checkLatestFirmwareAuthenticated`.
  - `listDevices`, including `matchedTerminalID` selection by `openUdid`.
  - `getUserInfo`, `getUserPrefs`, `getUserSettings`.
  - `bindDevice`, `unbindDevice`, `setOnBoarded`, `updateSet`.
- Verify error mapping for:
  - non-2xx HTTP responses.
  - API envelope failures (`code != 0`).
  - invalid/missing payload data.

## Phase 4: Cover Firmware Download Semantics
- Add deterministic tests around `downloadFirmware(...)`:
  - successful binary download.
  - expected size mismatch.
  - MD5 mismatch.
  - progress callback phase transitions.
- Store a small synthetic binary fixture in the test bundle instead of relying on a real multi-megabyte EVENOTA package.
- Keep parser/EVENOTA validation tests separate from transport tests so failures are easier to localize.

## Phase 5: Organize Fixtures
- Create a dedicated fixture folder under the new test target.
- Seed fixtures from already-known local examples instead of re-recording production traffic:
  - JSON samples already embedded in `G2DebugLogger.swift`.
  - sanitized captures from `captures/even_api_capture_*.json` and related auth/header logs where useful.
- Normalize fixtures so they are minimal, redacted, and named by endpoint/outcome:
  - `login_success.json`
  - `login_invalid_password.json`
  - `check_latest_firmware_success.json`
  - `user_settings_missing_sn.json`

## Phase 6: Add Opt-In Live Smoke Coverage
- Keep a small separate suite for live verification against real endpoints.
- Gate live tests behind environment variables for credentials and an explicit opt-in flag.
- Restrict the live suite to read-only or low-risk calls by default:
  - login
  - latest firmware
  - list devices
  - user info/prefs/settings
- Only run mutating endpoints (`bind`, `unbind`, `setOnBoarded`, `updateSet`) in explicitly targeted manual runs.

## CI / Tooling Changes
- Update `project.yml` with the new test target and its sources/resources.
- Regenerate or sync `EvenG2Shortcuts.xcodeproj` so the checked-in project matches `project.yml`.
- Add a CI step that runs the offline test suite on every change to API/model files.
- Keep live smoke tests out of the default CI lane.

## Coverage Priority
1. `checkLatestFirmwareFull` and shared request/error plumbing.
2. `loginAndCreateSession` and auth header generation.
3. `listDevices`, `getUserInfo`, `getUserPrefs`, `getUserSettings`.
4. `downloadFirmware`.
5. Mutating endpoints: `bindDevice`, `unbindDevice`, `setOnBoarded`, `updateSet`.

## Definition Of Done
- A test target exists and runs locally from Xcode and `xcodebuild test`.
- Core API behavior is covered by offline automated tests with no live network dependency.
- `G2FirmwareAPIClient` no longer relies exclusively on hard-coded global transport/state for testing.
- Fixtures are checked in, sanitized, and easy to extend.
- Live API checks remain available, but are clearly separated from deterministic automated tests.

## First Implementation Slice
- Add the test target and fixture folder.
- Introduce the transport seam and deterministic dependency injection points.
- Write tests for:
  - `checkLatestFirmwareFull` success + HTTP failure + API failure.
  - `loginAndCreateSession` success + password fallback.
  - `downloadFirmware` success + size mismatch + MD5 mismatch.
