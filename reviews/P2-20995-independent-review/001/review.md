# P2-20995 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed; instruction and reference outputs match candidate for 0x47E878..0x47E8F2. The first entry is an 8-byte-frame infinite driver, confirming the branch target 0x47E8F2 and no local epilogue. The second entry uses a 24-byte frame, compares unsigned R6 against R5, computes a wrapping subtraction, and uses separate pointer loads. The final POP takes R0/R1 from stack slots which may be overwritten by callees, rather than returning the final helper result. Helper contracts remain unresolved.
