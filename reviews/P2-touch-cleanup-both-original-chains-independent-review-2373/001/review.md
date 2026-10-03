# Independent review 2373

**Result:** PASS_SCOPED.

Candidate receipt SHA-256 cddae2842c5929d2f5af7345bd448ce2c434ddae15b311d7c341c3507f582bd0; source SHA-256 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87 matches the pinned 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87. The four body ranges total 126 bytes with digest dbc3eed305e6b4d0d645756a591169c0c18694dc87e4269f53e5eb4da8ecf11b; additional range [0x4E36,0x4F6E) has digest 4f789b90461fe7aaada7494c1dc4e6094054112d4544e21385d9dded89864852. Candidate evidence-file hashes match its receipt.

Independent isolated replay passes all 324 cases (9 flag-byte values × 3 counts × 4 halfword values × 3 fills). Original 4F54 runs first and original 4E1C runs second on the same fixture memory; neither call is intercepted. The copy pass dispatches rows 2, 1, 0 and processes each row's items in increasing order. The finalization pass dispatches rows 2, 1, 0 and processes items in decreasing order.

The combined independent oracle matches ordered writes and complete modeled memory for both passes. With the exercised flags byte 0x81, copy stores halfwords to each row's distinct destination; finalization clears item byte +8, copies item halfword +0 to halfword +2, then clears byte +7. Call arguments, dispatch/item order, R4-R11 and SP assertions pass. Candidate replay output hash equals its pinned replays.json hash.

**Limits:** Only flags byte 0x81 and the fixture's separate row/source/destination allocations are covered; aliasing and mutable counts/pointers are not established. The enclosing 4AF4 routine is not executed, so activation-level effects and broader caller behavior remain open. Evidence is bounded instruction-level execution with synthetic memory; it makes no physical-hardware or canonical-admission claim.
