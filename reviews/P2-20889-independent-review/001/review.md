# P2-20889 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 162 bytes at 0x47D516..0x47D5B8; image/source hashes and tiling match. Initial helper result is held full-width in R6; the next helper precedes an independent byte5 read and LOW8 comparison. Separate status paths have independent byte6 observations. Exact one sets flag bit3 and exact zero clears it; each calls 0x47D8CE, then narrows the old R6 only after that call and compares it to full new R0, assigning R4=1/0. Other byte6 values leave R4 unchanged. The branch at the endpoint continues to the shared pending exit.
