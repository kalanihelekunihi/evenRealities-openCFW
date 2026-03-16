# Even Android App Architecture

Comprehensive architecture documentation for the Even Realities Android app (`com.even.sg`), reverse-engineered from APK analysis including `libapp.so` string extraction, `apktool` resource decompilation, and native library symbol analysis.

---

## Table of Contents

- [Technology Stack](#technology-stack)
- [App Pages Structure](#app-pages-structure)
- [Service Architecture](#service-architecture)
- [BLE Services](#ble-services)
- [Audio Pipeline](#audio-pipeline)
- [Data Packages](#data-packages)
- [Device Settings Extensions](#device-settings-extensions)
- [Ring Extensions](#ring-extensions)

---

## Technology Stack

| Category | Technology | Notes |
|----------|-----------|-------|
| **Framework** | Flutter with Kotlin platform channels | Dart AOT compiled into `libapp.so` (29.4 MB) |
| **State Management** | GetX (`package:get`) | Reactive controllers, dependency injection, routing |
| **HTTP Client** | Dio with interceptors | Token refresh, retry, logging interceptors |
| **Reactive Streams** | RxDart | BehaviorSubject/PublishSubject for BLE event streams |
| **Local Storage (KV)** | MMKV (Tencent) | High-performance key-value store (`libmmkv.so`, 718 KB) |
| **Local Storage (Lightweight)** | Hive | NoSQL box-based storage for settings and caches |
| **Local Storage (SQL)** | Drift (SQLite ORM) + SQLite3 | Structured data: health records, conversation history |
| **Push Notifications** | Firebase Cloud Messaging | `FlutterFirebaseMessagingBackgroundService` |
| **Analytics** | Firebase Analytics | Event tracking, user properties |
| **Crash Reporting** | Firebase Crashlytics | Automatic crash capture with Flutter error handler |
| **Logging** | Talker (with Flutter UI) + custom `flutter_ezw_logger` | Talker provides in-app log viewer overlay |
| **Image Processing** | `image` package | BMP generation for glasses display |
| **PDF Rendering** | PdfBox (`tom_roush`) + `jniPdfium` (`libmodpdfium.so`, 4.8 MB) | Teleprompter document import |
| **Barcode/QR** | ZXing (`CaptureActivity`) | Device pairing QR scan |
| **Deep Links** | `evenG2://` URL scheme | Cross-app navigation, OAuth callbacks |
| **App Protection** | 360 Jiagu (奇虎360加固) | Runtime DEX packer via `StubApp`/`libjiagu.so` |

---

## App Pages Structure

Recovered from `package:even/pages/` path strings in `libapp.so`. The app follows a tab-based main screen with feature pages pushed onto the navigation stack via GetX routing.

### Main Screen (Bottom Tab Bar)

#### Home Tab
- Device status card (glasses + ring connection state, battery levels)
- Quick action grid (AI, Translate, Navigate, Teleprompter, Conversate, Dashboard)
- Firmware update banner (when OTA available)
- Deep link entry point for `evenG2://` scheme

#### Health Tab
- Health metrics dashboard with card-based layout
- **Metrics**: Heart rate, blood oxygen (SpO2), temperature, steps, calories, sleep, HRV, productivity
- Data sourced from R1 Ring health sensors via BLE relay through G2 glasses
- Historical charts and trend analysis
- Activity ring / goal tracking

#### Mine Tab
- User profile display and editing
- App settings (theme, language, units)
- Privacy policy and regulatory information
- Device management (bound devices list)
- Account management (logout, delete account)
- Debug entry point (hidden in release builds)

---

### Feature Pages

#### AI Agent (`ai_agent/`)

AI chat interface for the Even AI assistant. Manages the full lifecycle from voice activation through response display on the glasses.

| Component | Purpose |
|-----------|---------|
| AI Agent page | Main chat UI with message history |
| Settings | Provider selection, model configuration |
| Language selection | ASR and response language |
| Shortcuts | Quick-action prompts, custom commands |

The AI Agent page coordinates with the AI Agent Service (see [Service Architecture](#ai-agent-service)) for state machine transitions and BLE command dispatch.

#### Conversate (`converse/`)

Live conversation AI for meetings and real-time dialogue. Captures audio, transcribes, and optionally provides semantic analysis.

| Component | Purpose |
|-----------|---------|
| Live mode | Real-time transcription display on glasses |
| History view | Past conversation sessions with timestamps |
| Semantic analysis | AI-powered summary, key points, action items |
| Context/background upload | Upload reference documents for context-aware transcription |
| Callback system | BLE event handlers for glasses-side interactions |

The Conversate page uses a dedicated `ConversateTask` in the Task Manager for BLE lifecycle orchestration. The `magic_random` deduplication counter (protobuf field 8) is used in all conversate BLE packets.

#### Teleprompter (`teleprompter/`)

Script reading with three scroll modes and rich document import.

| Component | Purpose |
|-----------|---------|
| Manual mode | Tap/swipe-controlled scrolling via glasses gesture |
| Auto scroll mode | Timer-based constant-speed scrolling |
| AI voice-sync mode | ASR-driven scroll that follows the speaker's pace |
| Document parsing | DOCX import via platform channel, PDF via PdfBox/jniPdfium |
| Preview | Phone-side preview of glasses display |
| Settings | Speed, font size, text style, line spacing |
| Color/width/text helpers | Display formatting utilities for the 576x288 Gray4 display |

Text is sent to glasses in 30-byte fixed-width, space-padded chunks on service `0x06-20` with 0.6s inter-packet delay. The `magic_random` dedup counter is active.

#### Translate (`translate/`)

Real-time bidirectional translation with dual ASR backend.

| Component | Purpose |
|-----------|---------|
| Configuration | Source/target language pair selection |
| Preview | Live translation preview on phone |
| History | Past translation sessions |
| Language picker | Full language list with regional variants |
| Settings | ASR provider preference, display formatting |
| Service layer | Azure Speech Services + Soniox ASR backends |

Translation uses service `0x05-20` with types 20-23. The `TranslationTask` manages BLE display lifecycle including `magic_random` sequencing.

#### Navigate (`navigate/`)

Turn-by-turn navigation with Mapbox integration and glasses HUD overlay.

| Component | Purpose |
|-----------|---------|
| Mapbox integration | Full map rendering via `libnavigator-android.so` (27.6 MB) + `libmapbox-maps.so` (12.2 MB) |
| Search | POI and address search with autocomplete |
| Favorites | Saved locations with quick-start navigation |
| BLE glasses display overlay | Direction arrows, distance, street names sent via `0x08-20` |
| Preload map tiles | Offline map area download for connectivity-constrained use |

Navigation uses 10 sub-commands on service `0x08-20` with 36 icon types for directional indicators. Map tile images are sent as BMPs via file transfer (`0xC4/0xC5`).

#### Dashboard (`dashboard/`)

Widget system for the glasses idle/home screen. Each widget type has its own settings page.

| Widget | Service ID | Notes |
|--------|-----------|-------|
| Calendar | `0x01-20` | Synced from phone calendar via `READ_CALENDAR` permission |
| Weather | `0x01-20` | Location-based, configurable units |
| News | `0x01-20` | RSS/API feed, configurable sources |
| Stocks | `0x01-20` | Symbol watchlist, real-time quotes |
| Quick List | `0x01-20` | Task items from Quicklist feature |
| Reminder | `0x01-20` | Time-based alerts |
| Health | `0x01-20` | Summary metrics from R1 Ring |
| Time | `0x01-20` | Clock face with configurable format |
| Battery/Electricity | `0x01-20` | Glasses + case + ring battery levels |
| Pro features | `0x01-20` | Premium widget types |

Dashboard widgets are managed through the Dashboard service on `0x01-20` (Dashboard/Gesture service).

#### Quicklist (`quicklist/`)

Task management with glasses-side display and interaction.

| Component | Purpose |
|-----------|---------|
| Task list | CRUD operations synced to glasses via `0x0C-20` |
| Per-item fields | uid, index, isCompleted, title, timestamp, tsType |
| Commands | fullUpdate (1), batchAdd (2), singleItem (3), delete (4), toggleComplete (5), pagingRequest (6) |

Quicklist shares service `0x0C-20` with Health data (command IDs 10-12), using disjoint command ID ranges to multiplex.

#### PDF View (`pdf_view/`)

Document viewing for teleprompter script import and general file reading. Uses `jniPdfium` (`libmodpdfium.so`) for rendering.

#### WYSIWYG (`wyswyg/`)

Rich text editor with embedded translation widget. Used for composing and editing teleprompter scripts and AI prompts with formatting support.

---

### Device Pages

#### Discovery

BLE scanning and device connection flow.

- Scans for G2 glasses (Even UART Service UUID) and R1 Ring (`BAE80001-4F05-4503-8E65-3AF1F7329D1F`)
- QR code pairing via ZXing `CaptureActivity`
- Connection state management with retry logic
- Device type detection (G1 legacy, G2, R1)

#### Device Info

- Custom device information display
- Serial number, firmware version, hardware model
- Device sharing and transfer functionality

#### Mine/Settings (Per-Device)

Per-device configuration pages accessed from the device management screen.

| Setting | Details |
|---------|---------|
| **Brightness** | 0-100% UI scale mapped to 0-42 DAC scale. Per-eye calibration via `leftMaxBrightness` / `rightMaxBrightness` |
| **Display settings** | Screen-off interval (15s/30s/1m/2m/5m/never), anti-shake, wakeup angle |
| **Motion/gesture settings** | Gesture-to-action mapping (6 gesture types to 9 action types) |
| **Head-up display recalibration** | Accelerometer-based display angle adjustment |
| **Ring hand selection** | Left/right hand configuration for R1 Ring gesture orientation |
| **Advanced settings** | Silent mode, wear detection toggle, compass calibration |

Brightness is sent via protobuf `G2SettingPackage` on `0x0D-00`. The secondary path uses EvenAI SKILL (type 6 on `0x07-20`, skill ID 0 for brightness, 7 for auto-brightness).

#### OTA Update

Multi-component firmware update with parallel DFU capability.

| Update Type | Protocol | Target |
|-------------|----------|--------|
| **Glasses OTA** | EVENOTA format (4-phase: START, INFORMATION, FILE, RESULT_CHECK) | G2 main firmware (6-entry container) |
| **Ring DFU** | Nordic DFU (`mcumgr_flutter`) | R1 Ring firmware |
| **Ring bootloader** | Nordic DFU | R1 Ring bootloader/softdevice |
| **DFU error handling** | Retry, rollback, error reporting | All targets |

The 8 parallel `DfuService` instances (declared in AndroidManifest.xml) support concurrent firmware updates to multiple G2 sub-components (main MCU, BLE EM9305, touch CY8C4046FNI, codec GX8002B, box case MCU, bootloader).

OTA file packets use a 5-byte header + 1000-byte payload + CRC at byte offset 1005.

#### Nickname

Device naming page for user-assigned friendly names stored locally.

---

### Settings Pages

#### Gesture Customization

Maps physical gestures to software actions.

**Gesture Types** (6): Single tap, double tap, long press, slide forward, slide backward, (reserved)

**Action Types** (9): Dashboard, AI Agent, Conversate, Teleprompter, Translate, Navigate, Quicklist, None, Custom

Configuration is written via `G2GestureControlListProtocol` on `0x0D-00/0x0D-20`.

#### Language

- App language selection (affects UI strings)
- Glasses language selection (affects on-device firmware text rendering)
- ASR language configuration (affects speech recognition model)

#### Notification

- Notification forwarding toggle (per-app whitelist or forward-all mode)
- Display time configuration
- Uses `EvNLService` (Android `NotificationListenerService`) to intercept all device notifications
- Forwarded via `0x02-20` with JSON payload using `"android_notification"` key (even on iOS, firmware expects this key)

#### Theme

App theme selection (light/dark/system). Does not affect glasses display (which is always monochrome Gray4).

#### Unit

- Metric/imperial unit system
- Date format selection
- Distance unit
- Temperature unit (Celsius/Fahrenheit)
- Time format (12h/24h)

Persisted via `G2UniversalSettingsReader` protocol on `0x0D-00`.

#### Foreground Service

Background/foreground service management for Android. Controls persistent notification and wake lock behavior for:
- Audio recording service (microphone capture for ASR)
- Navigation service (GPS tracking)
- BLE connection maintenance

---

### Login/Auth Pages

| Page | Purpose |
|------|---------|
| Email entry | Account identification |
| Password | Authentication |
| Captcha | Bot prevention |
| Registration | New account creation |
| Password reset | Account recovery flow |
| Country selection | Region configuration (affects API endpoint and content) |
| **Onboarding flow** | Multi-step device setup |

**Onboarding sub-pages**:
- G2 glasses pairing and setup
- R1 Ring pairing and setup
- Device selection (when multiple devices available)
- Firmware update prompt (when OTA available during onboarding)

Onboarding uses service `0x10-20` with 7 states: `sendStartUp`, `sendStart`, `sendEnd`, plus `queryHeadUpStatus`.

---

### Debug Pages

Available in debug/development builds, hidden in release.

| Page | Purpose |
|------|---------|
| Audio test | Microphone capture and playback verification |
| Scanner/connect device | Low-level BLE device scanning without pairing flow |
| Glass log viewer | Download and display firmware log files (12 log types, 5 levels) |
| API mock settings | Override API responses for testing |
| Debug controller | Master debug panel with sub-widgets for protocol inspection |

---

## Service Architecture

### Common Services (`even/common/services/`)

#### AI Agent Service

Central state machine managing the full AI interaction lifecycle from wake word through response display.

**State Machine**:

```
idle  -->  wakeup  -->  asr (listening)  -->  cmd_dispatch  -->  ai  -->  stay
 ^                                                                        |
 |                                                                        |
 +------------------------------------------------------------------------+
```

| State | Description |
|-------|-------------|
| `idle` | Waiting for activation (tap gesture, voice wake, or explicit trigger) |
| `wakeup` | Glasses microphone activated, audio pipeline starting |
| `asr` | Active speech recognition -- audio streaming to ASR engine |
| `cmd_dispatch` | Transcript received, determining intent (local command vs. cloud AI) |
| `ai` | Cloud AI processing, streaming response to glasses display |
| `stay` | Response displayed, waiting for follow-up or timeout to idle |

**Sub-components**:

| Component | Purpose |
|-----------|---------|
| ASR engine helper | Manages dual ASR backend (Azure Speech Services + Soniox), with automatic failover |
| Audio recorder | Ring buffer-based audio capture from glasses microphone via NUS (`0x0E` mic control) |
| VAD helper | Voice Activity Detection for automatic speech endpoint detection |
| Text stream manager | Manages incremental text display on glasses during AI streaming response |
| Cancellable future manager | Handles async operation cancellation on state transitions |
| AI BT command manager | Translates AI state transitions into BLE commands on `0x07-20` |

EvenAI types: 0=NONE, 1=CTRL, 3=ASK, 4=ANALYSE, 5=REPLY, 6=SKILL, 7=PROMPT, 8=EVENT, 9=HB, 10=CONFIG, 161=COMM_RSP. Echo pattern: response type = request type + 2.

#### Firebase/FCM Service

Push notification handling via `FlutterFirebaseMessagingBackgroundService`. Supports remote actions:
- Silent firmware update prompts
- Remote device commands
- Server-side configuration refresh

#### Global Service

App-wide state management singleton (GetX `GetxService`). Manages:
- Current device connection state
- Active feature state (which feature page is foreground)
- App lifecycle events (foreground/background/terminated)
- Deep link handling for `evenG2://` scheme

#### Log Service

Structured logging across three domains:

| Domain | Source | Transport |
|--------|--------|-----------|
| Glass log | Firmware log files on glasses | Downloaded via `0x0F-20` Logger service (12 file types, 5 levels) |
| Ring log | R1 Ring diagnostic data | Retrieved via Ring BLE service |
| General log | App-side events | Talker framework + `flutter_ezw_logger` |

#### Network Service

Connectivity monitoring with automatic behavior adjustment:
- WiFi/cellular state detection
- Automatic ASR provider switching (cloud to on-device when offline)
- API request queuing during connectivity gaps
- Map tile cache management

#### Performance Tracking Service

Performance metrics collection for:
- BLE connection time
- Feature activation latency
- Audio pipeline round-trip time
- API response times

#### Setting Service

User preference management with reactive updates:
- Unit system (metric/imperial)
- Date/time format
- Temperature scale
- Distance unit
- Persisted via MMKV for instant access, synced to glasses via `G2UniversalSettingsReader`

#### Task Manager

Feature task orchestration layer. Each feature has a dedicated task that manages its BLE lifecycle, display state, and cleanup.

| Task | Feature | BLE Services Used |
|------|---------|------------------|
| `ConversateTask` | Live conversation | `0x0B-20` (Conversate), `0x0E-20` (DisplayConfig) |
| `NavigationTask` | Turn-by-turn | `0x08-20` (Navigation), `0xC4/0xC5` (FileTransfer for map tiles) |
| `QuicklistTask` | Task management | `0x0C-20` (Quicklist+Health) |
| `SettingsTask` | Device settings | `0x0D-00/0x0D-20` (Configuration) |
| `TelepromptTask` | Teleprompter | `0x06-20` (Teleprompter), `0x0E-20` (DisplayConfig) |
| `TranslationTask` | Real-time translate | `0x05-20` (Translate) |

Tasks handle display lifecycle management: feature activation, display mode transitions (`G2DisplayMode`), and cleanup on exit. Teleprompter is the only feature requiring explicit `displayConfig` (`0x0E-20`) setup; other features use firmware-native display activation.

---

## BLE Services

### Package Structure (`even_connect`)

The BLE layer is isolated in the `even_connect` package (119 files) with a clean separation between device abstraction, protocol construction, and transport.

```
even_connect/
  EvenDeviceService        -- Base device abstraction
  BleG2Service             -- G2 glasses composite service
    BleG2CmdService        -- Command dispatch and routing
    BleG2CmdProto          -- Protocol/packet construction
    BleG2CmdTransport      -- Packet queue, split, retry, CRC
  BleG1Service             -- G1 glasses (legacy)
  BleRing1Service          -- R1 Ring service
  EvenDeviceDiscovery      -- BLE scanning
  EvenBeatHearPool         -- Heartbeat management
```

### EvenDeviceService

Base class for all device types. Provides:
- Connection state management
- Characteristic discovery and subscription
- Write queue with MTU-aware packet splitting
- Reconnection logic with exponential backoff

### BleG2Service

Composite service for G2 glasses. Manages three BLE pipe types:

| Pipe | Type | Characteristics | Purpose |
|------|------|----------------|---------|
| EUS (Even UART Service) | `BleG2PsType=0` | TX: `0x5401`, RX: `0x5402` | Protobuf control commands |
| EFS (Even File Service) | `BleG2PsType=1` | TX: `0x7401`, RX: `0x7402` | File transfer (BMP images, map tiles, documents) |
| ESS (Even Sensor Service) | `BleG2PsType=2` | TX: `0x6401`, RX: `0x6402` | Display telemetry (LFSR-scrambled, ~20Hz, 205 bytes/pkt) |

#### BleG2CmdService

Command dispatch layer that routes feature requests to the correct protocol constructor and transport pipe. Maintains command sequence counters and response callback registration.

#### BleG2CmdProto

Protocol construction with 19 data package creators (see [Data Packages](#data-packages)). Each creator builds a protobuf payload wrapped in the G2 packet format:

```
AA [21] [seq] [len] [total] [num] [svc_hi] [svc_lo] [payload] [CRC16-LE]
```

Where:
- `0x21` = TX direction (phone to glasses)
- `seq` = incrementing sequence counter
- `len` = payload_size + 2 (service ID bytes counted in length)
- CRC16/CCITT: init=0xFFFF, poly=0x1021, computed over payload only (skip 8-byte header)

#### BleG2CmdTransport

Packet queue and transport management:
- MTU-aware packet splitting for payloads exceeding BLE MTU
- Write queue with configurable concurrency
- Retry logic with timeout
- Transport ACK handling (8-byte header-only packets, no payload, no CRC)
- Sequence number management (glasses maintain independent RX sequence counter)

### BleG1Service

Legacy G1 glasses support. Uses raw byte protocol (not protobuf). Brightness example: `[0x01, level, auto]` -- this format does NOT work on G2.

### BleRing1Service

R1 Ring BLE service.

| Aspect | Detail |
|--------|--------|
| Service UUID | `BAE80001-4F05-4503-8E65-3AF1F7329D1F` |
| TX characteristic | `BAE80012` |
| RX characteristic | `BAE80013` |
| Init sequence | Write `0xFC`, wait 200ms, write `0x11` |
| Keepalive | `0x11` every 5 seconds (prevents BLE timeout) |
| DFU service | `FE59` (Nordic DFU) |

Features: file transfer, health data retrieval, system commands. Gesture-only input (no passive sensor events).

### EvenDeviceDiscovery

BLE scanning with:
- Service UUID filtering (G2 EUS, R1, G1)
- RSSI-based proximity sorting
- Duplicate filtering with configurable window
- Background scan support (Android foreground service required)

### EvenBeatHearPool

Heartbeat management for maintaining BLE connections:
- G2: Type `0x0E` heartbeat ONLY (types `0x0D`/`0x0F` cause pairing removal)
- Configurable interval (default matches firmware expectation)
- Per-eye heartbeat tracking (left and right eyes respond independently)
- Auth keepalive: type `0x06` on `0x80-01`

---

## Audio Pipeline

### Architecture

The audio pipeline spans three packages with native library support:

```
flutter_ezw_audio          -- Audio capture and ML enhancement
  libeven.so (30.5 MB)     -- On-device ML models
flutter_ezw_asr            -- Speech recognition
  Azure Speech SDK (8.5 MB) -- Cloud ASR/TTS
  Sherpa-ONNX (4.6 MB)     -- On-device ASR
flutter_ezw_lc3            -- BLE audio codec
  liblc3.so (173 KB)       -- LC3 codec
```

### Audio Capture

- Glasses microphone audio arrives on NUS RX with `0xF1` prefix (stripped before processing)
- G2 mic uses LC3 codec; the app receives raw PCM after decoding
- Mic control: NUS `[0x0E, 0x01]` (enable) / `[0x0E, 0x00]` (disable)
- Ring buffer for continuous capture with configurable lookback

### ML Enhancement (`libeven.so`)

On-device audio processing pipeline (runs without cloud dependency):

| Stage | Purpose |
|-------|---------|
| Speech enhancement | ML-based cleanup of glasses microphone audio |
| AGC (Automatic Gain Control) | Normalize audio levels |
| Noise reduction | Environmental noise suppression |
| BERT-based intent recognition | Local NLU for command classification before cloud dispatch |

### ASR (Speech Recognition)

Dual-provider architecture with automatic failover:

| Provider | Library | Mode | Use Case |
|----------|---------|------|----------|
| **Azure Speech Services** | `libMicrosoft.CognitiveServices.Speech.core.so` | Cloud | Primary -- best accuracy, requires connectivity |
| **Soniox** | Cloud API | Cloud | Secondary cloud provider |
| **Sherpa-ONNX** | `libsherpa-onnx-c-api.so` + `libonnxruntime.so` | On-device | Offline fallback -- works without internet |

The ASR engine helper in the AI Agent Service manages provider selection based on:
- Network connectivity (automatic switch to Sherpa-ONNX when offline)
- Language availability (not all languages supported by all providers)
- User preference (configurable in settings)

### Voice Activity Detection (VAD)

VAD helper provides:
- Speech start/end detection for automatic recording segmentation
- Energy-based + ML-based hybrid detection
- Configurable sensitivity thresholds
- VAD notifications sent to glasses via `0x07-00` (f1=2, G2VADNotification)

---

## Data Packages

The Android app's `BleG2CmdProtoExt` creates 20 data package types for BLE transmission. Each corresponds to a G2 protocol service.

| # | Method | Service ID | Purpose |
|---|--------|-----------|---------|
| 1 | `_createDashboardDataPackage` | `0x01-20` | Dashboard widget updates (calendar, weather, stocks, time, battery) |
| 2 | `_createConverseDataPackage` | `0x0B-20` | Conversate session control and text display |
| 3 | `_createTelepromptDataPackage` | `0x06-20` | Teleprompter text pages and scroll control |
| 4 | `_createEvenAiDataPackage` | `0x07-20` | AI agent commands (CTRL, ASK, REPLY, SKILL, PROMPT, EVENT) |
| 5 | `_createEvenHubDataPackage` | `0x07-20` | EvenHub app framework (shares service with EvenAI, distinguished by COMM_RSP f12.f1=8) |
| 6 | `_createNavigationDataPackage` | `0x08-20` | Navigation directions, icons, distances |
| 7 | `_createNotificationDataPackage` | `0x02-20` | Phone notification forwarding (JSON with `"android_notification"` key) |
| 8 | `_createQuickListDataPackage` | `0x0C-20` | Quicklist CRUD operations (command IDs 1-6) |
| 9 | `_createHealthDataPackage` | `0x0C-20` | Health metrics display (command IDs 10-12, multiplexed with Quicklist) |
| 10 | `_createMenuDataPackage` | `0x03-20` | Menu system display and selection |
| 11 | `_createLoggerDataPackage` | `0x0F-20` | Firmware log retrieval and streaming control |
| 12 | `_createOnboardingDataPackage` | `0x10-20` | Device onboarding flow (7 states) |
| 13 | `_createModuleConfigureDataPackage` | `0x20-20` | Per-eye brightness calibration and module settings |
| 14 | `_createRingDataPackage` | `0x91-20` | R1 Ring relay commands through G2 glasses |
| 15 | `_createSyncInfoDataPackage` | `0x0A-20` | Session initialization and time sync |
| 16 | `_createTranscribeDataPackage` | `0x0B-20` | Transcription mode (variant of Conversate) |
| 17 | `_createG2SettingDataPackage` | `0x0D-00` | Protobuf `G2SettingPackage` (brightness, units, display preferences) |
| 18 | `_createGlassesCaseDataPackage` | `0x81-20` | Case detection and battery queries (BoxDetect/DisplayTrigger) |
| 19 | `_createDevCfgDataPackage` | `0x0D-20` | Device configuration (20 setting IDs, 15 firmware-internal) |
| 20 | `_createFileTransmitDataPackage` | `0xC4/0xC5` | File transfer lifecycle (BMP images, map tiles, firmware chunks) |

All data packages use protobuf varint encoding. Payloads are wrapped in the G2 packet envelope with CRC16/CCITT computed over the payload bytes only.

---

## Device Settings Extensions

`BleG2CmdProtoDeviceSettingsExt` provides device management commands that operate outside the standard service-based data package model.

| Method | Description | Protocol Details |
|--------|-------------|-----------------|
| `sendHeartbeat` | Connection keepalive | Type `0x0E` on `0x80-00`. ONLY type `0x0E` is valid; `0x0D`/`0x0F` trigger pairing removal |
| `startPair` | Initiate 7-packet auth sequence | `0x80-00/0x80-20`. Auth success: f1=4, f3={f1=1} on `0x80-01` |
| `unpair` | Remove device pairing | Clears auth state on both phone and glasses |
| `createTimeSyncCommand` | Synchronize glasses clock | f128={f1=Unix timestamp, f3=timezone offset} |
| `connectRing` | Relay R1 Ring connection through G2 | Via `0x91-20` Ring relay service |
| `disconnect` | Clean disconnection | Graceful BLE teardown with state cleanup |
| `sendFile` | Initiate file transfer to glasses | Uses EFS pipe (`0x7401/0x7402`). 3-phase: fileCheck(0), data(1), complete(2) |
| `receiveFile` | Initiate file transfer from glasses | Reverse direction on EFS pipe |
| `selectPipeChannel` | Switch active BLE pipe | `PIPE_ROLE_CHANGE` for dynamic pipe switching between EUS/EFS/ESS |
| `quickRestart` | Restart glasses firmware | Soft reset without re-pairing |
| `restoreFactory` | Factory reset glasses | Full state wipe, requires re-pairing |

---

## Ring Extensions

`BleG2CmdProtoRingExt` provides R1 Ring-specific commands relayed through the G2 glasses BLE connection.

| Method | Description | Notes |
|--------|-------------|-------|
| `controlDevice` | Ring power and mode control | On/off, sleep/wake, DFU mode entry |
| `openRingBroadcast` | Enable Ring BLE advertising | Makes Ring discoverable for direct connection |
| `switchRingHand` | Change left/right hand orientation | Affects gesture direction interpretation |

Ring commands are sent via the `0x91-20` service (Ring relay protocol). The G2 glasses act as a BLE relay, forwarding commands to the R1 Ring over the inter-device link. Ring responses arrive on `0x91-00` as `G2RingRelayResponse` (type, messageId, payload).

The R1 Ring itself uses service UUID `BAE80001-4F05-4503-8E65-3AF1F7329D1F` with TX on `BAE80012` and RX on `BAE80013`. Direct Ring connections (bypassing G2 relay) use the init sequence: write `0xFC`, 200ms delay, write `0x11`, then `0x11` keepalive every 5 seconds.
