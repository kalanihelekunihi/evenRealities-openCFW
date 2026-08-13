# G2 menu page dependency boundary

Status: complete read-only closure of `app\gui\menu\menu_page.c` in
authenticated stock G2 firmware 2.2.6.10. This is analysis evidence, not a
production route.

The source-order object is `[0x0046018E,0x00463C68)`: 15,066 physical bytes.
Its fourteen retained-path anchors expand to 34 functions / 13,906 body bytes;
nine entries were restored beyond Ghidra. Seven inline data regions and the
remaining pools/alignment account for 1,236 non-instruction bytes. Whole-image
analysis pins 98 direct entries, eight aligned function-start pointers, one
stored shared interior entry, and five ordinary wide intra-function branches.
There is no unresolved interior, non-code, or indirect ingress.

The 746 external calls close as 124 selected LVGL 9.3-hybrid calls, 445
EasyLogger 2.2.99-compatible diagnostics, three exact CMSIS-FreeRTOS v10.5.1
event/mutex calls, 24 bounded IAR memory/string calls, fifteen admitted nanopb
calls, and 135 first-party menu, role, resource, persistence, and service
calls. No reusable dependency body is embedded, and the object adds no new
version or historical producing-commit discriminator. Menu layout, selection,
persistence, page routing, and product policy remain private G2 reconstruction
work.

Reproduce with `make menu-page-closure`.
