# G2 `pb_service_dev_config.c` recovery

Status: complete linked-object census and fail-closed behavioral analysis; no
historical source candidate and not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

Three exact-named functions and three owned literal regions occupy
`[0x004D83D8,0x004D8F4C)`. The bodies contribute 2,646 bytes with SHA-256
`401049831bcd87292d5897f5f6eca7d19eb0f8dc906233bb89d4e77a0214647b`;
the 286 gap/pool bytes have SHA-256
`c28c50a8e79cf41c63c0ffc56384d7b3b6ea1481e482d64ebfcd9f78e57cbe4d`.
The complete 2,932-byte object has SHA-256
`d956ed13c98123c0ddb960e65c1ca1baa8629675bba7663b2978505d122f044a`.
An unrelated Thumb prologue begins at `0x004D8F4C`.

The object contains `APP_PbRxDevCfgFrameDataProcess`, `APP_PbRxErrorCode`,
and `APP_PbTxEncodeErrorCode`. One exterior call enters the dispatcher; its
two internal calls root the other bodies. The three functions contain 172
calls. There is no direct or `B.W` strict-interior ingress and no stored exact
entry pointer. Two all-byte address collisions are retained in the audit as
non-entry instruction windows rather than promoted as pointers. One 20-byte
assertion record pins the retained path, dispatcher symbol, and line 45.

## Message behavior

The dispatcher rejects null input with status 2 and decodes a 0xD0-byte
nanopb message; decode failure returns `0x2B`. Success returns zero after
dispatching these command IDs:

- 4 authentication, 5 pipe-role change, 6 ring-connect information;
- 7 BLE connection parameters, 8 disconnect information, 9 unpair;
- 10 command exception/error code, 11 set-device information, 12 get-device
  information;
- 13 restore factory settings, 14 base-connect heartbeat, 15 quick restart;
- 128 time synchronization and 129 audio control.

The command handlers cross into the separately ranked pairing-manager and
device-setting objects. Command 10 calls the local error classifier, which
recognizes error values 1, 5, 7, 8, and 9 for diagnostics and returns zero.
An unknown command sends error value 8 through the local response encoder.

The response encoder uses the shared 0xD0-byte message at `0x200F57B4` and
the 256-byte buffer at `0x2037C3A0`. It emits command 10 / tag 9, preserves
the request magic, and carries the original command plus one-byte error code.
It transmits on route 1 / service `0x80`; success returns zero and nanopb
encode failure returns `0x2B`.

The historical source tree and license remain unavailable, so source-only
functions are not inferred. No clean-room candidate exists, the service is
absent from `overlay.json`, and OpenCFW claims zero production ownership
bytes. The next retained protobuf service frontier is `pb_service_health.c`.
