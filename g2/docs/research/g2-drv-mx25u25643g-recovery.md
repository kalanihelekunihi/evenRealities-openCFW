# G2 MX25U25643G driver recovery

The 21 retained-path anchors / 5,420 bytes expand to forty functions / 6,726
body bytes for `driver\flash\drv_mx25u25643g.c`. The complete physical object
is `[0x0046F4A4,0x00471164)`, 7,360 bytes, including 634 bounded literal,
string, table, and alignment bytes. Nineteen restored functions recover GPIO
callbacks, transaction locks, mode helpers, and the littlefs read/program/
erase adapters already characterized by the block-port audit.

The audit pins 2,479 instructions, 386 direct calls, 126 whole-image BL
entries, four stored Thumb pointers, no indirect calls, and zero strict-
interior ingress. All 297 external calls are classified: 230 EasyLogger calls;
31 AmbiqSuite Apollo510 MSPI/GPIO HAL calls; five CMSIS-FreeRTOS wrappers;
three calls to the shared nanopb-linked initializer address; seven IAR DLIB
memory calls; sixteen production-owned runtime-log calls; and five source-
owned delay-wrapper calls.

The driver therefore reuses AmbiqSuite 5.1.0-lineage commit `5efc0228…`,
CMSIS-FreeRTOS `d213f261…`, and the already admitted shared initializer at
nanopb compatibility commit `98bf4db6…`. It embeds no third-party definition
and adds no version discriminator. The object is not production-routed;
remaining work is clean-room flash policy/command reconstruction and hardware
validation, not dependency discovery.
