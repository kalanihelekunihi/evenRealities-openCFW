# BMA456 identity probe in C

`r1_bma456w_identity_probe` in `native_bma_reads.c` now uses ordinary C in
place of its naked assembly body. Stock entry `0x53b2c` and REA/Ghidra show
that it initializes the interface only when the context's read callback is
null, reads register zero into a zero-initialized byte, and returns that byte
only when the read succeeds. Initialization or read failure returns zero
after the corresponding error logging.

The replacement preserves separate log-mode queries and their short-circuit
order: bit zero in the first result enables ring logging; otherwise a second
query tests bit two. A subsequent query tests bit one for SDK logging.
It preserves the ring header `0x04400000`, SDK header `0x001c0001`, string
contents, duplicate ring-string arguments and full 32-bit error value.
The Bosch header pins the read callback field at offset 36.

The stock/source execution comparison passes 2,562 scenarios. These include
all 512 triples of three-bit log-mode values on three failure routes,
random changing full-width mode/error values, both initial callback states,
all 256 chip-ID values with and without initialization, and successful reads
that leave the output byte untouched. Probes compare ordered context reads
and callback traces, return values, callee-saved registers, restored stack
and interrupt masks. Callback entries require eight-byte stack alignment
and clobber caller-saved registers. The bus, initializer and logging calls
are modeled; this does not prove physical sensor operation.

The C body is 162 bytes versus the stock 160-byte instruction body. The
other three functions in this source retain their previous compiled bodies.
Private scratch upper bytes, private stack layout, timing and complete fault
state are outside this comparison. The direct-read function's separate
128-byte scratch boundary still retains assembly.

All 562 R1 units compile without failures or duplicate strong symbols in
`build/sources-goal-r1-bma-identity-verified/report.json`. Both normal
relocatable compositions retain their previous import sets: 227 application
and 34 bootloader imports. No source-plan selection, workflow gate, final
firmware linking or whole-image byte identity is claimed.

[Machine-readable evidence](bma-c-identity-review.json) binds the source,
manifest, build report, stock span, REA evidence and ignored probe artifacts
under `build/goal-r1-bma-identity/`.
