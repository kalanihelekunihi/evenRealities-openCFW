# R1 application fault entries in C source

The locked 2.2.6.0009 application has five exception entries at
`0x274ac`, `0x274b8`, `0x274c4`, `0x274d0` and `0x274dc`. Disassembly shows
each moves exception LR to R0 and handler SP to R1, calls the CmBacktrace
fault provider, then calls the reset adapter at `0x7a5e0`. That adapter writes
reset tag 7, captures the reset site and requests an architectural reset.

`r1/src/application/rtos/native_fault_vectors.c` now owns those five entries
and the reset adapter. Each `naked` C entry uses only a three-instruction ARM
register handoff, preserving LR and the original handler SP before any C
prologue. Shared C then calls the existing CmBacktrace, reset-trace and CMSIS
reset providers in stock order. Object disassembly and relocations confirm
the register handoff and call sequence. This removes five unresolved vector
symbols without using stock executable bytes or a default-handler substitute.

The 952-unit source build at `build/r1-fault-vectors-final-20261110/report.json`
compiles 870 application and 82 bootloader units, with no failures or
duplicate strong symbols. The strict bootloader link passes. The application
link receipt at `build/r1-fault-vectors-final-20261110/app-link/report.json`
reports 51 unresolved references and 218,520 bytes of FLASH overflow.

The source-level exception path is not byte-identical to stock. The selected
CmBacktrace provider and R1 diagnostic extensions need integration review,
and physical fault entry, final RAM placement and reset-record contents have
not been tested on hardware.

## Pure C entry probe, 2026-11-11

A current R1 Clang `-Os` probe under `build/r1-fault-c-probe-20261111/`
uses `__builtin_return_address(0)` and `__builtin_frame_address(0)` to pass
the exception LR and the original handler SP to `r1_fault_entry`. The
compiled entry first pushes R7 and LR, then adds eight to its frame pointer
to reconstruct the prior SP. This changes live handler SP and writes two
stack words before the fault recorder runs, which is material on a stack
fault. Clang also rejects the normal two-argument `musttail` call from a
zero-argument vector, and rejects C statements in a `naked` function. The
probe therefore does not replace the production register-only vector
adapters or establish a safe assembly-free fault path.
