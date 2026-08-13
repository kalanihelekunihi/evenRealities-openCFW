# Ambiq GPU-patch accessor source-candidate audit

Status: three bounded, production-excluded clean-room candidates; no overlay,
release manifest, archive, or hardware state is changed.

Target: G2 `s200_v2.2.6.10` and the exact AmbiqSuite 5.1.0
`extensions/gpu_patch.a` artifact.

## Result

Three of the 11 binary-only Ambiq GPU-patch exports are now source-transparent
at the behavioral and private-layout boundary:

| Public export | Original DWARF line | ELF section | SHA-256 | Recovered operation |
|---|---:|---:|---|---|
| `lv_ambiq_get_vg_paint_tex` | 301 | 16 bytes | `f3a3a1a5…` | return image object; return palette object for LUT textures and `NULL` otherwise |
| `lv_ambiq_get_path_aabb` | 313 | 24 bytes | `e51f6519…` | return `bbox.min.x/y` and `bbox.max.x/y` |
| `lv_ambiq_get_path_vbuf` | 326 | 28-byte section, 26-byte symbol | `bdf5a633…` | return the four leading vertex-buffer fields |

These include three of the six patch calls required by the exact Ambiq LVGL
subtree. A subsequent bounded candidate closes dash-line creation too. The
remaining directly required patch routines are gradient creation and corner-
shadow blur; gradient already has an authenticated stock IAR span.

## Exact artifact and source-coordinate evidence

The input archive is the 51,902-byte `gpu_patch.a` with SHA-256
`31a0e5494cf27a3794212118c152513c16efa0424c51311c70a6f55024b4c95c`
and Git blob `f05c83b4306c9f21efc495325d1214eb72f85e49`. It first appears publicly
at Ambiq commit `e3eec7f3c1148fee3dfa33ca861be176de66c584` and is reproduced by
the complete NemaSDK subtree tree `e690768a6e7b4d6a8d526fc75e8278a2764deff3`
at commit `b853fded7e545f005727e13bf2ce83018c7e242d`.

Its sole object, `ambiq_nema_extension.o`, carries full GCC DWARF. The compile
unit names the unavailable implementation as
`gpu_patch/ambiq_nema_extension.c` under the original absolute checkout
`/Users/wangzhengwei/lv_port_ambiq/lvgl_ambiq_porting`, and names the private
layout header `gpu_patch/nema_vg_p.h`. Function-level sections contain no
relocations, so their complete behavior is local to the displayed loads,
stores, conditional branch, and return.

The offline analyzer now parses GNU `ar` and little-endian ELF32 directly. In
optional `--sdk-root` mode it extracts `ambiq_nema_extension.o`, locates each
`.text.<function>` section, and rejects a size or byte-hash change. This is
stronger than an export-name/string check and does not require host `ar`,
`objcopy`, or network access.

## Recovered private ABI

The exact DWARF fixes the layouts that the public header intentionally hides:

| Private type | Size | Accessed fields |
|---|---:|---|
| `nema_vg_paint_tex_t` | `0x30` | image `+0x00`, palette `+0x04`, LUT flag `+0x2C` |
| `nema_vg_paint_t` | `0xE0` | texture view begins at `+0x00` |
| `nema_vg_path_bbox_t` | `0x50` | minimum at `+0x00`, maximum at `+0x08` |
| `nema_vbuf_t_` | `0x60` | sizes at `+0x00/+0x04`, pointers at `+0x08/+0x0C`, bbox at `+0x10` |
| `nema_vg_path_t` | `0x88` | shape `+0x00`, matrix `+0x60`, flags `+0x84` |

The candidate encodes these facts as 32-bit compile-time assertions. A
fixed-width address token keeps the same layout in host tests; the real Arm
build uses native 32-bit pointers. This avoids accidentally qualifying a
64-bit host layout as the Apollo5 ABI.

One subtle point is now explicit: the paint accessor's `cbz` lands on the
common palette store. Therefore a non-LUT texture writes zero to
`*palette_obj`; it does not leave that output untouched. This agrees with the
public header's stated contract.

## LVGL shortcut value

The exact Ambiq subtree uses the helpers at three ownership boundaries:

- vector teardown reads the paint image/palette before freeing them;
- vector path setup reads the untransformed AABB before applying its matrix;
- vector-font outline teardown reads both private buffers before freeing them.

Consequently OpenCFW can implement those boundaries without importing the
private NemaVG header or reverse-engineering allocator ownership from callers.
The candidates are independently named to avoid masquerading as the BSD-
licensed archive exports and remain production-excluded until an atomic
LVGL/Nema/HAL admission is reviewed.

## Reproduction

```sh
make ambiq-gpu-patch-accessors-candidate
python3 tools/analyze_g2_nemagfx_ambiq_provenance.py \
  --sdk-root /path/to/AmbiqSuite_v5
```

The focused suite covers both paint branches, exact AABB and vbuf values,
private layout assertions, relocation-free Cortex-M55 output, independent
naming, production exclusion, and exact archive-section metadata.

## Remaining gates

- Recover or explicitly admit the other six GPU-patch exports. Of those,
  gradient and shadow blur are required by the exact LVGL subtree.
- Obtain the original implementation source if available; these candidates do
  not claim textual identity.
- Bind and qualify the stock bare-metal allocator, IRQ, cache, reset, and power
  port atomically with LVGL and the Nema archives.
- Validate command-list submission, rendering, memory ownership, and power
  retention on Apollo510 hardware.
