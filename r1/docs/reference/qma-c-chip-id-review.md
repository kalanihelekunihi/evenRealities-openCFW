# QMA chip-ID logic in C with native frame capture

`r1_qma6100_chip_id` now delegates its read-and-return logic to the C
helper `r1_qma_chip_id_byte`. A ten-byte assembly bridge remains to push
incoming R3/LR, pass the saved word's address to C and pop R3/PC. Stock
entry `0x86e34` uses that saved R3 word as its one-byte output buffer,
ignores read-retry status and returns the final low byte. REA/Ghidra
independently identifies this incoming-register seed.

The bridge preserves entry SP-8 as the buffer address. The C body calls
the actual C retry loop for register zero, length one, then reloads the
byte through a volatile view. A zero-initialized C local would change
failed/non-writing-read behavior; an indeterminate C local would not
establish the native register-derived data. The capture bridge avoids
both substitutions. It restores the modified saved word into R3, as
stock does, including the returned byte and original upper 24 bits.

Stock/source comparison passes 2,816 scenarios. Coverage includes all
256 incoming low-byte seeds, full-width R3 words, every combination of
five-attempt success and write masks, non-writing success/failure,
last-failure delays, address changes, delay-driven data changes and
interrupt masks. The actual C retry implementation executes; only bus
and delay wrappers are modeled.

Probes compare the initial word push, final byte/word reads, exact native
buffer address, live runtime reads, bus/delay sequence, R0 and restored
R3, callee-saved registers, stack restoration and masks. An independent
oracle checks retry counts and the final byte. Mocked callbacks clobber
caller-saved registers/flags and require eight-byte alignment. Callback
frame depths differ because the C helper adds its own frame below the
captured word.

Stock uses 18 bytes; the new entry uses a ten-byte assembly bridge and
an 18-byte C body. All other transport function instruction bodies remain
unchanged. All 562 R1 units compile without failures or duplicate strong
symbols in `build/sources-goal-r1-qma-chip-id/report.json`; imports remain
227 application and 34 bootloader.

This is a partial C extraction, not an assembly-free entry. Physical ID
reads, timing, complete fault state, final linking and byte identity
remain unverified. No source-plan selection or G2 workflow gate changed.
[Machine-readable evidence](qma-c-chip-id-review.json) binds source/build/native
hashes, REA observations and ignored probes under `build/goal-r1-qma-chip-id/`.
