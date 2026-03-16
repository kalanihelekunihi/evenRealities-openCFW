# Sequence Replay Validation

Capture-backed validation of G2 response packet sequence counters, testing the hypothesis that non-auth RX packets (`aa12`, `svc_hi != 0x80`) from split capture logs and simulator replay exports exhibit multi-endpoint counter separation (left eye vs right eye maintaining independent sequence counters).

The method compares global sequence deltas against a greedy two-stream fit to detect multi-endpoint counter separation.

## Thresholds

| Parameter | Value |
|---|---:|
| `min_packets` | 120 |
| `min_global_median_delta` | 64 |
| `min_two_stream_improvement` | 20 |
| `min_stream_balance` | 0.6 |
| `min_stream_packets` | 30 |
| `require_endpoint_labels` | False |
| `min_endpoint_count` | 2 |
| `min_endpoint_packets` | 30 |
| `max_endpoint_median_delta` | 8 |
| `max_endpoint_p90_delta` | 24 |

## Results

| Trace | Input Formats | Endpoint Labels | Packets | Global Median Delta | 2-Stream Median Delta | Improvement | Stream Counts | Balance | Status |
|---|---|---|---:|---:|---:|---:|---|---:|---|
| `captures/20260302-2-testAll` | `capture_verbose_rx` | `-` | 157 | 97.00 | 66.00 | 31.00 | [82, 75] | 0.915 | PASS |
| `captures/20260302-3-testAll` | `capture_verbose_rx` | `-` | 176 | 96.00 | 45.50 | 50.50 | [85, 91] | 0.934 | PASS |

## Assertion Details

### `captures/20260302-2-testAll`

| Assertion | Threshold | Actual | Result |
|---|---|---|---|
| `min_packets` | >= 120 | 157 | PASS |
| `global_median_delta` | >= 64 | 97.00 | PASS |
| `two_stream_improvement` | >= 20 | 31.00 | PASS |
| `stream_balance` | >= 0.60 | 0.915 | PASS |
| `stream_packets` | min stream >= 30 | [82, 75] | PASS |
| `endpoint_labels_presence` | required: no | skipped (no endpoint labels observed) | PASS |

### `captures/20260302-3-testAll`

| Assertion | Threshold | Actual | Result |
|---|---|---|---|
| `min_packets` | >= 120 | 176 | PASS |
| `global_median_delta` | >= 64 | 96.00 | PASS |
| `two_stream_improvement` | >= 20 | 50.50 | PASS |
| `stream_balance` | >= 0.60 | 0.934 | PASS |
| `stream_packets` | min stream >= 30 | [85, 91] | PASS |
| `endpoint_labels_presence` | required: no | skipped (no endpoint labels observed) | PASS |

## Endpoint Metrics

### `captures/20260302-2-testAll`

No endpoint-labeled replay packets in this trace.

### `captures/20260302-3-testAll`

No endpoint-labeled replay packets in this trace.

## Improvements

1. Extend inference to 3-stream decomposition for traces that include ring protocol responses with enough packet density.
2. Add per-service decomposition metrics (`0x06/0x07/0x0B/0x0D`) to localize cross-coupling regressions.
3. Use endpoint labels (`G2-L/G2-R/R1`) for identity-aware decomposition and per-identity regression thresholds.
