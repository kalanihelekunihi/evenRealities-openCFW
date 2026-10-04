# P2-9085 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 140 instructions match the pinned image byte-for-byte.
- The builder requests command 0x2013 with payload length 14. On nonnull allocation, it stores the low-byte field plus its high byte and copies six halfwords through twelve separate fresh loads into payload offsets 5..16, then dispatches.
- Null allocation skips source reads and payload writes; both branches return saved entry R3 through POP-to-R0 and restore R4/R5.

Limitations:

- Source pointer validity and allocation/dispatch contracts remain unresolved. Separate source reads preserve possible mutation/overlap behavior; no snapshot, concurrency, or physical claim.
