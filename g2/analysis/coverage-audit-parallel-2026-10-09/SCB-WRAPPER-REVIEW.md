# Independent SCB wrapper linkage review

Verified ReadArray30, WriteArray48 and WriteDefaultArray48 complete linked target bytes:126 distinct wrapper bytes. [SCB-WRAPPER-VERIFICATION.json](SCB-WRAPPER-VERIFICATION.json) independently checks object/script/ELF hashes, parses all six linked sections and wrapper-inclusive coordinates, and decodes three original BLs. No compilation/linking was repeated.

Original calls0x9266->0x9218,0x92CA->0x926E and0x930A->0x92D6 bind Read/Write/Default no-check helpers. The unchanged object hash agrees with prior independently audited SCB holdout object and its source/header/flag environment. Original known wrapper extents are `[0x9250,0x926E)`, `[0x92A6,0x92D6)` and `[0x92E6,0x9316)`; no overlap with helper spans occurs. Fixed link starts are original boundaries, not an address search.

Pinned public source says ReadArray selects min(request,current RX occupancy), calls the no-check reader and returns selected count. WriteArray/Default select min(request,FIFO capacity minus current TX occupancy), call their no-check helpers and return selected count. This describes a register-snapshot admission contract, not requested-count waiting, interrupt scheduling or wire completion. Capacity-minus-occupancy uses source unsigned arithmetic; do not add a saturation guarantee for impossible/incoherent hardware occupancy beyond that stated operation. Byte/halfword helper behavior was previously reviewed.

Three no-check sections128 bytes are reused exact dependencies and excluded from the addition. Supported combined distinct comparator total is1260 bytes across14 selected functions/three translation units: prior1134+126 wrappers. This is selected comparator scope, not new recovered/admitted coverage or a whole-family/source-complete percentage. Campaign adoption and prior attribution reconciliation remain separate.

No complete touch build, original producer identity or physical semantics is inferred. Audit changed only additive output and performed no build, source/packet/state/index/device mutation.
