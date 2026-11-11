# Native model graph execution in C

`native_model_graph_execute.c/.h` implements five native entries with no assembly or writable global state. The native interface is distinct from the historical portable bool/scratch routines.

The seven-argument native graph runner executes the second subgraph, dense/dense/softmax, preserves its three probabilities at workspace+0x8b8, copies the first input to workspace, executes the first subgraph, concatenates120+3 features, runs the16-unit recurrent stage and two dense stages, then copies the final live output descriptor span. Callback status words are ignored. Reset clears recurrent state only when its full32-bit value equals1; nonzero state is seeded before each test.

Both subgraphs execute the native quantize/convolution/pool/residual/dequantize/projection/float-add topology. Quantization bounds are overwritten from the model after the first quantizer, scalar auxiliary data is2000, and byte/float scratch offsets are0x3e0/0x1f0. Native dimensions and20-byte descriptor copies are preserved. Local descriptor pointer variables remain mutable for callback use; cached versus live public buffer addresses are retained.

The u8 three-stage pipeline uses fixed local descriptor addresses and forwards the live second output pointer between calls. The float projection pipeline reloads its mutable descriptor pointer variables. Both return the final descriptor-copy destination in native R0. The veneer passes all seven arguments; incidental caller-scratch register restoration is outside the scalar C ABI.

Every positive graph comparison constructs the full model with actual C heap/model constructors and the locked3924-word parameter data, then executes all actual reconstructed C operators, math and memory providers. The source machine maps no stock executable code. Only45 explicitly enumerated model callback fields are normalized, after checking each against its exact native address or corresponding C symbol. No arbitrary differing data is normalized.

256 stock/C comparisons pass, including128 with the normal build object. All1476 native instruction bytes/549 starts execute. Eight compiled defects are detected: short input/concatenation copies, wrong subgraph/config/range/softmax input, broad reset and missing reset. Tests compare full public RAM and ABI, not merely final predictions.

All934 normal units compile without failures or duplicate strong symbols. All923 prior nongenerated source/object pairs are unchanged. Normal sections and decoded symbols equal the tested candidate after source-file symbol normalization. Imports stay67 application/22 boot.

Proof covers valid aligned model/descriptor/buffer contracts and the actual generated model, randomized finite input windows, all32 FPSCR configurations, and reset0/1/2/UINT32_MAX. It does not prove arbitrary custom model graphs or malicious callback mutation. Callback status failures and null/undersized buffers retain no invented recovery.

Public RAM excludes8192 private stack bytes below incoming SP. R0, full FPSCR, SP, savedR4-R11/S16-S31 and interrupt masks are compared. Caller scratch registers and APSR, timing, interrupts/concurrency and physical hardware are unverified. All1476 instruction bytes/549 starts execute, which is coverage rather than exhaustive input proof.

The normal934-unit build is relocatable composition with67 application and22 boot imports, not a complete bootable firmware image. The five parent SpO2 stages and other hardware/startup dependencies remain open. A parent inference candidate exists only as an ignored probe and is not admitted by this receipt. Source-plan qualification and health-cache layout are unchanged.

[Machine-readable evidence](goodix-model-graph-execute-c-review.json).
