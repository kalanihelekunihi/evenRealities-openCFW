# G2 Conversate prep-note-page dependency boundary

Two retained-path anchors / 884 bytes expand to sixteen functions / 3,114 body
bytes for `app\gui\conversate\conversate_ui_prep_note_page.c`: nine
Ghidra-discovered (two path-anchored) plus seven restored from source-order,
path-cell, and handler-table evidence. The complete physical object is
`[0x005B69D4,0x005B7684)`, 3,248 bytes, bounded below by the closed
`conversate_ui_tag_page.c` extent and above by the `expand_anim.c` cluster
(four stored-pointer helpers at `0x005B7684`-`0x005B7704` plus the
path-anchored `0x005B7704` body, which carries the only two
`expand_anim.c` literal references in the region). The trailing 128-byte
noncode block `0x005B7604`-`0x005B7684` holds this object's path cell
`0x005B7610` and stored pointers to three of its own restored functions.

Restored-function ownership: `0x005B6C48` and `0x005B6F8E` reference the path
cell directly; `0x005B7138` also references it and, with `0x005B74BA`,
`0x005B7518`, and `0x005B7556`, is stored as a page-event handler in the
authenticated conversate_ui 7x21 dispatch table at `0x00686920` alongside
closed main/menu/tag-page handlers.

The 188 external direct calls terminate at admitted EasyLogger (40), bounded
IAR DLIB zero fill (7), admitted LVGL 9.3-compatible primitives (123 across 45
targets — `lv_obj_get_content_width` at `0x0043FE16` and `lv_obj_delete_async`
at `0x0044D90E` identities confirmed by their retained `lvgl_v9.3` path
strings), first-party display/fade-animation policy (8), and closed conversate
providers plus the bounded `expand_anim.c` entry `0x005B7704` (10). No
CMSIS-FreeRTOS or FreeRTOS kernel seam exists in this object; there is no
embedded third-party definition and no new version discriminator.

Ingress closes over 24 BL entry sites and nine stored pointers (six
dispatch-table entries plus three trailing cells) with no indirect call and no
strict interior entry. The single interior pointer-shaped word at
`0x004D2301` is an odd-offset byte window inside the data word `0x5B6E4363`
in a literal/string area (immediately preceding the `"scanf_s: bad %n
argument"` literal), not a stored Thumb pointer; stored function pointers in
this image are 4-aligned. The object is not production-routed.
