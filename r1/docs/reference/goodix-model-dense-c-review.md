# Native float dense layer in C

`native_model_dense.c` implements252 native instruction bytes at`0x85b9c`
and resolves`r1_goodix_model_dense_executor_address`. No assembly, stock fallback
or writable global state is added.

Cache input rows*columns (32-bit wrapped), input data, output descriptor, weight/bias pointers, operation unit count and output data in native order. Input batch count is unused. Unit and inner span loops are signed. For each unit start +0, load live input and unit-major weight, multiply then add separately rounded, and add bias as first operand before storing.

Activation selector byte at operation+5 is read after dense writes. Selector1 caches slope at+8, but reloads output descriptor and batch*rows*columns each loop test. Signaling compare carry-clear selects strictly negative values, excluding unordered; multiply negative by slope then store, retaining zero/NaN payloads otherwise.

Selector byte is read again before sigmoid; earlier alias writes can change it. Selector2 negates raw sign bits, compares signed bits against0x42b00000 and substitutes88 at or above it; calls actual C expf, adds1 as second operand and divides1 by the result. Output count remains live on every loop test. No fused arithmetic or numeric-float clamp substitutes.

Actual C dense descriptor constructor writes real C callback relocation and indirect probe invokes it. Callback identity is guarded; only the callback pointer word is normalized for stock/C RAM comparison. All weight/bias/cursor and output memory is compared. Source maps no stock code and uses no expf/memory models.

REA raw252-byte body,12 literal bytes and binding0x74c44 match locked stock. Current Ghidra has no function record at0x85b9c; no fresh pseudocode is claimed. Capstone/native replay establish ordering.

20,074 stock/C comparisons pass:10,346 direct and9,728 constructor/callback
comparisons, including1,536 with normal objects. Independent finite arithmetic,
leaky-negative and zero-sigmoid oracles pass. All252 body bytes/85 instruction
starts execute. Ten compiled defects are rejected: span/unit owner, weight stride,
lost/reversed bias, lost slope, unordered activation, lost exponent clamp,
wrong sign negation and cached output count.

All929 normal units compile without failures or duplicate strong symbols.
All918 prior nongenerated source/object pairs are unchanged. Normal provider
sections/decoded symbols match the tested candidate after source-file metadata
normalization. Application imports fall71 to70; boot imports stay22. Source plan
and cache layout remain unchanged.

Valid aligned pointers and mapped effective spans required; wrapped spans tested only when effective storage is mapped. Signed negative counts skip relevant loops but initial cached descriptor reads remain required. Large invalid buffers have no invented fallback.

Public RAM/full FPSCR, saved R4-R11/S16-S31, SP/masks and R0 checked;8192 private stack bytes below incoming SP and caller scratch/APSR excluded. Coverage includes all252 body bytes/85 instruction starts and32 FP settings, not every input or interleaving.

Probe linker enum-size warnings are retained; called interfaces use integers/pointers/floats rather than enums. Timing, concurrency, interrupts, cold FPU and physical hardware unverified.

Three model callbacks, parent SpO2 stages, hardware imports and startup remain.929-unit relocatable composition with70 application/22 boot imports is not a bootable firmware proof.

[Machine-readable evidence](goodix-model-dense-c-review.json).
