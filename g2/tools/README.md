# G2 tools

| Tool | Purpose |
| --- | --- |
| `open_cfw.py` | EVENOTA packer and validator: TOC, 128-byte component headers, CRC-32C variants, main/case/touch wrappers. `make reference` repacks the official payloads byte-identically |
| `analyze_g2_codec_fwpk_segments.py`, `analyze_g2_codec_stage2_sections.py` | GX8002 FWPK segments and the stage-2 BINH A/B layout (hash-pinned by `workflow/tools/validate_campaign.py`) |
| `analyze_em9305_record_package.py` (+ `../components/em9305/source_image/record_package.py`) | EM9305 record-package inventory and codec |
| `disassemble_em9305_arcompact.py` | ARCompact/ARCv2 disassembly helper for the EM9305 |
| `analyze_g2_touch_identity.py` | touch FWPK wrapper, PSoC 4000T vector and identity checks |
| `analyze_g2_box_function_map.py`, `extract_g2_case_final_decomp.py`, `merge_case_backup.py` | case EVEN wrapper, function map, decompilation extraction, device-backup merge |
| `harvest_ghidra_decomp.py`, `generate_apollo_ghidra_chunks.py`, `run_apollo_ghidra_chunk_batch.sh`, `run_ghidra_shard_batch.sh`, `benchmark_headless_ghidra.sh` | headless Ghidra export pipeline |
| `ghidra_scripts/` | Ghidra Java scripts: vector-table seeding, whole-program and ranged decompilation dumps, ARCompact long-immediate discovery, C-SKY checks |
| `thumb_branch_audit.py` | Thumb branch/veneer audit |
| `analyze_apollo_embedded_source_paths.py`, `recover_apollo_embedded_source_paths.py` | recover vendor source paths embedded in the Apollo image (naming seeds) |
| `consolidate_symbol_seeds.py` | how `../symbols/` was generated. Its inputs are at commit `1a865ec3`; run it against a worktree of that commit to regenerate |
| `verify_research_corpus.py` | authenticate `../research/` |
| `assetgen_*.py` | LVGL image/font, nanopb descriptor and string-pool generators for the C stage |
| `gxdnn_command_emitter.py`, `gxdnn_quantize.py` | GX8002 gxDNN NPU command and quantization tools |
| `build_g2_csky_macos.py`, `toolchain-patches/` | pinned C-SKY toolchain build recipe |

Tool installation is in [`../../tools/bootstrap/`](../../tools/bootstrap/README.md).
Tool selection is explained in [`../../docs/tooling.md`](../../docs/tooling.md).
