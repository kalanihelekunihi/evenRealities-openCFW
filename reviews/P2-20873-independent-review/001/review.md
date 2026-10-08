# P2-20873 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 180 bytes at 0x47D15A..0x47D20E; locked image/source hashes and instruction tiling match. The mismatch path performs another helper call before a fresh byte5 comparison. Matching then flows through separate diagnostics and independent fresh byte6 reads for mask, functional exact-1 action, and additional logger arguments. Exact-one sets flag bit1 before the two helper calls; the alternate branch freshly clears that bit. Shared code reloads the runtime flag for bit-pair tests and calls subsequent routines according to those observations. R4 remains unassigned and no flag value is cached across reads; pending continuation and helper contracts remain open.
