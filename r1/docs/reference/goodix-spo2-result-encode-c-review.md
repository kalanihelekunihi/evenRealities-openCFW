# SpO2 cached result encoder in C

`native_spo2_result_encode.c` replaces the252-byte native encoder used for partial/error windows. It preserves owner reloads, signed metadata, float scaling, native encoded rounding and the cleared update flag. The historical provider name `r1_goodix_spo2_failure` covers cached results as well as failures. No new state or inline assembly is introduced.

**2,541 native/C case pairs pass:**2,139 direct cases and402 integrated frame cases. Direct tests exercise all252 native instruction bytes,323 matching selected faults, overlapping state/output/owner buffers, all FP modes, exceptional values and independent finite rational oracles. Four compiled defects are rejected. Public RAM, FPSCR, saved registers, stack and masks match.

All905 R1 units compile and compose without failures or duplicate strong symbols. The tested object equals the normal object;894 prior nongenerated source/object pairs remain unchanged. Application imports fall89 to88; bootloader imports stay22.

Eleven later processing stages and allocator/free ports remain modeled in frame tests. Arbitrary fault atomicity, interrupts/concurrency, cold FPU, physical sampling and final startup/layout remain unverified. This is relocatable composition, not bootable firmware.

[Machine-readable evidence](goodix-spo2-result-encode-c-review.json) records contracts and hashes.
