# Motion provider wrappers in C

Seven wrappers in `native_motion_selection.c` now use ordinary C instead
of naked assembly: probe/configuration pairs for Bosch, LIS2DW12 and
QMA6100, plus the QMA interrupt wrapper. Stock instructions and REA/Ghidra
establish their common acquire/provider/release order.

Probe wrappers return the full provider ID after release. Configuration
wrappers pass rate 25 and return one for any nonzero provider result,
otherwise zero, preserving that decision across release. Acquisition
results are ignored; even failure does not suppress the provider call
or release. The QMA interrupt wrapper ignores the provider result and
tail-calls release, returning its full result. REA infers a void IRQ
return; native instructions and execution establish the inherited R0.

Stock/source comparison passes 2,485 scenarios, 355 per wrapper. Cases
vary full-width acquisition/provider/release values, zero/nonzero
configuration results, caller-saved flags and registers, and interrupt
masks. Mocked calls clobber R0-R3, R12 and APSR flags. Probes compare
ordered calls, defined arguments, returns, callee-saved registers, stack
restoration and masks. Every callback enters eight-byte aligned. The IRQ
release specifically observes the original SP and return address,
confirming the tail release. No non-stack RAM access occurs in these
isolated wrapper runs. Unused argument-register observations also match,
but are not promoted to public parameter contracts.

| Wrapper group | Stock bytes each | C bytes each |
| --- | --- | --- |
| Three probe wrappers | 20 | 20 |
| Three configuration wrappers | 30 | 28 |
| QMA interrupt wrapper | 18 | 18 |

All other function bodies in the source retain their previous instruction
bytes. The three provider operation tables retain their bytes, alignment
and relocation targets. The refresh-selection entry still contains
assembly; no table or provider-selection behavior was changed.

All 562 R1 units compile without failures or duplicate strong symbols in
`build/sources-goal-r1-motion-wrappers/report.json`; normal import sets
remain 227 application and 34 bootloader. Providers and bus operations
are mocked here. Physical hardware, timing, complete fault state, final
linking and byte identity remain unverified. No source-plan selection or
G2 workflow gate changed.

[Machine-readable evidence](motion-c-wrappers-review.json) binds the source,
manifest, build/native hashes, seven REA analyses and ignored probes under
`build/goal-r1-motion-wrappers/`.

The later [refresh-selection review](motion-c-refresh-review.md) removes the
last assembly entry and introduces typed operation fields without table changes.
