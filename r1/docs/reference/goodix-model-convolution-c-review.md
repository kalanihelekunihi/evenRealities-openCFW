# Native float convolution in C

`native_model_convolution.c` implements1234 native instruction bytes at`0x76bdc`
and resolves`r1_goodix_graph_convolution_executor_address`. No assembly, stock
fallback or writable global state is added.

Operation bytes0..7 are kernel,stride,left/right padding,input/output channels,groups,activation; slope float8, weights12,bias16. Cache input descriptor element size/rows/columns as BYTES, input data and padded low8(columns+padding). Output rows*columns word product is cached, but arithmetic uses low8 output columns.

When padding changes row*columns, expand input descending rows using actual C memmove/memset. Copy/clear lengths use cached element-size byte, while addresses advance four bytes per element. Reload input descriptor/data and padding bytes at native points. Cache arithmetic input data before expansion writes.

Output overlap relocation compares unsigned output pointer strictly between input pointer and input+padded-element-count, not a byte-scaled upper bound. Save original and move output pointer to input+padded-count*4. After computation/activation, restore input ascending rows. Copy relocated output using live output rows*columns*element-size word products, then restore pointer through current output descriptor.

Unsigned division determines channels per group. Kernel1 computes one out-per-group set; kernel3 uses specialized groups1 or general grouped path; kernel5 executes only groups1. Unsupported kernels/groups skip arithmetic but retain activation/restoration. Specialized3/5 output-channel bound rereads operation byte5. Grouped3 weight base advances group*out-per-group*kernel words, omitting in-per-group from that group offset, as native evidence requires.

Convolution reads live input/weight words, multiplies then adds with separate rounding and accumulator first. Bias is added SECOND after the inner sum. Output stores and overlaps remain live for subsequent computations. No numeric activation simplification or reassociation is used.

Activation selector byte7 is read separately before each pass. Selector1 always signaling-compares cached slope with zero, including empty output. Zero-slope path replaces strictly negative values with raw positive zero; nonzero path multiplies. Unordered inputs are retained. Each loop test multiplies cached output row/column span by LIVE output batches. Selector2 sign-bit negates raw output bits, signed-compares against0x42b00000, clamps to88, calls actual C expf, adds1 as second operand and divides1 by the result.

Actual C descriptor constructor installs real C relocation; indirect callback identity is verified and invoked. Only callback word at operation+20 is normalized after execution. Source maps no stock code and uses no math/memory models. REA full function-manager body/pseudocode/assembly and raw body/literals/binding authenticate1234 bytes at0x76bdc..0x770ad and Thumb pointer0x76bdd at0x74b40. Instruction evidence resolves pseudocode float/int and incidental return-register ambiguities.

41,428 stock/C comparisons pass:34,132 direct and7,296 constructor/callback
comparisons, including1,152 with normal objects. Independent finite convolution,
restored-input, zero-sigmoid and live-metadata oracles pass. All1234 body bytes /
442 instruction starts execute. Sixteen compiled defects are rejected, including
word-vs-byte metadata, padded wrap, relocation bounds/target, element copy length,
grouped weight stride, invented kernel/group support, bias operand order, slope
compare/zero handling, numeric exponent clamp, reloaded cached span, cached live
channel bounds, input stride and missing input restoration.

All930 normal units compile without failures or duplicate strong symbols.
All919 prior nongenerated source/object pairs are unchanged. Normal provider
sections/decoded symbols match tested candidate after source-file metadata
normalization. Application imports fall70 to69; boot imports stay22. Source plan
and health-cache layout remain unchanged.

Valid aligned descriptors and sufficient mapped backing capacity for padded input/output/scratch are required. Wrapped metadata is tested only where effective accesses remain mapped. No invented fallback is provided for invalid enormous buffers.

Constructors require nonzero groups. Direct callback tests include zero groups with Cortex-M DIV_0_TRP clear: native UDIV yields0, matched by explicit C guards. Division-trap-enabled zero groups and asynchronous interleaving are outside proof.

Public RAM/full FPSCR, saved R4-R11/S16-S31, SP/masks and scalar R0 checked;8192 private stack bytes below incoming SP and caller scratch/APSR excluded. Native incidental R1 operation-pointer restoration is not a promised C scalar ABI return. Only constructor callback address word is normalized after identity guard.

All1234 bytes/442 instruction starts execute. Broad cases use six FP settings; targeted edge/metadata/oracle/live and constructor suites use all32 settings. This is not all inputs or interleavings. Cold FPU, timing, interrupts, concurrency and physical hardware remain unverified.

Probe linker enum-size warnings retained; called interfaces use pointers/integers/floats rather than enums.930-unit relocatable composition with69 application/22 boot imports is not a complete bootable image. Quantized convolution and recurrent bindings, five parent SpO2 stages, other hardware imports and startup remain.

[Machine-readable evidence](goodix-model-convolution-c-review.json).
