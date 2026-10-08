# P2-21075 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47FCA2..0x47FDB4 (274-byte middle fragment); instruction/reference outputs match candidate. The version and S predicates retain their individual fresh loads and short-circuit ordering. Offset adjustments are unsigned comparisons with wrapping +7 or +6, using the inherited R2 pointer; the implementation must not collapse to a cached pair of version/state bytes. The later section performs seven ordered fullword copies/extractions, followed by a byte guard write. The preceding guard branch and this fragment both lead to FDB4; one path bypasses all writes. No helper or unwind behavior is introduced.
