# P2-20853 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 82 bytes at 0x47CED6..0x47CF28; pinned image/source hashes and instruction tiling match. The 16-byte PUSH frame is overlaid by two template words from literal 0x47D904. Two independent 0x45A568 calls feed SP4 low byte and a full-width exact-1 comparison selecting SP5=2/1. A single fresh byte read at 0x47D900 extracts bit 4 to select SP6=3/2; there is no second flag read in this slice. The 0x4651E0 result is discarded; POP aliases return words from SP0/SP4 and saved entry R7 from SP8. Template bytes may be modified by the callee, so pointed-to protocol semantics remain unclaimed.
