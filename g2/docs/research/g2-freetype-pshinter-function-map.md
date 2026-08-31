# G2 FreeType 2.9.1 PSHinter function map

This closure selects PSHinter as the largest authenticated remaining FreeType
module and partitions its complete stock callable envelope.  It does not route
replacement code or claim original-compiler byte identity.

## Selection

The pinned retained-source census gives the following ranking after the base,
CFF, TrueType, and SFNT work already admitted elsewhere.

| Candidate | Source-backed functions | Body bytes | Direct stock callbacks |
| --- | ---: | ---: | ---: |
| PSHinter | 67 | 8,480 | 18 |
| PSAux | 57 | 7,114 | not used as a tie-breaker |
| PSNames | 7 | 1,010 | not used as a tie-breaker |
| Smooth rasterizers | 0 | 0 | 7 unique renderer callbacks |

The PSHinter total deliberately excludes six `psmodule.c` functions belonging
to the adjacent PSNames module.  PSHinter is largest by both retained function
count and bytes.

## Stock anchors and map

The official image identifies `pshinter` through the module class at
`0x00758A3C`, the string at `0x0078BCD8`, the three-entry public interface at
`0x0078BCE4`, and the 13-entry globals/Type-1/Type-2 function table at
`0x005D948C`.  The bounded callable envelope is `0x005D70A4`–`0x005D94C0`
(9,244 bytes).

The closed census and pinned Ghidra relation supply 67 functions / 8,480
bytes.  Six of those bodies / 846 bytes are independently promoted by direct
dispatch pointers.  Twelve callback bodies / 708 bytes omitted from the
harvested callable relation are recovered from exact pointer targets, complete
Thumb boundaries and body hashes, source definitions, and single-object source
order:

- `psh_globals_new`;
- `ps_hinter_done`, `ps_hinter_init`, and all three `pshinter_get_*_funcs`
  accessors;
- `ps_hints_t1reset`, `ps_hints_close`, `t1_hints_open`, and
  `t1_hints_stem`; and
- `t2_hints_open` and `t2_hints_stems`.

| Confidence | Functions | Bytes |
| --- | ---: | ---: |
| Exact | 0 | 0 |
| High | 18 | 1,554 |
| Medium | 61 | 7,634 |
| Mapped total | 79 | 9,188 |
| Unresolved callable code | 0 | 0 |

The only physical complement is a four-byte literal at
`0x005D8AB8`–`0x005D8ABC` and the 52-byte authenticated function-pointer table
at `0x005D948C`–`0x005D94C0`.  Thus all 9,244 envelope bytes are classified,
with no callable or unclassified residue.

## Source-admission and release boundary

The isolated `components/shared/freetype_pshinter` component selects the
unmodified FreeType 2.9.1 `src/pshinter/pshinter.c` single-object translation
unit.  Its complete 12-file / 147,127-byte source inventory is pinned and the
translation unit compiles warning-clean for Cortex-M55 Thumb hard-float.

This is community-source admission only.  No stock callsite, overlay,
relocation, or placement is changed.  Pinned IAR-compatible code generation,
font payloads, stack/WCET qualification, and authorized hardware rendering
remain external release gates; no hardware behavior is claimed.

Run the focused software checks with:

```sh
python3 g2/tools/analyze_g2_freetype_pshinter_function_map.py --pretty
python3 -m unittest g2.tests.test_analyze_g2_freetype_pshinter_function_map
python3 g2/tools/analyze_g2_freetype_pshinter_source_admission.py --check-manifest
python3 -m unittest g2.tests.test_freetype_pshinter_source_admission
```
