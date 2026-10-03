# Independent review 2225

**Result:** PASS_SCOPED.

The source, code [0x664C, 0x6772), literal pool [0x6774, 0x6780), and all receipt files match their hashes. Independent Thumb/M-class decoding agrees with the listing.

An isolated replay regenerated all 160 fixtures exactly. Original 664C, 6608, A324 and 4480 execute without helper interception; only the optional callback is controlled. The complete ordered descriptor/register write ledger, effective count, callback argument, high-register/SP state, and 441 delay entries when bit 24 is clear match the assertions.

With supplied scale byte 2 and mode 2, a clear status bit causes 441 calls to original A324(1), each executing the one-iteration leaf, then 6608 returns exhausted-budget status 4. The 664C caller continues through its common register-block start writes rather than returning on that status. A set bit bypasses polling.

**Limits:** The status word is static/modelled and scale is supplied as 2; this does not establish physical readiness or elapsed-time behavior. The callback is controlled. Factory scale provenance, pointer mutation, concurrency and physical MMIO effects remain unresolved. No canonical admission is made.
