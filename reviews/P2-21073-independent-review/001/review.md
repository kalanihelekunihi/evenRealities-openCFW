# P2-21073 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47FC14..0x47FCA2 (142-byte middle fragment); instruction/reference outputs match candidate. The fresh byte guard branches outside the fragment when nonzero. Zero enters nine ordered source-load/extraction/fullword-store sequences. Repeated source words are independently loaded for their separate fields; prior stores may alias later reads. The stores write extracted full words rather than RMWs. The fragment ends at FCA2 with the inherited 24-byte frame active; no return/completion claim. External address-space/ownership semantics remain unresolved.
