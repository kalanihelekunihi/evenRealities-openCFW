# G2 `pb_service_ring.c` recovery

Status: complete linked-object census, clean-room production implementation,
and fail-closed stock/production analysis. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

Four exact-named bodies and their alignment/literal tail occupy
`[0x005CE1DC,0x005CE7C4)`. The bodies contribute 1,362 bytes with SHA-256
`6bf1505dabaea4b5a7a4d4708729bf96cd61dba84b7bfef4a15b0224732f2be7`;
the 150-byte tail has SHA-256
`dabbf3fe420fa5c2fb505c225a4641a092f66ccc9ac4ad01118557fb018e4deb`.
The complete 1,512-byte object has SHA-256
`2e570db8cab30734f3a547a7ad4dfa704d167010710fa5a925d465dc4e81348c`.
The next unrelated body begins at `0x005CE7C4`.

The bodies are `APP_PbRxRingFrameDataProcess`, `PB_RxRingEvent`,
`APP_PbTxEncodeRingEvent`, and `RingDataRelay_common_data_handler`. Three
internal `BL` sites enter exact starts. The relay record at `0x006A45B0`
contains service `0x91` and the only stored entry pointer, the odd Thumb value
`0x005CE691`. The bodies contain 82 calls. No real branch or pointer reaches a
strict interior. A raw halfword scan reports `0x004DDD58 -> 0x005CE370`, but
the site is the second halfword of the valid 32-bit `SDIV` instruction at
`0x004DDD56`; its exact bytes are pinned rather than misclassified as ingress.

## Message contract

Relay event type zero forwards its data and 16-bit length to the RX body;
other types are diagnosed and ignored. The callback always returns zero. RX
decodes through nanopb into the 64-byte object at `0x200F86BC`. Null input
returns 2, decode failure returns `0x2B`, and an unsupported command or invalid
nested pointer returns 1. Command 1 dispatches the nested ring event and
returns the encoder status.

The nested event representation contains a 16-bit MAC count, up to six MAC
bytes, an event-ID byte, and a 32-bit event parameter. Event ID 1 is the
supported value. Other event IDs are logged but not rejected by the helper.

TX clears the separate 64-byte object at `0x200F86FC`, sets command 1,
echoes the request sequence, selects nested payload 3, and copies the event
ID/parameter and MAC count. MAC bytes are copied only when the count is 1-6;
the count itself remains preserved outside that range. The error byte is set
to zero. Nanopb encodes into the 256-byte buffer at `0x2037C8A0`; success
calls the already bounded protobuf BLE transmit wrapper with route 1 and
service `0x91`. TX returns 2/`0x2B`/0 for null/encode failure/success.

Two retained 20-byte assertion descriptors identify the nested validator and
encoder at source lines 88 and 130. Together with the pool they provide all
three references to the exact retained source path.

The historical source tree and license remain unavailable. OpenCFW therefore
implements only the four linked stock entries plus the source-only bounded
nanopb output callback required by the recovered encoder ABI. The five
functions compile to 594 bytes with four bytes of generated alignment and nine
strict relocations. Four entry redirects replace all 1,362 stock body bytes;
the 150-byte alignment/literal tail remains official. Host tests cover null,
decode/encode failure, command routing, event behavior, MAC bounds, output
buffer bounds, transport arguments, and relay dispatch. The production source,
overlay leaves, redirects, component, package, and deployment plan are pinned
by `tools/analyze_g2_pb_service_ring.py`.

Software closure is complete for this object. Live paired-G2 BLE relay,
nanopb-peer interoperability, and physical ring-event behavior remain blocked
because no authorized physical evidence is available; this is not a claim of
hardware validation. The next smallest retained service frontier is
`pb_service_conversate.c`.
