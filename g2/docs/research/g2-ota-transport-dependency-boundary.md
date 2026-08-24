# G2 OTA transport dependency boundary

Status: production source replacement complete; hardware validation blocked.
`platform\protocols\ota_service\ota_transport.c` in authenticated G2 2.2.6.10
is fully bounded, clean-room implemented, and routed into the complete source
firmware package.

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
buffer ownership, and callback ABI are first-party behavior.

`components/apollo_main/core_overlay/ota_transport.c` now owns all three
functions. The production build emits 1,300 bytes of Thumb text plus two bytes
of alignment, applies 14 strict relocations, redirects all 2,004 stock body
bytes, and retains the authenticated 288-byte official pool. The component,
source manifest, and complete source package are pinned and byte-reproducible.

The host oracle covers C0/C1/C2 receive paths, CRC success and failure,
same-sequence error suppression, default and dynamic receive-buffer ownership,
resource failure, overflow bounds, delayed timeout scheduling, registered
callback delivery, payload-capacity-aware fragmentation, transmit failure,
malformed frames, and the transfer-state getter. Three isolated target builds
prove each production entry is independently compilable.

Live OTA qualification is explicitly blocked by physical evidence: there is no
authorized responsive G2 peer/receiver for retransmission timeout, callback
timing, CRC-failure, disconnect, and recovery workflows. The authorized right
temple is nonresponsive and the left temple must remain on stock firmware. No
hardware or flash state was changed.

Reproduce with `make ota-transport-closure`.
