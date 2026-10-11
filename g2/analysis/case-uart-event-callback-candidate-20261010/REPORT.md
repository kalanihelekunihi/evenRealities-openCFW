# CASE UART receive-event callback

Fixed CASE `g2-2.2.6.10/firmware_box.bin` SHA-256 is
`36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`.
The retained original RX8 `0x08008998` and RX16 `0x08008758` helpers both
call `0x08005e6a` for their TOIDLE receive-event completion. The exact
two-byte body at `0x08005e6a` is `bx lr`. This binds the selected stock
callback entry and its no-op behavior; it does not establish behavior for
runtime callback registration or the separate RX-completion path.

`uart_event_callback.c` source-defines `HAL_UARTEx_RxEventCallback` with
the observed no-op body. `verify.py` checks the original caller references
and bytes, then compares stock and compiled source across **32** UART
pointer, size and initial PRIMASK combinations in both isolated `-Og` and
archive `-Os` builds. All input registers, 64 KiB RAM, and PRIMASK match;
receipts are `results.json` and `archive_results.json`. This has no physical
UART or callback registration claim.

The deterministic archive rebuild and whole-archive relocatable link pass
with **36 objects, 60 provided symbols, and 6 unresolved imports**. Archive
SHA-256: `b0c6d9feda844782fbb05efcc6302a91982cc10637097ee503773256ec41c40d`.
The original 12-name direct tally is **7 complete, 5 open**. The five
remaining direct names are RX completion callback, binary and legacy command
dispatch, UART DMA boundary, and other UART IRQ path. The lower formatter
`case_vformat` is the sixth unresolved import. RX completion points to the
larger product parser `0x08006544`; the existing parser comparator stops at
bulk receive and event post, so this pass does not alias or claim that whole
callback. These are symbol counts, not equal-sized tasks or a time estimate;
full CASE startup/link, runtime ownership, and hardware remain open.
