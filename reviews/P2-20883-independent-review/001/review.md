# P2-20883 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 104 bytes at 0x47D3D4..0x47D43C; locked image/source hashes and tiling match. Three independent byte6 loads drive distinct zero, three, and two tests. Zero clears flag bit2 and calls 0x47D8CE, then narrows the old R6 result only after the helper call for comparison against full new R0. Exact three sets bit4 before ordered 0x4D306C/0x49E448 calls; exact two clears bit4 before its distinct ordered helper calls. Other values take the pending path without flag writes or helper calls. R4 remains unchanged on the latter branches; no helper contracts are inferred.
