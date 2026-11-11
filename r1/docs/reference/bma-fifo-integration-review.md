# Combined Bosch FIFO path execution

The current normal R1 objects pass 904 combined stock/source scenarios
through six real functions: the C interface initializer, device checker,
outer FIFO wrapper, FIFO-length query, bounded byte reader and default
read adapter. This supplements the individual conversion reviews with
execution of their actual call chain. Firmware sources are unchanged.

The probe first executes each initializer against a seeded context and
compares its eight ordered writes, normalizing callback pointer values
by role. It then runs the outer FIFO wrapper through the actual checker,
length routine, bounded reader and registered default read callback.
Only power control, delay, the two-byte register-length response, final
motion-bus request and logging are mocked. Mocked calls clobber caller-
saved registers and require eight-byte stack alignment.

Scenarios cover zero and wrapping sample requests, FIFO lengths through
the 14-bit maximum, high length bits, all four partial-fill patterns,
SPI/I2C register selection, missing read/write/delay callbacks, changing
log-mode results, full-width bus success/failure values, random address
words and interrupt masks. Stock/source results match for ordered public
context reads/writes and calls, log strings/statuses, returned sample
counts, all context bytes, output data and guards. Expected bus reachability
and power restore are also checked independently of trace equality.

The actual default adapter loads only the low address byte and maps any
nonzero bus result to success. The bus model writes a deterministic byte
pattern even on failure, verifying that the outer routines preserve
partial output rather than undoing it. Callee-saved registers, restored
stack and interrupt masks match; private frame depths differ and are
recorded separately.

The controlled link places the context at `0x2001e4e8` and address word
at `0x200076c0`. Those placements are probe inputs, not evidence of final
firmware layout. Real sensor operation, direct-read scratch behavior,
bus timing, complete fault state, full linking and byte identity remain
unverified. No source-plan selection or G2 workflow gate changed.

The bound normal report remains
`build/sources-goal-r1-bma-fifo-bytes-verified/report.json`: all 562 units
compiled, no failures or duplicate strong symbols, 227 application and
34 bootloader imports. [Machine-readable evidence](bma-fifo-integration-review.json)
binds that report, all three input units and objects, existing REA results,
and ignored probes under `build/goal-r1-bma-fifo-integration/`.
