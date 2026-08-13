# G2 `pb_service_translate.c` recovery

Status: complete linked-object census and fail-closed behavioral analysis; no
historical source candidate and not production-routed. Run addresses use
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

The exact source path and four symbols survive, but no authenticated source
tree or license is available. Source-only function count is therefore not
inferred. No clean-room candidate exists, the object is absent from
`overlay.json`, and OpenCFW claims zero production ownership bytes.
