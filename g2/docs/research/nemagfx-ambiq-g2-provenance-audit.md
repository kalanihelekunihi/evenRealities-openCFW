# G2 NemaGFX, NemaVG, and Ambiq GPU dependency audit

Status date: 2026-08-10  
Target: official G2 `s200_v2.2.6.10`  
Scope: third-party identity, version, public commit recovery, stock configuration,
and production-admission boundary

## Result

The GPU dependency under the recovered Ambiq LVGL backend is no longer an
unidentified third-party family. The strongest reproducible package is:

| Layer | Recovered identity |
|---|---|
| Ambiq package | AmbiqSuite 5.1.0, revision `release_sdk5p1p0-634f7c117b` |
| NemaGFX | 1.4.12, API `0x01040C`, implementation `0x00241000` (2024-10) |
| NemaVG | 1.1.8, API `0x010108`, implementation `0x00241000` (2024-10) |
| Public repository | `https://github.com/AmbiqMicro/ambiqhal_ambiq.git` |
| Complete reproducible subtree | `components/graphics/NemaGFX_SDK`, tree `e690768a6e7b4d6a8d526fc75e8278a2764deff3` |
| First public commit with that complete tree | `b853fded7e545f005727e13bf2ce83018c7e242d` |
| Apollo5 Nema archive first public commit | `c6f54a9587fcdc3cd10a9af5db0b602f34d5304f` |
| Ambiq GPU-patch archive first public commit | `e3eec7f3c1148fee3dfa33ca861be176de66c584` |

The available AmbiqSuite package and public Git subtree contain the same 50
files and 3,913,845 bytes. A verifier reconstructs the Git tree directly from
the package, without requiring it to be a Git checkout, and obtains the exact
tree ID above. Ten decisive artifacts are also pinned independently by byte
count, Git blob SHA-1, and SHA-256.

This closes a reproduction commit, not the historical Even checkout. The
public commits post-date the internal source state visible in G2 and expose
GCC archives, whereas stock functions use IAR code generation. The public
state is therefore an exact package/source-interface oracle and a practical
OpenCFW dependency pin; it is not a byte-identical explanation of the linked
stock archive.

## Stock version evidence

Two independent stock facts force NemaGFX 1.4.12 or later:

- `lv_ambiq_common_start` calls `nema_cl_bind_sectored_circular`; and
- the firmware retains `INVALID_SECTORED_CL_SIZE` at `0x0076C8E8`.

The NemaGFX changelog first adds both the sectored-circular command-list API
and `NEMA_ERR_INVALID_SECTORED_CL_SIZE` in 1.4.12. The exact AmbiqSuite
candidate's version header declares 1.4.12, so stock and package evidence agree.
This is an authenticated stock lower bound and the exact available package
version. It is not proof that a hypothetical later source-identical internal
release could not have been used.

NemaVG 1.1.8 is the exact co-packaged version and matches the Ambiq backend's
API/structure use, but stock does not retain a unique NemaVG version token.
The documentation therefore deliberately labels 1.1.8 an exact package
candidate rather than an independently forced stock point release.

## Public artifact history

The useful commit history is layered rather than a single unsupported claim:

1. `c6f54a9587fcdc3cd10a9af5db0b602f34d5304f` first publishes the exact
   `lib_nema_apollo5x_nemagfx.a` blob
   `98cfec6fa60c7372777ec0a31cea477c33df1483`.
2. `e3eec7f3c1148fee3dfa33ca861be176de66c584` first publishes the exact
   `gpu_patch.a` blob `f05c83b4306c9f21efc495325d1214eb72f85e49`
   and its BSD-3-Clause header.
3. `b853fded7e545f005727e13bf2ce83018c7e242d` is the first public commit
   whose complete 50-file `NemaGFX_SDK` subtree matches the independent
   AmbiqSuite 5.1.0 package exactly.

For OpenCFW reproduction, `b853fded…` is the proper all-in-one compatibility
commit. For historical attribution, the archive-specific first commits are
the more precise facts, and no public commit is asserted as Even's original
private checkout.

## Stock symbol and configuration recovery

Exact Ambiq source from subtree `1e774257…` maps the following stock entries:

| Stock entry | Recovered symbol | Size |
|---|---|---:|
| `0x004B092A` | `lv_ambiq_common_start` | 560 |
| `0x004C73D6` | `lv_draw_ambiq_init` | 280 |
| `0x0051418E` | `nema_get_last_cl_id` | 6 |
| `0x00514194` | `nema_get_last_submission_id` | 6 |
| `0x0051419A` | `nemagfx_power_control` | 158 |
| `0x00514278` | `nema_cl_create_sized` | 118 |
| `0x00514384` | `nema_cl_rewind` | 80 |
| `0x005143D4` | `nema_cl_bind_sectored_circular` | 230 |
| `0x005144FA` | `nema_cl_get_bound` | 16 |
| `0x005FA238` | `lv_ambiq_gradient_create` | 1,416 |
| `0x005FA7C0` | `lv_ambiq_dashline_create` | 138 |

Every listed span is pinned by SHA-256. The two last entries are out-of-line
Ambiq GPU-patch implementations identified by exact caller order and argument
shape. Four other GPU-patch APIs required by the recovered LVGL subtree do not
have a separate surviving stock entry in the current function corpus; their
logic is consistent with IAR cross-module optimization/inlining or folding.
That absence is not treated as proof of source ownership.

`lv_draw_ambiq_init` passes `0x19000` (102,400) to
`nema_cl_create_sized`. `lv_ambiq_common_start` later passes 100 sectors to
`nema_cl_bind_sectored_circular`. The only exact integer solution is therefore:

```c
#define LV_AMBIQ_COMMAND_LIST_SECTOR      100
#define LV_AMBIQ_COMMAND_LIST_SECTOR_SIZE 1024
```

The same stock path calls `nemagfx_power_control(AM_HAL_SYSCTRL_WAKE, true)`
and retains the failure diagnostic. This proves `NEMAGFX_POWER_SAVE=1` and
retained-context wake policy. Creation of a VG path, paint, and gradient proves
`LV_USE_AMBIQ_VG=1`; the linked backend proves `LV_USE_DRAW_AMBIQ=1`.

These values are now recorded in
`third_party/lvgl/g2-config/lv_conf_recovered.h` and the LVGL ABI metadata.
They do not change the already exact `lv_global_t==0x1EC` result.

## GPU-patch boundary

The public `gpu_patch.a` contains one object, `ambiq_nema_extension.o`, with 11
exported functions:

- `lv_ambiq_create_corner_mask`
- `lv_ambiq_dashline_create`
- `lv_ambiq_draw_bitmap_glyph`
- `lv_ambiq_get_glyph`
- `lv_ambiq_get_path_aabb`
- `lv_ambiq_get_path_vbuf`
- `lv_ambiq_get_vg_paint_tex`
- `lv_ambiq_gradient_create`
- `lv_ambiq_l8_l4_convert`
- `lv_ambiq_shadow_blur_corner`
- `lv_ambiq_shadow_blur_corner_vg`

Every export now has an exact section/symbol/relocation ledger:

| Export | Section / symbol bytes | Relocations | Original line | Source status |
|---|---:|---:|---:|---|
| `create_corner_mask` | 164 / 164 | 10 | 349 | bounded candidate |
| `dashline_create` | 144 / 144 | 8 | 268 | bounded candidate |
| `draw_bitmap_glyph` | 1,036 / 1,036 | 34 | 590 | bounded candidate |
| `get_glyph` | 188 / 188 | 1 | 818 | bounded candidate |
| `get_path_aabb` | 24 / 24 | 0 | 313 | bounded candidate |
| `get_path_vbuf` | 28 / 26 | 0 | 326 | bounded candidate |
| `get_vg_paint_tex` | 16 / 16 | 0 | 301 | bounded candidate |
| `gradient_create` | 1,416 / 1,416 | 16 | 138 | bounded candidate |
| `l8_l4_convert` | 224 / 224 | 15 | 706 | bounded candidate |
| `shadow_blur_corner` | 668 / 668 | 39 | 383 | bounded candidate |
| `shadow_blur_corner_vg` | 324 / 324 | 15 | 454 | bounded candidate |

The 11 sections total 4,232 bytes, their symbols total 4,230 bytes (the vbuf
section has one trailing NOP), and they carry 138 relocations. The analyzer
authenticates all section hashes, symbol sizes, relocation counts, and unique
targets from the ELF object rather than accepting this table as prose.

The exact recovered LVGL subtree directly requires six: dash-line creation,
gradient creation, path AABB, path vertex-buffer access, paint texture access,
and corner-shadow blur. The public repository contains the complete header and
GCC binary archive, but not the implementation source. All 11 exports / 4,232
section bytes are now behaviorally source-transparent through exact
DWARF/layout, section-byte evidence, stock-IAR correlation, exact-object
control-flow recovery, and exact Cortex-M55 emulation. This includes all six
required exports and all five non-required exports. See the [accessor audit](ambiq-gpu-patch-accessor-source-candidate-audit.md),
[dash-line audit](ambiq-gpu-patch-dashline-source-candidate-audit.md), and
[glyph audit](ambiq-gpu-patch-get-glyph-source-candidate-audit.md), plus the
[gradient audit](ambiq-gpu-patch-gradient-source-candidate-audit.md) and
[shadow-blur audit](ambiq-gpu-patch-shadow-blur-source-candidate-audit.md),
[small-raster audit](ambiq-gpu-patch-small-raster-source-candidate-audit.md),
[VG-shadow audit](ambiq-gpu-patch-shadow-blur-vg-source-candidate-audit.md), and
[bitmap-glyph audit](ambiq-gpu-patch-bitmap-glyph-source-candidate-audit.md).

## Compiler and license qualification

The 1,809,800-byte Apollo5 archive has SHA-256
`109840f6e0bbeb8618a1a853966cdf68cf169620bcc4075ed7a1c86ab0d3286f`.
It contains 33 objects and full DWARF identifying GCC 13.2.1, Cortex-M55,
hard-float Armv8.1-M Mainline with MVE/FP, `-O3`, function/data sections, and
the internal source path
`third_party/ThinkSi/NemaGFX_SDK/NemaGFX/Nema/nema_blender.c`.

The stock spans are not byte-identical to these GCC sections and exhibit IAR
code generation. OpenCFW may use the public archive as a maintained GNU
compatibility artifact after target validation, but must not cite it as the
stock generating archive.

Think Silicon's `headers/LICENSE` is permissive and MIT-like but adds a
normative-header warning. The manifest preserves it as
`LicenseRef-Think-Silicon-NemaSDK-Permissive` rather than silently collapsing
it to a standard SPDX assertion. Ambiq's GPU-patch header and port carry the
full BSD-3-Clause notice. Any imported archive/header set must preserve both
notice families.

## Reproduction

The offline stock/manifest audit is:

```sh
python3 tools/analyze_g2_nemagfx_ambiq_provenance.py
python3 -m unittest tests.test_analyze_g2_nemagfx_ambiq_provenance -v
```

When an AmbiqSuite 5.1.0 package is available, authenticate its complete tree:

```sh
python3 tools/analyze_g2_nemagfx_ambiq_provenance.py \
  --sdk-root /path/to/AmbiqSuite_v5
```

The optional mode rejects a one-byte tree mutation, verifies the SDK revision,
reconstructs the exact public Git tree, hashes all selected artifacts, checks
the GCC/DWARF markers and every export, and extracts/hashes all 11 function
sections and their relocation graphs directly. All modes are read-only and have no device or
flash operation.

## Remaining production gates

Dependency identity is closed, but production admission remains fail-closed on:

- the original IAR-built NemaGFX/NemaVG archive or its exact private source
  commit, if stock-byte reproduction is required;
- original implementation-source recovery or explicit admission of the
  independently named clean-room candidates for all 11 GPU-patch exports;
- atomic admission of the bounded 18-function / 614-byte bare-metal HAL
  candidate (the exact private generating source/commit remains unavailable);
- atomic integration of the exact Ambiq LVGL subtree, handler ABI patch,
  Nema archives, and board port; and
- Apollo510 hardware validation of command-list submission, sector wrap,
  cache coherency, power retention, and rendering output.

The display/input manager, FreeType system glue, font assets, and Even UI
remain separate first-party boundaries. The private display-panel port is also
separate from Nema provenance, but its complete seven-function / 638-byte
linked surface is already source-owned. None should be folded into the Nema
provenance claim.
