# P2-9097 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 130 instructions match the pinned image.
- The first builder creates a zero-payload 0x202F packet, dispatches if nonnull, and returns saved entry R7. The 0x2017 builder copies two sequential 16-byte spans to offsets 3 and 19, dispatches and returns child R0; null returns zero before source reads.
- The 0x201B builder requests two payload bytes and stores low16(field) little-endian at packet+3/+4; dispatch occurs only for nonnull allocation, and null returns zero.

Limitations:

- Copy overlap and pointer validity are unresolved; allocation/header and dispatch child contracts are out of range. No semantic packet type, concurrency, physical, or whole-firmware claim.
