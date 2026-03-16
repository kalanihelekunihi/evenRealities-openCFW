# Even Realities Android App - Reverse Engineering Analysis

Reverse engineering analysis of the Even Realities Android app (com.even.sg), complementing the iOS-derived protocol documentation in the parent `docs/` directory. The Android APK provides additional visibility into architecture decisions, native ML pipelines, and API surface area that are obscured in the iOS build.

## Analysis Methodology

The Android APK uses **360 Jiagu** (奇虎360加固) runtime packing. The `classes.dex` is encrypted at rest by a `StubApp` loader that decrypts into memory via `libjiagu.so` / `libjiagu_x86.so` at launch. Direct Java/Kotlin decompilation of the DEX files is therefore not possible.

Analysis was performed through four alternative approaches:

1. **apktool extraction** -- AndroidManifest.xml, smali stubs, resource files, and asset bundles were extracted from the APK without requiring DEX decryption.
2. **Dart AOT snapshot string analysis** -- `libapp.so` (29.4MB) contains the Flutter Dart ahead-of-time compiled business logic. String extraction from this binary yields class names, method signatures, API routes, protobuf field names, and UI text.
3. **Native library string extraction** -- `libeven.so` (30.5MB) and other native libraries were analyzed for embedded strings, symbol tables, and configuration data.
4. **Proto file extraction** -- Protobuf `.proto` definitions were recovered from the APK assets and native binaries.

## APK Identity

| Field | Value |
|-------|-------|
| Package name | `com.even.sg` |
| App name | Even |
| compileSdkVersion | 36 |
| Platform | Flutter 2.x with Kotlin platform channel plugins |
| Protection | 360 Jiagu (StubApp/libjiagu DEX packer) |
| Deep link scheme | `evenG2://` |
| Google Play | https://play.google.com/store/apps/details?id=com.even.sg |
| APK size (universal) | ~140 MB |
| APK size (arm64) | ~160 MB |

## Flutter Package Architecture

The app is structured as a multi-package Flutter project with Kotlin platform channels for native BLE, audio, and ML inference.

| Package | Files | Purpose |
|---------|-------|---------|
| `even` | 869 | Main app: UI pages, services, API client, state management |
| `even_connect` | 119 | BLE protocol layer for G1, G2, and R1 Ring |
| `even_core` | 43 | Core services, network client, local storage |
| `even_navigate` | 30 | Mapbox turn-by-turn navigation integration |
| `dashboard` | 68 | Dashboard widget system (clock, weather, stocks, etc.) |
| `teleprompt` | 33 | Teleprompter engine with scroll control |
| `conversate` | 40 | Conversation/meeting AI transcription |
| `translate` | 24 | Real-time translation engine |
| `flutter_ezw_ble` | 27 | Low-level BLE driver (platform channel to Kotlin) |
| `flutter_ezw_asr` | 31 | ASR engine with dual-provider support (Azure + Soniox) |
| `flutter_ezw_audio` | 18 | Audio pipeline with ML-based enhancement |
| `flutter_ezw_utils` | 16 | Utility library |
| `flutter_ezw_lc3` | 2 | LC3 BLE audio codec bindings |
| `flutter_ezw_health_algorithm` | 2 | Health data processing algorithms |
| `flutter_ezw_logger` | 6 | Structured logging framework |

## Native Libraries (arm64-v8a)

The arm64 build includes 30.5 MB of on-device ML inference in `libeven.so` alone, plus substantial navigation and speech SDKs.

| Library | Size | Purpose |
|---------|------|---------|
| `libeven.so` | 30.5 MB | On-device ML: speech enhancement, BERT NLU, noise reduction, AGC |
| `libapp.so` | 29.4 MB | Flutter Dart AOT snapshot (compiled business logic) |
| `libnavigator-android.so` | 27.6 MB | Mapbox turn-by-turn navigation |
| `libonnxruntime.so` | 16.0 MB | ONNX Runtime ML inference engine |
| `libmapbox-maps.so` | 12.2 MB | Mapbox Maps SDK |
| `libflutter.so` | 11.3 MB | Flutter engine |
| `libMicrosoft.CognitiveServices.Speech.core.so` | 8.5 MB | Azure Speech Services (STT/TTS) |
| `libmapbox-common.so` | 6.3 MB | Mapbox Common utilities |
| `libmodpdfium.so` | 4.8 MB | PDF rendering (teleprompter document import) |
| `libsherpa-onnx-c-api.so` | 4.6 MB | Sherpa-ONNX on-device ASR |
| `libsqlite3.so` | 1.5 MB | SQLite database engine |
| `libmmkv.so` | 718 KB | MMKV key-value storage (WeChat/Tencent) |
| `liblc3.so` | 173 KB | LC3 BLE audio codec |
| Microsoft Speech extensions | ~3.4 MB | Audio codec, keyword spotting, language understanding |

See [native-libraries.md](native-libraries.md) for detailed analysis of `libeven.so` ML models and `libapp.so` string findings.

## API Endpoints

| Environment | URL |
|-------------|-----|
| Production API | `https://api2.evenreal.co` |
| Pre-production | `https://pre-g2.evenreal.co` |
| CDN (primary) | `https://cdn.evenreal.co` |
| CDN (secondary) | `https://cdn2.evenreal.co` |
| Staging | `https://api2.ev3n.co` (note: `ev3n` not `even`) |
| Development | `http://192.168.2.113:8888` |
| Web portal | `https://evenapp.evenrealities.com` |

See [api-endpoints.md](api-endpoints.md) for the full route inventory and request/response analysis.

## Android Permissions (30)

The app requests 30 permissions spanning 8 categories:

- **Bluetooth (5)**: `BLUETOOTH`, `BLUETOOTH_ADMIN`, `BLUETOOTH_CONNECT`, `BLUETOOTH_SCAN`, `BLUETOOTH_ADVERTISE`
- **Location (3)**: `ACCESS_FINE_LOCATION`, `ACCESS_COARSE_LOCATION`, `ACCESS_BACKGROUND_LOCATION`
- **Audio (4)**: `RECORD_AUDIO`, `RECORD_AUDIO_BACKGROUND`, `MODIFY_AUDIO_SETTINGS`, `CAPTURE_AUDIO_OUTPUT`
- **Calendar (2)**: `READ_CALENDAR`, `WRITE_CALENDAR`
- **Camera (1)**: `CAMERA`
- **Storage (2)**: `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE`
- **Network (5)**: `INTERNET`, `ACCESS_NETWORK_STATE`, `CHANGE_NETWORK_STATE`, `CHANGE_WIFI_STATE`, `ACCESS_WIFI_STATE`
- **Other (8)**: `READ_PHONE_STATE`, `POST_NOTIFICATIONS`, `ACCESS_NOTIFICATION_POLICY`, `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`, `QUERY_ALL_PACKAGES`, foreground service types (`MICROPHONE`, `LOCATION`, `CONNECTED_DEVICE`, `SPECIAL_USE`)

## Android Services

| Service | Type | Purpose |
|---------|------|---------|
| `FlutterFirebaseMessagingBackgroundService` | Background | Firebase push notification handling |
| `ForegroundService` | Foreground | Local notification dispatch |
| `AudioRecordingService` | Foreground (microphone) | Microphone capture for ASR |
| `EvNLService` | NotificationListenerService | Intercepts all device notifications for forwarding to glasses |
| `NavigationForegroundService` | Foreground (location) | Turn-by-turn navigation tracking |
| `DfuService` 1--8 | Service | **8 parallel Nordic DFU services** for firmware updates |
| `NavigationNotificationService` | Service | Mapbox navigation notifications |

The 8 parallel DFU services are notable -- this likely supports concurrent firmware updates to multiple components (main MCU, BLE, touch, codec, box, bootloader).

## External SDK Dependencies

| SDK | Purpose |
|-----|---------|
| Firebase (Analytics, Crashlytics, Messaging) | Telemetry, crash reporting, push notifications |
| Mapbox (Maps + Navigation) | Map rendering and turn-by-turn navigation |
| Microsoft Cognitive Services Speech | Cloud ASR/TTS (Azure) |
| Sherpa-ONNX | On-device ASR (offline fallback) |
| ONNX Runtime | ML model inference engine |
| Nordic DFU (`mcumgr_flutter`) | BLE firmware update protocol |
| ZXing | Barcode/QR code scanning |
| Hive + Drift + SQLite | Local data persistence (3 storage engines) |
| GetX | Flutter state management and routing |
| Dio | HTTP client with interceptors |
| RxDart | Reactive stream extensions |
| MMKV | High-performance key-value store |

## Detailed Analysis Documents

| Document | Description |
|----------|-------------|
| [ble-connectivity.md](ble-connectivity.md) | **Complete BLE connectivity reference**: all devices, UUIDs, connection lifecycle, heartbeat, reconnection |
| [protocol-layer.md](protocol-layer.md) | BLE protocol analysis: G2 packet format, characteristic UUIDs, transport layer |
| [protobuf-services.md](protobuf-services.md) | Protobuf service definitions extracted from the APK |
| [api-endpoints.md](api-endpoints.md) | Cloud API route inventory with request/response structure |
| [native-libraries.md](native-libraries.md) | Native library analysis: `libeven.so` ML models, symbol tables |
| [app-architecture.md](app-architecture.md) | App architecture: Flutter packages, state management, data flow |
| [audio-pipeline.md](audio-pipeline.md) | Audio and ASR pipeline: dual-provider, ML enhancement, LC3 codec |
| [firmware-update.md](firmware-update.md) | OTA/DFU process: Nordic DFU services, update flow |
| [new-findings.md](new-findings.md) | Knowledge discovered here that is not in the existing iOS-derived docs |
| [api-routes-complete.md](api-routes-complete.md) | Complete API route table (81 routes with paths) |
| [protocol-commands.md](protocol-commands.md) | All protocol command type enums for every service |
| [protobuf-message-catalog.md](protobuf-message-catalog.md) | Complete catalog of 152 protobuf message types across 19 services |
| [api-signing.md](api-signing.md) | API signing algorithm (HMAC-SHA256), key discovery, per-endpoint requirements |
| [api-security-assessment.md](api-security-assessment.md) | API signature enforcement audit, PII exposure, JWT analysis |

## Relationship to iOS Documentation

The parent `docs/` directory contains protocol documentation primarily derived from iOS app reverse engineering and live BLE packet captures. The Android analysis here serves three purposes:

1. **Validation** -- Confirms protocol details independently (the G2 protocol is platform-neutral; both apps speak the same wire format).
2. **Gap filling** -- The Android APK leaks more implementation detail through `libapp.so` strings than the iOS binary, particularly around API routes, protobuf field names, and feature flags.
3. **Platform differences** -- Documents Android-specific behaviors such as `EvNLService` (NotificationListenerService), 8 parallel DFU services, and background location handling that have no iOS equivalent.

## Key Observations

- The 360 Jiagu packing is a deliberate anti-RE measure. The Flutter/Dart layer in `libapp.so` is unaffected by it, making string analysis the primary analysis vector.
- `libeven.so` at 30.5 MB is the largest single library and contains substantial on-device ML (speech enhancement, BERT NLU, noise reduction, AGC) -- this runs locally without cloud dependency.
- The dual ASR architecture (Azure cloud + Sherpa-ONNX local) provides offline fallback, which is not obvious from the iOS analysis.
- 8 parallel DFU services suggest the firmware update pipeline can flash multiple G2 sub-components concurrently, matching the 6-entry EVENOTA container format documented in [firmware-updates.md](../firmware/firmware-updates.md).
- The staging domain `api2.ev3n.co` (with a `3` replacing the second `e`) is a useful indicator for identifying pre-production traffic.
