# G2 input-manager dependency boundary

Status: complete read-only closure of
`platform\input\service_input_manager.c` in authenticated G2 2.2.6.10.

The physical object `[0x004C5886,0x004C6240)` contains ten functions / 2,242
body bytes / 2,490 physical bytes. Five retained-path anchors expand through
five contiguous Ghidra-discovered helpers. Twenty-nine direct entries and two
stored function pointers close ingress; there is no indirect body call or
strict-interior entry.

Its 103 external calls resolve to 85 admitted EasyLogger calls, two exact
CMSIS-FreeRTOS v10.5.1 tick calls, two admitted nanopb iterator calls, two
bounded IAR memory calls, one eight-byte signed absolute-value leaf, and eleven
first-party input/event/timer/transport providers. It directly calls neither
LVGL nor Cordio and embeds no third-party implementation. The retained private
path therefore represents G2 input policy, not a missing Ambiq/LVGL input port.
No public origin, version, or historical generating commit is attributable to
this first-party object.

Reproduce with `make service-input-manager-closure`.
