# Unidentified Functionality

This document is the clean-room unknowns register for `openCFW`.

## Priority Unknowns

| Priority | Unknown | Why It Matters |
|---|---|---|
| P0 | Fully symbolized Apollo510b reset/runtime call graph | Needed for a faithful task/init model and safe boot replacement |
| P0 | Exact left/right/master/slave ownership split | Needed for dual-eye role logic and ring/case routing correctness |
| P0 | Standalone R1 application runtime image (distinct from the already present Nordic bootloader and SoftDevice artifacts) | Required before any serious clean-room ring firmware implementation |
| P1 | Exact inter-eye TinyFrame frame taxonomy and peer-sync ownership | Needed to replace peer coordination without regressing dual-eye behavior |
| P1 | Exact `0x08` command enum / field map | Needed for full navigation implementation |
| P1 | Exact `0x09` command field map and final symbolic handler names | Needed for authoritative device-info/dev-config behavior |
| P1 | Unknown `0x90-??` service | Could block a reserved system lane or hidden feature path |
| P1 | Full symbolized startup/runtime call graph and descriptor-fanout ownership | Needed for a faithful startup/task rewrite instead of a compatible skeleton |
| P1 | Settings root `case6/case7`, `case4 tag11`, and unresolved local-data lanes | Needed for authoritative settings/schema compatibility |
| P1 | Exact `PIPE_ROLE_CHANGE` / alternate-pipe semantics | Needed to model role-sensitive transport switching and peer coordination safely |
| P1 | Separate transcribe protocol lane / service ID | Needed to keep Conversate and any speech-to-text path correctly separated |
| P1 | Ring relay enum tables (`command_id`, `event_id`, touch `type`) | Needed for typed ring support instead of raw relay passthrough |
| P1 | Direct ring `BAE80001` proprietary command vocabulary | Needed for any non-relay ring integration beyond battery/state basics |
| P1 | Exact mapping between proprietary battery/charging fields across `0x09`, `0x0D`, `0x81`, and app callbacks | Needed for a coherent clean-room state model without duplicate or contradictory status sources |
| P1 | Exact external-flash partition map and LittleFS/XIP split | Needed for safe asset placement, OTA staging, and future image packaging |
| P1 | Exact `otaFlag`, `boot_count`, and boot metadata storage layout | Needed for a safe clean-room update and recovery story |
| P1 | Exact OTA-specific command byte IDs and 5-byte file-header layout | Needed for a faithful native OTA session instead of generic file-transfer fallback |
| P1 | Exact update retry, peer-arbitration, and rollback triggers | Needed for robust dual-eye update safety and recovery parity |
| P1 | EM9305 function-level patch semantics | Needed if `openCFW` ever has to own radio patch behavior directly |
| P2 | Exact deployment target of `B210_ALWAY_BL_DFU_NO`, `B210_BL_DFU_NO_v2.0.3.0004`, and `B210_SD_ONLY_NO_v2.0.3.0004` across ring, auxiliary recovery, or legacy product paths | Needed to avoid attributing the wrong firmware family to the wrong device domain |
| P2 | Exact selection policy between the failsafe and versioned R1 bootloader bundles | Needed before modeling ring recovery and boot update behavior clean-room |
| P2 | Exact auth keepalive payload schema and failure escalation rules | Needed for long-lived session parity without triggering disconnect or pairing-removal edge cases |
| P2 | Exact advertising-set restart and fallback policy across left/right/ring identities | Needed for high-fidelity multi-endpoint discoverability and recovery behavior |
| P2 | Exact connection-parameter update policy, retry backoff, and OTA fast-mode transitions | Needed for throughput and power parity without guessing BLE link posture |
| P2 | ALS brightness numeric transform | Needed for faithful auto-brightness |
| P2 | Exact ModuleConfigure / SyncInfo nested field schema for calibration and structured config payloads | Needed for compatible brightness calibration, module flags, and system setting sync |
| P2 | Exact head-up calibration lifecycle enum and `tag17`/`0x20073004` relationship | Needed for faithful calibration UI state and gating behavior |
| P2 | Exact IMU/head-angle and heading packet ownership beyond current `0x6402` observations | Needed for orientation parity without guessing the wrong service path |
| P2 | Case UART frame grammar and opcode map | Needed for case support and case OTA clean-room implementation |
| P2 | BoxDetect auxiliary callee semantics (`0x00545866 -> 0x00543E06`) | Needed to close the case relay logic fully |
| P2 | Exact long-press `0x0D-01` counter semantics and producer ownership | Needed for faithful long-press handling instead of a guessed boolean or timer |
| P2 | Exact arbitration or dedupe rules between protobuf gesture traffic and NUS `0xF5` gesture traffic | Needed to avoid duplicate or dropped user-input events |
| P2 | Exact screen-on/screen-off gesture policy schema and persisted mapping layout | Needed for configurable gesture actions without inventing the wrong settings contract |
| P2 | Codec TinyFrame runtime command/event dictionary | Needed for authoritative codec-host control, error handling, and audio-state parity |
| P2 | Exact NUS microphone enable echo, heartbeat cadence, and stream-recovery semantics | Needed for robust low-latency voice capture over the side channel |
| P2 | Exact audio-manager appId map and forced-unregister handoff behavior | Needed to keep EvenAI, Conversate, and future voice features from stealing the mic incorrectly |
| P2 | Exact wake-word or wakeup-response payload schema and ownership split | Needed for hands-free voice compatibility without over-implementing AI on-glasses |
| P2 | Touch DFU row/update grammar and gesture calibration tables | Needed for clean-room touch-controller support beyond host-level stubs |
| P2 | FlashDB key/value schema and transaction-log layout | Needed for authoritative non-file persistence compatibility |
| P2 | Exact logger export opcode bytes and export result semantics | Needed for faithful diagnostics retrieval over the shared file lane |
| P2 | Exact logger live-stream payload schema and filter map | Needed for real-time diagnostics and tooling parity |
| P2 | Log compression format and retention policy beyond known filenames | Needed for faithful diagnostics export and storage budgeting |
| P2 | Font/external-flash asset packing headers and placement rules | Needed for reproducible asset/image packaging to the XIP window |
| P2 | `0x6402` display-sensor stream internals and descrambling details | Needed for faithful render/sensor parity |
| P2 | Exact `0x0D-01` empty companion packet producer and meaning | Needed for faithful feature-mode close/reset behavior |
| P2 | Exact `0x10` onboarding command schema, delayed-ACK payloads, and state-notify model | Needed for faithful first-run lifecycle handling instead of a stub-only onboarding path |
| P2 | Exact head-up angle / dashboard-trigger wire contract and relationship to calibration-state lanes | Needed to preserve motion-triggered dashboard wake without guessing the wrong settings path |
| P2 | Exact `0x21` SystemAlert event ids and `0x22` SystemClose action/result enums | Needed for faithful alert/close lifecycle behavior instead of generic dialogs |
| P2 | Exact timeout tables and close-policy ownership across dashboard, teleprompter, EvenAI-adjacent, and other user-facing services | Needed for lifecycle parity without inventing client-side timeout behavior |
| P2 | Exact wakeup-response payload schema and owning service path | Needed to preserve voice-triggered lifecycle behavior without over-implementing assistant logic |
| P2 | Brightness protobuf field numbers and exact ALS curve | Needed for a compatible auto-brightness implementation |
| P2 | Exact `0x07` multiplex between EvenAI, skill, and dashboard/widget families | Needed to avoid lane collisions in clean-room feature services |
| P2 | Exact teleprompter mid-stream marker and sync-trigger semantics | Needed for full teleprompter parity instead of a tolerant sender-only path |
| P2 | Exact `0xFF` system-monitor command/event schema and nested appId fields | Needed for monitor parity beyond a minimal idle-probe stub |
| P2 | Exact AT/CLI grammar, transport boundary, and privilege gating | Needed to separate lab tooling from normal compatibility interfaces safely |
| P2 | Notification metadata proto vs file-transfer dependency | Needed to separate notification and file subsystems cleanly |

## Lower-Priority Unknowns

| Unknown | Current State |
|---|---|
| JBD4010 display scrambling/LFSR polynomial | Still unresolved at hardware/display-driver level |
| Exact meaning of DisplayTrigger `f3.f1=67` | Constant observed, semantic meaning still unknown |
| Exact ring SoC model | Nordic family is known, exact production SKU still unresolved |
| `S201` model variant meaning | Mention exists, purpose still unclear |
| Compass / magnetometer IC | Device role is inferred, exact part not yet identified |
| Battery capacity numbers | Not recoverable from current corpus |
| SessionInit `0x0A-20` | No reliable runtime meaning yet |
| Dashboard/menu/widget field ownership | Runtime feature family is visible, but the full schema split is still incomplete |
| Transcribe protocol lane | Confirmed separate from Conversate, wire service still not closed |

## Missing Artifacts

| Missing Artifact | Blocks |
|---|---|
| Standalone R1 application image (not the already present `bootloader.bin` / `softdevice.bin` Nordic artifacts) | Ring runtime RE and clean-room ring firmware |
| Endpoint-labeled live traces with ring/dual-eye ownership | Role/authority closure and ring state semantics |
| Deeper case-UART captures or lifted parser | Full case opcode grammar |
| More OTA control/response correlation | Exact OTA result semantics and error handling |

## Source Documents

- `../firmware/re-gaps-tracker.md`
- `../firmware/firmware-reverse-engineering.md`
- `../protocols/authentication.md`
- `../protocols/connection-lifecycle.md`
- `../firmware/device-boot-call-trees.md`
- `../firmware/ota-protocol.md`
- `../firmware/s200-bootloader.md`
- `../firmware/firmware-files.md`
- `../firmware/firmware-updates.md`
- `../firmware/modules/ble-multi-connection.md`
- `../firmware/modules/settings-local-data-status.md`
- `../firmware/modules/settings-runtime-context.md`
- `../firmware/modules/wear-detection.md`
- `../firmware/modules/settings-sync-module-config.md`
- `../firmware/modules/settings-headup-calibration.md`
- `../firmware/ble-em9305.md`
- `../firmware/codec-gx8002b.md`
- `../firmware/touch-cy8c4046fni.md`
- `../firmware/box-case-mcu.md`
- `../features/gestures.md`
- `../protocols/nus-protocol.md`
- `../firmware/modules/logger.md`
- `../firmware/modules/file-transfer.md`
- `../firmware/firmware-communication-topology.md`
- `../firmware/s200-firmware-ota.md`
- `../firmware/modules/quicklist-health.md`
- `../firmware/modules/settings-compact-notify.md`
- `../firmware/g2-service-handler-index.md`
- `../firmware/modules/settings-selector-schema.md`
- `../firmware/modules/settings-dispatch.md`
- `../protocols/services.md`
- `../firmware/even-app-reverse-engineering.md`
- `../devices/g2-glasses.md`
- `../firmware/analysis/2026-03-05-g2-system-monitor-callchain.md`
- `../devices/r1-ring.md`
- `../reference/unidentified-behaviors.md`
- `../reference/magic-numbers.md`
