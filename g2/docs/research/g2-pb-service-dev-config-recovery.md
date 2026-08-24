# G2 `pb_service_dev_config.c` recovery

Status: software-complete and production-routed from clean-room C; live
service-`0x80` master/peer device-configuration validation is explicitly
blocked by unavailable authorized responsive G2 hardware evidence. Run
addresses use `run = file_offset + 0x00437FE0`.

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

The historical source tree and license remain unavailable, so historical
source-only functions are not inferred.

## Production closure

`components/apollo_main/core_overlay/pb_service_dev_config.c` is an
11,435-byte GPL-3.0-only clean-room implementation (SHA-256
`46c79dbaad289491f195562aea10d3d8ba92684e7227e463b697a04f31b67bc4`).
Five selector-isolated source functions compile to 998 Thumb text bytes plus
four alignment bytes. Three guarded `B.W` redirects replace all 2,646 stock
body bytes while the authenticated 286 gap/pool bytes remain official. The 33
strict relocations bind the dispatcher to the recovered nanopb, command
provider, heartbeat timer, BLE transport, and sibling-source interfaces.

Host tests cover null/decode statuses, all fourteen command IDs, provider
success gating, error classification, unknown-command response encoding, the
30-second heartbeat timer refresh, output bounds, and transmit arguments.
The canonical overlay/component/package are 203,486 / 3,726,882 / 4,505,376
bytes with SHA-256 values
`ef060f12222fcd55be84927416752e0091541b0573921a4bda1588663d46e36b`,
`70446d59e2d7080732284af9d860c78b9561dba3552b0fd696b20e9e84dbd1ab`,
and `7a6aba86acf50a5c05dfdc8039793df2f8840599af5446dbd869f0c36e584991`.
The 2,132,348-byte flash plan has 3,046 placed, two unresolved, and five
container-only regions and hashes to
`8d11759463eb12bc531222dff14d8a5d01e8fa4c3c6ea8fd5fd8df53b124d098`.

No hardware was accessed. Live pairing, role changes, BLE parameters,
disconnect/unpair, restore, heartbeat timing, restart, time synchronization,
audio-control, and peer nanopb interoperability remain blocked because the
authorized right temple is nonresponsive and the left temple must remain
stock. This closes the object software gap, not the wider firmware.
