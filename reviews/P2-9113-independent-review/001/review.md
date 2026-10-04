# P2-9113 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 120 mapped instruction bytes match the pinned image.
- The 0x2001 builder requests eight bytes and copies them to payload+3; the 0x2005 builder requests six bytes and uses the six-byte copy helper. Both null paths skip source reads and dispatch; successful paths return child R0.
- The 0x200C builder requests two bytes, writes low8 of both scalar inputs at offsets 3 and 4, dispatches if nonnull, and returns saved entry R3 rather than child status.

Limitations:

- Copy and dispatch child contracts and source validity are unresolved. No physical delivery, concurrency, whole-artifact completeness, or C claim.
