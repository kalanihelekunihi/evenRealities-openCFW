# P2-20881 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 120 bytes at 0x47D35C..0x47D3D4; image/source hashes and tiling match. A helper call precedes a fresh buffer byte4 read; the full byte is compared against the helper LOW8. The match path includes separate diagnostic status reads and independent byte6 observations. On exact byte6=1, the runtime flag is freshly ORed with bit2, then another helper runs; only the prior R6 is narrowed to LOW8 after that call, while the new R0 remains full-width for the comparison. The two comparison outcomes assign R4=1/0, and the non-one path branches to another pending slice.
