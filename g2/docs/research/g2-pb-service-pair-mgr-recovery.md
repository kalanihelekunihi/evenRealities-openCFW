# G2 `pb_service_pair_mgr.c` recovery

Status: complete linked-object census and fail-closed behavioral analysis; no
historical source candidate and not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The 17 path-correlated functions expand to 20 linked functions after restoring
three tiny source-order helpers. Thirteen owned alignment/literal regions close
the object at `[0x004BB3DC,0x004BD054)`. Bodies contribute 6,564 bytes with
SHA-256
`959c59f6d2ef16c33f05f2084595c5eaf29ced61bb6d85354df45a94e784c94d`;
the 724 gap/pool bytes have SHA-256
`91fd838ab679b32d0c207f7fbdcb6b98a0a8c630d910e5f1fd307597eb060c91`.
The complete 7,288-byte object has SHA-256
`563a40809c252f16286eba50c48c5ec70086a0ac925e7b0d1344f8cb5fb5f79d`.
An unrelated function begins at `0x004BD054`.

Twenty-five calls enter exact starts and the bodies contain 418 calls. Direct
and `B.W` strict-interior ingress are zero. Six intentional stored Thumb
pointers all target `PB_TxEncodeNotifyRingConnectInfo` at `0x004BC419`; the
only other raw interior-looking value is an unaligned collision. Twenty-three
assertion records and seven additional exact retained function strings pin the
path, source order, public/helper names, and validation/encode source lines.

## Message behavior

The receive/transmit surfaces cover security authentication (command 4/tag 3),
pipe-role change (5/4), ring-connect information (6/5), BLE connection
parameters (7/6), disconnect information (8/7), and unpair information (9/8).
They use route 1 and service `0x80`. Standard receive null status is 2;
transmit helpers return 2 for invalid or unavailable storage, `0x2B` on nanopb
encode failure, zero on success, and -1 for notification transport failure.
Allocated security-auth and ring-connect notifications use 0x1A8-byte message
objects.

The byte at `0x20074FFC` gates deferred security-auth notification. Ring-connect
processing separates common validation from owner execution, applies connection
policy/throttling, and exposes both direct and queued notification paths. BLE
parameter requests select the product connection mode. Disconnect processing
clears connection policy and schedules teardown; unpair processing accepts a
six-byte ring MAC when present and still performs global binding cleanup for
the supported device states.

The historical source tree and license remain unavailable, so source-only
functions are not inferred. No clean-room candidate exists, the service is
absent from `overlay.json`, and OpenCFW claims zero production ownership
bytes.

## Completed protobuf-service frontier

`tools/manifests/g2-pb-service-complete-closure.tsv` reconciles all 15 retained
protobuf-service paths. Their original lower-bound census of 119 functions /
40,844 body bytes expands to 143 linked functions / 47,644 body bytes and
51,744 total physical object bytes. Twenty-four restored functions contribute
the 6,800-byte body delta. Every retained protobuf-service path now has a
pinned linked-object closure; historical source inventory and production
ownership remain deliberately separate and open/zero.
