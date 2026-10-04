# P2-9087 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 230 instruction bytes across builder and copy helper match the pinned image.
- The builder requests type 0x200D/payload 25, exits before stack argument loads on null allocation, and otherwise reads stack arguments at entry SP+0,+4,+8 after its 32-byte frame. It writes fields at packet+3..8, copies six bytes to +9, stores the next byte at +15, then serializes six halfwords via separate low/high source loads at +16..27.
- The final dispatch child result is returned in R0; this is distinct from wrappers that pop a saved register to R0. The copy helper passes size 6 to the underlying copy child.

Limitations:

- Stack/source pointers are unchecked. Allocation and dispatch contracts, source mutation between repeated halfword reads, and ownership/lifetime are unresolved; no physical or concurrency claims.
