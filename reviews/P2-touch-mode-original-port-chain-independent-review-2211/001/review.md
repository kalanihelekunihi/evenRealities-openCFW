# Independent review 2211

**Result:** PASS_SCOPED.

The source and all receipt files match their hashes. Code [0x6AC0, 0x6BCA), literal pool [0x6BCC, 0x6BD4), and jump table [0xB4FC, 0xB51C) independently match the declared range hashes and decoded listing.

An isolated replay regenerated all 20 fixtures exactly. Original 6AC0, 6078, 60EA, 6044, 5FC6, 5CF8, 5D34, 4492 and 449A execute; only 8FD0 is controlled. The replay verifies four ordered port calls and arguments, resulting mode/function/high-bit/enable words, PRIMASK restoration, saved mode and flag, parameter clearing, selected register writes, and R4/R8/SP preservation.

For requested modes 2 and 3, the observed child sequence is 6078, 60EA, 6044, including two 5FC6 entries from the paired helper. Mode 2 then calls 8FD0 with the decoded register base, context field, selector 2 and table word. A nonzero 8FD0 result returns 64 without committing the new saved mode or mode-2 register writes, while earlier port-chain effects remain; zero follows the success writes. Equality and invalid-saved-mode guards agree with the fixtures.

**Limits:** 8FD0 is controlled, so its behavior is not established. Port lists/buffers are fixed; dynamic mutation and invalid-entry BKPT continuation are unresolved. RAM-backed register tests do not establish physical MMIO effects. No canonical admission is made.
