# G2 health data-manager dependency boundary

The five retained-path anchors / 1,848 bytes expand to ten functions / 2,644
body bytes for `health_data_manager.c`. The complete physical object is
`[0x005597F0,0x0055A350)`, 2,912 bytes. One source-order parser missed by
Ghidra completes health-record validation, bounded aggregation, lookup, and
shared-storage update behavior. The endpoint is the hidden protobuf-health
dispatcher that begins the adjacent already closed service object.

The closure records 976 reachable instructions, 149 direct calls, eighteen
whole-image BL entry sites, no stored function pointer, no indirect call, and
no strict-interior ingress. All 136 external calls terminate at admitted
EasyLogger (120), bounded IAR/runtime memory primitives (6), or the already
closed first-party health mutex acquire/release wrappers (10). Those wrappers
in turn use exact source-owned CMSIS-FreeRTOS v10.5.1 mutex APIs; this object
has zero direct CMSIS-FreeRTOS or FreeRTOS edge.

No reusable calculation, DSP implementation, or new version discriminator is
embedded. The historical first-party producing commit remains unobservable.
Remaining work is clean-room health schema/policy recreation and device data
validation; the object is not production-routed.
