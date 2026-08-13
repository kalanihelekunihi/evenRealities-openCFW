# G2 EFS transport dependency boundary

Status: complete read-only closure of
`platform\protocols\efs_service\efs_transport.c` in authenticated G2 2.2.6.10.

The physical object `[0x004D0D80,0x004D15E8)` contains two functions / 1,990
body bytes / 2,152 physical bytes. Two direct entries close external ingress;
there is no stored entry or strict-interior ingress.

Its 87 direct calls resolve to 60 admitted EasyLogger calls, one exact
CMSIS-FreeRTOS v10.5.1 tick call, eight bounded IAR memory calls, five calls
into the already closed first-party EFS service, four calls to the production
source-owned CRC-16/CCITT-FALSE leaf, six calls to the source-owned
synchronized TLSF free wrapper, and three first-party event/transport
providers. Four `BLX` sites dispatch through registered callback slots at RAM
`0x2000096C` and `0x20000970`.

The object embeds no third-party implementation and adds no version or
historical generating-commit discriminator. Its packet sequencing, buffer
ownership, and callback ABI remain first-party reconstruction work.

Reproduce with `make efs-transport-closure`.
