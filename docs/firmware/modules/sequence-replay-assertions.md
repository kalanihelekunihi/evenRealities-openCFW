# Sequence Replay Assertions (Multi-Endpoint Seq Counters)

## Scope
- Capture-backed assertions for non-auth G2 response sequence behavior.
- Detect cross-coupled seq-counter regressions (single global counter behavior) in mixed multi-endpoint traffic.
- Provide a CI-friendly gate (`--assert` non-zero exit) that can be run against capture traces and simulator replay exports.

## Firmware + Capture Evidence
- Source captures (local):
  - `captures/20260302-2-testAll/*`
  - `captures/20260302-3-testAll/*`
- Assertion artifact outputs:
  - `captures/firmware/analysis/2026-03-05-sequence-replay-assertions.json`
  - `captures/firmware/analysis/2026-03-05-sequence-replay-assertions.md`
- Both captures pass current thresholds with strong multi-stream signatures:
  - global median delta: `96..97`
  - two-stream median delta: `45.5..66`
  - median improvement: `31..50.5`

## Tooling
- Script: `tools/g2_seq_replay_assert.py`
- Default run (captures only):
  - `python3 tools/g2_seq_replay_assert.py --assert`
- Simulator replay export run:
  - `python3 tools/g2_seq_replay_assert.py --assert --trace <simulator-log.txt>`
- Tri-endpoint identity run (`G2-L/G2-R/R1` must all appear):
  - `python3 tools/g2_seq_replay_assert.py --assert --trace <simulator-log.txt> --require-endpoint-labels --expected-endpoint-label G2-L --expected-endpoint-label G2-R --expected-endpoint-label R1 --min-endpoint-count 3`
- Tri-endpoint dwell run (minimum concurrent overlap window):
  - `python3 tools/g2_seq_replay_assert.py --assert --trace <simulator-log.txt> --require-endpoint-labels --expected-endpoint-label G2-L --expected-endpoint-label G2-R --expected-endpoint-label R1 --min-endpoint-count 3 --min-expected-overlap-ms 12000 --endpoint-idle-timeout-ms 500`
- Endpoint-specific dwell run (independent per-label gates):
  - `python3 tools/g2_seq_replay_assert.py --assert --trace <simulator-log.txt> --require-endpoint-labels --min-endpoint-dwell G2-L=12000 --min-endpoint-dwell G2-R=12000 --min-endpoint-dwell R1=12000 --endpoint-idle-timeout-ms 500`
- Endpoint-specific percentile dwell run (`P50/P95` active windows):
  - `python3 tools/g2_seq_replay_assert.py --assert --trace <simulator-log.txt> --require-endpoint-labels --min-endpoint-dwell-p50 G2-L=12000 --min-endpoint-dwell-p50 G2-R=12000 --min-endpoint-dwell-p50 R1=12000 --min-endpoint-dwell-p95 G2-L=12000 --min-endpoint-dwell-p95 G2-R=12000 --min-endpoint-dwell-p95 R1=12000 --endpoint-idle-timeout-ms 500`
- Service-endpoint percentile dwell run (`SERVICE/ENDPOINT`):
  - `python3 tools/g2_seq_replay_assert.py --assert --trace <simulator-log.txt> --require-endpoint-labels --min-service-endpoint-dwell-p50 06-00/G2-L=12000 --min-service-endpoint-dwell-p50 07-00/G2-R=12000 --min-service-endpoint-dwell-p50 91-00/R1=12000 --min-service-endpoint-dwell-p95 06-00/G2-L=12000 --min-service-endpoint-dwell-p95 07-00/G2-R=12000 --min-service-endpoint-dwell-p95 91-00/R1=12000 --endpoint-idle-timeout-ms 500`
- Save reproducible artifacts:
  - `python3 tools/g2_seq_replay_assert.py --assert --trace <trace-or-capture> --out-json captures/firmware/analysis/<stamp>.json --out-md captures/firmware/analysis/<stamp>.md`
- CI wrapper:
  - `tools/ci_seq_replay_assert.sh`
  - workflow: `.github/workflows/sequence-replay-assert.yml`
- Calibration tool (derive recommended thresholds from long traces):
  - `python3 tools/g2_seq_replay_calibrate.py --trace <simulator-log.txt> --endpoint-idle-timeout-ms 500 --min-intervals 3 --guardband-p50 0.80 --guardband-p95 0.80 --out-json captures/firmware/analysis/<stamp>-calibration.json --out-md captures/firmware/analysis/<stamp>-calibration.md --out-ci captures/firmware/analysis/<stamp>-calibration.flags`
- Calibration drift tool (compare recommendations vs committed CI thresholds):
  - `python3 tools/g2_seq_replay_calibration_drift.py --trace <simulator-log.txt> --ci-script tools/ci_seq_replay_assert.sh --source-manifest captures/firmware/analysis/seq-replay-source-manifest.json --endpoint-idle-timeout-ms 500 --min-intervals 3 --guardband-p50 0.80 --guardband-p95 0.80 --drift-warn-ms 1500 --drift-warn-ratio 0.20 --history-json captures/firmware/analysis/seq-replay-calibration-drift-history.json --history-window 20 --trend-min-points 3 --trend-warn-slope-ms 250 --trend-warn-total-ms 1000 --trend-warn-accel-ms 350 --trend-weight-min-packets 450 --trend-weight-min-active-ms 12000 --trend-weight-floor 0.25 --source-class auto --source-confidence-floor 0.50 --source-weight-real 1.0 --source-weight-synthetic 0.35 --source-weight-mixed 0.70 --source-weight-unknown 0.85 --expected-source-class real --out-source-telemetry captures/firmware/analysis/<stamp>-source-telemetry.ndjson --out-json captures/firmware/analysis/<stamp>-calibration-drift.json --out-md captures/firmware/analysis/<stamp>-calibration-drift.md --out-ci captures/firmware/analysis/<stamp>-calibration-drift.flags`
- Source-manifest confidence calibration tool (update rule confidence from telemetry):
  - `python3 tools/g2_seq_replay_source_manifest_calibrate.py --manifest captures/firmware/analysis/seq-replay-source-manifest.json --telemetry captures/firmware/analysis/<stamp>-source-telemetry.ndjson --min-support 5 --min-weighted-support 1.5 --blend-alpha 0.60 --recency-half-life-days 30 --recency-min-weight 0.10 --decay-half-life-days 45 --decay-half-life-real 60 --decay-half-life-synthetic 30 --decay-half-life-mixed 45 --decay-half-life-unknown 20 --decay-target-confidence 0.50 --decay-target-real 0.55 --decay-target-synthetic 0.50 --decay-target-mixed 0.50 --decay-target-unknown 0.45 --guardrail-max-positive-jump 0.20 --guardrail-max-positive-jump-real 0.18 --guardrail-max-positive-jump-synthetic 0.20 --guardrail-max-positive-jump-mixed 0.20 --guardrail-max-positive-jump-unknown 0.16 --guardrail-trend-threshold 0.05 --guardrail-trend-threshold-real 0.04 --guardrail-trend-threshold-synthetic 0.05 --guardrail-trend-threshold-mixed 0.05 --guardrail-trend-threshold-unknown 0.06 --guardrail-trend-hard-stop 0.20 --guardrail-trend-hard-stop-real 0.18 --guardrail-trend-hard-stop-synthetic 0.20 --guardrail-trend-hard-stop-mixed 0.20 --guardrail-trend-hard-stop-unknown 0.24 --guardrail-history-window 5 --guardrail-min-history-points 2 --guardrail-history-max-points 20 --guardrail-debug-max-points 40 --guardrail-debug-half-life-days 21 --guardrail-debug-min-weight 0.05 --out-json captures/firmware/analysis/<stamp>-source-calibration.json --out-md captures/firmware/analysis/<stamp>-source-calibration.md --out-manifest captures/firmware/analysis/<stamp>-source-manifest.calibrated.json`
- Guardrail policy fixture assertions (class-specific `none/limited/blocked` expectations):
  - `python3 tools/g2_seq_replay_guardrail_policy_fixture.py --out-json captures/firmware/analysis/<stamp>-guardrail-policy-fixture.json`

### Assertion Model
- Input packets:
  - capture verbose RX lines (`[RX] RX from ... | <hex>`)
  - simulator replay export lines (`[SIM_REPLAY] RX from <conn> [<endpoint>] | <n> bytes | <hex>`) with optional timestamp prefix (`[HH:MM:SS.mmm]`)
  - G2 response packets (`aa12...`)
  - non-auth services only (`svc_hi != 0x80`)
- Metrics:
  - global forward-seq delta distribution
  - greedy two-stream decomposition delta distribution
  - endpoint-labeled per-identity delta distributions (`G2-L/G2-R/R1`) when simulator labels are present
  - endpoint activity windows (`max/p50/p95`) from timestamped replay lines
  - service-endpoint activity windows (`service/endpoint`, for example `06-00/G2-L`)
  - stream balance / stream packet counts
- Pass/fail thresholds (current defaults):
  - `min_packets=120`
  - `min_global_median_delta=64`
  - `min_two_stream_improvement=20`
  - `min_stream_balance=0.60`
  - `min_stream_packets=30`
  - `require_endpoint_labels=false` (set true in identity-focused checks)
  - `expected_endpoint_labels=[]` (set to `G2-L/G2-R/R1` for tri-endpoint assertions)
  - `min_endpoint_count=2`
  - `min_endpoint_packets=30`
  - `max_endpoint_median_delta=8`
  - `max_endpoint_p90_delta=24`
  - `min_expected_overlap_ms=0` (disabled by default)
  - `endpoint_idle_timeout_ms=3000`
  - `min_endpoint_dwell_ms={}` (disabled by default; set with `--min-endpoint-dwell LABEL=MS`)
  - `min_endpoint_dwell_p50_ms={}` (disabled by default; set with `--min-endpoint-dwell-p50 LABEL=MS`)
  - `min_endpoint_dwell_p95_ms={}` (disabled by default; set with `--min-endpoint-dwell-p95 LABEL=MS`)
  - `min_service_endpoint_dwell_ms={}` (disabled by default; set with `--min-service-endpoint-dwell SERVICE/ENDPOINT=MS`)
  - `min_service_endpoint_dwell_p50_ms={}` (disabled by default; set with `--min-service-endpoint-dwell-p50 SERVICE/ENDPOINT=MS`)
  - `min_service_endpoint_dwell_p95_ms={}` (disabled by default; set with `--min-service-endpoint-dwell-p95 SERVICE/ENDPOINT=MS`)
- CI wrapper also builds a synthetic tri-endpoint fixture and enforces:
  - expected labels: `G2-L`, `G2-R`, `R1`
  - `min_endpoint_count=3`
  - `min_endpoint_packets=100`
  - `max_endpoint_median_delta=4`
  - `max_endpoint_p90_delta=8`
  - timestamped fixture + `min_expected_overlap_ms=12000`, `endpoint_idle_timeout_ms=500`
  - endpoint-specific dwell thresholds: `G2-L=12000`, `G2-R=12000`, `R1=12000`
  - endpoint-specific percentile thresholds: `P50/P95 >= 12000` for `G2-L/G2-R/R1`
  - service-endpoint percentile thresholds: `06-00/G2-L`, `07-00/G2-R`, `91-00/R1` with `P50/P95 >= 12000`
  - calibration drift assertions against committed CI thresholds (`drift_warn_ms=1500`, `drift_warn_ratio=0.20`) using `tools/g2_seq_replay_calibration_drift.py`
  - persisted drift snapshot writes (`history-json`) so trend telemetry is always emitted in the CI fixture run
  - source classification from `captures/firmware/analysis/seq-replay-source-manifest.json` (CI synthetic fixture path matches `synthetic` manifest rules)
  - source telemetry capture + confidence calibration dry-run (`tools/g2_seq_replay_source_manifest_calibrate.py`) from CI fixture telemetry, including recency weighting, class-specific decay targets, class-specific jump caps, and precision/recall trend guardrail flags
  - class-specific guardrail policy fixture assertions (`tools/g2_seq_replay_guardrail_policy_fixture.py`) so `real/synthetic/mixed/unknown` expected actions stay stable, including short/long half-life decay sweeps, history-readiness (`guardrail_min_history_points`) skip-vs-apply gating checks, recency-floor (`guardrail_debug_min_weight`) severity sweeps, combined 3-knob parameter-matrix coverage, cross-class mixed metric-vs-debug dominance matrix coverage, support-gate/stale-prior-decay matrix coverage, recency-weight support-boundary matrix coverage, and cross-class TP/FP/FN recency-confusion guardrail matrices with asymmetric FP/FN staleness plus support-gate boundary variants (`min_weighted_support` edge around `1.0`) so `none -> limited -> blocked` transitions and support suppression are exercised together.

### Calibration Output Contract
- `tools/g2_seq_replay_calibrate.py` outputs:
  - `endpoint_stats`: interval-count + `p50/p95/max` + recommended `p50/p95` thresholds per endpoint.
  - `service_endpoint_stats`: same metrics keyed by `SERVICE/ENDPOINT`.
  - `ci_snippet`: ready-to-paste flags for `tools/g2_seq_replay_assert.py`.
- Recommendation logic:
  - recommendations are derived from observed percentile values with guardbands (`recommended = observed * guardband`), clamped by `min/max threshold` bounds.
  - keys with insufficient interval count (`--min-intervals`) are reported but not recommended.

### Calibration Drift Output Contract
- `tools/g2_seq_replay_calibration_drift.py` outputs:
  - `baseline_thresholds`: parsed `--min-endpoint-dwell-p50/p95` and `--min-service-endpoint-dwell-p50/p95` maps from CI script.
  - `recommended_thresholds`: calibrated percentile recommendations from trace input.
  - `entries`: per-key delta table (`baseline`, `recommended`, `delta_ms`, `delta_ratio`, `status`, `action`).
  - `ci_patch_snippet`: flag lines for keys that drift or are missing in CI defaults.
  - `history`: history/trend config + snapshot count.
  - `trend_entries`: per-key history trend stats (`points`, `first/last`, `total_delta_ms`, `slope_ms_per_run`, `status`, `action`).
  - `trend_summary`: aggregate status counts for trend drift.
  - source metadata: manifest/heuristic source class (`real/synthetic/mixed/unknown`) plus confidence and effective source weight.
  - `source_telemetry`: optional telemetry payload for manifest-confidence calibration (`expected`, `predicted`, `correct`, matched rule indexes).
- Trend weighting and acceleration:
  - per-snapshot quality weight is derived from observed packets and endpoint active-window duration (`median endpoint p50 active ms`), then clamped by `--trend-weight-floor`.
  - trend slope limits and total-delta limits are scaled by inverse quality, so low-quality snapshots require larger movement to trigger drift.
  - acceleration checks (`--trend-warn-accel-ms`) detect abrupt directional changes even when long-window slope is still moderate.
  - source-class weighting (`--source-class`, `--source-weight-*`) further prioritizes real-session snapshots over synthetic fixture runs.
  - when `--source-manifest` is set, source class and confidence are resolved from manifest rules first; heuristics are only used when no manifest is supplied.

### Source Manifest Contract
- File: `captures/firmware/analysis/seq-replay-source-manifest.json`
- Shape:
  - `rules[]` entries support:
    - `path` or `path_glob` to match trace paths
    - `input_format` to match parser-detected formats (`capture_verbose_rx`, `sim_replay_rx`)
    - `source_class` (`real|synthetic|mixed|unknown`)
    - `confidence` (`0..1`)
  - `default` fallback with `source_class` and `confidence`.
- Resolution:
  - matched rule confidences are aggregated per class, winner class is selected by score, and confidence is normalized from winner/total score.
  - `--source-class` can still force explicit override when needed.
- Drift status semantics:
  - `aligned`: absolute/relative delta within tolerance (`--drift-warn-ms`, `--drift-warn-ratio`).
  - `drift`: tolerance exceeded; CI threshold should be raised/lowered.
  - `missing_ci_default`: recommendation exists but no corresponding CI flag.
  - `insufficient_calibration_data`: key was targeted but interval evidence was below `--min-intervals`.
- Assert mode:
  - `--assert` exits non-zero on drift or missing CI defaults.
  - `--fail-on-insufficient` also fails when data is insufficient.
  - `--fail-on-trend` also fails when trend drift thresholds are exceeded.

### Source Telemetry Contract
- `--out-source-telemetry` appends one NDJSON record per run containing:
  - predicted source class/confidence/method
  - optional expected source class (`--expected-source-class`) and correctness
  - matched manifest rule indexes (`matched_rule_indices`)
  - quality signals (`packets_analyzed`, `median_endpoint_p50_ms`)
- `tools/g2_seq_replay_source_manifest_calibrate.py` uses these records to adjust rule confidence by recency-weighted observed accuracy/alignment, emits per-rule confusion metrics (`TP/FP/FN/TN`, weighted precision/recall), applies class-specific stale-prior decay targets/half-lives, applies class-specific trend-threshold/hard-stop + max-positive-jump guardrails over smoothed multi-run history, applies time-decayed smoothing to persisted guardrail debug history, and persists per-rule guardrail debug snapshots/history in calibrated manifests.

## Current Simulator Link
- Runtime changes in simulator already partition seq generation by active connection context:
  - `g2_next_seq()` now uses `g_current_conn` context when available.
  - `route_g2_packet(...)` restores request-scoped connection context for all routed services.
- Simulator now exports normalized replay lines for outbound G2 response/file notifications:
  - emitted from `g2-mock-firmware/src/ble_core.cpp` send paths (`send_g2_response`, `send_file_response`)
  - format: `[HH:MM:SS.mmm] [SIM_REPLAY] RX from <connHandleHex> [G2-L|G2-R|R1|GLOBAL] | <len> bytes | <hex>`
- This assertion harness is the replay-side regression detector for those changes.

## Next Actionable Improvements
1. Add explicit 3-stream decomposition scoring (`L/R/R1`) and compare against 2-stream fit to detect partial coupling.
2. Add per-service scorecards (`0x06/0x07/0x0B/0x0D/0x91`) to isolate where cross-coupling begins.
3. Add mixed metric-vs-debug dominance variants to the TP/FP/FN recency-confusion matrices (inject stale debug history spikes alongside confusion records) so `effective_trend_drop = max(metric_drop, debug_drop)` arbitration is validated with class-specific thresholds/hard-stops.
