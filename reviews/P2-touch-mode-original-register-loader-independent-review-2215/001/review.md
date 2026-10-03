# Independent review 2215

**Result:** PASS_SCOPED.

Source and all receipt files/ranges match their hashes: dispatcher [0x6AC0, 0x6BCA), literal pool [0x6BCC, 0x6BD4), and table [0xB4FC, 0xB51C). The listing agrees with Thumb/M-class decoding.

An isolated replay regenerated all 20 fixtures exactly. Original 6AC0, both port lists, paired wrapper, port leaves, interrupt helpers and 8FD0 execute without helper interception. For the successful mode-2 transitions, the recorded 59-write loader ledger matches the expected order independently: 28 sparse zero-word stores, eight zero-word stores at base+1024, three groups of seven zero-word stores at 64-byte stride, then factory words `0x55` and `0xAA` at base+`0xFF04` and base+`0xFF0C`. Version mismatch performs no loader copies and propagates mode-dispatch return 64 while earlier port effects remain.

The run also verifies four original port calls, final port register words, saved mode/flag, mode-2 register writes, helper arguments, and R4/R8/SP/PRIMASK preservation. Mode 3 bypasses the loader as decoded.

**Limits:** Factory bytes and the register block are modeled. Arbitrary configuration contents, physical MMIO effects, aliasing/concurrency and external factory-byte authentication are not established. No canonical admission is made.
