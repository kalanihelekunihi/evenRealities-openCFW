# G2 `pb_service_quicklist.c` recovery

Status: complete linked-object census plus clean-room production C routing;
live G2 workflow validation is blocked by unavailable authorized physical
evidence. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

Ten exact-named functions and five owned alignment/literal regions occupy
`[0x0055894C,0x005597F0)`. The bodies contribute 3,468 bytes with SHA-256
`422a8a9bf8b95f2407dff2a37edd28e4086da06184f1aa99ca42e99ec9e831eb`;
the 280 gap/pool bytes have SHA-256
`e9bbff217f66e505c5bf9932b5192b496a7283ee4887e6fb511da63579f9e8ec`.
The complete 3,748-byte object has SHA-256
`50654068015e5cced557275529f0ebf3cfe2b16e9d34c86e2071607ac9fb5a18`.
An unrelated function begins at `0x005597F0`.

Ten exterior calls enter exact starts and the bodies contain 199 calls.
Direct and `B.W` strict-interior ingress are zero, and there is no stored exact
entry pointer. One all-byte interior-looking value is an unaligned collision.
Eight standard assertion records plus two exact retained strings pin all ten
function names, their source order, the retained path, and validation/encode
source lines.

## Message behavior

The dispatcher decodes the shared 0x1238-byte message at `0x200F624C` and
routes item (command 1/tag 3), multi-item (2/4), and event (3/5) payloads.
Null input returns 2 and nanopb decode failure returns `0x2B`; successful
known commands propagate the receive/transmit helper result. Events 1 and 2
are accepted. Item logging exposes UID, index, completion state, bounded title,
timestamp, and timestamp type; multi-item processing exposes data type, total
count, and item count.

Transmit uses the separate 0x1238-byte object at `0x200F7484`, the 0x400-byte
nanopb buffer at `0x2037A5A0`, route 1, and service `0x0C`. Transmit helpers
return 2 on null input, `0x2B` on encode failure, and zero on success. Raw
Thumb instructions show that notification transport results are ignored after
a successful encode. Multi-item notification copies 0xE8-byte item records
into the transmit object, while both notification paths advance the sequence
byte at `0x20074FFD`.

## Production closure

`components/apollo_main/core_overlay/pb_service_quicklist.c` provides thirteen
clean-room source functions: the ten linked entries plus bounded buffer-write,
workspace-zero, and common-transmit helpers. The Apple-clang build emits 1,060
text bytes, 18 alignment bytes, and 26 strict relocations. Ten guarded `B.W`
redirects replace all 3,468 stock body bytes; the five official gap/pool
regions remain retained. The notification copy rejects counts above the twenty
0xE8-byte records that fit exactly before the recovered 0x1230 callback cell.

The host suite covers null/decode/encode failures, all three dispatch paths,
data-manager callbacks, response layouts, sequence wrap, the maximum-item
bound, and send/notify routing. The canonical overlay is 211,718 bytes with
SHA-256 `fd223453f93db03efe91b9c05d601d33938b32af36cab672bfbcf0ded3e46e94`;
the Apollo component is 3,735,114 bytes with SHA-256
`ec639e5f23f1bfc145ac8dc4eeebfebbe07da3c9662864cca2b5387fbba44670`;
the 4,513,608-byte package has SHA-256
`245b64451dbc30eb898e6cea07baf79002544434f85c9ae89b9f151ae8a97799`.

The historical source tree and source-only inventory remain unavailable.
Software functionality is closed, but live service-0x0C peer BLE, persistent
quicklist load/save, response, and notification validation is explicitly
blocked: the authorized right temple is nonresponsive and the left temple must
remain stock. The next protobuf-service software frontier is
`pb_service_dev_config/pb_service_pair_mgr.c`.
