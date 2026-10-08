# P2-20885 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 118 bytes at 0x47D43C..0x47D4B2; pinned image/source hashes and tiling match. The second-match path calls 0x45A568, then reads buffer byte5 freshly and compares against the helper LOW8 result. Matching diagnostic routes include independent byte6 observations. Exact byte6=1 freshly sets flag bit3, calls 0x47D8CE, then narrows only prior R6 to LOW8 and compares it against the full new R0; unequal/equal map to R4=1/0 respectively. The new helper result is not narrowed. Non-one branches to pending continuation; helper and flag effects are not generalized.
