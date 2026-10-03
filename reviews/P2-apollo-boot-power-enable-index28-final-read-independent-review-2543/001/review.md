# Independent review 2543

**Result: PASS_SCOPED.**

The exact candidate is `g2/build/pseudocode-first/20260930T190500Z/analysis/apollo-boot-power-enable-index28-final-read-2542/001`. Receipt, pseudocode, replay and fixture hashes match; the locked inventory and both flash/decoded-ITCM source pins also match. I ran the replay from an isolated copy and all 24 original-instruction cases passed.

The cases separate the poll reads from the later read at `0x40021008`: ready on read 1 or 2 proceeds to a final read; its modeled bit set returns 0 and clear returns 1. A never-ready poll returns 4 after six poll reads/five delay calls and skips the final read. Callback order and the one PRIMASK-protected `0x40021004` write are preserved, and the assertions cover read/write traces, SP, high registers and PRIMASK. This confirms polling success alone does not force a zero return in the bounded modeled path.

The final read’s value is supplied by a hook, so this does not establish a physical status transition. Null callback slots and index 28 are the only composition exercised. Other indices, nonnull callbacks, hardware timing, startup setup and broader ownership remain unresolved. Private evidence only; accepted:false and no canonical admission.
