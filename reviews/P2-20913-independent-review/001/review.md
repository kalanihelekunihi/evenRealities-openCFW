# P2-20913 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed for the two entries at 0x47D9C4..0x47D9FA (54 instruction bytes). Candidate and fresh instruction JSON hashes match (`9e25f0a9bac3ed738035eaace1332e5983a1d45fcc6915e285fe3352a95111f5`); exact instruction byte tiling and branch targets agree. The two entries each push R7/LR and pop R1/PC, so R1 receives saved entry R7. First entry calls 4A2FDC and returns its unnormalized live R0. Second calls 4A2914, tests its full-width result, and selects 0x47D8E4 for nonzero or 0x47D8F0 for zero; each selected leaf's result is normalized to 0/1 before return.

I independently inspected the locked bytes at both selected leaves: 0x47D8E4 extracts bit 4 from the runtime flag byte; 0x47D8F0 extracts bit 5. This agrees with the selector description. The calls remain externally defined behavior, and no broader coverage or contract is inferred. Candidate status remains partial/unaccepted; no source or gate files changed.
