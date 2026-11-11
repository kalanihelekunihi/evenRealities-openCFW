# Double-log equality in C, 2026-11-10

`r1/src/application/runtime/native_log.c` previously called the integer-key
comparison through inline assembly solely to return the Z flag. The reverse
comparison keys every negative 64-bit encoding to itself and maps each
nonnegative encoding `x` to `0x8000000000000000 - x`. This mapping has one
collision: the positive and negative encodings of zero. The C predicate now
tests raw equality or both operands being a zero encoding. It performs no
floating point operation, preserving the absence of FPSCR side effects.

An ignored deterministic probe checked 600,121 edge and seeded input pairs
against the original key transform. The source build at
`build/sources-r1-log-equal-c-20261110/report.json` compiled all 975 R1 units
without failures or duplicate strong symbols. The generated log object no
longer imports `r1_binary64_compare_reverse_flags`. `make sources-check` and
the strict bootloader link pass. The strict application link still reports 24
undefined functions and 29,464 bytes of full flash-load overflow; the log
section is discarded by that incomplete link. This predicate check does not
establish whole-log behavioral equivalence, hardware behavior, or byte identity.
