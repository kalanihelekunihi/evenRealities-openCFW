# G2 FreeType base-cluster source admission

This software-only tranche closes the inherited 83-function, 7,874-byte
base-module census. The ten named anchors, 17-function / 1,294-byte direct
tranche, and 56-function / 4,428-byte bounded indirect tranche are backed by three
independent bounds: exact official-image span hashes, distinctive stock
decompiler shapes, and definitions in the hash-authenticated FreeType 2.9.1
snapshot. The source remains under the FreeType Project License.

`analyze_base_cluster_candidate.py` performs the complete fail-closed check.
Source admission means that the authenticated upstream implementation is an
attributable clean replacement; it does not claim compiler byte identity.

## Newly admitted direct cluster

| Stock entry | Upstream definition | Source |
|---:|---|---|
| `0x0052502A` | `FT_Stream_Free` | `ftobjs.c` |
| `0x00525386` | `FT_New_GlyphSlot` | `ftobjs.c` |
| `0x005253F4` | `FT_Done_GlyphSlot` | `ftobjs.c` |
| `0x0052586E` | `destroy_charmaps` | `ftobjs.c` |
| `0x0052594A` | `find_unicode_charmap` | `ftobjs.c` |
| `0x00525ADE` | `FT_New_Memory_Face` | `ftobjs.c` |
| `0x00525B6E` | `open_face_from_buffer` | `ftobjs.c` |
| `0x0052687E` | `FT_New_Size` | `ftobjs.c` |
| `0x005270D2` | `ft_add_renderer` | `ftobjs.c` |
| `0x00527466` | `FT_Remove_Module` | `ftobjs.c` |
| `0x005288E0` | `FT_Stream_Seek` | `ftstream.c` |
| `0x00529148` | `ft_mem_alloc` | `ftutil.c` |
| `0x00529256` | `ft_mem_free` | `ftutil.c` |
| `0x005292E6` | `FT_List_Find` | `ftutil.c` |
| `0x00529304` | `FT_List_Add` | `ftutil.c` |
| `0x00529324` | `FT_List_Remove` | `ftutil.c` |
| `0x00529378` | `FT_List_Finalize` | `ftutil.c` |

The five formerly largest residuals are now identified as
`FT_GlyphLoader_CheckPoints`, `ft_lookup_PS_in_sfnt_stream`, `FT_CMap_New`,
`ft_glyphslot_clear`, and `FT_Render_Glyph_Internal`. Their 1,010 bytes match
upstream semantics without an Even-specific policy boundary.

The same evidence method closes the complete bounded glyph-loader and
glyph-slot helper chains surrounding those bodies: ten additional
`FT_GlyphLoader_*` definitions and five `ft_glyphslot_*` definitions account
for another 848 bytes.

The additional indirect tranche names `FT_Raccess_Guess`, the bounded
resource-fork helpers, ten `FT_Stream_*` operations, five `ft_mem_*` operations,
and the renderer, module, charmap, size, driver, and memory-stream helpers that
formed the final 16-function / 752-byte residue. These retain their inherited
low-confidence call-community tier while their complete bounded semantics now
have authenticated upstream source identities. No row remains unadmitted.

The two 28-byte Apple resource-fork wrappers decompile to the same call shape.
They are distinguished fail-closed by their Thumb literal-load instructions,
the official-image magic words `0x00051607` (AppleDouble) and `0x00051600`
(AppleSingle), and the matching order and definitions in upstream `ftrfork.c`.

## Fallback-loader boundary

The earlier engine-census limitation described a vendor-extended nine-slot
fallback loader. The bounded evidence now distinguishes implementation from
policy: the seven stock functions at `0x00525D32..0x005264A6` are the upstream
2.9.1 `open_face_PS_from_sfnt_stream`, `Mac_Read_POST_Resource`,
`Mac_Read_sfnt_Resource`, `IsMacResource`, `IsMacBinary`,
`load_face_in_embedded_rfork`, and `load_mac_face` bodies. Together they are
1,862 bytes, and the source independently fixes `FT_RACCESS_N_RULES` at nine.
They lie outside the inherited 83-row census and are not counted twice.

No separate Even loader implementation is required. Stock selects upstream
driver autodetection with Mac/resource-fork fallback. The isolated
`runtime_freetype_base_cluster_candidate` adapter makes the remaining policy
explicit:

- upstream autodetection preserves stock behavior;
- TrueType-only pins the authenticated `truetype` driver;
- CFF-only pins the authenticated `cff` driver.

The strict modes use public `FT_OPEN_DRIVER` and therefore bypass cross-driver
and Mac/resource fallback without copying or replacing any upstream loader.

Run the focused gates with:

```sh
cd g2
python3 -m unittest -v \
  tests.test_runtime_freetype_base_cluster_candidate \
  tests.test_runtime_freetype_base_candidate \
  tests.test_runtime_target_provider_candidate
```
