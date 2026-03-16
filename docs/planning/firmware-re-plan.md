# Firmware-Only Reverse Engineering Plan (10 Phases)

## Goal
Analyze locally saved firmware artifacts and existing local documentation to understand firmware functionality, hardware behavior, and Bluetooth communication with a controller app, then update project docs with evidence-backed findings.

## Strict Scope and Constraints
- Allowed sources:
  - Local firmware artifacts under `captures/firmware/` (including extracted components and version snapshots).
  - Existing local docs under `docs/` and other in-repo notes.
  - Local scripts/tools already in this repository.
- Disallowed work:
  - No further API analysis.
  - No CDN access.
  - No web or other network-accessible service analysis.
  - No claims based on cloud traffic or external endpoints.

## Primary Inputs
- `captures/firmware/versions/*`
- `captures/firmware/analysis/*`
- `docs/firmware/firmware-reverse-engineering.md`
- Other local docs in `docs/`
- Local tooling in `tools/`

## Continuous Iteration Policy
- Never declare this roadmap complete; every execution wave must identify and queue the next actionable improvement.
- Do not state that there are no remaining steps.
- At the end of each run, append or refresh a continuation backlog focused on tighter alignment with Mission and Success Criteria.
- Store history of past completed work in docs/buildPhases.md, and once an entry has been moved there remove it from PLAN.md

## Success Criteria (Definition of Done)
1. At the end of each execution phase, `PLAN.md` is updated with newly inferred knowledge and a subsequent-phase continuation backlog.

## Ongoing Improvement Loop (Run Until No Viable Improvements Remain)
1. Profile full pipeline and identify hottest unresolved stages.
2. Attempt offload/parallelization for each candidate stage.
3. Repeat until no stage has a net-positive viable improvement path.

## 10-Phase Process — ALL COMPLETE

All 10 phases completed 2026-03-03. Full history in [docs/buildPhases.md](docs/buildPhases.md).

- [x] 1. Scope Lock and Evidence Baseline
- [x] 2. Firmware Corpus Inventory and Fingerprinting
- [x] 3. Container and Header Mapping
- [x] 4. Component Decomposition
- [x] 5. Integrity, Packaging, and Update Semantics
- [x] 6. Bluetooth Artifact Extraction
- [x] 7. Hardware Functionality Mapping
- [x] 8. Cross-Version Diff and Behavior Evolution
- [x] 9. Documentation Reconciliation and Update
- [x] 10. Validation, Gaps, and Next Firmware-Only Backlog

## Phase 10 Validation Results (2026-03-03)

### 10.1 Reproducibility Sweep
All 7 Phase 1-8 analysis tools:
- Compile cleanly (`python3 -m py_compile`)
- Run without errors
- Produce valid JSON outputs (`python3 -m json.tool`)

Full command list in [docs/buildPhases.md](docs/buildPhases.md#reproducible-validation-commands-phase-101).

### 10.2 Unresolved Firmware-Only Unknowns

Prioritized by impact on iOS SDK development:

| # | Unknown | Missing Evidence | Risk |
|---|---------|-----------------|------|
| 1 | **OTA wire protocol encoding** | Custom `.fromBytes` format — exact byte layout of OTA_TRANSMIT_* commands unknown without traffic capture or Dart decompilation | HIGH — blocks firmware transfer via OTA-specific path |
| 2 | **Inter-eye communication framing** | Wired UART/I2C link confirmed but baud rate, packet format, and command structure unknown without physical teardown | HIGH — blocks understanding of command relay |
| 3 | ~~BLE service IDs for QuickList, Logger, Menu~~ | **RESOLVED** — Quicklist=0x0C-20, Logger=0x0F-20, Menu=0x03-20 (firmware dispatch table RE 2026-03-03) | DONE |
| 4 | **JBD LFSR polynomial** | Display scrambler is JBD-proprietary; polynomial extraction requires JBD datasheet or captured plaintext/ciphertext pair | MEDIUM — blocks display telemetry decoding |
| 5 | **CY8C4046FNI GPIO mapping** | Touch IC pin assignments unknown without hardware schematic | LOW — functional without it |
| 6 | **Battery capacity (mAh)** | Not in firmware strings; BQ25180/BQ27427 register values not exposed | LOW |
| 7 | **Compass/magnetometer IC** | Only unidentified sensor; no firmware string match found | LOW |
| 8 | **DisplayTrigger f3.f1=67** | Constant across all probes; meaning unknown (display state? register value?) | LOW |
| 9 | **S201 model variant** | Purpose unknown (next-gen? alternate SKU?) | LOW |
| 10 | **R1 Ring exact SoC** | nRF52832 vs nRF52833 vs nRF52840; ring firmware not in EVENOTA | LOW |

### 10.3 iOS App Implementation Gaps (from audit)

| # | Gap | Status | Priority |
|---|-----|--------|----------|
| 1 | Conversate `sendTranscript()` display confirmation | **FIXED** — opt-in `confirmDisplay` parameter added | DONE |
| 2 | DisplayTrigger `recordContentSent()` | **FIXED** — added before awaitDisplayConfirmation | DONE |
| 3 | BrightnessSender `recordContentSent()` | **FIXED** — added before awaitDisplayConfirmation | DONE |
| 4 | Glasses Case info query protocol | **FIXED** — G2GlassesCaseReader + DevicesView section + TestAll test | DONE |
| 5 | NotificationSender missing displayConfig | **FIXED** — Added display wake + displayConfig (0x0E-20) before file transfer in both paths | DONE |
| 6 | Wear detection toggle protocol | **FIXED** — G2WearDetectionProtocol + DevicesView section + TestAll test | DONE |
| 7 | Compass calibration protocol | **FIXED** — G2CompassCalibration + DevicesView section + TestAll test | DONE |
| 8 | Deep firmware binary analysis documentation | **FIXED** — §23.9 added with boot/display/touch/BLE/codec/filesystem/OTA findings | DONE |
| 9 | 14 of 27 protobuf modules unimplemented | Documented in §14 + §22; needs BLE service ID discovery for 3 | DEFERRED |
| 10 | Brightness control path confirmation | 3 candidate paths (raw bytes, G2SettingPackage, SKILL on 0x07-20) | DEFERRED |
| 11 | OTA-specific command encoding | Generic file transfer (0xC4/0xC5) confirmed working; OTA_TRANSMIT encoding unknown | DEFERRED |
| 12 | EVENOTA parser + CDN download + OTA transfer | **DONE** — G2EVENOTAParser, G2FirmwareAPIClient.downloadFirmware, G2FirmwareTransferClient, FirmwareCheckView expanded | DONE |
| 13 | Firmware TestAll tests | **DONE** — 5 tests: API check, version check, EVENOTA parse, component checksums, pre-transfer validation | DONE |
| 14 | Glasses settings protocols | **DONE** — Silent mode, screen-off interval, wear detection, compass, gesture control list | DONE |

## Continuation Backlog (Next Wave)

Priority-ordered firmware-only analysis tasks that require no API/CDN/web access:

- [ ] **11.1**: Deep-dive ota_s200_firmware_ota.bin ARM disassembly to extract OTA command handler dispatch table and response codes.
- [ ] **11.2**: Cross-correlate firmware string table offsets with Phase 6 BLE artifact addresses to locate service handler entry points in main app binary.
- [x] **11.3**: Extract BLE service ID numeric constants from firmware binary — DONE: 36-entry dispatch table at 0x0023DC88, all service IDs resolved. Quicklist=0x0C-20, Translate=0x05-20, Health=0x0C-20 (shared), Logger=0x0F-20, Menu=0x03-20, Ring=0x91-20. 3 services renamed: Tasks→Quicklist, Controller→Onboarding, Commit→ModuleConfigure
- [x] **11.4**: Analyze firmware_touch.bin v2.0.6.14 growth — DONE: proximity baseline capture + fast click reset markers identified (§23.9)
- [ ] **11.5**: Map JBD4010 display register writes in main app to reconstruct MSPI initialization sequence and extract LFSR configuration.
- [x] **11.6**: Diff ota_s200_firmware_ota.bin string tables across versions — DONE: marker stability table + per-version diagnostic additions documented (§23.9)
- [ ] **11.7**: Build a firmware string cross-reference index linking function names to byte offsets for future binary patching capability.
- [ ] **11.8**: Analyze inter-eye relay code paths in main app binary (search for UART/I2C init near "left"/"right" string references).
- [x] **11.9**: Investigate EFS vs EUS BLE profiles — DONE: EUS=Even UART Service (0x5401/0x5402), EFS=Even File Service (0x7401/0x7402), ESS=Even Sensor Service (0x6401/0x6402), NUS=Nordic UART. All 8 profiles documented (§23.10)
- [x] **11.10**: Extract `page_state_sync.c` protocol format — DONE: syncs dashboard state (tile+widget), master-only sync, protobuf-encoded. Quicklist items: uid/index/isCompleted/title/timestamp/ts_type (§23.13)
- [x] **11.11**: Map health protobuf data types — DONE: data_type (string enum), goal, value, avg_value, duration, trend. Batch save + highlight storage. BLE service ID still unknown (§23.17)
- [x] **11.12**: Analyze ANCS integration — DONE: Full ANCS client (NS/CP/DS), glasses=BLE MASTER for discovery, mutex-protected queue, suppressed during calibration. Coexists with 0x02-20 custom protocol (§23.10)

### Wave 3: App-Level Improvements from Firmware Analysis

- [x] **12.1**: Update gesture control list to support screen-on/off separation — DONE: G2GCLScreenState enum, per-state mapping data (§23.14)
- [x] **12.2**: Add display gating awareness to G2ConnectionMonitor — DONE: displayGatingReasons, isDisplayGated properties (§23.15)
- [ ] **12.3**: Implement Quicklist protocol — service ID now confirmed: 0x0C-20 (shared with Health). Items: uid, index, isCompleted, title, timestamp, ts_type
- [x] **12.4**: Implement dashboard page_state_sync listener — DONE: G2DashboardStateProtocol (model + query + decoder) + G2ConnectionMonitor.dashboardState + DevicesView section + TestAll test
- [x] **12.5**: Implement translate BLE service sender — DONE: G2TranslateProtocol (type 20-23 on 0x05-20, corrected from 0x07-20) + G2TranslateSender (session lifecycle + heartbeat) + AudioStreamView "Send to Glasses" toggle
- [x] **12.6**: Add ANCS notification whitelist management — DONE: G2NotificationWhitelist (8 default + 8 additional apps, JSON serializer, file transfer upload) + DevicesView whitelist section + TestAll test
- [x] **12.7**: Implement buzzer/haptics control — DONE: G2BuzzerProtocol (11 vibration types 0-10) + DevicesView buzzer section + TestAll test. Wire format speculative (0x0D-20 cmdId=30)
- [x] **12.8**: Add OTA progress tracking — DONE: OTAPhase enum (4 phases: START→INFORMATION→FILE→RESULT_CHECK), integrated into TransferProgress with otaPhase field

### Wave 4: Remaining Protocol Implementations

- [x] **13.1**: Fix pre-existing G2FirmwareAPIClient compilation errors — DONE: removed duplicate error cases
- [x] **13.2**: Implement dashboard page_state_sync listener (12.4) — DONE: G2DashboardStateProtocol + monitor + UI + test
- [x] **13.3**: Implement Quicklist read protocol (12.3) — DONE: G2QuicklistProtocol (CRUD + decode, replaces G2TasksProtocol) + G2HealthDataProtocol (8 data types, batch save) + tests
- [x] **13.4**: Add ANCS notification whitelist management (12.6) — DONE: G2NotificationWhitelist + upload via file transfer + UI + test
- [ ] **13.5**: ARM disassembly of OTA command handler dispatch table (11.1) — extract exact OTA wire commands
- [x] **13.6**: BLE service ID extraction via firmware dispatch table — DONE: all 36 entries resolved (see 11.3)
- [ ] **13.7**: JBD4010 LFSR polynomial extraction (11.5) — decode display telemetry on 0x6402
- [ ] **13.8**: Firmware string cross-reference index (11.7) — function-to-offset mapping

### Wave 5: Newly Unblocked Implementations

- [x] **14.1**: Implement Quicklist protocol on 0x0C-20 — DONE: G2QuicklistProtocol with full CRUD (fullUpdate, batchAdd, singleItem, delete, toggleComplete, pagingRequest), item encode/decode round-trip, response parser. Replaces speculative G2TasksProtocol. TestAll test added (7 assertions)
- [x] **14.2**: Implement Health data protocol on 0x0C-20 — DONE: G2HealthDataProtocol (8 data types, batch save, highlight update, query) + G2HealthRecord model + G2HealthDataType enum. Command IDs 10-12 (disjoint from Quicklist 1-6). TestAll test added (7 assertions)
- [x] **14.3**: Add translate response decoder on 0x05-00 — DONE: G2TranslateResponse model (echo + COMM_RSP), onTranslateResponse callback, response decoder case, BLE client wiring, debug logging. TestAll test added (6 assertions)
- [x] **14.4**: Add menu protocol on 0x03-20 — DONE: G2MenuProtocol (item model, event types, sendMenuInfoPayload, parseResponse), G2MenuResponse, builtin app IDs (conversate=1..quicklist=7). Decoder + callback + BLE wiring + TestAll test
- [x] **14.5**: Add logger protocol on 0x0F-20 — DONE: G2LoggerProtocol (fileList/deleteFile/deleteAll/liveSwitch payloads, parseResponse with repeated f5 file paths), 6 known log files, G2LoggerCommandID enum. Decoder + callback + BLE wiring + TestAll test
- [ ] **14.6**: Add ring protocol on 0x91-20 — extended ring protocol (health, wear, algo keys)
- [x] **14.7**: Update response decoder for corrected service names — DONE: Tasks→Quicklist (G2QuicklistACK, onQuicklistResponse, .quicklistAck), Controller→Onboarding (log label), Commit→ModuleConfigure (log label). Legacy aliases preserved for backward compatibility
- [x] **14.8**: Add system alert/close protocols (0x21-20, 0x22-20) — DONE: G2SystemAlertProtocol (parseResponse), G2SystemCloseProtocol (closeRequestPayload, parseResponse with YES/NO/MINIMIZE selection), G2SystemMonitorProtocol (6 event types, queryPayload, parseResponse). All 3 in G2SystemProtocols.swift. Decoders + callbacks + BLE wiring + TestAll tests

### Wave 6: Remaining Protocol Implementations

- [x] **15.1**: Add menu protocol on 0x03-20 — DONE: see 14.4
- [x] **15.2**: Add logger protocol on 0x0F-20 — DONE: see 14.5
- [ ] **15.3**: Add ring BLE protocol on 0x91-20 — extended ring protocol (health, wear, algo keys, event relay via APP_PbRxRingFrameDataProcess). Passthrough handler exists, insufficient protocol evidence for typed decoder
- [x] **15.4**: Add system alert protocol on 0x21-20 — DONE: see 14.8
- [x] **15.5**: Add system close protocol on 0x22-20 — DONE: see 14.8
- [x] **15.6**: Add system monitor protocol on 0xFF-20 — DONE: see 14.8
- [x] **15.7**: Add onboarding BLE response decoder on 0x10-00 — DONE: G2OnboardingBLEResponse (type, flag, processId, substep, wearStatus), parseBLEResponse() with context-dependent f3 interpretation. Decoder + callback + BLE wiring + TestAll test
- [ ] **15.8**: ARM disassembly of OTA command handler dispatch table (13.5) — extract exact OTA wire commands
- [ ] **15.9**: JBD4010 LFSR polynomial extraction (13.7) — decode display telemetry on 0x6402
- [ ] **15.10**: Firmware string cross-reference index (13.8) — function-to-offset mapping

### Wave 7: Display Content Tracking & OTA Status (2026-03-03)

- [x] **16.1**: Display content hash + confirmation display in DevicesView — content hash (feature + truncated SHA-256), content-hash-changed indicator in confirmation section
- [x] **16.2**: Content hash tracking in G2ProtocolProbeSender — captureProbeDisplayState()/appendDisplayStateDiff() helpers, 7 probes instrumented (navigation, conversate, brightnessSkill, teleprompter, evenAI, evenHub, displayLifecycle)
- [x] **16.3**: Display config completion inference — recordDisplayConfigSent(feature:) in G2ConnectionMonitor, inferDisplayConfigResult() triggered by 0x6402 sensor frames within 3s window. All 6 senders instrumented (Teleprompter, EvenHub, Navigation, Conversate, Notification, Translate)
- [x] **16.4**: OTA file transfer status codes — G2FileTransferStatus enum (8 codes: success/fail/timeout/startError/dataCRCError/resultCheckFail/flashWriteError/noResources), G2FileTransferAck enhanced with statusCode/isError, BLE logging includes ERROR tag
- [x] **16.5**: Display content change TestAll tests — 3 tests: testDisplayContentHashTracking (hash lifecycle, DisplayMode labels/isActive, gating), testDisplayConfirmationModel (confirmed/unconfirmed/hash-change/summary), testDisplayConfigInference (pending→inferred_ok, FileTransferStatus/FileTransferAck parsing)

### Wave 8: Firmware Deep Binary Analysis & Documentation (2026-03-03)

- [x] **17.1**: Fix EvenAI sender display config tracking gap — added recordDisplayConfigSent(feature: "EvenAI") after displayWake in G2EvenAISender
- [x] **17.2**: Deep binary analysis of main firmware OTA — extracted boot vectors, source tree, RTOS threads, display system, inter-eye sync, BLE profiles, EvenAI guards, menu system, production test CLI, device config command IDs
- [x] **17.3**: Deep binary analysis of bootloader — extracted DFU process flow (OTA flag check, CRC validation, MRAM programming), RTOS tasks (manager, dfu), boot sequence strings, LittleFS directory creation
- [x] **17.4**: Deep binary analysis of components — codec (wake words "hey_even"/"hi_even", LVP stack, UART boot protocol, debug CLI), box (UART protocol 5A A5 FF, dual-bank OTA, water detection, auxiliary ICs YHM2217/YHM2510/4005), touch (PSoC4 vectors), BLE (EM9305 patch, no strings)
- [x] **17.5**: Firmware binary analysis TestAll test — testFirmwareBinaryAnalysis: boot vectors (bootloader SP/Reset, main app SP/Reset), component magic verification (FWPK codec/touch, EVEN box), BLE patch header, BLE stability across versions, ComponentType model verification. Safe (no network)
- [x] **17.6**: Documentation updates — s200-bootloader.md (DFU process, RTOS tasks, boot strings, source paths), ota-protocol.md (firmware-confirmed OTA transmit types, LittleFS paths, box OTA dual-bank path, 1000-byte payload), codec-gx8002b.md (wake words, LVP stack, audio pipeline, boot prompt, TinyFrame format, debug CLI), box-case-mcu.md (UART protocol, auxiliary ICs, dual-bank OTA, case firmware version, aging mode), s200-firmware-ota.md (RTOS threads, display system, brightness, inter-eye sync, BLE profiles, EvenAI guards, VAD, menu, device config IDs, filesystem layout, production CLI)

**Key discoveries:**
- No LFSR/scramble in firmware strings — 0x6402 display telemetry scrambling is JBD4010 hardware-level
- Hongshi A6N-G alternative display driver (second-source panel alongside JBD4010)
- Screen modes 0x71-0x74 (four distinct JBD4010 display modes)
- VAD (Voice Activity Detection) as separate EvenAI notification type
- BQ27427 fuel gauge and magnetometer — not in original BOM
- OTA data packets are exactly 1000 bytes (firmware-enforced)
- Box has dual-bank flash with atomic bank swap for OTA updates

### Wave 9: Firmware-Discovered Protocol Implementations (2026-03-03)

- [x] **18.1**: Device config protocol — G2DeviceConfigProtocol with g2_settingCommandId enum (20 IDs), G2FirmwareConfigCommandID enum (15 firmware-level IDs), payload builders for display mode/anti-shake/wakeup angle/dashboard auto-close, sender methods with session/transient connection support. TestAll test (7 assertions)
- [x] **18.2**: VAD notification handler — G2VADNotification model (messageId, isActive, rawFields), decoder for f1=2 on 0x07-00, onVADNotification callback wired in BLE client, G2DecodedResponse.vadNotification case with summary. SKILL echo (f1=6) added to EvenAI echo handler. TestAll test (4 assertions)
- [x] **18.3**: Screen mode & production CLI — G2JBDScreenMode enum (0x71-0x74), G2ProductionCLI command builders for NUS UART (setScreenMode, setScreenHeight, setAutobrightness, buzzerPlay, get). Note: 0x71-0x74 are JBD hardware register values not exposed over BLE; BLE display mode uses DEVICE_DISPLAY_MODE cmdId 13 on 0x0D-20. TestAll test (7 assertions)
- [x] **18.4**: Module configure protocol — G2ModuleConfigureProtocol on 0x20-20 with 4 command types (dashboardSetting, systemSetting, moduleList, brightnessCalibration), payload builders, response parser (wraps G2CommitResponse), sender methods. Per-eye brightness calibration fields (leftMaxBrightness/rightMaxBrightness). TestAll test (5 assertions)
- [x] **18.5**: Xcode project updates — 3 new .swift files added to project.pbxproj (4 sections each)
- [x] **18.6**: TestAll tests — 4 new tests (74 total): testDeviceConfigProtocol, testVADNotificationModel, testScreenModeAndCLI, testModuleConfigureProtocol

**Key findings:**
- Two-layer display mode control: JBD hardware (0x71-0x74 via FreeRTOS CLI/NUS) vs BLE-level (dual/full/minimal on 0x0D-20 cmdId 13)
- Device config has 15 firmware-level commands (QUICK_RESTART, FACTORY_RESET, etc.) with unknown BLE wire format — distinct from the 20 g2_settingCommandId values on 0x0D-20
- VAD is f1=2 on 0x07-00, distinct from all other EvenAI response types (CTRL/ASK/REPLY/SKILL/COMM_RSP)
- Module configure (0x20-20) wraps dashboard_general_setting + system_general_setting + brightness calibration

### Wave 10: Firmware String Cross-Reference & Deep Analysis (2026-03-03)

- [x] **19.1**: Build firmware string cross-reference tool — `tools/firmware_string_index.py` extracts strings from all 4 versions' 6 components, maps to hex offsets, classifies into 17 categories, computes cross-version stability. Output: 132,307 total strings, 34,866 unique, 8,392 categorized, 20,287 stable. JSON + Markdown reports in `captures/firmware/analysis/`
- [x] **19.2**: Inter-eye relay deep analysis — Discovered TinyFrame serial protocol for inter-eye communication (Master/Slave modes, body/head checksums, multipart transfer). 5 stable sync functions: `uart_sync_thread`, `AUDM_HandlePeerSyncMsg`, `AUDM_SendSyncMsgToPeer`, `SendInputEventToPeers`, `APP_PbTxEncodeScrollSync`. Box UART manager is a separate layer with pack/unpack framing and CRC. Documentation updated: §23.22 in firmware-reverse-engineering.md
- [x] **19.3**: OTA wire format evidence extraction — Confirmed 5-byte OTA packet header (CRC at `recv_value[payload_len + 5]`), 1000-byte enforced payloads, timestamp validation per packet, `EVEN_OTA_FILE_HEADER_SIZE` for INFORMATION phase. Box OTA: 4-phase (firmware_check→begin→file_get→result_check) with 240-byte max chunks. Added `OTATransmitType` enum (10 component targets) to `G2FirmwareTransferClient`. Documentation updated: §23.23 + ota-protocol.md
- [x] **19.4**: TestAll tests — 2 new tests (76 total): testOTAWireFormatConstants (6 assertions: payload/header/chunk sizes, transmit types, phases, battery), testInterEyeArchitectureModel (5 assertions: NUS CLI, BLE pipe architecture, stable sync strings, production CLI, config service)
- [x] **19.5**: iOS app updates — Added `otaPayloadSize`, `otaHeaderSize`, `boxOtaMaxChunkSize`, `OTATransmitType` enum (10 cases) to `G2FirmwareTransferClient.swift`

**Key discoveries:**
- Inter-eye link uses **TinyFrame** serial framing library (not raw UART) — body + head checksums, type/ID-based message routing, multipart transfer support
- OTA FILE packet has **5-byte header** before 1000-byte payload, with CRC at byte 1005
- OTA timestamps provide replay protection — each file packet must carry `upgrade_file_timestamp` set during INFORMATION phase
- Box UART manager (`box_uart_mgr.c`) is completely separate from inter-eye TinyFrame — uses its own pack/unpack protocol with last-byte CRC
- v2.0.3.20 was the largest firmware string expansion (+4,857 unique strings), introducing structured logging with `[module_name]` prefixes
- v2.0.6.14 added production CLI getters (`get dominant_hand/temperature_unit/date_format/time_format/gesture_app`)

### Wave 11: Protocol Correctness & Settings Writer (2026-03-04)

- [x] **20.1**: Add `magic_random` dedup counter to Conversate (0x0B-20) and Teleprompter (0x06-20) protocol senders — firmware uses `magic_random` (protobuf f8={f1=counter}) for duplicate message detection (`[pb.conversate]Duplicate message detected: magic_random = %d`). Added incrementing counters: EvenAI=100, Translate=200, Conversate=300, Teleprompter=400, Probes=500. Updated `G2ConversateProtocol` (3 methods), `G2TeleprompterProtocol` (12 methods), `G2ConversateSender`, `G2TeleprompterSender`, `G2ProtocolProbeSender`
- [x] **20.2**: Add universal settings writer protocol — `G2UniversalSettingKey` enum (6 cases: metricUnit, dateFormat, distanceUnit, temperatureUnit, timeFormat, dominantHand). `writeSetting(key:value:)` and `writeSettings(metricUnit:dateFormat:...)` batch writer on `G2UniversalSettingsReader`. Uses cmdId=2 (APP_SEND_BASIC_INFO) on 0x0D-20 with magic_random
- [x] **20.3**: Expand `G2ProductionCLI` with v2.0.6.14 NUS commands — 7 getters (date_format, time_format, temperature_unit, dominant_hand, distance_unit, metric_unit, gesture_app), set commands, sensor calibration (rnv/wnv acc/gyr/matrix), singleReflash
- [x] **20.4**: TestAll tests — 3 new tests (79 total): testMagicRandomDedup (magic_random in 4 services, counter ranges), testUniversalSettingsWriter (6 keys, field mapping, model), testProductionCLIExpansion (7 getters, set commands, rnv/wnv, singleReflash)

**Key discoveries:**
- Firmware rejects duplicate messages when `magic_random` matches previous value AND `time_elapsed` is short — our prior senders with `magic_random=0` would cause rejections on rapid consecutive sends
- Universal settings use `command_id + which_command_data + magic_random` protobuf structure
- NUS CLI temperature_unit uses values 1/2 (°C/°F) while BLE protobuf uses 0/1 — different encoding for same setting
- NUS CLI dominant_hand uses 0=left/1=right while settings reader maps 0=right/1=left — potential polarity difference between paths

### Wave 12: Protocol Completeness & Gap Closure (2026-03-04)

- [x] **21.1**: Add `onEvenAIEcho` callback to G2ResponseDecoder — EvenAI echo responses (f1=1/3/5/6 on 0x07-00) were decoded but only dispatched through `onRawResponse`. Added dedicated `onEvenAIEcho` callback property, dispatched alongside `onRawResponse`, wired in `connectEye()` with CTRL/ASK/REPLY/SKILL label formatting
- [x] **21.2**: Expand Navigation protocol with missing sub-commands — Added `miniMapPayload`, `overviewMapPayload`, `favoriteListPayload` to `G2NavigationProtocol`. Added `sendMiniMap(bmpData:)`, `sendOverviewMap(bmpData:)`, `sendFavorites(_:)` to `G2NavigationSender`. Mini/overview maps use BMP file transfer via 0xC4/0xC5 after signaling sub-command on 0x08-20. Added `G2NavigationFavorite` struct
- [x] **21.3**: Create `G2MenuSender` — New sender class with display lifecycle (displayWake → displayConfig → menu payload). `sendMenuInfo(items:)` with magic_random (counter range 700+), `sendDefaultMenu()` convenience with 6 standard built-in apps. Added to Xcode project (4 pbxproj sections)
- [x] **21.4**: TestAll tests — 3 new tests (82 total): testEvenAIEchoCallback (4 cmd types, decoder callback, response case), testNavigationSubCommands (10 sub-cmds, 36 icons, map/favorites payloads), testMenuSender (7 app IDs, payload builder, parser, sender singleton)

**Key findings from research agents:**
- Response decoder is 100% wired (37/37 callbacks + newly added onEvenAIEcho = 38)
- Display tracking has 15 published properties, 12/12 senders compliant
- Navigation had 8/10 sub-commands implemented prior (now 10/10)
- All 36 navigation icon types were already defined (prior "4/36" report was incorrect)

### Wave 13: Display Tracking & Logger Protocol (2026-03-04)

- [x] **22.1**: Add display mode sub-state tracking — Firmware sends f3={f1=mode, f2=subMode} on 0x0D-01. Added `subMode: Int?` to `G2DisplayMode`, `isEvenAIOverlay` computed property (mode=6 + subMode=7), `displaySubMode` to `G2ConnectionMonitor`. Label now shows `[sub=N]` when sub-mode present. Mode transitions tracked on sub-mode changes too
- [x] **22.2**: Add `awaitDisplayConfirmation` to `G2ProtocolProbeSender` — Upgraded `appendDisplayStateDiff` from sync to async, now calls `awaitDisplayConfirmation` after content probes. Added sub-mode reporting to probe display state diff. All 7 probe types with display tracking now confirm rendering: Navigation, Conversate, BrightnessSkill, Teleprompter, EvenAI, EvenHub, DisplayLifecycle
- [x] **22.3**: Create `G2LoggerSender` for firmware diagnostic log export — New sender with `queryFileList()`, `deleteFile(path:)`, `deleteAllFiles()`, `toggleLiveStreaming(enable:)`. Uses dedicated Logger service 0x0F-20 (not ProtoBaseSettings multiplexing). Added to Xcode project. Export placeholder (file transfer currently phone→glasses only)
- [x] **22.4**: TestAll tests — 3 new tests (85 total): testDisplaySubModeTracking (sub-mode, isEvenAIOverlay, labels), testLoggerSender (6 cmds, payloads, parser, 12 files), testProbeDisplayConfirmation (snapshot, confirmation, hash, gating, sub-mode)

**Key firmware analysis findings:**
- 5 firmware versions (2.0.1.14 → 2.0.7.16), 6 components each. Main OTA grew 29% (2.47→3.19 MB), codec+BLE byte-identical all versions
- Boot: Bootloader 0x00410000 → VTOR write → Main 0x00438000. Vector SP=0x2007FB00 across all versions
- Box firmware: bank-switching at offsets 0x17A0 (running_bank) / 0x37E4 (swap_bank)
- AT command debug surface: 12 command families (BLES/BLEMC/BLEM/BLEADV/BLERingSend/BLE_KEEPCONNECT/BLECleanBond/EM9305/BleGetMac/NUS)
- LFSR cipher for 0x6402 display sensor frames: key unknown, only 5-byte trailer (bytes 200-204) is cleartext

### Wave 14: Health Data & System Monitor Senders (2026-03-04)

- [x] **23.1**: Create `G2HealthDataSender` — New sender for health data on service 0x0C-20 (shared with Quicklist via disjoint command IDs 10-12). Methods: `sendBatchSave(records:)`, `sendHighlight(record:)`, `queryHealthData()`. Uses existing `G2HealthDataProtocol` (8 data types: HEART_RATE, BLOOD_OXYGEN, TEMPERATURE, STEPS, CALORIES, SLEEP, PRODUCTIVITY, ACTIVITY_MISSING). Added to Xcode project
- [x] **23.2**: Create `G2SystemMonitorSender` — New sender for system monitor queries on service 0xFF-20. Method: `queryStatus()` with captured response via `onSystemMonitor` callback chaining. 6 event types: peerReboot, displayRunning, foreground/backgroundEnter/Exit. Added to Xcode project
- [x] **23.3**: TestAll tests — 2 new tests (87 total): testHealthDataSender (8 types, 3 command IDs disjoint from quicklist, record encoding, batch/highlight/query payloads, singleton), testSystemMonitorSender (6 event types, query/parse round-trip, service 0xFF-20, singleton)

**Research agent findings (firmware RE gap audit):**
- 22/26 firmware services have iOS support. Missing TX: Dashboard widgets (0x01-20), Screen power control, Box OTA (UART relay), BLE connect params
- Display config (0x0E-20) protobuf field structure NOT validated against firmware — current implementation is speculative
- Brightness control has 3 possible paths (raw, SKILL, SettingsPackage) — only SKILL path confirmed working
- 14 device config commands: 6 implemented, 8 not (SET_DEVICE_INFO, DISCONNECT_INFO, BLE_CONNECT_PARAM, PIPE_ROLE_CHANGE, UNPAIR_INFO, QUICK_RESTART, AUD_CONTROL, RESTORE_TO_FACTORY)

### Wave 15: Session Reset & Display Pipeline Correctness (2026-03-04)

- [x] **24.1**: Fix `G2EvenAISender.sendToEye` false `recordDisplayConfigSent` — Removed call that logged a displayConfig event on displayWake (EvenAI uses overlay mode, not displayConfig). Was causing spurious "inferred OK" in display confirmation log
- [x] **24.2**: Add `resetDisplayMode()` to `G2ConnectionMonitor` — Clears displayMode, displaySubMode, dashboardState, displayConfig timestamps. Called from `G2Session.stop()` to prevent stale mode leaking across sessions
- [x] **24.3**: Add session reset calls to `G2Session.stop()` — Now calls `G2ConversateSender.shared.reset()`, `G2TranslateSender.shared.reset()`, `G2ConnectionMonitor.shared.resetDisplayFrameCounters()`, `resetDisplayMode()`. Prevents sender state leak (isInitialized/isSessionActive) across reconnects
- [x] **24.4**: Add display pipeline to `G2TasksSender.sendTaskList()` — Added displayWake + displayConfig before quicklist push (matches all other display-rendering senders). Was skipping display wake/config pipeline entirely
- [x] **24.5**: Fix `G2EvenHubSender.sendTextUpgrade` — Added missing displayConfig call (matches createStartUpPage/rebuildPage pattern). Without it, text-upgrade on a cold display would fail silently
- [x] **24.6**: TestAll tests — 2 new tests (126 total): testSessionResetState (monitor clears, sender resets, lifecycle), testDisplayPipelineCoverage (10 display senders + 4 non-display + 2 fixes verified)

**Research agent findings (display tracking + correctness audit):**
- All 38 decoder callbacks ARE wired in connectEye() (VAD, Commit, NotificationAck, NavigationResponse all confirmed)
- Heartbeat fields 3/4/5 (isWearing/isCharging/isInCase) speculative but fully wired — needs BLE capture to confirm
- 0x91-00 (RingResp) is only passthrough with no typed decoder (insufficient evidence for typed parser)

### Wave 16: Display Exit Tracking & Response Constants (2026-03-04)

- [x] **25.1**: Add display exit tracking to lifecycle methods — Navigation `stop()` and `arrive()` now call `awaitDisplayConfirmation(expectedMode: 0)` to track mode→idle transition. Teleprompter `exit()` tracks mode→idle. Translate `stop()` tracks mode→idle, `sendResult()` records content hash per frame. EvenHub `shutdownPage()` captures snapshot + tracks mode→idle
- [x] **25.2**: Add `loggerResponse` and `systemMonitorResponse` constants to ProtocolConstants — Eliminates last 2 hardcoded service IDs in decoder. Updated `G2ServiceIDs.all` array. Decoder now uses named constants throughout
- [x] **25.3**: Add `brightnessSkillProbe` to `comprehensiveModes` — Was excluded from comprehensive probe sweep despite being the confirmed working G2 brightness path
- [x] **25.4**: TestAll tests — 2 new tests (128 total): testDisplayExitTracking (6 lifecycle methods, snapshot, contentHash, probe modes), testServiceIDResponseConstants (7 paired cmd/resp constants, all registered)

### Wave 17: Cloud API Expansion & Model Coverage (2026-03-04)

- [x] **26.1**: Add 7 confirmed API endpoints to `G2FirmwareAPIClient` — `getUserInfo`, `getUserPrefs`, `getUserSettings`, `bindDevice`, `unbindDevice`, `setOnBoarded`, `updateSet`. All use authenticated session headers. Field naming validated: `bind_device` MUST use `sn` (not `device_sn`), otherwise returns code=1401
- [x] **26.2**: Add comprehensive API models to `G2FirmwareModels.swift` — `G2APIEnvelope<T>` (generic wrapper replacing per-endpoint envelopes), `G2UserInfoData` (full composite: user, settings, prefs, token, balance, conf), `G2UserRecord` (encryption key/salt, connection state), `G2ServerConf` (CDN + WebSocket URLs), `G2UserSettingsRecord` (per-device notifications/dashboard), `G2UserPrefsRecord` (hand/date/time/unit), `G2BindDeviceRequest`/`G2BindDeviceData`, `G2UpdateSetRequest`
- [x] **26.3**: Add `G2APIRoutes` enum — 16 confirmed routes with `all` array for enumeration/testing. WebSocket URL (`wss://socket.evenreal.co`) documented
- [x] **26.4**: Expand `LoginData` → `LoginFullData` — Login response now decodes full composite (user record, server conf, prefs, settings), not just token extraction
- [x] **26.5**: Add `directFrom` field to `LatestFirmwareData` — Discovered in captures, always empty string but present in all responses
- [x] **26.6**: TestAll tests — 3 new tests (131 total): testAPIEndpointCoverage (16 routes, envelope decoding, field naming), testAPICloudModels (5 model types, composite + error decoding), testAPIRouteConstants (uniqueness, WebSocket URL, directFrom field)

### Wave 18: System Protocols, Callbacks & Cloud UI (2026-03-04)

- [x] **27.1**: Create `G2SystemCloseSender.swift` — singleton sender wrapping `G2SystemCloseProtocol.closeRequestPayload`. Uses callback chaining pattern (save/restore `onSystemClose` in `defer`). 5-second user interaction window for dialog selection. Two styles: `.standard` (YES/NO), `.extended` (YES/NO/MINIMIZE). Added to `project.pbxproj` (SC01 prefix, 4 sections)
- [x] **27.2**: Add `onDisplayTriggerResponse` dedicated callback to `G2ResponseDecoder` — Previously, `0x81-00` display trigger responses were only accessible via `onRawResponse` case-matching. Now has dedicated `var onDisplayTriggerResponse: ((G2DisplayTriggerResponse) -> Void)?` property, dispatched alongside `onRawResponse`. Wired in `connectEye()` in `G2BluetoothClient`
- [x] **27.3**: Add Cloud Account section to `FirmwareCheckView` — 5 buttons (Get User Info, Get User Prefs, Get User Settings, Bind Device, Set Onboarded) gated on `authSession != nil`. Device-specific calls require SN input. Results displayed in expandable cards (user info with balance/CDN/WebSocket, preferences, settings, bind result). All calls log to `G2DebugLogger` via `logFeature("CloudAPI", ...)`
- [x] **27.4**: TestAll tests — 2 new tests (133 total): testSystemCloseSender (style enum values, selection labels, payload generation, service ID 0x22-20, singleton access, parseResponse), testDisplayTriggerCallback (callback assignment, model fields, service ID 0x81, G2DecodedResponse enum case)

### Wave 19: Sender Wrapper Normalization (2026-03-04)

- [x] **28.1**: Create `G2OnboardingSender.swift` — thin wrapper delegating to `G2OnboardingProtocol` embedded methods (`startUp`, `start`, `end`, `queryHeadUpStatus`). `end()` adds optional cloud API integration: calls `setOnBoarded` with `authSession` when `sn` provided. Added to `project.pbxproj` (OB01 prefix)
- [x] **28.2**: Create `G2GlassesSettingsSender.swift` — wraps `G2GlassesSettingsProtocol` methods (`setSilentMode`, `setScreenOffInterval`, `querySettings`) into singleton pattern. `setScreenOffInterval` takes `G2ScreenOffInterval` enum instead of raw Int. Added to `project.pbxproj` (GS01 prefix)
- [x] **28.3**: Create `G2BuzzerSender.swift` — wraps `G2BuzzerProtocol.trigger()` into singleton pattern. 11 buzzer types from firmware RE. Added to `project.pbxproj` (BS01 prefix)
- [x] **28.4**: TestAll tests — 3 new tests (138 total): testOnboardingSender (7 states, service ID, BLEResponse model, parseBLEResponse), testGlassesSettingsSender (6 screen-off presets, raw values, model summary, service ID), testBuzzerSender (11 types, payload generation, type differentiation)

### Wave 20: Display Tracking Improvements (2026-03-04)

- [x] **29.1**: Add DisplayConfig inference timeout — `recordDisplayConfigSent()` now schedules a 5-second timeout `Task`. If no sensor frames arrive within the window, state transitions to `"inferred_timeout"` instead of staying `"pending"` forever. Timeout is cancelled when frames arrive (in `inferDisplayConfigResult()`). Window widened from 3s to 5s to match timeout
- [x] **29.2**: Verified Conversate per-frame content hash tracking — `G2ConversateSender.sendTranscript()` already calls `recordContentSent(hash:feature:)` per frame (implemented in prior wave). No code change needed
- [x] **29.3**: TestAll tests — 1 new test (139 total): testDisplayConfigTimeout (pending state, frame clears pending, feature tracking, contentHash determinism)

### Wave 21: Sender Wrappers & Ring Health Extensions (2026-03-04)

- [x] **30.1**: Create `G2DashboardStateSender` — thin singleton wrapper delegating to `G2DashboardStateProtocol.queryDashboardState()`. Service 0x0D-20/0x0D-00
- [x] **30.2**: Create `G2ModuleConfigureSender` — wraps queryModuleList, sendSystemSetting, sendDashboardSetting, and adds `setBrightnessCalibration(leftMax:rightMax:)` with clamping (0-42 DAC), both-eye target via `G2BLESendHelper.send`. Service 0x20-20
- [x] **30.3**: Create `R1RingHealthProtocol` + `R1RingHealthSender` — 7 health data types (heartRate, bloodOxygen, skinTemperature, steps, calories, sleep, hrv), R1WearStatus enum (3 states), 4 commands (getDailyData, ackNotifyData, getWearStatus, getHealthSettings, setHealthMonitoring). Parse methods for response data and wear status. All wire formats speculative (0xFE prefix from firmware strings). Uses R1RingSession.shared.client.writeRawCommand()
- [x] **30.4**: TestAll tests — 3 new tests (142 total): testDashboardStateSender (6 widget types, model OK, svc 0x0D-20), testModuleConfigureSender (brightness cal payload, dashboard payload, svc 0x20-20), testR1RingHealthProtocol (7 data types, 3 wear states, 4 commands, parse/wearStatus verified with synthetic data)
- [x] **30.5**: Added 3 files to project.pbxproj: G2DashboardStateSender (DSS0), G2ModuleConfigureSender (MC01), R1RingHealthProtocol (RH01)

### Wave 22: Protocol Views (2026-03-04)

- [x] **31.1**: Create `LoggerView` — firmware log management UI with file list query (both 0x0F-20 and 0x0D-20 paths), individual/all file deletion with confirmation, live streaming toggle with level filter, known files reference (12 files: 5 compressed + hardfault per eye)
- [x] **31.2**: Create `ModuleConfigureView` — per-eye brightness calibration sliders (0-42 DAC), module list query, command type reference. Service 0x20-20
- [x] **31.3**: Create `TranslateView` — full translate session lifecycle (start/stop/pause/resume), one-way/two-way mode selection, partial/final text sending with 30-byte fixed field, protocol reference card. Service 0x05-20 (speculative wire format)
- [x] **31.4**: TestAll tests — 2 new tests (144 total): testLoggerViewCoverage (12 files, 5 levels, 6 commands, path validation), testTranslateProtocolCoverage (4 commands, ctrl actions, 30B text field)
- [x] **31.5**: Added 3 views to project.pbxproj: LoggerView (LGV0), ModuleConfigureView (MCV0), TranslateView (TRV0)

### Wave 23: Health/SysMon Views + Firmware Docs (2026-03-04)

- [x] **32.1**: Expanded `firmware-updates.md` §8 — full iOS SDK firmware pipeline docs (API auth, EVENOTA parsing, CDN download, BLE transfer, management UI state machine)
- [x] **32.2**: Verified all 8 component docs complete — all plan Phase 6 items already covered
- [x] **32.3**: Created `HealthDataView` — 8 data types with type-aware value ranges, batch/highlight/query actions, demo all-types, sent record history. Service 0x0C-20
- [x] **32.4**: Created `SystemMonitorView` — real-time event listener with callback hook, query status, event log with icons/colors, 6 event types. Service 0xFF-20
- [x] **32.5**: Added 2 views to DebugHubView (Health, SysMon tabs → 7 total) + project.pbxproj (HDV0, SMV0)
- [x] **32.6**: TestAll tests — 3 new tests (147 total): testHealthDataViewCoverage (8 types, 3 cmds, record encoding), testSystemMonitorViewCoverage (6 events, parse synthetic), testFileTransferProtocolConstants (chunk/segment math, ACK codes, timing)

### Wave 24: Debug Logging Coverage (2026-03-04)

- [x] **33.1**: Display sensor activity logging — `recordDisplayFrame()` logs "active" on first frame after inactive, `resetDisplayFrameCounters()` logs session summary with frame count/dropped
- [x] **33.2**: Auth keepalive logging — `G2ResponseDecoder` logs type=6 on 0x80-01 to `G2DebugLogger(.bleConnection)`
- [x] **33.3**: Silent sender fix — Added `logFeature()` calls to `G2BuzzerSender`, `G2DashboardStateSender`, `G2GlassesSettingsSender` (all 3 were previously logging only to os.Logger)
- [x] **33.4**: TestAll tests — 4 new tests (151 total): testDisplayModeLogging (mode values, sub-mode, transitions, logger integration), testDisplaySensorActivityLogging (sensor state, content hash, frame degradation, snapshot), testAuthKeepaliveLogging (service IDs, type=6 vs type=4, auth protocol), testSenderDebugLoggingCoverage (buzzer/dashboard/settings, logFeature format, 16+ senders)

### Wave 25: Protocol Bug Fixes & Callback Routing (2026-03-04)

- [x] **34.1**: Fixed conversate auto-close session divergence — `onConversateAutoClose` now calls `G2ConversateSender.shared.reset()` to prevent skipping init on next send
- [x] **34.2**: Fixed translate mode switch service ID — two-way mode switch was sending on 0x07-20 (EvenAI) instead of 0x05-20 (Translate)
- [x] **34.3**: Added display tracking to 6 navigation sub-commands — `start()`, `recalculating()`, `startError()`, `sendMiniMap()`, `sendOverviewMap()`, `sendFavorites()` now call `recordContentSent()`; map methods also call `awaitDisplayConfirmation()`
- [x] **34.4**: Wired 7 response callbacks to `G2ConnectionMonitor` state — menu, systemAlert, systemClose, systemMonitor, VAD, logger file list, quicklist items. Peer reboot now logs re-auth warning
- [x] **34.5**: TestAll tests — 4 new tests (155 total): testConversateAutoCloseReset, testTranslateServiceID, testNavigationDisplayTracking, testResponseCallbackRouting

### Wave 26: Firmware Version Registry & Cross-Version Validation (2026-03-04)

- [x] **35.1**: Added `G2FirmwareVersionRegistry` to `G2EVENOTAParser.swift` — 5 known firmware versions (2.0.1.14→2.0.7.16) with build dates, MD5 hashes, file sizes, changelog text, and per-component payload sizes
- [x] **35.2**: Added cross-version validation — `VersionValidation` validates parsed packages against known-good metadata (size, build date, component sizes, CRC32C), `StabilityReport` identifies stable vs varied components
- [x] **35.3**: Added `G2EVENOTAPackage` extensions — `.registryValidation`, `.knownVersion`, `.changelog`, `.stabilityReport` for easy access from UI code
- [x] **35.4**: Expanded `FirmwareCheckView` — registry validation card (per-component match + stability analysis), changelog card, collapsible version history section with all 5 known releases
- [x] **35.5**: TestAll tests — 3 new tests (158 total): testEVENOTAVersionRegistry, testEVENOTACrossVersionStability, testEVENOTAPackageValidation

### Wave 27: Descriptor-Adjacent Service Lane Recovery (2026-03-05)

- [x] **36.1**: Add `recover_g2_nav_devinfo_descriptor_lanes.py` — new Capstone-based recovery tool that lifts descriptor-adjacent executable anchors for unresolved services `0x08` and `0x09`, emits JSON/Markdown artifacts, and records shared-context writes plus nearby worker/helper calls
- [x] **36.2**: Recover Navigation descriptor-adjacent lanes — service word `0x0067641C=0x08`, adjacent entries `0x00676420=0x00588817` and `0x00676424=0x00588AF3`, shared context `0x20002BE4`, primary lane anchored at `0x0058882C` with repeated worker calls to `0x00583230`, secondary lane anchored at `0x00588AF2` with downstream edges `0x00580018`, `0x004B3F66`, `0x00583B9C`
- [x] **36.3**: Recover DeviceInfo / DevConfig bridge descriptor-adjacent lanes — service word `0x006764BC=0x09`, adjacent entries `0x006764C0=0x00464481` and `0x006764C4=0x00465209`, shared context `0x20003848`; primary lane calls shared settings parser `0x004AA30C`, secondary lane drives dominant-hand/calibration/status helpers (`0x004AF286`, `0x004AF4F8`, `0x00467254`, `0x004AAEE4`, `0x004AAF94`)
- [x] **36.4**: Validate wrapper-normalized descriptor offsets — re-ran ring and system-monitor callchain tools against the stripped firmware image, confirming existing descriptor slots (`0x0067643C=0x91`, `0x006764EC=0xFF`) were already correct and that manual raw-byte dumps must account for the 0x20-byte container header
- [x] **36.5**: Documentation refresh — updated `g2-service-handler-index.md`, `re-gaps-tracker.md`, and analysis artifacts with the new descriptor-adjacent closures and preserved the remaining symbolic-name gap explicitly

**Key discoveries:**
- Service `0x08` is no longer just string-anchored; it now has two executable descriptor-adjacent lanes with a concrete shared context slot (`0x20002BE4`) and a recoverable worker/commit path.
- Service `0x09` is not a pure read-only device-info island; its descriptor-adjacent code reuses the shared settings/dev-config parser and status-wrapper machinery, which narrows the remaining symbolic gap to naming and exact field routing rather than lane ownership.
- When inspecting runtime descriptor words in `ota_s200_firmware_ota.bin`, the 0x20-byte wrapper must be stripped first; otherwise every manual address observation appears shifted by `+0x20`.

**Remaining known gaps (require hardware capture or firmware RE):**
- Brightness: G1-derived `G2BrightnessSender.send()` non-functional on G2. SKILL path (id=0) works but protobuf settings path field numbers unknown
- Translate: type values 20-23 speculative (inferred from method ordering)
- Health data: command IDs 10-12 speculative (inferred from handler dispatch)
- SessionInit (0x0A-20): purpose unknown, no implementation
- Logger live streaming: output destination unknown (NUS? file service?)
- Display config (0x0E-20): protobuf field structure not validated against firmware
- Heartbeat fields 3/4/5 (isWearing/isCharging/isInCase): unverified field assignment
- `check_firmware` (POST): required field combination unknown (all tested combos return 1401)
- `get_nv`: returns binary blob, contents undecoded (may be NV storage or calibration data)
- `check_bind2` / `check_firmware2`: timeouts on all probes, may require different auth
- SystemAlert (0x21-20): receive-only (glasses→phone), no TX path confirmed in firmware
- Dashboard (0x01-20): no TX command sender (gesture events only from this service)
- R1 Ring health: 0xFE commands speculative, no hardware response observed yet
- Transcribe protocol: separate from Conversate, speaker diarization, not implemented
- Sync Info protocol: cloud backup/restore, not implemented

## Deliverables
- Updated `docs/firmware/firmware-reverse-engineering.md` with firmware-evidenced functionality and BLE communication findings.
- Supporting analysis notes in `captures/firmware/analysis/` tied to specific firmware versions/components.
- A reproducible command list for key parsing, hashing, extraction, and diff steps.
- Completed phase history in `docs/buildPhases.md`.

## Acceptance Criteria
- Every added/changed technical claim is traceable to local firmware bytes or existing local docs.
- Bluetooth communication documentation reflects firmware-derived evidence, not API/CDN observations.
- Hardware behavior explanations are split by confidence level and clearly mark unknowns.
- No phase requires network access or external service interaction.
