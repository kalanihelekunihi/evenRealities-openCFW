# CASE UART RX completion callback

Authenticated CASE `g2-2.2.6.10/firmware_box.bin` SHA-256 is
`36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`.
The retained stock RX8/RX16 helpers call product parser `0x08006544` for
standard RX completion. `frame_callback_offline/frame.c` already source
defines that parser; `uart_rx_complete_callback.c` binds its HAL callback
ABI by calling the source parser. This pass validates the suffix that the
earlier parser comparator stopped before, while keeping event posting as
an explicit child boundary.

`verify.py` executes the stock `0x08006544` body and compiled source HAL
callback plus frame parser, UART start, blocking bulk read, tick getter and
UART flag wait. The event-post child is intercepted on both sides with
argument comparison and the same return. Both isolated `-Og` and archive
`-Os` objects pass **4,192** coherent frame/UART states: count boundaries
0/1/2/3/4/5/7/59/1199/1200, binary and DE prefixes, current bytes,
UART ready/busy state, USART1/other handle, and prior last byte. The oracle
compares event calls, 8 KiB of shared RAM (including frame and UART handle),
peripheral register window, and PRIMASK through return. Receipts:
`results.json`, `archive_results.json`.

Count-four CF fixtures whose newly appended high length byte would request
a bulk read beyond the synthetic frame allocation are excluded. This is a
bounded source contract for coherent available storage; it does not prove
malformed-frame safety or every arbitrary input. Event group side effects,
real UART traffic, scheduler behavior and object lifetime also remain
outside this comparator.

The deterministic archive and whole-archive relocatable link pass with
**37 objects, 61 provided symbols, and 5 unresolved imports**. Archive
SHA-256: `7b26065eb1ae19f242b5a387559e322285f5f34f30e408da68cc9a880cfa9a00`.
The original direct 12-name tally is **8 complete, 4 open**: binary and
legacy command dispatch, UART DMA boundary, and remaining UART IRQ path.
The lower formatter `case_vformat` is the fifth import. These are named
contracts, not equal-size tasks or a time estimate; CASE full startup/link
and physical-device validation remain open.
