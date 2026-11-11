# ST25 millisecond delay native binding

`board/stock_seams.c::r1_st25_delay_ms` now calls the existing
`r1_rtt_delay_cycles(64000)` once per millisecond. Native `0x784f0` performs
that exact handoff to the subtract-three loop at `0x99cd0`; REA and raw
instructions agree. The six-byte source primitive matches that native
body. The previous C seam depended on the excluded microsecond wrapper.
That import is now used only by software-TWI records and remains unresolved.

The probe passes 275 stock/C comparisons: 135 bounded modeled cases through
4,095 iterations, five actual-primitive cases for 0–4 ms, and 135 first-
handoff cases covering selected and random full-width inputs. Zero returns
without invoking the primitive. Each completed case checks its full call
count and the argument `64000`; handoff cases stop at the first primitive
entry and do not claim that enormous countdowns complete. Actual loop
instructions execute in both native and source runs for the five actual
cases. Modeled returns clobber caller-saved registers and flags.

Checks verify callee-saved registers, SP, interrupt masks, callback alignment,
unchanged memory outside private stack frames, and no non-stack data writes.
R0 is unowned because this is a void API. The native callback frame is at
caller SP-24 and C uses SP-8. The C wrapper is 26 bytes versus 28 native
instruction bytes; primitive identity does not establish wrapper identity.

Other public seam functions, log strings and the log-mode cell retain exact
bytes and relocation identities. The other 561 source units are unchanged.
All 562 R1 units compile without failures or duplicate strong symbols;
imports remain 211 application / 34 bootloader. Eligibility is unchanged
and `make sources-check` passes. Exact bindings are in
[the machine-readable review](st25-c-delay-binding-review.json).

CPU frequency, elapsed time, physical NFC/ST25/wire behavior, private frames,
arbitrary faults, exceptions, cycle identity, final boot/linking,
qualification and whole-image byte identity remain unproven. No G2 gate
or source-plan selection changes.
