# G2 FreeType 2.9.1 TrueType complete-map source admission

After the base, CFF, SFNT, PSHinter, PSAux, PSNames, smooth, and autofit
closures, the authenticated default-module table leaves only the TrueType
driver without a complete stock physical map.  The pre-existing TrueType
candidate is valuable but narrower: it closes a reachable driver/interpreter
graph of 248 functions / 38,828 bytes and proves a full-source link.  It does
not classify every byte in a stock module envelope.

## Complete stock closure

The driver class at `0x006DED34`, property service at `0x0078ECB4`,
multi-masters service at `0x007505A8`, and metrics-variation service at
`0x00767290` authenticate the public and indirect entry surfaces.  The pinned
candidate analyzer supplies its already-closed reachable graph.  Exact
FreeType 2.9.1 source order and the authenticated Ghidra corpus add the 17
previously omitted functions / 2,900 bytes.

| Category | Functions | Bytes |
|---|---:|---:|
| existing reachable graph | 248 | 38,828 |
| newly mapped service/source-order bodies | 17 | 2,900 |
| complete callable map | 265 | 41,728 |
| literal, pointer, data pools | 24 intervals | 474 |
| alignment padding | 1 interval | 2 |
| unresolved callable / unclassified physical | 0 | 0 |

The exact envelope is `0x005EF0B0..0x005F958C` (42,204 bytes).  It begins at
the property-service setter and ends after `tt_face_get_device_metrics` plus
two alignment bytes.  The next Ghidra body at `0x005F958C` is separately
bounded and outside the TrueType source order.  The analyzer rejects input,
table, source, body, gap, overlap, and complement drift.

## Source admission and bounds

The unmodified FreeType 2.9.1 `src/truetype/truetype.c` single-object unit
is admitted under the FreeType Project License.  Its authenticated inventory
contains 18 `.c`/`.h` files / 739,559 bytes.  A focused gate compiles it for
Cortex-M55 Thumb hard-float, freestanding C11, optimization enabled, and
warnings as errors.  The documented `-Wno-cast-function-type-mismatch`
compatibility exception matches the existing full FreeType candidate gate.

This is not an original-IAR compiler-byte identity claim.  No stock callsite,
relocation, target placement, production-image route, external font payload,
stack/WCET measurement, or authorized hardware rendering result is added.

```sh
python3 g2/tools/analyze_g2_freetype_truetype_function_map.py --pretty
python3 g2/tools/analyze_g2_freetype_truetype_source_admission.py --check-manifest
python3 -m unittest g2.tests.test_freetype_truetype_map_source_admission
```
