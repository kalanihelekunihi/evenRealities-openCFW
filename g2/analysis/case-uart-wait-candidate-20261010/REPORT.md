# CASE UART flag wait lower provider

Fixed CASE `g2-2.2.6.10/firmware_box.bin` SHA-256 is
`36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374`.
Original `case_wait_condition` occupies `0x08008ec4..0x08008f96`. It polls
a UART peripheral ISR flag until its expected state changes. A finite timeout
uses unsigned HAL tick subtraction; timeout zero expires after the first
tick check. On expiry it masks/restores PRIMASK around CR1/CR3 clears and
resets UART states/lock. A guarded error branch also writes ICR and resets
the error state. `uart_wait_provider.c` source-defines the bounded body with
explicit ARM `mrs/msr primask` instructions. The HAL tick getter is already
source-defined separately.

`verify.py` runs stock and compiled C with coherent synthetic UART handle,
peripheral register and scripted tick/ISR evolution. Both isolated `-Og`
and archive `-Os` objects pass **5,040** cases covering immediate success,
flag polarity, finite and infinite timeout where return is reachable, tick
wrap subtraction, error cleanup, CR1/CR3 state, initial PRIMASK 0/1, and
return values. It compares all UART/peripheral bytes and PRIMASK. Receipts:
`results.json`, `archive_results.json`. Infinite wait with unchanged ISR
is excluded from returning comparisons; actual peripheral timing and HAL
interrupt effects remain outside synthetic state.

With the archive source writer, source tick getter and source wait provider
linked together, `verify.py --archive-object --compose-wait` passes **16**
stock/source end-to-end writer cases with ready ISR flags and no child hooks.
Receipt: `../case-uart-write-candidate-20261010/composed_wait_results.json`.
This tests the valid ready path, not real UART delivery.

The deterministic archive and whole-archive relocatable link pass with
**34 objects, 58 provided symbols, and 8 unresolved imports**. Archive
SHA-256: `a2e155ae2ee9a60dc9e924837131c648571dec6c5cbbe44c832b191f5c67d8b5`.
The original direct 12-name tally remains **5 complete, 7 open**. Of the
lower contracts exposed along the send/logger/UART chain, only formatter
`case_vformat` remains unresolved. Seven direct plus one lower symbol is
an explicit work count, not an equal-effort or time estimate. CASE full
link/startup, peripheral hardware and logger output remain open.
