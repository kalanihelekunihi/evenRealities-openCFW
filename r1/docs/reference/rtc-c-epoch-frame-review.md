# RTC epoch initialization order and scratch frame

`board/native_rtc_lifecycle.c` now gives its C epoch initializer the native
48-byte calendar scratch span at entry SP minus 72. An 18-byte ABI bridge
preserves six saved registers around that span. The C kernel stores the UTC
offset before name validation, loads caller name before record name, tests
opened only after a matching name, captures the input epoch, stores it in the
shared counter and converts that captured value. Volatile views preserve the
stock shared/input access sequence.

Raw instructions at `0x5649c`, earlier REA observations and current execution
provide the evidence. Null block returns 4 without touching shared state;
name mismatch or a closed record returns 17 after the offset store. Successful
initialization returns zero. No new argument guard or table normalization was
introduced.

All 936 direct stock/C comparisons pass. Cases include opened/name/null states,
epoch wrap values, signed UTC offsets, zero/partial/full calendar writes,
controlled name changes between lookup reads and input/counter storage aliasing.
A further 20 comparisons execute the actual stock and C calendar converters.
Checks compare status, ordered name reads, comparison/conversion arguments,
exact scratch pointer and 48 bytes, shared counter/record state, R4-R11, SP,
interrupt masks and call alignment. Boundaries clobber caller-saved registers.

The old source has a controlled name-order counterexample: stock and corrected
C retain the caller name loaded before the record read and return success;
old C loads the changed caller name and returns 17. This is semantic evidence,
not a claim of physical race frequency. All other preexisting lifecycle
function bodies and normalized relocations remain unchanged.

All 562 R1 units compile without failures or duplicate strong symbols; imports
remain 211 application / 34 bootloader, the other 561 units are unchanged and
source checks pass. strcmp is modeled; conversion is modeled in the direct
set and executes in the integrated set. Physical RTC behavior, complete
fault/concurrency equivalence, byte identity and complete source-only firmware
remain open. Source-plan selections and G2 gates are unchanged. Exact bindings
are in the [machine-readable review](rtc-c-epoch-frame-review.json).
