# P2-20935 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed for 124 bytes at 0x47DDFE..0x47DE7A. Candidate and fresh instruction, pseudocode, and reference artifacts match exactly.

The first wrapper calls 4D34C4 with `(entry R0,12,0,live R3)` and returns its full R0 with saved entry R7 in R1. The second passes entry R0/R1, literal 0x47E294, and entry R2 as the fourth argument to 44B728, then returns its own saved R7 into R0. In the main entry, 44A43C's full result is checked unsigned against 8. Passing that guard, the code calls 44B610 and then 46CACC with the wrapping 32-bit expression `entry R0 + length - 4`; any nonzero helper result fails.

The parser call receives `entry R0 + 3`, SP, 10, and live R3, with SP0 initialized to zero first. Its full result is retained. The caller freshly loads SP0 and requires nonzero, then independently reloads SP0 and compares it to the same wrapping end-pointer expression. Only equality stores the full parser result to `[entry R1]` and returns 1; otherwise it returns 0. No null-output, numeric-range, or parser-overflow check is recovered. The 24-byte frame's POP restores saved slots, with R1 reflecting SP0 (original saved entry R2 on early failure or parser-written local state later).

Helper contracts remain unresolved; status remains partial/unaccepted, and no source or gate files changed.
