# P2-19021 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x4685E8–0x46862E (70 bytes) against locked flash SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. Instruction and reference records match the candidate exactly, and the replay tiles the interval.

The first branch tests bit 1 of the fresh `43D0CE` result; the set route reads the diagnostic literal and writes the shown SP slots before calling `43D574`. Bit 0 and conditional bit 2 are separate fresh calls, with the latter only reached when bit 0 is clear. The enabled diagnostic loads its first literal, copies it to R2, and calls `43CE9E` with mask `0x04000000` and live R3. Both paths join at 0x46862C and branch to 0x468A2A, outside this range; no return value or epilogue is established here. No acceptance/gate claim is made.
