# P2-20871 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 128 bytes at 0x47D0DA..0x47D15A; image/source hashes and instruction tiling match. Three byte6 observations are independent: diagnostic SP8 load, mask-path R3 load, and functional exact-1 test. On exact 1, a fresh runtime flag byte is ORed with 1 and stored, R5 is replaced by the literal pointer, then two helpers receive the explicit arguments shown; the other path freshly clears bit0 and skips that helper pair. R6 remains the original buffer pointer. The runtime read-modify-write is not claimed atomic, and the pending continuation remains outside this slice.
