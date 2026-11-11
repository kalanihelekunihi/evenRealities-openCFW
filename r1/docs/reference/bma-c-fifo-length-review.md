# Bosch FIFO length in C

`r1_bma4_get_fifo_length` in `native_bma_fifo.c` now uses ordinary C instead
of naked assembly. Stock entry `0x54440` initializes a four-byte scratch
word to zero, checks the device before the output pointer, then reads two
bytes from register `0x24`. On success it masks the high byte with `0x3f`
and stores the resulting halfword to the caller. On transport failure it
propagates the complete status without writing the output. Invalid inputs
return `0xffffffff`. REA/Ghidra independently confirms that control flow.

The C scratch array preserves the initialized four-byte extent. Zero-fill
therefore also matches stock when a successful callback writes only one
byte or leaves both bytes untouched. Output writes occur only after a
successful read and retain their two-byte width.

Stock/source comparison passes 1,536 scenarios: all 256 high-byte values
with all four partial-fill patterns, plus randomized low/high bytes,
full-width transport statuses, checker failures, null outputs, interrupt
masks and read callbacks that mutate the output before returning. Probes
compare ordered callback/output traces, scratch initialization, output
guards, return values, callee-saved registers, stack restoration and masks.
The checker and transport are mocked and clobber caller-saved registers.

The C body is 66 bytes versus the stock 62-byte instruction body. Callback
frames differ: stock uses SP-16 and C SP-24, both eight-byte aligned. The
other two FIFO functions retain their previous instruction bodies.
All 562 R1 units compile without failures or duplicate strong symbols in
`build/sources-goal-r1-bma-fifo-length/report.json`; both normal relocatable
compositions retain their import sets, 227 application and 34 bootloader.

Private spills, complete fault state, timing, physical sensor operation,
final linking and whole-image byte identity remain open. No source-plan
selection or G2 workflow gate changed. [Machine-readable evidence](bma-c-fifo-length-review.json)
binds source/build/native hashes, REA observations and ignored probes under
`build/goal-r1-bma-fifo-length/`.
