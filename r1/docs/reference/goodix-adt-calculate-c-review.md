# ADT wear execution and filter in C

`native_adt_calculate.c` implements the native ADT wear executor, moving filter and soft-event reporter: **588 stock instruction bytes across three entries**. It shares the existing three ADT flags with init/deinit and defines the native four-byte cached sample and six-word history. No assembly, executable blob, trap or placeholder calculation is added.

The filter preserves the native delay: append the current sample, then average only the preceding samples, wrapping the sum at 32 bits. The executor keeps strict on/off thresholds, signed wrapped differences, initial-state handling, live state/result reloads after logging and existing update bytes. The reporter clears the opposite software event before setting the new event.

Validation passes **10,325 stock-versus-C pairs**:

- 6,948 direct cases cover all 588 native instruction bytes, threshold equality and signed extremes, all filter count bytes, bypasses, data aliases, retained updates and logger/helper mutations. An independent filter oracle checks wrapped sums and exclusion of the newest sample.
- 3,377 dispatcher cases use the actual ADT/filter/reporter and native/C sleep, popcount, memory and software-event helpers. They cover the 190-byte dispatcher and 440/94/46 ADT bytes; some cases intentionally gate or fault before ADT. Logging and the other four engines remain modeled.
- Thirteen compiled defects are rejected. Full nonstack RAM, boundary snapshots, callback arguments/order, status, saved registers, stack and interrupt masks agree. Source execution cannot enter stock code.

All **895 R1 units** compile and compose without failures or duplicate strong symbols. The tested ADT object equals the normal-build object; all 884 prior nongenerated source/object pairs are unchanged. Application imports fall from 78 to 77; boot imports remain 22. Source-plan/cache layout is unchanged.

This is relocatable composition, not a bootable firmware image. The 28-byte cache/history owners correspond to native RAM, but final placement/startup and physical sampling, interrupts and concurrency remain unverified. HR, HRV, SpO2 and soft ADT executors are still unfinished.

[Machine-readable evidence](goodix-adt-calculate-c-review.json) records source/stock/object hashes, exact contracts, fixtures and limitations.
