# Independent review 2217

**Result:** PASS_SCOPED.

The source and all receipt hashes match. Code [0x664C, 0x6772) is 294 bytes; literals [0x6774, 0x6780) are separate. The stored listing matches independent Thumb/M-class decoding.

An isolated replay regenerated all 160 fixtures exactly. It checks count clamping at 21, zero length, source stride 28 and destination stride 44, the full ordered register-write ledger, 6608 arguments, the callback argument at context+28, base/config state and R4/R8/SP. 6608 and the callback are controlled.

The corrected armed-status path is confirmed by decode: after callback and config-byte reload, the armed test and base+384 bit-24 test lead to a store of 256 at base+324, then branch to 0x673C. That common path ORs bit 31 into base word 0, stores 1 at base+320 and returns. The fixture ledger expects those common writes after the 256 store, correcting the prior attempt's mistaken early-return assumption.

**Limits:** The replay uses a RAM-backed register block, synthetic source words and controlled helper/callback stubs. Their effects, aliasing/concurrency, arbitrary pointer behavior and physical MMIO are not established. No canonical admission is made.
