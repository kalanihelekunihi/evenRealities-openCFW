# P2-20715 independent review

Status: **partial / unaccepted**.

Fresh replay passed against the locked image; image SHA-256 and source/fresh receipt hashes were verified.

102B: captures bytes19..5 descending, then byte4, then independently rereads byte14 and composes the LOW4 nibble mask into the mask argument.

No helper contract, byte-stability assumption, or whole-firmware coverage is inferred. No source or gate files were changed.
