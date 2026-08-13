# R1 touch-slider and gesture-event correlation

## Decision

Thirteen functions / 2,784 executable bytes are now admitted as R1 product behavior: twelve formerly unclassified Ghidra functions / 2,776 bytes plus one eight-byte manual provenance
supplement. This closure contains no IQS7211E register implementation and no Azoteq provider state
machine. It starts after the existing R1 IQS7211E adapter has produced normalized touch samples and
ends at the product gesture/event dispatcher.

The decisive ownership edge is the odd Thumb pointer `0x00092CBD` stored at `0x0008E7CC`. The R1
touch-service initializer at `0x0008E7B0` installs it through the callback setter/thunk at
`0x00067460` / `0x00093388`. The target `0x00092CBC` contains the R1 slider state machine and
explicit `RING` diagnostics for uninitialized scale, coordinate overflow, and slider-event press
timeout. It has no direct callsite because it is invoked through that registered callback.

The controller-facing bus, register, communication-end, ATI recovery, and reset semantics remain
owned by the separately pinned IQS7211E provider and R1 port boundary. This closure is only the
ring-specific calibration, press/release/slide/click timing policy, event assembly, and service
callback plumbing that may be implemented as clean-room behavior.

## Exact functions

| Entry | Bytes | Clean-room role |
| --- | ---: | --- |
| `0x0003E938` | 690 | `r1_touch_gesture_dispatch` |
| `0x00059AAC` | 238 | `r1_touch_slider_velocity_filter` |
| `0x00067460` | 12 | `r1_touch_slider_callback_setter` |
| `0x0008E758` | 70 | `r1_touch_slider_calibration` |
| `0x0008E7B0` | 22 | `r1_touch_service_callback_registration` |
| `0x0008E9D0` | 50 | `r1_touch_pending_tap_timeout` |
| `0x00092C70` | 66 | `r1_touch_release_debounce` |
| `0x00092CBC` | 1,422 | `r1_touch_slider_state_machine` |
| `0x00093388` | 4 | `r1_touch_slider_callback_setter_thunk` |
| `0x000933FC` | 8 | `r1_touch_ready_irq_callback` (manual supplement) |
| `0x00093404` | 12 | `r1_touch_ready_callback_setter` |
| `0x00093424` | 180 | `r1_touch_synthetic_release_dispatch` |
| `0x00093504` | 10 | `r1_touch_task_event_post` |

The 1,422 executable bytes of `0x00092CBC` are noncontiguous:

- `0x00092CBC..<0x000930D8`
- `0x0009320C..<0x00093320`
- `0x00093322..<0x00093380`

The omitted `0x000930D8..<0x0009320C` region is a literal/string pool, and the two-byte gap at
`0x00093320` is not executable ownership. The manual IRQ callback is exactly
`0x000933FC..<0x00093404`; it posts touch-task event bit `1` through `0x00093504`.

## Recovered configuration and behavior

The initial product configuration at runtime address `0x200067C4` establishes:

- long-press threshold: raw time `1000`;
- normalized active coordinate bounds: `10...180`;
- pressure reference: `240.0`;
- initial pressure peak: `400.0`;
- normalized coordinate span: `200.0`.

Calibration at `0x0008E758` consumes the recovered per-ring endpoint bytes. It multiplies each raw
endpoint by `213.3333282470703`, stores the lower endpoint as the origin, and divides the resulting
span by `200.0` to produce the coordinate scale. The state machine refuses to emit a normal event
when that scale is zero, clamps normalized coordinates above 200, and maintains observed minimum
and maximum coordinates.

The three-sample velocity helper at `0x00059AAC` treats coordinate deltas of `-3...3` as neutral,
tracks direction outside that dead band, clears accumulated speed on reversal, computes
`abs(delta) * 100 / elapsed`, saturates at 255, and smooths later samples as 40% new plus 60%
previous. The release helper at `0x00092C70` recognizes the fifth qualifying release inside the
2,501-raw-unit window while touch service state permits it.

The product event byte is a composable bitset:

| Bit | Recovered event |
| --- | --- |
| `0x01` | press |
| `0x02` | release |
| `0x04` | tap/click |
| `0x08` | multi-click completion |
| `0x10` | long press |
| `0x20` | negative-direction slide |
| `0x40` | positive-direction slide |
| `0x80` | press timeout/error |

Slide events include an absolute coordinate delta and the smoothed velocity byte. The first
movement gate requires a 50-unit coordinate delta; tracking updates use 15 units, at least 100 raw
time units between accepted movements, pressure-delta rejection at 1000, and the recovered
150-unit early-pressure gate. A held press beyond 10,000 raw time units is reset and reported as
`0x80`. Release policy distinguishes short interior clicks, longer interior clicks, slides, and
the recovered multi-click sequence before forwarding the four-byte record to
`r1_touch_gesture_dispatch`.

## Reproducible evidence

The static census pins the application image, all thirteen entry/body hashes, every executable
segment and direct caller, the indirect callback pointer, initial configuration, and event map:

```sh
python3 tools/summarize_r1_touch_slider_closure.py
```

The parser accesses no live GPIO or I2C bus and emits no raw IQS7211E sender. These functions are
eligible for an independent product-behavior implementation; the attributable controller provider
remains separately sourced and fail-closed until its required hardware/provider conditions pass.
