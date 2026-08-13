# G2 `pb_service_conversate.c` recovery

Status: complete linked-object census and fail-closed behavioral analysis; no
historical source candidate and not production-routed. Run addresses use
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

The historical source tree and license remain unavailable, so source-only
functions are not inferred. No clean-room candidate exists, the service is
absent from `overlay.json`, and OpenCFW claims zero production ownership
bytes. The next smallest retained service frontier is
`pb_service_teleprompt.c`.
