# G2 LVGL flex/grid layout helper and grid-engine closure

Status date: 2026-09-11
Scope: reviewed clean-room C for 49 of the retained functions in
`0x0048C7B4..0x0048D866` (Apollo main application, component
`apollo_main`), work item AM-040
Mode: reviewed source, host differential tests, freestanding
target-profile compile check; no flashing, signing, or hardware
operation

## Result

53 functions (3,336 of 4,102 function bytes) are recovered as reviewed
MIT C in `components/apollo_main/core_overlay/lvgl_layout_style_getters.c`
(25 style getters, 262 bytes) and
`components/apollo_main/core_overlay/lvgl_grid_engine.c` (28 flex/grid
helpers including `calc`, `grid_update`, `calc_free`, `count_tracks`,
`lv_grid_init`, `calc_cols`, `calc_rows`, `item_repos` and `grid_align`,
3,074 bytes):

| Stock span | Bytes | Port symbol | Upstream identity |
| --- | ---: | --- | --- |
| `0x0048C7B4..0x0048C7D8` | 36 | `open_cfw_lvgl_obj_get_width_with_margin` | `lv_obj_get_width_with_margin` (`src/layouts/flex/lv_flex.c`, file-static) |
| `0x0048C7D8..0x0048C7FC` | 36 | `open_cfw_lvgl_obj_get_height_with_margin` | `lv_obj_get_height_with_margin` (same file) |
| `0x0048C7FC..0x0048C80E` | 18 | `open_cfw_lvgl_area_copy` | `lv_area_copy` (`src/misc/lv_area.h`, inline) |
| `0x0048C80E..0x0048C81A` | 12 | `open_cfw_lvgl_memzero` | `lv_memzero` (`src/stdlib/lv_string.h`, inline over `lv_memset` at `0x00454746`) |
| `0x0048C81A..0x0048C920` | 262 (25 fns) | `open_cfw_lvgl_get_style_*` (25) | `lv_obj_style_gen.h` inline getters, out-of-line; property IDs `0x01,0x02,0x6C,0x6D,0x10,0x12,0x14,0x15,0x18,0x19,0x1A,0x1B,0x30,0x34,0x27,0x82,0x7F,0x81,0x80,0x83,0x85,0x84,0x86,0x88,0x87`; the `0x34,0x27,0x7F,0x80,0x85,0x88` six narrow with `uxtb` |
| `0x0048C920..0x0048C94E` | 46 | `open_cfw_lvgl_get_style_space_left` | `lv_obj_style.h` inline (`LV_BORDER_SIDE_LEFT == 0x04` bit test) |
| `0x0048C94E..0x0048C97C` | 46 | `open_cfw_lvgl_get_style_space_top` | `lv_obj_style.h` inline (`LV_BORDER_SIDE_TOP == 0x02` bit test) |
| `0x0048C97C..0x0048C9D6` | 100 (10 fns) | `open_cfw_lvgl_grid_get_*` (10) | grid `get_col_dsc/get_row_dsc/get_col_pos/get_row_pos/get_col_span/get_row_span/get_cell_col_align/get_cell_row_align/get_grid_col_align/get_grid_row_align` (each forwards with part 0) |
| `0x0048C9E0..0x0048C9FC` | 28 | `open_cfw_lvgl_grid_get_margin_hor` | grid `get_margin_hor` |
| `0x0048C9FC..0x0048CA18` | 28 | `open_cfw_lvgl_grid_get_margin_ver` | grid `get_margin_ver` |
| `0x0048CA18..0x0048CA26` | 14 | `open_cfw_lvgl_grid_div_round_closest` | grid `lv_div_round_closest` (`sdiv` order) |
| `0x0048CA26..0x0048CA3C` | 20 | `open_cfw_lvgl_grid_init` | `lv_grid_init` (stores `0x48CA3D` + NULL through slot `base+0x5C`) |
| `0x0048CA3C..0x0048CAD8` | 156 | `open_cfw_lvgl_grid_update` | `grid_update` (see below) |
| `0x0048CAD8..0x0048CBDA` | 258 | `open_cfw_lvgl_grid_calc` | `calc` (see below) |
| `0x0048CBDA..0x0048CBF8` | 30 | `open_cfw_lvgl_grid_calc_free` | `calc_free` (four `lv_free` calls, x/y/w/h order) |
| `0x0048D4D0..0x0048D4E6` | 22 | `open_cfw_lvgl_grid_count_tracks` | `count_tracks` (loop to `LV_GRID_TEMPLATE_LAST`) |

The item stays `partial`: the remaining 11 functions (762 bytes
across the trailing spans, all outside LVGL per the second-wave
survey) are not yet ported; see "What remains" and "Second wave".

## Identity method

Upstream is the pinned compatibility-ceiling snapshot
(`third_party/lvgl`, commit `344c7c318047b7348e1be8572a9fd4260c251cfa`).

- Census: `tools/manifests/g2-lvgl-vendor-fork-census.tsv` places the
  getter run in `LVGL/src/core/lv_obj_style.c` (medium, single-file
  topology) and the `0x0048C7B4/0x0048C7D8` pair in
  `LVGL/src/core/lv_obj_pos.c` (medium). The census alone does not name
  symbols; every name below is confirmed independently.
- Assert-line numbers baked into NULL-check branches match the vendored
  source exactly: `lv_obj_get_width` (stock `0x0043FD9E`, line 545 =
  `0x221`), `lv_obj_get_height` (`0x0043FDDA`, line 552 = `0x228`),
  `lv_obj_get_content_width` (`0x0043FE16`, line 559 = `0x22F`),
  `lv_obj_get_content_height` (`0x0043FE70`, line 569 = `0x239`),
  `lv_obj_get_child` (`0x0044DCE2`, line 337 = `0x151`).
- The `0x0048C7B4/0x0048C7D8` three-term sums
  (margin_left+width+margin_right, margin_top+height+margin_bottom)
  are the verbatim bodies of flex's `lv_obj_get_width_with_margin` /
  `lv_obj_get_height_with_margin`; no other upstream function has that
  shape (`lv_obj_get_content_*` subtract instead).
- `calc` is confirmed statement-for-statement: empty-container 32-byte
  memzero, rows-then-cols order, pad_column/pad_row gaps, base_dir RTL
  check feeding `grid_align`'s reverse flag, CONTENT-gated auto flags
  from the `w_layout` (bit 11) / `h_layout` (bit 10) halfword at
  obj+`0x2A` (matching `_lv_obj_t` bitfield order in
  `src/core/lv_obj_private.h`), and grid_w/grid_h stores at calc
  words 6/7.
- `grid_update` is confirmed instruction-for-instruction against the
  disassembly: `calc` call, 16-byte hint memzero, space_left/top,
  scroll-corrected origin at hint+8/+12 from coords+`0x14`/`0x18`,
  per-child retained-`item_repos` loop over spec_attr children/count
  (+`0x08`+`0x00`/`0x30`), `calc_free`, `LV_SIZE_CONTENT`
  (`0x3FFFFFFF`, materialized as `mvns r1, #0xC0000000`)-gated
  refresh, and the `(obj, 0x33, NULL)` event send
  (`LV_EVENT_LAYOUT_CHANGED` is index 51 in the vendored
  `src/misc/lv_event.h`).
- `lv_grid_init` is confirmed by the stored callback value
  (`0x48CA3D` = the `grid_update` entry with the Thumb bit), which is
  independently identified above.
- `0x0048C80E` resolves through the `0x00454746` wrapper to the
  `__aeabi_memset`-shaped core at `0x0043C0E4`; with `(dst, 0, len)`
  it is the out-of-line `lv_memzero`. `0x0048C7FC` is the 16-byte
  `lv_area_copy` (stock word-copy order equals upstream field order).

Deliberate port deviations (behavior-preserving, noted in code):

- The `grid_update` child-vector reads are hoisted out of the loop;
  `item_repos` cannot mutate the vector under its upstream contract,
  so the trip sequence is identical.
- `count_tracks` returns the count in C; the stock body only leaves it
  in r0 (which is exactly what its callers consume).
- `lv_grid_init` reproduces the two register stores with the anchor
  taken from the stock literal-pool word at `0x0048D3A0`
  (`0x2006F548`); the anchor's decomposition into global-plus-slot is
  link-time and stays a named constant until the lv_global layout is
  recovered.
- Signed-overflow order in the margin sums follows the stock
  instruction order; inputs are pixel geometry (no overflow domain).

## What remains

| Stock span | Bytes | Status | Note |
| --- | ---: | --- | --- |
| `0x0048CBF8..0x0048CDEC` | 500 | ported (second wave) | `calc_cols` in `lvgl_grid_engine.c`; 18-test host suite covers fixed/FR/CONTENT/subgrid/WARN paths |
| `0x0048CDEC..0x0048CFE0` | 500 | ported (second wave) | `calc_rows` (row twin), same suite |
| `0x0048CFE0..0x0048D3A0` | 960 | ported (second wave) | `item_repos`, same suite (placement/RTL/STRETCH/pct/guards) |
| `0x0048D3C8..0x0048D4D0` | 264 | ported (second wave) | `grid_align`, same suite (all six aligns, auto, reverse, single-track) |
| `0x0048D4E8..0x0048D53E` | 86 | out of scope | already a generated-source entry replacement in the flash plan (bounded string-length leaf) |
| `0x0048D540..0x0048D724` | ~480 (12 fns) | unidentified | not LVGL-shaped: strcpy-like, struct init, pixel/classifier helpers, RNG-backed (calls `0x004D5888`) retry loop, global flag set/get/mask; needs its own investigation |
| `0x0048D724..0x0048D866` | 318 | unidentified | calls into `0x004Dxxxx` and `0x00439CB2`; needs its own investigation |
| `0x0048D3A0..0x0048D3C8` | 40 | data | literal pool / assert-pointer words (`0x2006F548` anchor, `LV_GRID_FR(0)`/`CONTENT`/`TEMPLATE_LAST`/`COORD_MIN` constants, assert strings); derivable constants are used symbolically in the ports, assert pointers stay stock |
| overlay routing | — | follow-up | the 53 ports are not yet registered in `core_overlay/overlay.json` (`relocated_leaves` + `patch_sites`, modeled on `integrate_g2_apollo_draw_style_getters_overlay.py`), the core-source manifest pins are untouched, and `tools/transparent/reviewed_sources.json` is untouched; flash-plan bytes for this range remain `official_blob` |

Hardware qualification stays blocked by unavailable physical evidence;
no flashing, DFU, MMIO probing, signing, or publishing was performed.

## Second wave, 2026-09-11 evening (AM-040 continued)

The four identified-but-unported grid internals are now recovered as
reviewed MIT C in the same `lvgl_grid_engine.c` (now 28 functions,
3,074 bytes): `open_cfw_lvgl_grid_calc_cols` (stock `0x0048CBF8`,
500 B), `open_cfw_lvgl_grid_calc_rows` (`0x0048CDEC`, 500 B),
`open_cfw_lvgl_grid_item_repos` (`0x0048CFE0`, 960 B), and
`open_cfw_lvgl_grid_align` (`0x0048D3C8`, 264 B). 53 of the item's 64
functions (3,336 of 4,102 function bytes) are now reviewed C; the
item stays `partial`.

Identity deltas beyond the first wave (all checked against
`g2/third_party/lvgl`, commit `344c7c3...`, and the stock bytes):

- The stock rodata pointer at `0x0048D3B0` resolves to the vendor
  build path
  `D:\01_workspace\s200_ap510b_iar_git\third_party\lvgl_v9.3\LVGL\src\layouts\grid\lv_grid.c`,
  naming the exact upstream file; the sibling words are the
  `LV_LOG_WARN` message/function-name pointers consumed by the two
  subgrid-miss paths (assert lines `0x11D`/`0x179`), reproduced as
  named address constants.
- `DAT_0048D3A4/D3B8/D3B4/D3BC` are `LV_COORD_MAX-100`
  (`0x1FFFFF9B`, FR base), `LV_COORD_MAX-101` (`0x1FFFFF9A`,
  CONTENT), `LV_COORD_MIN` (`0xE0000001`), and
  `IGNORE_LAYOUT|FLOATING|HIDDEN` (`0x60001`), each equal to the
  vendored `lv_area.h`/`lv_obj.h` macro expansion.
- `item_repos` event codes are `LV_EVENT_SIZE_CHANGED` (`0x31`) and
  `LV_EVENT_CHILD_CHANGED` (`0x2A`) per the vendored `lv_event.h`
  order; `w_layout`/`h_layout` are bits 11/10 at obj+`0x2A`;
  out-of-range aligns fall into START exactly as the stock branch
  structure does; the size-change block rewrites both axes whenever
  either differs (as stock does).
- `calc_cols`/`calc_rows` return void like upstream; the stock
  trailing words (content width / caller-discarded garbage) are
  leftovers no caller consumes (`calc` discards them).
- One deliberate test hook: the template-array reads go through
  `OPEN_CFW_LVGL_GRID_COL_TEMPL`/`ROW_TEMPL` (production default is
  the verbatim getter dereference) because a 64-bit host cannot
  round-trip an array pointer through the 32-bit style-core return;
  getter-to-core forwarding itself is pinned by the first-wave
  wrapper tests.

Trailing-cluster survey (still retained, for the next run):

| Stock span | Bytes | Finding |
| --- | ---: | --- |
| `0x0048D540..0x0048D558` | 24 | `strcpy` (NUL-inclusive byte loop, returns dst); likely IAR DLib — needs iar-dlib family confirmation, not LVGL |
| `0x0048D558..0x0048D568` | 16 | 3-word struct init from `DAT_0048D568/56C` + `0x400`; referent unidentified |
| `0x0048D570..0x0048D588` | 24 | nibble-to-mode map (1-2→4, 6→0, else 7); helper of the next row |
| `0x0048D588..0x0048D620` | 152 | display mode/state switch over globals `0x0048D704/708`, calls `0x004C44BC/004C4530` (both 116 B, still decompiled) |
| `0x0048D620..0x0048D654` | 52 | flag getter over the same globals |
| `0x0048D654..0x0048D670` | 28 | RNG wrapper around `0x004D5888` (28 B, decompiled) |
| `0x0048D670..0x0048D6DC` | 108 | RNG-backed retry loop with IRQ guard, tables at `0x0048D70C/720` |
| `0x0048D6DC..0x0048D6E6` | 10 | global flag OR-set at `0x0048D710` |
| `0x0048D6E6..0x0048D6F0` | 10 | global store at `0x0048D718`, returns word at `0x0048D714` |
| `0x0048D6F0..0x0048D704` | 20 | masked global get (`0x0048D714 & 0x0048D710` when arg nonzero) |
| `0x0048D724..0x0048D866` | 318 | `strtoul`-shaped integer parser (base detect, `0x`-prefix skip, leading zeros, overflow → `0xFFFFFFFF` + errno-style flag via `0x00439CB2`); callees `0x004D58AE/C2`, `0x004D40E0` all still decompiled — iar-dlib candidate, needs family confirmation |

None of the eleven is LVGL-shaped; none is ported here.

Routing still open (unchanged): none of the 53 ports is registered
in `core_overlay/overlay.json`, the core-source manifest, or
`tools/transparent/reviewed_sources.json`; flash-plan bytes for the
whole range remain `official_blob`. The recipe is an integrate script
modeled on `tools/integrate_g2_apollo_draw_style_getters_overlay.py`
(prepare → lock → core-component → promote → sync-manifest →
pin-package), with cross-TU relocations from `lvgl_grid_engine.c`
into `lvgl_layout_style_getters.c` as `target_function` entries.

## Verification performed

- `python3 -m unittest tests.test_runtime_lvgl_grid_engine` — 18
  tests pass on macOS (Apple clang 21.0.0): stock-body SHA-256 pins
  for all 49 functions against `ota_s200_firmware_ota.bin`, getter
  (obj, part, property) forwarding incl. the six `uxtb` narrowings,
  part-zero grid-wrapper forwarding, space branch behavior, margin
  sums, div-round cases incl. negative truncation, area/memzero byte
  moves, track counting, free order, empty/full `calc` sequences
  (RTL/reverse, auto-flag, align-arg order, grid_w/grid_h stores),
  full `grid_update` sequences (child order, hint origin math,
  CONTENT-gated refresh, `0x33` event), and `grid_init` stores.
- Freestanding target-profile syntax check passes for both new
  translation units (`--target=thumbv7em-none-eabi -mcpu=cortex-m55
  -O2 -ffreestanding -fno-jump-tables -fomit-frame-pointer
  -fno-builtin -mno-unaligned-access -fno-unwind-tables
  -fno-asynchronous-unwind-tables -fropi -Wall -Wextra -Werror`).
- Not run: `make -C g2 core-component`, `make -C g2 source`,
  `verify-artifacts`, `make -C g2 transparent-test` (no shared build
  inputs were changed; the new units are not yet overlay-registered).

Second-wave verification (2026-09-11 evening):

- `python3 -m unittest g2.tests.test_runtime_lvgl_grid_calc
  g2.tests.test_runtime_lvgl_grid_engine` — 36 tests pass on macOS
  (18 new + 18 first-wave): stock-body SHA-256 pins for all four new
  functions, fixed/FR/CONTENT distribution, widest-visible-child
  measurement with hidden/span/pos filters, subgrid borrow-and-free
  (free order pinned), double-NULL WARN level/line, row-twin
  coverage, full `item_repos` sequences (START placement math,
  STRETCH resize with `0x31`/`0x2A` events, CENTER/END, RTL mirror,
  early guards, positive/negative/plain translate), and all six
  `grid_align` modes plus auto/reverse/single-track.
- The same freestanding target-profile syntax check passes for the
  extended `lvgl_grid_engine.c` (the four ports live in the existing
  file, so no new translation unit).
- Two test-expectation bugs found during development are recorded
  here, not hidden: spaced `grid_align` modes accumulate the grid
  span with the gap first zeroed (pure track sum, e.g. 60 not 70),
  and the size-change block rewrites both axes whenever either
  differs — both match the stock body and the port was already
  faithful; only the expectations were corrected.
- Not run (unchanged): `make -C g2 core-component`, `make -C g2
  source`, `verify-artifacts`, `make -C g2 transparent-test`.
  Routing the 53 ports is the remaining production step.

## Third wave, 2026-09-11 evening (AM-040 continued): overlay routing

All 53 LVGL ports plus the 11 trailing string/state ports (64 leaves,
4,966 compiled bytes) are now registered in
`components/apollo_main/core_overlay/overlay.json` with 64 `B.W` patch
sites by `tools/integrate_g2_apollo_am040_overlay.py`. Selectors are
ordered callee-before-caller (style getters first, grid update last;
nibble map before the mode switch, vote before the retry loop) because
the builder resolves `target_function` relocations only against
already-placed overlay functions. Leaves carry
`allow_discarded_alloc_sections` (multi-function TUs, 291 precedents).
Placement pins were filled by the script's `compute-pins` step, which
replicates the builder's hermetic compile, align-up placement, and
`encode_thumb_branch` relocation encoding exactly; the canonical build
then verifies all 64 leaves (any divergence fails closed there).

Notes for the next run: the AM-019 recorder recipe
(prepare → record-profile build → promote) is not runnable — the
component builder rejects `--record-profile`, and the AM-019 script's
own 27 leaves were never actually routed. `reviewed_sources.json` was
deliberately left untouched (1999 routed leaves, 4 entries: live
practice routes via the overlay only, and strtoul's split ranges are
ineligible there). The flash-plan/manifest/package steps are blocked on
the pre-existing LLD/toolchain drift and the foreign manifest edit
described in `progress.md`; the holder words, literal pool, and pads
remain retained data.

## Fourth wave, 2026-09-12 (stage re-verification under the live tree)

A private replica of the canonical core-stage overlay build (same
`_stage_config` + `apollo_overlay.build`, apple-clang, outputs under
`g2/build/continue-analysis/AM-040/core-stage-check/`) verifies all
2,058 stage leaves including all 64 AM-040 leaves, with overlay pins
unchanged at size 385,460 / sha `8c93066a…`. 52/52 host tests pass via
the documented `python3 -m unittest` path, all four translation units
pass the freestanding target-profile compile with `-Werror`, and the
`transparent-test` trio passes 39/39. The full `core-component` build
still aborts downstream of the overlay stage in the LC3 service-audio
route experiment (pins Homebrew LLD 23.1.0, host has 23.1.1 — LC3
lane's environment drift, untouched here), so the shared build
report, manifest `sync-manifest`, flash-plan flip, and
`verify-artifacts` remain for the re-run after that drift is resolved;
the `littlefs-snapshot` aggregate re-pin must land atomically with
that green full build (overlay pins above plus the full-build
component pins, which cannot be produced while the build aborts).

## Fifth wave, 2026-09-12 (AM-040 re-run: recorder cleanup + stage re-verification)

The live tree still held all 64 AM-040 leaves with filled pins (28 in
`lvgl_grid_engine.c`, 25 in `lvgl_layout_style_getters.c`, 9 in
`runtime_peripheral_state_helpers.c`, 2 in `runtime_string_helpers.c`;
offsets `380444..385460`, ending exactly at `overlay_size`), but in the
intermediate `prepare` state: every overlay item (3,534) carried the
`apollo-am040-grid-state-record` profile and the recorder key sat in
`toolchain_profiles` (`promote` never ran because the recorder-profile
build flow is rejected by the component builder). Under the
integration lock this run stripped the recorder profile from all
3,534 items plus the `toolchain_profiles` key (round-trip
byte-identical otherwise; `compute-pins` correctly refuses a second
run since it resolves `target_function` relocations one-shot — pins
were already filled, 0 zero-sha). `overlay.json` round-trips through
`json.dumps(indent=2)` byte-identically, and the remaining diff vs
HEAD is exactly the AM-040 registration (64 leaves + 64
`replace_apollo_am040_*` patch sites + functions list + expected
sizes); no other lane's entries were touched.

Verification under the live tree: a fresh private replica of the
canonical core-stage build (`build/continue-analysis/AM-040/
stage_replica.py`, same `_stage_config` + `apollo_overlay.build`,
outputs under `core-stage-check-rerun/`) verifies all 2,063 stage
leaves including all 64 AM-040 leaves — overlay 385,460 bytes /
`8c93066a…` matches `expected`, stage component 3,908,856 bytes /
`c8945453…` matches `core_stage_expected`. Host suites pass 52/52
(`test_runtime_lvgl_grid_engine`, `test_runtime_lvgl_grid_calc`,
`test_runtime_str_state_helpers`); `make -C g2 transparent-test`
passes 39/39.

Still open (not this item's scope to re-pin): the full
`core-component` build aborts downstream of the overlay stage in the
LC3 service-audio route experiment on the pre-existing toolchain
drift (pinned Homebrew LLD 23.1.0 vs host 23.1.1, LC3 lane's), and
`vendor-snapshots` stops earlier at `littlefs-snapshot`, whose
aggregate pins (`overlay_size` 380444 / `21095c67…`) predate the
AM-040 registration and must be re-pinned atomically with the green
full build. So the manifest sync, flash-plan flip (range still
`official_blob`), and `verify-artifacts` remain for the re-run after
that drift is resolved. Four overlapping placeholder leaves
(`tinyframe_cksum/crc32/crc16` at offset 0, `freertos_port_start_
scheduler` vs `at_nus_handler_linux`) belong to other lanes and were
left untouched. Hardware qualification stays blocked by unavailable
physical evidence; no flashing, DFU, MMIO probing, signing, or
publishing was performed.

Rerun + pool decode 2026-09-12 (AM-040): 52/52 host tests re-pass
(`test_runtime_lvgl_grid_engine`, `test_runtime_lvgl_grid_calc`,
`test_runtime_str_state_helpers`); all four TUs recompile
warning-free for Cortex-M55 under clang. The 40-byte literal pool at
`0x0048D3A0..0x0048D3C8` is now fully decoded (capstone, Thumb-2
PC-relative LDR): anchor `0x2006F548`, FR_BASE `0x1FFFFF9B`, cols
format `0x0073F5AC`, cols func `0x0078AEEC`, file `0x006E079C`,
COORD_MIN `0xE0000001`, CONTENT `0x1FFFFF9A`, IGNORE_MASK
`0x00060001`, rows format `0x0073F5D8`, rows func `0x0078AEF8`.
Eight words are folded as named constants in
`lvgl_grid_engine.c`; the format words resolve to "No col
descriptor found even on the parent" / "No row descriptor found
even on the parent", the file word to the vendor fork's own
`lv_grid.c` path, and the func words to `calc_cols`/`calc_rows`.

Finding: the stock double-NULL WARN paths (cols
`0x48CC1E..0x48CC32`, rows `0x48CE12..0x48CE26`) pass five args to
retained `lv_log` at `0x0044D25C` (level/file/line/func in r0-r3,
format on the stack), but `OPEN_CFW_LVGL_RETAINED_LOG_WARN` passes
four (no format). Host tests pin level/line/call-count only, so this
is invisible to them; on target the callee would read a stale stack
word as the format pointer. Follow-up once the LC3 LLD drift
unblocks promotion: extend the macro with source-authored format
literals, re-promote `calc_cols`/`calc_rows` pins, and assert the
format argument in the host tests. Production C and pins are
therefore unchanged by this turn.

## Sixth wave, 2026-09-12 (AM-040 independent re-verification)

No production files were changed by this run; every claim below was
re-observed against the live tree. All 64 work-item function starts
have exactly one `replace_apollo_am040_*` patch site each (no missing,
no extras), and a fresh `compile_inventory()` matches all 64 overlay
leaf pins (size + unrelocated SHA-256, 64/64). The private canonical
core-stage replica (`build/continue-analysis/AM-040/stage_replica.py`,
outputs under `core-stage-check-rerun/`) is green: 2,063/2,063 stage
leaves verified including all 64 AM-040 leaves, overlay 385,460 bytes
/ `8c93066a…` matching `expected`, stage component 3,908,856 bytes /
`c8945453…` matching `core_stage_expected`. All four TUs recompile
warning-free (`-Werror`, Cortex-M55 profile). Host suites pass 52/52
via `python3 -m unittest g2.tests.test_runtime_lvgl_grid_engine
g2.tests.test_runtime_lvgl_grid_calc
g2.tests.test_runtime_str_state_helpers`; the transparent trio
(`test_transparent_reviewed_source`, `test_transparent_runtime`,
`test_transparent_source_pipeline`) passes 39/39.
`test_report_transparent_coverage_release_gate` fails 3/11 on the
pre-existing whole-image state (7,370 placed functions still on
unreviewed decompilation) — unrelated to this range, no change made.
The flash plan still lists the range as `official_blob`; the flip
awaits the LC3 lane's LLD drift resolution (host Homebrew LLD 23.1.1
vs the pinned 23.1.0 downstream of the overlay stage) plus the atomic
manifest re-pin, neither in this item's scope. The dropped-WARN-format
follow-up above is unchanged. No image was signed, flashed, or
installed. Hardware qualification stays blocked by unavailable
physical evidence.

Re-run 2026-09-12 (AM-040): all of the above re-verified under the
live tree with no production changes. `make -C g2 core-component`
was attempted under the integration lock and stops at the
`littlefs-snapshot` prerequisite before any compile:
`third_party/littlefs/verify_snapshot.py` pins the whole-overlay
aggregate at 380,444 bytes / `21095c67…`, while the live
`overlay.json` `expected` is 385,460 / `8c93066a…` (includes these 64
leaves plus other lanes' uncommitted overlay growth), so the atomic
re-pin cannot land from this lane without blessing foreign mid-flight
work. The production manifest still carries zero `apollo_am040_`
regions (`sync-manifest` needs a fresh `build-report.json`, stale at
1,994/2,063 leaves from Sep 7), and `reviewed_sources.json` still
lists only the 4 Cortex-M55-tranche functions, so the transparent
image still traps these 64 (transparent admission needs per-function
`expected_text` compiles; follow-up, not attempted here). 52/52 host,
private replica 2,063/2,063 green, 39/39 transparent trio re-passed
this run. No image was signed, flashed, or installed. Hardware
qualification stays blocked by unavailable physical evidence.

Re-run 2026-09-12 (AM-040): narrowed the canonical-build blockage one
layer deeper under the integration lock. Behind the `littlefs-snapshot`
prerequisite gate, `build_component.py` itself refuses the default path
with `apple-clang: reviewed toolchain identity drift`. The throw site is
the LC3 service-audio route-experiment toolchain gate
(`components/apollo_main/liblc3_encoder/build_service_audio_route_experiment.py`,
version-prefix check), reached unconditionally through
`build_service_audio_production_replay` (`build_component.py:1569`) even
without `--record-canonical`: host Homebrew LLD reports 23.1.1 while the
reviewed pin demands the 23.1.0 prefix, and no second LLD exists on this
Mac (only `/opt/homebrew/Cellar/llvm/23.1.1`; no `OPENCFW_LLD` override
in the replay path). Re-pinning the LC3 lane's toolchain identity or
restoring LLD 23.1.0 belongs to that lane, not this item, so the
production `source` build, flash-plan flip, manifest splice, and
`verify-artifacts` stay blocked. Re-verified this turn with no tree
changes: 52/52 AM-040 host tests pass, the private stage replica is
green (2,063/2,063 leaves incl. 64/64 AM-040, overlay 385,460 /
`8c93066a…`, stage component matching `core_stage_expected`), on-disk
TU hashes match all four leaf source pins, and
`make -C g2 transparent-test` passes 39/39. No image was signed,
flashed, or installed. Hardware qualification stays blocked by
unavailable physical evidence.

Re-run 2026-09-12 (AM-040): re-verified with no production tree
changes. 52/52 AM-040 host tests pass
(`test_runtime_lvgl_grid_engine`, `test_runtime_str_state_helpers`,
`test_runtime_lvgl_grid_calc` via unittest); the private stage
replica is green (2,063/2,063 leaves incl. 64/64 AM-040, overlay
385,460 / `8c93066a…`, stage component matching
`core_stage_expected`), which also proves warning-free TU compiles
(the stage path builds with `-Wall -Wextra -Werror`); and
`make -C g2 transparent-test` passes 39/39. Read-only probes confirm
both canonical-build blockers are unchanged: host LLD is still
23.1.1 (LC3 lane's 23.1.0-prefix gate), and the `littlefs-snapshot`
aggregate still pins 380,444 / `21095c67…` against live 385,460 /
`8c93066a…`, so no lock-gated rebuild or re-pin was attempted from
this lane. New evidence on the transparent-admission follow-up: the
style-getter TU compiled under the transparent profile
(`armv8.1m.main`, Cortex-M55, `-Oz`) emits 12 bytes for
`open_cfw_lvgl_get_style_width` (`ldr/movs/bx/nop` + absolute target
word) against the 10-byte stock body at `0x0048C81A`, with different
bytes — the behavioral MIT leaves cannot satisfy the transparent
`payload == stock` contract (`test_transparent_reviewed_source`
asserts byte equality for every entry but `0x442228`), so
`reviewed_sources.json` admission stays infeasible without weakening
that gate; the production `B.W`-redirect route is unaffected. Range
`0x0048C7B4..0x0048D866` therefore stays `official_blob` in the
flash plan pending the LC3-lane drift fix and the atomic
littlefs-aggregate re-pin. No image was signed, flashed, or
installed. Hardware qualification stays blocked by unavailable
physical evidence.

Re-run 2026-09-12 (AM-040): re-verified with no production tree
changes. 52/52 host tests pass (36 grid + 16 string/state via
unittest); the private stage replica is green (2,063/2,063 leaves
incl. 64/64 AM-040, overlay 385,460 / `8c93066a…` unchanged,
proving warning-free TU compiles under the builder's
`-Wall -Wextra -Werror` stage path); `make -C g2 transparent-test`
passes 39/39. Lock-gated `core-component` still stops at the
foreign `littlefs-snapshot` drift and the Apple-clang identity
drift (host clang 21.0.0) — both pre-existing, neither from this
item. Range `0x0048C7B4..0x0048D866` stays `official_blob`;
manifest splice and `reviewed_sources.json` admission remain
follow-ups. No image was signed, flashed, or installed. Hardware
qualification stays blocked by unavailable physical evidence.

Re-run 2026-09-12 (AM-040, session 84e175ec): re-verified with no
production tree changes. 52/52 host tests pass
(`test_runtime_lvgl_grid_engine`, `test_runtime_lvgl_grid_calc`,
`test_runtime_str_state_helpers` via
`python3 -m unittest g2.tests.test_runtime_lvgl_grid_engine g2.tests.test_runtime_lvgl_grid_calc g2.tests.test_runtime_str_state_helpers`);
the private stage replica (`g2/build/continue-analysis/AM-040/stage_replica.py`,
outputs under `core-stage-check-rerun/`, no integration lock needed)
is green: 2,063/2,063 stage leaves incl. 64/64 AM-040, overlay
385,460 bytes / `8c93066a…` matching `expected`, stage component
3,908,856 bytes / `c8945453…` matching `core_stage_expected`
(stage path builds with `-Wall -Wextra -Werror`, so warning-free TU
compiles are proven); `make -C g2 transparent-test` passes 39/39.
Read-only probes confirm both canonical-build blockers unchanged:
host LLVM is 23.1.1 (LC3 lane pins the 23.1.0 prefix) and the
`littlefs-snapshot` aggregate still predates the AM-040 registration,
so no lock-gated `core-component`/`source` rebuild, manifest splice,
or re-pin was attempted from this lane. Range `0x0048C7B4..0x0048D866`
stays `official_blob`; the holder-table source-authoring follow-up
(8 live-read words at `0x0048D704..0x0048D720`, see
`g2-display-state-string-helpers-closure.md`) and the transparent
`payload == stock` negative result stand. No image was signed,
flashed, or installed. Hardware qualification stays blocked by
unavailable physical evidence.

Re-run 2026-09-12 (AM-040): full 64-function transparent-envelope
survey corroborates the admission negative result with exact numbers.
All four TUs recompile cleanly under the transparent profile
(`--target=armv8.1m.main-none-eabi -mcpu=cortex-m55 -mthumb
-ffreestanding -fno-builtin -ffunction-sections -Oz`; objects under
`g2/build/continue-analysis/AM-040/probe/`), and per-symbol
`.text` sizes (toolchain `llvm-size`) were compared against the
stock envelopes in `overlay.json` `patch_sites`: 27 FIT (text size
<= envelope, incl. the ten 6-byte grid forwards, both 36-byte
`with_margin` leaves, `memzero` at exactly 12/12, `calc` 256/258,
`item_repos` 860/960, `mode_switch` 140/152) and 37 OVER (all 25
style getters at 12-16 bytes vs 10-12 envelopes, `strtoul` 340/322,
`calc_cols` 508/500, `calc_rows` 504/500, `grid_update` 188/156,
`grid_init` 24/20, `area_copy` 20/18, `sample_retry` 116/108,
`sample_vote` 36/28, `value_get` 24/20, flag/latch 16/10).
`place_unit` lays down every allocatable section of the unit object,
so even the FIT set needs per-function file splits (the multi-
function TUs also emit 9 `OUTLINED_FUNCTION_*` sections) plus
`.rodata` literal-pool accounting before any `reviewed_sources.json`
row could be pinned; reviewed-source units are never relocated, so
the 37 OVER functions cannot be admitted without weakening that
gate. No manifest or overlay change was made from this lane. No
image was signed, flashed, or installed. Hardware qualification
stays blocked by unavailable physical evidence.

Re-run 2026-09-12 (AM-040, session 121a9119): re-verified with no
production tree changes. 52/52 host tests pass
(`test_runtime_lvgl_grid_engine` 18, `test_runtime_lvgl_grid_calc`
18, `test_runtime_str_state_helpers` 16); the 4 transparent test
modules (`test_report_transparent_coverage_release_gate`,
`test_transparent_reviewed_source`, `test_transparent_runtime`,
`test_transparent_source_pipeline`, run via unittest discover) pass
39/39. The private stage replica
(`g2/build/continue-analysis/AM-040/stage_replica.py`) is green:
2,063/2,063 stage leaves incl. 64/64 AM-040, overlay 385,460 bytes /
`8c93066a…` matching the canonical pins, component matching the
stage pin. All 64 `replace_apollo_am040_*` patch sites resolve to
relocated leaves with filled size/sha256 pins. Flash plan
(`g2/build/source/flash-plan.json`, Sep 11 20:45, newer than the
Sep 11 19:46 registration) still shows the range `official_blob`.
Canonical-build blockers unchanged (host LLD 23.1.1 vs pinned
23.1.0), so no lock-gated rebuild or manifest splice was attempted.
No image was signed, flashed, or installed. Hardware qualification
stays blocked by unavailable physical evidence.

Re-run 2026-09-12 (AM-040): re-verified with no production tree changes.
52/52 host tests pass (`test_runtime_lvgl_grid_engine`,
`test_runtime_lvgl_grid_calc`, `test_runtime_str_state_helpers` via
`python3 -m unittest`); the private stage replica
(`g2/build/continue-analysis/AM-040/stage_replica.py`) is green:
2,063/2,063 stage leaves incl. 64/64 AM-040, overlay 385,460 bytes /
`8c93066a…` matching `expected`, stage component 3,908,856 bytes /
`c8945453…` matching `core_stage_expected` (canonical `expected`
`7bfc8a60…` still stale — another lane's drift, not this item's);
`make -C g2 transparent-test` passes 39/39. Read-only probes confirm
both canonical-build blockers unchanged: host LLD is 23.1.1 and the
flash plan (Sep 11 20:45) still shows `0x0048C7B4..0x0048D866`
`official_blob`, so no lock-gated `core-component`/`source` rebuild,
manifest splice, holder-table const authoring, or
`reviewed_sources.json` admission was attempted (37 OVER envelopes +
`OUTLINED_FUNCTION_*` sections still forbid admission under the
no-relocation gate). No image was signed, flashed, or installed.
Hardware qualification stays blocked by unavailable physical evidence.

Re-run 2026-09-12 (AM-040): re-verified with no production tree changes.
All four TUs (`lvgl_grid_engine.c`, `lvgl_layout_style_getters.c`,
`runtime_string_helpers.c`, `runtime_peripheral_state_helpers.c`)
recompile warning-free under the canonical Cortex-M55 flags
(`--target=thumbv7em-none-eabi -mthumb -mcpu=cortex-m55 -O2
-ffreestanding -fno-builtin -fropi -Wall -Wextra -Werror`, private
objects under `g2/build/continue-analysis/AM-040/tu-check/`); 52/52
host tests pass via `python3 -m unittest`
(`test_runtime_lvgl_grid_engine`, `test_runtime_lvgl_grid_calc`,
`test_runtime_str_state_helpers`); `make -C g2 transparent-test`
passes 39/39. Overlay still carries all 64 `replace_apollo_am040_*`
patch sites; flash plan still shows `0x0048C7B4..0x0048D866`
`official_blob`. Read-only probes confirm both canonical-build
blockers unchanged (Homebrew LLD 23.1.1 vs pinned 23.1.0; Apple
clang 21.0.0 identity drift), so no lock-gated rebuild, manifest
splice, or admission was attempted. No image was signed, flashed,
or installed. Hardware qualification stays blocked by unavailable
physical evidence.

Re-run 2026-09-12 (AM-040): re-verified with no production tree changes
by this lane. 52/52 host tests pass (`test_runtime_lvgl_grid_engine`,
`test_runtime_lvgl_grid_calc`, `test_runtime_str_state_helpers` via
`python3 -m unittest`); all four TUs recompile warning-free under the
canonical Cortex-M55 flags (private objects under
`g2/build/continue-analysis/AM-040/tu-check/`); the private stage
replica is green (64/64 AM-040 leaves, overlay 385,460 bytes /
`8c93066a…` matching `expected`, stage component 3,908,856 bytes /
`c8945453…` vs canonical `7bfc8a60…` still stale — another lane's
drift, not this item's); `make -C g2 transparent-test` passes 39/39.
Overlay still carries all 64 `replace_apollo_am040_*` patch sites;
flash plan still shows `0x0048C7B4..0x0048D866` `official_blob`.
Read-only probes confirm the canonical-build blocker unchanged
(Homebrew LLD 23.1.1), so no lock-gated rebuild, manifest splice, or
admission was attempted. No image was signed, flashed, or installed.
Hardware qualification stays blocked by unavailable physical evidence.

Re-run 2026-09-12 01:48 (AM-040): re-verified with no production tree changes
by this lane. 52/52 host tests pass (`test_runtime_lvgl_grid_engine`,
`test_runtime_lvgl_grid_calc`, `test_runtime_str_state_helpers` via
`python3 -m unittest`); all four TUs recompile warning-free under the
canonical Cortex-M55 flags (fresh private objects under
`g2/build/continue-analysis/AM-040/tu-check-rerun/`); the private stage
replica is green (2,063/2,063 stage leaves incl. 64/64 AM-040, overlay
385,460 bytes / `8c93066a…` matching `expected`; stage component
3,908,856 bytes / `c8945453…` vs canonical `7bfc8a60…` still stale —
another lane's drift, not this item's); `make -C g2 transparent-test`
passes 39/39. Overlay still carries all 64 `replace_apollo_am040_*`
patch sites; flash plan still shows `0x0048C7B4..0x0048D866`
`official_blob`. Read-only probes confirm both canonical-build blockers
unchanged: host LLD is 23.1.1 (vs pinned 23.1.0) and
`g2/third_party/littlefs/verify_snapshot.py` still fails on the stale
scalar-tag aggregate pins, so no lock-gated rebuild, manifest splice, or
`reviewed_sources.json` admission was attempted. No image was signed,
flashed, or installed. Hardware qualification stays blocked by
unavailable physical evidence.

Re-run 2026-09-12 (AM-040): no production changes. 52/52 host tests pass
(`test_runtime_lvgl_grid_engine`, `test_runtime_lvgl_grid_calc`,
`test_runtime_str_state_helpers`), all four TUs recompile `-Werror` clean
for `armv8.1m.main`/`cortex-m55`/`-Oz` (private objects under
`g2/build/continue-analysis/AM-040/tu-check/`), `make -C g2 transparent-test`
passes 39/39, and all 64 `replace_apollo_am040_*` patch sites remain
registered. Read-only probes confirm blockers unchanged (Homebrew LLD 23.1.1
vs pinned 23.1.0; flash plan still `official_blob` over
`0x0048C7B4..0x0048D866`), so no lock-gated rebuild, manifest splice, or
admission was attempted. No image was signed, flashed, or installed.
Hardware qualification stays blocked by unavailable physical evidence.

Re-run 2026-09-12 (AM-040): re-verified with no production tree changes.
52/52 host tests pass (`test_runtime_lvgl_grid_engine`,
`test_runtime_lvgl_grid_calc`, `test_runtime_str_state_helpers` via
`python3 -m unittest` from `g2/`); all four TUs recompile `-Werror` clean
for `thumbv7em`/`cortex-m55` (private objects under
`g2/build/continue-analysis/AM-040/tu-check-rerun2/`); the private stage
replica (`stage_replica.py`) is green with 2,063/2,063 stage leaves incl.
64/64 AM-040 (overlay 385,460 / `8c93066a…` matching `expected`, stage
component 3,908,856 / `c8945453…` matching `core_stage_expected`; the
canonical top-level `expected` `7bfc8a60…` stays stale from another lane);
`make -C g2 transparent-test` passes 39/39. Registration re-checked: all
64 work-item starts carry exactly one `replace_apollo_am040_*` patch site
each (no missing, no extras), 2,063 relocated leaves total.
`compute-pins` re-run refuses as designed (one-shot `target_function` ->
`target_address` resolution; pins already filled) — not a regression.
Read-only probes confirm both canonical-build blockers unchanged: host
LLD is 23.1.1 (only `/opt/homebrew/Cellar/llvm/23.1.1`) and
`third_party/littlefs/verify_snapshot.py` still fails on the stale
380,444 / `21095c67…` aggregate vs live 385,460 / `8c93066a…`, so no
lock-gated rebuild, manifest splice, or `reviewed_sources.json`
admission was attempted. Flash plan (Sep 11 20:45) still shows
`0x0048C7B4..0x0048D866` `official_blob`. No image was signed, flashed,
or installed. Hardware qualification stays blocked by unavailable
physical evidence.

Re-run 2026-09-12 (AM-040): re-verified with no production tree changes
by this lane. 52/52 host tests pass (`test_runtime_lvgl_grid_engine`,
`test_runtime_lvgl_grid_calc`, `test_runtime_str_state_helpers` via
`python3 -m unittest`); all four TUs recompile `-Werror` clean for
`thumbv7em`/`cortex-m55` (fresh private objects under
`g2/build/continue-analysis/AM-040/tu-check-20260912/`); the private
stage replica (`stage_replica.py`) is green (2,063/2,063 stage leaves
incl. 64/64 AM-040, overlay 385,460 bytes / `8c93066a…` matching
`expected`; stage component 3,908,856 / `c8945453…` matching
`core_stage_expected`); `make -C g2 transparent-test` passes 39/39.
Registration re-checked: 64 `replace_apollo_am040_*` patch sites, all
resolving to relocated leaves, 2,063 relocated leaves total. Read-only
probes confirm both canonical-build blockers unchanged (Homebrew LLD
23.1.1 vs pinned 23.1.0; flash plan still `official_blob` over
`0x0048C7B4..0x0048D866`), so no lock-gated rebuild, manifest splice,
or admission was attempted. No image was signed, flashed, or
installed. Hardware qualification stays blocked by unavailable
physical evidence.

Re-run 2026-09-12 (AM-040, no production changes): 52/52 host
tests, `transparent-test` 39/39, four-TU `-Werror` Cortex-M55
recompiles clean, and all four working-tree file sha256/sizes still
match the leaf pins (64/64 leaves, 64 patch sites, overlay 385,460 /
`8c93066a…`). Flash plan still `official_blob` over
`0x0048C7B4..0x0048D866`; splice still waits on the LC3-lane LLD
fix and the atomic littlefs re-pin. Hardware qualification stays
blocked by unavailable physical evidence.
