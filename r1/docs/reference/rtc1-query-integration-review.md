# R1 RTC1 tick and kernel-query integration

All 1,046 integrated scenarios pass, covering 1,228 handler invocations.
The candidate executes the actual C RTC1 handler, tick getter and
scheduler-state query from the normal build. Only `xTaskIncrementTick` is
replaced with a function mock; earlier handler tests mocked the two queries
as well. No firmware source change was needed.

The increment mock advances the same shared tick word modulo 32 bits and
returns a scripted switch request. Repeated handler calls therefore observe
the updated tick through the real getter. Tests cover zero/single/multiple
correction steps, 24-bit RTC and 32-bit tick wrap, scheduler word combinations,
four interrupt masks, alternating/high-bit switch results and callbacks
changing scheduler state, the counter or BASEPRI. Independent per-invocation
checks verify correction counts, final tick, PendSV-set and restored BASEPRI.

Complete ordered peripheral/shared-word reads and writes, BASEPRI access,
increment calls, PendSV/SEV ordering and final state match stock. The mock
poisons r0–r3; r4–r11, entry SP and callback eight-byte alignment pass. Private
stack depths differ and are recorded separately.

RTC and SCB are controlled MMIO models. Kernel tick list maintenance, task
switch selection and actual context switching remain outside this test.
No physical clock/interrupt, exception entry/return, event-register or
sleep/wake claim is made. Complete fault state, private spills, timing and
byte identity remain open.

The probe binds the unchanged source/object hashes to the existing successful
562-unit R1 report. No new compile was needed. No source-plan selection or
workflow gate changed.

[rtc1-query-integration-review.json](rtc1-query-integration-review.json)
binds build/source identities, the preceding REA-backed handler/query
reviews and ignored probes under `build/goal-r1-rtc-query-integration/`.
