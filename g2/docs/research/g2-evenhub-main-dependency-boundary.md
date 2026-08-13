# G2 EvenHub main dependency boundary

The three retained-path anchors / 1,848 bytes expand to five functions / 3,130
body bytes for `app\gui\EvenHub\evenhub_main.c`. The complete physical object is
`[0x004E0CCE,0x004E1A48)`, 3,450 bytes. One source-order routine at
`0x004E1490` missed by Ghidra completes the event-state, protobuf, heap, and UI
control surface.

The closure records 1,193 reachable instructions, 181 direct body calls, three
whole-image BL entry sites, two stored exact function pointers, and no indirect
call. The raw BL scanner also finds `0x006312BE -> 0x004E1180`, while the raw
word scanner finds `0x0064BA02 -> 0x004E0E1F`. Both source sites are in the
post-`0x00600FAA` data/resource region where the authenticated whole-image
Ghidra census discovers no functions; the latter is additionally unaligned at
two bytes. Pinned source windows classify both as scanner coincidences rather
than callable ingress, leaving no unexplained strict-interior entry.

All 180 external direct calls terminate at admitted EasyLogger (120), bounded
IAR DLIB/source-owned EABI runtime (6), LVGL (2), exact CMSIS-FreeRTOS tick
wrapper (2), nanopb decoder (3), production-routed synchronized TLSF heap
wrappers (2), or bounded first-party EvenHub/service providers (45). This
reuses EasyLogger `a596b264…`, LVGL `344c7c318…`, CMSIS-FreeRTOS `d213f261…`,
nanopb `98bf4db6…`, and TLSF `deff9ab5…`; it embeds no third-party definition
and adds no version or private generating-commit discriminator.

Remaining work is first-party EvenHub behavior recreation and device-level
validation. The object is not production-routed.
