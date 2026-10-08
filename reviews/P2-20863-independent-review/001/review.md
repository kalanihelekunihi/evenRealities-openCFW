# P2-20863 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 88 bytes at 0x47CFB6..0x47D00E; pinned image/source hashes and tiling match. Within the inherited 40-byte frame, one path calls 0x45A568, stores its LOW8 result at SP12, then independently reads buffer byte4 into SP8 before constructing logger arguments. A separate status-query path calls 0x45A568 again, stores its LOW8 result at SP0, and then freshly reads byte4 into R3 for the mask call. Status queries remain separate and the helper precedes each corresponding byte read. No pointer/length guard is shown; continuation is pending.
