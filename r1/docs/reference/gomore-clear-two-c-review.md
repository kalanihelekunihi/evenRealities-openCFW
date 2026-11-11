# R1 ordered two-record clear in C

`native_gomore_clear_two.c` supplies stock `0x883d4`, with its pointer declaration
in `native_gomore_clear_two.h`. The [receipt](gomore-clear-two-c-review.json)
binds production source/object, REA, replay, defect controls, checked-wrapper
comparisons, qualification and composition. No assembly or persistent RAM is added.

The implementation calls EABI clear for twenty bytes at record, then twenty at
record+20. The second call is a tail call. Provider SP depths match stock exactly:
eight bytes below entry for the first call and restored entry SP for the second.
The selected compiled void routine also retains observed raw R0; that observation
is not asserted as a portable C return contract.

The production object passes **2,056 native/C cases**, including **seven faults**.
Independent forty-byte expectations cover 2,048 guarded alignment/pattern cases.
Arguments, partial writes, surrounding bytes, fault address/size, registers and
completed SP agree. Five variants compiled from production source are rejected,
including reversed/merged calls detected by call-order/shape rather than only
final bytes. Underlying EABI clearing executes from stock in that replay.

The generic API is now `gomore_primitives_clear_two_records_checked`. Its null,
length and bool behavior remain, and it delegates to this one native operation.
**262,144 host comparisons** against the exact previous body pass; host EABI
clearing is supplied by a C memset fixture. The respiratory prototype now uses
the shared pointer declaration, avoiding incompatible cross-unit declarations.

That prototype passes **2,792 respiratory cases and 51 boundary cases** with this
production clear object, existing C history and all three C statistics helpers
linked. Optical estimation remains modeled; software FP and EABI clearing execute
natively. Exact estimator scratch pointers and 96-byte respiratory frame are
checked. The respiratory root and proposed coordinator frame reservation are
still experimental and are not claimed as source-build providers here.

The normal build compiles **688 units** (614 application, 74 bootloader), with
**179 application and 34 bootloader imports**, unchanged. All **686 preceding
units outside the consolidated generic owner** retain identical source/object
hashes. Source checks and relocatable composition pass without new failures or
duplicate strong symbols.

Qualification selects no new replacement and the canonical source plan remains
unchanged. Hybrid raw equality still depends on executable stock pull-through.
Physical execution, complete source-only linking, private frame/concurrency
behavior and byte identity remain unproven. Reproduction artifacts are under
`build/goal-r1-gomore-clear-two-c/`; the normal report is
`build/sources-goal-r1-gomore-clear-two-c/report.json`.
