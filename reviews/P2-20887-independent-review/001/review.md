# P2-20887 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 100 bytes at 0x47D4B2..0x47D516; pinned image/source hashes and tiling match. Byte6 exact-zero clears flag bit3 then calls 0x47D8CE; only prior R6 is narrowed after the call before comparison with full new R0, and the message helper at 0x47CE90 follows. Exact three sets flag bit5 and calls 0x4A2914, with a zero result triggering 0x4A2EA4(1,...); exact two clears bit5 without a helper. Each selector observation is fresh. The shared D514 tail branches out to 0x47D7B6; no side effect is inferred from helpers.
