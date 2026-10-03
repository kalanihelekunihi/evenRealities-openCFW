# Independent review 2219

**Result:** PASS_SCOPED.

The source, body [0x6608, 0x664A) and all receipt files match their hashes. Independent Thumb/M-class decoding agrees with the listing.

An isolated replay regenerated all 72 fixtures exactly. It checks modes 0/1/2/3/4/`0xFFFFFFFF`, budgets 0/1/3 and status changes after 0/1/3/4 controlled delays. Status read and delay counts, A324 argument 1, return 0 on mismatch, return 4 on an equal status with exhausted budget, and R4/SP preservation match.

The instructions use mask `0x01000000` for modes 2/3 and mask `1` otherwise. The wanted value is `(mode << 24) & mask` for modes 2/3 and the full mode value for other modes. Each poll reloads context root, root+8 register pointer, base pointer and the word at base+384. A mismatch returns 0; equality checks the remaining budget before calling the delay helper and decrementing.

**Limits:** A324 is controlled, so physical timing/readiness behavior is not established. Pointer mutation, full-width budget wraparound and concurrent changes are not covered. No canonical admission is made.
