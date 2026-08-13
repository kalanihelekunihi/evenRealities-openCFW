# G2 health-page dependency boundary

Status: complete read-only closure of `app\gui\health\ui_health_page.c` in
authenticated stock G2 firmware 2.2.6.10. This is analysis evidence, not a
production route.

The object is `[0x004FB1FA,0x004FD940)`: twelve functions / 9,414 body bytes /
10,054 physical bytes. One stored callback was restored beyond Ghidra. Nineteen
direct entries, two aligned stored pointers, and one data-only pseudo-call pin
whole-image ingress; there is no indirect call.

Its 666 external calls close as 437 selected LVGL calls, 55 admitted
EasyLogger diagnostics, four bounded IAR calls, 36 selected mpaland formatter
calls, and 134 first-party health/dashboard/navigation/service calls. There is
no direct CMSIS-FreeRTOS call, embedded reusable body, or new version or
historical producing-commit discriminator. Health layout and product policy
remain first-party reconstruction work.

Reproduce with `make ui-health-page-closure`.
