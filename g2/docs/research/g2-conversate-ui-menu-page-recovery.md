# G2 Conversate menu-page recovery

The retained `app\gui\conversate\conversate_ui_menu_page.c` anchor expands
from one 218-byte body to eight functions / 1,492 body bytes plus a 100-byte
pool, for 1,592 physical bytes at `[0x005B57AC,0x005B5DE4)`. Six source-order
bodies missed by the baseline Ghidra census recover page construction, BLE and
UI callbacks, styling, focus handling, and scroll-down policy. Five exact
stored Thumb pointers register four of those bodies as UI callbacks. Seven BL
entries, 102 body calls, the pool and adjacent boundaries, and the absence of
indirect/interior/unresolved targets are pinned by the analyzer.

The 101 direct external calls close over 35 admitted EasyLogger calls, 34 LVGL
object/group/label/style/scroll calls at selected 9.3-compatible commit
`344c7c318047b7348e1be8572a9fd4260c251cfa`, and 32 first-party Conversate,
animation, exit-prompt, and page-state calls. There is no CMSIS-FreeRTOS,
allocator, nanopb, or IAR runtime edge and no embedded upstream definition.
This supplies no new third-party version discriminator; the remaining port is
first-party UI policy and is not yet production-routed.
