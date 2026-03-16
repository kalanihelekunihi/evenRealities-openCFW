# G2 Firmware Modules and Simulator Parity

This document maps G2 firmware modules to BLE/API behavior and the ESP32 simulator implementation.

All evidence below is from local artifacts only:
- `captures/firmware/analysis/firmware-string-cross-reference.json`
- `captures/firmware/analysis/2026-03-03-ble-artifact-extraction.md`
- `captures/firmware/analysis/2026-03-04-v207-string-diff.json` (v2.0.6.14 → v2.0.7.16 diff: 1,301 new strings, 123 protocol-relevant)
- `captures/firmware/g2_extracted/ota_s200_firmware_ota.bin`
- `captures/firmware/versions/v2.0.7.16/extracted/` (production firmware, build 2026-02-13)
- local app protocol model under `Sources/EvenG2Shortcuts/*`

## Module Map (Sorted by Function/Service)

| Module | Service IDs | Firmware Evidence (local) | Simulator Status |
|---|---|---|---|
| BLE Multi-Connection | Identity-level BLE (`G2-L`/`G2-R`/`R1`) | `AT^BLEADV`, `AT^BLEMC`, `AT^CLEANBOND`, `AT^BLEM [Scan/DisScan/RINGSTATE]` strings in `firmware-string-cross-reference.json`; `ring_and_peer_sync` in `2026-03-03-ble-artifact-extraction.md`; left/right/ring connect evidence in `captures/20260301-2-testAll.txt` and `captures/20260302-2-testAll.txt` | Implemented+: 3 extended instances, descriptor-based local-address instance mapping, hardware-active checks (`ble_gap_ext_adv_active`), per-connection notify targeting, endpoint-profile write gating, watchdog re-advertise recovery, and adaptive single-instance fallback when multi-start repeatedly fails |
| Dashboard | `0x01-20` + sync on `0x0D-00` | `Dashboard_common_data_handler @ 0x002D93E4`; `page_state_sync_init @ 0x00266FD4` | Partial+: stateful ACK on `0x01-00` plus sync-info style state push on `0x0D-00` (tile/widget/quicklist-expanded) |
| Menu | `0x03-20` -> `0x03-00` | `[menu.page]menu page recv data from BLE, cmd = %d, magicRandom = %d, which_Msg_Ctx = %d @ 0x00272510` | Implemented: response emits type/msgId and menu item echo/cache |
| Translate | `0x05-20` -> `0x05-00` | `...\pb_service_translate\pb_service_translate.c @ 0x0026FB4C` | Implemented: command echo; COMM_RSP completion for final result/stop |
| Teleprompter | `0x06-20` -> `0x06-00/01` | `pb_service_teleprompt` evidence in `2026-03-03-ble-artifact-extraction.md` | Implemented (existing): ACK/progress/completion/timed scroll behavior |
| EvenAI | `0x07-20` -> `0x07-00/01` | `[service.evenAI]` + `pb_service_even_ai` evidence in `2026-03-03-ble-artifact-extraction.md` | Implemented (existing): enter/exit/ASK/REPLY/SKILL + completion/status |
| Navigation | `0x08-20` -> `0x08-00` | `navigation.ui` string evidence in `2026-03-03-ble-artifact-extraction.md` | Partial+: command echo response on `0x08-00` with state/subcmd tracking and mode transitions |
| Device Info | `0x09-00/20` -> `0x09-01` | version/SN strings in main OTA + capture-derived payload shape | Implemented: deterministic nested device info payload |
| Conversate | `0x0B-20` -> `0x0B-00/01` | `pb_service_conversate` evidence; v2.0.7.16: `CONVERSATE_EVENT_PAUSE/RESUME`, `conversate_action_app_pause/resume`, FSM (`conversate_fsm.c`), config params (`summary_and_tag`, `transcribe`, `auto_pop_en`, `use_audio`, `cue_duration`), duplicate detection, reflash events; enum table at `0x002EE7CC`: NONE(0)/START(1)/PAUSE(2)/RESUME(3)/CLOSE(4)/CONFIG(5) | Implemented+: ACK, finalize marker, idle auto-close, **pause/resume/close lifecycle** (firmware enum-derived type values: pause=2, resume=3, close=4) |
| Quicklist + Health | `0x0C-20` -> `0x0C-00` | `...\pb_service_quicklist\pb_service_quicklist.c @ 0x0026FA38`; `[pb.quicklist]quicklist command_id: %d @ 0x002C8D10`; `[pb.health]health command_id: %d @ 0x002D29E0` | Implemented+: stateful quicklist CRUD/toggle/delete + UID paging, plus health save/highlight/query on cmd `10/11/12` with canonical goal/value/avg ordering and fixed32-float metric support |
| Settings / ProtoBaseSettings | `0x0D-00` and `0x0D-20` -> `0x0D-00/01` | settings parse/dispatch chain (`0x4AA30C -> 0x464548`), selector load at `0x4646DA`, descriptor-recovered root/selector schema (`root=0x727E44`, `case3=0x727F1C`, `case4=0x727F34`, `case5=0x727F4C`), parser/notify common path (`0x4AACB4`) with root descriptor load (`literal 0x727E44`) and dispatcher call (`0x46F6EA`), BL-target callsite sweep for `0x4AACB4` (`0x4AAFA0`, `0x4AB016`, `0x4AB098`) with `0x4AB098` resolved as internal wrapper callsite (`0x4AB02C`), wrapper lane artifacts (`2026-03-05-settings-notify-wrapper-callgraph-resolution.*`, `2026-03-05-settings-device-status-wrapper-case4-map.*`), case5 notify wrappers (`0x4AAFB4` recalibration, `0x4AB02C` silent mode), selector4 subtype3 calibration gate/notify branch (`0x464CD2`), wear-enable branch (`selector=5 -> 0x464D04 -> 0x4AB196`), case4 status-lane writers (`settings+0x24/+0x28` via `0x22F20C`), head-up handler (`setting_handle_head_up_setting @ 0x22D228`) and calibration flag helper (`0x22D2D1 -> 0x20073004`), capture-backed compact `0x0D-01` event family + service correlation (`2026-03-05-settings-compact-notify-*`) | Implemented+: dual-lane handler (firmware selector + legacy `cmdId`), canonical selector envelope unwrap (`root case3` only), root case4 local-data response lane, selector `1..11` schema-aware decode, selector-shadow context/bank state, case5 notify-group emission parity on `0x0D-01`, paired case4 local-data status notify parity on selector4 subtype3 gate transitions (`0x4AAF04` lane), compact `0x0D-01` event parity sourced from shared `config_state` mode transitions (`6/11/16` + empty companion packets), inbound root case5 state application, root case6/7 capture shadows for iterative RE, case4 `tag12/tag13` power-lane refresh, case4 `tag17` calibration-UI lane parity |
| Wear Detection | `0x0D-20` / `0x0D-00` + onboarding notify path `0x10-20` / `0x10-00` | `WearDetect_SetEnable @ 0x002F56CC`; `WearDetect_DataHandler @ 0x002F572C`; `get_wear_status @ 0x002FF710`; `onboarding_notify_wear_status_to_app @ 0x002C95D0` | Implemented+: explicit simulator wear enable/status state, onboarding raw wear side-channel packet parity (`0x10-00` `[0x0D, wear]`) documented in app/docs, plus simulator-only deterministic control shim (`cmdId=250`) |
| Display Config | `0x0E-20` -> `0x0E-00` | `CONVERSATE_UI_EVENT_DISPLAY_CONFIG @ 0x002CE540` + capture-backed `0x0E-00` variants; v2.0.7.16: `ALSSyncHandler` (inter-eye brightness sync via OPT3007 ALS), `JBD_CHANGE_BRIGHTNESS no use now` (direct JBD brightness deprecated) | Implemented+: writes trigger capture-backed feedback variants and render-mode notify |
| Logger | `0x0F-20` -> `0x0F-00` | `loggerSetting_common_data_handler` + `/log/` path validation strings @ `0x0026C488` | Implemented+: file list/delete/delete-all, live switch/level/heartbeat state ACKs, `/log/` prefix guard |
| Onboarding | `0x10-20` -> `0x10-00` | `...\pb_service_onboarding\pb_service_onboarding.c @ 0x0026F980`; `onboarding_data_manager.c` side-channel packets | Implemented+: protobuf ACK decode for type/msg/subtype + onboarding flag/process payload, plus raw `0x0D` wear and raw `0x09` head-up packet diagnostics |
| ModuleConfigure + SyncInfo | `0x20-20` -> `0x20-00` | `ModuleConfigureService_common_data_handler @ 0x002BD764`; `SyncInfoService_common_data_handler @ 0x002D559C` | Implemented+: typed ACKs, module-list stub payload, brightness calibration, dashboard auto-close (`<=240` + `0xFF55`) and system-language fallback |
| SystemAlert | `0x21-20` (receive-only) | `system_alert_common_data_handler @ 0x002D5650` | Partial: send-side alert lane modeled; `0x21-00` decode retained only for unexpected diagnostic traffic because firmware does not expose a normal response path |
| SystemClose | `0x22-20` -> `0x22-00` | `system_close_common_data_handler @ 0x002D5728` | Implemented: style-aware response with nested YES/NO/MINIMIZE selection |
| BoxDetect / DisplayTrigger | `0x81-20` -> `0x81-00` | `path_service_box_detect` evidence in `2026-03-03-hardware-functionality-mapping.md` | Implemented: response shape `f1=1, f2=counter, f3={f1=67}` |
| Ring Service | `0x91-20` -> `0x91-00` | `pb_service_ring` + `[pb.ring]ring command_id/event_id/event_param` strings in `firmware-string-cross-reference.json`; `APP_PbRxRingFrameDataProcess`; v2.0.7.16: `RING_CmdTouchUpdata tick/type`, `RING_TASK_MSG_RECONNECT_RING` | Implemented+: `command_id` envelope handling with stateful event (`f3`) and raw-data (`f4`) response payloads |
| SystemMonitor | `0xFF-20` reset magic + `0xFF-00` pushed events | `system_monitor_common_data_handler @ 0x002D562C` | Partial+: pushed event decode + nested `appId`, reset-magic helper documented; normal host query path intentionally treated as diagnostic-only |
| File/OTA transport | `0xC4-00`, `0xC5-00` | `pt_ota_transmit_file`, `ota.service`, `ota.tran` evidence in `2026-03-03-ble-artifact-extraction.md`; `_efsExportFileParse` strings | Implemented+: FILE_CHECK/START/DATA/END lifecycle ACKs + inferred export start/result-check + streamed export data chunks |

## Simulator Implementation Points

Primary implementation lives in:
- `g2-mock-firmware/src/ble_core.cpp`
- `g2-mock-firmware/src/config.h`
- `g2-mock-firmware/src/config_state.cpp`
- `g2-mock-firmware/src/case_state.cpp`

Notable parity updates in this cycle:
- Hardened BLE multi-endpoint orchestration for simulator parity:
  - map connections to `L/R/Ring` using local connection descriptor address (`ble_gap_conn_find`)
  - use hardware active checks (`ble_gap_ext_adv_active`) alongside cached NimBLE state
  - scope notifications to active connection handle when processing endpoint-local requests
  - expose explicit proactive target APIs (`*_to_conn` / `*_to_instance`) for G2/NUS/R1 gesture injection plus devinfo/auth keepalive pushes
  - support serial injection targeting via `@<connHandle>` suffix for deterministic endpoint-local automation
  - route default proactive devinfo/auth pushes as explicit per-connection fan-out (not global notify broadcast)
  - restore connection context across all control/base routed service handlers (`route_g2_packet`) so response routing remains endpoint-local
  - make `g2_next_seq` context-aware (`g_current_conn` -> per-connection counter) to remove cross-endpoint non-auth sequence coupling
  - add capture-backed seq replay assertion harness (`tools/g2_seq_replay_assert.py`) with non-zero assert mode and saved artifacts under `captures/firmware/analysis/`
  - add simulator replay export lines (`[SIM_REPLAY] RX from ... [G2-L/G2-R/R1]`) on outbound G2 response/file notify paths for replay-tool ingestion
  - add CI wiring for replay assertions (`tools/ci_seq_replay_assert.sh`, `.github/workflows/sequence-replay-assert.yml`)
  - add identity-aware endpoint checks in replay assertions (per-label packet counts + median/p90 delta guards for `G2-L/G2-R/R1`)
  - add timestamp-aware endpoint/service dwell checks (max + `P50/P95`) and service-endpoint gates (`SERVICE/ENDPOINT`) in replay assertions
  - add threshold calibration tool (`tools/g2_seq_replay_calibrate.py`) that emits recommended CI flags from long-running replay traces
  - add calibration-drift comparison tool (`tools/g2_seq_replay_calibration_drift.py`) that diffs calibrated recommendations against committed CI defaults and emits structured delta artifacts
  - add calibration-drift history/trend support (`--history-json`, `--trend-*`, `--fail-on-trend`) for directional threshold instability detection across runs
  - add trend quality weighting + acceleration detection (packet/dwell-weighted slope limits + second-derivative checks) in drift analysis
  - add source-class weighting (`--source-class`, `--source-weight-*`) so real-session histories carry higher trend influence than synthetic fixtures
  - add source-manifest backed source labeling with confidence scoring for drift histories (`captures/firmware/analysis/seq-replay-source-manifest.json`)
  - add source-manifest confidence calibration tool (`tools/g2_seq_replay_source_manifest_calibrate.py`) driven by drift-run telemetry (`--out-source-telemetry`), with recency weighting, class-specific stale-prior decay targets/half-life controls, per-rule confusion metrics, class-specific trend-threshold/hard-stop/max-jump guardrails, and time-decayed persisted guardrail debug summaries
  - add deterministic class-action fixture runner (`tools/g2_seq_replay_guardrail_policy_fixture.py`) and wire it into CI to assert `none/limited/blocked` guardrail behavior for `real/synthetic/mixed/unknown`, including stale/fresh half-life boundary sweeps, history-readiness skip-vs-apply checks, recency-floor severity transitions, combined 3-knob parameter-matrix coverage, cross-class mixed metric-vs-debug dominance matrices, and support-gate/stale-prior-decay matrices
  - add labeled synthetic replay fixture in CI to execute endpoint-threshold code paths on every run
  - run auth keepalive scheduling per connection context instead of a global timer
  - enforce identity profile on writes (`G2/NUS` only on left/right; `R1` only on ring)
  - bind deferred teleprompter/conversate/evenhub timeout emissions to the originating connection handle
  - add periodic watchdog re-advertise for unbound identities and richer `adv_status` diagnostics
  - add adaptive ad-mode failover: repeated multi-start failures auto-switch to single-instance round-robin fallback across unbound identities, with periodic probe back to full multi-instance mode
  - surface effective NimBLE runtime config (`max_conn`, `ext_adv`, `max_ext_adv_inst`) in BLE init logs for quick config-drift diagnosis
- Added concrete handlers for `0x03-20`, `0x05-20`, `0x0F-20`, `0x20-20`, `0x21-20`, `0x22-20`, `0xFF-20`, `0x91-20`.
- Routed `0x0D-20` into settings handling (in addition to `0x0D-00`).
- Added logger file-state simulation (`/log/compress_log_*.bin`, `/log/hardfault.txt`).
- Replaced quicklist cache echo with persistent item-state model (full update, add, single, delete, toggle, paging).
- Added onboarding payload fields (`f3`, `f5`) beyond bare ACK.
- Added dashboard/service parity path: `0x01-20` handler + `0x01-00` ACK + `0x0D-00` sync-info state payload.
- Added notification ACK path for `0x02-20` and navigation response path for `0x08-20` -> `0x08-00`.
- Added `0x0E-00` display-config feedback emission (three observed payload families) while preserving mode notify.
- Added dashboard auto-close state handling across settings/module-config paths.
- Added explicit wear-detection state model (`enabled` + `wear/unwear`) with `cmdId=0` snapshot responses and onboarding raw wear side-channel parity (`0x10-00` `[0x0D, wear]`).
- Added simulator-only `cmdId=250` settings shim + serial console wear controls for deterministic automation of wear transitions.
- Added firmware selector-dispatch lane for settings (`selector 1..11`) while preserving legacy `cmdId` compatibility for existing app traces.
- Added selector runtime-context shadow model for firmware context bytes (`+0x01/+0x02/+0x03/+0x04/+0x08/+0x09/+0x0A..+0x0C/+0x14/+0x15/+0x16/+0x17`), selector10 bank arrays (`0x4641EE` parity), and gate parity (`0x2D320`).
- Added settings notify-group emit path (`root case5`) on `0x0D-01`: recalibration notify (`subcase1`) and silent-mode notify (`subcase2`) from selector-backed runtime transitions.
- Added inbound root-case parity for settings envelopes:
  - root case5 decode/apply path (`subcase1/2` -> calibration/silent-mode shadows)
  - root case6/7 first-field capture shadows (field/wire/scalar/blob/seen-count) for continuous firmware-wave analysis
- Added compact settings-status notify parity on `0x0D-01`:
  - payload shape from captures: `f1=1`, `f3={f1=event[,f2=status]}`
  - simulator now sources emits from shared `config_state` transitions (module/mode lane), aligned with capture correlation to `0x06/0x07/0x0B`
  - `settings status` reports compact shadow telemetry from `config_state`
- Added serial-console observability hook `settings status` to dump settings selector shadows, case4 status lanes, and root case6/7 capture counters during replay sessions.
- Corrected descriptor-grounded settings schema mapping:
  - root oneof table `0x727E2C` (`case3=0x727F1C`, `case4=0x727F34`, `case5=0x727F4C`, `case6=0x727FDC`, `case7=0x727FF4`)
  - selector table `0x6ED668` (`1..11 => 0x727E5C..0x727FC4`)
  - root case4 local-data encoder now emits full tags `1..19` with firmware-aligned sources (`tag18=auto_brightness_enabled`, `tag19=unread_message_count lane`)
- Added case4 status-lane parity update:
  - `tag12/settings+0x24` -> inferred battery-percent lane
  - `tag13/settings+0x28` -> inferred charge-state lane
  - `tag17/settings+0x2C` -> inferred calibration-UI lane (`setting_handle_head_up_setting` flow)
  - `tag11/settings+0x20` remains unresolved dashboard callback/session lane
  - selector4 subtype3 gate transitions now emit paired case5/subcase1 + case4 local-data status notifies (`0x4AAF04` parity)
- Added firmware-aligned logger `/log/` path prefix guard.
- Added health-state simulation for shared quicklist/health service (`cmd 10/11/12`).
- Aligned health record parsing/encoding to firmware `pSingleData` ordering (`goal`, `value`, `avg_value`, `duration`, `trend`) with fixed32-float and varint compatibility.
- Added module-config system language handling and `0xFF55` auto-close sentinel support.
- Added inferred file-export simulation (`0xC4:0x03/0x04`, `0xC5` data stream) for logger automation flows.
- Added fragment-aware export chunk headers (`packetTotalNum`/`packetSerialNum`) on simulated `0xC5` export packets.
- Expanded ring relay handler (`0x91`) from echo-only ACK into command-aware event/raw-data envelope simulation.

Module deep dives:
- [modules/ble-multi-connection.md](modules/ble-multi-connection.md)
- [modules/sequence-replay-assertions.md](modules/sequence-replay-assertions.md)
- [modules/quicklist-health.md](modules/quicklist-health.md)
- [modules/display-config.md](modules/display-config.md)
- [modules/file-transfer.md](modules/file-transfer.md)
- [modules/logger.md](modules/logger.md)
- [modules/settings-dispatch.md](modules/settings-dispatch.md)
- [modules/settings-compact-notify.md](modules/settings-compact-notify.md)
- [modules/settings-envelope-parser.md](modules/settings-envelope-parser.md)
- [modules/settings-local-data-status.md](modules/settings-local-data-status.md)
- [modules/settings-headup-calibration.md](modules/settings-headup-calibration.md)
- [modules/settings-selector-schema.md](modules/settings-selector-schema.md)
- [modules/settings-runtime-context.md](modules/settings-runtime-context.md)
- [modules/settings-sync-module-config.md](modules/settings-sync-module-config.md)
- [modules/wear-detection.md](modules/wear-detection.md)
- [modules/ring-relay.md](modules/ring-relay.md)

## v2.0.7.16 Key Discoveries (2026-03-04)

String diff analysis between v2.0.6.14 (23,474 strings) and v2.0.7.16 (23,541 strings) yielded 1,301 new strings:

| Category | Count | Highlights |
|----------|-------|------------|
| Protocol-relevant | 123 | Conversate FSM, ALSSyncHandler, RING_CmdTouchUpdata, reflash events, factory test, codec host protocol |
| Source paths | 330 | Full IAR EWARM project tree — confirms module architecture, build system, and inter-component dependencies |
| Other | 848 | Error messages, config labels, UI strings, CLI commands |

### Protocol Evolution Points
- **Conversate FSM**: Full state machine with pause/resume/close events, config params (summary_and_tag, transcribe, auto_pop_en, use_audio, cue_duration), duplicate packet detection, screen reflash requests
- **ALSSyncHandler**: Inter-eye brightness sync — left eye (master) computes brightness from OPT3007 ALS, syncs to right eye via wired UART. Replaces deprecated `JBD_CHANGE_BRIGHTNESS` direct path
- **RING_CmdTouchUpdata**: Ring touch events now carry tick (duration/timestamp) and type (gesture classification) metadata
- **Codec host protocol**: `[codec.host]Unpack message: cmd=0x%04X(NR=0x%02X, TYPE=0x%02X), seq=0x%02X, flags=0x%02X, length=%d, crc32=0x%08X` — TinyFrame serial protocol details between Apollo510b and GX8002B
- **Factory test**: `PdtGrayScreen_common_data_handler` + `panel_show_gray_screen`/`panel_hide_gray_screen` — production display test mode
- **xip2file**: CLI command for reading XIP flash contents to file (firmware debug/extraction utility)
- **Reflash events**: Conversate/teleprompt/translate services can request screen refresh via `reflash` event pipeline

Full diff saved in `captures/firmware/analysis/2026-03-04-v207-string-diff.json`.

## Firmware Version Corpus

| Version | Build Date | Package Size | Main App Size | Key Changes |
|---------|-----------|-------------|---------------|-------------|
| v2.0.1.14 | 2024-12-16 | 3,720,531 | 2,951,168 | Baseline |
| v2.0.3.20 | 2025-02-10 | 3,870,063 | 3,101,696 | +150KB main app |
| v2.0.5.12 | 2025-04-10 | 3,911,919 | 3,142,656 | +41KB main app |
| v2.0.6.14 | 2025-09-19 | 3,936,175 | 3,166,720 | +24KB main app, +22% touch firmware |
| v2.0.7.16 | 2026-02-13 | 3,958,551 | 3,189,184 | +22KB main app, conversate FSM, ALSSyncHandler, ring touch update |

Cross-version constants (byte-identical all versions): BLE EM9305 (211,948 bytes), codec GX8002B (319,372 bytes).

## Open Reverse-Engineering Queue (Always Active)

1. Recover exact dashboard `0x01-20` field map (command IDs, nested widget payload schema) beyond current stateful ACK/sync shim.
2. Replace translate completion heuristics with firmware-faithful subtype mapping per command/action.
3. Derive exact `ModuleConfigure` field-3 payload schema (module flags, calibration structs, sync-info variants).
4. Validate and correct export opcode assumptions (`0x03/0x04`) from deeper traces and firmware control tables.
5. Recover authoritative `0x91` command/event enum tables and heartbeat/status push semantics beyond current `command_id=1/2` envelope model.
6. Recover exact `health command_id` variant routing (`SingleData/MultData/SingleHighlight/MultHighlight`) and map their protobuf schemas to command paths.
7. Map `SystemAlert` event IDs to concrete firmware-side UI events (IMU reflash/click/scroll classes).
8. Map `SystemClose` user-selection behavior to realistic state transitions and timing windows.
9. Extend runtime mapping from resolved root cases `4/5` to unresolved root oneof cases `6/7` in settings descriptor (`0x727E44`) and identify producer/consumer paths.
10. Resolve remaining unresolved case4 status-mode lane (`tag11/settings+0x20`) and connect it to concrete app event domains; continue tightening `tag17` calibration-lifecycle parity.
11. Recover `0x463F0E`-driven app-visible packet side effects after selector `9/10/11` runtime writes, then model those async responses in simulator.
12. Reconcile canonical EvenHub service usage (`0xE0-20`) versus legacy operational paths in app flows.
13. Add capture-backed regression fixtures per service module so simulator responses are replay-validated against firmware-era traces.
14. Map `RING_CmdTouchUpdata` tick/type values to gesture classification and integrate into ring event envelope decoder.
15. Trace ALS→brightness pipeline end-to-end: OPT3007 raw lux → conversion curve → DAC level (0–42) → ALSSyncHandler inter-eye relay → JBD4010 update.
16. ~~Recover exact conversate FSM state IDs~~ — **RESOLVED** (2026-03-04): Sequential string table at `0x002EE7CC` confirms NONE(0)/START(1)/PAUSE(2)/RESUME(3)/CLOSE(4)/CONFIG(5). Protocol updated.
17. Resolve exact emission conditions for device-status wrapper `0x4AAF04` and map empty companion packet semantics (`08011a00`) to concrete firmware branch conditions.
18. Split simulator GATT/service exposure by endpoint identity (`G2-L`, `G2-R`, `R1`) so discovery and subscription behavior match multi-device hardware topology.
19. ~~Bind all deferred async emits (teleprompter scroll ticks, conversate auto-close, evenhub completion timers) to their originating connection handle~~ — **RESOLVED** (2026-03-05): deferred teleprompter/conversate/evenhub emits now restore per-connection context before notify.
20. ~~Route remaining proactive simulator-originated packets (gesture injectors, forced devinfo/status pushes) through explicit per-connection targeting APIs instead of global fallback.~~ — **RESOLVED** (2026-03-05): added explicit `*_to_conn` / `*_to_instance` APIs and console `@<connHandle>` targeting for G2/NUS/R1 gesture, devinfo, and auth status pushes.
21. ~~Partition non-auth service sequence counters (`g2_next_seq` call sites) by endpoint and replay-verify against multi-connection captures to avoid cross-endpoint counter coupling.~~ — **PARTIALLY RESOLVED** (2026-03-05): partitioning implemented via context-aware `g2_next_seq` + `route_g2_packet` connection context restore; replay verification remains.
22. ~~Build capture-backed replay assertions for per-endpoint sequence evolution (L/R/Ring connected concurrently), and fail simulator CI when counters cross-couple.~~ — **PARTIALLY RESOLVED** (2026-03-05): capture-backed assertion harness implemented (`tools/g2_seq_replay_assert.py`) with `--assert` non-zero gating and baseline artifacts (`2026-03-05-sequence-replay-assertions.*`), CI workflow wiring is active, and simulator replay trace input is supported; endpoint-identity attribution in replay decomposition remains open.
23. ~~Wire `tools/g2_seq_replay_assert.py --assert` into CI and add simulator replay export so cross-coupled counters fail PR checks automatically.~~ — **PARTIALLY RESOLVED** (2026-03-05): CI wiring added (`tools/ci_seq_replay_assert.sh`, `.github/workflows/sequence-replay-assert.yml`), parser accepts simulator replay lines, simulator emits endpoint-labeled `[SIM_REPLAY]` exports on outbound G2 responses, and reports expose detected endpoint labels; real-session threshold calibration remains open.
24. ~~Use simulator endpoint labels (`G2-L/G2-R/R1`) to add identity-aware decomposition and per-identity regression thresholds in `tools/g2_seq_replay_assert.py`.~~ — **PARTIALLY RESOLVED** (2026-03-05): endpoint-labeled metrics/checks implemented (`--require-endpoint-labels`, per-endpoint packet floor, median/p90 guards) and exercised in CI via synthetic labeled replay fixture; thresholds still need calibration against real concurrent simulator logs.
25. Capture real simulator replay logs from true concurrent `G2-L/G2-R/R1` sessions and tune endpoint-threshold defaults/alert bands from empirical distributions.
26. ~~Add calibration-delta automation to compare recommended thresholds with committed CI defaults and emit machine-readable drift reports.~~ — **PARTIALLY RESOLVED** (2026-03-05): `tools/g2_seq_replay_calibration_drift.py` now parses CI defaults, computes recommendation deltas, and emits JSON/Markdown/flag snippets with assert-mode gating; historical trend baselining is still open.
27. ~~Persist calibration drift history and enforce trend-aware guards so repeated directional drift is caught before endpoint churn escapes single-run tolerances.~~ — **PARTIALLY RESOLVED** (2026-03-05): history snapshots, quality-weighted slope/total thresholds, acceleration checks, source-class weighting, manifest-backed source labeling, confidence calibration telemetry loop, class-action fixture gating, half-life boundary sweeps, history-readiness gating coverage, debug recency-floor sweeps, combined 3-knob matrix coverage, cross-class mixed metric-vs-debug dominance matrices, and support-gate/stale-prior-decay matrices are implemented (`tools/g2_seq_replay_calibration_drift.py`, `tools/g2_seq_replay_source_manifest_calibrate.py`, `tools/g2_seq_replay_guardrail_policy_fixture.py`); recency-weight boundary matrix expansion remains open.
28. ~~Add telemetry recency weighting and confidence-decay policy for source-manifest calibration so stale evidence influence is bounded.~~ — **PARTIALLY RESOLVED** (2026-03-05): source-manifest calibration now applies recency half-life weighting, weighted-support gates, class-specific stale-prior decay targets, and per-rule confusion metrics (`TP/FP/FN/TN` + weighted precision/recall).
29. ~~Add per-rule source-class confusion matrices and class-specific decay targets so manifest confidence updates distinguish precision loss from recall loss by source class.~~ — **PARTIALLY RESOLVED** (2026-03-05): confusion metrics and class-specific decay targets are now emitted/applied in calibration reports; recency-weight boundary matrix fixture coverage remains open.
30. ~~Add source-class-specific decay targets and confidence-jump guardrails keyed to weighted precision/recall trends so confidence updates cannot overfit noisy telemetry.~~ — **PARTIALLY RESOLVED** (2026-03-05): upward confidence jumps are now limited/blocked when weighted precision/recall regressions exceed configured thresholds, with class-specific trend gates and smoothed multi-run baselines.
31. ~~Add source-class-specific decay half-life controls and multi-run trend smoothing windows so guardrails are stable under sparse telemetry.~~ — **PARTIALLY RESOLVED** (2026-03-05): class-specific half-life controls are implemented and guardrails now consume smoothed history windows with bounded per-rule history retention.
32. ~~Add source-class-specific guardrail trend thresholds and persisted per-rule guardrail debug summaries so calibration decisions are auditable and less sensitive to class imbalance.~~ — **PARTIALLY RESOLVED** (2026-03-05): class-specific trend thresholds/hard-stops are now supported and per-rule guardrail debug snapshots/history are persisted in manifests.
33. ~~Add source-class-specific guardrail max-positive-jump controls and time-decay weighting for guardrail debug history so stale degradations influence current decisions less.~~ — **PARTIALLY RESOLVED** (2026-03-05): class-specific guardrail max-positive-jump controls are now wired, guardrail decisions now include time-decayed trend smoothing from persisted guardrail debug history, and new calibration parameters/history fields are emitted in reports/manifests.
34. ~~Add calibration-policy fixtures that encode expected `limited/blocked/none` outcomes for each source class under mixed metric/debug histories, then gate CI on those expectations.~~ — **PARTIALLY RESOLVED** (2026-03-05): deterministic fixture runner now asserts class-specific outcomes (`none/limited/blocked`) across `real/synthetic/mixed/unknown` and is wired into `tools/ci_seq_replay_assert.sh` CI flow.
35. ~~Add fixture sweeps for decayed debug-history half-life boundaries (fresh/aged/mixed timestamps) to validate trend-decay transitions and severity scaling under class-specific jump caps.~~ — **PARTIALLY RESOLVED** (2026-03-05): fixture sweeps now assert half-life transitions (`none -> limited`) and severity scaling (`limited -> blocked`) under stale/fresh debug-history mixes in `tools/g2_seq_replay_guardrail_policy_fixture.py`.
36. ~~Add fixture scenarios that enforce history-readiness boundaries (`guardrail_min_history_points`) and assert when guardrail checks must be skipped versus applied.~~ — **PARTIALLY RESOLVED** (2026-03-05): fixture scenarios now force skip-vs-apply outcomes and validate `guardrail_skipped_history_rules` accounting plus clamp behavior in `tools/g2_seq_replay_guardrail_policy_fixture.py`.
37. ~~Add fixture sweeps for debug recency-floor tuning (`guardrail_debug_min_weight`) to validate severity/jump-cap stability when stale-history weight floors are adjusted.~~ — **PARTIALLY RESOLVED** (2026-03-05): fixture sweeps now assert floor-driven action/severity transitions (`none -> limited`, `limited -> blocked`) and allowed-jump scaling across `synthetic` and `unknown` classes in `tools/g2_seq_replay_guardrail_policy_fixture.py`.
38. ~~Add combined parameter-matrix fixture coverage (`guardrail_debug_half_life_days` x `guardrail_debug_min_weight` x `guardrail_min_history_points`) to validate guardrail transition stability under interacting tuning knobs.~~ — **PARTIALLY RESOLVED** (2026-03-05): 8-case matrix coverage is now implemented in `tools/g2_seq_replay_guardrail_policy_fixture.py` and validated in CI, including readiness-gated skip behavior and action transitions under interacting knobs.
39. ~~Expand guardrail parameter-matrix fixtures across source classes (`real/synthetic/mixed/unknown`) and mixed metric-vs-debug dominance scenarios to validate class-specific transition stability under interacting knobs.~~ — **PARTIALLY RESOLVED** (2026-03-05): `tools/g2_seq_replay_guardrail_policy_fixture.py` now executes cross-class (`real/synthetic/mixed/unknown`) matrix sweeps for both debug-dominant and metric-dominant paths across interacting knobs (`guardrail_debug_half_life_days` x `guardrail_debug_min_weight` x `guardrail_min_history_points`) and validates class-specific thresholds/hard-stops/jump caps in CI.
40. ~~Expand fixture matrices to cover support-gate and stale-prior decay interactions (`min_support`, `min_weighted_support`, class-specific decay half-life/target) so confidence updates remain bounded under sparse and aged telemetry.~~ — **PARTIALLY RESOLVED** (2026-03-05): `tools/g2_seq_replay_guardrail_policy_fixture.py` now executes cross-class support-gate and stale-prior-decay sweeps, validating `min_support`/`min_weighted_support` suppression behavior and class-specific decay half-life/target effects under no-support stale priors.
41. Expand fixture matrices to cover recency-weight boundaries (`recency_half_life_days`, `recency_min_weight`) with mixed-age multi-record telemetry so weighted-support gating remains stable under stale-evidence blends.
