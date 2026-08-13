# G2 calendar-page dependency boundary

Status: complete read-only closure of
`app\gui\dashboard\screens\ui_calendar_page.c` in authenticated G2 2.2.6.10.

The physical object `[0x004ED7D8,0x004EFF94)` contains fifteen functions /
9,690 body bytes / 10,172 physical bytes. Five retained-path anchors expand
through seven additional Ghidra bodies and three restored functions at
`0x004ED81C`, `0x004EFA78`, and `0x004EFEB0`. Thirty-two direct entries and
three stored function pointers close ingress. A wide-branch target at
`0x004EEAA2` is a shared tail within the same large function, not another
entry or object.

Its 722 external calls resolve to 533 admitted LVGL calls, 85 admitted
EasyLogger calls, 34 exact CMSIS-FreeRTOS v10.5.1 mutex calls, twelve bounded
IAR memory/runtime calls, and 58 first-party dashboard/time/weather/storage
providers. It embeds no reusable implementation and exposes no new version or
historical generating-commit discriminator. Calendar layout, timers, weather
state, and page lifecycle remain first-party product policy.

Reproduce with `make ui-calendar-page-closure`.
