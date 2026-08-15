# Quantized-runtime reduction correlation (owner-authorized, 2026-08)

## Decision

Under the "Owner-authorized full reduction (2026-08-14)" section of
[`../SOURCE-ADMISSION.md`](../SOURCE-ADMISSION.md), the 27-function family
`unknown_shared_quantized_neural_runtime_candidate` is reduced from the
recovered decompilation evidence to compilable C at
[`../../reconstructed/quantized_runtime/`](../../reconstructed/quantized_runtime/).
The reconstruction is not vendor source and is never presented as such;
every file carries the provenance banner.  The ledger disposition for the 26
entries becomes `clean_room_reimplementation_owner_authorized` when the
integrator wave re-pins it.  The boundary doc
[`../boundaries/QUANTIZED-POOLING-PROVIDER-BOUNDARY.md`](../boundaries/QUANTIZED-POOLING-PROVIDER-BOUNDARY.md)
remains the provenance record of why no upstream source could be admitted
(CMSIS-NN, TFLM, NNoM, uTensor, tinyMaix, X-CUBE-AI all eliminated with
quoted evidence in the 2026-08 attribution re-examination; the runtime is
Bravechip BCL603M "ChipletRing" middleware with no public footprint).

Stock image: application, load base `0x00027000`, SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

## Evidence extraction path

- Ghidra bodies: `research/decompilation/application/decompiler-output.c`
  (26 shared entries and twenty-three Goodix extensions). Ghidra missed two
  installed executors: the shared float dense body at
  `0x00085B9C..<0x00085C98` and the Goodix body at `0x00085DC4`; their complete
  `0x00085DC4..<0x00086BAC` extent is therefore a manual provenance
  supplements are pinned from constructor Thumb tokens `0x00085B9D` and
  `0x00085DC5`, full disassembly, literal-pool boundaries, and the next
  independent prologues.
- Every body was cross-checked against fresh `arm-none-eabi-objdump -D -b
  binary -m arm -M force-thumb` disassembly of the byte-exact rebuilt image
  (`research/decompilation/rebuild/rebuilt-application.bin`).  The
  disassembly corrected two Ghidra renderings (below) and confirmed all
  others instruction-for-instruction.
- Literal pools were read from the rebuilt image: `1e-4f` (`0x38D1B717`),
  `255.0f`, `253.0f` (`0x437D0000`), `254.0f`, `-255.0f`, the fraction
  range-check constants `0xC77FFFFF`/`0x06FFFBFF`, softmax `-FLT_MAX`
  (`0xFF7FFFFF`) and `88.0f` (`0x42B00000`), and the code-pointer constants
  `0x00095B21`, `0x00036DCD`, `0x00076BDD`, `0x0005D245`,
  `0x000293FD`, `0x00098EDD`.
- Callee attribution (`research/decompilation/application/functions.csv` +
  ownership ledger): `0x000392D8` = toolchain `fminf`, `0x00039290` =
  `fmaxf`, `0x00039220` = `floorf`, `0x00038F08` = `expf`, `0x00027606` =
  `qsort` (all `arm_toolchain_runtime`); `0x0002775C` = `memmove` thunk,
  `0x000277AA` = `memset(..., 0, n)` thunk; `0x00091CCC` (scaled multiply)
  and `0x00091E02` (tensor slice) are `gomore_health_algorithm_candidate`.
  Both exact bodies are now separately owner-authorized; the slice is implemented here as
  `quantized_runtime_tensor_slice`, while cross-family dispatch remains an explicit binding.
  `0x00058D4A` (the compactor's qsort comparator, three
  instructions: `ldr r0,[r0]; ldr r1,[r1]; subs; bx lr`) sits inside a
  GoMore-candidate audit extent and is reproduced as a local static.

## Recovered layout

- Executor tensor record (20 bytes): `+0x00` flag word (the float->int8
  quantizer stores `1`), `+0x04/+0x08/+0x0C` word dims, `+0x10` data
  pointer.  Element counts are dim products read per executor (quantizer:
  all three; int8-add and float-add: `dims[1]*dims[2]`; softmax: output
  `dims[1]`; pooling: input `dims[2]` row stride, output `dims[1]` rows,
  `dims[2]` columns).
- Pool tensor descriptor (`0x14` bytes): `+0x00` arena data pointer, `+0x04`
  element count, `+0x08..+0x0D` three uint16 dims, `+0x0E` flag byte (bits
  0-1 dimension count, bit 2 "no arena buffer", bit 3 slice/view),
  `+0x10` trailing word.
- Shared pool state root: 12 descriptors at `0x14` stride (`+0x000`), 12
  in-use bytes (`+0x0F0`), `0x6A4`-word compacting arena (`+0x0FC`),
  used-word watermark (`+0x1B8C`); total `0x1B90` bytes.  The
  reconstruction static-asserts all of these offsets for the 32-bit target
  ABI only.
- Layer/operator descriptor records: 24-byte conv-like record (eight packed
  parameter bytes, context float `+0x08`, weights offset `+0x0C`, bias
  offset `+0x10`, run pointer `+0x14`), a second 24-byte record shape
  (word `+0x00`, flag bytes `+0x04/+0x05`), the 16-byte operator record
  `{type, float argument, 0, executor}`, and the 12-byte quantizer record
  `{min, max, executor}`.  The int8-add executor reads its output
  `{min, max}` floats at descriptor `+0x04/+0x08`; the float-add executor
  reads activation type at byte 0 and alpha at `+0x04`.

## Per-function contract and reconstruction decisions

| Stock extent | Bytes | Reconstructed symbol | Contract |
| --- | ---: | --- | --- |
| `0x000290FE..<0x00029120` | 34 | `quantized_runtime_round_half_away_from_zero_290fe` | `(int)(value + (value > 0 ? +0.5f : -0.5f))`; NaN takes -0.5 (vcmpe+ble), vcvt truncates |
| `0x00029120..<0x00029142` | 34 | `quantized_runtime_round_half_away_from_zero_29120` | identical twin instantiation |
| `0x0002F624..<0x0002F658` | 52 | `quantized_runtime_goodix_model_owner_initialize` | Goodix extension: retain recovered `{1,1,125}` primary/secondary settings and `{1,2,1}` dimensions, then create/store the typed generated-model instance; reserved owner bytes remain untouched |
| `0x00030800..<0x0003096C` | 364 | `quantized_runtime_goodix_layer_block_build` | emit the complete 176-byte layer subgraph from seven shape bytes: five aligned descriptors, quantizer, optional sixth descriptor/flag, and cursor-pair int8 add; model words and target base are separate checked inputs, optional/no-optional paths consume the exact recovered spans, and failure clears the partial block |
| `0x000293FC..<0x000294B6` | 186 | `quantized_runtime_float_to_int8_quantize` | derive params from descriptor {min,max}; per element `(x-min)*scale`, round-half-away, clamp to [0,255], bias -128; store adjusted {min,max} to outputs[1], type flag 1 to outputs[0]; return 0 |
| `0x0002951A..<0x000295DE` | 196 | `quantized_runtime_goodix_five_stage_32_execute` | execute five explicit float stages over recovered `{1,12,32}->{1,12,1}...->{1,1,12}` tensor topology and `0x310`/`0x620` scratch banks |
| `0x00035E34..<0x00035F26` | 242 | `quantized_runtime_quantization_params_derive` | clamp min<=0<=max, range>=1e-4f, scale=255/range; when min<0 and the fraction's bits pass the recovered range check, shift min or max so the zero point is integral; outputs {min, max, range/255, scale}; void |
| `0x00035D6E..<0x00035E32` | 196 | `quantized_runtime_goodix_five_stage_27_execute` | five-stage sibling with `{1,12,27}` first tensor and tight `0x510`/`0x540` banks |
| `0x00036408..<0x00036574` | 364 | `quantized_runtime_recurrent_range_adjust` | mode-selectable asymmetric-u8 range correction; return -1/0/1/2/3 for invalid/unchanged/min/max/both adjustment |
| `0x00036590..<0x000366FC` | 364 | `quantized_runtime_recurrent_range_adjust` | exact second instantiation of the same helper: all 364 stock bytes match `0x36408` except one Thumb `BL floorf` displacement byte; constants, branches, outputs, and return codes are identical, so both entries intentionally map to one local C body |
| `0x00036C26` head + `0x00099014..<0x00099110` tail | 262 | `quantized_runtime_goodix_model_instance_create` | Goodix extension: allocate typed target-0x344 instance; build two fixed graphs, four shared descriptor records, softmax/external vectors, and one 16-unit/123-input recurrent descriptor; consume exactly 3,924 model words |
| `0x00036C7C..<0x00036D60` | 228 | `quantized_runtime_int8_add_execute` | per element: dequantize both int8 operands (zero point - 128), float add, divide by output step, round-half-away, add output zero point - 128, SSAT #8; store output {min,max} (descriptor +4/+8) to outputs[1]; return 0 |
| `0x00041816..<0x000419C8` | 434 | `quantized_runtime_pooling_execute` | byte0 type / byte1 window / byte2 stride: (0,2) max pool 4x-unrolled, (0,4) max pool, (1,3) average pool with sign-aware half rounding and truncating int8 store; all else silent no-op; return 0 |
| `0x0003F7F8..<0x0003F89C` | 164 | `quantized_runtime_goodix_f32_three_stage_execute` | three explicit float stages from six shape bytes; middle scratch bank is `max(minimum_span,(shape1+pad0+pad1)*shape0*4)` |
| `0x00042024..<0x00042108` | 228 | `quantized_runtime_goodix_u8_three_stage_execute` | quantized three-stage sibling with auxiliary range tensor propagation and recovered optional input-storage middle bank |
| `0x0004387C..<0x00043B2A` | 686 | `quantized_runtime_goodix_graph_build` | Goodix extension: emit the complete 0x160-byte fixed graph; consume exactly 439 explicit model words through quantizer, seven aligned descriptors, two cursor-pair adds, four shared descriptors, three pools, one external vector, and one add operator |
| `0x0005D01C..<0x0005D1AC` | 400 | `quantized_runtime_goodix_second_graph_build` | emit the complete 0x3D8-byte graph consumed by `0x617F8`: top quantizer, three aligned descriptors, five fixed `0x30800` layer blocks, explicit release binding, packed pool `{1,3,3,0}`, and conversion binding; exactly 1,567 caller-supplied model words are consumed and failures clear the partial graph |
| `0x000617F8..<0x00061C44` | 1,100 | `quantized_runtime_goodix_second_executor_execute` | complete second Goodix generated-model executor: six typed direct stages, explicit four-branch merge, five checked `0x876C8` layer plans using the recovered 14-byte records at `0xBD6A0...0xBD6E7`, exact 7×180→4×180→10×180 head, three 1×180 branches, 24→16→1 layer chain, overlapping `0x12FC` move, and concatenated 1×60 plus 3×60 float output; stock heap temporaries and descriptor pointers are replaced by caller-owned storage and typed bindings |
| `0x0005A3D4..<0x0005A40E` | 58 | `quantized_runtime_two_output_thirds_slice` | third = a->dims[0]/3; outputs[0]/[1] = bound slice(pool, a/b, third*index, third*(index+1)); stock void -> status return introduced |
| `0x0005D244..<0x0005D2DC` | 152 | `quantized_runtime_float_softmax_execute` | max pass, subtract, bit-level 88.0f cap (NaN-only in practice), bound expf, normalize; descriptor never read; return 0 |
| `0x00065680..<0x000656AA` | 42 | `quantized_runtime_scaled_mul_conditional_release` | bound scaled-mul seam(alpha=*source, pool, tensor, in_place=1), then release tensor when flag != 0; returns seam result |
| `0x0006FDE0..<0x0006FE16` | 54 | `quantized_runtime_recurrent_zero_point` | recurrent helper: `round((value-min) * 255/fmaxf(1e-4,max-min))` through the recovered 0x290DC rounding twin |
| `0x0006FE20..<0x0006FE56` | 54 | `quantized_runtime_zero_point_compute` | `round((value-min) * (255.0f / fmaxf(1e-4f, max-min)))` (tail-chains the 0x290FE rounder) |
| `0x000739A8..<0x00073E08` | 1,120 | `quantized_runtime_recurrent_execute` / `_target` | complete one-step quantized recurrent cell: dynamic input quantization, three input/recurrent matrix rows, two sigmoid gates, candidate `tanhf`, persistent state, and output; checked API resolves caller-supplied model bytes and workspace, target adapter retains the generated graph ABI |
| `0x0007400C..<0x0007405C` | 80 | `quantized_runtime_float_min_max` | first-element float minimum/maximum scan; checked no-op replaces stock empty/null fault |
| `0x0007405C..<0x0007412C` | 208 | `quantized_runtime_u8_matrix_vector` | row-major centered-u8 matrix/vector product with the recovered 32-bit accumulating behavior |
| `0x0003007E`, `0x00038050`, `0x000417F0` | 48 | `quantized_runtime_goodix_executor_execute` | three byte-identical 16-byte veneers preserve the six-argument target ABI and forward directly to `0x000742E4`; the typed reconstruction aliases them to the already tested complete executor body |
| `0x000742E4..<0x0007487E` | 1,426 | `quantized_runtime_goodix_executor_execute` | complete Goodix generated-model executor: modes 0/1/2, eighteen direct stages, five explicit nested stage plans, recovered 99→49→24→12 tensor topology, fixed/dynamic scratch banks, 16-byte tail input, alternating four-stage head, optional mode-2 tail, and checked final tensor copy; the opaque stock descriptor table and embedded target words are replaced by typed caller bindings |
| `0x00085B9C..<0x00085C98` | 252 | `quantized_runtime_float_dense_execute` / `_target` | complete row-major float dense layer with per-output biases, no-activation/leaky-ReLU/sigmoid modes, and the recovered signed-raw-bit 88.0f exponent cap; checked model and buffer extents plus alias scratch replace unchecked target pointers, while the descriptor constructor now installs the local target adapter |
| `0x00085DC4..<0x00086BAC` | 3,560 | `quantized_runtime_i8_conv1d_execute` / `_target` | complete signed-int8 channel-major grouped 1-D convolution: kernel-5 1/4-channel specializations, kernel-3 ordinary/depthwise paths, every kernel-1 unroll family, zero-point padding/correction, modulo-2^32 MACs, per-channel Q31 requantization, recurrent output-range correction, and final range propagation; the checked API exposes the exact weight/scale/bias/range schema with buffer extents and alias scratch, while the target adapter decodes the recovered arena ABI |
| `0x000876C8..<0x00087A6C` | 932 | `quantized_runtime_goodix_layer_execute` | complete quantized layer executor used five times by the second generated graph: optional preprocessing, signed-row means, three explicit conversion stages, capped sigmoid weighting, in-place range conversion, three tail stages, and four-input final merge; stock heap temporaries and the `0x00030535` vector are replaced by bounded caller storage and typed callbacks, including explicit handling of the stock unaligned float scratch bank |
| `0x00074A20..<0x00074A98` | 120 | `quantized_runtime_recurrent_layer_descriptor_construct` | Goodix extension: allocate/clear `units` floats; arena offsets are cursor, cursor+align4(units*input_dim*3), then +align4(units*units*3); advance by `(units*10+6)*4`; bind the local target executor adapter |
| `0x00074A9C..<0x00074AA0` | 4 | `quantized_runtime_executor_vector_95b20` | return the bound token for stock constant `0x00095B21` (0 unbound) |
| `0x00074AAC..<0x00074B3E` | 146 | `quantized_runtime_descriptor_construct` | zero 24 bytes; 8 packed bytes; context float +8; weights=*cursor +0xC; bias=*cursor + b5*b0*(b4/b6)*4 +0x10 (unsigned udiv, b6==0 -> 0, ARM quirk); run token +0x14; *cursor += b5*4 + span |
| `0x00074B44..<0x00074BD4` | 144 | `quantized_runtime_aligned_descriptor_construct` | Goodix extension: same packed header, align4(b5*b0*(b4/b6)) arena span, fixed b5*4+8 secondary offset, b5*8+24 cursor tail, reconstructed `0x85DC4` target-adapter binding |
| `0x00074BD8..<0x00074BDC` | 4 | `quantized_runtime_executor_vector_36dcc` | return the bound token for stock constant `0x00036DCD` (0 unbound) |
| `0x00074BE0..<0x00074C42` | 98 | `quantized_runtime_descriptor_record_construct` | 24-byte record: dim_b word +0, flag bytes +4/+5, context float +8, *cursor +0xC, *cursor+dim_a*dim_b*4 +0x10, reconstructed float-dense target adapter +0x14; *cursor += dim_b*4 + dim_a*dim_b*4 |
| `0x00074C6C..<0x00074C8A` | 30 | `quantized_runtime_packed_pool_descriptor_initialize` | Goodix extension: pack four low bytes, bind reconstructed pooling executor at +4 (stock absolute `0x00041817` removed) |
| `0x00074C90..<0x00074C94` | 4 | `quantized_runtime_executor_vector_30534` | Goodix extension: return explicit provider token for stock constant `0x00030535` (0 unbound) |
| `0x00074C98..<0x00074CAE` | 22 | `quantized_runtime_operator_descriptor_init` | {type & 0xFF, float argument bits, 0, in-family float-add executor vector} |
| `0x00074CB4..<0x00074CD6` | 34 | `quantized_runtime_cursor_pair_add_descriptor_construct` | Goodix extension: consume two cursor words and emit {0, word0, word1, reconstructed int8-add executor} |
| `0x00074CDC..<0x00074CE0` | 4 | `quantized_runtime_softmax_executor_vector` | in-family: returns the reconstructed softmax executor address (stock `0x0005D245`) |
| `0x00074CE4..<0x00074D02` | 30 | `quantized_runtime_quantizer_descriptor_construct` | cursor: read {min,max} word pair and advance by 2 words; NULL cursor: {0.0f, 1.0f}; install in-family quantizer vector (stock `0x000293FD`) |
| `0x00091C48..<0x00091C56` + `0x000936FC..<0x0009371C` | 46 | `quantized_runtime_tensor_release` | discontiguous body: 14-byte head tail-branches into the shared 32-byte slot-scan tail (this is why the ledger lists the entry end as `0x0009371B`); clear data pointer when flag bit 2 is clear, then free the matching pool slot |
| `0x00091C56..<0x00091C80` | 42 | `quantized_runtime_tensor_release_many` | for i in [0,count): release non-NULL entries, zero every array slot; signed count bound |
| `0x00091D9C..<0x00091DBE` | 34 | `quantized_runtime_tensor_allocate` | construct + arena allocate + clear bufferless flag |
| `0x00091DBE..<0x00091E02` | 68 | `quantized_runtime_tensor_create_fill` | construct + arena allocate + fill every word with the fill float's bits (signed count loop) |
| `0x00091E02..<0x00091E6C` | 106 | `quantized_runtime_tensor_slice` | GoMore-owned first-dimension descriptor view; retain trailing dimensions, derive the exact byte/halfword offset, and propagate int8 scale/flag state |
| `0x00091E6C..<0x00091EBA` | 78 | `quantized_runtime_tensor_construct` | claim slot, zero 0x14 bytes, bfi ndims into flags, copy dims with count product, set bufferless flag, NULL data |
| `0x00091EBA..<0x00091EDC` | 34 | `quantized_runtime_tensor_reshape` | bfi ndims into flag bits 0-1, copy dims; count NOT recomputed (quirk); stock's unused first argument dropped |
| `0x00093628..<0x000936F8` | 208 | `quantized_runtime_arena_allocate` | when used+count >= 0x6A4: collect live arena-backed buffers, qsort by offset (comparator 0x00058D4A), memmove down, rebuild watermark; return arena + old watermark, advance by count |
| `0x0009371C..<0x00093744` | 40 | `quantized_runtime_pool_slot_claim` | first free slot -> mark in use and return it; NULL when full |
| `0x00098EDC..<0x00098F80` | 164 | `quantized_runtime_float_add_execute` | out = in0 + in1 (count = in0 dims[1]*dims[2]); descriptor byte0 == 1: alpha at +4 == 0.0f -> ReLU, else leaky ReLU; return 0 |

## Disassembly corrections to the Ghidra rendering

1. **SSAT width.**  Ghidra renders the int8-add saturation as
   `SignedSaturate(iVar7,7)`; the instruction at `0x00036D3A` is
   `ssat r0, #8, r0` — full signed-8-bit [-128, 127] saturation.
2. **Rounding NaN sense.**  Ghidra renders the round-half-away helpers as
   `param_1 <= 0.0 ? -0.5 : +0.5`; the actual `vcmpe`+`ble` sequence gives
   NaN the -0.5 adjust as well.  The reconstruction uses
   `(value > 0.0f) ? +0.5f : -0.5f`, which matches the flags exactly.
3. **`0x00091C48` extent.**  The body is discontiguous (head at
   `0x00091C48` + shared tail at `0x000936FC`); the ledger/Ghidra end
   `0x0009371B` is the tail's end, not a data bug.
4. **`0x00085DC4` missing function.** Ghidra retained only
   `LAB_00085dc4+1`; the aligned descriptor constructor installs that Thumb
   address, control flow starts with a complete stack-frame prologue, and the
   next independent prologue begins at `0x00086BAC`. The ledger therefore
   carries the exact 3,560-byte body as a manual provenance supplement.
5. **`0x00085B9C` missing function.** Ghidra likewise omitted the function
   installed by `0x00074BE0` as Thumb entry `0x00085B9D`. Its return ends at
   `0x00085C98`, immediately before the two-word 0/88.0f literal pool, so the
   ledger carries an exact 252-byte manual supplement.

## Divergences from the stock binary (all deliberate)

1. **Explicit provider bindings.**  Stock calls the toolchain `fminf`,
   `fmaxf`, `floorf`, `expf`, and `qsort` directly; the reconstruction binds
   them through `quantized_runtime_providers` (production should bind the
   selected toolchain runtime, per the ledger's `use_toolchain_runtime`
   disposition).  Unbound mandatory providers fail explicitly
   (`QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT`, NULL, or 0 per return type).
2. **Other-family seams.**  The slice helper (`0x00091E02`) and scaled
   multiply (`0x00091CCC`) retain explicit bindings at the shared-runtime
   boundary even though both exact bodies are now owner-authorized in the GoMore
   reduction. Unbound cross-family dispatch still fails explicitly.
3. **Out-of-family pointer tokens.**  The four remaining absolute Thumb constants
   `0x00095B21`, `0x00036DCD`, `0x00076BDD` (GoMore candidate
   `FUN_00076BDC`), and `0x00030535`
   target bodies outside this family.  The
   reconstruction returns/stores integrator-bound tokens (0 when unbound)
   instead of fabricating addresses.  The seven locally reconstructed vectors
   (softmax, quantizer, float-add, float-dense, pooling, int8-add, signed-int8 convolution) return/store the reconstructed
   functions' real addresses. The former `0x000739A9` recurrent token now binds
   the reconstructed target adapter; the stock Thumb bit is an image ABI detail.
4. **Bad-argument handling.**  Stock dereferences every argument unchecked;
   the reconstruction validates and returns
   `QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT` (code 4 follows the sibling B210
   platform families' recovered bad-argument code; no error scheme was
   recovered inside this family itself, so the code is an introduced
   convention, not recovered behavior).
5. **Arena overflow guard.**  Stock writes past the 0x6A4-word arena when
   live data plus the request exceed capacity (unreachable in stock-sized
   AOT model graphs, which are compile-time sized).  The reconstruction
   returns NULL instead of corrupting memory.
6. **ndims guard.**  Stock callers always mask ndims with 3; values above 3
   would overwrite a descriptor's own flag/trailing words.  The
   reconstruction fails explicitly (NULL / no-op) for ndims outside 0..3.
7. **Recurrent-constructor overflow handling.**  Stock uses wrapping 32-bit
   arithmetic for its model-arena partitions.  The reconstruction checks
   allocation size and every target offset before allocating, returning false
   with the cursor unchanged instead of wrapping into an unrelated region.
8. **Explicit graph model input.**  Stock receives one absolute model pointer
   and advances it without a length.  The graph builder receives a word array,
   length, and target base token; it requires all 439 recovered words, rejects
   unaligned/overflowing target ranges, and reports the exact consumed count
   and end token.
9. **Failure-clean model ownership.**  Stock assumes its zeroing allocator's
   fatal exhaustion path and can return a partially initialized recurrent
   record.  The instance constructor requires paired allocate/release seams
   and releases the outer instance when recurrent-state allocation fails; its
   paired destroy releases state before the instance and clears the owner.
10. **Status returns introduced on stock-void functions.**
   `quantized_runtime_two_output_thirds_slice` (stock void) returns a status
   so the unbound slice seam can fail explicitly; the recurrent constructor
   returns a boolean so allocation/overflow failure is observable.
11. **Checked recurrent model and workspace.** The host-safe recurrent API
   resolves all three descriptor offsets through a caller-supplied model
   region, checks their complete spans, and requires an explicit workspace.
   The target adapter retains stock's absolute-address ABI and exact trailing
   input scratch convention. Fixed weights still must quantize zero to 128;
   otherwise the recovered `0xF000000E` status is returned.
12. **No libc memory dependency in the freestanding unit.**  The memmove/memset thunks and the
   descriptor-record packing use local loops and explicit little-endian
   byte assembly, matching the r1 freestanding convention (no `string.h`).
   The recurrent closure calls the attributable toolchain `floorf`, `fmaxf`,
   `expf`, and `tanhf` symbols directly, as stock did; qsort stays a bound
   provider (the comparator is a local static).
13. **qsort ordering.**  The stock comparator subtracts first words; live
   offsets are distinct, so any correct sort yields the recovered order.
14. **Checked convolution storage.** Stock temporarily pads input rows in
   place and, on overlap, moves the output pointer past the padded input.
   The checked API reads virtual zero-point padding without modifying input
   and requires caller-owned scratch for overlap. The target adapter retains
   the recovered arena layout while using the same bounded arithmetic core.

Preserved exactly: the rounding idiom including NaN sense and truncation,
the derivation bit-level range checks (`0xC77FFFFF`/`0x06FFFBFF`,
`0x437D0000`), the min/max shift formulas, the zero-point formula and
`1e-4f` range floor, SSAT #8 saturation, the pooling dispatch matrix
(including the silent no-op default and the 4x-unrolled window-2 loop that
overshoots column counts not divisible by four), the softmax max/cap/expf/
normalize passes (count from the *output* tensor's `dims[1]`), the ReLU /
leaky-ReLU selection (NaN alpha selects the leaky path), descriptor field
offsets and cursor arithmetic (including the udiv-by-zero -> 0 quirk), the
12-slot pool and 0x6A4-word arena with compaction trigger `used+count >=
0x6A4`, the release flag-bit rules, the signed loop bounds, and the
reshape-without-recount quirk.

"Docs describe intent, binary does less": the boundary doc's behavioral
census already matched the binary; nothing in the docs overclaims.  Two
recovered behaviors are effectively dead in stock-reachable states and are
documented as quirks rather than features: the softmax 88.0f cap (finite
inputs always produce differences <= 0, so only NaN reaches the cap) and
the derivation's fraction range check (rejects fractions near 0 or 1,
leaving the unadjusted range in place).

## Goodix in-place quantizer wrapper and configured veneer

The 116-byte Goodix entry at `0x00036B58` constructs the admitted default
quantizer descriptor `{0.0f, 1.0f}`, builds a `[1, rows, columns]` Float32
tensor over the caller buffer, and passes the same tensor as both input and
first output to `0x000293FC`. The raw stack layout proves that this alias is
intentional; the second output is an eight-byte local range scratch. Because
the quantizer reads Float32 elements forward while writing compact Int8 bytes
forward, the alias does not overwrite unread input. Mode values other than one
return exact stock word `0xF000000E`. The adjacent 22-byte entry at
`0x00095B04` only supplies two shape words from its owner configuration and
delegates to this wrapper.

`quantized_runtime_goodix_in_place_float_to_int8` and its configured veneer
replace the absolute configuration root and executor vector with typed shape,
runtime, buffer, and capacity inputs. Tests pin four exact output bytes,
in-place aliasing, the non-mode-one return word and no-write behavior,
configured-shape forwarding, short-buffer rejection, and null-shape
rejection. These two entries add 138 transparent Goodix bytes without stock
runtime or model content.

## NADT three-stage Float32 projection

The 138-byte entry at `0x0002F7DC` builds three 20-byte Float32 tensor
descriptors and invokes the three executor slots at operator-record offsets
`0x14`, `0x2C`, and `0x44`. Raw register flow pins the banks and shapes:
the first `{1, shape[0], shape[1]}` tensor uses the target buffer base, the
middle `{1, shape[2], shape[3]}` tensor uses base `+0x1F0`, and the final
`{1, shape[4], shape[5]}` tensor returns to the base. The caller supplies
exact shape `{1,15, 1,15, 8,15}`; the function copies the final 20-byte
descriptor back to the caller after all three stages.

`quantized_runtime_goodix_nadt_projection_execute` is a checked veneer over
the already admitted Float32 three-stage engine. It fixes the minimum bank
span to `0x1F0`, requires the no-padding/no-input-alias plan that preserves the
stock address, and bounds the complete 556-byte workspace. Tests pin every
stage descriptor, all three shapes and data addresses, final descriptor copy,
exact minimum extent, and padding rejection. No generated-model weight or
executor bytes are embedded.

## Host test mapping (`tests/test_reconstructed_quantized_runtime.c`)

- `test_round_helpers`: both rounder twins across sign/half boundaries;
  zero-point compute vectors (including the `1e-4f` degenerate-range clamp);
  unbound/NULL -> 0.
- `test_recurrent_executor`: range correction and zero point, min/max scan,
  centered-u8 matrix products, exact model-region/workspace bounds, fixed
  weight-zero rejection, both sigmoid gates, candidate tanh, and persistent
  state over two steps.
- `test_params_derive`: six float32-exact derivation vectors covering plain
  clamping, the max-shift branch (`{-1,1}`), the deep max-shift branch
  (`{-3,1}`), the min-shift branch (`{-0.1,10}`), positive min clamping,
  and negative max clamping; untouched outputs on bad arguments.
- `test_quantize_executor`: bit-exact quantized vectors derived from the
  recovered formula (including the adjusted range stored back), both
  saturation rails, type flag, the bad-argument matrix, and the Goodix
  in-place/default-range wrapper plus configured-shape veneer.
- `test_int8_add_executor`: mixed vectors with independent input/output
  quantization parameters (expected bytes simulated float32-exact from the
  recovered formula), both SSAT rails, output range write-back, bad
  arguments, unbound fmaxf.
- `test_i8_conv1d_executor`: all nine stock dispatch shapes (kernel 5 with
  1/4 channels, kernel 3 ordinary/depthwise, kernel 1 with 1/2/4/6 and
  scalar-remainder channel counts), nonzero zero-point padding, typed model
  ranges/scales/biases, Q31 output bytes, exact output-range propagation,
  rejected unsupported shape, and in-place overlap failure/success without
  and with bounded scratch.
- `test_float_dense_executor`: exact row-major dot/bias vectors, plain and
  leaky-ReLU modes, sigmoid and its 88.0f cap, short-model rejection, and
  overlapping input/output failure then success with caller scratch.
- `test_pooling_executor`: window-2 max over two signed rows, window-4 max,
  window-3 average (sums 0/5/-3/-5 -> 0/2/-1/-2), five unsupported
  descriptors leaving the output untouched while returning 0, bad
  arguments.
- `test_softmax_executor`: `{1,2,3}` within 1e-6 of the recovered
  computation, uniform input exactly 0.5, the NaN->88.0f cap quirk, bad
  arguments, unbound expf.
- `test_float_add_executor`: plain add, ReLU, leaky ReLU
  (`-0.5 * 0.1f` bit-exact), type 2 passthrough, bad arguments.
- `test_descriptor_constructors`: all twelve constructors/accessors,
  including cursor advancement, the udiv-by-zero quirk, bound vs unbound
  run tokens, the in-family executor vector identities, and the complete
  fixed graph's 439-word consumption, key record offsets, and bounds failures;
  the enclosing instance test pins both graphs, all four outer record cursors,
  recurrent state/offsets, exact 3,924-word consumption, teardown order, and
  nested-allocation rollback; the owner-wrapper test pins all nine written
  configuration fields, untouched reserved bytes, retained instance, and
  failure-visible configuration semantics.
- `test_tensor_pool`: slot claim exhaustion, construct fields, allocate
  watermark, create-fill contents, reshape quirk, release rules
  (buffer-backed vs bufferless vs foreign descriptor), release_many
  (NULL entries, negative count).
- `test_arena_compaction`: compaction move with contents preserved and
  watermark rebuild, both overflow-guard cases, unbound-qsort failure, bad
  arguments.
- `test_cross_family_seams`: thirds-slice argument forwarding (thirds 3 and
  2), unbound-seam failure with NULLed outputs, scaled-mul alpha/in-place
  forwarding with release and without, unbound/bad-argument failures.

## Integration state

The module is freestanding and carries host tests. Memory operations are
local; math resolves through explicit providers or the four attributable
libm symbols used by the recurrent closure.  The integrator wave owns:
wiring `test_reconstructed_quantized_runtime()` into `tests/test_openr1.c`,
adding the TU to the r1 Makefiles' `SOURCES`, flipping the 27 shared-runtime
and twenty-seven Goodix-extension ledger rows to
`clean_room_reimplementation_owner_authorized`, and re-pinning verifier
sites. The generated Goodix instance now stores the local recurrent target
adapter, while model words remain caller-supplied transparent build input.
Remaining graph executors and private model constants are still outside this
closure; no opaque model data or dispatch commands are exposed.
