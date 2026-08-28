# G2 production raw-encoding source-ownership audit

Production overlay source ownership must describe maintainable source, not a
verbatim executable-byte transcription wrapped in inline assembly. This audit
therefore inventories every production-routed Apollo and bootloader source
that emits `.byte`, `.short`, `.hword`, or `.word` directives and assigns every
directive byte one explicit disposition.

The current production and public-component census is clean. Its only raw
directives are 16 legitimate literal-data bytes: the three typed constants in
`duration_delay.c` (12 bytes) and the typed thread-pointer address literal
(4 bytes). There are zero raw instruction bytes and zero `.byte` executable
transcript files in the public component tree.

Eight former bootloader MSPI files rendered 8,902 executable stock bytes as C
`.byte` directives. All thirteen routes across their eight exact spans were
removed, and the files themselves were deleted from the public tree. The
functional provider retains the authenticated official bytes at those spans;
the audit preserves only file sizes, SHA-256 digests, and boundary dispositions.
The 38 former raw branch/call bytes are now mnemonic source: explicit symbolic
relocations for the bootloader leaves and named placement-bound mnemonic calls
for the Apollo in-place copies. Both compiler profiles reproduce the reviewed
bytes exactly.

Artifacts:

- `tools/analyze_g2_production_raw_encoding_quality.py`
- `tools/manifests/g2-production-raw-encoding-quality.tsv`
- `tools/manifests/g2-production-raw-encoding-quality-summary.json`
- `tests/test_analyze_g2_production_raw_encoding_quality.py`

The audit is fail closed across both production routing and the complete public
component-source scope: a restored transcript path, any `.byte` body, any raw
instruction halfword, a changed routed span, or an unclassified directive byte
rejects the ledger. It performs no hardware, MMIO, reset, flashing, signing,
build, or production-file mutation. Hardware validation remains deferred by
project direction.
