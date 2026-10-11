# CASE timed UART writer and tick getter

Authenticated CASE `g2-2.2.6.10/firmware_box.bin` SHA-256 is
`36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`.
Original `case_write_controller_blocking` is `0x080066ac..0x08006776`.
The bounded body validates UART state, data pointer, length and alignment;
sets busy/error/transfer counts; obtains a tick; waits for TX-ready per item;
writes 8-bit or 9-bit data to the peripheral register; waits for completion;
and restores ready state on success. Failure branches return HAL status 1,
2 or 3 as observed. `uart_write_provider.c` source-defines this body, with
`case_tick_word2` and `case_wait_condition` as explicit lower contracts.

`verify.py` executes original and compiled C with synthetic coherent UART
handle, peripheral register, and source buffer. It compares return,
complete UART/peripheral/buffer windows, PRIMASK, and every tick/wait call
argument and branch result. Both isolated `-Og` and archive `-Os` objects
pass **720 cases**: ready/busy states, lengths 0/1/2/3/5, 8-bit/9-bit and
parity modes, aligned/odd/null pointers, and wait failure at multiple calls.
The wait helper is intercepted, so timeout side effects and real peripheral
timing are outside this proof. Receipts are `results.json` and
`archive_results.json`.

Original `case_tick_word2` at `0x08004eac..0x08004eb2` reads a distinct
HAL tick word at RAM `0x20000120`. `tick_word_provider.c` defines it from
source. `verify_tick_word.py` matches seven stock/source values in isolated
and archive builds. `verify.py --archive-object --compose-tick` also passes
**720** writer cases with stock and source tick getters actually executing;
only the wait helper is intercepted. Receipt: `composed_results.json`.

The deterministic archive rebuild and whole-archive relocatable link pass
with **33 objects, 57 provided symbols, and 9 unresolved imports**. Archive
SHA-256: `980f3c36d32396421b46b2f02d9e0906d11db48f8fea890bc7ca5405a51dcd1d`.
The direct original 12-name tally stays **5 complete, 7 open**. Lower
`case_send` dependency work now has UART writer, HAL tick getter, hex dump,
and logger wrapper source-defined. Two lower imports remain: formatter
`case_vformat` and UART flag wait `case_wait_condition`. The total nine
unresolved names are seven direct plus two lower contracts. These counts
do not predict time or cover CASE startup, full link, hardware UART output,
or scheduling behavior.
