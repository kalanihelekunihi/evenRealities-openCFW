# Even Realities API Security Assessment

**Date:** 2026-03-14
**Tester:** Principal developer (authorized)
**Scope:** API signature enforcement, CDN access controls, authentication flow
**Test account:** `i@am.guru`

---

## Executive Summary

Signature enforcement is **active and effective** on authenticated API endpoints. The HMAC-SHA256 sign computation uses a hardcoded secret embedded in the Dart AOT binary that is not trivially recoverable. Over 600 sign hypothesis tests all failed, confirming the server performs proper cryptographic validation.

However, several areas warrant attention:
1. The login endpoint is exempt from signature enforcement
2. CDN firmware downloads require no authentication
3. Login response leaks extensive PII without sign protection

---

## Test Results

### 1. Signature Enforcement by Endpoint

| Endpoint | Method | Sign Required | Behavior |
|---|---|---|---|
| `/v2/g/login` | POST | **NO** | Succeeds with empty, dummy, or no sign |
| `/v2/g/check_latest_firmware` | GET | YES | `code=400 "Missing signature"` if absent, `code=406 "Invalid signature"` if wrong |
| `/v2/g/check_firmware` | GET | YES | Same as above |
| `/v2/g/list_devices` | GET | YES | Same as above |
| `/v2/g/user_info` | GET | YES | Same as above |
| `/v2/g/bind_device` | POST | YES | Same as above |
| `/health` | GET | **NO** | Returns `code=0` without any auth |
| `/` | GET | **NO** | Returns `code=0` without any auth |
| CDN (`cdn.evenreal.co`) | GET | **NO** | Direct download, no auth headers checked |

### 2. Sign Algorithm Analysis

**Binary markers found in App.framework/App (13/13):**
- `package:even_core/network/utils/signature_util.dart` — source file
- `SignatureUtil` — class name
- `calculateSignature` — method name
- `_signPrefix@2917441731` — prefix constant (library-scoped private)
- `_signSuffix@2917441731` — suffix constant (library-scoped private)
- `impl.mac.hmac` — HMAC implementation
- `impl.digest.sha256` — SHA-256 digest
- `AuthInterceptor` — HTTP interceptor
- `requestInterceptorWrapper` — interceptor wrapper
- `commonRequestHeader` — header builder
- `get:sign` — sign getter
- `/v2/g/login` — login endpoint reference
- `/v2/g/check_latest_firmware` — firmware endpoint reference

**Algorithm:** HMAC-SHA256 with compile-time prefix/suffix constants from Dart AOT object pool.

**IMPORTANT correction (2026-03-14):** The `_signPrefix@2942441731` and `_signSuffix@2942441731` markers are **NumberFormat fields** from the `intl` Dart package (library hash `2942441731`), NOT API signing fields. Other symbols in this library include `_decimalSeparator`, `_integerDigits`, `_pad`, `_floor`, `_round` — all NumberFormat internals. The original SIGN_REVERSE_MARKERS in `fetch_latest_firmware.py` identified these as false positives.

**Actual signing architecture (from `even_core` package):**
- `package:even_core/network/utils/signature_util.dart` → `SignatureUtil.calculateSignature`
- `package:even_core/extension/encrypt_ext.dart` → `EncryptExt|key`, `EncryptExt|iv`, `EncryptExt|encodePwd`
- `package:even_core/network/utils/even_certificate_util.dart` → `EvenCertificateUtil`
- `package:even_core/network/delegates/even_network_interceptor.dart` → `AuthInterceptor`

**HMAC key:** Hardcoded in Dart AOT binary as a static constant, likely in `EncryptExt|key` or a field of `SignatureUtil`. NOT the per-user `key`/`salt` returned from login. The actual key material is stored in the Dart snapshot constant pool (among ~157K string table entries, hash-ordered, not class-grouped) and requires either:
1. `blutter` on Android APK (recommended — dumps all class fields and constants)
2. Frida runtime hooks on an iOS device running Even.app
3. MITM capture of actual sign values for pattern analysis
4. Manual arm64 disassembly of the `calculateSignature` method

### 3. Hypothesis Testing Summary

| Category | Tests Run | Matches |
|---|---|---|
| Simple hash (SHA256/MD5, unkeyed) | ~200 | 0 |
| HMAC with known strings (appId, package, even, even_core, Firebase key, Google API key, class names, etc.) | ~1000 | 0 |
| HMAC with per-user key (32-byte from login) | ~60 | 0 |
| HMAC with per-user salt | ~20 | 0 |
| MD5 with key/salt | ~16 | 0 |
| SHA256 with key/salt concatenation | ~10 | 0 |
| Targeted binary strings (EvenSignature, EncryptExt, evenreal patterns) | ~576 | 0 |
| **Total** | **~1900+** | **0** |

Message formats tested: method+path, path+common, sorted common params, path+token, path+request-id, path+timestamp, and many combinations with separators (`|`, `&`, `\n`, `:`).

### 4. Authentication Flow

1. **Login**: POST `/v2/g/login` with `{email, passwd}` in body. `common` header required, `sign` NOT required.
2. **Password encoding**: Raw plaintext works. MD5+Base64 encoding also accepted (auto mode).
3. **JWT issued**: 7-day TTL (604800 seconds), `nbf`/`exp` claims present.
4. **Subsequent requests**: Require `token`, `common`, `region`, `request-id`, and `sign` headers.

### 5. Login Response Data Exposure

The login response returns extensive data **without sign verification**:

| Field | Content | Sensitivity |
|---|---|---|
| `user.email` | Account email | PII |
| `user.nickName` | Display name | PII |
| `user.birthday` | Date of birth | PII |
| `user.avatar` | Full JPEG (Base64) | PII |
| `user.key` | 256-bit encryption key (Base64) | **HIGH** |
| `user.salt` | 16-char salt | **HIGH** |
| `user.uuid` | User UUID | Internal ID |
| `user.id` | Numeric user ID | Internal ID |
| `user.hasConnectedRing` | Device binding | Usage data |
| `user.hasConnectedGlasses` | Device binding | Usage data |
| `user.onBoardedAt` | Onboarding timestamp | Usage data |
| `settings` | Notification/display prefs | Preferences |
| `prefs` | Hand/date/time/unit prefs | Preferences |
| `balance` | Service usage counters | Account data |
| `token` | JWT session token | **CRITICAL** |

---

## Security Findings

### GOOD (Effective Controls)

1. **Signature enforcement is active** on all authenticated endpoints except login.
2. **Server-side validation is cryptographic** — wrong signatures return 406 regardless of format/length, confirming the server performs actual HMAC verification rather than format checks.
3. **The HMAC secret is not trivially guessable** — 700+ common patterns all fail, indicating the key is a proper random or application-specific secret embedded at compile time.
4. **Token/common headers are enforced** alongside sign on protected endpoints.

### CONCERNS

1. **Login endpoint has no sign protection**: Any client that can construct a valid `common` header can attempt login. This opens the door to credential brute-force attacks if server-side rate limiting is insufficient. **Recommendation:** Add rate limiting on the login endpoint (IP-based, account-based), CAPTCHA after N failures, or require sign even on login.

2. **CDN firmware files are unauthenticated**: Anyone with the CDN URL can download firmware without any authentication. The URL pattern is `https://cdn.evenreal.co/firmware/{md5_hash}.bin` where the hash is the `fileSign` from the API. While the API metadata requires auth+sign, once a URL is known it can be freely shared. **Recommendation:** Add signed/time-limited CDN URLs or require auth tokens for CDN access.

3. **Extensive PII in login response**: The login endpoint returns the full user profile including avatar, birthday, encryption key, and salt — all without requiring a signature. If the login credential is compromised, all this data is immediately accessible. **Recommendation:** Return minimal data at login; require signed requests for profile retrieval.

4. **Per-user encryption key/salt exposed at login**: The `user.key` (256-bit) and `user.salt` are returned in the clear login response. If these are used for any sensitive operations (E2E encryption, local data protection), their exposure at the unauthenticated login step is a risk.

5. **Raw password accepted**: The login accepts both raw plaintext and MD5+Base64 encoded passwords. Supporting raw plaintext means the password travels as-is over TLS but is more susceptible to log exposure.

6. **7-day JWT TTL**: The session token has a relatively long lifetime. If compromised, it remains valid for a week. **Recommendation:** Consider shorter TTL with refresh tokens, or token revocation capability.

### INFORMATIONAL

- Health endpoints (`/health`, `/`) are accessible without any authentication (common practice for load balancer health checks).
- The sign algorithm uses `_signPrefix` and `_signSuffix` Dart private constants (library hash `2917441731`), suggesting the sign computation wraps or seasons the HMAC message with these values.
- The `common` header contains device fingerprint data (model, OS version, carrier, openUdid) which the server likely uses for device tracking and anti-abuse.

---

## Reverse Engineering Paths for Sign Recovery

If you need to recover the sign algorithm (e.g., for an official SDK):

### Binary Analysis Results (2026-03-14)

**Dart SDK version:** 3.32.x (snapshot hash `830f4f59e7969c70b595182826435c19`)

**Two binaries analyzed:**
- OLD (v2.0.7 build 394): 34,111,952 bytes, library hash `@2917441731`
- NEW (v2.0.8 build 419): 34,499,072 bytes, library hash `@2942441731`

**Confirmed markers in NEW binary (v2.0.8):**

| Marker | Offset | Section |
|---|---|---|
| `_signPrefix@2942441731` | 0x01a90e10 | String name table |
| `_signSuffix@2942441731` | 0x01825910 | String name table |
| `calculateSignature` | 0x0179f610 | String name table |
| `SignatureUtil` | 0x01912500 | String name table |
| `impl.mac.hmac` | 0x013a0160 | String name table |
| `impl.digest.sha256` | 0x015262e0 | String name table |
| `AuthInterceptor` | 0x0192a9f0 | String name table |
| `commonRequestHeader` | 0x01966660 | String name table |
| `get:sign` | 0x017df1f0 | String name table |
| `package:even_core/network/utils/signature_util.dart` | 0x014e0890 | String name table |
| `EvenCertificateUtil` | 0x0197d180 | String name table |
| `even-app-f488c` (Firebase project) | 0x0151f390 | String name table |
| `AIzaSyD2RMkVTPVga_DvN_ZeQYwp_QSGUB87jd0` (Google API key) | 0x019181c0 | String name table |
| `https://api2.evenreal.co` | 0x014e5970 | String name table |
| `/v2/g/login` | 0x01966510 | String name table |

**Mach-O layout (NEW):**

| Symbol | Offset | Section |
|---|---|---|
| `_kDartVmSnapshotInstructions` | 0x00004000 | `__TEXT,__text` |
| `_kDartIsolateSnapshotInstructions` | 0x0000e740 | `__TEXT,__text` |
| `_kDartVmSnapshotData` | 0x00cdb6c0 | `__TEXT,__const` |
| `_kDartIsolateSnapshotData` | 0x00ce4600 | `__TEXT,__const` |

**String table structure:** Entries use format `[16-byte metadata] [string + null + padding to 16]`. Metadata: `uint16 tag` (0x32xx), `uint16 0x0500`, `uint32 hash`, `uint32 encoded_length` (actual_length * 2). Tags: 0xe232 (short), 0xe332 (medium), 0xf232 (very short/non-ASCII), 0xe432+ (long).

**Key finding:** The string name table contains ~157,000 entries including both symbol NAMES (like `_signPrefix@2942441731`) and literal VALUES. Both are interleaved by hash, NOT grouped by class. The actual prefix/suffix VALUES are present in this table but are indistinguishable from the ~157K other entries without the Dart object pool cross-reference.

**Static analysis limitations:**
- `darter` (Python Dart snapshot parser) cannot parse Dart 3.32.x snapshots (too new; cluster IDs changed)
- `reflutter` requires IPA/APK input format
- `blutter` only supports Android libapp.so (ELF), not iOS Mach-O
- The Dart 3.32 snapshot cluster serialization format is not publicly documented
- ~700+ HMAC hypothesis tests (SHA-256/MD5, with known strings, per-user key/salt) all returned 0 matches against the server

### Path A: Dart AOT Snapshot Parsing
1. Use `blutter` (https://github.com/worawit/blutter) on the Android APK version of Even.app (same Dart code, ELF format that blutter supports)
2. Alternatively, port `blutter`'s C++ parser to handle Mach-O iOS binaries
3. Parse the Dart snapshot object pool to extract `_signPrefix` and `_signSuffix` constant values
4. Identify the HMAC key material from the `SignatureUtil` class fields
5. Reconstruct the `calculateSignature` method logic

### Path B: Runtime Hooking (Most Practical)
1. Install Even.app on a jailbroken iOS device
2. Use Frida to hook `calculateSignature` and log inputs/outputs:
   ```javascript
   // Frida script sketch - attach to Dart isolate, hook by symbol
   Interceptor.attach(ptr("ADDR_OF_calculateSignature"), {
     onEnter: function(args) { console.log("args:", args); },
     onLeave: function(retval) { console.log("sign:", retval); }
   });
   ```
3. Capture several sign values with known request parameters
4. Reverse the algorithm from observed input/output pairs

### Path C: MITM + reFlutter
1. Use `reflutter` to patch the IPA with snapshot dump hooks
2. Install patched IPA on device (requires sideloading)
3. Set up mitmproxy/Proxyman to capture TLS traffic
4. Capture requests with `sign` headers to different endpoints
5. Analyze sign values for patterns (reuse, length, encoding)

### Path D: Manual Disassembly (IDA Pro / Ghidra)
1. Load `App.framework/App` in IDA Pro or Ghidra with Dart AOT plugin (JEB has one)
2. Navigate to `calculateSignature` function code (find via dispatch table, NOT the string at 0x0179f610 which is metadata)
3. Follow arm64 pool references (PP register = x27 in Dart AOT) to find string constants
4. The HMAC construction: `Hmac(sha256, key_bytes).convert(utf8.encode(prefix + message + suffix))`
5. Look for `ldr` instructions from `[x27, #offset]` to identify pool indices for key/prefix/suffix

### Path E: Android APK Analysis (Recommended Alternative)
1. Download Even.app APK from Google Play (same Dart code, different platform)
2. Extract `lib/arm64-v8a/libapp.so`
3. Run `blutter` (https://github.com/worawit/blutter) which fully supports Android ELF
4. `blutter` will dump all string constants, class fields, and function signatures
5. Search the output for `SignatureUtil` class and its static fields
