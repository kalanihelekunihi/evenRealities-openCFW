# R1 subscriber consume callback C tail call, 2026-11-10

`r1/src/application/runtime/native_subscriber_consume.c` now expresses the
subscriber callback transfer as a C `musttail` call. Its payload is passed in
R0 and its target address is passed both as the call target and in R1, exactly
as the previous `bx r1` trampoline did. The tail transfer preserves the
caller's link register. This models the native register boundary; it does not
claim that every subscriber callback has the same source-level C prototype.

The old assembly and new C `native_subscriber_consume.c.o` files have the
identical SHA-256
`c2f206e0820e02d822faf61c73ab9eb734177554397b0efc0f4950b413616ec0`.
They are the objects under
`build/r1-multicast-tail-c-20261110/r1/r1-application/` and
`build/r1-subscriber-tail-c-20261110/r1/r1-application/`, respectively.
The selected Clang profile therefore generated the same complete object,
including call sites and relocations. This compiler-specific result does not
qualify other toolchains.

The new 959-unit source build has no failures or duplicate strong symbols.
The strict bootloader link passes. The strict application link still reports
43 undefined references and a 28,240-byte full flash load overflow. Board
execution and stock bundle byte identity remain unverified.
