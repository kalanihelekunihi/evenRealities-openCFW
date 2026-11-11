# R1 RTC1 tickless-idle dependency closure

The selected RTC unit now supplies the pinned Nordic
`vPortSuppressTicksAndSleep` body using the existing recovered tickless
contract. This includes its FPU exception preparation and stock error
reporter binding, rather than the SDK defaults alone. Application imports
fall from 233 to 232 with no new imports; bootloader imports remain 34.
The RTC1 tick handler and timer-setup instruction bodies are unchanged.

All 904 stock/candidate comparisons pass. They cover aborted sleep, zero and
clamped idle times, 24-bit counter wrap, debug correction clamping, both
initial PRIMASK values, nested NVIC critical state, enabled/disabled
SoftDevice, SVC success/error returns, repeated WFE polling and pending FPU
exceptions. Comparisons include ordered RTC/NVIC/shared-state reads and
writes, mask transitions, callback arguments and final state. Explicit
checks verify compare targets, tick stepping, skipped wait/FPU paths on
abort or zero idle, and clearing FPSCR exception flags while retaining its
unrelated seeded state. Mocks poison r0–r3; r4–r11, entry SP and callback
eight-byte alignment pass.

The candidate links the normal `nrf_nvic_state` definition. The probe models
NVIC enable/clear aliases and pending flags. Scheduler sleep confirmation,
SoftDevice enabled query, tick stepping and error reporting are mocks; SVC
`0x41` returns a selected status. WFE is detected and skipped at a controlled
wake point, so polling behavior is checked without claiming actual sleep.
FPSCR is initialized through VMSR/VMRS before measurement to establish an
active emulated FP context. Those setup instructions exist only in the
ignored probe, never in a firmware provider.

REA recovers the stock 286-byte function and its control flow. The compiled
candidate body is 354 bytes; private stack depths differ and are recorded.
Physical clock/sleep current/wake latency, real SoftDevice execution, FPU
lazy stacking, interrupt delivery, complete fault state, timing and whole-
image byte identity remain unverified.

All 562 R1 units compile and both compositions pass without duplicate strong
symbols. `make sources-check` passes for both device trees. No source-plan
selection or workflow gate changed.

[rtc1-tickless-closure-review.json](rtc1-tickless-closure-review.json) binds
source/upstream/configuration/build hashes, shared-state provider, native/
candidate bytes, REA results and ignored probes under
`build/goal-r1-rtc1-sleep/`.
