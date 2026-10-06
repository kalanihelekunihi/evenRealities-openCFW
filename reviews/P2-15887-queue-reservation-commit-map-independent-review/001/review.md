# P2-15887 independent review

Fresh GNU ARM disassembly reproduces all 102 bytes in 0x538FB4..0x53901A against the pinned image. NULL or masked-signature mismatch returns 2; equal q16/q20 returns 7. On the success path the routine writes the node marker and next pointer, advances q20 and then q16, conditionally issues DMB for q8 >= 0x20080000, and publishes the low byte of q32 through the pointer loaded at q36+12. R2 retains the queue pointer. The leaf does not increment the producer counter.

Child behavior, physical visibility, faults, aliasing, and concurrency remain unqualified. This instruction map does not inherit behavioral claims from the separate fixture. Status remains partial and unaccepted.
