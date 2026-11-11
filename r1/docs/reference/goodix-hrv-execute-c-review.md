# HRV hardware-frame adapter in C

The [HR frame-execution review](goodix-hr-execute-c-review.md) adds the C HR adapter and disabled report. Dispatcher replays now execute real ADT, HR and HRV adapters, including the HR record consumed by HRV; calculation cores and HR diagnostics remain explicit unfinished providers.

`native_hrv_execute.c` implements the native HRV frame adapter and disabled result hook: **378 instruction bytes across two entries**. It reuses the canonical frame-table owner and the last-HR cache at `0x20007c2c`, retaining the existing cache symbol name. No persistent state, assembly, executable blob or calculation stub is added to firmware.

The adapter builds the exact 56-byte input packet and local buffers, including signed accelerometer samples, four PPG channels, raw sleep state, gain nibbles, summed driver bytes and the cached HR byte. Invalid last-gain value 255 remains unchanged. Only core status `0x10000006` publishes results; status zero leaves the current result untouched and other full-width statuses return -5. The disabled report hook has no effects in stock and becomes a C void function.

Validation passes **4,620 stock-versus-C pairs**:

- 1,240 direct cases cover both native entries, independent packet/buffer oracles, typed pointer normalization, AGC aliases, callback pointer changes and 22 matching selected faults.
- 3,380 dispatcher cases execute actual ADT and HRV adapters with real native/C helper code. The HRV calculation core, remaining three engine executors and logging effects are modeled. Null HRV frames exercise initialized, inactive and sleep-flag gate order.
- Thirteen compiled defects are rejected. Full nonstack RAM, boundary snapshots, status, saved registers, stack and masks agree; source execution cannot enter stock code.

All **896 R1 units** compile and compose without failures or duplicate strong symbols. The tested object equals the normal-build object, and all 885 prior nongenerated source/object pairs are unchanged. No writable state is added. Source-plan/cache layout remains unchanged.

`goodix_hrv_calc` at `0x6d51c` is still unfinished. It replaces the adapter's aggregate import, so application/boot imports remain 77/22. HR, SpO2 and soft-ADT executors also remain open. This is relocatable composition, not a bootable firmware image or physical sensor/concurrency proof.

[Machine-readable evidence](goodix-hrv-execute-c-review.json) records exact source/stock/object hashes, contracts, fixtures and limitations.
