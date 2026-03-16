# Even Android App — New Findings vs iOS/Firmware Analysis

> Critical discoveries from Android APK reverse engineering (2026-03-14) that are NOT present in existing iOS Flutter or firmware documentation.

## BLE UUID Discovery

### Complete UUID Table (from Dart snapshot)
All Even UUIDs share base `00002760-08C2-11E1-9073-0E8AC72Exxxx`:

| UUID | Previously Known | Discovery |
|------|:---:|-------------|
| 0x0001 | No | Primary service declaration |
| 0x0002 | No | Service characteristic |
| 0x1001 | Partial | Confirmed in code (was "unknown" in firmware) |
| 0x5401 | Yes | EUS TX |
| 0x5402 | Yes | EUS RX |
| **0x5450** | **No** | **EUS GATT service declaration** |
| 0x6401 | Yes | ESS TX |
| 0x6402 | Yes | ESS RX |
| **0x6450** | **No** | **ESS GATT service declaration** |
| 0x7401 | Yes | EFS TX |
| 0x7402 | Yes | EFS RX |
| **0x7450** | **No** | **EFS GATT service declaration** |

**The x450 characteristics are GATT service declarations** — the "parent services" we identified in firmware strings but couldn't map. Each pipe has a triplet: TX (x401), RX (x402), service (x450).

## Protocol-Level Discoveries

### 1. NEW Service: Transcribe (BLE)
- `_createTranscribeDataPackage` — Dedicated BLE service for transcription
- `transcribe.pb.dart` / `transcribe.pbenum.dart` — Full protobuf definition
- Previously only seen as `TranscribeEventType` in proto files, now confirmed as a **distinct BLE service** separate from EvenAI and Translate
- This may share service ID with 0x04-xx (MessageNotify) or use an unassigned ID

### 2. NEW Service: SyncInfo
- `_createSyncInfoDataPackage` — New synchronization service
- `sync_info.pb.dart` / `sync_info.pbenum.dart` — Full protobuf definition
- Not present in any previous iOS or firmware analysis
- Likely used for data synchronization between phone and glasses (settings, state)

### 3. Conversate Protocol — Much Richer Than Known
New protobuf messages not in our iOS implementation:
- `ConversateKeypointData` — Real-time key point extraction
- `ConversateTagData` + `ConversateTagType` — Content tagging/categorization
- `ConversateTagTrackingData` — Tag tracking over time
- `ConversateTitleData` — Title/topic extraction
- `ConversateTranscribeData` — Transcription data within conversate
- `ConversateSettings` — Configurable settings
- `ConversateHeartBeat` — Service-specific heartbeat
- `ConversateStatusNotify` — Status notifications
- `ConversateErrorCode` — Error enumeration
- `ConversateActionCallback` — Action callback system

**Insight**: Conversate is far more sophisticated than our basic text display implementation. It includes real-time semantic analysis with key points, tags, and titles.

### 4. Teleprompter — File Management on Glasses
New protobuf messages:
- `TelepromptFileInfo` / `TelepromptFileList` / `TelepromptFileListRequest` — File catalog on glasses
- `TelepromptFileSelect` — Select file from glasses storage
- `TelepromptAISync` — AI voice synchronization
- `TelepromptTask` — Task scheduling
- `TelepromptScrollSync` — Scroll position sync
- `TelepromptMode` — Mode selection (manual/auto/AI)

**Insight**: Teleprompter can store and manage files directly on the glasses, not just stream from phone.

### 5. Dashboard — Bidirectional Protocol
- `DashboardReceiveFromApp` — Glasses receiving from app
- `DashboardRespondToApp` — Glasses responding to app
- `DashboardSendToApp` — Glasses initiating to app
- `DashboardReceiveFLAG` — Receive flag for tracking
- `DashboardMainPageState` — Dashboard page state protobuf
- `DashboardContent` — Content definition
- `DashboardDisplaySetting` / `DashboardGeneralSetting` — Settings protos

**Insight**: Dashboard is a full bidirectional protocol, not just push-from-phone.

### 6. Health Protocol — Structured Delivery
- `HealthDataPackage_CommandData` — Nested command structure
- `HealthEnvelope` — Wrapper/envelope for health data
- `HealthMultData` / `HealthMultHighlight` — Multi-value health data with highlights
- `HealthModuleType` — Typed health modules
- `HealthInfo` — Generic health info message

### 7. Display Modes — Three Explicit Types
```
display_mode_dual     — Dual-eye separate content
display_mode_full     — Full single content
display_mode_minimal  — Minimal overlay (notifications)
```
Previously we only had mode numbers (0, 1, 6, 11, 16) without these explicit names.

### 8. Gesture Control List Protocol
- `APP_Send_Gesture_Control` — Individual gesture command
- `APP_Send_Gesture_Control_List` — Complete gesture mapping
- Full gesture customization page in settings

## Architecture Discoveries

### 9. On-Device ML Pipeline (libeven.so)
- **30.5MB** native C++ library with:
  - BERT-based intent recognition (NLU)
  - Real-time speech enhancement
  - Noise reduction
  - AGC (Automatic Gain Control)
  - SSR smoothing
- Uses ONNX Runtime (16MB) for model inference
- Protobuf IPC between Dart and native layer
- **This enables offline voice commands without cloud dependency**

### 10. Triple ASR Provider Architecture
1. **Azure Speech Services** — Primary cloud ASR (8.5MB native SDK)
2. **Soniox** — Secondary cloud ASR via WebSocket (v2 recognizer)
3. **Sherpa-ONNX** — Offline on-device ASR (4.6MB + 16MB ONNX Runtime)

Selection via `transcribe_recognizer_factory.dart` and server-side `getASRConfig`.

### 11. AI Agent State Machine
Full state machine implementation:
```
idle → wakeup → asr → cmd_dispatch → ai → stay → idle
```
With: `VadHelper`, `AudioRingBuffer`, `TextStreamManager`, `CancellableFutureManager`

### 12. Conversate WebSocket
- Dedicated WebSocket connection for live Conversate sessions
- `websocket_manager.dart` / `websocket_callback.dart`
- Separate from main API — likely for low-latency AI cue streaming

### 13. Conversate Background Documents
- Can upload context/background files for AI to reference during conversations
- API: `createConverseBackground`, `getConverseBackgroundList`, `getConverseBackgroundStatus`
- AI uses these for context-aware cues

## API Discoveries

### 14. New API Endpoints
| Endpoint | Description |
|----------|-------------|
| `login6` | Login API version 6 |
| `getTranslateAiSummary` | AI summary of translation sessions |
| `batchQueryMetricWindow` | Batch health metric queries |
| `getGoMorePKey` | GoMore health platform integration |
| `isSnInBlacklist` | Serial number blacklist check |
| `getConverseBackgroundStatus` | Background doc processing status |
| `submitFeedbackWithLog` | Feedback with device log upload |

### 15. New API Domains
- `https://api2.ev3n.co` — Staging API (ev3n, not even)
- `http://192.168.2.113:8888` — Development server (internal IP leaked)
- `https://cdn2.evenreal.co` — Secondary CDN

### 16. Request Signing
- `signature_util.dart` — Requests are signed
- `even_certificate_util.dart` — SSL certificate pinning
- `encrypt_ext.dart` — Encryption utilities
- `auth_interceptor.dart` / `login_expired_interceptor.dart` — Token management

## Device Discoveries

### 17. R1 Ring — GoMore Integration
- `BleRing1CmdGoMoreExt` — GoMore health platform
- `getAlgoKeyStatus` / `setAlgoKey` — Algorithm key management
- GoMore provides advanced health analytics (HRV, stress, etc.)

### 18. R1 Ring — NV Data Recovery
- `BleRing1SystemNvRecover` — Non-volatile data recovery
- `getRingNv` / `uploadRingNv` API endpoints
- System for backing up and restoring ring configuration

### 19. R1 Ring — Comprehensive Health Data
| Model | Description |
|-------|-------------|
| `BleRing1HealthActivityAllDay` | Full day activity |
| `BleRing1HealthActivityDaily` | Daily breakdown |
| `BleRing1HealthCommonDaily` | Common daily metrics |
| `BleRing1HealthSleep` | Sleep analysis |
| `BleRing1HealthHourItem` | Hourly granularity |
| `BleRing1HealthPoint` + State | Real-time sensor data |

### 20. MCU Case Update
- `McuOtaUpgrade` mixin with `mcumgr_flutter`
- Separate from G2 EVENOTA update
- `McuManifest` / `McuManifestFile` for update packaging

## UI/Feature Discoveries

### 21. EvenHub Hot Apps
- `HotAppInfo` / `HotAppList` — App store for glasses
- `HotAppOsType` — OS type enum (cross-platform apps)
- Server-delivered app catalog

### 22. Inbox/Messaging System
- `inboxList`, `inboxUnreadCount`, `inboxMarkAsRead`, `inboxDelete`
- `MsgBubble` model — In-app messaging
- Push notifications via FCM

### 23. User Balance / Monthly Usage
- `UserBalance` — Account balance tracking
- `MonthlyUsed` — Monthly usage metrics (likely for AI quota)

### 24. Glasses Lens Info
- `GlassesLenseInfo` / `GlassesLenseType` — Lens type tracking
- Likely for optical correction profiles

### 25. Notification Listener Service
- `EvNLService` — Android NotificationListenerService
- Intercepts ALL device notifications for forwarding to glasses
- `foregroundServiceType="specialUse"` — Runs as foreground service

### 26. Background Audio Recording
- `RECORD_AUDIO_BACKGROUND` permission
- `AudioRecordingService` with `foregroundServiceType="microphone"`
- Enables continuous mic capture for Conversate/Translate while backgrounded

## Deep Native Analysis (from libeven.so agent)

### 27. BERT NLU — 29 Voice Command Intents
The on-device BERT model classifies voice commands into these intents:

**Feature activation:**
- `CONVERSATE_ON`, `NAVI_ON`, `TELEP_ON`, `TRANSC_ON`, `TRANSL_ON`, `DISP_ON`, `SILENT_ON`, `DP_OFF`

**Brightness control:**
- `DISP_BRIGHT_AUTO_OFF/ON`, `DISP_BRIGHT_DEC/INC/MAX/MIN/SET`

**Display distance (NEW — not in firmware):**
- `DISP_DIST_DEC/INC/MAX/MIN/SET`

**Display height (NEW — not in firmware):**
- `DISP_HT_DEC/INC/MAX/MIN/SET`

**Notifications:**
- `NOTIFY_CLEAR`, `NOTIFY_OFF`, `NOTIFY_ON`, `NOTIFY_SHOW`

**Entity types:** `FROM_LAN` (source language), `TO_LAN` (target language), `TRANSP` (transport/destination)

### 28. llama.cpp — On-Device LLM
libeven.so includes a **full llama.cpp build** supporting 98 model architectures (llama, qwen, qwen2, qwen3, deepseek, deepseek2, gemma, phi, command_r, etc.). GGUF model loading is supported. This enables on-device LLM inference for the EvenAI feature.

### 29. Silero VAD Models
Two Voice Activity Detection ONNX models bundled:
- `silero_vad.onnx` (2.3MB) — v4
- `silero_vad.v5.onnx` (2.3MB) — v5

### 30. Audio EQ ONNX Model
- `modeleqlayer4_388_9.onnx` (1.9MB) — Audio equalization/processing model

### 31. EvenEmoji Custom Font
- `EvenEmoji-Regular.ttf` (57KB) — Custom emoji font for glasses display (limited glyph set for 576x288 Gray4)
- **Not present in iOS build**

### 32. Even C++ FFI Exports (Dart→Native)
```
even_start, bert_load_model, bert_infer
speech_enhance_load_model, speech_processor_process/set_config/reset
even_ai_smoother_set_para/update/reset
translate_one_way_smoother_set_para/update/reset
```

### 33. API Keys Discovered (from strings.xml)
- Firebase project: `even-app-f488c`
- Mapbox token: `pk.eyJ1IjoidG9tb3V5YW5nIi...` (user: `tomouyang`)
- GCM sender ID: `258827750841`

### 34. App Version
- Android: **v2.0.8 build 42** (newer than iOS v2.0.7 build 394)
- Min SDK: 28 (Android 9), Target SDK: 35 (Android 15)

## Pass 3: Deep Protobuf & Asset Findings

### 35. EvenHub Container Display Model
The EvenHub uses a **container-based display model** with typed containers:
- `CreateStartUpPageContainer` / `RebuildPageContainer` / `ShutDownContaniner`
- `ImageContainerProperty`, `TextContainerProperty`, `ListContainerProperty`, `List_ItemContainerProperty`
- Container events: `Sys_ItemEvent`, `Text_ItemEvent`, `List_ItemEvent`
- Matching OS_RESPONSE_* constants for every command

### 36. Complete Oneof Field Structures
Every DataPackage uses `oneof commandData` with named fields matching our protobuf analysis. Key confirmed field names:
- `magicRandom` — dedup counter (Conversate, Teleprompter, Translate, Settings)
- `modeLocked` — Translate mode lock state (NEW)
- `vadStatus`, `skillId`, `promptType` — EvenAI typed fields
- `multData`, `singleData`, `multHighlight`, `singleHighlight` — Health data variants

### 37. DeviceInfo Sub-Messages
- `ALSInfo` — Ambient Light Sensor data
- `HeadAngle` — Head tilt angle
- `BleMac`, `SnInfo`, `Mode` — Device identification

### 38. Auth/DevPairManager Messages
- `AuthMgr` — Authentication manager message
- `BleConnectParam` — Connection parameters
- `DisconnectInfo` / `UnpairInfo` — Disconnect/unpair notifications
- `PipeRoleChange` — Pipe role switching (part of auth protocol!)

### 39. G2 Hardware Revisions
Device images confirm **two hardware revisions** (G2-A and G2-B), each in 3 colors (brown, green, grey).

### 40. Dashboard Page Types
- `PAGE_TYPE_DASHBOARD_MAIN`, `PAGE_TYPE_CALENDAR_EXPANDED`, `PAGE_TYPE_HEALTH_EXPANDED`
- `PAGE_TYPE_NEWS_EXPANDED`, `PAGE_TYPE_QUICKLIST_EXPANDED`, `PAGE_TYPE_STOCK_EXPANDED`

### 41. Logger File Management
- `ble_trans_level_msg`, `delete_file_msg`, `request_filelist_msg`
- `DELETE_ALL_LOGGER_FILE` command

### 42. ModuleConfigure Revealed
- `dashboard_general_setting` — Dashboard-level general settings
- `send_system_general_setting` — System-level general settings broadcast

### 43. EvenAI Sentiment Analysis
- `EvenAISentiment` — AI can analyze message sentiment
- Available via `/v2/g/jarvis/message/sentiment` API

### 44. Quicklist OS Handling Patterns
- `OS->App osSetNoteStatus:` — Individual note status updates
- `OS->App osSetNoteStatus(batch): total=` — Batch status updates
- `OS->App paging:` — Paging support for large lists

### 45. Health OS Handling Patterns
- `OS->App SINGLE` / `MULT` / `RAW_DATA` / `EVENT` / `ITEM` — 5 distinct delivery patterns
- Battery level included in RAW_DATA: `OS->App RAW_DATA handled: batt=`

## Summary of Action Items

Based on these findings, potential improvements to our Swift SDK:

1. **Implement Transcribe BLE service** — Dedicated service separate from EvenAI
2. **Implement SyncInfo service** — Data synchronization
3. **Enrich Conversate protocol** — Add keypoint, tag, title, transcribe data
4. **Teleprompter file management** — File list/select on glasses storage
5. **Dashboard bidirectional** — Implement receive/respond from glasses
6. **Add display mode names** — dual/full/minimal
7. **Ring health data models** — Activity, sleep, hourly granularity
8. **GoMore integration** — Health platform via Ring
9. **Background document upload** — For Conversate AI context
10. **On-device ASR** — Sherpa-ONNX integration for offline use
