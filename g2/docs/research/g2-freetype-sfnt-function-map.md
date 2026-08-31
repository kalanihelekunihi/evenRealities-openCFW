# G2 FreeType 2.9.1 SFNT function map

This closure selects the SFNT module as the largest authenticated remaining
FreeType mapping frontier and converts a bounded stock-image interval into a
fail-closed, function-level research map.  It does not create an overlay or
claim a maintained implementation is routed into the production image.

## Why SFNT

The authenticated closed source census and stock class tables rank the four
requested candidates as follows.

| Candidate | Closed-census source functions | Body bytes | Direct stock callbacks |
| --- | ---: | ---: | ---: |
| SFNT | 61 | 16,520 | 31 |
| PSAux | 57 | 7,114 | not used as a tie-breaker |
| Smooth | 0 | 0 | 7 unique callbacks across three renderer classes |
| Autofit | 0 | 0 | 3 module callbacks |

SFNT is largest by both retained source-attributed functions and bytes.  Its
module class at `0x0075A3F8` points to the 31-word interface at `0x0069CA14`,
and its name pointer resolves to the stock string `sfnt`.  The analyzer checks
these facts directly in the pinned G2 2.2.6.10 image.

## Evidence and confidence

The map covers `0x005DA1E8` through `0x005E1594` (29,612 bytes).  Evidence is
combined rather than inferred from address adjacency alone:

- the exact FreeType tag `VER-2-9-1`, peeled commit, source hashes, `sfnt.c`
  single-object include order, `SFNT_Interface` field count, and initializer
  slot order;
- the pinned official image, SFNT module class, readable module-name string,
  and all 31 Thumb interface pointers;
- 75 pinned Ghidra callable records totaling 21,238 body bytes, including
  body hashes and selected private ttsbit call-graph edges; and
- the earlier closed source census plus the separately authenticated
  `ttpost.c:load_post_names` record; and
- stock BDF service, all relevant 13-word cmap class records, the cmap-info
  service, two WOFF function literals, and the sbit loader table, together
  with a decoded Thumb `BL` edge from `tt_face_find_bdf_prop` to its private
  loader.

`high` requires a complete body plus a direct stock pointer or decoded call
anchor and exact 2.9.1 source order.  Interface rows have a source slot and
either a pinned Ghidra body or an adjacent single-object source boundary.
Private/source-census rows remain `medium` without equivalent stock anchors.
`exact` remains empty: no original compiler-byte identity proof is available.

| Result | Functions | Bytes |
| --- | ---: | ---: |
| Exact | 0 | 0 |
| High | 75 | 13,164 |
| Medium | 61 | 16,094 |
| Mapped total | 136 | 29,258 |
| Named unresolved candidates | 0 | 0 |

To avoid inflating progress with prior work, the net addition beyond the
closed census is 75 functions / 12,738 bytes.  Ten prior census rows / 3,444
bytes are promoted to high confidence, while 51 / 13,076 remain medium.

## Recovered callable records

The previously named records are now bounded and mapped:

| Symbol | Body | Bytes | Independent stock anchor |
| --- | --- | ---: | --- |
| `tt_face_load_bdf_props` | `0x005DC290`–`0x005DC38A` | 250 | decoded `BL` at `0x005DC3E4` |
| `tt_face_find_bdf_prop` | `0x005DC3C4`–`0x005DC53C` | 376 | service pointer at `0x0078E6B8` |
| `tt_sbit_decoder_load_bit_aligned` | `0x005E0A70`–`0x005E0C48` | 472 | middle entry of the loader table at `0x005E1484` |

The BDF interval also revealed a 58-byte aligned tag/literal pool and the
six-byte `tt_cmap_init` body at `0x005DC53C`–`0x005DC542`.  Five stock cmap
class records point to that callback, so it is mapped as an additional high
record rather than hidden inside BDF residue.

## Table-pointer frontier

The 2,978-byte callable-code envelope contained 38 pointer records.  The
analyzer now resolves all 38 to 38 distinct complete bodies (2,374 bytes).
For every row it pins the pointer location and Thumb target, exact body bounds
and SHA-256, exact 2.9.1 definition and source order, and, for cmap records,
the class format plus typed macro slot.  The complete per-pointer ledger is in
the analyzer output; this is its exhaustive symbol summary.

| Dispatch owner | Mapped callbacks | Functions | Bytes |
| --- | --- | ---: | ---: |
| SFNT BDF service | `sfnt_get_charset_id` | 1 | 72 |
| WOFF function literals | `sfnt_stream_close`, `compare_offsets` | 2 | 60 |
| Cmap format 0 | `tt_cmap0_char_index`, `tt_cmap0_char_next`, `tt_cmap0_get_info` | 3 | 76 |
| Cmap format 2 | `tt_cmap2_char_index`, `tt_cmap2_char_next`, `tt_cmap2_get_info` | 3 | 408 |
| Cmap format 4 | `tt_cmap4_init`, `tt_cmap4_char_next`, `tt_cmap4_get_info` | 3 | 130 |
| Cmap format 6 | `tt_cmap6_validate`, `tt_cmap6_char_index`, `tt_cmap6_char_next`, `tt_cmap6_get_info` | 4 | 350 |
| Cmap format 8 | `tt_cmap8_get_info` | 1 | 34 |
| Cmap format 10 | `tt_cmap10_validate`, `tt_cmap10_char_index`, `tt_cmap10_char_next`, `tt_cmap10_get_info` | 4 | 450 |
| Cmap format 12 | `tt_cmap12_init`, `tt_cmap12_char_index`, `tt_cmap12_char_next`, `tt_cmap12_get_info` | 4 | 134 |
| Cmap format 13 | `tt_cmap13_init`, `tt_cmap13_char_index`, `tt_cmap13_char_next`, `tt_cmap13_get_info` | 4 | 134 |
| Cmap format 14 | `tt_cmap14_done`, `tt_cmap14_init`, `tt_cmap14_char_index`, `tt_cmap14_char_next`, `tt_cmap14_get_info`, `tt_cmap14_char_var_isdefault`, `tt_cmap14_variants`, `tt_cmap14_char_variants` | 8 | 504 |
| TT cmap-info service | `tt_get_cmap_info` | 1 | 22 |
| **Total** |  | **38** | **2,374** |

There are no duplicate targets among these 38 pointer records and thus no
ambiguous pointer aliases.  `tt_cmap12_init` and `tt_cmap13_init` have
identical body hashes but distinct entry addresses and distinct typed class
slots; the analyzer records this explicitly as byte identity, not aliasing.
Outside this frontier, the already mapped `tt_cmap_init` is deliberately
shared by five cmap class init slots, and those five references are also
listed explicitly.

## Private cmap helper closure

The last two callable envelopes are now independently resolved:

| Symbol | Body | Bytes | Public wrapper calls | Private next call |
| --- | --- | ---: | --- | --- |
| `tt_cmap12_char_map_binary` | `0x005DDD38`–`0x005DDE72` | 314 | `0x005DDE78`, `0x005DDEAE` | `0x005DDE58` → `tt_cmap12_next` |
| `tt_cmap13_char_map_binary` | `0x005DE0CA`–`0x005DE1EC` | 290 | `0x005DE1F2`, `0x005DE228` | `0x005DE1D2` → `tt_cmap13_next` |

Both bodies begin with a complete eight-register Thumb prologue and terminate
at an eight-register `pop ... pc`; their full SHA-256 hashes are pinned.  In
each format, `char_index` calls the candidate with `next=0`, while the fallback
path in `char_next` calls it with `next=1`.  Reviewed Thumb behavior also
matches the 2.9.1 source: both decode big-endian 12-byte group records and run
the same binary search/state update, while format 12 computes
`start_id + (char_code - start)` with overflow rejection and format 13 uses the
group's constant glyph id.  These call edges, boundaries, source neighborhood,
and format-specific semantic differences are independent corroboration, so
both records are promoted to high confidence.

## Physical classification and remaining opacity

The former 3,274 unparsed bytes are fully typed at the physical level:

| Physical category | Bytes |
| --- | ---: |
| Recovered table-pointer callback bodies | 2,374 |
| Recovered private cmap helper bodies | 604 |
| Literal/constant pools | 272 |
| Function-pointer data | 12 |
| Alignment padding | 12 |
| Unclassified | 0 |

Including the newly exposed BDF tag pool, the mapped-function complement is
10 intervals / 354 bytes: 328 literal/constants, 12 function pointers, and 14
padding.  No callable-code bytes remain in the physical complement and all 136
bounded function records have source identities.  `exact` nevertheless stays
empty because source/behavior identity is not original-compiler byte identity.

## Routing and validation boundary

The stock SFNT interface is an authenticated dispatch surface, not a route for
new maintained code.  Neither the core overlay nor its builder references this
map, and no placement, relocation, callsite rewrite, ABI reproduction, target
budget, or live-hardware validation has been established.  The output is a
mapping closure only.

The completed callable census does permit a bounded community-source
admission.  `components/shared/freetype_sfnt` selects the unmodified 2.9.1
`src/sfnt/sfnt.c` single-object translation unit, pins the complete 25-file /
413,337-byte SFNT source inventory, and compiles that translation unit for
Cortex-M55 Thumb hard-float.  One narrowly documented Clang compatibility
exception suppresses the historical format-14 `FT_Int`/`FT_Bool` callback-cast
diagnostic; all other selected warnings remain errors.  The admission still
does not establish stock placement, original IAR byte identity, or hardware
rendering behavior.

Run the deterministic analyzer and focused tests with:

```sh
python3 g2/tools/analyze_g2_freetype_sfnt_function_map.py --pretty
python3 -m unittest g2.tests.test_analyze_g2_freetype_sfnt_function_map
python3 g2/tools/analyze_g2_freetype_sfnt_source_admission.py --check-manifest
python3 -m unittest g2.tests.test_freetype_sfnt_source_admission
```

The checked summary is
`g2/tools/manifests/g2-freetype-sfnt-function-map.json`; the analyzer emits the
complete per-function and per-residual records.
