# R1 interpolation/filter kernel wrappers in C

`native_gomore_kernels.c` supplies stock ACC `0x8245c` and PPG `0x8247e`.
The [receipt](gomore-kernels-c-review.json) binds the production object, REA,
direct and integrated replay, consolidation, qualification and build checks.
The [ABI investigation](gomore-kernel-abi-investigation.md) records the stock
instruction evidence and decompiler argument-recovery limitations.

Both four-word entry points unconditionally call interpolation as
`(source,count,25,count,output)` and then filtering as `(state,output,25)`.
ACC returns zero. PPG preserves the final provider's raw machine return word
using a C return; this does not infer a public semantic return contract for
the underlying filter. Null/count guards are not added.

The earlier seven-argument generic exports were removed from the generic owner
and header. Their two high-level callers now invoke the existing checked
`resample25_and_filter_common` helper directly, with identical arguments and
ignored return. The helper body and all other generic source are unchanged.
This replaces the superseded stock owners rather than keeping a second copy.
No inline assembly, executable data or persistent RAM is added.

The production object passes **320 direct native/C cases**, each with independent
ordered-call and return expectations, covering count extremes, null/invalid/
aliased pointer words and arbitrary lower return words. Integer callee-saved
registers and final SP are checked. Five compiled defective controls are
rejected. The interpolation/filter providers are modeled here: invalid pointers
prove unconditional dispatch, not native provider dereference behavior.

Actual native/C host adapters, resampling adapters and these kernel wrappers
pass **442 integration cases** with **4,074 modeled lower-provider calls**.
Stock memory clearing executes on both paths. Interpolation, filtering, logging
and final algorithm output remain modeled. Numeric PPG scratch pointers and
host scratch/context effects are compared without normalization.

The kernels use 24 bytes of C stack before interpolation versus stock's 16.
PPG restores entry SP before its final filter call on both paths; ACC retains
the 24/16-byte difference at filtering. Outer sensor-update stack differences
also remain open. These are explicit limits on whole-chain ABI equivalence.

The normal build compiles **681 units** (607 application, 74 bootloader) with
**167 application and 34 bootloader unresolved imports**. All **679 prior units
outside the consolidated generic owner** retain identical source/object hashes.
The kernel wrapper imports are resolved and interpolation `0x882ec` and filtering
`0x641f0` become the next unresolved providers. Source checks and relocatable
composition pass without duplicate strong symbols.

Qualification selects no new replacement. The canonical source plan is unchanged;
hybrid raw equality still uses executable stock pull-through. Fully C firmware,
a complete source-only link, physical device validation and byte identity remain
unproven. Reproduction artifacts are under `build/goal-r1-gomore-kernels-c/`;
the normal report is `build/sources-goal-r1-gomore-kernels-c/report.json`.

The subsequent [filter review](gomore-filter-c-review.md) supplies the native
filter and replays it through the actual host chain. Interpolation remains modeled.
