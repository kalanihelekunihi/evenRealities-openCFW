# R1 GoMore motion gate in C, 2026-11-10

The locked `r1-2.2.6.0009/application.bin` has SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
The native motion gate at `0x5f264` now has a C adapter in
`r1/src/application/runtime/native_gomore_motion_gate.c`, using the existing
`gomore_primitives_motion_gate_accumulate` primitive. Its 18 non-executable
Float32 weights are expressed as exact hexadecimal C constants; the compiled
72 bytes match the locked table at `0xbd2e4`.

The primitive's state layout was corrected to the stock 36-byte record:
`pending_sum` begins at byte 24, `pending_count` at 28 and `last_bucket` at
32. The long-gap reset now clears all 36 bytes, as the stock helper does.
The native function permits unsigned timestamp subtraction, including
elapsed counts greater than the timestamp.

An ignored ARM Cortex-M4 Unicorn probe under
`build/r1-motion-gate-probe-20261110/` linked the final manifest objects.
It compared return value, all 36 state bytes and eight output bytes with
the locked routine over 832 bounded cases covering bucket edges, gaps,
negative values, NaNs and randomized input/state. All 352 stock instruction
bytes executed and all pairs matched. A source code hook rejected entry into
the stock executable region. The stock routine itself does not terminate for
some extreme timestamp wrap inputs during its fill loop; those inputs were
excluded from this bounded result.

The fresh `build/r1-gomore-motion-gate-c-20261110/report.json` compiles
959/959 R1 units without duplicate strong definitions. Its strict
bootloader link passes. The strict application receipt at
`build/r1-gomore-motion-gate-c-20261110/app-link/report.json` still has 43
unresolved references and a 28,240-byte full flash overflow. Full
application linkage, byte identity and board behavior remain unverified.
