# R1 native-ABI autocorrelation in C

`native_gomore_accel_autocorrelation.c` now supplies the stock kernel (`0x5c5f0`) and wrapper (`0x56d78`) as C providers. The vendor checked analyzer retains its validation and delegates to the shared kernel. The direction-statistics and centered-ratio C utilities moved into this unit, so each implementation exists once. No inline assembly, firmware opcode arrays or native-address calls are used in the new unit.

The stock evidence is the REA instruction/pseudocode dossier saved for both entries under `build/goal-r1-gomore-accel-period-c/rea-autocorrelation-{wrapper,kernel}.json`. The prior [approximation review](gomore-autocorrelation-c-review.md) describes corrected strict thresholds, wrapped differences and reversed rejection tests. Those corrections are retained. Signed 32-bit direction differences now wrap explicitly as well.

The two Clang exception differences identified in that earlier review came from speculative division. An instruction trace found `vdiv.f32` executing with zero count before Clang selected the guarded zero result. Guarded divisions now use a noinline C helper with volatile operands, preventing their execution on the zero branch. Clang replay of the corrected precursor eliminated noncomparison FPSCR differences. The production unit uses the existing strict GCC 9 profile, with all lower C utilities in the same unit.

The wrapper initializes five outputs in native order and enables the kernel only for raw value 1. Its raw return is conditional: disabled paths preserve incoming R0/R1; enabled paths return the fourth and fifth output pointers. Stock overwrites its saved R0/R1 slots with these outgoing arguments. The kernel returns the incoming sample and first-output pointers in R0/R1. These contracts are explicit C uint64 returns, verified separately from the checked bool API.

Verification against the locked stock application passed:

- 738 kernel pairs using the actual normal-build object: 82 sample vectors, three FP environments, and three initial status words. Full external memory, raw R0/R1, SP and callee-preserved registers agree. Lower 28 FPSCR bits agree. Comparison flags differ in 36 cases and are not claimed equivalent.
- 288 wrapper pairs: four raw enable values, eight vectors, three FP environments and three output alias layouts. External memory, raw R0/R1, lower FPSCR bits, SP and preserved registers agree.
- 216 actual stock-classifier pairs with C autocorrelation, period and existing C preprocessing helpers. The new wrapper executes 216 times; the C period executes 432 times, IIR 86,400 times and transition 2,520 times. External memory, ordered external writes, other helper arguments/depths, return, SP, masks, preserved registers and lower FPSCR bits agree. Comparison flags are masked in this new integration fixture. Memory-clear entry tracing is omitted because C kernel initialization does not follow the stock clear-call shape.
- Three compiled defects rejected: inclusive threshold, reversed crowded weak-peak rejection, and reversed direction-change ratio.

The production kernel/wrapper subset links without undefined symbols, native-address bindings or placeholders. Both roots and the C lower utility symbols are defined text. The normal R1 source build passes 719 units (645 application / 74 bootloader), with no failed units or duplicate strong symbols and unchanged 178 application / 34 bootloader imports. Both source manifests pass `make sources-check`.

This establishes a C implementation of this subset and tested native boundary behavior, not complete firmware or complete equivalence. The tests do not prove all input/output aliases, ordered kernel writes, invalid-pointer faults, private scratch identity, full FPSCR flags, physical device operation, stack bounds or timing. Frame layout differs. The classifier root at `0x67e4c` remains stock, and other firmware hardware providers remain unresolved. No instruction-identity qualification, source-plan selection, flashing, commit or publication occurred. Byte identity is no longer a completion requirement.

Reproducible probes live under ignored `build/goal-r1-gomore-autocorrelation-c/`; [the receipt](gomore-autocorrelation-native-c-review.json) records their results and the production input hashes.
