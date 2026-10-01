# Independent review 2145: Sample difference helper at 0x5920

**Result: PASS_SCOPED.** Candidate `analysis/touch-sensor-sample-difference-5920-2142/001` remains unaccepted.

Independent Thumb disassembly confirms the 24-byte body clears item+4 first, loads unsigned halfwords from item+0, item+2 and params+0x1A, adds baseline and margin in a 32-bit register, uses an unsigned <= branch, and stores sample-baseline only on strict greater-than.

The isolated 599-case boundary/random replay checks exact ordered halfword writes, surrounding item bytes, preserved R0/R1/R4/SP, and byte-identical replay JSON. The comparison uses the full-width sum; given both inputs are halfwords, the sum cannot overflow 32 bits, and on the store branch sample exceeds baseline so the result fits a halfword.

Limit: Sample/baseline/margin are descriptive labels; physical meaning is not established.
Limit: Fixtures use separate allocations and static inputs; aliasing, concurrent mutation, and broader callers are outside scope.
Limit: No canonical admission or C implementation.
