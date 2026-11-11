# Native quantized convolution in C

`native_model_i8_convolution.c/.h` implements the remaining model executor at
`0x85dc4` and three native helpers. It resolves
`r1_goodix_graph_aligned_executor_address` and adds no assembly or writable state.

Full-word input rows/columns/element size are cached, as is input data before padding. Padded width is full32-bit columns+left+right. Padding zero point uses round(-inputLow*255/max(1e-4,inputWidth))-128, but later scale product uses ORIGINAL unclamped input width/255 and weight width/255. Unsigned arithmetic preserves wrapped addresses and dot/bias sums.

Expand input descending rows using actual C memmove and memset of signed-byte zero point. Copy lengths are columns*element; addresses and pad fills advance bytes. Inclusive input<=output<input+padded-count relocation moves output to input+padded-count and records its original address. After computation restore input ascending rows, copy relocated output using live descriptor row*column*element product, restore output data pointer, and fetch/store output range late.

Operation channel/group bytes use native nonnegative signed-division results. Weight bytes count is groups*in-per-group*kernel*out-per-group, rounded up4; then two weight-range floats and per-channel coefficients. Bias table contains signed32 biases, two bias-range floats and two output-range floats. Adjust output range through actual shared C range-adjust policy3. Private128word array stores scale and bias entries for at most64 total output channels.

Scale factor is2^31*(inputStep*weightStep/outputStep), then coefficient FIRST times cached factor. Signed raw-bit value<0.5 yields0; otherwise separately add0.5, native unsigned RTZ conversion/status and clampUINT>=INTMAX toINTMAX. Bias step is((biasHigh-biasLow)*2^-32)/inputWeightProduct; each bias code rounds((float(bias)*biasStep)/coefficient)-(adjustedOutputLow/inputWeightProduct/coefficient). All native operation order/raw-bit decisions are retained; no undefined C float-to-int casts.

Dots and zero-point compensation wrap32 bits. Signed accumulator times nonnegativeQ31 multiplier fits int64; add positive2^30, shift31 and clip code0..255 then subtract128, returning sign-extended centeredbyte. Negative ties follow native positive-half rounding. Kernel5 computes only in-per-group1or4, one out-per-group set. Kernel3 group1 computes generic dots with per-read zero subtraction; groups!=1 preserves native depthwise-like computation of one output channel per group, even when out-per-group>1.

Kernel1 precompensates every out-per-group bias before outputs. In-per-group1or2 caches FOUR output accumulators before any stores and writes offsets0..3 even for a partial last block; other channel-unroll cases preserve per-pixel live data effects through modulo32 accumulation. Kernel5/grouped3 compensation also precedes output writes. Unsupported shapes/kernels retain native untouched outputs while still preprocessing/restoring/storing range. Stride byte1, activation byte7 and slope word8 are unused; no generic behavior is invented.

Round29120 stock bytes equal290dc; range36590 stock bytes/literals equal36408 except floor-call displacement to the same39220. Exported C wrappers delegate to proven actual C recurrent helpers; clipping37b68 has its own native scalar contract. Source maps no stock code and uses no algorithm/math/memory models. Actual C aligned constructor installs C relocation and invokes callback; only guarded operation+20 pointer word is normalized.

Canonical stock ELF had no function-manager record at85dc4. Additional ignored ELF sets Thumb entry/function symbol85dc5; every PT_LOAD field/byte and text payload is verified identical to canonical/locked stock. REA then supplies complete dossiers. Main body3546 instruction bytes lies in two ranges85dc4..86209 and86218..86bab;14-byte inline-pool/alignment gap is excluded from code coverage. Synthetic analysis name is not an official recovered name. Original artifacts and source qualification references are unchanged.

211,945 stock/C comparisons pass:14,546 direct main comparisons,160,665
helper comparisons,7,424 constructor/callback comparisons and29,310 normal-object
main/helper comparisons. Constructors include1,152 normal-object comparisons.
All3968 instruction bytes/1314 starts execute. Eighteen compiled defects are
rejected:relocation bounds/stride,element copy length,Q exponent,scale gate/
conversion/clamp,zero compensation,invented shapes/grouped outputs,missing
four-output tail,signed accumulator/rounding,clip offset,restoration,output range
and full-word column geometry.

All933 normal units compile without failures or duplicate strong symbols.
All922 prior nongenerated source/object pairs are unchanged. Normal sections and
decoded symbols match tested candidate after source-file metadata normalization.
Imports fall68 to67 application;boot imports stay22. All model callback bindings
resolve. Source plan and health-cache layout remain unchanged.

Valid aligned descriptors/range/coefficient words and mapped backing spans, including padding, relocation and four-output tails, are required. Legal private-table capacity is64 total output channels; tests include64,63,62 and groups up to64. Invalid oversized tables/caller buffers have no invented fallback. Preserved selective/unrolled behavior is not generic grouped convolution.

Constructors require nonzero groups and tested output counts divisible by groups. Direct callback tests include zero groups with DIV_0_TRP clear; explicit C guards match zero division results there. Trap-enabled zero groups are outside proof. Arithmetic scalar code and register scratch do not promise caller APSR/Q flags.

Public RAM/full FPSCR,saved R4-R11/S16-S31,SP/masks and scalarR0 are checked;8192 private stack bytes and caller scratch/APSR excluded. Only guarded constructor callback word normalized. All3968 bytes/1314 instruction starts execute, not all inputs/interleavings. Broad suites use six FP settings; targeted/helper/constructor/limit suites all32. Timing,interrupts,concurrency,cold FPU and physical hardware unverified.

Independent zero-dot and rational gain oracles cover all256 byte codes and partial output tails; descriptor/resource cursor layouts are independently checked. Header inclusion preserves entire candidate object byte-for-byte. Probe enum-size/link warnings retained; tested interfaces use integers,pointers,floats rather than enums.

All model executor address bindings now resolve to C. Normal933-unit relocatable composition still has67 application/22 boot imports. Five parent SpO2 stages, other hardware dependencies, startup and complete physical boot remain open. This does not establish complete inference or a bootable final image.

[Machine-readable evidence](goodix-model-i8-convolution-c-review.json).
