# P2-20961 independent review

Status: **partial / unaccepted**.

Fresh replay passed for the 8-byte slice at 0x47E60C..0x47E614 from the locked image. Candidate and fresh data hashes match (`0f9fa6c0598a467c8f91527985ec6c9a2fbc686fd63d1245fbce52cc5bf6a923`). The two little-endian words are 0x200F4800 and 0x20074830. Both mapped LDR.W consumers in map 21358 were verified against its receipt, and independent PC-relative arithmetic resolves the loads at 0x47E2D4 and 0x47E2EC to 0x47E60C and 0x47E610 respectively.

This establishes the literal values and mapped references only; RAM ownership, semantics, and exhaustive consumer coverage remain unproven. Candidate remains partial/unaccepted; no source or gate files changed.
