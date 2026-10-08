# P2-21043 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47F294..0x47F3C6 (306 bytes) with exact instruction/reference match. In the inherited 40-byte frame, the branch on SP4 versus a fresh word at R7 bypasses all later update/checks and R5 cleanup. The first helper receives five explicit arguments; successful return proceeds through a helper that may mutate SP4, then a store and second helper call. The second helper-zero route performs distinct fresh word reads for each comparison pair; no observed fields are cached. The record tail preserves repeated fresh reads of bytes 4 and 2, ordered bit updates, and the possible final status 5 after bit1 was changed. Common POP releases the full frame, with SP0/SP4 aliases affecting restored registers on applicable paths. No PRIMASK restore exists in this routine; external helper and pointed-object semantics remain unresolved.
