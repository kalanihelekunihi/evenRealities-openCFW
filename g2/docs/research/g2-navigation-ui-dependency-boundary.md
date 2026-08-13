# G2 navigation UI dependency boundary

Status: complete read-only closure of `app\gui\navigation\navigation_ui.c` in
authenticated stock G2 firmware 2.2.6.10. This is analysis evidence, not a
production route.

The source-order object is `[0x00545588,0x0054EE18)`: 39,056 physical bytes.
Its 16 retained-path anchors expand to 61 functions / 36,612 body bytes; 29
entries were restored beyond Ghidra. Fifteen bounded inline data regions and
the remaining alignment/pools account for 2,976 non-instruction bytes.
Whole-image analysis pins 152 direct entries, fourteen aligned function-start
pointers, and five stored pointers to two intentional shared-tail callback
entries. Nineteen wide branches are ordinary intra-function transfers. Two
apparent direct calls land in data or the second half of an instruction and
are pinned as decoder lookalikes; there is no indirect call.

The 2,237 external calls close as 702 selected LVGL 9.3-hybrid calls, 1,245
EasyLogger 2.2.99-compatible diagnostics, twenty exact CMSIS-FreeRTOS v10.5.1
mutex calls, 67 bounded IAR memory/string/format calls, 22 admitted nanopb
calls, two selected mpaland formatter calls, and 179 first-party navigation,
time, role, resource, dashboard, and service calls. No reusable dependency
body is embedded, and the object adds no new version or historical
producing-commit discriminator. Navigation layout, route policy, callbacks,
and page-state behavior remain private G2 reconstruction work.

Reproduce with `make navigation-ui-closure`.
