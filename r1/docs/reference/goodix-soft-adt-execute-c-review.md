# Soft-ADT frame execution and event reporting in C

`native_soft_adt_execute.c` implements the sensor adapter and green/IR reporters: **578 native instruction bytes across three entries**. It shares the existing capacitor flag, selector and timeout counter. Five owned bytes represent the native report state and timeout-seconds setting.

The adapter preserves sparse PPG/gain/driver packing, capacitor mode exactly equal to one, nested input arrays and zero enable bytes. Timeout processing occurs even after calculation errors, uses wrapped 32-bit multiplication/increment, and distinguishes the IR function ID. Output gates and live pointer/selector reloads follow stock. Both event reporters share de-duplication state, ignore the result update byte, and store their new state after clear/set event calls.

Validation passes **7,270 stock-versus-C pairs**:

- 3,884 direct cases cover typed nested input pointers, independent packing/timeout oracles, wraparound, error timing, live mutations and 87 matching selected faults.
- 3,386 dispatcher cases execute actual ADT, HR, HRV and soft-ADT adapters and native/C helpers. Calculation cores, diagnostics, logging and the remaining SpO2 executor are modeled.
- All 578 native bytes execute in both fixtures. Seventeen compiled defects are rejected. Full nonstack RAM, snapshots, status, saved registers, stack and masks agree; source cannot execute stock.

The stock RW initializer was replayed on two poisoned regions and checked against an independent decoder. It matches the C object defaults: report state zero and timeout limit 30 seconds. Whole-region guards remain intact.

All **898 R1 units** compile and compose without failures or duplicate strong symbols. The tested object equals the normal object; all 887 prior nongenerated source/object pairs are unchanged. Source-plan/cache files remain unchanged. The aggregate soft-ADT import is replaced by unfinished `goodix_nadt_calc`, leaving imports at 78 application and 22 bootloader.

This is relocatable composition, not a completed NADT computation engine or bootable firmware image. Final placement/startup and physical hardware/concurrency behavior remain unverified.

[Machine-readable evidence](goodix-soft-adt-execute-c-review.json) records exact source/stock/object hashes, contracts, fixtures and limitations.
