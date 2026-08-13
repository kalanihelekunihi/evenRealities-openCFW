# G2 LVGL font-manager recovery

The seven-anchor / 2,586-byte retained-path view expands to eight functions /
2,590 body bytes plus 382 owned literal/alignment bytes. The complete object is
`[0x0046CAE0,0x0046D67C)`, 2,972 physical bytes. The added four-byte getter is
pathless but belongs to the same post-text pool. The audit pins 973 reachable
instructions, 149 direct calls, twelve whole-image BL entries, both path cells
and physical boundaries, and zero stored, indirect, or interior ingress.

The object builds four-entry font chains for background and foreground roles,
validates external XIP headers, creates/destroys LVGL FreeType faces, and
serializes header access through the closed MSPI transaction lock. Its reusable
graph is fully classified: 125 EasyLogger calls at `a596b264…`; two bounded IAR
DLIB calls; two calls to the closed G2 MSPI lock pair; nine calls to the
production-routed TLSF-backed file-runtime heap wrappers; and the exact
`lv_freetype_font_create`/`delete` entries from `lv_freetype.c`.

The adapter confirms selected LVGL hybrid commit `344c7c318…` and exact
FreeType 2.9.1 tag commit `86bc8a950…`. This strengthens the functional seam
but does not prove the private G2 generating checkout or an unpatched pristine
LVGL tree. No third-party implementation body remains embedded in the manager,
and it is not production-routed. Remaining work is first-party manager source,
external font assets, and device/XIP validation.
