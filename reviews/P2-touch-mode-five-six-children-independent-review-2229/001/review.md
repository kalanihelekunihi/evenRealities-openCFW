# Independent review 2229

**Result:** PASS_SCOPED.

The source, both code bodies [0x685C, 0x68DE) and [0x6A80, 0x6AB8), and both literal pools [0x68E0, 0x68EC) and [0x6AB8, 0x6AC0) match their declared hashes. All receipt files match, and independent Thumb/M-class disassembly agrees with the listing.

An isolated replay regenerated all 16 fixtures exactly. Original 685C, 6A80, 6608, A324 and 4480 execute without interceptions. The full ordered register-write ledger, config byte 113 clear, R4/SP and 6A80 tail writes match.

With modeled scale byte 2, a clear status bit causes 315 calls to original A324(1); 6608 reaches budget exhaustion and returns 4, which 685C ignores before continuing its writes. A set status bit mismatches the requested bit and skips polling. 6A80 calls 685C then performs its three pairs of tail writes.

**Limits:** Scale and status are modeled in RAM. This verifies software polling/call flow, not physical timing, readiness, MMIO effects or hardware meaning. Aliasing and concurrency are not covered. No canonical admission is made.
