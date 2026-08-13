# G2 Conversate UI dependency boundary

Four retained-path anchors / 830 bytes expand to twenty-three functions /
3,774 body bytes for `app\gui\conversate\conversate_ui.c`: eight
Ghidra-discovered (four path-anchored) plus fifteen restored Ghidra-missed
bodies. The complete physical object is `[0x005B0B58,0x005B1B4C)`, 4,084
bytes, bounded exactly by the closed `conversate.c` controller extent below
and the closed `pb_service_conversate.c` extent above; the 310 noncode bytes
are literal pools and pointer/name tables between and behind the functions.
Twenty-one path-cell references across cells `0x005B15CC` and `0x005B1ADC`
resolve exclusively inside this object, anchoring twelve of the fifteen
restored bodies; the remaining three (the two page-policy callbacks
`0x005B1998`/`0x005B1A14` and the event dispatcher `0x005B1724`) sit in the
same contiguous cluster and are corroborated by the dispatch table below.

The 221 external direct calls terminate at admitted EasyLogger (100), bounded
IAR DLIB zero fill (2), admitted LVGL 9.3-compatible primitives (84 across 41
targets), first-party display/role/sync policy (15), and closed or bounded
first-party providers (20): `list_anim.c` bodies, exit-prompt, the
`conversate.c` trailing style body `0x005B0AC4`, main/menu/tag page entries,
and this batch's `conversate_timer_mgr.c` and `conversate_ui_prep_note_page.c`
functions. No CMSIS-FreeRTOS or FreeRTOS kernel seam exists in this object;
there is no embedded third-party definition and no new version discriminator.

The single indirect BLX site `0x005B18C0` is the conversate page-event
dispatch: the state id is range-checked below 7, the event id below 0x15, the
row stride is 0xA8 and the column stride 8 over the authenticated flash table
at `0x00686920` (base word `0x005B1B20`). Exactly 50 of the 147 slots are
non-null, and every non-null target is either this object's own page-policy
callbacks (`0x005B1998`, `0x005B1A14`) or a closed conversate page object
(main/menu/tag/prep-note pages), so the indirect closure is exact. Ingress
closes over 74 BL entry sites and eleven stored pointers (one self-referential
cell `0x005B1720` plus ten dispatch-table entries) with no strict interior
entry. The sole interior pointer-shaped word at `0x005D041E` combines the
second halfword of `movs.w ip,#1` with `lsls r3,r3,#1` into a pointer-shaped
word and is not callable ingress. The object is not production-routed;
remaining work is first-party page-policy recreation and UI validation.
