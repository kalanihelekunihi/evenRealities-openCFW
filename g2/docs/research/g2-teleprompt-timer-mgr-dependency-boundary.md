# G2 Teleprompt timer-manager dependency boundary

Five retained-path anchors / 844 bytes expand to thirteen functions / 1,498
body bytes for `app\gui\teleprompt\teleprompt_timer_mgr.c`: nine
Ghidra-discovered (five path-anchored) plus four restored Ghidra-missed
callback bodies at the object head. The complete physical object is
`[0x00588D74,0x005893F0)`, 1,660 bytes, bounded below by the closed
`pb_service_teleprompt.c` extent and above by the `list_anim.c` cluster (whose
first body `0x005893F0` is called only from inside `list_anim.c`-anchored
functions). The 162 noncode bytes are the trailing literal/pointer tables,
including the object path cell `0x00589360`.

The four restored callbacks `0x00588D74`-`0x00588F1A` each reference the path
cell directly (eleven path references, all inside this object) and are stored
as the only non-null entries of the three-slot timer-callback table at
`0x0077C52C`, which is their sole ingress (no BL caller exists).

The 65 external direct calls terminate at admitted EasyLogger (55), the exact
CMSIS-FreeRTOS `osKernelGetTickCount` wrapper at `0x004490CC` (3; the only
CMSIS-FreeRTOS seam, kernel V10.5.1 `def7d2df…`, wrappers `d213f261…`), the
closed `service_time.c` RTC refresh `0x0044A1EA` plus first-party role gating
`0x0045A568` (5), and the already-closed teleprompt providers `0x005548C4`
(teleprompt_ui.c) and `0x00589B68` (teleprompt.c) (2). There is no embedded
third-party definition and no new version/private-commit discriminator.

Two indirect BLX sites (`0x00588F92`, `0x00589060`) dispatch start/stop
callbacks through the authenticated flash table at `0x0077C52C` (pool word
`0x005893B0`). Both dispatcher heads range-check the timer id identically
(`cmp #3`/`bge` reject, `cmp #0`/`bne` select, so only ids 1-2 reach the
table), and all four non-null entries are this object's own restored
callbacks, so the indirect closure is exact. Ingress closes over 13 BL entry
sites and the four stored table pointers with no strict interior entry and no
interior pointer collision. The object is not production-routed; remaining
work is first-party timer-policy recreation and on-device validation.
