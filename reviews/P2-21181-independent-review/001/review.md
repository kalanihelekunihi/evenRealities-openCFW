# P2-21181 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x4814F0..0x481574 (132 bytes); instruction and literal-reference outputs match. UXTB selector 0 and 1 call the helper with the recorded full/low-byte argument variants, stage its full result at SP0, and perform seven ordered direct input-word stores to their respective literal target banks before reloading SP0 for MSR PRIMASK. Other nonnull selectors join the common path without helper calls or writes. That path includes the fresh read at literal pointer 0x4817D4 whose value is discarded, then returns zero. The null-input return bypasses this read and returns 6. POP routes current SP0 or saved entry R2 into R1 according to the path and releases 16 bytes.
