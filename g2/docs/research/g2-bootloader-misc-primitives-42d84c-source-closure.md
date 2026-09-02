# G2 bootloader miscellaneous primitive source closure

Five authenticated post-MSPI primitives are now produced by reviewable
MIT-licensed C in `runtime_misc_primitives_42d84c.c`: stream-mode selection at
`0x0042D84C`, runtime-context retrieval at `0x0042D88A`, Cortex-M vector
handoff at `0x0042DC90`, table-driven CRC32 at `0x0042E1EC`, and terminal-mode
control at `0x0042E514`.

Both reviewed compiler profiles reproduce all 170 executable bytes exactly
without raw encoding directives or relocations. Host tests cover every
stream-mode branch, standard and seeded CRC32, vector-state transfer, context
identity, and terminal-mode selection. Actual VTOR/MSP branch handoff and
terminal MMIO behavior are blocked by unavailable physical evidence.
