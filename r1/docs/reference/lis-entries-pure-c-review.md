# Ordinary C LIS2DW12 register entries

`r1/src/application/runtime/native_lis_call_frames.c` replaces all **22 naked entry bridges** with ordinary C functions: sixteen byte setters, reset/FIFO-level getters, data-rate/filter-path setters, native power mode and register-17 enable. ST public functions now use the pinned header's typed signatures. Existing field/update and multi-register bodies remain canonical; this unit contains no assembly or fixed-register declarations.

Private scratch bytes start at zero. Successful one-byte reads retain the stock update/extraction behavior, transport status, live context callback/handle reloads and write sequencing. Setters still stop on their established read/write error paths. The native power helper still writes after its second-read error and adds the two final statuses modulo 2^32. Getter outputs and R0 status remain public; extracted R1, saved R3 and other private-frame residues are excluded. Provider writes beyond the requested byte are outside the API contract.

REA bytes match the official artifact for all 22 entries. Direct execution passes **190,272 stock/C comparisons** across all 256 register bytes, field values and overflow encodings, read/write errors, second-transfer errors and live context changes. Actual C field kernels, read/write adapters, ST multi-register bodies and native power logic execute. Tests compare transport calls and bytes, return words, context and unaligned byte outputs, plus caller stack, callee-saved integer/FP registers, SP, interrupt masks and destination guards. Modeled callbacks overwrite caller-saved registers.

Another **528 unwritten-read cases** check the initialized fallback against zero-seeded native scratch while the C caller carries a different seed. This is a deliberate C policy, not equivalence to arbitrary old stack values.

The existing configuration graph passes **378 additional stock/C comparisons** with the updated register entries. It covers rates, reset completion/timeouts, filled reads carrying errors, write errors and scratch seeds. The real configuration body and register helpers execute; identity, FIFO output, bus callbacks, delays and logs are modeled. Only helpers reached by configuration execute in this fixture; the direct fixture covers all 22 entries. The separate configuration call adapter and auxiliary/FIFO assembly remain unchanged.

Five compiled defects are rejected using a reduced test matrix: wrong register, wrong extraction shift, writing after the initial read error, wrong byte fallback and wrong two-register fallback. Physical sensor/bus behavior, electrical reset and timing, faults/concurrency, incomplete/overrunning provider buffers and final application linking/startup remain unverified.

The open-toolchain report `build/sources-goal-r1-lis-entries-pure-c/report.json` compiles all **855 units** and completes both relocatable compositions. All **844 other nongenerated objects** remain unchanged. The normal register-entry object exactly equals both executed probe objects. Imports remain **61 application / 22 bootloader**. R1 manifest validation passes and source-plan selections remain unchanged. Byte identity is not claimed.

[Machine receipt](lis-entries-pure-c-review.json) binds sources, REA and ignored probe evidence under `build/goal-r1-lis-entries-pure-c/`.
