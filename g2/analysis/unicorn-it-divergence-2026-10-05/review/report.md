# Independent review: optimized tick / Unicorn hook divergence

## Result

The stripped-down reproduction isolates this specific failure to memory-hooked Unicorn execution. I ran the current self-contained reproducer under the repository's Unicorn 2.1.4 environment. It executes only three unchanged O2 machine-code bodies (238-byte tick, 26-byte list insertion, and 32-byte list removal) against synthetic aligned RAM. Its memory callback is empty: it does not read registers, inspect memory, or mutate state.

All 32 combinations completed according to expectation. With one due task, every hook mode completes. With two due tasks, no hook and code-hook-only complete; read-only, write-only, and combined memory hooks fail at `0x10296`, whether or not the code hook is present. The captured second insertion trace runs `0x10292` and then `0x10296`, omitting `0x10290`. Yet `0x10290` is the unconditional Thumb instruction `0x6842: ldr r2, [r0, #4]`, and the ready-list `pxIndex` cell at `0x2006a4dc` still contains `0x2006a4e0`. At the fault, `r2=0`, so the following load from `[r2,#8]` faults. The preserved list state has count 1: the first task insertion completed, then the second hit the skipped load. This is an architectural expectation checked against the saved disassembly and trace, not an assertion that the emulator has a particular internal defect.

The result excludes the project's memory-hook callback as a necessary cause: the same failure occurs with a no-op callback in a standalone machine-code harness. Code-hook-only execution also completes despite reading `R2` and `XPSR` at each instruction. The evidence supports describing this bounded divergence as memory-hook-sensitive Unicorn execution. It does not establish the exact emulator root cause or general behavior outside this fixture.

Separately, `bounded-stock-comparison.json` compares one valid two-expiry case with no source memory hook against the authenticated stock execution and independent graph model. The O2, O2-with-`-fno-strict-aliasing`, and O0 outputs each match the stock final state and model. It is a single-case result, not a replacement for the broader optimized comparison or the production build profile.

The unchanged full project verifier was also rerun against current O2 and O0 profiles: O2 exits with the expected unmapped-read failure and creates no passing comparison; O0 passes all 271 cases with the previously accepted result hash. The validation record reports zero new validated firmware bytes. The one-case no-memory-hook comparison is observational diagnostic evidence only and receives no coverage credit; the full optimized correctness gate remains blocked.

## C and ABI review

The compatibility layouts use 32-bit-aligned pointer/integer fields and assert the `List_t`/`ListItem_t` sizes; the recovered global cells use volatile lvalues where asynchronous kernel-cell semantics matter. The O2 list insertion body performs aligned pointer/count loads followed by intrusive-link and count stores. I found no concrete misalignment, volatile-cell, or sparse-layout defect in the reviewed accesses.

There remains a separate strict-aliasing caveat. Pinned FreeRTOS list code casts the address of `List_t.xListEnd` to `ListItem_t *` and accesses it through `ListItem_t` fields; the local ABI represents that compact sentinel as `MiniListItem_t` behind `ListItem_t *pxIndex`. This is an intentional upstream memory-saving layout but raises a potential ISO C effective-type/strict-aliasing question for optimized builds. The O2 and O2-with-no-strict-aliasing runs show the same memory-hook failure, so aliasing does not explain the observed correlation. Apollo G2's original compiler flags are not established here.

## Evidence and limits

The isolated run is `g2/build/foundation/unicorn-it-divergence/machine-repro.json` (SHA-256 `d1a226a517b68b591178fc15e9515a585472cd57c891c8d05f9f4c08842337f1`), generated from `machine-fixture.json` (SHA-256 `3ff092b94a5d68132db46d7df1bb1957e453be99fe6c248a51a679c084bc91fc`). The fixture pins the three body byte ranges to O2 diagnostic ELF `a04b6f3c7fd1c47d71ccd31615b95ebf44e793382e845cf3bd2c7452d165c478`; this is a reconstructed diagnostic replica, not a retained authenticated firmware object. The bounded stock/model comparison is `g2/build/foundation/unicorn-it-divergence/bounded-stock-comparison.json` (SHA-256 `b851e1f3db1679a3512b4cc49f2854a23c495c8f0ecb16f0c276ae50dc21b9ab`) and explicitly limits itself to one input without source memory-hook invariants.

Keep the optimized divergence out of passing coverage. The broader optimized simulator profile, original production optimization flags, byte equality, and the emulator's internal root cause remain unresolved. No source or shared campaign state was changed; only this owned review was updated.
