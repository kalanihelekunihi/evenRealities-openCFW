# G2 Ambiq LVGL source and ABI recovery

Status: read-only source-provenance and ABI audit for official G2 firmware
`2.2.6.10`. No backend source is registered in production and no hardware or
flash operation is performed.

## Result

The formerly opaque `LVGL/src/draw/ambiq` layer is public AmbiqMicro LVGL
source. Its exact subtree is Git tree
`1e774257495fa43177e04fc5c8a42a77c2d7d619` from
<https://github.com/AmbiqMicro/LVGL>. The canonical `ambiq-stable` commit is
`5be8e0ae5077aa3880aba8a322b1487d6bc73c07`, dated 2025-07-09. Commit
`67fd93e268f86b2ce90d4f1b14b53e36bf49ddd0` is a replay with different whole
repository history but byte-identical `src/draw/ambiq`. Linked firmware cannot
distinguish those two commit objects, so the exact subtree is proven while the
historical commit object remains honestly two-way ambiguous.

The immediately following backend commit,
`6770071cb7c4ab97b83669078fe461df812bc79e`, changes the letter/vector-font
sources and is excluded by G2's retained line diagnostics. The authenticated
candidate census contains 16 source/header files and 170,833 bytes. Their
sizes, SHA-256 identities, Git blob IDs, license identity, and commit bounds
are pinned in
[`../../tools/manifests/g2-lvgl-ambiq-source-provenance.json`](../../tools/manifests/g2-lvgl-ambiq-source-provenance.json).

This does not make the complete vendor LVGL tree one public checkout. G2
combines this July Ambiq backend subtree with an older official LVGL core state
equivalent to `60d976c..344c7c`. It is a demonstrably hybrid tree.

## Source evidence

Stock retains the original Ambiq paths for `lv_draw_ambiq_buffer.c`,
`lv_draw_ambiq_vector_font.c`, and `lv_draw_ambiq_letter.c`. Assertion and log
line constants match the recovered subtree, including:

| Source | Retained line numbers |
|---|---|
| `lv_draw_ambiq_buffer.c` | 68, 107, 120, 181, 221, 255 |
| `lv_draw_ambiq_letter.c` | 80, 112, 130, 134 |
| `lv_draw_ambiq_vector_font.c` | 186, 199, 202, 209, 235, 240, 281, 297, 299, 312 |
| `lv_draw_ambiq_private.c` | 273, 277, 282, 295, 297, 301, 332, 377, 385, 399, 482, 509, 538, 555, 559, 663, 708, 715, 725, 731 |

Seven additional Ambiq translation units have matching retained diagnostics.
The analyzer authenticates 11 exact stock spans, the path pointer cells, and
the complete literal table used by `lv_draw_ambiq_init_buf_handlers`.

## Patch ancestry and handler ABI

Ambiq commit `d4dcd26bd97a0b09778ab9f789b6e7a7354bc967`, authored 2025-01-08
with subject `use GPU for memcopy and memclear`, adds `clear_cb` and `copy_cb`
to `lv_draw_buf_handlers_t`. Commit
`925470ddbff5f445f6bca3905305ca9d0f2cf5c8`, authored two minutes later,
adds the Ambiq buffer implementation and GPU callback wiring.

G2 independently proves that ancestry:

- `lv_draw_buf_handlers_init` clears 32 bytes and initializes the first six
  callback slots;
- three handler tables begin at `lv_global+0xC8`, `+0xE8`, and `+0x108`;
- `lv_draw_ambiq_init_buf_handlers` at
  `[0x0053D5DA,0x0053D65C)` writes all eight callbacks in each table; and
- its `clear_cb@+0x18` and `copy_cb@+0x1C` slots point to live Ambiq GPU
  implementations.

The 130-byte initializer has SHA-256
`5a62de8cc39482ab76a6319fd44451d76696e95efd4b203fdb265b47c4d18ed6`.
The minimal source delta required by the selected official-core snapshot is
recorded as
[`../../tools/patches/lvgl-g2-ambiq-draw-buffer-abi.patch`](../../tools/patches/lvgl-g2-ambiq-draw-buffer-abi.patch).

## Exact global-object reconstruction

The previous 12-byte discrepancy was the net result of three independently
recoverable choices, not an unknown padding change:

| Effect relative to the unpatched official reference | Bytes |
|---|---:|
| disable `LV_DRAW_SW_COMPLEX` software circle-mask cache | -112 |
| use `LV_STDLIB_CUSTOM` rather than built-in TLSF state | -32 |
| add two callbacks to each of three Ambiq handler tables | +24 |

Together with the already proven feature switches and newly pinned
`LV_USE_SPAN=1` and `LV_USE_OBJ_ID_BUILTIN=1`, the recovered build reproduces
`sizeof(lv_global_t)==0x1EC` and every observed internal boundary:

| Field | Offset |
|---|---:|
| three 32-byte draw-buffer handler tables | `0xC8`, `0xE8`, `0x108` |
| image decoder list / two cache pointers | `0x128`, `0x134`, `0x138` |
| draw global info / blend-handler list | `0x13C`, `0x160` |
| log callback / timestamp | `0x16C`, `0x170` |
| simple/default/mono theme pointers | `0x174`, `0x178`, `0x17C` |
| filesystem list / littlefs driver | `0x180`, `0x18C` |
| FreeType / span state | `0x1C0`, `0x1C4` |
| object-ID array / count | `0x1C8`, `0x1CC` |
| general mutex / FreeRTOS statistics | `0x1D0`, `0x1D8` |
| user data / object end | `0x1E8`, `0x1EC` |

The same compile retains the stock sizes `lv_display_t==0x31C`,
`lv_indev_t==0xDC`, and `lv_draw_buf_t==0x1C`. The unpatched official snapshot
continues to compile as `lv_global_t==0x1F8` and is retained as a negative ABI
discriminator. Both tests target Cortex-M55 with 32-bit pointers and short
enums.

## Reproduction and remaining boundary

Run:

```sh
python3 tools/analyze_g2_lvgl_ambiq_provenance.py
python3 tools/analyze_g2_nemagfx_ambiq_provenance.py
python3 -m unittest tests.test_analyze_g2_lvgl_ambiq_provenance -v
python3 third_party/lvgl/verify_snapshot.py
```

The new test rejects mutations to authenticated stock code, retained source
paths, handler literals, or the source manifest. It also applies the Ambiq ABI
patch to a temporary official-core snapshot and statically asserts the exact
Arm layout.

The LVGL global ABI is therefore closed. The GPU dependency identity is now
closed separately as AmbiqSuite 5.1.0 with NemaGFX 1.4.12, NemaVG 1.1.8,
public reproduction subtree `e690768a…` at commit `b853fded…`, and exact
Apollo5/GPU-patch archive blobs. Stock additionally fixes a 100 x 1,024-byte
command-list geometry and retained-context GPU wake policy. See the
[NemaGFX/Ambiq dependency audit](nemagfx-ambiq-g2-provenance-audit.md).

Production remains fail-closed on stock-IAR Nema/GPU-patch/HAL candidate
admission, hardware validation, and atomic integration. The separate
`lv_ambiq_display.c` boundary is already source-owned across all seven linked
functions / 638 stock bytes; its original private commit remains unknown.
Input/display managers, FreeType system glue, font assets, and Even application
code remain separate first-party or vendor ports.
