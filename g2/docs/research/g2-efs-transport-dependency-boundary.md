# G2 EFS transport dependency boundary

Status: production-routed clean-room C closure of
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
historical generating-commit discriminator. Two selector-isolated clean-room
functions compile to 1,276 Thumb bytes. Two guarded redirects and 15 strict
relocations replace all 1,990 stock body bytes; the authenticated 162-byte
alignment/string/literal pool remains official. The host oracle covers C4/C5/C6
receive, CRC success/failure, resource/overflow handling, error-sequence
suppression, delayed timeout, registered callbacks, CMSIS-tick transmit
sequencing, fragmentation, transmit failure, and malformed input.

Software functional gap: false. Hardware validation: blocked. No authorized
responsive G2 peer is physically available for live EFS import/export,
fragmentation, CRC-failure, timeout, disconnect/resume, or media-content
evidence; the authorized right temple is nonresponsive and the left temple
must remain stock.

Reproduce with `make efs-transport-closure`.
