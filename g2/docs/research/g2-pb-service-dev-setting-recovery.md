# G2 `pb_service_dev_setting.c` recovery

Status: software-closed and production-routed through an independently authored
clean-room C implementation. Hardware validation is explicitly blocked because
the authorized right temple is nonresponsive and the left temple must remain
stock. Run addresses use `run = file_offset + 0x00437FE0`.

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
names, and the repeated validation/encode/error source lines. The complete
stock surface remains retained as evidence: all 3,432 body bytes are replaced
in production while the 284 alignment/literal bytes remain official.

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
five-byte cache at `0x20004394`, applies the system clock/timezone, synchronizes
the peer, refreshes heartbeat state, and persists the cached pair after
transmit. Audio-control remains deliberately accepted as a no-op, matching the
stock service's unsupported behavior, while its response still uses the normal
bounded serializer and transport.

## Production closure

`components/apollo_main/core_overlay/pb_service_dev_setting.c` contributes 12
selector-compiled functions: two bounded transport helpers and all ten stock
receive/transmit leaves. Apple clang emits 934 text bytes and 6 alignment bytes
with 30 strict relocations. Ten `B.W` entry replacements redirect all 3,432
stock body bytes. The canonical artifacts are:

- overlay: 211,718 bytes, SHA-256
  `fd223453f93db03efe91b9c05d601d33938b32af36cab672bfbcf0ded3e46e94`;
- Apollo component: 3,735,114 bytes, SHA-256
  `ec639e5f23f1bfc145ac8dc4eeebfebbe07da3c9662864cca2b5387fbba44670`;
- package: 4,513,608 bytes, SHA-256
  `245b64451dbc30eb898e6cea07baf79002544434f85c9ae89b9f151ae8a97799`.

Host tests cover factory-reset ordering and gates, restart, heartbeat, time
cache/system/peer/persistence behavior, audio-control compatibility, null and
encoding failures, caller-owned buffers, and both normal and direct protobuf
transport routes. The destructive and peer-dependent workflows cannot be
claimed as physically validated without live service-`0x80` evidence. The next
unimplemented retained protobuf services are `pb_service_quicklist.c` and
`pb_service_pair_mgr.c`.
