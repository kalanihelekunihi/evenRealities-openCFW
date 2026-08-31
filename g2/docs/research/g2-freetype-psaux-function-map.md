# G2 FreeType 2.9.1 PSAux function map

This closure expands the earlier 57-function retained census into the complete
stock PSAux callable and physical envelope.  It does not route replacement
code or claim original-compiler byte identity.

## Stock scope and correction

The module class at `0x00758A18` names `psaux` and points to the service at
`0x00741F70`.  Its parser, table, Type-1/CFF builder, decoder, cmap, AFM, and
CF2 callback tables authenticate 65 direct callback bodies.  Single-object
source order and the closed Ghidra mappings extend the physical envelope from
`0x005CF8E4` through `0x005D70A4` (30,656 bytes).

The prior 57-function / 7,114-byte census was incomplete rather than a module
boundary.  This analyzer adds 116 already-authenticated Ghidra/source bodies /
21,120 bytes and recovers 26 omitted bodies / 1,516 bytes.  It also corrects
three shifted early identities using code semantics and the stock table:
`0x005D0414` is `PS_Conv_ASCIIHexDecode`, `0x005D049E` is
`PS_Conv_EexecDecode`, and table target `0x005D04E8` is `ps_table_new`.

| Confidence | Functions | Bytes |
| --- | ---: | ---: |
| Exact | 0 | 0 |
| High | 65 | 7,020 |
| Medium | 134 | 22,730 |
| Mapped PSAux total | 199 | 29,750 |
| Unresolved PSAux callable code | 0 | 0 |

Two interleaved Cordio callables at `0x005D2BAE` and `0x005D2E0C` account for
762 bytes and remain explicitly foreign.  The remaining 144 bytes are twelve
pinned intervals of literals, a callback table, strings, and alignment.  All
30,656 physical bytes are therefore classified with no callable or physical
residue.

## Source admission boundary

The isolated `components/shared/freetype_psaux` component selects the
unmodified FreeType 2.9.1 `src/psaux/psaux.c` single-object translation unit.
Its complete 37-file / 625,815-byte source inventory is pinned, including the
Adobe CF2 notices and patent grant, and the translation unit compiles
warning-clean for Cortex-M55 Thumb hard-float.

No stock callsite, overlay, relocation, or placement is changed.  Pinned
IAR-compatible generation, an authenticated PostScript font payload,
stack/WCET qualification, and authorized hardware rendering remain release
gates; no hardware behavior is claimed.

Run the focused checks with:

```sh
python3 g2/tools/analyze_g2_freetype_psaux_function_map.py --pretty
python3 -m unittest g2.tests.test_analyze_g2_freetype_psaux_function_map
python3 g2/tools/analyze_g2_freetype_psaux_source_admission.py --check-manifest
python3 -m unittest g2.tests.test_freetype_psaux_source_admission
```
