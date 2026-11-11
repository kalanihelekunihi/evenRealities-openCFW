# R1 SpO2 session and short-pair initialization in C

The [model resource review](goodix-spo2-model-resource-c-review.md) supplies the readonly model data, weights getter and forwarding head. The generated-model constructor at `0x99014` remains unimplemented.

`r1/src/application/goodix/native_spo2_session_initialize.c` implements four more native routines. The shared initialization header gives the constructor and queue providers consistent declarations; the existing constructor's machine object remains unchanged. The [machine-readable receipt](goodix-spo2-session-c-review.json) pins sources, objects, REA evidence, fixtures and the normal build.

All 882 units compile and compose without duplicate strong symbols. Two imports are removed, with no additions: application imports fall from 66 to 64, while bootloader imports remain 22. No new writable state is introduced.

| Native entry | C provider |
| --- | --- |
| `0x5cd90` | `r1_goodix_spo2_session_initialize` |
| `0x31914` | `r1_goodix_spo2_short_pair_initialize` |
| `0x3df18` | `r1_goodix_spo2_initialize_session_channel` |
| `0x6633a` | `r1_goodix_native_extended_s16_queue_initialize` |

Session initialization creates two 100-byte channel groups, three 125-element float records and one 125-element extended s16 queue. Each channel group uses capacities 25, live window plus 12, 25, one, signed 125/window, and signed 125/period. Allocation receives the full 32-bit counts; metadata stores their low 16 bits. Reserved gaps remain untouched.

Short-pair initialization writes a zero header, creates a 125-element s16 queue, reloads its divisor after that allocation, and truncates the signed quotient to 16 bits **before** passing it to the second queue initializer. The extended s16 initializer preserves the allocation/provided-buffer distinction, wrapping allocation size, zero index/flags and low-byte mode.

All 670 direct stock/C comparisons pass, executing all 288 native instruction bytes. They cover signed extreme nonzero divisors, wrapping counts, provided buffers, mode truncation, allocator changes to descriptor fields, and modeled null allocations. Complete allocation arguments, records and arena images match, as does divisor read order. Independent allocation-sequence oracles check the numeric behavior. Saved integer/FP registers, SP, masks, guards and exact active-context FPSCR also match.

The existing descriptor builder always supplies nonzero divisors 5/25/25 on the known constructor path. Malformed zero-divisor descriptors and CCR divide-trap behavior are outside this proof. Large or negative symbolic allocation arguments test ABI behavior, not physical allocation validity.

A further 614 full-constructor comparisons now execute the session and short-pair graph as actual C. The 128 real-C-heap lifecycle cases also execute all recovered session/short-pair allocations, the constructor and complete teardown. Heap images match stock, and every recovered allocation coalesces back to the prior top. Only the weights getter and model constructor remain modeled; model creation returns null, excluding its missing allocations.

Sixteen compiled defects are rejected: signedness and truncation errors; wrong divisors, offsets, capacities or element sizes; incorrect mode/index initialization; reserved-gap overwrites; and caching descriptor values before allocator callbacks.

The final tests retain the scoped instrumentation established by the earlier independent copy probe. No broad memory-write trace is claimed. Source execution cannot enter stock, and modeled ports return through BX LR instructions. Cold FP/task activation, concurrency, invalid pointers, caller scratch, APSR and private frames remain outside the proof.

All 870 other prior nongenerated source/object pairs remain unchanged. The caller object is also unchanged, and both tested objects match the normal build. Existing generated startup and uecc objects differ. Source-plan and cache layout remain unchanged.

The SpO2 weights getter and model constructor remain unresolved, alongside other algorithm/hardware dependencies, final executable linking/startup, physical sensors and boot. Relocatable composition is not bootable firmware; no instruction or image identity is claimed.
