# G2 list-anim dependency boundary

The seven retained-path anchors / 1,112 bytes expand to eleven functions /
1,348 body bytes for `app\gui\anim\list_anim.c`. The complete physical object
is `[0x005893F0,0x005899A4)`, 1,460 bytes, ending exactly where the closed
teleprompt-controller object begins (`0x005899A4`).

Four source-order functions missed by Ghidra complete the object: the
tick-elapsed helper at `0x005893F0` (a fourteen-byte `osKernelGetTickCount`
delta used only by the first anchor), the stop-and-reset helper at
`0x0058949E` (its Thumb pointer is stored in the object pool at `0x00589958`),
the scroll-position animator at `0x005894D6` (LVGL child-tree, scroll, and
style operations), and the state getter at `0x005897E0`. The 112 noncode
bytes `[0x00589934,0x005899A4)` are the object-final literal pool holding the
retained-path pointer cell `0x00589940`, whose eight LDR-literal reference
sites all lie inside object functions.

The start boundary is proven structurally: the preceding teleprompt-timer-mgr
functions (`0x0058922C`, `0x0058930A`) reference the pool that ends at
`0x005893F0` — an object-final pool of the preceding translation unit — so
`0x005893F0` opens list-anim. Its tiny tick helper is called exclusively from
list-anim's first anchor (three sites), consistent with single-object
ownership.

Ingress closure records 37 whole-image BL entry sites, the one stored pointer
above, zero strict-interior BL decodes, zero raw interior word collisions,
and zero indirect calls.

All 73 external direct calls terminate at admitted EasyLogger (40), bounded
IAR DLIB memset (2), the exact CMSIS-FreeRTOS v10.5.1 `osKernelGetTickCount`
wrapper (2 — the sole RTOS seam; no direct FreeRTOS kernel edge exists), the
admitted LVGL 9.3-compatible baseline (27; object-tree targets anchored by
`lv_obj_tree.c` / `lv_obj_scroll.c`), or the already-closed fade_anim object
(2 — fade stop `0x0058C622` and fade start `0x0058C6C4`, closed in the same
batch). No animation edge terminates inside an embedded LVGL body. The object
embeds no reusable third-party implementation and adds no version or
producing-commit discriminator. Remaining work is first-party source
recreation and display validation; the object is not production-routed.
Reproduce with `python3 tools/analyze_g2_list_anim.py` and its focused test.
