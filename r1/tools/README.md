# R1 tools

| Tool | Purpose |
| --- | --- |
| `export_r1_decompilation.py` | headless Ghidra whole-image export of the application and bootloader into `research/decompilation/`, plus the `*.bytes.inc` arrays for the rebuild oracle |
| `verify_r1_decompilation.py` | fail-closed structural check of the corpus (`--corpus-only`) and the exact-byte oracle |
| `audit_r1_ghidra_explicit_entries.py` | census of explicitly seeded function entries (`docs/reference/GHIDRA-EXPLICIT-ENTRY-CENSUS.json`) |
| `run_r1_bootloader_decompilation.sh` | reproduce the named bootloader export in `research/bootloader-reconstruction/generated/` |
| `run_r1_bootloader_source_correlation.sh`, `run_r1_application_source_correlation.sh` | BSim correlation against symbol-bearing SDK reference builds |
| `generate_r1_model_data.py` | regenerate the model-constant tables in `reconstructed/model_data/` from the official application |
| `ghidra_scripts/` | Ghidra Java scripts used by the drivers above |

The headless drivers find Ghidra through `GHIDRA_INSTALL_DIR` (or
`R1_GHIDRA_HEADLESS`) and Java 21 through `R1_JAVA_RUNTIME`. Before doing
anything, they check the input image's SHA-256 against
[`../blobs/official/2.2.6.0009/PROVENANCE.md`](../blobs/official/2.2.6.0009/PROVENANCE.md).
Install the tools with [`../../tools/bootstrap/`](../../tools/bootstrap/README.md).
