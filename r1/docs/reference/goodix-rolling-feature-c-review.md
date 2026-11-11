# Native sensor rolling features in C

`native_rolling_feature.c` recovers the native float decimation window, reverse weighted accumulation, two25-tap filters and shared optical/NADT rolling-feature pair. Four native providers cover542 unique instruction bytes; the pair includes a70-byte shared tail at0x2f2ac. Separate portable model APIs remain available. No writable owner or inline assembly is added.

**27,208 native/C invocation comparisons pass:**22,464 direct cases,384 independent finite Fraction weighted-sum cases,3,840 calls in24 manual-record lifecycles and520 calls in two sessions created by actual C/native constructors. Constructor scenarios check the native5/25 averaging periods and six allocation sizes; allocation is modeled. Nine compiled defects are rejected. All542 instruction bytes execute. The two filter arrays match all200 stock coefficient bytes.

Actual C memory helpers execute; algorithm and math stages are not mocked. Full public RAM, active FPSCR, saved registers, stack and masks match across window fill/shift, phase/cursor wrap, selected aliases, signed/zero periods, special floats and repeated sessions. Default nontrapping division is part of the tested contract.

All906 R1 units compile and compose without failures or duplicate strong symbols. The tested object equals the normal object;895 prior nongenerated source/object pairs are unchanged. Imports remain88 application/22 bootloader. Source-plan and cache-layout files remain unchanged.

The higher-level optical/motion parent remains unfinished; these are verified dependencies, not a recovered whole sensor engine. Arbitrary malformed capacities, faults/private aliases, real allocator lifecycle, interrupts/concurrency, timing, cold FPU, final startup/layout and physical sampling remain unverified. Weighted counts beyond65535 retain native16-bit wrapping and are not a supported terminating workload. Relocatable composition is not bootable firmware.

[Machine-readable evidence](goodix-rolling-feature-c-review.json) records contracts, profiles and hashes.
