# GX8002 codec UART3 drain/copy boundary

**320 original/source comparisons PASS** for ring-empty0x598134, single-byteget0x5981E0, bounded ringread0x59820A and actual codecUARTread0x58FB2A. [Results](results.json), [receipt](reproduction-receipt.json), [readable C](../../components/audio/codec_uart_drain_offline/drain.c), [interface](../../components/audio/codec_uart_drain_offline/drain.h). Four small bodies are reconstructed, with valid initialized mask63/storage inputs only. No source/vendor byte-identity claim.

Single get returns0 on empty without writing destination; otherwise copies one byte and advances read withmask63. Bounded read returns min(capacity,available), including wrap, copying caller-owned output independently of later ring reuse. Empty, capacity0/1/3/64/205, occupancy0/1/3/63 and readpositions0/1/62/63 are tested. Original58FB2A returns actual drained count; decompiler's void prototype must not be used as a caller contract.

**UART3 is the GX8002 codec control/DFU link, not the temple-sync task stream.** Existing [consolidated protocol reference](../../docs/reference/protocols.md) already identifies that role; actual callers of58FB2A are codec serial/command receive paths58FAD2,579CBC and57C1FC. Raw callback58FB1C writes ring20073ED4/storage200731B0 via5981C4. CodecUARTread drains that same ring. There is no demonstrated UART3-to-5417A4 sync-stream route. Any earlier tentative next-lead wording implying such a route is superseded by this concrete caller chain.

The previous staging source shows63usable ring bytes and **oldest-byte eviction** when full. Consumer read now establishes the other ownership boundary: synchronous caller copy and read-index advancement. In contrast, logger/sync stream admission can reject an incoming suffix. Neither fixture behavior establishes live codec/temple loss or concurrency safety.

58FAD2 statically loops one-byte reads with an OS tick-based deadline/delay boundary; its exact timer arithmetic, wrap and scheduling remain unvalidated here. Do not label its numeric timeout milliseconds. Fixed codecBUXX framing, control and DFU consumers are already documented; a complete command/response execution with actual timeout/IRQ arrival is a remaining bounded composition lead.

Prior seals,110inputs,fourcheckpoints and observed index preserved. No Git mutations, commits, production/device/shared-state edits. No synthetic successful codec response or physical measurement is fabricated.
