# Sub-32-byte frontier correlation

The sub-32-byte inventory tier is now source-routed: 268 functions, 4,326 declared body bytes
(4,282 range-pinned; 44 remote continuation bytes recorded as omitted). Thirty functions in the
tier stayed unclassified: shared intrusive-list/hash helpers used by both the registry and
sensor-stream candidates, one unidentifiable FreeRTOS-global getter called from queue-FromISR
functions (`0x0009566C`), registry operation wrappers on orphaned record blocks with no callers,
and callerless validators/stubs with no topology.

| Family | Functions |
| --- | ---: |
| R1 product-specific | 165 |
| Goodix GH3X2X candidate | 21 |
| Sensor-algorithm heap candidate | 21 |
| GoMore licensed-provider candidate | 19 |
| Sensor-stream framework candidate | 15 |
| YHM2710 candidate | 14 |
| Shared quantized-neural runtime candidate | 4 |
| Generic device-registry candidate | 4 |
| Nordic nRF5 SDK 17.1.0 | 3 |
| Arm toolchain runtime | 2 |

Every provider-candidate and unresolved-framework entry above carries the
`vendor_source_required_not_redistributable` or `investigate_before_implementing`
disposition and remains implementation-blocked.

## Exact upstream closures

`0x00030CA8`, `0x00030CB8`, and `0x00030CC8` are the Nordic `nrfx_pwm.c` per-instance vector
stubs `nrfx_pwm_0_irq_handler`, `nrfx_pwm_1_irq_handler`, and `nrfx_pwm_2_irq_handler`: each is a
single-call wrapper passing the instance register base (`0x4001C000`, `0x40021000`,
`0x40022000`) and its successive control block to the pinned shared `irq_handler` at
`0x00072A32`. The stock vector table routes TIMER4 and MWU slots into two of these stubs; that
wiring is vendor board configuration, while the code is Nordic's.

`0x000620F4` is the toolchain `fabs` (double-precision sign-bit clear) and `0x00098ECA` is
`fabsf` (`vcmpe.f32 #0` + conditional negate). Both are second statically-linked runtime copies
inside provider regions; the clean-room build links the selected toolchain runtime instead.

## R1 product anchors

165 small product closures: event-loop and queue helpers, connection/ble state accessors, the
`vApplicationMallocFailedHook` body (privileged BASEPRI halt loop, sole caller the FreeRTOS
pvPortMalloc failure path) as the R1 malloc-failed hook, a SysTick/scheduler guard at
`0x00033350`, ack/event record plumbing, and product configuration accessors — anchored by
RING-tagged diagnostics, pinned R1 state structures, and product call topology.

## Provider and framework boundaries

YHM2710 candidates include the transport write wrappers and thunks around `0x00035760`/
`0x0003540C`, the `0xF8`/`0xA8` command senders, registry slot dispatches on the YHM record at
`0x2000687C`, the charge-state nibble map, and the stacmd delay loop. Sensor-algorithm-heap
candidates are the guarded free-and-null helpers, buffer descriptor initializers, and teardown
steps consumed exclusively by Goodix/gated teardown chains. Four sensor-stream and four registry
plumbing candidates follow the framework regions and the `0x20015708`/`0x20015404` structures.

## Documented reservations

- `0x00033350` is R1 product rather than the FreeRTOS family: the guarded pattern has no exact
  match in the pinned SDK 17.1.0 port sources.
- The registry lock pair `0x00097730`/`0x00097748` and chain walkers `0x0005DA30`/`0x0005DBEA`
  are filed as registry candidates on mutex-table evidence; they are framework plumbing
  regardless of the final framework attribution.
- GXT310 register read/write glue without a recovered GXT310-specific marker stays out of the
  GXCAS gate; see `NAMED-PERIPHERAL-BOUNDARIES.md`.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_frontier_sub32.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
