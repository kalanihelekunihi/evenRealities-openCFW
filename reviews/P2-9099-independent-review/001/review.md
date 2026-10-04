# P2-9099 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All mapped instructions match the pinned source.
- The 0x201A builder writes a little-endian low16 field at payload+3/+4 then copies 16 bytes at +5; null allocation skips source read and returns zero, while success returns dispatch-child R0.
- The three zero-payload wrappers call allocation with commands 0x2018, 0x2002, and 0x2003, conditionally dispatch on nonnull pointer, and return saved entry R7 regardless of child status.

Limitations:

- Allocation, copy, dispatch, and ownership contracts remain unresolved. No source validation, concurrency, physical transport, or whole-firmware claim.
