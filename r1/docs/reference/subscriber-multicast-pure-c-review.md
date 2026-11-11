# R1 subscriber multicast callback C tail call, 2026-11-10

`r1/src/application/runtime/native_event_multicast.c` now expresses the
callback transfer in C as a required tail call. The callback receives the
payload, thread-cell reference and its own target in R0/R1/R2. Clang's
`musttail` attribute requires a tail transfer, which preserves the caller's
link register. The resulting instruction is the same `bx r2` as the former
handwritten assembly trampoline.

The two complete `native_event_multicast.c.o` objects have identical SHA-256
`aa333a9938984dfc5485bc3922416273cb653706d9f4e39806cc04a38dc21b7d`:
the prior assembly build is
`build/r1-gomore-motion-gate-c-20261110/r1/r1-application/r1__src__application__runtime__native_event_multicast.c.o`;
the C build is
`build/r1-multicast-tail-c-20261110/r1/r1-application/r1__src__application__runtime__native_event_multicast.c.o`.
This checks the entire object, including the call site and relocations, with
the repository's selected Clang profile. The attribute is compiler-specific;
other compilers are not qualified by this byte comparison.

The current R1 build compiles all 959 manifest units with no duplicate strong
symbols. The strict bootloader link passes. The strict application link still
has 43 undefined references and exceeds the full flash load region by 28,240
bytes. Board execution and stock bundle byte identity remain unverified.
