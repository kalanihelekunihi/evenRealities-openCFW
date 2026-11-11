# R1 kernel tick and scheduler query closure

The selected task-query unit now supplies the pinned FreeRTOS C bodies for
`xTaskGetTickCount`, `xTaskGetTickCountFromISR` and `xTaskGetSchedulerState`.
They use the same recovered tick/running/suspended words as the selected
scheduler units: `0x20007828`, `0x20007830` and `0x20007850`. Application imports
fall from 232 to 229, with no added imports and bootloader imports still 34.
The existing task-count function's instruction bytes are unchanged.

REA confirms stock tick reads at `0x987C4`, ISR tick reads at `0x987D0` and
the scheduler-state query at `0x987A8`. The ISR path calls interrupt-priority
validation before reading the tick. The first C candidate omitted that call
because the port header selected its macros before the assertion definition
was visible. Including the existing native assertion contract before
`FreeRTOS.h` preserves the validation call. Initial and corrected object
evidence is bound in the JSON. The 32-bit atomic tick configuration is
asserted at compile time.

All 3,002 comparisons pass, covering 86 tick values, four BASEPRI masks,
both PRIMASK values, state-word combinations and mutations between ordered
reads. The canonical tick getter and the native `0x7D2A0` branch thunk are
checked against the same C provider; no duplicate thunk implementation is
added. The ISR validator mock poisons caller-saved registers and optionally
changes the tick word before returning, verifying that validation precedes
the fresh read. Return values, memory reads, absence of state writes,
r4–r11/SP preservation, unchanged masks and callback alignment pass.

The actual priority-validator body and assertion faults are outside this
probe. Full kernel initialization/scheduling, physical interrupt delivery,
complete fault state, private spills and timing remain unverified. Candidate
body sizes are 12/18/30 bytes versus stock's 6/12/22; no whole-image byte
identity or source qualification is claimed.

All 562 R1 units compile and both compositions pass without duplicate strong
symbols. `make sources-check` passes for both device trees. No source-plan
selection or workflow gate changed.

[rtos-query-closure-review.json](rtos-query-closure-review.json) binds source,
upstream/configuration/build hashes, initial include-order evidence, native/
candidate bytes, REA results and ignored probes under
`build/goal-r1-rtos-queries/`.

The subsequent [RTC1 integration](rtc1-query-integration-review.md) executes
the actual queries with the tick handler in 1,046 scenarios, moving the mock
boundary down to tick advancement.
