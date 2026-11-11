# R1 FreeRTOS critical-section dependency closure

The selected Nordic port unit now supplies `vPortEnterCritical` and
`vPortExitCritical`, resolving two application imports (238 to 236) without
adding objects or duplicate strong symbols. The complete SDK port remains
excluded because it duplicates other selected functions. The pair is adapted
from its licensed C, using the existing recovered nesting word `0x20007814`
already used by scheduler startup. Captured local transition values avoid
extra reads of the volatile contract cell. The scheduler-start body is
unchanged.

Stock enter at `0x95CF4` writes BASEPRI 64, increments the nesting word with
32-bit wrap, and checks ICSR active-vector bits only when the new count is
one. Stock exit at `0x95D24` asserts on zero, decrements once and clears
BASEPRI only when the new count is zero. The existing selected assertion
contract masks BASEPRI and attempts a four-byte zero store at `0xFFFFFFFF`.

All 372 M-class execution comparisons pass: nesting values 0/1/2/3 and both
upper 32-bit extremes, seven ICSR patterns, four starting masks, balanced
depths 1–8 and unbalanced/mixed sequences. Checks compare ordered BASEPRI
write values, nesting/ICSR reads and counter writes, final state, per-call
results and assertion-store access kind/address/size/value. Valid returns
preserve r4–r11 and entry SP. ICSR is a controlled register model; this does
not test real interrupt delivery, scheduler execution, full exception
escalation or complete fault-register/private-stack state.

REA was attempted for both functions but Ghidra returned a decompilation
failure: memory-range construction beyond the RAM address space. The
functions contain the deliberate end-of-address-space assertion store; no
target bytes were altered to bypass the failure. No completed REA pseudocode
is claimed. Stock instruction decoding and direct execution support this
review, and the diagnostics are retained.

All 561 R1 units compile and both compositions pass. Application imports are
236 and bootloader imports remain 34, with no new imports. `make sources-check`
passes for both trees. Byte/timing identity and physical interrupt behavior
remain unproven. No source-plan selection or workflow gate changed.

[rtos-critical-closure-review.json](rtos-critical-closure-review.json) binds
source/upstream/contracts/build hashes, native/candidate bytes, REA failure
diagnostics and ignored probes in `build/goal-r1-rtos-critical/`.
