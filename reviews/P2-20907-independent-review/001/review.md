# P2-20907 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 94 bytes at 0x47D870..0x47D8CE; pinned image/source hashes and tiling match. The 16-byte frame saves R2/R3/R4/LR, then STRD overwrites the SP0/SP4 slots with template data. Two independent helper calls use full-width exact-1 comparison for SP5 selection; entry R0 is separately narrowed to LOW8 and tested for SP6 boolean, so 256 maps to zero. The 0x464D1C call is distinct, and POP returns template-derived SP0/SP4 plus saved entry R4. Separate frameless leaves read the runtime flag byte and return bit0 or bit1 as 0/1, preserving R1-R3.
