# Native quantized merge in C

`native_model_merge.c` replaces the418-byte callback at`0x28ec8` and resolves
`r1_goodix_graph_merge_executor_address`. Actual C rounding and memory providers
execute. No assembly, stock fallback or writable global state is added.

Four arguments: operation unused, interleaved input data/range descriptors, output data/range descriptors, unsigned operand count. Descriptor words are element size, batches, rows, columns, data.

Cache output descriptor/batches and first input columns before union scan. First range replaces zero bounds without comparison. Later lower selection uses signaling compare carry-clear, upper ordered greater-than; raw signed zeros and NaNs retained. Cache output data after union.

Batch traversal is signed. Reload operand range/data descriptors and rows each iteration. Byte span wraps rows*cached columns; source offset wraps batch*span. Close-upper then close-lower short-circuit subtract/signaling compare chooses subtraction direction; signed raw result bits must be less than 0x358637bd. This is not a numeric epsilon comparison.

Close bounds call actual C memmove for unsigned span. Otherwise compute input/output widths and low delta; divide widths by255, ratio their steps, delta/output step, add separately rounded scale*128. Read live signed bytes, multiply scale then add offset, call actual C quantize-round, clamp integer code0..255 then subtract128. No invented width clamp or fused arithmetic.

Forward slow writes retain live aliases. Fetch output range descriptor/data late and store cached union even with no batches/operands. Output metadata remains untouched.

REA body/literals/binding match authenticated stock. No Ghidra function-manager record or fresh pseudocode is claimed. Actual C getter returns relocation to C callback and invokes all four arguments indirectly. Source replay maps no stock code and has no rounding/memory models.

Verification passes26,381 stock/C comparisons:20,301 direct and6,080 through
the real getter/four-argument callback, including960 with normal objects.
All418 bytes/144 instruction starts execute. Thirteen compiled defects are
rejected. Independent byte/range oracles cover all256 byte codes, epsilon
neighbors, empty operands and live bounds mutation causing both clipping limits.

All928 normal units compile without failures or duplicate strong symbols.
All917 prior nongenerated source/object pairs are unchanged. The normal provider
matches tested sections/decoded symbols after source-file metadata normalization.
Application imports fall72 to71; boot imports remain22. Source plan and cache
layout are unchanged.

Valid aligned descriptors and mapped effective spans required, including first/output cache reads for zero operands. Unsigned operand loops require valid lists. Signed batch/slow-span bounds differ from unsigned fast copy length; invalid huge copies are not assigned fallback behavior.

Public RAM, full FPSCR, saved R4-R11/S16-S31, SP/masks and R0 checked; only8192 private stack bytes below incoming SP excluded. Caller scratch R12/APSR is not promised. Tests cover32 FP settings, both NaN signs, live range mutation, clipping, epsilon boundaries, all byte codes and all418 bytes/144 instruction starts, not every input/interleaving.

Enum-size linker warnings retained in probe logs; called interfaces use pointers/integers rather than enums. Timing, interrupts, concurrency, cold FPU and physical hardware unverified.

Four callback bindings, five parent SpO2 stages, other hardware imports and startup remain.928-unit relocatable composition with71 application/22 boot imports is not a complete bootable firmware image.

[Machine-readable evidence](goodix-model-merge-c-review.json).
