# P2-9025 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All instructions across 0x530E64..0x530F08 match the pinned image byte-for-byte; the pool literal reference matches its locked word.
- The copy path truncates allocation size (fresh length+8) to 16 bits, then separately reloads and passes untruncated length+8 to the copy helper. These values can differ at high lengths.
- Type 6 writes output halfword at offset 18; non-6 writes at offsets 16 and 18 using separately reloaded record bytes. Transfer mode clears record+8 before formatting and downstream calls. The function returns the final child R0.

Limitations:

- Allocation, copy, scheduling, dispatch, pointer validity, ownership, and concurrent mutation behavior are unresolved. No generic buffer/API contract is claimed.
