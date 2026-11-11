# R1 polling and registered hook closure

The generated Goodix demo-user unit now applies the caller's existing interrupt-mode condition to `hal_gh3x2x_int_init` itself. The recovered R1 configuration uses polling. Its interrupt initializer and its only caller are therefore absent together, removing the unused `gh3026_int_pin_init` import without inventing a board callback or a no-op interrupt initializer. Preprocessor checks confirm normal and mixed modes retain both definition and call.

The registered raw-data hook at `0x6a4fe` is a single return through LR. The public template instead called `Gh3x2xFifoMonitorPro`; its generated body now comes from the empty C implementation in `r1/src/application/goodix/native_empty_hooks.h`. The pinned vendor source remains unchanged. This corrects an observable extra sensor-processing action rather than changing the global FIFO-monitor configuration.

An executed native registration fragment identifies four empty hooks: sampling start `0x6a59c`, sampling stop `0x6a59e`, raw data `0x6a4fe`, and configuration start `0x6a4b0`. The other three template bodies already matched. Across 768 paired native/C cases, each body executes exactly one two-byte return, accesses no data, and preserves all registers, flags and interrupt masks. A raw-buffer-write variant is rejected.

Configuration stop at `0x6a4b2` is **not** empty: stock calls the trigger helper, slot-time update, three sensor-enable getters and the algorithm-sensor-enable provider. An initial mistaken no-op assumption failed the native fixture and was reverted. The final audit proves this function unchanged. No configuration-stop entry or replacement was admitted.

All 576 R1 units compile; both relocatable compositions succeed without failures or duplicate strong symbols. Application imports fall from 166 to 165 and bootloader imports remain 34. All 574 unrelated objects are unchanged. In the two affected units, only the raw-data body changes and the unused interrupt initializer disappears; the other 34 functions remain unchanged. `make sources-check` and `git diff --check` pass.

Official qualification compiles the generated hook unit and selects the four two-byte C bodies. Its unmodified selected unit is appended to the canonical source plan. The full hybrid matches locked application SHA-256 `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`: **3,953 source-built bytes**, 642,207 fallback bytes and 248 resource bytes. The eight-byte increase is exact scoped source replacement; full source completeness remains false.

REA could not return a procedure at the unrecognized `0x6a4b0` entry. That limitation is retained; no REA procedure coverage is claimed. The locked raw bytes, explicit Thumb disassembly, executed registration fragment and native/C execution fixtures provide the bounded proof. No G2 workflow gate advances, and physical sensor/interrupt operation and a complete source-only image remain unverified.

[Machine-readable evidence](goodix-polling-hook-closure-review.json) records source hashes, registration arguments, native disassembly, compiler receipts, guard checks, rejected variants, audits, qualification and hybrid output. Probes remain under ignored `build/goal-r1-goodix-polling-hook-closure/`.
