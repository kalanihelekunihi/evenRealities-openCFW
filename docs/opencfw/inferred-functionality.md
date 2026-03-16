# Inferred Functionality

This document records behavior that is strongly suggested by the current artifacts but is not yet closed strongly enough to freeze as final implementation truth.

## Runtime and UI Services

| Functionality | Current Inference | Why It Is Not Fully Closed |
|---|---|---|
| Full scheduler-core naming and helper equivalence | Startup/runtime helper families correspond to thread/event primitives and likely map onto a coherent RTOS backend | Semantic labels are strong, but exact vendor-level symbol equivalence is still incomplete |
| Dashboard/widget OS around `0x01` | Widget and dashboard runtime services clearly exist behind the known dispatch slots | Full field maps and runtime behavior are still less complete than the primary user features |
| Translate, transcribe-adjacent, onboarding, system alert, and system close services | These feature families are active in the runtime and visible in app/static RE | Their service contracts are not closed to the same standard as teleprompter, navigation, EvenAI, or conversate |
| ModuleConfigure / SyncInfo / general config sync | Calibration and config-sync behavior is real and implementation-relevant | The schema and selector closure are still incomplete |
| Display config payload structure | Existing field layout is close enough to drive device behavior | Exact protobuf field contract is still only partially validated against firmware |
| EvenHub canonical service usage | Runtime clearly has a dedicated display/config/content path | Full separation between legacy operational paths and canonical service usage is still not fully reconciled |
| Compact feature-mode companion packets | Empty `0x0D-01` companion packets appear around feature close or reset transitions | Exact producer path and semantic meaning of `event=0` are still unresolved |
| `0x07` feature multiplex | EvenAI, brightness skill commands, and dashboard or widget families likely share or overlap one runtime lane | Canonical split between `0x07` type families and `0x01` widget service is still incomplete |
| Logger export path | Logger command plane is real and file-backed | Final live-stream/export destination path is still open |
| System close / alert state effects | Dialog/event paths are present and decodable | Exact firmware-side state transitions after user action remain incomplete |

## Lifecycle and Orchestration Plane

| Functionality | Current Inference | Why It Is Not Fully Closed |
|---|---|---|
| Shared orchestration owner above feature services | Compact modes, onboarding, alert/close flows, and timeout-driven exits likely converge on one shared lifecycle owner | The exact owning module and callback graph are still incomplete |
| Head-up trigger and calibration policy | Head-up angle, dashboard-trigger enable, head-up calibration, and dashboard wake policy likely belong to one motion/display lifecycle family | Exact wire schema and ownership split with settings/sensor helpers are still incomplete |
| Empty compact companion packets | `event=0` packets likely represent close/reset fences rather than a standalone feature mode | Exact producer and state semantics are still unresolved |
| DisplayTrigger lifecycle coupling | `0x81` likely bridges case, wake, and display-trigger policy rather than carrying only passive case state | Exact field meaning and state linkage are still incomplete |
| Wakeup-response orchestration path | Voice wakeup response likely enters the same lifecycle plane as head-up/dashboard activation and assistant entry | Owning service path and payload schema are still incomplete |

## Connection and Identity Plane

| Functionality | Current Inference | Why It Is Not Fully Closed |
|---|---|---|
| Advertising restart and fallback policy | Firmware likely has active restart logic and more than one discoverability posture across left, right, and ring identities | Exact multi-set scheduling, fallback order, and restart heuristics are not fully closed |
| Auth keepalive session-health semantics | Periodic `0x80-01` traffic likely carries more than a single success bit and participates in session stability | Exact payload fields, failure thresholds, and disconnect-escalation rules remain incomplete |
| Ring discovery and `connectRing` ownership split | Ring connection may be partly glasses-mediated and partly direct depending on mode or actor | Exact authoritative path and retry ownership are still mixed in local evidence |
| Mode-dependent connection-parameter policy | OTA and low-power evidence suggest the BLE link posture changes with runtime mode | Exact parameter tables, retry backoff, and mode triggers are not yet closed |

## Diagnostics and Debug Surfaces

| Functionality | Current Inference | Why It Is Not Fully Closed |
|---|---|---|
| Logger live-stream payload family | Logger live control clearly goes beyond static file management and likely carries level or category filtered output | Final envelope shapes, category map, and transport sink remain incomplete |
| SystemMonitor event vocabulary | The `0xFF` lane likely covers peer reboot, display-running, app-running, and scheduler idle state beyond a single ping | Exact command IDs, nested appId schema, and notify timing are still incomplete |
| AT or CLI to BLE/service equivalence | Debug shell commands overlap with brightness, teleprompter, BLE, filesystem, and sensor control that also exist in runtime services | Exact one-to-one mapping, privilege split, and build gating remain incomplete |
| Lab-only XIP and production-test utilities | `file2xip`, `xip2file`, gray-screen, and reflash-style tooling are real firmware concepts | Exact safe-operating boundary and production exposure rules are not closed |

## Audio and Voice Stack

| Functionality | Current Inference | Why It Is Not Fully Closed |
|---|---|---|
| Right-eye microphone primacy and peer-audio sync policy | The right eye is likely the default microphone producer while peer-eye sync propagates audio state changes | Exact split between right-eye capture ownership and master-role policy remains mixed in current evidence |
| Wake-word and VAD ownership split | GX8002B and Apollo likely gate microphone or wake events before phone-side assistant logic runs | Exact codec-side versus Apollo-side versus phone-side event ownership is still incomplete |
| EvenAI and Conversate audio-owner takeover | Voice-facing features likely compete for one shared microphone owner through the same audio manager | Exact appId map, takeover order, and teardown behavior are not closed |
| NUS liveness and keepalive semantics | Heartbeat and microphone echo behavior likely help hold background or low-latency audio sessions open | Exact ACK cadence, timeout, and retry rules are still incomplete |

## Input and Gesture Stack

| Functionality | Current Inference | Why It Is Not Fully Closed |
|---|---|---|
| Protobuf versus NUS gesture-plane arbitration | The two gesture planes likely coexist for latency, compatibility, or feature-specific routing reasons | Exact producer precedence and dedupe behavior are not yet closed |
| Long-press nested counter meaning | The `0x0D-01` counter likely carries duration, zone, or dedupe metadata | Exact semantic meaning is still unresolved |
| Screen-on versus screen-off gesture policy | Gesture decode is likely separate from a higher-level action map keyed by display state | Exact app-type schema and persistence format remain incomplete |
| Ring gesture routing topology | Ring gestures may reach the input domain through different paths depending on connection topology and active owner | Exact direct-versus-phone-mediated routing split is still mixed in local evidence |

## Sensors and Calibration Plane

| Functionality | Current Inference | Why It Is Not Fully Closed |
|---|---|---|
| Shared brightness policy owner | Manual brightness, auto-brightness, per-eye calibration, ALS polling, and peer-eye sync likely converge on one internal brightness policy owner | Exact merge and precedence rules are not fully closed |
| `0x6402` telemetry schema | The display notify lane likely mixes display-active, render-state, and sensor or head-angle data in one hardware-facing stream | Exact descrambling, trailer semantics, and field ownership remain incomplete |
| Orientation and calibration subsystem boundary | Head-up angle, zero-position recalibration, heading fetches, and calibration UI likely belong to one broader orientation subsystem | Exact runtime packet ownership and lifecycle are still incomplete |
| `0x20` structured calibration objects | ModuleConfigure and SyncInfo likely carry nested calibration/config structures rather than flat scalars | Exact field-3 schema and object layout are not yet closed |

## Descriptor-Adjacent Service Recovery

| Functionality | Current Inference | Why It Is Not Fully Closed |
|---|---|---|
| Navigation service `0x08` | Two descriptor-adjacent executable lanes implement the navigation UI/data path, with a shared context slot at `0x20002BE4` | Final symbolic handler name and field-level command map remain unresolved |
| DeviceInfo / DevConfig service `0x09` | The lane is a bridge into shared settings/dev-config parser/status logic, not just a read-only device-info response path | Exact command-family ownership and final `*_common_data_handler` symbol name remain unresolved |

## Hardware and Subsystem Inferences

| Functionality | Current Inference | Why It Is Not Fully Closed |
|---|---|---|
| Left/right runtime authority split | Runtime role split is real and includes master/slave plus mixed audio/ring ownership | Exact per-feature authority is still mixed in local evidence |
| Pipe-role change semantics | `PIPE_ROLE_CHANGE` and alternate pipe anchors clearly affect runtime channel selection or coordination | Exact behavior and its relationship to `5450/6450/7450` are still incomplete |
| Power/status local-data mapping | Case4 local-data lanes strongly point to battery percent, charge-state/trend, dashboard state, and calibration UI | Final authoritative field semantics and producer ownership are still incomplete |
| Inter-eye TinyFrame message taxonomy | `uart_sync` master/slave transport and peer input/display sync are real | Exact frame families, payload schemas, and ownership per message are still incomplete |
| Extended ring control and health relay | Ring control reaches beyond basic gesture forwarding and includes richer command/event families | Full enum tables and event semantics are still unresolved |
| Right-eye ring and audio primacy | Captures and module notes strongly suggest the right eye is primary for ring and microphone-facing work | Exact split versus master-side coordination is still mixed in local evidence |
| Direct ring `BAE80001` control/health schema | Ring runtime clearly has a proprietary direct BLE surface beyond the phone-visible battery/state examples | Full command vocabulary and authoritative health payload contract remain undocumented |
| Case/BoxDetect charging telemetry and display-trigger coupling | BoxDetect carries more than a simple dock-state notification path | Exact command grammar and state linkage are still only partly closed |
| Device-info versus settings power fields | Battery and signal-like state appear across multiple proprietary surfaces | Exact ownership split between `0x09`, settings local-data, and case relay remains incomplete |
| Bundled Nordic DFU artifact role | `B210_ALWAY_BL_DFU_NO` likely serves failsafe recovery, `B210_BL_DFU_NO_v2.0.3.0004` likely serves the normal bootloader path, and `B210_SD_ONLY_NO_v2.0.3.0004` likely serves BLE-stack updates for the ring-side Nordic domain rather than the Apollo main runtime | Exact deployment target and field selection policy in the product family are still unresolved |
| ALS brightness pipeline | OPT3007 feeds an inter-eye synchronized brightness path that replaces direct JBD writes | Exact lux-to-DAC transform and smoothing logic remain unknown |
| External flash partition and XIP layout | LittleFS-backed storage and an XIP asset window both exist on the MX25U25643G | Exact boundary and placement policy inside the 32 MB flash are still unresolved |
| FlashDB-backed KV persistence | Firmware clearly contains `flashDB`/transaction-log persistence beyond plain files | Exact on-flash schema, key naming, and migration rules are not yet closed |
| Cross-eye persistence mirroring | OTA status and some settings/config state are synchronized or relayed between eyes | Exact replication rules per namespace and per object remain incomplete |
| OTA-specific five-command session | A richer `START -> INFORMATION -> FILE -> RESULT_CHECK -> NOTIFY` OTA flow exists beyond the generic file client | Exact command byte IDs and full field layouts are not fully closed |
| Conservative update/recovery policy | Bootloader install checks, case bank-swap, and MCUboot slot confirmation all suggest a conservative recovery posture across devices | Exact rollback triggers and persistence records are still incomplete |
| Dual-eye OTA arbitration | Firmware tracks OTA state from self and peer and likely coordinates install timing across eyes | Final conflict-resolution and retry rules are still not fully recovered |
| Case UART protocol | The case link uses a framed, checksummed transport with OTA and status commands | Full opcode grammar is not yet recovered |
| Codec host command dictionary | TinyFrame steady-state host traffic clearly extends beyond BINH boot stages into runtime audio control/status | The complete command/event set is not yet lifted instruction-by-instruction |
| Touch controller runtime and DFU grammar | Touch/prox and wear-adjacent behavior are real and version-linked | Exact event encoding, thresholds, and row-level update grammar remain incomplete |
| EM9305 function-level patch behavior | Patch records and ownership are known | Function-level radio behavior is not yet decoded |
| R1 ring runtime capabilities | Gesture and health capabilities are clear from protocols/app evidence | Standalone ring runtime image is still missing |
| Audio, on-device ML, and cloud-assisted voice stack | The stack is clearly present across app evidence, audio components, and firmware strings | Device-side protocol closure is still weaker than the app/static story |
| OTA command vocabulary | `FILE_CHECK`, `START`, `DATA`, `END`, metadata/result-check phases, timestamps, and target-type values are all visible | Some OTA-specific higher-level response/result semantics are still inferred rather than fully lifted |

## Clean-Room Guidance

For `openCFW`, inferred functionality should be implemented behind explicit feature flags or instrumentation until one of these happens:

- a direct firmware string or xref closes the symbol path,
- an instruction-level lift closes the data flow,
- or live capture confirms the wire contract.

## Source Documents

- `../protocols/services.md`
- `../protocols/authentication.md`
- `../protocols/connection-lifecycle.md`
- `../devices/g2-case.md`
- `../devices/r1-ring.md`
- `../protocols/nus-protocol.md`
- `../protocols/notification.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/firmware-communication-topology.md`
- `../firmware/s200-firmware-ota.md`
- `../firmware/s200-bootloader.md`
- `../firmware/firmware-updates.md`
- `../firmware/firmware-files.md`
- `../firmware/ota-protocol.md`
- `../firmware/modules/ble-multi-connection.md`
- `../firmware/modules/settings-local-data-status.md`
- `../firmware/modules/settings-runtime-context.md`
- `../firmware/codec-gx8002b.md`
- `../firmware/touch-cy8c4046fni.md`
- `../firmware/box-case-mcu.md`
- `../features/gestures.md`
- `../features/brightness.md`
- `../features/even-ai.md`
- `../features/conversate.md`
- `../firmware/re-gaps-tracker.md`
- `../firmware/g2-service-handler-index.md`
- `../firmware/g2-firmware-modules.md`
- `../firmware/even-app-reverse-engineering.md`
- `../firmware/modules/settings-sync-module-config.md`
- `../firmware/modules/display-config.md`
- `../firmware/modules/quicklist-health.md`
- `../firmware/modules/settings-compact-notify.md`
- `../firmware/modules/wear-detection.md`
- `../firmware/modules/ring-relay.md`
- `../firmware/modules/settings-sync-module-config.md`
- `../firmware/modules/settings-headup-calibration.md`
- `../firmware/modules/file-transfer.md`
- `../firmware/modules/logger.md`
- `../firmware/firmware-communication-topology.md`
- `../firmware/s200-firmware-ota.md`
- `../devices/g2-glasses.md`
- `../features/display-pipeline.md`
- `../features/eventhub.md`
- `../features/brightness.md`
- `../reference/unidentified-behaviors.md`
- `../firmware/analysis/2026-03-05-g2-nav-devinfo-descriptor-lanes.md`
- `../firmware/analysis/2026-03-05-g2-ring-relay-callchain.md`
- `../firmware/analysis/2026-03-05-g2-system-monitor-callchain.md`
