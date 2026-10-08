# P2-20897 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 98 bytes at 0x47D7B6..0x47D818; pinned image/source hashes and tiling match. R4 is narrowed to LOW8 before the guard. Three possible independent 0x47D8CE observations feed a LOW8 logger value, a separate LOW8 mask value, and a final 0x4ABD60 call with explicit zero plus LOW8 result. The shared epilogue explicitly sets R0=0, adds 20 to SP (discarding 16 local bytes and saved entry R3), then POPs R4-R7/PC to complete the 40-byte frame. The case flag is not returned.
