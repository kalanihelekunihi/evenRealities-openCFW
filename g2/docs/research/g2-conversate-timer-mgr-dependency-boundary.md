# G2 Conversate timer-manager dependency boundary

Seven retained-path anchors / 952 bytes expand to twenty-four functions /
2,204 body bytes for `app\gui\conversate\conversate_timer_mgr.c`: nine
Ghidra-discovered (seven path-anchored) plus fifteen restored from source-order
call/table evidence. The complete physical object is
`[0x005B3570,0x005B3EF8)`, 2,440 bytes, bounded exactly by the closed
`conversate_ui_main_page.c` extent below and the closed
`conversate_comm_data.c` extent above; the 236 noncode bytes are literal pools
and pointer tables between and behind the functions.

Ownership of the fifteen restored functions is proven three ways: nine of them
carry direct literal references to the object path cell `0x005B3E14`
(seventeen path references, all resolving inside this object); six contiguous
callbacks are stored alongside two path-anchored callbacks in the four-slot
timer-callback table at `0x0075EA90`; and every remaining restored body is
called only from inside the anchored cluster.

The 102 external direct calls terminate at admitted EasyLogger (85), the exact
CMSIS-FreeRTOS `osKernelGetTickCount` wrapper at `0x004490CC` (2; the only
CMSIS-FreeRTOS seam, kernel V10.5.1 `def7d2df…`, wrappers `d213f261…`), the
closed `service_time.c` epoch getter `0x0044A1C6` plus first-party role gating
`0x0045A568` (6), and already-closed conversate objects `0x005B02E4`
(conversate.c), `0x005B16DC` (conversate_ui.c, this batch), `0x005B57AC`
(conversate_ui_menu_page.c) (11). There is no embedded third-party definition
and no new version/private-commit discriminator.

Two indirect BLX sites (`0x005B36F4`, `0x005B3712`) dispatch start/stop
callbacks through the authenticated flash table at `0x0075EA90` (pool word
`0x005B3E2C`). The dispatcher head range-checks the timer id (`cmp #0`,
`cmp #4` before either BLX), and all six non-null table entries are this
object's own functions, so the indirect closure is exact. Ingress closes over
33 BL entry sites and the six stored table pointers with no strict interior
entry and no interior pointer collision. The object is not production-routed;
remaining work is first-party timer-policy recreation and on-device validation.
