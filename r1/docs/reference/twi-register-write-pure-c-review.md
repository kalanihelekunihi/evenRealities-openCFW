# TWI register writers use an explicit C buffer

Both register-write adapters in `native_hw_twi_register.c` now use ordinary C. The complete adapter unit has no fixed-register declarations, empty assembly or stack helpers. Writes allocate 81 bytes explicitly: one register byte and up to 80 payload bytes. Lengths above 80 still return nine before transmitting.

This intentionally repairs a stock defect. Stock's admitted length-80 copy places the final payload byte over the saved R4 low byte. It transmits the intended 81 bytes but returns a corrupted callee-saved register. The C buffer preserves the same payload and accepted length while preserving R4. Reproducing the corruption is not part of the functional C firmware target.

The [receipt](twi-register-write-pure-c-review.json) records 11,550 cases with modeled legacy TX and another 11,550 executing the actual stock/C legacy TX wrappers. Both suites compare payload bytes, transmitted lengths, no-stop=false, controller state, wait arguments and declared status. They cover zero through 80 bytes, rejected 81/full-width lengths, byte register narrowing, full-status seventeen, returning error-handler retries, low-byte wait results, mutable transmit buffers and ordinary/caller-owned input memory. Each suite observes 1,446 corrupted stock length-80 returns; the C implementation preserves all callee-saved registers in every case. Private-frame aliases and incidental scratch outputs are excluded.

Four controls reject valid-length-80 rejection, shifted payload bytes, a truncated status-seventeen check and the wrong primary wait. Primary/secondary waits remain 500/200. Full-width seventeen stops immediately; other nonzero TX results call the error provider and retry if it returns. Wait results remain narrowed to a byte.

REA raw-byte observations identify both stock entries. SDK TX, waits and the returning error handler remain modeled, including when the actual legacy wrapper executes. Physical bus operation, IRQ timing, arbitrary faults and concurrency are unverified. This is behavioral preservation with an explicit register-corruption fix, not byte identity.

The normal report is `build/sources-goal-r1-twi-register-write-pure-c/report.json`: 727 units compile without failures or duplicate strong symbols. Imports remain 178 application and 34 bootloader. Only the register-adapter object changed; 726 objects remain unchanged. Both read-adapter instruction sections are byte unchanged. Both manifests pass `make sources-check`.
