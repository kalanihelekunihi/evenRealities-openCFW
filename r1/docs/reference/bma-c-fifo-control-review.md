# Bosch FIFO control wrapper in C

`r1_bma456w_fifo_read` in `native_bma_fifo.c` now uses C instead of naked
assembly. Stock entry `0x541a8` rejects null output or zero sample count
with `0xffffffff`. It disables power saving, delays 450 microseconds,
requests `(uint16_t)(samples * 6)` bytes, then restores power saving only
after a nonnegative read result. A successful restore returns bytes read
divided by six. REA/Ghidra independently recovers those branches.

The error paths retain stock behavior: disable or restore failure logs
the full status and returns zero; a negative read result logs that result
and returns `0xffffffff` without restoring power saving. No additional
cleanup, retries or bounds checks are introduced.

A local C helper preserves each failure route's strings, ring header
`0x04400000`, SDK header `0x001c0001`, duplicate ring-string arguments,
full error word and separate short-circuiting mode queries. It tests bit
zero on the first result, otherwise bit two on a second result, and bit
one on a subsequent result for SDK logging.

Stock/source comparison passes 2,168 scenarios. Coverage includes all
512 triples of three-bit log-mode values across the three failure routes,
request arithmetic boundaries and wrap, zero/positive/negative read
results, null output, changing full-width mode/error values and interrupt
mask combinations. Probes compare ordered call traces and arguments,
strings, returns, callee-saved registers, stack restoration and masks.
They independently assert whether restore is reached. Mocked calls
clobber caller-saved registers and require eight-byte stack alignment.

The C wrapper is 180 bytes with a 66-byte local logging helper, compared
with the stock 256-byte instruction body. Private frames differ. The
FIFO-length and bounded byte-transfer functions retain their previous
instruction bodies; the latter still contains assembly.

All 562 R1 units compile without failures or duplicate strong symbols in
`build/sources-goal-r1-bma-fifo-control/report.json`. Both normal relocatable
compositions retain their import sets: 227 application and 34 bootloader.
Power, delay, FIFO transfer and logging are mocked here. Physical sensor
operation, timing, complete fault state, final linking and byte identity
remain unverified. No source-plan selection or G2 workflow gate changed.

[Machine-readable evidence](bma-c-fifo-control-review.json) binds source,
manifest, build/native hashes, REA results and ignored probes under
`build/goal-r1-bma-fifo-control/`.
