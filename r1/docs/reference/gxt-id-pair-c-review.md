# Exact GXT310 chip-ID pair read in C

`runtime/native_gxt310_id_pair.c` supplies missing stock `0x510d8`. It acquires
the bus, enables the sensor pair, calls `osDelay(80)`, writes count byte 2,
reads the channel-0 ID into byte 1 and channel-2 ID into byte 2, then disables
the pair and releases the bus. Each ID is truncated to its low byte. Provider
errors do not change the sequence. Empty R4 constraints retain the output
pointer at each provider boundary; every executed operation is C.

The final release remains a native tail call: the root restores the caller's
R4/LR and eight-byte frame before branching. The release provider sees the
original caller registers, SP and LR, and its raw R0 is observed unchanged
at return. The C API itself is void.

`tools/build/qualify_sources.py` selects all 46 native bytes. The product C
routine executes the already-qualified C chip-ID wrappers, which pass raw
address words `0x90`/`0x94` to the final chip-ID provider. The test passes
36,864 paired stock/C cases over every ID byte, raw high-word results, output
alignments, interrupt-mask states and provider errors. Controlled callbacks
mutate pending, previous and final output bytes to verify exact store order
and cleanup visibility. Tests compare all three ordered byte stores, provider
traces, live R4–R11, saved-frame accesses, final output/guards, SP/masks and
observed final R0. Wrong count, channel order, delay and missing-release
variants are rejected.

All 584 R1 units compile. All 583 prior objects and 164/34 import sets remain
unchanged. Only this 46-byte region is added to the source plan; the existing
chip-ID wrappers are not duplicated. The canonical hybrid now contains
4,201 source-built bytes, 641,959 fallback bytes and 248 resource bytes.
Application SHA-256 remains
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

Bus/mode/delay and final chip-ID providers are modeled. Caller-clobbered
registers/flags except observed final R0, electrical response, actual timing,
arbitrary aliases/faults/concurrency and complete source-only rebuilding
remain unproven. Reproducible probes, REA evidence, qualification and audit
are under `build/goal-r1-gxt-id-pair-c`; durable results are in the adjacent JSON.
