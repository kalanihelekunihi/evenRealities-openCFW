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
and does not itself embed third-party implementation bytes.

The first-party manager is now production-routed from
`components/apollo_main/core_overlay/lvgl_font_manager.c`. Eight strict
Cortex-M55 leaves contribute 904 compiled text bytes plus 10 alignment bytes;
19 strict relocations bind the reviewed allocator, FreeType adapter, MSPI
lock, and memory providers. Eight guarded redirects replace all 2,590 stock
function-body bytes while 382 authenticated literal/alignment bytes remain.
The host oracle covers native and FreeType mixtures, failed allocation and
face creation, manager tracking and cleanup, ordered fallback links, both XIP
headers, MSPI lock symmetry, background/foreground roles, and initialization.

The external font payloads remain a physical-media boundary, not a software
implementation gap. Their identity, contents, XIP readability, typography,
and live rendering cannot be validated because no golden external-flash
capture, responsive authorized G2 display path, or matching physical evidence
is available. No font bytes were guessed, and no image was signed, flashed,
or installed.
