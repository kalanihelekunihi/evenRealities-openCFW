# G2 Conversate tag-page recovery

The retained `app\gui\conversate\conversate_ui_tag_page.c` anchor expands
from one 238-byte Ghidra body to eleven functions / 2,910 body bytes plus a
146-byte pool, for 3,056 physical bytes at `[0x005B5DE4,0x005B69D4)`. Ten
source-order bodies missed by the baseline path census recover tag-page
construction, show/update actions, duration calculation, input handling,
focus and scroll policy, and the return-to-main-page action. Eleven stored
Thumb pointers, three direct entries, one alternate interior callback entry,
204 body calls, exact adjacent boundaries, and the absence of indirect or
unrecovered direct targets are pinned by the analyzer.

The 202 direct external calls close over 40 admitted EasyLogger diagnostics,
113 LVGL UI calls at selected 9.3-compatible commit
`344c7c318047b7348e1be8572a9fd4260c251cfa`, two exact CMSIS-FreeRTOS
`osKernelGetTickCount` calls at selected commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`, four bounded IAR DLIB
clear/copy calls, and 43 first-party Conversate, animation, tracking, and
service-state calls. There is no embedded upstream definition and this object
adds no version discriminator. The remaining implementation work is
first-party UI policy, and the recovered object is not yet production-routed.
