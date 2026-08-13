# G2 `pb_service_dev_setting.c` recovery

Status: complete linked-object census and fail-closed behavioral analysis; no
historical source candidate and not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

Ten exact-named functions and four owned alignment/literal regions occupy
`[0x00542DC4,0x00543C48)`. The bodies contribute 3,432 bytes with SHA-256
`dc1d832025cc77165d7be3e84a37074fb244e78fe6558f2b0941a048f0404d04`;
the 284 gap/pool bytes have SHA-256
`021cd839f9bdc85358f25bf9340d0662e6bc736b41b35786c3604ba374de0cdc`.
The complete 3,716-byte object has SHA-256
`f65791291601ac4dc39715a64b3efbe361a6df101a3c691d6aa17af680abfd99`.
An unrelated function begins at `0x00543C48`.

Ten exterior calls enter exact starts and the bodies contain 222 calls.
Direct and `B.W` strict-interior ingress are zero, and there is no stored exact
entry pointer. One all-byte interior-looking value is an unaligned collision.
Twenty standard assertion records pin the retained path, all ten function
names, and the repeated validation/encode/error source lines.

## Message behavior

The five receive/transmit pairs cover factory restore (command `0x0D`, tag
`0x0C`), base-connection heartbeat (`0x0E`/`0x0D`), quick restart
(`0x0F`/`0x0E`), time synchronization (`0x80`/`0x80`), and the currently
unsupported audio-control surface (`0x81`/`0x81`). Transmit uses route 1 and
service `0x80`; buffers and message storage are caller-owned. Receive wrappers
return 2 for null payload and zero for accepted input. Transmit wrappers return
2 if any required pointer is null, `0x2B` on nanopb encode failure, and zero on
success.

Factory restore coordinates display shutdown, persistent reset, onboarding
state, whitelist-file removal, bond clearing, filesystem formatting, and
restart. Time synchronization copies `{utc_seconds:u32, timezone:i8}` to the
five-byte cache at `0x20004394`, applies the system clock/timezone, and reports
the cached pair after transmit. The historical source tree and license remain
unavailable, so source-only functions are not inferred. No clean-room
candidate exists, the service is absent from `overlay.json`, and OpenCFW claims
zero production ownership bytes. The next retained protobuf-service frontier
is `pb_service_quicklist.c`.
