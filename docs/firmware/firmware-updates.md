# Even.app Firmware Updates - API Session, Token, and CDN Build Retrieval

Date: 2026-03-04  
Primary evidence window: 2026-03-03 API matrix waves + MITM/WireGuard captures

## 1) Executive Summary

The firmware retrieval pipeline is reproducible:

1. Build a valid `common` header (including `openUdid` and `ts`).
2. Optionally supply a `sign` header for compatibility (currently not required on tested routes).
3. Create or refresh a session by calling `POST /v2/g/login` to mint a fresh JWT `token`.
4. Query `GET /v2/g/check_latest_firmware`.
5. Download from CDN `https://cdn.evenreal.co{subPath}` (no CDN auth required).

As of live checks on `2026-03-04`, `sign` is not required for tested firmware/login endpoints (missing/random `sign` still returns `code: 0` with valid token/common).

`/v2/g/check_firmware` remains unresolved for code `0` despite extensive parameter/contract sweeps; it consistently returns `1401` (`Params error`) under all tested key families.

## 2) Observed Header and Token Generation Model

### Required headers for firmware metadata endpoints

- `sign`: Optional in currently tested flows; value can still be supplied for compatibility.
- `token`: JWT from `/v2/g/login`.
- `common`: URL-encoded device/app envelope.
- `region`: Usually `US`.
- `request-id`: UUID per request.

### `token` generation and lifecycle

- Minted by: `POST /v2/g/login`.
- JWT algorithm: `HS256`.
- Claims observed: `UUID`, `ID`, `Username`, `AuthorityId`, `AppId`, `BufferTime`, `iss`, `aud`, `nbf`, `exp`.
- TTL observed: `exp - nbf = 604800` seconds (`7.0` days).
- Expired tokens return `401` (`Your login session has expired`).

### `request-id` generation

- UUID-style value generated per request.
- Observed format matches UUID v4-style patterns in traffic.
- Reuse is unnecessary; generate a new one each request.

### `common` generation

`common` is a URL-encoded K/V envelope. Typical keys:

- `platform`, `package`, `versionName`, `build`
- `brand`, `model`, `osVersion`, `carrier`, `mcc`, `mnc`
- `buildTime`, `appId`, `v`, `os`, `channel`
- `openUdid`, `ts`, `language`, `sysLanguage`, `sttLanguage`
- `tzName`, `dateFmt`, `timeFmt`, `unit`, `region`

Dynamic fields:

- `openUdid`: terminal identifier (UUID-like string).
- `ts`: UTC timestamp (ISO-8601).
- `versionName`: controls build-family selection returned by `check_latest_firmware`.

### `openUdid` and terminal ID behavior

- `openUdid` appears in `common` and in `list_devices.data.terminals[*].openUdid`.
- Logging in with a newly generated `openUdid` can create a new terminal record (new terminal `id`) visible via `/v2/g/list_devices`.
- This gives a practical path to creating fresh session/device context without reusing old terminal IDs.

## 3) Login Session Bootstrap Contract

### Endpoint

`POST https://api2.evenreal.co/v2/g/login`

### Body

```json
{
  "email": "<account email>",
  "passwd": "<Even.app API value>"
}
```

`passwd` notes:

- Captures show the app sending an encoded value (example shape: Base64-like, 24 chars).
- Tooling supports:
  - direct API value via `--login-passwd-b64` (recommended), or
  - plain account password via `--login-passwd-plain` (raw passthrough), or
  - inferred transform via `--login-passwd-plain` fallback -> `base64(raw_md5(password))`.
- 2026-03-04 validation with `i@am.guru`:
  - raw password passthrough succeeded (`code: 0`, fresh JWT minted),
  - inferred `base64(raw_md5(password))` failed (`code: 1102`, `Email or password is error`).
- Conclusion: password encoding is not universally one-shape; use raw-first with fallback.

### Headers for login

- `sign` (optional in current behavior; accepted when absent)
- `common` (required)
- `request-id` (auto-generated if missing)
- `region` (recommended, typically `US`)
- `content-type: application/json;charset=utf-8`
- `user-agent: iPhone Safari-style UA` (tool default matches capture profile)

## 4) Firmware Build Discovery via `common.versionName`

`GET /v2/g/check_latest_firmware` returns different G2 packages based on `common.versionName`.

Observed thresholds:

| Request `common.versionName` | Returned firmware | `minAppVer` | CDN `subPath` |
|---|---|---|---|
| `0.0.1` to `2.0.2` | `2.0.1.14` | `0.0.0` | `/firmware/09fe9c0df7b14385c023bc35a364b3a9.bin` |
| `2.0.3` to `2.0.4` | `2.0.3.20` | `2.0.3` | `/firmware/57201a6e7cd6dadeee1bdb8f6ed98606.bin` |
| `2.0.5` | `2.0.5.12` | `2.0.5` | `/firmware/53486f03b825cb22d13e769187b46656.bin` |
| `2.0.6` | `2.0.6.14` | `2.0.6` | `/firmware/0c9f9ca58785547278a5103bc6ae7a09.bin` |
| `2.0.7+` | `2.0.7.16` | `2.0.7` | `/firmware/650176717d1f30ef684e5f812500903c.bin` |

## 5) `check_latest_firmware` vs `check_firmware`

### `GET /v2/g/check_latest_firmware`

- Stable success path (`code: 0`) with fresh `token` + valid `common`; `sign` is currently not enforced in tested probes.
- Primary endpoint for available firmware metadata and CDN path retrieval.

### `GET /v2/g/check_firmware`

- Exhaustive sweeps (snake_case, camelCase, mixed aliases, serial transforms, bind/onboard state, host variants, method/transport variants) produced no `code: 0`.
- Dominant response: `code: 1401` (`Params error`).
- POST route typically `404`.
- Forcing `v=2` variants yielded `406` (`Invalid signature`) in wave 22 cases.

## 6) CDN Retrieval Contract

Download URL:

`https://cdn.evenreal.co{subPath}`

Key points:

- CDN download requires no additional auth headers.
- `fileSign` from API metadata equals the firmware file MD5 (and filename stem).
- Verify integrity with MD5 after download.

## 7) Tooling: `tools/fetch_latest_firmware.py`

The script now supports:

- login-based session creation (`/v2/g/login`) to mint fresh JWT tokens
- raw-first plain-password login with fallback (`--login-passwd-plain`, `--login-passwd-plain-mode`)
- operation with no captured `sign` (warning-only if `sign` is absent)
- `request-id` auto-generation
- `openUdid` control (`--openudid` or `--new-openudid`)
- `common.versionName` override (`--version-name`) for build-family discovery
- build enumeration (`--enumerate-builds`, `--probe-version-names`)
- bulk download of all unique discovered builds (`--download-all-discovered`)
- versioned storage layout (`--store-by-version-dir`) at `captures/firmware/g2/<version>/`
- optional auth/session export (`--save-auth-file`)
- sign reverse diagnostics from extracted app binary (`--sign-reverse-report`)
- capture-driven sign hypothesis checks (`--sign-capture-file`)
- Mach-O sign-reverse context output (`__TEXT` mapping + `cryptid`)

### Example: fresh session + latest firmware query

```bash
python3 tools/fetch_latest_firmware.py \
  --login-email 'user@example.com' \
  --login-passwd-plain '<account-password>' \
  --refresh-common-ts \
  --query-only
```

### Example: generate new `openUdid` and persist refreshed auth headers

```bash
python3 tools/fetch_latest_firmware.py \
  --login-email 'user@example.com' \
  --login-passwd-plain '<account-password>' \
  --new-openudid \
  --refresh-common-ts \
  --save-auth-file captures/even_auth_refreshed.json \
  --query-only
```

### Example: query older build family (2.0.5 line)

```bash
python3 tools/fetch_latest_firmware.py \
  --login-email 'user@example.com' \
  --login-passwd-plain '<account-password>' \
  --version-name 2.0.5 \
  --refresh-common-ts \
  --query-only
```

### Example: enumerate and download all currently discoverable G2 builds

```bash
python3 tools/fetch_latest_firmware.py \
  --login-email 'user@example.com' \
  --login-passwd-plain '<account-password>' \
  --refresh-common-ts \
  --enumerate-builds \
  --download-all-discovered \
  --store-by-version-dir \
  --output-json captures/firmware/g2/build-enumeration-YYYY-MM-DD.json
```

### Example: full pull + extract

```bash
python3 tools/fetch_latest_firmware.py \
  --login-email 'user@example.com' \
  --login-passwd-plain '<account-password>' \
  --refresh-common-ts \
  --extract
```

### Example: inspect local `App.framework/App` for sign reverse markers

```bash
python3 tools/fetch_latest_firmware.py --sign-reverse-report
```

### Example: run sign reverse report with capture hypothesis checks

```bash
python3 tools/fetch_latest_firmware.py \
  --sign-reverse-report \
  --app-framework-binary captures/firmware/Even.app/Wrapper/Runner.app/Frameworks/App.framework/App \
  --sign-capture-file captures/even_api_capture_1772533143.json
```

## 8) iOS SDK Firmware Pipeline (`EvenG2Shortcuts`)

The iOS app implements the full firmware lifecycle — from API query through EVENOTA parsing to BLE transfer:

### 8.1) Source Files

| File | Purpose |
|------|---------|
| `G2FirmwareAPIClient.swift` | API auth (login, JWT), firmware check, CDN download with MD5 |
| `G2FirmwareModels.swift` | Response models, version comparison, `LatestFirmwareAPIResponse` |
| `G2EVENOTAParser.swift` | Binary parser: EVENOTA header, TOC, sub-headers, CRC32C validation |
| `G2FirmwareTransferClient.swift` | Multi-segment BLE transfer orchestrator (FILE_CHECK→START→DATA→END) |
| `G2FileTransferClient.swift` | Generic file transfer protocol (reused for notifications + firmware) |
| `FirmwareCheckView.swift` | Full firmware management UI: check, download, inspect, transfer |

### 8.2) API Authentication

- Login: `POST /v2/g/login` with email + password (raw-first mode with MD5+B64 fallback)
- Token: JWT (HS256, 7-day TTL), stored in session for subsequent requests
- Common header: URL-encoded device envelope (`openUdid`, `ts`, `versionName`, etc.)
- Sign: Optional header (not currently enforced server-side)

### 8.3) Firmware Check & Download

- `checkLatestFirmware()`: Queries `GET /v2/g/check_latest_firmware`, decodes `LatestFirmwareAPIResponse`
- Response wrapping: `{"code": 0, "data": {...}}` with version, subPath, fileSign, fileSize
- `downloadFirmware(subPath:expectedMD5:expectedSize:progress:)`: Streams from CDN via `URLSession`
- MD5 verification: `CryptoKit.Insecure.MD5` against API `fileSign`
- Version comparison: `G2FirmwareVersion` supports `>` operator for upgrade detection

### 8.4) EVENOTA Parsing

- Validates `EVENOTA\0` magic at offset 0
- Parses 160-byte container header (entry count, build date/time, version string)
- Reads TOC (N × 16 bytes): entry ID, offset, size, CRC32C checksum
- Extracts 128-byte sub-headers per entry: payload size, checksum echo, type, filename
- Validates each payload CRC32C via `G2CRC.crc32c()` (from `G2Protocol.swift`)
- Returns `G2EVENOTAPackage` with typed `G2EVENOTAEntry` array (6 components)
- Component types: `mainApp(0)`, `bootloader(1)`, `touch(3)`, `codec(4)`, `ble(5)`, `box(6)`

### 8.5) BLE Transfer

- Segments firmware into ≤255 chunks per segment (234 bytes/chunk)
- Per segment: FILE_CHECK → START → DATA[×N] → END cycle with unique sequence
- Monitors ACKs via `onFileTransferAck` (2-byte LE status words)
- Progress reporting: `G2FirmwareTransferProgress` (phase, bytesTransferred, totalBytes)
- Phases: downloading → validating → transferring → verifying → complete
- Prerequisites: device connected, battery ≥50%, on charger

### 8.6) Firmware Management UI

State machine in `FirmwareCheckView`:
```
idle → checking → updateAvailable → downloading → downloaded →
  parsing → parsed → [transferring → transferred → complete]
```

UI sections: API credentials, firmware check results, download progress with MD5 status, EVENOTA package inspector (component list with CRC validation), transfer controls with safety confirmation

## 9) Currently Archived G2 Builds (2026-03-04 Sweep)

Enumerated with `--enumerate-builds` and downloaded with `--download-all-discovered --store-by-version-dir`:

- `2.0.1.14` -> `captures/firmware/g2/2.0.1.14/09fe9c0df7b14385c023bc35a364b3a9.bin`
- `2.0.3.20` -> `captures/firmware/g2/2.0.3.20/57201a6e7cd6dadeee1bdb8f6ed98606.bin`
- `2.0.5.12` -> `captures/firmware/g2/2.0.5.12/53486f03b825cb22d13e769187b46656.bin`
- `2.0.6.14` -> `captures/firmware/g2/2.0.6.14/0c9f9ca58785547278a5103bc6ae7a09.bin`
- `2.0.7.16` -> `captures/firmware/g2/2.0.7.16/650176717d1f30ef684e5f812500903c.bin`

Enumeration artifact:

- `captures/firmware/g2/build-enumeration-2026-03-04.json`

## 10) Evidence Artifacts

Session/token/header behavior:

- `captures/even_api_capture_1772533143.json`
- `captures/firmware/analysis/2026-03-03-api-wave9-openudid-common-matrix.json`
- `captures/firmware/analysis/2026-03-03-api-wave9-openudid-token-aligned-matrix.json`
- `captures/firmware/analysis/2026-03-03-api-wave9-openudid-token-listcommon-matrix.json`
- `captures/firmware/analysis/2026-03-03-api-wave17-check-firmware-reauth-matrix.json`
- `captures/firmware/analysis/2026-03-03-api-wave19-stateful-host-sequence.json`
- `captures/firmware/analysis/2026-03-03-api-wave22-onboard-stateful-matrix.json`
- `captures/firmware/analysis/2026-03-03-api-wave24-canonical-key-check-firmware-matrix.json`
- `captures/firmware/analysis/2026-03-03-api-wave31-key-mined-check-firmware-matrix.json`
- `captures/firmware/analysis/2026-03-03-api-wave32-terminal-method-contract-sweep.json`
- `captures/firmware/analysis/2026-03-03-sign-enforcement-matrix.json`

Build threshold mapping:

- `captures/firmware/analysis/2026-03-03-api-wave6-threshold-sweep.json`
- `captures/firmware/analysis/2026-03-03-g2-extracted-wave.md`

No successful `/check_firmware` evidence:

- `captures/firmware/analysis/2026-03-03-api-wave20-check-firmware-evidence-scan.json`
- `captures/firmware/analysis/2026-03-03-api-wave30-corpuswide-check-firmware-evidence-scan.json`

Tagged artifact inventory:

- `captures/firmware/analysis/2026-03-05-tagged-firmware-artifacts.md`
- `captures/firmware/analysis/2026-03-05-tagged-firmware-artifacts.json`

## 11) Known Unknowns

- The exact `sign` algorithm and key derivation remain unreversed.
- `sign` is currently non-blocking for tested firmware/login routes, but may be re-enforced server-side in the future.
- `check_firmware` success contract is still unknown despite broad parameter/state coverage.
- Password handling likely has multiple valid formats depending on account/server contract; raw-pass and transformed-pass behavior can differ by account/session.

## 12) 2026-03-04 Live Login + Download Revalidation

Run executed at `2026-03-04T01:33Z` using `tools/fetch_latest_firmware.py`:

- `/v2/g/login` succeeded with raw password mode (`code: 0`), minting a fresh JWT.
- JWT validity observed: `nbf=2026-03-04T01:33:23Z`, `exp=2026-03-11T01:33:23Z` (7 days).
- `/v2/g/check_latest_firmware` returned `G2 2.0.7.16` with `fileSign=650176717d1f30ef684e5f812500903c`.
- CDN download succeeded and MD5 matched:
  - `captures/firmware/recheck-login-download/g2/2.0.7.16/650176717d1f30ef684e5f812500903c.bin`

This confirms the current end-to-end workflow (fresh login session + firmware fetch) is still valid.

## 12.1) 2026-03-04 Dynamic `sign` Enforcement Probe

Artifact: `captures/firmware/analysis/2026-03-03-sign-enforcement-matrix.json`

Probe summary:

- `POST /v2/g/login`: `captured`, `random`, `tampered`, and `missing` `sign` all returned `code: 0`.
- `GET /v2/g/check_latest_firmware`, `/v2/g/list_devices`, `/v2/g/check_app`, `/v2/g/health/get_latest_data?metric_type=sleep&v=2`:
  - all four `sign` variants returned the same success code as long as token/common were valid.
- Token enforcement remains active:
  - removing or corrupting `token` yields `code: 401` (`Your login session has expired`).
- `/v2/g/check_firmware` behavior remained `code: 1401` (`Params error`) independent of `sign` variant.

Conclusion:

- For currently tested routes, `sign` is not server-enforced.
- `token` + `common` drive access control and firmware-query behavior.

## 12.2) Static App Triage (No DRM Circumvention)

Static observations from local App Store install at `/Applications/Even.app/Wrapper/Runner.app`:

- Entitlements (`codesign -d --entitlements :-`) include:
  - `application-identifier = JVW78TTXUJ.com.even.sg`
  - `com.apple.developer.team-identifier = JVW78TTXUJ`
- `embedded.mobileprovision` is absent (expected for App Store delivery).
- `Info.plist` highlights:
  - `CFBundleIdentifier = com.even.sg`
  - `ITSDRMScheme = v2`
  - `CFBundleSupportedPlatforms = [iPhoneOS]`
  - `NSAppTransportSecurity.NSAllowsArbitraryLoads = true`
- Linked runtime dependencies (`otool -L Runner`) include:
  - `@rpath/even_core.framework/even_core`
  - `@rpath/even.framework/even`
  - `@rpath/Flutter.framework/Flutter`
  - multiple networking/feature frameworks (Mapbox, Speech, Bluetooth-related stacks)
- Signing-related strings and interceptors are present in `App.framework/App` as detailed in section 13.

## 12.3) 2026-03-05 G2-Case + R1-Ring Discovery Recheck

Fresh live checks were repeated on `2026-03-05` to determine whether the case image or ring image can be fetched as first-class firmware artifacts, rather than only as components/bundles already in the repo.

- `POST /v2/g/login` still succeeded and minted a fresh JWT.
- `GET /v2/g/check_latest_firmware` returned the same `G2 2.0.7.16` EVENOTA package even when probed with `device_type` aliases such as `g2`, `G2`, `r1`, `R1`, `g1`, and `G1`.
- `GET /v2/g/check_firmware` remained unresolved (`code: 1401`, `Params error`) for ring-oriented parameter sweeps.
- `GET /v2/g/check_bind2` and `GET /v2/g/check_firmware2` returned HTTP `404`.

Result:

- No separate `G2-Case` CDN artifact was exposed by the API. The case image remains the `firmware/box.bin` component embedded inside each downloaded G2 EVENOTA package.
- No separate `R1-Ring` runtime image was exposed by the currently working firmware endpoints. The ring-tagged artifacts currently available in the repo are the Even.app-bundled Nordic DFU bundles (`B210_ALWAY_BL_DFU_NO`, `B210_BL_DFU_NO_v2.0.3.0004`, `B210_SD_ONLY_NO_v2.0.3.0004`).

To make those artifacts explicit, tagged local copies were materialized at:

- `captures/firmware/tagged/g2-case/<version>/firmware_box.bin`
- `captures/firmware/tagged/r1-ring/failsafe-bootloader/`
- `captures/firmware/tagged/r1-ring/bootloader-2.0.3.0004/`
- `captures/firmware/tagged/r1-ring/softdevice-2.0.3.0004/`

Inventory + provenance:

- `captures/firmware/analysis/2026-03-05-tagged-firmware-artifacts.md`
- `captures/firmware/analysis/2026-03-05-tagged-firmware-artifacts.json`

## 13) `sign` Reverse Status and Required Next Work

Latest static + capture-assisted report (run via `--sign-reverse-report`):

- Binary: `captures/firmware/Even.app/Wrapper/Runner.app/Frameworks/App.framework/App`
- Marker coverage: `13/13` configured sign markers found, including:
  - `package:even_core/network/utils/signature_util.dart`
  - `SignatureUtil`
  - `calculateSignature`
  - `requestInterceptorWrapper`
  - `commonRequestHeader`
  - `AuthInterceptor`
  - `_signPrefix` and `_signSuffix`
  - `impl.mac.hmac` and `impl.digest.sha256`
- Mach-O context for `App.framework/App`:
  - `magic=0xfeedfacf`, `ncmds=17`
  - `__TEXT vmaddr=0x0`, `fileoff=0` (marker offsets map directly in this segment)
  - `cryptid=0` (binary is not FairPlay-encrypted)
- Capture analysis (`captures/even_api_capture_1772533143.json`):
  - signed requests: `93/93`
  - unique sign values: `93` (`0` reused)
  - sign length set: `[44]` (Base64 length consistent with 32-byte digest/HMAC output)
  - hypothesis checks run by tool:
    - unkeyed formulas tested: `225`
    - HMAC formulas tested: `490`
    - full matches: `0`

Interpretation:

- `sign` construction almost certainly lives in Dart AOT code in `App.framework/App`.
- The signing path likely uses hidden constant/key material and/or a canonicalization path not present in simple request-field formulas.
- Dynamic API probes show `sign` is currently optional for tested firmware/login routes.
- Reverse work is now risk-reduction/future-proofing rather than a blocker for firmware retrieval.

Recommended reverse sequence:

1. Recover string table/constant pool references around `_signPrefix` and `_signSuffix` in AOT data.
2. Map `requestInterceptorWrapper` -> `AuthInterceptor` callsites to exact sign input assembly.
3. Re-implement the recovered canonicalization + key usage in Python and diff against captures.
4. Keep optional support for computed `sign` ready in case server-side enforcement is re-enabled.

## 14) Simulator/Resign Feasibility Constraints

Latest local feasibility checks (`2026-03-03`):

- `Runner` executable is `Mach-O 64-bit arm64` (`iPhoneOS` app binary, not a macOS executable).
- Ad-hoc re-sign succeeds (`codesign --force --deep --sign -`), but local macOS launch fails:
  - `open -n Runner.app` -> `The application cannot be opened because it has an incorrect executable format.`
- Simulator install can succeed (`simctl install`), but launch fails:
  - `FBSOpenApplicationServiceErrorDomain code=1`
  - underlying `NSPOSIXErrorDomain code=153` (`Launchd job spawn failed`)

Practical alternatives:

- Continue static reverse on extracted `App.framework/App` (this doc + `--sign-reverse-report` workflow).
- If runtime hooks are required, run on real iOS hardware (jailbroken or instrumentation-friendly path).
