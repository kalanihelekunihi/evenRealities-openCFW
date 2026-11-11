# R1 GoMore eleven-byte record table in C, 2026-11-10

The locked `r1-2.2.6.0009/application.bin` has SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
Its native `0x684b4` entry copies eleven bytes from a table whose stock base
is `0xb1bde`. The application caller at `native_gomore_consume.c` supplies a
zero-extended byte index, so its reachable index set is 0..255.

The table already lives inside the C `r1_model_data_words` array: its offset
from `R1_MODEL_DATA_STOCK_BASE` is 506 bytes. A source-versus-locked-image
comparison verified the 1,760 table bytes reachable by all 256 caller
indices. The new native ABI adapter in
`r1/src/application/runtime/native_gomore_table_record11.c` calls the
existing C record selector against that source-owned model region; it does
not duplicate the table or read firmware bytes at build or runtime.

An ignored ARM Cortex-M4 Unicorn probe under
`build/r1-record11-probe-20261110/` linked the actual compiled adapter,
primitive and model-data units. It compared the complete 11-byte output and
five trailing guard bytes against stock execution and a direct table oracle
for all 256 caller indices. All matched. Negative indices are outside this
caller's byte-index contract and were not qualified.

The fresh `build/r1-gomore-record11-c-20261110/report.json` compiles 957/957
R1 units without duplicate strong symbols. Its strict bootloader link
passes. The strict application receipt at
`build/r1-gomore-record11-c-20261110/app-link/report.json` still has 45
unresolved references and a 28,088-byte full flash overflow. This function
check does not establish full application linkage, byte identity, or board
behavior.
