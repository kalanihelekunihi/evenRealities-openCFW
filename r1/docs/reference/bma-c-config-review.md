# Bosch configuration sequence in C

`r1_bma456w_configure_boundary` now uses ordinary C, leaving
`native_bma_initialize.c` free of inline assembly. Stock entry `0x53c6c`
and REA/Ghidra establish this nine-step sequence:

1. Initialize the interface context.
2. Initialize the Bosch device.
3. Set accelerometer config bytes `{ODR, 0, 0, 2}`.
4. Enable the accelerometer with value 1.
5. Disable power saving with value 0.
6. Clear FIFO config with mask `0x7f`, value 0.
7. Enable FIFO accelerometer data with mask `0x40`, value 1.
8. Disable the FIFO header with mask `0x10`, value 0.
9. Enable power saving with value 1.

Rates 50, 100 and 200 select ODR codes 7, 8 and 9; all other full-width
rate values select code 6, including rate 25. The pinned four-byte config
layout is asserted. Each step receives the same context. A failed step
logs its full status with the existing strings and returns zero, without
later steps or added cleanup. All nine successes return one.

A local C logging helper preserves separate short-circuiting mode queries,
the duplicate ring-string arguments and headers `0x04400000`/`0x001c0001`.
It tests bit zero first, otherwise bit two in another result, then bit one
in a subsequent result for SDK logging.

Stock/source comparison passes 5,378 scenarios: all 512 three-bit mode
triples at every failure stage, 258 successful rate values, and randomized
full-width rates, statuses and changing mode results. Callback mutations
to context and config input test propagation without added resets.
Probes independently assert the exact stage prefix, arguments, config
bytes and expected log sequence, then compare stock/source traces,
returns, context/guards, callee-saved registers, restored stack and masks.
All step/logging calls are mocked, clobber caller-saved registers and
require eight-byte stack alignment.

The C wrapper is 386 bytes with a 66-byte logging helper, compared with
the stock 604-byte instruction body. Private frame depths differ. The
two initializer instruction bodies retain their previous compiled bytes.
All 562 R1 units compile without failures or duplicate strong symbols in
`build/sources-goal-r1-bma-config/report.json`; normal import sets remain
227 application and 34 bootloader.

This validates the sequencing boundary. Complete sensor configuration
execution, physical bus operation, timing, complete fault state, final
linking and byte identity remain unverified. No source-plan selection or
G2 workflow gate changed. [Machine-readable evidence](bma-c-config-review.json)
binds source/build/native hashes, REA results and ignored probes under
`build/goal-r1-bma-config/`.
