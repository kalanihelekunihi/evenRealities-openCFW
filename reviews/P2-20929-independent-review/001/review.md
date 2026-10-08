# P2-20929 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed for the full 90-byte routine at 0x47DD08..0x47DD62. Candidate and fresh instruction, pseudocode, and reference files match, with contiguous instruction tiling.

The routine allocates a 24-byte frame and seeds SP0 with a literal pointer; 43C0E4 is called to initialize/prepare the local result area, but its write contract is unverified. Each loop iteration reads the pointer and byte for the zero check, then makes a separate pointer/byte observation before subtracting 48 and doing an unsigned `<10` digit test. The slot limit is a signed `R4 >= 3` comparison. Nondigits advance the pointer with wrapping addition; digits call 48D874 with the fresh pointer, SP, 10, and live R3, then store the full R0 result into slot `SP+4+4*R4` and increment R4. There is no explicit caller-side pointer increment on that digit path.

The exit packs the complete words without field masks: `(slot1 << 16) | (slot2 << 8) | slot3`, with 32-bit shift/OR behavior. The frame's first local slot is discarded, then POP restores R4/PC. Unfilled slot values and helper pointer effects are not assumed. Candidate remains partial/unaccepted; no source or gate files changed.
