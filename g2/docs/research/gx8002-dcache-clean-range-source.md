# Cache clean range C candidate

Original package17678/runtime10025664 occupies92 bytes. Native macOS C-SKY
build emits88 bytes; no inline assembly or extracted bytes are used. The
builder authenticates the stock image and upstream gx_dcache.h declaration.
The snpu.o reference establishes caller relocation identity, not byte identity
of the cache implementation. Candidate remains unqualified/unregistered.

The C retains the eight unrolled register writes per128-byte chunk and the
16-byte residual loop. It aligns down the address and ORs command8, then
writes only e000f004. Signed negative sizes and zero issue no writes. Address
arithmetic is explicitly unsigned32; residual signed subtraction is bounded
(no signed overflow). No size adjustment compensates for initial misalignment,
matching the observed target. Upstream documents16-byte aligned arguments.
Synthetic unaligned/wrapping cases will test arithmetic, not valid hardware use.

Generated code has the same loop structure as stock with different register
allocation. Both are leaf functions. The upstream API returns void; their
incidental r0 values differ and must not be treated as an API return value.
Call sites depending on an undeclared return would require separate evidence.

Next qualify signed boundaries, all16 low address bits patterns, 16/128-byte
transitions, address wrapping, full moderate-size traces and bounded prefixes
for huge positive sizes. Compare every register address/value and callee-save
ABI. Physical cache coherence/timing and other cache operations remain open.

## Qualification

verify_gx8002_dcache_clean_range.py passes12,864 complete cases and144
65-write prefix cases for huge positive sizes. All16 address alignments are
covered at zero, SRAM and wrap-boundary bases. Sizes0..257,511..513,
4095..4097 and signed negatives cover scalar/unrolled transitions. Eight
tests check counts, negative/zero, misalignment, wrapping, wrong command,
port, unrolled stride and ABI. Unknown instructions/wrong MMIO reject.

The independent expected sequence is ceil(positive signed size/16) writes
of consecutive16-byte command addresses. The decoded implementations retain
their own loop/control structure. Huge positive termination is not claimed
from prefix checks. Full-return cases check callee-preserved registers and
SP; the API returns void. The reviewed report admits the fixed code section,
but integration registration is still pending. Package remains unchanged.

Integration checkpoint: the qualified cache-clean routine and descriptor
wrapper are now registered and integrated; all 557 macOS integration tests
pass. Neither qualification establishes physical cache coherence.
