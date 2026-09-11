# G2 LVGL obj-style getters, transition engine, and tree-search closure

Status date: 2026-09-11
Scope: production-routed clean-room C for 27 of the 32 retained functions in
`0x0043E1FA..0x0043EF70` (Apollo main application, component `apollo_main`),
work item AM-004
Mode: reviewed source, host unit tests, `make -C g2 core-component` +
`make -C g2 source`, `verify-artifacts`; no flashing, signing, or hardware
operation

## Result

27 of the 32 retained functions in this span (1,126 of 3,248 function bytes)
are now produced from reviewed C, admitted through
`components/apollo_main/core_overlay/overlay.json` `patch_sites` (direct
whole-function `b_w` replacement; no relocation was required because every
covered function's stock body pins by size/SHA-256 as its own patch span):

| Stock span | Bytes | New source | Identity evidence |
| --- | ---: | --- | --- |
| `0x0043E1FA..0x0043E282` | 136 | `runtime_obj_spec_attr.c` `open_cfw_runtime_obj_allocate_spec_attr` | embedded assert-log string `"lv_obj_allocate_spec_attr"` at `0x0043EE34` (data word `0x0076DC7C`) |
| `0x0043E2BC..0x0043E2D4` | 24 | `runtime_obj_pointer_predicates.c` `open_cfw_runtime_obj_field_equals_or_null` | census link-order (low conf.); behavior fully recovered |
| `0x0043E2D4..0x0043E2EA` | 22 | `runtime_obj_pointer_predicates.c` `open_cfw_runtime_obj_pointer_chain_contains` | census link-order (low conf.); behavior fully recovered |
| `0x0043E2EA..0x0043E33E` | 84 | `runtime_obj_tree_search.c` `open_cfw_runtime_obj_is_valid` | algorithm match to LVGL `lv_obj_is_valid` (display/screen scan + recursive child search) |
| `0x0043EBEC..0x0043EE2C` | 576 | `runtime_obj_state_transition.c` `open_cfw_runtime_update_obj_state` | embedded assert-log string `"update_obj_state"` at `0x0043EE4C` (data word `0x00780EB8`); property ID `0x68` confirmed as `LV_STYLE_TRANSITION` |
| `0x0043EE54..0x0043EE94` | 64 | `runtime_obj_tree_search.c` `open_cfw_runtime_obj_valid_child` | recursion partner of `lv_obj_is_valid` above; shares its spec_attr children/count fields with `runtime_obj_spec_attr.c` |
| `0x0043EE94..0x0043EEA6` | 18 | `runtime_obj_record_copy16.c` `open_cfw_runtime_obj_copy_record16` | census link-order (low conf.); behavior fully recovered |
| `0x0043EEA6..0x0043EF70` | 202 (20 functions) | `runtime_obj_style_getters.c` | census call-topology to `LVGL/src/core/lv_obj_style.c` (medium conf.) + independent property-ID confirmation against the pinned upstream `lv_style.h` interval |

The remaining 5 functions (2,122 bytes: `0x0043E33E` 160B, `0x0043E442`
508B, `0x0043E63E` 104B, `0x0043E6A6` 300B, `0x0043E7D2` 1050B) are **not**
closed by this tranche; see "What remains" below. The item stays `partial`.

## Identity method

Two of the "no-census-row" functions singled out by this work item resolve
directly: the G2 Apollo build keeps `LV_USE_ASSERT_NULL`/`LV_USE_LOG`-style
assert diagnostics that embed the failing function's own name as a C string
argument to the shared log/assert call (`FUN_0044D25C`). Reading those
literal data words directly from
`blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin` (offline, read-only;
no device access) gives an authenticated identity independent of call-graph
census:

```
0x0043E298 -> 0x006E8890 "...\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj.c"
0x0043EE34 -> 0x0076DC7C "lv_obj_allocate_spec_attr"      (FUN_0043E1FA)
0x0043E290 -> 0x00761CB0 "Asserted at expression: %s (%s)"
0x0043E28C -> 0x0078B3F0 "obj != NULL"
0x0043E288 -> 0x00787610 "NULL pointer"
0x0043EE3C -> 0x007791FC "obj->spec_attr != NULL"
0x0043EE38 -> 0x00787640 "Out of memory"
0x0043EE50 -> 0x006E8890 "...\\lvgl_v9.3\\LVGL\\src\\core\\lv_obj.c"
0x0043EE4C -> 0x00780EB8 "update_obj_state"                (FUN_0043EBEC)
```

`FUN_0043EBEC` (`update_obj_state`) walks the object's local/cascaded style
list looking for `LV_STYLE_TRANSITION` descriptors (property ID `0x68`).
`0x68 == 104` is confirmed as `LV_STYLE_TRANSITION` against the official
LVGL `src/misc/lv_style.h` at both ends of the compatible interval
`60d976c466e8619326edfbd193fd2a046c10113f`..`344c7c318047b7348e1be8572a9fd4260c251cfa`
already pinned by
[`lvgl-version-recovery-audit.md`](lvgl-version-recovery-audit.md). The
same source confirms the 16 property IDs used by the 20 style getters at
`0x0043EEA6..0x0043EF70` (`runtime_obj_style_getters.c` header comment lists
the full ID table); every one of those getters is a two-argument
(`obj`, `part`) forward to the shared style-lookup core `FUN_0044BDEA`
(itself outside this item's byte range and therefore still a retained-stock
callee, tracked separately) with a distinct constant property ID appended.

`FUN_0043E2EA`/`FUN_0043EE54` match LVGL's public `lv_obj_is_valid` and its
static recursive helper (upstream names it `obj_valid_child`) by algorithm,
not by embedded name: the display iterator (`FUN_0044FA22`, matching
`lv_display_get_next`), the `screens`/`screen_cnt` fields at
`+0x2B8`/`+0x2D4` of the display struct, and the recursive descent through
each object's `lv_obj_spec_attr_t` children array/count (`+0x00`/`+0x30`,
the same fields `open_cfw_runtime_obj_allocate_spec_attr` initializes) are
an exact structural match for that pair.

`FUN_0043E2BC`, `FUN_0043E2D4`, and `FUN_0043EE94` remain identified only at
"lv_obj.c, low confidence" per the link-order census
(`../../tools/manifests/g2-lvgl-vendor-fork-census.tsv`); their exact
canonical LVGL names are **not** claimed. Their *behavior* (a null-safe
first-field equality test; a singly linked pointer-chain membership walk
starting one link past the head; an unconditional four-word record copy)
is fully recovered from the decompilation
(`../../research/corpus/apollo-main/ghidra/decomp/bundles/apollo-decomp-00.c`,
`FUN_0043e2bc`/`FUN_0043e2d4`/`FUN_0043ee94`) and reviewed source is routed
for it regardless of the open naming question.

## `update_obj_state` reconstruction confidence

This is the most structurally complex function closed by this tranche
(576 stock bytes). The overall shape -- classify the state-change via a
style-state-compare helper (`FUN_0044C178`, modeled here as returning the
same four-way `LV_STYLE_STATE_CMP_*`-shaped result LVGL's
`lv_style_state_cmp_t` uses: same / diff-redraw / diff-draw-pad /
diff-layout), commit `obj->state`, collect at most 32 deduplicated
transition candidates from every non-local style whose guard state is
satisfied by the new state, start each surviving transition, then dispatch
a final refresh by classification -- is reconstructed by direct,
field-by-field translation of the decompiled control flow (every scratch
record field, loop bound, and comparison in `runtime_obj_state_transition.c`
traces to a specific line in `FUN_0043ebec`; see the file's header comment
for the line-by-line correspondence). The four external callee roles named
in the header comment (`open_cfw_runtime_style_state_cmp`, the pre/post
invalidate hooks, the transition-descriptor lookup, `open_cfw_runtime_
start_transition`, `open_cfw_runtime_refresh_ext_draw`) are inferred from
their call shape and from the confirmed `LV_STYLE_TRANSITION` property ID,
not from an embedded name; they are still retained-stock callees at
addresses outside this item's range, tracked by their own future items.

## What remains

Five functions in this span are not yet source-routed and stay `partial`
followups for a future AM-004-successor item:

| Stock span | Bytes | Census attribution | Note |
| --- | ---: | --- | --- |
| `0x0043E33E..0x0043E3DE` | 160 | `LVGL/src/core/lv_obj_scroll.c` (medium conf.) | coordinate/flag setup touching a parent's scrollbar geometry; not yet reviewed |
| `0x0043E442..0x0043E63E` | 508 | mixed lvgl-core / lvgl-draw (no census confidence) | largest unresolved function in the span; calls into both style-cache and draw-rect helpers |
| `0x0043E63E..0x0043E6A6` | 104 | `LVGL/src/draw/lv_draw_rect.c` (medium conf.) | calls `FUN_0043E6A6` directly below |
| `0x0043E6A6..0x0043E7D2` | 300 | `LVGL/src/core/lv_obj_style.c`/`lv_obj_tree.c` (low conf., second-order) | called by `0x0043E63E` |
| `0x0043E7D2..0x0043EBEC` | 1050 | `LVGL/src/core/lv_obj.c`/`lv_obj_event.c`/`lv_obj_pos.c`/`lv_obj_scroll.c`/`lv_obj_tree.c` (medium conf.) | largest function in the whole item; call topology spans five LVGL files, consistent with a central dispatcher (e.g. the object event/class dispatch path); needs substantially more decompilation review before a faithful reimplementation is safe |

None of these five were force-fit into this tranche: the task's completion
bar requires reviewed, evidence-grounded C, not merely-compiling
decompiler output, and the evidence for these five was not yet strong
enough within this tranche's effort budget to meet that bar responsibly.

## Verification performed

- Host compiles: all six new translation units compile clean
  (`-target thumbv7em-none-eabi -mthumb -O2 -ffreestanding -fno-jump-tables
  -fomit-frame-pointer -fno-builtin -mno-unaligned-access
  -fno-unwind-tables -fno-asynchronous-unwind-tables -fropi -Wall -Wextra
  -Werror -Wno-unused-parameter -Wno-misleading-indentation`, the exact
  profile pinned by `overlay.json`'s `toolchain` block) with Apple clang
  21.0.0, and with a plain freestanding host `-fsyntax-only` pass.
- `make -C g2 core-component` and `make -C g2 source` (see progress.md for
  the exact run and resulting component/overlay digests).
- `python3 tools/open_cfw.py verify-artifacts --manifest
  manifests/g2-2.2.6.10-core-source.json --output-dir build/source
  --toolchain-profile apple-clang`.
- `tools/report_transparent_coverage.py` was not run against this tranche;
  the transparent/reviewed-sources registration
  (`tools/transparent/reviewed_sources.json`) was updated for the 27 closed
  functions so `make -C g2 transparent-test` stops trapping them.

No hardware operation (flashing, DFU, MMIO probing, signing) was performed
or attempted.
