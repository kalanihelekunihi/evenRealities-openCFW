# G2 `pb_service_notification.c` recovery

Status: complete linked-object census and fail-closed behavioral analysis; no
historical source candidate and not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

Nine exact-named functions and three owned alignment/literal regions occupy
`[0x004D6BA8,0x004D798C)`. The bodies contribute 3,318 bytes with SHA-256
`167ff554f205c1df565617756cf9321ccab7fcbc9bded302080997562cdd183b`;
the 238 gap/pool bytes have SHA-256
`4b85b9eedc1ef5fcbddaef6215a002a83668c0af083342d881909b3a97cd6396`.
The complete 3,556-byte object has SHA-256
`367b877b9bd7c1c6c23beee8a5d6b14b37e6f2548437b25706edb75a20959701`.
An unrelated function begins at `0x004D798C`.

Ten exterior calls enter exact starts and the bodies contain 202 calls.
Direct and `B.W` strict-interior ingress are zero, and there is no stored exact
entry pointer. Three all-byte interior-looking values are unaligned
instruction/data collisions. Seven standard 20-byte assertion records pin the
retained path, command-specific function names, and source lines 103, 122, 160,
243, 259, 296, and 312. The dispatcher and app-not-whitelisted notification
wrapper retain exact diagnostic names outside that assertion table.

## Message behavior

`APP_PbRxNotificationFrameDataProcess` returns 2 for null input and `0x2B`
for nanopb decode failure. Commands 1, 3, and 4 run notification-control,
whitelist-control, and whitelist-check handlers and then their matching
transmit wrappers. Other command IDs produce a generic command-`0xA1`/tag-5
response while the dispatcher itself returns success.

The object uses a 76-byte message at `0x200F60E0`, the 256-byte buffer at
`0x2037C7A0`, and route 1 / service 4. Notification control uses command 1/tag
3. App-not-whitelisted notifications use command 2/tag 4, a dedicated notify
transport, and two bounded strings. Whitelist control uses command 3/tag 6.
Whitelist checks use command 4/tag 7: cache failure maps to status 1/error 7,
equal CRCs to status 2/error 0, and unequal CRCs to status 3/error 0.

Regular transmit wrappers return 2 for null input, `0x2B` for encode failure,
and zero for success. The allocated app-not-whitelisted path additionally
returns -1 if notification delivery fails. The historical source tree and
license remain unavailable, so source-only functions are not inferred. No
clean-room candidate exists, the service is absent from `overlay.json`, and
OpenCFW claims zero production ownership bytes. The next retained
protobuf-service frontier is `pb_service_dev_setting.c`.
