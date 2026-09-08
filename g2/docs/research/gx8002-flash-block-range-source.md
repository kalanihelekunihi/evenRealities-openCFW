# Flash block bounds, range and synchronization recovery

Recovered C in runtime_gx8002_flash_block_range.c builds with the native macOS
C-SKY compiler. The leaf at package0x158b8 compiles to68/72 bytes; the range
wrapper at0x15aa4 to38/40; synchronization at0x15acc to8/8, byte-identical.

The leaf writes zero to end, then start, before reading signed device_index.
Negative index returns-1. Otherwise usable_bytes is rounded down to4096 and
blocks are visited in ascending order. A matching half-open block writes start
then end and returns0; exhaustion returns-1. The size is loaded once after
the initial writes. Output pointers may therefore alter the state subsequently
read. The final partial block is excluded.

The wrapper first resolves address into caller start and a stack temporary.
On failure it returns immediately without touching caller end. On success it
resolves wrapped address+length-1 into the temporary and caller end. Zero length
is not rejected. Both calls propagate failure. Its original stack frame is20
bytes; compiled frame also20. This observation still needs decoded call/stack
qualification. Sync saves LR, calls the already qualified wait-ready routine,
and returns its result (normally1); its compiled bytes equal stock.

compare_gx8002_flash_block_bounds.py currently passes1600 decoded leaf cases
covering boundaries, rounded capacities, invalid indices and five pointer
alias arrangements, including shared outputs and state aliases. The stock
image hash is authenticated before decoding. This comparison shares an ISA
interpreter, so independent expected-result and rejection tests remain, along
with large-capacity cases and wrapper qualification. None of these three
functions is admitted to the package yet. No hardware operation was performed.

Block-boundary qualification expanded:1600 stock/source cases now also match
an independent closed-form expected trace. Four large-capacity cases complete
at sizes0xffffffff and0x80000001, covering the last full block and first
excluded block. Seven expected-result and interpreter-rejection tests pass.
The range wrapper passes240 decoded cases checking its20-byte frame, helper
arguments, wrapped end calculation, failure propagation and caller-register
clobbers. Both calls use the same local slot; helpers remain separately
modeled. Sync remains byte-exact. Admission adapter and wrapper rejection
tests remain before package integration. Existing108-function package remains
unchanged; no hardware operation. Full source-only goal stays active.

Admission adapter now pins the shared state header and requires all three
functions to fit, along with exact sync bytes. Eleven focused tests pass,
including wrapper wrong-helper, wrong-frame, wrong-argument and unknown-op
rejections. Reviewed verification report generated successfully. Registered
for full integration, which is in progress; do not treat registration alone
as a successful rebuilt package.

Block-bounds/range/sync integration is complete in the experimental package.
Native macOS codec build passes194 tests; full package build and
verify-artifacts pass with apple-clang. Current ownership7052 compiled C,
2040 source data,80 metadata,302 fill,316618 retained bytes. There are111
functions/127 code occurrences and16 data regions. Codec SHA-256:
0de84f82cd67e10efd7c5cf82d2a54e5dbb55e39b5756adcb7296d02484e31ee.
Package SHA-256:eec3a743137a7677b744fafc764eb4d2e30fca0add1d01f1222c4743a7bd21e2.
The new hash pin identifies this candidate, not vendor-byte equivalence.
No hardware operation; complete source-only firmware remains unfinished.
