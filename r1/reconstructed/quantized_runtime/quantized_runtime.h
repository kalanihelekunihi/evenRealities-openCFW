#ifndef OPENR1_RECONSTRUCTED_QUANTIZED_RUNTIME_H
#define OPENR1_RECONSTRUCTED_QUANTIZED_RUNTIME_H

/*
 * Provenance banner
 * -----------------
 * Families:       unknown_shared_quantized_neural_runtime_candidate
 *                 (shared AOT-compiled static-graph quantized-neural
 *                 runtime; attributed platform: Bravechip BCL603M
 *                 "ChipletRing" middleware serving both the GoMore sleep
 *                 classifier and the Goodix GH_SPO2/dlCom model graphs),
 *                 plus twenty-three Goodix-specific graph/instance/runtime
 *                 routines.
 * Stock image:    application image, load base 0x00027000, sha256
 *                 0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a.
 * Evidence:       r1/research/decompilation/application/decompiler-output.c
 *                 (all 26 shared and twenty-three Goodix-extension Ghidra bodies),
 *                 each cross-checked against fresh
 *                 Thumb disassembly of the byte-exact rebuilt image
 *                 r1/research/decompilation/rebuild/rebuilt-application.bin
 *                 (arm-none-eabi-objdump -D -b binary -m arm -M force-thumb).
 *                 Literal pools were read from the rebuilt image; callee
 *                 attribution used
 *                 r1/research/decompilation/application/functions.csv and
 *                 the ownership ledger (fminf/fmaxf/floorf/expf/qsort are
 *                 arm_toolchain_runtime; 0x00091CCC/0x00091E02 are
 *                 gomore_health_algorithm_candidate).
 * Status:         RECONSTRUCTED FROM DECOMPILATION EVIDENCE; NOT VENDOR
 *                 SOURCE.  Never present this file as Even Realities,
 *                 Bravechip, GoMore, or Goodix source.  No upstream source,
 *                 version, or license exists for this family; reduction is
 *                 owner-authorized per docs/SOURCE-ADMISSION.md
 *                 ("Owner-authorized full reduction (2026-08-14)").
 *
 * Reduced stock functions (application image extents, end-exclusive):
 *
 *   0x000290FE..<0x00029120   34   round-half-away-from-zero (twin A)
 *   0x00029120..<0x00029142   34   round-half-away-from-zero (twin B)
 *   0x000293FC..<0x000294B6   186  float -> signed-int8 quantizer executor
 *   0x00035E34..<0x00035F26   242  quantization min/max/scale derivation
 *   0x00036C7C..<0x00036D60   228  quantized int8-add executor (SSAT #8)
 *   0x00041816..<0x000419C8   434  pooling executor (max2/max4/avg3)
 *   0x0005A3D4..<0x0005A40E   58   two-output thirds-slice compute
 *   0x0005D244..<0x0005D2DC   152  float softmax executor (88.0f cap)
 *   0x00065680..<0x000656AA   42   scaled-mul call + conditional release
 *   0x0006FE20..<0x0006FE56   54   zero-point / requantization compute
 *   0x00074A9C..<0x00074AA0   4    executor-vector accessor -> 0x00095B21
 *   0x00074AAC..<0x00074B3E   146  24-byte descriptor constructor (conv-like)
 *   0x00074BD8..<0x00074BDC   4    executor-vector accessor -> 0x00036DCD
 *   0x00074BE0..<0x00074C42   98   24-byte descriptor record constructor
 *   0x00074C98..<0x00074CAE   22   16-byte operator descriptor init
 *   0x00074CDC..<0x00074CE0   4    executor-vector accessor -> softmax
 *   0x00074CE4..<0x00074D02   30   12-byte quantizer descriptor constructor
 *   0x00091C48..<0x00091C56 + 0x000936FC..<0x0009371C   46 (split body)
 *                                  tensor-descriptor release
 *   0x00091C56..<0x00091C80   42   release loop over a pointer array
 *   0x00091D9C..<0x00091DBE   34   tensor construct + arena allocate
 *   0x00091DBE..<0x00091E02   68   tensor construct + allocate + fill
 *   0x00091E6C..<0x00091EBA   78   0x14-byte tensor descriptor constructor
 *   0x00091EBA..<0x00091EDC   34   tensor flags/dims update (no recount)
 *   0x00093628..<0x000936F8   208  12-slot / 0x6A4-word arena compactor
 *   0x0009371C..<0x00093744   40   tensor-pool slot claim
 *   0x00098EDC..<0x00098F80   164  float add executor + ReLU / leaky ReLU
 *
 * Goodix GH_SPO2/dlCom graph extensions reduced in the same typed runtime:
 *   0x0002F624..<0x0002F658   52   generated-model owner wrapper
 *   0x00030800..<0x0003096C   364  generated quantized-layer block builder
 *   0x00036408..<0x00036574   364  recurrent dynamic-range adjustment
 *   0x00036590..<0x000366FC   364  exact recurrent range-adjust twin
 *   0x00036C26 + 0x00099014 tail 262  generated-model instance initializer
 *   0x0004387C..<0x00043B2A   686  fixed generated-model graph builder
 *   0x0005D01C..<0x0005D1AC   400  second generated-model graph builder
 *   0x000617F8..<0x00061C44   1100 complete second generated graph executor
 *   0x0006FDE0..<0x0006FE16   54   recurrent zero-point helper
 *   0x000739A8..<0x00073E08   1120 quantized recurrent executor
 *   0x0007400C..<0x0007405C   80   float min/max scan helper
 *   0x0007405C..<0x0007412C   208  unsigned-byte matrix/vector kernel
 *   0x000742E4..<0x0007487E   1426 complete generated graph executor
 *   0x00085DC4..<0x00086BAC   3560 signed-int8 grouped 1-D convolution
 *   0x000876C8..<0x00087A6C   932  complete quantized layer executor
 *   0x00074A20..<0x00074A98   120  recurrent-layer descriptor constructor
 *   0x00074B44..<0x00074BD4   144  aligned descriptor constructor
 *   0x00074C6C..<0x00074C8A   30   packed pooling descriptor constructor
 *   0x00074C90..<0x00074C94   4    external executor-vector accessor
 *   0x00074CB4..<0x00074CD6   34   cursor-pair int8-add descriptor
 *
 * The extents above use each body's real end address; the ownership ledger
 * records the same 26 entries with end-exclusive extents (the 0x00091C48
 * entry is discontiguous: its 14-byte head tail-branches into the shared
 * 32-byte release tail at 0x000936FC, which is why the ledger lists its end
 * as 0x0009371B).
 *
 * Correlation doc: docs/correlation/QUANTIZED-RUNTIME-REDUCTION-CORRELATION.md.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* The stock family has no recovered error scheme: every executor returns 0
 * and unsupported descriptors are silent no-ops.  NULL/invalid arguments
 * faulted in stock; the reconstruction instead fails explicitly with
 * QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT (code 4 follows the sibling B210
 * platform families' recovered bad-argument code; it is introduced by the
 * reconstruction, not recovered). */
enum {
    QUANTIZED_RUNTIME_STATUS_OK = 0,           /* recovered */
    QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT = 4  /* introduced (see above) */
};

/* Recovered executor-facing tensor record (20 bytes on target):
 * word dims at +0x04/+0x08/+0x0C, data pointer at +0x10, flag word at
 * +0x00 (the float->int8 quantizer stores 1 there). */
typedef struct {
    uint32_t type_flag; /* +0x00 */
    uint32_t dims[3];   /* +0x04, +0x08, +0x0C */
    void *data;         /* +0x10 */
} quantized_runtime_exec_tensor;

/* Recovered 0x14-byte pool tensor descriptor: arena pointer at +0x00,
 * element count at +0x04, three uint16 dims at +0x08..+0x0D, flag byte at
 * +0x0E (bits 0-1 dimension count, bit 2 "no arena buffer", bit 3
 * slice/view), trailing word at +0x10. */
typedef struct {
    uint32_t *data;     /* +0x00 */
    uint32_t count;     /* +0x04 */
    uint16_t dims[3];   /* +0x08, +0x0A, +0x0C */
    uint8_t flags;      /* +0x0E */
    uint8_t reserved_0f;/* +0x0F */
    uint32_t reserved_10; /* +0x10 */
} quantized_runtime_tensor;

#define QUANTIZED_RUNTIME_TENSOR_SLOTS 12u
#define QUANTIZED_RUNTIME_ARENA_WORDS 0x6A4u /* 1,700 words */
#define QUANTIZED_RUNTIME_TENSOR_FLAG_BUFFERLESS 0x04u
#define QUANTIZED_RUNTIME_TENSOR_FLAG_VIEW 0x08u
#define QUANTIZED_RUNTIME_GOODIX_GRAPH_BYTES 0x160u
#define QUANTIZED_RUNTIME_GOODIX_GRAPH_MODEL_WORDS 439u
#define QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS 3924u
#define QUANTIZED_RUNTIME_RECURRENT_RANGE_ERROR UINT32_C(0xF000000E)

/* Recovered shared tensor pool state root: 12 descriptors at 0x14 stride,
 * 12 in-use bytes, compacting word arena, used-word watermark. */
typedef struct {
    quantized_runtime_tensor slots[QUANTIZED_RUNTIME_TENSOR_SLOTS]; /* +0x000 */
    uint8_t in_use[QUANTIZED_RUNTIME_TENSOR_SLOTS];                 /* +0x0F0 */
    uint32_t arena[QUANTIZED_RUNTIME_ARENA_WORDS];                  /* +0x0FC */
    uint32_t used_words;                                            /* +0x1B8C */
} quantized_runtime_pool;

/* Provider bindings.  Every dependency the stock code called directly is an
 * explicit, bindable seam; an unbound mandatory provider fails explicitly
 * instead of faulting. */
typedef float (*quantized_runtime_f32_unary_fn)(float value);
typedef float (*quantized_runtime_f32_binary_fn)(float left, float right);
typedef int (*quantized_runtime_compare_fn)(const void *left,
                                            const void *right);
typedef void (*quantized_runtime_qsort_fn)(void *base, size_t count,
                                           size_t size,
                                           quantized_runtime_compare_fn compare);

/* GoMore-candidate family seams (that family is separately blocked; do not
 * reconstruct it here): the stock thirds-slice helper 0x00091E02 and the
 * stock scaled-multiply helper 0x00091CCC. */
typedef quantized_runtime_tensor *(*quantized_runtime_slice_fn)(
    quantized_runtime_pool *pool, const quantized_runtime_tensor *input,
    uint32_t begin, uint32_t end);
typedef uint32_t (*quantized_runtime_scaled_mul_fn)(
    float alpha, quantized_runtime_pool *pool, quantized_runtime_tensor *tensor,
    uint32_t in_place);

typedef struct {
    /* arm_toolchain_runtime: fminf, fmaxf, floorf, expf, qsort. */
    quantized_runtime_f32_binary_fn fminf_fn;
    quantized_runtime_f32_binary_fn fmaxf_fn;
    quantized_runtime_f32_unary_fn floorf_fn;
    quantized_runtime_f32_unary_fn expf_fn;
    quantized_runtime_qsort_fn qsort_fn;
    /* gomore_health_algorithm_candidate seams. */
    quantized_runtime_slice_fn slice_fn;         /* stock 0x00091E02 */
    quantized_runtime_scaled_mul_fn scaled_mul_fn; /* stock 0x00091CCC */
    /* Out-of-family executor code-pointer tokens.  Stock stored/returned the
     * absolute Thumb addresses listed beside each field.  The targets live
     * outside this recovered family, so the integrator binds linked addresses
     * (or test tokens) here.  Zero means unbound: accessors return 0 and
     * constructors store 0. */
    uintptr_t vector_95b20;
    uintptr_t vector_36dcc;
    uintptr_t run_76bdc;
    uintptr_t run_85b9c;
    uintptr_t vector_30534; /* stock 0x00030535 */
} quantized_runtime_providers;

typedef struct {
    quantized_runtime_providers providers;
} quantized_runtime;

typedef void *(*quantized_runtime_allocate_fn)(void *context, size_t bytes);
typedef void (*quantized_runtime_release_fn)(void *context, void *allocation);

/* Native-pointer representation of the recovered recurrent descriptor.
 * Its target ABI is exactly six words / 24 bytes; wider hosts retain the
 * state and executor pointers without truncation. */
typedef struct {
    uint32_t units;                  /* target +0x00 */
    float *state;                    /* target +0x04 */
    uint32_t input_weights_offset;   /* target +0x08 */
    uint32_t recurrent_weights_offset; /* target +0x0C */
    uint32_t bias_offset;            /* target +0x10 */
    uintptr_t execute;               /* target +0x14 */
} quantized_runtime_recurrent_descriptor;

/* Transparent view of model bytes whose target address is recorded in the
 * generated descriptors.  The checked host executor resolves all three
 * recurrent sections through this view instead of dereferencing stock-style
 * absolute addresses. */
typedef struct {
    const uint8_t *bytes;
    size_t size;
    uint32_t target_address;
} quantized_runtime_model_region;

/* Transparent form of the 24-byte descriptor built at 0x00074B44 for the
 * signed-int8 executor at 0x00085DC4.  The target record appends two model
 * addresses and an executor word; the checked API resolves those addresses
 * into the typed model view below instead. */
typedef struct {
    uint8_t kernel_width;    /* target +0x00: recovered modes 1, 3, or 5 */
    uint8_t kernel_height;   /* target +0x01: recovered graphs require 1 */
    uint8_t left_padding;    /* target +0x02 */
    uint8_t right_padding;   /* target +0x03 */
    uint8_t input_channels;  /* target +0x04 */
    uint8_t output_channels; /* target +0x05 */
    uint8_t groups;          /* target +0x06 */
    uint8_t flags;           /* target +0x07; retained, not read by stock */
    float context;           /* target +0x08; retained, not read by stock */
} quantized_runtime_i8_conv1d_descriptor;

/* Decoded model-arena schema consumed by 0x00085DC4.  weights are ordered
 * [output][input-within-group][kernel].  channel_scales and biases each have
 * output_channels entries.  weight_min/max derive the global quantization
 * step, bias_min/max convert the stored Q23 biases, and output_min/max seed
 * the recovered mode-3 dynamic-range correction. */
typedef struct {
    const int8_t *weights;
    size_t weight_count;
    float weight_min;
    float weight_max;
    const float *channel_scales;
    size_t channel_scale_count;
    const int32_t *biases;
    size_t bias_count;
    float bias_min;
    float bias_max;
    float output_min;
    float output_max;
} quantized_runtime_i8_conv1d_model;

/* Explicit buffer extents for the checked executor.  workspace is optional
 * unless output data overlaps input data; in that case it must hold the
 * complete output.  The input is never modified by the checked form. */
typedef struct {
    quantized_runtime_exec_tensor *input;
    quantized_runtime_exec_tensor *input_range;
    quantized_runtime_exec_tensor *output;
    quantized_runtime_exec_tensor *output_range;
    size_t input_capacity;
    size_t input_range_capacity;
    size_t output_capacity;
    size_t output_range_capacity;
    void *workspace;
    size_t workspace_size;
} quantized_runtime_i8_conv1d_io;

typedef uint32_t (*quantized_runtime_stage_execute_fn)(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs);

typedef struct {
    const void *descriptor;
    quantized_runtime_stage_execute_fn execute;
} quantized_runtime_stage;

typedef struct {
    quantized_runtime_stage stages[5];
} quantized_runtime_five_stage_plan;

typedef struct {
    quantized_runtime_stage stages[3];
    uint8_t row_padding;
    uint8_t column_padding;
    bool middle_uses_input_storage;
} quantized_runtime_three_stage_plan;

/* Target-ABI graph descriptor emitted by Goodix builder 0x0004387C.  Its
 * records intentionally remain a byte schema: executor pointers and model
 * arena references are 32-bit target tokens, never native host pointers. */
typedef struct {
    uint8_t bytes[QUANTIZED_RUNTIME_GOODIX_GRAPH_BYTES];
} quantized_runtime_goodix_graph;

/* Typed representation of stock's 0x344-byte generated-model instance.
 * Target offsets are asserted in the implementation; native-pointer hosts
 * widen only the three live pointer/vector fields. */
typedef struct {
    uint32_t reserved_000;
    quantized_runtime_goodix_graph graph_a;
    quantized_runtime_goodix_graph graph_b;
    uint8_t descriptor_a[0x18];
    uint8_t descriptor_b[0x18];
    uintptr_t softmax_execute;
    uintptr_t vector_36dcc;
    quantized_runtime_recurrent_descriptor recurrent;
    uint8_t descriptor_c[0x18];
    uint8_t descriptor_d[0x18];
} quantized_runtime_goodix_model_instance;

/* Owner record configured by stock wrapper 0x0002F624.  Bytes 0..7 and
 * 0x0E..0x0F are deliberately retained as reserved because stock left them
 * untouched. */
typedef struct {
    uint8_t reserved_00[8];
    uint8_t primary_enabled;
    uint8_t primary_stride;
    uint8_t primary_window;
    uint8_t secondary_enabled;
    uint8_t secondary_stride;
    uint8_t secondary_window;
    uint8_t reserved_0e[2];
    uint32_t input_channels;
    uint32_t graph_count;
    uint32_t output_channels;
    quantized_runtime_goodix_model_instance *instance;
} quantized_runtime_goodix_model_owner;

/* Zeroes the context and binds providers.  NULL providers leave every
 * provider-dependent path failing explicitly. */
void quantized_runtime_initialize(quantized_runtime *rt,
                                  const quantized_runtime_providers *providers);

/* Zeroes the shared pool (stock: zero-initialized BSS). */
void quantized_runtime_pool_initialize(quantized_runtime_pool *pool);

/* 0x000290FE / 0x00029120: identical 34-byte round-half-away-from-zero
 * helpers (two link-time instantiations; 0x290FE is the one the int8-add
 * and zero-point paths call).  vcvt.s32.f32 truncates; values <= 0 or NaN
 * take the -0.5 adjust. */
int32_t quantized_runtime_round_half_away_from_zero_290fe(float value);
int32_t quantized_runtime_round_half_away_from_zero_29120(float value);

/* 0x0006FE20: round((value - min) * (255.0f / fmaxf(1e-4f, max - min))).
 * Returns 0 when the fmaxf provider is unbound (stock always linked libm). */
int32_t quantized_runtime_zero_point_compute(const quantized_runtime *rt,
                                             float value, float min,
                                             float max);

/* 0x00035E34: derive asymmetric-int8 quantization parameters.  Clamps
 * min <= 0 <= max, range to at least 1e-4f, scale = 255/range, then (when
 * min < 0) shifts min or max so the zero point lands on an integer.
 * No-op on NULL outputs or unbound math providers (stock was void). */
void quantized_runtime_quantization_params_derive(
    const quantized_runtime *rt, float min_input, float max_input,
    float *out_min, float *out_max, float *out_step, float *out_scale);

/* 0x000293FC: float -> signed-int8 quantizer executor.  descriptor points at
 * the recovered {min, max} float pair; inputs[0] is the float source tensor
 * (element count = product of its three dims); outputs[0] receives the int8
 * data plus type flag 1; outputs[1]->data receives the derived {min, max}. */
uint32_t quantized_runtime_float_to_int8_quantize(
    const quantized_runtime *rt, const float *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs);

/* 0x00036C7C: quantized int8-add executor.  descriptor +0x04/+0x08 hold the
 * output {min, max} floats; inputs = {data0, qparams0, data1, qparams1};
 * outputs = {data, qparams}.  Dequantizes both operands, adds, requantizes
 * in float with round-half-away-from-zero, SSAT #8 saturates, and writes the
 * output range into outputs[1]->data. */
uint32_t quantized_runtime_int8_add_execute(
    const quantized_runtime *rt, const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs);

/* 0x00041816: pooling executor.  descriptor byte0 = type, byte1 = window,
 * byte2 = stride: type 0/window 2 = max pool (4x unrolled), type 0/window 4
 * = max pool, type 1/window 3 = average pool with sign-aware half rounding.
 * Anything else is a silent no-op returning 0 (recovered). */
uint32_t quantized_runtime_pooling_execute(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs);

/* Exact output scratch required when the checked signed-int8 convolution's
 * input and output buffers overlap.  Zero reports an invalid/overflowing
 * shape as well as a legitimate zero-sized shape (which the executor
 * rejects). */
size_t quantized_runtime_i8_conv1d_workspace_bytes(
    const quantized_runtime_i8_conv1d_descriptor *descriptor,
    uint32_t output_width);

/* 0x00085DC4: checked signed-int8 grouped 1-D convolution.  The supported
 * stock modes are kernel 5 with groups=1 and 1/4 input channels, kernel 3
 * with groups=1 or depthwise groups, and kernel 1 with groups=1.  Inputs and
 * outputs use channel-major [1, channels, width] tensors; range tensors hold
 * two floats.  Arithmetic preserves the stock modulo-2^32 accumulators and
 * Q31 round/center clamp. */
uint32_t quantized_runtime_i8_conv1d_execute(
    const quantized_runtime_i8_conv1d_descriptor *descriptor,
    const quantized_runtime_i8_conv1d_model *model,
    quantized_runtime_i8_conv1d_io *io);

/* Target-ABI adapter for generated graph records.  It decodes the two model
 * pointers in the recovered 24-byte descriptor and retains stock's assumed
 * backing-storage contract.  Host integrations should use the checked form. */
uint32_t quantized_runtime_i8_conv1d_execute_target(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs);

/* 0x0005D244: float softmax executor (descriptor is accepted but never
 * read -- recovered).  Element count comes from outputs[0]->dims[1].
 * Subtracts the max, clamps differences whose raw bits reach 0x42B00000
 * (>= 88.0f, reachable only for NaN inputs) to 88.0f, applies the bound
 * expf, and normalizes by the sum. */
uint32_t quantized_runtime_float_softmax_execute(
    const quantized_runtime *rt, const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs);

/* 0x00098EDC: float add executor.  outputs[0] = inputs[0] + inputs[1],
 * element count = inputs[0]->dims[1] * inputs[0]->dims[2].  descriptor
 * byte0 == 1 applies an activation: the float at descriptor +0x04 == 0.0f
 * selects ReLU, otherwise leaky ReLU with that alpha. */
uint32_t quantized_runtime_float_add_execute(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs);

/* 0x0005A3D4: two-output thirds-slice compute.  third = input_a->dims[0]/3;
 * outputs[0] = slice(pool, a, third*index, third*(index+1)), outputs[1] the
 * same for input_b.  The slice itself is the bound GoMore-candidate seam
 * (stock 0x00091E02).  Stock returned void; the reconstruction returns a
 * status so the unbound seam fails explicitly (outputs become NULL). */
uint32_t quantized_runtime_two_output_thirds_slice(
    const quantized_runtime *rt, quantized_runtime_pool *pool,
    const quantized_runtime_tensor *input_a,
    const quantized_runtime_tensor *input_b,
    quantized_runtime_tensor **outputs, uint32_t index);

/* 0x00065680: call the bound scaled-multiply seam (stock 0x00091CCC) with
 * alpha = *alpha_source and in_place = 1, then release the tensor back to
 * the pool when release != 0.  Returns the seam's result, or
 * QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT when unbound. */
uint32_t quantized_runtime_scaled_mul_conditional_release(
    const quantized_runtime *rt, const float *alpha_source,
    quantized_runtime_pool *pool, quantized_runtime_tensor *tensor,
    uint32_t release);

/* 0x00074A9C / 0x00074BD8: 4-byte executor-vector accessors.  Stock
 * returned the absolute Thumb pointers 0x00095B21 / 0x00036DCD into bodies
 * outside this family; the reconstruction returns the bound token (0 when
 * unbound). */
uintptr_t quantized_runtime_executor_vector_95b20(const quantized_runtime *rt);
uintptr_t quantized_runtime_executor_vector_36dcc(const quantized_runtime *rt);

/* 0x00074C90: Goodix graph executor-vector accessor.  Stock returned the
 * absolute Thumb pointer 0x00030535 into a body outside the reduced family;
 * the reconstruction returns the explicit bound token (0 when unbound). */
uintptr_t quantized_runtime_executor_vector_30534(const quantized_runtime *rt);

/* 0x00074CDC: returns the executor vector for the (in-family) float softmax
 * executor.  Stock returned the absolute Thumb pointer 0x0005D245; the
 * reconstruction returns the address of the reconstructed executor. */
uintptr_t quantized_runtime_softmax_executor_vector(void);

/* 0x00074AAC: 24-byte descriptor constructor.  Writes eight packed
 * parameter bytes, the context float at +0x08, the weight-arena cursor at
 * +0x0C, the bias offset *cursor + byte5*byte0*(byte4/byte6)*4 at +0x10,
 * and the bound run token (stock 0x00076BDD, GoMore candidate) at +0x14;
 * advances the cursor by byte5*4 + byte5*byte0*(byte4/byte6)*4.  The
 * division is the recovered unsigned udiv; byte6 == 0 yields 0 (ARM udiv
 * returns 0 on divide-by-zero -- recovered quirk). */
void quantized_runtime_descriptor_construct(
    const quantized_runtime *rt, void *destination, uint8_t byte0,
    uint8_t byte1, uint8_t byte2, uint8_t byte3, uint8_t byte4,
    uint8_t byte5, uint8_t byte6, uint32_t reserved, uint8_t byte7,
    uint32_t *arena_cursor, float context);

/* 0x00074BE0: 24-byte descriptor record constructor.  +0x00 = dim_b word,
 * +0x04/+0x05 = flag bytes, +0x08 = context float, +0x0C = *cursor,
 * +0x10 = *cursor + dim_a*dim_b*4, +0x14 = bound run token (stock
 * 0x00085B9D); advances the cursor by dim_b*4 + dim_a*dim_b*4. */
void quantized_runtime_descriptor_record_construct(
    const quantized_runtime *rt, void *destination, uint32_t dim_a,
    uint32_t dim_b, uint8_t flag_a, uint8_t flag_b, uint32_t *arena_cursor,
    float context);

/* 0x00036408: adjust an observed float range so asymmetric 8-bit
 * quantization represents zero exactly.  Returns -1 for a non-positive
 * range, 0 when unchanged, and 1/2/3 for the recovered min/max/both
 * adjustment paths. */
int32_t quantized_runtime_recurrent_range_adjust(float *min_value,
                                                 float *max_value,
                                                 uint32_t mode);

/* 0x0006FDE0: round((value-min) * 255/max(1e-4,max-min)). */
int32_t quantized_runtime_recurrent_zero_point(float value, float min_value,
                                               float max_value);

/* 0x0007400C: scan count float values and return their maximum/minimum.
 * Invalid or empty input is a checked no-op (stock unconditionally read the
 * first element). */
void quantized_runtime_float_min_max(const float *values, uint16_t count,
                                     float *max_value, float *min_value);

/* 0x0007405C: row-major unsigned-byte matrix/vector kernel.  Each byte is
 * centered by its own zero point before multiplication. */
void quantized_runtime_u8_matrix_vector(const uint8_t *vector,
                                        const uint8_t *matrix,
                                        int32_t *output, uint32_t columns,
                                        uint32_t rows,
                                        int32_t vector_zero_point,
                                        int32_t matrix_zero_point);

/* Scratch required by the checked recurrent executor.  Zero means the
 * dimensions overflow size_t. */
size_t quantized_runtime_recurrent_workspace_bytes(uint32_t units,
                                                   uint32_t input_dimension);

/* 0x000739A8: checked form of the generated Goodix recurrent executor.
 * Model offsets are resolved through model_region and all temporary storage
 * is caller-owned.  Returns 0, 0xF000000E when either fixed weight zero point
 * is not 128 (stock behavior), or BAD_ARGUMENT for invalid/bounded inputs. */
uint32_t quantized_runtime_recurrent_execute(
    const quantized_runtime_recurrent_descriptor *descriptor,
    const quantized_runtime_model_region *model_region,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs, void *workspace,
    size_t workspace_size);

/* Target ABI adapter used by generated graph records.  Like stock, it uses
 * descriptor absolute model addresses and the scratch bytes immediately
 * following the input float vector.  Host code should call the checked form
 * above. */
uint32_t quantized_runtime_recurrent_execute_target(
    const quantized_runtime_recurrent_descriptor *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs);

/* 0x0002951A / 0x00035D6E: fixed five-stage float pipelines used by the
 * generated Goodix executor.  The two variants differ only in their first
 * tensor width and recovered scratch-bank offsets. */
bool quantized_runtime_goodix_five_stage_32_execute(
    const quantized_runtime_five_stage_plan *plan,
    quantized_runtime_exec_tensor *input,
    quantized_runtime_exec_tensor *output, void *workspace,
    size_t workspace_size);
bool quantized_runtime_goodix_five_stage_27_execute(
    const quantized_runtime_five_stage_plan *plan,
    quantized_runtime_exec_tensor *input,
    quantized_runtime_exec_tensor *output, void *workspace,
    size_t workspace_size);

/* 0x00042024 / 0x0003F7F8: shape-driven three-stage pipelines over u8 and
 * float tensors. The caller supplies six {rows,columns} bytes and a minimum
 * bank span; all operator callbacks and storage are explicit. */
bool quantized_runtime_goodix_u8_three_stage_execute(
    const quantized_runtime_three_stage_plan *plan,
    quantized_runtime_exec_tensor *const inputs[2],
    quantized_runtime_exec_tensor *const outputs[2],
    const uint8_t shape[6], size_t minimum_span, void *workspace,
    size_t workspace_size);
bool quantized_runtime_goodix_f32_three_stage_execute(
    const quantized_runtime_three_stage_plan *plan,
    quantized_runtime_exec_tensor *input,
    quantized_runtime_exec_tensor *output, const uint8_t shape[6],
    size_t minimum_span, void *workspace, size_t workspace_size);

#define QUANTIZED_RUNTIME_GOODIX_LAYER_STAGE_COUNT 8u
#define QUANTIZED_RUNTIME_GOODIX_LAYER_SHAPE_BYTES 14u
#define QUANTIZED_RUNTIME_GOODIX_LAYER_BLOCK_BYTES 176u
#define QUANTIZED_RUNTIME_GOODIX_LAYER_BLOCK_SHAPE_BYTES 7u
#define QUANTIZED_RUNTIME_GOODIX_SECOND_GRAPH_BYTES 984u
#define QUANTIZED_RUNTIME_GOODIX_SECOND_GRAPH_MODEL_WORDS 1567u

typedef struct {
    uint8_t bytes[QUANTIZED_RUNTIME_GOODIX_LAYER_BLOCK_BYTES];
} quantized_runtime_goodix_layer_block;

typedef struct {
    uint8_t bytes[QUANTIZED_RUNTIME_GOODIX_SECOND_GRAPH_BYTES];
} quantized_runtime_goodix_second_graph;

typedef struct {
    bool optional_preprocess;
    float output_min;
    float output_max;
    quantized_runtime_f32_unary_fn expf_fn;
    quantized_runtime_stage stages[QUANTIZED_RUNTIME_GOODIX_LAYER_STAGE_COUNT];
} quantized_runtime_goodix_layer_plan;

/* 0x000876C8: generated quantized-layer executor used five times by the
 * dormant 0x617F8 graph.  All eight possible operators, the temporary
 * allocation, and the workspace arena are explicit; the fourteen recovered
 * shape bytes retain the stock descriptor topology. */
bool quantized_runtime_goodix_layer_execute(
    const quantized_runtime_goodix_layer_plan *plan,
    quantized_runtime_exec_tensor *const inputs[2],
    quantized_runtime_exec_tensor *const outputs[2],
    const uint8_t shape[QUANTIZED_RUNTIME_GOODIX_LAYER_SHAPE_BYTES],
    uint8_t *workspace, size_t workspace_size,
    uint8_t *temporary, size_t temporary_size);

/* 0x00030800: construct the descriptor block consumed by 0x617F8/0x876C8.
 * Model words and their target base address are separate so host tests never
 * dereference stock absolute addresses. */
bool quantized_runtime_goodix_layer_block_build(
    const quantized_runtime *rt,
    quantized_runtime_goodix_layer_block *block,
    const uint32_t *model_words, size_t model_word_count,
    uint32_t model_base_address,
    const uint8_t shape[QUANTIZED_RUNTIME_GOODIX_LAYER_BLOCK_SHAPE_BYTES],
    size_t *consumed_words, uint32_t *model_end_address);

/* 0x0005D01C: build the complete graph consumed by 0x617F8 from 1,567
 * explicit model words.  release_context_pair_vector replaces stock's
 * embedded 0x74AA4 result. */
bool quantized_runtime_goodix_second_graph_build(
    const quantized_runtime *rt,
    quantized_runtime_goodix_second_graph *graph,
    const uint32_t *model_words, size_t model_word_count,
    uint32_t model_base_address, uintptr_t release_context_pair_vector,
    size_t *consumed_words, uint32_t *model_end_address);

#define QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_STAGE_COUNT 6u
#define QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_LAYER_COUNT 5u
#define QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_WORKSPACE_BYTES 7740u
#define QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_TEMPORARY_BYTES 4320u
#define QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_OUTPUT_BYTES 960u

typedef uint32_t (*quantized_runtime_multi_stage_execute_fn)(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *input_pairs,
    quantized_runtime_exec_tensor *const *outputs,
    uint32_t input_count);

typedef struct {
    const void *descriptor;
    quantized_runtime_multi_stage_execute_fn execute;
} quantized_runtime_multi_stage;

typedef struct {
    quantized_runtime_stage stages[
        QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_STAGE_COUNT];
    quantized_runtime_multi_stage merge_four;
    quantized_runtime_goodix_layer_plan layers[
        QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_LAYER_COUNT];
} quantized_runtime_goodix_second_executor_plan;

typedef struct {
    uint8_t *workspace;
    size_t workspace_size;
    uint8_t *temporary;
    size_t temporary_size;
    uint8_t *output;
    size_t output_capacity;
} quantized_runtime_goodix_second_executor_io;

/* 0x000617F8: complete second generated Goodix graph executor.  The five
 * embedded 0x876C8 plans, six direct stages, four-branch merge, former heap
 * temporary, arena, and destination are all explicit. */
bool quantized_runtime_goodix_second_executor_execute(
    const quantized_runtime_goodix_second_executor_plan *plan,
    const quantized_runtime_goodix_second_executor_io *io,
    size_t *output_bytes);

#define QUANTIZED_RUNTIME_GOODIX_EXECUTOR_STAGE_COUNT 18u

typedef struct {
    uint32_t mode; /* recovered variants 0, 1, or 2 */
    quantized_runtime_stage stages[
        QUANTIZED_RUNTIME_GOODIX_EXECUTOR_STAGE_COUNT];
    quantized_runtime_three_stage_plan quantized_49;
    quantized_runtime_three_stage_plan quantized_24;
    quantized_runtime_five_stage_plan five_stage_27;
    quantized_runtime_five_stage_plan five_stage_32;
    quantized_runtime_three_stage_plan float_12;
    uint32_t head_width_mode0;
    uint32_t head_width_other;
    uint32_t tail_widths[4];
} quantized_runtime_goodix_executor_plan;

typedef struct {
    uint8_t *workspace;
    size_t workspace_size;
    const uint8_t *tail_input;
    size_t tail_input_size;
    uint8_t *output;
    size_t output_capacity;
} quantized_runtime_goodix_executor_io;

/* 0x000742E4: complete generated Goodix graph executor.  The stock object
 * embedded target pointers throughout a 0x23C+ byte descriptor table; this
 * typed plan makes all eighteen stages and five nested pipelines explicit.
 * Workspace offsets, mode branches, tensor shapes, and final output length
 * retain the recovered topology. */
bool quantized_runtime_goodix_executor_execute(
    const quantized_runtime_goodix_executor_plan *plan,
    const quantized_runtime_goodix_executor_io *io,
    size_t *output_bytes);

/* 0x00074A20: Goodix quantized recurrent-layer descriptor.  Allocates and
 * clears units floats of state, then partitions the model arena into aligned
 * 3-byte input/recurrent matrices and a `(units * 10 + 6) * 4` tail.  Its
 * executor points at the reconstructed target adapter above.  Allocation or
 * checked-arithmetic failure leaves the cursor unchanged and returns false. */
bool quantized_runtime_recurrent_layer_descriptor_construct(
    const quantized_runtime *rt,
    quantized_runtime_recurrent_descriptor *descriptor, uint32_t units,
    uint32_t input_dimension, uint32_t *arena_cursor,
    quantized_runtime_allocate_fn allocate, void *allocate_context);

/* 0x00074B44: Goodix-specific 24-byte aligned descriptor constructor.  The
 * packed byte ABI matches quantized_runtime_descriptor_construct, but its
 * weight span is rounded up to four bytes; +0x10 skips an additional
 * byte5*4 + 8 bytes and the cursor advances past byte5*8 + 24 bytes.  +0x14
 * receives the bound executor token (stock 0x00085DC5).  byte6 == 0 retains
 * the recovered ARM udiv result of zero. */
void quantized_runtime_aligned_descriptor_construct(
    const quantized_runtime *rt, void *destination, uint8_t byte0,
    uint8_t byte1, uint8_t byte2, uint8_t byte3, uint8_t byte4,
    uint8_t byte5, uint8_t byte6, uint32_t reserved, uint8_t byte7,
    uint32_t *arena_cursor, float context);

/* 0x00074C6C: Goodix pooling descriptor constructor.  Packs four low bytes
 * into +0x00 and stores the address of the reconstructed pooling executor at
 * +0x04 (stock stored the absolute Thumb pointer 0x00041817). */
void quantized_runtime_packed_pool_descriptor_initialize(
    void *destination, uint32_t byte0, uint32_t byte1, uint32_t byte2,
    uint32_t byte3);

/* 0x00074CB4: Goodix cursor-pair add descriptor.  Reads two words from the
 * cursor, advances it by two, and emits {0, word0, word1, int8-add-vector}.
 * Stock stored absolute Thumb pointer 0x00036C7D; the reconstruction binds
 * the local int8-add executor directly. */
void quantized_runtime_cursor_pair_add_descriptor_construct(
    void *destination, const uint32_t **cursor);

/* 0x0004387C: build the fixed Goodix GH_SPO2/dlCom quantized graph from a
 * caller-supplied transparent model-word array.  model_base_address is the
 * target address represented by model_words[0]; it replaces stock's implicit
 * absolute pointer.  Exactly 439 words are consumed. */
bool quantized_runtime_goodix_graph_build(
    const quantized_runtime *rt, quantized_runtime_goodix_graph *graph,
    const uint32_t *model_words, size_t model_word_count,
    uint32_t model_base_address, size_t *consumed_words,
    uint32_t *model_end_address);

/* 0x00036C26 head + 0x00099014 tail: allocate and build the complete Goodix
 * generated-model instance from 3,924 explicit model words.  All allocation
 * ownership is visible; failure releases both recurrent state and instance.
 * The paired destroy API expresses the already reconstructed 0x00036C60
 * two-release contract for the typed instance. */
bool quantized_runtime_goodix_model_instance_create(
    const quantized_runtime *rt,
    quantized_runtime_goodix_model_instance **out_instance,
    const uint32_t *model_words, size_t model_word_count,
    uint32_t model_base_address, quantized_runtime_allocate_fn allocate,
    quantized_runtime_release_fn release, void *allocator_context,
    size_t *consumed_words, uint32_t *model_end_address);
void quantized_runtime_goodix_model_instance_destroy(
    quantized_runtime_goodix_model_instance **instance,
    quantized_runtime_release_fn release, void *release_context);

/* 0x0002F624: install recovered {1,1,125}/{1,1,125} configuration and
 * {1,2,1} dimensions, then create and retain the generated-model instance.
 * The stock helper's incidental two-word return was ignored by its sole
 * caller; success is explicit here. */
bool quantized_runtime_goodix_model_owner_initialize(
    const quantized_runtime *rt,
    quantized_runtime_goodix_model_owner *owner,
    const uint32_t *model_words, size_t model_word_count,
    uint32_t model_base_address, quantized_runtime_allocate_fn allocate,
    quantized_runtime_release_fn release, void *allocator_context);
void quantized_runtime_goodix_model_owner_destroy(
    quantized_runtime_goodix_model_owner *owner,
    quantized_runtime_release_fn release, void *release_context);

/* 0x00074C98: 16-byte operator descriptor init: {type & 0xFF, argument
 * float bits, 0, executor vector}.  Stock installed the in-family float-add
 * executor (0x00098EDD); the reconstruction stores the reconstructed
 * executor's address. */
void quantized_runtime_operator_descriptor_init(uintptr_t *descriptor,
                                                uint32_t type, float argument);

/* 0x00074CE4: 12-byte quantizer descriptor constructor.  With a cursor it
 * reads two words (min, max float bits) and advances it by two words; with
 * a NULL cursor it defaults to {0.0f, 1.0f} (recovered).  Installs the
 * (in-family) float->int8 quantizer executor vector. */
void quantized_runtime_quantizer_descriptor_construct(
    uintptr_t *descriptor, const uint32_t **cursor);

/* 0x0009371C: claim the first free pool slot (marks it in use); NULL when
 * the pool is full. */
quantized_runtime_tensor *quantized_runtime_pool_slot_claim(
    quantized_runtime_pool *pool);

/* 0x00091C48 + shared tail 0x000936FC: release a tensor descriptor.  When
 * the descriptor's bufferless flag (bit 2) is clear, its data pointer is
 * zeroed first; the matching pool slot is then marked free.  Foreign
 * descriptors simply miss the slot scan (recovered). */
void quantized_runtime_tensor_release(quantized_runtime_pool *pool,
                                      quantized_runtime_tensor *tensor);

/* 0x00091C56: release each non-NULL entry of a pointer array and zero the
 * array slots (count is the recovered signed loop bound). */
void quantized_runtime_tensor_release_many(quantized_runtime_pool *pool,
                                           quantized_runtime_tensor **tensors,
                                           int32_t count);

/* 0x00091E6C: construct a 0x14-byte tensor descriptor in a claimed slot:
 * zero the record, store ndims in flag bits 0-1, copy dims, store the
 * element-count product, set the bufferless flag, NULL the data pointer.
 * ndims outside 0..3 fails explicitly (stock callers always mask with 3;
 * larger values would overwrite the record's own flag/trailing words). */
quantized_runtime_tensor *quantized_runtime_tensor_construct(
    quantized_runtime_pool *pool, int32_t ndims, const uint16_t *dims);

/* 0x00093628: arena allocator with compaction.  When
 * used_words + tensor->count >= 0x6A4 the live arena buffers are sorted by
 * offset (stock qsort with the 0x00058D4A comparator) and memmoved down
 * before allocating.  Returns the arena base of the new buffer and advances
 * the watermark.  Fails explicitly (NULL) when compaction is needed but the
 * qsort provider is unbound, or when the request cannot fit even after
 * compaction (stock would corrupt memory past the arena -- unreachable in
 * stock-sized model graphs). */
uint32_t *quantized_runtime_arena_allocate(
    const quantized_runtime *rt, quantized_runtime_pool *pool,
    quantized_runtime_tensor *tensor);

/* 0x00091D9C: construct + arena-allocate + clear the bufferless flag. */
quantized_runtime_tensor *quantized_runtime_tensor_allocate(
    const quantized_runtime *rt, quantized_runtime_pool *pool, int32_t ndims,
    const uint16_t *dims);

/* 0x00091DBE: construct + arena-allocate + fill every element with the raw
 * bits of `fill`. */
quantized_runtime_tensor *quantized_runtime_tensor_create_fill(
    const quantized_runtime *rt, quantized_runtime_pool *pool, int32_t ndims,
    const uint16_t *dims, float fill);

/* 0x00091EBA: update flag bits 0-1 and the dims of an existing descriptor.
 * The element count is NOT recomputed (recovered quirk).  The stock first
 * argument was unused and is dropped. */
void quantized_runtime_tensor_reshape(quantized_runtime_tensor *tensor,
                                      int32_t ndims, const uint16_t *dims);

#endif
