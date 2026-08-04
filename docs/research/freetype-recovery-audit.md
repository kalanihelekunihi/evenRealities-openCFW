# FreeType Recovery Audit — Even Realities G2 firmware (g2-2.2.6.10)

**Status: research-only recovery**

The official FreeType 2.9.1 release source is now authenticated and vendored
as a production-excluded snapshot; see
[`freetype-2.9.1-snapshot-audit.md`](freetype-2.9.1-snapshot-audit.md).  This
document remains authoritative for the G2-specific configuration evidence and
unresolved runtime seams.

Target blob: `blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`
(3,523,396 bytes; raw ARM Cortex‑M55 Thumb‑2 XIP image)

Load mapping (given, confirmed by working xrefs): **run address = file_offset + 0x00437FE0**.
All addresses below are *run* addresses unless labeled `fileoff`.

Method: string mining (`strings -a -t x`), literal‑pool LE32 pointer xrefs, and bounded
capstone (Thumb, Cortex‑M/MCLASS) disassembly from `push {…,lr}` prologues. No blob or build
files were modified.

---

## 1. Identity evidence

| Evidence | Run addr (fileoff) | Meaning |
|---|---|---|
| `FT_New_Library` writes `version_major = 2` (`movs r0,#2; str r0,[r1,#4]`) | 0x5274da (0x0ef4fa) | FREETYPE_MAJOR = 2 |
| `FT_New_Library` writes `version_minor = 9` (`movs r0,#9; str r0,[r1,#8]`) | 0x5274de | FREETYPE_MINOR = 9 |
| `FT_New_Library` writes `version_patch = 1` (`movs r0,#1; str r0,[r1,#0xc]`) | 0x5274e2 | FREETYPE_PATCH = 1 |
| `FT_New_Library` allocates `FT_LibraryRec` of size `0xB8` (`movs r1,#0xb8`) | 0x5274c8 | sizeof(FT_LibraryRec)=184; refcount `str.w r0,[r1,#0xb4]` at 0x5274e8 |
| `FT_Init_FreeType` (calls FT_New_Memory → FT_New_Library → FT_Add_Default_Modules) | 0x52431c | entry point used by LVGL |
| `FT_Add_Default_Modules` (walks `ft_default_modules[]`, calls FT_Add_Module) | 0x5242fc | loads array base via `ldr r5,[pc,#0x14]` |
| `FT_Add_Module` (callee inside the loop) | 0x52729c | — |
| `ft_default_modules[]` array base (literal pool) | 0x73eef8 (0x306f18) | NULL‑terminated at 0x73ef20 |
| Service id `truetype-engine` | 0x789ce0 (0x351d00) | FT_SERVICE_ID_TRUETYPE_ENGINE (TT bytecode) |
| Service id `cff-load` | 0x78a5d4 (0x3525f4) | FT_SERVICE_ID_CFF_LOAD — **added in FreeType 2.9.0** |
| Autofit property `warping` | 0x78cdac (0x354dcc) | AF warper — **removed in FreeType 2.13.0** ⇒ build predates 2.13 |
| LVGL wrapper source path | (fileoff 0x2a0f04…) | `D:\01_workspace\s200_ap510b_iar_git\third_party\lvgl_v9.3\LVGL\src\libs\freetype\lv_freetype*.c` (IAR build, Ambiq S200/AP510) |

**Conclusion: FreeType 2.9.1.** This is not inferred from a string — it is read directly from the
integer constants stored by `FT_New_Library` into `FT_LibraryRec.version_{major,minor,patch}`
(offsets 4/8/0xC). The feature signature is fully consistent: `cff-load` service requires ≥ 2.9.0,
and the presence of the autofit `warping` property requires < 2.13.0. FreeType itself was compiled
with source paths stripped (only the LVGL `lv_freetype` wrapper paths survive); no `FreeType 2.x`
banner string is embedded (FreeType keeps its version only as numeric constants, which is what we
recovered).

---

## 2. Compiled module table — `ft_default_modules[]`

Static, NULL‑terminated array of `const FT_Module_Class*`, base **0x73eef8**. Each entry points to
a class struct whose `module_name` field (struct+8) was resolved to a string. Order is the compiled
`FT_USE_MODULE` order from the build's `ftmodule.h`.

| # | array slot | class base | `module_name` | flags | obj size | role (flag decode) |
|---|---|---|---|---|---|---|
| 0 | 0x73eef8 | 0x752520 | `autofitter` | 0x00000004 | 56  | HINTER |
| 1 | 0x73eefc | 0x6ded34 | `truetype`   | 0x00000501 | 68  | FONT_DRIVER \| SCALABLE \| HAS_HINTER (native bytecode) |
| 2 | 0x73ef00 | 0x6dcb74 | `cff`        | 0x00000d01 | 72  | FONT_DRIVER \| SCALABLE \| HAS_HINTER \| HINTS_LIGHTLY |
| 3 | 0x73ef04 | 0x758a18 | `psaux`      | 0x00000000 | 12  | helper (PostScript aux) |
| 4 | 0x73ef08 | 0x758a60 | `psnames`    | 0x00000000 | 12  | helper (glyph‑name service) |
| 5 | 0x73ef0c | 0x758a3c | `pshinter`   | 0x00000000 | 168 | helper (PostScript hinter) |
| 6 | 0x73ef10 | 0x75a3f8 | `sfnt`       | 0x00000000 | 12  | helper (SFNT wrapper) |
| 7 | 0x73ef14 | 0x718d9c | `smooth`     | 0x00000002 | 64  | RENDERER (anti‑aliased, FT_RENDER_MODE_NORMAL) |
| 8 | 0x73ef18 | 0x718dd8 | `smooth-lcd` | 0x00000002 | 64  | RENDERER (horizontal LCD) |
| 9 | 0x73ef1c | 0x718e14 | `smooth-lcdv`| 0x00000002 | 64  | RENDERER (vertical LCD) |
|   | 0x73ef20 | `NULL`   | —            | —          | —   | terminator |

**10 built‑in modules.** Flag legend: FONT_DRIVER=0x1, RENDERER=0x2, HINTER=0x4,
DRIVER_SCALABLE=0x100, DRIVER_HAS_HINTER=0x400, DRIVER_HINTS_LIGHTLY=0x800.

### Present renderers / drivers
- Anti‑aliased **smooth** rasterizer plus both **LCD** subpixel renderer classes (`smooth-lcd`,
  `smooth-lcdv`).
- **TrueType** driver with the native **bytecode interpreter** (flag 0x400 + `truetype-engine`
  service + `interpreter-version` property @0x784694).
- **CFF/OpenType‑CFF** driver (flag 0x800 HINTS_LIGHTLY; `cff-load`
  service @0x78a5d4, `random-seed` property @0x78aab4, `OTTO` tag
  @0x78566c).  Its module initializer at `0x005B004A` selects Adobe's
  hinting engine, proving the old CFF engine compile guard is off.
- **autofitter** with the `glyph-to-script-map`, `fallback-script`,
  `default-script`, `hinting-engine`, `no-stem-darkening`,
  `darkening-parameters`, `increase-x-height`, and guarded `warping`
  properties.  CJK/Indic style-table inclusion is not inferred from the
  generic properties.
- SFNT/psaux/psnames/pshinter support modules (required by TrueType + CFF).

### Explicitly ABSENT from the module table
No `type1`, `t1cid`/`cid`, `pfr`, `type42`, `winfonts`, `pcf`, `bdf`, `raster1` (monochrome),
`sdf`/`bsdf`, or OT‑SVG driver is present in `ft_default_modules[]`. (Loose strings `type1` /
`Type 1` / `cid` / `IsCIDFont` exist only in a font‑format/PostScript name data table near fileoff
0xEE000 and inside the CFF/psaux CID‑keyed parser; they are **not** referenced by any module‑class
entry, so no standalone Type 1 / CID driver is built in.)

---

## 3. Recovered FT_CONFIG_OPTION_* / build configuration

The fail-closed audit `tools/freetype_g2_config_audit.py` pins the complete
official-image hash plus twenty-one focused code/data spans.  The following states
are now direct firmware conclusions, not upstream-default assumptions:

| Option | State | Firmware evidence |
|---|---|---|
| `TT_CONFIG_OPTION_BYTECODE_INTERPRETER` | **ON** | TrueType class flag `0x400`, engine service, live interpreter initializer |
| `TT_CONFIG_OPTION_SUBPIXEL_HINTING` | **2 (minimal)** | `tt_driver_init` at `0x005F903C` stores 35 and then 40 to `TT_DriverRec+0x40`; the property setter accepts 35/40 but contains no 38 branch |
| TrueType interpreter default | **40** | final store in the exact 12-byte initializer; span SHA-256 `e9fa34c7e36a2d040315b03e434364a291c604ba644338fdcd2e3de12e37ecab` |
| `TT_CONFIG_OPTION_GX_VAR_SUPPORT` | **ON** | six-entry `tt_services` table at `0x00725060` plus multi-master record at `0x007505A4` and metrics record at `0x00767290` |
| `TT_CONFIG_OPTION_EMBEDDED_BITMAPS` | **ON** | non-null `select_size` callback at TrueType class offset `0x5C` |
| `FT_CONFIG_OPTION_PIC` | **OFF** | static `FT_Driver_ClassRec` at `0x006DED34` and direct class pointers in `ft_default_modules[]` |
| `FT_CONFIG_OPTION_ENVIRONMENT_PROPERTIES` | **OFF** | `tt_property_set` at `0x005EF0B0` ignores its fourth argument and directly loads the integer value; `FT_Init_FreeType` has no default-property parser call |
| `FT_CONFIG_OPTION_INCREMENTAL` | **ON** | face-internal allocation at `0x00525A0C` is `0x44` bytes; the `incr` tag `0x696E6372` at `0x005262A8` is compared by the parameter loop, which installs its data pointer at internal offset `0x34` |
| `FT_CONFIG_OPTION_SUBPIXEL_RENDERING` | **OFF** | smooth renderer `0x005E22E0..0x005E2636` is the authenticated 2.9.1 fallback body: three raster passes with ±21/42 outline shifts and a temporary interleave buffer; this is mutually exclusive with the filter-enabled branch |
| default stream support | **ON** | `FT_Stream_Open` is present at `0x00784BF0` and used by the face-opening path |
| `AF_CONFIG_OPTION_USE_WARPER` | **ON** | `warping` property at `0x0078CDAC`; that branch is guarded by this macro in authenticated 2.9.1 source |
| `AF_CONFIG_OPTION_CJK` | **ON** | autofit initializer stores fallback style enum 83, which is `AF_STYLE_HANI_DFLT`; the fallback macro selects HANI only under the CJK guard |
| `AF_CONFIG_OPTION_INDIC` | **ON** | in authenticated 2.9.1 `AF_STYLE_HANI_DFLT` is enum 79 without the four guarded Indic styles and enum 83 with them; the stored enum is 83 |
| LCD renderer classes | **ON** | `smooth-lcd` and `smooth-lcdv` in the authenticated module table |
| `CFF_CONFIG_OPTION_OLD_ENGINE` | **OFF** | CFF class initializer pointer is `0x005B004B`; its body stores `FT_HINTING_ADOBE` (value 1) at driver offset `0x1C`, the exact upstream `#else` selection |

### GX/AAT depth

The GX result is stronger than the earlier service-string observation.  The
2.9.1 `TT_CONFIG_OPTION_GX_VAR_SUPPORT` guard adds two service records:

- `FT_Service_MultiMastersRec` at `0x007505A4`: its legacy `get_mm` and
  `set_mm_design` slots are null exactly as upstream defines them, while all
  eight modern blend/design/instance/get-blend/done-blend slots are non-null;
- `FT_Service_MetricsVariationsRec` at `0x00767290`: horizontal advance,
  vertical advance, and MVAR metrics-adjust callbacks are non-null, matching
  the 2.9.1 record; side-bearing and vertical-origin hooks remain null.

This proves the guarded `fvar`/`gvar`/`cvar`/`avar` implementation and the
HVAR/VVAR/MVAR service paths were selected.  It does not prove that any
deployed font uses every table or that the vendor made no private changes
inside those functions.

### Corrected boundaries

The earlier HINTS_LIGHTLY and property-string observations alone did **not**
distinguish `CFF_CONFIG_OPTION_OLD_ENGINE`; the CFF initializer now resolves
that guard independently.  Generic `fallback-script` and `default-script`
properties alone did not prove the CJK/Indic guards either.  The exact
initializer fallback enum now does: `AF_STYLE_HANI_DFLT` selects CJK, and its
enum shift from 79 to 83 proves inclusion of all four guarded Indic styles.
Absence of compression/PNG strings is not a fail-closed compile-option proof,
so those states are intentionally not promoted.

Net proven picture: a size-trimmed FreeType 2.9.1 with TrueType and CFF
drivers, v40 minimal TrueType hinting, the Adobe-only CFF engine, complete
guarded variation services, incremental loading, embedded bitmap selection,
smooth/LCD renderers using the non-filtered three-pass LCD implementation,
stream support, and autofit warping with CJK and Indic styles.  Unsupported
module-table entries remain absent as listed above.

---

## 4. API surface actually used

FreeType APIs referenced by the LVGL wrapper (recovered from error‑message strings and confirmed
by disassembly of the init path):

- `FT_Init_FreeType` — @0x788f30 string; init path disassembled (0x52431c).
- `FT_New_Face` — `FT_New_Face error(0x%x)` @0x78846c.
- `FT_Set_Pixel_Sizes` — several call sites (@0x760f30, 0x760f50, …).
- `FT_Set_Char_Size` — @0x7610b0.
- `FT_Load_Glyph` — multiple (@0x76cc88, 0x76cd14, 0x76cd84).
- `FT_Render_Glyph` — @0x76ccf8.
- `FT_Get_Glyph` — @0x76cd14.
- `FT_Outline_Decompose` — @0x755678 (outline‑font callback path).
- `FT_Outline_Embolden` — @0x7610f0.
- `FT_Stream_Open` — @0x784bf0.

Internal (non‑LVGL) APIs proven by disassembly: `FT_New_Library` (0x5274b2),
`FT_Add_Default_Modules` (0x5242fc), `FT_Add_Module` (0x52729c),
`FT_New_Memory` (0x5676a0), and `FT_Done_Memory` (0x5676c6).  The LVGL
font-create/delete entries are fixed below.  `FT_Done_Face` is now exactly
identified at `0x00526814..0x0052687E`.  Its direct caller set is exhaustive
under the authenticated image: the LVGL/FTC face-cache destructor call at
`0x004B2310` and the two `FT_Open_Face` cleanup calls at `0x0052659C` and
`0x005267D0`.  Its body decrements `FT_Face_InternalRec.refcount`, removes the
face from `FT_DriverRec.faces_list`, frees the list node, and calls the private
`destroy_face` body at `0x005258A8`.

No exact stock `FT_Done_FreeType` entry can be assigned safely.  A
conventional 2.9.1 implementation must reach separately compiled
`FT_Done_Memory` at `0x005676C6`, but the only immediate branch to that body in
the complete image is `FT_Init_FreeType`'s new-library failure cleanup at
`0x0052433E`; neither the even nor Thumb address is stored as a word.  This is
positive absence evidence for the normal stock topology, not a license to
invent an entry or equate a nearby function with the API.  Link-time removal
or non-stock whole-program transformation cannot be distinguished from the
raw image, so the report marks the entry `null` and unrecoverable.

Higher‑level integration: LVGL `lv_freetype_font_create` / `_delete`, outline + image font
callbacks (`freetype_get_glyph_bitmap_cb`, `freetype_glyph_create_cb`,
`lv_freetype_set_cbs_outline_font`), and an LVGL‑side glyph/outline cache
(`FREETYPE_CACHE_NODE`, `FREETYPE_OUTLINE`, `FREETYPE_GLYPH`, `FREETYPE_IMAGE`).

---

## 5. Allocator and lifecycle integration

The retained source path at `0x006D82B4` is:

```text
D:\01_workspace\s200_ap510b_iar_git\third_party\lvgl_v9.3\lvgl_ambiq_demo\lvgl_ttf\src\am_ftsystem.c
```

The implementation is a target-specific replacement for upstream
`ftsystem.c`, not an opaque FreeType allocator:

| Boundary | Address | Recovered behavior |
|---|---:|---|
| `FT_New_Memory` | `0x005676A0` | allocates 16-byte `FT_MemoryRec`, clears `user`, installs three callbacks |
| `FT_Done_Memory` | `0x005676C6` | returns the record to the same global heap |
| allocation callback | `0x005676D4` | ignores `FT_Memory.user`; calls generic allocator `0x00484180` |
| reallocation callback | `0x005676E0` | forwards only the block/new allocation request through generic realloc `0x00484234` |
| free callback | `0x005676EC` | calls generic free `0x0048429E` |
| heap descriptor | `0x20000354` | common first argument to all three generic heap operations |

`FT_Init_FreeType` at `0x0052431C` calls `FT_New_Memory`,
`FT_New_Library`, and `FT_Add_Default_Modules`; on new-library failure it
calls `FT_Done_Memory`.  LVGL creates and deletes font objects through
`lv_freetype_font_create` at `0x004B1C9C` and
`lv_freetype_font_delete` at `0x004B1EF6`.  The latter drains LVGL cache and
face-ID ownership paths; the face cache's node destructor at `0x004B2308`
owns the exact `FT_Done_Face` call at `0x004B2310`.

This allocator seam can be recreated from source using the already recovered
generic heap providers.  It does not require retaining an opaque FreeType
allocator blob once FreeType itself is integrated.

## 6. Compiler and ABI boundary

Retained paths use the build root `s200_ap510b_iar_git`, establishing the IAR
Arm compiler family for this firmware.  The decoded records and functions
establish little-endian 32-bit pointers/longs, Thumb-2 code, four-byte struct
lanes, and the Arm EABI register calling convention.  These facts are enough
to define the FreeType-facing object ABI and adapter signatures.

The raw, stripped image does not identify the IAR release, exact optimization
level, FPU calling mode, full preprocessor command, section-placement flags,
or linker configuration.  The redundant version-35 store immediately before
the version-40 store is compatible with low-optimization IAR codegen, but it
is not promoted into an exact flag claim.

## 7. Font registration and remaining asset boundary

The first-party manager at `0x0046D29A` checks two external XIP header bases:

| Role | XIP header | `lv_font_t` descriptor | four-entry config array |
|---|---:|---:|---:|
| background | `0x80100000` | `0x20002C00` | `0x20002C48` |
| foreground | `0x80700000` | `0x20002C24` | `0x20002C78` |

Each external header is accepted only when word zero is `0x5A5A5A5A`.  The
manager logs the name at `header+4`, installs the font pointer from
`header+0x34`, applies optional halfword size values at `header+0x38` and
`header+0x3A` when they are not `0xFFFF`, and creates a chain of at most four
entries for each role.

Each role's runtime array is exactly 48 bytes: four 12-byte records.  Record
offset 0 is an 8-bit type discriminator, offset 4 is a 32-bit native-font
pointer or FreeType face-path pointer, offset 8 is a 16-bit pixel size, and
offset `0xA` is an 8-bit style.  Padding/unused bytes at offsets 1..3 and
`0xB` are not assigned semantics.  This is a recovered RAM record ABI; it does
not imply that the absent runtime contents are known.

The 12-byte chain configuration discriminator is recovered from
`create_single_font` at `0x0046CFA6`:

- type 0 returns a native `lv_font_t*` from config offset 4;
- type 1 calls `lv_freetype_font_create` with the name/face path at offset 4,
  fixed render-mode value 1, the halfword size at offset 8, and style byte at
  offset `0xA`;
- type 2 is the disabled binary-font path in this build; and
- other type values are rejected.

The XIP payloads are outside the main image, and the two configuration arrays
are runtime RAM state.  Therefore the official main image proves registration
addresses and record layout but does not reveal deployed font names, face
paths, file formats, byte lengths, hashes, or glyph coverage.  The XIP header
could describe a native font while another chain entry names a FreeType face;
the two must not be conflated.  Recovering the external font partition is the
remaining prerequisite for asset-level source equivalence.

## 8. Fail-closed offline gate

`tools/freetype_g2_config_audit.py` authenticates the entire official image,
twenty-one focused spans, the complete ten-entry default-module table, decoded
class/service records, Thumb BL/B.W topology, source paths, heap seams, and
XIP registration constants.  It emits deterministic JSON and fails before
reporting any recovered parameter if the official image or a pinned evidence
span changes.

```sh
cd openCFW
PYTHONDONTWRITEBYTECODE=1 python3 tools/freetype_g2_config_audit.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  tests.test_freetype_g2_config_audit
```

Seven focused tests pass.  The mutation gate re-authenticates a deliberately
changed whole-image digest and then proves that every newly added focused span
fails by name; a separate gate scans production inputs.  Neither the tool,
test, authenticated snapshot, nor this audit is
linked by a production component or manifest.

## 9. Explicitly unresolved

- complete `FT_CONFIG_OPTION_*` state outside the proven subset;
- optional compression helpers;
- an exact stock address for `FT_Done_FreeType` (the normal retained topology
  is absent, as described above);
- exact IAR version and compiler/linker flags; and
- external font payload identities and runtime configuration-array contents.

---

*Recovery performed statically; no firmware code was executed or flashed.
Only production-excluded audit, test, and documentation artifacts were added.*
