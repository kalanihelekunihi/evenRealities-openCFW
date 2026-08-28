# Apollo opacity wave 11: FreeType CFF source closure

Wave 11 starts at the authoritative post-Wave-10 residual maximum, `0x005AF88C` / 1,912 bytes. Static closure through still-unclassified callees reaches 43 functions across depths zero through five and accounts for 10,098 official opaque bytes.

## Positive identity

`0x005AF88C` is `cff_face_init` from the authenticated FreeType 2.9.1 `VER-2-9-1` snapshot. The body contains the diagnostic module/service strings `postscript-cmaps`, `psaux`, and `cff-load`; the style strings `Regular`, `Bold`, and `Black`; and the same SFNT/CFF2 initialization, matrix scaling, font-name, charmap, and face-flag topology as `src/cff/cffobjs.c`.

The closure then follows exact FreeType structures into:

- `cffparse.c`: parser setup/teardown, integer/real/fixed decoding, and DICT dispatch;
- `cffload.c`: INDEX handling, charset/encoding, variation store, private/subfont dictionaries, and full font load;
- `cffobjs.c`: name duplication, subset/style normalization, and face initialization;
- base modules: fixed math, scaled matrix/vector transforms, stream reads, and service lookup.

Forty-two bodies / 10,056 bytes therefore have maintained source identities under the FreeType Project License. They are not relicensed as MIT. The snapshot files, provenance, and license remain checked in beneath `g2/third_party/freetype`.

The 42-byte body at `0x0044B610` is the exact three-argument `strncmp` shape used by `cff_face_init`, but the linked implementation is an IAR DLIB runtime body. Its proprietary maintained source, library model, and configuration are absent, so it remains an explicit SHA-pinned unavailable-provider boundary.

## Graph and data closure

All 43 selected function records contain one contiguous authenticated range: there are zero interior islands and no census-omitted function bytes. The terminal frontier has 23 targets and 78 distinct owner-to-target edges. Earlier typed/source-owned targets add zero Wave-11 bytes.

The decompiler exposes 34 distinct direct four-byte data cells. `shared_data.tsv` pins every cell, its consumer set, and its installed bytes. Eight diagnostic pointer targets are additionally dereferenced and checked as NUL-terminated strings. The 136 physical cell bytes are evidence, not extra function-envelope accounting.

Residual accounting changes deterministically:

| State | Functions | Official opaque bytes |
|---|---:|---:|
| Before Wave 11 | 1,352 | 152,498 |
| Wave 11 closure | 43 | 10,098 |
| After Wave 11 | 1,309 | 142,400 |

The next largest envelope is `0x004BFED6` / 1,902 bytes.

## Production admission

This wave is source-level, research-only admission. Exact upstream identity does not prove the shipped feature macros, ABI, IAR DLIB model, optimization/LTO choices, Cortex-M55 code generation, relocation, link order, or placement. Production routing remains excluded until both release/debug profiles have reviewed build receipts and byte/relocation-equivalent placement proof. No hardware action is performed by the analyzer or tests.
