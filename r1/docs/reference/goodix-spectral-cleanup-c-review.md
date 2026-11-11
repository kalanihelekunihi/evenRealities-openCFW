# Native spectral cleanup and window/copy in C

`native_spectral_cleanup.c` implements sign-run cleanup and scale/window copy. The latter includes its26-byte shared tail, giving308 unique instruction bytes in total. Live input/output/mask/factor aliases, masked zero/NaN retention and VCMPE/FPSCR semantics are preserved. The125-sample window is500 bytes of explicit coefficient data. No writable owner or inline assembly is added.

**21,472 native/C scenario pairs pass**, including1,344 two-call cleanup-to-window chains and3,040 independent finite oracle scenarios. The chains make the top-level entry-call count22,816. Oracles cover untouched outputs and long signed runs, plus rationally rounded window products. All308 instruction bytes execute, and all500 coefficient bytes match stock.

Actual C memory helpers run; full public RAM, active FPSCR, saved registers, stack and masks match. All FP settings and selected live aliases are checked. Ten compiled defects are rejected; the altered coefficient is caught by the table-data oracle, while the remaining controls expose runtime behavior/status errors.

All909 R1 units compile and compose without failures or duplicate strong symbols. The tested object equals normal build;898 prior nongenerated source/object pairs are unchanged. Imports stay87 application/22 boot. Source-plan and cache-layout files remain unchanged.

Mode1 lengths0..125 cover the observed sensor caller. Broader table/adjacent-RO layouts, arbitrary faults/private aliases, cold FPU, interrupts/concurrency, throughput/stack budget, final startup/layout and physical sensor/boot behavior remain unverified. Quantile/mask/FFT processing and the spectral parent remain unfinished. Relocatable composition is not bootable firmware.

[Machine-readable evidence](goodix-spectral-cleanup-c-review.json) records contracts, profiles and hashes.
