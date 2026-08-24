# G2 `pb_service_notification.c` recovery

Status: complete linked-object census, clean-room implementation, production
routing, and software verification. Live hardware validation is explicitly
blocked by unavailable authorized responsive-device evidence. Run addresses
use `run = file_offset + 0x00437FE0`.

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
license remain unavailable, so source-only functions are not inferred.

## Production closure

The independently authored `pb_service_notification.c` contributes 12
selector-isolated functions totaling 1,326 compiled Thumb bytes plus 16
alignment bytes. Nine guarded redirects replace all 3,318 stock body bytes;
34 strict relocations bind only to recovered nanopb, BLE, allocation,
notification-state, tick, whitelist, and redirected sibling-source
interfaces. The 238 authenticated alignment/literal/descriptor bytes remain
retained. Host behavior, selector compilation, relocation, component,
manifest, package, deployment-plan, complete-service-ledger, and origin-
accounting gates are green.

The Apple overlay/component/package identities are 205,714 / 3,729,110 /
4,507,604 bytes with SHA-256 values
`a84d243b3a561e7db38d16bc30def52906da0530b984b25cb1606f7749c35ff8`,
`2b19af2b2887c2a3f20d1603cf08db95a617428475018aaa7d3fa880840060ce`,
and `07b3e44039e7c1f33ff31552f5997992fa658006f432f50c57b1a58cc4893755`.

No hardware was used. Live service-4 peer BLE, notification-control,
whitelist-control, whitelist-check, app-not-whitelisted, and nanopb
interoperability remain blocked: the authorized right temple is nonresponsive
and the left temple must remain stock. The next unresolved software frontier
is `pb_service_setting.c`.
