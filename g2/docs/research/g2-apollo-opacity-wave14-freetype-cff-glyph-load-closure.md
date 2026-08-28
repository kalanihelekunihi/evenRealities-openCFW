# G2 Apollo opacity Wave 14: FreeType CFF glyph-load closure

Status date: 2026-08-28  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Mode: software-only, read-only

## Result

The largest post-Wave-13 residual root, `0x005AC66E` / 1,684 bytes, is
FreeType 2.9.1 `cff_slot_load`. Its complete residual-only static closure adds
four exact source functions:

- `ft_synthesize_vertical_metrics` at `0x00526A02`;
- `cff_get_glyph_data` at `0x005AC5F0`;
- `cff_free_glyph_data` at `0x005AC634`;
- `cff_fd_select_get` at `0x005ADDB8`.

Together the five functions close **2,006 official opaque bytes** under the
FreeType Project License. The authoritative residual changes from **1,297
functions / 136,482 bytes** to **1,292 functions / 134,476 bytes**. The next
largest root is `0x0051B8F0` / 1,668 bytes.

No aggregate, package, overlay, Makefile, or production artifact changed.

## Evidence and graph closure

The root matches `cffgload.c` field-for-field: CID-to-GID mapping, embedded
bitmap metrics, FDSelect subfont scaling, decoder initialization and retry on
`Glyph_Too_Big`, incremental metrics override, outline metrics, transforms,
and final scaling. The helper bodies reproduce their source branches exactly.

All nine static terminal functions were admitted by Wave 8 or Wave 11. Four
direct data cells are exact: the FreeType bitmap and outline FourCC values and
Thumb pointers to `cff_free_glyph_data` and `cff_get_glyph_data`. All five
selected function ranges are contiguous.

Six source-authenticated indirect interface classes are kept explicit:
registered SFNT metric/bitmap hooks, PSAux decoder/builder hooks, and optional
client incremental-data/metrics hooks. The optional interfaces are typed
external boundaries; this record does not invent a client implementation or
its license.

## Production admission

Production routing remains excluded. Source identity does not prove the exact
feature macros, object ABI, or dual-profile Cortex-M55 code generation,
relocation, link order, and placement. No hardware action was performed.

## Reproduction

```sh
python3 g2/tools/analyze_g2_apollo_opacity_wave14.py --pretty
python3 -m unittest g2.tests.test_analyze_g2_apollo_opacity_wave14
```
