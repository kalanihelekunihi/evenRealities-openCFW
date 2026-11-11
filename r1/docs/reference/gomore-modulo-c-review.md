# R1 respiratory history helper in C

`native_gomore_history_record.c` supplies stock `0x94938`, declared in
`native_gomore_history_record.h`. The [receipt](gomore-modulo-c-review.json)
binds production source/object, REA, direct/boundary/caller replay, defect controls,
checked-wrapper comparisons, consolidation, qualification and composition.

The native helper takes a record pointer and two word arguments. It retains live
counter-byte reads, primary-before-secondary stores, full-word sentinel equality,
noncanonical counter destinations and `(counter+1)%20` before byte narrowing.
Raw return is record+40. Pointer-width integer arithmetic also lets the checked
host utility delegate without truncating host pointers; the firmware ABI remains
three 32-bit words with a 32-bit raw pointer result. No assembly or persistent
RAM is added.

The old generic API is now `gomore_primitives_modulo5_record_checked`. It retains
its null/length/counter guards and byte arguments, then delegates to this single
native implementation. Both respiratory generic callers use that checked name.
**100,352 host comparisons** against the exact previous checked-function body
confirm identical return and memory behavior, including rejected/null inputs.
The previous history module is unchanged; a filename collision during preparation
was corrected using an exact prior source-hash match, verified again in the build.

The production object passes **12,544 native/C cases** with independent guarded
byte expectations across every counter value and word-argument extremes. Full
record/guard views, raw return, saved integer registers and SP agree. **42 boundary
cases**, including **28 faults**, match invalid access address/size, partial writes,
RAM-tail contents and completed return. Six compiled defects are rejected.

The actual native respiratory caller prefix passes **3,884 paired executions**
with the stock helper versus the production C helper. History bytes, all six
estimator arguments, exact zero-scratch pointers/contents, 96-byte native parent
frame and FPSCR agree. This fixture stops at estimator `0x69834`; it does not
claim the remaining respiratory algorithm or lower estimator is reconstructed.

The normal build compiles **686 units** (612 application, 74 bootloader), with
**179 application and 34 bootloader imports**, unchanged. All **684 prior units
outside the consolidated generic owner** retain identical source/object hashes.
The new helper is available to the respiratory stage and already supplies the
generic checked wrapper. Source checks and relocatable composition pass without
new failures or duplicate strong symbols.

Qualification selects no new replacement, and the canonical source plan is
unchanged. Hybrid raw equality still uses executable stock pull-through. Physical
execution, concurrency/private stack behavior, fully C firmware, source-only
final linking and byte identity remain unproven. Reproduction artifacts are under
`build/goal-r1-gomore-modulo-c/`; the production report is
`build/sources-goal-r1-gomore-modulo-c-final/report.json`.
