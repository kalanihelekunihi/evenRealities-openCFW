# R1 GoMore motion classifier stage in C, 2026-11-10

The locked `r1-2.2.6.0009/application.bin` has SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The stock entry at `0x5f4b6` receives the motion state, elapsed count, input
record, feature record and output, then dispatches through the existing
GoMore classifier helpers. The native ABI C adapter is
`r1/src/application/runtime/native_gomore_motion_classifier.c`; it invokes
the existing source-owned `gomore_primitives_motion_classifier_update` graph.

An ignored ARM Cortex-M4 Unicorn probe under `build/r1-motion-probe-20261110/`
linked the actual manifest objects and their C runtime dependencies. It ran
548 paired stock/C cases across elapsed counts 0, 1, 2, 5, 6 and 255,
source flags, zero and nonzero float features, and randomized state and
feature bytes. It compared the return value, 32 state bytes and eight output
bytes. All pairs matched; all 180 stock instruction bytes executed, including
both lower dispatch paths. A code hook rejected any source run that entered
the locked stock executable region. The ignored receipt is `result.json`.
The cases do not validate physical motion input or concurrent state changes.

The fresh `build/r1-gomore-motion-c-20261110/report.json` compiles 958/958
R1 units without duplicate strong definitions. The strict bootloader link
passes. The strict application receipt at
`build/r1-gomore-motion-c-20261110/app-link/report.json` has 44 unresolved
references and a 28,136-byte full flash overflow. Full application linkage,
byte identity and board behavior remain unverified.
