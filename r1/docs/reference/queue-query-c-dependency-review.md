# Queue occupancy C dependency review

The selected native-layout queue unit now includes pinned FreeRTOS 10.5.1
`uxQueueMessagesWaiting` and `uxQueueMessagesWaitingFromISR`. The task query
asserts a nonnull handle, enters a critical section, reads the volatile count
at offset 56 and leaves the critical section. The ISR query asserts and reads
without entering a critical section. These resolve two runtime imports;
`uxQueueSpacesAvailable` remains unresolved pending its own stock evidence.

[Machine-readable evidence](queue-query-c-dependency-review.json) binds the
source, pinned upstream selection, build, REA instructions, probes, audit and
qualification by SHA-256. Stock entries are 0x95634 (34 bytes) and 0x95656
(20 bytes), including their assertion paths. REA/Ghidra groups these ranges
with a wrapper at 0x7d5e8, whose tail branches target these entries. The frontier
therefore records manual stock-entry supplements, not new accepted Ghidra
inventory coverage. Raw instruction checks and execution establish these local
contracts; global corpus completeness is not inferred.

There are 3,272 paired stock/C cases (6,544 executions), covering boundary and
seeded 32-bit count values, four entry interrupt masks, null handles, and count
mutations at critical entry or exit. Read hooks check load width and mask.
The task result reflects an entry mutation but retains its sampled value after
an exit mutation; the ISR routine invokes neither boundary. Queue and guard
bytes, return values, call ordering, stack and callee-saved registers agree.
Wrong-field and omitted-critical-section mutations are rejected. Critical
functions are modeled; physical interrupt concurrency and full exception state
are unverified. Logical assertion address, width, value and BASEPRI agree.
Caller-clobbered registers/flags are excluded.

All 25 preexisting queue-unit function bodies remain byte unchanged. All 573 R1
units compile without failures or duplicate strong symbols. Application imports
fall from 186 to 184; bootloader imports remain 34, with no added imports.

Five qualification profiles produce only two previously covered BASEPRI regions;
neither new query is byte-qualified. The canonical source plan is unchanged:
3,833 source-built bytes, 642,327 binary-pull-through bytes and 248 resource
bytes. The hybrid still equals the locked application byte for byte. Complete
source linking, source completeness and physical execution remain unproven.
No G2 corpus gate advances and no low-level processor instruction is removed
without evidence for an appropriate replacement.
