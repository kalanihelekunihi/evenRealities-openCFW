# Apollo data/asset source-representation generator tooling (XC-005)

## Scope

This closes XC-005 as *host tooling*, not as a byte-range closure: it defines
and delivers the generator tooling the "Apollo main application - retained
data, tables, and assets" AD-* items (`docs/../remaining-work.md`) are
directed to use so that a reconstructed data region is a documented source
asset run through a reviewed generator, never a byte array copied out of the
stock image. XC-005 itself owns no flash range (`bytes: 0`) and reads the
stock firmware image nowhere in the tooling below; per-AD-item differential
comparison against the stock oracle remains that item's job.

The work item names five data-region families. Each is addressed below with
either working, tested generator tooling, or a documented representation
decision with a stated reason no new tool is needed.

## LVGL images -- `tools/assetgen_lvgl_image.py` (done)

**Representation:** the original artwork (a PNG, or anything Pillow can
read) under a documented license, converted by this tool into an
`lv_image_dsc_t` initializer matching
`third_party/lvgl/src/draw/lv_image_dsc.h` at the pinned openCFW LVGL
snapshot (commit `344c7c318047b7348e1be8572a9fd4260c251cfa`).

Supported `lv_color_format_t` values: `L8`, `A8`, `I8` (256-entry BGRA8888
palette + index bytes), `RGB565`, `RGB888`, `XRGB8888`, `ARGB8888`. `L8`/`A8`
match the recovered G2 `LV_COLOR_DEPTH` of 8
(`third_party/lvgl/g2-config/lv_conf_recovered.h`), so they are the most
likely fit for the monochrome-panel image regions; the others are provided
for regions that turn out to need color or per-pixel alpha.

Every generated file is independently round-trip-verified inside the tool
(the packed bytes are decoded back with a from-scratch reference decoder and
compared to the pixels that were encoded) before it is written, and the
`lv_image_header_t` bit-packing was cross-checked against the real, compiled
struct layout (not just modeled in Python) -- see
`tests/test_assetgen_lvgl_image.py::test_header_packing_matches_compiled_bitfield_layout`.
All seven formats compile cleanly (`-Wall -Wextra -Werror`) against the real
vendored header with `LV_CONF_SKIP=1`. Output is deterministic byte-for-byte
for a given input.

This tool is openCFW-authored (MIT) and does not embed or depend on any LVGL
source at generation time; it only targets the vendored header's documented
layout.

**What it does not do:** decide which AD-* region is an image, recover the
original artwork, or pick the color format a given region's caller code
expects -- those remain per-AD-item analysis.

## String pools -- `tools/assetgen_string_pool.py` (done)

**Representation:** a small JSON list of named strings, packed by this tool
into a single NUL-terminated blob plus a selectable offset table
(`--layout=offsets`), pointer table (`--layout=pointers`), or both. The
physical layout a specific retained caller expects (offsets vs. pointers) is
an AD-* item's own finding from its reference-closure analysis (the same
technique the existing `analyze_g2_*` tools already use for other data
objects); this generator supports either without guessing.

Round-trip verified (packed blob decodes back to the exact source strings)
before every write; output is deterministic. Generated sources compile
cleanly and were exercised at runtime (`strcmp` against the emitted pointer
table) in `tests/test_assetgen_string_pool.py`.

## Protobuf descriptors -- `tools/assetgen_nanopb_descriptor.py` (done)

**Representation:** a source `.proto` schema (recovered field
numbers/types/names from the matching `nanopb-*` decoder-boundary audit's
call sites), compiled by the *real* nanopb reference generator -- not a
hand-rolled reimplementation -- into `pb_msgdesc_t` C source.

The generator (`protoc` + the `nanopb` PyPI package) is treated as an
external host build dependency, exactly like the C compiler already is
(`tools/detect_toolchain.py`), rather than vendored into the tree. It is
pinned to `nanopb==0.4.9`, the exact tag/commit already vendored as this
repo's nanopb runtime (`third_party/nanopb/PROVENANCE.json`: tag
`nanopb-0.4.9`, commit `98bf4db69897b53434f3d0ba72e0a3ab1a902824`, Zlib
license); the tool fails closed if a different version is installed instead
of silently generating against a mismatched ABI (`PB_PROTO_HEADER_VERSION`
is checked by the generated header itself, and the wrapper checks the
package version before running).

Verified end-to-end in `tests/test_assetgen_nanopb_descriptor.py`: a sample
`.proto` is compiled to `.pb.c`/`.pb.h`, which compile cleanly against the
vendored `third_party/nanopb` runtime headers, and re-running against the
same input reproduces byte-identical output.

Installed and exercised in this session via `pip install --user
nanopb==0.4.9` (recorded in `tools/requirements-assetgen.txt`); this is a
host Python environment change, not a repository change.

## LVGL fonts -- `tools/assetgen_lvgl_font.py` (done, with a stated limitation)

**Representation:** a source TTF/OTF font file under a documented, AD-item-
recorded license, rasterized by the official LVGL font converter
(`lv_font_conv`, MIT, https://github.com/lvgl/lv_font_conv) into the same
`lv_font_fmt_txt_dsc_t`/`lv_font_t` layout the already-reviewed decoder in
`docs/research/g2-lvgl-font-fmt-source-admission.md` consumes.
Hand-rolling a TrueType shaper/rasterizer instead of using the upstream
project's own converter would itself be an unreviewable reimplementation
risk, so this wraps the real tool rather than reinventing it.

`lv_font_conv` is treated as an external host build dependency (Node.js/npm)
and is *not* vendored -- vendoring its npm dependency tree (opentype.js,
pngjs, yargs, ...) would trade a reviewable diff for an unreviewable one.
It is pinned to the exact published version `1.5.3` and to the npm
registry's own content-integrity hash for that version
(`sha512-0xJQThBOw2iptFccSXrKDIUTQAwr/2zhKjCI1lATIRgZo8uvYRTmenKafW9yTw6G0y5AyW00tqGpUtYuTuBIbQ==`);
a version or integrity mismatch fails closed.

**Stated limitation:** unlike the other three generators, this one requires
network access at generation time (to resolve/fetch the pinned npm package),
so it cannot be exercised in a fully offline macOS build. This is recorded
here rather than hidden. `tests/test_assetgen_lvgl_font.py` exercises the
real tool end-to-end (a system TTF, rasterized and compiled against the
vendored LVGL headers with `LV_CONF_SKIP=1`) and passed in this session; it
skips cleanly instead of failing when npx/network is unavailable.

## Cordio tables -- no new generator tool (design decision)

Apollo's Cordio "tables" -- ATT/GATT attribute and service databases, UUID
constant tables, and similar -- are not opaque data needing a bitmap-style
converter. `docs/research/cordio-att-uuid-source-recovery.md` (one of the 73
`cordio-*` audits) already demonstrates the pattern: the retained bytes are a
linked subset of a public, byte-identical Packetcraft/AmbiqSuite upstream
`.c` translation unit (`att_uuid.c`), already vendored license-and-commit
-pinned at `third_party/cordio`. The maintainable source representation for
a Cordio table region is therefore **the matching upstream Cordio/Packetcraft
`.c` file itself**, identified and routed exactly like any other reviewed
function or data object (overlay entry, manifest pin, EVIDENCE update) --
the existing `analyze_g2_cordio_*`/`cordio-*` audit methodology already
covers identification. No new conversion tool is needed or would help: there
is no separate "source asset" upstream of these tables other than the
upstream source file that already exists.

An AD-* item that turns out to cover a genuinely first-party (non-Packetcraft)
Cordio-adjacent table -- e.g. an application-authored GATT service database
built with the vendored Cordio attribute-table macros -- should hand-author
that table in reviewed C using those macros directly, the same way any other
first-party G2 data structure is written; that is not a generator-tooling
gap either.

## FreeType payloads -- no new generator tool (design decision)

A "FreeType payload" data region is, per the existing `freetype-*`/
`analyze_g2_freetype_*` audits, most plausibly a complete embedded
TrueType/OpenType font file consumed via `FT_New_Memory_Face` by the
already-vendored, license-pinned FreeType 2.9.1 engine
(`third_party/freetype`, commit `86bc8a95056c97a810986434a3f268cbe67f2902`)
-- not FreeType's own code or an internal table needing conversion.
FreeType consumes standard font-file bytes directly; there is nothing to
generate. The maintainable source representation is **a licensed,
redistributable TTF/OTF file**, provenance-recorded the same way
`third_party/*/PROVENANCE.json` records every other vendored dependency
(upstream project, version, SHA-256, license), chosen by the AD-* item for
glyph-repertoire fit against whatever the retained caller code requires.

This is a genuine, stated gap: no specific font has been selected yet, and
doing so is scoped to whichever AD-* item first needs it, not to this
tooling item.

## How an AD-* item uses this

1. Identify the region's structure from its referencing code (the existing
   `analyze_g2_*` methodology).
2. Place a licensed source asset (image / string list / `.proto` / font)
   under the component's asset tree, with its own SHA-256 and license record.
3. Run the matching `tools/assetgen_*.py` (or, for Cordio tables and FreeType
   payloads, follow the design decisions above) to produce reviewed C source.
4. Register the result exactly like any other reviewed source: overlay
   entry, manifest pin, EVIDENCE/README update, and a differential check
   against the stock image as oracle (not as an input).

## Reproduction

```sh
python3 -m unittest \
    tests.test_assetgen_lvgl_image \
    tests.test_assetgen_string_pool \
    tests.test_assetgen_nanopb_descriptor \
    tests.test_assetgen_lvgl_font
```

All four suites passed on this macOS host on 2026-09-11, including the two
end-to-end suites that require external tools (`protoc` + `pip install
nanopb==0.4.9`; Node's `npx` + network access to the npm registry).
