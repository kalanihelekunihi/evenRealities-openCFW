# P2-20959 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed for 80 bytes at 0x47E2D0..0x47E320. Candidate and fresh instruction, pseudocode, and reference artifacts match exactly.

The entry saves R4-R6/LR and unconditionally clears state byte 2 before dispatching on LOW8(entry R0). Mode 1 enters the update path; modes 2 and 3 return zero without further state writes; mode 0 and modes 4..255 return one. In the mode-1 path, the handle word is freshly loaded for 4497B6. The code then compares state byte 0 with a fresh input byte and conditionally clears byte 1. It separately rereads the input byte to copy into state byte 0, writes state byte 2=2, freshly reloads the handle for 44981C, and returns zero. Thus compare and copy use distinct input observations; helper effects and atomicity are not assumed. Entry mode 256 is narrowed to zero and follows the return-one path after the initial clear.

Candidate remains partial/unaccepted; no source or gate files changed.
