# CASE blocking UART receive direct provider

Fixed CASE `g2-2.2.6.10/firmware_box.bin` SHA-256 is
`36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`.
Original `case_read_controller_blocking` is `0x080063ec..0x080064e8`;
the source archive exposes its selected caller name `case_bulk_receive`.
The retained body validates UART RX state, buffer, length and 9-bit
alignment; sets busy/error/count state; gets a tick; selects a word-width
and parity mask; waits per item; copies RDR into an 8-bit or 9-bit buffer;
and restores RX ready state on success. `uart_read_provider.c` source-defines
this full bounded body using the separately source-defined tick and wait
providers.

`verify.py` compares stock and compiled C against coherent synthetic UART
handle, peripheral register and writable buffer state. Both isolated `-Og`
and archive `-Os` objects pass **1,440** cases spanning ready/busy RX state,
lengths 0/1/2/3/5, four word-length modes, parity, aligned/odd/null buffer,
and wait failure at multiple calls. The comparator records tick and wait
arguments, return, all UART/peripheral/buffer bytes, and PRIMASK; each
successful wait scripts an RDR value. Receipts: `results.json` and
`archive_results.json`.

With archive source read, source tick getter and source wait provider linked,
`verify.py --archive-object --compose-children` also passes **32** stock/source
ready-ISR cases without child hooks. Receipt: `composed_results.json`.
This is bounded register-memory execution, not a claim about incoming UART
traffic, HAL timing, buffer lifetime, or physical hardware.

The deterministic archive and whole-archive relocatable link pass with
**35 objects, 59 provided symbols, and 7 unresolved imports**. Archive
SHA-256: `5f96f711577e6a8516224770e9ced1791d69bced9320fa8ea454c2d7f9f9a7cf`.
The original 12-name direct provider tally is **6 complete, 6 open**.
The six open direct names are two HAL callbacks, binary and legacy command
dispatch, UART DMA boundary and other UART IRQ path. The lower formatter
`case_vformat` remains the seventh unresolved import. These are named
contracts, not equal-size tasks or a time estimate. Full CASE startup/link,
product state and physical UART behavior remain open.
