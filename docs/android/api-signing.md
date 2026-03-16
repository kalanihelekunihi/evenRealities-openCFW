# Even Realities API Signing Algorithm

## The Algorithm (confirmed 144/144 captured requests)

```
SIGN_KEY = "a7964f42c39200cfa25c258b7a311b106e20232173667e543c34ced91d63b404"

def compute_sign(method, path, query, common, token, body=""):
    # 1. Parse query string into key=value pairs, sort by key, rejoin with "&"
    qp = parse_qsl(query) -> dict
    sorted_q = '&'.join(f'{k}={v}' for k,v in sorted(qp.items()))

    # 2. Build parts list: always include method, path, common header
    parts = [method, path, common]
    if sorted_q:  parts.append(sorted_q)   # only if query params exist
    if token:     parts.append(token)       # only if authenticated (post-login)
    if body:      parts.append(body)        # only for POST/PUT/PATCH with body

    # 3. Sort ALL parts alphabetically, join with newline
    parts.sort()
    message = '\n'.join(parts)

    # 4. HMAC-SHA256, base64-encode
    sign = base64(HMAC-SHA256(utf8_encode(SIGN_KEY), utf8_encode(message)))
    return sign
```

## Key Facts

- **SIGN_KEY**: `a7964f42c39200cfa25c258b7a311b106e20232173667e543c34ced91d63b404` (64-char hex string, used as raw UTF-8 bytes -- NOT hex-decoded)
- **EncryptExt|key**: `2f7b4c9ac8dd6dd471ab12f7b000d0b5` (32-char hex string for AES-CBC password encryption, NOT for API signing)
- **Output**: Base64-encoded HMAC-SHA256 digest (44 characters, 32 bytes decoded)
- **The key is the same on iOS and Android** -- same Dart code, same constant

## Endpoint Sign Requirements (verified 2026-03-14)

| Endpoint | Method | Sign Required |
|---|---|---|
| `/v2/g/login` | POST | NO (server ignores sign) |
| `/v2/g/check_latest_firmware` | GET | YES |
| `/v2/g/check_firmware` | GET | YES |
| `/v2/g/list_devices` | GET | YES |
| `/v2/g/user_info` | GET | YES |
| `/v2/g/bind_device` | POST | YES |
| `/v2/g/get_user_prefs` | GET | YES |
| `/v2/g/jarvis/conversate/list` | POST | YES |
| `/v2/g/asr_sconf` | GET | YES |
| `/v2/g/check_app` | GET | YES |
| `/v2/g/get_ios_app_list` | GET | YES |
| `/v2/g/inbox/unread_count` | GET | YES |
| `/v2/g/health/*` | GET | YES |
| CDN (`cdn.evenreal.co`) | GET | NO (no auth at all) |
| `/health` | GET | NO |

## Discovery Methodology

### Timeline
1. **MITM capture** (mitmproxy `--mode local`) of Even.app v2.0.8 on macOS -- captured 144 signed requests
2. **1,900+ hypothesis tests** against the live API -- all returned `code=406 Invalid signature`
3. **Binary analysis** of iOS App.framework/App -- found `SignatureUtil`, `calculateSignature`, `impl.mac.hmac`, `impl.digest.sha256` markers but couldn't extract the key from the Dart 3.32 AOT snapshot format
4. **Android APK extraction** -- pulled Even.app APK from Samsung Galaxy Fold 7 via `adb`
5. **Jiagu bypass** -- the base APK is packed with Qihoo 360 Jiagu, but `libapp.so` is in the unprotected `split_config.arm64_v8a.apk` split APK
6. **blutter decompilation** -- ran blutter (https://github.com/worawit/blutter) on `libapp.so`, which dumped the full Dart class hierarchy including `SignatureUtil.calculateSignature` with the HMAC key at pool offset `[pp+0xed30]`
7. **Algorithm confirmed** -- 144/144 captured requests verified, then successfully queried `/v2/g/check_latest_firmware` with a computed sign

### Tools Used
- **mitmproxy 12.2.1** with `--mode local` for macOS traffic interception
- **adb** (Android Debug Bridge) for APK extraction from device
- **blutter** (https://github.com/worawit/blutter) for Dart AOT decompilation
- Python scripts for HMAC hypothesis testing and verification

### Key Source References
- Decompiled Dart: `captures/firmware/blutter_output/asm/even_core/network/utils/signature_util.dart`
  - Line 313-314: HMAC key string at `[pp+0xed30]`
  - Line 159: `"&"` separator for query params
  - Line 303: `"\n"` separator for message parts
  - Lines 222-254: Conditional body inclusion for POST/PUT/PATCH methods
  - Lines 333-343: `Hmac(sha256, key_bytes).convert(message_bytes)`
  - Lines 348-351: Base64 encoding of result
- Auth interceptor: `captures/firmware/blutter_output/asm/even/common/api/interceptors/auth_interceptor.dart`
  - Lines 405-412: Call to `calculateSignature(body, common_value, method, path, queryParams, token)`
  - The method is `.toUpperCase()` before passing (line 363)

## False Positives (Historical)

During the investigation, several markers in the iOS binary appeared to be signing-related but were not:

| Marker | Actual Purpose |
|---|---|
| `_signPrefix@2917441731` / `_signSuffix@2942441731` | `NumberFormat` fields from Dart `intl` package (library hash `@2942441731` contains `_decimalSeparator`, `_integerDigits`, `_pad`, `_floor`, `_round`) |
| `EncryptExt\|key` (`2f7b4c9ac8dd6dd471ab12f7b000d0b5`) | AES-CBC encryption key for password encoding (`EncryptExt.encodePwd`), not API signing |
| `EncryptExt\|iv` | AES-CBC initialization vector (16 bytes: `[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]`) |
| `EvenSignature` | Even Signature font class for glasses display rendering |
| `user.key` / `user.salt` from login response | Per-user encryption material, not the global HMAC signing key |

## Re-derivation Guide

If Even Realities changes the signing key in a future app version:

### Method A: Android APK + blutter (Recommended)
1. Download the latest Even.app APK from Google Play onto an Android device
2. Connect device via USB with ADB debugging enabled
3. Extract the APK:
   ```bash
   adb shell pm path com.even.sg
   # Pull the arm64 split APK (contains libapp.so unprotected by Jiagu):
   adb pull <path_to_split_config.arm64_v8a.apk> even_arm64.apk
   ```
4. Extract `libapp.so`:
   ```bash
   unzip even_arm64.apk "lib/arm64-v8a/libapp.so" "lib/arm64-v8a/libflutter.so"
   ```
5. Run blutter:
   ```bash
   python3 blutter.py lib/arm64-v8a output_dir
   ```
6. Search for the key:
   ```bash
   grep -A5 "calculateSignature" output_dir/asm/even_core/network/utils/signature_util.dart
   ```
   Look for the 64-character hex string at a `[pp+0x...]` pool reference.

### Method B: MITM Capture + Brute Force
If the algorithm structure remains the same but only the key changes:
1. Capture signed requests via `mitmdump --mode local -s tools/even_mitm_capture.py`
2. Extract a (sign, method, path, query, common, token, body) tuple
3. Brute-force the key by searching the binary's string table for 64-char hex strings
4. Test each candidate: `base64(HMAC-SHA256(candidate, sorted_parts.join("\n"))) == captured_sign`

### Method C: iOS Binary + Dart Snapshot Parser
If a Dart 3.32+ snapshot parser becomes available:
1. Extract `App.framework/App` from the iOS app
2. Parse the Dart snapshot object pool
3. Find `SignatureUtil` class fields
4. Extract the string constant from the pool

### Indicators That the Key Has Changed
- API returns `code=406 "Invalid signature"` for requests that previously worked
- Login still succeeds (no sign needed) but all other endpoints fail
- The app version in Info.plist / AndroidManifest.xml has changed
- The `snapshot_hash` in the Dart snapshot header differs from `830f4f59e7969c70b595182826435c19`

## Worked Example

**Request:** `GET /v2/g/check_latest_firmware`

```
method  = "GET"
path    = "/v2/g/check_latest_firmware"
query   = ""        (no query params)
common  = "platform=26.4&package=com.even.sg&versionName=2.0.8&..."
token   = "eyJhbGciOiJIUzI1NiI..."
body    = ""        (GET request, no body)

# Step 1: sorted_q = "" (empty, excluded from parts)
# Step 2: parts = ["GET", "/v2/g/check_latest_firmware", "platform=26.4&package=..."]
#          token is non-empty, so: parts.append(token)
#          body is empty, so: not appended
# Step 3: parts.sort() -> alphabetical order
# Step 4: message = parts.join("\n")
# Step 5: sign = base64(HMAC-SHA256("a7964f42...", message))
```

**Request:** `POST /v2/g/jarvis/conversate/list`

```
method  = "POST"
path    = "/v2/g/jarvis/conversate/list"
query   = ""
common  = "platform=26.4&..."
token   = "eyJhbGciOiJIUzI1NiI..."
body    = '{"page":1,"page_size":50,"sort":[...]}'

# Step 1: sorted_q = "" (excluded)
# Step 2: parts = ["POST", "/v2/g/jarvis/conversate/list", common_value, token, body_string]
# Step 3: parts.sort()
# Step 4-5: HMAC-SHA256 and base64
```
