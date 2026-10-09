# Independent raw artifact interval union review

PASS for discovery PARTIAL-COVERAGE-RECONCILIATION.md and partial-artifact-range-unions.json. Independently read and hash-verified all10,499 bounding envelopes against authenticated canonical image bytes and all contributing nonempty C exports against the research manifest. Declared ranges are in image bounds. Rebuilt half-open interval unions (inclusive ends+1), merged overlap/adjacency, and independently matched saved union and complement arrays. Only successful decompiled:true entries with real nonempty exported bodies enter pseudocode unions;378main and54bootloader false rows remain excluded. No new decompiler/assembly/build execution.

| Component | Raw export-associated union | Whole payload denominator | Artifact-associated payload fraction |
|---|---:|---:|---:|
| Apollo main |1,555,524 bytes|3,523,396 bytes|44.148430%|
| Apollo bootloader |112,506 bytes|148,599 bytes|75.711142%|
| Touch |27,879 bytes|34,464 bytes|80.893106%|
| Case |43,072 bytes|55,784 bytes|77.212104%|

These percentages use **whole payload**, including wrappers/data/padding. Discovery's44.148830/75.711142/80.968285/77.256421 percentages use header-stripped canonical image denominators instead; both arithmetic results are correct, but must be labeled differently. No codec/BLE whole-payload union established, so no six-component weighted global total.

This cohort's Apollo main is8,475successful/8,853recognized envelopes, different from the earlier authenticated7,449/7,449 harvest. Do not combine or substitute their denominators. Within this exact cohort: bootloader849/903, touch308/308, case435/435. Nonempty/hashes establish authentic raw artifacts, not valid semantics, actual function identity, reviewed admission or C compilability.

No complete per-byte code/data/padding classification accompanies these ranges, so this audit cannot establish whether every envelope is exclusively instruction bytes. Bounding envelopes can span holes in noncontiguous bodies; only declared ranges enter unions, and envelope-byte authentication alone cannot classify the holes or decode semantics. A concrete counter to treating all provider extent as raw pseudocode: touch constructor's historical envelope endsAA1C before its authenticated16-byte literal poolAA1C–AA2C. Some pools are excluded, but no exhaustive classifier proves all other union spans free of data/alignment. Consequently these remain artifact-associated fractions rather than executable/semantic coverage percentages. Complements are unassociated bytes, not missing code by subtraction.

Supporting independent script partial_union_verify.py and PARTIAL-UNION-VERIFICATION.json. No canonical coverage ledger, source admission or campaign gate modified.
