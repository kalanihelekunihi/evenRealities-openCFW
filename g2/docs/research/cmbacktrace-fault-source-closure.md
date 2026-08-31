# CmBacktrace fault-path source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

Status: implemented in compilable source; physical fault-path validation is
explicitly blocked by unavailable authorized hardware evidence. This closure
does not replace the production HardFault vector, sign an image, or access a
device.

The authenticated compatibility snapshot at upstream commit
`73714489f9d8af130aacb515586b397b604a5768` supplies all six public
CmBacktrace definitions. The exact vendor checkout remains unknown; the stock
image proves only the compatible interval recorded in
[`cmbacktrace-version-recovery-audit.md`](cmbacktrace-version-recovery-audit.md).
The recovered configuration selects FreeRTOS, English diagnostics, M33-class
fault behavior, 40-byte names, 32 call-stack entries, and 16 dump-stack words.

`tools/analyze_g2_cmbacktrace_fault_source.py` performs a freestanding
Cortex-M55/Thumb target build of the complete upstream implementation with
warnings as errors. The object exports:

- `cm_backtrace_init`
- `cm_backtrace_firmware_info`
- `cm_backtrace_call_stack_any`
- `cm_backtrace_call_stack`
- `cm_backtrace_assert`
- `cm_backtrace_fault`

Its unresolved symbols are an exact, audited platform seam: five linker-range
symbols, three FreeRTOS task adapters, formatted output/string helpers, the
logging port, and `__aeabi_memclr4`. No implementation body remains missing.

The maintained C file
`components/shared/cmbacktrace/runtime_cmbacktrace_fault_entry.c` implements
the Cortex-M exception entry as a naked function. Its disassembly is audited
to copy `lr` into `r0`, copy `sp` into `r1`, call `cm_backtrace_fault`, and
loop if the call unexpectedly returns. The distinct symbol
`open_cfw_cmbacktrace_hardfault_entry` deliberately avoids claiming
`HardFault_Handler` or taking over the vector table before device evidence
exists.

The official 786-byte stock `cm_backtrace_fault` body at
`[0x005944BC,0x005947CE)` remains SHA-pinned. The selected source also retains
the historical pre-`55e7b699` exception-frame alignment behavior found in the
official image; this is parity, not a claim that the later safety fix is
undesirable.

Run the reproducible gate with:

```sh
make cmbacktrace-fault-closure
```

Promotion of the vector requires an authorized responsive G2 and deliberate
fault injection that validates register capture, FreeRTOS task and stack
bounds, logger output, floating-point exception frames, and terminal behavior.
The authorized right temple is nonresponsive/unavailable and the left temple
remains stock, so that evidence cannot presently be collected.
