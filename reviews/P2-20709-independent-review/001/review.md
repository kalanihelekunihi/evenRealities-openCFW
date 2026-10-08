# P2-20709 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed; source and fresh receipt hashes and image SHA were verified.

102B: mask call captures bytes19..5 descending, then reads byte4 and independently rereads byte14 for LOW4-to-bit22 mask composition; preserves the second observation.

No helper contract, stability assumption, or whole-firmware coverage is inferred. No source or gate files were changed.
