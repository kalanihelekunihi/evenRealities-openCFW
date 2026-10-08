# Independent review: P2-19159

Status: partial / unaccepted. No source or gate changes.

Fresh replay of `0x469EB0..0x469F16` (102 bytes) exactly matches candidate instruction/reference records. Selector 69 uses four distinct word reads to assemble the six-byte SP32 record; the input+16 pointer is unguarded, and later loads replace it as described. Selector 74 builds the separate six-byte zero-filled record at SP24. Both routes call `0x464BB2(34, SP-record, 6, 0)` and branch with the full child R0 live. The two records are distinct stack regions. No pointer safety or child contract is inferred.
