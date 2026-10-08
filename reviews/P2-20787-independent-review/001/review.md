# P2-20787 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed; image SHA-256 and source/fresh receipt hashes verified.

134B: initial fresh byte47 zero takes diagnostics2039; nonzero uses distinct diagnostics2036. Full R9 signed comparison to 10; R10 is table base + (R9<<8). Byte48 is checked before byte47; either zero loops to 47BD90 and rereads byte47. Both nonzero increments R11. Fresh replay and hashes verified.

No stable-memory assumption or field contract is inferred; later continuation remains outside the slice. No source or gate files changed.
