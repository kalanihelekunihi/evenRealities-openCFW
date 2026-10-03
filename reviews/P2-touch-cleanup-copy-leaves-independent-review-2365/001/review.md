# Independent review 2365

**Result:** PASS_SCOPED.

Receipt 4fed2c6a68662b5c595ecfe97ad3e25b368353132e5e3abe856df3ba5f343c4e pins source and the exact [0x4E36,0x4E6C) span; file hashes match. Independent execution passes 600 fixtures.

The span decodes contiguously as three leaf bodies: 4E36..4E58 (34 bytes), 4E58..4E60 (8 bytes), and 4E60..4E6C (12 bytes). Replay's byte-memory oracle agrees with original ordered halfword loads/stores and exact write hooks for all source values, five destination relations, optional pointer settings and flag patterns. The 4E36 flags are read after its destination store, so destination aliasing row+116 affects the branch as described. The 4E60 second halfword store can alias source when destination=source-2; its subsequent load observes the resulting current bytes.

All supplied memory bytes and ordered write ledger match; R4-R11 and SP are preserved. These are original-instruction executions with no helper interception.

**Limits:** Only enumerated allocations/overlap relations are tested; unmapped addresses, unaligned accesses, arbitrary aliases and asynchronous mutation are unresolved. R0-R3 are caller-clobbered; no incidental return contract is asserted. Private evidence only; accepted:false, no canonical admission.
