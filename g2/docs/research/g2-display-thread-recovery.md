# G2 display-thread recovery

The fourteen retained-path anchors / 8,442 bytes for
`framework\sync\display_thread.c` expand to 27 functions / 9,100 body bytes.
The complete physical interval `[0x0044228A,0x004448F4)` is 9,834 bytes,
including 734 bounded literal, string, table, and alignment bytes. Thirteen
pathless functions recover display-state getters, lifecycle helpers, and
callback adapters.

The audit pins 3,370 instructions, 545 direct calls, 201 whole-image BL
entries, three stored Thumb pointers, twelve indirect callback sites, and zero
strict-interior ingress. Every external direct edge is classified: 310
EasyLogger calls; 21 exact CMSIS-FreeRTOS wrappers; eleven FreeRTOS delay/assert
leaves; twelve LVGL timer-handler calls; 23 bounded IAR DLIB operations; five
production source-owned application-log calls; and 140 first-party display,
page, settings, synchronization, and service calls.

No third-party implementation is embedded. The object reinforces
CMSIS-FreeRTOS `d213f261…`, FreeRTOS-Kernel `def7d2df…`, and LVGL
`344c7c318…` without adding a version discriminator. The 2,558-byte main
command loop and twelve-byte stored display callback are already production-
routed. Remaining work is clean-room recovery of the other first-party display
state/event helpers and hardware/UI validation.
