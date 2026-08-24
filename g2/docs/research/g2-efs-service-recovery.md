# G2 `efs_service.c` recovery

Status: complete linked-object census, clean-room twelve-function C
reconstruction, production routing, host behavior tests, Cortex-M55 selector
builds, and fail-closed artifact accounting. Live media validation is blocked
because no authorized responsive G2 peer is physically available. Run
addresses use `run = file_offset + 0x00437FE0`.

## Result

The six retained-path anchors are only half of the object. Six adjacent
pathless functions complete a twelve-function inventory in
`[0x00456722,0x00458DF0)`. The bodies contribute 9,276 bytes with SHA-256
`bbc93a69d35b24750a74a667598ff599189ca52d2b6223578a303854a16edf44`;
the 658 owned alignment/literal bytes have SHA-256
`fcd21039255ece1191801ddc03d6d9ab01209d468a6decfaa39cf369f43f23d6`.
The complete 9,934-byte object has SHA-256
`22a070bb00d0a5555c5a1867804a1fe89678350777c9f3e42258bc7953473175`.
The next translation unit begins at `0x00458DF0`.

Thirty-five direct calls enter exact starts: twenty-five are intra-object and
ten are exterior. The bodies contain 559 direct calls. Direct strict-interior
ingress is zero. Ten wide branches stay inside their owning bodies, there are
no stored exact-entry pointers, and eight all-byte interior-looking values are
unaligned collisions. Four path cells and the retained diagnostic strings pin
the exact names `_evenEfsReplyToAPP`, `_fileCaculateCRC`,
`_efsFileCmdParse`, `_efsFileRawDataParse`, `_efsExportFileParse`, and
`EFS_CancelExport`; the six pathless helpers retain conservative semantic
names in the function manifest.

## Protocol and state

The frame dispatcher routes `0xC4` to import control, `0xC5` to import raw
data, and `0xC6`/`0xC7` to export control/data. Replies are two-byte payloads
sent through the already recovered EFS-over-BLE wrapper. Control values are
start (0), continuation/activation (1), result check (2), and export cancel
(3). Three small pathless helpers emit fixed `0xC5` payloads `{1,4}`, `{1,2}`,
and `{1,5}`.

The shared 0x78-byte transfer object is at `0x20071CC8`. It contains the file
handle/open flag, an 80-byte path, file type, size, received/calculated CRCs,
chunk length, received/remaining totals, progress, and the `isStart` byte.
Import and export use separate 4 KiB buffers at `0x2035BE08` and `0x2035ADF8`.
Android notification JSON is capped at `0x2137` bytes; its dynamic pointer is
stored at `0x20074554`. The standalone export-active flag is at `0x20074FBC`.

Import types are notification whitelist (0), Android message JSON (1), logger
file (2), tracepoint file (3), and arbitrary file (`0xAA`). Types 2 and 3 are
rejected on import. Whitelist chunks are written and read back for immediate
verification; completion checks both size and the previously recovered
non-reflected CRC-32C. Android JSON accumulates in RAM and is handed to its
consumer only after size/CRC validation. Export validates logger/tracepoint
paths, calculates size/CRC, sends metadata, streams 4 KiB chunks, and closes
or resets state on completion, failure, result acknowledgement, or cancel.

The historical source tree and its license remain unavailable, so historical
source-only functions are not inferred. The independently authored
`components/apollo_main/core_overlay/efs_service.c` now supplies all twelve
recovered entry points. Its 2,936 compiled text bytes plus 16 alignment bytes
are appended to the Apollo component with 68 strict relocations; generated
entry redirects replace all 9,276 stock body bytes while the authenticated 658
alignment/literal bytes remain official compatibility data. The production
package is 4,521,690 bytes with SHA-256
`1b92f424d318c6c24579daf4af11ed3b5dbc689a9addfa45ead3b339141e6487`.

Host tests cover whitelist verification, Android JSON capacity/consume,
arbitrary-file import, path-gated logger/trace export, metadata, 4 KiB chunks,
status helpers, dispatch, registration, and cancellation. Physical evidence
for live whitelist import, Android JSON consumption, arbitrary-file import,
logger/trace export, streaming, CRC/size failure, disconnect, and resume is
explicitly blocked: the authorized right temple is nonresponsive, the left
temple must remain stock, and no authorized responsive peer/media pair is
available. This is not a hardware completeness claim.
