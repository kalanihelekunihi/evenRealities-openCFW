# P2-9121 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 94 instructions match the pinned image.
- The two zero-payload wrappers use commands 0x1009 and 0x1001, conditionally dispatch on nonnull allocation, and return saved entry R7.
- The command 0x1405 builder requests two payload bytes, writes low16(field) little-endian at offsets 3 and 4, dispatches when nonnull, returns child R0, and returns zero on null.

Limitations:

- No pointer or copy behavior occurs in the mapped builders. Allocation and dispatch contracts remain unresolved; no concurrency, physical, or whole-firmware claims.
