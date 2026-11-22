# G2 binary-slice audit (2026-10-26)

This is a historical snapshot. The 2026-11-11 Apollo source audit found 212
address-looking integer tokens across 29 first-party C/header files after
symbolic RAM relocations and removal of a duplicate initialized-data tail.
Those tokens include packed descriptors and bit masks; the count is not
directly comparable to the literal-use counts below, and it does not prove
all pointer uses are resolved. See
[`apollo-ram-literal-source-audit-20261111.json`](../evidence/apollo-ram-literal-source-audit-20261111.json).

Question: is each g2 component plain compilable C, or does it depend on slicing the stock image?

Method: grep for `.incbin`, `-I binary` and `.bin` INCLUDEs; byte-overlap of each final ELF against the stock 2.2.6.10 blobs (32-byte windows, /tmp/overlap.py, attributed per source with /tmp/bysrc.py); asm-transcription share of FUNC bytes (/tmp/asmshare.py).

**Finding:** no target links stock bytes at build time. There are no `.incbin` or binary INCLUDEs in `g2/src`. The tools/build `source_providers`/cut path writes provider .bin files only for the byte-matching flow. The compose + link-final flow that produces our ELFs does not use it.

| Target | Classification | Stock-matching bytes | Asm-transcribed FUNC bytes | Notes |
|---|---|---|---|---|
| apollo-main | C + data tables | 821 KB in runs ≥64 B (code ≈0.8 KB; data ≈795 KB) | 0.4% (8.7 KB) | Data is mostly assets copied from the OTA, with provenance headers (below). ~235 KB matches upstream library tables (FreeType adobe glyph list, LC3, lvgl montserrat, nrf battery model) plus log strings; 26 KB more is unsymbolized log text. `g2c_gnu_init.c` `.word` lines are linker-symbol tables (fine). |
| bootloader | C (+34 .S, 40 KB) | 2.2 KB in runs ≥256 B; 106 B code | 0.5% | gpio descriptors/names |
| em9305 | **C with heavy inline asm** | 1.7 KB in runs ≥256 B; 12 KB code | **29.5% (61,860 / 209,364 B)** | 489 of 622 files contain `__asm__`, ~42k asm lines; top-level bodies transcribed from disassembly (e.g. `init_native_child_322630.c`). Compilable, but not idiomatic C. Biggest remaining "reduce to C" item. |
| codec-a | C | 5.3 KB; 3 KB code | 2.4% | uart stage1 init 1352 B |
| codec-b | C | 3.4 KB; 1.1 KB code | 0% | FFT tables |
| touch | C + 1 stock-bytes file | 1.3 KB; 147 B code | 0% | `touch/reset-data/touch_stock_reset_gaps.c` is generated from the stock image by `.waves/w14/touch_gen_ram.py`. It is the only STOCK-BYTES file. touch_i2c_config is 433 B. |

## apollo-main asset files (copied from ota_s200_firmware_ota.bin, VA = file offset + 0x437fe0)
| File | Source size | Matched |
|---|---|---|
| ui/S5-ui-b-data/navigation_image_assets_data.c | 1.25 MB | 187 KB |
| onboarding_image_assets_data.c | 314 KB | 45 KB |
| drivers/display/legal-regulatory/legal_regulatory_assets.c | 270 KB | 40 KB |
| ui/S4-ui-a-data/ui_image_assets_data.c | 279 KB | 35 KB |
| watchface_image_assets_data.c | – | 28 KB |
| notify_image_assets_data.c | – | 24 KB |
| app/locale-data/display_locale_data_20001588.c | 345 KB | 14.5 KB |
| even_ai_image_assets_data.c | – | 11 KB |
| ui/S6-fonts-residual-data/rom_fonts_data.c | 229 KB | 9.7 KB |
| app_image_assets_data.c | – | 8 KB |
| terminal/conversate asset files | – | small |

These assets are legitimate data with provenance, but they are Even Realities' proprietary assets. Redistributing them is a licensing question, not a technical one.

## Hidden stock-layout dependency (found by the simulator; see sim-test-report.md)
apollo-main is "C" but still carries stock **addresses**:
- ~1,905 literal stock SRAM addresses (855 distinct, 544 files). 478 of those addresses are also named C objects (972 uses), so code reaches the same cell by symbol in one place and by literal in another. Our linker places the symbols elsewhere.
- 278 `(uintptr_t)0x4xxxxx..0x7xxxxx` stock flash literals (strings or tables at stock addresses), mostly on error/log paths.
- Data tables that held stock code pointers as raw bytes. 8 cells have been fixed so far; the remaining .data scan is clean.

Until these are fixed, the image is not layout-independent C.

Data: /tmp/absram.json (named cells with literal uses), /tmp/absram_all.json (all literal uses).
