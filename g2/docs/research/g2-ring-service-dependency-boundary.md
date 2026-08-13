# G2 Ring service dependency boundary

Status: complete read-only closure of
`platform\protocols\ring_service\ring_service.c` in authenticated G2 2.2.6.10.

The object `[0x00472244,0x00472C7C)` contains eighteen functions / 2,412 body
bytes / 2,616 physical bytes. Twenty-seven direct entries and two stored
function pointers close ingress. Its 121 external calls resolve to 76 admitted
EasyLogger, two exact CMSIS-FreeRTOS tick, eight bounded IAR, one admitted
nanopb, zero Packetcraft Cordio, and 34 first-party calls. The five targets
previously grouped as Cordio are retained-path-identified input-manager,
thread-ring, and device-manager policy plus adjacent first-party helpers. It
embeds no vendor body and adds no version or producing-commit discriminator.
Ring state and product policy remain first-party work.

Reproduce with `make ring-service-closure`.
