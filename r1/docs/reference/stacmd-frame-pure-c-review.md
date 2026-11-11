# STACMD frame and bit-output adapters in ordinary C

`board/native_stacmd_frames.c` removes incoming R12 capture and explicit
R2/R3/R12 restoration from the read frame, and R3 restoration from the write
frame. ACK, data and header state remain explicit C locals. Command gates,
header arithmetic, parity, ordered bytes, partial failure output, signed
length decisions, cleanup and line release policy are unchanged.

`board/native_stacmd_receive.c` replaces the scratch-register capture in the
bit-output adapter with an ordinary C output local. The concrete bit reader
always stores its computed bit before returning, including both timeout
paths. No incoming R3 fallback is therefore needed for a returning call to
that reader. The adapter retains its status and unaligned output support.
An arbitrary substitute reader that returns without writing is outside this
concrete-reader contract. No NOP delay is removed or replaced with a C delay.

Normal source objects, previous compiled objects and locked stock firmware
match in 479 cases (1437 executions): 112 read frames, 110 write frames, one
recovery flow and 256 direct bit-adapter cases. All five normal protocol units
execute. Only the GPIO callbacks are C models, shared by all paths. Cases
cover valid headers and bytes, parity errors, invalid command gates, zero and
signed-negative lengths, partial output after timeouts, first/last edge waits
at 0/1/999/1000 samples, nonbinary sample values and four output alignments.
Tests compare complete GPIO traces and explicit NOP counts, status, guarded
output/configuration bytes, final saved registers, SP and interrupt masks.
Source execution may not enter stock instructions. The recovery NOP count is
4180; bit sample loops retain the existing delay instructions.

The receive bit driver's allocated bytes and relocations are unchanged.
Transmit, delay and recovery objects are unchanged. Private frames, incidental
caller-clobbered return registers, private-stack aliases, faults and concurrency
are excluded from the typed C contract. Function-call/prologue overhead may
differ; NOP/trace agreement is not proof of cycle timing, electrical response
or operation on the physical STACMD bus. The necessary raw GPIO-result gateway
and timing NOPs remain in the existing lower-level drivers.

Four compiled defects are detected: wrong header arithmetic, corrupted read
byte, omitted read release and ignored timeout status. A clean final baseline
runs afterward. Fresh REA bytes for the stock read/write/adapter entries match
the locked application; evidence identifiers and probe/build hashes are in
the companion JSON.

All 799 R1 units compile without failures or duplicate strong symbols. Imports
remain 97 application and 22 bootloader linker metadata; strict source
bootloader linking succeeds. The 795 unrelated object hashes are unchanged;
the two generated bootloader objects retain allocated bytes and relocations.
Global source checking retains the unrelated unlisted G2
resident_rom_thumb_set.S failure. Full application linking and physical bus
validation remain unfinished. No new source-plan qualification or byte-identity
claim is made.
