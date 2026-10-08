# P2-20837 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 66 instruction bytes at 0x47CC1C..0x47CC5E; pinned image and all source hashes match, raw instruction rows tile the range, and internal branches resolve to instruction starts. The leading ANDS extracts the sign bit; low/high NEG plus carry-dependent SBC performs wrapping two-word negation. A zero test branches to the next routine at 0x47CC60 before the local frame is pushed. Otherwise the helper call is framed; subsequent carry/sign tests conditionally negate the returned R1:R0 pair and R3:R2 pair, then POP restores R4/PC. Helper arithmetic and pending-tail behavior are not inferred.
