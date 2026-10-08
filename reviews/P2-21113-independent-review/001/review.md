# P2-21113 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x480358..0x4803C2 (106 bytes); instruction/reference outputs match candidate. Five wrappers use table offsets 20, 24, 28, 32, and 44. Each has separate test and callback reloads, preserving possible table mutation between reads. Calls pass callback address in R0, table pointer in R1, and live entry R2/R3; returns are full callback R0 for the first four. The offset-44 wrapper’s common POP R0,PC returns saved entry R7, discarding call/zero result. No output initialization or callback contract is inferred.
