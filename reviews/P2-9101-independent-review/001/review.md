# P2-9101 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 128 mapped instruction bytes match the pinned image.
- The 0x2016 builder writes a two-byte low16 field and returns zero on null allocation or child R0 on successful dispatch. Zero-payload 0x201C/0x200F wrappers return saved R7, not child status.
- The 0x200A builder writes one low-byte argument to payload+3; null returns zero and success returns the dispatch-child result.

Limitations:

- No input pointers are dereferenced in these functions; allocation and dispatch contracts remain unresolved. No physical, concurrency, or whole-firmware claim.
