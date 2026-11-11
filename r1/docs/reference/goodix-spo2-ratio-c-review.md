# Native SpO2 ratio and peak histories in C

`native_spo2_peak_history.c` implements the ratio parent and all nine peak-grid, ranking, selection and history dependencies. All **1,304 native instruction bytes** execute in the fixture. The unit adds no assembly or writable state. A shared typed header corrects the caller declaration while leaving its object unchanged.

The grid preserves native FP carry/zero predicates, including unordered comparisons satisfying unsigned HI. It also retains the right multiplication after the first comparison; a signaling-NaN control catches the lost invalid-operation flag if it is skipped. Plateau propagation, first-maximum row selection, last-capacity index retention and live aliases are verified.

History insertion uses the single old last-entry threshold for the entire call. Its cursor is adjusted for shifts and stored only when cutoff scanning finds a qualifying entry. The all-old-entry case deliberately retains the pre-scan cursor, matching stock. These raw native contracts differ from the existing portable bool/scratch-buffer helpers.

**9,334 routine scenario pairs pass**, including 3,464 independent-oracle cases and thirteen positive defect controls. Thirteen compiled defects are rejected. Independent models cover finite grid/plateau constraints, column sentinels, signed maxima, deque histories, alternate first labels and 256 complete ratio graphs.

Real descriptor/aggregate constructors and rolling queues also pass **1,014 ratio-window pairs and 33,150 float-push pairs** across candidate and final normal-product streams. Tests use the locked configuration, cover dropout/recovery and saturate the native 20-entry histories. The candidate streams cover all 32 tested FP control/status settings; the final normal-product check uses four representative seeds. Source-only probes map no stock code/data and execute the actual C heap/memory helpers without algorithm models.

Push totals count paired invocations; full RAM/FPSCR comparisons occur at constructor and ratio-window boundaries. Saved registers and SP are checked after every call.

All **916 R1 units** compile and compose without failures or duplicate strong symbols. Application imports fall **86 to 85**; boot imports remain **22**. The 904 unrelated source/object pairs, caller object, source-plan and cache layout are unchanged. Normal/probe executable sections, relocations and symbol contracts match; source-file name metadata differs.

Malformed inputs, exhaustion/fatal paths, traps, cold FPU, physical IRQ/concurrency/timing/stack/throughput, optical ADC/batch conversion, final layout/startup and boot remain unverified. Eight later SpO2 stages remain open. Relocatable composition is not bootable firmware. No paid compiler or byte identity is required.

[Machine-readable evidence](goodix-spo2-ratio-c-review.json) records exact contracts, cases and hashes.
