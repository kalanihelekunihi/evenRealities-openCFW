# G2 EvenHub data-parser recovery

The twelve-anchor / 8,136-byte retained-path view expands to nineteen
functions / 10,336 executable bytes plus 538 object-owned literal, table, and
alignment bytes. The complete object is `[0x004D9B34,0x004DC5AE)`, 10,874
physical bytes. Two functions missed by Ghidra are recovered. The large
dispatcher at `0x004DA834` contains six reachable inline literal/table islands
(160 bytes); the audit authenticates its full interval but counts those islands
as noncode. The object begins after `service_kvdb.c` data and ends exactly at
the first `common_image_container.c` function.

The audit pins 3,819 reachable instructions, 590 direct calls, 93 whole-image
BL entries, four retained-path cells, no stored function pointers, no indirect
calls, and zero strict-interior ingress.

Every reusable direct edge is classified: 385 EasyLogger calls at
`a596b264…`; 25 nanopb calls at selected compatibility commit `98bf4db6…`;
three exact CMSIS-FreeRTOS v10.5.1 mutex wrappers; 14 LVGL calls at selected
hybrid commit `344c7c318…`; 54 bounded IAR DLIB calls; twelve calls to the
production-routed TLSF-backed heap wrappers; and 48 calls to bounded first-
party schema, role, transport, image, and container providers. No third-party
implementation body or new version discriminator is embedded.

The object is not production-routed. Remaining work is clean-room first-party
schema/dispatch reconstruction and device/UI validation, not dependency
discovery.
