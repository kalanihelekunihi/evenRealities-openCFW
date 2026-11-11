# Native recurrent GRU in C

`native_model_recurrent.c` implements1120 native instruction bytes at`0x739a8`
and resolves`r1_goodix_model_recurrent_executor_address`.

Operation words are units,state,input-byte weights,recurrent-byte weights,parameter table. Input descriptor rows word supplies vector length and data word16 supplies vector start; output data cached. Exactly one frame runs per call regardless of descriptor batch/column/element fields. Both weight zero points must be128 or returnf000000e without public writes. Recompute state zero point from recurrent bounds after eligibility.

Parameter table contains4N bias floats,6 metadata float words(two input bounds,two recurrent bounds,two unused),3N input coefficients and3N recurrent coefficients. Caller-backed scratch starts input+M*4:3N input scale floats,3N recurrent scale floats,2N integer dots,2N gate floats,align4(N) state bytes,N candidate floats,M input bytes. All native address/count arithmetic wraps32 bits; traversal counts are signed.

Recurrent scale factor is (1/127)*(recurrent-width/255), then coefficient. Input range starts at+0, lower selects signaling-compare carry-clear and upper orderedGT. Call actual C range-adjust policy3, clamp step with signed raw bits to1e-6, derive rounded zero point and input-step*input-weight-step before coefficients. Quantize current input and state with actual C round and native USAT8; state conversion uses signed integer zero point plus state*127.

Four actual C unsigned-byte matrix calls compute2N input/recurrent gate dots thenN candidate input/recurrent dots. Bias is accumulator first and dot*scale product added with separate rounding. Gate sigmoid negates raw sign bits, uses signed raw-bit clamp88, actual C expf, add(exp,1), divide(1,sum). Candidate recurrent term is bias+dot*scale, multiplied by reset gate and added to candidate input term before actual C tanhf.

Final blend separately rounds update-gate*current-state, subtract(1,gate), its product with candidate, then accumulator+product. Store state before output per unit. State, output and scratch aliases remain live, including effects on later units/frames. New input data can be supplied between calls while retaining state and sticky FPSCR.

Actual C constructor, heap initialization, malloc, clearing, memory and callback execute. Callback identity guarded; only operation+20 callback word is normalized after execution. Independent descriptor/cursor/pool/payload-address and zero-state/output oracles pass. Fatal/OS boundary link placeholders are guarded to fail if invoked; positive allocation suites never reach them. Source maps no stock code and uses no algorithm/math/memory/allocator models.

Complete REA function-manager dossier and raw1120-byte body,36-byte literal pool and callback binding authenticate against locked stock. Body0x739a8..0x73e07, literal0x74a98=Thumb0x739a9. No assembly or writable global state is added. Actual normal C support, quantization, classifier and math objects execute in normal tests.

18,504 stock/C case or sequence comparisons cover20,604 paired callback
invocations. This includes13,232 direct cases/sequences,552 with normal objects,
and4,720 constructor/heap/callback comparisons(720 with normal objects).
Tests use all32 FP configurations, nine live aliases, changing inputs and state
persisting across calls, signed input lengths and ignored batch metadata.
All1120 bytes/365 instruction starts execute. Seventeen compiled defects are
rejected: eligibility logic, vector dimension, scratch alignment, recurrent
coefficients/factor, range adjustment, epsilon, input zero point, saturation,
weight tail, candidate bias/reset gate/tanh, complement, state/output stores and
bias operand order.

All932 normal units compile without failures or duplicate strong symbols.
All921 prior nongenerated source/object pairs are unchanged. Normal sections and
decoded symbols match tested candidate after source-file metadata normalization.
Application imports fall69 to68; boot imports remain22. Source plan and cache
layout remain unchanged.

Valid aligned descriptors and sufficient mapped caller-owned backing capacity for input-adjacent scratch are required. Tests cover units0..4, ordinary and negative input lengths where effective accesses remain mapped. Invalid enormous buffers or concurrent descriptor mutation have no invented fallback.

Public RAM/full FPSCR, saved R4-R11/S16-S31, SP/masks and scalarR0 are checked.8192 private stack bytes below incoming SP and caller scratch/APSR excluded. Constructor normalization affects only a guarded callback pointer word. All1120 bytes/365 instruction starts execute, not all inputs or interleavings.

Independent GRU finite-state/output recurrence checks cover repeated calls; zero-candidate recurrence is exact and finite tanhf oracle tolerance2e-6 is confined to that independent numerical check. Direct stock/C comparisons remain exact, including per-frame state/output/FPSCR traces.

Constructor tests use a fresh16384-byte heap, units0..4 and valid nonnegative input lengths; zero-unit minimum allocation remains native. Allocation failure/fatal routes are outside this integration proof and were separately reconstructed. Enum-size/absolute-Thumb linker warnings retained; tested interfaces use integer/pointer/float types.

Normal932-unit relocatable composition has68 application/22 boot imports. Quantized convolution is the remaining model callback. Parent SpO2 stages, other hardware dependencies, startup, interrupts, timing, concurrency, cold FPU and physical boot remain unresolved or unverified.

[Machine-readable evidence](goodix-model-recurrent-c-review.json).
