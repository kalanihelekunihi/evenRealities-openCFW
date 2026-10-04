# P2-9051 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 74 instructions at 0x53013C..0x530186 match the pinned image byte-for-byte.
- 53013C uses entry R1 as the buffer and ignores entry R0; it freshly reads bytes +2/+3, passes low16(length+4) to the child, then compares the child’s full R0 to that low16 expected value. If length+4 wraps to zero (length 65532), matching child result zero returns zero.
- 530166 likewise passes its entry R0 buffer as R2 and returns 1 only when the full child result equals the byte-derived count; otherwise returns zero. R4/SP/PC restoration matches the epilogues.

Limitations:

- The transport child 4B4A02 behavior is not established here; the map records only observed argument setup and result comparison. No pointer guard, concurrency, or physical claim.
