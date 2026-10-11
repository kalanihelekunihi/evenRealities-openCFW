# CASE diagnostic wrapper and byte output callback

Fixed CASE image `g2-2.2.6.10/firmware_box.bin` SHA-256 is
`36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`.
Original `g2_log_printf` at `0x08009170..0x08009188` saves the four argument
registers, passes a contiguous variadic word stream and context
`0x200001a0` to formatter `0x08009210`, and supplies callback
`0x0800a381`. The callback body at `0x0800a380..0x0800a392` sends the low
character byte through the same UART writer used by CASE transport and
returns the original character. These are the complete bounded wrapper and
callback bodies; formatter and UART writer remain lower contracts.

`log_wrapper_provider.c` source-defines both. Its use of ARM `va_list`
representation is explicit and guarded by a size assertion; it is not a
portable host-C ABI claim. `verify.py` executes stock and compiled C and
intercepts only the formatter or UART lower call. It compares five argument
words spanning R1-R3 and caller stack, format text, context and callback,
formatter return, UART handle/byte/length/timeout, callback return and
PRIMASK. Both isolated `-Og` and archive `-Os` objects pass **27 cases**:
12 wrapper cases and 15 callback cases. Receipts are `results.json` and
`archive_results.json`. After the source declarations were aligned, the
archive-compiled send and hex dump comparators were rerun and remain PASS
at 28 and 42 cases respectively.

The deterministic archive and whole-archive relocatable link pass with
**31 objects, 55 provided symbols, and 9 unresolved imports**. Archive
SHA-256: `0f9b4211dfed267113172f772df11269ee2ad976735ea4d12e0a36e7d72a5f66`.
The original direct 12-name tally remains **5 complete, 7 open**. Two
source-defined lower `case_send` dependencies are now complete: hex dump
and logger wrapper; two lower contracts remain, the timed UART writer and
formatter. Replacing the logger wrapper import with formatter leaves the
unresolved count at nine. These are symbol counts, not equal-sized tasks or
a time estimate. Full formatting, UART peripheral state, CASE link/startup
and hardware output remain unverified.
