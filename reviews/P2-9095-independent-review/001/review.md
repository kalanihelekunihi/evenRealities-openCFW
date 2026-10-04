# P2-9095 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 144 instructions across the three builders match the locked image.
- Builder 0x2024 writes two low16 fields into a four-byte payload and returns saved entry R3; builder 0x2025 creates a zero-payload packet and returns saved entry R7. Both dispatch only after successful allocation.
- Builder 0x2026 requests 64 bytes, returns zero on null allocation before reading either source, otherwise copies two consecutive 32-byte spans to payload offsets 3 and 35 in order, dispatches, and returns child R0. The order preserves possible source/output overlap effects.

Limitations:

- No source validation, snapshot behavior, or copy-helper contract beyond the mapped calls. Overlap, concurrency, allocation, ownership, and physical transport semantics are unresolved.
