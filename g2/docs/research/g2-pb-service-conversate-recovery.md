# G2 `pb_service_conversate.c` recovery

Status: complete linked-object census, clean-room implementation, and
production routing. Software gates pass; live hardware validation is explicitly
blocked by unavailable authorized physical evidence. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

Six exact-named bodies and their shared pool occupy
`[0x005B1B4C,0x005B22BC)`. The bodies contribute 1,776 bytes with SHA-256
`a5a3e25703df5244595d88d3c2653a814fcd43854f059ea5dce3b2a9af0c2fce`;
the 128-byte pool has SHA-256
`fc31e0445401528eb108e36d401ac1f290153a7f9ea1afc9599a348873dc9153`.
The complete 1,904-byte object has SHA-256
`8973bc2f23588773f4ce41491809689c35bbe7f1f835bf5b21c038a5c657e841`.
A separate pathless Thumb body begins at `0x005B22BC`; its diagnostics use a
later pool belonging to another object, closing the conversate boundary.

The exact retained symbols are `APP_PbConversateRxFrameDataProcess`,
`APP_PbConversateTxEncodeNotify`,
`APP_PbConversateTxEncodePrepNoteListRequest`,
`APP_PbConversateTxEncodePrepNoteSelect`,
`APP_PbConversateTxEncodeCommResp`, and
`APP_PbConversateTxEncodeTagTrackingData`. Ten exterior `BL` sites enter
exact starts and the bodies contain 96 calls. Exhaustive direct, `B.W`, and
all-byte scans find no stored entry or strict-interior ingress.

## Message behavior

RX rejects null input or destination with status 6, logs at most the first 32
input bytes, and decodes through nanopb into caller-owned storage. Decode
failure returns 5. Successful input uses byte 1 as its magic value and
suppresses a repeat of the byte at `0x20074FF8` received within 3,000 ms of
the tick at `0x2007485C`, returning 13. A new message updates both globals and
returns zero.

All TX paths clear the 0xFAC-byte message at `0x200F4808` and encode into the
256-byte buffer at `0x2037C2A0`. Successful sends are master-role gated and
use route 1 / service `0x0B`. The five envelopes are:

- notify: command `0xA1`, nested tag 9, 16-bit supplied payload, notify;
- prepared-note list request: command 2, tag 4, zero-valued payload, notify;
- prepared-note selection: command 4, tag 6, one byte plus one 32-bit value,
  notify;
- command response: command `0xA2`, tag 10, supplied response byte and
  caller-supplied magic, transmit;
- tag tracking: command `0xA3`, tag 12, twelve supplied payload bytes,
  notify.

Every envelope except command response derives its magic as the last RX magic
plus one without mutating the global. Encoders return 5 on encode failure and
zero on success even when the role gate suppresses transport. Pointer-taking
encoders return 6 on null; the two prepared-note helpers have no pointer-null
path.

The historical source tree and license remain unavailable. The independently
authored GPL-3.0-only
`components/apollo_main/core_overlay/pb_service_conversate.c` implements the
six linked entries plus bounded buffer-write and message-zero helpers. Eight
selector-isolated leaves produce 1,098 bytes of Thumb text plus eight alignment
bytes with 33 strict relocations. Six guarded redirects replace all 1,776 stock
body bytes while the authenticated 128-byte pool remains official.

Host tests cover buffer bounds, RX null/decode/truncation/replay boundaries,
all five envelopes, role suppression, encoding failure, exact transport
arguments, and last-magic immutability. The canonical overlay/component/package
are `197488/3720884/4499378` bytes with SHA-256
`a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183`,
`026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a`,
and `03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783`.
The 2,018,179-byte flash plan has 2,874 placed, two protected unresolved, and
five container-only regions.

Live master/peer service-`0x0B`, BLE timing, and conversate UI validation needs
a booting source-divergent authorized temple and peer. The right temple is
nonresponsive, the left must remain stock, and the recovery gate prohibits
writes without debugger evidence. Hardware behavior is therefore blocked by
unavailable physical evidence, not validated.
