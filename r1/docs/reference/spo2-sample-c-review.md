# R1 SpO2 sample handling in C

`native_spo2_sample.c` implements the 252-byte callback at `0x4ada0` in
ordinary C, reusing the existing GoMore predicate, calibration and SpO2
state/timer coordinator. No assembly or RAM is added. The
[receipt](spo2-sample-c-review.json) binds production hashes, REA bytes,
replay results, rejected defects and build checks.

Raw logging reloads mode and packet fields in native order (2, 5, 4, signed
3, 1, 0). Validation captures the byte after raw logging; wear detection then
precedes a fresh calibration-byte load. A valid sample while worn publishes
event 8 with an eight-byte record: calibrated byte followed by seven zeros.
Calibration logs preserve fresh raw reads and the cached converted value.
Incoming length is ignored. Cleanup always unregisters the incoming handle,
including zero, clears timing-stream slot 1 after unregister, then releases
the fresh shared timer through the existing coordinator. The final flag is
chosen from captured validity, independently of wear or publication result.

Validation passed 13,152 stock/C comparisons, including 48 matching payload
faults and 13,104 completed returns. All byte values, signed log levels,
zero/nonzero handles and timers, changing log modes, state aliases and 768
provider-mutation configurations are covered; 528 mutations are reached.
Comparisons include provider arguments/order/state, guarded SRAM, write
widths, preserved registers, SP, masks and FPSCR on completed returns.
Void R0, caller-clobbered state and private stack bytes are excluded.
Logging-enabled invalid payloads first fault at offset 2; disabled logging
first faults at offset 0, before cleanup.

Another 512 paired comparisons execute both production C helpers over every
byte input. The native pointer predicate is adapted to the C scalar interface.
Calibration equivalence is bounded to this byte domain; the portable helper's
wider integer interface is not asserted equivalent. Actual existing C signed
division and compiler-rt arithmetic execute, including the existing EABI
assembly bridge. Unused imports from the monolithic vendor object are trapped
and verified unreachable. Wear, logging, publication, unregister and the lower
timer-release provider are modeled; the C timer coordinator executes.

Ten compiled defects are rejected: unsigned level, wrong payload read order,
length guard, shared handle substitution, skipping zero-handle unregister,
early stream clear, wrong event, nonzero padding, wrong valid flag and early
completion. All 664 units compile and both relocatable compositions pass.
All 663 prior objects remain unchanged; the scheduler source only adopts the
shared callback prototype. Application imports fall to 164, bootloader imports
remain 34, and no imports are added.

Instruction qualification rejects the callback's relocation pattern. The
canonical plan remains 4,369 source-built bytes, 641,791 executable pull-through
bytes and 248 resource bytes. A fresh hybrid application matches the locked
artifact through that pull-through. Final source-only linking, physical
stream/sensor behavior and concurrency remain unproven.
