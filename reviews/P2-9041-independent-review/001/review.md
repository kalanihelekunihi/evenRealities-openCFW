# P2-9041 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 126 instruction bytes in the three mapped extents match the locked image, and five literal references resolve to the recorded common global base.
- The lookup scans at most three records of stride 28, compares low-16-bit keys, returns the first matching record even for key 0xFFFF, and tests no validity/active flag. High input bits are ignored.
- Accessors read the specified halfwords/byte; LDRD returns two words after clearing bit 1 only from the first. Queue count traverses fresh node links under the mapped lock calls, returns low16 count via R0, and restores entry R3 into R1 on return.

Limitations:

- No malformed/cyclic list or pointer validity checks are established; queue traversal has no count bound and can fail to terminate for cycles. Lock/preemption semantics and field meanings are not inferred.
