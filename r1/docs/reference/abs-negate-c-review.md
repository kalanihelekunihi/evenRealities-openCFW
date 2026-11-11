# C negation in the charger ladder math dependency

`runtime/native_math_selection.c` now uses unary C negation in
`r1_native_compare_absf` at native `0x98eca`, replacing its explicit VNEG assembly.
The VCMPE/FPSCR observation remains: an ordinary quiet C comparison loses the
stock quiet-NaN invalid-operation flag. This is a narrow source improvement,
not a claim that the complete helper is portable C or byte-identical.

The normal Clang product and a strict GCC object each pass 66,112 paired stock
comparisons (132,224 executions per compiler). Tests cover 2,066 input encodings
across 32 FPSCR configurations: signs, both zero encodings, subnormals, extrema,
infinities, quiet/signaling NaNs, rounding modes, flush-to-zero, default-NaN and
sticky flags. They compare exact S0 bits and the complete FPSCR and check
R4-R11, S16-S31, SP and interrupt masks. APSR and other caller-clobbered registers
are outside this proof.

The actual Clang charger-ladder C chain also passes 23,872 stock comparisons
with the changed dependency, including its exposed 40-byte frame, eight helper
operands, retained words, return index, callbacks and floating-point state.
Transport is modeled and the source table uses controlled native placement.
Compiled controls reject missing negation and a quiet comparison. For quiet NaN
`0x7fc00001`, the latter returns the same float bits but loses FPSCR invalid
operation (`0x30000001` versus `0x30000000`).

All 579 R1 units compile and compose without failures or duplicate strong
symbols. The 578 unrelated objects, every other math function/data section and
its relocations, manifest and imports (164 application / 34 bootloader) are
unchanged. The selected twelve-byte floor data remains identical. Scoped
qualification compiles this unit but selects no new function region.

The source plan and canonical hybrid retain SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
with 4,043 selected source bytes, 642,117 binary fallback bytes and 248 resource
bytes. Counts include assembly and data elsewhere. The normal report is
`build/sources-goal-r1-abs-negate-c/report.json`.

[Machine-readable evidence](abs-negate-c-review.json) includes REA observations,
hashes, audits and counterexamples. Probes live under ignored
`build/goal-r1-abs-negate-c/`. Trap-enabled exceptions, physical timing, final
linker placement and complete source-only firmware remain unproven. Original
Arm Compiler 5 is unavailable; whole-image byte identity from source is incomplete.
