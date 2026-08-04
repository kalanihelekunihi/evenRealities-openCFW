# LVGL compatibility-ceiling source snapshot

This directory contains an authenticated, production-excluded LVGL source
snapshot selected by openCFW at official commit
`344c7c318047b7348e1be8572a9fd4260c251cfa` (tree
`2c76db856ec570f3ee12565181e5cf52bdd33d78`).  It is the newest official
commit inside the G2-compatible interval recovered from firmware 2.2.6.10.

This commit is an **openCFW compatibility-baseline choice**.  It is not a
claim that Even Realities used that exact checkout, and it is not the released
LVGL `v9.3.0` tag.  G2 stores `LV_STYLE_LAST_BUILT_IN_PROP == 137` and
`LV_EVENT_LAST == 66`, constraining equivalent official history to inclusive
`60d976c466e8619326edfbd193fd2a046c10113f..344c7c318047b7348e1be8572a9fd4260c251cfa`.
The later release has event sentinel 67 and no longer has
`src/misc/cache/lv_cache_lru_rb.c`.

## Snapshot boundary

The upstream payload is 2,503,751 bytes in 318 files:

- 65 exact `.c` paths authenticated in the G2 image: 61 LVGL core/optional
  modules and four official LVGL FreeType wrappers;
- 251 headers selected by a compiler dependency pass over those translation
  units using the proven G2 feature definitions and otherwise the selected
  commit's defaults;
- `src/osal/lv_os_none.h`, used only by the independently reproduced minimal
  reference ABI compile; and
- the unmodified 1,072-byte MIT `LICENCE.txt`.

The broad public-header surface is expected: several selected translation
units include LVGL's umbrella `lvgl.h`.  Header inclusion does not establish
that the corresponding optional implementation was linked into G2.  No
unobserved optional `.c` file was imported.

The dependency calculation treats the existing openCFW FreeType 2.9.1,
FreeRTOS V10.5.1, and littlefs snapshots as external inputs.  Their headers and
licenses remain in their own provenance boundaries.

## Deliberate exclusions

The snapshot excludes all eleven G2 `LVGL/src/draw/ambiq/*.c` translation
units, `lvgl_ambiq_porting/lv_ambiq_display.c`, and
`lvgl_ambiq_demo/lvgl_ttf/src/am_ftsystem.c`.  It also excludes Ambiq/Even font
assets, the platform display and input managers, the Even font manager and
animation code, all application/UI sources, and all vendor patches.  None is
covered by this official LVGL commit or MIT-license identity.

## Configuration and promotion boundary

[`g2-config/lv_conf_recovered.h`](g2-config/lv_conf_recovered.h) defines only
values proven by retained G2 bytes.  Missing options are unknown, not presumed
to equal upstream defaults.  [`g2-config/lvgl_g2_abi.json`](g2-config/lvgl_g2_abi.json)
records the required short-enum, 32-bit ABI and the remaining fail-closed gate:
the official minimal reference configuration produces `lv_global_t == 0x1F8`,
while G2 requires `0x1EC`.  The display, input, and draw-buffer sizes do match.

Nothing here is registered in a production component, manifest, overlay, or
flashing path.  Run `python3 third_party/lvgl/verify_snapshot.py` from the
`openCFW` directory for offline commit/tree/blob/license verification.

See [`docs/research/lvgl-version-recovery-audit.md`](../../docs/research/lvgl-version-recovery-audit.md)
for the G2 evidence and limitations.
