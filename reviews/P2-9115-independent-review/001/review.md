# P2-9115 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- All 152 instructions match the pinned image.
- The 0x200B builder reads its fifth stack argument only after nonnull allocation, writes five payload bytes, and returns full saved entry R3.
- The 0x2009 length/fill builder copies low8(count) bytes and computes fill size as modulo-32-bit 31-low8(count) without a <=31 guard, then dispatches; null skips source reads and returns zero.

Limitations:

- Counts above 31 cause the literal observed overcopy/wrapped fill behavior; memory safety is not established. Source, allocator, copy/fill and dispatch contracts remain unresolved.
