# R1 sensor-stream bootstrap in C

Four assembly routines in `runtime/native_stream_bootstrap.c` now use C:
`r1_stream_tick_now`, `r1_stream_wake`, `r1_stream_enable` and
`r1_native_stream_initialize`. The source-owned 48-byte housekeeping record at
`0x2001a2bc` and four-byte clock callback cell at `0x2001a2b4` are retained.
The actual timer constructor remains C; its object body changes as the compiler
inlines the new helpers. Its direct and initializer paths are both checked.
The hardware BASEPRI instruction in the allocation-failure handler remains
assembly; that function and the keepalive function retain their instruction bytes.

The clock leaf reads the callback cell once and propagates either that callback's
return or the kernel-tick fallback. Wake clears housekeeping +16, then loads the
callback at +40 and its context at +44; it propagates the callback return, or
returns the housekeeping address when no callback exists. Enable stores the low
byte at +12 but tests the whole incoming 32-bit argument before deciding whether
to wake. Thus `0x100` stores zero yet still wakes. Initialization calls the
actual list initializer with payload size 24, enables the framework, then creates
a 1000-tick timer with the keepalive callback and zero context.

REA/Ghidra confirms the stock clock (`0x8a1d0`) and wake (`0x8a540`) bodies. Its
default database lacks the enable (`0x8a3f0`) and initialization (`0x8a55c`)
entries; those errors are retained without coverage credit. Direct Thumb
disassembly and execution of the locked application supply their local evidence.
These local observations do not establish corpus coverage.

The normal source object passes 1,536 paired stock/C emulator cases: 384 each for
clock, wake and enable; 192 each for initialization and direct timer creation.
The source execution includes actual C list initialization and prepend. The
allocator return, kernel clock and external clock/wake callbacks are modeled.
Cases vary callback presence/results, full-width enable arguments, existing list
heads, allocation failure, interrupt masks and callback mutations between the
initial wake, clock sampling and second wake. They compare new bootstrap/timer
shared accesses, final list/node state and guards, native return values, successful
return SP, saved registers and masks. OOM still sets BASEPRI to 64 and faults on
the native write at `0xffffffff`. Each invocation resets XPSR/IT state. The
initializer's stored keepalive pointer is checked against the actual source/native
function symbol before normalizing that address for state comparison. Two
negative controls (testing only the enable byte and discarding the wake callback
return) are rejected.

The list provider's internal accesses are checked through final state and call
graph, not instruction-for-instruction memory traffic. Private frames,
caller-clobbered registers/flags, physical sensor scheduling, actual heap
allocation and asynchronous execution remain outside this evidence. Linking
probe data cells at native addresses does not prove final startup placement.

All 573 R1 units compile without failures or duplicate strong symbols. Application
imports remain 176; bootloader imports remain 34. The manifest and every
unrelated object retain their hashes. Five official qualification profiles
compile, but no region qualifies. The source plan is unchanged. A fresh complete
hybrid application equals the locked 646,408-byte image: 3,881 source-built
bytes, 642,279 binary pull-through bytes and 248 resource bytes. These stored-byte
provenance counts do not establish executable-C coverage, admission of these new
C routines into that hybrid, or full source completeness. No G2 implementation
or workflow gate changed.

Hashes and build paths are recorded in
[stream-bootstrap-c-review.json](stream-bootstrap-c-review.json).
