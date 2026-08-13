# G2 fade-anim dependency boundary

The five retained-path anchors / 1,164 bytes expand to eleven functions /
1,678 body bytes for `app\gui\anim\fade_anim.c`. The complete physical object
is `[0x0058C12C,0x0058C836)`, 1,802 bytes — exactly bounded by the closed
exit-prompt object (`[0x0058BDA8,0x0058C12C)`) below and the closed
teleprompt-FSM object (`[0x0058C836,0x0058D51C)`) above.

Six source-order functions missed by Ghidra complete the object: the LVGL
style helper at `0x0058C12C`, the recursive fade exec callback at
`0x0058C138` (color-channel interpolation over the widget child tree), its
wrapper at `0x0058C230`, the animimage-based fade starter at `0x0058C6C4`
(called by the list-anim object closed in the same batch), and the public
fade-create / fade-start pair at `0x0058C7A0` / `0x0058C824` whose three
external callers sit in the teleprompt-UI, translate-UI, and conversate-UI
regions. The 124 noncode bytes are the shared literal pool
`[0x0058C72A,0x0058C7A0)` — holding the retained-path pointer cell
`0x0058C740` (nine LDR-literal reference sites, all inside object functions)
and two aligned stored Thumb pointers to the exec-callback helpers
`0x0058C12C` and `0x0058C230` — plus a six-byte pad/single-cell mini-pool at
`0x0058C81E` used by `0x0058C7A0`.

Ingress closure records 38 whole-image BL entry sites, the two stored
pointers above, zero strict-interior BL decodes, zero raw interior word
collisions, and zero indirect calls.

All 89 external direct calls terminate at admitted EasyLogger (45) or the
admitted LVGL 9.3-compatible baseline (44): animation lifecycle
(`lv_anim_init`/`lv_anim_set_*`/`lv_anim_start` span around the anchored
`0x00450408`), object-tree, style, and color primitives, and the lv_animimage
widget family (`0x00597E90`-`0x00597F82`, every member anchored by the
admitted `lv_animimage.c` path). No animation edge terminates inside an
embedded LVGL body and no CMSIS-FreeRTOS or FreeRTOS seam exists. The object
embeds no reusable third-party implementation and adds no version or
producing-commit discriminator. Remaining work is first-party source
recreation and display validation; the object is not production-routed.
Reproduce with `python3 tools/analyze_g2_fade_anim.py` and its focused test.
