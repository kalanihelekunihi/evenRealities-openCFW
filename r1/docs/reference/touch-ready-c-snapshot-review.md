# Touch ready input/callback snapshot in C

The stock board-open routine at `0x4eb80` reads adjacent input and callback
words (`0x20006804`, `0x20006808`) with one LDRD after opening the input device.
The previous C implementation used separate volatile loads. The shared C owner
now uses a four-byte-aligned, eight-byte union; a volatile 64-bit snapshot emits
one LDRD in the configured ARM build. Individual field stores remain four bytes.
The input cache producer and callback setter share this single storage owner.

The instruction-level comparison passes 12,800 paired board cases (25,600
executions), including late handle/callback changes, null methods, raw return
statuses and actual registry/event-forwarder execution. Every cold-open case
checks that both snapshot reads come from the same LDRD instruction, in native
and C. A separate-load negative control is rejected by that oracle. All 2,016
paired touch-device operation cases pass again. Another 64 C cache-producer
cases check zero initialization, lookup/cache behavior, four-byte input stores
and preservation of the neighboring callback word. The prior board comparison
also checks callback-setter accesses against native four-byte stores.

All 573 registered R1 units compile and compose without failures or duplicate
strong symbols; application/bootloader imports remain 197/34. `make sources-check`
passes. The unchanged canonical source plan produces a stock-identical hybrid
application (SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`),
with 3,827 source-built bytes and 642,333 unclassified binary-pull-through bytes.
This snapshot change has no new byte qualification.

This verifies instruction grouping for the tested compiler, not C11 atomicity,
bus-level atomicity or concurrent-writer correctness. Device/RTOS boundaries
remain modeled; reset placement, physical IRQ behavior and electrical/timing
behavior remain unverified. The native instruction evidence is retained in
`touch-board-c-sequencing-review.json`; current source and test hashes are in
`touch-ready-c-snapshot-review.json`. No G2 workflow gate advances.
