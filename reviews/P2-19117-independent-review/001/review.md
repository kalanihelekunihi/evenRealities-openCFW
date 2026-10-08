# P2-19117 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x46976A–0x4697EC (130 bytes, 46 instructions), matching candidate instruction/reference records against locked image SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

Verified the ordered fresh base and offset +8/+12 loads and result stores, subsequent fresh child reads, and explicit word-zero store at +24 before the external branch. The alternate 0x4697BA entry has its own register state: R5 is original R3 and is not replaced by the preceding resource-path literal. The second branch’s result remains live at the boundary. No child contract is inferred.
