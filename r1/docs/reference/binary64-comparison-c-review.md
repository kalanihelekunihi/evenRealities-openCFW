# R1 binary64 comparison flags consumed in C

The native flag helper compares encoded 64-bit integer keys. Callers in
`native_exp.c`, `native_expm1.c`, `native_pow_core.c`, and
`native_double_directed.c` consumed only carry, or carry and zero. They now
use the shared C comparison in `native_float_bits.h`; their inline `bl`/`mrs`
sites and register bindings are removed. `native_math_round.c` uses the same
helper after its earlier standalone conversion. The architectural flag
entries in `native_double_flags.c` remain for other callers that need APSR.

The ignored Cortex-M4 probe at
`build/r1-binary64-compare-c-probe-20261110/compare.py` executes the compiled
C helper and preceding native flag helpers for 32,912 bit-pattern pairs in
both argument orders. All **65,824 comparisons** agree on carry and zero.
Pairs include zeros, finite boundaries, infinities, NaNs, all-one words and
32,768 seeded random 64-bit pairs. The full double-round replay at
`build/r1-binary64-round-replay-20261110/compare.py` also passes its 2,624
compiled old/new cases. The latter's compiled C ELF hash is unchanged by
moving the helper into the shared header.

The source build compiles all 975 R1 units, including 893 application and 82
bootloader units, with no failures or duplicate strong symbols. The strict
bootloader link passes with its C vector. The strict application still has
the same 24 undefined functions; its current full flash load falls from
602,872 to **602,776 bytes** of 696,320 available. Receipts:
`build/sources-r1-binary64-compare-c-20261110/report.json` and its
`app-link/report.json`. `make sources-check` reports zero R1 units not built.
This removes 20 `__asm__` occurrences; 103 remain across 30 R1 C files.

The probe compares the new C result with the prior compiled flag helper,
not directly with every stock caller or physical-device execution. The
remaining assembly, unresolved imports, and final application behavior
remain open gates.
