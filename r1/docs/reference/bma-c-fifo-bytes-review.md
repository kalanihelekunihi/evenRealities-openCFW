# Bosch bounded FIFO byte reader in C

`r1_bma_fifo_read_bytes` now uses C, leaving `native_bma_fifo.c` free of
inline assembly. Stock entry `0x544c8` checks the device first, rejects a
null output or zero request with `0xffffffff`, and chooses register `0xa6`
for SPI or `0x26` otherwise. It queries FIFO length into a zero-initialized
halfword and maps a length-query failure to `0xfffffffe`. An empty FIFO
returns zero. A nonempty transfer is capped at the caller's requested
length before loading the bus callback and handle from the live context.

The read result's low byte is stored at context offset 9. A failed bus
read returns `0xfffffffe`; a successful read reloads and sign-extends the
length halfword. REA/Ghidra independently recovers those branches and
accesses. A const volatile view of the ordinary length local preserves
the reload after callbacks, including a callback using the scratch pointer
retained by the length provider. The register choice remains captured
before the length query, while callback and handle loads occur afterward.

Stock/source comparison passes 1,092 scenarios covering zero, capped and
large lengths, SPI/I2C selection, empty/partially written length results,
errors, invalid inputs, callback/handle/interface changes, and late scratch
changes through the retained pointer. Ordered public context reads/writes,
callback traces, arguments, status-byte stores, signed returns,
callee-saved registers, stack restoration and interrupt masks match.
Bus statuses use canonical signed-byte callback ABI values. Lengths above
the normal getter's 14-bit range exercise the reader boundary with a mock.

The C byte reader is 114 bytes versus 108 stock bytes. The length query
and logging helper retain their previous instruction bodies. The compiler
also regenerated the outer FIFO wrapper after seeing the C callee. Its
full-width result is read through a const volatile view before the signed
test and division, preserving the native outer return contract rather
than relying on inferred callee ranges. The wrapper's complete 2,168-case
stock comparison passes against this same build, including full-width
mock read results outside the byte reader's usual return range.

The reader's native callback frame is SP-32 and C uses SP-24; both preserve
eight-byte alignment. The native scratch's saved upper bytes are private;
only the initialized low halfword is owned here. Checker, length and bus
calls are mocked. Physical transfers, timing, complete fault state, final
linking and byte identity remain unverified.

All 562 R1 units compile without failures or duplicate strong symbols in
`build/sources-goal-r1-bma-fifo-bytes-verified/report.json`. Normal import
sets remain 227 application and 34 bootloader. No source-plan selection or
G2 workflow gate changed. [Machine-readable evidence](bma-c-fifo-bytes-review.json)
binds source/build/native hashes, REA results and ignored probes under
`build/goal-r1-bma-fifo-bytes/`.
