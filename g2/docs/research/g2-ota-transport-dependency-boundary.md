# G2 OTA transport dependency boundary

Status: complete read-only closure of
`platform\protocols\ota_service\ota_transport.c` in authenticated G2 2.2.6.10.

The physical object `[0x0048D8D8,0x0048E1CC)` contains three functions / 2,004
body bytes / 2,292 physical bytes. The two retained-path anchors expand through
a four-byte transfer-state getter at `0x0048E0A8`. Six direct entries close
external ingress; there is no stored entry or strict-interior ingress.

Its 86 direct calls resolve to 60 admitted EasyLogger calls, eight bounded IAR
memory calls, five calls into the already closed first-party OTA service, four
calls to the production source-owned CRC-16/CCITT-FALSE leaf, six calls to the
source-owned synchronized TLSF free wrapper, and three first-party event and
transport providers. Four `BLX` sites dispatch through registered callback
slots at RAM `0x20003058` and `0x2000305C`; they are first-party OTA delivery
and write callbacks whose concrete targets depend on product registration.

The object embeds no third-party implementation and adds no version or
historical generating-commit discriminator. Its packet sequencing, CRC checks,
buffer ownership, and callback ABI remain first-party reconstruction work.

Reproduce with `make ota-transport-closure`.
