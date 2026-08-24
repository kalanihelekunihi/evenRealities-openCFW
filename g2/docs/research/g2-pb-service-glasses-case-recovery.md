# G2 `pb_service_glasses_case.c` recovery

Status: software-complete clean-room production replacement; physical
glasses/case interoperability validation is explicitly blocked by unavailable
authorized evidence. Run addresses use `run = file_offset + 0x00437FE0`.

## Result

Four exact-named bodies and their shared pool occupy
`[0x00510A0C,0x00510FD8)`. The bodies contribute 1,360 bytes with SHA-256
`39f291afe8bb87e933c35c4d28ed0a66f7f925dcdb0ca765b2bf3562f25e2472`;
the 124-byte pool has SHA-256
`e6e942104a74517b41485867b0b592911951af365363935b324d92110a362de1`.
The complete 1,484-byte object has SHA-256
`ac1926863f4700afd938a0f9d234c3a6c0be103f327f591c7cc066d13be61bf2`.
A separate Thumb function begins at `0x00510FD8`, closing the trailing
boundary two bytes earlier than the first discovered function at
`0x00510FE2` suggested.

The bodies are `APP_PbRxGlassesCaseFrameDataProcess`,
`PB_RxGlassesCaseInfo`, `APP_PbTxEncodeGlassesCaseInfo`, and
`APP_PbNotifyEncodeGlassesCaseInfo`. Four `BL` sites enter exact starts: two
external callers and two calls within the object. The bodies contain 86
calls. No direct call or `B.W` reaches a strict interior. An all-byte scan
finds six accidental byte windows whose values fall inside bodies, but no
exact or Thumb entry value; their complete set is pinned.

## Message contract

RX decodes through nanopb into the ten-byte object at `0x200F5A90`. Null
input returns 2, decode failure returns `0x2B`, and an unsupported command or
invalid nested payload returns 1. Command 1 with a valid nested payload is
answered and returns zero.

Both TX paths clear a separate ten-byte object at `0x200F5A9C` and encode it
into the 256-byte buffer at `0x2037C5A0`. The in-memory representation is:

- command discriminator 1 at byte 0;
- response/notification sequence at byte 1;
- nested-payload selector 3 at bytes 2-3;
- battery, charging, lid, glasses-present, and error bytes at offsets 4-8;
- final padding byte at offset 9.

The response echoes the request sequence and reads the first four state bytes
from providers `0x004AC726`, `0x004AC73C`, `0x004AC752`, and `0x004ACAD0`;
it sets error to zero. The notification copies four supplied bytes, sets error
to zero, and post-increments the byte counter at `0x20074FFA` before encode.
Consequently, encode failure still consumes a notification sequence value.
Both paths return 2/`0x2B`/0 for null/encode failure/success. Success calls
the already bounded protobuf BLE transmit or notify wrapper with route 1 and
service `0x81`.

Three retained 20-byte assertion descriptors identify the nested validator
and both encoders at source lines 86, 100, and 138. Together with the main
pool they provide all four references to the exact retained source path.

## Production closure

The independently authored GPL-3.0-only source at
`components/apollo_main/core_overlay/pb_service_glasses_case.c` contains the
four linked entries plus the bounded nanopb output callback. Five
selector-isolated Thumb leaves compile to 546 text bytes plus ten alignment
bytes with sixteen strict relocations. Four guarded `B.W` redirects replace
all 1,360 stock body bytes while preserving the authenticated 124-byte stock
literal pool.

The canonical Apple build is pinned at 195,030 overlay bytes
(`2005214a...f116`), 3,718,426 Apollo-component bytes
(`2431adf1...1aaa`), and 4,496,920 package bytes
(`3a049e5c...272b`). The 2,004,497-byte deployment plan
(`ff3e18cf...aa93`) contains 2,854 placed regions, two protected unresolved
regions, and five container-only regions. Host behavior, one-entry selector
builds, source identity, relocation topology, component replacements, retained
pool, manifest regions, package, and aggregate protobuf ownership are all
fail-closed.

No authorized live service-`0x81` temple/case exchange or physical case-state
evidence is available. The authorized right temple is application-dead, the
left temple must remain stock, and the recovery gate forbids further writes.
Battery/charging/lid/presence providers, BLE interoperability, notification
sequencing, and physical state transitions therefore remain hardware-blocked;
they are not claimed as validated or as overall firmware completeness.
