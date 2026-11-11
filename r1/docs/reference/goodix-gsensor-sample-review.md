# Goodix accelerometer sample consumer in C

`r1_goodix_gsensor_sample` reconstructs stock `0x6f920` in C and consumes the
existing shared callback table. The board callback receives the buffer in R0
and count pointer in R1, preserving the observed native live register values.
This describes the dispatch boundary, not an identification of concrete target
prototypes or hidden register conventions. The [earlier analysis](goodix-gsensor-boundary-review.md)
records why absence of a second-argument move alone was insufficient to infer
a one-argument hook.

The implementation reads the sample callback word once, calls it if present,
and reloads the volatile 16-bit count on every loop test. Each sample is three
signed halfwords loaded in Z/Y/X order, then delivered as timestamp zero and
sign-extended X/Y/Z arguments. Only after the loop does count greater than 100
enter nonreturn. The count, guard and axis order match REA's native instruction
observations; no pre-loop clamp or count snapshot was introduced.

`stock_gsensor_sink.c` owns `r1_gsensor_sample_sink_nop`. REA confirms native
`0x2adfc` consists solely of BX LR. Its C body compiles to two bytes. It is a
stock-backed no-op, not a substitute for a missing algorithm. A separate
translation unit preserves the sample call boundary in the non-LTO source
build while keeping its volatile input reads. Future LTO changes require
revalidation.

The execution probe passes 448 paired stock/C cases (896 executions), covering
zero/one/2/3/99/100/101 counts, optional board callback, callback-produced counts,
sink-induced count growth/shrinkage, and two signed-axis patterns. It compares
ordered callback-slot/count/axis reads, R0/R1 at the board boundary, sink argument
words, count effects, return/nonreturn and preserved registers/stack/masks.
The sink executes the native/C return body; optional count mutations are
controlled perturbations at that boundary, not claimed physical stock behavior.
A count-snapshot negative control fails when the first sink changes one sample
to three: stock processes three, the variant only one.

All 1,029 registration and 72 stop regression cases pass against the new object.
The normal report `build/sources-goal-r1-goodix-gsensor-sample/report.json`
compiles 567 R1 units without failures or duplicate strong symbols. Imports
remain 199 application and 34 bootloader. `make sources-check` passes.
[Machine evidence](goodix-gsensor-sample-review.json) binds source, REA snapshots,
execution probes, negative control and the normal build by hash.

The C sample body is 72 bytes versus 64 native instruction bytes. Neither
body is byte-qualified, including the two-byte sink. The canonical source plan
and G2 gates are unchanged. SDK public HAL binding remains separate work.
Private frames, caller-clobbered registers/flags, arbitrary pointer aliases or
faults, concurrency, concrete callback targets, physical accelerometer behavior
and complete source-only byte identity remain unverified.
