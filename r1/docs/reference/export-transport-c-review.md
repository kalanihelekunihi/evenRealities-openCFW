# R1 generic export transport dependencies in C, 2026-11-11

The stock `0x32598` `pb_tran` fragmenter now has a C implementation in
`r1/src/application/board/native_protocol_fragment.c`, next to the distinct
`0x32408` EUS fragmenter. It computes the existing CRC-32C before the
4,096-byte limit check, emits descending sequence fragments with a six-byte
sequence/CRC/channel header and at most 238 payload bytes, includes an empty
terminal fragment for an exact multiple of 238, reloads the shared sender
callback for each fragment, and ignores the callback result. The callback
cell remains owned by `native_protocol_fragment_state.c`.

The stock `0x4ca08` fast-parameter command now has a C implementation in
`r1/src/application/board/native_connection_parameters.c`. It cancels the
pending packed fast and slow events in that order, schedules fast mode
immediately, then schedules the slow-mode return after 61,440 milliseconds.
It uses the existing delayed-event provider and source-owned dispatcher.

The ignored probes under `build/r1-pb-fragment-c-20261111/` compile the
source function bodies for host use. The fragment probe covers lengths
0, 1, 237, 238, 239, 4,096 and 4,097, channel narrowing, CRC placement,
fragment payloads and ignored sender status. The fast-mode probe covers
2,048 handle/log-mode combinations and the exact provider-call order.
ASan and UBSan pass. A separate Unicorn probe executes the locked stock
`0x32598` body for the same seven lengths with external CRC, move, logger,
and send calls mocked; its frame and limit checks pass. These probes do not
validate live BLE delivery.

`build/sources-r1-pb-fast-c-20261111/report.json` compiles 939/939
application and 82/82 bootloader units with no failures or duplicate strong
symbols. The strict application receipt at
`build/r1-link-pb-fast-c-20261111/report.json` retains 12 unresolved
functions and uses 644,624 of 696,320 flash bytes. The strict bootloader
receipt at `build/r1-boot-link-pb-fast-c-20261111/report.json` links with a
valid vector. This was the transport-only checkpoint; the
[export command](export-command-c-review.md) now reaches both providers.

Executing the stock `0x286f4` scatter decoder over the locked
`0xc4610` stream confirms the cold command state at `0x20006c28`:
inactive, descriptor pointer `0x20006918`, offset zero. That descriptor
starts with identifier one, zero length and checksum, then Thumb callback
pointers `0x58de5` (prepare), `0x592bd` (read), `0x58d65`
(start guard), and `0x58d55` (finish guard). The ignored decoder
probe is `build/r1-export-descriptor-20261111/decode.py`. The start and
finish callbacks have C owners in `native_export_guard.c`. The prepare/read
callbacks and command now have C owners as recorded in the
[command review](export-command-c-review.md).
