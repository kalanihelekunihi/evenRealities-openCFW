# Independent review 2473

**Result:** PASS_SCOPED.

Candidate: `g2/build/pseudocode-first/20260930T190500Z/analysis/touch-mode-two-distinct-root-table-lifetimes-2472/001`. Receipt SHA-256 `6ec6f1c63f9b88a1dc2cb7a1144c2267cf3d217811856e899056d3a13c2b4c62`; all four artifact hashes match. Each listed body span matches the pinned source image.

The isolated replay passed all 160 cases. Original 6AC0, 8FD0, 6078, 60EA, and 6044 execute; only 5FC6 is controlled. During the first controlled pin call, ctx.word0 changes to a replacement root with a distinct table. The list loops observe the reduced counts, and original 6044 uses replacement-root paired ports/pins. The later 8FD0 call receives the original table’s version pointer, while the replacement table has a distinct version byte. Assertions check these exact arguments, per-pin calls, shortened list effects, selector-dependent loader/mode writes, final result, and R4–R11/SP.

This supports the stated cached-versus-fresh root behavior for the tested path: list/pair setup observes the replacement root, while loader setup follows the original root/table retained by the dispatcher. The distinct version bytes make that distinction observable.

**Limits:** This does not test mutation of the original root’s own table pointer. Pin helpers remain controlled, and factory/MMIO values are modeled; physical effects, concurrency, and fault behavior are unresolved. Private evidence only; accepted:false, no canonical admission.
