# R1 guarded byte event adapter in C

`r1_event_callback_0004210c` in
`r1/src/application/board/native_event_callbacks.c` now uses ordinary C in
place of its naked assembly body. It calls service `0x4c4b8` only when the
full 32-bit length equals 1, passing the payload's low byte zero-extended.
Other lengths return without a service call. It does not dereference payload.
REA byte reads match the locked application; local disassembly of the service
shows that the incoming R0 is its sole input before calls overwrite R1.
The service remains an unresolved implementation. A size-zero frontier row
records its entry only, alongside a 12-byte callback anchor.

[The review receipt](conditional-event-c-review.json) records production object
hashes, REA evidence and 2,120 paired stock/C replays. At the service entry or
normal return, all R0–R12, SP, LR, APSR, PRIMASK, BASEPRI, CONTROL, FPSCR and
S0–S31 match. Neither body writes RAM. The cases include all 256 byte payloads,
high-bit payload values, exact and non-exact lengths, varied flags and masks.
Three separately compiled defects are rejected: testing only length's low byte,
omitting payload narrowing and inverting the length guard.

The compiler emits an ITE-based 12-byte sequence, different from stock's
branch-based sequence. Exact qualification therefore rejects this callback;
no new source-plan region is admitted. The one-argument service declaration
avoids a redundant MOVS reload of the already-tested length, which otherwise
changes APSR. Two other null/length-wrapper probes also changed APSR and remain
assembly. Probe sources and diagnostics stay under ignored
`build/goal-r1-conditional-events-c/`.

All 619 units compile and both relocatable payloads compose without duplicate
strong symbols. The 618 other objects and 105 other allocated sections of the
event unit are unchanged. Its strong symbols and imports are unchanged, with
166 application and 34 bootloader imports remaining. The canonical plan is
unchanged; a fresh hybrid retains 4,295 source-built bytes and matches locked
application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

This proves the tested adapter boundary, not the service implementation,
physical hardware behavior, a complete source-only link or instruction identity.
