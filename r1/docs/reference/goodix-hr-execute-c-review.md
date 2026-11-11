# HR hardware-frame adapter in C

`native_hr_execute.c` implements the native HR frame adapter and disabled report: **344 executed native instruction bytes**. It reuses the existing scenario and channel-map owners. No persistent state, assembly, executable blob or calculation/diagnostic stub is added.

The adapter fills twelve PPG slots through the native banked channel map, retaining disabled value 255, zero gain/driver fields and signed accelerometer samples. It calls calculation and then diagnostics on every valid frame, including calculation errors. Publication occurs only for zero status and output flag exactly one. It preserves wrapped SNR scaling, six result fields, mask/popcount and the separate HR record consumed by HRV.

Validation passes **4,995 stock-versus-C pairs**:

- 1,612 direct cases cover input/padding oracles, typed local pointers, mapping gaps and aliases, boundary fields, diagnostic mutations and 34 matching selected faults.
- 3,383 dispatcher cases execute actual ADT, HR and HRV adapters with real native/C helper code. HR output records feed the HRV cache/input path. Calculation cores, diagnostics, logging and the remaining two executors are modeled.
- Fourteen compiled defects are rejected. All 342 HR adapter bytes and the two-byte disabled report execute. The adapter span includes an unreachable two-byte branch excluded from the admitted ranges.

All **897 R1 units** compile and compose without failures or duplicate strong symbols. The tested object equals the normal-build object; all 886 prior nongenerated source/object pairs are unchanged. No writable state is added, and source-plan/cache files remain unchanged.

The unfinished dependencies are `goodix_hba_calc` and `goodix_hba_essential_info_print`. They replace one aggregate import, increasing application imports from 77 to 78; boot imports remain 22. This is relocatable composition, not a completed HR engine, final executable or physical hardware proof.

[Machine-readable evidence](goodix-hr-execute-c-review.json) records exact ranges, source/object hashes, contracts, fixtures and limitations.
