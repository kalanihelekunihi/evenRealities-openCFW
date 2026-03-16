# Identified Functionality

This document records behavior that is already solid enough to treat as implementation input for `openCFW`.

## Transport, Session, and Routing

| Functionality | Status | Notes |
|---|---|---|
| Apollo510b main runtime ownership | Confirmed | Main G2 runtime image owns BLE host, scheduler, UI, and OTA orchestration |
| Core BLE transport/session/service routing | Confirmed | Control, display, and file planes are distinct and persist across the documented protocol flow |
| Authentication and connection lifecycle | Confirmed | Pairing/session bring-up is documented strongly enough to preserve in clean-room form |
| FreeRTOS-based task model | Confirmed | Runtime threads include BLE RX/TX, audio, input, ring, and display lanes |
| Reset-to-runtime bootstrap chain | Confirmed | Reset, init-table, descriptor callback seed, worker bootstrap, and idle loop are instruction-anchored |
| Descriptor-seeded runtime object model | Confirmed | `0x20003DB4` is a real startup/runtime descriptor object, not a loose magic pointer |
| Packet framing baseline | Confirmed | `0x5401/0x5402`, `0x6401/0x6402`, and `0x7401/0x7402` are the core lane split |
| Multi-endpoint BLE identity model | Confirmed | left and right are runtime-selected identities on the same firmware image and keep independent phone BLE connections |
| Application-level auth family | Confirmed | `0x80-00/01/02/20` implements fast and full auth plus time sync without relying on standard BLE pairing for session establishment |
| Endpoint-local sequence and notify context | Confirmed | each connected endpoint carries its own response timing, sequence evolution, and keepalive expectations |
| NUS low-latency side channel | Confirmed | Raw BLE traffic outside the protobuf envelope carries gestures, microphone control, and LC3 audio frames |
| Production CLI / AT debug surfaces | Confirmed | Firmware exposes FreeRTOS CLI and AT command families for diagnostics, filesystem, sensors, and lab control |

## Display and Rendering

| Functionality | Status | Notes |
|---|---|---|
| Display wake path | Confirmed | `0x04-20` wakes the display path before rendering |
| Display bring-up sequencing | Confirmed | User-visible render flows require wake -> config -> content ordering |
| Display configuration path | Confirmed | `0x0E-20` configures render/display state before content |
| Display sensor/feedback lane | Confirmed | `0x6402` reports display/render-side feedback |
| EvenHub render/container system | Confirmed | Runtime supports custom page/layout rendering |
| LVGL + NemaGFX graphics stack | Confirmed | UI/render path is graphics-stack-backed rather than raw frame blits only |
| Screen mode layering | Confirmed | JBD hardware mode handling and BLE-visible display mode handling are distinct |
| Compact feature-mode notify lane | Confirmed | `0x0D-01` carries idle, render, conversate, and teleprompter mode transitions used by display-facing features |

## Feature Protocols

| Functionality | Status | Notes |
|---|---|---|
| Teleprompter text/session path | Confirmed | Runtime ACK, progress, completion, and page-stream flow exist |
| EvenAI control/status path | Confirmed | Assistant entry, ask or reply flow, and VAD-related hooks are present |
| Navigation feature presence | Confirmed | Navigation is a first-class runtime feature even though full field mapping is still partial |
| Conversate session FSM | Confirmed | Start, pause, resume, close, and config states are string-confirmed |
| Single-owner microphone arbitration | Confirmed | Only one feature or app can own live microphone capture at a time and peer-eye audio state sync exists |
| Phone-side speech and AI orchestration | Confirmed | Glasses capture and stream audio while decode, denoise, VAD, ASR, transcription, and higher-order assistant logic remain phone-owned |
| Menu payload path | Confirmed | Menu content delivery is a stable app-layer service |

## Lifecycle and Orchestration

| Functionality | Status | Notes |
|---|---|---|
| Compact mode / feature transition plane | Confirmed | `0x0D-01` carries explicit idle, render, conversate, and teleprompter transitions |
| Onboarding lifecycle service | Confirmed | `0x10` is a dedicated first-run service with startup/start/end flow and staged onboarding states |
| Head-up dashboard trigger surface | Confirmed | Motion-triggered dashboard wake exists separately from standard display wake and ties into onboarding calibration |
| Timeout and auto-close control surfaces | Confirmed | Dashboard auto-close persistence and conversate idle-close notifications are real runtime behaviors |
| System alert / close / monitor lifecycle services | Confirmed | `0x21`, `0x22`, and `0xFF` are dedicated orchestration-facing services rather than generic feature payload aliases |

## Settings, State, and Interaction

| Functionality | Status | Notes |
|---|---|---|
| Settings / ProtoBaseSettings | Confirmed | `0x0D` selector-based dispatch path is a core runtime surface |
| Settings root-case split | Confirmed | selector receive, local-data response, and notify-group lanes are distinct roots |
| Brightness manual/state path | Confirmed | Brightness control exists independently of the still-open ALS curve |
| ALS-driven inter-eye brightness sync | Confirmed | auto-brightness uses sensor polling and peer-eye relay instead of only direct display writes |
| Wear detection and calibration hooks | Confirmed | Settings dispatch and module notes close the main wear/state path |
| Head-up / calibration UI state path | Confirmed | selector `4`, case4 `tag17`, and calibration gating helpers expose a real calibration-state lane |
| Proprietary power/state surfaces | Confirmed | Battery, charging, and case state are carried through proprietary status paths rather than the standard BLE Battery Service |
| Case state relay surface | Confirmed | Case battery, charging, and in-case state are exposed through case relay / BoxDetect paths |
| ModuleConfigure / SyncInfo presence | Confirmed | Calibration and config-sync services are present and implementation-relevant, including brightness calibration and structured module/config payloads |
| Dual-plane gesture input path | Confirmed | G2 touch gestures surface on protobuf lanes and on NUS `0xF5`, and both planes are implementation-relevant |
| Gesture policy/configuration presence | Confirmed | Universal settings include per-gesture action mapping with distinct screen-on and screen-off policy |
| Wear-gated input policy | Confirmed | Wear state can block input acceptance and some display-adjacent control paths |
| Ring gesture forwarding | Confirmed | Basic relay path exists even though enum closure is incomplete |
| Touch/proximity firmware split | Confirmed | Touch logic runs on the Cypress sidecar controller |
| Quicklist + Health | Confirmed | Shared service with full-update, paging, health-save, query, and highlight families |
| Notifications | Confirmed | Metadata, file-backed display payloads, and whitelist storage are all part of the runtime contract |

## Files, Diagnostics, and OTA

| Functionality | Status | Notes |
|---|---|---|
| Logger | Confirmed | File list/delete/live-control path is known and `/log/` is an explicit namespace guard |
| Diagnostic file export flow presence | Confirmed | File lane supports a distinct glasses-to-phone export direction used for logs and captured data |
| File transfer path | Confirmed | File/OTA lane is a first-class runtime plane, not a logger-only special case |
| Apollo flash and SRAM anchors | Confirmed | Bootloader `0x00410000`, app `0x00438000`, SRAM `0x20000000-0x2007FFFF`, stack `0x2007FB00`, and runtime descriptor `0x20003DB4` are all anchored |
| LittleFS namespace and OTA staging layout | Confirmed | `/firmware`, `/ota`, `/user`, and `/log` are real mounted namespaces used by bootloader and runtime |
| Persistent user and crash artifacts | Confirmed | `user/notify_whitelist.json`, `/log/compress_log_*.bin`, and `/log/hardfault.txt` are stable runtime objects |
| Bootloader-managed OTA install cycle | Confirmed | Runtime stages `/ota/*`, sets an OTA flag, reboots, and the bootloader performs CRC/program/verify before app handoff |
| OTA prerequisites and restart behavior | Confirmed | G2 OTA requires charging and both eyes at or above 50% battery, and successful update ends in system restart |
| Package order vs apply order split | Confirmed | EVENOTA bundle order (`codec -> BLE -> touch -> box -> bootloader -> main`) differs from runtime subordinate apply order (`box -> EM9305 -> touch -> codec`) |
| SystemMonitor | Confirmed | Dedicated status and idle-probe path is anchored to `0xFF` |
| EVENOTA container parsing | Confirmed | Package structure, per-entry header, checksum path are known |
| G2 OTA transfer over BLE | Confirmed | Uses `0x7401/0x7402` with `0xC4/0xC5` command/data flow |
| OTA file packets | Confirmed | 1000-byte payloads with 5-byte OTA file header |
| Box OTA relay | Confirmed | Case update is relayed through G2 and chunked separately |
| Sub-component update chain | Confirmed | Main runtime orchestrates box, touch, codec, and EM9305 updates |
| BoxDetect / display trigger family | Confirmed | Case relay and display-trigger responses share this lane |

## Device and Hardware Topology

| Functionality | Status | Notes |
|---|---|---|
| Left/right eye shared firmware image | Confirmed | Identity is runtime-configured rather than build-specific |
| Inter-eye link exists | Confirmed | Peer coordination uses a wired `uart_sync` / TinyFrame path rather than BLE between eyes |
| Master/slave peer-role framework | Confirmed | Runtime has explicit master/slave branches, with left-eye master and right-eye slave sync roles |
| Dominant-hand setting is separate from eye role | Confirmed | User handedness is a runtime preference and not the same thing as left/right/master/slave role selection |
| EM9305 host/controller split | Confirmed | Apollo owns the BLE host while EM9305 is patched over HCI and handles radio/link-layer work |
| ALS and IMU hardware presence | Confirmed | OPT3007 and ICM-45608 are real runtime-visible sensor subsystems |
| Codec MCU control boundary | Confirmed | GX8002B is a discrete codec/voice subsystem loaded over TinyFrame with BINH stage1/stage2 boot images |
| Touch/proximity firmware split | Confirmed | Touch/prox logic runs on the CY8C4046FNI sidecar and is updated over I2C DFU |
| Case is relayed through G2 | Confirmed | Case traffic is framed through `box_uart_mgr` / `glasses_case`, not exposed as a direct phone BLE endpoint |
| Ring has its own BLE/runtime path | Confirmed | G2 exposes `0x91` relay handling while the ring separately uses `BAE80001` and `FE59`/SMP DFU |
| In-corpus R1 Nordic bundle family | Confirmed | `B210_ALWAY_BL_DFU_NO`, `B210_BL_DFU_NO_v2.0.3.0004`, and `B210_SD_ONLY_NO_v2.0.3.0004` are real tagged bootloader/SoftDevice artifacts with vector, reset, and idle anchors; they are not the standalone ring app runtime |
| G2 dual-eye shared image family | Confirmed | G2-L and G2-R use the same bootloader, main app, EM9305, codec, and touch image family rather than separate per-eye builds |
| Apollo main runtime is the G2 update owner | Confirmed | The Apollo app owns subordinate EM9305, codec, touch, and case update orchestration |
| Ring firmware domain is outside EVENOTA | Confirmed | R1 uses a separate FE59 + SMP/MCUboot-style update path rather than the G2 EVENOTA package |
| R1 charging cradle has no firmware | Confirmed | The cradle is passive and is not a clean-room firmware target |
| Log path namespace | Confirmed | `/log/` namespace is validated by firmware |
| Notification whitelist storage | Confirmed | `user/notify_whitelist.json` is used by runtime |
| Firmware-managed persistent config | Confirmed | Settings/status values are written into shared runtime/config structures |
| LittleFS usage | Confirmed | Runtime stores files, logs, and user payloads in flash-backed filesystem space |

## Clean-Room Implication

The first `openCFW` implementation can safely assume:

- Apollo510b is the main executable target.
- Control, display, and file lanes are separate and must stay separate.
- `0x09` and `0x0D` are core bring-up services, not optional features.
- Auth, non-auth sequence counters, and keepalive behavior must remain per-connection instead of collapsing into one BLE-global session object.
- Display wake/config and filesystem support are foundational, not add-ons.
- Sensor acquisition, calibration state, and `0x6402` telemetry need to remain separate layers instead of being flattened into UI-only feature logic.
- Compact modes, onboarding, head-up wake, timeout/auto-close, and alert/close flows should remain a dedicated lifecycle plane instead of being inferred from content traffic alone.
- OTA, settings, notifications, and topology are documented strongly enough to anchor a minimal runtime skeleton.
- `openCFW` should target one Apollo image family for both eyes and keep case/ring/cradle ownership outside that first-wave rewrite scope.
- Touch-controller transport, gesture normalization, and wear-gated input policy should remain separate layers instead of one generic tap callback.
- Codec boot/control, NUS mic or audio streaming, and voice-feature UX should remain separate layers with explicit microphone-owner arbitration.
- Logger, file export, and system-monitor behavior are documented strongly enough to anchor an initial observability plane.

## Source Documents

- `../protocol-overview.md`
- `../protocols/packet-structure.md`
- `../protocols/services.md`
- `../protocols/authentication.md`
- `../protocols/connection-lifecycle.md`
- `../protocols/nus-protocol.md`
- `../features/display-pipeline.md`
- `../features/eventhub.md`
- `../features/teleprompter.md`
- `../features/even-ai.md`
- `../features/navigation.md`
- `../features/conversate.md`
- `../features/brightness.md`
- `../features/gestures.md`
- `../protocols/notification.md`
- `../firmware/firmware-reverse-engineering.md`
- `../firmware/firmware-files.md`
- `../firmware/s200-firmware-ota.md`
- `../firmware/s200-bootloader.md`
- `../firmware/firmware-updates.md`
- `../firmware/ota-protocol.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/g2-service-handler-index.md`
- `../firmware/g2-firmware-modules.md`
- `../firmware/even-app-reverse-engineering.md`
- `../firmware/modules/ble-multi-connection.md`
- `../firmware/ble-em9305.md`
- `../firmware/codec-gx8002b.md`
- `../firmware/touch-cy8c4046fni.md`
- `../firmware/box-case-mcu.md`
- `../firmware/modules/display-config.md`
- `../firmware/modules/settings-sync-module-config.md`
- `../firmware/modules/settings-headup-calibration.md`
- `../firmware/modules/quicklist-health.md`
- `../firmware/modules/settings-compact-notify.md`
- `../firmware/modules/settings-dispatch.md`
- `../firmware/modules/settings-local-data-status.md`
- `../firmware/modules/settings-runtime-context.md`
- `../firmware/modules/settings-selector-schema.md`
- `../firmware/modules/wear-detection.md`
- `../firmware/modules/file-transfer.md`
- `../firmware/modules/logger.md`
- `../firmware/firmware-communication-topology.md`
- `../devices/g2-glasses.md`
- `../devices/g2-case.md`
- `../devices/r1-ring.md`
- `../devices/r1-cradle.md`
