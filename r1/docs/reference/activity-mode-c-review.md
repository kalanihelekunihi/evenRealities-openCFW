# R1 hardware health activity-mode getter in C

`native_activity_mode.c` implements the six-byte getter at `0x4a8bc` in
ordinary C. It reads and zero-extends the volatile byte at `0x20006ed4`,
returning all values 0–255 unchanged. The [receipt](activity-mode-c-review.json)
binds REA bytes, production hashes, standalone/linked comparisons, startup
initialization, rejected defects, qualification and builds.

The unit owns only that byte. Executing the native RW and ZI scatter handlers
on poisoned SRAM, with guards and an independent compressed RW decoder,
establishes its cold value **zero**. Adjacent bytes remain unowned. No assembly
was added. Runtime writers and physical activity transitions remain outside
this getter implementation.

The standalone getter passed **1,024 paired cases**, covering all 256 byte
values, two APSR patterns and both interrupt-mask states. It preserves every
non-result integer register, all FP registers, APSR, SP, masks, FPSCR and SRAM
guards. Four compiled defects were rejected: boolean normalization, signed
extension, adjacent-byte access and writing before reading.

The linked C RMSSD/getter path passed **6,505 further cases**, with actual C
memset, float-bit promotion and sqrt providers. The activity getter executes
rather than being replaced with a modeled return. Those cases include 6,503
completed calls, two matched bounded nonterminating prefixes, all previously
verified filtering/rounding/allocation/logging edges, and twenty post-filter
input mutations. Allocation/free/logging remain modeled. The prefix cases
are not completed calls. See the [RMSSD review](rmssd-c-review.md) for the
arithmetic and loop-width proof boundaries; physical allocator behavior,
concurrency and hardware transitions remain unproven.

All **658 units** compile and both relocatable compositions pass without
duplicate strong symbols. All **657 prior source/object hashes** are unchanged.
The activity-mode import resolves with no new imports, leaving **168 application /
34 bootloader imports**. The getter does not qualify as instruction-exact under
production bindings. The canonical plan stays at 4,369 source-built bytes; the
fresh hybrid still matches the locked application through executable
pull-through. Complete source-only linking and physical health operation
remain unproven.

The subsequent [sleep report/shared-state review](algo-sleep-report-c-review.md) now supplies the report and consolidates activity mode with the canonical sleep/wake state at 0x20006ed4. The updated getter/default-mode callers and mixed transitions are replayed there.
