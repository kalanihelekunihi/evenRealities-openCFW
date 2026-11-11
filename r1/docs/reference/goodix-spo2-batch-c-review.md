# SpO2 batch accumulation in C

The [cached-result encoder](goodix-spo2-result-encode-c-review.md) now executes in C for partial/error windows. Eleven later core stages remain unfinished.

`native_spo2_batch.c` implements the490-byte batch-window stage. It preserves window resets, four selected float lanes per record, wrapped metadata sums, signed averaging, compact-summary updates and incomplete-window status3. No state or imports are added.

An ordinary noinline C addition helper keeps the accumulator as the first NaN operand under the tested profile. Defined unsigned arithmetic implements integer division without C zero-divisor or signed-overflow undefined behavior, matching default nontrapping SDIV/UDIV results.

**3,766 native/C invocation comparisons pass across2,422 scenario pairs**:

- 2,020 direct scenarios include72 two-window lifecycles, totaling3,364 batch calls. Finite rational oracles, explicit NaN-payload pairs, all rounding/FZ/DN combinations, INT_MIN/-1 wrap, zero divisors, aliased buffers and four matching faults are checked.
- 402 frame cases execute actual frame/core/assembler/decoder/batch/polynomial code and real clear helpers. Twelve later stages and allocator/free ports remain modeled; some frame cases gate before batch.
- Both fixtures cover all490 new native instruction bytes. Lifecycle boundary hashes, final public RAM bytes, full active FPSCR, saved registers, stack and masks agree. Twelve compiled defects are rejected; source cannot execute stock.

All **904 R1 units** compile and compose without failures or duplicate strong symbols. The tested object equals the normal object;893 prior nongenerated source/object pairs and source-plan/cache files are unchanged. Application imports fall90 to89; bootloader imports stay22.

Enabled integer-division trapping, physical concurrency/interrupts, cold FPU, arbitrary private aliases and final startup/placement remain unverified. Compiler changes require rechecking NaN operand order. This is relocatable composition, not a complete sensor engine or bootable firmware.

[Machine-readable evidence](goodix-spo2-batch-c-review.json) records contracts, profiles and hashes.
