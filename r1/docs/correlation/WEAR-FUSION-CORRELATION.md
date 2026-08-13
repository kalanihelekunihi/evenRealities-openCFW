# R1 wear-fusion correlation

Status: seven R1 product functions byte-pinned; clean-room pure policy implemented.

## Outcome

The recovered wear service is product policy around motion, optical-history, living-object,
timer, and topic providers. `r1` now implements the bounded policy in
`r1/src/r1_wear.c`. It does not reproduce the unidentified sensor-stream framework, Goodix
algorithms, CMSIS scheduling, logging, or BLE publication code.

The implementation is deliberately side-effect-free. Callers supply normalized motion statistics
and optical observations, and receive `START_LIVING_PROBE` / `STOP_LIVING_PROBE` action flags.
The Nordic integration layer remains responsible for using admitted SDK/provider APIs to perform
those actions.

## Exact function closure

`tools/summarize_r1_wear_fusion_closure.py` verifies the rebuilt application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`, every function body,
all direct branch callsites, and both indirect callback literals.

| Function | Bytes | SHA-256 | Recovered role |
|---|---:|---|---|
| `0x0003CD80..<0x0003CE12` | 146 | `f116ced7cb0afb9e407c46d6303a75599c9777d518a574cea49e6e4195f121be` | motion callback and fusion dispatch |
| `0x0003CE44..<0x0003CEA2` | 94 | `d6c2c908e569d860d2cb8f8ddef5d451725261bbef9861e1f2e1e81c1c6ad84a` | living-object callback/timestamp |
| `0x0003CEEC..<0x0003D066` | 378 | `80b734b5c2cb4c64f422ebd7c2ca9473160fef4224879a04a1b85658dac77f7e` | three-axis mean/population variance |
| `0x0003D06C..<0x0003D0B4` | 72 | `57d87392bb9452ec09f0fcb09a403ca8588c64ba5768ca6336c47157408995d1` | five-slot optical-history range |
| `0x0003D0C0..<0x0003D0EA` | 42 | `d6ae14c1275550283ca9072f6e55ac7beb5e1e42596aa632b9da832fbd6dbe25` | probe teardown |
| `0x0003D268..<0x0003D38E` | 294 | `57cc089fca628777de825cb9c557c0657bc6b7f7f224e26a7740a0153866dae2` | suspected-wear transition |
| `0x0003D45C..<0x0003D63C` | 480 | `8511cd323737b80efcc86f314395b7f4a89f0b29710947b9b1276243e40efac9` | living/IR/stationary wear-off transition |

The seven Ghidra functions total 1,506 bytes. The callback entry points have no direct branch
callers: exact Thumb literals bind motion callback `0x0003CD81` at `0x0004C614` and living callback
`0x0003CE45` at `0x0003D644`.

The earlier full-service audit in `tools/summarize_r1_wear_fusion_service.py` separately
pins 20 executable ranges and public/lifecycle neighbors. This narrower ownership closure admits
only complete Ghidra functions whose behavior is implemented or isolated here; composite runtime
and generic topic-provider bodies remain outside it.

## Functional contract

The internal states are distinct from the public protocol values:

| Internal state | Meaning | Notification mapping | Explicit-query mapping |
|---:|---|---|---|
| `0` | not worn | `notWear(1)` | `notWear(1)` |
| `1` | suspected worn | `wear(2)` | `wear(2)` |
| `2` | living-confirmed worn | `wear(2)` | `unknown(0)` |

Health-algorithm eligibility requires exact internal state `2`. The explicit-query state-2 mapping
is a verified stock inconsistency and is preserved for compatibility.

Wear-on policy:

- Motion statistics require at least ten samples and use population variance.
- With optical history, an absent baseline permits the initial check. Otherwise the history range
  must be at least `100,000`; the latest IR value must be strictly greater than `9,050,000`.
- Without optical history, any axis variance strictly greater than `2,000.0` enters suspected-worn.

Wear-off policy for suspected-worn:

- A living callback no more than `0x800` ticks old maps status `1` to confirmed and status `0` to
  not-worn. Unsigned tick subtraction preserves wraparound behavior.
- After that window, IR strictly below `9,050,000` for five decisions clears wear, except sleep
  status `1` preserves suspected-worn.
- Absolute mean Y strictly between `972.0` and `1076.0`, with all three variances strictly below
  `40.0`, clears wear after 60 decisions under the same sleep preservation rule.
- Boundary values are not accepted: the comparisons above are intentionally strict.

`r1/tests/test_openr1.c` covers the sample minimum, statistics, optical range, every strict
threshold, the inclusive living window, five/60-decision counters, sleep preservation, negative
gravity orientation, and both public mappings.

## Source and provider boundary

Local source may own only the recovered R1 state transitions, bounded arithmetic, counter policy,
and public mapping. The following stay external:

- motion acquisition and normalization: pinned Bosch BMA456W or ST LIS2DW12 providers plus the R1
  motion adapter;
- optical and living-object production: licensed Goodix provider;
- topic subscribe/unsubscribe, buffers, allocation, and timers: unresolved sensor-stream framework
  or an independently designed adapter over Nordic/CMSIS APIs;
- tick source: CMSIS-FreeRTOS `osKernelGetTickCount`;
- notification transport and protocol dispatch: existing R1 BLE/runtime adapters.

The pure API neither accesses a physical sensor nor performs BLE, flash, timer, or subscription
operations. This keeps provider code attributable and prevents the decompilation evidence from
becoming a vendor-library rewrite.

## Reproduction

```sh
python3 tools/summarize_r1_wear_fusion_closure.py
make -C openR1 test
make -C openR1 sanitize
make -C openR1 arm-objects
```
