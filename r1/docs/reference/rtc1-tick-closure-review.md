# R1 RTC1 FreeRTOS tick dependency closure

The selected RTC port now includes the pinned Nordic RTC-mode tick handler,
resolving `RTC1_IRQHandler` without enabling the duplicate full SDK port.
The existing configuration maps `xPortSysTickHandler` to that symbol. The
timer-setup function's instruction body is unchanged. Application imports
fall from 236 to 235, with no added imports and bootloader imports still 34.

Stock entry `0x316E8` clears compare event zero with readback, saves BASEPRI
and masks at 64, captures the RTC1 counter, then clears tick with readback.
It computes a 24-bit difference from the kernel tick, clamps gaps above one
when the scheduler is not running, and ORs the correction-call results. A
nonzero switch request writes PendSV-set and executes SEV before restoring
the saved mask. The application vector word at offset `0x84` is `0x316E9`,
the Thumb target of this stock entry. This does not validate final placement
of a complete source vector table.

All 932 M-class comparisons pass. They cover zero/single/multiple correction
steps, 24-bit wrap, suspended versus running states, four starting masks,
alternating and high-bit switch results and callback changes to the counter
or interrupt mask. Ordered MMIO accesses/readbacks, BASEPRI reads/writes,
scheduler calls, correction counts, PendSV/SEV ordering and final state match.
Mocks poison r0–r3; r4–r11, entry SP and callback eight-byte alignment pass.
Private stack depths differ and are recorded separately. Large running-state
gaps are not exhaustively executed; large suspended gaps are tested.

REA supplies stock control-flow evidence, but its pseudocode abstracts
privileged-register operations and reorders some expressions. Direct
instruction execution establishes the hardware access order here. RTC/SCB
are controlled register models and the scheduler APIs are mocks. Physical
clock drift, interrupt delivery, full scheduler execution, SEV sleep/wake
effects, complete fault state and timing remain unverified. The candidate
handler is 124 bytes versus stock's 96; no byte identity is claimed.

All 561 R1 units compile and both compositions pass without duplicate strong
symbols. `make sources-check` passes for both device trees. No source-plan
selection or workflow gate changed.

[rtc1-tick-closure-review.json](rtc1-tick-closure-review.json) binds source,
upstream/configuration/build hashes, stock/candidate bytes, native vector,
REA results and ignored probes in `build/goal-r1-rtc1-tick/`.
