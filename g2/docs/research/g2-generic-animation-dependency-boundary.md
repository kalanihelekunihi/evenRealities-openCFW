# G2 generic-animation dependency boundary

The four retained-path anchors / 826 bytes expand to seventeen functions /
1,622 body bytes for `app\gui\common\generic_animation.c`. The complete
physical object is `[0x00463C68,0x00464330)`, 1,736 bytes.

Thirteen source-order functions missed by Ghidra fill the 796-byte gap
between the second and third anchors: record field getters (`0x00463E9A`,
`0x00463FA4`), start/pause/resume-style state setters (`0x00463EA6`,
`0x00463EEE`), the elapsed-frame ticker (`0x00463F34`), the indexed frame
setter (`0x00463F5C`), the style-apply helper (`0x00463FB0`), the frame
advance/loop state machine (`0x00464008`), two EasyLogger diagnostic helpers
(`0x004640C0`, `0x0046415E`), two LVGL style wrappers (`0x004640FE`,
`0x00464152`), and the `lv_anim` starter (`0x0046410A`). Two restored
functions (`0x004640C0`, `0x0046415E`) reference the retained-path pointer
cell `0x004642C8` directly, independently proving single-object ownership.
The 114 noncode bytes `[0x004642BE,0x00464330)` are the object-final literal
pool holding the path cell (eight LDR-literal reference sites, all inside
object functions) and four aligned stored Thumb pointers to the callback
functions `0x004640FE`, `0x004640C0`, `0x00464152`, and `0x0046415E` — the
`lv_anim` exec/ready callbacks installed by this object.

The end boundary is proven by the following function at `0x00464330`: it is
called from the LVGL `lv_init` translation unit and initializes LVGL timer
state (`lv_timer.c` begins at `0x00464344`), so it is LVGL's, not this
object's. The preceding bytes below `0x00463C68` are the prior object's pool,
pinned by a boundary hash.

Ingress closure records 90 whole-image BL entry sites, the four aligned
stored pool pointers above, zero strict-interior BL decodes, and zero
indirect calls. Five unaligned raw words equal to the `0x00464008` entry
(mid-instruction byte sequences inside code at `0x005495E3`, `0x00549607`,
`0x0054962B`, `0x0054964F`, `0x005C2095`) and 32 raw odd words colliding with
instruction interiors (all but one unaligned; the one aligned word sits in
the retained string-data region) are byte-level coincidences, not pointers.

All 80 external direct calls terminate at admitted EasyLogger (40), bounded
IAR DLIB memory primitives (4), the exact CMSIS-FreeRTOS v10.5.1
`osKernelGetTickCount` wrapper (3 — the sole RTOS seam; no direct FreeRTOS
kernel edge exists), the production source-owned synchronized heap wrappers
over TLSF (3 — one record allocation, two frees), the admitted LVGL
9.3-compatible baseline (27 — `lv_anim` lifecycle, `lv_image_set_src` at the
`lv_image.c`-anchored `0x00498680`, object-flag/style/position operations
anchored by `lv_obj_pos.c`), or first-party role, sync-interface, and
image-resource providers (3). No animation edge terminates inside an embedded
LVGL body. The object embeds no reusable third-party implementation and adds
no version or producing-commit discriminator. Remaining work is first-party
source recreation and display validation; the object is not
production-routed. Reproduce with `python3
tools/analyze_g2_generic_animation.py` and its focused test.
