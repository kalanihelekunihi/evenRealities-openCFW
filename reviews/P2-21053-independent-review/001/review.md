# P2-21053 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47F6F2..0x47F7AE (188 bytes); instruction and reference outputs match candidate. The helper receives LOW8 index and copies a 16-byte record over saved entry slots. Full nonzero maps to normalized 1. Zero-result dispatch compares the full class word against its ordered constants and literal; class-matched predicates use two separate pointer and word reads, plus the independent SP4 record mask, preserving potential changes between observations. Common return narrows the Boolean, discards 16-byte record/entry overlay, and pops R4/PC. External helper/ownership semantics remain unknown.
