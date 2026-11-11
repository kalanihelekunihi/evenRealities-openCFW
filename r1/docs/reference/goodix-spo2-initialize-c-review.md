# R1 SpO2 context initialization in C

The [SpO2 frame execution review](goodix-spo2-execute-c-review.md) adds the C sensor adapter with bounded floating-point rounding validation and reuses the canonical channel map. All five sensor frame adapters now execute in dispatcher comparisons; `goodix_spo2_calc` remains unfinished.

The [session initialization review](goodix-spo2-session-c-review.md) implements the session and short-pair boundaries described below. The weights getter and model constructor remain unresolved.

`r1/src/application/goodix/native_spo2_initialize.c` implements the SpO2 constructor and twelve descriptor, allocation, queue, buffer and model-owner helpers. The [machine-readable receipt](goodix-spo2-initialize-c-review.json) pins REA bytes, sources, objects, fixtures and the final build.

All 881 units compile and compose without duplicate strong symbols. The build replaces `goodix_spo2_init` with four deeper initialization/resource dependencies, raising application imports from 63 to 66; bootloader imports remain 22. No new writable state is introduced. The canonical SpO2 context owner, existing allocator and complete teardown remain unchanged.

The constructor clears the owner before validating the configuration pointer, size and interface string. Invalid input returns six without allocating. Valid input allocates and publishes a 212-byte context, clears it, and reloads the owner between child initializers. It retains the stock absence of a local allocation-null guard.

| Native entry | C provider |
| --- | --- |
| `0x6eb94` | `goodix_spo2_init` |
| `0x36bd4` | `r1_goodix_spo2_initialize_descriptor` |
| `0x34a3c` | `r1_goodix_spo2_allocate_pair` |
| `0x3727c` | `r1_goodix_spo2_initialize_aggregate` |
| `0x362b6` | `r1_goodix_spo2_initialize_owned` |
| `0x96a20` | `r1_goodix_spo2_initialize_buffer_owner` |
| `0x2f624` | `r1_goodix_spo2_initialize_model_owner` |
| `0x34aa0` | `r1_goodix_spo2_initialize_channels` |
| `0x6635c` | `r1_goodix_native_float_record_initialize` |
| `0x2963a` | `r1_goodix_native_buffer_initialize` |
| `0x5a62c` | `r1_goodix_spo2_initialize_descriptor_pair` |
| `0x662ea` | `r1_goodix_native_f32_queue_initialize` |
| `0x66304` | `r1_goodix_native_s16_queue_initialize` |

The helpers preserve overlap-safe descriptor copying, unsigned division and wrapping allocation sizes, sixteen-bit capacity fields, provided-buffer index semantics, reserved bytes, live pointers/counts and native return words. The model-owner helper has an unusual return: its stack template overwrites the slots later popped into R0–R3. C now reloads the potentially modified first template word after the callback; it does not return the incoming record address.

All 614 paired stock/C cases pass, executing all 668 native instruction bytes. Comparisons include complete public records and the allocated arena, owner writes, allocation/provider arguments and snapshots, return words, saved registers, SP, masks, guards and exact active-context FPSCR. Cases include invalid configurations, channel gates, arithmetic boundaries, overlapping copies, provider mutations, provided buffers, modeled null allocations and callback changes to the model template.

A further 128 lifecycle cases execute the actual C constructor, existing complete C teardown, C pool initializer/allocator/free and compiled memory routines. The full heap matches stock, and every allocation made by recovered code coalesces back to the prior top. Deeper session/short-pair effects are modeled as zero and model creation returns null; their missing allocations are excluded. The isolated byte-fill object used for linking has the exact same 104 relocation-free machine bytes as the normal monolithic C provider.

Twenty compiled defects are rejected, covering validation and owner clearing, interface/size checks, context filling, owner reloads, metadata division/returns, allocation sizes and strides, maximum selection, model-template reloads, channel gates, provided-buffer state, queue element sizes, reserved bytes and full-width allocation counts.

The remaining boundaries are explicit:

| Native entry | Dependency |
| --- | --- |
| `0x5cd90` | `r1_goodix_spo2_session_initialize` |
| `0x31914` | `r1_goodix_spo2_short_pair_initialize` |
| `0x6a018` | `r1_goodix_spo2_weights_get` |
| `0x36c26` | `r1_goodix_spo2_model_create` |

A separate same-ELF copy probe isolates a Unicorn 2.1.4 instrumentation discrepancy: QEMU and Unicorn without a broad write hook exit zero; Unicorn with a no-op broad hook exits one. Final direct tests restrict the write hook to the owner word, retaining the original owner-write assertions and full memory comparisons. Lifecycle tests compare full heap images without a broad write trace. Firmware was not changed to mask this discrepancy. The real model-owner return mismatch was corrected and tested through callback mutation.

All 870 prior nongenerated source/object pairs remain unchanged, and the tested object matches the normal build object. Existing generated startup and uecc objects differ. Source-plan and cache layout remain unchanged.

Null allocation failures are logical access-shape checks, not physical fault proof. Cold FP/task activation, interrupt concurrency, invalid pointers, allocator exhaustion/scheduler behavior, final placement/startup, deeper initialization/resources, physical sensors and boot remain open. Relocatable composition is not bootable firmware. No instruction or image identity is claimed.
