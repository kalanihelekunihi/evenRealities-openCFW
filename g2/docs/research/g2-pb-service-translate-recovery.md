# G2 `pb_service_translate.c` recovery

Status: software-complete and production-routed from clean-room C; live
master/peer BLE and translation-UI validation is explicitly blocked by
unavailable authorized responsive G2 hardware evidence. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

Four exact-named bodies and a shared pool occupy
`[0x0059F53C,0x0059FAE0)`. The bodies contribute 1,324 bytes with SHA-256
`0acba12ce622e3f5044a45e29164bf275f64d30ee8eb8615f3c211beef50f27d`;
the 120-byte pool has SHA-256
`0a9dfaa6ddd2c98157724e809baff1d222b91fc3e2d23238333be1258f86d781`.
The complete 1,444-byte object has SHA-256
`9d31e156165c7371a649d7f048b7b5aaae63554d6e558caa67c20ae04b885ed8`.
The next function at `0x0059FAE0` has unrelated display/startup behavior,
closing the trailing boundary.

The bodies are `APP_PbTranslateRxFrameDataProcess`,
`APP_PbTranslateTxEncodeNotify`, `APP_PbTranslateTxEncodeCommResp`, and
`APP_PbTranslateTxEncodeModeSwitch`. Eight exterior `BL` sites enter exact
starts; the bodies contain 74 calls. No direct call or `B.W` reaches a strict
interior. An all-byte scan finds 28 instruction-byte windows whose values fall
inside the large response body, but no exact/Thumb entry value; their complete
set is pinned so it cannot silently become stored ingress.

## Message behavior

The RX path rejects null input/message with status 6, decodes through nanopb,
returns 5 on decode failure, and suppresses a repeated magic byte received
within 3,000 ms with status 13. Successful new input updates the last-magic
byte at `0x20075000` and tick at `0x20074878`, returning zero.

All TX paths clear the shared 0x854-byte message at `0x200F9EE4`, construct a
small translate envelope, encode into the 0x100-byte buffer at `0x2037CAA0`,
and return 6/5/0 for null/encode failure/success. Notify, mode-switch, and
command-response subtypes are 5, 6, and 7. Notify and mode-switch derive their
magic byte from the last RX magic; command response takes the supplied magic.
Successful sends are gated on the master-role provider and use the already
bounded protobuf BLE send/notify wrappers with transport/service pair `(1,5)`.

The exact historical source path and four stock symbols survive, but no
authenticated historical source tree or historical license is available.
Source-only historical inventory is therefore not inferred.

## Production closure

`components/apollo_main/core_overlay/pb_service_translate.c` is a 9,294-byte,
MIT clean-room implementation (SHA-256
`1e6429d33df883ca498112850f6e38254798d82e88de86d2b2c450d9300d0095`).
Seven selector-isolated source functions compile to 748 Thumb text bytes plus
four alignment bytes. Four guarded `B.W` redirects replace all 1,324 stock
body bytes; the authenticated 120-byte literal pool remains official. The 13
strict relocations bind only to recovered nanopb, tick, role, BLE transport,
and sibling-source interfaces. Host tests cover buffer bounds, RX decode and
replay statuses, every envelope layout, role gating, null/encode failures, and
send-versus-notify behavior.

The canonical production overlay/component/package are 202,484 / 3,725,880 /
4,504,374 bytes with SHA-256 values
`0201c5d6961d87cf65fb189d6ea125a2b627ed0b5fc5cf75036fc58f8019166f`,
`37efb5b3d63c9830646a2a1c50783d60823cbb209a9118c2da224dcc0b673959`,
and `7e6b2ced0cf4adab423d2f3080de733d9bb1feb7b93890bf4cfd48972e70c6b1`.
The 2,123,068-byte flash plan has 3,032 placed, two unresolved, and five
container-only regions and hashes to
`16e1c6df34a39685f9bc891ec71dd472f7078341a0bbfa1fdb034c2d74237705`.

No hardware was accessed. Live service-`0x05` master/peer BLE, replay timing,
nanopb peer interoperability, and translation-UI behavior remain blocked: the
authorized right temple is nonresponsive and the left temple must remain
stock. This is an explicit physical-evidence blocker, not a software-complete
firmware declaration.
