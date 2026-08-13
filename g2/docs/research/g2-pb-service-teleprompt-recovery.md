# G2 `pb_service_teleprompt.c` recovery

Status: complete linked-object census and fail-closed behavioral analysis; no
historical source candidate and not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

Seven exact-named bodies and their shared alignment/literal tail occupy
`[0x005885B4,0x00588D74)`. The bodies contribute 1,854 bytes with SHA-256
`24f933ac204a24fdd8946526538df3b7e301314c079c8ea60a7b0c59813f8b3b`;
the 130-byte tail has SHA-256
`9bd568fdf74affc604e3f493fa2fa3665bc5a08a87e1b828be1a8271364ef0c8`.
The complete 1,984-byte object has SHA-256
`06e85d974b48111ab51fbfdff1cc23c56e1274f4971f1ca5407989440b75d0cc`.
A separate pathless Thumb body begins at `0x00588D74`, closing the teleprompt
boundary without absorbing its later literals.

The retained symbols are `APP_PbRxTelepromptFrameDataProcess`,
`APP_PbTelepromptTxEncodeCommResp`, `APP_PbTxEncodeStatusNotify`,
`APP_PbTxEncodeFileListRequest`, `APP_PbTxEncodeFileSelect`,
`APP_PbTxEncodePageDataRequest`, and `APP_PbTxEncodeScrollSync`. Eleven
exterior `BL` sites enter exact starts and the bodies contain 98 calls. No
stored function pointer or real strict-interior branch survives. The sole raw
interior-looking pair, `0x0057FE74 -> 0x005885D8`, begins on the second
halfword of the valid four-byte `mul r0, r0, r8` at `0x0057FE72`; it is not an
instruction boundary.

## Message behavior

RX rejects null input or destination with status 6, logs at most the first 32
bytes, and decodes through nanopb into caller-owned storage. Decode failure
returns 5. Successful input uses byte 1 as its magic value and suppresses a
repeat of the byte at `0x20074FFE` received within 3,000 ms of the tick at
`0x20074870`, returning 13. A new message updates both globals and returns
zero.

Every TX helper clears the 0xF58-byte message at `0x200F873C`, encodes into
the 256-byte buffer at `0x2037C9A0`, and uses route 1 / service 6 when the
master-role gate permits transport. Encode failure returns `0x2B`; success
returns zero even when the role gate suppresses transport. These TX functions
dereference their pointer arguments without a null guard, so no null-status
contract is inferred. The envelopes are:

- command response: caller magic, command `0xA6`, tag 12, one-byte response,
  transmit;
- status: last RX magic plus one, command `0xA1`, tag 7, 16-bit status,
  notify;
- file-list request: last magic plus one, command `0xA2`, tag 8, one byte,
  notify;
- file selection: last magic plus one, command `0xA3`, tag 9, 66 bytes,
  notify;
- page-data request: last magic plus one, command `0xA4`, tag 10, 32 bits,
  notify;
- scroll synchronization: last magic plus one, command `0xA5`, tag 11,
  twelve bytes, notify.

The derived TX magic is not written back to the RX global. The historical
source tree and license remain unavailable, so source-only functions are not
inferred. No clean-room candidate exists, the service is absent from
`overlay.json`, and OpenCFW claims zero production ownership bytes. The next
retained protobuf service frontier is `pb_service_even_ai.c`.
