# P2-21197 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x48191E..0x481972 (84 bytes); instruction and literal-reference outputs match. Star precision stores the full argument word at SP56 and advances the argument cursor by four without normalizing negative values. Non-star parsing distinguishes a textual minus by retaining marker value 45 and advancing the format pointer; each digit is still consumed, but numeric updates are skipped for that marker, leaving precision zero. Otherwise digits update SP56 only while the signed value is below the literal limit, using the mapped wrapping arithmetic. R4/R5 clobbers and fresh stack reloads are preserved. The following modifier stage remains unresolved.
