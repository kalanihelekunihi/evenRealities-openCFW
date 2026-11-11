# Motion initialization and FIFO dispatch in C

Three entries in `native_motion_stream.c` now use C and the existing
typed motion operation table: selected-provider initialization, its
initialization forwarding entry, and selected FIFO read.

Stock initializer `0x50270` reads the selected-provider word. Only a null
value triggers selection; it then reloads the word, ignoring the selection
function's return. A null selected value or null configure field returns
zero. Otherwise it tail-calls configure and returns its full result.
Entry `0x6f400` forwards to this initializer and ignores its context input.
Stock FIFO dispatcher `0x502ac` reads the selected value and field at
offset eight, returning `0xffffffff` if either is null. Otherwise it
tail-calls FIFO with destination and sample count unchanged.

REA/Ghidra confirms those branches; its FIFO prototype omits arguments.
Native instructions and execution establish full R0/R1 forwarding.
Volatile selected-word and table-field reads preserve the single-read
path and the required additional selected-word read after selection.
The selection declaration now matches its actual uint32 result type.

Stock/source comparison passes 1,728 scenarios: 464 for each initialization
entry and 800 for FIFO. Cases include selection returning a nonzero ID
while leaving the global null, replacing the selected table, null
callbacks, full-width returns, zero/large sample counts, null or opaque
destinations, pointer mutations during field reads, callback mutations,
and interrupt masks. Probes independently check global/field read order,
fallback reachability, callback identity, FIFO arguments, full returns,
selected state, callee-saved registers, restored stack and masks.

Operation callbacks observe the original SP and LR, confirming tail calls.
FIFO dispatch itself does not touch sample memory; modeled callback writes
and surrounding guards match. Mocked calls clobber caller-saved registers
and flags and require eight-byte stack alignment.

| Entry | Stock bytes | C bytes |
| --- | --- | --- |
| Selected-provider initialize | 30 | 36 |
| Initialization forwarding entry | 4 | 4 |
| Selected FIFO read | 20 | 24 |

All other stream function instruction bodies remain unchanged. Interrupt
dispatch still contains assembly: its slot mixes void notifications and a
status-returning entry, so a uniform uint32 C return is not admitted here.
Calibration and batch-frame assembly also remain outside this conversion.

All 562 R1 units compile without failures or duplicate strong symbols in
`build/sources-goal-r1-motion-dispatch/report.json`; imports remain 227
application and 34 bootloader. Probe placement at `0x200076ac` does not
establish final layout. Physical operation, timing, complete fault state,
final linking and byte identity remain unverified. No source-plan selection
or G2 workflow gate changed.

[Machine-readable evidence](motion-c-dispatch-review.json) binds source,
header, manifest, build/native hashes, REA observations and ignored probes
under `build/goal-r1-motion-dispatch/`.

The later [batch-producer review](motion-c-batch-review.md) replaces the batch
frame with C and restores native halfword sample/offset accesses.
