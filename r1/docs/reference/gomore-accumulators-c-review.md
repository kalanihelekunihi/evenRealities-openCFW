# R1 GoMore accumulators in C, 2026-11-10

The locked `r1-2.2.6.0009/application.bin` (SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`)
contains a step accumulator at `0x61198` and an activity accumulator at
`0x61274`. Their native ABI adapters now live in
`r1/src/application/runtime/native_gomore_step_accumulate.c` and
`native_gomore_activity_accumulate.c`, each using its existing C primitive.
The step stage returns zero and logs the completed float as a double. The
activity stage returns zero, updates a 52-byte state behind a pointer cell,
and writes a 44-byte output.

Paired ARM Cortex-M4 Unicorn probes under
`build/r1-hr-selection-probe-20261110/` compared the actual final manifest
objects with the locked stock bytes. The step probe compared return value,
28 state bytes, eight output bytes, and logger arguments over 680 cases. It
exposed a signed comparison of the required and positive streak counts; the
shared C primitive now uses that comparison. The activity probe compared
return value, all 52 state bytes and all 44 output bytes over 564 cases. It
exposed stock behavior that rejects unordered NaNs from all four nonnegative
increment paths; the shared C primitive now uses `>= 0.0f`. The ignored
receipts are `result-step.json` and `result-activity.json`. These are bounded
function comparisons; aliasing, interrupts and physical sensors are not
validated.

The fresh R1 build is `build/r1-gomore-four-stages-c-20261110/report.json`:
956/956 units compile without duplicate strong definitions. The strict
bootloader link passes. The strict application receipt at
`build/r1-gomore-four-stages-c-20261110/app-link/report.json` has 46
unresolved references and a 28,040-byte full flash overflow. The full
application remains unlinked and no byte identity or hardware operation is
claimed.
