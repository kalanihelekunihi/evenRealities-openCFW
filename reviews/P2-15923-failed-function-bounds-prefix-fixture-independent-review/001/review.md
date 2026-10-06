# P2-15923 independent review

Fresh no-hook replay passes all 2,048 bounded cases through the 130-byte prefix, stopping at 0x5400B8 before the next instruction. The oracle uses signed division by two truncating toward zero and checks 32-bit wrapped coordinate results. Full mapped RAM, the pushed register frame and locals, preserved registers, SP/LR/PC, PRIMASK, final NZCV, and firmware image were checked.

This does not cover the rest of the discovered function, children, fault cases, aliases, or concurrency. Status remains partial and unaccepted.
