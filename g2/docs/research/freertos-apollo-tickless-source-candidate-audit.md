# FreeRTOS Apollo STIMER tickless-idle source-candidate audit

Status: production-excluded G2 clean-room candidate; first-party power policy
and hardware sleep/timing validation remain explicit gates

## Result

The complete G2 tickless-idle override at `[0x00456498,0x0045655C)` is
196 bytes with SHA-256
`d6716a7a132b61665a401d513ce75119e5210640f69f5d16424067cb4216e8da`.
Its only direct caller is the authenticated FreeRTOS idle task at
`0x004555FC`. It is downstream Apollo/power integration rather than pristine
FreeRTOS or Ambiq source.

## Recovered contract

The function clamps requested idle ticks to `max_suppressed_ticks`, disables
interrupts, and aborts cleanly when `eTaskConfirmSleepModeStatus()` returns
zero. Otherwise it computes elapsed STIMER counts from the last aligned
compare, preserving the same stock wrap formula without `+1`, and programs
compare A for `expected_ticks * counts_per_tick - elapsed`.

The first-party pre-sleep hook receives the clamped tick count. WFI executes
only when that hook returns nonzero; the post-sleep hook always runs. On wake,
the function recomputes complete ticks and remainder, aligns the last-compare
global, clears STIMER compare A and pending IRQ 32, re-arms compare A, caps
elapsed complete ticks to the requested interval, calls source-owned
`vTaskStepTick`, and re-enables interrupts.

## Qualification

Host tests cover the full sleep/WFI path, abort, maximum clamp, pre-hook WFI
suppression, elapsed-step cap, rearm arithmetic, and wrap behavior before and
after sleep. The stock test pins the complete body, sole caller, all ten
outgoing calls, three global literals, and absence of stored entry/interior
words.

Apple and Linux emit the same 192-byte function with SHA-256
`253c0ab060d9ed9eee8c73e89e028b17c5eb61b810410fe00a106b0d51ab265b`
and identical 19 relocations. Apple object size/hash is 2,260 /
`d48efce527610f422d19a33e43f89e37b0f26811d18002e7025a18b8e3ed00c4`;
Linux is 2,240 /
`75211fd04388f5987a0eec5d148d2fbf2f17d96bbd0909cd2bd30d688b256bbd`.

## Boundary

Together with the setup and elapsed-tick/IRQ candidates, every bounded Apollo
STIMER scheduler algorithm is now source-recreated. Production remains
unchanged because the pre/post-sleep hooks are first-party power policy and
real WFI, counter wrap, IRQ latency, and compare timing need device validation.
The remaining FreeRTOS port work is atomic scheduler/global integration and
trace/application-hook ownership rather than an opaque STIMER algorithm.

Verification:

```sh
python3 -m unittest -v tests.test_runtime_freertos_apollo_tickless_candidate
```
