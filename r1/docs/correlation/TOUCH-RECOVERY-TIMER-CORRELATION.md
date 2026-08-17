# Touch recovery-timer correlation

## Decision

The 72-byte callback at `0x00046EAC..<0x00046EF4` is R1 task policy
around the touch recovery latch and CMSIS event flags. It is classified
`r1_product_specific` / `clean_room_behavior_only`. The clean implementation is
the pure `r1_touch_recovery_timer_plan_build`; it does not clear live firmware
state, call an RTOS primitive, log, or access the IQS7211E.

## Exact callback and registration

| Range | Bytes | SHA-256 |
| --- | ---: | --- |
| `0x00046EAC..<0x00046EF4` | 72 | `9d328097ca50117b08d6ca156979e387453ea6d873a1d6922252359a6d07afbd` |

There are no direct branch callers. The touch dispatcher stores the exact Thumb
pointer `0x00046EAD` at `0x00046898`. The callback first calls the recovered
pending-latch clear at `0x0007287C`, performs diagnostics only, and tail-branches
to the task event poster at `0x00093504` with bit `2`.

The curated script's separate `0x00046908` seed is not a function. It is the
four-byte word `0x00000052` immediately before the independently exported
20-byte timer-cancel function at `0x0004690C`; the seed was off by four bytes.
The census retains that error as an explicit non-function-data adjudication,
while the real `0x0004690C` function keeps its existing ownership row.

## Clean plan

`r1_touch_recovery_timer_plan_build` emits exactly two obligations:

- clear the recovery-pending latch;
- post `R1_TOUCH_RECOVERY_OPEN_EVENT_FLAG` (`0x00000002`) to the touch task.

The caller owns provider execution and ordering. Null output fails with
`R1_ERROR_ARGUMENT`, and no platform callback is embedded in the plan.

## Verification

```sh
python3 tools/evidence/summarize_r1_touch_recovery_timer.py
```

The evidence check pins the complete callback, recovered image, pointer
registration, latch-clear edge, and event-post tail edge. Host tests verify the
typed plan and null-output failure.
