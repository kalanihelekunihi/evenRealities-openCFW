# CASE hex dump lower provider

Authenticated CASE `g2-2.2.6.10/firmware_box.bin` has SHA-256
`36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`.
Original `log_hex_buffer` is `0x080067c8..0x080067fc`, followed by a RAM
pointer literal and the decoded `"%02x "` and `"\r\n"` strings. Its body
returns immediately when byte `0x200000bf` is nonzero. Otherwise it prints
each byte as hex, rechecking that flag before each child call and before the
final CRLF. The loop index is 16 bits; the source contract requires a
readable buffer and length at most 65535.

`hex_log_provider.c` source-defines that full bounded body. It leaves
`g2_log_printf` as an explicit lower import. `verify.py` executes original
and compiled C in Unicorn and intercepts only that child call. It compares
format text, promoted byte argument, flag state, source buffer, and PRIMASK.
Both isolated `-Og` and archive `-Os` objects pass **42 cases**: seven lengths
from 0 through 256, initially enabled/disabled logging, and no change or
disable after the first/second child call. Receipts are `results.json` and
`archive_results.json`. Actual formatted output is outside this boundary.

The deterministic archive and whole-archive relocatable link pass with
**30 objects, 53 provided symbols, and 9 unresolved imports**. Archive
SHA-256: `bae8cb8e420c839ec92f7ab0ca6d6324326b43c9a916eff78a0c3455fd1755d9`.
The original direct 12-name tally remains **5 complete, 7 open**. Of the
three lower imports introduced by `case_send`, **one is now source-defined,
two remain** (`case_write_controller_blocking` and `g2_log_printf`). Thus
the archive has seven open direct names plus two named lower contracts.
These are symbol counts, not equal-sized tasks or time estimates. CASE
startup, full link, runtime ownership, logger output and UART hardware
remain unverified.
