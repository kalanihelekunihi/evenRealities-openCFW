# G2 translate controller dependency boundary

Seven retained-path anchors / 1,838 bytes expand to eleven functions / 2,504
body bytes for `app\gui\translate\translate.c`. The physical object is
`[0x0059E9E2,0x0059F510)`, 2,862 bytes. Two source-order handlers at
`0x0059EFE0` and `0x0059F0EA` were restored beyond Ghidra.

The object has 168 direct calls and no indirect call. All 156 external calls
terminate at admitted EasyLogger (105), bounded IAR/EABI runtime (7), LVGL
(2), exact CMSIS-FreeRTOS v10.5.1 wrappers (7), nanopb (3), or bounded
first-party translate UI/service providers (32). It therefore reuses commits
`a596b264…`, `344c7c318…`, `d213f261…`, and `98bf4db6…` without embedding a
third-party implementation or adding a version discriminator.

Whole-image ingress is closed by 23 BL sites and two aligned stored pointers.
One unaligned exact-entry byte window in the terminal data/resource region and
two aligned raw words that are complete four-byte Thumb instructions are
scanner coincidences, not pointers. Remaining work is first-party translate
behavior recreation and device validation; the object is not production-routed.
