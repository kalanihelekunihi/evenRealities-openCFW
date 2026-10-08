# P2-20893 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 218 bytes at 0x47D642..0x47D71C; pinned image/source hashes and instruction tiling match. Separate diagnostic branches use distinct fresh byte6 loads and status queries. On the functional path, a helper call precedes fresh byte5 comparison against helper LOW8. Matching paths again read byte6 independently. Exact three freshly sets flag bit5, then orders 0x4D306C, 0x49E448 and 0x4A2914; only a zero full result from 0x4A2914 triggers 0x4A2EA4(1,...). Exact two clears bit5 and makes its two ordered calls. Other values branch to the shared pending tail; R4 is unassigned in this slice.
