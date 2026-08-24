# G2 `pb_service_even_ai.c` recovery

Status: complete linked-object census, fail-closed behavioral analysis, and
production-routed clean-room C implementation. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The initial seven retained-path anchors understated this object substantially.
Source-order branches, five code-pool path cells, and 23 retained assertion
records recover 25 exact-named functions in
`[0x004E31CC,0x004E54C8)`. Their bodies total 8,404 bytes with SHA-256
`ecd0001396802c71a88baa787a818f2344cd94403d81b7603eefbf6393a9a6f6`;
the 552 bytes of alignment and distributed literal pools hash to
`6c01debe83935542a43981a122f1a505f1fcb42806a0e40676ec5af895d7638c`.
The complete 8,956-byte object has SHA-256
`d69f6c3ad3c31b07005e0f0f6da22f3c0be4868dbfbe1eb16b1b6549b35e8fed`.
The next unrelated Thumb prologue begins exactly at `0x004E54C8`.

The object contains the frame decoder, ten `PB_RxEvenAI*` handlers, ten
`APP_PbTxEncodeEvenAI*` encoders, notification variants for control, VAD, and
event, and `APP_PbTxEncodeEvenAICommResp`. Twenty-six direct calls enter exact
starts and the bodies contain 494 calls. There is no direct or `B.W`
strict-interior ingress and no stored exact-entry pointer. An all-byte scan
does produce 89 accidental values inside the unusually large code interval;
none names an entry, and the digest is retained so these byte-window
collisions cannot silently become claimed callback ingress.

## Message behavior

`APP_PbRxEvenAIFrameDataProcess` rejects null input with status 2, logs at
most 32 bytes, clears and decodes a 0x20C-byte union, and returns `0x2B` on
nanopb failure. The two-byte state at `0x20074F36` records whether a message
has been seen and its last one-byte magic. An identical subsequent magic is
immediately rejected with status 1—unlike translate, conversate, and
teleprompt, this service has no elapsed-time window. New input updates the
state and dispatches command IDs 1 through 10. Nested handlers return zero on
success, one on provider failure, and two for a null payload.

All encoders clear the shared 0x20C-byte message at `0x200F5884`, encode into
the 256-byte buffer at `0x2037C4A0`, and use route 1 / service 7. Null payload
returns 2, encode failure returns `0x2B`, and successful transport returns
zero. The regular command/tag pairs are `(1,3)` through `(9,11)`, followed by
configuration `(10,13)`:

- control, VAD, ask, analyse, reply;
- skill, prompt, event, heartbeat, configuration.

The retained diagnostics further pin control/VAD status, ask status plus
stream-enable/text-mode, reply command count, skill ID, prompt type, event,
heartbeat count, and configuration voice/speed/duplex fields. Control, VAD,
and event have separate notification encoders driven by the sequence byte at
`0x20074FF9`. The command-response helper uses caller magic, command `0xA1`,
tag 12, a one-byte payload, and the transmit path.

The ten receive handlers relay fixed payload lengths of 2, 2, `0x208`, 1,
`0x208`, `0x10C`, 2, 2, 2, and 4 bytes. Heartbeat response byte 1 is zero only
for left-role plus display-ready selector 7, otherwise 8. Configuration uses
payload bytes 0, 1, and 3 while preserving a zero byte 2. The command-response
helper alone uses tag 12.

The 23 assertion records at `[0x00781C30,0x00781DF4)` independently preserve
each helper name, the same source path, and source-line order. Historical
source and license remain unavailable, so source-only historical functions
are not inferred. The independently authored `pb_service_even_ai.c` provides
25 linked replacements plus two bounded helpers. Its 27 selector-isolated
leaves compile to 2,832 Thumb text bytes plus 36 alignment bytes. Twenty-five
guarded redirects replace all 8,404 stock body bytes through 107 strict
relocations while the 552 distributed official gap/pool bytes remain
retained. Live service-7 master/peer BLE and Even-AI UI validation are
explicitly blocked by unavailable authorized physical evidence.
