# R1 double-round comparison in C

`r1/src/application/runtime/native_math_round.c` now computes the integer-key
carry and zero results used by `r1_native_round` in C. The previous helper
used inline `bl` and `mrs APSR` instructions; its two call sites and four
register-bound declarations are gone. The external binary64 flag helpers
remain for their other callers.

The ignored probe at `build/r1-double-round-pure-c-replay-20261110/compare.py`
links the preceding and current compiled source objects separately. In a
Cortex-M4 Unicorn environment, 2,624 paired cases agree on return bits,
FPSCR, stack pointer, and lower-provider call trace. The cases include signed
zero, half and unit boundaries, infinities, NaNs, all-ones bit patterns,
random 64-bit patterns, and varied FPSCR rounding modes. Lower providers are
modeled by the same harness in both images; this is an old-C/new-C comparison,
not a new stock-image equivalence claim.

The 975-unit R1 source build compiles all 893 application and 82 bootloader
units. The strict bootloader link passes with its C vector. The strict
application has the same 24 undefined functions as before, while full flash
overflow falls from 28,072 to 28,056 bytes. Receipts:
`build/sources-r1-double-round-pure-c-20261110/report.json` and its
`app-link/report.json`. `make sources-check` reports zero R1 units not built;
its separate G2 report still has one unit not built.
