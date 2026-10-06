# P2-15863 independent review

Fresh replay passed all 4,096 original calls with zero budget. The oracle covers equality and inequality outcomes across the low-byte polarity values while varying upper argument bits, and confirms the comparison remains unmasked. Returned status is 0 or 4 as expected. Full mapped RAM outside the 24-byte stack area, registers, SP/PC/PRIMASK, and pinned flash are checked.

Nonzero-budget delay behavior and resident-ROM timing are not qualified; RAM backing does not establish physical MMIO, fault, or concurrency behavior. Status remains partial and unaccepted.
