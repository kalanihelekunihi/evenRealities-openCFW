# G2 touch application-policy helper source closure

Status: isolated MIT candidate complete for all eight clean-room boundaries.
Four sufficiently established helpers are implemented directly; four opaque
hardware/private-policy boundaries require providers and fail closed.

## Scope

The helper-attribution tranche identified eight reachable functions as G2
application-policy rather than Infineon or toolchain code:

| Stock entry | Evidence name | Candidate closure |
|---:|---|---|
| `0x0268` | `touch_config_read_adapter` | implemented |
| `0x071C` | `saved_proximity_baseline_read` | implemented |
| `0x0738` | `touch_config_load_from_eeprom` | implemented |
| `0x07FC` | `attention_release_timeout_rearm` | fail-closed provider |
| `0x0BE8` | `timeout_default_1000_if_zero` | implemented |
| `0x0BFC` | `gesture_policy_helper_0bfc` | fail-closed provider |
| `0x0D70` | `touch_gesture_state_machine` | fail-closed provider |
| `0x111C` | `proximity_baseline_update_adapter` | fail-closed provider |

The new source is
`components/shared/touch/runtime_touch_policy_helpers.c` with its public header
`runtime_touch_policy_helpers.h`. It is not production-routed by this tranche.

## Implemented behavior

The executable helpers cover only authenticated behavior:

- a storage read is bounded to the stock 256-byte logical window, requires
  explicit ready/read callbacks, and translates missing, not-ready, range, and
  provider failures into distinct statuses;
- config load installs the observed `UNVE` (`0x45564E55`) defaults, reads the
  exact eight-byte config layout into a temporary object, validates the magic,
  and commits only valid data;
- saved-baseline read requires both a valid-config flag and `UNVE` magic before
  returning the u16 baseline;
- the zero timeout default returns 1000, while every nonzero value is preserved.

Config defaults remain available after storage failure, but the load function
still returns the actual negative error. It does not silently report success.

## Fail-closed providers

The remaining behavior is not filled in speculatively:

- attention rearm requires one transactional callback with the observed
  200-millisecond argument; the MIT source contains no GPIO address or delay
  implementation;
- both gesture bodies share an explicit observation/result callback. Missing,
  failed, or out-of-range provider results leave the caller's result unchanged;
- baseline update passes the saved baseline to an external provider and commits
  the returned current baseline only after success.

Absent callbacks return `OPEN_CFW_TOUCH_POLICY_UNAVAILABLE`. Provider failures
return `OPEN_CFW_TOUCH_POLICY_PROVIDER_ERROR`. No fallback gesture, GPIO,
CapSense, EEPROM, or timing semantics are invented.

## License boundary

The source, header, fixture, tests, analyzer, and manifests in this tranche use
MIT SPDX markers. The source audit rejects direct PSoC MMIO constants and
Infineon CAPSENSE/Em_EEPROM symbol dependencies.

The public Infineon EULA sources identified by the preceding attribution work
remain external providers only. No CAPSENSE or Emulated EEPROM implementation
is copied or compiled into this candidate. Apache-2.0 CAT2 PDL and upstream
toolchain-runtime decisions likewise remain outside this isolated component.

## Verification

`tools/analyze_g2_touch_policy_helpers_source.py` pins the source, header, and
host fixture; re-runs the 44-helper attribution audit; requires exact coverage
of the eight clean-room entries; compiles for Cortex-M0+; checks the eight
exports; and emits:

- `tools/manifests/g2-touch-policy-helper-source-closure.tsv`;
- `tools/manifests/g2-touch-policy-helper-source-summary.json`.

Host tests exercise valid/invalid config, storage range/readiness, default and
saved-baseline behavior, missing providers, provider errors, transactional
gesture/baseline commits, the 200 ms attention contract, and a freestanding
Thumbv6-M compile.

Run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 \
  g2/tools/analyze_g2_touch_policy_helpers_source.py --write-manifests
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest \
  g2/tests/test_analyze_g2_touch_policy_helpers_source.py \
  g2/tests/test_runtime_touch_policy_helpers.py -v
```

This work performs no device access, MMIO, reset, DFU, flash, signing, timing
measurement, or electrical test and makes no hardware-validation claim.
