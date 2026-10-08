# P2-20865 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 88 bytes at 0x47D00E..0x47D066; pinned image/source hashes and instruction tiling match. Under the inherited 40-byte frame, the logger path calls 0x45A568, stores its LOW8 result at SP12, and then reads buffer byte5 freshly into SP8. The alternate status path makes a distinct helper call, stores LOW8 at SP0, then independently reads byte5 into R3 for the mask arguments. Both helper calls precede their respective byte5 reads; status-query calls remain separate. No pointer or length guard is present in this slice; tail is pending.
