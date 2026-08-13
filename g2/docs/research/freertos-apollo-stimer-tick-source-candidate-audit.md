# FreeRTOS Apollo STIMER elapsed-tick/IRQ source-candidate audit

Status: production-excluded G2 clean-room candidate; hardware timing
validation remains mandatory

## Result

The Apollo elapsed-tick dispatcher and compare-A interrupt wrapper are now
separate source-qualified units:

| Role | Stock range | Bytes | SHA-256 |
|---|---:|---:|---|
| elapsed-tick dispatcher | `[0x004563B4,0x00456426)` | 114 | `43a3151849cd96e46d45ad12bb338ea09f586e9fe734b01d485fb9b21c6775fa` |
| IRQ 32 compare-A wrapper | `[0x00456426,0x0045643E)` | 24 | `518fea2d6b0fab0ff4dce31adcaa55015c872000ee314e97987aed9459040f4a` |

These are downstream G2 Apollo port routines, not pristine FreeRTOS or Ambiq
source. The candidate keeps every kernel, interrupt-mask, STIMER, and register
dependency explicit.

## Recovered behavior

The dispatcher reads the wrapping STIMER counter and computes elapsed counts
from `last_compare @ 0x20074884`. The wrap branch deliberately uses
`current + (UINT32_MAX - last)` without adding one; this stock quirk is
preserved. It performs four separate volatile reads of counts-per-tick at
`0x20074888`: two divisions, the remainder product, and compare re-arm.

It aligns `last_compare` down to the last complete tick, re-arms compare A for
`counts_per_tick - remainder`, masks interrupts, calls source-owned
`xTaskIncrementTick` once per elapsed tick, and writes PendSV-set
`0x10000000` to ICSR `0xE000ED04` if any call requests a switch. It then clears
BASEPRI with argument zero, matching stock rather than restoring the ignored
mask return.

The vector-table word at `0x004380C0` is the Thumb pointer `0x00456427` for
external IRQ 32. The wrapper reads raw interrupt status with argument zero,
does nothing unless compare-A bit one is set, and otherwise clears bit one
before dispatching elapsed ticks.

## Qualification

Host tests cover multiple elapsed ticks and aggregated PendSV, the missing
wrap `+1`, partial-tick rearm, compare-A gating, clear-before-dispatch, and the
zero-tick interrupt case. Stock tests pin both spans, complete caller/outgoing
graphs, the vector word, ICSR literal, and the single byte-granular false
interior word candidate.

Apple/Linux emit identical 130-byte dispatcher and 28-byte IRQ functions with
identical relocations. Apple object size/hash is 2,300 /
`a57be26f3424d7ddef546c8510191b5ee168860474c8d465c6c14920474b5141`;
Linux is 2,280 /
`dab49d2e696ca0f8a45b20dab73fa2d3c10e66ad50c2f06f9edd7881ff2a6f8e`.

## Boundary

This closes local semantic opacity in periodic STIMER delivery. Production
remains unchanged pending atomic scheduler/port admission and hardware timing
tests. The remaining scheduler-port algorithm is tickless idle
`[0x00456498,0x0045655C)`, including first-party pre/post-sleep power hooks.

Verification:

```sh
python3 -m unittest -v tests.test_runtime_freertos_apollo_stimer_tick_candidate
```
