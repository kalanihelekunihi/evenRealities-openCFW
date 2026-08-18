/*
 * Provenance banner
 * -----------------
 * Families:       unknown_shared_quantized_neural_runtime_candidate
 *                 (shared AOT-compiled static-graph quantized-neural
 *                 runtime; Bravechip BCL603M "ChipletRing" middleware
 *                 serving both the GoMore sleep classifier and the Goodix
 *                 GH_SPO2/dlCom model graphs), plus twenty-four Goodix-specific
 *                 graph, instance, and recurrent-runtime routines.
 * Stock image:    application image, load base 0x00027000, sha256
 *                 0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a.
 * Evidence:       r1/research/decompilation/application/decompiler-output.c
 *                 (26 shared and twenty-three Goodix-extension Ghidra bodies,
 *                 plus disassembly-pinned executors at 0x00085B9C and
 *                 0x00085DC4),
 *                 each cross-checked against fresh
 *                 Thumb disassembly of the byte-exact rebuilt image
 *                 r1/research/decompilation/rebuild/rebuilt-application.bin.
 * Status:         RECONSTRUCTED FROM DECOMPILATION EVIDENCE; NOT VENDOR
 *                 SOURCE.  Never present this file as Even Realities,
 *                 Bravechip, GoMore, or Goodix source.  Reduction is
 *                 owner-authorized per docs/SOURCE-ADMISSION.md
 *                 ("Owner-authorized full reduction (2026-08-14)").
 *
 * Per-function mapping (stock extent, end-exclusive / size -> symbol here):
 *
 *   0x000290FE..<0x00029120   34  -> quantized_runtime_round_half_away_from_zero_290fe
 *   0x0002F624..<0x0002F658   52  -> quantized_runtime_goodix_model_owner_initialize
 *   0x00030800..<0x0003096C   364 -> quantized_runtime_goodix_layer_block_build
 *   0x00029120..<0x00029142   34  -> quantized_runtime_round_half_away_from_zero_29120
 *   0x000293FC..<0x000294B6   186 -> quantized_runtime_float_to_int8_quantize
 *   0x00028EC8..<0x00029068   416 -> quantized_runtime_int8_concatenate_execute
 *   0x00030534..<0x000305D0   156 -> quantized_runtime_int8_to_float_execute
 *   0x0002951A..<0x000295DE   196 -> quantized_runtime_goodix_five_stage_32_execute
 *   0x00035E34..<0x00035F26   242 -> quantized_runtime_quantization_params_derive
 *   0x00035D6E..<0x00035E32   196 -> quantized_runtime_goodix_five_stage_27_execute
 *   0x00036408..<0x00036574   364 -> quantized_runtime_recurrent_range_adjust
 *   0x00036590..<0x000366FC   364 -> quantized_runtime_recurrent_range_adjust (exact twin)
 *   0x00036C7C..<0x00036D60   228 -> quantized_runtime_int8_add_execute
 *   0x00036DCC..<0x00036DD4 + 0x0003F6B4..<0x0003F740  148
 *                               -> quantized_runtime_float_concatenate_two_execute
 *   0x00036C26 head + 0x00099014..<0x00099110 tail   262
 *                               -> quantized_runtime_goodix_model_instance_create
 *   0x00041816..<0x000419C8   434 -> quantized_runtime_pooling_execute
 *   0x0003F7F8..<0x0003F89C   164 -> quantized_runtime_goodix_f32_three_stage_execute
 *   0x00042024..<0x00042108   228 -> quantized_runtime_goodix_u8_three_stage_execute
 *   0x0002874C..<0x00028AC8   892 -> quantized_runtime_gomore_sleep_graph_family_zero_build
 *   0x0002966C..<0x000299E0   884 -> quantized_runtime_gomore_sleep_graph_family_nonzero_build
 *   0x0004387C..<0x00043B2A   686 -> quantized_runtime_goodix_graph_build
 *   0x0005D01C..<0x0005D1AC   400 -> quantized_runtime_goodix_second_graph_build
 *   0x000617F8..<0x00061C44   1100 -> quantized_runtime_goodix_second_executor_execute
 *   0x0005A3D4..<0x0005A40E   58  -> quantized_runtime_two_output_thirds_slice
 *   0x0005D244..<0x0005D2DC   152 -> quantized_runtime_float_softmax_execute
 *   0x00065680..<0x000656AA   42  -> quantized_runtime_scaled_mul_conditional_release
 *   0x0006FDE0..<0x0006FE16   54  -> quantized_runtime_recurrent_zero_point
 *   0x0006FE20..<0x0006FE56   54  -> quantized_runtime_zero_point_compute
 *   0x000739A8..<0x00073E08   1120 -> quantized_runtime_recurrent_execute
 *   0x0007400C..<0x0007405C   80  -> quantized_runtime_float_min_max
 *   0x0007405C..<0x0007412C   208 -> quantized_runtime_u8_matrix_vector
 *   0x0003007E / 0x00038050 / 0x000417F0  16 each
 *                               -> quantized_runtime_goodix_executor_execute
 *   0x000742E4..<0x0007487E   1426 -> quantized_runtime_goodix_executor_execute
 *   0x00076BDC..<0x000770AE   1234 -> quantized_runtime_float_conv1d_execute
 *   0x00085B9C..<0x00085C98   252  -> quantized_runtime_float_dense_execute
 *   0x00085DC4..<0x00086BAC   3560 -> quantized_runtime_i8_conv1d_execute
 *   0x000876C8..<0x00087A6C   932 -> quantized_runtime_goodix_layer_execute
 *   0x00074A9C..<0x00074AA0   4   -> quantized_runtime_executor_vector_95b20
 *   0x00074A20..<0x00074A98   120 -> quantized_runtime_recurrent_layer_descriptor_construct
 *   0x00074AAC..<0x00074B3E   146 -> quantized_runtime_descriptor_construct
 *   0x00074B44..<0x00074BD4   144 -> quantized_runtime_aligned_descriptor_construct
 *   0x00074BD8..<0x00074BDC   4   -> quantized_runtime_executor_vector_36dcc
 *   0x00074BE0..<0x00074C42   98  -> quantized_runtime_descriptor_record_construct
 *   0x00074C6C..<0x00074C8A   30  -> quantized_runtime_packed_pool_descriptor_initialize
 *   0x00074C90..<0x00074C94   4   -> quantized_runtime_executor_vector_30534
 *   0x00074C98..<0x00074CAE   22  -> quantized_runtime_operator_descriptor_init
 *   0x00074CB4..<0x00074CD6   34  -> quantized_runtime_cursor_pair_add_descriptor_construct
 *   0x00074CDC..<0x00074CE0   4   -> quantized_runtime_softmax_executor_vector
 *   0x00074CE4..<0x00074D02   30  -> quantized_runtime_quantizer_descriptor_construct
 *   0x00091C48..<0x00091C56 + 0x000936FC..<0x0009371C  46
 *                               -> quantized_runtime_tensor_release
 *   0x00091C56..<0x00091C80   42  -> quantized_runtime_tensor_release_many
 *   0x00091D9C..<0x00091DBE   34  -> quantized_runtime_tensor_allocate
 *   0x00091DBE..<0x00091E02   68  -> quantized_runtime_tensor_create_fill
 *   0x00091E02..<0x00091E6C   106 -> quantized_runtime_tensor_slice
 *   0x00091E6C..<0x00091EBA   78  -> quantized_runtime_tensor_construct
 *   0x00091EBA..<0x00091EDC   34  -> quantized_runtime_tensor_reshape
 *   0x00093628..<0x000936F8   208 -> quantized_runtime_arena_allocate
 *   0x0009371C..<0x00093744   40  -> quantized_runtime_pool_slot_claim
 *   0x00098EDC..<0x00098F80   164 -> quantized_runtime_float_add_execute
 *   0x00095B20..<0x00095BB8   152 -> quantized_runtime_float_multiply_execute
 *
 * Observable behavior is preserved; restructuring is limited to explicit
 * provider bindings (toolchain fminf/fmaxf/floorf/expf/qsort, the
 * source-admitted GoMore slice/scaled-mul seams, and six out-of-family
 * executor pointer tokens), pointer/argument validation, and checked arena,
 * model-region, and recurrent-workspace bounds.  The recurrent executor's
 * target adapter calls attributable libm floorf/fmaxf/expf/tanhf directly;
 * the stock body called the corresponding linked toolchain routines.
 * overflow guard.  Every divergence is listed in
 * docs/correlation/QUANTIZED-RUNTIME-REDUCTION-CORRELATION.md.
 */

#include "quantized_runtime/quantized_runtime.h"

/* The freestanding Cortex-M4 object gate intentionally has no hosted C
 * headers.  These four C99 libm declarations match the attributable
 * toolchain routines called by stock and are resolved by the final SDK
 * link. */
extern float expf(float value);
extern float floorf(float value);
extern float fmaxf(float left, float right);
extern float tanhf(float value);

/* The recovered field offsets are a property of the 32-bit target ABI; on
 * wider host pointer ABIs the C layout legitimately differs, so the exact
 * layout asserts apply to the target ABI only. */
#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(quantized_runtime_exec_tensor) == 20u,
               "recovered executor tensor is 20 bytes");
_Static_assert(offsetof(quantized_runtime_exec_tensor, dims) == 0x04u,
               "executor tensor +0x04");
_Static_assert(offsetof(quantized_runtime_exec_tensor, data) == 0x10u,
               "executor tensor +0x10");
_Static_assert(sizeof(quantized_runtime_tensor) == 0x14u,
               "recovered pool tensor is 0x14 bytes");
_Static_assert(offsetof(quantized_runtime_tensor, count) == 0x04u,
               "pool tensor +0x04");
_Static_assert(offsetof(quantized_runtime_tensor, dims) == 0x08u,
               "pool tensor +0x08");
_Static_assert(offsetof(quantized_runtime_tensor, flags) == 0x0Eu,
               "pool tensor +0x0E");
_Static_assert(offsetof(quantized_runtime_pool, in_use) == 0xF0u,
               "pool +0xF0");
_Static_assert(offsetof(quantized_runtime_pool, arena) == 0xFCu,
               "pool +0xFC");
_Static_assert(offsetof(quantized_runtime_pool, used_words) == 0x1B8Cu,
               "pool +0x1B8C");
_Static_assert(sizeof(quantized_runtime_pool) == 0x1B90u,
               "recovered pool is 0x1B90 bytes");
_Static_assert(sizeof(quantized_runtime_recurrent_descriptor) == 0x18u,
               "recovered recurrent descriptor is 24 bytes");
_Static_assert(offsetof(quantized_runtime_recurrent_descriptor, state) == 0x04u,
               "recurrent descriptor +0x04");
_Static_assert(offsetof(quantized_runtime_recurrent_descriptor, execute) == 0x14u,
               "recurrent descriptor +0x14");
_Static_assert(sizeof(quantized_runtime_goodix_model_instance) == 0x344u,
               "recovered Goodix model instance is 0x344 bytes");
_Static_assert(offsetof(quantized_runtime_goodix_model_instance, graph_a) == 0x004u,
               "Goodix model graph A +0x004");
_Static_assert(offsetof(quantized_runtime_goodix_model_instance, graph_b) == 0x164u,
               "Goodix model graph B +0x164");
_Static_assert(offsetof(quantized_runtime_goodix_model_instance, descriptor_a) == 0x2C4u,
               "Goodix model descriptor A +0x2C4");
_Static_assert(offsetof(quantized_runtime_goodix_model_instance, recurrent) == 0x2FCu,
               "Goodix model recurrent +0x2FC");
_Static_assert(offsetof(quantized_runtime_goodix_model_instance, descriptor_d) == 0x32Cu,
               "Goodix model descriptor D +0x32C");
_Static_assert(offsetof(quantized_runtime_goodix_model_owner, instance) == 0x1Cu,
               "Goodix model owner instance +0x1C");
#endif

/* Recovered float constants (literal pools read from the rebuilt image). */
#define QUANTIZED_RUNTIME_RANGE_FLOOR 1e-4f      /* 0x38D1B717 */
#define QUANTIZED_RUNTIME_FULL_SCALE 255.0f      /* 0x437F0000 */
#define QUANTIZED_RUNTIME_SOFTMAX_CAP 88.0f      /* 0x42B00000 */
#define QUANTIZED_RUNTIME_SOFTMAX_CAP_BITS INT32_C(0x42B00000)
#define QUANTIZED_RUNTIME_DERIVE_FRACTION_BIAS UINT32_C(0xC77FFFFF)
#define QUANTIZED_RUNTIME_DERIVE_FRACTION_LIMIT UINT32_C(0x06FFFBFF)
#define QUANTIZED_RUNTIME_DERIVE_FLOOR_LIMIT_BITS INT32_C(0x437D0000) /* 253.0f */
#define QUANTIZED_RUNTIME_RECURRENT_MIN_STEP_BITS UINT32_C(0x358637BD)
#define QUANTIZED_RUNTIME_RECURRENT_FRACTION_LOW_BITS UINT32_C(0x38800000)
#define QUANTIZED_RUNTIME_RECURRENT_FRACTION_HIGH_BITS UINT32_C(0x3F7FFC00)
#define QUANTIZED_RUNTIME_RECURRENT_ONE_BITS UINT32_C(0x3F800000)
#define QUANTIZED_RUNTIME_RECURRENT_63_75_BITS UINT32_C(0x427F0000)
#define QUANTIZED_RUNTIME_RECURRENT_192_25_BITS UINT32_C(0x43404000)
#define QUANTIZED_RUNTIME_RECURRENT_254_BITS UINT32_C(0x437E0000)

/* Local float/word punning and record access helpers; the freestanding
 * build does not use libc string.h. */
static uint32_t f32_to_bits(float value) {
    union {
        float f;
        uint32_t u;
    } pun;
    pun.f = value;
    return pun.u;
}

static float bits_to_f32(uint32_t bits) {
    union {
        float f;
        uint32_t u;
    } pun;
    pun.u = bits;
    return pun.f;
}

/* Descriptor records are a recovered little-endian byte ABI; assemble and
 * disassemble explicitly so the layout holds on any host. */
static uint32_t load_u32_le(const uint8_t *record) {
    return (uint32_t)record[0] | ((uint32_t)record[1] << 8) |
           ((uint32_t)record[2] << 16) | ((uint32_t)record[3] << 24);
}

static void store_u32_le(uint8_t *record, uint32_t value) {
    record[0] = (uint8_t)(value & 0xFFu);
    record[1] = (uint8_t)((value >> 8) & 0xFFu);
    record[2] = (uint8_t)((value >> 16) & 0xFFu);
    record[3] = (uint8_t)((value >> 24) & 0xFFu);
}

static float load_f32_le(const uint8_t *record) {
    return bits_to_f32(load_u32_le(record));
}

static void store_f32_le(uint8_t *record, float value) {
    store_u32_le(record, f32_to_bits(value));
}

static void zero_bytes(uint8_t *destination, size_t count) {
    for (size_t index = 0u; index < count; ++index) {
        destination[index] = 0u;
    }
}

static void store_native_words_as_u32(uint8_t *destination,
                                      const uintptr_t *words,
                                      size_t count) {
    for (size_t index = 0u; index < count; ++index) {
        store_u32_le(destination + index * 4u, (uint32_t)words[index]);
    }
}

/* Recovered rounding idiom (0x000290FE/0x00029120 and inlined at the
 * average-pool and quantizer sites): vcmpe + ble, so NaN and value <= 0
 * take the -0.5 adjust; vcvt.s32.f32 truncates toward zero. */
static int32_t round_half_away_from_zero(float value) {
    const float adjust = (value > 0.0f) ? 0.5f : -0.5f;
    return (int32_t)(value + adjust);
}

void quantized_runtime_initialize(
    quantized_runtime *rt, const quantized_runtime_providers *providers) {
    if (rt == NULL) {
        return;
    }
    zero_bytes((uint8_t *)rt, sizeof(*rt));
    if (providers != NULL) {
        rt->providers = *providers;
    }
}

void quantized_runtime_pool_initialize(quantized_runtime_pool *pool) {
    if (pool == NULL) {
        return;
    }
    zero_bytes((uint8_t *)pool, sizeof(*pool));
}

int32_t quantized_runtime_round_half_away_from_zero_290fe(float value) {
    return round_half_away_from_zero(value);
}

int32_t quantized_runtime_round_half_away_from_zero_29120(float value) {
    return round_half_away_from_zero(value);
}

/* Shared core of 0x0006FE20; the fmaxf binding is validated by callers. */
static int32_t zero_point_compute(const quantized_runtime_providers *providers,
                                  float value, float min, float max) {
    const float range = providers->fmaxf_fn(QUANTIZED_RUNTIME_RANGE_FLOOR,
                                            max - min);
    return round_half_away_from_zero(
        (value - min) * (QUANTIZED_RUNTIME_FULL_SCALE / range));
}

int32_t quantized_runtime_zero_point_compute(const quantized_runtime *rt,
                                             float value, float min,
                                             float max) {
    if (rt == NULL || rt->providers.fmaxf_fn == NULL) {
        return 0;
    }
    return zero_point_compute(&rt->providers, value, min, max);
}

int32_t quantized_runtime_recurrent_range_adjust(float *min_value,
                                                 float *max_value,
                                                 uint32_t mode) {
    if (min_value == NULL || max_value == NULL) {
        return -1;
    }
    const float min_original = *min_value;
    const float max_original = *max_value;
    const float range = max_original - min_original;
    if (!(range > 0.0f)) {
        return -1;
    }
    if (min_original == 0.0f) {
        return 0;
    }

    const float zero_position = (min_original * -255.0f) / range;
    const float lower_integer = floorf(zero_position);
    const float fraction = zero_position - lower_integer;
    const uint32_t fraction_bits = f32_to_bits(fraction);
    if (fraction_bits <= QUANTIZED_RUNTIME_RECURRENT_FRACTION_LOW_BITS ||
            fraction_bits >= QUANTIZED_RUNTIME_RECURRENT_FRACTION_HIGH_BITS) {
        return 0;
    }

    const float left_error = (fraction - 1.0f) * min_original;
    const float right_error = fraction * max_original;
    const uint32_t lower_bits = f32_to_bits(lower_integer);
    const uint32_t position_bits = f32_to_bits(zero_position);
    float upper_integer = lower_integer;
    if (fraction_bits >= UINT32_C(0x3F000000)) {
        upper_integer = lower_integer + 1.0f;
    }

    bool adjust_max = false;
    bool adjust_min = false;
    float max_denominator = lower_integer;
    switch (mode & 3u) {
        case 1u:
            adjust_max = lower_bits >= QUANTIZED_RUNTIME_RECURRENT_ONE_BITS &&
                (position_bits >= QUANTIZED_RUNTIME_RECURRENT_192_25_BITS ||
                 left_error * 8.0f > right_error);
            adjust_min = !adjust_max;
            break;
        case 2u:
            adjust_max =
                position_bits >= QUANTIZED_RUNTIME_RECURRENT_63_75_BITS &&
                (lower_bits >= QUANTIZED_RUNTIME_RECURRENT_254_BITS ||
                 right_error * 8.0f < left_error);
            max_denominator = upper_integer;
            adjust_min = !adjust_max;
            break;
        case 3u:
            if (position_bits <= QUANTIZED_RUNTIME_RECURRENT_63_75_BITS) {
                adjust_min = true;
            } else if (position_bits <
                       QUANTIZED_RUNTIME_RECURRENT_192_25_BITS) {
                const float shift =
                    (zero_position - upper_integer) * range *
                    bits_to_f32(UINT32_C(0x3B808081));
                *min_value = min_original + shift;
                *max_value = max_original + shift;
                return 3;
            } else {
                adjust_max = true;
                max_denominator = upper_integer;
            }
            break;
        default:
            adjust_max = lower_bits >= QUANTIZED_RUNTIME_RECURRENT_ONE_BITS &&
                (lower_bits >= QUANTIZED_RUNTIME_RECURRENT_254_BITS ||
                 left_error >= right_error);
            adjust_min = !adjust_max;
            break;
    }

    if (adjust_max) {
        *max_value = min_original -
                     (min_original * 255.0f) / max_denominator;
        return 2;
    }
    if (adjust_min) {
        const float integer = lower_integer + 1.0f;
        *min_value = (max_original * integer) / (integer - 255.0f);
        return 1;
    }
    return 0;
}

int32_t quantized_runtime_recurrent_zero_point(float value, float min_value,
                                               float max_value) {
    const float range = fmaxf(QUANTIZED_RUNTIME_RANGE_FLOOR,
                              max_value - min_value);
    return round_half_away_from_zero(
        (value - min_value) * (QUANTIZED_RUNTIME_FULL_SCALE / range));
}

void quantized_runtime_float_min_max(const float *values, uint16_t count,
                                     float *max_value, float *min_value) {
    if (values == NULL || count == 0u || max_value == NULL ||
            min_value == NULL) {
        return;
    }
    *max_value = values[0];
    *min_value = values[0];
    for (uint32_t index = 0u; index < count; ++index) {
        if (*max_value < values[index]) {
            *max_value = values[index];
        }
        if (values[index] < *min_value) {
            *min_value = values[index];
        }
    }
}

void quantized_runtime_u8_matrix_vector(const uint8_t *vector,
                                        const uint8_t *matrix,
                                        int32_t *output, uint32_t columns,
                                        uint32_t rows,
                                        int32_t vector_zero_point,
                                        int32_t matrix_zero_point) {
    if (vector == NULL || matrix == NULL || output == NULL) {
        return;
    }
    for (uint32_t row = 0u; row < rows; ++row) {
        uint32_t accumulator = 0u;
        const uint8_t *matrix_row = matrix + (size_t)row * columns;
        for (uint32_t column = 0u; column < columns; ++column) {
            const int32_t vector_value =
                (int32_t)vector[column] - vector_zero_point;
            const int32_t matrix_value =
                (int32_t)matrix_row[column] - matrix_zero_point;
            accumulator += (uint32_t)(vector_value * matrix_value);
        }
        output[row] = (int32_t)accumulator;
    }
}

size_t quantized_runtime_recurrent_workspace_bytes(uint32_t units,
                                                   uint32_t input_dimension) {
    const uint64_t state_bytes = ((uint64_t)units + 3u) & ~UINT64_C(3);
    const uint64_t total = (uint64_t)units * 11u * sizeof(float) +
                           state_bytes + input_dimension;
    return total <= (uint64_t)SIZE_MAX ? (size_t)total : 0u;
}

static uint8_t saturate_u8(int32_t value) {
    if (value < 0) {
        return 0u;
    }
    if (value > 255) {
        return UINT8_MAX;
    }
    return (uint8_t)value;
}

static uint32_t recurrent_execute_core(
    const quantized_runtime_recurrent_descriptor *descriptor,
    const uint8_t *input_weights, const uint8_t *recurrent_weights,
    const uint8_t *tail, quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs, void *workspace,
    size_t workspace_size) {
    if (descriptor == NULL || descriptor->state == NULL || input_weights == NULL ||
            recurrent_weights == NULL || tail == NULL || inputs == NULL ||
            outputs == NULL || inputs[0] == NULL || outputs[0] == NULL ||
            inputs[0]->data == NULL || outputs[0]->data == NULL ||
            workspace == NULL || ((uintptr_t)workspace & 3u) != 0u) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const uint32_t units = descriptor->units;
    const uint32_t input_dimension = inputs[0]->dims[1];
    const size_t required =
        quantized_runtime_recurrent_workspace_bytes(units, input_dimension);
    if (units == 0u || input_dimension == 0u || required == 0u ||
            workspace_size < required) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }

    const size_t three_units = (size_t)units * 3u;
    uint8_t *scratch = (uint8_t *)workspace;
    float *input_scales = (float *)scratch;
    float *recurrent_scales = input_scales + three_units;
    int32_t *accumulator = (int32_t *)(recurrent_scales + three_units);
    float *gates = (float *)(accumulator + (size_t)units * 2u);
    uint8_t *quantized_state = (uint8_t *)(gates + (size_t)units * 2u);
    uint8_t *candidate_bytes =
        quantized_state + (((size_t)units + 3u) & ~(size_t)3u);
    float *candidate = (float *)candidate_bytes;
    uint8_t *quantized_input = (uint8_t *)(candidate + units);

    const float *input = (const float *)inputs[0]->data;
    float *output = (float *)outputs[0]->data;
    const size_t range_offset = (size_t)units * 4u * sizeof(float);
    const float input_weight_min = load_f32_le(tail + range_offset);
    const float input_weight_max =
        load_f32_le(tail + range_offset + sizeof(float));
    const float recurrent_weight_min =
        load_f32_le(tail + range_offset + 2u * sizeof(float));
    const float recurrent_weight_max =
        load_f32_le(tail + range_offset + 3u * sizeof(float));
    const float input_weight_step =
        (input_weight_max - input_weight_min) / 255.0f;
    const float recurrent_weight_step =
        (recurrent_weight_max - recurrent_weight_min) / 255.0f;
    const int32_t input_weight_zero = quantized_runtime_recurrent_zero_point(
        0.0f, input_weight_min, input_weight_max);
    const int32_t recurrent_weight_zero =
        quantized_runtime_recurrent_zero_point(
            0.0f, recurrent_weight_min, recurrent_weight_max);
    if (input_weight_zero != 128 || recurrent_weight_zero != 128) {
        return QUANTIZED_RUNTIME_RECURRENT_RANGE_ERROR;
    }

    const size_t correction_offset = range_offset + 6u * sizeof(float);
    for (size_t index = 0u; index < three_units; ++index) {
        const float correction =
            load_f32_le(tail + correction_offset + index * sizeof(float));
        const float recurrent_correction = load_f32_le(
            tail + correction_offset +
            (three_units + index) * sizeof(float));
        input_scales[index] = correction;
        recurrent_scales[index] =
            bits_to_f32(UINT32_C(0x3C010204)) * recurrent_weight_step *
            recurrent_correction;
    }

    float observed_min = 0.0f;
    float observed_max = 0.0f;
    for (uint32_t index = 0u; index < input_dimension; ++index) {
        if (input[index] < observed_min) {
            observed_min = input[index];
        }
        if (input[index] > observed_max) {
            observed_max = input[index];
        }
    }
    (void)quantized_runtime_recurrent_range_adjust(&observed_min,
                                                   &observed_max, 3u);
    float input_step = (observed_max - observed_min) / 255.0f;
    if (f32_to_bits(input_step) <
        QUANTIZED_RUNTIME_RECURRENT_MIN_STEP_BITS) {
        input_step = bits_to_f32(QUANTIZED_RUNTIME_RECURRENT_MIN_STEP_BITS);
    }
    const int32_t input_zero =
        round_half_away_from_zero(-observed_min / input_step);
    for (size_t index = 0u; index < three_units; ++index) {
        input_scales[index] *= input_step * input_weight_step;
    }
    for (uint32_t index = 0u; index < input_dimension; ++index) {
        quantized_input[index] = saturate_u8(
            round_half_away_from_zero(input[index] / input_step) + input_zero);
    }
    for (uint32_t index = 0u; index < units; ++index) {
        quantized_state[index] = saturate_u8(round_half_away_from_zero(
            (float)recurrent_weight_zero + descriptor->state[index] * 127.0f));
    }

    quantized_runtime_u8_matrix_vector(
        quantized_input, input_weights, accumulator, input_dimension,
        units * 2u, input_zero, input_weight_zero);
    for (uint32_t index = 0u; index < units * 2u; ++index) {
        gates[index] = load_f32_le(tail + (size_t)index * sizeof(float)) +
                       (float)accumulator[index] * input_scales[index];
    }
    quantized_runtime_u8_matrix_vector(
        quantized_state, recurrent_weights, accumulator, units, units * 2u,
        recurrent_weight_zero, recurrent_weight_zero);
    for (uint32_t index = 0u; index < units * 2u; ++index) {
        gates[index] +=
            (float)accumulator[index] * recurrent_scales[index];
        float exponent = -gates[index];
        if (exponent >= 88.0f) {
            exponent = 88.0f;
        }
        gates[index] = 1.0f / (expf(exponent) + 1.0f);
    }

    const size_t third_input_matrix =
        (size_t)units * 2u * input_dimension;
    quantized_runtime_u8_matrix_vector(
        quantized_input, input_weights + third_input_matrix, accumulator,
        input_dimension, units, input_zero, input_weight_zero);
    for (uint32_t index = 0u; index < units; ++index) {
        candidate[index] =
            load_f32_le(tail + ((size_t)units * 2u + index) * sizeof(float)) +
            (float)accumulator[index] * input_scales[(size_t)units * 2u + index];
    }
    const size_t third_recurrent_matrix = (size_t)units * 2u * units;
    quantized_runtime_u8_matrix_vector(
        quantized_state, recurrent_weights + third_recurrent_matrix,
        accumulator, units, units, recurrent_weight_zero,
        recurrent_weight_zero);
    for (uint32_t index = 0u; index < units; ++index) {
        const float recurrent_term =
            load_f32_le(tail + ((size_t)units * 3u + index) * sizeof(float)) +
            (float)accumulator[index] *
                recurrent_scales[(size_t)units * 2u + index];
        candidate[index] = tanhf(candidate[index] +
                                 recurrent_term * gates[units + index]);
    }
    for (uint32_t index = 0u; index < units; ++index) {
        const float updated = gates[index] * descriptor->state[index] +
            (1.0f - gates[index]) * candidate[index];
        descriptor->state[index] = updated;
        output[index] = updated;
    }
    return QUANTIZED_RUNTIME_STATUS_OK;
}

static const uint8_t *resolve_model_bytes(
    const quantized_runtime_model_region *region, uint32_t address,
    uint64_t span) {
    if (region == NULL || region->bytes == NULL ||
            address < region->target_address) {
        return NULL;
    }
    const uint64_t offset = (uint64_t)address - region->target_address;
    if (offset > region->size || span > (uint64_t)region->size - offset) {
        return NULL;
    }
    return region->bytes + (size_t)offset;
}

uint32_t quantized_runtime_recurrent_execute(
    const quantized_runtime_recurrent_descriptor *descriptor,
    const quantized_runtime_model_region *model_region,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs, void *workspace,
    size_t workspace_size) {
    if (descriptor == NULL || inputs == NULL || inputs[0] == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const uint64_t units = descriptor->units;
    const uint64_t input_dimension = inputs[0]->dims[1];
    if (units == 0u || input_dimension == 0u ||
            units > UINT32_MAX / 2u ||
            units * input_dimension > UINT64_MAX / 3u ||
            units * units > UINT64_MAX / 3u) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const uint8_t *input_weights = resolve_model_bytes(
        model_region, descriptor->input_weights_offset,
        units * input_dimension * 3u);
    const uint8_t *recurrent_weights = resolve_model_bytes(
        model_region, descriptor->recurrent_weights_offset,
        units * units * 3u);
    const uint8_t *tail = resolve_model_bytes(
        model_region, descriptor->bias_offset, (units * 10u + 6u) * 4u);
    if (input_weights == NULL || recurrent_weights == NULL || tail == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    return recurrent_execute_core(descriptor, input_weights,
                                  recurrent_weights, tail, inputs, outputs,
                                  workspace, workspace_size);
}

uint32_t quantized_runtime_recurrent_execute_target(
    const quantized_runtime_recurrent_descriptor *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    if (descriptor == NULL || inputs == NULL || inputs[0] == NULL ||
            inputs[0]->data == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const uint32_t input_dimension = inputs[0]->dims[1];
    uint8_t *workspace =
        (uint8_t *)inputs[0]->data + (size_t)input_dimension * sizeof(float);
    return recurrent_execute_core(
        descriptor,
        (const uint8_t *)(uintptr_t)descriptor->input_weights_offset,
        (const uint8_t *)(uintptr_t)descriptor->recurrent_weights_offset,
        (const uint8_t *)(uintptr_t)descriptor->bias_offset, inputs, outputs,
        workspace, quantized_runtime_recurrent_workspace_bytes(
                       descriptor->units, input_dimension));
}

static void exec_tensor_initialize(quantized_runtime_exec_tensor *tensor,
                                   uint32_t batches, uint32_t rows,
                                   uint32_t columns, uint32_t element_bytes,
                                   void *data) {
    tensor->type_flag = element_bytes;
    tensor->dims[0] = batches;
    tensor->dims[1] = rows;
    tensor->dims[2] = columns;
    tensor->data = data;
}

static bool stage_callable(const quantized_runtime_stage *stage) {
    if (stage == NULL) {
        return false;
    }
    if (stage->adapter == QUANTIZED_RUNTIME_STAGE_DIRECT) {
        return stage->execute != NULL;
    }
    return stage->runtime != NULL &&
        (stage->adapter == QUANTIZED_RUNTIME_STAGE_QUANTIZE_WITH_RUNTIME ||
         stage->adapter == QUANTIZED_RUNTIME_STAGE_INT8_ADD_WITH_RUNTIME ||
         stage->adapter == QUANTIZED_RUNTIME_STAGE_SOFTMAX_WITH_RUNTIME);
}

static uint32_t stage_invoke(
    const quantized_runtime_stage *stage,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    if (!stage_callable(stage)) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    if (stage->adapter == QUANTIZED_RUNTIME_STAGE_QUANTIZE_WITH_RUNTIME) {
        return quantized_runtime_float_to_int8_quantize(
            stage->runtime, stage->descriptor, inputs, outputs);
    }
    if (stage->adapter == QUANTIZED_RUNTIME_STAGE_INT8_ADD_WITH_RUNTIME) {
        return quantized_runtime_int8_add_execute(
            stage->runtime, stage->descriptor, inputs, outputs);
    }
    if (stage->adapter == QUANTIZED_RUNTIME_STAGE_SOFTMAX_WITH_RUNTIME) {
        return quantized_runtime_float_softmax_execute(
            stage->runtime, stage->descriptor, inputs, outputs);
    }
    return stage->execute(stage->descriptor, inputs, outputs);
}

uint32_t quantized_runtime_stage_invoke(
    const quantized_runtime_stage *stage,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    return stage_invoke(stage, inputs, outputs);
}

static bool five_stage_execute(
    const quantized_runtime_five_stage_plan *plan,
    quantized_runtime_exec_tensor *input,
    quantized_runtime_exec_tensor *output, void *workspace,
    size_t workspace_size, uint32_t first_columns, size_t bank_two,
    size_t bank_three) {
    const size_t first_bytes = (size_t)12u * first_columns * sizeof(float);
    const size_t required = bank_three + 12u * sizeof(float);
    if (plan == NULL || input == NULL || output == NULL || workspace == NULL ||
            workspace_size < first_bytes || workspace_size < required) {
        return false;
    }
    for (size_t index = 0u; index < 5u; ++index) {
        if (!stage_callable(&plan->stages[index])) {
            return false;
        }
    }

    quantized_runtime_exec_tensor tensors[5];
    uint8_t *bytes = (uint8_t *)workspace;
    exec_tensor_initialize(&tensors[0], 1u, 12u, first_columns, 4u, bytes);
    exec_tensor_initialize(&tensors[1], 1u, 12u, 1u, 4u, bytes);
    exec_tensor_initialize(&tensors[2], 1u, 12u, 1u, 4u,
                           bytes + bank_two);
    exec_tensor_initialize(&tensors[3], 1u, 12u, 1u, 4u,
                           bytes + bank_three);
    exec_tensor_initialize(&tensors[4], 1u, 1u, 12u, 4u, bytes);

    quantized_runtime_exec_tensor *stage_input[1] = {input};
    quantized_runtime_exec_tensor *stage_output[1] = {&tensors[0]};
    (void)stage_invoke(&plan->stages[0], stage_input, stage_output);
    for (size_t index = 1u; index < 5u; ++index) {
        stage_input[0] = &tensors[index - 1u];
        stage_output[0] = &tensors[index];
        (void)stage_invoke(&plan->stages[index], stage_input, stage_output);
    }
    *output = tensors[4];
    return true;
}

bool quantized_runtime_goodix_five_stage_32_execute(
    const quantized_runtime_five_stage_plan *plan,
    quantized_runtime_exec_tensor *input,
    quantized_runtime_exec_tensor *output, void *workspace,
    size_t workspace_size) {
    return five_stage_execute(plan, input, output, workspace, workspace_size,
                              32u, 0x310u, 0x620u);
}

bool quantized_runtime_goodix_five_stage_27_execute(
    const quantized_runtime_five_stage_plan *plan,
    quantized_runtime_exec_tensor *input,
    quantized_runtime_exec_tensor *output, void *workspace,
    size_t workspace_size) {
    return five_stage_execute(plan, input, output, workspace, workspace_size,
                              27u, 0x510u, 0x540u);
}

static bool three_stage_validate(
    const quantized_runtime_three_stage_plan *plan, const uint8_t shape[6],
    uint32_t element_bytes, size_t minimum_span, size_t workspace_size,
    size_t *bank_span) {
    if (plan == NULL || shape == NULL || bank_span == NULL) {
        return false;
    }
    for (size_t index = 0u; index < 3u; ++index) {
        if (!stage_callable(&plan->stages[index])) {
            return false;
        }
    }
    const uint64_t padded_columns = (uint64_t)shape[1] +
                                    plan->row_padding +
                                    plan->column_padding;
    uint64_t span = padded_columns * shape[0] * element_bytes;
    if (span < minimum_span) {
        span = minimum_span;
    }
    const uint64_t first_bytes =
        (uint64_t)shape[0] * shape[1] * element_bytes;
    const uint64_t middle_bytes =
        (uint64_t)shape[2] * shape[3] * element_bytes;
    const uint64_t last_bytes =
        (uint64_t)shape[4] * shape[5] * element_bytes;
    uint64_t required = first_bytes > last_bytes ? first_bytes : last_bytes;
    if (!plan->middle_uses_input_storage) {
        const uint64_t middle_end = span + middle_bytes;
        if (middle_end > required) {
            required = middle_end;
        }
    }
    if (span > SIZE_MAX || required > workspace_size) {
        return false;
    }
    *bank_span = (size_t)span;
    return true;
}

bool quantized_runtime_goodix_u8_three_stage_execute(
    const quantized_runtime_three_stage_plan *plan,
    quantized_runtime_exec_tensor *const inputs[2],
    quantized_runtime_exec_tensor *const outputs[2],
    const uint8_t shape[6], size_t minimum_span, void *workspace,
    size_t workspace_size) {
    size_t bank_span = 0u;
    if (inputs == NULL || outputs == NULL || inputs[0] == NULL ||
            outputs[0] == NULL || workspace == NULL ||
            !three_stage_validate(plan, shape, 1u, minimum_span,
                                  workspace_size, &bank_span)) {
        return false;
    }
    uint8_t *bytes = (uint8_t *)workspace;
    quantized_runtime_exec_tensor tensors[3];
    exec_tensor_initialize(&tensors[0], 1u, shape[0], shape[1], 1u, bytes);
    void *middle_data = plan->middle_uses_input_storage
        ? inputs[0]->data : (void *)(bytes + bank_span);
    if (middle_data == NULL) {
        return false;
    }
    exec_tensor_initialize(&tensors[1], 1u, shape[2], shape[3], 1u,
                           middle_data);
    exec_tensor_initialize(&tensors[2], 1u, shape[4], shape[5], 1u, bytes);

    quantized_runtime_exec_tensor *stage_inputs[2] = {inputs[0], inputs[1]};
    quantized_runtime_exec_tensor *stage_outputs[2] = {&tensors[0], outputs[1]};
    (void)stage_invoke(&plan->stages[0], stage_inputs, stage_outputs);
    stage_inputs[0] = &tensors[0];
    stage_inputs[1] = outputs[1];
    stage_outputs[0] = &tensors[1];
    (void)stage_invoke(&plan->stages[1], stage_inputs, stage_outputs);
    stage_inputs[0] = &tensors[1];
    stage_outputs[0] = &tensors[2];
    (void)stage_invoke(&plan->stages[2], stage_inputs, stage_outputs);
    *outputs[0] = tensors[2];
    return true;
}

bool quantized_runtime_goodix_f32_three_stage_execute(
    const quantized_runtime_three_stage_plan *plan,
    quantized_runtime_exec_tensor *input,
    quantized_runtime_exec_tensor *output, const uint8_t shape[6],
    size_t minimum_span, void *workspace, size_t workspace_size) {
    size_t bank_span = 0u;
    if (input == NULL || output == NULL || workspace == NULL || plan == NULL ||
            plan->middle_uses_input_storage ||
            !three_stage_validate(plan, shape, 4u, minimum_span,
                                  workspace_size, &bank_span)) {
        return false;
    }
    uint8_t *bytes = (uint8_t *)workspace;
    quantized_runtime_exec_tensor tensors[3];
    exec_tensor_initialize(&tensors[0], 1u, shape[0], shape[1], 4u, bytes);
    exec_tensor_initialize(&tensors[1], 1u, shape[2], shape[3], 4u,
                           bytes + bank_span);
    exec_tensor_initialize(&tensors[2], 1u, shape[4], shape[5], 4u, bytes);
    quantized_runtime_exec_tensor *stage_inputs[1] = {input};
    quantized_runtime_exec_tensor *stage_outputs[1] = {&tensors[0]};
    (void)stage_invoke(&plan->stages[0], stage_inputs, stage_outputs);
    for (size_t index = 1u; index < 3u; ++index) {
        stage_inputs[0] = &tensors[index - 1u];
        stage_outputs[0] = &tensors[index];
        (void)stage_invoke(&plan->stages[index], stage_inputs, stage_outputs);
    }
    *output = tensors[2];
    return true;
}

bool quantized_runtime_goodix_nadt_projection_execute(
    const quantized_runtime_three_stage_plan *plan,
    quantized_runtime_exec_tensor *input,
    quantized_runtime_exec_tensor *output, const uint8_t shape[6],
    size_t workspace_size) {
    if (plan == NULL || output == NULL || output->data == NULL ||
            plan->row_padding != 0u || plan->column_padding != 0u ||
            plan->middle_uses_input_storage) {
        return false;
    }
    void *const workspace = output->data;
    return quantized_runtime_goodix_f32_three_stage_execute(
        plan, input, output, shape, 0x1F0u, workspace, workspace_size);
}

enum {
    GOODIX_EXEC_BOOTSTRAP = 0,
    GOODIX_EXEC_EXPAND_99,
    GOODIX_EXEC_REDUCE_49,
    GOODIX_EXEC_MERGE_49,
    GOODIX_EXEC_REDUCE_24,
    GOODIX_EXEC_MERGE_24,
    GOODIX_EXEC_REDUCE_12,
    GOODIX_EXEC_FLOAT_CONVERT,
    GOODIX_EXEC_BRANCH_MERGE,
    GOODIX_EXEC_AFTER_FLOAT_PIPELINE,
    GOODIX_EXEC_REMAP,
    GOODIX_EXEC_HEAD_EXPAND,
    GOODIX_EXEC_HEAD_MERGE,
    GOODIX_EXEC_TAIL_0,
    GOODIX_EXEC_TAIL_1,
    GOODIX_EXEC_TAIL_2,
    GOODIX_EXEC_TAIL_3,
    GOODIX_EXEC_TAIL_OPTIONAL
};

static bool workspace_contains(size_t workspace_size, size_t offset,
                               uint32_t rows, uint32_t columns,
                               uint32_t element_bytes) {
    const uint64_t bytes =
        (uint64_t)rows * columns * element_bytes;
    return offset <= workspace_size &&
           bytes <= (uint64_t)workspace_size - offset;
}

static void move_bytes_local(uint8_t *destination, const uint8_t *source,
                             size_t count) {
    if (destination == source || count == 0u) {
        return;
    }
    if (destination < source || destination >= source + count) {
        for (size_t index = 0u; index < count; ++index) {
            destination[index] = source[index];
        }
    } else {
        for (size_t index = count; index > 0u; --index) {
            destination[index - 1u] = source[index - 1u];
        }
    }
}

static bool goodix_stage_call(
    const quantized_runtime_stage *stage,
    quantized_runtime_exec_tensor *input0,
    quantized_runtime_exec_tensor *input1,
    quantized_runtime_exec_tensor *output0,
    quantized_runtime_exec_tensor *output1) {
    if (!stage_callable(stage) || input0 == NULL ||
            output0 == NULL) {
        return false;
    }
    /* Stock lays the two {data,range} pairs contiguously before invoking an
     * int8-add record.  Unary/binary stages ignore the unused trailing pair. */
    quantized_runtime_exec_tensor *inputs[4] = {
        input0, input1, output0, output1,
    };
    quantized_runtime_exec_tensor *outputs[2] = {output0, output1};
    (void)stage_invoke(stage, inputs, outputs);
    return true;
}

enum {
    GOODIX_LAYER_OPTIONAL = 0,
    GOODIX_LAYER_MEAN_STAGE,
    GOODIX_LAYER_MEAN_REMAP,
    GOODIX_LAYER_LOGISTIC_CONVERT,
    GOODIX_LAYER_INPUT_STAGE,
    GOODIX_LAYER_MIDDLE_STAGE,
    GOODIX_LAYER_TAIL_STAGE,
    GOODIX_LAYER_FINAL_STAGE
};

static bool add_size_checked(size_t left, size_t right, size_t *result) {
    if (result == NULL || left > SIZE_MAX - right) {
        return false;
    }
    *result = left + right;
    return true;
}

static bool multiply_size_checked(size_t left, size_t right, size_t *result) {
    if (result == NULL || (right != 0u && left > SIZE_MAX / right)) {
        return false;
    }
    *result = left * right;
    return true;
}

static bool layer_stage_call(
    const quantized_runtime_stage *stage,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    if (!stage_callable(stage) || inputs == NULL ||
            outputs == NULL) {
        return false;
    }
    (void)stage_invoke(stage, inputs, outputs);
    return true;
}

bool quantized_runtime_goodix_layer_execute(
    const quantized_runtime_goodix_layer_plan *plan,
    quantized_runtime_exec_tensor *const inputs[2],
    quantized_runtime_exec_tensor *const outputs[2],
    const uint8_t shape[QUANTIZED_RUNTIME_GOODIX_LAYER_SHAPE_BYTES],
    uint8_t *workspace, size_t workspace_size,
    uint8_t *temporary, size_t temporary_size) {
    if (plan == NULL || inputs == NULL || outputs == NULL || shape == NULL ||
            inputs[0] == NULL || inputs[1] == NULL || outputs[0] == NULL ||
            outputs[1] == NULL || inputs[0]->data != workspace ||
            inputs[1]->data == NULL || outputs[1]->data == NULL ||
            workspace == NULL || temporary == NULL || plan->expf_fn == NULL ||
            inputs[0]->dims[1] == 0u || inputs[0]->dims[2] == 0u ||
            !(plan->output_max > plan->output_min)) {
        return false;
    }
    for (size_t index = 0u;
            index < QUANTIZED_RUNTIME_GOODIX_LAYER_SHAPE_BYTES; ++index) {
        if (shape[index] == 0u) {
            return false;
        }
    }
    if (inputs[0]->dims[1] != shape[0] ||
            inputs[0]->dims[2] != shape[1]) {
        return false;
    }
    for (size_t index = GOODIX_LAYER_MEAN_STAGE;
            index < QUANTIZED_RUNTIME_GOODIX_LAYER_STAGE_COUNT; ++index) {
        if (!stage_callable(&plan->stages[index])) {
            return false;
        }
    }
    if (plan->optional_preprocess &&
            !stage_callable(&plan->stages[GOODIX_LAYER_OPTIONAL])) {
        return false;
    }

    size_t temporary_bytes = 0u;
    size_t mean_offset = 0u;
    size_t float_offset = 0u;
    size_t mean_bytes = 0u;
    size_t float_bytes = 0u;
    size_t tail_bytes = 0u;
    size_t input_bytes = 0u;
    size_t tensor_bytes = 0u;
    if (!multiply_size_checked(shape[12], shape[13], &temporary_bytes) ||
            temporary_bytes > temporary_size ||
            !multiply_size_checked(shape[0], shape[1], &mean_offset) ||
            !multiply_size_checked(inputs[0]->dims[1], inputs[0]->dims[2],
                                   &input_bytes) ||
            !multiply_size_checked(inputs[0]->dims[1], sizeof(float),
                                   &mean_bytes) ||
            !add_size_checked(mean_offset, (size_t)shape[0] * sizeof(float),
                              &float_offset) ||
            !multiply_size_checked(shape[4], shape[5], &float_bytes) ||
            !multiply_size_checked(float_bytes, sizeof(float), &float_bytes) ||
            !multiply_size_checked(shape[6], shape[7], &tail_bytes)) {
        return false;
    }
    if (!multiply_size_checked(shape[4], shape[5], &tensor_bytes) ||
            inputs[0]->dims[1] > tensor_bytes) {
        return false;
    }
    size_t required = input_bytes;
    size_t end = 0u;
    if (!add_size_checked(mean_offset, mean_bytes, &end)) {
        return false;
    }
    if (end > required) {
        required = end;
    }
    if (!multiply_size_checked(shape[2], shape[3], &tensor_bytes) ||
            !add_size_checked(float_offset, tensor_bytes, &end)) {
        return false;
    }
    if (end > required) {
        required = end;
    }
    if (!multiply_size_checked(shape[4], shape[5], &tensor_bytes) ||
            !add_size_checked(mean_offset, tensor_bytes, &end)) {
        return false;
    }
    if (end > required) {
        required = end;
    }
    if (!add_size_checked(mean_offset, tail_bytes, &end)) {
        return false;
    }
    if (end > required) {
        required = end;
    }
    if (!add_size_checked(float_offset, float_bytes, &end)) {
        return false;
    }
    if (end > required) {
        required = end;
    }
    if (!multiply_size_checked(shape[8], shape[9], &end)) {
        return false;
    }
    if (end > required) {
        required = end;
    }
    if (!multiply_size_checked(shape[10], shape[11], &tensor_bytes) ||
            !add_size_checked(tail_bytes, tensor_bytes, &end)) {
        return false;
    }
    if (end > required) {
        required = end;
    }
    if (!multiply_size_checked(tail_bytes, 2u, &end)) {
        return false;
    }
    if (end > required) {
        required = end;
    }
    if (required > workspace_size) {
        return false;
    }

    float copied_range_values[2] = {0.0f, 0.0f};
    quantized_runtime_exec_tensor copied_range;
    exec_tensor_initialize(&copied_range, 1u, 1u, 2u, 4u,
                           copied_range_values);
    quantized_runtime_exec_tensor temporary_tensor;
    exec_tensor_initialize(&temporary_tensor, 1u, shape[12], shape[13], 1u,
                           temporary);
    quantized_runtime_exec_tensor *pre_inputs[2] = {inputs[0], inputs[1]};
    quantized_runtime_exec_tensor *pre_outputs[2] = {
        &temporary_tensor, &copied_range,
    };
    if (plan->optional_preprocess) {
        if (!layer_stage_call(&plan->stages[GOODIX_LAYER_OPTIONAL],
                              pre_inputs, pre_outputs)) {
            return false;
        }
    } else {
        move_bytes_local(temporary, (const uint8_t *)inputs[0]->data,
                         temporary_bytes);
        move_bytes_local((uint8_t *)copied_range.data,
                         (const uint8_t *)inputs[1]->data,
                         2u * sizeof(float));
    }

    const uint32_t rows = inputs[0]->dims[1];
    const uint32_t columns = inputs[0]->dims[2];
    const int8_t *row_data = (const int8_t *)inputs[0]->data;
    uint8_t *mean_data = workspace + mean_offset;
    for (uint32_t row = 0u; row < rows; ++row) {
        int32_t sum = 0;
        for (uint32_t column = 0u; column < columns; ++column) {
            sum += row_data[column];
        }
        const float mean = (float)sum / (float)columns;
        const int32_t rounded = (int32_t)(mean +
            (mean > 0.0f ? 0.5f : -0.5f));
        mean_data[row] = (uint8_t)rounded;
        row_data += columns;
    }

    quantized_runtime_exec_tensor mean_tensor;
    exec_tensor_initialize(&mean_tensor, 1u, rows, 1u, 1u, mean_data);
    move_bytes_local((uint8_t *)copied_range.data,
                     (const uint8_t *)inputs[1]->data,
                     2u * sizeof(float));
    quantized_runtime_exec_tensor first_tensor;
    exec_tensor_initialize(&first_tensor, 1u, shape[2], shape[3], 1u,
                           workspace + float_offset);
    quantized_runtime_exec_tensor *mean_inputs[2] = {
        &mean_tensor, &copied_range,
    };
    quantized_runtime_exec_tensor *mean_outputs[2] = {
        &first_tensor, outputs[1],
    };
    if (!layer_stage_call(&plan->stages[GOODIX_LAYER_MEAN_STAGE],
                          mean_inputs, mean_outputs)) {
        return false;
    }

    quantized_runtime_exec_tensor remapped_mean;
    exec_tensor_initialize(&remapped_mean, 1u, shape[4], shape[5], 1u,
                           mean_data);
    quantized_runtime_exec_tensor *remap_inputs[2] = {
        &first_tensor, outputs[1],
    };
    quantized_runtime_exec_tensor *remap_outputs[2] = {
        &remapped_mean, &copied_range,
    };
    if (!layer_stage_call(&plan->stages[GOODIX_LAYER_MEAN_REMAP],
                          remap_inputs, remap_outputs)) {
        return false;
    }

    quantized_runtime_exec_tensor logistic_tensor;
    exec_tensor_initialize(&logistic_tensor, 1u, shape[4], shape[5], 4u,
                           workspace + float_offset);
    quantized_runtime_exec_tensor *logistic_outputs[1] = {&logistic_tensor};
    if (!layer_stage_call(&plan->stages[GOODIX_LAYER_LOGISTIC_CONVERT],
                          remap_outputs, logistic_outputs)) {
        return false;
    }
    uint8_t *logistic = (uint8_t *)logistic_tensor.data;
    for (uint32_t row = 0u; row < rows; ++row) {
        float exponent = -load_f32_le(logistic + (size_t)row * sizeof(float));
        if ((int32_t)f32_to_bits(exponent) >=
                QUANTIZED_RUNTIME_SOFTMAX_CAP_BITS) {
            exponent = QUANTIZED_RUNTIME_SOFTMAX_CAP;
        }
        store_f32_le(logistic + (size_t)row * sizeof(float),
                     1.0f / (plan->expf_fn(exponent) + 1.0f));
    }

    float *input_range = (float *)inputs[1]->data;
    const float old_min = input_range[0];
    const float old_max = input_range[1];
    input_range[0] = plan->output_min;
    input_range[1] = plan->output_max;
    const float old_step = (old_max - old_min) / 255.0f;
    const float new_step =
        (plan->output_max - plan->output_min) / 255.0f;
    int8_t *adjusted = (int8_t *)inputs[0]->data;
    for (uint32_t row = 0u; row < shape[0]; ++row) {
        const float probability =
            load_f32_le(logistic + (size_t)row * sizeof(float));
        const float scale = probability * old_step / new_step;
        const float bias =
            (plan->output_min - probability * old_min) / new_step;
        for (uint32_t column = 0u; column < shape[1]; ++column) {
            const float value = bias +
                (float)((int32_t)adjusted[column] + 128) * scale;
            const int32_t rounded = (int32_t)(value +
                (value > 0.0f ? 0.5f : -0.5f));
            if (rounded < 0) {
                adjusted[column] = INT8_MIN;
            } else if (rounded > 255) {
                adjusted[column] = INT8_MAX;
            } else {
                adjusted[column] = (int8_t)(rounded - 128);
            }
        }
        adjusted += shape[1];
    }

    quantized_runtime_exec_tensor input_stage_tensor;
    exec_tensor_initialize(&input_stage_tensor, 1u, shape[6], shape[7], 1u,
                           mean_data);
    quantized_runtime_exec_tensor *main_inputs[2] = {inputs[0], inputs[1]};
    quantized_runtime_exec_tensor *main_outputs[2] = {
        &input_stage_tensor, outputs[1],
    };
    if (!layer_stage_call(&plan->stages[GOODIX_LAYER_INPUT_STAGE],
                          main_inputs, main_outputs)) {
        return false;
    }
    move_bytes_local(workspace + tail_bytes,
                     (const uint8_t *)input_stage_tensor.data, tail_bytes);
    input_stage_tensor.data = workspace + tail_bytes;

    exec_tensor_initialize(inputs[0], 1u, shape[8], shape[9], 1u, workspace);
    quantized_runtime_exec_tensor *middle_inputs[2] = {
        &input_stage_tensor, outputs[1],
    };
    quantized_runtime_exec_tensor *middle_outputs[2] = {
        inputs[0], inputs[1],
    };
    if (!layer_stage_call(&plan->stages[GOODIX_LAYER_MIDDLE_STAGE],
                          middle_inputs, middle_outputs)) {
        return false;
    }

    exec_tensor_initialize(&input_stage_tensor, 1u, shape[10], shape[11], 1u,
                           workspace + tail_bytes);
    quantized_runtime_exec_tensor *tail_inputs[2] = {inputs[0], inputs[1]};
    quantized_runtime_exec_tensor *tail_outputs[2] = {
        &input_stage_tensor, outputs[1],
    };
    if (!layer_stage_call(&plan->stages[GOODIX_LAYER_TAIL_STAGE],
                          tail_inputs, tail_outputs)) {
        return false;
    }
    quantized_runtime_exec_tensor *final_inputs[4] = {
        &input_stage_tensor, outputs[1], &temporary_tensor, &copied_range,
    };
    if (!layer_stage_call(&plan->stages[GOODIX_LAYER_FINAL_STAGE],
                          final_inputs, outputs)) {
        return false;
    }
    return true;
}

static bool goodix_layer_block_aligned(
    const quantized_runtime *rt, uint8_t *destination, uint8_t byte0,
    uint8_t byte1, uint8_t byte2, uint8_t byte3, uint8_t byte4,
    uint8_t byte5, uint8_t byte6, uint8_t byte7,
    uint32_t *target_cursor, size_t *consumed_words) {
    const uint32_t before = *target_cursor;
    quantized_runtime_aligned_descriptor_construct(
        rt, destination, byte0, byte1, byte2, byte3, byte4, byte5,
        byte6, 1u, byte7, target_cursor, 0.0f);
    if (*target_cursor < before) {
        return false;
    }
    *consumed_words += (size_t)(*target_cursor - before) / sizeof(uint32_t);
    return true;
}

bool quantized_runtime_goodix_layer_block_build(
    const quantized_runtime *rt,
    quantized_runtime_goodix_layer_block *block,
    const uint32_t *model_words, size_t model_word_count,
    uint32_t model_base_address,
    const uint8_t shape[QUANTIZED_RUNTIME_GOODIX_LAYER_BLOCK_SHAPE_BYTES],
    size_t *consumed_words, uint32_t *model_end_address) {
    if (consumed_words != NULL) {
        *consumed_words = 0u;
    }
    if (model_end_address != NULL) {
        *model_end_address = model_base_address;
    }
    if (block == NULL || model_words == NULL || shape == NULL) {
        return false;
    }
    zero_bytes(block->bytes, sizeof(block->bytes));
    uint32_t target_cursor = model_base_address;
    size_t consumed = 0u;

    if (!goodix_layer_block_aligned(
            rt, block->bytes + 0x00u, 1u, 1u, 0u, 0u,
            shape[0], shape[1], 1u, 1u, &target_cursor, &consumed) ||
            !goodix_layer_block_aligned(
                rt, block->bytes + 0x18u, 1u, 1u, 0u, 0u,
                shape[1], shape[2], 1u, 1u,
                &target_cursor, &consumed) ||
            consumed > model_word_count ||
            model_word_count - consumed < 2u) {
        zero_bytes(block->bytes, sizeof(block->bytes));
        return false;
    }
    const uint32_t *host_cursor = model_words + consumed;
    uintptr_t quantizer_descriptor[3];
    quantized_runtime_quantizer_descriptor_construct(
        quantizer_descriptor, &host_cursor);
    store_native_words_as_u32(block->bytes + 0x30u,
                              quantizer_descriptor, 3u);
    consumed += 2u;
    if (target_cursor > UINT32_MAX - 2u * sizeof(uint32_t)) {
        zero_bytes(block->bytes, sizeof(block->bytes));
        return false;
    }
    target_cursor += 2u * sizeof(uint32_t);

    if (!goodix_layer_block_aligned(
            rt, block->bytes + 0x3Cu, 1u, 1u, 0u, 0u,
            shape[2], shape[3], 1u, 1u, &target_cursor, &consumed) ||
            !goodix_layer_block_aligned(
                rt, block->bytes + 0x54u, 3u, 1u, 1u, 1u,
                shape[3], shape[4], shape[4], 1u,
                &target_cursor, &consumed) ||
            !goodix_layer_block_aligned(
                rt, block->bytes + 0x6Cu, 1u, 1u, 0u, 0u,
                shape[4], shape[5], 1u, 0u,
                &target_cursor, &consumed)) {
        zero_bytes(block->bytes, sizeof(block->bytes));
        return false;
    }
    store_u32_le(block->bytes + 0x84u, shape[6] != 0u ? 1u : 0u);
    if (shape[6] != 0u && !goodix_layer_block_aligned(
            rt, block->bytes + 0x88u, 1u, 1u, 0u, 0u,
            shape[0], shape[6], 1u, 0u, &target_cursor, &consumed)) {
        zero_bytes(block->bytes, sizeof(block->bytes));
        return false;
    }
    if (consumed > model_word_count || model_word_count - consumed < 2u) {
        zero_bytes(block->bytes, sizeof(block->bytes));
        return false;
    }
    host_cursor = model_words + consumed;
    quantized_runtime_cursor_pair_add_descriptor_construct(
        block->bytes + 0xA0u, &host_cursor);
    consumed += 2u;
    if (target_cursor > UINT32_MAX - 2u * sizeof(uint32_t)) {
        zero_bytes(block->bytes, sizeof(block->bytes));
        return false;
    }
    target_cursor += 2u * sizeof(uint32_t);
    if (consumed_words != NULL) {
        *consumed_words = consumed;
    }
    if (model_end_address != NULL) {
        *model_end_address = target_cursor;
    }
    return true;
}

bool quantized_runtime_goodix_second_graph_build(
    const quantized_runtime *rt,
    quantized_runtime_goodix_second_graph *graph,
    const uint32_t *model_words, size_t model_word_count,
    uint32_t model_base_address, uintptr_t release_context_pair_vector,
    size_t *consumed_words, uint32_t *model_end_address) {
    static const uint8_t shapes[5]
        [QUANTIZED_RUNTIME_GOODIX_LAYER_BLOCK_SHAPE_BYTES] = {
            {10u, 2u, 10u, 1u, 1u, 1u, 1u},
            {4u, 1u, 4u, 1u, 1u, 1u, 1u},
            {24u, 2u, 24u, 15u, 15u, 24u, 0u},
            {24u, 8u, 24u, 16u, 16u, 16u, 16u},
            {16u, 1u, 16u, 5u, 5u, 1u, 1u},
        };
    static const size_t block_offsets[5] = {
        0x028u, 0x0F0u, 0x1BCu, 0x26Cu, 0x31Cu,
    };
    if (consumed_words != NULL) {
        *consumed_words = 0u;
    }
    if (model_end_address != NULL) {
        *model_end_address = model_base_address;
    }
    if (graph == NULL || model_words == NULL ||
            model_word_count <
                QUANTIZED_RUNTIME_GOODIX_SECOND_GRAPH_MODEL_WORDS) {
        return false;
    }
    zero_bytes(graph->bytes, sizeof(graph->bytes));
    store_u32_le(graph->bytes, 6u);
    const uint32_t *host_cursor = model_words;
    uintptr_t quantizer_descriptor[3];
    quantized_runtime_quantizer_descriptor_construct(
        quantizer_descriptor, &host_cursor);
    store_native_words_as_u32(graph->bytes + 0x004u,
                              quantizer_descriptor, 3u);
    size_t consumed = 2u;
    if (model_base_address > UINT32_MAX - 2u * sizeof(uint32_t)) {
        zero_bytes(graph->bytes, sizeof(graph->bytes));
        return false;
    }
    uint32_t target_cursor =
        model_base_address + 2u * sizeof(uint32_t);
    if (!goodix_layer_block_aligned(
            rt, graph->bytes + 0x010u, 5u, 1u, 2u, 2u,
            4u, 10u, 1u, 0u, &target_cursor, &consumed)) {
        zero_bytes(graph->bytes, sizeof(graph->bytes));
        return false;
    }

    const uint8_t top_rows[2] = {1u, 4u};
    const uint8_t top_columns[2] = {4u, 24u};
    const size_t top_offsets[2] = {0x0D8u, 0x1A4u};
    for (size_t index = 0u; index < 5u; ++index) {
        quantized_runtime_goodix_layer_block block;
        size_t block_words = 0u;
        uint32_t block_end = target_cursor;
        if (consumed > model_word_count ||
                !quantized_runtime_goodix_layer_block_build(
                    rt, &block, model_words + consumed,
                    model_word_count - consumed, target_cursor,
                    shapes[index], &block_words, &block_end)) {
            zero_bytes(graph->bytes, sizeof(graph->bytes));
            return false;
        }
        move_bytes_local(graph->bytes + block_offsets[index], block.bytes,
                         sizeof(block.bytes));
        consumed += block_words;
        target_cursor = block_end;
        if (index == 0u || index == 1u) {
            const size_t top = index;
            if (!goodix_layer_block_aligned(
                    rt, graph->bytes + top_offsets[top], 5u, 1u, 2u, 2u,
                    top_rows[top], top_columns[top], 1u, 0u,
                    &target_cursor, &consumed)) {
                zero_bytes(graph->bytes, sizeof(graph->bytes));
                return false;
            }
            if (index == 1u) {
                store_u32_le(graph->bytes + 0x1A0u,
                             (uint32_t)release_context_pair_vector);
            }
        }
    }
    quantized_runtime_packed_pool_descriptor_initialize(
        graph->bytes + 0x3CCu, 1u, 3u, 3u, 0u);
    store_u32_le(graph->bytes + 0x3D4u,
                 (uint32_t)quantized_runtime_executor_vector_30534(rt));
    if (consumed != QUANTIZED_RUNTIME_GOODIX_SECOND_GRAPH_MODEL_WORDS ||
            target_cursor !=
                model_base_address + (uint32_t)consumed * sizeof(uint32_t)) {
        zero_bytes(graph->bytes, sizeof(graph->bytes));
        return false;
    }
    if (consumed_words != NULL) {
        *consumed_words = consumed;
    }
    if (model_end_address != NULL) {
        *model_end_address = target_cursor;
    }
    return true;
}

static bool goodix_second_plan_stage(
    const quantized_runtime *rt,
    const quantized_runtime_goodix_second_graph *graph,
    quantized_runtime_stage *stage, size_t descriptor_offset,
    size_t token_offset, quantized_runtime_stage_token_resolver_fn resolve,
    void *resolve_context, bool required) {
    if (descriptor_offset >= sizeof(graph->bytes) ||
            token_offset + 4u > sizeof(graph->bytes)) {
        return false;
    }
    const uint32_t token = load_u32_le(graph->bytes + token_offset);
    stage->descriptor = graph->bytes + descriptor_offset;
    stage->execute = token != 0u ? resolve(resolve_context, token) : NULL;
    if (stage->execute != NULL) {
        /* Explicit resolvers may replace even source-local target adapters;
         * host fixture plans use this to avoid dereferencing target records. */
    } else if (token == (uint32_t)(uintptr_t)
            &quantized_runtime_float_to_int8_quantize) {
        stage->runtime = rt;
        stage->adapter = QUANTIZED_RUNTIME_STAGE_QUANTIZE_WITH_RUNTIME;
    } else if (token == (uint32_t)(uintptr_t)
                   &quantized_runtime_int8_add_execute) {
        stage->runtime = rt;
        stage->adapter = QUANTIZED_RUNTIME_STAGE_INT8_ADD_WITH_RUNTIME;
    } else if (token == (uint32_t)(uintptr_t)
                   &quantized_runtime_float_softmax_execute) {
        stage->runtime = rt;
        stage->adapter = QUANTIZED_RUNTIME_STAGE_SOFTMAX_WITH_RUNTIME;
    }
    return !required || stage_callable(stage);
}

bool quantized_runtime_goodix_second_executor_plan_build(
    const quantized_runtime *rt,
    const quantized_runtime_goodix_second_graph *graph,
    quantized_runtime_goodix_second_executor_plan *plan,
    quantized_runtime_stage_token_resolver_fn resolve,
    void *resolve_context,
    quantized_runtime_multi_stage_token_resolver_fn resolve_multi,
    void *resolve_multi_context) {
    if (rt == NULL || graph == NULL || plan == NULL || resolve == NULL ||
            resolve_multi == NULL || load_u32_le(graph->bytes) != 6u ||
            rt->providers.expf_fn == NULL) {
        return false;
    }
    zero_bytes((uint8_t *)plan, sizeof(*plan));
    static const uint16_t direct_descriptors[
        QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_STAGE_COUNT] = {
        0x004u, 0x010u, 0x0D8u, 0x1A4u, 0x3CCu, 0x3D4u,
    };
    static const uint16_t direct_tokens[
        QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_STAGE_COUNT] = {
        0x00Cu, 0x024u, 0x0ECu, 0x1B8u, 0x3D0u, 0x3D4u,
    };
    for (size_t index = 0u;
            index < QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_STAGE_COUNT;
            ++index) {
        if (!goodix_second_plan_stage(
                rt, graph, &plan->stages[index], direct_descriptors[index],
                direct_tokens[index], resolve, resolve_context, true)) {
            zero_bytes((uint8_t *)plan, sizeof(*plan));
            return false;
        }
    }

    const uint32_t merge_token = load_u32_le(graph->bytes + 0x1A0u);
    plan->merge_four.descriptor = graph->bytes + 0x1A0u;
    plan->merge_four.execute = merge_token != 0u
        ? resolve_multi(resolve_multi_context, merge_token) : NULL;
    if (plan->merge_four.execute == NULL) {
        zero_bytes((uint8_t *)plan, sizeof(*plan));
        return false;
    }

    static const uint16_t block_offsets[
        QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_LAYER_COUNT] = {
        0x028u, 0x0F0u, 0x1BCu, 0x26Cu, 0x31Cu,
    };
    static const uint8_t descriptor_offsets[
        QUANTIZED_RUNTIME_GOODIX_LAYER_STAGE_COUNT] = {
        0x88u, 0x00u, 0x18u, 0x30u, 0x3Cu, 0x54u, 0x6Cu, 0xA0u,
    };
    static const uint8_t token_offsets[
        QUANTIZED_RUNTIME_GOODIX_LAYER_STAGE_COUNT] = {
        0x9Cu, 0x14u, 0x2Cu, 0x38u, 0x50u, 0x68u, 0x80u, 0xACu,
    };
    for (size_t layer = 0u;
            layer < QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_LAYER_COUNT;
            ++layer) {
        quantized_runtime_goodix_layer_plan *layer_plan =
            &plan->layers[layer];
        const size_t block = block_offsets[layer];
        layer_plan->optional_preprocess =
            load_u32_le(graph->bytes + block + 0x84u) != 0u;
        layer_plan->output_min = load_f32_le(graph->bytes + block + 0x30u);
        layer_plan->output_max = load_f32_le(graph->bytes + block + 0x34u);
        layer_plan->expf_fn = rt->providers.expf_fn;
        if (!(layer_plan->output_max > layer_plan->output_min)) {
            zero_bytes((uint8_t *)plan, sizeof(*plan));
            return false;
        }
        for (size_t stage = 0u;
                stage < QUANTIZED_RUNTIME_GOODIX_LAYER_STAGE_COUNT;
                ++stage) {
            const bool required = stage != 0u ||
                layer_plan->optional_preprocess;
            if (!goodix_second_plan_stage(
                    rt, graph, &layer_plan->stages[stage],
                    block + descriptor_offsets[stage],
                    block + token_offsets[stage], resolve, resolve_context,
                    required)) {
                zero_bytes((uint8_t *)plan, sizeof(*plan));
                return false;
            }
        }
    }
    return true;
}

enum {
    GOODIX_SECOND_INITIAL_CONVERT = 0,
    GOODIX_SECOND_EXPAND_10,
    GOODIX_SECOND_BLOCK_EXPAND_4,
    GOODIX_SECOND_EXPAND_24,
    GOODIX_SECOND_REDUCE_60,
    GOODIX_SECOND_FLOAT_CONVERT
};

static const uint8_t goodix_second_layer_shapes
    [QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_LAYER_COUNT]
    [QUANTIZED_RUNTIME_GOODIX_LAYER_SHAPE_BYTES] = {
        {10u, 180u, 2u, 1u, 10u, 1u, 1u, 180u,
         1u, 180u, 1u, 180u, 1u, 180u},
        {4u, 180u, 1u, 1u, 4u, 1u, 1u, 180u,
         1u, 180u, 1u, 180u, 1u, 180u},
        {24u, 180u, 2u, 1u, 24u, 1u, 15u, 180u,
         15u, 180u, 24u, 180u, 24u, 180u},
        {24u, 180u, 8u, 1u, 24u, 1u, 16u, 180u,
         16u, 180u, 16u, 180u, 16u, 180u},
        {16u, 180u, 1u, 1u, 16u, 1u, 5u, 180u,
         5u, 180u, 1u, 180u, 1u, 180u},
};

static bool second_layer_plan_valid(
    const quantized_runtime_goodix_layer_plan *plan) {
    if (plan == NULL || plan->optional_preprocess || plan->expf_fn == NULL ||
            !(plan->output_max > plan->output_min)) {
        return false;
    }
    for (size_t index = 1u;
            index < QUANTIZED_RUNTIME_GOODIX_LAYER_STAGE_COUNT; ++index) {
        if (!stage_callable(&plan->stages[index])) {
            return false;
        }
    }
    return true;
}

bool quantized_runtime_goodix_second_executor_execute(
    const quantized_runtime_goodix_second_executor_plan *plan,
    const quantized_runtime_goodix_second_executor_io *io,
    size_t *output_bytes) {
    if (output_bytes != NULL) {
        *output_bytes = 0u;
    }
    if (plan == NULL || io == NULL || io->workspace == NULL ||
            io->temporary == NULL || io->output == NULL ||
            io->workspace_size <
                QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_WORKSPACE_BYTES ||
            io->temporary_size <
                QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_TEMPORARY_BYTES ||
            io->output_capacity <
                QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_OUTPUT_BYTES ||
            plan->merge_four.execute == NULL) {
        return false;
    }
    for (size_t index = 0u;
            index < QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_STAGE_COUNT;
            ++index) {
        if (!stage_callable(&plan->stages[index])) {
            return false;
        }
    }
    for (size_t index = 0u;
            index < QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_LAYER_COUNT;
            ++index) {
        if (!second_layer_plan_valid(&plan->layers[index])) {
            return false;
        }
    }

    uint8_t *const base = io->workspace;
    float range_values[4][2] = {{0.0f, 0.0f}};
    quantized_runtime_exec_tensor ranges[4] = {{0}};
    for (size_t index = 0u; index < 4u; ++index) {
        ranges[index].data = range_values[index];
    }

    quantized_runtime_exec_tensor a;
    quantized_runtime_exec_tensor b;
    quantized_runtime_exec_tensor c;
    quantized_runtime_exec_tensor d;
    quantized_runtime_exec_tensor e;
    quantized_runtime_exec_tensor *stage_inputs[8] = {NULL};
    quantized_runtime_exec_tensor *stage_outputs[2] = {NULL};

    exec_tensor_initialize(&a, 1u, 7u, 180u, 4u, base);
    stage_inputs[0] = &a;
    stage_outputs[0] = &a;
    stage_outputs[1] = &ranges[0];
    if (!layer_stage_call(&plan->stages[GOODIX_SECOND_INITIAL_CONVERT],
                          stage_inputs, stage_outputs)) {
        return false;
    }
    move_bytes_local(base + 0x4ECu, base, 0x2D0u);

    exec_tensor_initialize(&a, 1u, 4u, 180u, 1u, base + 0x4ECu);
    exec_tensor_initialize(&b, 1u, 10u, 180u, 1u, base + 0x4ECu);
    stage_inputs[0] = &a;
    stage_inputs[1] = &ranges[0];
    stage_outputs[0] = &b;
    stage_outputs[1] = &ranges[1];
    if (!layer_stage_call(&plan->stages[GOODIX_SECOND_EXPAND_10],
                          stage_inputs, stage_outputs)) {
        return false;
    }

    exec_tensor_initialize(&c, 1u, 1u, 180u, 1u, base);
    quantized_runtime_exec_tensor *layer_inputs[2] = {&b, &ranges[1]};
    quantized_runtime_exec_tensor *layer_outputs[2] = {&c, &ranges[3]};
    if (!quantized_runtime_goodix_layer_execute(
            &plan->layers[0], layer_inputs, layer_outputs,
            goodix_second_layer_shapes[0], base + 0x4ECu,
            io->workspace_size - 0x4ECu, io->temporary,
            io->temporary_size)) {
        return false;
    }

    for (size_t index = 0u; index < 3u; ++index) {
        const size_t block = index * 180u;
        move_bytes_local(base + 0x4ECu, base + block + 0x2D0u, 180u);
        exec_tensor_initialize(&a, 1u, 1u, 180u, 1u, base + 0x4ECu);
        exec_tensor_initialize(&b, 1u, 4u, 180u, 1u, base + 0x4ECu);
        stage_inputs[0] = &a;
        stage_inputs[1] = &ranges[0];
        stage_outputs[0] = &b;
        stage_outputs[1] = &ranges[1];
        if (!layer_stage_call(
                &plan->stages[GOODIX_SECOND_BLOCK_EXPAND_4],
                stage_inputs, stage_outputs)) {
            return false;
        }
        exec_tensor_initialize(&c, 1u, 1u, 180u, 1u,
                               base + block + 180u);
        layer_inputs[0] = &b;
        layer_inputs[1] = &ranges[1];
        layer_outputs[0] = &c;
        layer_outputs[1] = &ranges[2];
        if (!quantized_runtime_goodix_layer_execute(
                &plan->layers[1], layer_inputs, layer_outputs,
                goodix_second_layer_shapes[1], base + 0x4ECu,
                io->workspace_size - 0x4ECu, io->temporary,
                io->temporary_size)) {
            return false;
        }
    }

    exec_tensor_initialize(&a, 1u, 1u, 180u, 1u, base);
    exec_tensor_initialize(&b, 1u, 1u, 180u, 1u, base + 0xB4u);
    exec_tensor_initialize(&c, 1u, 1u, 180u, 1u, base + 0x168u);
    exec_tensor_initialize(&d, 1u, 1u, 180u, 1u, base + 0x21Cu);
    exec_tensor_initialize(&e, 1u, 4u, 180u, 1u, base);
    stage_inputs[0] = &a;
    stage_inputs[1] = &ranges[3];
    stage_inputs[2] = &b;
    stage_inputs[3] = &ranges[2];
    stage_inputs[4] = &c;
    stage_inputs[5] = &ranges[2];
    stage_inputs[6] = &d;
    stage_inputs[7] = &ranges[2];
    stage_outputs[0] = &e;
    stage_outputs[1] = &ranges[0];
    (void)plan->merge_four.execute(plan->merge_four.descriptor, stage_inputs,
                                   stage_outputs, 4u);
    move_bytes_local((uint8_t *)ranges[2].data,
                     (const uint8_t *)ranges[3].data, 2u * sizeof(float));

    exec_tensor_initialize(&a, 1u, 4u, 180u, 1u, base);
    exec_tensor_initialize(&b, 1u, 24u, 180u, 1u, base + 0x2D0u);
    stage_inputs[0] = &a;
    stage_inputs[1] = &ranges[0];
    stage_outputs[0] = &b;
    stage_outputs[1] = &ranges[1];
    if (!layer_stage_call(&plan->stages[GOODIX_SECOND_EXPAND_24],
                          stage_inputs, stage_outputs)) {
        return false;
    }
    move_bytes_local(base, base + 0xB4u, 0x12FCu);

    const uint32_t layer_rows[3] = {24u, 16u, 1u};
    quantized_runtime_exec_tensor *current_data = &b;
    quantized_runtime_exec_tensor *next_data = &c;
    quantized_runtime_exec_tensor *current_range = &ranges[1];
    quantized_runtime_exec_tensor *next_range = &ranges[3];
    exec_tensor_initialize(current_data, 1u, 24u, 180u, 1u,
                           base + 0x21Cu);
    for (size_t index = 0u; index < 3u; ++index) {
        exec_tensor_initialize(next_data, 1u, layer_rows[index], 180u, 1u,
                               base + 0x21Cu);
        layer_inputs[0] = current_data;
        layer_inputs[1] = current_range;
        layer_outputs[0] = next_data;
        layer_outputs[1] = next_range;
        if (!quantized_runtime_goodix_layer_execute(
                &plan->layers[index + 2u], layer_inputs, layer_outputs,
                goodix_second_layer_shapes[index + 2u], base + 0x21Cu,
                io->workspace_size - 0x21Cu, io->temporary,
                io->temporary_size)) {
            return false;
        }
        quantized_runtime_exec_tensor *swap_data = current_data;
        current_data = next_data;
        next_data = swap_data;
        quantized_runtime_exec_tensor *swap_range = current_range;
        current_range = next_range;
        next_range = swap_range;
    }

    exec_tensor_initialize(&c, 1u, 4u, 180u, 1u, base);
    exec_tensor_initialize(&b, 1u, 4u, 60u, 1u, base);
    stage_inputs[0] = &c;
    stage_outputs[0] = &b;
    if (!layer_stage_call(&plan->stages[GOODIX_SECOND_REDUCE_60],
                          stage_inputs, stage_outputs)) {
        return false;
    }
    exec_tensor_initialize(&c, 1u, 1u, 60u, 1u, base + 0xB4u);
    exec_tensor_initialize(&b, 1u, 1u, 60u, 4u, base + 0xF0u);
    stage_inputs[0] = &c;
    stage_inputs[1] = current_range;
    stage_outputs[0] = &b;
    if (!layer_stage_call(&plan->stages[GOODIX_SECOND_FLOAT_CONVERT],
                          stage_inputs, stage_outputs)) {
        return false;
    }
    exec_tensor_initialize(&a, 1u, 3u, 60u, 1u, base);
    exec_tensor_initialize(&b, 1u, 3u, 60u, 4u, base + 0x1E0u);
    stage_inputs[0] = &a;
    stage_inputs[1] = &ranges[3];
    stage_outputs[0] = &b;
    if (!layer_stage_call(&plan->stages[GOODIX_SECOND_FLOAT_CONVERT],
                          stage_inputs, stage_outputs)) {
        return false;
    }
    move_bytes_local(io->output, base + 0xF0u,
                     QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_OUTPUT_BYTES);
    if (output_bytes != NULL) {
        *output_bytes =
            QUANTIZED_RUNTIME_GOODIX_SECOND_EXECUTOR_OUTPUT_BYTES;
    }
    return true;
}

bool quantized_runtime_goodix_executor_execute(
    const quantized_runtime_goodix_executor_plan *plan,
    const quantized_runtime_goodix_executor_io *io,
    size_t *output_bytes) {
    if (output_bytes != NULL) {
        *output_bytes = 0u;
    }
    if (plan == NULL || io == NULL || io->workspace == NULL ||
            io->tail_input == NULL || io->tail_input_size < 16u ||
            io->output == NULL || plan->mode > 2u) {
        return false;
    }
    for (size_t index = 1u;
            index < QUANTIZED_RUNTIME_GOODIX_EXECUTOR_STAGE_COUNT - 1u;
            ++index) {
        if (!stage_callable(&plan->stages[index])) {
            return false;
        }
    }
    if ((plan->mode == 0u &&
         !stage_callable(&plan->stages[GOODIX_EXEC_BOOTSTRAP])) ||
            (plan->mode == 2u &&
             !stage_callable(&plan->stages[GOODIX_EXEC_TAIL_OPTIONAL]))) {
        return false;
    }

    uint8_t *const base = io->workspace;
    const uint32_t width = plan->mode == 0u ? 27u : 32u;
    if (!workspace_contains(io->workspace_size, 0x18Cu, 4u, 99u, 1u)) {
        return false;
    }

    float range_in_values[2] = {0.0f, 1.0f};
    float range_out_values[2] = {0.0f, 0.0f};
    quantized_runtime_exec_tensor range_in;
    quantized_runtime_exec_tensor range_out;
    exec_tensor_initialize(&range_in, 1u, 1u, 2u, 4u, range_in_values);
    exec_tensor_initialize(&range_out, 1u, 1u, 2u, 4u, range_out_values);

    quantized_runtime_exec_tensor a;
    quantized_runtime_exec_tensor b;
    quantized_runtime_exec_tensor c;
    quantized_runtime_exec_tensor saved;
    if (plan->mode == 0u) {
        exec_tensor_initialize(&a, 1u, 4u, 99u, 4u, base);
        exec_tensor_initialize(&b, 1u, 4u, 99u, 1u, base);
        if (!goodix_stage_call(&plan->stages[GOODIX_EXEC_BOOTSTRAP],
                               &a, &range_in, &b, &range_out)) {
            return false;
        }
        move_bytes_local(base + 0x18Cu, base, 0x18Cu);
    }

    exec_tensor_initialize(&a, 1u, 4u, 99u, 1u, base + 0x18Cu);
    exec_tensor_initialize(&b, 1u, width, 99u, 1u, base + 0x18Cu);
    if (!goodix_stage_call(&plan->stages[GOODIX_EXEC_EXPAND_99],
                           &a, &range_in, &b, &range_out)) {
        return false;
    }
    exec_tensor_initialize(&a, 1u, width, 49u, 1u, b.data);
    if (!goodix_stage_call(&plan->stages[GOODIX_EXEC_REDUCE_49],
                           &b, &range_out, &a, &range_in)) {
        return false;
    }

    uint8_t shape_49[6] = {1u, 49u, 1u, 49u, (uint8_t)width, 49u};
    if (plan->mode == 0u) {
        shape_49[0] = 14u;
    }
    quantized_runtime_exec_tensor *quant_inputs[2] = {&a, &range_in};
    quantized_runtime_exec_tensor *quant_outputs[2] = {&b, &range_out};
    const size_t span_49 = plan->mode == 0u ? (size_t)width * 49u : 0x620u;
    if (!quantized_runtime_goodix_u8_three_stage_execute(
            &plan->quantized_49, quant_inputs, quant_outputs, shape_49,
            span_49, base + 0x18Cu, io->workspace_size - 0x18Cu) ||
            !goodix_stage_call(&plan->stages[GOODIX_EXEC_MERGE_49],
                               &b, &range_out, &b, &range_in)) {
        return false;
    }

    exec_tensor_initialize(&a, 1u, width, 24u, 1u, base + 0x18Cu);
    if (!goodix_stage_call(&plan->stages[GOODIX_EXEC_REDUCE_24],
                           &b, &range_in, &a, &range_out)) {
        return false;
    }
    uint8_t shape_24[6] = {2u, 24u, 2u, 24u, (uint8_t)width, 24u};
    if (plan->mode == 0u) {
        shape_24[0] = 7u;
    }
    quant_inputs[0] = &a;
    quant_inputs[1] = &range_out;
    quant_outputs[0] = &b;
    quant_outputs[1] = &range_in;
    const size_t span_24 = plan->mode == 0u ? (size_t)width * 24u : 0x620u;
    if (!quantized_runtime_goodix_u8_three_stage_execute(
            &plan->quantized_24, quant_inputs, quant_outputs, shape_24,
            span_24, base + 0x18Cu, io->workspace_size - 0x18Cu) ||
            !goodix_stage_call(&plan->stages[GOODIX_EXEC_MERGE_24],
                               &b, &range_in, &b, &range_out)) {
        return false;
    }

    size_t bank = 0x7ACu;
    if (plan->mode == 0u) {
        bank = 0x18Cu + (size_t)width * 48u;
    }
    if (!workspace_contains(io->workspace_size, bank, width, 12u, 4u)) {
        return false;
    }
    exec_tensor_initialize(&a, 1u, width, 12u, 1u, base + bank);
    if (!goodix_stage_call(&plan->stages[GOODIX_EXEC_REDUCE_12],
                           &b, &range_out, &a, &range_in)) {
        return false;
    }
    exec_tensor_initialize(&b, 1u, width, 12u, 4u, base + 0x18Cu);
    if (!goodix_stage_call(&plan->stages[GOODIX_EXEC_FLOAT_CONVERT],
                           &a, &range_in, &b, &range_out)) {
        return false;
    }
    exec_tensor_initialize(&a, 1u, 1u, 12u, 4u, base + bank);
    const bool five_ok = plan->mode == 0u
        ? quantized_runtime_goodix_five_stage_27_execute(
              &plan->five_stage_27, &b, &a, base + bank,
              io->workspace_size - bank)
        : quantized_runtime_goodix_five_stage_32_execute(
              &plan->five_stage_32, &b, &a, base + bank,
              io->workspace_size - bank);
    if (!five_ok ||
            !goodix_stage_call(&plan->stages[GOODIX_EXEC_BRANCH_MERGE],
                               &b, &a, &b, &range_out)) {
        return false;
    }

    const uint8_t branch_width = plan->mode == 1u ? 4u : 8u;
    uint8_t shape_12[6] = {1u, 12u, 1u, 12u, branch_width, 12u};
    if (plan->mode == 0u) {
        shape_12[0] = 11u;
    }
    exec_tensor_initialize(&a, 1u, branch_width, 12u, 4u, base + bank);
    if (!quantized_runtime_goodix_f32_three_stage_execute(
            &plan->float_12, &b, &a, shape_12, 49u * 56u,
            base + bank, io->workspace_size - bank)) {
        return false;
    }
    const size_t branch_bank = bank + (plan->mode == 0u ? 0x180u : 0x620u);
    if (!workspace_contains(io->workspace_size, branch_bank,
                            branch_width, 12u, 4u)) {
        return false;
    }
    exec_tensor_initialize(&c, 1u, branch_width, 12u, 4u,
                           base + branch_bank);
    if (!goodix_stage_call(
            &plan->stages[GOODIX_EXEC_AFTER_FLOAT_PIPELINE],
            &b, &range_out, &c, &range_in)) {
        return false;
    }
    saved = a;
    a.data = base + 0x18Cu;
    if (!goodix_stage_call(&plan->stages[GOODIX_EXEC_REMAP],
                           &saved, &c, &a, &range_out)) {
        return false;
    }

    const size_t tail_bank = plan->mode == 0u ? 0x30Cu : 0x7ACu;
    if (!workspace_contains(io->workspace_size, tail_bank, 4u, 1u, 4u)) {
        return false;
    }
    move_bytes_local(base + tail_bank, io->tail_input, 16u);
    exec_tensor_initialize(&b, 1u, 4u, 1u, 4u, base + tail_bank);
    const uint32_t head_width = plan->mode == 0u
        ? plan->head_width_mode0 : plan->head_width_other;
    const size_t head_bank = plan->mode == 0u ? 0xF4Cu : 0xDCCu;
    if (head_width == 0u ||
            !workspace_contains(io->workspace_size, head_bank,
                                head_width, 1u, 4u)) {
        return false;
    }
    exec_tensor_initialize(&c, 1u, head_width, 1u, 4u, base + head_bank);
    if (!goodix_stage_call(&plan->stages[GOODIX_EXEC_HEAD_EXPAND],
                           &b, &range_out, &c, &range_in)) {
        return false;
    }
    const uint32_t selected_width[3] = {104u, 56u, 104u};
    exec_tensor_initialize(&b, 1u, selected_width[plan->mode], 1u, 4u,
                           base + tail_bank);
    if (!goodix_stage_call(&plan->stages[GOODIX_EXEC_HEAD_MERGE],
                           &a, &c, &b, &range_out)) {
        return false;
    }

    quantized_runtime_exec_tensor *current = &b;
    quantized_runtime_exec_tensor *next = &a;
    for (size_t index = 0u; index < 4u; ++index) {
        const uint32_t tail_width = plan->tail_widths[index];
        const size_t offset = (index & 1u) == 0u ? 0x18Cu : tail_bank;
        if (tail_width == 0u ||
                !workspace_contains(io->workspace_size, offset,
                                    tail_width, 1u, 4u)) {
            return false;
        }
        exec_tensor_initialize(next, 1u, tail_width, 1u, 4u, base + offset);
        if (!goodix_stage_call(
                &plan->stages[GOODIX_EXEC_TAIL_0 + index],
                current, &range_out, next, &range_in)) {
            return false;
        }
        quantized_runtime_exec_tensor *temporary = current;
        current = next;
        next = temporary;
    }
    if (plan->mode == 2u) {
        const uint32_t tail_width = plan->tail_widths[3];
        if (!workspace_contains(io->workspace_size, 0x18Cu,
                                tail_width, 1u, 4u)) {
            return false;
        }
        exec_tensor_initialize(next, 1u, tail_width, 1u, 4u,
                               base + 0x18Cu);
        if (!goodix_stage_call(&plan->stages[GOODIX_EXEC_TAIL_OPTIONAL],
                               current, &range_out, next, &range_in)) {
            return false;
        }
        current = next;
    }

    const uint64_t final_bytes = (uint64_t)current->type_flag *
        current->dims[0] * current->dims[1] * current->dims[2];
    if (current->data == NULL || final_bytes > io->output_capacity ||
            final_bytes > SIZE_MAX) {
        return false;
    }
    move_bytes_local(io->output, (const uint8_t *)current->data,
                     (size_t)final_bytes);
    if (output_bytes != NULL) {
        *output_bytes = (size_t)final_bytes;
    }
    return true;
}

void quantized_runtime_quantization_params_derive(
    const quantized_runtime *rt, float min_input, float max_input,
    float *out_min, float *out_max, float *out_step, float *out_scale) {
    if (rt == NULL || out_min == NULL || out_max == NULL || out_step == NULL ||
            out_scale == NULL) {
        return;
    }
    const quantized_runtime_providers *providers = &rt->providers;
    if (providers->fminf_fn == NULL || providers->fmaxf_fn == NULL ||
            providers->floorf_fn == NULL) {
        return;
    }
    float min = providers->fminf_fn(0.0f, min_input);
    float max = providers->fmaxf_fn(0.0f, max_input);
    float range = providers->fmaxf_fn(QUANTIZED_RUNTIME_RANGE_FLOOR,
                                      max - min);
    float scale = QUANTIZED_RUNTIME_FULL_SCALE / range;
    if (min < 0.0f) {
        const float scaled = -(min * scale);
        const float floored = providers->floorf_fn(scaled);
        const float fraction = scaled - floored;
        /* Recovered bit-level range check on the fraction: accepts roughly
         * [6.1e-5, 0.99997] and rejects fractions near 0 or 1. */
        if (f32_to_bits(fraction) + QUANTIZED_RUNTIME_DERIVE_FRACTION_BIAS <
                QUANTIZED_RUNTIME_DERIVE_FRACTION_LIMIT) {
            if (floored <= 0.0f ||
                    ((int32_t)f32_to_bits(floored) <=
                         QUANTIZED_RUNTIME_DERIVE_FLOOR_LIMIT_BITS &&
                     (fraction - 1.0f) * min < fraction * max)) {
                min = ((floored + 1.0f) * max) / (floored - 254.0f);
                range = max - min;
            } else {
                range = (min * -255.0f) / floored;
                max = min + range;
            }
            scale = QUANTIZED_RUNTIME_FULL_SCALE / range;
        }
    }
    *out_min = min;
    *out_max = max;
    *out_step = range / QUANTIZED_RUNTIME_FULL_SCALE;
    *out_scale = scale;
}

uint32_t quantized_runtime_float_to_int8_quantize(
    const quantized_runtime *rt, const float *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    if (rt == NULL || descriptor == NULL || inputs == NULL || outputs == NULL ||
            inputs[0] == NULL || outputs[0] == NULL || outputs[1] == NULL ||
            inputs[0]->data == NULL || outputs[0]->data == NULL ||
            outputs[1]->data == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    if (rt->providers.fminf_fn == NULL || rt->providers.fmaxf_fn == NULL ||
            rt->providers.floorf_fn == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    float min = 0.0f;
    float max = 0.0f;
    float step = 0.0f;
    float scale = 0.0f;
    quantized_runtime_quantization_params_derive(rt, descriptor[0],
                                                 descriptor[1], &min, &max,
                                                 &step, &scale);
    (void)step;
    const quantized_runtime_exec_tensor *input = inputs[0];
    quantized_runtime_exec_tensor *output = outputs[0];
    const float *input_data = (const float *)input->data;
    int8_t *output_data = (int8_t *)output->data;
    const int32_t count =
        (int32_t)(input->dims[0] * input->dims[1] * input->dims[2]);
    for (int32_t index = 0; index < count; ++index) {
        const float quantized = (input_data[index] - min) * scale;
        const int32_t rounded = round_half_away_from_zero(quantized);
        int8_t element;
        if (rounded < 0) {
            element = INT8_MIN;
        } else if (rounded <= 255) {
            element = (int8_t)(rounded - 128);
        } else {
            element = INT8_MAX;
        }
        output_data[index] = element;
    }
    float *output_range = (float *)outputs[1]->data;
    output_range[0] = min;
    output_range[1] = max;
    output->type_flag = 1u;
    return QUANTIZED_RUNTIME_STATUS_OK;
}

uint32_t quantized_runtime_goodix_in_place_float_to_int8(
    const quantized_runtime *rt, uint32_t mode, uint32_t rows,
    uint32_t columns, float *data, size_t data_count) {
    if (mode != 1u) {
        return QUANTIZED_RUNTIME_GOODIX_MODE_ERROR;
    }
    if (rt == NULL || data == NULL || rows == 0u || columns == 0u ||
            rows > SIZE_MAX / columns ||
            (size_t)rows * (size_t)columns > data_count) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }

    quantized_runtime_exec_tensor tensor = {
        .type_flag = 4u,
        .dims = {1u, rows, columns},
        .data = data,
    };
    float range[2] = {0.0f, 0.0f};
    quantized_runtime_exec_tensor range_tensor = {
        .type_flag = 0u,
        .dims = {0u, 0u, 0u},
        .data = range,
    };
    quantized_runtime_exec_tensor *inputs[1] = {&tensor};
    quantized_runtime_exec_tensor *outputs[2] = {&tensor, &range_tensor};
    const float descriptor[2] = {0.0f, 1.0f};
    return quantized_runtime_float_to_int8_quantize(
        rt, descriptor, inputs, outputs);
}

uint32_t quantized_runtime_goodix_configured_in_place_float_to_int8(
    const quantized_runtime *rt, uint32_t mode, const uint32_t shape[2],
    float *data, size_t data_count) {
    if (shape == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    return quantized_runtime_goodix_in_place_float_to_int8(
        rt, mode, shape[0], shape[1], data, data_count);
}

uint32_t quantized_runtime_int8_add_execute(
    const quantized_runtime *rt, const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    if (rt == NULL || descriptor == NULL || inputs == NULL || outputs == NULL ||
            inputs[0] == NULL || inputs[1] == NULL || inputs[2] == NULL ||
            inputs[3] == NULL || outputs[0] == NULL || outputs[1] == NULL ||
            inputs[0]->data == NULL || inputs[1]->data == NULL ||
            inputs[2]->data == NULL || inputs[3]->data == NULL ||
            outputs[0]->data == NULL || outputs[1]->data == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const quantized_runtime_providers *providers = &rt->providers;
    if (providers->fmaxf_fn == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const uint8_t *record = (const uint8_t *)descriptor;
    const int8_t *input0_data = (const int8_t *)inputs[0]->data;
    const float *qparams0 = (const float *)inputs[1]->data;
    const int8_t *input1_data = (const int8_t *)inputs[2]->data;
    const float *qparams1 = (const float *)inputs[3]->data;
    int8_t *output_data = (int8_t *)outputs[0]->data;
    const float step0 = (qparams0[1] - qparams0[0]) / QUANTIZED_RUNTIME_FULL_SCALE;
    const int32_t zero0 =
        zero_point_compute(providers, 0.0f, qparams0[0], qparams0[1]) - 128;
    const float step1 = (qparams1[1] - qparams1[0]) / QUANTIZED_RUNTIME_FULL_SCALE;
    const int32_t zero1 =
        zero_point_compute(providers, 0.0f, qparams1[0], qparams1[1]) - 128;
    const float out_min = load_f32_le(record + 4);
    const float out_max = load_f32_le(record + 8);
    const float out_step = (out_max - out_min) / QUANTIZED_RUNTIME_FULL_SCALE;
    const int32_t out_zero =
        zero_point_compute(providers, 0.0f, out_min, out_max) - 128;
    const int32_t count = (int32_t)(inputs[0]->dims[1] * inputs[0]->dims[2]);
    for (int32_t index = 0; index < count; ++index) {
        const float term0 = (float)(input0_data[index] - zero0) * step0;
        const float term1 = (float)(input1_data[index] - zero1) * step1;
        const float sum = term0 + term1;
        int32_t result = round_half_away_from_zero(sum / out_step) + out_zero;
        /* Recovered SSAT #8 saturation (Ghidra mislabels it as width 7). */
        if (result > 127) {
            result = 127;
        } else if (result < -128) {
            result = -128;
        }
        output_data[index] = (int8_t)result;
    }
    float *output_range = (float *)outputs[1]->data;
    output_range[0] = out_min;
    output_range[1] = out_max;
    return QUANTIZED_RUNTIME_STATUS_OK;
}

uint32_t quantized_runtime_pooling_execute(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    if (descriptor == NULL || inputs == NULL || outputs == NULL ||
            inputs[0] == NULL || outputs[0] == NULL ||
            inputs[0]->data == NULL || outputs[0]->data == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const uint8_t *record = (const uint8_t *)descriptor;
    const uint8_t type = record[0];
    const uint8_t window = record[1];
    const uint8_t stride = record[2];
    const quantized_runtime_exec_tensor *input = inputs[0];
    quantized_runtime_exec_tensor *output = outputs[0];
    const int32_t input_stride = (int32_t)input->dims[2];
    const int32_t out_rows = (int32_t)output->dims[1];
    const int32_t out_cols = (int32_t)output->dims[2];
    const int8_t *input_data = (const int8_t *)input->data;
    int8_t *output_data = (int8_t *)output->data;
    if (type == 0u) {
        if (window == 2u) {
            /* Recovered 4x-unrolled window-2 maximum.  The column loop steps
             * four outputs per iteration regardless of the column count
             * (recovered quirk: column counts not a multiple of four run
             * past the row, exactly as stock). */
            for (int32_t row = 0; row < out_rows; ++row) {
                const int8_t *row_data = input_data + row * input_stride;
                for (int32_t column = 0; column < out_cols; column += 4) {
                    const int32_t base = column * (int32_t)stride;
                    int8_t best0 = row_data[base];
                    int8_t best1 = row_data[base + 2];
                    int8_t best2 = row_data[base + 4];
                    int8_t best3 = row_data[base + 6];
                    if (best0 < row_data[base + 1]) {
                        best0 = row_data[base + 1];
                    }
                    if (best1 < row_data[base + 3]) {
                        best1 = row_data[base + 3];
                    }
                    if (best2 < row_data[base + 5]) {
                        best2 = row_data[base + 5];
                    }
                    if (best3 < row_data[base + 7]) {
                        best3 = row_data[base + 7];
                    }
                    int8_t *out = output_data + row * out_cols + column;
                    out[0] = best0;
                    out[1] = best1;
                    out[2] = best2;
                    out[3] = best3;
                }
            }
        } else if (window == 4u) {
            for (int32_t row = 0; row < out_rows; ++row) {
                const int8_t *row_data = input_data + row * input_stride;
                for (int32_t column = 0; column < out_cols; ++column) {
                    const int32_t base = column * (int32_t)stride;
                    int8_t best = INT8_MIN;
                    for (int32_t tap = 0; tap < (int32_t)window; ++tap) {
                        const int8_t value = row_data[base + tap];
                        if (best < value) {
                            best = value;
                        }
                    }
                    output_data[row * out_cols + column] = best;
                }
            }
        }
    } else if (type == 1u && window == 3u) {
        for (int32_t row = 0; row < out_rows; ++row) {
            const int8_t *row_data = input_data + row * input_stride;
            for (int32_t column = 0; column < out_cols; ++column) {
                const int32_t base = column * (int32_t)stride;
                int32_t sum = 0;
                for (int32_t tap = 0; tap < (int32_t)window; ++tap) {
                    sum += row_data[base + tap];
                }
                const float average = (float)sum / (float)(int32_t)window;
                const float adjust = (average > 0.0f) ? 0.5f : -0.5f;
                output_data[row * out_cols + column] =
                    (int8_t)(int32_t)(average + adjust);
            }
        }
    } else {
        /* Recovered: unsupported descriptor combinations are a silent
         * no-op returning zero. */
    }
    return QUANTIZED_RUNTIME_STATUS_OK;
}

static bool f32_is_finite_local(float value) {
    return (f32_to_bits(value) & UINT32_C(0x7F800000)) !=
           UINT32_C(0x7F800000);
}

static int8_t u8_bits_to_i8(uint8_t value) {
    return (value < 0x80u) ? (int8_t)value
                           : (int8_t)((int32_t)value - 256);
}

static int32_t u32_bits_to_i32(uint32_t value) {
    union {
        uint32_t u;
        int32_t i;
    } pun;
    pun.u = value;
    return pun.i;
}

static int32_t i8_conv_wrap_add(int32_t accumulator, int32_t addend) {
    return u32_bits_to_i32((uint32_t)accumulator + (uint32_t)addend);
}

/* Stock forms a signed-accumulator times unsigned-Q31 64-bit product, adds
 * 2^30, and takes an arithmetic shift by 31.  Spell out floor division so
 * the result does not depend on C's implementation-defined negative shift. */
static int32_t i8_conv_requantize(int32_t accumulator, uint32_t multiplier) {
    const int64_t rounded =
        (int64_t)accumulator * (int64_t)multiplier + INT64_C(0x40000000);
    int64_t scaled = rounded / INT64_C(0x80000000);
    if (rounded < 0 && rounded % INT64_C(0x80000000) != 0) {
        --scaled;
    }
    if (scaled < 0) {
        scaled = 0;
    } else if (scaled > 255) {
        scaled = 255;
    }
    return (int32_t)scaled - 128;
}

static uint32_t i8_conv_q31_multiplier(float value) {
    if (!(value >= 0.5f)) {
        return 0u;
    }
    if (value >= 2147483648.0f) {
        return UINT32_C(0x7FFFFFFF);
    }
    const uint32_t rounded = (uint32_t)(value + 0.5f);
    return (rounded < UINT32_C(0x7FFFFFFF))
               ? rounded
               : UINT32_C(0x7FFFFFFF);
}

static bool byte_ranges_overlap(const void *left, size_t left_size,
                                const void *right, size_t right_size) {
    if (left == NULL || right == NULL || left_size == 0u || right_size == 0u) {
        return false;
    }
    const uintptr_t left_begin = (uintptr_t)left;
    const uintptr_t right_begin = (uintptr_t)right;
    if (left_size > UINTPTR_MAX - left_begin ||
            right_size > UINTPTR_MAX - right_begin) {
        return true;
    }
    return left_begin < right_begin + right_size &&
           right_begin < left_begin + left_size;
}

size_t quantized_runtime_i8_conv1d_workspace_bytes(
    const quantized_runtime_i8_conv1d_descriptor *descriptor,
    uint32_t output_width) {
    size_t bytes = 0u;
    if (descriptor == NULL || descriptor->output_channels == 0u ||
            output_width == 0u ||
            !multiply_size_checked((size_t)descriptor->output_channels,
                                   (size_t)output_width, &bytes)) {
        return 0u;
    }
    return bytes;
}

static bool i8_conv_descriptor_supported(
    const quantized_runtime_i8_conv1d_descriptor *descriptor,
    uint32_t input_per_group, uint32_t output_per_group) {
    if (descriptor->kernel_height != 1u) {
        return false;
    }
    if (descriptor->kernel_width == 5u) {
        return descriptor->groups == 1u &&
               (input_per_group == 1u || input_per_group == 4u);
    }
    if (descriptor->kernel_width == 3u) {
        return descriptor->groups == 1u ||
               (input_per_group == 1u && output_per_group == 1u);
    }
    return descriptor->kernel_width == 1u && descriptor->groups == 1u;
}

uint32_t quantized_runtime_i8_conv1d_execute(
    const quantized_runtime_i8_conv1d_descriptor *descriptor,
    const quantized_runtime_i8_conv1d_model *model,
    quantized_runtime_i8_conv1d_io *io) {
    if (descriptor == NULL || model == NULL || io == NULL ||
            io->input == NULL || io->input_range == NULL ||
            io->output == NULL || io->output_range == NULL ||
            io->input->data == NULL || io->input_range->data == NULL ||
            io->output->data == NULL || io->output_range->data == NULL ||
            model->weights == NULL || model->channel_scales == NULL ||
            model->biases == NULL || descriptor->input_channels == 0u ||
            descriptor->output_channels == 0u || descriptor->groups == 0u ||
            descriptor->input_channels % descriptor->groups != 0u ||
            descriptor->output_channels % descriptor->groups != 0u ||
            io->input->dims[0] != 1u || io->output->dims[0] != 1u ||
            io->input->dims[1] != descriptor->input_channels ||
            io->output->dims[1] != descriptor->output_channels ||
            io->input->dims[2] == 0u || io->output->dims[2] == 0u ||
            io->input_range_capacity < 2u * sizeof(float) ||
            io->output_range_capacity < 2u * sizeof(float)) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }

    const uint32_t input_per_group =
        descriptor->input_channels / descriptor->groups;
    const uint32_t output_per_group =
        descriptor->output_channels / descriptor->groups;
    if (!i8_conv_descriptor_supported(descriptor, input_per_group,
                                      output_per_group)) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }

    size_t padded_width = 0u;
    size_t expected_output_width = 0u;
    size_t input_bytes = 0u;
    size_t output_bytes = 0u;
    size_t weight_count = 0u;
    if (!add_size_checked((size_t)io->input->dims[2],
                          descriptor->left_padding, &padded_width) ||
            !add_size_checked(padded_width, descriptor->right_padding,
                              &padded_width) ||
            padded_width < descriptor->kernel_width) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    expected_output_width =
        padded_width - (size_t)descriptor->kernel_width + 1u;
    if (expected_output_width != io->output->dims[2] ||
            !multiply_size_checked(descriptor->input_channels,
                                   io->input->dims[2], &input_bytes) ||
            !multiply_size_checked(descriptor->output_channels,
                                   io->output->dims[2], &output_bytes) ||
            !multiply_size_checked(descriptor->output_channels,
                                   input_per_group, &weight_count) ||
            !multiply_size_checked(weight_count, descriptor->kernel_width,
                                   &weight_count) ||
            io->input_capacity < input_bytes ||
            io->output_capacity < output_bytes ||
            model->weight_count < weight_count ||
            model->channel_scale_count < descriptor->output_channels ||
            model->bias_count < descriptor->output_channels) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }

    const uint8_t *input_range = (const uint8_t *)io->input_range->data;
    const float input_min = load_f32_le(input_range);
    const float input_max = load_f32_le(input_range + sizeof(float));
    if (!f32_is_finite_local(input_min) ||
            !f32_is_finite_local(input_max) || input_min > 0.0f ||
            input_max < 0.0f || input_max < input_min ||
            !f32_is_finite_local(model->weight_min) ||
            !f32_is_finite_local(model->weight_max) ||
            !(model->weight_max > model->weight_min) ||
            !f32_is_finite_local(model->bias_min) ||
            !f32_is_finite_local(model->bias_max) ||
            !f32_is_finite_local(model->output_min) ||
            !f32_is_finite_local(model->output_max)) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }

    const float input_span = fmaxf(QUANTIZED_RUNTIME_RANGE_FLOOR,
                                   input_max - input_min);
    const int32_t input_zero_unwrapped =
        round_half_away_from_zero(-input_min *
                                  (QUANTIZED_RUNTIME_FULL_SCALE / input_span)) -
        128;
    const int8_t input_zero =
        u8_bits_to_i8((uint8_t)((uint32_t)input_zero_unwrapped & 0xFFu));
    const float input_step = input_span / QUANTIZED_RUNTIME_FULL_SCALE;
    const float weight_step =
        (model->weight_max - model->weight_min) /
        QUANTIZED_RUNTIME_FULL_SCALE;
    const float combined_step = input_step * weight_step;
    float output_min = model->output_min;
    float output_max = model->output_max;
    if (!(combined_step > 0.0f) || !f32_is_finite_local(combined_step) ||
            quantized_runtime_recurrent_range_adjust(
                &output_min, &output_max, 3u) < 0 ||
            !f32_is_finite_local(output_min) ||
            !f32_is_finite_local(output_max) || !(output_max > output_min)) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }

    const float output_step =
        (output_max - output_min) / QUANTIZED_RUNTIME_FULL_SCALE;
    const float multiplier_base =
        (combined_step / output_step) * 2147483648.0f;
    const float bias_scale =
        ((model->bias_max - model->bias_min) * 8388608.0f) / combined_step;
    const float bias_min_scale = output_min / combined_step;
    if (!(output_step > 0.0f) || !f32_is_finite_local(multiplier_base) ||
            !f32_is_finite_local(bias_scale) ||
            !f32_is_finite_local(bias_min_scale)) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    for (uint32_t channel = 0u; channel < descriptor->output_channels;
         ++channel) {
        if (!(model->channel_scales[channel] > 0.0f) ||
                !f32_is_finite_local(model->channel_scales[channel])) {
            return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
        }
    }

    uint8_t *destination = (uint8_t *)io->output->data;
    const bool overlaps = byte_ranges_overlap(
        io->input->data, input_bytes, io->output->data, output_bytes);
    if (overlaps) {
        if (io->workspace == NULL || io->workspace_size < output_bytes ||
                byte_ranges_overlap(io->workspace, output_bytes,
                                    io->input->data, input_bytes)) {
            return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
        }
        destination = (uint8_t *)io->workspace;
    }

    const int8_t *input = (const int8_t *)io->input->data;
    const uint32_t input_width = io->input->dims[2];
    const uint32_t output_width = io->output->dims[2];
    for (uint32_t output_channel = 0u;
         output_channel < descriptor->output_channels; ++output_channel) {
        const uint32_t group = output_channel / output_per_group;
        const float channel_scale = model->channel_scales[output_channel];
        const uint32_t multiplier =
            i8_conv_q31_multiplier(channel_scale * multiplier_base);
        const float raw_bias = (float)model->biases[output_channel];
        const float bias_value =
            raw_bias * bias_scale / channel_scale -
            bias_min_scale / channel_scale;
        if (!f32_is_finite_local(bias_value) ||
                bias_value > 2147483520.0f ||
                bias_value < -2147483520.0f) {
            return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
        }
        int32_t bias = round_half_away_from_zero(bias_value);
        const size_t weight_base =
            (size_t)output_channel * input_per_group *
            descriptor->kernel_width;
        for (uint32_t position = 0u; position < output_width; ++position) {
            int32_t accumulator = bias;
            for (uint32_t input_channel = 0u;
                 input_channel < input_per_group; ++input_channel) {
                const size_t source_row =
                    (size_t)(group * input_per_group + input_channel) *
                    input_width;
                const size_t weight_row =
                    weight_base + (size_t)input_channel *
                                      descriptor->kernel_width;
                for (uint32_t kernel = 0u;
                     kernel < descriptor->kernel_width; ++kernel) {
                    const int64_t source_position =
                        (int64_t)position + kernel -
                        descriptor->left_padding;
                    const int32_t input_value =
                        (source_position < 0 ||
                         source_position >= (int64_t)input_width)
                            ? input_zero
                            : input[source_row + (size_t)source_position];
                    const int32_t weight = model->weights[weight_row + kernel];
                    accumulator = i8_conv_wrap_add(
                        accumulator, (input_value - input_zero) * weight);
                }
            }
            destination[(size_t)output_channel * output_width + position] =
                (uint8_t)(int8_t)i8_conv_requantize(accumulator, multiplier);
        }
    }

    if (overlaps) {
        move_bytes_local((uint8_t *)io->output->data, destination, output_bytes);
    }
    uint8_t *output_range = (uint8_t *)io->output_range->data;
    store_f32_le(output_range, output_min);
    store_f32_le(output_range + sizeof(float), output_max);
    return QUANTIZED_RUNTIME_STATUS_OK;
}

uint32_t quantized_runtime_i8_conv1d_execute_target(
    const void *descriptor_record,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    if (descriptor_record == NULL || inputs == NULL || outputs == NULL ||
            inputs[0] == NULL || inputs[1] == NULL || outputs[0] == NULL ||
            outputs[1] == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const uint8_t *record = (const uint8_t *)descriptor_record;
    quantized_runtime_i8_conv1d_descriptor descriptor = {
        record[0], record[1], record[2], record[3],
        record[4], record[5], record[6], record[7], load_f32_le(record + 8u),
    };
    if (descriptor.groups == 0u ||
            descriptor.input_channels % descriptor.groups != 0u) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    size_t weight_count = 0u;
    if (!multiply_size_checked(descriptor.output_channels,
                               descriptor.input_channels / descriptor.groups,
                               &weight_count) ||
            !multiply_size_checked(weight_count, descriptor.kernel_width,
                                   &weight_count)) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const size_t aligned_weight_count = (weight_count + 3u) & ~(size_t)3u;
    const uint8_t *weights =
        (const uint8_t *)(uintptr_t)load_u32_le(record + 0x0Cu);
    const uint8_t *quantization =
        (const uint8_t *)(uintptr_t)load_u32_le(record + 0x10u);
    if (weights == NULL || quantization == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    quantized_runtime_i8_conv1d_model model = {
        (const int8_t *)weights,
        weight_count,
        load_f32_le(weights + aligned_weight_count),
        load_f32_le(weights + aligned_weight_count + 4u),
        (const float *)(const void *)(weights + aligned_weight_count + 8u),
        descriptor.output_channels,
        (const int32_t *)(const void *)quantization,
        descriptor.output_channels,
        load_f32_le(quantization + (size_t)descriptor.output_channels * 4u),
        load_f32_le(quantization +
                    ((size_t)descriptor.output_channels + 1u) * 4u),
        load_f32_le(quantization +
                    ((size_t)descriptor.output_channels + 2u) * 4u),
        load_f32_le(quantization +
                    ((size_t)descriptor.output_channels + 3u) * 4u),
    };
    size_t input_bytes = 0u;
    size_t output_bytes = 0u;
    size_t padded_elements = 0u;
    if (!multiply_size_checked(inputs[0]->dims[1], inputs[0]->dims[2],
                               &input_bytes) ||
            !multiply_size_checked(outputs[0]->dims[1], outputs[0]->dims[2],
                                   &output_bytes) ||
            !add_size_checked(inputs[0]->dims[2], descriptor.left_padding,
                              &padded_elements) ||
            !add_size_checked(padded_elements, descriptor.right_padding,
                              &padded_elements) ||
            !multiply_size_checked(padded_elements, inputs[0]->dims[1],
                                   &padded_elements)) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    quantized_runtime_i8_conv1d_io io = {
        inputs[0], inputs[1], outputs[0], outputs[1],
        input_bytes, 2u * sizeof(float), output_bytes, 2u * sizeof(float),
        (uint8_t *)inputs[0]->data + padded_elements, output_bytes,
    };
    return quantized_runtime_i8_conv1d_execute(&descriptor, &model, &io);
}

uint32_t quantized_runtime_float_dense_execute(
    const quantized_runtime_float_dense_descriptor *descriptor,
    const quantized_runtime_float_dense_model *model,
    quantized_runtime_float_dense_io *io) {
    if (descriptor == NULL || model == NULL || io == NULL ||
            io->input == NULL || io->output == NULL ||
            io->input->data == NULL || io->output->data == NULL ||
            model->weights == NULL || model->biases == NULL ||
            descriptor->output_count == 0u || descriptor->activation > 2u ||
            io->input->dims[0] != 1u) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    size_t input_count = 0u;
    size_t output_elements = 0u;
    size_t weight_count = 0u;
    size_t input_bytes = 0u;
    size_t output_bytes = 0u;
    if (!multiply_size_checked(io->input->dims[1], io->input->dims[2],
                               &input_count) ||
            !multiply_size_checked(io->output->dims[0], io->output->dims[1],
                                   &output_elements) ||
            !multiply_size_checked(output_elements, io->output->dims[2],
                                   &output_elements) ||
            output_elements != descriptor->output_count ||
            !multiply_size_checked(descriptor->output_count, input_count,
                                   &weight_count) ||
            !multiply_size_checked(input_count, sizeof(float), &input_bytes) ||
            !multiply_size_checked(output_elements, sizeof(float),
                                   &output_bytes) ||
            input_count == 0u || io->input_capacity < input_bytes ||
            io->output_capacity < output_bytes ||
            model->weight_count < weight_count ||
            model->bias_count < descriptor->output_count) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }

    uint8_t *destination_bytes = (uint8_t *)io->output->data;
    const bool overlaps = byte_ranges_overlap(
        io->input->data, input_bytes, io->output->data, output_bytes);
    if (overlaps) {
        if (io->workspace == NULL || io->workspace_size < output_bytes ||
                byte_ranges_overlap(io->workspace, output_bytes,
                                    io->input->data, input_bytes)) {
            return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
        }
        destination_bytes = (uint8_t *)io->workspace;
    }
    const float *input = (const float *)io->input->data;
    float *destination = (float *)(void *)destination_bytes;
    for (uint32_t output = 0u; output < descriptor->output_count; ++output) {
        float accumulator = 0.0f;
        const size_t weight_base = (size_t)output * input_count;
        for (size_t input_index = 0u; input_index < input_count;
             ++input_index) {
            accumulator += input[input_index] *
                           model->weights[weight_base + input_index];
        }
        destination[output] = accumulator + model->biases[output];
    }
    if (descriptor->activation == 1u) {
        for (uint32_t output = 0u; output < descriptor->output_count; ++output) {
            if (destination[output] < 0.0f) {
                destination[output] *= descriptor->alpha;
            }
        }
    } else if (descriptor->activation == 2u) {
        for (uint32_t output = 0u; output < descriptor->output_count; ++output) {
            float exponent = -destination[output];
            if (u32_bits_to_i32(f32_to_bits(exponent)) >=
                    INT32_C(0x42B00000)) {
                exponent = QUANTIZED_RUNTIME_SOFTMAX_CAP;
            }
            destination[output] = 1.0f / (1.0f + expf(exponent));
        }
    }
    if (overlaps) {
        move_bytes_local((uint8_t *)io->output->data, destination_bytes,
                         output_bytes);
    }
    return QUANTIZED_RUNTIME_STATUS_OK;
}

uint32_t quantized_runtime_float_dense_execute_target(
    const void *descriptor_record,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    if (descriptor_record == NULL || inputs == NULL || outputs == NULL ||
            inputs[0] == NULL || outputs[0] == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const uint8_t *record = (const uint8_t *)descriptor_record;
    quantized_runtime_float_dense_descriptor descriptor = {
        load_u32_le(record), record[4], record[5], load_f32_le(record + 8u),
    };
    size_t input_count = 0u;
    size_t weight_count = 0u;
    size_t input_bytes = 0u;
    size_t output_bytes = 0u;
    if (!multiply_size_checked(inputs[0]->dims[1], inputs[0]->dims[2],
                               &input_count) ||
            !multiply_size_checked(input_count, descriptor.output_count,
                                   &weight_count) ||
            !multiply_size_checked(input_count, sizeof(float), &input_bytes) ||
            !multiply_size_checked(descriptor.output_count, sizeof(float),
                                   &output_bytes)) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    quantized_runtime_float_dense_model model = {
        (const float *)(uintptr_t)load_u32_le(record + 0x0Cu), weight_count,
        (const float *)(uintptr_t)load_u32_le(record + 0x10u),
        descriptor.output_count,
    };
    quantized_runtime_float_dense_io io = {
        inputs[0], outputs[0], input_bytes, output_bytes, NULL, 0u,
    };
    return quantized_runtime_float_dense_execute(&descriptor, &model, &io);
}

uint32_t quantized_runtime_float_conv1d_execute(
    const quantized_runtime_float_conv1d_descriptor *descriptor,
    const quantized_runtime_float_conv1d_model *model,
    quantized_runtime_float_conv1d_io *io) {
    if (descriptor == NULL || model == NULL || io == NULL ||
            io->input == NULL || io->output == NULL ||
            io->input->data == NULL || io->output->data == NULL ||
            model->weights == NULL || model->biases == NULL ||
            io->input->type_flag != sizeof(float) ||
            io->output->type_flag != sizeof(float) ||
            io->input->dims[0] != 1u || io->output->dims[0] != 1u ||
            descriptor->stride == 0u || descriptor->groups == 0u ||
            descriptor->input_channels == 0u ||
            descriptor->output_channels == 0u ||
            descriptor->input_channels % descriptor->groups != 0u ||
            descriptor->output_channels % descriptor->groups != 0u ||
            io->input->dims[1] != descriptor->input_channels ||
            io->output->dims[1] != descriptor->output_channels ||
            descriptor->activation > 2u ||
            (descriptor->activation == 2u && io->expf_fn == NULL) ||
            (descriptor->kernel_width != 1u &&
             descriptor->kernel_width != 3u &&
             descriptor->kernel_width != 5u) ||
            (descriptor->groups != 1u &&
             (descriptor->kernel_width != 3u ||
              descriptor->input_channels / descriptor->groups != 1u))) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }

    size_t padded_width = 0u;
    size_t logical_input_count = 0u;
    size_t output_count = 0u;
    size_t weights_per_output = 0u;
    size_t required_weights = 0u;
    size_t input_bytes = 0u;
    size_t output_bytes = 0u;
    if (!add_size_checked(io->input->dims[2], descriptor->left_padding,
                          &padded_width) ||
            !add_size_checked(padded_width, descriptor->right_padding,
                              &padded_width) ||
            padded_width < descriptor->kernel_width ||
            io->output->dims[2] !=
                (padded_width - descriptor->kernel_width) /
                    descriptor->stride + 1u ||
            !multiply_size_checked(descriptor->input_channels,
                                   io->input->dims[2],
                                   &logical_input_count) ||
            !multiply_size_checked(descriptor->output_channels,
                                   io->output->dims[2], &output_count) ||
            !multiply_size_checked(
                descriptor->input_channels / descriptor->groups,
                descriptor->kernel_width, &weights_per_output) ||
            !multiply_size_checked(descriptor->output_channels,
                                   weights_per_output, &required_weights) ||
            !multiply_size_checked(logical_input_count, sizeof(float),
                                   &input_bytes) ||
            !multiply_size_checked(output_count, sizeof(float),
                                   &output_bytes) ||
            io->input_capacity < input_bytes ||
            io->output_capacity < output_bytes ||
            model->weight_count < required_weights ||
            model->bias_count < descriptor->output_channels) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }

    uint8_t *destination_bytes = (uint8_t *)io->output->data;
    const bool overlaps = byte_ranges_overlap(
        io->input->data, input_bytes, io->output->data, output_bytes);
    if (overlaps) {
        if (io->workspace == NULL || io->workspace_size < output_bytes ||
                byte_ranges_overlap(io->workspace, output_bytes,
                                    io->input->data, input_bytes)) {
            return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
        }
        destination_bytes = (uint8_t *)io->workspace;
    }

    const float *input = (const float *)io->input->data;
    float *destination = (float *)(void *)destination_bytes;
    const size_t input_width = io->input->dims[2];
    const size_t output_width = io->output->dims[2];
    const size_t input_per_group =
        descriptor->input_channels / descriptor->groups;
    const size_t output_per_group =
        descriptor->output_channels / descriptor->groups;
    for (size_t group = 0u; group < descriptor->groups; ++group) {
        for (size_t output_in_group = 0u;
                output_in_group < output_per_group; ++output_in_group) {
            const size_t output_channel =
                group * output_per_group + output_in_group;
            const size_t weight_base = descriptor->groups == 1u
                ? output_channel * weights_per_output
                : group * output_per_group * descriptor->kernel_width +
                      output_in_group * weights_per_output;
            for (size_t position = 0u; position < output_width; ++position) {
                float accumulator = 0.0f;
                for (size_t input_in_group = 0u;
                        input_in_group < input_per_group; ++input_in_group) {
                    const size_t input_channel =
                        group * input_per_group + input_in_group;
                    for (size_t tap = 0u; tap < descriptor->kernel_width;
                         ++tap) {
                        const size_t padded_position =
                            position * descriptor->stride + tap;
                        float value = 0.0f;
                        if (padded_position >= descriptor->left_padding) {
                            const size_t input_position =
                                padded_position - descriptor->left_padding;
                            if (input_position < input_width) {
                                value = input[input_channel * input_width +
                                              input_position];
                            }
                        }
                        accumulator += value * model->weights[
                            weight_base +
                            input_in_group * descriptor->kernel_width + tap];
                    }
                }
                destination[output_channel * output_width + position] =
                    accumulator + model->biases[output_channel];
            }
        }
    }

    if (descriptor->activation == 1u) {
        for (size_t index = 0u; index < output_count; ++index) {
            if (destination[index] < 0.0f) {
                destination[index] = descriptor->alpha == 0.0f
                    ? 0.0f : destination[index] * descriptor->alpha;
            }
        }
    } else if (descriptor->activation == 2u) {
        for (size_t index = 0u; index < output_count; ++index) {
            float exponent = -destination[index];
            if (u32_bits_to_i32(f32_to_bits(exponent)) >=
                    INT32_C(0x42B00000)) {
                exponent = QUANTIZED_RUNTIME_SOFTMAX_CAP;
            }
            destination[index] =
                1.0f / (io->expf_fn(exponent) + 1.0f);
        }
    }
    if (overlaps) {
        move_bytes_local((uint8_t *)io->output->data, destination_bytes,
                         output_bytes);
    }
    return QUANTIZED_RUNTIME_STATUS_OK;
}

uint32_t quantized_runtime_float_conv1d_execute_target(
    const void *descriptor_record,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    if (descriptor_record == NULL || inputs == NULL || outputs == NULL ||
            inputs[0] == NULL || outputs[0] == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const uint8_t *record = (const uint8_t *)descriptor_record;
    const quantized_runtime_float_conv1d_descriptor descriptor = {
        record[0], record[1], record[2], record[3], record[4], record[5],
        record[6], record[7], load_f32_le(record + 8u),
    };
    size_t input_count = 0u;
    size_t output_count = 0u;
    size_t weight_count = 0u;
    size_t padded_width = 0u;
    if (descriptor.groups == 0u ||
            !multiply_size_checked(inputs[0]->dims[1], inputs[0]->dims[2],
                                   &input_count) ||
            !multiply_size_checked(outputs[0]->dims[1], outputs[0]->dims[2],
                                   &output_count) ||
            !multiply_size_checked(
                descriptor.input_channels / descriptor.groups,
                descriptor.kernel_width, &weight_count) ||
            !multiply_size_checked(weight_count, descriptor.output_channels,
                                   &weight_count) ||
            !add_size_checked(inputs[0]->dims[2], descriptor.left_padding,
                              &padded_width) ||
            !add_size_checked(padded_width, descriptor.right_padding,
                              &padded_width) ||
            !multiply_size_checked(padded_width, inputs[0]->dims[1],
                                   &padded_width)) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const quantized_runtime_float_conv1d_model model = {
        (const float *)(uintptr_t)load_u32_le(record + 0x0Cu), weight_count,
        (const float *)(uintptr_t)load_u32_le(record + 0x10u),
        descriptor.output_channels,
    };
    const size_t input_bytes = input_count * sizeof(float);
    const size_t output_bytes = output_count * sizeof(float);
    quantized_runtime_float_conv1d_io io = {
        inputs[0], outputs[0], input_bytes, output_bytes,
        (uint8_t *)inputs[0]->data + padded_width * sizeof(float),
        output_bytes, expf,
    };
    return quantized_runtime_float_conv1d_execute(&descriptor, &model, &io);
}

uint32_t quantized_runtime_float_softmax_execute(
    const quantized_runtime *rt, const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    (void)descriptor; /* recovered: accepted but never read */
    if (rt == NULL || inputs == NULL || outputs == NULL || inputs[0] == NULL ||
            outputs[0] == NULL || inputs[0]->data == NULL ||
            outputs[0]->data == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    if (rt->providers.expf_fn == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const float *input_data = (const float *)inputs[0]->data;
    float *output_data = (float *)outputs[0]->data;
    const int32_t count = (int32_t)outputs[0]->dims[1];
    float maximum = -3.4028234663852886e+38f; /* 0xFF7FFFFF */
    for (int32_t index = 0; index < count; ++index) {
        if (input_data[index] > maximum) {
            maximum = input_data[index];
        }
    }
    float sum = 0.0f;
    for (int32_t index = 0; index < count; ++index) {
        float difference = input_data[index] - maximum;
        /* Recovered signed bit-level cap: only reachable for NaN inputs
         * (finite differences are always <= 0). */
        if ((int32_t)f32_to_bits(difference) >=
                QUANTIZED_RUNTIME_SOFTMAX_CAP_BITS) {
            difference = QUANTIZED_RUNTIME_SOFTMAX_CAP;
        }
        const float exponential = rt->providers.expf_fn(difference);
        output_data[index] = exponential;
        sum = exponential + sum;
    }
    for (int32_t index = 0; index < count; ++index) {
        output_data[index] = output_data[index] / sum;
    }
    return QUANTIZED_RUNTIME_STATUS_OK;
}

uint32_t quantized_runtime_float_add_execute(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    if (descriptor == NULL || inputs == NULL || outputs == NULL ||
            inputs[0] == NULL || inputs[1] == NULL || outputs[0] == NULL ||
            inputs[0]->data == NULL || inputs[1]->data == NULL ||
            outputs[0]->data == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const uint8_t *record = (const uint8_t *)descriptor;
    const float *input0_data = (const float *)inputs[0]->data;
    const float *input1_data = (const float *)inputs[1]->data;
    float *output_data = (float *)outputs[0]->data;
    const int32_t count = (int32_t)(inputs[0]->dims[1] * inputs[0]->dims[2]);
    for (int32_t index = 0; index < count; ++index) {
        output_data[index] = input0_data[index] + input1_data[index];
    }
    if (record[0] == 1u) {
        const float alpha = load_f32_le(record + 4);
        if (alpha == 0.0f) {
            for (int32_t index = 0; index < count; ++index) {
                if (output_data[index] < 0.0f) {
                    output_data[index] = 0.0f;
                }
            }
        } else {
            for (int32_t index = 0; index < count; ++index) {
                if (output_data[index] < 0.0f) {
                    output_data[index] = output_data[index] * alpha;
                }
            }
        }
    }
    return QUANTIZED_RUNTIME_STATUS_OK;
}

uint32_t quantized_runtime_int8_to_float_execute(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    (void)descriptor;
    if (inputs == NULL || outputs == NULL || inputs[0] == NULL ||
            inputs[1] == NULL || outputs[0] == NULL ||
            inputs[0]->data == NULL || inputs[1]->data == NULL ||
            outputs[0]->data == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    size_t count = 0u;
    if (!multiply_size_checked(inputs[0]->dims[1], inputs[0]->dims[2],
                               &count) ||
            outputs[0]->dims[1] > SIZE_MAX / outputs[0]->dims[2] ||
            (size_t)outputs[0]->dims[1] * outputs[0]->dims[2] < count) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const float *const range = (const float *)inputs[1]->data;
    float span = range[1] - range[0];
    if (span < 0x1.a36e2ep-14f) { /* exact stock Float32 1e-4 */
        span = 0x1.a36e2ep-14f;
    }
    const float step = span / 255.0f;
    if (!(step > 0.0f)) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    int32_t zero = quantized_runtime_round_half_away_from_zero_290fe(
        -range[0] / step);
    if (zero < 0) {
        zero = 0;
    } else if (zero > 255) {
        zero = 255;
    }
    zero -= 128;
    const int8_t *const source = (const int8_t *)inputs[0]->data;
    float *const destination = (float *)outputs[0]->data;
    for (size_t index = 0u; index < count; ++index) {
        destination[index] = (float)((int32_t)source[index] - zero) * step;
    }
    return QUANTIZED_RUNTIME_STATUS_OK;
}

uint32_t quantized_runtime_float_multiply_execute(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    (void)descriptor;
    if (inputs == NULL || outputs == NULL || inputs[0] == NULL ||
            inputs[1] == NULL || outputs[0] == NULL ||
            inputs[0]->data == NULL || inputs[1]->data == NULL ||
            outputs[0]->data == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    size_t count = 0u;
    size_t output_count = 0u;
    if (!multiply_size_checked(inputs[0]->dims[1], inputs[0]->dims[2],
                               &count) ||
            !multiply_size_checked(outputs[0]->dims[1], outputs[0]->dims[2],
                                   &output_count) || output_count < count) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const float *const left = (const float *)inputs[0]->data;
    const float *const right = (const float *)inputs[1]->data;
    float *const destination = (float *)outputs[0]->data;
    if (inputs[1]->dims[1] + inputs[1]->dims[2] == 3u) {
        for (size_t index = 0u; index < count; ++index) {
            destination[index] = left[index] * right[0];
        }
        return QUANTIZED_RUNTIME_STATUS_OK;
    }
    if (inputs[1]->dims[1] != 1u ||
            inputs[1]->dims[2] < inputs[0]->dims[2]) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const size_t columns = inputs[0]->dims[2];
    for (size_t row = 0u; row < inputs[0]->dims[1]; ++row) {
        for (size_t column = 0u; column < columns; ++column) {
            const size_t index = row * columns + column;
            destination[index] = left[index] * right[column];
        }
    }
    return QUANTIZED_RUNTIME_STATUS_OK;
}

uint32_t quantized_runtime_float_concatenate_two_execute(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    (void)descriptor;
    if (inputs == NULL || outputs == NULL || inputs[0] == NULL ||
            inputs[1] == NULL || outputs[0] == NULL ||
            inputs[0]->data == NULL || inputs[1]->data == NULL ||
            outputs[0]->data == NULL ||
            inputs[0]->dims[0] != inputs[1]->dims[0] ||
            inputs[0]->dims[0] != outputs[0]->dims[0] ||
            inputs[0]->dims[2] != inputs[1]->dims[2] ||
            inputs[0]->dims[2] != outputs[0]->dims[2] ||
            inputs[0]->dims[1] > UINT32_MAX - inputs[1]->dims[1] ||
            outputs[0]->dims[1] <
                inputs[0]->dims[1] + inputs[1]->dims[1]) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    float *destination = (float *)outputs[0]->data;
    quantized_runtime_exec_tensor *const source_tensors[2] = {
        inputs[0], inputs[1],
    };
    for (size_t outer = 0u; outer < outputs[0]->dims[0]; ++outer) {
        for (size_t source_index = 0u; source_index < 2u; ++source_index) {
            const quantized_runtime_exec_tensor *const source_tensor =
                source_tensors[source_index];
            size_t slice = 0u;
            if (!multiply_size_checked(source_tensor->dims[1],
                                       source_tensor->dims[2], &slice)) {
                return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
            }
            const float *const source =
                (const float *)source_tensor->data + outer * slice;
            move_bytes_local((uint8_t *)destination,
                             (const uint8_t *)source,
                             slice * sizeof(float));
            destination += slice;
        }
    }
    return QUANTIZED_RUNTIME_STATUS_OK;
}

uint32_t quantized_runtime_int8_concatenate_execute(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *input_pairs,
    quantized_runtime_exec_tensor *const *outputs,
    uint32_t input_count) {
    (void)descriptor;
    if (input_pairs == NULL || outputs == NULL || outputs[0] == NULL ||
            outputs[1] == NULL || outputs[0]->data == NULL ||
            outputs[1]->data == NULL || input_count == 0u) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const uint32_t outer_count = outputs[0]->dims[0];
    const uint32_t tail_count = outputs[0]->dims[2];
    uint32_t concatenated_rows = 0u;
    float minimum = 0.0f;
    float maximum = 0.0f;
    for (uint32_t index = 0u; index < input_count; ++index) {
        quantized_runtime_exec_tensor *const tensor = input_pairs[index * 2u];
        quantized_runtime_exec_tensor *const range_tensor =
            input_pairs[index * 2u + 1u];
        if (tensor == NULL || range_tensor == NULL || tensor->data == NULL ||
                range_tensor->data == NULL || tensor->dims[0] != outer_count ||
                tensor->dims[2] != tail_count ||
                concatenated_rows > UINT32_MAX - tensor->dims[1]) {
            return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
        }
        concatenated_rows += tensor->dims[1];
        const float *const range = (const float *)range_tensor->data;
        if (index == 0u) {
            minimum = range[0];
            maximum = range[1];
        } else {
            if (range[0] < minimum) {
                minimum = range[0];
            }
            if (range[1] > maximum) {
                maximum = range[1];
            }
        }
    }
    if (outputs[0]->dims[1] < concatenated_rows || !(maximum > minimum)) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const float output_step = (maximum - minimum) / 255.0f;
    if (!(output_step > 0.0f)) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    int8_t *destination = (int8_t *)outputs[0]->data;
    for (uint32_t outer = 0u; outer < outer_count; ++outer) {
        for (uint32_t index = 0u; index < input_count; ++index) {
            const quantized_runtime_exec_tensor *const tensor =
                input_pairs[index * 2u];
            const float *const range =
                (const float *)input_pairs[index * 2u + 1u]->data;
            size_t slice = 0u;
            if (!multiply_size_checked(tensor->dims[1], tail_count, &slice)) {
                return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
            }
            const int8_t *const source =
                (const int8_t *)tensor->data + (size_t)outer * slice;
            const float low_delta = range[0] - minimum;
            const float high_delta = range[1] - maximum;
            const float low_abs = low_delta < 0.0f ? -low_delta : low_delta;
            const float high_abs = high_delta < 0.0f ? -high_delta : high_delta;
            if (low_abs < 0x1.0c6f7ap-20f &&
                    high_abs < 0x1.0c6f7ap-20f) {
                move_bytes_local((uint8_t *)destination,
                                 (const uint8_t *)source, slice);
                destination += slice;
                continue;
            }
            const float input_step = (range[1] - range[0]) / 255.0f;
            const float slope = input_step / output_step;
            const float intercept =
                (range[0] - minimum) / output_step + slope * 128.0f;
            for (size_t value = 0u; value < slice; ++value) {
                int32_t converted =
                    quantized_runtime_round_half_away_from_zero_290fe(
                        (float)source[value] * slope + intercept);
                if (converted < 0) {
                    converted = -128;
                } else if (converted > 255) {
                    converted = 127;
                } else {
                    converted -= 128;
                }
                *destination++ = (int8_t)converted;
            }
        }
    }
    float *const output_range = (float *)outputs[1]->data;
    output_range[0] = minimum;
    output_range[1] = maximum;
    return QUANTIZED_RUNTIME_STATUS_OK;
}

uint32_t quantized_runtime_float_strided_copy_2d_execute(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    if (descriptor == NULL || inputs == NULL || outputs == NULL ||
            inputs[0] == NULL || outputs[0] == NULL ||
            inputs[0]->data == NULL || outputs[0]->data == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const uint8_t *const record = (const uint8_t *)descriptor;
    if (record[1] > 2u || record[2] > 2u) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    size_t source_count = 0u;
    size_t destination_count = 0u;
    if (!multiply_size_checked(inputs[0]->dims[1], inputs[0]->dims[2],
                               &source_count) ||
            !multiply_size_checked(outputs[0]->dims[1], outputs[0]->dims[2],
                                   &destination_count)) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const size_t strides[3] = {
        source_count, inputs[0]->dims[2], 1u,
    };
    const size_t row_stride = strides[record[1]];
    const size_t column_stride = strides[record[2]];
    const float *const source = (const float *)inputs[0]->data;
    float *const destination = (float *)outputs[0]->data;
    for (size_t row = 0u; row < outputs[0]->dims[1]; ++row) {
        for (size_t column = 0u; column < outputs[0]->dims[2]; ++column) {
            if ((row != 0u && row_stride > SIZE_MAX / row) ||
                    (column != 0u && column_stride > SIZE_MAX / column)) {
                return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
            }
            const size_t row_offset = row * row_stride;
            const size_t column_offset = column * column_stride;
            if (row_offset > SIZE_MAX - column_offset ||
                    row_offset + column_offset >= source_count) {
                return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
            }
            destination[row * outputs[0]->dims[2] + column] =
                source[row_offset + column_offset];
        }
    }
    (void)destination_count;
    return QUANTIZED_RUNTIME_STATUS_OK;
}

uint32_t quantized_runtime_float_pool_1d_execute(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    if (descriptor == NULL || inputs == NULL || outputs == NULL ||
            inputs[0] == NULL || outputs[0] == NULL ||
            inputs[0]->data == NULL || outputs[0]->data == NULL ||
            outputs[0]->dims[1] > inputs[0]->dims[1]) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const uint8_t *const record = (const uint8_t *)descriptor;
    const uint8_t mode = record[0];
    const uint8_t window = record[1];
    const uint8_t stride = record[2];
    const uint8_t padding = record[3];
    if (mode > 1u || window == 0u) {
        return mode > 1u ? QUANTIZED_RUNTIME_STATUS_OK
                         : QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const float *const source = (const float *)inputs[0]->data;
    float *const destination = (float *)outputs[0]->data;
    const size_t source_columns = inputs[0]->dims[2];
    const size_t destination_columns = outputs[0]->dims[2];
    for (size_t output_column = 0u;
            output_column < destination_columns; ++output_column) {
        if (output_column != 0u && stride > SIZE_MAX / output_column) {
            return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
        }
        const size_t unpadded = output_column * stride;
        const size_t start = unpadded < padding ? 0u : unpadded - padding;
        size_t end = unpadded > SIZE_MAX - window
            ? source_columns : unpadded + window;
        if (end > padding) {
            end -= padding;
        } else {
            end = 0u;
        }
        if (end > source_columns) {
            end = source_columns;
        }
        for (size_t row = 0u; row < outputs[0]->dims[1]; ++row) {
            float value = mode == 0u ? -3.4028234663852886e38f : 0.0f;
            size_t count = 0u;
            for (size_t column = start; column < end; ++column) {
                const float sample = source[row * source_columns + column];
                if (mode == 0u) {
                    if (value < sample) {
                        value = sample;
                    }
                } else {
                    value += sample;
                }
                ++count;
            }
            if (mode == 1u) {
                if (count == 0u) {
                    return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
                }
                value /= (float)count;
            }
            destination[row * destination_columns + output_column] = value;
        }
    }
    return QUANTIZED_RUNTIME_STATUS_OK;
}

uint32_t quantized_runtime_two_output_thirds_slice(
    const quantized_runtime *rt, quantized_runtime_pool *pool,
    const quantized_runtime_tensor *input_a,
    const quantized_runtime_tensor *input_b,
    quantized_runtime_tensor **outputs, uint32_t index) {
    if (rt == NULL || pool == NULL || input_a == NULL || input_b == NULL ||
            outputs == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    if (rt->providers.slice_fn == NULL) {
        outputs[0] = NULL;
        outputs[1] = NULL;
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const uint32_t third = (uint32_t)input_a->dims[0] / 3u;
    outputs[0] = rt->providers.slice_fn(pool, input_a, third * index,
                                        third * (index + 1u));
    outputs[1] = rt->providers.slice_fn(pool, input_b, third * index,
                                        third * (index + 1u));
    return QUANTIZED_RUNTIME_STATUS_OK;
}

uint32_t quantized_runtime_scaled_mul_conditional_release(
    const quantized_runtime *rt, const float *alpha_source,
    quantized_runtime_pool *pool, quantized_runtime_tensor *tensor,
    uint32_t release) {
    if (rt == NULL || alpha_source == NULL || pool == NULL || tensor == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    if (rt->providers.scaled_mul_fn == NULL) {
        return QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
    }
    const uint32_t result =
        rt->providers.scaled_mul_fn(*alpha_source, pool, tensor, 1u);
    if (release != 0u) {
        quantized_runtime_tensor_release(pool, tensor);
    }
    return result;
}

uintptr_t quantized_runtime_executor_vector_95b20(const quantized_runtime *rt) {
    if (rt == NULL) {
        return (uintptr_t)0;
    }
    return rt->providers.vector_95b20;
}

uintptr_t quantized_runtime_executor_vector_36dcc(const quantized_runtime *rt) {
    if (rt == NULL) {
        return (uintptr_t)0;
    }
    return rt->providers.vector_36dcc;
}

uintptr_t quantized_runtime_executor_vector_30534(const quantized_runtime *rt) {
    if (rt == NULL) {
        return (uintptr_t)0;
    }
    return rt->providers.vector_30534;
}

static uint32_t quantized_runtime_recurrent_stage_adapter(
    const void *descriptor,
    quantized_runtime_exec_tensor *const *inputs,
    quantized_runtime_exec_tensor *const *outputs) {
    return quantized_runtime_recurrent_execute_target(
        (const quantized_runtime_recurrent_descriptor *)descriptor,
        inputs, outputs);
}

quantized_runtime_stage_execute_fn
quantized_runtime_source_stage_token_resolve(
    void *context, uint32_t target_token) {
    (void)context;
#define QUANTIZED_RUNTIME_RESOLVE_STAGE(function_)                         \
    do {                                                                  \
        if (target_token == (uint32_t)(uintptr_t)&(function_)) {          \
            return &(function_);                                          \
        }                                                                 \
    } while (false)
    QUANTIZED_RUNTIME_RESOLVE_STAGE(quantized_runtime_pooling_execute);
    QUANTIZED_RUNTIME_RESOLVE_STAGE(
        quantized_runtime_i8_conv1d_execute_target);
    QUANTIZED_RUNTIME_RESOLVE_STAGE(
        quantized_runtime_float_dense_execute_target);
    QUANTIZED_RUNTIME_RESOLVE_STAGE(
        quantized_runtime_float_conv1d_execute_target);
    QUANTIZED_RUNTIME_RESOLVE_STAGE(quantized_runtime_float_add_execute);
    QUANTIZED_RUNTIME_RESOLVE_STAGE(quantized_runtime_int8_to_float_execute);
    QUANTIZED_RUNTIME_RESOLVE_STAGE(quantized_runtime_float_multiply_execute);
    QUANTIZED_RUNTIME_RESOLVE_STAGE(
        quantized_runtime_float_concatenate_two_execute);
    QUANTIZED_RUNTIME_RESOLVE_STAGE(
        quantized_runtime_float_strided_copy_2d_execute);
    QUANTIZED_RUNTIME_RESOLVE_STAGE(quantized_runtime_float_pool_1d_execute);
    if (target_token == (uint32_t)(uintptr_t)
            &quantized_runtime_recurrent_execute_target) {
        return quantized_runtime_recurrent_stage_adapter;
    }
#undef QUANTIZED_RUNTIME_RESOLVE_STAGE
    /* These three checked implementations require a runtime argument and
     * are selected by the plan builder's explicit adapter cases. */
    return NULL;
}

quantized_runtime_multi_stage_execute_fn
quantized_runtime_source_multi_stage_token_resolve(
    void *context, uint32_t target_token) {
    (void)context;
    return target_token == (uint32_t)(uintptr_t)
               &quantized_runtime_int8_concatenate_execute
        ? quantized_runtime_int8_concatenate_execute : NULL;
}

uintptr_t quantized_runtime_softmax_executor_vector(void) {
    return (uintptr_t)&quantized_runtime_float_softmax_execute;
}

void quantized_runtime_descriptor_construct(
    const quantized_runtime *rt, void *destination, uint8_t byte0,
    uint8_t byte1, uint8_t byte2, uint8_t byte3, uint8_t byte4,
    uint8_t byte5, uint8_t byte6, uint32_t reserved, uint8_t byte7,
    uint32_t *arena_cursor, float context) {
    (void)reserved; /* recovered: accepted but never stored */
    if (destination == NULL || arena_cursor == NULL) {
        return;
    }
    uint8_t *record = (uint8_t *)destination;
    zero_bytes(record, 0x18u);
    record[0] = byte0;
    record[1] = byte1;
    record[2] = byte2;
    record[3] = byte3;
    record[4] = byte4;
    record[5] = byte5;
    record[6] = byte6;
    record[7] = byte7;
    store_f32_le(record + 8, context);
    /* Recovered unsigned udiv; ARM returns 0 on divide-by-zero. */
    const uint32_t ratio =
        (byte6 != 0u) ? ((uint32_t)byte4 / (uint32_t)byte6) : 0u;
    const uint32_t span = ratio * (uint32_t)byte0 * (uint32_t)byte5 * 4u;
    const uint32_t weights = *arena_cursor;
    store_u32_le(record + 0x0C, weights);
    store_u32_le(record + 0x10, weights + span);
    (void)rt;
    store_u32_le(record + 0x14,
                 (uint32_t)(uintptr_t)&quantized_runtime_float_conv1d_execute_target);
    *arena_cursor = weights + (uint32_t)byte5 * 4u + span;
}

void quantized_runtime_descriptor_record_construct(
    const quantized_runtime *rt, void *destination, uint32_t dim_a,
    uint32_t dim_b, uint8_t flag_a, uint8_t flag_b, uint32_t *arena_cursor,
    float context) {
    if (destination == NULL || arena_cursor == NULL) {
        return;
    }
    uint8_t *record = (uint8_t *)destination;
    zero_bytes(record, 0x18u);
    store_u32_le(record + 0x00, dim_b);
    record[4] = flag_a;
    record[5] = flag_b;
    store_f32_le(record + 8, context);
    const uint32_t weights = *arena_cursor;
    const uint32_t span = dim_a * dim_b * 4u;
    store_u32_le(record + 0x0C, weights);
    store_u32_le(record + 0x10, weights + span);
    (void)rt;
    store_u32_le(record + 0x14,
                 (uint32_t)(uintptr_t)&quantized_runtime_float_dense_execute_target);
    *arena_cursor = weights + dim_b * 4u + span;
}

bool quantized_runtime_recurrent_layer_descriptor_construct(
    const quantized_runtime *rt,
    quantized_runtime_recurrent_descriptor *descriptor, uint32_t units,
    uint32_t input_dimension, uint32_t *arena_cursor,
    quantized_runtime_allocate_fn allocate, void *allocate_context) {
    (void)rt;
    if (descriptor == NULL || arena_cursor == NULL || allocate == NULL) {
        return false;
    }
    zero_bytes((uint8_t *)descriptor, sizeof(*descriptor));
    descriptor->units = units;

    if ((uint64_t)units * sizeof(float) > (uint64_t)SIZE_MAX) {
        return false;
    }
    const uint64_t input_unaligned =
        (uint64_t)units * (uint64_t)input_dimension * 3u;
    const uint64_t recurrent_unaligned =
        (uint64_t)units * (uint64_t)units * 3u;
    const uint64_t input_span = (input_unaligned + 3u) & ~UINT64_C(3);
    const uint64_t recurrent_span =
        (recurrent_unaligned + 3u) & ~UINT64_C(3);
    const uint64_t tail_span = ((uint64_t)units * 10u + 6u) * 4u;
    const uint64_t input_offset = *arena_cursor;
    const uint64_t recurrent_offset = input_offset + input_span;
    const uint64_t bias_offset = recurrent_offset + recurrent_span;
    const uint64_t arena_end = bias_offset + tail_span;
    if (input_span > UINT32_MAX || recurrent_offset > UINT32_MAX ||
            bias_offset > UINT32_MAX || arena_end > UINT32_MAX) {
        return false;
    }

    descriptor->state =
        (float *)allocate(allocate_context, (size_t)units * sizeof(float));
    if (descriptor->state == NULL) {
        return false;
    }
    zero_bytes((uint8_t *)descriptor->state, (size_t)units * sizeof(float));
    descriptor->input_weights_offset = (uint32_t)input_offset;
    descriptor->recurrent_weights_offset = (uint32_t)recurrent_offset;
    descriptor->bias_offset = (uint32_t)bias_offset;
    descriptor->execute =
        (uintptr_t)&quantized_runtime_recurrent_execute_target;
    *arena_cursor = (uint32_t)arena_end;
    return true;
}

void quantized_runtime_aligned_descriptor_construct(
    const quantized_runtime *rt, void *destination, uint8_t byte0,
    uint8_t byte1, uint8_t byte2, uint8_t byte3, uint8_t byte4,
    uint8_t byte5, uint8_t byte6, uint32_t reserved, uint8_t byte7,
    uint32_t *arena_cursor, float context) {
    (void)reserved; /* recovered: accepted but never stored */
    if (destination == NULL || arena_cursor == NULL) {
        return;
    }
    uint8_t *record = (uint8_t *)destination;
    zero_bytes(record, 0x18u);
    record[0] = byte0;
    record[1] = byte1;
    record[2] = byte2;
    record[3] = byte3;
    record[4] = byte4;
    record[5] = byte5;
    record[6] = byte6;
    record[7] = byte7;
    store_f32_le(record + 8, context);
    /* Recovered unsigned udiv and add-three/mask-down alignment idiom. */
    const uint32_t ratio =
        (byte6 != 0u) ? ((uint32_t)byte4 / (uint32_t)byte6) : 0u;
    const uint32_t packed_span =
        ((uint32_t)byte5 * (uint32_t)byte0 * ratio + 3u) & ~UINT32_C(3);
    const uint32_t weights = *arena_cursor;
    const uint32_t aligned_end = weights + packed_span;
    store_u32_le(record + 0x0C, weights);
    store_u32_le(record + 0x10,
                 aligned_end + (uint32_t)byte5 * 4u + 8u);
    (void)rt;
    store_u32_le(record + 0x14,
                 (uint32_t)(uintptr_t)&quantized_runtime_i8_conv1d_execute_target);
    *arena_cursor = aligned_end + (uint32_t)byte5 * 8u + 0x18u;
}

void quantized_runtime_packed_pool_descriptor_initialize(
    void *destination, uint32_t byte0, uint32_t byte1, uint32_t byte2,
    uint32_t byte3) {
    if (destination == NULL) {
        return;
    }
    uint8_t *record = (uint8_t *)destination;
    const uint32_t packed = (byte0 & 0xFFu) | ((byte1 & 0xFFu) << 8) |
                            ((byte2 & 0xFFu) << 16) | (byte3 << 24);
    store_u32_le(record, packed);
    store_u32_le(record + 4,
                 (uint32_t)(uintptr_t)&quantized_runtime_pooling_execute);
}

void quantized_runtime_cursor_pair_add_descriptor_construct(
    void *destination, const uint32_t **cursor) {
    if (destination == NULL || cursor == NULL || *cursor == NULL) {
        return;
    }
    const uint32_t *words = *cursor;
    uint8_t *record = (uint8_t *)destination;
    store_u32_le(record + 0x00, 0u);
    store_u32_le(record + 0x04, words[0]);
    store_u32_le(record + 0x08, words[1]);
    store_u32_le(record + 0x0C,
                 (uint32_t)(uintptr_t)&quantized_runtime_int8_add_execute);
    *cursor = words + 2;
}

typedef struct {
    uint16_t destination_offset;
    uint8_t byte0;
    uint8_t byte1;
    uint8_t byte2;
    uint8_t byte3;
    uint8_t byte4;
    uint8_t byte5;
    uint8_t byte6;
    uint8_t byte7;
} quantized_runtime_graph_record_spec;

static void graph_build_aligned_record(
    const quantized_runtime *rt, uint8_t *graph_bytes,
    const quantized_runtime_graph_record_spec *spec, uint32_t *target_cursor,
    size_t *consumed_words) {
    const uint32_t before = *target_cursor;
    quantized_runtime_aligned_descriptor_construct(
        rt, graph_bytes + spec->destination_offset, spec->byte0, spec->byte1,
        spec->byte2, spec->byte3, spec->byte4, spec->byte5, spec->byte6, 1u,
        spec->byte7, target_cursor, 0.0f);
    *consumed_words += (size_t)(*target_cursor - before) / 4u;
}

static void graph_build_descriptor_record(
    const quantized_runtime *rt, uint8_t *graph_bytes,
    const quantized_runtime_graph_record_spec *spec, uint32_t *target_cursor,
    size_t *consumed_words) {
    const uint32_t before = *target_cursor;
    quantized_runtime_descriptor_construct(
        rt, graph_bytes + spec->destination_offset, spec->byte0, spec->byte1,
        spec->byte2, spec->byte3, spec->byte4, spec->byte5, spec->byte6, 1u,
        spec->byte7, target_cursor, 0.0f);
    *consumed_words += (size_t)(*target_cursor - before) / 4u;
}

static void gomore_sleep_graph_store_binding(uint8_t *destination,
                                             uint32_t packed,
                                             uintptr_t binding) {
    store_u32_le(destination, packed);
    store_u32_le(destination + 4u, (uint32_t)binding);
}

static void gomore_sleep_graph_build_common_prefix(
    const quantized_runtime *rt, uint8_t *graph_bytes,
    const quantized_runtime_graph_record_spec aligned_specs[7],
    const uint32_t *model_words, uint32_t *target_cursor,
    size_t *consumed_words) {
    graph_build_aligned_record(rt, graph_bytes, &aligned_specs[0],
                               target_cursor, consumed_words);
    quantized_runtime_packed_pool_descriptor_initialize(
        graph_bytes + 0x024u, 0u, 2u, 0u, 0u);
    for (size_t index = 1u; index < 4u; ++index) {
        graph_build_aligned_record(rt, graph_bytes, &aligned_specs[index],
                                   target_cursor, consumed_words);
    }
    const uint32_t *host_cursor = model_words + *consumed_words;
    quantized_runtime_cursor_pair_add_descriptor_construct(
        graph_bytes + 0x078u, &host_cursor);
    *consumed_words += 2u;
    *target_cursor += 8u;
    quantized_runtime_packed_pool_descriptor_initialize(
        graph_bytes + 0x088u, 0u, 2u, 0u, 0u);

    for (size_t index = 4u; index < 7u; ++index) {
        graph_build_aligned_record(rt, graph_bytes, &aligned_specs[index],
                                   target_cursor, consumed_words);
    }
    host_cursor = model_words + *consumed_words;
    quantized_runtime_cursor_pair_add_descriptor_construct(
        graph_bytes + 0x0E0u, &host_cursor);
    *consumed_words += 2u;
    *target_cursor += 8u;
    quantized_runtime_packed_pool_descriptor_initialize(
        graph_bytes + 0x0F0u, 0u, 2u, 0u, 0u);
    store_u32_le(graph_bytes + 0x090u,
                 (uint32_t)quantized_runtime_executor_vector_30534(rt));
}

static void gomore_sleep_graph_build_common_tail(
    const quantized_runtime *rt, uint8_t *graph_bytes,
    const quantized_runtime_graph_record_spec descriptor_specs[6],
    uint32_t *target_cursor, size_t *consumed_words) {
    const uintptr_t vector_35d12 =
        rt != NULL ? rt->providers.vector_35d12 : (uintptr_t)0;
    const uintptr_t vector_7ca94 =
        rt != NULL ? rt->providers.vector_7ca94 : (uintptr_t)0;
    gomore_sleep_graph_store_binding(graph_bytes + 0x0F8u,
                                     UINT32_C(0x00010200), vector_35d12);
    gomore_sleep_graph_store_binding(graph_bytes + 0x100u,
                                     UINT32_C(0x00000001), vector_7ca94);

    graph_build_descriptor_record(rt, graph_bytes, &descriptor_specs[0],
                                  target_cursor, consumed_words);
    graph_build_descriptor_record(rt, graph_bytes, &descriptor_specs[1],
                                  target_cursor, consumed_words);
    gomore_sleep_graph_store_binding(graph_bytes + 0x138u,
                                     UINT32_C(0x00020100), vector_35d12);
    store_u32_le(graph_bytes + 0x140u,
                 (uint32_t)quantized_runtime_executor_vector_95b20(rt));
    for (size_t index = 2u; index < 6u; ++index) {
        graph_build_descriptor_record(rt, graph_bytes,
                                      &descriptor_specs[index],
                                      target_cursor, consumed_words);
    }

    uintptr_t operator_descriptor[4];
    quantized_runtime_operator_descriptor_init(operator_descriptor, 1u, 0.0f);
    store_native_words_as_u32(graph_bytes + 0x1A8u,
                              operator_descriptor, 4u);
}

bool quantized_runtime_gomore_sleep_graph_family_zero_build(
    const quantized_runtime *rt,
    quantized_runtime_gomore_sleep_graph *graph,
    const uint32_t *model_words, size_t model_word_count,
    uint32_t model_base_address, size_t *consumed_words,
    uint32_t *model_end_address) {
    if (graph == NULL || model_words == NULL ||
            model_word_count <
                QUANTIZED_RUNTIME_GOMORE_SLEEP_GRAPH_ZERO_MODEL_WORDS ||
            (model_base_address & 3u) != 0u ||
            model_base_address > UINT32_MAX -
                QUANTIZED_RUNTIME_GOMORE_SLEEP_GRAPH_ZERO_MODEL_WORDS * 4u) {
        return false;
    }

    static const quantized_runtime_graph_record_spec aligned_specs[7] = {
        {0x00Cu, 5u, 1u, 2u, 2u, 4u, 27u, 1u, 0u},
        {0x02Cu, 1u, 1u, 0u, 0u, 27u, 14u, 1u, 1u},
        {0x044u, 3u, 1u, 1u, 1u, 14u, 14u, 14u, 1u},
        {0x05Cu, 1u, 1u, 0u, 0u, 14u, 27u, 1u, 0u},
        {0x094u, 1u, 1u, 0u, 0u, 27u, 7u, 1u, 1u},
        {0x0ACu, 3u, 1u, 1u, 1u, 7u, 7u, 7u, 1u},
        {0x0C4u, 1u, 1u, 0u, 0u, 7u, 27u, 1u, 0u},
    };
    static const quantized_runtime_graph_record_spec descriptor_specs[6] = {
        {0x108u, 1u, 1u, 0u, 0u, 12u, 12u, 1u, 1u},
        {0x120u, 1u, 1u, 0u, 0u, 12u, 12u, 1u, 2u},
        {0x15Cu, 1u, 1u, 0u, 0u, 27u, 11u, 1u, 1u},
        {0x174u, 3u, 1u, 1u, 1u, 11u, 11u, 11u, 1u},
        {0x18Cu, 1u, 1u, 0u, 0u, 11u, 8u, 1u, 0u},
        {0x144u, 1u, 1u, 0u, 0u, 27u, 8u, 1u, 0u},
    };

    zero_bytes(graph->bytes, sizeof(graph->bytes));
    uintptr_t quantizer[3];
    quantized_runtime_quantizer_descriptor_construct(quantizer, NULL);
    store_native_words_as_u32(graph->bytes, quantizer, 3u);
    uint32_t target_cursor = model_base_address;
    size_t consumed = 0u;
    gomore_sleep_graph_build_common_prefix(
        rt, graph->bytes, aligned_specs, model_words,
        &target_cursor, &consumed);
    gomore_sleep_graph_build_common_tail(
        rt, graph->bytes, descriptor_specs, &target_cursor, &consumed);

    if (consumed != QUANTIZED_RUNTIME_GOMORE_SLEEP_GRAPH_ZERO_MODEL_WORDS ||
            target_cursor != model_base_address + consumed * 4u) {
        zero_bytes(graph->bytes, sizeof(graph->bytes));
        return false;
    }
    if (consumed_words != NULL) {
        *consumed_words = consumed;
    }
    if (model_end_address != NULL) {
        *model_end_address = target_cursor;
    }
    return true;
}

bool quantized_runtime_gomore_sleep_graph_family_nonzero_build(
    const quantized_runtime *rt, uint32_t family,
    quantized_runtime_gomore_sleep_graph *graph,
    const uint32_t *model_words, size_t model_word_count,
    uint32_t model_base_address, size_t *consumed_words,
    uint32_t *model_end_address) {
    const size_t expected_words = family == 1u
        ? QUANTIZED_RUNTIME_GOMORE_SLEEP_GRAPH_FAMILY1_MODEL_WORDS
        : QUANTIZED_RUNTIME_GOMORE_SLEEP_GRAPH_FAMILY2_MODEL_WORDS;
    if (graph == NULL || model_words == NULL || family < 1u || family > 2u ||
            model_word_count < expected_words ||
            (model_base_address & 3u) != 0u ||
            model_base_address > UINT32_MAX - expected_words * 4u) {
        return false;
    }

    static const quantized_runtime_graph_record_spec aligned_specs[7] = {
        {0x00Cu, 5u, 1u, 2u, 2u, 4u, 32u, 1u, 0u},
        {0x02Cu, 1u, 1u, 0u, 0u, 32u, 1u, 1u, 1u},
        {0x044u, 3u, 1u, 1u, 1u, 1u, 1u, 1u, 1u},
        {0x05Cu, 1u, 1u, 0u, 0u, 1u, 32u, 1u, 0u},
        {0x094u, 1u, 1u, 0u, 0u, 32u, 2u, 1u, 1u},
        {0x0ACu, 3u, 1u, 1u, 1u, 2u, 2u, 2u, 1u},
        {0x0C4u, 1u, 1u, 0u, 0u, 2u, 32u, 1u, 0u},
    };
    quantized_runtime_graph_record_spec descriptor_specs[6] = {
        {0x108u, 1u, 1u, 0u, 0u, 12u, 12u, 1u, 1u},
        {0x120u, 1u, 1u, 0u, 0u, 12u, 12u, 1u, 2u},
        {0x15Cu, 1u, 1u, 0u, 0u, 32u, 1u, 1u, 1u},
        {0x174u, 3u, 1u, 1u, 1u, 1u, 1u, 1u, 1u},
        {0x18Cu, 1u, 1u, 0u, 0u, 1u, 0u, 1u, 0u},
        {0x144u, 1u, 1u, 0u, 0u, 32u, 0u, 1u, 0u},
    };
    const uint8_t output_channels = family == 1u ? 4u : 8u;
    descriptor_specs[4].byte5 = output_channels;
    descriptor_specs[5].byte5 = output_channels;

    zero_bytes(graph->bytes, sizeof(graph->bytes));
    const uint32_t *host_cursor = model_words;
    uintptr_t quantizer[3];
    quantized_runtime_quantizer_descriptor_construct(quantizer, &host_cursor);
    store_native_words_as_u32(graph->bytes, quantizer, 3u);
    uint32_t target_cursor = model_base_address + 8u;
    size_t consumed = 2u;
    gomore_sleep_graph_build_common_prefix(
        rt, graph->bytes, aligned_specs, model_words,
        &target_cursor, &consumed);
    gomore_sleep_graph_build_common_tail(
        rt, graph->bytes, descriptor_specs, &target_cursor, &consumed);

    if (consumed != expected_words ||
            target_cursor != model_base_address + consumed * 4u) {
        zero_bytes(graph->bytes, sizeof(graph->bytes));
        return false;
    }
    if (consumed_words != NULL) {
        *consumed_words = consumed;
    }
    if (model_end_address != NULL) {
        *model_end_address = target_cursor;
    }
    return true;
}

static void gomore_executor_pack_recurrent(
    uint8_t *destination,
    const quantized_runtime_recurrent_descriptor *descriptor) {
    zero_bytes(destination, 0x18u);
    store_u32_le(destination + 0x00u, descriptor->units);
    store_u32_le(destination + 0x04u,
                 (uint32_t)(uintptr_t)descriptor->state);
    store_u32_le(destination + 0x08u,
                 descriptor->input_weights_offset);
    store_u32_le(destination + 0x0Cu,
                 descriptor->recurrent_weights_offset);
    store_u32_le(destination + 0x10u, descriptor->bias_offset);
    store_u32_le(destination + 0x14u, (uint32_t)descriptor->execute);
}

void quantized_runtime_gomore_executor_graph_destroy(
    quantized_runtime_gomore_executor_graph *graph,
    quantized_runtime_release_fn release, void *release_context) {
    if (graph == NULL) {
        return;
    }
    if (release != NULL) {
        for (size_t index = 0u; index < 3u; ++index) {
            if (graph->recurrent[index].state != NULL) {
                release(release_context, graph->recurrent[index].state);
            }
        }
    }
    zero_bytes((uint8_t *)graph, sizeof(*graph));
}

bool quantized_runtime_gomore_executor_graph_build(
    const quantized_runtime *rt,
    quantized_runtime_gomore_executor_graph *graph, uint32_t mode,
    const uint32_t *model_words, size_t model_word_count,
    uint32_t model_base_address, const uint32_t *mode0_remap_words,
    size_t mode0_remap_word_count, uint32_t mode0_remap_base_address,
    const uint8_t tail_schema[8], quantized_runtime_allocate_fn allocate,
    quantized_runtime_release_fn release, void *allocator_context,
    size_t *consumed_words, uint32_t *model_end_address) {
    if (consumed_words != NULL) {
        *consumed_words = 0u;
    }
    if (model_end_address != NULL) {
        *model_end_address = model_base_address;
    }
    if (graph == NULL || model_words == NULL || tail_schema == NULL ||
            allocate == NULL || release == NULL || mode > 1u) {
        return false;
    }
    const size_t expected_words = mode == 0u
        ? QUANTIZED_RUNTIME_GOMORE_EXECUTOR_MODE0_MODEL_WORDS
        : QUANTIZED_RUNTIME_GOMORE_EXECUTOR_MODE1_MODEL_WORDS;
    if (model_word_count < expected_words ||
            (model_base_address & 3u) != 0u ||
            model_base_address > UINT32_MAX - expected_words * 4u ||
            (mode == 0u &&
             (mode0_remap_words == NULL || mode0_remap_word_count < 2u ||
              (mode0_remap_base_address & 3u) != 0u))) {
        return false;
    }

    zero_bytes((uint8_t *)graph, sizeof(*graph));
    graph->mode = mode;
    graph->runtime = rt;
    graph->byte_count = mode == 0u
        ? QUANTIZED_RUNTIME_GOMORE_EXECUTOR_GRAPH_MODE0_BYTES
        : QUANTIZED_RUNTIME_GOMORE_EXECUTOR_GRAPH_MODE1_BYTES;
    store_u32_le(graph->bytes, mode);

    quantized_runtime_gomore_sleep_graph prefix;
    size_t prefix_words = 0u;
    uint32_t target_cursor = model_base_address;
    const bool prefix_ok = mode == 0u
        ? quantized_runtime_gomore_sleep_graph_family_zero_build(
              rt, &prefix, model_words, model_word_count,
              model_base_address, &prefix_words, &target_cursor)
        : quantized_runtime_gomore_sleep_graph_family_nonzero_build(
              rt, mode, &prefix, model_words, model_word_count,
              model_base_address, &prefix_words, &target_cursor);
    if (!prefix_ok) {
        quantized_runtime_gomore_executor_graph_destroy(
            graph, release, allocator_context);
        return false;
    }
    move_bytes_local(graph->bytes + 4u, prefix.bytes, sizeof(prefix.bytes));
    size_t consumed = prefix_words;

    const uint32_t recurrent_units[3] = {
        8u, tail_schema[0], tail_schema[2],
    };
    const uint32_t recurrent_inputs[3] = {
        4u, tail_schema[1], tail_schema[3],
    };
    const size_t recurrent_offsets[3] = {0x1BCu, 0x1D8u, 0x1F0u};
    for (size_t index = 0u; index < 3u; ++index) {
        const uint32_t before = target_cursor;
        if (!quantized_runtime_recurrent_layer_descriptor_construct(
                rt, &graph->recurrent[index], recurrent_units[index],
                recurrent_inputs[index], &target_cursor, allocate,
                allocator_context)) {
            quantized_runtime_gomore_executor_graph_destroy(
                graph, release, allocator_context);
            return false;
        }
        consumed += (size_t)(target_cursor - before) / 4u;
        gomore_executor_pack_recurrent(
            graph->bytes + recurrent_offsets[index],
            &graph->recurrent[index]);
    }
    store_u32_le(graph->bytes + 0x1D4u,
                 (uint32_t)quantized_runtime_executor_vector_36dcc(rt));

    const uint32_t dense_a[2] = {tail_schema[4], tail_schema[6]};
    const uint32_t dense_b[2] = {tail_schema[5], tail_schema[7]};
    const uint8_t dense_flag_b[2] = {1u, 0u};
    const size_t dense_offsets[2] = {0x208u, 0x220u};
    for (size_t index = 0u; index < 2u; ++index) {
        const uint32_t before = target_cursor;
        quantized_runtime_descriptor_record_construct(
            rt, graph->bytes + dense_offsets[index], dense_a[index],
            dense_b[index], 1u, dense_flag_b[index], &target_cursor, 0.0f);
        consumed += (size_t)(target_cursor - before) / 4u;
    }

    if (consumed != expected_words ||
            target_cursor != model_base_address + expected_words * 4u) {
        quantized_runtime_gomore_executor_graph_destroy(
            graph, release, allocator_context);
        return false;
    }

    if (mode == 0u) {
        const uint32_t count = mode0_remap_words[0];
        if (count == 0u || mode0_remap_word_count <= count ||
                mode0_remap_base_address > UINT32_MAX -
                    mode0_remap_word_count * 4u) {
            quantized_runtime_gomore_executor_graph_destroy(
                graph, release, allocator_context);
            return false;
        }
        const size_t stride = (mode0_remap_word_count - 1u) / count;
        if (stride == 0u) {
            quantized_runtime_gomore_executor_graph_destroy(
                graph, release, allocator_context);
            return false;
        }
        for (size_t index = 0u; index < count; ++index) {
            const size_t entry = index * stride;
            if (entry + 1u >= mode0_remap_word_count) {
                quantized_runtime_gomore_executor_graph_destroy(
                    graph, release, allocator_context);
                return false;
            }
            const size_t destination_word =
                (size_t)mode0_remap_words[entry + 1u] + 0x8Eu;
            const uint64_t destination_offset = destination_word * 4u;
            const uint64_t source_address =
                (uint64_t)mode0_remap_base_address + (entry + 2u) * 4u;
            if (destination_offset + 4u > graph->byte_count ||
                    source_address > UINT32_MAX) {
                quantized_runtime_gomore_executor_graph_destroy(
                    graph, release, allocator_context);
                return false;
            }
            store_u32_le(graph->bytes + destination_offset,
                         (uint32_t)source_address);
        }
    }

    if (consumed_words != NULL) {
        *consumed_words = consumed;
    }
    if (model_end_address != NULL) {
        *model_end_address = target_cursor;
    }
    return true;
}

static bool gomore_executor_plan_stage(
    const quantized_runtime_gomore_executor_graph *graph,
    quantized_runtime_stage *stage, size_t descriptor_offset,
    size_t token_offset, quantized_runtime_stage_token_resolver_fn resolve,
    void *resolve_context, bool required) {
    if (descriptor_offset + 1u > graph->byte_count ||
            token_offset + 4u > graph->byte_count) {
        return false;
    }
    const uint32_t token = load_u32_le(graph->bytes + token_offset);
    stage->descriptor = graph->bytes + descriptor_offset;
    stage->execute = token != 0u ? resolve(resolve_context, token) : NULL;
    if (stage->execute != NULL) {
        /* See the complete-owner resolver path above. */
    } else if (token == (uint32_t)(uintptr_t)
            &quantized_runtime_float_to_int8_quantize) {
        stage->runtime = graph->runtime;
        stage->adapter = QUANTIZED_RUNTIME_STAGE_QUANTIZE_WITH_RUNTIME;
    } else if (token == (uint32_t)(uintptr_t)
                   &quantized_runtime_int8_add_execute) {
        stage->runtime = graph->runtime;
        stage->adapter = QUANTIZED_RUNTIME_STAGE_INT8_ADD_WITH_RUNTIME;
    } else if (token == (uint32_t)(uintptr_t)
                   &quantized_runtime_float_softmax_execute) {
        stage->runtime = graph->runtime;
        stage->adapter = QUANTIZED_RUNTIME_STAGE_SOFTMAX_WITH_RUNTIME;
    }
    return !required || stage_callable(stage);
}

bool quantized_runtime_gomore_executor_plan_build(
    const quantized_runtime_gomore_executor_graph *graph,
    quantized_runtime_goodix_executor_plan *plan,
    quantized_runtime_stage_token_resolver_fn resolve,
    void *resolve_context) {
    if (graph == NULL || plan == NULL || resolve == NULL || graph->mode > 1u ||
            graph->byte_count != (graph->mode == 0u
                ? QUANTIZED_RUNTIME_GOMORE_EXECUTOR_GRAPH_MODE0_BYTES
                : QUANTIZED_RUNTIME_GOMORE_EXECUTOR_GRAPH_MODE1_BYTES) ||
            load_u32_le(graph->bytes) != graph->mode) {
        return false;
    }
    zero_bytes((uint8_t *)plan, sizeof(*plan));
    plan->mode = graph->mode;

    static const uint16_t descriptor_offsets[
        QUANTIZED_RUNTIME_GOODIX_EXECUTOR_STAGE_COUNT] = {
        0x004u, 0x010u, 0x028u, 0x07Cu, 0x08Cu, 0x0E4u,
        0x0F4u, 0x094u, 0x144u, 0x148u, 0x1ACu, 0x1BCu,
        0x1D4u, 0x1D8u, 0x1F0u, 0x208u, 0x220u, 0x238u,
    };
    static const uint16_t token_offsets[
        QUANTIZED_RUNTIME_GOODIX_EXECUTOR_STAGE_COUNT] = {
        0x00Cu, 0x024u, 0x02Cu, 0x088u, 0x090u, 0x0F0u,
        0x0F8u, 0x094u, 0x144u, 0x15Cu, 0x1B8u, 0x1D0u,
        0x1D4u, 0x1ECu, 0x204u, 0x21Cu, 0x234u, 0x238u,
    };
    for (size_t index = 0u;
            index < QUANTIZED_RUNTIME_GOODIX_EXECUTOR_STAGE_COUNT; ++index) {
        if (index == 17u && graph->mode != 2u) {
            continue;
        }
        const bool required = index != 17u &&
            (index != 0u || graph->mode == 0u);
        if (!gomore_executor_plan_stage(
                graph, &plan->stages[index], descriptor_offsets[index],
                token_offsets[index], resolve, resolve_context, required)) {
            zero_bytes((uint8_t *)plan, sizeof(*plan));
            return false;
        }
    }
    plan->stages[11].descriptor = &graph->recurrent[0];
    plan->stages[13].descriptor = &graph->recurrent[1];
    plan->stages[14].descriptor = &graph->recurrent[2];

    static const uint16_t three_descriptors[3][3] = {
        {0x030u, 0x048u, 0x060u},
        {0x098u, 0x0B0u, 0x0C8u},
        {0x160u, 0x178u, 0x190u},
    };
    static const uint16_t three_tokens[3][3] = {
        {0x044u, 0x05Cu, 0x074u},
        {0x0ACu, 0x0C4u, 0x0DCu},
        {0x174u, 0x18Cu, 0x1A4u},
    };
    quantized_runtime_three_stage_plan *three_plans[3] = {
        &plan->quantized_49, &plan->quantized_24, &plan->float_12,
    };
    for (size_t group = 0u; group < 3u; ++group) {
        for (size_t index = 0u; index < 3u; ++index) {
            if (!gomore_executor_plan_stage(
                    graph, &three_plans[group]->stages[index],
                    three_descriptors[group][index],
                    three_tokens[group][index], resolve, resolve_context,
                    true)) {
                zero_bytes((uint8_t *)plan, sizeof(*plan));
                return false;
            }
        }
    }

    static const uint16_t five_descriptors[5] = {
        0x0FCu, 0x104u, 0x10Cu, 0x124u, 0x13Cu,
    };
    static const uint16_t five_tokens[5] = {
        0x100u, 0x108u, 0x120u, 0x138u, 0x140u,
    };
    quantized_runtime_five_stage_plan *five = graph->mode == 0u
        ? &plan->five_stage_27 : &plan->five_stage_32;
    for (size_t index = 0u; index < 5u; ++index) {
        if (!gomore_executor_plan_stage(
                graph, &five->stages[index], five_descriptors[index],
                five_tokens[index], resolve, resolve_context, true)) {
            zero_bytes((uint8_t *)plan, sizeof(*plan));
            return false;
        }
    }

    plan->head_width_mode0 = graph->recurrent[0].units;
    plan->head_width_other = graph->recurrent[0].units;
    plan->tail_widths[0] = graph->recurrent[1].units;
    plan->tail_widths[1] = graph->recurrent[2].units;
    plan->tail_widths[2] = load_u32_le(graph->bytes + 0x208u);
    plan->tail_widths[3] = load_u32_le(graph->bytes + 0x220u);
    return true;
}

bool quantized_runtime_goodix_graph_build(
    const quantized_runtime *rt, quantized_runtime_goodix_graph *graph,
    const uint32_t *model_words, size_t model_word_count,
    uint32_t model_base_address, size_t *consumed_words,
    uint32_t *model_end_address) {
    if (graph == NULL || model_words == NULL ||
            model_word_count < QUANTIZED_RUNTIME_GOODIX_GRAPH_MODEL_WORDS ||
            (model_base_address & 3u) != 0u ||
            model_base_address >
                UINT32_MAX - QUANTIZED_RUNTIME_GOODIX_GRAPH_MODEL_WORDS * 4u) {
        return false;
    }

    static const quantized_runtime_graph_record_spec aligned_specs[] = {
        {0x00Cu, 5u, 1u, 2u, 2u, 1u, 16u, 1u, 0u},
        {0x02Cu, 1u, 1u, 0u, 0u, 16u, 4u, 1u, 1u},
        {0x044u, 3u, 1u, 1u, 1u, 4u, 4u, 4u, 1u},
        {0x05Cu, 1u, 1u, 0u, 0u, 4u, 16u, 1u, 0u},
        {0x08Cu, 1u, 1u, 0u, 0u, 16u, 4u, 1u, 1u},
        {0x0A4u, 3u, 1u, 1u, 1u, 4u, 4u, 4u, 1u},
        {0x0BCu, 1u, 1u, 0u, 0u, 4u, 16u, 1u, 0u},
    };
    static const quantized_runtime_graph_record_spec descriptor_specs[] = {
        {0x108u, 1u, 1u, 0u, 0u, 16u, 1u, 1u, 1u},
        {0x120u, 3u, 1u, 1u, 1u, 1u, 1u, 1u, 1u},
        {0x138u, 1u, 1u, 0u, 0u, 1u, 8u, 1u, 0u},
        {0x0F0u, 1u, 1u, 0u, 0u, 16u, 8u, 1u, 0u},
    };

    zero_bytes(graph->bytes, sizeof(graph->bytes));
    uint32_t target_cursor = model_base_address;
    size_t consumed = 0u;

    /* Quantizer consumes the first {min,max} pair. */
    const uint32_t *host_cursor = model_words;
    uintptr_t quantizer[3];
    quantized_runtime_quantizer_descriptor_construct(quantizer, &host_cursor);
    store_native_words_as_u32(graph->bytes, quantizer, 3u);
    consumed += 2u;
    target_cursor += 8u;

    graph_build_aligned_record(rt, graph->bytes, &aligned_specs[0],
                               &target_cursor, &consumed);
    quantized_runtime_packed_pool_descriptor_initialize(
        graph->bytes + 0x024u, 0u, 2u, 2u, 0u);
    for (size_t index = 1u; index < 4u; ++index) {
        graph_build_aligned_record(rt, graph->bytes, &aligned_specs[index],
                                   &target_cursor, &consumed);
    }
    host_cursor = model_words + consumed;
    quantized_runtime_cursor_pair_add_descriptor_construct(
        graph->bytes + 0x074u, &host_cursor);
    consumed += 2u;
    target_cursor += 8u;
    quantized_runtime_packed_pool_descriptor_initialize(
        graph->bytes + 0x084u, 0u, 2u, 2u, 0u);

    for (size_t index = 4u; index < 7u; ++index) {
        graph_build_aligned_record(rt, graph->bytes, &aligned_specs[index],
                                   &target_cursor, &consumed);
    }
    host_cursor = model_words + consumed;
    quantized_runtime_cursor_pair_add_descriptor_construct(
        graph->bytes + 0x0D4u, &host_cursor);
    consumed += 2u;
    target_cursor += 8u;
    quantized_runtime_packed_pool_descriptor_initialize(
        graph->bytes + 0x0E4u, 0u, 2u, 2u, 0u);
    store_u32_le(graph->bytes + 0x0ECu,
                 (uint32_t)quantized_runtime_executor_vector_30534(rt));

    for (size_t index = 0u; index < 4u; ++index) {
        graph_build_descriptor_record(rt, graph->bytes,
                                      &descriptor_specs[index],
                                      &target_cursor, &consumed);
    }

    uintptr_t operator_descriptor[4];
    quantized_runtime_operator_descriptor_init(operator_descriptor, 1u, 0.0f);
    store_native_words_as_u32(graph->bytes + 0x150u,
                              operator_descriptor, 4u);

    if (consumed != QUANTIZED_RUNTIME_GOODIX_GRAPH_MODEL_WORDS ||
            target_cursor != model_base_address + consumed * 4u) {
        zero_bytes(graph->bytes, sizeof(graph->bytes));
        return false;
    }
    if (consumed_words != NULL) {
        *consumed_words = consumed;
    }
    if (model_end_address != NULL) {
        *model_end_address = target_cursor;
    }
    return true;
}

static void goodix_model_build_descriptor_record(
    const quantized_runtime *rt, uint8_t *destination, uint32_t dim_a,
    uint32_t dim_b, uint8_t flag_a, uint8_t flag_b,
    uint32_t *target_cursor, size_t *consumed_words) {
    const uint32_t before = *target_cursor;
    quantized_runtime_descriptor_record_construct(
        rt, destination, dim_a, dim_b, flag_a, flag_b, target_cursor, 0.0f);
    *consumed_words += (size_t)(*target_cursor - before) / 4u;
}

void quantized_runtime_goodix_model_instance_destroy(
    quantized_runtime_goodix_model_instance **instance,
    quantized_runtime_release_fn release, void *release_context) {
    if (instance == NULL || *instance == NULL || release == NULL) {
        return;
    }
    quantized_runtime_goodix_model_instance *owned = *instance;
    if (owned->recurrent.state != NULL) {
        release(release_context, owned->recurrent.state);
        owned->recurrent.state = NULL;
    }
    release(release_context, owned);
    *instance = NULL;
}

bool quantized_runtime_goodix_model_instance_create(
    const quantized_runtime *rt,
    quantized_runtime_goodix_model_instance **out_instance,
    const uint32_t *model_words, size_t model_word_count,
    uint32_t model_base_address, quantized_runtime_allocate_fn allocate,
    quantized_runtime_release_fn release, void *allocator_context,
    size_t *consumed_words, uint32_t *model_end_address) {
    if (out_instance != NULL) {
        *out_instance = NULL;
    }
    if (out_instance == NULL || model_words == NULL || allocate == NULL ||
            release == NULL ||
            model_word_count <
                QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS ||
            (model_base_address & 3u) != 0u ||
            model_base_address > UINT32_MAX -
                QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS * 4u) {
        return false;
    }
    quantized_runtime_goodix_model_instance *instance =
        (quantized_runtime_goodix_model_instance *)allocate(
            allocator_context, sizeof(*instance));
    if (instance == NULL) {
        return false;
    }
    zero_bytes((uint8_t *)instance, sizeof(*instance));

    size_t consumed = 0u;
    uint32_t target_cursor = model_base_address;
    size_t graph_consumed = 0u;
    uint32_t graph_end = 0u;
    if (!quantized_runtime_goodix_graph_build(
            rt, &instance->graph_a, model_words, model_word_count,
            target_cursor, &graph_consumed, &graph_end)) {
        release(allocator_context, instance);
        return false;
    }
    consumed += graph_consumed;
    target_cursor = graph_end;
    if (!quantized_runtime_goodix_graph_build(
            rt, &instance->graph_b, model_words + consumed,
            model_word_count - consumed, target_cursor,
            &graph_consumed, &graph_end)) {
        release(allocator_context, instance);
        return false;
    }
    consumed += graph_consumed;
    target_cursor = graph_end;

    goodix_model_build_descriptor_record(
        rt, instance->descriptor_a, 120u, 8u, 1u, 1u,
        &target_cursor, &consumed);
    goodix_model_build_descriptor_record(
        rt, instance->descriptor_b, 8u, 3u, 1u, 0u,
        &target_cursor, &consumed);
    instance->softmax_execute = quantized_runtime_softmax_executor_vector();
    instance->vector_36dcc = quantized_runtime_executor_vector_36dcc(rt);

    const uint32_t recurrent_before = target_cursor;
    if (!quantized_runtime_recurrent_layer_descriptor_construct(
            rt, &instance->recurrent, 16u, 123u, &target_cursor,
            allocate, allocator_context)) {
        release(allocator_context, instance);
        return false;
    }
    consumed += (size_t)(target_cursor - recurrent_before) / 4u;
    goodix_model_build_descriptor_record(
        rt, instance->descriptor_c, 16u, 12u, 1u, 1u,
        &target_cursor, &consumed);
    goodix_model_build_descriptor_record(
        rt, instance->descriptor_d, 12u, 1u, 1u, 0u,
        &target_cursor, &consumed);

    if (consumed != QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS ||
            target_cursor != model_base_address + consumed * 4u) {
        quantized_runtime_goodix_model_instance *rollback = instance;
        quantized_runtime_goodix_model_instance_destroy(
            &rollback, release, allocator_context);
        return false;
    }
    *out_instance = instance;
    if (consumed_words != NULL) {
        *consumed_words = consumed;
    }
    if (model_end_address != NULL) {
        *model_end_address = target_cursor;
    }
    return true;
}

bool quantized_runtime_goodix_model_owner_initialize(
    const quantized_runtime *rt,
    quantized_runtime_goodix_model_owner *owner,
    const uint32_t *model_words, size_t model_word_count,
    uint32_t model_base_address, quantized_runtime_allocate_fn allocate,
    quantized_runtime_release_fn release, void *allocator_context) {
    if (owner == NULL) {
        return false;
    }
    owner->primary_enabled = 1u;
    owner->primary_stride = 1u;
    owner->primary_window = 125u;
    owner->secondary_enabled = 1u;
    owner->secondary_stride = 1u;
    owner->secondary_window = 125u;
    owner->input_channels = 1u;
    owner->graph_count = 2u;
    owner->output_channels = 1u;
    owner->instance = NULL;
    return quantized_runtime_goodix_model_instance_create(
        rt, &owner->instance, model_words, model_word_count,
        model_base_address, allocate, release, allocator_context,
        NULL, NULL);
}

void quantized_runtime_goodix_model_owner_destroy(
    quantized_runtime_goodix_model_owner *owner,
    quantized_runtime_release_fn release, void *release_context) {
    if (owner == NULL) {
        return;
    }
    quantized_runtime_goodix_model_instance_destroy(
        &owner->instance, release, release_context);
}

void quantized_runtime_operator_descriptor_init(uintptr_t *descriptor,
                                                uint32_t type, float argument) {
    if (descriptor == NULL) {
        return;
    }
    descriptor[0] = (uintptr_t)(type & 0xFFu);
    descriptor[1] = (uintptr_t)f32_to_bits(argument);
    descriptor[2] = (uintptr_t)0;
    descriptor[3] = (uintptr_t)&quantized_runtime_float_add_execute;
}

void quantized_runtime_quantizer_descriptor_construct(
    uintptr_t *descriptor, const uint32_t **cursor) {
    if (descriptor == NULL) {
        return;
    }
    float min = 0.0f; /* recovered defaults: 0.0f / 1.0f */
    float max = 1.0f;
    if (cursor != NULL && *cursor != NULL) {
        const uint32_t *words = *cursor;
        min = bits_to_f32(words[0]);
        max = bits_to_f32(words[1]);
        *cursor = words + 2;
    }
    descriptor[0] = (uintptr_t)f32_to_bits(min);
    descriptor[1] = (uintptr_t)f32_to_bits(max);
    descriptor[2] = (uintptr_t)&quantized_runtime_float_to_int8_quantize;
}

quantized_runtime_tensor *quantized_runtime_pool_slot_claim(
    quantized_runtime_pool *pool) {
    if (pool == NULL) {
        return NULL;
    }
    for (uint32_t index = 0u; index < QUANTIZED_RUNTIME_TENSOR_SLOTS; ++index) {
        if (pool->in_use[index] == 0u) {
            pool->in_use[index] = 1u;
            return &pool->slots[index];
        }
    }
    return NULL;
}

void quantized_runtime_tensor_release(quantized_runtime_pool *pool,
                                      quantized_runtime_tensor *tensor) {
    if (pool == NULL || tensor == NULL) {
        return;
    }
    if ((tensor->flags & QUANTIZED_RUNTIME_TENSOR_FLAG_BUFFERLESS) == 0u) {
        tensor->data = NULL;
    }
    for (uint32_t index = 0u; index < QUANTIZED_RUNTIME_TENSOR_SLOTS; ++index) {
        if (&pool->slots[index] == tensor) {
            pool->in_use[index] = 0u;
            return;
        }
    }
}

void quantized_runtime_tensor_release_many(quantized_runtime_pool *pool,
                                           quantized_runtime_tensor **tensors,
                                           int32_t count) {
    if (pool == NULL || tensors == NULL) {
        return;
    }
    for (int32_t index = 0; index < count; ++index) {
        if (tensors[index] != NULL) {
            quantized_runtime_tensor_release(pool, tensors[index]);
        }
        tensors[index] = NULL;
    }
}

quantized_runtime_tensor *quantized_runtime_tensor_construct(
    quantized_runtime_pool *pool, int32_t ndims, const uint16_t *dims) {
    if (pool == NULL || dims == NULL) {
        return NULL;
    }
    /* Stock callers always pass ndims masked with 3; larger values would
     * overwrite the record's own flag/trailing words, so the reconstruction
     * fails explicitly instead. */
    if (ndims < 0 || ndims > 3) {
        return NULL;
    }
    quantized_runtime_tensor *tensor = quantized_runtime_pool_slot_claim(pool);
    if (tensor == NULL) {
        return NULL;
    }
    zero_bytes((uint8_t *)tensor, sizeof(*tensor));
    tensor->flags = (uint8_t)((uint32_t)ndims & 3u);
    uint32_t count = 1u;
    for (int32_t index = 0; index < ndims; ++index) {
        tensor->dims[index] = dims[index];
        count *= (uint32_t)dims[index];
    }
    tensor->count = count;
    tensor->flags =
        (uint8_t)(tensor->flags | QUANTIZED_RUNTIME_TENSOR_FLAG_BUFFERLESS);
    tensor->data = NULL;
    return tensor;
}

quantized_runtime_tensor *quantized_runtime_tensor_slice(
    quantized_runtime_pool *pool, const quantized_runtime_tensor *input,
    uint32_t begin, uint32_t end) {
    if (pool == NULL || input == NULL || input->data == NULL) {
        return NULL;
    }
    const uint32_t rank = (uint32_t)input->flags & 3u;
    if (rank == 0u || begin > end || end > (uint32_t)input->dims[0]) {
        return NULL;
    }
    uint16_t dims[3] = {0u, 0u, 0u};
    dims[0] = (uint16_t)(end - begin);
    uint32_t trailing_count = 1u;
    for (uint32_t index = 1u; index < rank; ++index) {
        const uint32_t dimension = (uint32_t)input->dims[index];
        if (dimension != 0u && trailing_count > UINT32_MAX / dimension) {
            return NULL;
        }
        trailing_count *= dimension;
        dims[index] = input->dims[index];
    }
    if (begin != 0u && trailing_count > SIZE_MAX / begin) {
        return NULL;
    }
    size_t byte_offset = (size_t)begin * (size_t)trailing_count;
    const bool int8_form =
        (input->flags & QUANTIZED_RUNTIME_TENSOR_FLAG_INT8) != 0u;
    if (!int8_form) {
        if (byte_offset > SIZE_MAX / 2u) {
            return NULL;
        }
        byte_offset *= 2u;
    }
    quantized_runtime_tensor *slice = quantized_runtime_tensor_construct(
        pool, (int32_t)rank, dims);
    if (slice == NULL) {
        return NULL;
    }
    slice->data = (uint32_t *)(void *)
        ((uint8_t *)(void *)input->data + byte_offset);
    if (int8_form) {
        slice->reserved_10 = input->reserved_10;
        slice->flags = (uint8_t)(slice->flags |
                                 QUANTIZED_RUNTIME_TENSOR_FLAG_INT8);
    }
    return slice;
}

/* Recovered qsort comparator at 0x00058D4A: ascending first-word
 * subtraction. */
typedef struct {
    int32_t offset;
    int32_t slot;
} quantized_runtime_live_entry;

static int compare_live_entries(const void *left, const void *right) {
    const quantized_runtime_live_entry *left_entry =
        (const quantized_runtime_live_entry *)left;
    const quantized_runtime_live_entry *right_entry =
        (const quantized_runtime_live_entry *)right;
    return (int)(left_entry->offset - right_entry->offset);
}

/* memmove semantics with local word loops (no libc string.h). */
static void move_words(uint32_t *destination, const uint32_t *source,
                       uint32_t count) {
    if (destination < source) {
        for (uint32_t index = 0u; index < count; ++index) {
            destination[index] = source[index];
        }
    } else if (destination > source) {
        for (uint32_t index = count; index > 0u; --index) {
            destination[index - 1u] = source[index - 1u];
        }
    } else {
        /* identical buffers: nothing to move */
    }
}

uint32_t *quantized_runtime_arena_allocate(
    const quantized_runtime *rt, quantized_runtime_pool *pool,
    quantized_runtime_tensor *tensor) {
    if (rt == NULL || pool == NULL || tensor == NULL) {
        return NULL;
    }
    if (pool->used_words + tensor->count >= QUANTIZED_RUNTIME_ARENA_WORDS) {
        if (rt->providers.qsort_fn == NULL) {
            return NULL;
        }
        /* Recovered compaction: collect live arena-backed buffers, sort by
         * offset, move them down, and rebuild the watermark. */
        quantized_runtime_live_entry live[QUANTIZED_RUNTIME_TENSOR_SLOTS];
        uint32_t live_count = 0u;
        pool->used_words = 0u;
        for (uint32_t index = 0u; index < QUANTIZED_RUNTIME_TENSOR_SLOTS;
                ++index) {
            quantized_runtime_tensor *candidate = &pool->slots[index];
            if (pool->in_use[index] != 0u &&
                    (candidate->flags &
                         QUANTIZED_RUNTIME_TENSOR_FLAG_BUFFERLESS) == 0u) {
                live[live_count].offset =
                    (int32_t)(candidate->data - pool->arena);
                live[live_count].slot = (int32_t)index;
                ++live_count;
            }
        }
        rt->providers.qsort_fn(live, live_count,
                               sizeof(quantized_runtime_live_entry),
                               compare_live_entries);
        for (uint32_t index = 0u; index < live_count; ++index) {
            quantized_runtime_tensor *candidate =
                &pool->slots[live[index].slot];
            move_words(pool->arena + pool->used_words, candidate->data,
                       candidate->count);
            candidate->data = pool->arena + pool->used_words;
            pool->used_words += candidate->count;
        }
    }
    /* Reconstruction guard (stock would write past the arena; unreachable in
     * stock-sized model graphs). */
    if (pool->used_words + tensor->count > QUANTIZED_RUNTIME_ARENA_WORDS) {
        return NULL;
    }
    const uint32_t base = pool->used_words;
    pool->used_words = base + tensor->count;
    return pool->arena + base;
}

quantized_runtime_tensor *quantized_runtime_tensor_allocate(
    const quantized_runtime *rt, quantized_runtime_pool *pool, int32_t ndims,
    const uint16_t *dims) {
    quantized_runtime_tensor *tensor =
        quantized_runtime_tensor_construct(pool, ndims, dims);
    if (tensor == NULL) {
        return NULL;
    }
    uint32_t *buffer = quantized_runtime_arena_allocate(rt, pool, tensor);
    if (buffer == NULL) {
        return NULL;
    }
    tensor->data = buffer;
    tensor->flags =
        (uint8_t)(tensor->flags & ~QUANTIZED_RUNTIME_TENSOR_FLAG_BUFFERLESS);
    return tensor;
}

quantized_runtime_tensor *quantized_runtime_tensor_create_fill(
    const quantized_runtime *rt, quantized_runtime_pool *pool, int32_t ndims,
    const uint16_t *dims, float fill) {
    quantized_runtime_tensor *tensor =
        quantized_runtime_tensor_construct(pool, ndims, dims);
    if (tensor == NULL) {
        return NULL;
    }
    uint32_t *buffer = quantized_runtime_arena_allocate(rt, pool, tensor);
    if (buffer == NULL) {
        return NULL;
    }
    tensor->data = buffer;
    tensor->flags =
        (uint8_t)(tensor->flags & ~QUANTIZED_RUNTIME_TENSOR_FLAG_BUFFERLESS);
    const uint32_t fill_bits = f32_to_bits(fill);
    for (int32_t index = 0; index < (int32_t)tensor->count; ++index) {
        tensor->data[index] = fill_bits;
    }
    return tensor;
}

void quantized_runtime_tensor_reshape(quantized_runtime_tensor *tensor,
                                      int32_t ndims, const uint16_t *dims) {
    if (tensor == NULL || dims == NULL) {
        return;
    }
    if (ndims < 0 || ndims > 3) {
        return;
    }
    tensor->flags = (uint8_t)((tensor->flags & 0xFCu) |
                              ((uint32_t)ndims & 3u));
    /* Recovered quirk: the element count is not recomputed here. */
    for (int32_t index = 0; index < ndims; ++index) {
        tensor->dims[index] = dims[index];
    }
}
