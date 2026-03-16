# BLE Multi-Connection Module (`L/R/Ring`)

## Scope
- Simulator-side BLE identity orchestration for three concurrent endpoints:
  - left glasses (`Even G2_32_L_*`)
  - right glasses (`Even G2_32_R_*`)
  - ring relay endpoint (`R1`)
- Advertising, connect/disconnect attribution, and recovery behavior needed to match real hardware pairing flows used by iOS automation.

## Firmware + Capture Evidence (Local)

### Firmware string evidence (`ota_s200_firmware_ota.bin`)
- Advertising control CLI:
  - `AT^BLEADV` (e.g. `START/STOP/STATE`) from `captures/firmware/analysis/firmware-string-cross-reference.json`
- Master connect/disconnect CLI:
  - `AT^BLEMC [Conn/Disc] [addr...]` from the same cross-reference corpus
- Bond reset path:
  - `AT^CLEANBOND`
- BLE scan + ring-state path:
  - `AT^BLEM [Scan/DisScan/RINGSTATE]`
- Ring/peer coupling evidence:
  - `ring_and_peer_sync` in `captures/firmware/analysis/2026-03-03-ble-artifact-extraction.md`

These artifacts confirm the firmware has explicit advertising control, direct peer connect/disconnect handling, ring-state coupling, and bond reset flows.

### Runtime capture evidence
- `captures/20260301-2-testAll.txt` shows the app connecting left and right endpoints in sequence during one run.
- `captures/20260302-2-testAll.txt` and `captures/20260302-3-testAll.txt` show successful R1 ring connection/service probes in the same end-to-end suites used for G2 validation.

## Current Simulator Implementation (`g2-mock-firmware/src/ble_core.cpp`)
- Uses 3 extended advertising instances (`ADV_INST_LEFT/RIGHT/RING`) with fixed random addresses.
- Uses non-legacy, connectable, non-scannable advertising payloads for stable multi-endpoint connectability.
- Maps incoming connections to endpoint identity via low-level descriptor lookup:
  - `ble_gap_conn_find(conn_handle, &desc)`
  - resolves by `desc.our_ota_addr` / `desc.our_id_addr`.
- Uses controller-level active checks (`ble_gap_ext_adv_active`) instead of only cached `NimBLEExtAdvertising::isActive`.
- Adds a periodic advertising watchdog (`ble_tick`, 1.5s) to re-start unbound identities after stack-side drops.
- Adds adaptive advertising failover:
  - default mode is multi-instance extended advertising across unbound identities.
  - if repeated multi-start failures occur while more than one identity is unbound, simulator switches to single-instance fallback.
  - fallback mode round-robins one unbound identity at a time (`L` -> `R` -> `Ring`) to preserve eventual 3-endpoint connectability on controllers that degrade under concurrent adv sets.
  - periodic probe returns to multi-instance mode when stack conditions recover.
- Targets notifications by active connection handle (`g_current_conn`) so command/ACK traffic stays endpoint-local during concurrent sessions.
- Adds explicit proactive-target APIs for simulator-originated packets:
  - `ble_send_*_to_conn(...)` / `ble_send_*_to_instance(...)` for G2, NUS, R1 gestures and devinfo/auth-status pushes.
  - serial console targeting via command suffix `@<connHandle>` (for example `g2_long@9`, `auth_ping@11`).
  - console defaults avoid blind broadcast: gesture injectors route deterministically by profile; `devinfo`/`auth_ping` fan out as explicit per-connection sends.
- Restores per-request connection context for all control/base service routing (`route_g2_packet`), so non-auth responses also stay endpoint-local.
- Uses context-aware sequence generation (`g2_next_seq` -> active connection seq when context exists) to avoid cross-endpoint seq coupling during concurrent sessions.
- Enforces endpoint profile on writes:
  - `G2` + `NUS` + file/display writes are accepted only on `ADV_INST_LEFT/RIGHT`.
  - `R1` writes are accepted only on `ADV_INST_RING`.
  - cross-identity writes are rejected with explicit BLE warnings.
- Binds deferred module emissions to the originating connection:
  - teleprompter scroll progress/completion ticks
  - conversate auto-close timeout notification
  - evenhub deferred completion callback
- Uses per-connection auth keepalive timing (instead of one global timer) so each authenticated endpoint emits its own periodic `0x80-01` status cadence.
- Adds capture-backed replay assertions for non-auth sequence behavior via `tools/g2_seq_replay_assert.py` (`--assert` returns non-zero on regression).
- Replay assertions now support explicit identity requirements (`--expected-endpoint-label G2-L/G2-R/R1`) so CI can fail if any endpoint is missing from simulator replay traffic.
- Replay assertions now include timestamp-aware overlap windows (`--min-expected-overlap-ms`, `--endpoint-idle-timeout-ms`) to gate uninterrupted tri-endpoint dwell behavior in simulator traces.
- Replay assertions now support per-endpoint dwell requirements (`--min-endpoint-dwell G2-L=...`, `G2-R=...`, `R1=...`) so ring and glasses stability can be gated independently.
- Replay assertions now support per-endpoint percentile dwell requirements (`--min-endpoint-dwell-p50`, `--min-endpoint-dwell-p95`) to catch churn before hard disconnect behavior.
- Replay assertions now support service-endpoint percentile dwell requirements (`--min-service-endpoint-dwell-p50`, `--min-service-endpoint-dwell-p95`) to localize churn to concrete module channels.
- Threshold calibration is now scriptable via `tools/g2_seq_replay_calibrate.py`, which emits recommended endpoint/service-endpoint flags and CI snippets from timestamped replay traces.
- Calibration drift is now scriptable via `tools/g2_seq_replay_calibration_drift.py`, which compares calibrated recommendations with committed CI defaults and emits JSON/Markdown/flag-delta outputs.
- Calibration drift now supports persisted history snapshots (`--history-json`) and trend-slope gating (`--trend-*`, `--fail-on-trend`) so repeated directional threshold movement can be flagged.
- Trend drift now includes quality weighting (packet volume + active dwell) and acceleration checks, so short/noisy snapshots are down-weighted and abrupt instability is still caught.
- Trend drift now includes source-class weighting (`real/synthetic/mixed/unknown` with override flag), so real concurrent sessions can be prioritized above CI synthetic fixtures.
- Source-class resolution now supports manifest-backed labeling (`captures/firmware/analysis/seq-replay-source-manifest.json`) with confidence scoring, reducing dependency on path heuristics.
- Source-manifest confidence calibration is now supported via telemetry (`tools/g2_seq_replay_source_manifest_calibrate.py`) with recency weighting, class-specific stale-prior decay targets and half-life controls, per-rule confusion metrics (`TP/FP/FN/TN`), class-specific trend-threshold/hard-stop/max-jump guardrails over smoothed multi-run precision/recall history, time-decayed smoothing of persisted guardrail debug history, and persisted per-rule guardrail debug summaries.
- Deterministic guardrail policy fixtures now run in CI (`tools/g2_seq_replay_guardrail_policy_fixture.py`) to assert class-specific `none/limited/blocked` outcomes for `real/synthetic/mixed/unknown`, including half-life boundary sweeps, history-readiness (`guardrail_min_history_points`) skip-vs-apply checks, recency-floor (`guardrail_debug_min_weight`) severity transitions, combined 3-knob parameter-matrix sweeps, cross-class mixed metric-vs-debug dominance matrices, support-gate/stale-prior-decay matrices, recency-weight support-boundary matrices, and cross-class TP/FP/FN recency-confusion guardrail matrices with asymmetric FP/FN staleness plus support-gate edge variants.
- Emits simulator replay export lines for outbound G2 responses (`[SIM_REPLAY] RX from ... [G2-L/G2-R/R1]`) so sequence assertions can run on simulator traces with endpoint labels.
  - replay lines now include an uptime timestamp prefix (`[HH:MM:SS.mmm]`) to support overlap/dwell assertions.
- Enhances diagnostics:
  - connect/disconnect logs include endpoint mapping source and per-instance runtime state.
  - `adv_status` prints `active_hw`, `active_cached`, `tracked`, ad mode (`MULTI_INSTANCE`/`SINGLE_FALLBACK`), failure streak, and fallback target instance.
  - BLE init logs effective NimBLE runtime config (`max_conn`, `ext_adv`, `max_ext_adv_inst`) so build-time config drift is visible in serial traces.

## Known Gaps vs Hardware
- All identities still share one GATT server surface in the simulator (real topology is physically split across devices).
- Service discovery still exposes the superset attribute table to every identity, even though write-path behavior is now profile-gated.
- Single-fallback mode rotates connectable identity every watchdog window when multi-instance starts fail; this preserves connectivity but may increase scan-to-connect latency versus real hardware behavior.
- Build still reports `CONFIG_BT_NIMBLE_TRANSPORT_EVT_SIZE` redefinition warning (existing upstream config mismatch).

## Next Actionable Improvements
1. Capture a dedicated fallback-validation trace set (`multi-start fail -> single-fallback rotation -> multi-probe recovery`) and store labeled pass/fail artifacts under `captures/firmware/analysis/` for regression gating.
2. Split simulator endpoint service exposure by identity profile (L/R glasses vs R1 ring) so discovery behavior matches real hardware contracts.
3. Add a deterministic BLE stress harness (`connect L -> connect R -> connect R1 -> disconnect/reconnect permutations`, including induced adv-start failure injection) and store pass/fail traces under `captures/firmware/analysis/`.
4. Eliminate NimBLE transport event-size redefinition by aligning sdkconfig/compile-time BLE config sources for both ESP32 targets.
5. Add mixed metric-vs-debug dominance variants to TP/FP/FN recency-confusion sweeps (inject stale debug-trend history along confusion telemetry) so effective-trend arbitration and class-specific threshold/hard-stop behavior stay stable under combined pressure.
