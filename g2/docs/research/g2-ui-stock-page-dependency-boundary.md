# G2 dashboard stock-page dependency boundary

Status: complete read-only closure of
`app\gui\dashboard\screens\ui_stock_page.c` in authenticated stock G2 firmware
2.2.6.10. This is analysis evidence, not a production route.

The source-order object is `[0x004E9DD4,0x004ED7D8)`: 14,852 physical bytes.
Its 19 retained-path anchors expand to 34 functions / 13,892 body bytes. Two
entries at `0x004E9E32` and `0x004ED6C4` were restored from external direct
calls. The remaining 982 bytes are pools, alignment, and three inline data
regions. Whole-image analysis pins 116 direct entries, two aligned stored
callbacks, three classified ordinary wide interior branches, and no indirect
call.

The 852 external calls close as 454 selected LVGL 9.3-hybrid calls, 355
EasyLogger 2.2.99-compatible diagnostics, ten bounded IAR memory/string/format
calls, and 33 first-party role/dashboard/quicklist/resource/service calls.
There is no direct CMSIS-FreeRTOS or FreeRTOS call, no embedded reusable body,
and no new dependency-version or producing-commit discriminator. Page layout,
data rendering, focus, and scroll policy remain private G2 reconstruction work.

Reproduce with `make ui-stock-page-closure`.
