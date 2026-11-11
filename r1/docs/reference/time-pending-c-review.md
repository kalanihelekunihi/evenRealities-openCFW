# Pending time-update flag: C replacement and 12 exact bytes

The current [constraint-free clock review](time-update-pure-c-review.md) supersedes the register/frame constraints below. Both entries now use ordinary C; Clang and GCC retain the backend/state contract without byte identity or incidental caller-register requirements.

`application/runtime/native_time_update.c` now implements the setter at
`0x8aea4` with a C byte store and return. Its naked body, four assembly
instructions and authored literal were removed. An empty R0/R1 compiler
constraint preserves the native register results; it emits no instructions.
The adjacent backend-update adapter remains assembly and is unchanged.

REA read the complete native eight-byte body and four-byte state literal.
It stores one byte, value 1, at `r1_time_state + 11`, returns R0=1 and leaves
R1 pointing at the state root. The typed state layout has an offset assertion.
REA's xref query returned no entries despite the visible native call at
`0x42a34`; that result is not evidence of complete caller coverage.

The normal Clang object passes 4,096 stock/C execution pairs: every prior
flag byte, four neighboring-memory patterns and four incoming APSR patterns.
Checks compare all R0–R12, APSR, LR, SP, interrupt masks, neighboring state,
stack contents and the sole byte-write address/width/value. Negative controls
reject a wrong offset, wrong value and an additional caller-register clobber.
GCC compiles but uses R3 for its narrowed byte value; it fails the full-register
comparison and is not qualified.

Official qualification compiles ten generic and six supported GCC variants.
The Clang `-Oz` fragment matches all 12 native bytes, including its relocated
literal, and is admitted through the official source-plan selection. The
qualifier also finds the retained assembly parent; that parent is not newly
admitted. The prior source-plan prefix is unchanged.

All 576 R1 units compile with no failures or duplicate strong symbols.
The other 575 objects, manifest and strong symbol sets are unchanged. The
parent's code and relocations are unchanged. Imports remain 164 application
and 34 bootloader symbols.

The canonical hybrid rebuild retains locked application SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Source-built coverage increases from 4,023 to 4,035 bytes; retained executable
bytes decrease to 642,125, with 248 resource bytes. Source-built totals include
assembly and data. Complete source firmware remains unproven.

The separate tick-callback investigation tested seven source/flag variants;
all retain a 16-byte callback frame instead of the native eight bytes. Those
probes remain ignored, and the callback and compile-only bootstrap were not
changed. Concurrency, arbitrary faults and physical device behavior remain
outside this setter validation.

The [machine-readable receipt](time-pending-c-review.json) records the REA
evidence, execution, negative controls, GCC limitation, qualification and
audits. Probes are under `build/goal-r1-time-pending-c/` and
`build/goal-r1-clock-tick-frame/`.

The subsequent [time-update C review](time-update-c-review.md) replaces the formerly retained parent assembly with C, validates both compiler parents and preserves the existing exact source plan.
