# P2-21177 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x4813BC..0x481468 (172 bytes); instruction and literal-reference outputs match. The UXTB bank selector accepts only 1 in this tail; other byte values set status 6, but only after the earlier helper work, and perform no output writes. For bank 1, nonzero mask-enable triggers seven ordered fresh mask reads; zero retains the stack-initialized all-ones masks subject to possible helper aliasing. Seven output words are then formed with a fresh target read before each mask reload and store. The shared tail reloads SP0 for MSR PRIMASK, selects status 0 or 6, and releases the 56-byte frame via ADD SP,36 plus POP 20.
