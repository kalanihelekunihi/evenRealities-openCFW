#include <assert.h>
#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "gomore_primitives/gomore_primitives.h"
#include "openr1/r1_crc.h"

static uint32_t scaled_sample_topic;
static size_t scaled_sample_length;
static uint8_t scaled_sample_payload[8];
static unsigned scaled_sample_publish_calls;

static void publish_scaled_sample(
    uint32_t topic, const void *payload, size_t payload_length) {
    scaled_sample_topic = topic;
    scaled_sample_length = payload_length;
    memcpy(scaled_sample_payload, payload, payload_length);
    ++scaled_sample_publish_calls;
}

typedef struct {
    uintptr_t arguments[4];
    float score;
    unsigned prepare_calls;
} score_trace;

static void prepare_score(uintptr_t first, uintptr_t second, uintptr_t third,
                          uintptr_t fourth, void *workspace) {
    score_trace *trace = workspace;
    trace->arguments[0] = first;
    trace->arguments[1] = second;
    trace->arguments[2] = third;
    trace->arguments[3] = fourth;
    ++trace->prepare_calls;
}

static float read_score(const void *workspace) {
    return ((const score_trace *)workspace)->score;
}

static int compare_float(const void *left, const void *right) {
    const float a = *(const float *)left;
    const float b = *(const float *)right;
    return (a > b) - (a < b);
}

static void sort_values(void *base, size_t count, size_t size,
                        gomore_primitives_compare_fn compare) {
    qsort(base, count, size, compare);
}

static int32_t max_index(const float *values, uint32_t count) {
    int32_t result = -1;
    float largest = 0.0f;
    for (uint32_t index = 0u; index < count; ++index) {
        if (values[index] > largest) {
            largest = values[index];
            result = (int32_t)index;
        }
    }
    return result;
}

typedef struct {
    size_t calls;
    void *pool;
    size_t pool_length;
    uint32_t rank;
    uint16_t dimensions[2];
    bool pool_was_clear;
} sleep_tensor_trace;

static sleep_tensor_trace g_sleep_tensor_trace;

static uint32_t construct_sleep_tensor(
    void *pool, size_t pool_length, uint32_t rank,
    const uint16_t *dimensions, size_t dimension_count) {
    ++g_sleep_tensor_trace.calls;
    g_sleep_tensor_trace.pool = pool;
    g_sleep_tensor_trace.pool_length = pool_length;
    g_sleep_tensor_trace.rank = rank;
    g_sleep_tensor_trace.pool_was_clear = true;
    const uint8_t *bytes = pool;
    for (size_t index = 0u; index < pool_length; ++index) {
        if (bytes[index] != 0u) {
            g_sleep_tensor_trace.pool_was_clear = false;
        }
    }
    if (dimensions != NULL && dimension_count >= 2u) {
        g_sleep_tensor_trace.dimensions[0] = dimensions[0];
        g_sleep_tensor_trace.dimensions[1] = dimensions[1];
    }
    return UINT32_C(0x12345678);
}

static gomore_primitives_sleep_stage_classifier_result
    g_sleep_stage_classifier_result;
static unsigned g_sleep_stage_classifier_calls;
static uint8_t g_sleep_stage_classifier_iteration;

static bool classify_sleep_stage_stream(
    gomore_primitives_sleep_stage_classifier_result *result,
    gomore_primitives_sleep_stage_stream_state *state,
    uint8_t iteration, const int8_t mode_adjustment[4], void *context) {
    assert(result != NULL && state != NULL);
    assert(mode_adjustment != NULL && context == NULL);
    *result = g_sleep_stage_classifier_result;
    g_sleep_stage_classifier_iteration = iteration;
    ++g_sleep_stage_classifier_calls;
    return true;
}

static float sleep_classifier_square_root_fixture(float value) {
    assert(value > 0.0f);
    return 1.0f;
}

static float sleep_classifier_exponential_fixture(float value) {
    (void)value;
    return 1.0f;
}

static float sleep_classifier_logistic_fixture(float value) {
    (void)value;
    return 0.5f;
}

static float sleep_classifier_tanh_fixture(float value) {
    return value;
}

typedef struct {
    size_t format_calls;
    size_t emit_calls;
    const char *format;
    uint32_t value;
    char wrapper[3];
    char message[256];
} log_trace;

static log_trace g_log_trace;
static unsigned g_accelerometer_resample_calls;
static unsigned g_accelerometer_filter_calls;

static uint32_t format_log_value(
    char *destination, size_t capacity, const char *format, uint32_t value) {
    ++g_log_trace.format_calls;
    g_log_trace.format = format;
    g_log_trace.value = value;
    assert(destination != NULL && capacity == 248u);
    static const char payload[] = "status";
    memcpy(destination, payload, sizeof(payload));
    return (uint32_t)(sizeof(payload) - 1u);
}

static void emit_log_message(const char *format, const char *message) {
    ++g_log_trace.emit_calls;
    assert(format != NULL && message != NULL);
    memcpy(g_log_trace.wrapper, format, sizeof(g_log_trace.wrapper));
    size_t index = 0u;
    while (index + 1u < sizeof(g_log_trace.message) && message[index] != '\0') {
        g_log_trace.message[index] = message[index];
        ++index;
    }
    g_log_trace.message[index] = '\0';
}

static void accelerometer_resample(
    const float *source, int32_t input_count, int32_t output_count,
    int32_t source_total, float *destination) {
    assert(source != NULL && input_count == 7 && output_count == 25 &&
           source_total == 7 && destination != NULL);
    for (size_t index = 0u; index < 25u; ++index) {
        destination[index] = source[0] + (float)index;
    }
    ++g_accelerometer_resample_calls;
}

static void accelerometer_filter(
    void *filter_state, float *values, size_t count) {
    assert(filter_state != NULL && values != NULL && count == 25u);
    for (size_t index = 0u; index < count; ++index) {
        values[index] += 10.0f;
    }
    ++g_accelerometer_filter_calls;
}

static float bits_float(uint32_t bits) {
    union {
        uint32_t u;
        float f;
    } pun;
    pun.u = bits;
    return pun.f;
}

static uint32_t float_bits(float value) {
    union {
        uint32_t u;
        float f;
    } pun;
    pun.f = value;
    return pun.u;
}

static bool float_matches_bits_within_ulps(
    float value, uint32_t expected, uint32_t maximum_ulps) {
    const uint32_t actual = float_bits(value);
    if ((actual >> 31u) != (expected >> 31u)) {
        return false;
    }
    const uint32_t difference = actual >= expected ?
        actual - expected : expected - actual;
    return difference <= maximum_ulps;
}

static float iir_cosine_fixture(float value) {
    return cosf(value);
}

static float iir_sine_fixture(float value) {
    return sinf(value);
}

static float iir_tangent_fixture(float value) {
    return tanf(value);
}

static float iir_power_fixture(float base, float exponent) {
    return powf(base, exponent);
}

static void store_u32_fixture(uint8_t destination[4], uint32_t value) {
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8u);
    destination[2] = (uint8_t)(value >> 16u);
    destination[3] = (uint8_t)(value >> 24u);
}

static void store_u16_fixture(uint8_t destination[2], uint16_t value) {
    destination[0] = (uint8_t)value;
    destination[1] = (uint8_t)(value >> 8u);
}

static uint32_t load_u32_fixture(const uint8_t source[4]) {
    return (uint32_t)source[0] |
           (uint32_t)source[1] << 8u |
           (uint32_t)source[2] << 16u |
           (uint32_t)source[3] << 24u;
}

static uint16_t load_u16_fixture(const uint8_t source[2]) {
    return (uint16_t)((uint16_t)source[0] |
                      (uint16_t)((uint16_t)source[1] << 8u));
}

typedef struct {
    unsigned mode_calls;
    unsigned release_calls;
    unsigned init_calls;
    uint32_t mode;
    uint32_t mode_value;
    uint32_t init_mode;
    unsigned consume_calls;
    uint8_t staged[32];
} tier2_trace;

static tier2_trace *active_tier2_trace;

static bool load_blob(void *context, uint8_t *destination, size_t length) {
    const uint8_t seed = *(const uint8_t *)context;
    for (size_t index = 0u; index < length; ++index) {
        destination[index] = (uint8_t)(seed + (uint8_t)index);
    }
    return true;
}

typedef struct {
    uint8_t key[64];
    uint8_t device_uuid[28];
    uint8_t device_uuid_length;
    uint32_t timestamp;
    int32_t apply_status;
    unsigned timestamp_calls;
    unsigned apply_calls;
} auth_setup_trace;

static auth_setup_trace g_auth_setup_trace;

static bool fail_blob_load(void *context, uint8_t *destination,
                           size_t length) {
    (void)context;
    (void)destination;
    (void)length;
    return false;
}

static uint32_t auth_timestamp_fixture(void *context) {
    ++g_auth_setup_trace.timestamp_calls;
    return *(const uint32_t *)context;
}

static int32_t auth_apply_fixture(
    const gomore_primitives_auth_parameters *parameters) {
    assert(parameters != NULL && parameters->key != NULL &&
           parameters->device_uuid != NULL);
    ++g_auth_setup_trace.apply_calls;
    memcpy(g_auth_setup_trace.key, parameters->key,
           sizeof(g_auth_setup_trace.key));
    memcpy(g_auth_setup_trace.device_uuid, parameters->device_uuid,
           sizeof(g_auth_setup_trace.device_uuid));
    g_auth_setup_trace.device_uuid_length =
        parameters->device_uuid_length;
    g_auth_setup_trace.timestamp = parameters->timestamp;
    return g_auth_setup_trace.apply_status;
}

typedef struct {
    const char *plaintexts[2];
    int accepted_attempt;
    int32_t parser_results[4];
    int32_t validator_results[3];
    size_t decrypt_calls;
    size_t parser_calls;
    size_t validator_calls;
    char parser_tokens[4][16];
    char validator_tokens[3][16];
    uint8_t normalized_uuid[17];
    uint8_t normalized_uuid_length;
    uint32_t timestamp;
} sdk_auth_trace;

static bool sdk_auth_decrypt_fixture(
    void *context, const uint8_t *input, size_t input_length,
    const uint8_t key[GOMORE_PRIMITIVES_SDK_AUTH_KEY_BYTES],
    uint8_t *output, size_t output_capacity, size_t *written) {
    sdk_auth_trace *trace = context;
    assert(input != NULL && input_length == 48u && key != NULL &&
           output != NULL && written != NULL && trace->decrypt_calls < 2u);
    const char *plaintext = trace->plaintexts[trace->decrypt_calls++];
    const size_t length = strlen(plaintext);
    assert(length <= output_capacity);
    memcpy(output, plaintext, length);
    *written = length;
    return true;
}

static bool sdk_auth_match_fixture(
    void *context, const uint8_t *message, size_t message_length) {
    sdk_auth_trace *trace = context;
    assert(message != NULL && message_length == strlen((const char *)message));
    return (int)(trace->decrypt_calls - 1u) == trace->accepted_attempt;
}

static int32_t sdk_auth_parse_fixture(
    void *context, char *field,
    const gomore_primitives_auth_parameters *parameters,
    gomore_primitives_sdk_auth_status *status, uint32_t scratch[4]) {
    sdk_auth_trace *trace = context;
    const size_t index = trace->parser_calls++;
    assert(index < 4u && field != NULL && parameters != NULL &&
           status != NULL && scratch != NULL && scratch[0] == parameters->timestamp);
    (void)strncpy(trace->parser_tokens[index], field,
                  sizeof(trace->parser_tokens[index]) - 1u);
    memcpy(trace->normalized_uuid, parameters->device_uuid, 17u);
    trace->normalized_uuid_length = parameters->device_uuid_length;
    trace->timestamp = parameters->timestamp;
    return trace->parser_results[index];
}

static int32_t sdk_auth_validate_fixture(
    void *context, char *field,
    const gomore_primitives_auth_parameters *parameters,
    gomore_primitives_sdk_auth_status *status) {
    sdk_auth_trace *trace = context;
    const size_t index = trace->validator_calls++;
    assert(index < 3u && field != NULL && parameters != NULL && status != NULL);
    (void)strncpy(trace->validator_tokens[index], field,
                  sizeof(trace->validator_tokens[index]) - 1u);
    return trace->validator_results[index];
}

static int32_t consume_stage(uintptr_t first, uintptr_t second,
                             const uint8_t staged[32], uintptr_t fourth,
                             uintptr_t fifth) {
    assert(first == 1u && second == 2u && fourth == 4u && fifth == 5u);
    ++active_tier2_trace->consume_calls;
    memcpy(active_tier2_trace->staged, staged,
           sizeof(active_tier2_trace->staged));
    return 0;
}

static void set_mode(uint32_t mode, uint32_t value) {
    ++active_tier2_trace->mode_calls;
    active_tier2_trace->mode = mode;
    active_tier2_trace->mode_value = value;
}

static void release_state(void *context) {
    tier2_trace *trace = context;
    ++trace->release_calls;
}

static void initialize_state(uint32_t mode) {
    ++active_tier2_trace->init_calls;
    active_tier2_trace->init_mode = mode;
}

static uint32_t read_time(void *context) {
    (void)context;
    return UINT32_C(0x12345678);
}

static uint16_t read_offset(void *context) {
    (void)context;
    return UINT16_C(0xABCD);
}

static int32_t read_sync(void *context) {
    return *(const int32_t *)context;
}

static bool validate_parameter(void *context, uint32_t value) {
    return value == *(const uint32_t *)context;
}

static float square_value(float value, float exponent) {
    assert(exponent == 2.0f);
    return value * value;
}

static float sqrt_passthrough(float value) {
    return value;
}

static unsigned locomotion_summary_sqrt_calls;
static float locomotion_summary_sqrt_inputs[4];

static float locomotion_summary_sqrt(float value) {
    assert(locomotion_summary_sqrt_calls < 4u);
    locomotion_summary_sqrt_inputs[locomotion_summary_sqrt_calls++] = value;
    if (value == 0.0f) {
        return 0.0f;
    }
    assert(value == 9.0f);
    return 3.0f;
}

static float exp_one(float value) {
    (void)value;
    return 1.0f;
}

typedef struct {
    unsigned prepare_calls;
    unsigned initialize_calls;
    unsigned tensor_calls;
    unsigned finish_calls;
    unsigned filter_calls;
    unsigned first_stage_calls;
    unsigned second_stage_calls;
    unsigned mode_lt2_calls;
    unsigned mode2_calls;
    unsigned large_init_calls;
    unsigned resample_calls;
    unsigned apply_filter_calls;
    size_t allocation_length;
    uintptr_t binding;
} closure_trace;

static closure_trace active_closure_trace;
static uint8_t closure_allocation[0x2DC];

static void closure_prepare(void) {
    ++active_closure_trace.prepare_calls;
}

static int32_t closure_random(void) {
    return 177;
}

static void *closure_allocate(size_t length) {
    assert(length <= sizeof(closure_allocation));
    active_closure_trace.allocation_length = length;
    memset(closure_allocation, 0, sizeof(closure_allocation));
    return closure_allocation;
}

static void closure_allocated_initialize(void *record, uintptr_t binding) {
    assert(record == closure_allocation);
    ++active_closure_trace.initialize_calls;
    active_closure_trace.binding = binding;
}

static void closure_mode0_initialize(void *record, uintptr_t binding) {
    closure_allocated_initialize(record, binding);
    store_u32_fixture(&((uint8_t *)record)[0x1E0u],
                      UINT32_C(0xA1B2C3D4));
}

static uint32_t closure_tensor_call(
    uintptr_t first, uintptr_t second,
    uint32_t descriptor0, uint32_t descriptor1, uint32_t descriptor2) {
    assert(first == 4u && second == 5u);
    ++active_closure_trace.tensor_calls;
    return descriptor0 + descriptor1 + descriptor2;
}

static void closure_tensor_finish(uintptr_t first, uintptr_t second) {
    assert(first == 4u && second == 5u);
    ++active_closure_trace.finish_calls;
}

static void closure_filter_initialize(
    void *record, uint32_t rows, uint32_t columns,
    const float parameters[2]) {
    assert(record != NULL && rows == 2u && columns == 2u);
    assert(parameters[0] == bits_float(UINT32_C(0x3C83126F)));
    assert(parameters[1] == bits_float(UINT32_C(0x3E23D70A)));
    ++active_closure_trace.filter_calls;
}

static void closure_first_stage(
    uintptr_t first, uintptr_t second, uintptr_t third, uintptr_t fourth,
    void *output) {
    assert(first == 1u && second == 2u && third == 3u && fourth == 4u);
    *(uint8_t *)output = 0x11u;
    ++active_closure_trace.first_stage_calls;
}

static void closure_second_stage(
    uintptr_t first, uintptr_t second, uintptr_t third, uintptr_t fourth,
    void *output) {
    assert(first == 1u && second == 2u && third == 3u && fourth == 4u);
    *(uint8_t *)output = 0x22u;
    ++active_closure_trace.second_stage_calls;
}

static void closure_tail_initialize(void *record) {
    *(uint8_t *)record = 0x5Au;
}

static float closure_root_power(float value, float exponent) {
    assert(exponent == 0.5f);
    return value * 2.0f;
}

static void closure_mode_lt2_initialize(
    void *record, uint32_t mode, uint32_t count, float parameter) {
    assert(record != NULL);
    assert((mode == 1u && count == 3u && parameter == 0.25f) ||
           (mode == 0u && count == 2u &&
            parameter == bits_float(UINT32_C(0x3F75C28F))));
    ++active_closure_trace.mode_lt2_calls;
}

static void closure_mode2_initialize(
    void *record, uint32_t count, const float parameters[2]) {
    assert(record != NULL && count == 2u);
    assert((parameters[0] == bits_float(UINT32_C(0x3D23D70A)) &&
            parameters[1] == bits_float(UINT32_C(0x3EA3D70A))) ||
           (parameters[0] == bits_float(UINT32_C(0x3C2A64C3)) &&
            parameters[1] == bits_float(UINT32_C(0x3F75C28F))));
    ((uint8_t *)record)[4] = 0x66u;
    ++active_closure_trace.mode2_calls;
}

static void closure_large_initialize(void *record) {
    ((uint8_t *)record)[0] = 0x77u;
    ++active_closure_trace.large_init_calls;
}

static void closure_resample(
    const float *source, int32_t input_count, int32_t output_count,
    int32_t source_total, float *destination) {
    assert(source != NULL && input_count == 25 && output_count == 25 &&
           (source_total == 25 || source_total == 50) &&
           destination != NULL);
    for (size_t index = 0u; index < 25u; ++index) {
        destination[index] = source[0] + (float)index;
    }
    ++active_closure_trace.resample_calls;
}

static void closure_apply_filter(
    void *filter_state, float *values, size_t count) {
    assert(filter_state != NULL && values != NULL && count == 25u);
    for (size_t index = 0u; index < count; ++index) {
        values[index] += 1.0f;
    }
    ++active_closure_trace.apply_filter_calls;
}

static float closure_third_power(float value, float exponent) {
    assert(exponent == bits_float(UINT32_C(0x3EAAAAAB)));
    return value + 1.0f;
}

typedef struct {
    uint32_t topics[2];
    uintptr_t handlers[2];
    uintptr_t contexts[2];
    uint32_t seed;
    unsigned topic_calls;
    unsigned finish_calls;
    unsigned state_calls;
    uint8_t *state;
    uint8_t state_value;
    unsigned record_steps;
    uint32_t record_sequences[4];
} adapter_trace;

static adapter_trace active_adapter_trace;

static void adapter_register_topic(uint32_t topic, uintptr_t handler,
                                   uintptr_t context) {
    const unsigned index = active_adapter_trace.topic_calls;
    assert(index < 2u);
    active_adapter_trace.topics[index] = topic;
    active_adapter_trace.handlers[index] = handler;
    active_adapter_trace.contexts[index] = context;
    ++active_adapter_trace.topic_calls;
}

static float adapter_exponential(float value) {
    return value + 10.0f;
}

static float complex_atan2_fixture(float imaginary, float real) {
    assert(imaginary == 4.0f && real == 3.0f);
    return 0.25f;
}

static float complex_sqrt_fixture(float value) {
    assert(value == 25.0f);
    return 5.0f;
}

static float complex_log_fixture(float value) {
    assert(value == 5.0f);
    return 2.0f;
}

static float complex_exp_fixture(float value) {
    assert(value == 4.0f);
    return 10.0f;
}

static float complex_cos_fixture(float value) {
    assert(value == 0.5f);
    return 0.75f;
}

static float complex_sin_fixture(float value) {
    assert(value == 0.5f);
    return 0.25f;
}

static unsigned g_cardano_power_calls;
static unsigned g_cardano_math_calls;

static float cardano_power_fixture(float base, float exponent) {
    assert(float_bits(exponent) == UINT32_C(0x3EAAAAAB));
    ++g_cardano_power_calls;
    if (base == 8.0f) {
        return 2.0f;
    }
    assert(base == 27.0f);
    return 3.0f;
}

static float cardano_atan2_fixture(float imaginary, float real) {
    assert(imaginary == 0.0f && real == 1.0f);
    ++g_cardano_math_calls;
    return 0.0f;
}

static float cardano_sqrt_fixture(float value) {
    assert(value == 1.0f);
    ++g_cardano_math_calls;
    return 1.0f;
}

static float cardano_log_fixture(float value) {
    assert(value == 1.0f);
    ++g_cardano_math_calls;
    return 0.0f;
}

static float cardano_exp_fixture(float value) {
    assert(value == 0.0f);
    ++g_cardano_math_calls;
    return 1.0f;
}

static float cardano_cos_fixture(float value) {
    assert(value == 0.0f);
    ++g_cardano_math_calls;
    return 1.0f;
}

static float cardano_sin_fixture(float value) {
    assert(value == 0.0f);
    ++g_cardano_math_calls;
    return 0.0f;
}

static unsigned g_cubic_power_calls;

static float cubic_power_fixture(float base, float exponent) {
    ++g_cubic_power_calls;
    if (exponent == 2.0f) {
        return base * base;
    }
    if (exponent == 3.0f) {
        return base * base * base;
    }
    if (exponent == 0.5f) {
        if (base == 3.0f) {
            return bits_float(UINT32_C(0x3FDDB3D7));
        }
        assert(base == 0.0f);
        return 0.0f;
    }
    assert(float_bits(exponent) == UINT32_C(0x3EAAAAAB) &&
           base == 0.0f);
    return 0.0f;
}

static float positive_floor_fixture(float value) {
    assert(value >= 0.0f);
    return (float)(int32_t)value;
}

static float zero_sqrt_fixture(float value) {
    assert(value == 0.0f);
    return 0.0f;
}

static float square_power_fixture(float base, float exponent) {
    assert(exponent == 2.0f);
    return base * base;
}

static float peak_sqrt_inputs[4];
static unsigned peak_sqrt_calls;

static float peak_sqrt_fixture(float value) {
    assert(peak_sqrt_calls < 4u);
    peak_sqrt_inputs[peak_sqrt_calls++] = value;
    return value;
}

static float quadratic_power_fixture(float base, float exponent) {
    if (exponent == 2.0f) {
        return base * base;
    }
    assert(exponent == 0.5f && base == 1.0f);
    return 1.0f;
}

static unsigned variability_sqrt_calls;

static float variability_sqrt_fixture(float value) {
    ++variability_sqrt_calls;
    if (value == 1690000.0f) {
        return 1300.0f;
    }
    assert(value == 90000.0f);
    return 300.0f;
}

static unsigned sps_selection_log_calls;
static float sps_selection_log_values[3];

static void sps_selection_log_fixture(
    float reference, float gpd, float accelerometer) {
    ++sps_selection_log_calls;
    sps_selection_log_values[0] = reference;
    sps_selection_log_values[1] = gpd;
    sps_selection_log_values[2] = accelerometer;
}

static bool autocorrelation_fixture(
    const uint16_t *samples,
    float *first, float *second, float *third, float *fourth, float *fifth,
    uintptr_t first_binding, uintptr_t second_binding) {
    assert(samples != NULL && samples[0] == 7 &&
           first_binding == 11u && second_binding == 12u);
    *first = 1.0f;
    *second = 2.0f;
    *third = 3.0f;
    *fourth = 4.0f;
    *fifth = 5.0f;
    return true;
}

static bool locomotion_classifier_autocorrelation_fixture(
    const uint16_t *samples,
    float *first, float *second, float *third, float *fourth, float *fifth,
    uintptr_t first_binding, uintptr_t second_binding) {
    assert(samples != NULL && samples[0] == 900 &&
           first_binding != 0u && second_binding != 0u);
    *first = 2.0f;
    *second = 3.0f;
    *third = 4.0f;
    *fourth = 5.0f;
    *fifth = 6.0f;
    *(uint32_t *)first_binding = UINT32_C(0x00000102);
    float *const shape = (float *)second_binding;
    shape[0] = 1.0f;
    shape[1] = 2.0f;
    return true;
}

static unsigned sps_commit_calls;

static float sps_primary_model0(const float *values) {
    return values[0] + 1.0f;
}

static float sps_secondary_model0(const float *values) {
    return values[1] + 2.0f;
}

static float sps_primary_model1(const float *values) {
    return values[2] + 10.0f;
}

static float sps_secondary_model1(const float *values) {
    return values[3] + 20.0f;
}

static float sps_adjust_fixture(float primary, void *state) {
    assert(state != NULL);
    return primary * 2.0f;
}

static void sps_commit_fixture(
    void *state, float primary, float secondary) {
    assert(state != NULL && primary >= 0.0f && secondary >= 0.0f);
    ++sps_commit_calls;
}

static float sps_candidate_state2_primary(const float *values) {
    return values[1] / 20.0f;
}

static float sps_candidate_state2_secondary(const float *values) {
    return values[2] / 100.0f;
}

static float sps_candidate_state1_primary(const float *values) {
    return values[2] / 100.0f;
}

static float sps_candidate_state1_secondary(const float *values) {
    return values[0] / 20.0f;
}

static float sps_candidate_adjust(float primary, void *state) {
    const gomore_primitives_sps_model_state *model = state;
    return primary * model->calibration_slope +
           model->calibration_intercept;
}

static void sps_candidate_commit(
    void *state, float primary, float secondary) {
    assert(gomore_primitives_accumulate_pair(
        state, sizeof(gomore_primitives_sps_model_state),
        primary, secondary));
}

typedef struct {
    int32_t auth[2];
    int32_t init[2];
    unsigned auth_calls;
    unsigned init_calls;
    bool previous_found;
    bool crash_present;
    bool crash_restored;
    size_t crash_length;
    bool profile_found;
    unsigned crash_clear_calls;
    unsigned apply_calls;
    unsigned mode_calls;
    unsigned subscribe_calls;
    uint8_t subscription;
    uint8_t init_previous_first;
    uint8_t init_profile_first;
} health_lifecycle_trace;

static uint32_t lifecycle_size(void *context) {
    (void)context;
    return 1u;
}
static int32_t lifecycle_auth(void *context) {
    health_lifecycle_trace *trace = context;
    return trace->auth[trace->auth_calls++];
}
static bool lifecycle_previous(void *context, uint8_t *data) {
    health_lifecycle_trace *trace = context;
    if (trace->previous_found) data[0] = UINT8_C(0x11);
    return trace->previous_found;
}
static int32_t lifecycle_crash_present(void *context) {
    return ((health_lifecycle_trace *)context)->crash_present ? 1 : 0;
}
static bool lifecycle_crash(void *context, uint8_t *data, size_t *length) {
    health_lifecycle_trace *trace = context;
    if (trace->crash_restored) data[0] = UINT8_C(0x22);
    *length = trace->crash_length;
    return trace->crash_restored;
}
static void lifecycle_crash_clear(void *context) {
    ++((health_lifecycle_trace *)context)->crash_clear_calls;
}
static bool lifecycle_profile(void *context, uint8_t *profile) {
    health_lifecycle_trace *trace = context;
    if (trace->profile_found) profile[0] = UINT8_C(0x33);
    return trace->profile_found;
}
static uint32_t lifecycle_timestamp(void *context) {
    (void)context;
    return UINT32_C(1234);
}
static int32_t lifecycle_initialize(
    void *context, uint32_t timestamp, const uint8_t *profile,
    const uint8_t *previous) {
    health_lifecycle_trace *trace = context;
    assert(timestamp == UINT32_C(1234));
    trace->init_profile_first = profile[0];
    trace->init_previous_first = previous[0];
    return trace->init[trace->init_calls++];
}
static void lifecycle_apply(void *context, uint32_t mode, uint32_t value) {
    health_lifecycle_trace *trace = context;
    assert(mode == 1u && value == 0u);
    ++trace->apply_calls;
}
static void lifecycle_mode(void *context, uint32_t mode, uint32_t value) {
    health_lifecycle_trace *trace = context;
    assert(mode == 1u && value == UINT32_C(0x66));
    ++trace->mode_calls;
}
static uint8_t lifecycle_subscribe(
    void *context, uint32_t topic, uintptr_t callback,
    uintptr_t callback_context) {
    health_lifecycle_trace *trace = context;
    assert(topic == 0u && callback == UINT32_C(0x1235) &&
           callback_context == UINT32_C(0x5678));
    ++trace->subscribe_calls;
    return trace->subscription;
}

static unsigned update_failure_log_calls;
static unsigned update_failure_reset_calls;
static uint32_t update_failure_status;
static uint32_t update_failure_timestamp;

static void update_failure_log_fixture(uint32_t status, uint32_t timestamp) {
    ++update_failure_log_calls;
    update_failure_status = status;
    update_failure_timestamp = timestamp;
}

static void update_failure_reset_fixture(void) {
    ++update_failure_reset_calls;
}

static float energy_exponential_fixture(float value) {
    return value + 1.0f;
}

static float energy_log_fixture(float value) {
    return value + 0.5f;
}

static double energy_double_log_fixture(double value) {
    return value - 0.25;
}

static double sleep_tanh_zero_fixture(double value) {
    assert(value >= 0.0);
    return 0.0;
}

static unsigned g_final_sleep_refine_calls;

static bool final_sleep_refine_fixture(
    const uint8_t configuration[11], int8_t *stages,
    size_t stage_capacity, size_t *stage_count,
    uint32_t duration_seconds) {
    ++g_final_sleep_refine_calls;
    assert(configuration != NULL && configuration[1] == 0u &&
           stages != NULL && stage_capacity == 64u &&
           stage_count != NULL && *stage_count == 30u &&
           duration_seconds == 900u);
    return true;
}

static double g_sps_secondary_sqrt_input;
static double g_sps_secondary_sqrt_output;
static unsigned g_sps_secondary_sqrt_calls;

static double sps_secondary_sqrt_fixture(double value) {
    g_sps_secondary_sqrt_input = value;
    ++g_sps_secondary_sqrt_calls;
    return g_sps_secondary_sqrt_output;
}

static unsigned g_positive_round_calls;

static double positive_round_fixture(double value) {
    assert(value >= 0.0);
    ++g_positive_round_calls;
    return (double)(int32_t)(value + 0.5);
}

static unsigned g_locomotion_control_reduce_calls;

static double locomotion_power_f64_fixture(double base, double exponent) {
    return pow(base, exponent);
}

static double locomotion_square_root_f64_fixture(double value) {
    return sqrt(value);
}

static float locomotion_square_root_f32_fixture(float value) {
    return sqrtf(value);
}

static const gomore_primitives_locomotion_feature_reduce_math
    locomotion_reduce_math = {
        .qsort_provider = sort_values,
        .compare = compare_float,
        .power_f32 = square_value,
        .square_root_f32 = locomotion_square_root_f32_fixture,
        .power_f64 = locomotion_power_f64_fixture,
        .square_root_f64 = locomotion_square_root_f64_fixture,
    };

static bool locomotion_control_reduce_fixture(
    float expanded[GOMORE_PRIMITIVES_LOCOMOTION_EXPANDED_COUNT],
    uint8_t first_indices[
        GOMORE_PRIMITIVES_LOCOMOTION_FEATURE_INDEX_CAPACITY],
    uint8_t second_indices[
        GOMORE_PRIMITIVES_LOCOMOTION_FEATURE_INDEX_CAPACITY],
    float controls[GOMORE_PRIMITIVES_LOCOMOTION_CONTROL_CAPACITY],
    float *primary, float *secondary,
    const gomore_primitives_locomotion_feature_reduce_math *math) {
    ++g_locomotion_control_reduce_calls;
    assert(math == &locomotion_reduce_math);
    assert(expanded[0] == 10.0f && expanded[249] == 10.0f &&
           controls[0] == 10.0f && controls[1] == 10.0f);
    first_indices[0] = 3u;
    second_indices[0] = 4u;
    *primary = 3.0f;
    *secondary = 4.0f;
    return true;
}

static unsigned crossing_estimate_calls;
static uint32_t crossing_estimate_modes[2];
static int16_t crossing_estimate_baselines[2];
static float crossing_estimate_values[2];

static bool locomotion_crossing_estimate(
    const uint16_t *samples, size_t sample_count, int16_t baseline,
    uint32_t mode, float *output) {
    assert(samples != NULL && sample_count == 200u && output != NULL &&
           crossing_estimate_calls < 2u);
    const unsigned call = crossing_estimate_calls++;
    crossing_estimate_modes[call] = mode;
    crossing_estimate_baselines[call] = baseline;
    *output = crossing_estimate_values[call];
    return true;
}

typedef struct {
    uint32_t called_mask;
    uint32_t elapsed[GOMORE_PRIMITIVES_OUTPUT_STAGE_COUNT];
} output_orchestrator_trace;

static bool output_orchestrator_stage(
    void *context, uint8_t *engine, size_t engine_length,
    uint32_t elapsed_updates,
    const gomore_primitives_output_stage_descriptor *descriptor,
    uint32_t *status) {
    static const uint16_t state_offsets[] = {
        0x01F8u, 0x08F4u, 0x0B62u, 0x0B74u,
        0x0BD0u, 0x0BD4u, 0x0C54u, 0x0C58u,
        0x0CB4u, 0x33B4u, 0x0FF0u, 0x112Cu,
        0x12B8u, 0x33D8u, 0x37DCu, 0x37F8u,
    };
    static const uint16_t control_offsets[] = {
        0x3848u, 0x384Cu, 0x384Du, 0x384Eu,
        0x384Fu, 0x3850u, 0x3857u, 0x3859u,
        0x385Cu, 0x3868u, 0x3861u, 0x3863u,
        0x3865u, 0x3877u, 0x3881u, 0x3886u,
    };
    static const uint16_t status_offsets[] = {
        0x3800u, 0x3804u, 0x3805u, 0x3806u,
        0x3807u, 0x3808u, 0x380Fu, 0x3811u,
        0x3814u, 0x3820u, 0x3819u, 0x381Bu,
        0x381Du, 0x382Fu, 0x3839u, 0x383Eu,
    };
    static const uint8_t stage_numbers[] = {
        3u, 7u, 8u, 9u, 10u, 11u, 18u, 20u,
        23u, 35u, 28u, 30u, 32u, 50u, 60u, 65u,
    };
    static const uint8_t argument_counts[] = {
        3u, 2u, 4u, 4u, 4u, 2u, 3u, 10u,
        7u, 3u, 9u, 2u, 5u, 3u, 3u, 6u,
    };
    output_orchestrator_trace *trace = context;
    assert(trace != NULL && engine != NULL && engine_length == 0x3894u &&
           descriptor != NULL && status != NULL);
    const size_t index = (size_t)descriptor->id;
    assert(index < GOMORE_PRIMITIVES_OUTPUT_STAGE_COUNT &&
           descriptor->stage_state_offset == state_offsets[index] &&
           descriptor->control_offset == control_offsets[index] &&
           descriptor->status_offset == status_offsets[index] &&
           descriptor->stock_stage_number == stage_numbers[index] &&
           descriptor->argument_count == argument_counts[index] &&
           descriptor->stage_state_offset < engine_length);
    trace->called_mask |= UINT32_C(1) << (uint32_t)index;
    trace->elapsed[index] = elapsed_updates;
    *status = UINT32_C(0xA0) + (uint32_t)index;
    return true;
}

typedef struct {
    uint8_t bytes[GOMORE_PRIMITIVES_PKEY_PARTITION_BYTES];
    uint32_t offsets[16];
    size_t lengths[16];
    uint32_t write_offsets[16];
    size_t write_lengths[16];
    unsigned initialize_calls;
    unsigned read_calls;
    unsigned write_calls;
    unsigned erase_calls;
    unsigned fail_read_call;
    unsigned fail_write_call;
    unsigned fail_erase_call;
    bool initialize_success;
} pkey_store_trace;

static pkey_store_trace g_pkey_store_trace;

static bool pkey_store_initialize_fixture(
    gomore_primitives_pkey_store *store) {
    ++g_pkey_store_trace.initialize_calls;
    if (!g_pkey_store_trace.initialize_success) {
        return false;
    }
    store->initialized = true;
    return true;
}

static bool pkey_store_read_fixture(
    void *context, uint32_t offset,
    uint8_t *destination, size_t length) {
    pkey_store_trace *trace = context;
    const unsigned call = trace->read_calls;
    assert(call < 8u);
    trace->offsets[call] = offset;
    trace->lengths[call] = length;
    ++trace->read_calls;
    if (trace->fail_read_call == trace->read_calls) {
        return false;
    }
    if (offset < UINT32_C(0xA000) || destination == NULL) {
        return false;
    }
    const size_t source_offset = (size_t)(offset - UINT32_C(0xA000));
    if (source_offset > sizeof(trace->bytes) ||
            length > sizeof(trace->bytes) - source_offset) {
        return false;
    }
    memcpy(destination, &trace->bytes[source_offset], length);
    return true;
}

static bool pkey_store_write_fixture(
    void *context, uint32_t offset,
    const uint8_t *source, size_t length) {
    pkey_store_trace *trace = context;
    const unsigned call = trace->write_calls;
    assert(call < 16u);
    trace->write_offsets[call] = offset;
    trace->write_lengths[call] = length;
    ++trace->write_calls;
    if (trace->fail_write_call == trace->write_calls) {
        return false;
    }
    if (offset < UINT32_C(0xA000) || source == NULL) {
        return false;
    }
    const size_t destination_offset =
        (size_t)(offset - UINT32_C(0xA000));
    if (destination_offset > sizeof(trace->bytes) ||
            length > sizeof(trace->bytes) - destination_offset) {
        return false;
    }
    memcpy(&trace->bytes[destination_offset], source, length);
    return true;
}

static bool pkey_store_erase_fixture(
    void *context, uint32_t offset, size_t length) {
    pkey_store_trace *trace = context;
    ++trace->erase_calls;
    if (trace->fail_erase_call == trace->erase_calls ||
            offset != UINT32_C(0xA000) ||
            length != GOMORE_PRIMITIVES_PKEY_PARTITION_BYTES) {
        return false;
    }
    memset(trace->bytes, UINT8_MAX, sizeof(trace->bytes));
    return true;
}

static float sleep_power_fixture(float base, float exponent) {
    assert(base == bits_float(UINT32_C(0x3F8CCCCD)));
    return exponent < 1.0f ? 2.0f : 4.0f;
}

static float adapter_power10(float base, float exponent) {
    if (base == 10.0f) {
        assert(exponent == 2.0f || exponent == 3.0f || exponent == 5.0f);
        if (exponent == 2.0f) {
            return 100.0f;
        }
        return exponent == 3.0f ? 1000.0f : 100000.0f;
    }
    assert(exponent == 2.0f);
    return base * base;
}

static void adapter_seed(uint32_t seed) {
    active_adapter_trace.seed = seed;
}

static void adapter_finish_initialize(void *record) {
    ++active_adapter_trace.finish_calls;
    ((uint8_t *)record)[0x57] = 0x77u;
}

static int32_t adapter_state_mode0(void *state, uint8_t value) {
    assert(state == &active_adapter_trace.state[0xD14]);
    active_adapter_trace.state_value = value;
    ++active_adapter_trace.state_calls;
    return 0;
}

static int32_t adapter_state_mode1(void *state, uint8_t value) {
    assert(state == &active_adapter_trace.state[0x13F8]);
    active_adapter_trace.state_value = value;
    ++active_adapter_trace.state_calls;
    return 7;
}

static int32_t adapter_state_mode2(void *state) {
    assert(state == &active_adapter_trace.state[0xD98]);
    ++active_adapter_trace.state_calls;
    return 0;
}

static int32_t adapter_state_mode3(void *state) {
    assert(state == &active_adapter_trace.state[0x391C]);
    ++active_adapter_trace.state_calls;
    return 0;
}

static int32_t adapter_process_record(void *state, void *record) {
    (void)state;
    const uint8_t *bytes = record;
    const unsigned index = active_adapter_trace.record_steps;
    assert(index < 4u);
    active_adapter_trace.record_sequences[index] =
        (uint32_t)bytes[4] | (uint32_t)bytes[5] << 8u |
        (uint32_t)bytes[6] << 16u | (uint32_t)bytes[7] << 24u;
    ++active_adapter_trace.record_steps;
    return 42;
}

typedef struct {
    unsigned calls;
    uint32_t sample_indices[8];
    int32_t heart_rates[8];
    float speeds[8];
    float configurations[8];
    uint32_t current_time;
    float auxiliaries[3];
    float energy;
} dormant_estimator_trace;

static dormant_estimator_trace active_dormant_estimator_trace;

static int32_t dormant_estimator_process_record(void *state, void *record) {
    gomore_primitives_dormant_estimator_record *input = record;
    const unsigned index = active_dormant_estimator_trace.calls;
    assert(state != NULL && input != NULL && input->configuration != NULL);
    assert(index < 8u);
    active_dormant_estimator_trace.sample_indices[index] =
        input->sample_index;
    active_dormant_estimator_trace.heart_rates[index] =
        input->selected_heart_rate;
    active_dormant_estimator_trace.speeds[index] = input->selected_speed;
    active_dormant_estimator_trace.configurations[index] =
        input->configuration[2];
    active_dormant_estimator_trace.current_time = input->current_time;
    active_dormant_estimator_trace.auxiliaries[0] =
        input->current_auxiliary;
    active_dormant_estimator_trace.auxiliaries[1] =
        input->copied_auxiliary_1;
    active_dormant_estimator_trace.auxiliaries[2] =
        input->copied_auxiliary_2;
    active_dormant_estimator_trace.energy = input->trailing_total_energy;
    input->selected_heart_rate = (int32_t)(
        (uint32_t)input->selected_heart_rate + 1u);
    input->configuration[2] += 1.0f;
    ++active_dormant_estimator_trace.calls;
    return 0;
}

typedef struct {
    unsigned calls;
    uintptr_t runtime_binding;
    uintptr_t pool_binding;
    uint16_t dimensions[4];
} tensor_fill_trace;

static tensor_fill_trace active_tensor_fill_trace;

static uint32_t create_filled_tensor_fixture(
    uintptr_t runtime_binding, uintptr_t pool_binding, uint32_t rank,
    const uint16_t *dimensions, size_t dimension_count, float fill) {
    const unsigned index = active_tensor_fill_trace.calls;
    assert(index < 4u && rank == 1u && dimensions != NULL &&
           dimension_count == 1u && fill == 0.0f);
    active_tensor_fill_trace.runtime_binding = runtime_binding;
    active_tensor_fill_trace.pool_binding = pool_binding;
    active_tensor_fill_trace.dimensions[index] = dimensions[0];
    ++active_tensor_fill_trace.calls;
    return UINT32_C(0x9000) + index;
}

typedef struct {
    uint8_t record[64];
    uint8_t *lookup_result;
    uint32_t modes[3];
    size_t mode_index;
    char order[16];
    size_t order_length;
    uintptr_t lookup_binding;
    uint32_t publish_topic;
    const void *publish_payload;
    size_t publish_length;
    unsigned structured_logs;
    unsigned secondary_logs;
    bool accepted;
} final_sleep_trace;

static final_sleep_trace g_final_sleep_trace;

static void final_sleep_trace_step(char step) {
    assert(g_final_sleep_trace.order_length <
           sizeof(g_final_sleep_trace.order));
    g_final_sleep_trace.order[g_final_sleep_trace.order_length++] = step;
}

static uint8_t *final_sleep_lookup(uintptr_t record_binding) {
    final_sleep_trace_step('L');
    g_final_sleep_trace.lookup_binding = record_binding;
    return g_final_sleep_trace.lookup_result;
}

static uint32_t final_sleep_log_modes(void) {
    final_sleep_trace_step('M');
    assert(g_final_sleep_trace.mode_index < 3u);
    return g_final_sleep_trace.modes[g_final_sleep_trace.mode_index++];
}

static void final_sleep_check_log(
    uint8_t record_type, uint32_t start_timestamp,
    uint32_t end_timestamp, uint16_t compact_count) {
    assert(record_type == 2u);
    assert(start_timestamp == UINT32_C(0x11223344));
    assert(end_timestamp == UINT32_C(0x55667788));
    assert(compact_count ==
           (uint16_t)((uint16_t)g_final_sleep_trace.record[0x1Eu] |
                      (uint16_t)((uint16_t)
                          g_final_sleep_trace.record[0x1Fu] << 8u)));
}

static void final_sleep_structured_log(
    uint8_t record_type, uint32_t start_timestamp,
    uint32_t end_timestamp, uint16_t compact_count) {
    final_sleep_trace_step('S');
    ++g_final_sleep_trace.structured_logs;
    final_sleep_check_log(
        record_type, start_timestamp, end_timestamp, compact_count);
}

static void final_sleep_secondary_log(
    uint8_t record_type, uint32_t start_timestamp,
    uint32_t end_timestamp, uint16_t compact_count) {
    final_sleep_trace_step('N');
    ++g_final_sleep_trace.secondary_logs;
    final_sleep_check_log(
        record_type, start_timestamp, end_timestamp, compact_count);
}

static bool final_sleep_accept(const uint8_t *record) {
    final_sleep_trace_step('A');
    assert(record == g_final_sleep_trace.record);
    return g_final_sleep_trace.accepted;
}

static void final_sleep_publish(
    uint32_t topic, const void *payload, size_t payload_length) {
    final_sleep_trace_step('P');
    g_final_sleep_trace.publish_topic = topic;
    g_final_sleep_trace.publish_payload = payload;
    g_final_sleep_trace.publish_length = payload_length;
}

static void final_sleep_release(void *record) {
    final_sleep_trace_step('F');
    assert(record == g_final_sleep_trace.record);
}

typedef struct {
    char order[16];
    size_t order_length;
    bool ready;
    bool final_available;
    uint8_t sleep_status;
    uint32_t authorization_slot;
    bool authorization_enabled;
    uint32_t activity[2];
} output_lifecycle_trace;

static output_lifecycle_trace g_output_lifecycle_trace;

static void output_lifecycle_step(char step) {
    assert(g_output_lifecycle_trace.order_length <
           sizeof(g_output_lifecycle_trace.order));
    g_output_lifecycle_trace.order[
        g_output_lifecycle_trace.order_length++] = step;
}

static void output_lifecycle_refresh(void *context) {
    assert(context == &g_output_lifecycle_trace);
    output_lifecycle_step('R');
}

static void output_lifecycle_update(void *context) {
    assert(context == &g_output_lifecycle_trace);
    output_lifecycle_step('U');
}

static bool output_lifecycle_ready(void *context) {
    assert(context == &g_output_lifecycle_trace);
    output_lifecycle_step('Q');
    return g_output_lifecycle_trace.ready;
}

static void output_lifecycle_activity(
    void *context, const uint32_t activity[2]) {
    assert(context == &g_output_lifecycle_trace && activity != NULL);
    output_lifecycle_step('A');
    g_output_lifecycle_trace.activity[0] = activity[0];
    g_output_lifecycle_trace.activity[1] = activity[1];
}

static void output_lifecycle_status(void *context, uint8_t status) {
    assert(context == &g_output_lifecycle_trace);
    output_lifecycle_step('S');
    g_output_lifecycle_trace.sleep_status = status;
}

static bool output_lifecycle_final(void *context) {
    assert(context == &g_output_lifecycle_trace);
    output_lifecycle_step('F');
    return g_output_lifecycle_trace.final_available;
}

static void output_lifecycle_authorize(
    void *context, uint32_t slot, bool enabled) {
    assert(context == &g_output_lifecycle_trace);
    output_lifecycle_step('G');
    g_output_lifecycle_trace.authorization_slot = slot;
    g_output_lifecycle_trace.authorization_enabled = enabled;
}

typedef struct {
    char order[32];
    size_t order_length;
    uintptr_t next_handle;
} authorization_trace;

static authorization_trace g_authorization_trace;

static void authorization_step(char step) {
    assert(g_authorization_trace.order_length <
           sizeof(g_authorization_trace.order));
    g_authorization_trace.order[
        g_authorization_trace.order_length++] = step;
}

static uintptr_t authorization_register(
    void *context, uint8_t stream_index) {
    assert(context == &g_authorization_trace && stream_index < 4u);
    authorization_step((char)('A' + (char)stream_index));
    return ++g_authorization_trace.next_handle;
}

static void authorization_unregister(
    void *context, uint8_t stream_index, uintptr_t handle) {
    assert(context == &g_authorization_trace && stream_index < 4u &&
           handle != (uintptr_t)0);
    authorization_step((char)('a' + (char)stream_index));
}

static uintptr_t authorization_timer_create(
    void *context, uint32_t period_milliseconds) {
    assert(context == &g_authorization_trace &&
           period_milliseconds == 1000u);
    authorization_step('C');
    return ++g_authorization_trace.next_handle;
}

static void authorization_timer_delete(
    void *context, uintptr_t handle) {
    assert(context == &g_authorization_trace &&
           handle != (uintptr_t)0);
    authorization_step('X');
}

static void authorization_slot_enable(void *context) {
    assert(context == &g_authorization_trace);
    authorization_step('E');
}

static void authorization_slot_disable(void *context) {
    assert(context == &g_authorization_trace);
    authorization_step('D');
}

static unsigned g_locomotion_preprocess_classify_calls;

static float locomotion_preprocess_sqrt(float value) {
    if (value == 25.0f) {
        return 5.0f;
    }
    assert(value == 0.0f);
    return 0.0f;
}

static void locomotion_preprocess_classify(void *state, void *output) {
    assert(state != NULL && output != NULL);
    ++g_locomotion_preprocess_classify_calls;
    ((uint8_t *)output)[0] = UINT8_C(0x77);
}

typedef struct {
    uint8_t record[56];
    uint8_t timeline[0xB40];
    size_t allocation_sizes[2];
    void *released[2];
    unsigned allocation_calls;
    unsigned release_calls;
    unsigned prepare_calls;
    unsigned mode_calls;
    unsigned dispatch_calls;
    unsigned publish_calls;
    unsigned fail_allocation_call;
    bool publish_requested;
} sleep_force_wake_trace;

static sleep_force_wake_trace g_sleep_force_wake_trace;

static void *sleep_force_wake_allocate(size_t length) {
    const unsigned call = ++g_sleep_force_wake_trace.allocation_calls;
    assert(call <= 2u);
    g_sleep_force_wake_trace.allocation_sizes[call - 1u] = length;
    if (call == g_sleep_force_wake_trace.fail_allocation_call) {
        return NULL;
    }
    if (call == 1u) {
        assert(length == sizeof(g_sleep_force_wake_trace.record));
        return g_sleep_force_wake_trace.record;
    }
    assert(length == sizeof(g_sleep_force_wake_trace.timeline));
    return g_sleep_force_wake_trace.timeline;
}

static void sleep_force_wake_release(void *memory) {
    assert(g_sleep_force_wake_trace.release_calls < 2u);
    g_sleep_force_wake_trace.released[
        g_sleep_force_wake_trace.release_calls++] = memory;
}

static void sleep_force_wake_prepare(uint32_t mode, uint8_t record[56]) {
    ++g_sleep_force_wake_trace.prepare_calls;
    assert(mode == 1u && record == g_sleep_force_wake_trace.record);
    for (size_t index = 0u; index < 56u; ++index) {
        assert(record[index] == 0u);
    }
    record[0] = 3u;
    if (g_sleep_force_wake_trace.publish_requested) {
        record[8] = 8u;
    }
}

static void sleep_force_wake_set_mode(uint32_t mode, uint32_t enabled) {
    ++g_sleep_force_wake_trace.mode_calls;
    assert(mode == 4u && enabled == 0u);
}

static void sleep_force_wake_dispatch(
    uint32_t result_words[2], uint8_t report[88],
    uint8_t timeline[0xB40]) {
    ++g_sleep_force_wake_trace.dispatch_calls;
    assert(result_words[0] == 0u && result_words[1] == 0u &&
           timeline == g_sleep_force_wake_trace.timeline);
    for (size_t index = 0u; index < 88u; ++index) {
        assert(report[index] == 0u);
    }
    for (size_t index = 0u; index < 0xB40u; ++index) {
        assert(timeline[index] == 0u);
    }
    result_words[0] = UINT32_C(0x11223344);
    report[4] = UINT8_C(0x55);
}

static void sleep_force_wake_publish(
    uint32_t result_words[2], uint8_t report[88]) {
    ++g_sleep_force_wake_trace.publish_calls;
    assert(result_words[0] == UINT32_C(0x11223344) &&
           report[4] == UINT8_C(0x55));
}

typedef struct {
    uint8_t *state;
    unsigned filter_calls;
    unsigned ratio_calls;
    int32_t filter_result;
    int32_t filtered_value;
    int32_t raw_value;
    uint32_t interval;
    float selected_heart_rate;
    float selected_speed;
} dormant_hr_ratio_trace;

static dormant_hr_ratio_trace g_dormant_hr_ratio_trace;

static int32_t dormant_hr_filter_update(
    void *state, int32_t input, int32_t output[2],
    uint32_t interval_milliseconds) {
    assert(state == &g_dormant_hr_ratio_trace.state[0x278u]);
    ++g_dormant_hr_ratio_trace.filter_calls;
    g_dormant_hr_ratio_trace.raw_value = input;
    g_dormant_hr_ratio_trace.interval = interval_milliseconds;
    output[0] = g_dormant_hr_ratio_trace.filtered_value;
    output[1] = input;
    return g_dormant_hr_ratio_trace.filter_result;
}

static void dormant_ratio_accumulate(
    void *state, const gomore_primitives_dormant_ratio_input *input) {
    assert(state == g_dormant_hr_ratio_trace.state && input != NULL);
    ++g_dormant_hr_ratio_trace.ratio_calls;
    g_dormant_hr_ratio_trace.selected_heart_rate =
        input->selected_heart_rate;
    g_dormant_hr_ratio_trace.selected_speed = input->selected_speed;
    assert(input->reserved_zero == 0.0f &&
           input->below_range_weight == 0.0f &&
           input->thresholds == (float *)(void *)&g_dormant_hr_ratio_trace
               .state[0x170u] &&
           input->primary_sums == (float *)(void *)&g_dormant_hr_ratio_trace
               .state[0x1C0u] &&
           input->primary_counts == (float *)(void *)&g_dormant_hr_ratio_trace
               .state[0x1D8u] &&
           input->auxiliary_first == (float *)(void *)&g_dormant_hr_ratio_trace
               .state[0x1F0u] &&
           input->auxiliary_second ==
               (float *)(void *)&g_dormant_hr_ratio_trace.state[0x1F4u]);
}

static unsigned dormant_ratio_power_calls;

static float dormant_ratio_power(float base, float exponent) {
    ++dormant_ratio_power_calls;
    if (exponent == 2.0f) {
        return base * base;
    }
    assert(exponent == 0.5f);
    if (base == 0.0f) {
        return 0.0f;
    }
    assert(base == 100.0f);
    return 10.0f;
}

typedef struct {
    void *state;
    float coefficients[4];
    float selected_root;
    unsigned power_calls;
    unsigned quadratic_calls;
    unsigned cubic_calls;
} dormant_root_trace;

static dormant_root_trace g_dormant_root_trace;

static float dormant_root_power(float value, float exponent) {
    assert(exponent == 2.0f);
    ++g_dormant_root_trace.power_calls;
    return value * value;
}

static void dormant_quadratic_dispatch(
    float coefficient_a, float coefficient_b, float coefficient_c,
    void *state) {
    ++g_dormant_root_trace.quadratic_calls;
    g_dormant_root_trace.state = state;
    g_dormant_root_trace.coefficients[0] = coefficient_a;
    g_dormant_root_trace.coefficients[1] = coefficient_b;
    g_dormant_root_trace.coefficients[2] = coefficient_c;
}

static void dormant_cubic_dispatch(
    float coefficient_a, float coefficient_b, float coefficient_c,
    float coefficient_d, void *state) {
    ++g_dormant_root_trace.cubic_calls;
    g_dormant_root_trace.state = state;
    g_dormant_root_trace.coefficients[0] = coefficient_a;
    g_dormant_root_trace.coefficients[1] = coefficient_b;
    g_dormant_root_trace.coefficients[2] = coefficient_c;
    g_dormant_root_trace.coefficients[3] = coefficient_d;
}

static void dormant_alternate_quadratic_dispatch(
    float coefficient_a, float coefficient_b, float coefficient_c,
    void *state) {
    dormant_quadratic_dispatch(
        coefficient_a, coefficient_b, coefficient_c, state);
    uint8_t *bytes = state;
    store_u32_fixture(&bytes[0x18u],
                      float_bits(g_dormant_root_trace.selected_root));
    store_u32_fixture(&bytes[0x1Cu], 0u);
    store_u32_fixture(&bytes[0x20u], 0u);
}

static void dormant_alternate_cubic_dispatch(
    float coefficient_a, float coefficient_b, float coefficient_c,
    float coefficient_d, void *state) {
    dormant_cubic_dispatch(
        coefficient_a, coefficient_b, coefficient_c, coefficient_d,
        state);
    uint8_t *bytes = state;
    store_u32_fixture(&bytes[0x18u],
                      float_bits(g_dormant_root_trace.selected_root));
    store_u32_fixture(&bytes[0x1Cu], 0u);
    store_u32_fixture(&bytes[0x20u], 0u);
}

typedef struct {
    float roots[3];
    unsigned power_calls;
    unsigned quadratic_calls;
    unsigned cubic_calls;
} dormant_root_resolve_trace;

static dormant_root_resolve_trace g_dormant_root_resolve_trace;

static float dormant_root_resolve_power(float value, float exponent) {
    ++g_dormant_root_resolve_trace.power_calls;
    const int32_t signed_exponent = (int32_t)exponent;
    assert((float)signed_exponent == exponent);
    const uint32_t magnitude = signed_exponent < 0
        ? (uint32_t)(-signed_exponent) : (uint32_t)signed_exponent;
    float result = 1.0f;
    for (uint32_t index = 0u; index < magnitude; ++index) {
        result *= value;
    }
    return signed_exponent < 0 ? 1.0f / result : result;
}

static void dormant_root_resolve_store(void *state) {
    uint8_t *bytes = state;
    for (size_t index = 0u; index < 3u; ++index) {
        store_u32_fixture(
            &bytes[0x18u + index * 4u],
            float_bits(g_dormant_root_resolve_trace.roots[index]));
    }
}

static void dormant_root_resolve_quadratic(
    float coefficient_a, float coefficient_b, float coefficient_c,
    void *state) {
    (void)coefficient_a;
    (void)coefficient_b;
    (void)coefficient_c;
    ++g_dormant_root_resolve_trace.quadratic_calls;
    dormant_root_resolve_store(state);
}

static void dormant_root_resolve_cubic(
    float coefficient_a, float coefficient_b, float coefficient_c,
    float coefficient_d, void *state) {
    (void)coefficient_a;
    (void)coefficient_b;
    (void)coefficient_c;
    (void)coefficient_d;
    ++g_dormant_root_resolve_trace.cubic_calls;
    dormant_root_resolve_store(state);
}

typedef struct {
    void *state;
    float primary;
    float secondary;
    float auxiliary;
    float reduced_input;
    float reducer_result;
    float finalizer_result;
    int32_t mode;
    unsigned power_calls;
    unsigned reducer_calls;
    unsigned finalizer_calls;
} dormant_mode1_target_trace;

static dormant_mode1_target_trace g_dormant_mode1_target_trace;

static float dormant_mode1_target_power(float value, float exponent) {
    assert(exponent == 2.0f);
    ++g_dormant_mode1_target_trace.power_calls;
    return value * value;
}

static float dormant_mode1_target_reduce(
    float primary, float secondary, float auxiliary,
    void *state, int32_t mode) {
    ++g_dormant_mode1_target_trace.reducer_calls;
    g_dormant_mode1_target_trace.state = state;
    g_dormant_mode1_target_trace.primary = primary;
    g_dormant_mode1_target_trace.secondary = secondary;
    g_dormant_mode1_target_trace.auxiliary = auxiliary;
    g_dormant_mode1_target_trace.mode = mode;
    return g_dormant_mode1_target_trace.reducer_result;
}

static float dormant_mode1_target_finalize(
    float reduced, float auxiliary, void *state, int32_t mode) {
    ++g_dormant_mode1_target_trace.finalizer_calls;
    assert(state == g_dormant_mode1_target_trace.state &&
           auxiliary == g_dormant_mode1_target_trace.auxiliary &&
           mode == g_dormant_mode1_target_trace.mode);
    g_dormant_mode1_target_trace.reduced_input = reduced;
    return g_dormant_mode1_target_trace.finalizer_result;
}

typedef struct {
    float arctangent_input;
    float trigonometric_input;
    unsigned arctangent_calls;
    unsigned cosine_calls;
    unsigned sine_calls;
} dormant_mode0_math_trace;

static dormant_mode0_math_trace g_dormant_mode0_math_trace;

static float dormant_mode0_arctangent(float value) {
    ++g_dormant_mode0_math_trace.arctangent_calls;
    g_dormant_mode0_math_trace.arctangent_input = value;
    return 0.5f;
}

static float dormant_mode0_cosine(float value) {
    ++g_dormant_mode0_math_trace.cosine_calls;
    g_dormant_mode0_math_trace.trigonometric_input = value;
    return 0.8f;
}

static float dormant_mode0_sine(float value) {
    ++g_dormant_mode0_math_trace.sine_calls;
    assert(value == g_dormant_mode0_math_trace.trigonometric_input);
    return 0.6f;
}

typedef struct {
    uint8_t *graph_state;
    unsigned zero_build_calls;
    unsigned nonzero_build_calls;
    unsigned recurrent_calls;
    unsigned dense_calls;
    int32_t family;
    uint32_t arena_seed;
    uint8_t recurrent_dimensions[6];
    uint8_t dense_dimensions[8];
} sleep_graph_dispatch_trace;

static sleep_graph_dispatch_trace g_sleep_graph_dispatch_trace;

static uint32_t sleep_graph_build_zero(void *graph_state) {
    ++g_sleep_graph_dispatch_trace.zero_build_calls;
    g_sleep_graph_dispatch_trace.graph_state = graph_state;
    return UINT32_C(0x1000);
}

static uint32_t sleep_graph_build_nonzero(
    int32_t family, void *graph_state, uint32_t arena_seed) {
    ++g_sleep_graph_dispatch_trace.nonzero_build_calls;
    g_sleep_graph_dispatch_trace.family = family;
    g_sleep_graph_dispatch_trace.graph_state = graph_state;
    g_sleep_graph_dispatch_trace.arena_seed = arena_seed;
    return UINT32_C(0x2000);
}

static void sleep_graph_construct_recurrent(
    uint8_t descriptor[24], uint8_t units, uint8_t input_dimension,
    uint32_t *arena_cursor) {
    const unsigned call = g_sleep_graph_dispatch_trace.recurrent_calls++;
    assert(call < 3u && descriptor != NULL && arena_cursor != NULL);
    g_sleep_graph_dispatch_trace.recurrent_dimensions[call * 2u] = units;
    g_sleep_graph_dispatch_trace.recurrent_dimensions[call * 2u + 1u] =
        input_dimension;
    memset(descriptor, (int)(UINT8_C(0x10) + (uint8_t)call), 24u);
    store_u32_fixture(&descriptor[0x0Cu], *arena_cursor);
    *arena_cursor += UINT32_C(0x100);
}

static void sleep_graph_construct_dense(
    uint8_t descriptor[24], uint8_t dim_a, uint8_t dim_b,
    uint8_t flag_a, uint8_t flag_b, uint32_t *arena_cursor) {
    const unsigned call = g_sleep_graph_dispatch_trace.dense_calls++;
    assert(call < 2u && descriptor != NULL && arena_cursor != NULL);
    const size_t offset = call * 4u;
    g_sleep_graph_dispatch_trace.dense_dimensions[offset] = dim_a;
    g_sleep_graph_dispatch_trace.dense_dimensions[offset + 1u] = dim_b;
    g_sleep_graph_dispatch_trace.dense_dimensions[offset + 2u] = flag_a;
    g_sleep_graph_dispatch_trace.dense_dimensions[offset + 3u] = flag_b;
    memset(descriptor, (int)(UINT8_C(0x20) + (uint8_t)call), 24u);
    store_u32_fixture(&descriptor[0x0Cu], *arena_cursor);
    *arena_cursor += UINT32_C(0x200);
}

typedef struct {
    void *state;
    uint32_t elapsed;
    unsigned calls;
} host_input_core_trace;

static host_input_core_trace g_host_input_core_trace;

static void host_input_update_core(void *engine_state,
                                   uint32_t elapsed_seconds) {
    ++g_host_input_core_trace.calls;
    g_host_input_core_trace.state = engine_state;
    g_host_input_core_trace.elapsed = elapsed_seconds;
}

typedef struct {
    unsigned diagnose_calls;
    unsigned error_calls;
    unsigned apply_calls;
    unsigned snapshot_calls;
    unsigned order_count;
    unsigned order[3];
    const gomore_primitives_host_input *input;
    uint32_t timestamp;
    int32_t error;
    int32_t apply_result;
} sensor_update_trace;

static sensor_update_trace g_sensor_update_trace;

static void sensor_update_diagnose(
    const void *context, const gomore_primitives_host_input *input) {
    assert(context == &g_sensor_update_trace && input != NULL &&
           g_sensor_update_trace.order_count < 3u);
    ++g_sensor_update_trace.diagnose_calls;
    g_sensor_update_trace.input = input;
    g_sensor_update_trace.order[g_sensor_update_trace.order_count++] = 1u;
}

static void sensor_update_log_error(const void *context, int32_t status) {
    assert(context == &g_sensor_update_trace);
    ++g_sensor_update_trace.error_calls;
    g_sensor_update_trace.error = status;
}

static int32_t sensor_update_apply(
    const void *context, const gomore_primitives_host_input *input,
    uint32_t normalized_timestamp) {
    assert(context == &g_sensor_update_trace && input != NULL &&
           g_sensor_update_trace.order_count < 3u);
    ++g_sensor_update_trace.apply_calls;
    g_sensor_update_trace.input = input;
    g_sensor_update_trace.timestamp = normalized_timestamp;
    g_sensor_update_trace.order[g_sensor_update_trace.order_count++] = 2u;
    return g_sensor_update_trace.apply_result;
}

static void sensor_update_snapshot(const void *context) {
    assert(context == &g_sensor_update_trace &&
           g_sensor_update_trace.order_count < 3u);
    ++g_sensor_update_trace.snapshot_calls;
    g_sensor_update_trace.order[g_sensor_update_trace.order_count++] = 3u;
}

typedef struct {
    unsigned calls;
    float first;
    float middle;
    float latest;
    float result;
    uint8_t consensus;
} motion_classifier_estimator_trace;

static motion_classifier_estimator_trace g_motion_classifier_estimator_trace;

static float motion_classifier_state1_estimate(
    float first, float middle, float latest, uint8_t *consensus) {
    ++g_motion_classifier_estimator_trace.calls;
    g_motion_classifier_estimator_trace.first = first;
    g_motion_classifier_estimator_trace.middle = middle;
    g_motion_classifier_estimator_trace.latest = latest;
    *consensus = g_motion_classifier_estimator_trace.consensus;
    return g_motion_classifier_estimator_trace.result;
}

typedef struct {
    unsigned calls;
    const float *values[4];
    uint32_t counts[4];
    uint32_t modes[4];
    float responses[4][4];
} activity_statistics_trace;

static activity_statistics_trace g_activity_statistics_trace;

static void activity_statistics_fixture(
    const float *values, uint32_t count, uint32_t mode, float output[4]) {
    const unsigned call = g_activity_statistics_trace.calls++;
    assert(call < 4u);
    g_activity_statistics_trace.values[call] = values;
    g_activity_statistics_trace.counts[call] = count;
    g_activity_statistics_trace.modes[call] = mode;
    memcpy(output, g_activity_statistics_trace.responses[call],
           sizeof(g_activity_statistics_trace.responses[call]));
}

static float activity_square_root_fixture(float value) {
    return sqrtf(value);
}

typedef struct {
    float rate;
    float confidence;
    int32_t result;
    unsigned calls;
    uint32_t elapsed;
    const void *input;
    uint32_t status;
} respiratory_estimate_trace;

static int32_t respiratory_estimate_fixture(
    void *state, uint32_t elapsed, const void *input, uint32_t status,
    float *rate, float *confidence) {
    respiratory_estimate_trace *trace = state;
    ++trace->calls;
    trace->elapsed = elapsed;
    trace->input = input;
    trace->status = status;
    *rate = trace->rate;
    *confidence = trace->confidence;
    return trace->result;
}

static double respiratory_square_root_fixture(double value) {
    return sqrt(value);
}

static void initialize_sleep_cycle_fixture(
    gomore_primitives_sleep_cycle_state *state,
    gomore_primitives_sleep_cycle_input *input,
    gomore_primitives_sleep_interval_result *output) {
    memset(state, 0, sizeof(*state));
    state->policy.minimum_slots = 1;
    state->policy.reserved = 60u;
    state->policy.disable_history_scan = 1u;
    state->policy.end_hour = 24u;
    memset(input, 0, sizeof(*input));
    input->quality_flag6 = true;
    memset(output, 0, sizeof(*output));
}

void test_reconstructed_gomore_primitives(void) {
    uint8_t records[GOMORE_PRIMITIVES_RECORD_COUNT *
                    GOMORE_PRIMITIVES_RECORD_STRIDE];
    memset(records, 0, sizeof(records));
    assert(gomore_primitives_records_all_clear(records, sizeof(records)));
    records[3u * GOMORE_PRIMITIVES_RECORD_STRIDE] = 1u;
    assert(!gomore_primitives_records_all_clear(records, sizeof(records)));
    records[3u * GOMORE_PRIMITIVES_RECORD_STRIDE] = 2u;
    assert(gomore_primitives_records_all_clear(records, sizeof(records)));

    uint32_t record5[5] = {UINT32_C(0xDEADBEEF), 0u, 0u, 0u, 0u};
    gomore_primitives_record5_initialize(record5, true, 4u, 8u, 100u);
    assert(record5[0] == UINT32_C(0xDEADBEEF));
    assert(record5[1] == 4u && record5[2] == 8u);
    assert(record5[3] == 100u && record5[4] == 120u);
    gomore_primitives_record5_initialize(record5, false, 5u, 9u, 200u);
    assert(record5[4] == 0u);
    uint32_t span[2] = {0u, 0u};
    gomore_primitives_span_initialize(span, true, 50u);
    assert(span[0] == 50u && span[1] == 70u);
    gomore_primitives_span_initialize(span, false, 60u);
    assert(span[0] == 60u && span[1] == 0u);

    uint8_t bytes[0xC0];
    memset(bytes, UINT8_C(0xA5), sizeof(bytes));
    assert(gomore_primitives_clear_two_records(bytes, sizeof(bytes)));
    for (size_t index = 0u; index < 0x28u; ++index) {
        assert(bytes[index] == 0u);
    }
    float missing[2] = {0.0f, 0.0f};
    assert(gomore_primitives_fill_missing_pair(missing));
    assert(missing[0] == -1.0f && missing[1] == -1.0f);
    memset(bytes, UINT8_C(0xA5), sizeof(bytes));
    assert(gomore_primitives_clear_90(bytes, sizeof(bytes)));
    for (size_t index = 0u; index < 0x5Au; ++index) {
        assert(bytes[index] == 0u);
    }

    score_trace trace = {{0u, 0u, 0u, 0u}, 3.25f, 0u};
    const gomore_primitives_score_providers score_providers = {
        prepare_score, read_score,
    };
    float output = 0.0f;
    assert(gomore_primitives_prepare_and_score(
        &score_providers, 1u, 2u, 3u, 4u, &trace, &output));
    assert(trace.prepare_calls == 1u && trace.arguments[3] == 4u);
    assert(output == 3.25f);

    assert(gomore_primitives_float_in_encoded_range(
        bits_float(UINT32_C(0x42200000))));
    assert(gomore_primitives_float_in_encoded_range(
        bits_float(UINT32_C(0x43600000))));
    assert(!gomore_primitives_float_in_encoded_range(
        bits_float(UINT32_C(0x43700001))));

    uint8_t cadence_consensus = UINT8_C(0xA5);
    assert(gomore_primitives_state1_cadence_estimate(
               125.0f, 125.0f, 125.0f, &cadence_consensus) == 125.0f);
    assert(cadence_consensus == 1u);
    assert(gomore_primitives_state1_cadence_estimate(
               60.0f, 69.0f, 78.0f, &cadence_consensus) == 69.0f);
    assert(cadence_consensus == 1u);
    assert(gomore_primitives_state1_cadence_estimate(
               60.0f, 70.0f, 80.0f, &cadence_consensus) == 70.0f);
    assert(cadence_consensus == 0u);
    assert(gomore_primitives_state1_cadence_estimate(
               60.0f, 60.0f, 120.0f, &cadence_consensus) == 120.0f);
    assert(cadence_consensus == 0u);
    assert(gomore_primitives_state1_cadence_estimate(
               120.0f, 60.0f, 132.0f, &cadence_consensus) == 132.0f);
    assert(gomore_primitives_state1_cadence_estimate(
               100.0f, 60.0f, 132.0f, &cadence_consensus) == 60.0f);
    assert(gomore_primitives_state1_cadence_estimate(
               102.0f, 50.0f, 51.0f, &cadence_consensus) == 102.0f);
    assert(gomore_primitives_state1_cadence_estimate(
               108.0f, 50.0f, 51.0f, &cadence_consensus) == 50.0f);
    assert(gomore_primitives_state1_cadence_estimate(
               50.0f, 50.0f, 50.0f, &cadence_consensus) == 50.0f);
    assert(gomore_primitives_state1_cadence_estimate(
               90.0f, 91.0f, 92.0f, NULL) == 91.0f);

    cadence_consensus = UINT8_C(0xA5);
    assert(gomore_primitives_state2_cadence_estimate(
               150.0f, 155.0f, 160.0f, &cadence_consensus) == 160.0f);
    assert(cadence_consensus == 1u);
    cadence_consensus = UINT8_C(0xA5);
    assert(gomore_primitives_state2_cadence_estimate(
               150.0f, 160.0f, 170.0f, &cadence_consensus) == 170.0f);
    assert(cadence_consensus == 0u);
    cadence_consensus = UINT8_C(0xA5);
    assert(gomore_primitives_state2_cadence_estimate(
               150.0f, 150.0f, 100.0f, &cadence_consensus) == 150.0f);
    assert(cadence_consensus == 0u);
    assert(gomore_primitives_state2_cadence_estimate(
               150.0f, bits_float(UINT32_C(0x42F00001)), 120.0f,
               &cadence_consensus) ==
           bits_float(UINT32_C(0x42F00001)));
    assert(cadence_consensus == 0u);

    gomore_primitives_locomotion_transition_state transition_state = {
        10u, false, 0.0f,
    };
    bool transition_updated = false;
    assert(gomore_primitives_locomotion_transition_accumulate(
        &transition_state, 20.0f, 10u, 10u,
        1.0f, 1.0f, &transition_updated));
    assert(transition_updated && transition_state.initialized &&
           transition_state.accumulated == 20u &&
           transition_state.estimate == 20.0f);
    assert(gomore_primitives_locomotion_transition_accumulate(
        &transition_state, 20.0f, 20u, 1u,
        0.0f, 0.0f, &transition_updated));
    assert(transition_updated && transition_state.accumulated == 21u &&
           transition_state.estimate == 20.25f);
    const gomore_primitives_locomotion_transition_state transition_before =
        transition_state;
    assert(gomore_primitives_locomotion_transition_accumulate(
        &transition_state, 20.0f, 21u, 2u,
        0.0f, 0.0f, &transition_updated));
    assert(!transition_updated &&
           transition_state.accumulated == transition_before.accumulated &&
           transition_state.estimate == transition_before.estimate);

    transition_state =
        (gomore_primitives_locomotion_transition_state){10u, false, 0.0f};
    assert(gomore_primitives_locomotion_transition_accumulate(
        &transition_state, 20.0f, 7u, 10u,
        1.0f, 1.0f, &transition_updated));
    assert(!transition_updated && !transition_state.initialized &&
           transition_state.accumulated == 10u);
    transition_state.accumulated = 5u;
    assert(gomore_primitives_locomotion_transition_accumulate(
        &transition_state, 20.0f, 5u, 10u,
        1.0f, 0.5f, &transition_updated));
    assert(!transition_updated && !transition_state.initialized);
    transition_state.accumulated = 10u;
    assert(gomore_primitives_locomotion_transition_accumulate(
        &transition_state, 5.0f, 10u, 10u,
        1.0f, 1.0f, &transition_updated));
    assert(!transition_updated && !transition_state.initialized);
    assert(!gomore_primitives_locomotion_transition_accumulate(
        NULL, 20.0f, 10u, 10u, 1.0f, 1.0f, &transition_updated));

    const int16_t window_axis0[8] = {
        500, 500, 500, 500, 500, 500, 500, 500,
    };
    const int16_t window_axis1[8] = {
        450, 450, 450, 450, 450, 450, 450, 450,
    };
    const int16_t window_axis2[8] = {
        100, 100, 100, 100, 100, 100, 100, 100,
    };
    assert(gomore_primitives_three_axis_window_gate(
               window_axis0, window_axis1, window_axis2, 8u, 8u, 0, 5u,
               400, 400) == 1);
    const int16_t sparse_axis1[8] = {
        100, 100, 100, 100, 100, 450, 450, 100,
    };
    assert(gomore_primitives_three_axis_window_gate(
               window_axis0, sparse_axis1, window_axis2, 8u, 8u, 0, 5u,
               400, 400) == -1);
    assert(gomore_primitives_three_axis_window_gate(
               window_axis0, window_axis1, window_axis2, 7u, 8u, 0, 5u,
               400, 400) == -1);

    uint8_t locomotion_classifier_state[0x26E];
    uint8_t locomotion_classifier_output[0x3E];
    memset(locomotion_classifier_state, 0,
           sizeof(locomotion_classifier_state));
    memset(locomotion_classifier_output, UINT8_C(0xA5),
           sizeof(locomotion_classifier_output));
    const int16_t classifier_x_std[8] = {
        500, 500, 500, 500, 500, 500, 500, 500,
    };
    const int16_t classifier_y_std[8] = {
        450, 450, 450, 450, 450, 450, 450, 450,
    };
    const int16_t classifier_z_std[8] = {
        100, 100, 100, 100, 100, 100, 100, 100,
    };
    const int16_t classifier_z_mean[8] = {
        300, 300, 300, 300, 300, 300, 300, 300,
    };
    const int16_t classifier_magnitude_std[8] = {
        100, 100, 100, 100, 100, 100, 100, 100,
    };
    const int16_t classifier_magnitude_mean[8] = {
        1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000,
    };
    const int16_t classifier_magnitude_range[8] = {
        500, 500, 500, 500, 500, 500, 500, 500,
    };
    const int16_t classifier_small_ring[8] = {
        10, 10, 10, 10, 10, 10, 10, 10,
    };
    uint16_t classifier_magnitude_history[200];
    for (size_t index = 0u; index < 200u; ++index) {
        classifier_magnitude_history[index] = 900u;
    }
    memcpy(&locomotion_classifier_state[0x02u], classifier_x_std, 16u);
    memcpy(&locomotion_classifier_state[0x12u], classifier_z_mean, 16u);
    memcpy(&locomotion_classifier_state[0x22u], classifier_magnitude_std, 16u);
    memcpy(&locomotion_classifier_state[0x32u], classifier_magnitude_mean, 16u);
    memcpy(&locomotion_classifier_state[0x42u], classifier_magnitude_range, 16u);
    locomotion_classifier_state[0x52u] = 5u;
    memcpy(&locomotion_classifier_state[0x54u],
           classifier_magnitude_history,
           sizeof(classifier_magnitude_history));
    memcpy(&locomotion_classifier_state[0x204u], classifier_y_std, 16u);
    memcpy(&locomotion_classifier_state[0x214u], classifier_z_std, 16u);
    for (size_t offset = 0x224u; offset <= 0x254u; offset += 0x10u) {
        memcpy(&locomotion_classifier_state[offset],
               classifier_small_ring, 16u);
    }
    const int16_t classifier_trend_history[5] = {
        1001, 1002, 1003, 1004, 1005,
    };
    memcpy(&locomotion_classifier_state[0x264u], classifier_trend_history,
           sizeof(classifier_trend_history));
    const gomore_primitives_six_channel_linear_model classifier_ring_model = {
        .weights = {0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f},
        .bias = 1.0f,
        .scale = 1.0f,
        .empty_window_value = 0.0f,
        .minimum_output = -32000,
    };
    const float classifier_linear_coefficients[4] = {
        1.0f, 1.0f, 1.0f, 1.0f,
    };
    const gomore_primitives_locomotion_classifier_configuration
        classifier_configuration = {
            .ring_score_model = &classifier_ring_model,
            .linear_sign_coefficients = classifier_linear_coefficients,
            .linear_sign_bias = -6.0f,
            .autocorrelation = locomotion_classifier_autocorrelation_fixture,
            .crossing_estimate = locomotion_crossing_estimate,
        };
    crossing_estimate_calls = 0u;
    crossing_estimate_values[0] = 200.0f;
    crossing_estimate_values[1] = 240.0f;
    assert(gomore_primitives_locomotion_window_classify(
        locomotion_classifier_state, sizeof(locomotion_classifier_state),
        locomotion_classifier_output, sizeof(locomotion_classifier_output),
        &classifier_configuration));
    assert(bits_float(load_u32_fixture(&locomotion_classifier_output[0x00u])) ==
               100.0f &&
           bits_float(load_u32_fixture(&locomotion_classifier_output[0x04u])) ==
               500.0f &&
           bits_float(load_u32_fixture(&locomotion_classifier_output[0x08u])) ==
               1000.0f &&
           bits_float(load_u32_fixture(&locomotion_classifier_output[0x0Cu])) ==
               300.0f &&
           bits_float(load_u32_fixture(&locomotion_classifier_output[0x10u])) ==
               120.0f &&
           bits_float(load_u32_fixture(&locomotion_classifier_output[0x14u])) ==
               200.0f);
    assert(bits_float(load_u32_fixture(&locomotion_classifier_output[0x20u])) ==
               2.0f &&
           locomotion_classifier_output[0x24u] == UINT8_C(0xA5) &&
           bits_float(load_u32_fixture(&locomotion_classifier_output[0x28u])) ==
               3.0f &&
           bits_float(load_u32_fixture(&locomotion_classifier_output[0x34u])) ==
               6.0f);
    const uint8_t classifier_expected_flags[6] = {
        1u, 1u, 1u, UINT8_MAX, 1u, 1u,
    };
    assert(memcmp(&locomotion_classifier_output[0x38u],
                  classifier_expected_flags,
                  sizeof(classifier_expected_flags)) == 0 &&
           crossing_estimate_calls == 2u);
    const int16_t classifier_expected_trend_history[5] = {
        1002, 1003, 1004, 1005, 1,
    };
    assert(memcmp(&locomotion_classifier_state[0x264u],
                  classifier_expected_trend_history,
                  sizeof(classifier_expected_trend_history)) == 0);
    uint8_t rejected_classifier_output[0x3E];
    memset(rejected_classifier_output, UINT8_C(0x5A),
           sizeof(rejected_classifier_output));
    assert(!gomore_primitives_locomotion_window_classify(
        locomotion_classifier_state, sizeof(locomotion_classifier_state),
        rejected_classifier_output, sizeof(rejected_classifier_output), NULL));
    for (size_t index = 0u; index < sizeof(rejected_classifier_output); ++index) {
        assert(rejected_classifier_output[index] == UINT8_C(0x5A));
    }

    float motion_filter_samples[5] = {1.0f, 0.0f, 0.0f, 0.0f, 0.0f};
    float motion_filter_input_history[5] = {0.0f, 0.0f, 0.0f, 0.0f, 0.0f};
    float motion_filter_output_history[5] = {0.0f, 0.0f, 0.0f, 0.0f, 0.0f};
    assert(gomore_primitives_motion_iir4_filter(
        motion_filter_samples, 5u, motion_filter_input_history,
        motion_filter_output_history));
    assert(motion_filter_samples[0] == bits_float(UINT32_C(0x3C87D6D4)));
    assert(motion_filter_input_history[0] == 1.0f &&
           motion_filter_input_history[4] == 0.0f);
    for (size_t index = 0u; index < 5u; ++index) {
        assert(motion_filter_output_history[index] ==
               motion_filter_samples[index]);
    }
    assert(!gomore_primitives_motion_iir4_filter(
        motion_filter_samples, 4u, motion_filter_input_history,
        motion_filter_output_history));

    const float histogram_boundaries[5] = {
        10.0f, 20.0f, 30.0f, 40.0f, 50.0f,
    };
    float histogram_sums[6] = {0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f};
    float histogram_counts[6] = {0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f};
    assert(gomore_primitives_weighted_histogram6_accumulate(
        15.0f, 2.0f, 6.0f, histogram_boundaries,
        histogram_sums, histogram_counts, 0.5f));
    assert(histogram_sums[1] == 3.0f && histogram_counts[1] == 1.0f);
    assert(gomore_primitives_weighted_histogram6_accumulate(
        5.0f, 2.0f, 6.0f, histogram_boundaries,
        histogram_sums, histogram_counts, 0.5f));
    assert(histogram_sums[0] == 1.5f && histogram_counts[0] == 1.0f);
    assert(gomore_primitives_weighted_histogram6_accumulate(
        50.0f, 2.0f, 6.0f, histogram_boundaries,
        histogram_sums, histogram_counts, 0.5f));
    assert(histogram_sums[5] == 3.0f && histogram_counts[5] == 1.0f);
    assert(gomore_primitives_weighted_histogram6_accumulate(
        15.0f, 0.0f, 6.0f, histogram_boundaries,
        histogram_sums, histogram_counts, 0.5f));
    assert(histogram_counts[1] == 1.0f);

    gomore_primitives_speed_smoother speed_smoother;
    assert(sizeof(speed_smoother) == 32u);
    memset(&speed_smoother, 0, sizeof(speed_smoother));
    speed_smoother.enabled = 1u;
    speed_smoother.maximum_raw_rise = 5.0f;
    speed_smoother.maximum_raw_fall = 4.0f;
    speed_smoother.maximum_output_rise = 3.0f;
    speed_smoother.maximum_output_fall = 2.0f;
    float speed_output = 0.0f;
    uint8_t speed_flag = 0u;
    assert(gomore_primitives_speed_smoother_update(
               &speed_smoother, 10.0f, 1000u,
               &speed_output, &speed_flag) == UINT32_MAX);
    assert(speed_output == 10.0f && speed_flag == 1u &&
           speed_smoother.sample_count == 1u);
    assert(gomore_primitives_speed_smoother_update(
               &speed_smoother, 20.0f, 1000u,
               &speed_output, &speed_flag) == UINT32_MAX);
    assert(speed_output == 13.0f && speed_flag == 1u &&
           speed_smoother.sample_count == 2u);
    assert(gomore_primitives_speed_smoother_update(
               &speed_smoother, 40.0f, 1000u,
               &speed_output, &speed_flag) == UINT32_MAX);
    assert(speed_output == 16.0f && speed_flag == 1u &&
           speed_smoother.previous_raw_input == 40.0f);
    speed_smoother.enabled = 2u;
    assert(gomore_primitives_speed_smoother_update(
               &speed_smoother, 10.0f, 1000u,
               &speed_output, &speed_flag) == UINT32_C(0x1389));
    speed_smoother.enabled = 1u;
    assert(gomore_primitives_speed_smoother_update(
               &speed_smoother, 10.0f, 700u,
               &speed_output, &speed_flag) == UINT32_MAX);
    assert(gomore_primitives_speed_smoother_update(
               &speed_smoother, 10.0f, 1300u,
               &speed_output, &speed_flag) == UINT32_MAX);
    assert(gomore_primitives_speed_smoother_update(
               &speed_smoother, 10.0f, 699u,
               &speed_output, &speed_flag) == UINT32_C(0x138A));
    speed_smoother.maximum_raw_rise = 0.0f;
    assert(gomore_primitives_speed_smoother_update(
               &speed_smoother, 10.0f, 1000u,
               &speed_output, &speed_flag) == UINT32_C(0x138B));

    gomore_primitives_speed_smoother ema_smoother;
    memset(&ema_smoother, 0, sizeof(ema_smoother));
    ema_smoother.enabled = 1u;
    ema_smoother.maximum_raw_rise = 100.0f;
    ema_smoother.maximum_raw_fall = 100.0f;
    ema_smoother.maximum_output_rise = 100.0f;
    ema_smoother.maximum_output_fall = 100.0f;
    for (size_t index = 0u; index < 10u; ++index) {
        assert(gomore_primitives_speed_smoother_update(
                   &ema_smoother, 10.0f, 1000u,
                   &speed_output, &speed_flag) == UINT32_MAX);
    }
    assert(ema_smoother.sample_count == 10u && speed_output == 10.0f);
    assert(gomore_primitives_speed_smoother_update(
               &ema_smoother, 20.0f, 1000u,
               &speed_output, &speed_flag) == UINT32_MAX);
    assert(speed_output == 13.5f && ema_smoother.sample_count == 10u &&
           speed_flag == 0u);

    float speed_gate_history[6] = {
        0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f,
    };
    assert(gomore_primitives_speed_gate(
               14.0f, 0.0f, speed_gate_history, 0, 0u) == 14.0f);
    assert(speed_gate_history[0] == 14.0f);
    memset(speed_gate_history, 0, sizeof(speed_gate_history));
    assert(gomore_primitives_speed_gate(
               15.0f, 0.0f, speed_gate_history, 0, 0u) == 0.0f);
    assert(speed_gate_history[0] == 0.0f);
    assert(gomore_primitives_speed_gate(
               16.0f, 0.0f, speed_gate_history, 0, 0u) == 0.0f);
    assert(speed_gate_history[0] == 0.0f);

    const float quiet_nan = bits_float(UINT32_C(0x7FC00000));
    const float nan_gate = gomore_primitives_speed_gate(
        quiet_nan, 0.0f, speed_gate_history, 0, 0u);
    assert(float_bits(nan_gate) == UINT32_C(0x7FC00000) &&
           float_bits(speed_gate_history[0]) == UINT32_C(0x7FC00000));

    const float unflagged_history[6] = {
        20.0f, 20.0f, 20.0f, 20.0f, 0.0f, 0.0f,
    };
    memcpy(speed_gate_history, unflagged_history,
           sizeof(speed_gate_history));
    assert(gomore_primitives_speed_gate(
               40.0f, 20.0f, speed_gate_history, 4, 0u) == 24.0f);
    assert(speed_gate_history[0] == 20.0f &&
           speed_gate_history[3] == 40.0f);
    memcpy(speed_gate_history, unflagged_history,
           sizeof(speed_gate_history));
    assert(gomore_primitives_speed_gate(
               40.0f, 22.0f, speed_gate_history, 4, 0u) == 40.0f);

    memset(speed_gate_history, 0, sizeof(speed_gate_history));
    assert(gomore_primitives_speed_gate(
               10.0f, 0.0f, speed_gate_history, 0,
               UINT32_C(0x0004)) == 10.0f);
    assert(speed_gate_history[0] == 5.5f);
    const float flagged_history[6] = {
        5.5f, 7.0f, 8.0f, 9.0f, 10.0f, 0.0f,
    };
    memcpy(speed_gate_history, flagged_history, sizeof(speed_gate_history));
    const float flagged_rolling = gomore_primitives_speed_gate(
        40.0f, 10.0f, speed_gate_history, 5, UINT32_C(0x0400));
    assert(flagged_rolling == 40.0f);
    assert(speed_gate_history[4] ==
           10.0f + (5.5f -
                    10.0f * bits_float(UINT32_C(0x3EEAA64C))));
    const float flagged_select_history[6] = {
        30.0f, 30.0f, 30.0f, 30.0f, 30.0f, 0.0f,
    };
    memcpy(speed_gate_history, flagged_select_history,
           sizeof(speed_gate_history));
    assert(float_bits(gomore_primitives_speed_gate(
               40.0f, 10.0f, speed_gate_history, 5,
               UINT32_C(0x1444))) == UINT32_C(0x41D68E55));

    assert(gomore_primitives_speed_gate(
               9.0f, 1.0f, NULL, 0, 0u) == 9.0f);
    assert(gomore_primitives_speed_gate(
               9.0f, 1.0f, speed_gate_history, -1, 0u) == 9.0f);

    const float source[3] = {1.0f, -2.0f, 4.0f};
    float scaled[3] = {0.0f, 0.0f, 0.0f};
    assert(gomore_primitives_scale(0.5f, source, scaled, 3u));
    assert(scaled[0] == 0.5f && scaled[1] == -1.0f && scaled[2] == 2.0f);
    assert(gomore_primitives_scale(1.0f, NULL, NULL, 0u));

    memset(bytes, UINT8_C(0xA5), sizeof(bytes));
    assert(gomore_primitives_callback_record_initialize(
        bytes, sizeof(bytes), UINT32_C(0x12345678), UINT32_C(0xAABBCCDD)));
    assert(bytes[0xB4] == 0u);
    assert(bytes[0xB8] == UINT8_C(0x78) && bytes[0xBB] == UINT8_C(0x12));
    assert(bytes[0xBC] == UINT8_C(0xDD) && bytes[0xBF] == UINT8_C(0xAA));

    float sortable[5] = {9.0f, 4.0f, 1.0f, 3.0f, 8.0f};
    assert(gomore_primitives_sort_float_subrange(
        sortable, 5u, 1u, 3u, sort_values, compare_float));
    assert(sortable[0] == 9.0f && sortable[1] == 1.0f &&
           sortable[2] == 3.0f && sortable[3] == 4.0f &&
           sortable[4] == 8.0f);
    assert(!gomore_primitives_sort_float_subrange(
        sortable, 5u, 3u, 1u, sort_values, compare_float));

    const float candidates[4] = {-2.0f, 1.0f, 7.0f, 3.0f};
    assert(gomore_primitives_max_index(candidates, 4u, max_index) == 2);
    uint32_t words[2] = {1u, 2u};
    assert(gomore_primitives_set_second_word(words, 9u));
    assert(words[0] == 1u && words[1] == 9u);
    assert(gomore_primitives_size_736() == UINT32_C(0x2E0));
    assert(gomore_primitives_size_14816() == UINT32_C(0x39E0));
    assert(gomore_primitives_return_zero() == 0u);
    gomore_primitives_noop_76500();
    gomore_primitives_noop_578c8();
    gomore_primitives_noop_49e58();
    gomore_primitives_noop_91080();
    assert(gomore_primitives_set_second_word(words, 11u));
    assert(words[1] == 11u);
    assert(gomore_primitives_return_zero() == 0u);
    uint8_t leaf_record[0x80];
    memset(leaf_record, UINT8_C(0xA5), sizeof(leaf_record));
    assert(gomore_primitives_clear_72(leaf_record, sizeof(leaf_record)));
    for (size_t index = 0u; index < 0x48u; ++index) {
        assert(leaf_record[index] == 0u);
    }
    uint32_t first_word = 3u;
    assert(gomore_primitives_store_first_word(&first_word, 7u));
    assert(first_word == 7u);
    uint8_t first_byte = UINT8_C(0xA5);
    assert(gomore_primitives_clear_first_byte(&first_byte));
    assert(first_byte == 0u);
    uint32_t triplet[3] = {0u, 0u, 0u};
    assert(gomore_primitives_triplet_initialize(triplet, 4u, 8u, 12u));
    assert(triplet[0] == 8u && triplet[1] == 4u && triplet[2] == 12u);
    assert(gomore_primitives_interpolate(0.25f, 10.0f, 2.0f) == 4.0f);
    assert(gomore_primitives_byte_in_70_100(70u));
    assert(gomore_primitives_byte_in_70_100(100u));
    assert(!gomore_primitives_byte_in_70_100(69u));
    assert(!gomore_primitives_byte_in_70_100(101u));
    uint8_t large_state[1001];
    memset(large_state, 0, sizeof(large_state));
    large_state[1000] = 1u;
    assert(gomore_primitives_clear_flag_1000(
        large_state, sizeof(large_state)));
    assert(large_state[1000] == 0u);
    const float cubic = gomore_primitives_cubic_scale(2.0f);
    assert(cubic > 1.1798f && cubic < 1.1800f);
    assert(gomore_primitives_linear_evaluate(3.0f, 2.0f, 1.0f) == 7.0f);
    uint8_t window5[5] = {1u, 2u, 3u, 4u, 5u};
    assert(gomore_primitives_shift_u8_window5(window5, 9u));
    assert(window5[0] == 2u && window5[3] == 5u && window5[4] == 9u);
    assert(gomore_primitives_nullable_strlen(NULL) == 0u);
    assert(gomore_primitives_nullable_strlen("ring") == 4u);
    assert(gomore_primitives_u16_in_30000_50000(UINT16_C(30000)));
    assert(gomore_primitives_u16_in_30000_50000(UINT16_C(50000)));
    assert(!gomore_primitives_u16_in_30000_50000(UINT16_C(29999)));
    assert(!gomore_primitives_u16_in_30000_50000(UINT16_C(50001)));
    memset(leaf_record, UINT8_C(0xA5), sizeof(leaf_record));
    assert(gomore_primitives_clear_36(leaf_record, sizeof(leaf_record)));
    assert(leaf_record[0] == 0u && leaf_record[0x23] == 0u &&
           leaf_record[0x24] == UINT8_C(0xA5));
    memset(leaf_record, UINT8_C(0xA5), sizeof(leaf_record));
    assert(gomore_primitives_step_record_initialize(
        leaf_record, sizeof(leaf_record)));
    assert(leaf_record[0] == 0u && leaf_record[0x10] == 5u &&
           leaf_record[0x14] == 0u);
    memset(leaf_record, UINT8_C(0xA5), sizeof(leaf_record));
    assert(gomore_primitives_clear_124(leaf_record, sizeof(leaf_record)));
    assert(leaf_record[0] == 0u && leaf_record[0x7B] == 0u &&
           leaf_record[0x7C] == UINT8_C(0xA5));
    memset(leaf_record, UINT8_C(0xA5), sizeof(leaf_record));
    assert(gomore_primitives_float_state_initialize(
        leaf_record, sizeof(leaf_record)));
    assert(leaf_record[0x7C] == UINT8_C(0xF4) &&
           leaf_record[0x7F] == UINT8_C(0x3C));
    assert(gomore_primitives_half_to_float_bits(UINT16_C(0x3C00)) ==
           UINT32_C(0x3F800000));
    uint32_t float_word = 0u;
    assert(gomore_primitives_store_half_as_float_bits(
        &float_word, UINT16_C(0x4000)));
    assert(float_word == UINT32_C(0x40000000));
    assert(!gomore_primitives_clear_72(NULL, 0x48u));
    assert(!gomore_primitives_store_half_as_float_bits(NULL, 0u));

    const int16_t signed_values[5] = {-3, -2, 7, -1, 9};
    assert(gomore_primitives_find_next_nonnegative_i16(
               signed_values, 5u, 0u) == 2);
    assert(gomore_primitives_find_next_nonnegative_i16(
               signed_values, 5u, 3u) == -1);
    assert(gomore_primitives_find_next_nonnegative_i16(
               signed_values, 5u, 4u) == -1);
    uint8_t paired_windows[10] = {1u, 2u, 3u, 4u, 5u,
                                  6u, 7u, 8u, 9u, 10u};
    assert(gomore_primitives_shift_two_u8_windows5(
        &paired_windows[0], &paired_windows[5], 11u, 12u));
    assert(paired_windows[0] == 2u && paired_windows[4] == 11u &&
           paired_windows[5] == 7u && paired_windows[9] == 12u);
    assert(gomore_primitives_normalized_position(15.0f, 20.0f, 10.0f) ==
           0.5f);
    assert(gomore_primitives_normalized_position(15.0f, 10.0f, 10.0f) ==
           0.0f);
    uint8_t packed[0x2D0];
    memset(packed, 0, sizeof(packed));
    packed[0] = UINT8_C(0xE4);
    uint8_t packed_value = UINT8_C(0xFF);
    assert(gomore_primitives_packed_2bit_get(
        packed, sizeof(packed), 0u, &packed_value) && packed_value == 0u);
    assert(gomore_primitives_packed_2bit_get(
        packed, sizeof(packed), 3u, &packed_value) && packed_value == 3u);
    assert(gomore_primitives_packed_2bit_get(
        packed, sizeof(packed), UINT32_C(0xB43), &packed_value) &&
           packed_value == 3u);
    assert(!gomore_primitives_packed_2bit_get(packed, 0u, 0u,
                                             &packed_value));

    uint8_t energy_state[0x5C];
    memset(energy_state, UINT8_C(0xA5), sizeof(energy_state));
    assert(gomore_primitives_energy_state_reset(
        energy_state, sizeof(energy_state)));
    assert(energy_state[0x0C] == 0u && energy_state[0x18] == 0u &&
           energy_state[0x14] == 0u && energy_state[0x17] == 0x3Fu &&
           energy_state[0x4C] == 0u && energy_state[0x57] == 0u &&
           energy_state[0x58] == UINT8_C(0xA5));
    uint8_t default_state[0x404];
    memset(default_state, UINT8_C(0xA5), sizeof(default_state));
    assert(gomore_primitives_large_default_state_initialize(
        default_state, sizeof(default_state)));
    assert(default_state[0] == 0u && default_state[0x3F8] == 3u &&
           default_state[0x3FC] == 0u && default_state[0x3FF] == 0x3Fu &&
           default_state[0x403] == 0u);
    float milli_values[2] = {1.0f, -2.0f};
    assert(gomore_primitives_scale_milli(milli_values, 2u));
    assert(milli_values[0] == bits_float(UINT32_C(0x3A83126F)) &&
           milli_values[1] == -2.0f * bits_float(UINT32_C(0x3A83126F)));
    memset(energy_state, UINT8_C(0xA5), sizeof(energy_state));
    assert(gomore_primitives_sps_state_reset(
        energy_state, sizeof(energy_state)));
    assert(energy_state[0x0C] == 0u && energy_state[0x14] == 0u &&
           energy_state[0x30] == 0u && energy_state[0x54] == 0u &&
           energy_state[0x20] == UINT8_C(0xA5));

    uint8_t status_history[10] = {1u, 2u, 3u, 4u, 5u,
                                  6u, 7u, 8u, 9u, 10u};
    uint8_t status_output[3] = {0u, 0u, 0u};
    assert(gomore_primitives_shift_status_windows(status_history,
                                                  status_output));
    assert(status_history[0] == 2u && status_history[4] == 0xFEu &&
           status_history[5] == 7u && status_history[9] == 0u);
    assert(status_output[0] == 0xFFu && status_output[1] == 0xFEu &&
           status_output[2] == 0u);
    const uint8_t labels[5] = {4u, 7u, 4u, 4u, 1u};
    assert(gomore_primitives_count_byte_plus_one(labels, 5u, 4u) == 4u);
    assert(gomore_primitives_count_byte_plus_one(NULL, 0u, 4u) == 1u);

    uint8_t accumulator[14];
    memset(accumulator, 0, sizeof(accumulator));
    const float initial_second = 2.0f;
    const float initial_first = 4.0f;
    memcpy(&accumulator[4], &initial_second, sizeof(initial_second));
    memcpy(&accumulator[8], &initial_first, sizeof(initial_first));
    accumulator[12] = UINT8_C(0xFF);
    accumulator[13] = UINT8_C(0xFF);
    assert(gomore_primitives_accumulate_pair(
        accumulator, sizeof(accumulator), 1.5f, 0.5f));
    float accumulated = 0.0f;
    memcpy(&accumulated, &accumulator[4], sizeof(accumulated));
    assert(accumulated == 2.5f);
    memcpy(&accumulated, &accumulator[8], sizeof(accumulated));
    assert(accumulated == 5.5f);
    assert(accumulator[12] == 0u && accumulator[13] == 0u);

    uint8_t selected_state[0x65];
    memset(selected_state, UINT8_C(0xA5), sizeof(selected_state));
    assert(gomore_primitives_selected_state_reset(
        selected_state, sizeof(selected_state)));
    assert(selected_state[0] == UINT8_C(0xA5) && selected_state[1] == 0u &&
           selected_state[4] == 0u && selected_state[5] == UINT8_C(0xA5) &&
           selected_state[0x0C] == 0u && selected_state[0x63] == 0u &&
           selected_state[0x64] == UINT8_C(0xA5));
    uint8_t pattern[17];
    memset(pattern, UINT8_C(0xA5), sizeof(pattern));
    assert(gomore_primitives_pattern17_initialize(pattern, sizeof(pattern)));
    assert(pattern[0] == 0xFEu && pattern[4] == 0xFEu &&
           pattern[5] == 0u && pattern[14] == 0u &&
           pattern[15] == 1u && pattern[16] == 1u);
    memset(energy_state, UINT8_C(0xA5), sizeof(energy_state));
    assert(gomore_primitives_energy_record_initialize(
        energy_state, sizeof(energy_state), UINT32_C(0x12345678)));
    assert(energy_state[0] == 1u && energy_state[0x14] == 0u &&
           energy_state[0x17] == 0x3Fu && energy_state[0x58] == 0x78u &&
           energy_state[0x5B] == 0x12u);
    uint8_t initialized_large_state[0x33C];
    memset(initialized_large_state, UINT8_C(0xA5),
           sizeof(initialized_large_state));
    void *active_record = NULL;
    assert(gomore_primitives_large_state_initialize(
        initialized_large_state, sizeof(initialized_large_state),
        UINT32_C(0x89ABCDEF), &active_record));
    assert(active_record == initialized_large_state &&
           initialized_large_state[0] == 0u &&
           initialized_large_state[0x338] == 0xEFu &&
           initialized_large_state[0x33B] == 0x89u);

    uint32_t binding_record[5] = {0u, 0u, 0u, 0u, 0u};
    const uint8_t low24[3] = {UINT8_C(0x56), UINT8_C(0x34),
                              UINT8_C(0x12)};
    assert(gomore_primitives_low24_binding_initialize(
        binding_record, low24, UINT32_C(0x10203040)));
    assert(binding_record[0] == UINT32_C(0x00123456) &&
           binding_record[1] == UINT32_C(0x10203040));
    assert(gomore_primitives_pack4_binding_initialize(
        binding_record, 0x11u, 0x22u, 0x33u, 0x44u,
        UINT32_C(0x50607080)));
    assert(binding_record[0] == UINT32_C(0x44332211) &&
           binding_record[1] == UINT32_C(0x50607080));
    const int16_t mean_i16[4] = {-5, 3, 7, 3};
    assert(gomore_primitives_i16_mean(mean_i16, 4u) == 2);
    assert(gomore_primitives_i16_mean(NULL, 0u) == 0);
    float floor_value = 8.0f;
    assert(gomore_primitives_float_floor_update(3.0f, &floor_value));
    assert(floor_value == 8.0f);
    assert(gomore_primitives_float_floor_update(10.0f, &floor_value));
    assert(floor_value == 10.0f);
    uint8_t selector_state[17];
    memset(selector_state, 0, sizeof(selector_state));
    int8_t selector = 1;
    assert(gomore_primitives_validate_selector(
        selector_state, sizeof(selector_state), &selector));
    assert(selector == -1);
    selector_state[16] = 1u;
    selector = 2;
    assert(gomore_primitives_validate_selector(
        selector_state, sizeof(selector_state), &selector));
    assert(selector == 2);
    assert(gomore_primitives_nullable_compare(
               (const uint8_t *)"ring", (const uint8_t *)"ring") == 0);
    assert(gomore_primitives_nullable_compare(
               (const uint8_t *)"rind", (const uint8_t *)"ring") < 0);
    assert(gomore_primitives_nullable_compare(NULL,
               (const uint8_t *)"ring") == 0);
    uint32_t strided[7] = {0u, 1u, 2u, 3u, 4u, 5u, 6u};
    size_t compact_count = 0u;
    assert(gomore_primitives_compact_u32_stride(
        strided, 7u, 7u, 3u, &compact_count));
    assert(compact_count == 3u && strided[0] == 0u &&
           strided[1] == 3u && strided[2] == 6u);

    uint8_t status_source[0x56];
    uint8_t status_destination[0x44];
    memset(status_source, 0, sizeof(status_source));
    memset(status_destination, UINT8_C(0xA5), sizeof(status_destination));
    status_source[0x52] = 0x34u;
    status_source[0x53] = 0x12u;
    assert(gomore_primitives_status_record_extract(
               status_source, sizeof(status_source), status_destination,
               sizeof(status_destination)) == 0);
    assert(status_destination[0] == UINT8_C(0xA5) &&
           status_destination[0x42] == 0x34u &&
           status_destination[0x43] == 0x12u);
    status_source[0x54] = 1u;
    assert(gomore_primitives_status_record_extract(
               status_source, sizeof(status_source), status_destination,
               sizeof(status_destination)) == -1008);
    for (size_t index = 0u; index < sizeof(status_destination); ++index) {
        assert(status_destination[index] == 0u);
    }
    assert(gomore_primitives_half_span_initialize(
        binding_record, UINT16_C(0x3C00), UINT32_C(0x20000000)));
    assert(binding_record[0] == UINT32_C(0x3F800000) &&
           binding_record[1] == UINT32_C(0x20000000) &&
           binding_record[4] == UINT32_C(0x2000003C));
    uint8_t parameter_init_state[0x20FC];
    memset(parameter_init_state, UINT8_C(0xA5),
           sizeof(parameter_init_state));
    assert(gomore_primitives_parameter_state_initialize(
        parameter_init_state, sizeof(parameter_init_state),
        UINT32_C(0x78563412)));
    assert(parameter_init_state[0] == 0u &&
           parameter_init_state[0x20F5] == 0u &&
           parameter_init_state[0x20F8] == 0x12u &&
           parameter_init_state[0x20FB] == 0x78u);
    const int32_t encoded_values[3] = {
        INT32_C(0x40E00000), INT32_C(0x40E00001), 0};
    assert(gomore_primitives_count_encoded_i32(encoded_values, 3u) == 2u);
    assert(gomore_primitives_scaled_ratio(2.8f, 2.0f) == 100.0f);
    assert(gomore_primitives_scaled_ratio(1.0f, 0.0f) == 0.0f);
    assert(gomore_primitives_piecewise_clamp_70_100(0) == 70u);
    assert(gomore_primitives_piecewise_clamp_70_100(96) == 96u);
    assert(gomore_primitives_piecewise_clamp_70_100(110) == 100u);
    uint8_t missing_window[0x3E];
    memset(missing_window, UINT8_C(0xA5), sizeof(missing_window));
    assert(gomore_primitives_missing_window_initialize(
        missing_window, sizeof(missing_window)));
    assert(missing_window[0] == 0u && missing_window[0x37] == 0u &&
           missing_window[0x38] == 0xFFu &&
           missing_window[0x3D] == 0xFFu);
    uint8_t modulo_bytes[0xB40];
    memset(modulo_bytes, 0, sizeof(modulo_bytes));
    modulo_bytes[0] = 0xE4u;
    modulo_bytes[0xB3F] = 0x5Au;
    assert(gomore_primitives_modulo_value_get(
        modulo_bytes, sizeof(modulo_bytes), 3u, true, &packed_value));
    assert(packed_value == 3u);
    assert(gomore_primitives_modulo_value_get(
        modulo_bytes, sizeof(modulo_bytes), UINT32_C(0x167F), false,
        &packed_value));
    assert(packed_value == 0x5Au);
    uint8_t mode8_state[0x26E];
    memset(mode8_state, UINT8_C(0xA5), sizeof(mode8_state));
    assert(gomore_primitives_mode8_state_initialize(
        mode8_state, sizeof(mode8_state)));
    assert(mode8_state[0] == 8u && mode8_state[1] == 0u &&
           mode8_state[0x26D] == 0u);

    const float pair_left[2] = {8.0f, 2.0f};
    const float pair_right[2] = {1.0f, 3.0f};
    float pair_output[2] = {0.0f, 0.0f};
    assert(gomore_primitives_vector_pair_transform(
        2.0f, 6.0f, pair_left, pair_right, pair_output));
    assert(pair_output[0] == 8.0f && pair_output[1] == 5.0f);
    uint8_t short_record[17];
    const uint8_t short_payload[3] = {7u, 8u, 9u};
    assert(gomore_primitives_encode_short_record(
        short_record, short_payload, sizeof(short_payload)));
    assert(short_record[0] == 7u && short_record[3] == 0u &&
           short_record[16] == 0x83u);
    float milli_accumulator[4] = {1.0f, 2.0f, 3.0f, 4.0f};
    const int8_t milli_increments[4] = {1, -2, 3, -4};
    assert(gomore_primitives_accumulate_i8x4_milli(
        milli_accumulator, milli_increments));
    assert(milli_accumulator[0] ==
           1.0f + bits_float(UINT32_C(0x3C23D70A)));
    uint8_t presence_record[0x19];
    memset(presence_record, 0, sizeof(presence_record));
    presence_record[0x14] = 1u;
    assert(gomore_primitives_shift_presence_history(
               presence_record, sizeof(presence_record), 1u) == 0u);
    memset(presence_record, 0, sizeof(presence_record));
    presence_record[0x16] = 1u;
    presence_record[0x17] = 0u;
    assert(gomore_primitives_shift_presence_history(
               presence_record, sizeof(presence_record), 1u) == 2u);
    float progression[5] = {-1.0f, -1.0f, -1.0f, -1.0f, -1.0f};
    assert(gomore_primitives_fill_float_progression(
        progression, 5u, 1u, 4u, 2.0f, 0.5f));
    assert(progression[0] == -1.0f && progression[1] == 2.0f &&
           progression[3] == 3.0f && progression[4] == -1.0f);
    uint8_t compact_time_record[8] = {
        15u, 0u, 240u, 0u, 0u, 0u, 23u, 23u};
    assert(gomore_primitives_time_record_valid(
        compact_time_record, sizeof(compact_time_record)));
    compact_time_record[6] = 24u;
    assert(!gomore_primitives_time_record_valid(
        compact_time_record, sizeof(compact_time_record)));
    const float maxima[4] = {-2.0f, 5.0f, 5.0f, 3.0f};
    assert(gomore_primitives_float_argmax_range(maxima, 4u, 0u, 4u) == 1u);
    assert(gomore_primitives_float_argmax_above_floor(maxima, 4u) == 1);
    const int16_t range_values[3] = {-100, 20, 300};
    assert(gomore_primitives_i16_range(range_values, 3u) == 400);
    memset(packed, 0, sizeof(packed));
    assert(gomore_primitives_packed_2bit_set(
        packed, sizeof(packed), 2u, 3u));
    assert(packed[0] == 0x30u);
    const float rational = gomore_primitives_rational_transform(1.0f, 1.0f);
    assert(rational > 0.32f && rational < 0.34f);
    const int16_t differences_i16[4] = {1, 4, 2, 8};
    assert(gomore_primitives_i16_mean_absolute_difference(
               differences_i16, 4u) == 3);
    const uint16_t nearby[3] = {1000u, 1200u, 1300u};
    assert(gomore_primitives_u16_all_within_300(nearby, 3u, 1000u));
    const int16_t nonzero_mean[8] = {0, 2, 0, 4, 0, 6, 0, 8};
    assert(gomore_primitives_nonzero_i16_mean8(nonzero_mean) == 5.0f);
    uint8_t circular_values[18];
    float circular_weights[18];
    for (size_t index = 0u; index < 18u; ++index) {
        circular_values[index] = (uint8_t)index;
        circular_weights[index] = index == 0u ? 1.0f : 0.0f;
    }
    assert(gomore_primitives_circular_u8_dot18(
               circular_values, 60u, circular_weights) == 2.0f);
    float motion_gate_weights[18];
    for (size_t index = 0u; index < 18u; ++index) {
        motion_gate_weights[index] = 1.0f;
    }
    gomore_primitives_motion_gate_state motion_gate = {
        .pending_sum = 20.0f,
        .pending_count = 2,
        .last_bucket = 7u,
    };
    gomore_primitives_motion_gate_output motion_gate_output = {
        .score = 99.0f,
    };
    assert(gomore_primitives_motion_gate_accumulate(
        &motion_gate, 1u, 30u, 4.0f, motion_gate_weights,
        &motion_gate_output));
    assert(motion_gate.buckets[0] == 10u &&
           motion_gate_output.score == 10.0f &&
           motion_gate_output.positive_after_bias &&
           motion_gate_output.updated && motion_gate_output.valid &&
           motion_gate.pending_sum == 4.0f &&
           motion_gate.pending_count == 1);
    motion_gate_output.score = 99.0f;
    motion_gate_output.positive_after_bias = false;
    assert(gomore_primitives_motion_gate_accumulate(
        &motion_gate, 0u, 30u, -1.0f, motion_gate_weights,
        &motion_gate_output));
    assert(!motion_gate_output.updated && motion_gate_output.valid &&
           motion_gate_output.score == 99.0f &&
           !motion_gate_output.positive_after_bias &&
           motion_gate.pending_sum == 4.0f &&
           motion_gate.pending_count == 1);
    memset(&motion_gate, 0, sizeof(motion_gate));
    motion_gate.pending_sum = 4.0f;
    motion_gate.pending_count = 1;
    assert(gomore_primitives_motion_gate_accumulate(
        &motion_gate, 61u, 90u, -1.0f, motion_gate_weights,
        &motion_gate_output));
    assert(motion_gate.buckets[0] == 4u &&
           motion_gate.buckets[1] == 4u &&
           motion_gate.buckets[2] == 4u &&
           motion_gate_output.score == 12.0f &&
           motion_gate.pending_sum == 0.0f &&
           motion_gate.pending_count == 0);
    memset(&motion_gate, UINT8_C(0xA5), sizeof(motion_gate));
    motion_gate.pending_sum = 12.0f;
    motion_gate.pending_count = 2;
    motion_gate.last_bucket = 6u;
    assert(gomore_primitives_motion_gate_accumulate(
        &motion_gate, 540u, 600u, 5.0f, motion_gate_weights,
        &motion_gate_output));
    for (size_t index = 0u; index < 18u; ++index) {
        assert(motion_gate.buckets[index] == 0u);
    }
    assert(motion_gate.last_bucket == 0u &&
           motion_gate_output.score == 0.0f &&
           motion_gate_output.positive_after_bias &&
           motion_gate_output.updated && motion_gate_output.valid &&
           motion_gate.pending_sum == 5.0f &&
           motion_gate.pending_count == 1);
    memset(&motion_gate, 0, sizeof(motion_gate));
    motion_gate.pending_sum = 300.0f;
    motion_gate.pending_count = 1;
    assert(gomore_primitives_motion_gate_accumulate(
        &motion_gate, 1u, 30u, -1.0f, motion_gate_weights,
        &motion_gate_output));
    assert(motion_gate.buckets[0] == UINT8_MAX);
    memset(&motion_gate, 0, sizeof(motion_gate));
    motion_gate.pending_sum = -10.0f;
    motion_gate.pending_count = 1;
    assert(gomore_primitives_motion_gate_accumulate(
        &motion_gate, 1u, 30u, -1.0f, motion_gate_weights,
        &motion_gate_output));
    assert(motion_gate.buckets[0] == 0u);
    const gomore_primitives_motion_gate_state saved_motion_gate = motion_gate;
    motion_gate_output.score = 77.0f;
    assert(!gomore_primitives_motion_gate_accumulate(
        &motion_gate, 31u, 30u, 1.0f, motion_gate_weights,
        &motion_gate_output));
    assert(memcmp(&motion_gate, &saved_motion_gate,
                  sizeof(motion_gate)) == 0 &&
           motion_gate_output.score == 77.0f);
    const float peak_values[9] = {
        0.0f, 2.0f, 0.0f, 1.0f, 4.0f, 1.0f, 0.0f, 6.0f, 0.0f,
    };
    float peak_output[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    peak_sqrt_calls = 0u;
    assert(gomore_primitives_peak_statistics(
        peak_values, 9u, 1u, peak_output,
        square_power_fixture, peak_sqrt_fixture));
    assert(peak_output[0] == 3.0f && peak_output[1] == 0.0f &&
           peak_output[2] == 4.0f &&
           peak_output[3] > 2.66f && peak_output[3] < 2.67f &&
           peak_sqrt_calls == 2u &&
           peak_sqrt_inputs[0] > 2.66f &&
           peak_sqrt_inputs[0] < 2.67f &&
           peak_sqrt_inputs[1] == 0.0f);
    const float single_peak[3] = {0.0f, 5.0f, 0.0f};
    peak_sqrt_calls = 0u;
    assert(gomore_primitives_peak_statistics(
        single_peak, 3u, 1u, peak_output,
        square_power_fixture, peak_sqrt_fixture));
    assert(peak_output[0] == -1.0f && peak_output[1] == -1.0f &&
           peak_output[2] == 5.0f && peak_output[3] == 0.0f &&
           peak_sqrt_calls == 1u);
    const float saved_peak_output[4] = {
        peak_output[0], peak_output[1], peak_output[2], peak_output[3],
    };
    assert(!gomore_primitives_peak_statistics(
        single_peak, 3u, 2u, peak_output,
        square_power_fixture, peak_sqrt_fixture));
    assert(memcmp(peak_output, saved_peak_output,
                  sizeof(peak_output)) == 0);
    const int32_t direction_values[7] = {0, 1, 3, 2, 0, -3, -1};
    gomore_primitives_direction_change_output direction_output;
    assert(gomore_primitives_direction_change_statistics(
        10.0f, 0.1f, GOMORE_PRIMITIVES_DIFFERENCE_INT32,
        direction_values, 6u, &direction_output));
    assert(direction_output.direction_changes == 2 &&
           direction_output.above_threshold_changes == 1 &&
           direction_output.normalized_variation > 0.316f &&
           direction_output.normalized_variation < 0.317f &&
           direction_output.average_completed_run == 2.5f);
    const int16_t monotonic_i16[7] = {0, 1, 2, 3, 4, 5, 6};
    assert(gomore_primitives_direction_change_statistics(
        0.0f, 1.0f, GOMORE_PRIMITIVES_DIFFERENCE_INT16,
        monotonic_i16, 6u, &direction_output));
    assert(direction_output.direction_changes == 0 &&
           direction_output.above_threshold_changes == 0 &&
           direction_output.normalized_variation == 0.0f &&
           direction_output.average_completed_run == 0.0f);
    const float short_differences[6] = {0.0f};
    assert(gomore_primitives_direction_change_statistics(
        1.0f, 1.0f, GOMORE_PRIMITIVES_DIFFERENCE_FLOAT32,
        short_differences, 5u, &direction_output));
    assert(direction_output.direction_changes == -1 &&
           direction_output.above_threshold_changes == -1 &&
           direction_output.normalized_variation == -1.0f &&
           direction_output.average_completed_run == -1.0f);
    const gomore_primitives_direction_change_output saved_direction =
        direction_output;
    assert(!gomore_primitives_direction_change_statistics(
        1.0f, 1.0f, (gomore_primitives_difference_mode)3,
        direction_values, 6u, &direction_output));
    assert(memcmp(&direction_output, &saved_direction,
                  sizeof(direction_output)) == 0);
    gomore_primitives_dormant_heart_rate_filter_state heart_rate_filter = {
        .enabled = 1u,
    };
    int32_t heart_rate_output[2] = {77, 88};
    assert(gomore_primitives_dormant_heart_rate_filter_update(
               &heart_rate_filter, 72, heart_rate_output, 699u) ==
           INT32_C(0x1771));
    assert(heart_rate_output[0] == 77 && heart_rate_output[1] == 72);
    heart_rate_filter.enabled = 0u;
    assert(gomore_primitives_dormant_heart_rate_filter_update(
               &heart_rate_filter, 72, heart_rate_output, 1000u) ==
           INT32_C(0x1772));
    heart_rate_filter.enabled = 1u;
    assert(gomore_primitives_dormant_heart_rate_filter_update(
               &heart_rate_filter, 0, heart_rate_output, 1000u) ==
           INT32_C(0x1775));
    assert(heart_rate_output[0] == 0 && heart_rate_filter.enabled == 1u);
    memset(&heart_rate_filter, 0, sizeof(heart_rate_filter));
    heart_rate_filter.enabled = 1u;
    assert(gomore_primitives_dormant_heart_rate_filter_update(
               &heart_rate_filter, 60, heart_rate_output, 1000u) == 1);
    assert(gomore_primitives_dormant_heart_rate_filter_update(
               &heart_rate_filter, 67, heart_rate_output, 1000u) == 1);
    assert(heart_rate_filter.last_effective_input == 66);
    memset(&heart_rate_filter, 0, sizeof(heart_rate_filter));
    heart_rate_filter.enabled = 1u;
    assert(gomore_primitives_dormant_heart_rate_filter_update(
               &heart_rate_filter, 60, heart_rate_output, 1000u) == 1);
    assert(gomore_primitives_dormant_heart_rate_filter_update(
               &heart_rate_filter, 52, heart_rate_output, 1000u) == 1);
    assert(heart_rate_filter.last_effective_input == 53);
    memset(&heart_rate_filter, 0, sizeof(heart_rate_filter));
    heart_rate_filter.enabled = 1u;
    const int32_t averaging_inputs[4] = {60, 61, 62, 63};
    const int32_t averaging_outputs[4] = {60, 60, 60, 61};
    for (size_t index = 0u; index < 4u; ++index) {
        assert(gomore_primitives_dormant_heart_rate_filter_update(
                   &heart_rate_filter, averaging_inputs[index],
                   heart_rate_output, 1000u) == 1);
        assert(heart_rate_output[0] == averaging_outputs[index]);
    }
    const int32_t missing_statuses[5] = {
        1, 1, 1, INT32_C(0x1773), INT32_C(0x1775),
    };
    for (size_t index = 0u; index < 5u; ++index) {
        assert(gomore_primitives_dormant_heart_rate_filter_update(
                   &heart_rate_filter, 0, heart_rate_output, 1000u) ==
               missing_statuses[index]);
    }
    memset(&heart_rate_filter, 0, sizeof(heart_rate_filter));
    heart_rate_filter.enabled = 1u;
    int32_t unchanged_status = 0;
    for (size_t index = 0u; index < 22u; ++index) {
        unchanged_status =
            gomore_primitives_dormant_heart_rate_filter_update(
                &heart_rate_filter, 60, heart_rate_output, 1000u);
        if (index == 19u) {
            assert(unchanged_status == 1);
        }
    }
    assert(unchanged_status == INT32_C(0x1774));
    memset(&heart_rate_filter, 0, sizeof(heart_rate_filter));
    heart_rate_filter.enabled = 1u;
    for (int32_t value = 60; value <= 81; ++value) {
        assert(gomore_primitives_dormant_heart_rate_filter_update(
                   &heart_rate_filter, value,
                   heart_rate_output, 1000u) == 1);
    }
    assert(heart_rate_output[0] == 71 &&
           heart_rate_filter.history_count == 19u &&
           heart_rate_filter.history[18] == 81.0f &&
           heart_rate_filter.history[19] == 81.0f);
    const int16_t score_channel0[5] = {1, 2, 3, 4, 5};
    const int16_t score_channel1[5] = {2, 2, 2, 2, 2};
    const int16_t score_channel2[5] = {3, 3, 3, 3, 3};
    const int16_t score_channel3[5] = {10, 10, 10, 10, 10};
    const int16_t score_channel4[5] = {5, 5, 5, 5, 5};
    const int16_t score_channel5[5] = {8, 8, 8, 8, 8};
    gomore_primitives_six_channel_linear_model score_model = {
        .weights = {1.0f, 1.0f, 1.0f, 1.0f, 1.0f, 1.0f},
        .bias = 1.0f,
        .scale = 2.0f,
        .empty_window_value = 10.0f,
        .minimum_output = -100,
    };
    int16_t six_channel_score = 0;
    assert(gomore_primitives_six_channel_ring_score(
        score_channel0, score_channel1, score_channel2,
        score_channel3, score_channel4, score_channel5,
        5u, 1u, 3u, &score_model, &six_channel_score));
    assert(six_channel_score == 64);
    assert(gomore_primitives_six_channel_ring_score(
        score_channel0, score_channel1, score_channel2,
        score_channel3, score_channel4, score_channel5,
        5u, 1u, 0u, &score_model, &six_channel_score));
    assert(six_channel_score == 22);
    score_model.scale = 2000.0f;
    assert(gomore_primitives_six_channel_ring_score(
        score_channel0, score_channel1, score_channel2,
        score_channel3, score_channel4, score_channel5,
        5u, 1u, 3u, &score_model, &six_channel_score));
    assert(six_channel_score == 32000);
    for (size_t index = 0u; index < 6u; ++index) {
        score_model.weights[index] = -1.0f;
    }
    score_model.bias = 0.0f;
    score_model.scale = 1.0f;
    score_model.minimum_output = -10;
    assert(gomore_primitives_six_channel_ring_score(
        score_channel0, score_channel1, score_channel2,
        score_channel3, score_channel4, score_channel5,
        5u, 1u, 3u, &score_model, &six_channel_score));
    assert(six_channel_score == -10);
    const int16_t saved_six_channel_score = six_channel_score;
    assert(!gomore_primitives_six_channel_ring_score(
        score_channel0, score_channel1, score_channel2,
        score_channel3, score_channel4, score_channel5,
        5u, 1u, 6u, &score_model, &six_channel_score));
    assert(six_channel_score == saved_six_channel_score);
    const uint8_t filtered_values[5] = {0u, 9u, 10u, 11u, 30u};
    assert(gomore_primitives_filtered_u8_mean(
               filtered_values, 5u, 10, 1) == 10);
    const float complex_left[2] = {2.0f, 3.0f};
    const float complex_right[2] = {4.0f, 5.0f};
    assert(gomore_primitives_complex_multiply(
        complex_left, complex_right, pair_output));
    assert(pair_output[0] == -7.0f && pair_output[1] == 22.0f);
    float complex_power[2] = {3.0f, 4.0f};
    assert(gomore_primitives_complex_power(
        2.0f, complex_power, complex_atan2_fixture,
        complex_sqrt_fixture, complex_log_fixture,
        complex_exp_fixture, complex_cos_fixture, complex_sin_fixture));
    assert(complex_power[0] == 7.5f && complex_power[1] == 2.5f);
    const float quantized_magnitude_values[10] = {
        0.01f, 0.1f, 3.0f, -0.1f, 0.0f,
        0.0f, 0.0f, 0.0f, 0.0f, 0.0f,
    };
    assert(gomore_primitives_sleep_quantized_magnitude10(
        quantized_magnitude_values, positive_floor_fixture) == 141.0f);
    const float range_center_values[4] = {3.0f, -1.0f, 5.0f, 2.0f};
    float range_center = 0.0f;
    float range_span = 0.0f;
    assert(gomore_primitives_range_center_span(
        range_center_values, 4u, 0u, &range_center, &range_span));
    assert(range_center == -1.0f && range_span == 6.0f);
    assert(gomore_primitives_range_center_span(
        range_center_values, 4u, 1u, &range_center, &range_span));
    assert(range_center == 2.0f && range_span == 3.0f);
    const gomore_primitives_linear_model3 linear_model = {
        .centers = {1.0f, 2.0f, 3.0f},
        .divisors = {2.0f, 4.0f, 5.0f},
        .weights = {10.0f, 20.0f, 30.0f},
        .bias = 7.0f,
    };
    const float linear_values[3] = {3.0f, 6.0f, 8.0f};
    assert(gomore_primitives_linear_model3_evaluate(
        linear_values, &linear_model) == 67.0f);
    uint8_t repair_stages[11] = {
        1u, 1u, 3u, 3u, 3u, 0u, 1u, 0u, 3u, 3u, 1u,
    };
    const uint8_t repaired_stages[11] = {
        1u, 1u, 2u, 2u, 2u, 0u, 2u, 2u, 3u, 3u, 1u,
    };
    assert(gomore_primitives_sleep_repair_deep_awake_transition(
        repair_stages, sizeof(repair_stages)));
    assert(memcmp(repair_stages, repaired_stages,
                  sizeof(repair_stages)) == 0);
    uint8_t circular_feature_state[0x224];
    memset(circular_feature_state, UINT8_C(0xA5),
           sizeof(circular_feature_state));
    circular_feature_state[0x52] = 3u;
    assert(gomore_primitives_circular_feature_slot_advance(
        circular_feature_state, sizeof(circular_feature_state)));
    const size_t circular_feature_bases[9] = {
        0x02u, 0x204u, 0x214u, 0x12u, 0x22u,
        0x32u, 0x42u, 0x1E4u, 0x1F4u,
    };
    for (size_t index = 0u; index < 9u; ++index) {
        assert(circular_feature_state[circular_feature_bases[index] + 6u]
                   == 0u &&
               circular_feature_state[circular_feature_bases[index] + 7u]
                   == 0u);
    }
    assert(circular_feature_state[0x52] == 4u);
    const int16_t circular_mean_first[8] = {
        1, 2, 3, 4, 5, 6, 7, 8,
    };
    const int16_t circular_mean_second[8] = {
        2, 4, 6, 8, 10, 12, 14, 16,
    };
    const int16_t circular_mean_third[8] = {
        3, 6, 9, 12, 15, 18, 21, 24,
    };
    int16_t circular_means[3] = {0, 0, 0};
    assert(gomore_primitives_circular_i16_mean3(
        circular_mean_first, circular_mean_second, circular_mean_third,
        8u, 1u, 3u, circular_means));
    assert(circular_means[0] == 5 && circular_means[1] == 10 &&
           circular_means[2] == 16);
    const int16_t fill_mean_values[8] = {
        10, 0, 30, 40, 50, 60, 70, 80,
    };
    assert(gomore_primitives_circular_positive_fill_mean(
        fill_mean_values, 8u, 3u, 1u, 3u) == 16);
    const int16_t crossing_baseline_ring[8] = {
        1500, 0, 0, 0, 0, 0, 0, 0,
    };
    uint16_t crossing_samples[200] = {0u};
    float crossing_mode2 = -1.0f;
    float crossing_mode1 = -1.0f;
    crossing_estimate_calls = 0u;
    crossing_estimate_values[0] = 60.0f;
    crossing_estimate_values[1] = bits_float(UINT32_C(0x43710000));
    assert(gomore_primitives_locomotion_crossing_wrapper(
        crossing_baseline_ring, 0, crossing_samples,
        200u, &crossing_mode2, &crossing_mode1,
        locomotion_crossing_estimate));
    assert(crossing_estimate_calls == 2u &&
           crossing_estimate_modes[0] == 2u &&
           crossing_estimate_modes[1] == 1u &&
           crossing_estimate_baselines[0] == 1500 &&
           crossing_estimate_baselines[1] == 1500 &&
           crossing_mode2 == 60.0f && crossing_mode1 == 0.0f);
    crossing_estimate_calls = 0u;
    crossing_estimate_values[0] = 240.0f;
    crossing_estimate_values[1] = 120.0f;
    assert(gomore_primitives_locomotion_crossing_wrapper(
        crossing_baseline_ring, 0, crossing_samples,
        200u, &crossing_mode2, &crossing_mode1,
        locomotion_crossing_estimate));
    assert(crossing_mode2 == 240.0f && crossing_mode1 == 120.0f);
    crossing_estimate_calls = 0u;
    crossing_mode2 = -1.0f;
    assert(!gomore_primitives_locomotion_crossing_wrapper(
        crossing_baseline_ring, 8, crossing_samples,
        200u, &crossing_mode2, &crossing_mode1,
        locomotion_crossing_estimate));
    assert(crossing_estimate_calls == 0u && crossing_mode2 == -1.0f);
    for (size_t index = 0u; index < 200u; ++index) {
        crossing_samples[index] = (index / 5u) % 2u == 0u
            ? UINT16_C(700) : UINT16_C(2300);
    }
    assert(gomore_primitives_locomotion_crossing_period_estimate(
        crossing_samples, 200u, 1500, 2u, &crossing_mode2));
    assert(gomore_primitives_locomotion_crossing_period_estimate(
        crossing_samples, 200u, 1500, 1u, &crossing_mode1));
    assert(load_u32_fixture((const uint8_t *)&crossing_mode2) ==
           UINT32_C(0x43160000));
    assert(load_u32_fixture((const uint8_t *)&crossing_mode1) ==
           UINT32_C(0x42C8F4FA));
    memset(crossing_samples, 0, sizeof(crossing_samples));
    for (size_t index = 0u; index < 200u; ++index) {
        crossing_samples[index] = UINT16_C(1500);
    }
    assert(gomore_primitives_locomotion_crossing_period_estimate(
        crossing_samples, 200u, 1500, 2u, &crossing_mode2));
    assert(crossing_mode2 == 0.0f);
    assert(!gomore_primitives_locomotion_crossing_period_estimate(
        crossing_samples, 199u, 1500, 2u, &crossing_mode2));
    assert(!gomore_primitives_locomotion_crossing_period_estimate(
        crossing_samples, 200u, 1500, 3u, &crossing_mode2));
    int8_t final_sleep_stages[66];
    memset(final_sleep_stages, 1, 64u);
    final_sleep_stages[64] = 2;
    final_sleep_stages[65] = 2;
    const gomore_primitives_final_sleep_record final_sleep_source = {
        .wire_type = 1u,
        .start_timestamp = -5,
        .end_timestamp = (int32_t)UINT32_C(0x12345678),
        .stages = final_sleep_stages,
        .stage_count = 66u,
        .efficiency = 0.876f,
        .score = 93.9f,
        .rem_fraction = 0.20f,
        .light_fraction = 0.50f,
        .deep_fraction = 0.15f,
        .total_minutes = 6.5f,
        .wake_minutes = 1.25f,
        .rem_minutes = 2.5f,
        .light_minutes = 1.5f,
        .deep_minutes = 1.25f,
        .body_temperature = 37u,
    };
    uint8_t serialized_sleep[35];
    memset(serialized_sleep, UINT8_C(0xA5), sizeof(serialized_sleep));
    size_t serialized_sleep_length = 0u;
    assert(gomore_primitives_final_sleep_record_serialize(
        &final_sleep_source, serialized_sleep, sizeof(serialized_sleep),
        &serialized_sleep_length));
    const uint8_t expected_sleep_header[32] = {
        1u, 87u, 93u, 0u, 15u, 20u, 50u, 15u,
        37u, 0u, 0u, 0u, 0u, 0u, 0u, 0u,
        0x78u, 0x56u, 0x34u, 0x12u, 0x86u, 0x01u, 75u, 0u,
        150u, 0u, 90u, 0u, 75u, 0u, 3u, 0u,
    };
    assert(serialized_sleep_length == sizeof(serialized_sleep) &&
           memcmp(serialized_sleep, expected_sleep_header,
                  sizeof(expected_sleep_header)) == 0 &&
           serialized_sleep[32] == 0xFDu &&
           serialized_sleep[33] == 0x05u &&
           serialized_sleep[34] == 0x0Au);
    uint8_t short_sleep[32];
    memset(short_sleep, UINT8_C(0xA5), sizeof(short_sleep));
    gomore_primitives_final_sleep_record short_sleep_source =
        final_sleep_source;
    short_sleep_source.wire_type = 2u;
    short_sleep_source.start_timestamp = 7;
    serialized_sleep_length = 0u;
    assert(gomore_primitives_final_sleep_record_serialize(
        &short_sleep_source, short_sleep, sizeof(short_sleep),
        &serialized_sleep_length));
    assert(serialized_sleep_length == sizeof(short_sleep) &&
           short_sleep[0] == 2u && short_sleep[0x0C] == 7u &&
           short_sleep[0x10] == 0x78u && short_sleep[0x1E] == 0u);
    serialized_sleep_length = 123u;
    serialized_sleep[0] = UINT8_C(0xA5);
    assert(!gomore_primitives_final_sleep_record_serialize(
        &final_sleep_source, serialized_sleep, sizeof(serialized_sleep) - 1u,
        &serialized_sleep_length));
    assert(serialized_sleep_length == 123u &&
           serialized_sleep[0] == UINT8_C(0xA5));
    uint8_t final_sleep_packed[720];
    memset(final_sleep_packed, 0, sizeof(final_sleep_packed));
    for (uint32_t epoch = 30u; epoch < 60u; ++epoch) {
        assert(gomore_primitives_packed_2bit_set(
            final_sleep_packed, sizeof(final_sleep_packed), epoch, 2u));
    }
    const uint8_t final_sleep_configuration[11] = {0u};
    gomore_primitives_sleep_interval_result final_sleep_interval;
    memset(&final_sleep_interval, 0, sizeof(final_sleep_interval));
    final_sleep_interval.start = 900u;
    final_sleep_interval.end = 1800u;
    final_sleep_interval.flags = UINT8_C(0x18);
    int8_t final_sleep_build_stages[64];
    memset(final_sleep_build_stages, -1,
           sizeof(final_sleep_build_stages));
    gomore_primitives_final_sleep_build_output final_sleep_build = {
        .stages = final_sleep_build_stages,
        .stage_capacity = sizeof(final_sleep_build_stages),
    };
    int32_t final_sleep_build_status = 99;
    g_final_sleep_refine_calls = 0u;
    assert(gomore_primitives_final_sleep_build(
        final_sleep_packed, sizeof(final_sleep_packed), 1800u,
        final_sleep_configuration, &final_sleep_interval,
        final_sleep_refine_fixture, sleep_tanh_zero_fixture,
        sleep_power_fixture, &final_sleep_build,
        &final_sleep_build_status));
    assert(final_sleep_build_status == 0 &&
           final_sleep_build.wire_type == 1u &&
           final_sleep_build.start_timestamp == 900u &&
           final_sleep_build.end_timestamp == 1800u &&
           final_sleep_build.stage_count == 30u &&
           final_sleep_build.statistics.interval_minutes == 15.0f &&
           final_sleep_build.statistics.non_awake_minutes == 15.0f &&
           final_sleep_build.statistics.efficiency == 1.0f &&
           final_sleep_build.statistics.light_fraction == 1.0f &&
           final_sleep_build.statistics.light_minutes == 15.0f &&
           final_sleep_build.score >= 0.0f &&
           g_final_sleep_refine_calls == 1u);
    for (size_t index = 0u; index < 30u; ++index) {
        assert(final_sleep_build_stages[index] == 2);
    }
    for (uint32_t epoch = 30u; epoch < 34u; ++epoch) {
        assert(gomore_primitives_packed_2bit_set(
            final_sleep_packed, sizeof(final_sleep_packed), epoch, 0u));
    }
    assert(gomore_primitives_final_sleep_build(
        final_sleep_packed, sizeof(final_sleep_packed), 1800u,
        final_sleep_configuration, &final_sleep_interval,
        final_sleep_refine_fixture, sleep_tanh_zero_fixture,
        sleep_power_fixture, &final_sleep_build,
        &final_sleep_build_status));
    assert(final_sleep_build.start_timestamp == 840u &&
           final_sleep_build.stage_count == 32u &&
           final_sleep_build_stages[0] == 0 &&
           final_sleep_build_stages[1] == 0 &&
           g_final_sleep_refine_calls == 2u);
    final_sleep_interval.flags = UINT8_C(0x08);
    assert(gomore_primitives_final_sleep_build(
        final_sleep_packed, sizeof(final_sleep_packed), 1800u,
        final_sleep_configuration, &final_sleep_interval,
        final_sleep_refine_fixture, sleep_tanh_zero_fixture,
        sleep_power_fixture, &final_sleep_build,
        &final_sleep_build_status));
    assert(final_sleep_build_status == 0 &&
           final_sleep_build.wire_type == 2u &&
           final_sleep_build.stage_count == 0u &&
           g_final_sleep_refine_calls == 2u);
    final_sleep_interval.flags = 0u;
    assert(gomore_primitives_final_sleep_build(
        final_sleep_packed, sizeof(final_sleep_packed), 1800u,
        final_sleep_configuration, &final_sleep_interval,
        final_sleep_refine_fixture, sleep_tanh_zero_fixture,
        sleep_power_fixture, &final_sleep_build,
        &final_sleep_build_status));
    assert(final_sleep_build_status == -1 &&
           final_sleep_build.stages == final_sleep_build_stages &&
           final_sleep_build.stage_capacity ==
               sizeof(final_sleep_build_stages));
    float moving_extrema_values[250];
    for (size_t index = 0u; index < 250u; ++index) {
        const int32_t phase = (int32_t)(index % 20u);
        moving_extrema_values[index] =
            (float)(10 - (phase > 10 ? phase - 10 : 10 - phase));
    }
    uint8_t moving_maxima[GOMORE_PRIMITIVES_EXTREMA_CAPACITY];
    uint8_t moving_minima[GOMORE_PRIMITIVES_EXTREMA_CAPACITY];
    memset(moving_maxima, UINT8_C(0xA5), sizeof(moving_maxima));
    memset(moving_minima, UINT8_C(0xA5), sizeof(moving_minima));
    size_t moving_maxima_count = 99u;
    size_t moving_minima_count = 99u;
    assert(gomore_primitives_moving_average_extrema_indices(
        moving_extrema_values, 250u, 25u, 6u,
        moving_maxima, sizeof(moving_maxima), &moving_maxima_count,
        moving_minima, sizeof(moving_minima), &moving_minima_count));
    assert(moving_maxima_count == 12u && moving_minima_count == 13u);
    for (size_t index = 0u; index < moving_maxima_count; ++index) {
        assert(moving_maxima[index] == (uint8_t)(10u + index * 20u));
    }
    for (size_t index = 0u; index < moving_minima_count; ++index) {
        assert(moving_minima[index] == (uint8_t)(index * 20u));
    }
    for (size_t index = 0u; index < 250u; ++index) {
        moving_extrema_values[index] =
            (index % 10u) < 5u ? 1.0f : -1.0f;
    }
    memset(moving_maxima, UINT8_C(0xA5), sizeof(moving_maxima));
    memset(moving_minima, UINT8_C(0x5A), sizeof(moving_minima));
    moving_maxima_count = 99u;
    moving_minima_count = 99u;
    assert(!gomore_primitives_moving_average_extrema_indices(
        moving_extrema_values, 250u, 25u, 6u,
        moving_maxima, sizeof(moving_maxima), &moving_maxima_count,
        moving_minima, sizeof(moving_minima), &moving_minima_count));
    assert(moving_maxima_count == 0u && moving_minima_count == 0u &&
           moving_maxima[0] == UINT8_C(0xA5) &&
           moving_minima[0] == UINT8_C(0x5A));
    moving_maxima_count = 99u;
    moving_minima_count = 99u;
    assert(!gomore_primitives_moving_average_extrema_indices(
        moving_extrema_values, 250u, 25u, 6u,
        moving_maxima, GOMORE_PRIMITIVES_EXTREMA_CAPACITY - 1u,
        &moving_maxima_count,
        moving_minima, sizeof(moving_minima), &moving_minima_count));
    assert(moving_maxima_count == 99u && moving_minima_count == 99u);
    uint8_t locomotion_preprocess_state[0x26E];
    uint8_t locomotion_preprocess_output[0x3E];
    float locomotion_axis_x[25];
    float locomotion_axis_y[25];
    float locomotion_axis_z[25];
    for (size_t index = 0u; index < 25u; ++index) {
        locomotion_axis_x[index] = 3.0f;
        locomotion_axis_y[index] = 4.0f;
        locomotion_axis_z[index] = 0.0f;
    }
    const float *const locomotion_axes[3] = {
        locomotion_axis_x, locomotion_axis_y, locomotion_axis_z,
    };
    memset(locomotion_preprocess_state, 0,
           sizeof(locomotion_preprocess_state));
    for (size_t slot = 0u; slot < 8u; ++slot) {
        locomotion_preprocess_state[0x32u + slot * 2u] = 1u;
    }
    memset(locomotion_preprocess_output, 0,
           sizeof(locomotion_preprocess_output));
    g_locomotion_preprocess_classify_calls = 0u;
    assert(gomore_primitives_locomotion_window_preprocess(
        locomotion_preprocess_state,
        sizeof(locomotion_preprocess_state), 1u,
        locomotion_axes, false,
        locomotion_preprocess_output,
        sizeof(locomotion_preprocess_output),
        locomotion_preprocess_sqrt,
        locomotion_preprocess_classify) == 0);
    assert(g_locomotion_preprocess_classify_calls == 1u &&
           locomotion_preprocess_output[0] == UINT8_C(0x77) &&
           locomotion_preprocess_state[0] == 0u &&
           locomotion_preprocess_state[0x52u] == 1u &&
           load_u16_fixture(&locomotion_preprocess_state[0x32u]) == 5u);
    for (size_t index = 0u; index < 25u; ++index) {
        assert(load_u16_fixture(
            &locomotion_preprocess_state[
                0x54u + (175u + index) * 2u]) == 5u);
    }

    memset(locomotion_preprocess_state, 0,
           sizeof(locomotion_preprocess_state));
    memset(locomotion_preprocess_output, 0,
           sizeof(locomotion_preprocess_output));
    assert(gomore_primitives_locomotion_window_preprocess(
        locomotion_preprocess_state,
        sizeof(locomotion_preprocess_state), 1u,
        NULL, true,
        locomotion_preprocess_output,
        sizeof(locomotion_preprocess_output),
        locomotion_preprocess_sqrt,
        locomotion_preprocess_classify) == 1);
    assert(locomotion_preprocess_state[0x52u] == 1u &&
           locomotion_preprocess_output[0x38u] == UINT8_C(0xFF) &&
           locomotion_preprocess_output[0x3Du] == UINT8_C(0xFF));
    memset(locomotion_preprocess_state, UINT8_C(0xA5),
           sizeof(locomotion_preprocess_state));
    assert(gomore_primitives_locomotion_window_preprocess(
        locomotion_preprocess_state,
        sizeof(locomotion_preprocess_state), 9u,
        locomotion_axes, false,
        locomotion_preprocess_output,
        sizeof(locomotion_preprocess_output),
        locomotion_preprocess_sqrt,
        locomotion_preprocess_classify) == 1);
    assert(locomotion_preprocess_state[0] == 8u &&
           locomotion_preprocess_state[0x52u] == 0u &&
           locomotion_preprocess_state[0x26Du] == 0u);
    locomotion_preprocess_output[0] = UINT8_C(0xA5);
    assert(gomore_primitives_locomotion_window_preprocess(
        locomotion_preprocess_state, 0x26Du, 1u,
        locomotion_axes, false,
        locomotion_preprocess_output,
        sizeof(locomotion_preprocess_output),
        locomotion_preprocess_sqrt,
        locomotion_preprocess_classify) == -1);
    assert(locomotion_preprocess_output[0] == UINT8_C(0xA5));
    const gomore_primitives_output_lifecycle_providers
        output_lifecycle_providers = {
            .refresh_input = output_lifecycle_refresh,
            .update_engine = output_lifecycle_update,
            .result_ready = output_lifecycle_ready,
            .consume_activity = output_lifecycle_activity,
            .publish_sleep_status = output_lifecycle_status,
            .publish_final_sleep = output_lifecycle_final,
            .authorize = output_lifecycle_authorize,
        };
    gomore_primitives_output_lifecycle_state output_lifecycle_state = {
        .active_slot_mask = UINT8_C(0x09),
        .activity = {UINT32_C(0x11223344), UINT32_C(0x55667788)},
        .sleep_lifecycle_flags = UINT8_C(0x0C),
        .stage_ppg_request = 1,
        .previous_stage_ppg_request = false,
        .accelerometer_pending = true,
        .optical_pending = true,
    };
    memset(&g_output_lifecycle_trace, 0,
           sizeof(g_output_lifecycle_trace));
    g_output_lifecycle_trace.ready = true;
    g_output_lifecycle_trace.final_available = true;
    assert(gomore_primitives_output_lifecycle_dispatch(
        &g_output_lifecycle_trace, &output_lifecycle_state,
        &output_lifecycle_providers));
    assert(g_output_lifecycle_trace.order_length == 7u &&
           memcmp(g_output_lifecycle_trace.order, "RUQASFG", 7u) == 0 &&
           g_output_lifecycle_trace.sleep_status == 0u &&
           g_output_lifecycle_trace.authorization_slot == 4u &&
           g_output_lifecycle_trace.authorization_enabled &&
           g_output_lifecycle_trace.activity[0] == UINT32_C(0x11223344) &&
           g_output_lifecycle_trace.activity[1] == UINT32_C(0x55667788) &&
           !output_lifecycle_state.accelerometer_pending &&
           !output_lifecycle_state.optical_pending);
    memset(&g_output_lifecycle_trace, 0,
           sizeof(g_output_lifecycle_trace));
    g_output_lifecycle_trace.ready = true;
    g_output_lifecycle_trace.final_available = true;
    output_lifecycle_state.active_slot_mask = UINT8_C(0x08);
    output_lifecycle_state.sleep_lifecycle_flags = UINT8_C(0x0E);
    output_lifecycle_state.stage_ppg_request = 0;
    output_lifecycle_state.previous_stage_ppg_request = true;
    output_lifecycle_state.accelerometer_pending = true;
    output_lifecycle_state.optical_pending = true;
    assert(gomore_primitives_output_lifecycle_dispatch(
        &g_output_lifecycle_trace, &output_lifecycle_state,
        &output_lifecycle_providers));
    assert(g_output_lifecycle_trace.order_length == 5u &&
           memcmp(g_output_lifecycle_trace.order, "RUQSG", 5u) == 0 &&
           g_output_lifecycle_trace.sleep_status == 1u &&
           !g_output_lifecycle_trace.authorization_enabled);
    memset(&g_output_lifecycle_trace, 0,
           sizeof(g_output_lifecycle_trace));
    output_lifecycle_state.accelerometer_pending = true;
    output_lifecycle_state.optical_pending = true;
    assert(gomore_primitives_output_lifecycle_dispatch(
        &g_output_lifecycle_trace, &output_lifecycle_state,
        &output_lifecycle_providers));
    assert(g_output_lifecycle_trace.order_length == 3u &&
           memcmp(g_output_lifecycle_trace.order, "RUQ", 3u) == 0 &&
           output_lifecycle_state.accelerometer_pending &&
           output_lifecycle_state.optical_pending);
    memset(&g_output_lifecycle_trace, 0,
           sizeof(g_output_lifecycle_trace));
    g_output_lifecycle_trace.ready = true;
    output_lifecycle_state.sleep_lifecycle_flags = UINT8_C(0x0C);
    output_lifecycle_state.stage_ppg_request = 1;
    output_lifecycle_state.previous_stage_ppg_request = false;
    assert(gomore_primitives_output_lifecycle_dispatch(
        &g_output_lifecycle_trace, &output_lifecycle_state,
        &output_lifecycle_providers));
    assert(g_output_lifecycle_trace.order_length == 5u &&
           memcmp(g_output_lifecycle_trace.order, "RUQSF", 5u) == 0);
    assert(!gomore_primitives_output_lifecycle_dispatch(
        &g_output_lifecycle_trace, &output_lifecycle_state, NULL));
    const gomore_primitives_authorization_providers
        authorization_providers = {
            .context = &g_authorization_trace,
            .register_stream = authorization_register,
            .unregister_stream = authorization_unregister,
            .create_timer = authorization_timer_create,
            .delete_timer = authorization_timer_delete,
        };
    gomore_primitives_authorization_state authorization_state;
    memset(&authorization_state, 0, sizeof(authorization_state));
    authorization_state.initialized = true;
    authorization_state.idle_timer_handle = (uintptr_t)99;
    authorization_state.auxiliary_handles[0] = (uintptr_t)55;
    authorization_state.auxiliary_handles[1] = (uintptr_t)66;
    authorization_state.heart_rate_state = 72.0f;
    authorization_state.hrv_state = 1u;
    authorization_state.slots[0].flags = UINT8_C(0x1E);
    authorization_state.slots[0].on_enable = authorization_slot_enable;
    authorization_state.slots[0].on_disable = authorization_slot_disable;
    authorization_state.slots[0].context = &g_authorization_trace;
    memset(&g_authorization_trace, 0, sizeof(g_authorization_trace));
    g_authorization_trace.next_handle = (uintptr_t)100;
    assert(gomore_primitives_authorization_dispatch(
        &authorization_state, 0u, true, &authorization_providers));
    assert(g_authorization_trace.order_length == 6u &&
           memcmp(g_authorization_trace.order, "ABCDEX", 6u) == 0 &&
           (authorization_state.slots[0].flags & UINT8_C(1)) != 0u &&
           authorization_state.stream_handles[0] == (uintptr_t)101 &&
           authorization_state.stream_handles[3] == (uintptr_t)104 &&
           authorization_state.idle_timer_handle == (uintptr_t)0);
    memset(g_authorization_trace.order, 0,
           sizeof(g_authorization_trace.order));
    g_authorization_trace.order_length = 0u;
    assert(gomore_primitives_authorization_dispatch(
        &authorization_state, 0u, false, &authorization_providers));
    assert(g_authorization_trace.order_length == 6u &&
           memcmp(g_authorization_trace.order, "abcdDC", 6u) == 0 &&
           (authorization_state.slots[0].flags & UINT8_C(1)) == 0u &&
           authorization_state.stream_handles[0] == (uintptr_t)0 &&
           authorization_state.stream_handles[3] == (uintptr_t)0 &&
           authorization_state.idle_timer_handle == (uintptr_t)105 &&
           authorization_state.auxiliary_handles[0] == (uintptr_t)0 &&
           authorization_state.auxiliary_handles[1] == (uintptr_t)0 &&
           authorization_state.heart_rate_state == 0.0f &&
           authorization_state.hrv_state == 0u);
    g_authorization_trace.order_length = 0u;
    assert(!gomore_primitives_authorization_dispatch(
        &authorization_state, 0u, false, &authorization_providers));
    assert(g_authorization_trace.order_length == 0u);

    authorization_state.slots[0].flags = UINT8_C(0x04);
    authorization_state.slots[1].flags = UINT8_C(0x05);
    authorization_state.stream_handles[1] = (uintptr_t)77;
    g_authorization_trace.order_length = 0u;
    assert(gomore_primitives_authorization_dispatch(
        &authorization_state, 0u, true, &authorization_providers));
    assert(g_authorization_trace.order_length == 2u &&
           memcmp(g_authorization_trace.order, "EX", 2u) == 0 &&
           authorization_state.stream_handles[1] == (uintptr_t)77 &&
           authorization_state.idle_timer_handle == (uintptr_t)0);
    g_authorization_trace.order_length = 0u;
    assert(gomore_primitives_authorization_dispatch(
        &authorization_state, 0u, false, &authorization_providers));
    assert(g_authorization_trace.order_length == 1u &&
           g_authorization_trace.order[0] == 'D' &&
           authorization_state.stream_handles[1] == (uintptr_t)77 &&
           authorization_state.idle_timer_handle == (uintptr_t)0);
    authorization_state.initialized = false;
    assert(!gomore_primitives_authorization_dispatch(
        &authorization_state, 1u, false, &authorization_providers));
    memset(&g_final_sleep_trace, 0, sizeof(g_final_sleep_trace));
    g_final_sleep_trace.lookup_result = g_final_sleep_trace.record;
    g_final_sleep_trace.record[0] = 2u;
    store_u32_fixture(&g_final_sleep_trace.record[0x0C],
                      UINT32_C(0x11223344));
    store_u32_fixture(&g_final_sleep_trace.record[0x10],
                      UINT32_C(0x55667788));
    g_final_sleep_trace.record[0x1E] = 2u;
    g_final_sleep_trace.modes[0] = 0u;
    g_final_sleep_trace.modes[1] = 4u;
    g_final_sleep_trace.modes[2] = 2u;
    g_final_sleep_trace.accepted = true;
    const gomore_primitives_final_sleep_providers final_sleep_providers = {
        final_sleep_lookup,
        final_sleep_log_modes,
        final_sleep_structured_log,
        final_sleep_secondary_log,
        final_sleep_accept,
        final_sleep_publish,
        final_sleep_release,
    };
    bool final_sleep_published = false;
    uint16_t final_sleep_length = 0u;
    assert(gomore_primitives_final_sleep_record_publish(
        true, UINT32_C(0x12345678), &final_sleep_providers,
        &final_sleep_published, &final_sleep_length));
    assert(final_sleep_published && final_sleep_length == 34u &&
           g_final_sleep_trace.lookup_binding == UINT32_C(0x12345678) &&
           g_final_sleep_trace.publish_topic == 0x0Du &&
           g_final_sleep_trace.publish_payload == g_final_sleep_trace.record &&
           g_final_sleep_trace.publish_length == 34u &&
           g_final_sleep_trace.structured_logs == 1u &&
           g_final_sleep_trace.secondary_logs == 1u &&
           g_final_sleep_trace.order_length == 9u &&
           memcmp(g_final_sleep_trace.order, "LMMSMNAPF", 9u) == 0);

    memset(g_final_sleep_trace.order, 0, sizeof(g_final_sleep_trace.order));
    g_final_sleep_trace.order_length = 0u;
    g_final_sleep_trace.mode_index = 0u;
    memset(g_final_sleep_trace.modes, 0, sizeof(g_final_sleep_trace.modes));
    g_final_sleep_trace.accepted = false;
    final_sleep_published = true;
    final_sleep_length = UINT16_MAX;
    assert(gomore_primitives_final_sleep_record_publish(
        true, 1u, &final_sleep_providers,
        &final_sleep_published, &final_sleep_length));
    assert(!final_sleep_published && final_sleep_length == 0u &&
           g_final_sleep_trace.order_length == 6u &&
           memcmp(g_final_sleep_trace.order, "LMMMAF", 6u) == 0);

    memset(g_final_sleep_trace.order, 0, sizeof(g_final_sleep_trace.order));
    g_final_sleep_trace.order_length = 0u;
    g_final_sleep_trace.mode_index = 0u;
    g_final_sleep_trace.accepted = true;
    g_final_sleep_trace.record[0x1E] = 0xE0u;
    g_final_sleep_trace.record[0x1F] = 0xFFu;
    assert(gomore_primitives_final_sleep_record_publish(
        true, 1u, &final_sleep_providers,
        &final_sleep_published, &final_sleep_length));
    assert(final_sleep_published && final_sleep_length == 0u &&
           g_final_sleep_trace.publish_length == 0u &&
           g_final_sleep_trace.order[g_final_sleep_trace.order_length - 1u]
               == 'F');

    g_final_sleep_trace.order_length = 0u;
    final_sleep_published = true;
    final_sleep_length = UINT16_MAX;
    assert(gomore_primitives_final_sleep_record_publish(
        false, 1u, &final_sleep_providers,
        &final_sleep_published, &final_sleep_length));
    assert(!final_sleep_published && final_sleep_length == 0u &&
           g_final_sleep_trace.order_length == 0u);
    assert(!gomore_primitives_final_sleep_record_publish(
        true, 1u, NULL, &final_sleep_published, &final_sleep_length));
    const gomore_primitives_sleep_force_wake_providers
        sleep_force_wake_providers = {
            .allocate = sleep_force_wake_allocate,
            .release = sleep_force_wake_release,
            .prepare = sleep_force_wake_prepare,
            .set_mode = sleep_force_wake_set_mode,
            .dispatch = sleep_force_wake_dispatch,
            .publish = sleep_force_wake_publish,
        };
    gomore_primitives_sleep_force_wake_status sleep_force_wake_status =
        GOMORE_PRIMITIVES_SLEEP_FORCE_WAKE_RECORD_ALLOCATION_FAILED;
    memset(&g_sleep_force_wake_trace, 0,
           sizeof(g_sleep_force_wake_trace));
    memset(g_sleep_force_wake_trace.record, UINT8_C(0xA5),
           sizeof(g_sleep_force_wake_trace.record));
    memset(g_sleep_force_wake_trace.timeline, UINT8_C(0xA5),
           sizeof(g_sleep_force_wake_trace.timeline));
    g_sleep_force_wake_trace.publish_requested = true;
    assert(gomore_primitives_sleep_force_wake(
        true, &sleep_force_wake_providers, &sleep_force_wake_status));
    assert(sleep_force_wake_status ==
               GOMORE_PRIMITIVES_SLEEP_FORCE_WAKE_COMPLETE &&
           g_sleep_force_wake_trace.allocation_calls == 2u &&
           g_sleep_force_wake_trace.prepare_calls == 1u &&
           g_sleep_force_wake_trace.mode_calls == 1u &&
           g_sleep_force_wake_trace.dispatch_calls == 1u &&
           g_sleep_force_wake_trace.publish_calls == 1u &&
           g_sleep_force_wake_trace.release_calls == 2u &&
           g_sleep_force_wake_trace.released[0] ==
               g_sleep_force_wake_trace.timeline &&
           g_sleep_force_wake_trace.released[1] ==
               g_sleep_force_wake_trace.record);

    memset(&g_sleep_force_wake_trace, 0,
           sizeof(g_sleep_force_wake_trace));
    assert(gomore_primitives_sleep_force_wake(
        false, &sleep_force_wake_providers, &sleep_force_wake_status));
    assert(sleep_force_wake_status ==
               GOMORE_PRIMITIVES_SLEEP_FORCE_WAKE_COMPLETE &&
           g_sleep_force_wake_trace.allocation_calls == 1u &&
           g_sleep_force_wake_trace.prepare_calls == 1u &&
           g_sleep_force_wake_trace.mode_calls == 0u &&
           g_sleep_force_wake_trace.dispatch_calls == 0u &&
           g_sleep_force_wake_trace.release_calls == 1u);

    memset(&g_sleep_force_wake_trace, 0,
           sizeof(g_sleep_force_wake_trace));
    g_sleep_force_wake_trace.publish_requested = true;
    g_sleep_force_wake_trace.fail_allocation_call = 2u;
    assert(gomore_primitives_sleep_force_wake(
        true, &sleep_force_wake_providers, &sleep_force_wake_status));
    assert(sleep_force_wake_status ==
               GOMORE_PRIMITIVES_SLEEP_FORCE_WAKE_TIMELINE_ALLOCATION_FAILED &&
           g_sleep_force_wake_trace.dispatch_calls == 0u &&
           g_sleep_force_wake_trace.publish_calls == 0u &&
           g_sleep_force_wake_trace.release_calls == 1u &&
           g_sleep_force_wake_trace.released[0] ==
               g_sleep_force_wake_trace.record);

    memset(&g_sleep_force_wake_trace, 0,
           sizeof(g_sleep_force_wake_trace));
    g_sleep_force_wake_trace.fail_allocation_call = 1u;
    assert(gomore_primitives_sleep_force_wake(
        true, &sleep_force_wake_providers, &sleep_force_wake_status));
    assert(sleep_force_wake_status ==
               GOMORE_PRIMITIVES_SLEEP_FORCE_WAKE_RECORD_ALLOCATION_FAILED &&
           g_sleep_force_wake_trace.prepare_calls == 0u &&
           g_sleep_force_wake_trace.release_calls == 0u);
    const unsigned sleep_force_allocations_before =
        g_sleep_force_wake_trace.allocation_calls;
    assert(!gomore_primitives_sleep_force_wake(
        true, NULL, &sleep_force_wake_status));
    assert(g_sleep_force_wake_trace.allocation_calls ==
           sleep_force_allocations_before);
    uint8_t dormant_hr_ratio_state[0x2DC];
    memset(dormant_hr_ratio_state, 0, sizeof(dormant_hr_ratio_state));
    memset(&g_dormant_hr_ratio_trace, 0,
           sizeof(g_dormant_hr_ratio_trace));
    g_dormant_hr_ratio_trace.state = dormant_hr_ratio_state;
    g_dormant_hr_ratio_trace.filter_result = 1;
    g_dormant_hr_ratio_trace.filtered_value = 65;
    store_u32_fixture(&dormant_hr_ratio_state[0x24u],
                      float_bits(6.0f));
    dormant_hr_ratio_state[0x56u] = 4u;
    int32_t dormant_hr_filter_status = 0;
    assert(gomore_primitives_dormant_heart_rate_ratio_wrapper(
        dormant_hr_ratio_state, sizeof(dormant_hr_ratio_state), 72,
        dormant_hr_filter_update, dormant_ratio_accumulate,
        &dormant_hr_filter_status));
    assert(dormant_hr_filter_status == 1 &&
           g_dormant_hr_ratio_trace.filter_calls == 1u &&
           g_dormant_hr_ratio_trace.ratio_calls == 1u &&
           g_dormant_hr_ratio_trace.raw_value == 72 &&
           g_dormant_hr_ratio_trace.interval == 1000u &&
           load_u32_fixture(&dormant_hr_ratio_state[0x1Cu]) == 65u &&
           g_dormant_hr_ratio_trace.selected_heart_rate == 65.0f &&
           g_dormant_hr_ratio_trace.selected_speed == 6.0f);

    g_dormant_hr_ratio_trace.filter_result = 0x1772;
    g_dormant_hr_ratio_trace.filtered_value = 60;
    g_dormant_hr_ratio_trace.ratio_calls = 0u;
    dormant_hr_ratio_state[0x56u] = 0u;
    assert(gomore_primitives_dormant_heart_rate_ratio_wrapper(
        dormant_hr_ratio_state, sizeof(dormant_hr_ratio_state), 67,
        dormant_hr_filter_update, dormant_ratio_accumulate,
        &dormant_hr_filter_status));
    assert(dormant_hr_filter_status == 0x1772 &&
           g_dormant_hr_ratio_trace.ratio_calls == 0u &&
           load_u32_fixture(&dormant_hr_ratio_state[0x1Cu]) == 67u);

    store_u32_fixture(&dormant_hr_ratio_state[0x2Cu],
                      float_bits(9.0f));
    dormant_hr_ratio_state[0x56u] = 0x00u;
    dormant_hr_ratio_state[0x57u] = 0x42u;
    assert(gomore_primitives_dormant_heart_rate_ratio_wrapper(
        dormant_hr_ratio_state, sizeof(dormant_hr_ratio_state), 70,
        dormant_hr_filter_update, dormant_ratio_accumulate,
        &dormant_hr_filter_status));
    assert(g_dormant_hr_ratio_trace.ratio_calls == 0u);
    const unsigned dormant_filter_calls_before =
        g_dormant_hr_ratio_trace.filter_calls;
    assert(!gomore_primitives_dormant_heart_rate_ratio_wrapper(
        dormant_hr_ratio_state, sizeof(dormant_hr_ratio_state) - 1u, 72,
        dormant_hr_filter_update, dormant_ratio_accumulate,
        &dormant_hr_filter_status));
    assert(g_dormant_hr_ratio_trace.filter_calls ==
           dormant_filter_calls_before);

    float dormant_ratio_thresholds[5] = {
        60.0f, 70.0f, 80.0f, 90.0f, 100.0f,
    };
    float dormant_ratio_primary_sums[6] = {0.0f};
    float dormant_ratio_primary_counts[6] = {0.0f};
    gomore_primitives_dormant_ratio_input dormant_ratio_input = {
        .selected_heart_rate = 55.0f,
        .reserved_zero = 0.0f,
        .selected_speed = 4.0f,
        .thresholds = dormant_ratio_thresholds,
        .primary_sums = dormant_ratio_primary_sums,
        .primary_counts = dormant_ratio_primary_counts,
        .below_range_weight = 0.0f,
        .auxiliary_first = NULL,
        .auxiliary_second = NULL,
    };
    gomore_primitives_dormant_ratio_accumulator_state
        dormant_ratio_accumulator_state = {0};
    dormant_ratio_power_calls = 0u;
    assert(gomore_primitives_dormant_ratio_accumulator(
        &dormant_ratio_accumulator_state, &dormant_ratio_input,
        dormant_ratio_power));
    assert(dormant_ratio_accumulator_state.all_heart_rate_mean == 55.0f &&
           dormant_ratio_accumulator_state.all_sample_count == 1.0f &&
           dormant_ratio_accumulator_state.qualified_sample_count == 0.0f &&
           dormant_ratio_primary_counts[0] == 0.0f &&
           dormant_ratio_power_calls == 0u);

    dormant_ratio_accumulator_state =
        (gomore_primitives_dormant_ratio_accumulator_state){0};
    memset(dormant_ratio_primary_sums, 0,
           sizeof(dormant_ratio_primary_sums));
    memset(dormant_ratio_primary_counts, 0,
           sizeof(dormant_ratio_primary_counts));
    dormant_ratio_input.selected_speed = 6.0f;
    dormant_ratio_power_calls = 0u;
    assert(gomore_primitives_dormant_ratio_accumulator(
        &dormant_ratio_accumulator_state, &dormant_ratio_input,
        dormant_ratio_power));
    assert(float_bits(dormant_ratio_primary_sums[0]) ==
               UINT32_C(0x3E0848FC) &&
           dormant_ratio_primary_counts[0] == 1.0f &&
           dormant_ratio_accumulator_state.qualified_square_sum == 3025.0f &&
           dormant_ratio_accumulator_state.qualified_heart_rate_mean ==
               55.0f &&
           dormant_ratio_accumulator_state.qualified_speed_mean == 6.0f &&
           dormant_ratio_accumulator_state.qualified_sample_count == 1.0f &&
           dormant_ratio_power_calls == 3u);

    dormant_ratio_accumulator_state =
        (gomore_primitives_dormant_ratio_accumulator_state){0};
    dormant_ratio_accumulator_state.profile_flag = 1u;
    memset(dormant_ratio_primary_sums, 0,
           sizeof(dormant_ratio_primary_sums));
    memset(dormant_ratio_primary_counts, 0,
           sizeof(dormant_ratio_primary_counts));
    assert(gomore_primitives_dormant_ratio_accumulator(
        &dormant_ratio_accumulator_state, &dormant_ratio_input,
        dormant_ratio_power));
    assert(float_bits(dormant_ratio_primary_sums[0]) ==
               UINT32_C(0x3E1374BD) &&
           dormant_ratio_primary_counts[0] == 1.0f);

    float dormant_ratio_zero_thresholds[5] = {0.0f};
    dormant_ratio_input.thresholds = dormant_ratio_zero_thresholds;
    dormant_ratio_input.selected_heart_rate = 72.0f;
    dormant_ratio_accumulator_state =
        (gomore_primitives_dormant_ratio_accumulator_state){0};
    memset(dormant_ratio_primary_sums, 0,
           sizeof(dormant_ratio_primary_sums));
    memset(dormant_ratio_primary_counts, 0,
           sizeof(dormant_ratio_primary_counts));
    for (unsigned index = 0u; index < 30u; ++index) {
        assert(gomore_primitives_dormant_ratio_accumulator(
            &dormant_ratio_accumulator_state, &dormant_ratio_input,
            dormant_ratio_power));
    }
    assert(float_bits(dormant_ratio_primary_sums[5]) ==
               UINT32_C(0x401FFFFF) &&
           dormant_ratio_primary_counts[5] == 30.0f &&
           dormant_ratio_accumulator_state.qualified_square_sum == 0.0f &&
           dormant_ratio_accumulator_state.qualified_heart_rate_mean ==
               0.0f &&
           dormant_ratio_accumulator_state.qualified_speed_mean == 0.0f &&
           dormant_ratio_accumulator_state.qualified_sample_count == 0.0f);

    dormant_ratio_accumulator_state =
        (gomore_primitives_dormant_ratio_accumulator_state){0};
    memset(dormant_ratio_primary_sums, 0,
           sizeof(dormant_ratio_primary_sums));
    memset(dormant_ratio_primary_counts, 0,
           sizeof(dormant_ratio_primary_counts));
    dormant_ratio_input.selected_heart_rate = 60.0f;
    dormant_ratio_input.selected_speed = 4.0f;
    assert(gomore_primitives_dormant_ratio_accumulator(
        &dormant_ratio_accumulator_state, &dormant_ratio_input,
        dormant_ratio_power));
    dormant_ratio_input.selected_heart_rate = 72.0f;
    dormant_ratio_input.selected_speed = 6.0f;
    for (unsigned index = 0u; index < 30u; ++index) {
        assert(gomore_primitives_dormant_ratio_accumulator(
            &dormant_ratio_accumulator_state, &dormant_ratio_input,
            dormant_ratio_power));
    }
    assert(float_bits(
               dormant_ratio_accumulator_state.all_heart_rate_mean) ==
               UINT32_C(0x428F39CE) &&
           dormant_ratio_accumulator_state.qualified_sample_count == 30.0f &&
           float_bits(dormant_ratio_accumulator_state.secondary_sums[5]) ==
               UINT32_C(0x3DAAAAAB) &&
           dormant_ratio_accumulator_state.secondary_counts[5] == 1.0f);

    const float dormant_ratio_all_count_before =
        dormant_ratio_accumulator_state.all_sample_count;
    dormant_ratio_input.thresholds = NULL;
    assert(!gomore_primitives_dormant_ratio_accumulator(
        &dormant_ratio_accumulator_state, &dormant_ratio_input,
        dormant_ratio_power));
    assert(dormant_ratio_accumulator_state.all_sample_count ==
           dormant_ratio_all_count_before);

    union {
        uint32_t alignment;
        uint8_t bytes[0x328];
    } dormant_cycle_state;
    gomore_primitives_dormant_cycle_auxiliary dormant_cycle_auxiliary = {
        .smoother_input = 9.0f,
        .mode0_first_input = 50.0f,
    };
    gomore_primitives_dormant_cycle_input dormant_cycle_input = {
        .sample_index = 0,
        .raw_heart_rate = 70,
        .selected_speed = 3.6f,
        .auxiliary_speed = 4.0f,
        .copied_auxiliary_1 = 5.0f,
        .copied_auxiliary_2 = 6.0f,
        .auxiliary = &dormant_cycle_auxiliary,
        .unused_heart_rate_feature = 71.5f,
    };
    const gomore_primitives_dormant_cycle_providers
        dormant_cycle_providers = {
            .arctangent = dormant_mode0_arctangent,
            .cosine = dormant_mode0_cosine,
            .sine = dormant_mode0_sine,
            .power = dormant_mode1_target_power,
            .reduce = dormant_mode1_target_reduce,
            .finalize = dormant_mode1_target_finalize,
            .filter_heart_rate = dormant_hr_filter_update,
            .accumulate_ratio = dormant_ratio_accumulate,
        };
    memset(&dormant_cycle_state, 0, sizeof(dormant_cycle_state));
    dormant_cycle_state.bytes[0x56u] = 8u;
    memset(&g_dormant_mode0_math_trace, 0,
           sizeof(g_dormant_mode0_math_trace));
    memset(&g_dormant_mode1_target_trace, 0,
           sizeof(g_dormant_mode1_target_trace));
    g_dormant_mode1_target_trace.reducer_result = 4.0f;
    g_dormant_mode1_target_trace.finalizer_result = 2.0f;
    memset(&g_dormant_hr_ratio_trace, 0,
           sizeof(g_dormant_hr_ratio_trace));
    g_dormant_hr_ratio_trace.state = dormant_cycle_state.bytes;
    g_dormant_hr_ratio_trace.filter_result = 1;
    g_dormant_hr_ratio_trace.filtered_value = 65;
    int32_t dormant_cycle_result = INT32_MAX;
    assert(gomore_primitives_dormant_estimator_cycle(
        dormant_cycle_state.bytes, sizeof(dormant_cycle_state.bytes),
        &dormant_cycle_input, &dormant_cycle_providers,
        &dormant_cycle_result));
    assert(dormant_cycle_result == 0 &&
           g_dormant_mode0_math_trace.arctangent_calls == 1u &&
           g_dormant_mode0_math_trace.cosine_calls == 2u &&
           g_dormant_mode0_math_trace.sine_calls == 1u &&
           g_dormant_mode1_target_trace.reducer_calls == 1u &&
           g_dormant_mode1_target_trace.finalizer_calls == 1u &&
           g_dormant_mode1_target_trace.mode == 0 &&
           load_u32_fixture(&dormant_cycle_state.bytes[0x24u]) ==
               float_bits(7.2f) &&
           load_u32_fixture(&dormant_cycle_state.bytes[0x28u]) ==
               float_bits(7.2f) &&
           load_u32_fixture(&dormant_cycle_state.bytes[0x2Cu]) ==
               float_bits(4.0f) &&
           load_u32_fixture(&dormant_cycle_state.bytes[0x30u]) ==
               float_bits(4.0f) &&
           load_u32_fixture(&dormant_cycle_state.bytes[0x38u]) ==
               float_bits(5.0f) &&
           load_u32_fixture(&dormant_cycle_state.bytes[0x3Cu]) ==
               float_bits(6.0f) &&
           load_u32_fixture(&dormant_cycle_state.bytes[0x20u]) == 65u &&
           dormant_cycle_state.bytes[0x60u] == 1u &&
           load_u16_fixture(&dormant_cycle_state.bytes[0x52u]) == 0u &&
           g_dormant_hr_ratio_trace.filter_calls == 1u &&
           g_dormant_hr_ratio_trace.ratio_calls == 1u &&
           g_dormant_hr_ratio_trace.selected_speed == 7.2f);

    memset(&dormant_cycle_state, 0, sizeof(dormant_cycle_state));
    dormant_cycle_state.bytes[0x56u] = 4u;
    gomore_primitives_speed_smoother *const dormant_cycle_smoother =
        (gomore_primitives_speed_smoother *)(void *)
            &dormant_cycle_state.bytes[0x2DCu];
    dormant_cycle_smoother->enabled = 1u;
    dormant_cycle_smoother->maximum_raw_rise = 1.0f;
    dormant_cycle_smoother->maximum_raw_fall = 1.0f;
    dormant_cycle_smoother->maximum_output_rise = 1.0f;
    dormant_cycle_smoother->maximum_output_fall = 1.0f;
    dormant_cycle_auxiliary.smoother_input = 9.0f;
    dormant_cycle_input.sample_index = 0;
    dormant_cycle_input.raw_heart_rate = 70;
    dormant_cycle_input.selected_speed = 6.0f;
    memset(&g_dormant_mode1_target_trace, 0,
           sizeof(g_dormant_mode1_target_trace));
    g_dormant_mode1_target_trace.reducer_result = 4.0f;
    g_dormant_mode1_target_trace.finalizer_result = 2.0f;
    memset(&g_dormant_hr_ratio_trace, 0,
           sizeof(g_dormant_hr_ratio_trace));
    g_dormant_hr_ratio_trace.state = dormant_cycle_state.bytes;
    g_dormant_hr_ratio_trace.filter_result = 0;
    assert(gomore_primitives_dormant_estimator_cycle(
        dormant_cycle_state.bytes, sizeof(dormant_cycle_state.bytes),
        &dormant_cycle_input, &dormant_cycle_providers,
        &dormant_cycle_result));
    assert(dormant_cycle_result == 0 &&
           dormant_cycle_auxiliary.smoother_input == 0.0f &&
           load_u32_fixture(&dormant_cycle_state.bytes[0x34u]) ==
               float_bits(0.0f) &&
           g_dormant_mode1_target_trace.mode == 1 &&
           g_dormant_mode1_target_trace.power_calls == 1u &&
           g_dormant_mode1_target_trace.reducer_calls == 1u &&
           g_dormant_mode1_target_trace.finalizer_calls == 1u &&
           load_u32_fixture(&dormant_cycle_state.bytes[0x24u]) ==
               float_bits(7.2f));

    memset(&dormant_cycle_state, 0, sizeof(dormant_cycle_state));
    dormant_cycle_input.sample_index = 10;
    dormant_cycle_input.raw_heart_rate = 20;
    dormant_cycle_input.selected_speed = 2.0f;
    const unsigned cycle_filter_calls_before =
        g_dormant_hr_ratio_trace.filter_calls;
    assert(gomore_primitives_dormant_estimator_cycle(
        dormant_cycle_state.bytes, sizeof(dormant_cycle_state.bytes),
        &dormant_cycle_input, &dormant_cycle_providers,
        &dormant_cycle_result));
    assert(dormant_cycle_result == -1016 &&
           load_u16_fixture(&dormant_cycle_state.bytes[0x52u]) ==
               UINT16_C(0xFC08) &&
           g_dormant_hr_ratio_trace.filter_calls ==
               cycle_filter_calls_before);
    uint8_t dormant_cycle_before[0x328];
    memcpy(dormant_cycle_before, dormant_cycle_state.bytes,
           sizeof(dormant_cycle_before));
    assert(!gomore_primitives_dormant_estimator_cycle(
        dormant_cycle_state.bytes, sizeof(dormant_cycle_state.bytes) - 1u,
        &dormant_cycle_input, &dormant_cycle_providers,
        &dormant_cycle_result));
    assert(memcmp(dormant_cycle_before, dormant_cycle_state.bytes,
                  sizeof(dormant_cycle_before)) == 0);
    uint8_t dormant_root_state[0x2C];
    memset(dormant_root_state, 0, sizeof(dormant_root_state));
    store_u32_fixture(&dormant_root_state[0], float_bits(1.2f));
    store_u32_fixture(&dormant_root_state[4], float_bits(70.0f));
    memset(&g_dormant_root_trace, 0, sizeof(g_dormant_root_trace));
    assert(gomore_primitives_dormant_speed_root_build(
        100.0f, 165.0f, dormant_root_state, sizeof(dormant_root_state),
        0, dormant_root_power, dormant_quadratic_dispatch,
        dormant_cubic_dispatch));
    assert(g_dormant_root_trace.state == dormant_root_state &&
           g_dormant_root_trace.power_calls == 1u &&
           g_dormant_root_trace.quadratic_calls == 1u &&
           g_dormant_root_trace.cubic_calls == 0u &&
           float_bits(g_dormant_root_trace.coefficients[0]) ==
               UINT32_C(0x40E8D917) &&
           float_bits(g_dormant_root_trace.coefficients[1]) ==
               UINT32_C(0x409B7C1C) &&
           float_bits(g_dormant_root_trace.coefficients[2]) ==
               UINT32_C(0x4299DD40));

    memset(&g_dormant_root_trace, 0, sizeof(g_dormant_root_trace));
    assert(gomore_primitives_dormant_speed_root_build(
        10.0f, 2.0f, dormant_root_state, sizeof(dormant_root_state),
        1, dormant_root_power, dormant_quadratic_dispatch,
        dormant_cubic_dispatch));
    assert(g_dormant_root_trace.power_calls == 1u &&
           g_dormant_root_trace.quadratic_calls == 0u &&
           g_dormant_root_trace.cubic_calls == 1u &&
           float_bits(g_dormant_root_trace.coefficients[0]) ==
               UINT32_C(0x3E1704FF) &&
           float_bits(g_dormant_root_trace.coefficients[1]) ==
               UINT32_C(0x3DB4A234) &&
           float_bits(g_dormant_root_trace.coefficients[2]) ==
               UINT32_C(0x3D713CAE) &&
           float_bits(g_dormant_root_trace.coefficients[3]) ==
               UINT32_C(0xBFB3A358));
    const unsigned root_power_calls_before =
        g_dormant_root_trace.power_calls;
    assert(!gomore_primitives_dormant_speed_root_build(
        10.0f, 2.0f, dormant_root_state, 0x23u, 1,
        dormant_root_power, dormant_quadratic_dispatch,
        dormant_cubic_dispatch));
    assert(g_dormant_root_trace.power_calls == root_power_calls_before);
    memset(dormant_root_state, 0, sizeof(dormant_root_state));
    store_u32_fixture(&dormant_root_state[0], float_bits(1.2f));
    store_u32_fixture(&dormant_root_state[4], float_bits(70.0f));
    memset(&g_dormant_root_trace, 0, sizeof(g_dormant_root_trace));
    g_dormant_root_trace.selected_root = 1.25f;
    float dormant_alternate_output = -1.0f;
    assert(gomore_primitives_dormant_alternate_root_solve(
        10.0f, 2.0f, dormant_root_state, sizeof(dormant_root_state),
        0, dormant_alternate_quadratic_dispatch,
        dormant_alternate_cubic_dispatch, &dormant_alternate_output));
    assert(g_dormant_root_trace.quadratic_calls == 1u &&
           g_dormant_root_trace.cubic_calls == 0u &&
           float_bits(g_dormant_root_trace.coefficients[0]) ==
               UINT32_C(0x3DB4A234) &&
           float_bits(g_dormant_root_trace.coefficients[1]) == 0u &&
           float_bits(g_dormant_root_trace.coefficients[2]) ==
               UINT32_C(0xC10BB4C5) &&
           float_bits(dormant_alternate_output) == UINT32_C(0x3FA00000));

    memset(&g_dormant_root_trace, 0, sizeof(g_dormant_root_trace));
    g_dormant_root_trace.selected_root =
        bits_float(UINT32_C(0x3FA00001));
    assert(gomore_primitives_dormant_alternate_root_solve(
        10.0f, 2.0f, dormant_root_state, sizeof(dormant_root_state),
        2, dormant_alternate_quadratic_dispatch,
        dormant_alternate_cubic_dispatch, &dormant_alternate_output));
    assert(g_dormant_root_trace.quadratic_calls == 0u &&
           g_dormant_root_trace.cubic_calls == 1u &&
           float_bits(g_dormant_root_trace.coefficients[0]) ==
               UINT32_C(0x3E1704FF) &&
           float_bits(g_dormant_root_trace.coefficients[1]) ==
               UINT32_C(0x3DB4A234) &&
           float_bits(g_dormant_root_trace.coefficients[2]) == 0u &&
           float_bits(g_dormant_root_trace.coefficients[3]) ==
               UINT32_C(0xC10BB4C5) &&
           float_bits(dormant_alternate_output) == UINT32_C(0x3F600001));

    g_dormant_root_trace.selected_root = -1.0f;
    assert(gomore_primitives_dormant_alternate_root_solve(
        10.0f, 2.0f, dormant_root_state, sizeof(dormant_root_state),
        1, dormant_alternate_quadratic_dispatch,
        dormant_alternate_cubic_dispatch, &dormant_alternate_output));
    assert(float_bits(dormant_alternate_output) == 0u);
    g_dormant_root_trace.selected_root =
        bits_float(UINT32_C(0x7FC00000));
    assert(gomore_primitives_dormant_alternate_root_solve(
        10.0f, 2.0f, dormant_root_state, sizeof(dormant_root_state),
        1, dormant_alternate_quadratic_dispatch,
        dormant_alternate_cubic_dispatch, &dormant_alternate_output));
    assert(float_bits(dormant_alternate_output) == 0u);
    const unsigned alternate_calls_before =
        g_dormant_root_trace.cubic_calls;
    dormant_alternate_output = -1.0f;
    assert(!gomore_primitives_dormant_alternate_root_solve(
        10.0f, 2.0f, dormant_root_state, 0x23u, 1,
        dormant_alternate_quadratic_dispatch,
        dormant_alternate_cubic_dispatch, &dormant_alternate_output));
    assert(g_dormant_root_trace.cubic_calls == alternate_calls_before &&
           dormant_alternate_output == -1.0f);

    memset(dormant_root_state, 0, sizeof(dormant_root_state));
    store_u32_fixture(&dormant_root_state[0], float_bits(1.2f));
    store_u32_fixture(&dormant_root_state[4], float_bits(70.0f));
    dormant_root_state[0x24u] = 0x40u;
    dormant_root_state[0x25u] = 0x04u;
    memset(&g_dormant_root_resolve_trace, 0,
           sizeof(g_dormant_root_resolve_trace));
    g_dormant_root_resolve_trace.roots[0] = 1.0f;
    float dormant_resolved_root = -1.0f;
    assert(gomore_primitives_rational_transform(1.0f, 1.2f) < 1.25f);
    assert(gomore_primitives_dormant_root_resolve(
        4.0f, 1.0f, dormant_root_state, sizeof(dormant_root_state), 0,
        dormant_root_resolve_power, dormant_root_resolve_quadratic,
        dormant_root_resolve_cubic, &dormant_resolved_root));
    assert(dormant_resolved_root == 1.0f &&
           g_dormant_root_resolve_trace.quadratic_calls == 1u &&
           g_dormant_root_resolve_trace.cubic_calls == 0u);

    memset(&g_dormant_root_resolve_trace, 0,
           sizeof(g_dormant_root_resolve_trace));
    g_dormant_root_resolve_trace.roots[0] = 1.0f;
    g_dormant_root_resolve_trace.roots[1] = 2.0f;
    assert(gomore_primitives_rational_transform(2.0f, 1.2f) >= 1.25f);
    assert(gomore_primitives_dormant_root_resolve(
        4.0f, 2.0f, dormant_root_state, sizeof(dormant_root_state), 0,
        dormant_root_resolve_power, dormant_root_resolve_quadratic,
        dormant_root_resolve_cubic, &dormant_resolved_root));
    assert(dormant_resolved_root == 2.0f &&
           g_dormant_root_resolve_trace.quadratic_calls == 1u &&
           g_dormant_root_resolve_trace.power_calls == 1u);

    dormant_root_state[0x24u] = 0u;
    dormant_root_state[0x25u] = 0u;
    memset(&g_dormant_root_resolve_trace, 0,
           sizeof(g_dormant_root_resolve_trace));
    const float dormant_resolve_baseline =
        gomore_primitives_speed_dynamics_baseline(
            1.0f, 1.0f, 1.2f, 70.0f, 0u,
            dormant_root_resolve_power);
    const float dormant_resolve_scale =
        bits_float(UINT32_C(0x3F0DD2F2));
    assert(dormant_resolve_baseline > 0.0f);
    assert(gomore_primitives_dormant_root_resolve(
        dormant_resolve_baseline * dormant_resolve_scale * 0.5f,
        1.0f, dormant_root_state, sizeof(dormant_root_state), 0,
        dormant_root_resolve_power, dormant_root_resolve_quadratic,
        dormant_root_resolve_cubic, &dormant_resolved_root));
    assert(dormant_resolved_root > 0.499f &&
           dormant_resolved_root < 0.501f &&
           g_dormant_root_resolve_trace.quadratic_calls == 0u);

    memset(&g_dormant_root_resolve_trace, 0,
           sizeof(g_dormant_root_resolve_trace));
    g_dormant_root_resolve_trace.roots[0] = 2.0f;
    g_dormant_root_resolve_trace.roots[1] = 4.0f;
    g_dormant_root_resolve_trace.roots[2] = 6.0f;
    const float dormant_root_primary =
        (dormant_resolve_baseline + 1.0f) * dormant_resolve_scale;
    assert(gomore_primitives_dormant_root_resolve(
        dormant_root_primary, 1.0f,
        dormant_root_state, sizeof(dormant_root_state), 0,
        dormant_root_resolve_power, dormant_root_resolve_quadratic,
        dormant_root_resolve_cubic, &dormant_resolved_root));
    assert(dormant_resolved_root == 3.0f &&
           g_dormant_root_resolve_trace.quadratic_calls == 1u);
    assert(gomore_primitives_dormant_root_resolve(
        dormant_root_primary, 1.0f,
        dormant_root_state, sizeof(dormant_root_state), 1,
        dormant_root_resolve_power, dormant_root_resolve_quadratic,
        dormant_root_resolve_cubic, &dormant_resolved_root));
    assert(dormant_resolved_root == 4.0f &&
           g_dormant_root_resolve_trace.cubic_calls == 1u);
    const unsigned resolved_calls_before =
        g_dormant_root_resolve_trace.cubic_calls;
    dormant_resolved_root = -1.0f;
    assert(!gomore_primitives_dormant_root_resolve(
        dormant_root_primary, 1.0f, dormant_root_state, 0x25u, 1,
        dormant_root_resolve_power, dormant_root_resolve_quadratic,
        dormant_root_resolve_cubic, &dormant_resolved_root));
    assert(g_dormant_root_resolve_trace.cubic_calls ==
               resolved_calls_before &&
           dormant_resolved_root == -1.0f);

    memset(dormant_root_state, 0, sizeof(dormant_root_state));
    store_u32_fixture(&dormant_root_state[0], float_bits(1.2f));
    store_u32_fixture(&dormant_root_state[4], float_bits(70.0f));
    memset(&g_dormant_mode0_math_trace, 0,
           sizeof(g_dormant_mode0_math_trace));
    float dormant_reduced = -1.0f;
    assert(gomore_primitives_dormant_root_reduce(
        0.5f, 0.0f, 165.0f,
        dormant_root_state, sizeof(dormant_root_state), 0,
        dormant_mode0_arctangent, dormant_mode0_cosine,
        adapter_power10, &dormant_reduced));
    assert(float_bits(dormant_reduced) == UINT32_C(0x41E8424F) &&
           g_dormant_mode0_math_trace.arctangent_calls == 0u &&
           g_dormant_mode0_math_trace.cosine_calls == 0u &&
           load_u32_fixture(&dormant_root_state[0x08u]) == 0u &&
           load_u32_fixture(&dormant_root_state[0x10u]) == 0u);

    assert(gomore_primitives_dormant_root_reduce(
        0.5f, 0.01f, 165.0f,
        dormant_root_state, sizeof(dormant_root_state), 0,
        dormant_mode0_arctangent, dormant_mode0_cosine,
        adapter_power10, &dormant_reduced));
    assert(float_bits(dormant_reduced) == UINT32_C(0x41E8424F) &&
           g_dormant_mode0_math_trace.arctangent_calls == 1u &&
           g_dormant_mode0_math_trace.cosine_calls == 2u);

    store_u32_fixture(&dormant_root_state[0x08u], float_bits(1.5f));
    store_u32_fixture(&dormant_root_state[0x10u], float_bits(100.0f));
    assert(gomore_primitives_dormant_root_reduce(
        2.0f, 0.0f, 165.0f,
        dormant_root_state, sizeof(dormant_root_state), 0,
        dormant_mode0_arctangent, dormant_mode0_cosine,
        adapter_power10, &dormant_reduced));
    assert(float_bits(dormant_reduced) == UINT32_C(0x42F38306) &&
           load_u32_fixture(&dormant_root_state[0x08u]) ==
               float_bits(2.0f) &&
           load_u32_fixture(&dormant_root_state[0x10u]) ==
               float_bits(140.0f));

    store_u32_fixture(&dormant_root_state[0x08u], float_bits(1.5f));
    store_u32_fixture(&dormant_root_state[0x10u], float_bits(100.0f));
    assert(gomore_primitives_dormant_root_reduce(
        2.0f, 0.25f, 165.0f,
        dormant_root_state, sizeof(dormant_root_state), 1,
        dormant_mode0_arctangent, dormant_mode0_cosine,
        adapter_power10, &dormant_reduced));
    assert(dormant_reduced > 0.0f &&
           load_u32_fixture(&dormant_root_state[0x08u]) ==
               float_bits(2.5f) &&
           load_u32_fixture(&dormant_root_state[0x10u]) ==
               float_bits(218.75f));
    const uint32_t dormant_reduced_previous = float_bits(dormant_reduced);
    assert(!gomore_primitives_dormant_root_reduce(
        2.0f, 0.25f, 165.0f,
        dormant_root_state, 0x25u, 1,
        dormant_mode0_arctangent, dormant_mode0_cosine,
        adapter_power10, &dormant_reduced));
    assert(float_bits(dormant_reduced) == dormant_reduced_previous);

    memset(dormant_root_state, UINT8_C(0xA5),
           sizeof(dormant_root_state));
    store_u32_fixture(&dormant_root_state[0], float_bits(1.2f));
    store_u32_fixture(&dormant_root_state[4], float_bits(70.0f));
    dormant_root_state[0x24u] = 0u;
    dormant_root_state[0x25u] = 0u;
    dormant_root_state[0x26u] = 0u;
    memset(&g_dormant_mode1_target_trace, 0,
           sizeof(g_dormant_mode1_target_trace));
    g_dormant_mode1_target_trace.reducer_result = 4.0f;
    g_dormant_mode1_target_trace.finalizer_result = 2.0f;
    float dormant_mode1_output = -1.0f;
    assert(gomore_primitives_dormant_speed_mode1_target_update(
        7.0f, 36.0f, dormant_root_state, sizeof(dormant_root_state), 1,
        dormant_mode1_target_power, dormant_mode1_target_reduce,
        dormant_mode1_target_finalize, &dormant_mode1_output));
    assert(g_dormant_mode1_target_trace.power_calls == 1u &&
           g_dormant_mode1_target_trace.reducer_calls == 1u &&
           g_dormant_mode1_target_trace.finalizer_calls == 1u &&
           g_dormant_mode1_target_trace.state == dormant_root_state &&
           g_dormant_mode1_target_trace.primary == 10.0f &&
           g_dormant_mode1_target_trace.secondary == 0.0f &&
           g_dormant_mode1_target_trace.auxiliary == 165.0f &&
           g_dormant_mode1_target_trace.reduced_input == 4.0f &&
           g_dormant_mode1_target_trace.mode == 1 &&
           load_u32_fixture(&dormant_root_state[0x08u]) ==
               float_bits(10.0f) &&
           load_u32_fixture(&dormant_root_state[0x0Cu]) ==
               float_bits(7.0f) &&
           load_u32_fixture(&dormant_root_state[0x10u]) ==
               float_bits(3500.0f) &&
           load_u32_fixture(&dormant_root_state[0x18u]) == 0u &&
           load_u32_fixture(&dormant_root_state[0x1Cu]) == 0u &&
           load_u32_fixture(&dormant_root_state[0x20u]) == 0u &&
           dormant_root_state[0x26u] == 1u &&
           float_bits(dormant_mode1_output) ==
               float_bits(2.0f * bits_float(UINT32_C(0x40666666))));

    g_dormant_mode1_target_trace.finalizer_result = -1.0f;
    assert(gomore_primitives_dormant_speed_mode1_target_update(
        9.0f, 36.0f, dormant_root_state, sizeof(dormant_root_state), 2,
        dormant_mode1_target_power, dormant_mode1_target_reduce,
        dormant_mode1_target_finalize, &dormant_mode1_output));
    assert(g_dormant_mode1_target_trace.power_calls == 1u &&
           g_dormant_mode1_target_trace.secondary == 2.0f &&
           g_dormant_mode1_target_trace.mode == 2 &&
           load_u32_fixture(&dormant_root_state[0x0Cu]) ==
               float_bits(9.0f) &&
           float_bits(dormant_mode1_output) == 0u);

    dormant_root_state[0x24u] = UINT8_C(0x40);
    g_dormant_mode1_target_trace.finalizer_result =
        bits_float(UINT32_C(0x7FC00000));
    assert(gomore_primitives_dormant_speed_mode1_target_veneer(
        9.0f, 36.0f, dormant_root_state, sizeof(dormant_root_state),
        dormant_mode1_target_power, dormant_mode1_target_reduce,
        dormant_mode1_target_finalize, &dormant_mode1_output));
    assert(float_bits(g_dormant_mode1_target_trace.auxiliary) ==
               float_bits(gomore_primitives_clamped_rational(10.0f, 1.2f)) &&
           g_dormant_mode1_target_trace.mode == 1 &&
           float_bits(dormant_mode1_output) == UINT32_C(0x7FC00000));
    const unsigned mode1_reduce_calls_before =
        g_dormant_mode1_target_trace.reducer_calls;
    dormant_mode1_output = -1.0f;
    assert(!gomore_primitives_dormant_speed_mode1_target_update(
        9.0f, 36.0f, dormant_root_state, 0x2Bu, 1,
        dormant_mode1_target_power, dormant_mode1_target_reduce,
        dormant_mode1_target_finalize, &dormant_mode1_output));
    assert(g_dormant_mode1_target_trace.reducer_calls ==
               mode1_reduce_calls_before &&
           dormant_mode1_output == -1.0f);
    memset(dormant_root_state, UINT8_C(0xA5),
           sizeof(dormant_root_state));
    store_u32_fixture(&dormant_root_state[0], float_bits(1.2f));
    store_u32_fixture(&dormant_root_state[4], float_bits(70.0f));
    dormant_root_state[0x24u] = 0u;
    dormant_root_state[0x25u] = 0u;
    dormant_root_state[0x26u] = 0u;
    memset(&g_dormant_mode0_math_trace, 0,
           sizeof(g_dormant_mode0_math_trace));
    memset(&g_dormant_mode1_target_trace, 0,
           sizeof(g_dormant_mode1_target_trace));
    g_dormant_mode1_target_trace.reducer_result = 4.0f;
    g_dormant_mode1_target_trace.finalizer_result = 2.0f;
    float dormant_mode0_output = -1.0f;
    assert(gomore_primitives_dormant_speed_mode0_target_update(
        50.0f, 36.0f, dormant_root_state, sizeof(dormant_root_state), 7,
        dormant_mode0_arctangent, dormant_mode0_cosine,
        dormant_mode0_sine, dormant_mode1_target_power,
        dormant_mode1_target_reduce, dormant_mode1_target_finalize,
        &dormant_mode0_output));
    assert(g_dormant_mode0_math_trace.arctangent_calls == 1u &&
           g_dormant_mode0_math_trace.cosine_calls == 2u &&
           g_dormant_mode0_math_trace.sine_calls == 1u &&
           g_dormant_mode0_math_trace.arctangent_input == 0.5f &&
           g_dormant_mode0_math_trace.trigonometric_input == 0.5f &&
           g_dormant_mode1_target_trace.power_calls == 1u &&
           g_dormant_mode1_target_trace.reducer_calls == 1u &&
           g_dormant_mode1_target_trace.finalizer_calls == 1u &&
           g_dormant_mode1_target_trace.primary == 8.0f &&
           g_dormant_mode1_target_trace.secondary == 6.0f &&
           g_dormant_mode1_target_trace.auxiliary == 165.0f &&
           g_dormant_mode1_target_trace.mode == 7 &&
           load_u32_fixture(&dormant_root_state[0x08u]) ==
               float_bits(8.0f) &&
           load_u32_fixture(&dormant_root_state[0x10u]) ==
               float_bits(2240.0f) &&
           load_u32_fixture(&dormant_root_state[0x18u]) == 0u &&
           load_u32_fixture(&dormant_root_state[0x1Cu]) == 0u &&
           load_u32_fixture(&dormant_root_state[0x20u]) == 0u &&
           dormant_root_state[0x26u] == 1u &&
           float_bits(dormant_mode0_output) ==
               float_bits(2.0f * bits_float(UINT32_C(0x40666666))));

    memset(&g_dormant_mode0_math_trace, 0,
           sizeof(g_dormant_mode0_math_trace));
    g_dormant_mode1_target_trace.finalizer_result = -1.0f;
    assert(gomore_primitives_dormant_speed_mode0_target_veneer(
        -50.0f, 36.0f, dormant_root_state, sizeof(dormant_root_state),
        dormant_mode0_arctangent, dormant_mode0_cosine,
        dormant_mode0_sine, dormant_mode1_target_power,
        dormant_mode1_target_reduce, dormant_mode1_target_finalize,
        &dormant_mode0_output));
    assert(g_dormant_mode0_math_trace.arctangent_calls == 1u &&
           g_dormant_mode0_math_trace.cosine_calls == 1u &&
           g_dormant_mode0_math_trace.sine_calls == 1u &&
           g_dormant_mode1_target_trace.power_calls == 1u &&
           g_dormant_mode1_target_trace.mode == 0 &&
           float_bits(dormant_mode0_output) == 0u);

    const unsigned mode0_atan_calls_before =
        g_dormant_mode0_math_trace.arctangent_calls;
    dormant_mode0_output = -1.0f;
    assert(!gomore_primitives_dormant_speed_mode0_target_update(
        50.0f, 36.0f, dormant_root_state, 0x2Bu, 0,
        dormant_mode0_arctangent, dormant_mode0_cosine,
        dormant_mode0_sine, dormant_mode1_target_power,
        dormant_mode1_target_reduce, dormant_mode1_target_finalize,
        &dormant_mode0_output));
    assert(g_dormant_mode0_math_trace.arctangent_calls ==
               mode0_atan_calls_before &&
           dormant_mode0_output == -1.0f);
    uint8_t sleep_graph_state[0x23C];
    memset(sleep_graph_state, UINT8_C(0xA5), sizeof(sleep_graph_state));
    static const uint8_t sleep_graph_dimensions[24] = {
        1u, 2u, 3u, 4u, 5u, 6u, 7u, 8u,
        11u, 12u, 13u, 14u, 15u, 16u, 17u, 18u,
        21u, 22u, 23u, 24u, 25u, 26u, 27u, 28u,
    };
    store_u32_fixture(&sleep_graph_state[0], 2u);
    memset(&g_sleep_graph_dispatch_trace, 0,
           sizeof(g_sleep_graph_dispatch_trace));
    assert(gomore_primitives_sleep_graph_family_dispatch(
        sleep_graph_state, sizeof(sleep_graph_state), UINT32_C(0x3456),
        sleep_graph_dimensions, sizeof(sleep_graph_dimensions),
        UINT32_C(0x36DCD), UINT32_C(0x5D245),
        sleep_graph_build_zero, sleep_graph_build_nonzero,
        sleep_graph_construct_recurrent, sleep_graph_construct_dense));
    assert(g_sleep_graph_dispatch_trace.zero_build_calls == 0u &&
           g_sleep_graph_dispatch_trace.nonzero_build_calls == 1u &&
           g_sleep_graph_dispatch_trace.recurrent_calls == 3u &&
           g_sleep_graph_dispatch_trace.dense_calls == 2u &&
           g_sleep_graph_dispatch_trace.family == 2 &&
           g_sleep_graph_dispatch_trace.graph_state ==
               &sleep_graph_state[4] &&
           g_sleep_graph_dispatch_trace.arena_seed == UINT32_C(0x3456));
    static const uint8_t expected_recurrent_dimensions[6] = {
        8u, 4u, 21u, 22u, 23u, 24u,
    };
    static const uint8_t expected_dense_dimensions[8] = {
        25u, 26u, 1u, 1u, 27u, 28u, 1u, 0u,
    };
    assert(memcmp(g_sleep_graph_dispatch_trace.recurrent_dimensions,
                  expected_recurrent_dimensions,
                  sizeof(expected_recurrent_dimensions)) == 0 &&
           memcmp(g_sleep_graph_dispatch_trace.dense_dimensions,
                  expected_dense_dimensions,
                  sizeof(expected_dense_dimensions)) == 0 &&
           sleep_graph_state[0x1BCu] == UINT8_C(0x10) &&
           sleep_graph_state[0x1D8u] == UINT8_C(0x11) &&
           sleep_graph_state[0x1F0u] == UINT8_C(0x12) &&
           sleep_graph_state[0x208u] == UINT8_C(0x20) &&
           sleep_graph_state[0x220u] == UINT8_C(0x21) &&
           load_u32_fixture(&sleep_graph_state[0x1D4u]) ==
               UINT32_C(0x36DCD) &&
           load_u32_fixture(&sleep_graph_state[0x238u]) ==
               UINT32_C(0x5D245));

    store_u32_fixture(&sleep_graph_state[0], 0u);
    store_u32_fixture(&sleep_graph_state[0x238u], UINT32_C(0xA5A5A5A5));
    memset(&g_sleep_graph_dispatch_trace, 0,
           sizeof(g_sleep_graph_dispatch_trace));
    assert(gomore_primitives_sleep_graph_family_dispatch(
        sleep_graph_state, sizeof(sleep_graph_state), UINT32_C(0x9999),
        sleep_graph_dimensions, sizeof(sleep_graph_dimensions),
        UINT32_C(0x36DCD), UINT32_C(0x5D245),
        sleep_graph_build_zero, sleep_graph_build_nonzero,
        sleep_graph_construct_recurrent, sleep_graph_construct_dense));
    assert(g_sleep_graph_dispatch_trace.zero_build_calls == 1u &&
           g_sleep_graph_dispatch_trace.nonzero_build_calls == 0u &&
           g_sleep_graph_dispatch_trace.recurrent_dimensions[2] == 1u &&
           g_sleep_graph_dispatch_trace.recurrent_dimensions[3] == 2u &&
           load_u32_fixture(&sleep_graph_state[0x238u]) ==
               UINT32_C(0xA5A5A5A5));
    const unsigned graph_zero_calls_before =
        g_sleep_graph_dispatch_trace.zero_build_calls;
    store_u32_fixture(&sleep_graph_state[0], 3u);
    assert(!gomore_primitives_sleep_graph_family_dispatch(
        sleep_graph_state, sizeof(sleep_graph_state), 0u,
        sleep_graph_dimensions, sizeof(sleep_graph_dimensions),
        0u, 0u, sleep_graph_build_zero, sleep_graph_build_nonzero,
        sleep_graph_construct_recurrent, sleep_graph_construct_dense));
    assert(g_sleep_graph_dispatch_trace.zero_build_calls ==
           graph_zero_calls_before);
    gomore_primitives_topic_input_state topic_input;
    memset(&topic_input, 0, sizeof(topic_input));
    uint8_t topic_acc_batch[GOMORE_PRIMITIVES_TOPIC_ACC_BATCH_BYTES];
    memset(topic_acc_batch, 0, sizeof(topic_acc_batch));
    store_u16_fixture(&topic_acc_batch[0], UINT16_C(1024));
    store_u16_fixture(&topic_acc_batch[2], (uint16_t)(int16_t)-1024);
    store_u16_fixture(&topic_acc_batch[4], UINT16_C(512));
    topic_acc_batch[GOMORE_PRIMITIVES_TOPIC_ACC_COUNT_OFFSET] = 30u;
    assert(gomore_primitives_topic_accelerometer_ingest(
        &topic_input, topic_acc_batch, sizeof(topic_acc_batch)));
    assert(topic_input.accelerometer_sample_count == 25u &&
           topic_input.accelerometer_axes[0][0] == 1000.0f &&
           topic_input.accelerometer_axes[1][0] == 1000.0f &&
           topic_input.accelerometer_axes[2][0] == 500.0f &&
           topic_input.ready_flags ==
               GOMORE_PRIMITIVES_TOPIC_READY_ACCELEROMETER);
    const gomore_primitives_topic_input_state topic_before_bad = topic_input;
    assert(!gomore_primitives_topic_accelerometer_ingest(
        &topic_input, topic_acc_batch, sizeof(topic_acc_batch) - 1u));
    assert(memcmp(&topic_input, &topic_before_bad, sizeof(topic_input)) == 0);

    uint8_t topic_raw_packet[104];
    memset(topic_raw_packet, 0, sizeof(topic_raw_packet));
    topic_raw_packet[0] = 26u;
    store_u32_fixture(&topic_raw_packet[4], UINT32_C(123456));
    store_u32_fixture(&topic_raw_packet[100], UINT32_C(654321));
    assert(gomore_primitives_topic_raw_optical_ingest(
        &topic_input, topic_raw_packet, sizeof(topic_raw_packet)));
    assert(topic_input.raw_optical_sample_count == 25u &&
           topic_input.raw_optical[0] == 123456.0f &&
           topic_input.raw_optical[24] == 654321.0f &&
           topic_input.ready_flags ==
               (GOMORE_PRIMITIVES_TOPIC_READY_ACCELEROMETER |
                GOMORE_PRIMITIVES_TOPIC_READY_RAW_OPTICAL));

    const uint8_t topic_hr_packet[] = {72u};
    assert(gomore_primitives_topic_heart_rate_ingest(
        &topic_input, topic_hr_packet, sizeof(topic_hr_packet)));
    assert(topic_input.direct_heart_rate == 72.0f &&
           topic_input.ready_flags ==
               (GOMORE_PRIMITIVES_TOPIC_READY_ACCELEROMETER |
                GOMORE_PRIMITIVES_TOPIC_READY_RAW_OPTICAL |
                GOMORE_PRIMITIVES_TOPIC_READY_HEART_RATE));

    uint8_t topic_hrv_packet[10];
    memset(topic_hrv_packet, 0, sizeof(topic_hrv_packet));
    store_u16_fixture(&topic_hrv_packet[0], UINT16_C(800));
    store_u16_fixture(&topic_hrv_packet[2], UINT16_C(810));
    store_u16_fixture(&topic_hrv_packet[4], UINT16_C(820));
    store_u16_fixture(&topic_hrv_packet[6], UINT16_C(830));
    topic_hrv_packet[GOMORE_PRIMITIVES_TOPIC_HRV_COUNT_OFFSET] = 5u;
    assert(gomore_primitives_topic_hrv_ingest(
        &topic_input, topic_hrv_packet, sizeof(topic_hrv_packet)));
    assert(topic_input.hrv_auxiliary_count == 4u &&
           topic_input.hrv_auxiliary[0] == 800u &&
           topic_input.hrv_auxiliary[3] == 830u &&
           topic_hrv_packet[GOMORE_PRIMITIVES_TOPIC_HRV_COUNT_OFFSET] == 5u);
    topic_hrv_packet[GOMORE_PRIMITIVES_TOPIC_HRV_COUNT_OFFSET] = 2u;
    assert(gomore_primitives_topic_hrv_ingest(
        &topic_input, topic_hrv_packet, sizeof(topic_hrv_packet)));
    assert(topic_input.hrv_auxiliary_count == 2u &&
           topic_input.hrv_auxiliary[0] == 800u &&
           topic_input.hrv_auxiliary[1] == 810u &&
           topic_input.hrv_auxiliary[2] == 0u &&
           topic_input.hrv_auxiliary[3] == 0u);
    assert(gomore_primitives_topic_update_take_ready(
        &topic_input, true, true));
    assert(topic_input.ready_flags == 0u);
    gomore_primitives_topic_update_complete(&topic_input, false);
    assert(topic_input.accelerometer_sample_count == 25u &&
           topic_input.raw_optical_sample_count == 25u);
    gomore_primitives_topic_update_complete(&topic_input, true);
    assert(topic_input.accelerometer_sample_count == 0u &&
           topic_input.raw_optical_sample_count == 0u &&
           topic_input.hrv_auxiliary_count == 2u &&
           topic_input.direct_heart_rate == 72.0f);
    topic_input.ready_flags =
        GOMORE_PRIMITIVES_TOPIC_READY_ACCELEROMETER;
    assert(!gomore_primitives_topic_update_take_ready(
        &topic_input, true, true));
    assert(gomore_primitives_topic_update_take_ready(
        &topic_input, true, false));
    assert(!gomore_primitives_topic_update_take_ready(
        &topic_input, false, false));
    assert(!gomore_primitives_topic_raw_optical_ingest(
        &topic_input, topic_raw_packet, sizeof(topic_raw_packet) - 1u));
    assert(!gomore_primitives_topic_heart_rate_ingest(
        &topic_input, NULL, 0u));
    assert(!gomore_primitives_topic_hrv_ingest(
        &topic_input, topic_hrv_packet,
        GOMORE_PRIMITIVES_TOPIC_HRV_COUNT_OFFSET));

    uint8_t host_input_engine[0x39D8];
    memset(host_input_engine, UINT8_C(0xA5), sizeof(host_input_engine));
    store_u32_fixture(&host_input_engine[0x39D4u], 2u);
    float host_accelerometer_sources[3][25];
    float host_raw_optical_source[25];
    for (size_t index = 0u; index < 25u; ++index) {
        host_accelerometer_sources[0][index] = 10.0f + (float)index;
        host_accelerometer_sources[1][index] = 20.0f + (float)index;
        host_accelerometer_sources[2][index] = 30.0f + (float)index;
        host_raw_optical_source[index] = 40.0f + (float)index;
    }
    const uint16_t dormant_hrv_samples[4] = {1u, 2u, 3u, 4u};
    const gomore_primitives_host_input host_input = {
        .unix_seconds = 1000u,
        .timezone_offset_minutes = -300,
        .accelerometer_axes = {
            host_accelerometer_sources[0],
            host_accelerometer_sources[1],
            host_accelerometer_sources[2],
        },
        .accelerometer_sample_count = 25u,
        .raw_optical_samples = host_raw_optical_source,
        .raw_optical_sample_count = 25u,
        .raw_optical_channel_count = 2u,
        .hrv_auxiliary_samples = dormant_hrv_samples,
        .hrv_auxiliary_count = 4u,
        .direct_heart_rate = 72.5f,
        .legacy_zero_word = UINT32_C(0x12345678),
        .wear_state_is_unknown = 1u,
        .mode2_legacy_byte0 = UINT8_C(0x31),
        .mode2_legacy_byte1 = UINT8_C(0x32),
        .raw_optical_binding = UINT32_C(0x20001000),
    };
    const gomore_primitives_host_input_bindings host_input_bindings = {
        .raw_optical_output_binding = UINT32_C(0x20002000),
        .accelerometer_output_bindings = {
            UINT32_C(0x20003000), UINT32_C(0x20003100),
            UINT32_C(0x20003200),
        },
    };
    float host_raw_optical_output[25];
    float host_accelerometer_outputs[3][25];
    memset(&g_host_input_core_trace, 0, sizeof(g_host_input_core_trace));
    active_closure_trace.resample_calls = 0u;
    active_closure_trace.apply_filter_calls = 0u;
    assert(gomore_primitives_host_input_adapter_update(
        host_input_engine, sizeof(host_input_engine), &host_input, 900u,
        host_raw_optical_output, host_accelerometer_outputs,
        &host_input_bindings, closure_resample, closure_apply_filter,
        NULL, host_input_update_core));
    assert(active_closure_trace.resample_calls == 4u &&
           active_closure_trace.apply_filter_calls == 4u &&
           g_host_input_core_trace.calls == 1u &&
           g_host_input_core_trace.state == &host_input_engine[0x140u] &&
           g_host_input_core_trace.elapsed == 100u &&
           load_u32_fixture(&host_input_engine[0x190u]) == 1000u &&
           load_u16_fixture(&host_input_engine[0x18Cu]) ==
               (uint16_t)(int16_t)-300 &&
           load_u32_fixture(&host_input_engine[0x170u]) ==
               UINT32_C(0x20002000) &&
           host_input_engine[0x174u] == 1u &&
           host_input_engine[0x175u] == 1u &&
           load_u32_fixture(&host_input_engine[0x178u]) ==
               UINT32_C(0x20001000) &&
           load_u16_fixture(&host_input_engine[0x17Cu]) == 25u &&
           host_input_engine[0x17Eu] == 1u &&
           host_input_engine[0x17Fu] == 0u &&
           host_input_engine[0x1D4u] == 0u &&
           load_u32_fixture(&host_input_engine[0x1C8u]) ==
               UINT32_C(0x20003000) &&
           load_u32_fixture(&host_input_engine[0x1CCu]) ==
               UINT32_C(0x20003100) &&
           load_u32_fixture(&host_input_engine[0x1D0u]) ==
               UINT32_C(0x20003200) &&
           load_u32_fixture(&host_input_engine[0x16Cu]) ==
               float_bits(72.5f) &&
           load_u32_fixture(&host_input_engine[0x150u]) ==
               UINT32_C(0x12345678) &&
           host_input_engine[0x2F5u] == UINT8_C(0x31) &&
           host_input_engine[0x2F6u] == UINT8_C(0x32) &&
           host_raw_optical_output[0] == 20.5f &&
           host_accelerometer_outputs[0][0] == 11.0f &&
           host_accelerometer_outputs[1][0] == 21.0f &&
           host_accelerometer_outputs[2][0] == 31.0f);
    const unsigned host_core_calls_before = g_host_input_core_trace.calls;
    assert(!gomore_primitives_host_input_adapter_update(
        host_input_engine, 0x39D7u, &host_input, 900u,
        host_raw_optical_output, host_accelerometer_outputs,
        &host_input_bindings, closure_resample, closure_apply_filter,
        NULL, host_input_update_core));
    assert(g_host_input_core_trace.calls == host_core_calls_before);

    gomore_primitives_host_input sensor_update_input = host_input;
    sensor_update_input.unix_seconds = 100u;
    const gomore_primitives_sensor_update_configuration
        sensor_update_configuration = {
            .diagnostics_enabled = true,
            .validation_enabled = false,
            .configured_timestamp_limit = 0u,
            .runtime_present = true,
            .configured_version = 7,
            .runtime_version = 7,
        };
    const gomore_primitives_sensor_update_providers
        sensor_update_providers = {
            .diagnose = sensor_update_diagnose,
            .log_error = sensor_update_log_error,
            .apply = sensor_update_apply,
            .snapshot = sensor_update_snapshot,
        };
    gomore_primitives_sensor_update_state sensor_update_state = {0};
    int32_t sensor_update_status = 99;
    g_sensor_update_trace = (sensor_update_trace){0};
    g_sensor_update_trace.apply_result = 7;
    assert(gomore_primitives_sensor_update_orchestrate(
        &g_sensor_update_trace, &sensor_update_state,
        &sensor_update_input, &sensor_update_configuration,
        &sensor_update_providers, &sensor_update_status));
    assert(sensor_update_status == 7 &&
           sensor_update_state.previous_timestamp == 100u &&
           sensor_update_state.update_flags == 1u &&
           g_sensor_update_trace.diagnose_calls == 1u &&
           g_sensor_update_trace.error_calls == 0u &&
           g_sensor_update_trace.apply_calls == 1u &&
           g_sensor_update_trace.snapshot_calls == 1u &&
           g_sensor_update_trace.input == &sensor_update_input &&
           g_sensor_update_trace.timestamp == 100u &&
           g_sensor_update_trace.order_count == 3u &&
           g_sensor_update_trace.order[0] == 1u &&
           g_sensor_update_trace.order[1] == 2u &&
           g_sensor_update_trace.order[2] == 3u);

    sensor_update_input.unix_seconds = 102u;
    g_sensor_update_trace = (sensor_update_trace){0};
    g_sensor_update_trace.apply_result = -9;
    assert(gomore_primitives_sensor_update_orchestrate(
        &g_sensor_update_trace, &sensor_update_state,
        &sensor_update_input, &sensor_update_configuration,
        &sensor_update_providers, &sensor_update_status));
    assert(sensor_update_status == -9 &&
           g_sensor_update_trace.timestamp == 101u &&
           sensor_update_state.previous_timestamp == 101u &&
           sensor_update_state.update_flags == 2u &&
           g_sensor_update_trace.snapshot_calls == 1u);

    sensor_update_input.unix_seconds = 90u;
    g_sensor_update_trace = (sensor_update_trace){0};
    assert(gomore_primitives_sensor_update_orchestrate(
        &g_sensor_update_trace, &sensor_update_state,
        &sensor_update_input, &sensor_update_configuration,
        &sensor_update_providers, &sensor_update_status));
    assert(sensor_update_status == -4 &&
           sensor_update_state.previous_timestamp == 101u &&
           sensor_update_state.update_flags == 2u &&
           g_sensor_update_trace.error_calls == 1u &&
           g_sensor_update_trace.error == -4 &&
           g_sensor_update_trace.apply_calls == 0u &&
           g_sensor_update_trace.snapshot_calls == 0u);

    sensor_update_state = (gomore_primitives_sensor_update_state){0};
    sensor_update_state.initialization_status = -3;
    g_sensor_update_trace = (sensor_update_trace){0};
    sensor_update_status = 99;
    assert(gomore_primitives_sensor_update_orchestrate(
        &g_sensor_update_trace, &sensor_update_state,
        &sensor_update_input, &sensor_update_configuration,
        &sensor_update_providers, &sensor_update_status));
    assert(sensor_update_status == -3 &&
           g_sensor_update_trace.diagnose_calls == 1u &&
           g_sensor_update_trace.error_calls == 0u &&
           g_sensor_update_trace.apply_calls == 0u);

    sensor_update_state = (gomore_primitives_sensor_update_state){0};
    gomore_primitives_sensor_update_configuration missing_runtime =
        sensor_update_configuration;
    missing_runtime.runtime_present = false;
    g_sensor_update_trace = (sensor_update_trace){0};
    assert(gomore_primitives_sensor_update_orchestrate(
        &g_sensor_update_trace, &sensor_update_state,
        &sensor_update_input, &missing_runtime,
        &sensor_update_providers, &sensor_update_status));
    assert(sensor_update_status == -1 &&
           g_sensor_update_trace.error_calls == 1u &&
           g_sensor_update_trace.error == -1 &&
           g_sensor_update_trace.apply_calls == 0u);

    sensor_update_state = (gomore_primitives_sensor_update_state){0};
    sensor_update_state.previous_timestamp = 10u;
    sensor_update_state.update_flags = UINT32_C(0x80000000);
    sensor_update_input.unix_seconds = 20u;
    g_sensor_update_trace = (sensor_update_trace){0};
    assert(gomore_primitives_sensor_update_orchestrate(
        &g_sensor_update_trace, &sensor_update_state,
        &sensor_update_input, &sensor_update_configuration,
        &sensor_update_providers, &sensor_update_status));
    assert(sensor_update_state.previous_timestamp == 20u &&
           sensor_update_state.update_flags == UINT32_C(0x80000001));

    gomore_primitives_sensor_update_providers incomplete_update_providers =
        sensor_update_providers;
    incomplete_update_providers.apply = NULL;
    sensor_update_status = 99;
    g_sensor_update_trace = (sensor_update_trace){0};
    assert(!gomore_primitives_sensor_update_orchestrate(
        &g_sensor_update_trace, &sensor_update_state,
        &sensor_update_input, &sensor_update_configuration,
        &incomplete_update_providers, &sensor_update_status));
    assert(sensor_update_status == 99 &&
           g_sensor_update_trace.diagnose_calls == 0u);
    float activity_samples[250];
    float activity_differences[249];
    for (size_t index = 0u; index < 250u; ++index) {
        activity_samples[index] = (float)index;
    }
    bool activity_classified = false;
    memset(&g_activity_statistics_trace, 0,
           sizeof(g_activity_statistics_trace));
    g_activity_statistics_trace.responses[0][0] = 12.0f;
    g_activity_statistics_trace.responses[1][0] = 25.0f;
    assert(gomore_primitives_activity_state_classify250(
        activity_samples, 250u, false,
        activity_differences, 249u, activity_statistics_fixture,
        &activity_classified));
    assert(activity_classified && g_activity_statistics_trace.calls == 2u &&
           g_activity_statistics_trace.values[0] == activity_samples &&
           g_activity_statistics_trace.counts[0] == 250u &&
           g_activity_statistics_trace.modes[0] == 3u &&
           g_activity_statistics_trace.values[1] == activity_differences &&
           g_activity_statistics_trace.counts[1] == 249u &&
           g_activity_statistics_trace.modes[1] == 7u &&
           activity_differences[0] == 1.0f &&
           activity_differences[248] == 1.0f);

    activity_samples[0] = 0.0f;
    for (size_t index = 0u; index < 249u; ++index) {
        const float difference = ((index / 5u) & 1u) == 0u
            ? 1.0f : -1.0f;
        activity_samples[index + 1u] = activity_samples[index] + difference;
    }
    memset(&g_activity_statistics_trace, 0,
           sizeof(g_activity_statistics_trace));
    g_activity_statistics_trace.responses[0][1] = 8.0f;
    g_activity_statistics_trace.responses[1][0] = 10.0f;
    g_activity_statistics_trace.responses[1][3] = 2.5f;
    assert(gomore_primitives_activity_state_classify250(
        activity_samples, 250u, true,
        activity_differences, 249u, activity_statistics_fixture,
        &activity_classified));
    assert(activity_classified && g_activity_statistics_trace.calls == 2u &&
           g_activity_statistics_trace.values[0] == activity_differences &&
           g_activity_statistics_trace.counts[0] == 249u &&
           g_activity_statistics_trace.modes[0] == 3u &&
           g_activity_statistics_trace.values[1] == activity_samples &&
           g_activity_statistics_trace.counts[1] == 250u &&
           g_activity_statistics_trace.modes[1] == 3u);

    memset(&g_activity_statistics_trace, 0,
           sizeof(g_activity_statistics_trace));
    g_activity_statistics_trace.responses[0][1] = 8.0f;
    g_activity_statistics_trace.responses[1][0] = 13.0f;
    assert(gomore_primitives_activity_state_classify250(
        activity_samples, 250u, true,
        activity_differences, 249u, activity_statistics_fixture,
        &activity_classified));
    assert(!activity_classified);
    memset(&g_activity_statistics_trace, 0,
           sizeof(g_activity_statistics_trace));
    g_activity_statistics_trace.responses[0][1] = 7.0f;
    g_activity_statistics_trace.responses[1][0] = 13.0f;
    assert(gomore_primitives_activity_state_classify250(
        activity_samples, 250u, true,
        activity_differences, 249u, activity_statistics_fixture,
        &activity_classified));
    assert(activity_classified);
    const unsigned activity_calls_before = g_activity_statistics_trace.calls;
    const float activity_difference_before = activity_differences[0];
    assert(!gomore_primitives_activity_state_classify250(
        activity_samples, 249u, true,
        activity_differences, 249u, activity_statistics_fixture,
        &activity_classified));
    assert(g_activity_statistics_trace.calls == activity_calls_before &&
           activity_differences[0] == activity_difference_before);

    float activity_axes[3][25];
    const float *activity_axis_pointers[3] = {
        activity_axes[0], activity_axes[1], activity_axes[2],
    };
    float activity_tail[27];
    for (size_t axis = 0u; axis < 3u; ++axis) {
        for (size_t index = 0u; index < 25u; ++index) {
            activity_axes[axis][index] = axis == 0u ? 1000.0f : 0.0f;
        }
    }
    for (size_t index = 0u; index < 27u; ++index) {
        activity_tail[index] = 500.0f + (float)index;
    }
    const gomore_primitives_activity_window_providers activity_providers = {
        {activity_axis_pointers[0], activity_axis_pointers[1],
         activity_axis_pointers[2]},
        false,
        activity_square_root_fixture,
        activity_statistics_fixture,
    };
    gomore_primitives_activity_window_input activity_input = {
        activity_tail, 25, 1u,
    };
    gomore_primitives_activity_window_output activity_window_output = {
        UINT8_C(0xA5), UINT8_C(0xA5),
    };
    gomore_primitives_activity_window_state activity_window_state;

    memset(&activity_window_state, 0, sizeof(activity_window_state));
    activity_window_state.state = 0u;
    activity_window_state.reset_threshold = 0.5f;
    activity_window_state.accumulated_samples = 225;
    activity_window_state.positive_windows = 4u;
    for (size_t index = 0u; index < 250u; ++index) {
        activity_window_state.window[index] = (float)index;
    }
    memset(&g_activity_statistics_trace, 0,
           sizeof(g_activity_statistics_trace));
    g_activity_statistics_trace.responses[0][0] = 12.0f;
    g_activity_statistics_trace.responses[1][0] = 25.0f;
    assert(gomore_primitives_activity_window_update(
        &activity_window_state, 1.0f, &activity_input,
        &activity_providers, activity_differences, 249u,
        &activity_window_output));
    assert(activity_window_state.state == 4u &&
           activity_window_state.hold_samples == 180 &&
           activity_window_state.accumulated_samples == 0 &&
           activity_window_state.transition_count == 0 &&
           activity_window_state.positive_windows == 0u &&
           activity_window_state.negative_windows == 0u &&
           activity_window_state.window[0] == 25.0f &&
           activity_window_state.window[224] == 249.0f &&
           activity_window_state.window[225] == 500.0f &&
           activity_window_state.window[249] == 524.0f &&
           activity_window_output.activity == 1u &&
           activity_window_output.confidence == 0u);

    memset(&activity_window_state, 0, sizeof(activity_window_state));
    activity_window_state.state = 2u;
    activity_window_state.reset_threshold = 0.5f;
    activity_window_state.hold_samples = 500;
    activity_window_state.accumulated_samples = 225;
    activity_window_state.negative_windows = 4u;
    memset(&g_activity_statistics_trace, 0,
           sizeof(g_activity_statistics_trace));
    assert(gomore_primitives_activity_window_update(
        &activity_window_state, 1.0f, &activity_input,
        &activity_providers, activity_differences, 249u,
        &activity_window_output));
    assert(activity_window_state.state == 1u &&
           activity_window_state.hold_samples == 600 &&
           activity_window_state.reset_threshold == 0.5f &&
           activity_window_state.accumulated_samples == 0 &&
           activity_window_state.positive_windows == 0u &&
           activity_window_state.negative_windows == 0u &&
           activity_window_output.activity == 0u &&
           activity_window_output.confidence == 0u);

    gomore_primitives_activity_window_providers alternate_activity_providers =
        activity_providers;
    alternate_activity_providers.axes[0] = NULL;
    alternate_activity_providers.axes[1] = NULL;
    alternate_activity_providers.axes[2] = NULL;
    alternate_activity_providers.alternate_conditioning = true;
    alternate_activity_providers.square_root = NULL;
    memset(&activity_window_state, 0, sizeof(activity_window_state));
    activity_window_state.score = 0.05f;
    activity_window_state.state = 3u;
    activity_window_state.reset_threshold = 2.0f;
    assert(gomore_primitives_activity_window_update(
        &activity_window_state, 1.0f, &activity_input,
        &alternate_activity_providers, activity_differences, 249u,
        &activity_window_output));
    assert(float_bits(activity_window_state.score) ==
               UINT32_C(0x3DC28F5C) &&
           activity_window_state.state == 3u &&
           activity_window_state.accumulated_samples == 25 &&
           activity_window_output.activity == 0u &&
           activity_window_output.confidence == 1u);

    memset(&activity_window_state, 0, sizeof(activity_window_state));
    activity_window_state.state = 1u;
    activity_window_state.reset_threshold = 0.5f;
    activity_window_state.hold_samples = 180;
    activity_window_state.transition_count = 179;
    assert(gomore_primitives_activity_window_update(
        &activity_window_state, 1.0f, &activity_input,
        &activity_providers, activity_differences, 249u,
        &activity_window_output));
    assert(activity_window_state.state == 2u &&
           activity_window_state.transition_count == 0 &&
           activity_window_output.activity == 0u &&
           activity_window_output.confidence == 1u);

    memset(&activity_window_state, 0, sizeof(activity_window_state));
    activity_window_state.score = 1.0f;
    activity_window_state.state = 2u;
    activity_window_state.reset_threshold = 0.5f;
    activity_window_state.transition_count = 3;
    activity_window_state.accumulated_samples = 200;
    activity_window_state.positive_windows = 4u;
    activity_window_state.negative_windows = 2u;
    assert(gomore_primitives_activity_window_update(
        &activity_window_state, 1.0f, &activity_input,
        &activity_providers, activity_differences, 249u,
        &activity_window_output));
    assert(activity_window_state.score == 0.9f &&
           activity_window_state.state == 3u &&
           activity_window_state.reset_threshold == 0.5f &&
           activity_window_state.transition_count == 0 &&
           activity_window_state.accumulated_samples == 0 &&
           activity_window_state.positive_windows == 0u &&
           activity_window_state.negative_windows == 0u &&
           activity_window_output.activity == 0u &&
           activity_window_output.confidence == 0u);

    memset(&activity_window_state, 0, sizeof(activity_window_state));
    activity_window_state.state = 0u;
    activity_window_state.reset_threshold = 0.5f;
    activity_window_state.accumulated_samples = 225;
    activity_input.samples = NULL;
    activity_input.channel_count = 0u;
    assert(gomore_primitives_activity_window_update(
        &activity_window_state, 1.0f, &activity_input,
        &activity_providers, activity_differences, 249u,
        &activity_window_output));
    assert(activity_window_state.state == 4u &&
           activity_window_state.hold_samples == 180 &&
           activity_window_output.activity == 1u &&
           activity_window_output.confidence == 0u);

    memset(&activity_window_state, 0, sizeof(activity_window_state));
    activity_window_state.state = 0u;
    activity_window_state.reset_threshold = 0.5f;
    activity_input.samples = activity_tail;
    activity_input.sample_count = 26;
    activity_input.channel_count = 1u;
    assert(gomore_primitives_activity_window_update(
        &activity_window_state, 1.0f, &activity_input,
        &activity_providers, activity_differences, 249u,
        &activity_window_output));
    assert(activity_window_state.state == 0u &&
           (uint32_t)activity_window_state.transition_count ==
               float_bits(activity_tail[25]) &&
           activity_window_state.accumulated_samples == 25 &&
           activity_window_output.activity == UINT8_C(0xFF) &&
           activity_window_output.confidence == 1u);

    const gomore_primitives_activity_window_state activity_state_before =
        activity_window_state;
    const gomore_primitives_activity_window_output activity_output_before =
        activity_window_output;
    activity_input.sample_count = -1;
    assert(!gomore_primitives_activity_window_update(
        &activity_window_state, 1.0f, &activity_input,
        &activity_providers, activity_differences, 249u,
        &activity_window_output));
    assert(memcmp(&activity_window_state, &activity_state_before,
                  sizeof(activity_window_state)) == 0 &&
           memcmp(&activity_window_output, &activity_output_before,
                  sizeof(activity_window_output)) == 0);
    activity_input.samples = activity_tail;
    activity_input.sample_count = 25;
    activity_input.channel_count = 1u;

    gomore_primitives_respiratory_rate_state respiratory_state;
    gomore_primitives_respiratory_rate_input respiratory_input = {
        &respiratory_state, false, 1u, 1u,
    };
    const gomore_primitives_respiratory_rate_providers
        respiratory_providers = {
            respiratory_estimate_fixture,
            respiratory_square_root_fixture,
        };
    respiratory_estimate_trace respiratory_trace = {
        .rate = 12.0f,
        .confidence = 1.0f,
    };
    float respiratory_output[2] = {-9.0f, -9.0f};
    uint32_t respiratory_status = UINT32_MAX;
    memset(&respiratory_state, 0, sizeof(respiratory_state));
    assert(gomore_primitives_respiratory_rate_update(
        &respiratory_state, 1u, &respiratory_input,
        &respiratory_trace, &respiratory_providers,
        respiratory_output, &respiratory_status));
    assert(respiratory_trace.calls == 1u &&
           respiratory_trace.elapsed == 1u &&
           respiratory_trace.input == &respiratory_state &&
           respiratory_trace.status == 0u &&
           respiratory_status == 0u &&
           respiratory_state.modulo_counter == 1u &&
           respiratory_state.primary_codes[0] == 1u &&
           respiratory_state.secondary_codes[0] == 1u &&
           respiratory_state.rate_history[4] == 12.0f &&
           respiratory_state.confidence_history[4] == 1.0f &&
           respiratory_output[0] == 12.0f &&
           respiratory_output[1] > 0.759f &&
           respiratory_output[1] < 0.761f);

    memset(&respiratory_state, 0, sizeof(respiratory_state));
    respiratory_trace = (respiratory_estimate_trace){
        .rate = 30.0f,
        .confidence = 0.8f,
        .result = 1,
    };
    respiratory_input.input_unavailable = true;
    respiratory_input.secondary_code = 0u;
    respiratory_input.primary_code = 0u;
    assert(gomore_primitives_respiratory_rate_update(
        &respiratory_state, 3u, &respiratory_input,
        &respiratory_trace, &respiratory_providers,
        respiratory_output, &respiratory_status));
    assert(respiratory_trace.status == UINT32_C(0x40));
    assert(respiratory_status == UINT32_C(0x78));
    assert(respiratory_state.modulo_counter == 3u);
    assert(respiratory_state.primary_codes[0] == 2u);
    assert(respiratory_state.secondary_codes[0] == 2u);
    assert(respiratory_state.rate_history[0] == 0.0f);
    assert(respiratory_state.rate_history[4] == 25.0f);
    assert(respiratory_output[0] == 25.0f);
    assert(float_bits(respiratory_output[1]) == UINT32_C(0x3EFC8BC3));

    memset(&respiratory_state, 0, sizeof(respiratory_state));
    respiratory_trace = (respiratory_estimate_trace){
        .rate = 0.0f,
        .confidence = 1.0f,
    };
    respiratory_input.input_unavailable = false;
    assert(gomore_primitives_respiratory_rate_update(
        &respiratory_state, 1u, &respiratory_input,
        &respiratory_trace, &respiratory_providers,
        respiratory_output, &respiratory_status));
    assert(respiratory_status == UINT32_C(0x10) &&
           respiratory_output[0] == -1.0f &&
           respiratory_output[1] == 1.0f);

    const gomore_primitives_respiratory_rate_state respiratory_before =
        respiratory_state;
    respiratory_output[0] = 3.0f;
    respiratory_output[1] = 4.0f;
    respiratory_status = 5u;
    assert(!gomore_primitives_respiratory_rate_update(
        &respiratory_state, 1u, &respiratory_input,
        &respiratory_trace, NULL, respiratory_output,
        &respiratory_status));
    assert(memcmp(&respiratory_state, &respiratory_before,
                  sizeof(respiratory_state)) == 0 &&
           respiratory_output[0] == 3.0f &&
           respiratory_output[1] == 4.0f &&
           respiratory_status == 5u);

    float optical_selected[2] = {9.0f, 9.0f};
    assert(gomore_primitives_optical_period_candidates_select(
        -1.0f, 0.0f, -1.0f, 0.0f,
        15.0f, 0.6f, optical_selected));
    assert(optical_selected[0] == 15.0f &&
           optical_selected[1] == 0.6f);
    assert(gomore_primitives_optical_period_candidates_select(
        -1.0f, 0.0f, -1.0f, 0.0f,
        26.0f, 0.6f, optical_selected));
    assert(optical_selected[0] == -1.0f && optical_selected[1] == 0.0f);
    assert(gomore_primitives_optical_period_candidates_select(
        12.0f, 0.6f, 12.5f, 0.7f,
        -1.0f, 0.0f, optical_selected));
    assert(optical_selected[0] == 12.25f &&
           float_bits(optical_selected[1]) == UINT32_C(0x3F47AE14));
    assert(gomore_primitives_optical_period_candidates_select(
        12.0f, 0.2f, 16.0f, 0.25f,
        14.0f, 0.75f, optical_selected));
    assert(optical_selected[0] == 14.0f &&
           optical_selected[1] == 0.75f);
    assert(!gomore_primitives_optical_period_candidates_select(
        0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, NULL));

    gomore_primitives_optical_interval_state optical_interval_state;
    gomore_primitives_optical_period_workspace optical_period_workspace;
    const gomore_primitives_optical_period_providers
        optical_period_providers = {
            .initialize_filter_state = closure_mode2_initialize,
            .apply_filter = closure_apply_filter,
            .round_value = positive_round_fixture,
            .feature_math = locomotion_reduce_math,
        };
    const float zero_optical_period_input[25] = {0.0f};
    float optical_period_output[2] = {9.0f, 9.0f};
    int32_t optical_period_status = -1;
    memset(&optical_interval_state, 0, sizeof(optical_interval_state));
    memset(&optical_period_workspace, 0, sizeof(optical_period_workspace));
    assert(gomore_primitives_large_filter_state_initialize(
        &optical_interval_state, sizeof(optical_interval_state),
        closure_mode2_initialize));
    active_closure_trace.apply_filter_calls = 0u;
    for (size_t index = 0u; index < 10u; ++index) {
        assert(gomore_primitives_optical_period_estimate(
            &optical_interval_state, 0u, zero_optical_period_input, 0u,
            &optical_period_providers, &optical_period_workspace,
            optical_period_output, &optical_period_status));
        assert(optical_period_status == 1 &&
               optical_period_output[0] == -1.0f &&
               optical_period_output[1] == 0.0f &&
               optical_interval_state.current_window == index + 1u);
    }
    assert(active_closure_trace.apply_filter_calls == 10u &&
           optical_interval_state.interval_count == 0u &&
           optical_interval_state.position_tolerance_scale == -0.75f &&
           optical_interval_state.amplitude_tolerance_scale == -0.75f);
    const gomore_primitives_optical_interval_state optical_period_before =
        optical_interval_state;
    optical_period_output[0] = 7.0f;
    optical_period_output[1] = 8.0f;
    optical_period_status = 9;
    assert(!gomore_primitives_optical_period_estimate(
        &optical_interval_state, 0u, zero_optical_period_input, 0u,
        NULL, &optical_period_workspace,
        optical_period_output, &optical_period_status));
    assert(memcmp(&optical_interval_state, &optical_period_before,
                  sizeof(optical_interval_state)) == 0 &&
           optical_period_output[0] == 7.0f &&
           optical_period_output[1] == 8.0f &&
           optical_period_status == 9);

    memset(&optical_interval_state, 0, sizeof(optical_interval_state));
    optical_interval_state.current_window = 20u;
    for (size_t index = 0u; index < 250u; ++index) {
        optical_interval_state.signal[index] =
            (float)(index * index);
    }
    const uint8_t interval_ends[2] = {20u, 40u};
    const uint8_t interval_starts[2] = {10u, 30u};
    float interval_mean = -1.0f;
    assert(gomore_primitives_optical_interval_merge(
        &optical_interval_state, interval_ends, interval_starts, 2u,
        &interval_mean));
    assert(optical_interval_state.interval_count == 2u &&
           optical_interval_state.intervals[0].end_position == 270u &&
           optical_interval_state.intervals[0].start_position == 260u &&
           optical_interval_state.intervals[0].peak_position == 269u &&
           optical_interval_state.intervals[1].end_position == 290u &&
           optical_interval_state.intervals[1].start_position == 280u &&
           optical_interval_state.intervals[1].peak_position == 289u &&
           interval_mean == 500.0f);

    memset(&optical_interval_state, 0, sizeof(optical_interval_state));
    optical_interval_state.current_window = 20u;
    optical_interval_state.interval_count = 2u;
    optical_interval_state.intervals[0] =
        (gomore_primitives_optical_interval_record){
            270u, 260u, 269u, 0u, 400.0f, 100.0f,
        };
    optical_interval_state.intervals[1] =
        (gomore_primitives_optical_interval_record){
            310u, 300u, 309u, 0u, 1600.0f, 900.0f,
        };
    for (size_t index = 0u; index < 250u; ++index) {
        optical_interval_state.signal[index] =
            (float)(index * index);
    }
    const uint8_t early_end[1] = {5u};
    const uint8_t early_start[1] = {1u};
    assert(gomore_primitives_optical_interval_merge(
        &optical_interval_state, early_end, early_start, 1u,
        &interval_mean));
    assert(optical_interval_state.interval_count == 3u &&
           optical_interval_state.intervals[0].end_position == 255u &&
           optical_interval_state.intervals[0].start_position == 251u &&
           optical_interval_state.intervals[1].end_position == 270u &&
           optical_interval_state.intervals[2].end_position == 310u &&
           float_bits(interval_mean) == UINT32_C(0x43AAAAAB));

    optical_interval_state.current_window = 21u;
    assert(gomore_primitives_optical_interval_merge(
        &optical_interval_state, NULL, NULL, 0u, &interval_mean));
    assert(optical_interval_state.intervals[0].end_position == 230u &&
           optical_interval_state.intervals[0].start_position == 226u &&
           optical_interval_state.intervals[2].end_position == 285u);

    const gomore_primitives_optical_interval_state interval_before =
        optical_interval_state;
    const uint8_t invalid_interval_end[1] = {250u};
    interval_mean = 7.0f;
    assert(!gomore_primitives_optical_interval_merge(
        &optical_interval_state, invalid_interval_end, early_start, 1u,
        &interval_mean));
    assert(memcmp(&optical_interval_state, &interval_before,
                  sizeof(optical_interval_state)) == 0 &&
           interval_mean == 7.0f);

    optical_interval_state = interval_before;
    optical_interval_state.interval_count = 2u;
    optical_interval_state.intervals[1].end_position =
        optical_interval_state.intervals[0].end_position;
    assert(!gomore_primitives_optical_interval_merge(
        &optical_interval_state, NULL, NULL, 0u, &interval_mean));
    assert(optical_interval_state.interval_count == 0u);

    uint16_t sleep_classifier_conv_weights[192] = {0u};
    uint16_t sleep_classifier_half_parameters[8] = {0u};
    int8_t sleep_classifier_affine_weights[3840] = {0};
    int16_t sleep_classifier_affine_bias[96] = {0};
    gomore_primitives_sleep_stage_classifier_model sleep_classifier_model;
    memset(&sleep_classifier_model, 0, sizeof(sleep_classifier_model));
    for (size_t index = 0u; index < 7u; ++index) {
        sleep_classifier_model.convolution[index] =
            (gomore_primitives_sleep_stage_conv_model){
                .weights_half = sleep_classifier_conv_weights,
                .weight_count = sizeof(sleep_classifier_conv_weights) /
                    sizeof(sleep_classifier_conv_weights[0]),
                .scale_half = sleep_classifier_half_parameters,
                .offset_half = sleep_classifier_half_parameters,
                .variance_half = sleep_classifier_half_parameters,
                .mean_half = sleep_classifier_half_parameters,
                .parameter_count =
                    sizeof(sleep_classifier_half_parameters) /
                    sizeof(sleep_classifier_half_parameters[0]),
            };
    }
    sleep_classifier_model.projection[0] =
        (gomore_primitives_sleep_stage_affine_model){
            sleep_classifier_affine_weights,
            sizeof(sleep_classifier_affine_weights),
            32u, 120u, 0.0f,
            sleep_classifier_affine_bias,
            sizeof(sleep_classifier_affine_bias) /
                sizeof(sleep_classifier_affine_bias[0]),
        };
    sleep_classifier_model.projection[1] =
        (gomore_primitives_sleep_stage_affine_model){
            sleep_classifier_affine_weights,
            sizeof(sleep_classifier_affine_weights),
            32u, 32u, 0.0f,
            sleep_classifier_affine_bias,
            sizeof(sleep_classifier_affine_bias) /
                sizeof(sleep_classifier_affine_bias[0]),
        };
    for (size_t index = 0u; index < 2u; ++index) {
        sleep_classifier_model.recurrent[index].input =
            (gomore_primitives_sleep_stage_affine_model){
                sleep_classifier_affine_weights,
                sizeof(sleep_classifier_affine_weights),
                96u, 32u, 0.0f,
                sleep_classifier_affine_bias,
                sizeof(sleep_classifier_affine_bias) /
                    sizeof(sleep_classifier_affine_bias[0]),
            };
        sleep_classifier_model.recurrent[index].recurrent =
            sleep_classifier_model.recurrent[index].input;
    }
    sleep_classifier_model.post_recurrent =
        sleep_classifier_model.projection[1];
    sleep_classifier_model.output =
        (gomore_primitives_sleep_stage_affine_model){
            sleep_classifier_affine_weights,
            sizeof(sleep_classifier_affine_weights),
            4u, 32u, 0.0f,
            sleep_classifier_affine_bias,
            sizeof(sleep_classifier_affine_bias) /
                sizeof(sleep_classifier_affine_bias[0]),
        };
    gomore_primitives_sleep_stage_classifier_context
        sleep_classifier_context = {
            .mode_below_100 = &sleep_classifier_model,
            .mode_100_and_above = &sleep_classifier_model,
            .math = {
                sleep_classifier_square_root_fixture,
                sleep_classifier_exponential_fixture,
                sleep_classifier_logistic_fixture,
                sleep_classifier_tanh_fixture,
            },
        };
    gomore_primitives_sleep_stage_stream_state classifier_state;
    memset(&classifier_state, 0, sizeof(classifier_state));
    for (size_t index = 0u; index < 90u; ++index) {
        classifier_state.stage_window[index] = (float)index * 0.01f;
    }
    const int8_t sleep_classifier_adjustment[4] = {1, -2, 3, -4};
    gomore_primitives_sleep_stage_classifier_result classifier_result = {
        9.0f, {9.0f, 9.0f, 9.0f}, -1,
    };
    assert(gomore_primitives_sleep_stage_classify(
        &classifier_result, &classifier_state, 1u,
        sleep_classifier_adjustment, &sleep_classifier_context));
    assert(classifier_result.primary > 0.2599f &&
           classifier_result.primary < 0.2601f &&
           classifier_result.candidates[0] > 0.2299f &&
           classifier_result.candidates[0] < 0.2301f &&
           classifier_result.candidates[1] > 0.2799f &&
           classifier_result.candidates[1] < 0.2801f &&
           classifier_result.candidates[2] > 0.2099f &&
           classifier_result.candidates[2] < 0.2101f &&
           classifier_result.selected == 2);
    const float *classifier_pool =
        (const float *)(const void *)classifier_state.tensor_storage;
    const float first_hidden = classifier_pool[1632];
    assert(first_hidden > 0.000022f && first_hidden < 0.000024f);
    assert(gomore_primitives_sleep_stage_classify(
        &classifier_result, &classifier_state, 1u,
        sleep_classifier_adjustment, &sleep_classifier_context));
    assert(classifier_pool[1632] > first_hidden &&
           classifier_pool[1632] < 0.000035f);
    assert(gomore_primitives_sleep_stage_classify(
        &classifier_result, &classifier_state, 2u, NULL, NULL));
    assert(classifier_result.primary == 1.0f &&
           classifier_result.candidates[0] == 0.0f &&
           classifier_result.candidates[1] == 0.0f &&
           classifier_result.candidates[2] == 0.0f &&
           classifier_result.selected == 0);
    classifier_state.mode = 100u;
    sleep_classifier_context.mode_100_and_above = NULL;
    const gomore_primitives_sleep_stage_stream_state classifier_before =
        classifier_state;
    classifier_result.primary = 9.0f;
    assert(!gomore_primitives_sleep_stage_classify(
        &classifier_result, &classifier_state, 1u,
        sleep_classifier_adjustment, &sleep_classifier_context));
    assert(memcmp(&classifier_state, &classifier_before,
                  sizeof(classifier_state)) == 0 &&
           classifier_result.primary == 9.0f);

    gomore_primitives_sleep_stage_stream_state stage_stream;
    gomore_primitives_sleep_stage_peak_input stage_peaks;
    gomore_primitives_sleep_stage_status stage_status = {
        .value = 0.0f,
        .packed_value = 1u,
        .reserved = 0u,
        .enabled = 0u,
    };
    uint8_t stage_activity[27] = {0u};
    uint8_t stage_output[3] = {
        UINT8_C(0xA5), UINT8_C(0xA5), UINT8_C(0xA5),
    };
    memset(&stage_stream, 0, sizeof(stage_stream));
    memset(&stage_peaks, 0, sizeof(stage_peaks));
    assert(gomore_primitives_sleep_stage_stream_update(
        &stage_stream, 30u, &stage_peaks,
        stage_activity, sizeof(stage_activity), &stage_status,
        stage_output, NULL, 0u, NULL, NULL, NULL));
    assert(stage_output[0] == 0u && stage_output[1] == 0u &&
           stage_output[2] == 0u && stage_stream.packed_stages[0] == 8u &&
           stage_stream.previous_timestamp == 30u &&
           stage_stream.previous_packed_value == 1u);

    memset(&stage_stream, 0, sizeof(stage_stream));
    memset(&stage_peaks, 0, sizeof(stage_peaks));
    stage_stream.active = 1u;
    stage_stream.batch_count = 2u;
    stage_stream.mode = 100u;
    stage_stream.update_counter = 4u;
    stage_peaks.positions[0] = 5u;
    stage_peaks.positions[1] = 10u;
    stage_peaks.count_with_flags = 2u;
    stage_activity[26] = 1u;
    memset(stage_output, UINT8_C(0xA5), sizeof(stage_output));
    assert(gomore_primitives_sleep_stage_stream_update(
        &stage_stream, 60u, &stage_peaks,
        stage_activity, sizeof(stage_activity), &stage_status,
        stage_output, NULL, 0u, NULL, NULL, NULL));
    assert(stage_stream.batch_count == 3u &&
           stage_stream.peak_count == 2u &&
           stage_stream.peaks[0] == 55 && stage_stream.peaks[1] == 60 &&
           stage_output[0] == UINT8_C(0xA5) &&
           stage_output[1] == 0u && stage_output[2] == 0u);

    memset(&stage_stream, 0, sizeof(stage_stream));
    memset(&stage_peaks, 0, sizeof(stage_peaks));
    stage_stream.active = 1u;
    stage_stream.batch_count = 2u;
    stage_stream.classifier_iteration = 1u;
    for (size_t index = 0u; index < 90u; ++index) {
        stage_stream.stage_window[index] = (float)index;
    }
    uint8_t stage_mode_table[11] = {0u};
    stage_mode_table[6] = 100u;
    g_sleep_stage_classifier_result =
        (gomore_primitives_sleep_stage_classifier_result){
            9.0f, {1.0f, 3.0f, 2.0f}, 1,
        };
    g_sleep_stage_classifier_calls = 0u;
    memset(stage_output, UINT8_C(0xA5), sizeof(stage_output));
    assert(gomore_primitives_sleep_stage_stream_update(
        &stage_stream, 60u, &stage_peaks,
        stage_activity, sizeof(stage_activity), &stage_status,
        stage_output, stage_mode_table, sizeof(stage_mode_table),
        NULL, classify_sleep_stage_stream, NULL));
    assert(g_sleep_stage_classifier_calls == 1u &&
           g_sleep_stage_classifier_iteration == 1u &&
           stage_stream.classifier_iteration == 0u &&
           stage_stream.selected_stage == 1 &&
           stage_stream.stage_window[0] == 30.0f &&
           stage_stream.stage_window[59] == 89.0f &&
           stage_stream.packed_stages[0] == 4u &&
           stage_output[0] == 1u && stage_output[1] == 1u &&
           stage_output[2] == 1u);

    memset(&stage_stream, 0, sizeof(stage_stream));
    memset(&stage_peaks, 0, sizeof(stage_peaks));
    stage_stream.active = 1u;
    stage_stream.batch_count = 31u;
    stage_stream.peak_count = 2u;
    stage_stream.peaks[0] = 740;
    stage_stream.peaks[1] = 760;
    stage_stream.update_counter = 7u;
    stage_peaks.positions[0] = 10u;
    stage_peaks.count_with_flags = 1u;
    g_sleep_stage_classifier_result =
        (gomore_primitives_sleep_stage_classifier_result){
            9.0f, {1.0f, 3.0f, 2.0f}, -1,
        };
    memset(stage_output, UINT8_C(0xA5), sizeof(stage_output));
    assert(gomore_primitives_sleep_stage_stream_update(
        &stage_stream, 60u, &stage_peaks,
        stage_activity, sizeof(stage_activity), &stage_status,
        stage_output, stage_mode_table, sizeof(stage_mode_table),
        NULL, classify_sleep_stage_stream, NULL));
    assert(stage_stream.batch_count == 2u &&
           stage_stream.update_counter == 8u &&
           stage_stream.peak_count == 2u &&
           stage_stream.peaks[0] == 10 && stage_stream.peaks[1] == 35 &&
           stage_stream.classifier_iteration == 2u &&
           stage_output[0] == UINT8_C(0xA5) &&
           stage_output[1] == 0u && stage_output[2] == 1u);

    memset(&stage_stream, 0, sizeof(stage_stream));
    memset(&stage_peaks, 0, sizeof(stage_peaks));
    stage_peaks.count_with_flags = 17u;
    const gomore_primitives_sleep_stage_stream_state stage_stream_before =
        stage_stream;
    memset(stage_output, UINT8_C(0xA5), sizeof(stage_output));
    assert(!gomore_primitives_sleep_stage_stream_update(
        &stage_stream, 60u, &stage_peaks,
        stage_activity, sizeof(stage_activity), &stage_status,
        stage_output, NULL, 0u, NULL, NULL, NULL));
    assert(memcmp(&stage_stream, &stage_stream_before,
                  sizeof(stage_stream)) == 0 &&
           stage_output[0] == UINT8_C(0xA5) &&
           stage_output[1] == UINT8_C(0xA5) &&
           stage_output[2] == UINT8_C(0xA5));

    float peak_match_signal[250];
    float peak_match_workspace[25];
    uint8_t peak_match_candidates[20];
    uint8_t peak_match_references[20];
    memset(peak_match_signal, 0, sizeof(peak_match_signal));
    for (size_t index = 0u; index < 250u; ++index) {
        peak_match_signal[index] = 10.0f;
    }
    const uint8_t regular_peaks[4] = {20u, 40u, 60u, 80u};
    memcpy(peak_match_candidates, regular_peaks, sizeof(regular_peaks));
    memcpy(peak_match_references, regular_peaks, sizeof(regular_peaks));
    peak_match_signal[12] = 0.0f;
    peak_match_signal[32] = 0.0f;
    peak_match_signal[52] = 0.0f;
    peak_match_signal[72] = 0.0f;
    uint8_t peak_match_candidate_count = 4u;
    uint8_t peak_match_reference_count = 4u;
    float peak_match_median = -1.0f;
    assert(gomore_primitives_peak_candidate_match(
        peak_match_signal, 250u,
        peak_match_candidates, peak_match_references,
        &peak_match_candidate_count, &peak_match_reference_count,
        &peak_match_median, peak_match_workspace,
        sort_values, compare_float, square_value,
        activity_square_root_fixture));
    const uint8_t expected_valleys[4] = {12u, 32u, 52u, 72u};
    assert(peak_match_candidate_count == 4u &&
           peak_match_reference_count == 4u &&
           peak_match_median == 20.0f &&
           memcmp(peak_match_candidates, regular_peaks, 4u) == 0 &&
           memcmp(peak_match_references, expected_valleys, 4u) == 0);

    const uint8_t offset_references[4] = {18u, 38u, 58u, 78u};
    memcpy(peak_match_candidates, regular_peaks, sizeof(regular_peaks));
    memcpy(peak_match_references, offset_references,
           sizeof(offset_references));
    peak_match_candidate_count = 4u;
    peak_match_reference_count = 4u;
    assert(gomore_primitives_peak_candidate_match(
        peak_match_signal, 250u,
        peak_match_candidates, peak_match_references,
        &peak_match_candidate_count, &peak_match_reference_count,
        &peak_match_median, peak_match_workspace,
        sort_values, compare_float, square_value,
        activity_square_root_fixture));
    assert(peak_match_candidate_count == 4u &&
           peak_match_reference_count == 4u &&
           peak_match_median == 20.0f &&
           memcmp(peak_match_references, offset_references, 4u) == 0);

    const uint8_t outlier_peaks[5] = {20u, 40u, 60u, 80u, 100u};
    memcpy(peak_match_candidates, outlier_peaks, sizeof(outlier_peaks));
    memcpy(peak_match_references, outlier_peaks, sizeof(outlier_peaks));
    peak_match_signal[20] = 1.0f;
    peak_match_signal[40] = 2.0f;
    peak_match_signal[60] = 3.0f;
    peak_match_signal[80] = 4.0f;
    peak_match_signal[100] = 100.0f;
    peak_match_candidate_count = 5u;
    peak_match_reference_count = 5u;
    assert(gomore_primitives_peak_candidate_match(
        peak_match_signal, 250u,
        peak_match_candidates, peak_match_references,
        &peak_match_candidate_count, &peak_match_reference_count,
        &peak_match_median, peak_match_workspace,
        sort_values, compare_float, square_value,
        activity_square_root_fixture));
    assert(peak_match_candidate_count == 4u &&
           peak_match_reference_count == 4u &&
           peak_match_median == 20.0f &&
           memcmp(peak_match_candidates, regular_peaks, 4u) == 0 &&
           memcmp(peak_match_references, expected_valleys, 4u) == 0);

    peak_match_candidates[0] = 20u;
    peak_match_references[0] = 20u;
    peak_match_candidate_count = 1u;
    peak_match_reference_count = 1u;
    peak_match_median = 7.0f;
    assert(!gomore_primitives_peak_candidate_match(
        peak_match_signal, 250u,
        peak_match_candidates, peak_match_references,
        &peak_match_candidate_count, &peak_match_reference_count,
        &peak_match_median, peak_match_workspace,
        sort_values, compare_float, square_value,
        activity_square_root_fixture));
    assert(peak_match_candidate_count == 0u &&
           peak_match_reference_count == 0u && peak_match_median == 0.0f);

    peak_match_candidates[0] = 250u;
    peak_match_candidate_count = 1u;
    peak_match_reference_count = 1u;
    peak_match_median = 7.0f;
    assert(!gomore_primitives_peak_candidate_match(
        peak_match_signal, 250u,
        peak_match_candidates, peak_match_references,
        &peak_match_candidate_count, &peak_match_reference_count,
        &peak_match_median, peak_match_workspace,
        sort_values, compare_float, square_value,
        activity_square_root_fixture));
    assert(peak_match_candidate_count == 1u &&
           peak_match_reference_count == 1u && peak_match_median == 7.0f);

    uint8_t motion_classifier_state[17];
    uint8_t motion_classifier_source[13] = {0u};
    uint8_t motion_classifier_features[62] = {0u};
    uint8_t motion_classifier_output[3] = {
        UINT8_C(0xA5), UINT8_C(0xA5), UINT8_C(0xA5),
    };
    assert(gomore_primitives_pattern17_initialize(
        motion_classifier_state, sizeof(motion_classifier_state)));
    store_u32_fixture(&motion_classifier_features[0], float_bits(1.0f));
    motion_classifier_features[0x38u] = UINT8_C(0xFF);
    memset(&g_motion_classifier_estimator_trace, 0,
           sizeof(g_motion_classifier_estimator_trace));
    assert(gomore_primitives_motion_classifier_update(
        motion_classifier_state, sizeof(motion_classifier_state), 1u,
        motion_classifier_source, sizeof(motion_classifier_source),
        motion_classifier_features, sizeof(motion_classifier_features),
        motion_classifier_output, sizeof(motion_classifier_output),
        motion_classifier_state1_estimate));
    assert(g_motion_classifier_estimator_trace.calls == 0u &&
           motion_classifier_output[0] == 0u &&
           motion_classifier_output[1] == UINT8_C(0xFF) &&
           motion_classifier_output[2] == 0u);

    for (size_t index = 0u; index < 5u; ++index) {
        motion_classifier_state[index] = (uint8_t)(index + 1u);
        motion_classifier_state[index + 5u] = (uint8_t)(index + 6u);
    }
    motion_classifier_source[0x0Cu] = 1u;
    g_motion_classifier_estimator_trace.calls = 0u;
    assert(gomore_primitives_motion_classifier_update(
        motion_classifier_state, sizeof(motion_classifier_state), 3u,
        motion_classifier_source, sizeof(motion_classifier_source),
        motion_classifier_features, sizeof(motion_classifier_features),
        motion_classifier_output, sizeof(motion_classifier_output),
        motion_classifier_state1_estimate));
    const uint8_t expected_gap_first[5] = {
        4u, 5u, UINT8_C(0xFE), UINT8_C(0xFE), UINT8_C(0xFE),
    };
    const uint8_t expected_gap_second[5] = {9u, 10u, 0u, 0u, 0u};
    assert(g_motion_classifier_estimator_trace.calls == 0u &&
           memcmp(motion_classifier_state, expected_gap_first, 5u) == 0 &&
           memcmp(&motion_classifier_state[5], expected_gap_second, 5u) == 0 &&
           motion_classifier_output[0] == UINT8_C(0xFF) &&
           motion_classifier_output[1] == UINT8_C(0xFE) &&
           motion_classifier_output[2] == 0u);

    motion_classifier_source[0x0Cu] = 0u;
    g_motion_classifier_estimator_trace.calls = 0u;
    assert(gomore_primitives_motion_classifier_update(
        motion_classifier_state, sizeof(motion_classifier_state), 6u,
        motion_classifier_source, sizeof(motion_classifier_source),
        motion_classifier_features, sizeof(motion_classifier_features),
        motion_classifier_output, sizeof(motion_classifier_output),
        motion_classifier_state1_estimate));
    for (size_t index = 0u; index < 5u; ++index) {
        assert(motion_classifier_state[index] == UINT8_C(0xFE) &&
               motion_classifier_state[index + 5u] == 0u);
    }
    assert(g_motion_classifier_estimator_trace.calls == 0u &&
           motion_classifier_output[0] == UINT8_C(0xFF));
    motion_classifier_output[0] = UINT8_C(0xA5);
    assert(!gomore_primitives_motion_classifier_update(
        motion_classifier_state, sizeof(motion_classifier_state), 1u,
        motion_classifier_source, sizeof(motion_classifier_source),
        motion_classifier_features, sizeof(motion_classifier_features),
        motion_classifier_output, 2u, motion_classifier_state1_estimate));
    assert(motion_classifier_output[0] == UINT8_C(0xA5));

    uint8_t motion_finalize_state[17];
    uint8_t motion_finalize_features[0x38] = {0u};
    uint8_t motion_finalize_output[3] = {1u, 0u, 60u};
    for (size_t index = 0u; index < 5u; ++index) {
        motion_finalize_state[index] = 1u;
        motion_finalize_state[index + 5u] = 100u;
        motion_finalize_state[index + 10u] = 100u;
    }
    motion_finalize_state[15] = 1u;
    motion_finalize_state[16] = 1u;
    store_u32_fixture(&motion_finalize_features[0x2Cu], float_bits(70.0f));
    store_u32_fixture(&motion_finalize_features[0x30u], float_bits(90.0f));
    store_u32_fixture(&motion_finalize_features[0x34u], float_bits(110.0f));
    memset(&g_motion_classifier_estimator_trace, 0,
           sizeof(g_motion_classifier_estimator_trace));
    g_motion_classifier_estimator_trace.result = 100.9f;
    g_motion_classifier_estimator_trace.consensus = 2u;
    assert(gomore_primitives_motion_classifier_finalize(
        motion_finalize_state, sizeof(motion_finalize_state),
        motion_finalize_features, sizeof(motion_finalize_features),
        motion_finalize_output, sizeof(motion_finalize_output),
        motion_classifier_state1_estimate));
    assert(g_motion_classifier_estimator_trace.calls == 1u &&
           g_motion_classifier_estimator_trace.first == 70.0f &&
           g_motion_classifier_estimator_trace.middle == 90.0f &&
           g_motion_classifier_estimator_trace.latest == 110.0f &&
           motion_finalize_output[1] == 1u &&
           motion_finalize_output[2] == 100u &&
           motion_finalize_state[9] == 100u &&
           motion_finalize_state[14] == 100u);

    for (size_t index = 0u; index < 5u; ++index) {
        motion_finalize_state[index] = 1u;
        motion_finalize_state[index + 5u] = 90u;
        motion_finalize_state[index + 10u] = 90u;
    }
    motion_finalize_output[0] = 1u;
    motion_finalize_output[2] = 60u;
    assert(gomore_primitives_motion_classifier_finalize(
        motion_finalize_state, sizeof(motion_finalize_state),
        motion_finalize_features, sizeof(motion_finalize_features),
        motion_finalize_output, sizeof(motion_finalize_output), NULL));
    assert(motion_finalize_output[1] == 1u &&
           motion_finalize_output[2] == 90u);

    for (size_t index = 0u; index < 5u; ++index) {
        motion_finalize_state[index] = 1u;
        motion_finalize_state[index + 5u] = 60u;
        motion_finalize_state[index + 10u] = 60u;
    }
    motion_finalize_output[0] = 1u;
    motion_finalize_output[2] = 60u;
    store_u32_fixture(&motion_finalize_features[0x30u], float_bits(80.0f));
    g_motion_classifier_estimator_trace.result = 121.0f;
    g_motion_classifier_estimator_trace.consensus = 1u;
    assert(gomore_primitives_motion_classifier_finalize(
        motion_finalize_state, sizeof(motion_finalize_state),
        motion_finalize_features, sizeof(motion_finalize_features),
        motion_finalize_output, sizeof(motion_finalize_output),
        motion_classifier_state1_estimate));
    assert(motion_finalize_output[1] == 1u &&
           motion_finalize_output[2] == 60u);

    for (size_t index = 0u; index < 5u; ++index) {
        motion_finalize_state[index] = 1u;
        motion_finalize_state[index + 5u] = 121u;
        motion_finalize_state[index + 10u] = 121u;
    }
    motion_finalize_output[0] = 1u;
    motion_finalize_output[2] = 60u;
    store_u32_fixture(
        &motion_finalize_features[0x30u], UINT32_C(0x42A00001));
    assert(gomore_primitives_motion_classifier_finalize(
        motion_finalize_state, sizeof(motion_finalize_state),
        motion_finalize_features, sizeof(motion_finalize_features),
        motion_finalize_output, sizeof(motion_finalize_output),
        motion_classifier_state1_estimate));
    assert(motion_finalize_output[1] == 1u &&
           motion_finalize_output[2] == 121u);

    for (size_t index = 0u; index < 5u; ++index) {
        motion_finalize_state[index] = 1u;
        motion_finalize_state[index + 5u] = 121u;
        motion_finalize_state[index + 10u] = 121u;
    }
    motion_finalize_output[0] = 1u;
    motion_finalize_output[2] = 60u;
    store_u32_fixture(&motion_finalize_features[0x10u], float_bits(121.0f));
    g_motion_classifier_estimator_trace.result = 60.0f;
    g_motion_classifier_estimator_trace.consensus = 2u;
    assert(gomore_primitives_motion_classifier_finalize(
        motion_finalize_state, sizeof(motion_finalize_state),
        motion_finalize_features, sizeof(motion_finalize_features),
        motion_finalize_output, sizeof(motion_finalize_output),
        motion_classifier_state1_estimate));
    assert(motion_finalize_output[2] == 121u);

    for (size_t index = 0u; index < 5u; ++index) {
        motion_finalize_state[index] = 2u;
        motion_finalize_state[index + 5u] = 150u;
        motion_finalize_state[index + 10u] = 150u;
    }
    motion_finalize_output[0] = 2u;
    motion_finalize_output[2] = 130u;
    store_u32_fixture(&motion_finalize_features[0x2Cu], float_bits(150.9f));
    store_u32_fixture(&motion_finalize_features[0x30u], float_bits(150.9f));
    store_u32_fixture(&motion_finalize_features[0x34u], float_bits(150.9f));
    const unsigned state1_calls_before =
        g_motion_classifier_estimator_trace.calls;
    assert(gomore_primitives_motion_classifier_finalize(
        motion_finalize_state, sizeof(motion_finalize_state),
        motion_finalize_features, sizeof(motion_finalize_features),
        motion_finalize_output, sizeof(motion_finalize_output),
        motion_classifier_state1_estimate));
    assert(g_motion_classifier_estimator_trace.calls == state1_calls_before &&
           motion_finalize_output[1] == 2u &&
           motion_finalize_output[2] == 150u);

    uint8_t motion_finalize_before[17];
    memcpy(motion_finalize_before, motion_finalize_state,
           sizeof(motion_finalize_before));
    assert(!gomore_primitives_motion_classifier_finalize(
        motion_finalize_state, 16u,
        motion_finalize_features, sizeof(motion_finalize_features),
        motion_finalize_output, sizeof(motion_finalize_output),
        motion_classifier_state1_estimate));
    assert(memcmp(motion_finalize_state, motion_finalize_before,
                  sizeof(motion_finalize_before)) == 0 &&
           g_motion_classifier_estimator_trace.calls == state1_calls_before);
    uint8_t sps_state[0x1F8];
    memset(sps_state, UINT8_C(0xA5), sizeof(sps_state));
    assert(gomore_primitives_sps_state_initialize(
        sps_state, sizeof(sps_state)));
    assert(sps_state[0x0C] == 1u && sps_state[0x34] == 1u &&
           sps_state[0x94] == 1u && sps_state[0x1C0] == 1u &&
           sps_state[0x10] == 0u && sps_state[0x13] == 0xBFu &&
           sps_state[0x54] == 0u && sps_state[0x57] == 0xC4u &&
           sps_state[0x5C] == 0xF0u && sps_state[0x5F] == 0xC9u &&
           sps_state[0x164] == 0xFFu && sps_state[0x167] == 0xFFu);
    float rolling_mean_window[5] = {0.0f, 0.0f, 0.0f, 0.0f, 0.0f};
    assert(gomore_primitives_rolling_mean5_update(
        10.0f, rolling_mean_window, 0u) == 10.0f);
    assert(gomore_primitives_rolling_mean5_update(
        20.0f, rolling_mean_window, 1u) == 15.0f);
    assert(gomore_primitives_rolling_mean5_update(
        30.0f, rolling_mean_window, 4u) == 12.0f);
    assert(rolling_mean_window[0] == 20.0f &&
           rolling_mean_window[3] == 30.0f &&
           rolling_mean_window[4] == 30.0f);
    const float nearest_values[3] = {0.0f, 5.0f, 7.0f};
    assert(gomore_primitives_nearest_nonzero3(
        6.0f, nearest_values) == 7.0f);
    const float quadratic_difference =
        gomore_primitives_activity_scaled_quadratic_difference(
            10.0f, 10.0f, 3.0f, 2.0f, square_power_fixture);
    assert(quadratic_difference > 0.37f &&
           quadratic_difference < 0.39f);
    const gomore_primitives_affine_reciprocal_model4 reciprocal_model = {
        .coefficients = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f, 6.0f},
    };
    const float reciprocal_values[4] = {2.0f, 4.0f, 1.0f, 2.0f};
    const float reciprocal_result =
        gomore_primitives_affine_reciprocal_model4_evaluate(
            reciprocal_values, &reciprocal_model);
    assert(reciprocal_result > 0.34f && reciprocal_result < 0.35f);
    assert(gomore_primitives_bounded_linear_complement(
               2.5f, 0.35f) == 0.5f);
    assert(gomore_primitives_bounded_linear_complement(
               6.0f, 0.35f) == 0.0f);
    const uint16_t autocorrelation_samples[1] = {7};
    float autocorrelation_outputs[5];
    assert(gomore_primitives_locomotion_autocorrelation_wrapper(
        false, NULL, autocorrelation_outputs, 0u, 0u, NULL));
    assert(autocorrelation_outputs[0] == -1.0f &&
           autocorrelation_outputs[1] == -1.0f &&
           autocorrelation_outputs[4] == 0.0f);
    assert(gomore_primitives_locomotion_autocorrelation_wrapper(
        true, autocorrelation_samples, autocorrelation_outputs,
        11u, 12u, autocorrelation_fixture));
    assert(autocorrelation_outputs[0] == 1.0f &&
           autocorrelation_outputs[4] == 5.0f);
    uint16_t alternating_autocorrelation[100];
    for (size_t index = 0u; index < 100u; ++index) {
        alternating_autocorrelation[index] =
            (index / 5u) % 2u == 0u ? 700u : 2300u;
    }
    int8_t autocorrelation_counts[2] = {0, 0};
    float autocorrelation_shape[2] = {0.0f, 0.0f};
    assert(gomore_primitives_locomotion_autocorrelation_wrapper(
        true, alternating_autocorrelation, autocorrelation_outputs,
        (uintptr_t)autocorrelation_counts,
        (uintptr_t)autocorrelation_shape,
        gomore_primitives_locomotion_autocorrelation_analyze));
    assert(float_bits(autocorrelation_outputs[0]) == UINT32_C(0x3F800000));
    assert(float_bits(autocorrelation_outputs[1]) == UINT32_C(0x3F800000));
    assert(float_bits(autocorrelation_outputs[2]) == UINT32_C(0x43160000));
    assert(float_bits(autocorrelation_outputs[3]) == UINT32_C(0x4315CABD));
    assert(float_bits(autocorrelation_outputs[4]) == UINT32_C(0x4315CABD));
    assert(autocorrelation_counts[0] == 1 && autocorrelation_counts[1] == 0);
    assert(float_bits(autocorrelation_shape[0]) == UINT32_C(0x3DA844A3));
    assert(float_bits(autocorrelation_shape[1]) == UINT32_C(0x40A00000));

    static const uint8_t sine_periods[6] = {12u, 15u, 20u, 25u, 30u, 35u};
    static const uint32_t sine_expected[6][5] = {
        {UINT32_C(0x3F800000), UINT32_C(0x3F800000),
         UINT32_C(0x42FA0000), UINT32_C(0x42FABDF3),
         UINT32_C(0x42FABDF3)},
        {UINT32_C(0x3F800000), UINT32_C(0x3F800000),
         UINT32_C(0x42C80000), UINT32_C(0x42C88B88),
         UINT32_C(0x42C88B88)},
        {UINT32_C(0x3F800000), UINT32_C(0x3F800000),
         UINT32_C(0x42960000), UINT32_C(0x4295FFCF),
         UINT32_C(0x4295FFCF)},
        {UINT32_C(0x3F800000), UINT32_C(0x3F800000),
         UINT32_C(0x42700000), UINT32_C(0x426FFFAD),
         UINT32_C(0x426FFFAD)},
        {UINT32_C(0x3F800000), UINT32_C(0x3F800000),
         UINT32_C(0x424A3F48), UINT32_C(0x424994E2),
         UINT32_C(0x424994E2)},
        {UINT32_C(0x3F800000), UINT32_C(0x3F800000),
         UINT32_C(0x00000000), UINT32_C(0x00000000),
         UINT32_C(0x00000000)},
    };
    uint16_t sine_autocorrelation[100];
    for (size_t fixture = 0u; fixture < 6u; ++fixture) {
        for (size_t index = 0u; index < 100u; ++index) {
            const double phase = 6.2831853071795864769 * (double)index /
                                 (double)sine_periods[fixture];
            sine_autocorrelation[index] =
                (uint16_t)(1500.0 + 800.0 * sin(phase));
        }
        assert(gomore_primitives_locomotion_autocorrelation_wrapper(
            true, sine_autocorrelation, autocorrelation_outputs,
            (uintptr_t)autocorrelation_counts,
            (uintptr_t)autocorrelation_shape,
            gomore_primitives_locomotion_autocorrelation_analyze));
        for (size_t output_index = 0u; output_index < 5u;
                ++output_index) {
            assert(float_bits(autocorrelation_outputs[output_index]) ==
                   sine_expected[fixture][output_index]);
        }
    }

    uint16_t constant_autocorrelation[100];
    for (size_t index = 0u; index < 100u; ++index) {
        constant_autocorrelation[index] = 1500u;
    }
    assert(gomore_primitives_locomotion_autocorrelation_wrapper(
        true, constant_autocorrelation, autocorrelation_outputs,
        (uintptr_t)autocorrelation_counts,
        (uintptr_t)autocorrelation_shape,
        gomore_primitives_locomotion_autocorrelation_analyze));
    assert(autocorrelation_outputs[0] == -1.0f &&
           autocorrelation_outputs[1] == -1.0f &&
           autocorrelation_outputs[2] == 0.0f &&
           autocorrelation_outputs[3] == 0.0f &&
           autocorrelation_outputs[4] == 0.0f);
    const gomore_primitives_hr_candidate estimated_hr = {
        .heart_rate = 80.0f,
        .quality = UINT32_C(0x12345678),
    };
    gomore_primitives_hr_selection selected_hr;
    assert(gomore_primitives_select_heart_rate(
        0u, 70.0f, &estimated_hr, &selected_hr));
    assert(selected_hr.heart_rate == 70.0f &&
           selected_hr.quality == 1u && selected_hr.source == 0u);
    assert(gomore_primitives_select_heart_rate(
        1u, 70.0f, &estimated_hr, &selected_hr));
    assert(selected_hr.heart_rate == 80.0f &&
           selected_hr.quality == UINT32_C(0x12345678) &&
           selected_hr.source == 1u);
    const gomore_primitives_hr_candidate invalid_estimated_hr = {
        .heart_rate = 0.0f,
        .quality = 9u,
    };
    assert(gomore_primitives_select_heart_rate(
        1u, 0.0f, &invalid_estimated_hr, &selected_hr));
    assert(selected_hr.heart_rate == 0.0f &&
           selected_hr.quality == 0u &&
           selected_hr.source == UINT8_C(0x40));
    uint8_t sps_dispatch_state[0x1C];
    memset(sps_dispatch_state, 0, sizeof(sps_dispatch_state));
    sps_dispatch_state[0x18] = 1u;
    const float sps_values[4] = {3.0f, 4.0f, 5.0f, 6.0f};
    float sps_primary = 0.0f;
    float sps_secondary = 0.0f;
    sps_commit_calls = 0u;
    assert(gomore_primitives_sps_model_dispatch(
        sps_dispatch_state, sizeof(sps_dispatch_state), sps_values,
        sps_primary_model0, sps_secondary_model0,
        sps_primary_model1, sps_secondary_model1,
        sps_adjust_fixture, sps_commit_fixture,
        &sps_primary, &sps_secondary));
    assert(sps_primary == 4.0f && sps_secondary == 8.0f &&
           sps_commit_calls == 1u);
    sps_dispatch_state[0] = 1u;
    sps_dispatch_state[0x18] = 0u;
    assert(gomore_primitives_sps_model_dispatch(
        sps_dispatch_state, sizeof(sps_dispatch_state), sps_values,
        sps_primary_model0, sps_secondary_model0,
        sps_primary_model1, sps_secondary_model1,
        sps_adjust_fixture, sps_commit_fixture,
        &sps_primary, &sps_secondary));
    assert(sps_primary == 15.0f && sps_secondary == 26.0f &&
           sps_commit_calls == 2u);

    const gomore_primitives_sps_candidate_providers sps_candidate_providers = {
        .state2_primary = sps_candidate_state2_primary,
        .state2_secondary = sps_candidate_state2_secondary,
        .state1_primary = sps_candidate_state1_primary,
        .state1_secondary = sps_candidate_state1_secondary,
        .adjust = sps_candidate_adjust,
        .commit = sps_candidate_commit,
    };
    gomore_primitives_sps_candidate_state sps_candidate_state;
    memset(&sps_candidate_state, 0, sizeof(sps_candidate_state));
    sps_candidate_state.state2_model.model_type = 0u;
    sps_candidate_state.state1_model.model_type = 1u;
    sps_candidate_state.state2_model.calibration_slope = 1.0f;
    sps_candidate_state.state1_model.calibration_slope = 1.0f;
    sps_candidate_state.startup_cooldown = 8u;
    gomore_primitives_sps_features sps_candidate_features = {{
        300.0f, 200.0f, 1500.0f, 0.0f, 100.0f, 150.0f,
    }};
    gomore_primitives_sps_motion sps_candidate_motion = {1, 1, 100u};
    gomore_primitives_sps_candidate_output sps_candidate_output;
    memset(&sps_candidate_output, 0xA5, sizeof(sps_candidate_output));
    assert(gomore_primitives_sps_accelerometer_candidate_update(
        &sps_candidate_state, 1u, &sps_candidate_features,
        &sps_candidate_motion, 175.0f, &sps_candidate_providers,
        &sps_candidate_output));
    assert(sps_candidate_output.candidate == 5.0f &&
           sps_candidate_output.status == 2u &&
           sps_candidate_output.reserved[0] == UINT8_C(0xA5) &&
           sps_candidate_state.smoothed_state1 == 5.0f &&
           sps_candidate_state.latest_candidate == 5.0f &&
           sps_candidate_state.latest_primary_model == 3.0f &&
           sps_candidate_state.state1_model.accumulated_secondary == 5.0f &&
           sps_candidate_state.state1_model.accumulated_primary == 3.0f &&
           sps_candidate_state.state1_model.accepted_count == 1u &&
           sps_candidate_state.startup_cooldown == 7u);

    sps_candidate_features.values[4] = 110.0f;
    assert(gomore_primitives_sps_accelerometer_candidate_update(
        &sps_candidate_state, 3u, &sps_candidate_features,
        &sps_candidate_motion, 175.0f, &sps_candidate_providers,
        &sps_candidate_output));
    const float expected_state1_smoothing =
        (float)((double)5.5f * 0.15 + (double)5.0f * 0.85);
    assert(float_bits(sps_candidate_output.candidate) ==
               float_bits(expected_state1_smoothing) &&
           sps_candidate_state.missing_update_count == 2u &&
           sps_candidate_state.state1_model.accepted_count == 4u &&
           sps_candidate_state.state1_model.accumulated_secondary == 20.5f &&
           sps_candidate_state.state1_model.accumulated_primary == 12.0f);

    memset(&sps_candidate_state, 0, sizeof(sps_candidate_state));
    sps_candidate_state.state2_model.model_type = 0u;
    sps_candidate_state.state1_model.model_type = 1u;
    sps_candidate_state.state2_model.calibration_slope = 1.0f;
    sps_candidate_state.state1_model.calibration_slope = 1.0f;
    sps_candidate_state.startup_cooldown = 8u;
    sps_candidate_motion.raw_state = 2;
    sps_candidate_motion.smoothed_state = 2;
    sps_candidate_motion.cadence = 150u;
    assert(gomore_primitives_sps_accelerometer_candidate_update(
        &sps_candidate_state, 1u, &sps_candidate_features,
        &sps_candidate_motion, 175.0f, &sps_candidate_providers,
        &sps_candidate_output));
    assert(sps_candidate_output.candidate == 14.0f &&
           sps_candidate_output.status == 2u &&
           sps_candidate_state.smoothed_state2 == 15.0f);
    sps_candidate_state.state2_model.calibration_enabled = 1u;
    sps_candidate_state.state2_model.calibration_slope = 2.0f;
    sps_candidate_state.state2_model.calibration_intercept = 1.0f;
    sps_candidate_state.smoothed_state2 = 0.0f;
    assert(gomore_primitives_sps_accelerometer_candidate_update(
        &sps_candidate_state, 1u, &sps_candidate_features,
        &sps_candidate_motion, 175.0f, &sps_candidate_providers,
        &sps_candidate_output));
    assert(sps_candidate_output.candidate == 16.0f &&
           sps_candidate_output.status == 3u);

    const gomore_primitives_sps_candidate_state before_rejection =
        sps_candidate_state;
    sps_candidate_motion.smoothed_state = 1;
    memset(&sps_candidate_output, 0xA5, sizeof(sps_candidate_output));
    assert(gomore_primitives_sps_accelerometer_candidate_update(
        &sps_candidate_state, 1u, &sps_candidate_features,
        &sps_candidate_motion, 175.0f, &sps_candidate_providers,
        &sps_candidate_output));
    assert(sps_candidate_output.candidate == -1.0f &&
           sps_candidate_output.status == 1u &&
           sps_candidate_output.reserved[2] == UINT8_C(0xA5) &&
           sps_candidate_state.startup_cooldown + 1u ==
               before_rejection.startup_cooldown);
    sps_candidate_motion.raw_state = 0;
    sps_candidate_motion.smoothed_state = 0;
    sps_candidate_motion.cadence = 0u;
    assert(gomore_primitives_sps_accelerometer_candidate_update(
        &sps_candidate_state, 1u, &sps_candidate_features,
        &sps_candidate_motion, 175.0f, &sps_candidate_providers,
        &sps_candidate_output));
    assert(sps_candidate_output.candidate == 0.0f &&
           sps_candidate_output.status == 1u);

    const gomore_primitives_sps_candidate_state before_invalid =
        sps_candidate_state;
    assert(!gomore_primitives_sps_accelerometer_candidate_update(
        &sps_candidate_state, 1u, &sps_candidate_features,
        &sps_candidate_motion, 175.0f, NULL, &sps_candidate_output));
    assert(memcmp(&sps_candidate_state, &before_invalid,
                  sizeof(before_invalid)) == 0);

    health_lifecycle_trace lifecycle_trace = {
        .auth = {-1, 0}, .init = {-5, 0},
        .previous_found = false, .crash_present = true,
        .crash_restored = true,
        .crash_length = GOMORE_PRIMITIVES_PREVIOUS_DATA_BYTES,
        .profile_found = false, .subscription = UINT8_C(7),
    };
    const gomore_primitives_health_lifecycle_providers lifecycle_providers = {
        .context = &lifecycle_trace,
        .query_previous_size = lifecycle_size,
        .query_engine_size = lifecycle_size,
        .configure_authorization = lifecycle_auth,
        .restore_previous = lifecycle_previous,
        .crash_record_present = lifecycle_crash_present,
        .restore_crash_previous = lifecycle_crash,
        .clear_crash_previous = lifecycle_crash_clear,
        .load_user_profile = lifecycle_profile,
        .timestamp = lifecycle_timestamp,
        .initialize_health = lifecycle_initialize,
        .apply_profile_state = lifecycle_apply,
        .configure_state_mode = lifecycle_mode,
        .subscribe = lifecycle_subscribe,
        .event_callback = UINT32_C(0x1235),
        .event_callback_context = UINT32_C(0x5678),
    };
    gomore_primitives_health_lifecycle_state lifecycle_state;
    memset(&lifecycle_state, 0xA5, sizeof(lifecycle_state));
    lifecycle_state.initialized = 0u;
    lifecycle_state.subscription = 0u;
    uint8_t lifecycle_previous[GOMORE_PRIMITIVES_PREVIOUS_DATA_BYTES];
    uint8_t lifecycle_default_profile[GOMORE_PRIMITIVES_USER_PROFILE_BYTES];
    uint8_t lifecycle_output[GOMORE_PRIMITIVES_OUTPUT_DESCRIPTOR_BYTES];
    memset(lifecycle_previous, 0xA5, sizeof(lifecycle_previous));
    memset(lifecycle_default_profile, 0x44, sizeof(lifecycle_default_profile));
    memset(lifecycle_output, 0xA5, sizeof(lifecycle_output));
    int32_t lifecycle_status = -99;
    assert(gomore_primitives_health_lifecycle_initialize(
        &lifecycle_state, false, lifecycle_previous,
        lifecycle_default_profile, lifecycle_output,
        UINT32_C(0x20001000), UINT32_C(0x20002000),
        &lifecycle_providers, &lifecycle_status) ==
        GOMORE_PRIMITIVES_HEALTH_LIFECYCLE_OK);
    assert(lifecycle_status == 0 && lifecycle_state.initialized == 1u &&
           lifecycle_state.subscription == 7u &&
           lifecycle_state.auth_retry_attempted == 1u &&
           lifecycle_state.auth_pending == 0u &&
           lifecycle_trace.auth_calls == 2u &&
           lifecycle_trace.init_calls == 2u &&
           lifecycle_trace.crash_clear_calls == 1u &&
           lifecycle_trace.init_profile_first == UINT8_C(0x44) &&
           lifecycle_trace.init_previous_first == 0u &&
           lifecycle_trace.apply_calls == 1u &&
           lifecycle_trace.mode_calls == 1u &&
           lifecycle_trace.subscribe_calls == 1u);
    assert(load_u32_fixture(&lifecycle_output[8]) == UINT32_C(0x20001000) &&
           load_u32_fixture(&lifecycle_output[0x0C]) ==
               UINT32_C(0x20001064) &&
           load_u32_fixture(&lifecycle_output[0x10]) ==
               UINT32_C(0x200010C8) &&
           load_u32_fixture(&lifecycle_output[0x18]) ==
               UINT32_C(0x2000112C) &&
           load_u32_fixture(&lifecycle_output[0x20]) ==
               UINT32_C(0x20002000));
    assert(lifecycle_output[0] == 0u && lifecycle_output[0x107] == 0u);

    health_lifecycle_trace auth_failure_trace = {
        .auth = {-2, -3},
    };
    gomore_primitives_health_lifecycle_providers auth_failure_providers =
        lifecycle_providers;
    auth_failure_providers.context = &auth_failure_trace;
    memset(lifecycle_output, 0xA5, sizeof(lifecycle_output));
    lifecycle_state.initialized = 0u;
    assert(gomore_primitives_health_lifecycle_initialize(
        &lifecycle_state, false, lifecycle_previous,
        lifecycle_default_profile, lifecycle_output,
        UINT32_C(0x20001000), UINT32_C(0x20002000),
        &auth_failure_providers, &lifecycle_status) ==
        GOMORE_PRIMITIVES_HEALTH_LIFECYCLE_AUTH_FAILED);
    assert(lifecycle_status == -3 && lifecycle_state.initialized == 0u &&
           lifecycle_state.auth_pending == 1u &&
           lifecycle_output[0] == UINT8_C(0xA5));
    assert(gomore_primitives_health_lifecycle_initialize(
        &lifecycle_state, false, lifecycle_previous,
        lifecycle_default_profile, lifecycle_output,
        UINT32_MAX - 299u, UINT32_C(0x20002000),
        &lifecycle_providers, &lifecycle_status) ==
        GOMORE_PRIMITIVES_HEALTH_LIFECYCLE_BAD_ARGUMENT);

    float sps_secondary_features[3] = {
        bits_float(UINT32_C(0x432DAD60)),
        bits_float(UINT32_C(0x432F2E7B)),
        bits_float(UINT32_C(0x44DF07BD)),
    };
    g_sps_secondary_sqrt_calls = 0u;
    g_sps_secondary_sqrt_output = 2.0;
    float sps_secondary_result = gomore_primitives_sps_secondary_model(
        sps_secondary_features, sps_secondary_sqrt_fixture);
    assert(g_sps_secondary_sqrt_calls == 1u &&
           g_sps_secondary_sqrt_input == 0.0 &&
           float_bits(sps_secondary_result) == UINT32_C(0x4100DE7F));

    sps_secondary_features[2] = bits_float(UINT32_C(0x4502886B));
    sps_secondary_result = gomore_primitives_sps_secondary_model(
        sps_secondary_features, sps_secondary_sqrt_fixture);
    assert(g_sps_secondary_sqrt_calls == 2u &&
           float_bits((float)g_sps_secondary_sqrt_input) ==
               UINT32_C(0x3F7FFFFE) &&
           float_bits(sps_secondary_result) == UINT32_C(0x4162FF1D));

    sps_secondary_features[0] = bits_float(UINT32_C(0x433375A8));
    sps_secondary_features[1] = bits_float(UINT32_C(0x433B9FAF));
    sps_secondary_features[2] = bits_float(UINT32_C(0x44DF07BD));
    g_sps_secondary_sqrt_output = 0.0;
    sps_secondary_result = gomore_primitives_sps_secondary_model(
        sps_secondary_features, sps_secondary_sqrt_fixture);
    assert(g_sps_secondary_sqrt_calls == 3u &&
           float_bits(sps_secondary_result) == UINT32_C(0x4151775F));
    assert(gomore_primitives_sps_secondary_model(
               NULL, sps_secondary_sqrt_fixture) == 0.0f &&
           gomore_primitives_sps_secondary_model(
               sps_secondary_features, NULL) == 0.0f);

    const uint16_t half_positions[2] = {3u, 8u};
    const float half_control_values[2] = {1.0f, 7.0f};
    float half_position_output[6];
    for (size_t index = 0u; index < 6u; ++index) {
        half_position_output[index] = -1.0f;
    }
    g_positive_round_calls = 0u;
    assert(gomore_primitives_expand_half_positions(
        half_positions, half_control_values, 2u,
        half_position_output, 6u, positive_round_fixture));
    assert(g_positive_round_calls == 2u &&
           half_position_output[0] == 1.0f &&
           half_position_output[1] == 1.0f &&
           half_position_output[2] == 1.0f &&
           half_position_output[3] == 3.0f &&
           half_position_output[4] == 5.0f &&
           half_position_output[5] == 7.0f);

    const uint16_t oversized_first_position[1] = {20u};
    half_position_output[0] = -1.0f;
    assert(!gomore_primitives_expand_half_positions(
        oversized_first_position, half_control_values, 1u,
        half_position_output, 6u, positive_round_fixture));
    assert(half_position_output[0] == -1.0f);
    const uint16_t zero_span_positions[2] = {0u, 0u};
    assert(!gomore_primitives_expand_half_positions(
        zero_span_positions, half_control_values, 2u,
        half_position_output, 6u, positive_round_fixture));

    const gomore_primitives_locomotion_control_sample control_samples[3] = {
        {0u, 30.0f, 20.0f},
        {200u, 21.0f, 20.0f},
        {400u, 0.0f, 0.0f},
    };
    gomore_primitives_locomotion_control_workspace control_workspace;
    memset(&control_workspace, 0, sizeof(control_workspace));
    float control_primary = -9.0f;
    float control_secondary = -9.0f;
    size_t control_accepted = SIZE_MAX;
    int32_t control_status = -9;
    g_positive_round_calls = 0u;
    g_locomotion_control_reduce_calls = 0u;
    assert(gomore_primitives_locomotion_control_extract(
        control_samples, 3u, 200.0f, 10.0f, 2u,
        &control_workspace, positive_round_fixture,
        locomotion_control_reduce_fixture,
        &locomotion_reduce_math,
        &control_primary, &control_secondary,
        &control_accepted, &control_status));
    assert(g_positive_round_calls == 2u &&
           g_locomotion_control_reduce_calls == 1u &&
           control_accepted == 2u && control_status == 0 &&
           control_workspace.positions[0] == 0u &&
           control_workspace.positions[1] == 200u &&
           control_primary == 3.0f && control_secondary == 4.0f &&
           control_workspace.first_indices[0] == 3u &&
           control_workspace.second_indices[0] == 4u);

    const size_t feature_periods[5] = {40u, 50u, 45u, 55u, 48u};
    size_t feature_cursor = 0u;
    for (size_t period_index = 0u; period_index < 5u; ++period_index) {
        const size_t period = feature_periods[period_index];
        for (size_t index = 0u; index < period; ++index) {
            const size_t mirrored = period - index;
            const size_t height = index < mirrored ? index : mirrored;
            control_workspace.expanded[feature_cursor++] = (float)height;
        }
    }
    while (feature_cursor < GOMORE_PRIMITIVES_LOCOMOTION_EXPANDED_COUNT) {
        control_workspace.expanded[feature_cursor++] = 0.0f;
    }
    memset(control_workspace.first_indices, 0,
           sizeof(control_workspace.first_indices));
    memset(control_workspace.second_indices, 0,
           sizeof(control_workspace.second_indices));
    memset(control_workspace.controls, 0,
           sizeof(control_workspace.controls));
    control_primary = -9.0f;
    control_secondary = -9.0f;
    assert(gomore_primitives_locomotion_feature_reduce(
        control_workspace.expanded,
        control_workspace.first_indices,
        control_workspace.second_indices,
        control_workspace.controls,
        &control_primary, &control_secondary,
        &locomotion_reduce_math));
    assert(float_bits(control_primary) == UINT32_C(0x41760E19) &&
           float_bits(control_secondary) == UINT32_C(0x3F2AC478));
    const uint8_t expected_first_indices[5] = {22u, 66u, 114u, 164u, 216u};
    const uint8_t expected_second_indices[5] = {5u, 42u, 92u, 137u, 191u};
    assert(memcmp(control_workspace.first_indices,
                  expected_first_indices,
                  sizeof(expected_first_indices)) == 0 &&
           memcmp(control_workspace.second_indices,
                  expected_second_indices,
                  sizeof(expected_second_indices)) == 0);

    float constant_features[GOMORE_PRIMITIVES_LOCOMOTION_EXPANDED_COUNT];
    for (size_t index = 0u;
            index < GOMORE_PRIMITIVES_LOCOMOTION_EXPANDED_COUNT; ++index) {
        constant_features[index] = 7.0f;
    }
    control_primary = -9.0f;
    control_secondary = -9.0f;
    assert(gomore_primitives_locomotion_feature_reduce(
        constant_features,
        control_workspace.first_indices,
        control_workspace.second_indices,
        control_workspace.controls,
        &control_primary, &control_secondary,
        &locomotion_reduce_math));
    assert(control_primary == -1.0f && control_secondary == 0.0f);
    control_primary = 7.0f;
    control_secondary = 8.0f;
    assert(!gomore_primitives_locomotion_feature_reduce(
        constant_features,
        control_workspace.first_indices,
        control_workspace.second_indices,
        control_workspace.controls,
        &control_primary, &control_secondary, NULL));
    assert(control_primary == 7.0f && control_secondary == 8.0f);

    const gomore_primitives_locomotion_control_sample
        insufficient_control_samples[3] = {
            {0u, 0.0f, 0.0f},
            {100u, 0.0f, 0.0f},
            {200u, 0.0f, 0.0f},
        };
    g_locomotion_control_reduce_calls = 0u;
    assert(gomore_primitives_locomotion_control_extract(
        insufficient_control_samples, 3u, 100.0f, 10.0f, 1u,
        &control_workspace, positive_round_fixture,
        locomotion_control_reduce_fixture,
        &locomotion_reduce_math,
        &control_primary, &control_secondary,
        &control_accepted, &control_status));
    assert(g_locomotion_control_reduce_calls == 0u &&
           control_accepted == 2u && control_status == 1 &&
           control_primary == -1.0f && control_secondary == 0.0f &&
           control_workspace.controls[0] == 100.0f &&
           control_workspace.controls[1] == 100.0f);

    control_primary = 7.0f;
    control_secondary = 8.0f;
    control_accepted = 9u;
    control_status = 10;
    assert(!gomore_primitives_locomotion_control_extract(
        control_samples,
        GOMORE_PRIMITIVES_LOCOMOTION_CONTROL_CAPACITY + 1u,
        200.0f, 10.0f, 2u,
        &control_workspace, positive_round_fixture,
        locomotion_control_reduce_fixture,
        &locomotion_reduce_math,
        &control_primary, &control_secondary,
        &control_accepted, &control_status));
    assert(control_primary == 7.0f && control_secondary == 8.0f &&
           control_accepted == 9u && control_status == 10);

    memset(&g_pkey_store_trace, 0, sizeof(g_pkey_store_trace));
    g_pkey_store_trace.initialize_success = true;
    for (size_t index = 0u; index < 64u; ++index) {
        g_pkey_store_trace.bytes[8u + index] = (uint8_t)(index + 1u);
    }
    const uint32_t pkey_crc = r1_crc32_castagnoli(
        &g_pkey_store_trace.bytes[8], 64u);
    store_u32_fixture(&g_pkey_store_trace.bytes[0], 64u);
    store_u32_fixture(&g_pkey_store_trace.bytes[4], pkey_crc);
    gomore_primitives_pkey_store pkey_store = {
        .initialized = false,
        .partition_offset = UINT32_C(0xA000),
        .flash_context = &g_pkey_store_trace,
        .read = pkey_store_read_fixture,
        .write = pkey_store_write_fixture,
        .erase = pkey_store_erase_fixture,
        .initialize = pkey_store_initialize_fixture,
    };
    uint8_t pkey_output[64];
    memset(pkey_output, 0, sizeof(pkey_output));
    gomore_primitives_pkey_result pkey_result;
    assert(gomore_primitives_pkey_load(
        &pkey_store, pkey_output, sizeof(pkey_output), &pkey_result));
    assert(pkey_result.valid &&
           pkey_result.status == GOMORE_PRIMITIVES_PKEY_OK &&
           pkey_result.stored_length == 64u &&
           pkey_result.stored_crc == pkey_crc &&
           pkey_result.computed_crc == pkey_crc &&
           g_pkey_store_trace.initialize_calls == 1u &&
           g_pkey_store_trace.read_calls == 2u &&
           g_pkey_store_trace.offsets[0] == UINT32_C(0xA000) &&
           g_pkey_store_trace.offsets[1] == UINT32_C(0xA008) &&
           g_pkey_store_trace.lengths[0] == 8u &&
           g_pkey_store_trace.lengths[1] == 64u &&
           memcmp(pkey_output, &g_pkey_store_trace.bytes[8], 64u) == 0);

    g_pkey_store_trace.read_calls = 0u;
    store_u32_fixture(&g_pkey_store_trace.bytes[4], pkey_crc ^ 1u);
    assert(!gomore_primitives_pkey_load(
        &pkey_store, pkey_output, sizeof(pkey_output), &pkey_result));
    assert(!pkey_result.valid &&
           pkey_result.status == GOMORE_PRIMITIVES_PKEY_CRC_MISMATCH &&
           pkey_result.computed_crc == pkey_crc &&
           pkey_result.stored_crc == (pkey_crc ^ 1u) &&
           g_pkey_store_trace.read_calls == 2u);

    g_pkey_store_trace.read_calls = 0u;
    store_u32_fixture(&g_pkey_store_trace.bytes[0], 63u);
    memset(pkey_output, UINT8_C(0xA5), sizeof(pkey_output));
    assert(!gomore_primitives_pkey_load(
        &pkey_store, pkey_output, sizeof(pkey_output), &pkey_result));
    assert(pkey_result.status == GOMORE_PRIMITIVES_PKEY_NOT_FOUND &&
           pkey_result.stored_length == 63u &&
           g_pkey_store_trace.read_calls == 1u &&
           pkey_output[0] == UINT8_C(0xA5));

    g_pkey_store_trace.read_calls = 0u;
    g_pkey_store_trace.fail_read_call = 2u;
    store_u32_fixture(&g_pkey_store_trace.bytes[0], 64u);
    assert(!gomore_primitives_pkey_load(
        &pkey_store, pkey_output, sizeof(pkey_output), &pkey_result));
    assert(pkey_result.status == GOMORE_PRIMITIVES_PKEY_READ_FAILED &&
           g_pkey_store_trace.read_calls == 2u);

    g_pkey_store_trace.read_calls = 0u;
    g_pkey_store_trace.fail_read_call = 0u;
    assert(!gomore_primitives_pkey_load(
        &pkey_store, pkey_output, sizeof(pkey_output) - 1u, &pkey_result));
    assert(pkey_result.status == GOMORE_PRIMITIVES_PKEY_OUTPUT_NULL &&
           g_pkey_store_trace.read_calls == 0u);

    pkey_store.initialized = false;
    g_pkey_store_trace.initialize_success = false;
    g_pkey_store_trace.initialize_calls = 0u;
    assert(!gomore_primitives_pkey_load(
        &pkey_store, pkey_output, sizeof(pkey_output), &pkey_result));
    assert(pkey_result.status == GOMORE_PRIMITIVES_PKEY_STORE_UNAVAILABLE &&
           g_pkey_store_trace.initialize_calls == 1u &&
           g_pkey_store_trace.read_calls == 0u);

    memset(&g_pkey_store_trace, 0, sizeof(g_pkey_store_trace));
    g_pkey_store_trace.initialize_success = true;
    for (size_t index = 0u; index < 64u; ++index) {
        g_pkey_store_trace.bytes[8u + index] = (uint8_t)(0x80u + index);
    }
    store_u32_fixture(&g_pkey_store_trace.bytes[0], 64u);
    store_u32_fixture(
        &g_pkey_store_trace.bytes[4],
        r1_crc32_castagnoli(&g_pkey_store_trace.bytes[8], 64u));
    for (size_t slot = 0u; slot < 4u; ++slot) {
        store_u32_fixture(
            &g_pkey_store_trace.bytes[72u + slot * 12u], UINT32_MAX);
    }
    store_u32_fixture(&g_pkey_store_trace.bytes[108], 4u);
    g_pkey_store_trace.bytes[116] = 0x11u;
    g_pkey_store_trace.bytes[117] = 0x22u;
    g_pkey_store_trace.bytes[118] = 0x33u;
    g_pkey_store_trace.bytes[119] = 0x44u;
    pkey_store.initialized = false;
    pkey_store.flash_context = &g_pkey_store_trace;
    uint8_t previous_state[4] = {0u, 0u, 0u, 0u};
    gomore_primitives_previous_state_result previous_state_result;
    assert(gomore_primitives_previous_state_restore(
        &pkey_store, pkey_output, previous_state, sizeof(previous_state),
        &previous_state_result));
    assert(previous_state_result.found &&
           previous_state_result.slot == 3u &&
           previous_state_result.record_offset == UINT32_C(0xA06C) &&
           previous_state_result.status == GOMORE_PRIMITIVES_PREVIOUS_STATE_OK &&
           g_pkey_store_trace.initialize_calls == 1u &&
           g_pkey_store_trace.read_calls == 4u &&
           previous_state[0] == 0x11u && previous_state[3] == 0x44u);

    g_pkey_store_trace.read_calls = 0u;
    store_u32_fixture(&g_pkey_store_trace.bytes[108], UINT32_MAX);
    store_u32_fixture(&g_pkey_store_trace.bytes[96], 4u);
    g_pkey_store_trace.bytes[104] = 0x55u;
    g_pkey_store_trace.bytes[105] = 0x66u;
    g_pkey_store_trace.bytes[106] = 0x77u;
    g_pkey_store_trace.bytes[107] = 0x88u;
    assert(gomore_primitives_previous_state_restore(
        &pkey_store, pkey_output, previous_state, sizeof(previous_state),
        &previous_state_result));
    assert(previous_state_result.slot == 2u &&
           previous_state_result.record_offset == UINT32_C(0xA060) &&
           g_pkey_store_trace.read_calls == 5u &&
           previous_state[0] == 0x55u && previous_state[3] == 0x88u);

    g_pkey_store_trace.read_calls = 0u;
    store_u32_fixture(&g_pkey_store_trace.bytes[96], UINT32_MAX);
    memset(previous_state, UINT8_C(0xA5), sizeof(previous_state));
    assert(!gomore_primitives_previous_state_restore(
        &pkey_store, pkey_output, previous_state, sizeof(previous_state),
        &previous_state_result));
    assert(!previous_state_result.found &&
           previous_state_result.slot == UINT8_MAX &&
           previous_state_result.status ==
               GOMORE_PRIMITIVES_PREVIOUS_STATE_NOT_FOUND &&
           g_pkey_store_trace.read_calls == 6u &&
           previous_state[0] == UINT8_C(0xA5));

    g_pkey_store_trace.read_calls = 0u;
    g_pkey_store_trace.fail_read_call = 3u;
    assert(!gomore_primitives_previous_state_restore(
        &pkey_store, pkey_output, previous_state, sizeof(previous_state),
        &previous_state_result));
    assert(previous_state_result.status ==
               GOMORE_PRIMITIVES_PREVIOUS_STATE_READ_FAILED &&
           g_pkey_store_trace.read_calls == 3u);

    g_pkey_store_trace.read_calls = 0u;
    g_pkey_store_trace.fail_read_call = 0u;
    store_u32_fixture(&g_pkey_store_trace.bytes[4], 0u);
    assert(!gomore_primitives_previous_state_restore(
        &pkey_store, pkey_output, previous_state, sizeof(previous_state),
        &previous_state_result));
    assert(previous_state_result.status ==
               GOMORE_PRIMITIVES_PREVIOUS_STATE_PKEY_INVALID &&
           g_pkey_store_trace.read_calls == 2u);

    memset(&g_pkey_store_trace, UINT8_MAX, sizeof(g_pkey_store_trace));
    g_pkey_store_trace.initialize_calls = 0u;
    g_pkey_store_trace.read_calls = 0u;
    g_pkey_store_trace.write_calls = 0u;
    g_pkey_store_trace.erase_calls = 0u;
    g_pkey_store_trace.fail_read_call = 0u;
    g_pkey_store_trace.fail_write_call = 0u;
    g_pkey_store_trace.fail_erase_call = 0u;
    g_pkey_store_trace.initialize_success = true;
    store_u32_fixture(&g_pkey_store_trace.bytes[0], 64u);
    store_u32_fixture(&g_pkey_store_trace.bytes[4], pkey_crc);
    for (size_t index = 0u; index < 64u; ++index) {
        g_pkey_store_trace.bytes[8u + index] = (uint8_t)(index + 1u);
    }
    pkey_store.initialized = true;
    pkey_store.flash_context = &g_pkey_store_trace;
    const uint8_t appended_state[8] = {
        0x10u, 0x20u, 0x30u, 0x40u, 0x50u, 0x60u, 0x70u, 0x80u,
    };
    uint8_t append_scratch[72];
    gomore_primitives_previous_append_result append_result;
    assert(gomore_primitives_previous_state_append(
               &pkey_store, appended_state, 5u, sizeof(appended_state),
               NULL, 0u, &append_result) ==
           GOMORE_PRIMITIVES_PREVIOUS_APPEND_OK);
    assert(!append_result.compacted && append_result.slot == 0u &&
           append_result.key_length == 64u &&
           append_result.aligned_key_length == 64u &&
           append_result.aligned_state_length == 8u &&
           append_result.record_offset == UINT32_C(0xA048) &&
           g_pkey_store_trace.read_calls == 3u &&
           g_pkey_store_trace.write_calls == 2u &&
           g_pkey_store_trace.write_offsets[0] == UINT32_C(0xA048) &&
           g_pkey_store_trace.write_offsets[1] == UINT32_C(0xA050) &&
           load_u32_fixture(&g_pkey_store_trace.bytes[72]) == 5u &&
           load_u32_fixture(&g_pkey_store_trace.bytes[76]) == 0u &&
           memcmp(&g_pkey_store_trace.bytes[80], appended_state, 8u) == 0);

    g_pkey_store_trace.read_calls = 0u;
    g_pkey_store_trace.write_calls = 0u;
    assert(gomore_primitives_previous_state_append(
               &pkey_store, appended_state, 5u, sizeof(appended_state),
               NULL, 0u, &append_result) ==
           GOMORE_PRIMITIVES_PREVIOUS_APPEND_OK);
    assert(append_result.slot == 1u &&
           append_result.record_offset == UINT32_C(0xA058) &&
           g_pkey_store_trace.read_calls == 4u);

    g_pkey_store_trace.read_calls = 0u;
    g_pkey_store_trace.write_calls = 0u;
    assert(gomore_primitives_previous_state_append(
               &pkey_store, appended_state, 5u, sizeof(appended_state),
               NULL, 0u, &append_result) ==
           GOMORE_PRIMITIVES_PREVIOUS_APPEND_OK);
    assert(append_result.slot == 2u &&
           append_result.record_offset == UINT32_C(0xA068) &&
           g_pkey_store_trace.read_calls == 5u);

    uint8_t preserved_key_record[72];
    memcpy(preserved_key_record, g_pkey_store_trace.bytes,
           sizeof(preserved_key_record));
    g_pkey_store_trace.read_calls = 0u;
    g_pkey_store_trace.write_calls = 0u;
    assert(gomore_primitives_previous_state_append(
               &pkey_store, appended_state, 5u, sizeof(appended_state),
               append_scratch, sizeof(append_scratch), &append_result) ==
           GOMORE_PRIMITIVES_PREVIOUS_APPEND_OK);
    assert(append_result.compacted && append_result.slot == 0u &&
           append_result.record_offset == UINT32_C(0xA048) &&
           g_pkey_store_trace.read_calls == 3u &&
           g_pkey_store_trace.erase_calls == 1u &&
           g_pkey_store_trace.write_calls == 3u &&
           g_pkey_store_trace.write_offsets[0] == UINT32_C(0xA000) &&
           g_pkey_store_trace.write_lengths[0] == 72u &&
           memcmp(g_pkey_store_trace.bytes, preserved_key_record, 72u) == 0 &&
           load_u32_fixture(&g_pkey_store_trace.bytes[72]) == 5u &&
           load_u32_fixture(&g_pkey_store_trace.bytes[88]) == UINT32_MAX);

    g_pkey_store_trace.read_calls = 0u;
    g_pkey_store_trace.write_calls = 0u;
    const uint8_t before_bad_capacity = g_pkey_store_trace.bytes[72];
    assert(gomore_primitives_previous_state_append(
               &pkey_store, appended_state, 5u, 5u,
               append_scratch, sizeof(append_scratch), &append_result) ==
           GOMORE_PRIMITIVES_PREVIOUS_APPEND_BAD_ARGUMENT);
    assert(g_pkey_store_trace.read_calls == 0u &&
           g_pkey_store_trace.write_calls == 0u &&
           g_pkey_store_trace.bytes[72] == before_bad_capacity);

    uint8_t oversized_state[948] = {0u};
    g_pkey_store_trace.read_calls = 0u;
    assert(gomore_primitives_previous_state_append(
               &pkey_store, oversized_state, 945u, sizeof(oversized_state),
               append_scratch, sizeof(append_scratch), &append_result) ==
           GOMORE_PRIMITIVES_PREVIOUS_APPEND_TOO_LARGE);
    assert(g_pkey_store_trace.read_calls == 1u &&
           g_pkey_store_trace.write_calls == 0u);

    gomore_primitives_pkey_store invalid_append_store = pkey_store;
    invalid_append_store.write = NULL;
    g_pkey_store_trace.read_calls = 0u;
    assert(gomore_primitives_previous_state_append(
               &invalid_append_store, appended_state, 8u,
               sizeof(appended_state), append_scratch,
               sizeof(append_scratch), &append_result) ==
           GOMORE_PRIMITIVES_PREVIOUS_APPEND_BAD_ARGUMENT);
    assert(g_pkey_store_trace.read_calls == 0u);

    g_pkey_store_trace.fail_read_call = 1u;
    assert(gomore_primitives_previous_state_append(
               &pkey_store, appended_state, 8u, sizeof(appended_state),
               append_scratch, sizeof(append_scratch), &append_result) ==
           GOMORE_PRIMITIVES_PREVIOUS_APPEND_READ_FAILED);
    assert(g_pkey_store_trace.read_calls == 1u &&
           g_pkey_store_trace.write_calls == 0u);
    g_pkey_store_trace.fail_read_call = 0u;

    /* An erased first slot isolates the surfaced header-write failure. */
    store_u32_fixture(&g_pkey_store_trace.bytes[72], UINT32_MAX);
    store_u32_fixture(&g_pkey_store_trace.bytes[104], UINT32_MAX);
    g_pkey_store_trace.read_calls = 0u;
    g_pkey_store_trace.write_calls = 0u;
    g_pkey_store_trace.fail_write_call = 1u;
    assert(gomore_primitives_previous_state_append(
               &pkey_store, appended_state, 8u, sizeof(appended_state),
               append_scratch, sizeof(append_scratch), &append_result) ==
           GOMORE_PRIMITIVES_PREVIOUS_APPEND_WRITE_FAILED);
    assert(g_pkey_store_trace.read_calls == 3u &&
           g_pkey_store_trace.write_calls == 1u);
    g_pkey_store_trace.fail_write_call = 0u;

    /* Reoccupy the trigger slot to exercise allocation and destructive
     * operation failures without hiding partial-write behavior. */
    store_u32_fixture(&g_pkey_store_trace.bytes[104], 5u);
    g_pkey_store_trace.read_calls = 0u;
    assert(gomore_primitives_previous_state_append(
               &pkey_store, appended_state, 8u, sizeof(appended_state),
               append_scratch, 71u, &append_result) ==
           GOMORE_PRIMITIVES_PREVIOUS_APPEND_SCRATCH_TOO_SMALL);
    assert(g_pkey_store_trace.read_calls == 2u &&
           g_pkey_store_trace.erase_calls == 1u);

    g_pkey_store_trace.read_calls = 0u;
    g_pkey_store_trace.fail_erase_call = g_pkey_store_trace.erase_calls + 1u;
    assert(gomore_primitives_previous_state_append(
               &pkey_store, appended_state, 8u, sizeof(appended_state),
               append_scratch, sizeof(append_scratch), &append_result) ==
           GOMORE_PRIMITIVES_PREVIOUS_APPEND_ERASE_FAILED);
    assert(g_pkey_store_trace.read_calls == 3u);
    g_pkey_store_trace.fail_erase_call = 0u;

    pkey_store.initialized = false;
    g_pkey_store_trace.initialize_success = false;
    g_pkey_store_trace.initialize_calls = 0u;
    g_pkey_store_trace.read_calls = 0u;
    assert(gomore_primitives_previous_state_append(
               &pkey_store, appended_state, 8u, sizeof(appended_state),
               append_scratch, sizeof(append_scratch), &append_result) ==
           GOMORE_PRIMITIVES_PREVIOUS_APPEND_STORE_UNAVAILABLE);
    assert(g_pkey_store_trace.initialize_calls == 1u &&
           g_pkey_store_trace.read_calls == 0u);

    uint8_t base64_decoded[6];
    size_t base64_written = 0u;
    memset(base64_decoded, UINT8_C(0xA5), sizeof(base64_decoded));
    assert(gomore_primitives_base64_decode_blocks(
        (const uint8_t *)"TWFu", 4u, base64_decoded,
        sizeof(base64_decoded), &base64_written));
    assert(base64_written == 3u &&
           memcmp(base64_decoded, "Man", 3u) == 0);
    memset(base64_decoded, UINT8_C(0xA5), sizeof(base64_decoded));
    assert(gomore_primitives_base64_decode_blocks(
        (const uint8_t *)"TQ==", 4u, base64_decoded,
        sizeof(base64_decoded), &base64_written));
    assert(base64_written == 1u && base64_decoded[0] == (uint8_t)'M' &&
           base64_decoded[1] == 0u && base64_decoded[2] == 0u);
    assert(!gomore_primitives_base64_decode_blocks(
        (const uint8_t *)"TWE", 3u, base64_decoded,
        sizeof(base64_decoded), &base64_written));
    const uint8_t quantized_mean_values[5] = {80u, 82u, 84u, 0u, 200u};
    const uint8_t sparse_mean_values[5] = {0u, 0u, 0u, 0u, 77u};
    assert(gomore_primitives_dominant_quantized_u8_mean5(
               quantized_mean_values) == 82u);
    assert(gomore_primitives_dominant_quantized_u8_mean5(
               sparse_mean_values) == 77u);
    const uint8_t dual_dominant_values[5] = {70u, 72u, 0u, 69u, 140u};
    const int8_t dual_dominant_categories[5] = {1, 1, -2, 2, 1};
    int32_t dual_dominant_value = -1;
    int32_t dual_dominant_category = -1;
    assert(gomore_primitives_dual_dominant_u8_select(
        dual_dominant_values, dual_dominant_categories,
        &dual_dominant_value, &dual_dominant_category));
    assert(dual_dominant_value == 70 && dual_dominant_category == 1);
    const uint8_t sparse_dominant_values[5] = {0u, 0u, 1u, 0u, 2u};
    const int8_t sparse_dominant_categories[5] = {-2, -2, -2, -2, -2};
    dual_dominant_value = 123;
    dual_dominant_category = 456;
    assert(gomore_primitives_dual_dominant_u8_select(
        sparse_dominant_values, sparse_dominant_categories,
        &dual_dominant_value, &dual_dominant_category));
    assert(dual_dominant_value == 123 && dual_dominant_category == 456);
    update_failure_log_calls = 0u;
    update_failure_reset_calls = 0u;
    update_failure_status = 0u;
    update_failure_timestamp = 0u;
    uint8_t update_failure_counter = 5u;
    assert(gomore_primitives_update_failure_counter(
               0u, 8u, &update_failure_counter,
               update_failure_log_fixture,
               update_failure_reset_fixture) == 1u);
    assert(update_failure_counter == 0u &&
           update_failure_log_calls == 0u &&
           update_failure_reset_calls == 0u);
    assert(gomore_primitives_update_failure_counter(
               7u, 9u, &update_failure_counter,
               update_failure_log_fixture,
               update_failure_reset_fixture) == 0u);
    assert(update_failure_counter == 1u &&
           update_failure_log_calls == 1u &&
           update_failure_status == 7u &&
           update_failure_timestamp == 9u);
    update_failure_counter = 3u;
    assert(gomore_primitives_update_failure_counter(
               8u, 10u, &update_failure_counter,
               update_failure_log_fixture,
               update_failure_reset_fixture) == 0u);
    assert(update_failure_counter == 4u &&
           update_failure_log_calls == 1u);
    update_failure_counter = 59u;
    assert(gomore_primitives_update_failure_counter(
               9u, 11u, &update_failure_counter,
               update_failure_log_fixture,
               update_failure_reset_fixture) == 0u);
    assert(update_failure_counter == 0u &&
           update_failure_reset_calls == 1u);
    int16_t trend_history[5] = {999, 1101, 1102, -1100, -1700};
    assert(gomore_primitives_shift_i16_trend_gate5(
               trend_history, -100) == 1);
    assert(trend_history[0] == 1101 && trend_history[1] == 1102 &&
           trend_history[2] == -1100 && trend_history[3] == -1700 &&
           trend_history[4] == -100);
    assert(gomore_primitives_shift_i16_trend_gate5(
               trend_history, -500) == -1);
    assert(gomore_primitives_shift_i16_trend_gate5(
               trend_history, 1) == 1);
    const float affine_source[4] = {0.0f, 2.0f, 1.0f, 0.0f};
    float first_affine[2] = {1.0f, 3.0f};
    float second_affine[2] = {5.0f, 0.0f};
    uint32_t first_affine_mode = UINT32_MAX;
    uint32_t second_affine_mode = UINT32_MAX;
    assert(gomore_primitives_sps_refresh_affine_pairs(
        affine_source, first_affine, &first_affine_mode,
        second_affine, &second_affine_mode));
    assert(first_affine[0] == 1.0f && first_affine[1] == 2.0f &&
           first_affine_mode == 1u && second_affine[0] == 1.0f &&
           second_affine[1] == 0.0f && second_affine_mode == 0u);
    float quadratic_roots[2] = {-1.0f, -1.0f};
    assert(gomore_primitives_positive_quadratic_roots(
        1.0f, -3.0f, 2.0f, quadratic_roots,
        quadratic_power_fixture));
    assert(quadratic_roots[0] == 2.0f && quadratic_roots[1] == 1.0f);
    assert(gomore_primitives_positive_quadratic_roots(
        1.0f, 1.0f, 1.0f, quadratic_roots,
        quadratic_power_fixture));
    assert(quadratic_roots[0] == 0.0f && quadratic_roots[1] == 0.0f);
    quadratic_roots[0] = 4.0f;
    quadratic_roots[1] = 5.0f;
    assert(gomore_primitives_positive_quadratic_roots(
        1.0f, 3.0f, 2.0f, quadratic_roots,
        quadratic_power_fixture));
    assert(quadratic_roots[0] == 4.0f && quadratic_roots[1] == 5.0f);
    float variability_axes[3][25];
    for (size_t index = 0u; index < 25u; ++index) {
        variability_axes[0][index] = 1300.0f;
        variability_axes[1][index] = 0.0f;
        variability_axes[2][index] = 0.0f;
    }
    const float *variability_axis_pointers[3] = {
        variability_axes[0], variability_axes[1], variability_axes[2]};
    float activity_score = 1.0f;
    variability_sqrt_calls = 0u;
    assert(gomore_primitives_activity_score_variability_adjust(
        &activity_score, variability_axis_pointers, false,
        variability_sqrt_fixture));
    assert(activity_score == 1.0f && variability_sqrt_calls == 51u);
    const float *empty_axis_pointers[3] = {NULL, NULL, NULL};
    activity_score = 2.0f;
    assert(gomore_primitives_activity_score_variability_adjust(
        &activity_score, empty_axis_pointers, true,
        variability_sqrt_fixture));
    assert(activity_score == 1.8f && variability_sqrt_calls == 51u);
    assert(sizeof(gomore_primitives_civil_time) == 16u);
    gomore_primitives_civil_time civil_time;
    memset(&civil_time, UINT8_C(0xA5), sizeof(civil_time));
    assert(gomore_primitives_epoch_to_civil_time(0u, &civil_time));
    assert(civil_time.timestamp == 0u && civil_time.year == 1970 &&
           civil_time.month == 1u && civil_time.day == 1u &&
           civil_time.hour == 0u && civil_time.minute == 0u &&
           civil_time.second == 0u && civil_time.reserved == 0u &&
           civil_time.padding[0] == UINT8_C(0xA5));
    assert(gomore_primitives_epoch_to_civil_time(
        UINT32_C(951782400), &civil_time));
    assert(civil_time.year == 2000 && civil_time.month == 2u &&
           civil_time.day == 29u && civil_time.hour == 0u);
    assert(gomore_primitives_epoch_to_civil_time(
        UINT32_C(1700000000), &civil_time));
    assert(civil_time.year == 2023 && civil_time.month == 11u &&
           civil_time.day == 14u && civil_time.hour == 22u &&
           civil_time.minute == 13u && civil_time.second == 20u);
    uint8_t algorithm_snapshot_source[
        GOMORE_PRIMITIVES_ALGORITHM_SNAPSHOT_SOURCE_BYTES];
    uint8_t algorithm_snapshot_destination[
        GOMORE_PRIMITIVES_ALGORITHM_SNAPSHOT_DESTINATION_BYTES];
    for (size_t index = 0u; index < sizeof(algorithm_snapshot_source);
            ++index) {
        algorithm_snapshot_source[index] = (uint8_t)index;
    }
    memset(algorithm_snapshot_destination, UINT8_C(0xA5),
           sizeof(algorithm_snapshot_destination));
    assert(gomore_primitives_copy_algorithm_output_snapshot(
        algorithm_snapshot_destination,
        sizeof(algorithm_snapshot_destination),
        algorithm_snapshot_source, sizeof(algorithm_snapshot_source)));
    assert(algorithm_snapshot_destination[0] == UINT8_C(0xA5) &&
           algorithm_snapshot_destination[0x33] == UINT8_C(0x19) &&
           algorithm_snapshot_destination[0x44] == UINT8_C(0xC2) &&
           algorithm_snapshot_destination[0x45] == UINT8_C(0xC3) &&
           algorithm_snapshot_destination[0x58] == UINT8_C(0x24) &&
           algorithm_snapshot_destination[0x5B] == UINT8_C(0x27) &&
           algorithm_snapshot_destination[0x70] == UINT8_C(0xDE) &&
           algorithm_snapshot_destination[0x73] == UINT8_C(0xE1) &&
           algorithm_snapshot_destination[0x78] == UINT8_C(0x08) &&
           algorithm_snapshot_destination[0x7F] == UINT8_C(0x11) &&
           algorithm_snapshot_destination[0x82] == UINT8_C(0x80) &&
           algorithm_snapshot_destination[0xA0] == UINT8_C(0x84) &&
           algorithm_snapshot_destination[0xA7] == UINT8_C(0x8B));
    assert(!gomore_primitives_copy_algorithm_output_snapshot(
        algorithm_snapshot_destination,
        sizeof(algorithm_snapshot_destination) - 1u,
        algorithm_snapshot_source, sizeof(algorithm_snapshot_source)));
    assert(sizeof(gomore_primitives_sleep_descriptor) == 40u);
    float sleep_descriptor_history[15];
    for (size_t index = 0u; index < 15u; ++index) {
        sleep_descriptor_history[index] = 1.0f;
    }
    gomore_primitives_sleep_descriptor sleep_descriptor;
    assert(gomore_primitives_sleep_descriptor_initialize(
        &sleep_descriptor, sleep_descriptor_history, false,
        900u, 0u, 7u, false));
    assert(sleep_descriptor.type == 2u && sleep_descriptor.profile == 7u &&
           sleep_descriptor.preceding_count == 15u &&
           sleep_descriptor.start == 0u && sleep_descriptor.tail == 0u);
    sleep_descriptor_history[13] = 0.6f;
    assert(gomore_primitives_sleep_descriptor_initialize(
        &sleep_descriptor, sleep_descriptor_history, true,
        900u, 0u, 8u, false));
    assert(sleep_descriptor.preceding_count == 1u &&
           sleep_descriptor.start == 840u &&
           sleep_descriptor.profile == 8u);
    assert(gomore_primitives_sleep_descriptor_initialize(
        &sleep_descriptor, NULL, true, 1234u, 5u, 9u, true));
    assert(sleep_descriptor.preceding_count == 0u &&
           sleep_descriptor.start == 1234u);
    const float sliding_input[4] = {1.0f, 2.0f, 3.0f, 4.0f};
    float sliding_output[4];
    size_t sliding_written = 0u;
    assert(gomore_primitives_sliding_window_mean(
        sliding_input, 1u, 4u, 3u, 1u, 1u,
        sliding_output, 4u, &sliding_written));
    assert(sliding_written == 4u && sliding_output[0] == 1.0f &&
           sliding_output[1] == 2.0f && sliding_output[2] == 3.0f &&
           sliding_output[3] > 2.33f && sliding_output[3] < 2.34f);
    uint8_t profile_state[0x39D8];
    memset(profile_state, 0, sizeof(profile_state));
    profile_state[0x3996] = 4u;
    assert(gomore_primitives_profile_state_apply(
               profile_state, sizeof(profile_state), 0, 2, 9u) == 0);
    assert(profile_state[0x3996] == 4u &&
           profile_state[0x3986] == 3u &&
           profile_state[0x39D4] == 0u);
    profile_state[0x39CA] = 4u;
    assert(gomore_primitives_profile_state_apply(
               profile_state, sizeof(profile_state), 11, 1, 9u) == 0);
    assert(profile_state[0x39CA] == 1u &&
           profile_state[0x39D4] == 11u);
    assert(gomore_primitives_profile_state_apply(
               profile_state, sizeof(profile_state), 7, 2, 9u) == -1);
    assert(profile_state[0x39D4] == UINT8_C(0xFF) &&
           profile_state[0x39D7] == UINT8_C(0xFF));
    float percentile_values[5] = {5.0f, 1.0f, 3.0f, 2.0f, 4.0f};
    float percentile_result = 0.0f;
    assert(gomore_primitives_sorted_percentile(
        percentile_values, 5u, 60u, sort_values,
        compare_float, &percentile_result));
    assert(percentile_result > 3.39f && percentile_result < 3.41f);
    assert(gomore_primitives_sorted_percentile(
        percentile_values, 5u, 0u, sort_values,
        compare_float, &percentile_result));
    assert(percentile_result == 1.0f);
    assert(gomore_primitives_sorted_percentile(
        percentile_values, 5u, 100u, sort_values,
        compare_float, &percentile_result));
    assert(percentile_result == 5.0f);
    gomore_primitives_sps_selection sps_selection;
    memset(&sps_selection, 0, sizeof(sps_selection));
    sps_selection_log_calls = 0u;
    assert(gomore_primitives_sps_select_available(
               -1.0f, 2.0f, 3.0f, 7u,
               sps_selection_log_fixture, &sps_selection) == 1u);
    assert(sps_selection.value == 2.0f &&
           sps_selection.reciprocal_hours == 1800.0f &&
           sps_selection.source == 1u && sps_selection.auxiliary == 7u &&
           sps_selection_log_calls == 1u &&
           sps_selection_log_values[0] == -1.0f);
    assert(gomore_primitives_sps_select_available(
               -1.0f, -2.0f, -3.0f, 8u,
               NULL, &sps_selection) == UINT32_C(0x40));
    assert(sps_selection.value == -1.0f &&
           sps_selection.reciprocal_hours == 0.0f &&
           sps_selection.source == 3u && sps_selection.auxiliary == 8u);
    assert(sizeof(gomore_primitives_statistics_accumulator) == 36u);
    gomore_primitives_statistics_accumulator statistics_accumulator;
    memset(&statistics_accumulator, 0, sizeof(statistics_accumulator));
    assert(gomore_primitives_statistics_accumulate(
        &statistics_accumulator, 3u, true, false,
        1.0f, false, false, 40.0f));
    assert(statistics_accumulator.observations == 1u &&
           statistics_accumulator.upper_count == 3u &&
           statistics_accumulator.lower_count == 2u &&
           statistics_accumulator.positive_count == 1u &&
           statistics_accumulator.quality_count == 1u &&
           statistics_accumulator.mean_count == 1u &&
           statistics_accumulator.mean == 40.0f);
    assert(gomore_primitives_statistics_accumulate(
        &statistics_accumulator, 1u, false, true,
        0.0f, false, true, 240.0f));
    assert(statistics_accumulator.observations == 2u &&
           statistics_accumulator.upper_count == 3u &&
           statistics_accumulator.lower_count == 3u &&
           statistics_accumulator.positive_count == 1u &&
           statistics_accumulator.quality_count == 1u &&
           statistics_accumulator.mean_count == 2u &&
           statistics_accumulator.mean == 140.0f);
    assert(gomore_primitives_statistics_accumulate(
        &statistics_accumulator, 1u, false, false,
        -1.0f, true, true, 39.0f));
    assert(statistics_accumulator.quality_count == 2u &&
           statistics_accumulator.mean_count == 2u &&
           statistics_accumulator.mean == 140.0f);
    assert(sizeof(gomore_primitives_interval_descriptor) == 40u);
    gomore_primitives_interval_descriptor previous_interval;
    gomore_primitives_interval_descriptor addition_interval;
    gomore_primitives_interval_descriptor merged_interval;
    memset(&previous_interval, 0, sizeof(previous_interval));
    memset(&addition_interval, 0, sizeof(addition_interval));
    previous_interval.start = 120u;
    previous_interval.totals[0] = 2;
    previous_interval.totals[4] = 5;
    previous_interval.mean = 10.0f;
    previous_interval.mean_count = 2;
    addition_interval.totals[0] = 3;
    addition_interval.totals[4] = 7;
    addition_interval.mean = 20.0f;
    addition_interval.mean_count = 1;
    assert(gomore_primitives_interval_descriptor_merge(
        &merged_interval, 999u, false,
        &previous_interval, &addition_interval, 6u));
    assert(merged_interval.start == 120u && merged_interval.type == 3u &&
           merged_interval.profile == 6u && merged_interval.totals[0] == 5 &&
           merged_interval.totals[4] == 12 &&
           merged_interval.mean_count == 3 &&
           merged_interval.mean > 13.33f && merged_interval.mean < 13.34f);
    assert(gomore_primitives_interval_descriptor_merge(
        &merged_interval, 999u, true, NULL, NULL, 7u));
    assert(merged_interval.start == 999u && merged_interval.type == 3u &&
           merged_interval.profile == 7u && merged_interval.mean_count == 0);
    assert(sizeof(gomore_primitives_step_accumulator) == 28u);
    gomore_primitives_step_accumulator step_accumulator;
    memset(&step_accumulator, 0, sizeof(step_accumulator));
    step_accumulator.required_streak = 2u;
    float completed_step = -1.0f;
    assert(gomore_primitives_step_accumulate(
        &step_accumulator, 2u, 1u, &completed_step));
    assert(completed_step == 0.0f &&
           step_accumulator.positive_streak == 1u &&
           step_accumulator.accumulated > 0.066f &&
           step_accumulator.accumulated < 0.067f);
    assert(gomore_primitives_step_accumulate(
        &step_accumulator, 2u, 1u, &completed_step));
    assert(completed_step > 0.133f && completed_step < 0.134f &&
           step_accumulator.positive_streak == 2u &&
           step_accumulator.accumulated == 0.0f);
    assert(gomore_primitives_step_accumulate(
        &step_accumulator, 2u, 0u, &completed_step));
    assert(step_accumulator.positive_streak == 0u &&
           step_accumulator.zero_streak == 1u &&
           step_accumulator.accumulated == 0.0f);
    uint8_t packed_timeline[720];
    memset(packed_timeline, 0, sizeof(packed_timeline));
    assert(gomore_primitives_packed_2bit_set(
        packed_timeline, sizeof(packed_timeline), 0u, 1u));
    assert(gomore_primitives_packed_2bit_set(
        packed_timeline, sizeof(packed_timeline), 1u, 2u));
    assert(gomore_primitives_packed_2bit_set(
        packed_timeline, sizeof(packed_timeline), 2u, 3u));
    uint8_t timeline_output[3] = {9u, 9u, 9u};
    size_t timeline_written = 0u;
    assert(gomore_primitives_packed_timeline_extract(
        packed_timeline, sizeof(packed_timeline),
        0u, 90u, 60u, 0u, 0u,
        timeline_output, sizeof(timeline_output), &timeline_written));
    assert(timeline_written == 3u && timeline_output[0] == 0u &&
           timeline_output[1] == 0u && timeline_output[2] == 3u);
    assert(sizeof(gomore_primitives_sleep_interval_source) == 40u);
    assert(sizeof(gomore_primitives_sleep_interval_result) == 32u);
    float interval_history[15];
    for (size_t index = 0u; index < 15u; ++index) {
        interval_history[index] = 1.0f;
    }
    gomore_primitives_sleep_interval_source interval_source;
    memset(&interval_source, 0, sizeof(interval_source));
    interval_source.start = 0u;
    interval_source.end = 120u;
    interval_source.count = 1u;
    interval_source.sum = 1;
    interval_source.metric = 50.0f;
    interval_source.type = 1u;
    gomore_primitives_sleep_interval_policy interval_policy = {
        .minimum_slots = 1,
        .reserved = 0u,
        .disable_history_scan = 0u,
        .reserved5 = 0u,
        .end_hour = 24u,
        .begin_hour = 0u,
    };
    gomore_primitives_sleep_interval_result interval_result;
    assert(gomore_primitives_sleep_interval_build(
        &interval_result, interval_history, false,
        0u, 0u, 0, 55u, 0, 0, 7u,
        &interval_source, &interval_policy));
    assert(interval_result.start == 0u && interval_result.end == 120u &&
           interval_result.source_start == 0u &&
           interval_result.source_end == 120u &&
           interval_result.metadata == 55u &&
           interval_result.flags == 12u &&
           interval_result.auxiliary == 7u && interval_result.status == 3u);
    interval_source.end = 60000u;
    interval_source.count = 10u;
    interval_source.sum = 10;
    assert(gomore_primitives_sleep_interval_build(
        &interval_result, interval_history, false,
        0u, 0u, 1, 56u, 0, 0, 8u,
        &interval_source, &interval_policy));
    assert(interval_result.status == 2u);
    interval_source.end = 120u;
    interval_source.metric = 100.0f;
    assert(gomore_primitives_sleep_interval_build(
        &interval_result, interval_history, false,
        0u, 0u, 1, 57u, 0, 0, 9u,
        &interval_source, &interval_policy));
    assert(interval_result.status == 1u);
    gomore_primitives_sleep_interval_result previous_sleep_interval;
    gomore_primitives_sleep_interval_result current_sleep_interval;
    memset(&previous_sleep_interval, 0, sizeof(previous_sleep_interval));
    memset(&current_sleep_interval, 0, sizeof(current_sleep_interval));
    previous_sleep_interval.flags = 8u;
    current_sleep_interval.start = 2000u;
    current_sleep_interval.end = 4000u;
    current_sleep_interval.flags = 8u;
    assert(gomore_primitives_sleep_interval_refine(
        &interval_result, &previous_sleep_interval, &current_sleep_interval,
        1800, 1000, 100));
    assert(interval_result.status == 5u && interval_result.start == 2000u);
    current_sleep_interval.start = 120u;
    current_sleep_interval.end = 240u;
    assert(gomore_primitives_sleep_interval_refine(
        &interval_result, &previous_sleep_interval, &current_sleep_interval,
        10, 1, 100));
    assert(interval_result.status == 0u && interval_result.start == 0u);
    interval_source.metric = 50.0f;
    interval_source.start = 120u;
    interval_source.end = 251u;
    assert(gomore_primitives_sleep_interval_compose(
        &interval_result, interval_history, false,
        0u, 0u, 1, 58u, 0, 0, 10u,
        &interval_source, &interval_policy, &previous_sleep_interval,
        10, 1, 100));
    assert(interval_result.start == 0u && interval_result.end == 240u &&
           interval_result.status == 0u);
    gomore_primitives_sleep_interval_context interval_context;
    memset(&interval_context, 0, sizeof(interval_context));
    interval_context.stored = previous_sleep_interval;
    interval_context.stored.start = 33u;
    interval_context.stored.flags = 8u;
    assert(gomore_primitives_sleep_interval_select(
        &interval_result, &interval_context, 120u, 0));
    assert(interval_result.start == 33u && interval_result.flags == 8u);
    interval_context.enabled = true;
    interval_context.base_source = interval_source;
    interval_context.base_source.start = 0u;
    interval_context.base_source.metric = 50.0f;
    interval_context.base_source.count = 1u;
    interval_context.base_source.sum = 1;
    interval_context.base_source.type = 1u;
    interval_context.stored.start = 0u;
    interval_context.stored.end = 0u;
    interval_context.stored.flags = 8u;
    interval_context.aggregation.totals[0] = 10;
    interval_context.aggregation.totals[3] = 1;
    interval_context.policy.minimum_slots = 1;
    interval_context.policy.end_hour = 24u;
    for (size_t index = 0u; index < 15u; ++index) {
        interval_context.history[index] = 1.0f;
    }
    assert(gomore_primitives_sleep_interval_select(
        &interval_result, &interval_context, 120u, 0));
    assert(interval_result.start == 0u && interval_result.end == 120u &&
           interval_result.flags == 12u && interval_result.status == 0u);
    uint8_t interval_policy_source[10] = {
        0u, 0u, 1u, 0u, 0u, 0u, 0u, 0u, 24u, 0u};
    interval_context.enabled = false;
    interval_result.flags = UINT8_C(0xFF);
    assert(gomore_primitives_sleep_interval_run(
               &interval_context, 120u, 0, 1,
               NULL, 0u, &interval_result) == UINT32_C(0x40));
    assert(interval_result.flags == 0u);
    interval_context.enabled = true;
    assert(gomore_primitives_sleep_interval_run(
               &interval_context, 120u, 0, 1,
               interval_policy_source, sizeof(interval_policy_source),
               &interval_result) == 0u);
    assert(interval_result.start == 0u && interval_result.end == 120u &&
           interval_result.flags == 12u && interval_result.auxiliary == 5u &&
           interval_result.status == 0u && !interval_context.enabled &&
           interval_context.control_profile == 3u &&
           interval_context.control_auxiliary == 5u &&
           interval_context.base_source.start == 120u &&
           interval_context.base_source.type == 3u &&
           interval_context.base_source.profile == 3u &&
           interval_context.policy.minimum_slots == 1 &&
           interval_context.policy.end_hour == 24u);
    interval_context.enabled = true;
    uint8_t interval_pending = UINT8_C(0xA5);
    uint8_t interval_compact_output[56];
    memset(interval_compact_output, UINT8_C(0xA5),
           sizeof(interval_compact_output));
    uint8_t interval_update_packed[1001];
    memset(interval_update_packed, 0, sizeof(interval_update_packed));
    interval_update_packed[0x2D0] = 90u;
    interval_update_packed[1000] = 1u;
    assert(gomore_primitives_packed_2bit_set(
        interval_update_packed, 0x2D0u, 1u, 2u));
    uint8_t interval_propagated = 0u;
    assert(gomore_primitives_sleep_interval_update(
        &interval_context, 240u, 0, 1,
        interval_policy_source, sizeof(interval_policy_source),
        &interval_pending, interval_compact_output,
        sizeof(interval_compact_output), 2u,
        interval_update_packed, sizeof(interval_update_packed),
        &interval_propagated));
    assert(interval_pending == 0u &&
           memcmp(interval_compact_output, &interval_context.stored, 8u) == 0 &&
           interval_compact_output[8] == interval_context.stored.flags &&
           interval_compact_output[9] == 5u &&
           interval_compact_output[10] == interval_context.stored.status &&
           interval_compact_output[12] == 0u &&
           interval_propagated == 2u &&
           interval_update_packed[1000] == 0u);
    tier2_trace interval_dispatch_trace = {0};
    active_tier2_trace = &interval_dispatch_trace;
    uint8_t interval_dispatch_output[12] = {0};
    interval_dispatch_output[8] = UINT8_C(0xEF);
    interval_dispatch_output[9] = UINT8_C(0xBE);
    interval_dispatch_output[10] = UINT8_C(0xAD);
    interval_dispatch_output[11] = UINT8_C(0xDE);
    assert(gomore_primitives_sleep_interval_dispatch(
        &interval_context, 120u, 0, UINT32_C(0x12345678),
        interval_dispatch_output, sizeof(interval_dispatch_output),
        1u, 2u, 4u, 5u, consume_stage) == 0);
    assert(interval_dispatch_trace.consume_calls == 1u &&
           interval_dispatch_trace.staged[0] == UINT8_C(0x78) &&
           interval_dispatch_trace.staged[3] == UINT8_C(0x12) &&
           interval_dispatch_output[8] == UINT8_C(0xEF) &&
           interval_dispatch_output[11] == UINT8_C(0xDE));
    const uint16_t crossings[6] = {900u, 1201u, 1100u,
                                    999u, 1300u, 900u};
    assert(gomore_primitives_count_hysteresis_crossings(crossings, 6u) == 2u);
    assert(gomore_primitives_nullable_compare_n(
               (const uint8_t *)"abc", (const uint8_t *)"abd", 3u) == -1);
    assert(gomore_primitives_nullable_compare_n(NULL, NULL, 0u) == 0xFFFF);
    uint8_t interval_record[0x1B];
    memset(interval_record, 0, sizeof(interval_record));
    interval_record[0] = 0xE8u;
    interval_record[1] = 0x03u;
    interval_record[4] = 0xD0u;
    interval_record[5] = 0x07u;
    interval_record[0x1A] = 8u;
    assert(gomore_primitives_recent_interval_predicate(
        interval_record, sizeof(interval_record), 2500u));
    uint8_t quality_record[0x3D];
    memset(quality_record, 0, sizeof(quality_record));
    quality_record[0x2F] = 0x43u;
    quality_record[0x33] = 0x43u;
    assert(gomore_primitives_record_quality_classify(
               quality_record, sizeof(quality_record)) == 1);
    quality_record[0x3B] = 1u;
    quality_record[0x3C] = 1u;
    assert(gomore_primitives_record_quality_classify(
               quality_record, sizeof(quality_record)) == 2);

    memset(&active_closure_trace, 0, sizeof(active_closure_trace));
    uint32_t stored_seed = 0u;
    assert(gomore_primitives_seeded_random_offset(
               UINT32_C(0x12345678), &stored_seed,
               closure_prepare, closure_random) == 100);
    assert(stored_seed == UINT32_C(0x12345678) &&
           active_closure_trace.prepare_calls == 1u);
    assert(gomore_primitives_allocate_mode2_state(
               9u, closure_allocate, closure_allocated_initialize) ==
           closure_allocation);
    assert(active_closure_trace.allocation_length == 0x23Cu &&
           closure_allocation[0] == 2u &&
           active_closure_trace.binding == 9u);
    assert(gomore_primitives_allocate_mode1_state(
               10u, closure_allocate, closure_allocated_initialize) ==
           closure_allocation);
    assert(active_closure_trace.allocation_length == 0x238u &&
           closure_allocation[0] == 1u &&
           active_closure_trace.binding == 10u);
    const uint32_t mode0_descriptors[7] = {
        2u, 3u, UINT32_C(0x11111111), UINT32_C(0x22222222),
        5u, UINT32_C(0x33333333), UINT32_C(0x44444444),
    };
    assert(gomore_primitives_allocate_mode0_state_remap(
               11u, mode0_descriptors, sizeof(mode0_descriptors),
               UINT32_C(0x20001000), closure_allocate,
               closure_mode0_initialize) == closure_allocation);
    assert(active_closure_trace.allocation_length == 0x2DCu &&
           load_u32_fixture(closure_allocation) == 0u &&
           active_closure_trace.binding == 11u &&
           load_u32_fixture(&closure_allocation[0x238u]) ==
               UINT32_C(0xA1B2C3D4) &&
           load_u32_fixture(&closure_allocation[0x244u]) ==
               UINT32_C(0x20001008) &&
           load_u32_fixture(&closure_allocation[0x24Cu]) ==
               UINT32_C(0x20001014));
    const uint32_t invalid_mode0_descriptors[3] = {1u, 41u, 0u};
    active_closure_trace.allocation_length = 0u;
    assert(gomore_primitives_allocate_mode0_state_remap(
               11u, invalid_mode0_descriptors,
               sizeof(invalid_mode0_descriptors), UINT32_C(0x20001000),
               closure_allocate, closure_mode0_initialize) == NULL);
    assert(active_closure_trace.allocation_length == 0u);
    assert(gomore_primitives_allocate_mode0_state_remap(
               11u, NULL, 0u, 0u, NULL,
               closure_mode0_initialize) == NULL);
    assert(gomore_primitives_decimal_parse((const uint8_t *)"1234") ==
           1234);
    const uint32_t tensor_descriptor[3] = {2u, 3u, 4u};
    assert(gomore_primitives_tensor_call_optional_finish(
               tensor_descriptor, 4u, 5u, true, closure_tensor_call,
               closure_tensor_finish) == 9u);
    assert(active_closure_trace.tensor_calls == 1u &&
           active_closure_trace.finish_calls == 1u);
    uint8_t classes[256];
    memset(classes, 0, sizeof(classes));
    classes[(uint8_t)' '] = 0x20u;
    const uint8_t class_bytes[3] = {' ', ' ', ' '};
    assert(gomore_primitives_all_class_0x20(
               class_bytes, sizeof(class_bytes), classes) == 0);
    classes[(uint8_t)' '] = 0u;
    assert(gomore_primitives_all_class_0x20(
               class_bytes, sizeof(class_bytes), classes) == -1);
    uint8_t filter_state[0x18C];
    memset(filter_state, UINT8_C(0xA5), sizeof(filter_state));
    assert(gomore_primitives_filter_state_initialize(
        filter_state, sizeof(filter_state), closure_filter_initialize));
    assert(filter_state[0] == 0u && filter_state[0x18B] == 0u &&
           active_closure_trace.filter_calls == 1u);
    gomore_primitives_quality_sample quality_samples[3] = {
        {1.0f, 0}, {-1.0f, 0}, {3.0f, INT32_C(0x3727C5AC)}};
    uint8_t quality_destination[0x24];
    memset(quality_destination, UINT8_C(0xA5),
           sizeof(quality_destination));
    assert(gomore_primitives_quality_samples_copy(
        quality_destination, sizeof(quality_destination), quality_samples));
    assert(quality_destination[0x18] == 0u &&
           quality_destination[0x1B] == 0x3Fu &&
           quality_destination[0x1C] == UINT8_C(0xA5) &&
           quality_destination[0x20] == UINT8_C(0xA5));

    const float cardano_root_of_unity[2] = {1.0f, 0.0f};
    float cardano_first[2] = {8.0f, 7.0f};
    float cardano_second[2] = {27.0f, 7.0f};
    uint8_t cardano_destination[0x24];
    memset(cardano_destination, UINT8_C(0xA5),
           sizeof(cardano_destination));
    g_cardano_power_calls = 0u;
    assert(gomore_primitives_cardano_candidates(
        0.0f, 1.0f, 0.0f,
        cardano_destination, sizeof(cardano_destination),
        cardano_root_of_unity, cardano_first, cardano_second,
        cardano_power_fixture, NULL, NULL, NULL, NULL, NULL, NULL));
    assert(g_cardano_power_calls == 2u &&
           cardano_first[0] == 2.0f &&
           float_bits(cardano_first[1]) == UINT32_C(0x358637BD) &&
           cardano_second[0] == 3.0f && cardano_second[1] == 0.0f);
    assert(load_u32_fixture(&cardano_destination[0x18u]) ==
               float_bits(5.0f) &&
           load_u32_fixture(&cardano_destination[0x1Cu]) ==
               float_bits(5.0f) &&
           load_u32_fixture(&cardano_destination[0x20u]) ==
               float_bits(5.0f));

    cardano_first[0] = 1.0f;
    cardano_first[1] = 0.0f;
    cardano_second[0] = 1.0f;
    cardano_second[1] = 0.0f;
    memset(cardano_destination, UINT8_C(0xA5),
           sizeof(cardano_destination));
    g_cardano_math_calls = 0u;
    assert(gomore_primitives_cardano_candidates(
        -1.0f, 1.0f, 0.0f,
        cardano_destination, sizeof(cardano_destination),
        cardano_root_of_unity, cardano_first, cardano_second,
        NULL, cardano_atan2_fixture, cardano_sqrt_fixture,
        cardano_log_fixture, cardano_exp_fixture,
        cardano_cos_fixture, cardano_sin_fixture));
    assert(g_cardano_math_calls == 12u &&
           cardano_first[0] == 1.0f && cardano_first[1] == 0.0f &&
           cardano_second[0] == 1.0f && cardano_second[1] == 0.0f);
    assert(load_u32_fixture(&cardano_destination[0x18u]) ==
               float_bits(2.0f) &&
           load_u32_fixture(&cardano_destination[0x1Cu]) ==
               float_bits(2.0f) &&
           load_u32_fixture(&cardano_destination[0x20u]) ==
               float_bits(2.0f));

    cardano_first[0] = 8.0f;
    cardano_first[1] = 7.0f;
    assert(!gomore_primitives_cardano_candidates(
        0.0f, 1.0f, 0.0f,
        cardano_destination, sizeof(cardano_destination) - 1u,
        cardano_root_of_unity, cardano_first, cardano_second,
        cardano_power_fixture, NULL, NULL, NULL, NULL, NULL, NULL));
    assert(cardano_first[0] == 8.0f && cardano_first[1] == 7.0f);

    memset(cardano_destination, UINT8_C(0xA5),
           sizeof(cardano_destination));
    g_cubic_power_calls = 0u;
    assert(gomore_primitives_cubic_candidates(
        1.0f, -6.0f, 12.0f, -8.0f,
        cardano_destination, sizeof(cardano_destination),
        cubic_power_fixture, NULL, NULL, NULL, NULL, NULL, NULL));
    assert(g_cubic_power_calls == 9u &&
           load_u32_fixture(&cardano_destination[0x18u]) ==
               UINT32_C(0x40000000) &&
           load_u32_fixture(&cardano_destination[0x1Cu]) ==
               UINT32_C(0x3FFFFFF9) &&
           load_u32_fixture(&cardano_destination[0x20u]) ==
               UINT32_C(0x40000004));
    g_cubic_power_calls = 0u;
    assert(!gomore_primitives_cubic_candidates(
        1.0f, -6.0f, 12.0f, -8.0f,
        cardano_destination, sizeof(cardano_destination) - 1u,
        cubic_power_fixture, NULL, NULL, NULL, NULL, NULL, NULL));
    assert(g_cubic_power_calls == 0u);

    uint8_t dual_output[0x38];
    memset(dual_output, 0, sizeof(dual_output));
    assert(gomore_primitives_dual_stage(
        1u, 2u, 3u, 4u, dual_output, sizeof(dual_output),
        closure_first_stage, closure_second_stage));
    assert(dual_output[0] == 0x11u && dual_output[0x1C] == 0x22u &&
           active_closure_trace.first_stage_calls == 1u &&
           active_closure_trace.second_stage_calls == 1u);
    uint8_t composite_record[0x31];
    memset(composite_record, UINT8_C(0xA5), sizeof(composite_record));
    assert(gomore_primitives_composite_record_initialize(
        composite_record, sizeof(composite_record), closure_tail_initialize));
    assert(composite_record[0] == 0u && composite_record[0x2E] == 0u &&
           composite_record[0x30] == 0x5Au);
    uint8_t quality_code = 0xAAu;
    uint8_t quality_code_record[0x3E];
    memset(quality_code_record, 0, sizeof(quality_code_record));
    quality_code_record[0x38] = 0xFFu;
    assert(gomore_primitives_quality_code(
        quality_code_record, sizeof(quality_code_record), &quality_code));
    assert(quality_code == 0u);
    const int16_t stddev_values[3] = {1, 2, 3};
    assert(gomore_primitives_i16_standard_deviation(
               stddev_values, 3u, 2, sqrt_passthrough) == 1.0f);
    const int16_t locomotion_first[3] = {0, 3, 6};
    const int16_t locomotion_second[3] = {10, 10, 10};
    const int16_t locomotion_third[3] = {-3, 0, 3};
    const int16_t locomotion_fourth[3] = {1, 4, 7};
    const int16_t *locomotion_channels[4] = {
        locomotion_first, locomotion_second,
        locomotion_third, locomotion_fourth,
    };
    gomore_primitives_locomotion_summary_state locomotion_summary = {0};
    locomotion_summary.next_slot = 7u;
    locomotion_summary_sqrt_calls = 0u;
    assert(gomore_primitives_locomotion_summary_update(
        &locomotion_summary, locomotion_channels, 3u,
        locomotion_summary_sqrt));
    assert(locomotion_summary.next_slot == 0u &&
           locomotion_summary_sqrt_calls == 4u &&
           locomotion_summary_sqrt_inputs[0] == 9.0f &&
           locomotion_summary_sqrt_inputs[1] == 0.0f &&
           locomotion_summary_sqrt_inputs[2] == 9.0f &&
           locomotion_summary_sqrt_inputs[3] == 9.0f &&
           locomotion_summary.means[0][7] == 3 &&
           locomotion_summary.means[1][7] == 10 &&
           locomotion_summary.means[2][7] == 0 &&
           locomotion_summary.means[3][7] == 4 &&
           locomotion_summary.standard_deviations[0][7] == 3 &&
           locomotion_summary.standard_deviations[1][7] == 0 &&
           locomotion_summary.standard_deviations[2][7] == 3 &&
           locomotion_summary.standard_deviations[3][7] == 3 &&
           locomotion_summary.fourth_range[7] == 6 &&
           locomotion_summary.mean_absolute_differences[0][7] == 3 &&
           locomotion_summary.mean_absolute_differences[1][7] == 0 &&
           locomotion_summary.mean_absolute_differences[2][7] == 3 &&
           locomotion_summary.mean_absolute_differences[3][7] == 3);
    locomotion_summary_sqrt_calls = 0u;
    assert(gomore_primitives_locomotion_summary_update(
        &locomotion_summary, locomotion_channels, 3u,
        locomotion_summary_sqrt));
    assert(locomotion_summary.next_slot == 1u &&
           locomotion_summary.means[0][0] == 3 &&
           locomotion_summary.standard_deviations[3][0] == 3 &&
           locomotion_summary.fourth_range[0] == 6 &&
           locomotion_summary.mean_absolute_differences[2][0] == 3);
    const uint8_t locomotion_slot_before = locomotion_summary.next_slot;
    const int16_t *invalid_locomotion_channels[4] = {
        locomotion_first, NULL, locomotion_third, locomotion_fourth,
    };
    assert(!gomore_primitives_locomotion_summary_update(
        &locomotion_summary, invalid_locomotion_channels, 3u,
        locomotion_summary_sqrt));
    assert(locomotion_summary.next_slot == locomotion_slot_before);
    uint8_t energy_formula_state[0x26];
    memset(energy_formula_state, 0, sizeof(energy_formula_state));
    const float energy_state_value = 2.0f;
    const float energy_multiplier = 3.0f;
    memcpy(&energy_formula_state[0], &energy_state_value, sizeof(float));
    memcpy(&energy_formula_state[4], &energy_multiplier, sizeof(float));
    energy_formula_state[0x24] = 0x40u;
    energy_formula_state[0x25] = 0x04u;
    const float energy_core = gomore_primitives_energy_core(
        energy_formula_state, sizeof(energy_formula_state), 1.0f, 2.0f);
    assert(energy_core > 0.046f && energy_core < 0.047f);
    const float energy_scaled = gomore_primitives_energy_scaled(
        energy_formula_state, sizeof(energy_formula_state), 1.0f, 2.0f);
    assert(energy_scaled > 0.09f && energy_scaled < 0.10f);
    uint8_t resting_profile[10] = {0};
    const float resting_height = 175.0f;
    const float resting_weight = 75.0f;
    memcpy(&resting_profile[0], &resting_height, sizeof(resting_height));
    memcpy(&resting_profile[4], &resting_weight, sizeof(resting_weight));
    resting_profile[8] = 28u;
    resting_profile[9] = 1u;
    assert(gomore_primitives_daily_resting_kcal(
               resting_profile, sizeof(resting_profile)) ==
           bits_float(UINT32_C(0x44D7F539)));
    resting_profile[9] = 0u;
    assert(gomore_primitives_daily_resting_kcal(
               resting_profile, sizeof(resting_profile)) ==
           bits_float(UINT32_C(0x44C20443)));
    assert(gomore_primitives_daily_resting_kcal(NULL, 0u) == 0.0f);
    const float substrate_fraction =
        gomore_primitives_substrate_fat_fraction(
            1.5f, 2.0f, 1.0f, energy_exponential_fixture);
    assert(substrate_fraction > 0.5368f && substrate_fraction < 0.5370f);
    assert(gomore_primitives_substrate_fat_fraction(
               1.5f, 2.0f, 1.0f, NULL) == 0.0f);
    float zone_thresholds[7] = {0.0f};
    assert(gomore_primitives_energy_zone_thresholds(
        0.0f, 10.0f, 0.0f, energy_exponential_fixture,
        zone_thresholds));
    assert(zone_thresholds[0] == 0.0f && zone_thresholds[6] == 10.0f);
    uint8_t zone_state[0x4C] = {0};
    float zone_totals[5] = {0.0f};
    assert(gomore_primitives_energy_zone_accumulate(
        zone_state, sizeof(zone_state), 300, 1.25f,
        (zone_thresholds[1] + zone_thresholds[3]) * 0.5f,
        10.0f, 0.0f, 0.0f, energy_exponential_fixture, zone_totals));
    assert(zone_totals[2] == 1.25f && zone_totals[4] == 0.0f);
    assert(gomore_primitives_energy_zone_accumulate(
        zone_state, sizeof(zone_state), 300, 2.75f,
        (zone_thresholds[1] + zone_thresholds[3]) * 0.5f,
        10.0f, 0.0f, 0.0f, energy_exponential_fixture, zone_totals));
    assert(zone_totals[2] == 4.0f && zone_totals[4] == 4.0f);
    assert(zone_state[0x44] == 0u && zone_state[0x47] == 0u &&
           zone_state[0x48] == 0x58u && zone_state[0x49] == 0x02u);
    assert(gomore_primitives_energy_zone_accumulate(
        zone_state, sizeof(zone_state), 1, 0.5f, 0.0f,
        10.0f, 0.0f, 0.0f, energy_exponential_fixture, zone_totals));
    assert(zone_totals[0] == 0.5f && zone_state[0x48] == 0u &&
           zone_state[0x49] == 0u);
    assert(!gomore_primitives_energy_zone_accumulate(
        zone_state, 0x4Bu, 1, 0.5f, 0.0f,
        10.0f, 0.0f, 0.0f, energy_exponential_fixture, zone_totals));
    uint8_t projection_state[8] = {0};
    const float projection_multiplier = 75.0f;
    memcpy(&projection_state[4], &projection_multiplier,
           sizeof(projection_multiplier));
    float projection[4] = {0.0f};
    assert(gomore_primitives_energy_projection(
        projection_state, sizeof(projection_state),
        1000.0f, 800.0f, projection));
    assert(projection[0] > 5.9f && projection[0] < 6.1f &&
           projection[1] > 5.6f && projection[1] < 5.9f &&
           projection[2] > 3.8f && projection[2] < 4.0f &&
           projection[3] > 2.0f && projection[3] < 2.2f);
    assert(!gomore_primitives_energy_projection(
        projection_state, 7u, 1000.0f, 800.0f, projection));
    const float nonlinear = gomore_primitives_energy_nonlinear_scale(
        2.0f, 100.0f);
    assert(nonlinear > -1.75f && nonlinear < -1.73f);
    assert(gomore_primitives_energy_nonlinear_scale(
               -2.0f, 100.0f) > 1.68f);
    assert(gomore_primitives_energy_nonlinear_scale(
               -2.0f, -100.0f) == 1.0f);
    uint8_t mode_rate_state[0x1A] = {0};
    mode_rate_state[8] = 1u;
    float mode_rate = 0.0f;
    assert(gomore_primitives_energy_mode_rate(
        mode_rate_state, sizeof(mode_rate_state),
        projection_state, sizeof(projection_state), 30.0f, &mode_rate));
    assert(mode_rate > 0.085f && mode_rate < 0.087f &&
           mode_rate_state[0x18] == 1u && mode_rate_state[0x19] == 0u);
    assert(gomore_primitives_energy_mode_rate(
        mode_rate_state, sizeof(mode_rate_state),
        projection_state, sizeof(projection_state), 1.0f, &mode_rate));
    assert(mode_rate == 0.0f && mode_rate_state[0x18] == 0u &&
           mode_rate_state[0x19] == 1u);
    mode_rate_state[8] = 4u;
    assert(gomore_primitives_energy_mode_rate(
        mode_rate_state, sizeof(mode_rate_state),
        projection_state, sizeof(projection_state), 40.0f, &mode_rate));
    assert(mode_rate > 0.03f && mode_rate < 0.04f);
    assert(!gomore_primitives_energy_mode_rate(
        mode_rate_state, 0x19u, projection_state,
        sizeof(projection_state), 2.0f, &mode_rate));
    float interpolation_pair[2] = {0.0f};
    assert(gomore_primitives_energy_interpolate_pair(
        true, 0.5f, 2.0f, 3.0f,
        energy_exponential_fixture, interpolation_pair));
    assert(interpolation_pair[0] > 2.15f && interpolation_pair[0] < 2.17f &&
           interpolation_pair[1] > 2.31f && interpolation_pair[1] < 2.33f);
    assert(gomore_primitives_energy_interpolate_pair(
        false, 2.0f, 100.0f, 1.0f,
        energy_exponential_fixture, interpolation_pair));
    assert(interpolation_pair[0] == interpolation_pair[0] &&
           interpolation_pair[1] == interpolation_pair[1]);
    assert(!gomore_primitives_energy_interpolate_pair(
        false, 2.0f, 100.0f, 1.0f, NULL, interpolation_pair));
    uint8_t family_a_state[0x58] = {0};
    float family_a_output[4] = {0.0f};
    assert(gomore_primitives_energy_estimator_family_a(
        family_a_state, sizeof(family_a_state),
        projection_state, sizeof(projection_state),
        2.0f, 3.8f, 10.0f, 0.0f,
        energy_exponential_fixture,
        family_a_output));
    assert(family_a_state[0x4C] == 0u && family_a_output[0] >= 0.0f);
    family_a_state[0x4C] = 0x58u;
    family_a_state[0x4D] = 0x02u;
    assert(gomore_primitives_energy_estimator_family_a(
        family_a_state, sizeof(family_a_state),
        projection_state, sizeof(projection_state),
        2.0f, 4.75f, 10.0f, 0.0f,
        energy_exponential_fixture,
        family_a_output));
    assert(family_a_state[0x4C] == 0x59u &&
           family_a_state[0x4D] == 0x02u &&
           family_a_state[0x57] == 0x3Fu);
    memset(family_a_state, 0, sizeof(family_a_state));
    family_a_state[0x4C] = 1u;
    family_a_state[0x50] = 0x2Cu;
    family_a_state[0x51] = 0x01u;
    family_a_state[0x19] = 10u;
    assert(gomore_primitives_energy_estimator_family_a(
        family_a_state, sizeof(family_a_state),
        projection_state, sizeof(projection_state),
        2.0f, 3.0f, 10.0f, 0.0f,
        energy_exponential_fixture,
        family_a_output));
    assert(family_a_state[0x4C] == 0u && family_a_state[0x50] == 0u &&
           family_a_state[0x14] == 0u && family_a_state[0x17] == 0x3Fu);
    float family_b_output[4] = {0.0f};
    assert(gomore_primitives_energy_estimator_family_b(
        projection_state, sizeof(projection_state),
        2.0f, 2.0f, 10.0f, 0.0f,
        energy_exponential_fixture, energy_log_fixture, family_b_output));
    assert(family_b_output[0] >= 0.0f);
    assert(gomore_primitives_energy_estimator_family_b(
        projection_state, sizeof(projection_state),
        2.0f, 6.0f, 10.0f, 0.0f,
        energy_exponential_fixture, energy_log_fixture, family_b_output));
    assert(family_b_output[0] >= 0.0f);
    assert(gomore_primitives_energy_estimator_family_b(
        projection_state, sizeof(projection_state),
        2.0f, 9.5f, 10.0f, 0.0f,
        energy_exponential_fixture, energy_log_fixture, family_b_output));
    assert(family_b_output[0] >= 0.0f);
    assert(!gomore_primitives_energy_estimator_family_b(
        projection_state, sizeof(projection_state),
        2.0f, 2.0f, 10.0f, 0.0f,
        NULL, energy_log_fixture, family_b_output));
    const float dispatch_settings[2] = {2.0f, 3.0f};
    float dispatch_output[4] = {0.0f};
    memset(family_a_state, 0, sizeof(family_a_state));
    family_a_state[8] = 3u;
    assert(gomore_primitives_energy_dispatch(
        family_a_state, sizeof(family_a_state),
        projection_state, sizeof(projection_state), dispatch_settings,
        5.0f, 10.0f, 0.0f,
        energy_exponential_fixture, energy_log_fixture,
        energy_double_log_fixture,
        NULL, dispatch_output));
    assert(dispatch_output[0] > 0.13f && dispatch_output[0] < 0.14f);
    family_a_state[8] = 26u;
    assert(gomore_primitives_energy_dispatch(
        family_a_state, sizeof(family_a_state),
        projection_state, sizeof(projection_state), dispatch_settings,
        5.0f, 10.0f, 0.0f,
        energy_exponential_fixture, energy_log_fixture,
        energy_double_log_fixture,
        NULL, dispatch_output));
    assert(dispatch_output[0] > 0.04f);
    family_a_state[8] = 6u;
    assert(gomore_primitives_energy_dispatch(
        family_a_state, sizeof(family_a_state),
        projection_state, sizeof(projection_state), dispatch_settings,
        5.0f, 10.0f, 0.0f,
        energy_exponential_fixture, energy_log_fixture,
        energy_double_log_fixture,
        &gomore_primitives_energy_table_defaults,
        dispatch_output));
    assert(dispatch_output[0] == dispatch_output[0]);
    assert(gomore_primitives_energy_table_estimator(
        family_a_state, sizeof(family_a_state),
        projection_state, sizeof(projection_state),
        &gomore_primitives_energy_table_defaults,
        2.0f, 5.0f, 10.0f, 0.0f,
        energy_exponential_fixture, dispatch_output));
    assert(dispatch_output[0] == dispatch_output[0]);

    uint8_t energy_profile[10] = {0};
    const float profile_height = 175.0f;
    const float profile_weight = 75.0f;
    memcpy(&energy_profile[0], &profile_height, sizeof(profile_height));
    memcpy(&energy_profile[4], &profile_weight, sizeof(profile_weight));
    energy_profile[8] = 28u;
    energy_profile[9] = 1u;
    gomore_primitives_energy_update_state top_energy_state;
    memset(&top_energy_state, 0, sizeof(top_energy_state));
    top_energy_state.blend = 1.0f;
    gomore_primitives_energy_update_output update_output;
    memset(&update_output, UINT8_C(0xA5), sizeof(update_output));
    assert(sizeof(top_energy_state) == 0x5Cu &&
           sizeof(update_output) == 0x2Cu);
    assert(gomore_primitives_energy_update(
        &top_energy_state, 0, 65.0f,
        energy_profile, sizeof(energy_profile),
        180.0f, 60.0f, dispatch_settings,
        1.0f, -1.0f, 0, 0.0f,
        energy_exponential_fixture, energy_log_fixture,
        energy_double_log_fixture,
        &gomore_primitives_energy_table_defaults,
        &update_output) == GOMORE_PRIMITIVES_ENERGY_STATUS_INVALID);
    const uint8_t *cleared_update = (const uint8_t *)&update_output;
    for (size_t index = 0u; index < sizeof(update_output); ++index) {
        assert(cleared_update[index] == 0u);
    }

    assert(gomore_primitives_energy_update(
        &top_energy_state, 10, 65.0f,
        energy_profile, sizeof(energy_profile),
        180.0f, 60.0f, dispatch_settings,
        1.0f, -1.0f, 0, 0.0f,
        energy_exponential_fixture, energy_log_fixture,
        energy_double_log_fixture,
        &gomore_primitives_energy_table_defaults,
        &update_output) == GOMORE_PRIMITIVES_ENERGY_STATUS_OK);
    assert(update_output.total_kcal > 0.0f &&
           update_output.resting_kcal > 0.0f &&
           update_output.active_kcal == 0.0f &&
           top_energy_state.reference_value == 65.0f);

    top_energy_state.variant = 2;
    top_energy_state.mode = 4u;
    assert(gomore_primitives_energy_update(
        &top_energy_state, 2, 100.0f,
        energy_profile, sizeof(energy_profile),
        180.0f, 60.0f, dispatch_settings,
        3.0f, -1.0f, 0, 0.0f,
        energy_exponential_fixture, energy_log_fixture,
        energy_double_log_fixture,
        &gomore_primitives_energy_table_defaults,
        &update_output) == GOMORE_PRIMITIVES_ENERGY_STATUS_OK);
    assert(update_output.resting_kcal == 0.0f &&
           update_output.active_kcal > 1.1f &&
           update_output.active_kcal < 1.3f &&
           update_output.total_kcal == update_output.active_kcal);

    top_energy_state.variant = 1;
    top_energy_state.mode = 5u;
    assert(gomore_primitives_energy_update(
        &top_energy_state, 1, 100.0f,
        energy_profile, sizeof(energy_profile),
        180.0f, 60.0f, dispatch_settings,
        3.0f, 20.0f, 1, 0.0f,
        energy_exponential_fixture, energy_log_fixture,
        energy_double_log_fixture,
        &gomore_primitives_energy_table_defaults,
        &update_output) == GOMORE_PRIMITIVES_ENERGY_STATUS_OK);
    assert(update_output.total_kcal == update_output.total_kcal &&
           top_energy_state.auxiliary_history[9] == 20.0f);

    top_energy_state.variant = 0;
    top_energy_state.mode = 4u;
    assert(gomore_primitives_energy_update(
        &top_energy_state, 1, 100.0f,
        energy_profile, sizeof(energy_profile),
        180.0f, 60.0f, dispatch_settings,
        3.0f, -1.0f, 0, 100.0f,
        energy_exponential_fixture, energy_log_fixture,
        energy_double_log_fixture,
        &gomore_primitives_energy_table_defaults,
        &update_output) == GOMORE_PRIMITIVES_ENERGY_STATUS_OK);
    assert(update_output.total_kcal == update_output.total_kcal &&
           update_output.metabolic_equivalent ==
               update_output.metabolic_equivalent);

    top_energy_state.reference_value = 100.0f;
    top_energy_state.elapsed_since_reference = 0;
    assert(gomore_primitives_energy_update(
        &top_energy_state, 5, 0.0f,
        energy_profile, sizeof(energy_profile),
        180.0f, 60.0f, dispatch_settings,
        3.0f, -1.0f, 0, 100.0f,
        energy_exponential_fixture, energy_log_fixture,
        energy_double_log_fixture,
        &gomore_primitives_energy_table_defaults,
        &update_output) == GOMORE_PRIMITIVES_ENERGY_STATUS_OK);
    assert(top_energy_state.reference_value == 100.0f &&
           top_energy_state.elapsed_since_reference == 5);

    gomore_primitives_activity_accumulator_state activity_state;
    gomore_primitives_activity_accumulator_output activity_output;
    memset(&activity_state, 0, sizeof(activity_state));
    memset(&activity_output, UINT8_C(0xA5), sizeof(activity_output));
    update_output.total_kcal = 5.75f;
    update_output.active_kcal = 2.25f;
    assert(gomore_primitives_activity_accumulate(
        &activity_state, UINT32_C(86400), 0, 12.5f,
        &update_output, 3.6f, &activity_output));
    assert(activity_state.local_day == 1u &&
           activity_state.timezone_minutes == 0 &&
           activity_output.steps == 12u &&
           activity_output.total_kcal == 5 &&
           activity_output.active_kcal == 2 &&
           activity_output.distance > 0.00099f &&
           activity_output.distance < 0.00101f);
    for (size_t index = 0u; index < sizeof(activity_output.reserved);
         ++index) {
        assert(activity_output.reserved[index] == 0u);
    }
    assert(gomore_primitives_activity_accumulate(
        &activity_state, UINT32_C(86500), 0, -1.0f,
        &update_output, -1.0f, &activity_output));
    assert(activity_output.steps == 12u &&
           activity_output.total_kcal == 11 &&
           activity_output.active_kcal == 4);
    update_output.total_kcal = 1.0f;
    update_output.active_kcal = 0.5f;
    assert(gomore_primitives_activity_accumulate(
        &activity_state, UINT32_C(172800), 0, 1.0f,
        &update_output, 0.0f, &activity_output));
    assert(activity_state.local_day == 2u &&
           activity_output.steps == 1u &&
           activity_output.total_kcal == 1 &&
           activity_output.active_kcal == 0 &&
           activity_output.distance == 0.0f);
    assert(!gomore_primitives_activity_accumulate(
        NULL, 0u, 0, 0.0f, &update_output, 0.0f, &activity_output));

    const gomore_primitives_profile_input default_profile_input = {
        .age_years = 28.0f,
        .binary_sex = 1.0f,
        .height_centimeters = 175.0f,
        .weight_kilograms = 75.0f,
        .parameter_4 = -1.0f,
        .parameter_5 = -1.0f,
        .parameter_6 = -1.0f,
    };
    float profile_cache[2] = {-1.0f, -1.0f};
    gomore_primitives_profile_output converted_profile;
    assert(gomore_primitives_profile_convert(
        &default_profile_input, profile_cache, &converted_profile) == 0);
    assert(converted_profile.age_years == 28u &&
           converted_profile.binary_sex == 1u &&
           converted_profile.height_centimeters == 175.0f &&
           converted_profile.weight_kilograms == 75.0f &&
           converted_profile.parameter_4 > 188.3f &&
           converted_profile.parameter_4 < 188.5f &&
           converted_profile.parameter_5_raw == -1.0f &&
           converted_profile.parameter_5_normalized == 60.0f &&
           converted_profile.cached_parameters[0] == 35.0f &&
           converted_profile.cached_parameters[1] == 35.0f &&
           profile_cache[0] == 35.0f && profile_cache[1] == -1.0f);

    gomore_primitives_profile_input invalid_profile_input =
        default_profile_input;
    invalid_profile_input.age_years = 200.0f;
    assert(gomore_primitives_profile_convert(
        &invalid_profile_input, profile_cache, &converted_profile) == -101);
    assert(converted_profile.age_years == 30u);
    invalid_profile_input.binary_sex = 2.0f;
    invalid_profile_input.height_centimeters = 300.0f;
    invalid_profile_input.weight_kilograms = 200.0f;
    invalid_profile_input.parameter_4 = 1000.0f;
    invalid_profile_input.parameter_5 = 1000.0f;
    invalid_profile_input.parameter_6 = 0.0f;
    profile_cache[0] = -1.0f;
    profile_cache[1] = 42.0f;
    assert(gomore_primitives_profile_convert(
        &invalid_profile_input, profile_cache, &converted_profile) == -107);
    assert(converted_profile.binary_sex == 1u &&
           converted_profile.height_centimeters == 170.0f &&
           converted_profile.weight_kilograms == 60.0f &&
           converted_profile.parameter_5_normalized == 60.0f &&
           converted_profile.cached_parameters[0] == 35.0f &&
           converted_profile.cached_parameters[1] == 42.0f);
    assert(gomore_primitives_profile_convert(
        NULL, profile_cache, &converted_profile) == -1);

    uint8_t sleep_stages[2880] = {0};
    sleep_stages[0] = 0u;
    sleep_stages[1] = 1u;
    sleep_stages[2] = 0u;
    sleep_stages[3] = 0u;
    sleep_stages[4] = 9u;
    sleep_stages[5] = 0u;
    float interval_statistics[7] = {0.0f};
    assert(gomore_primitives_sleep_interval_statistics(
        sleep_stages, sizeof(sleep_stages), 0u, 180u,
        false, interval_statistics));
    assert(interval_statistics[0] == 3.0f &&
           interval_statistics[1] == 0.5f &&
           interval_statistics[2] == 1.0f &&
           interval_statistics[3] == 1.0f &&
           interval_statistics[4] == 1.5f &&
           interval_statistics[5] == 2.0f &&
           interval_statistics[6] == (1.0f / 3.0f));
    assert(gomore_primitives_sleep_interval_statistics(
        sleep_stages, sizeof(sleep_stages), 0u, 0u,
        false, interval_statistics));
    for (size_t index = 0u; index < 7u; ++index) {
        assert(interval_statistics[index] == -1.0f);
    }
    assert(!gomore_primitives_sleep_interval_statistics(
        sleep_stages, 2u, 0u, 180u, false, interval_statistics));

    sleep_stages[0] = 0u;
    sleep_stages[1] = 1u;
    sleep_stages[2] = 2u;
    sleep_stages[3] = 3u;
    float sleep_statistics[12] = {0.0f};
    assert(gomore_primitives_sleep_stage_statistics(
        sleep_stages, sizeof(sleep_stages), 0u, 120u,
        false, sleep_statistics));
    assert(sleep_statistics[0] == 0.5f &&
           sleep_statistics[1] == 0.25f &&
           sleep_statistics[2] == 0.25f &&
           sleep_statistics[3] == 0.25f &&
           sleep_statistics[4] == 0.5f &&
           sleep_statistics[5] == 1.0f &&
           sleep_statistics[6] == 1.0f &&
           sleep_statistics[7] == 0.5f &&
           sleep_statistics[8] == 0.5f &&
           sleep_statistics[9] == 0.5f &&
           sleep_statistics[10] == 0.5f &&
           sleep_statistics[11] == 0.5f);
    assert(gomore_primitives_sleep_stage_statistics(
        sleep_stages, sizeof(sleep_stages), 0u, 0u,
        false, sleep_statistics));
    for (size_t index = 0u; index < 12u; ++index) {
        assert(sleep_statistics[index] == 0.0f);
    }
    assert(!gomore_primitives_sleep_stage_statistics(
        sleep_stages, 2u, 0u, 120u, false, sleep_statistics));

    gomore_primitives_sleep_statistics scored_statistics;
    memset(&scored_statistics, 0, sizeof(scored_statistics));
    scored_statistics.rem_fraction = 0.5f;
    scored_statistics.deep_fraction = 0.0f;
    const float score_minutes[] = {
        269.0f, 270.0f, 300.0f, 360.0f,
        480.0f, 510.0f, 540.0f, 541.0f,
    };
    const float score_baselines[] = {
        59.0f, 74.0f, 89.0f, 95.0f,
        89.0f, 74.0f, 0.0f, 59.0f,
    };
    float sleep_score = -1.0f;
    for (size_t index = 0u;
            index < sizeof(score_minutes) / sizeof(score_minutes[0]);
            ++index) {
        scored_statistics.non_awake_minutes = score_minutes[index];
        scored_statistics.awake_after_onset_minutes = 0.0f;
        assert(gomore_primitives_sleep_score(
            &scored_statistics, sleep_tanh_zero_fixture,
            sleep_power_fixture, &sleep_score));
        assert(sleep_score == score_baselines[index] / 2.0f +
                              0.1f + 0.1f);
    }
    scored_statistics.non_awake_minutes = 360.0f;
    scored_statistics.awake_after_onset_minutes = 36.0f;
    scored_statistics.rem_fraction = 0.25f;
    scored_statistics.deep_fraction = 0.20f;
    assert(gomore_primitives_sleep_score(
        &scored_statistics, sleep_tanh_zero_fixture,
        sleep_power_fixture, &sleep_score));
    assert(sleep_score == 95.0f / 2.0f + 0.3f + 0.4f);
    scored_statistics.awake_after_onset_minutes = 180.0f;
    assert(gomore_primitives_sleep_score(
        &scored_statistics, sleep_tanh_zero_fixture,
        sleep_power_fixture, &sleep_score));
    assert(sleep_score == 95.0f / 4.0f + 0.3f + 0.4f);
    assert(!gomore_primitives_sleep_score(
        NULL, sleep_tanh_zero_fixture, sleep_power_fixture, &sleep_score));

    const int16_t peak_positions[] = {25, 50, 100, 125};
    float peak_rates[6] = {0.0f};
    assert(gomore_primitives_sleep_peak_rate_interpolate(
        peak_positions,
        sizeof(peak_positions) / sizeof(peak_positions[0]),
        25, 0, peak_rates,
        sizeof(peak_rates) / sizeof(peak_rates[0])));
    assert(peak_rates[0] == 60.0f && peak_rates[1] == 60.0f &&
           peak_rates[2] == 30.0f && peak_rates[3] == 45.0f &&
           peak_rates[4] == 60.0f && peak_rates[5] == 60.0f);
    const int16_t invalid_peak_positions[] = {
        (int16_t)UINT16_C(0x8019), 50, 100,
    };
    assert(gomore_primitives_sleep_peak_rate_interpolate(
        invalid_peak_positions,
        sizeof(invalid_peak_positions) / sizeof(invalid_peak_positions[0]),
        25, 0, peak_rates,
        sizeof(peak_rates) / sizeof(peak_rates[0])));
    assert(peak_rates[0] == 30.0f && peak_rates[1] == 30.0f &&
           peak_rates[2] == 60.0f && peak_rates[3] == 60.0f &&
           peak_rates[4] == 60.0f && peak_rates[5] == 60.0f);
    assert(!gomore_primitives_sleep_peak_rate_interpolate(
        peak_positions,
        sizeof(peak_positions) / sizeof(peak_positions[0]),
        0, 0, peak_rates,
        sizeof(peak_rates) / sizeof(peak_rates[0])));

    int16_t window_peaks[] = {25, 50, 100, 125};
    float peak_window[90];
    for (size_t index = 0u; index < 90u; ++index) {
        peak_window[index] = (float)index;
    }
    uint16_t peak_update_counter = 0u;
    assert(gomore_primitives_sleep_peak_window_update(
        window_peaks,
        sizeof(window_peaks) / sizeof(window_peaks[0]),
        sizeof(window_peaks) / sizeof(window_peaks[0]),
        0u, &peak_update_counter, peak_window, 90u));
    assert(((uint16_t)window_peaks[1] & UINT16_C(0x8000)) != 0u &&
           peak_update_counter == 1u);
    for (size_t index = 60u; index < 90u; ++index) {
        assert(peak_window[index] == 0.0f);
    }
    for (size_t index = 0u; index < 90u; ++index) {
        peak_window[index] = (float)index;
    }
    peak_update_counter = 3u;
    assert(gomore_primitives_sleep_peak_window_update(
        window_peaks,
        sizeof(window_peaks) / sizeof(window_peaks[0]),
        sizeof(window_peaks) / sizeof(window_peaks[0]),
        100u, &peak_update_counter, peak_window, 90u));
    for (size_t index = 0u; index < 60u; ++index) {
        assert(peak_window[index] == (float)(index + 30u));
    }
    for (size_t index = 0u; index < 30u; ++index) {
        assert(peak_window[index + 60u] == (float)index);
    }
    assert(peak_update_counter == 4u);
    assert(!gomore_primitives_sleep_peak_window_update(
        window_peaks, 2u, 4u, 0u, &peak_update_counter,
        peak_window, 90u));

    int16_t tail_peaks[] = {
        700, 749, 750, (int16_t)UINT16_C(0x8320), 900,
    };
    size_t tail_peak_count =
        sizeof(tail_peaks) / sizeof(tail_peaks[0]);
    assert(gomore_primitives_sleep_peak_tail_rebase(
        tail_peaks,
        sizeof(tail_peaks) / sizeof(tail_peaks[0]),
        &tail_peak_count));
    assert(tail_peak_count == 3u && tail_peaks[0] == 0 &&
           (uint16_t)tail_peaks[1] == UINT16_C(0x8032) &&
           tail_peaks[2] == 150);
    tail_peak_count = 6u;
    assert(!gomore_primitives_sleep_peak_tail_rebase(
        tail_peaks,
        sizeof(tail_peaks) / sizeof(tail_peaks[0]),
        &tail_peak_count));

    const float valley_values[] = {
        3.0f, 2.0f, 2.0f, 4.0f, 1.0f, 5.0f,
    };
    uint8_t valley_candidates[12];
    memset(valley_candidates, UINT8_C(0xA5), sizeof(valley_candidates));
    size_t valley_count = 0u;
    assert(gomore_primitives_sleep_valley_candidates(
        valley_values,
        sizeof(valley_values) / sizeof(valley_values[0]),
        valley_candidates, &valley_count));
    assert(valley_count == 2u && valley_candidates[0] == 2u &&
           valley_candidates[1] == 4u && valley_candidates[2] == 0u &&
           valley_candidates[11] == 0u);
    valley_count = 13u;
    assert(!gomore_primitives_sleep_valley_candidates(
        valley_values,
        sizeof(valley_values) / sizeof(valley_values[0]),
        valley_candidates, &valley_count));

    gomore_primitives_sleep_optical_history optical_history;
    memset(&optical_history, 0, sizeof(optical_history));
    for (size_t index = 0u; index < 75u; ++index) {
        optical_history.window[index] = (float)index;
    }
    optical_history.positions[0] = 10u;
    optical_history.positions[1] = 24u;
    optical_history.positions[2] = 25u;
    optical_history.positions[3] = 50u;
    optical_history.position_count = 4u;
    assert(gomore_primitives_sleep_optical_history_advance(
        &optical_history, 1u, closure_filter_initialize));
    assert(optical_history.window[0] == 25.0f &&
           optical_history.window[49] == 74.0f &&
           optical_history.window[50] == 50.0f &&
           optical_history.position_count == 2u &&
           optical_history.positions[0] == 0u &&
           optical_history.positions[1] == 25u);
    active_closure_trace.filter_calls = 0u;
    assert(gomore_primitives_sleep_optical_history_advance(
        &optical_history, 3u, closure_filter_initialize));
    assert(active_closure_trace.filter_calls == 1u &&
           optical_history.window[0] == 0.0f &&
           optical_history.window[74] == 0.0f &&
           optical_history.position_count == 0u);

    memset(&optical_history, 0, sizeof(optical_history));
    for (size_t index = 0u; index < 50u; ++index) {
        optical_history.window[index] = 1.0f;
    }
    optical_history.window[5] = 0.0f;
    optical_history.window[15] = 0.0f;
    optical_history.window[25] = 0.0f;
    optical_history.positions[0] = 6u;
    optical_history.position_count = 1u;
    const gomore_primitives_sleep_optical_input invalid_optical_input = {
        .samples = NULL,
        .invalid = true,
    };
    uint8_t optical_record[17];
    memset(optical_record, UINT8_C(0xA5), sizeof(optical_record));
    assert(gomore_primitives_sleep_optical_peak_update(
        &optical_history, 0u, &invalid_optical_input, optical_record,
        closure_filter_initialize, NULL, NULL));
    assert(optical_record[0] == 16u && optical_record[1] == 0u &&
           optical_record[16] == UINT8_C(0x81) &&
           optical_history.position_count == 1u &&
           optical_history.positions[0] == 16u &&
           optical_history.positions[1] == 16u);

    const float valid_optical_samples[25] = {0.0f};
    const gomore_primitives_sleep_optical_input valid_optical_input = {
        .samples = valid_optical_samples,
        .invalid = false,
    };
    active_closure_trace.resample_calls = 0u;
    active_closure_trace.apply_filter_calls = 0u;
    assert(gomore_primitives_sleep_optical_peak_update(
        &optical_history, 3u, &valid_optical_input, optical_record,
        closure_filter_initialize, closure_resample,
        closure_apply_filter));
    assert(active_closure_trace.resample_calls == 1u &&
           active_closure_trace.apply_filter_calls == 1u &&
           optical_record[16] == UINT8_C(0x80) &&
           optical_history.position_count == 0u);
    active_closure_trace.resample_calls = 0u;
    active_closure_trace.apply_filter_calls = 0u;

    uint8_t explicit_state[0x1C];
    memset(explicit_state, 0, sizeof(explicit_state));
    explicit_state[0x18] = 0x78u;
    explicit_state[0x19] = 0x56u;
    explicit_state[0x1A] = 0x34u;
    explicit_state[0x1B] = 0x12u;
    uint32_t explicit_word = 0u;
    assert(gomore_primitives_state_word_24(
        explicit_state, sizeof(explicit_state), &explicit_word));
    assert(explicit_word == UINT32_C(0x12345678));
    float split_root[2] = {-1.0f, -1.0f};
    assert(gomore_primitives_split_signed_root(
        -4.0f, split_root, closure_root_power));
    assert(split_root[0] == 0.0f && split_root[1] == 8.0f);
    assert(gomore_primitives_clamped_rational(100.0f, 0.001f) == 220.0f);
    uint8_t table11[110];
    for (size_t index = 0u; index < sizeof(table11); ++index) {
        table11[index] = (uint8_t)index;
    }
    uint8_t table_record[11];
    assert(gomore_primitives_table_record11(
        table11, sizeof(table11), 3, table_record));
    assert(table_record[0] == 33u && table_record[10] == 43u);
    uint8_t random_state[0x14];
    memset(random_state, 0, sizeof(random_state));
    random_state[0x10] = 4u;
    uint8_t status_for_random[12];
    memset(status_for_random, 0, sizeof(status_for_random));
    status_for_random[0] = 0x44u;
    assert(gomore_primitives_status_or_random(
               random_state, sizeof(random_state), status_for_random,
               sizeof(status_for_random), closure_prepare,
               closure_random) == 100);
    assert(random_state[0] == 0x44u);
    uint8_t identifier_classes[256];
    memset(identifier_classes, 0, sizeof(identifier_classes));
    identifier_classes[(uint8_t)' '] = UINT8_C(0x20);
    uint8_t identifier_state[0x14];
    uint8_t identifier_status[12];
    memset(identifier_state, 0, sizeof(identifier_state));
    memset(identifier_status, 0, sizeof(identifier_status));
    assert(gomore_primitives_validate_identifier_status(
        (const uint8_t *)"abc", identifier_classes,
        identifier_state, sizeof(identifier_state),
        identifier_status, sizeof(identifier_status),
        closure_prepare, closure_random) == -1004);
    assert(identifier_state[0x10] == 1u &&
           identifier_state[4] == UINT8_C(0x14) &&
           identifier_state[5] == UINT8_C(0xFC) &&
           identifier_status[4] == UINT8_C(0x14) &&
           identifier_status[5] == UINT8_C(0xFC));
    memset(identifier_state, UINT8_C(0xA5), sizeof(identifier_state));
    identifier_state[0x10] = 0u;
    memset(identifier_status, 0, sizeof(identifier_status));
    assert(gomore_primitives_validate_identifier_status(
        NULL, identifier_classes,
        identifier_state, sizeof(identifier_state),
        identifier_status, sizeof(identifier_status),
        closure_prepare, closure_random) == 0);
    assert(identifier_state[0x10] == 1u && identifier_state[8] == 0xA5u);
    for (uint8_t digit = (uint8_t)'0'; digit <= (uint8_t)'9'; ++digit) {
        identifier_classes[digit] = UINT8_C(0x20);
    }
    memset(identifier_state, 0, sizeof(identifier_state));
    memset(identifier_status, 0, sizeof(identifier_status));
    assert(gomore_primitives_validate_identifier_status(
        (const uint8_t *)"1839052049009318", identifier_classes,
        identifier_state, sizeof(identifier_state),
        identifier_status, sizeof(identifier_status),
        closure_prepare, closure_random) == -1020);

    uint8_t mode_state[0x50];
    memset(mode_state, UINT8_C(0xA5), sizeof(mode_state));
    const float mode1_parameters[2] = {0.25f, 0.5f};
    assert(gomore_primitives_mode_state_configure(
        mode_state, sizeof(mode_state), 1u, 3u, mode1_parameters,
        closure_mode_lt2_initialize, NULL));
    assert(mode_state[0] == 3u && mode_state[0x30] == 0u &&
           mode_state[0x4F] == 0u &&
           active_closure_trace.mode_lt2_calls == 1u);

    gomore_primitives_iir_coefficients iir_coefficients;
    memset(&iir_coefficients, UINT8_C(0xA5), sizeof(iir_coefficients));
    assert(gomore_primitives_iir_low_high_coefficients(
        &iir_coefficients, 0u, 2u,
        bits_float(UINT32_C(0x3E23D70A)),
        iir_cosine_fixture, iir_sine_fixture, iir_power_fixture));
    assert(iir_coefficients.order == UINT32_C(0xA5A5A5A5) &&
           float_bits(iir_coefficients.reserved) == 0u &&
           float_bits(iir_coefficients.feedback[0]) == UINT32_C(0x3F800000) &&
           float_bits(iir_coefficients.feedback[1]) == UINT32_C(0xBFA7551D) &&
           float_matches_bits_within_ulps(
               iir_coefficients.feedback[2], UINT32_C(0x3EFBCECE), 1u) &&
           float_bits(iir_coefficients.feedback[3]) == UINT32_C(0xA5A5A5A5) &&
           float_bits(iir_coefficients.feedforward[0]) == UINT32_C(0x3D3CF4B5) &&
           float_bits(iir_coefficients.feedforward[1]) == UINT32_C(0x3DBCF4B5) &&
           float_bits(iir_coefficients.feedforward[2]) == UINT32_C(0x3D3CF4B5) &&
           float_bits(iir_coefficients.feedforward[3]) == UINT32_C(0xA5A5A5A5));

    memset(&iir_coefficients, UINT8_C(0xA5), sizeof(iir_coefficients));
    assert(gomore_primitives_iir_low_high_coefficients(
        &iir_coefficients, 1u, 4u,
        bits_float(UINT32_C(0x3ECCCCCD)),
        iir_cosine_fixture, iir_sine_fixture, iir_power_fixture));
    const uint32_t iir_high_feedback[5] = {
        UINT32_C(0x3F800000), UINT32_C(0xBF483763),
        UINT32_C(0x3F2E1313), UINT32_C(0xBE3B0F57),
        UINT32_C(0x3CF6BBE0),
    };
    const uint32_t iir_high_feedforward[5] = {
        UINT32_C(0x3E2B3108), UINT32_C(0xBF2B3108),
        UINT32_C(0x3F8064C6), UINT32_C(0xBF2B3108),
        UINT32_C(0x3E2B3108),
    };
    for (size_t index = 0u; index < 5u; ++index) {
        assert(float_matches_bits_within_ulps(
                   iir_coefficients.feedback[index],
                   iir_high_feedback[index], 3u) &&
               float_matches_bits_within_ulps(
                   iir_coefficients.feedforward[index],
                   iir_high_feedforward[index], 3u));
    }
    const gomore_primitives_iir_coefficients iir_before = iir_coefficients;
    assert(!gomore_primitives_iir_low_high_coefficients(
        &iir_coefficients, 2u, 2u, 0.16f,
        iir_cosine_fixture, iir_sine_fixture, iir_power_fixture));
    assert(!gomore_primitives_iir_low_high_coefficients(
        &iir_coefficients, 0u, 0u, 0.16f,
        iir_cosine_fixture, iir_sine_fixture, iir_power_fixture));
    assert(!gomore_primitives_iir_low_high_coefficients(
        &iir_coefficients, 0u, 2u, 0.0f,
        iir_cosine_fixture, iir_sine_fixture, iir_power_fixture));
    assert(!gomore_primitives_iir_low_high_coefficients(
        &iir_coefficients, 0u, 2u, 0.16f,
        NULL, iir_sine_fixture, iir_power_fixture));
    assert(memcmp(&iir_coefficients, &iir_before,
                  sizeof(iir_coefficients)) == 0);

    memset(&iir_coefficients, UINT8_C(0xA5), sizeof(iir_coefficients));
    const float sleep_peak_cutoffs[2] = {
        bits_float(UINT32_C(0x3C83126F)),
        bits_float(UINT32_C(0x3E23D70A)),
    };
    assert(gomore_primitives_iir_bandpass_coefficients(
        &iir_coefficients, 2u, sleep_peak_cutoffs,
        iir_cosine_fixture, iir_sine_fixture, iir_tangent_fixture));
    const uint32_t bandpass_feedback[5] = {
        UINT32_C(0x3F800000), UINT32_C(0xC0552C25),
        UINT32_C(0x408676E0), UINT32_C(0xC01980F5),
        UINT32_C(0x3F071CB3),
    };
    const uint32_t bandpass_feedforward[5] = {
        UINT32_C(0x3D1D6014), 0u, UINT32_C(0xBD9D6014),
        0u, UINT32_C(0x3D1D6014),
    };
    assert(iir_coefficients.order == UINT32_C(0xA5A5A5A5) &&
           float_bits(iir_coefficients.reserved) == 0u);
    for (size_t index = 0u; index < 5u; ++index) {
        assert(float_matches_bits_within_ulps(
                   iir_coefficients.feedback[index],
                   bandpass_feedback[index], 4u) &&
               float_matches_bits_within_ulps(
                   iir_coefficients.feedforward[index],
                   bandpass_feedforward[index], 4u));
    }
    const gomore_primitives_iir_coefficients bandpass_before =
        iir_coefficients;
    const float reversed_cutoffs[2] = {0.3f, 0.1f};
    assert(!gomore_primitives_iir_bandpass_coefficients(
        &iir_coefficients, 2u, reversed_cutoffs,
        iir_cosine_fixture, iir_sine_fixture, iir_tangent_fixture));
    assert(!gomore_primitives_iir_bandpass_coefficients(
        &iir_coefficients, 3u, sleep_peak_cutoffs,
        iir_cosine_fixture, iir_sine_fixture, iir_tangent_fixture));
    assert(!gomore_primitives_iir_bandpass_coefficients(
        &iir_coefficients, 2u, sleep_peak_cutoffs,
        iir_cosine_fixture, iir_sine_fixture, NULL));
    assert(memcmp(&iir_coefficients, &bandpass_before,
                  sizeof(iir_coefficients)) == 0);

    uint8_t large_filter_state[0x6C8];
    memset(large_filter_state, UINT8_C(0xA5), sizeof(large_filter_state));
    assert(gomore_primitives_large_filter_state_initialize(
        large_filter_state, sizeof(large_filter_state),
        closure_mode2_initialize));
    assert(large_filter_state[0] == 4u && large_filter_state[4] == 0x66u &&
           large_filter_state[0x30] == 0u &&
           large_filter_state[0x6C0] == 0x00u &&
           large_filter_state[0x6C3] == 0xBFu &&
           active_closure_trace.mode2_calls == 1u);
    uint8_t engine_state[0x3894];
    memset(engine_state, UINT8_C(0xA5), sizeof(engine_state));
    assert(gomore_primitives_engine_state_initialize(
        engine_state, sizeof(engine_state), UINT32_C(0x12345678),
        closure_large_initialize));
    assert(engine_state[0] == 0x77u && engine_state[0x3890] == 0x78u &&
           engine_state[0x3893] == 0x12u &&
           active_closure_trace.large_init_calls == 1u);
    const float linear_source[2] = {0.0f, 10.0f};
    float linear_destination[4] = {-1.0f, -1.0f, -1.0f, -1.0f};
    gomore_primitives_linear_resample(
        linear_source, 2, 4, 2, linear_destination);
    assert(linear_destination[0] == 0.0f &&
           linear_destination[1] == 5.0f &&
           linear_destination[2] == 10.0f &&
           linear_destination[3] == 10.0f);
    const float copy_source[3] = {1.0f, 2.0f, 3.0f};
    float copy_destination[3] = {0.0f, 0.0f, 0.0f};
    gomore_primitives_linear_resample(
        copy_source, 3, 3, 3, copy_destination);
    assert(memcmp(copy_source, copy_destination,
                  sizeof(copy_source)) == 0);
    float resample_source[25];
    float resample_destination[25];
    memset(resample_source, 0, sizeof(resample_source));
    memset(resample_destination, 0, sizeof(resample_destination));
    resample_source[0] = 2.0f;
    assert(gomore_primitives_resample25_and_filter(
               mode_state, resample_source, 25, 50, resample_destination,
               closure_resample, closure_apply_filter) == 0);
    assert(resample_destination[0] == 3.0f &&
           resample_destination[24] == 27.0f);
    gomore_primitives_resample25_and_filter_tail(
        mode_state, resample_source, 25, 50, resample_destination,
        closure_resample, closure_apply_filter);
    assert(active_closure_trace.resample_calls == 2u &&
           active_closure_trace.apply_filter_calls == 2u);
    uint8_t prepared_filter[0x17C];
    memset(prepared_filter, UINT8_C(0xA5), sizeof(prepared_filter));
    assert(gomore_primitives_prepare_filter_input(
        prepared_filter, sizeof(prepared_filter), NULL, true, 50,
        NULL, NULL));
    assert(prepared_filter[0x117] == UINT8_C(0xA5) &&
           prepared_filter[0x118] == 0u && prepared_filter[0x17B] == 0u);
    uint8_t commit_context[0x13C];
    uint8_t commit_destination[10];
    uint8_t valid_time_record[8] = {
        20u, 0u, 100u, 0u, 0u, 0u, 10u, 20u};
    memset(commit_context, 0, sizeof(commit_context));
    memset(commit_destination, 0, sizeof(commit_destination));
    assert(gomore_primitives_commit_valid_time_record(
        commit_context, sizeof(commit_context), commit_destination,
        sizeof(commit_destination), valid_time_record,
        sizeof(valid_time_record)));
    assert(commit_destination[2] == 20u && commit_destination[9] == 20u &&
           commit_context[0x130] == 20u &&
           commit_context[0x137] == 20u);
    float signed_power[2] = {-8.0f, 5.0f};
    assert(gomore_primitives_signed_power_third(
        signed_power, closure_third_power));
    assert(signed_power[0] == -9.0f && signed_power[1] == 0.0f);
    const uint8_t trim_reference[2] = {2u, 4u};
    uint8_t trim_values[5] = {1u, 3u, 5u, 6u, 7u};
    size_t trim_count = 5u;
    assert(gomore_primitives_trim_below_reference_tail(
        trim_reference, 2u, trim_values, 5u, &trim_count));
    assert(trim_count == 3u && trim_values[0] == 5u &&
           trim_values[2] == 7u);
    uint8_t selector_record[0x3E];
    memset(selector_record, 0, sizeof(selector_record));
    const float selector_positive = 1.0f;
    memcpy(&selector_record[0x20], &selector_positive, sizeof(float));
    selector_record[0x39] = 1u;
    selector = -1;
    assert(gomore_primitives_selector_transition(
        selector_record, sizeof(selector_record), &selector));
    assert(selector == 1);
    selector_record[0x28] = 0u;
    selector_record[0x29] = 0u;
    selector_record[0x2A] = 0x80u;
    selector_record[0x2B] = 0xBFu;
    assert(gomore_primitives_selector_transition(
        selector_record, sizeof(selector_record), &selector));
    assert(selector == -1);
    uint8_t packed_gap[0x2D5];
    memset(packed_gap, 0, sizeof(packed_gap));
    packed_gap[0x2D4] = 3u;
    assert(gomore_primitives_fill_packed_time_gap(
        packed_gap, sizeof(packed_gap), 90u));
    assert((packed_gap[0] & 0x3Cu) == 0x3Cu);
    assert(gomore_primitives_centered_ratio(5, 2, 1) == 1.0f);

    uint8_t iir_state[0x44];
    memset(iir_state, 0, sizeof(iir_state));
    const float iir_gain = 2.0f;
    memcpy(&iir_state[0x1C], &iir_gain, sizeof(iir_gain));
    float iir_values[2] = {1.0f, 3.0f};
    assert(gomore_primitives_iir_filter_apply(
        iir_state, sizeof(iir_state), iir_values, 2u));
    assert(iir_values[0] == 2.0f && iir_values[1] == 6.0f &&
           iir_state[4] == 1u);
    int32_t integer_iir_inputs[4] = {0, 0, 0, 0};
    int32_t integer_iir_outputs[4] = {0, 0, 0, 0};
    assert(gomore_primitives_integer_iir4_update(
               1000, integer_iir_inputs, integer_iir_outputs, 1) == 434);
    assert(integer_iir_inputs[0] == 1000 &&
           integer_iir_outputs[0] == 434);
    assert(gomore_primitives_integer_iir4_update(
               1000, integer_iir_inputs, integer_iir_outputs, 1) == 2049);
    memset(integer_iir_inputs, 0, sizeof(integer_iir_inputs));
    memset(integer_iir_outputs, 0, sizeof(integer_iir_outputs));
    assert(gomore_primitives_integer_iir4_update(
               1000, integer_iir_inputs, integer_iir_outputs, 0) == 9131);
    const float mean5_values[5] = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f};
    const float mean5_comparisons[5] = {0.0f, 2.0f, 3.0f, 4.0f, 5.0f};
    float thresholded_mean = 0.0f;
    assert(gomore_primitives_thresholded_mean5(
               3.0f, mean5_values, mean5_comparisons,
               &thresholded_mean) == 3 &&
           thresholded_mean == 4.0f);
    const float magnitude_values[10] = {
        0.5f, 1.0f, 3.0f, 0.0f, 0.0f,
        0.0f, 0.0f, 0.0f, 0.0f, 0.0f};
    const float magnitude_score = gomore_primitives_magnitude_score10(
        1.0f, magnitude_values);
    assert(magnitude_score > 190.0f && magnitude_score < 191.0f);
    const int16_t circular_predicate_values[5] = {5, 20, 25, 30, 40};
    assert(gomore_primitives_circular_count_predicate(
               circular_predicate_values, 5u, 1, 3, 10, 35,
            0x3Eu, 1) == 1);
    const int8_t run_values[3] = {1, 1, 2};
    uint8_t encoded_runs[3] = {0u, 0u, 0u};
    size_t encoded_run_count = 0u;
    assert(gomore_primitives_run_length_encode_2bit(
        run_values, 3u, encoded_runs, 3u, &encoded_run_count));
    assert(encoded_run_count == 2u && encoded_runs[0] == 9u &&
           encoded_runs[1] == 6u);
    uint8_t propagation_state[1001];
    memset(propagation_state, 0, sizeof(propagation_state));
    propagation_state[0x2D0] = 90u;
    propagation_state[1000] = 1u;
    assert(gomore_primitives_packed_2bit_set(
        propagation_state, 0x2D0u, 1u, 2u));
    uint8_t propagated = 0u;
    assert(gomore_primitives_propagate_packed_status(
        propagation_state, sizeof(propagation_state), &propagated));
    assert(propagated == 2u && propagation_state[1000] == 0u);
    uint8_t filter_bank[0x140];
    memset(filter_bank, UINT8_C(0xA5), sizeof(filter_bank));
    assert(gomore_primitives_filter_bank_initialize(
        filter_bank, sizeof(filter_bank), closure_mode_lt2_initialize,
        closure_mode2_initialize));
    assert(filter_bank[0] == 4u && filter_bank[0x50] == 2u &&
           filter_bank[0xA0] == 2u && filter_bank[0xF0] == 2u);
    const int8_t target_values[7] = {1, 2, 2, 0, 2, 2, 2};
    uint16_t target_runs[4][2];
    memset(target_runs, 0, sizeof(target_runs));
    size_t target_run_count = 0u;
    size_t target_match_count = 0u;
    assert(gomore_primitives_target_runs(
        2, target_values, 7u, target_runs, 4u,
        &target_run_count, &target_match_count));
    assert(target_run_count == 2u && target_match_count == 5u &&
           target_runs[0][0] == 1u && target_runs[0][1] == 3u &&
           target_runs[1][0] == 4u && target_runs[1][1] == 7u);
    int8_t negative_long_stage_adjustment[20];
    memset(negative_long_stage_adjustment, 1,
           sizeof(negative_long_stage_adjustment));
    int32_t remaining_stage_adjustment = 0;
    assert(gomore_primitives_sleep_stage_proportion_adjust(
        negative_long_stage_adjustment,
        sizeof(negative_long_stage_adjustment), 1, -20,
        &remaining_stage_adjustment));
    assert(remaining_stage_adjustment == -8);
    for (size_t index = 0u; index < 6u; ++index) {
        assert(negative_long_stage_adjustment[index] == 2 &&
               negative_long_stage_adjustment[19u - index] == 2);
    }
    for (size_t index = 6u; index < 14u; ++index) {
        assert(negative_long_stage_adjustment[index] == 1);
    }
    int8_t negative_short_stage_adjustment[5] = {1, 1, 1, 1, 1};
    assert(gomore_primitives_sleep_stage_proportion_adjust(
        negative_short_stage_adjustment,
        sizeof(negative_short_stage_adjustment), 1, -7,
        &remaining_stage_adjustment));
    assert(remaining_stage_adjustment == -12);
    for (size_t index = 0u;
            index < sizeof(negative_short_stage_adjustment); ++index) {
        assert(negative_short_stage_adjustment[index] == 2);
    }
    int8_t positive_trailing_stage_adjustment[15] = {
        1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
    };
    assert(gomore_primitives_sleep_stage_proportion_adjust(
        positive_trailing_stage_adjustment,
        sizeof(positive_trailing_stage_adjustment), 1, 20,
        &remaining_stage_adjustment));
    assert(remaining_stage_adjustment == 14);
    for (size_t index = 0u; index < 9u; ++index) {
        assert(positive_trailing_stage_adjustment[index] == 1);
    }
    for (size_t index = 9u;
            index < sizeof(positive_trailing_stage_adjustment); ++index) {
        assert(positive_trailing_stage_adjustment[index] == 2);
    }
    int8_t positive_fallback_stage_adjustment[40];
    memset(positive_fallback_stage_adjustment, 2,
           sizeof(positive_fallback_stage_adjustment));
    assert(gomore_primitives_sleep_stage_proportion_adjust(
        positive_fallback_stage_adjustment,
        sizeof(positive_fallback_stage_adjustment), 3, 20,
        &remaining_stage_adjustment));
    assert(remaining_stage_adjustment == 8);
    for (size_t index = 0u; index < 40u; ++index) {
        const int8_t expected = index >= 14u && index < 26u ? 3 : 2;
        assert(positive_fallback_stage_adjustment[index] == expected);
    }
    memset(positive_fallback_stage_adjustment, 2,
           sizeof(positive_fallback_stage_adjustment));
    assert(gomore_primitives_sleep_stage_proportion_adjust(
        positive_fallback_stage_adjustment,
        sizeof(positive_fallback_stage_adjustment), 2, 20,
        &remaining_stage_adjustment));
    assert(remaining_stage_adjustment == 7);
    for (size_t index = 0u; index < 40u; ++index) {
        assert(positive_fallback_stage_adjustment[index] == 2);
    }
    remaining_stage_adjustment = INT32_C(12345);
    assert(!gomore_primitives_sleep_stage_proportion_adjust(
        NULL, 1u, 1, 20, &remaining_stage_adjustment));
    assert(remaining_stage_adjustment == INT32_C(12345));
    int8_t smoothed_zero_run[10] = {
        4, 1, 0, 0, 0, 0, 0, 0, 3, 2,
    };
    assert(gomore_primitives_smooth_target_run_edges(
        0, smoothed_zero_run, 10u, false));
    static const int8_t expected_smoothed_zero_run[10] = {
        4, 1, 1, 1, 3, 3, 3, 3, 3, 2,
    };
    assert(memcmp(smoothed_zero_run, expected_smoothed_zero_run,
                  sizeof(smoothed_zero_run)) == 0);
    int8_t smoothed_one_run[44];
    memset(smoothed_one_run, 1, sizeof(smoothed_one_run));
    smoothed_one_run[43] = 0;
    assert(gomore_primitives_smooth_target_run_edges(
        1, smoothed_one_run, 44u, true));
    for (size_t index = 0u; index < 14u; ++index) {
        assert(smoothed_one_run[index] == 2);
    }
    for (size_t index = 14u; index < 29u; ++index) {
        assert(smoothed_one_run[index] == 1);
    }
    for (size_t index = 29u; index < 43u; ++index) {
        assert(smoothed_one_run[index] == 2);
    }
    assert(smoothed_one_run[43] == 0);
    assert(!gomore_primitives_smooth_target_run_edges(
        0, NULL, 1u, false));

    static const uint8_t stage_refine_profiles[4][11] = {
        {0x00u, 0x01u, 0x07u, 0x00u, 0x02u, 0x00u,
         0x64u, 0xECu, 0x0Au, 0x00u, 0x0Au},
        {0x01u, 0x00u, 0x00u, 0x00u, 0x00u, 0x02u,
         0x78u, 0x00u, 0x0Au, 0x07u, 0xEFu},
        {0x02u, 0x00u, 0x0Bu, 0x00u, 0x06u, 0x02u,
         0x78u, 0x00u, 0x0Au, 0x07u, 0xEFu},
        {0x03u, 0x00u, 0x0Bu, 0x00u, 0x0Au, 0x03u,
         0xA0u, 0x00u, 0x0Au, 0x00u, 0xF6u},
    };
    static const uint32_t stage_refine_hashes[4] = {
        UINT32_C(0xF57EAD45), UINT32_C(0x6322B241),
        UINT32_C(0xC5D5BFF9), UINT32_C(0x4D4F568B),
    };
    int8_t stage_refine_values[120];
    for (size_t profile = 0u; profile < 4u; ++profile) {
        static const int8_t cycle[60] = {
            0, 0, 0, 0,
            2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            2, 2, 2, 2, 2, 2, 2,
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
            2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
            3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
            0, 0, 0, 0,
        };
        memcpy(stage_refine_values, cycle, sizeof(cycle));
        memcpy(&stage_refine_values[60], cycle, sizeof(cycle));
        size_t stage_refine_count = 120u;
        assert(gomore_primitives_sleep_stage_refine(
            stage_refine_profiles[profile], stage_refine_values,
            sizeof(stage_refine_values), &stage_refine_count, 3600u));
        uint32_t hash = UINT32_C(2166136261);
        for (size_t index = 0u; index < stage_refine_count; ++index) {
            hash = (hash ^ (uint8_t)stage_refine_values[index]) *
                UINT32_C(16777619);
        }
        assert(stage_refine_count == 120u &&
               hash == stage_refine_hashes[profile]);
    }
    int8_t invalid_stage_refine[4] = {0, 2, 4, 1};
    const int8_t invalid_stage_refine_before[4] = {0, 2, 4, 1};
    size_t invalid_stage_refine_count = 4u;
    assert(!gomore_primitives_sleep_stage_refine(
        stage_refine_profiles[0], invalid_stage_refine,
        sizeof(invalid_stage_refine), &invalid_stage_refine_count, 120u));
    assert(memcmp(invalid_stage_refine, invalid_stage_refine_before,
                  sizeof(invalid_stage_refine)) == 0 &&
           invalid_stage_refine_count == 4u);
    uint8_t marked_history[8] = {1u, 0u, 1u, 0u, 0u, 0u, 0u, 0u};
    size_t marked_count = 4u;
    assert(gomore_primitives_shift_marked_history(
        marked_history, sizeof(marked_history), &marked_count, 2u));
    assert(marked_count == 6u && marked_history[0] == 0u &&
           marked_history[1] == 0u && marked_history[2] == 2u &&
           marked_history[4] == 2u);

    memset(&active_adapter_trace, 0, sizeof(active_adapter_trace));
    assert(gomore_primitives_register_mode_topics(
        (uintptr_t)UINT32_C(0x1234), (uintptr_t)UINT32_C(0x4444),
        (uintptr_t)UINT32_C(0x3333),
        adapter_register_topic));
    assert(active_adapter_trace.topic_calls == 2u &&
           active_adapter_trace.topics[0] == 4u &&
           active_adapter_trace.topics[1] == 3u &&
           active_adapter_trace.handlers[0] == (uintptr_t)UINT32_C(0x4444) &&
           active_adapter_trace.handlers[1] == (uintptr_t)UINT32_C(0x3333) &&
           active_adapter_trace.contexts[0] == (uintptr_t)UINT32_C(0x1234) &&
           active_adapter_trace.contexts[1] == (uintptr_t)UINT32_C(0x1234));
    assert(gomore_primitives_exponential_affine(
               5.0f, 2.0f, 3.0f, 1.0f, adapter_exponential) == 15.0f);

    uint8_t class_table[256];
    memset(class_table, 0, sizeof(class_table));
    class_table[(uint8_t)'a'] = 0x20u;
    class_table[(uint8_t)'b'] = 0x20u;
    uint8_t seed_source[0x10];
    uint8_t validation_destination[0x10];
    memset(seed_source, 0, sizeof(seed_source));
    memset(validation_destination, UINT8_C(0xA5),
           sizeof(validation_destination));
    seed_source[0x0C] = 0x78u;
    seed_source[0x0D] = 0x56u;
    seed_source[0x0E] = 0x34u;
    seed_source[0x0F] = 0x12u;
    const uint8_t classified_text[2] = {'a', 'b'};
    assert(gomore_primitives_seed_and_test_text_class(
               classified_text, sizeof(classified_text), class_table,
               seed_source, sizeof(seed_source), validation_destination,
               sizeof(validation_destination), adapter_seed) == 0);
    assert(active_adapter_trace.seed == UINT32_C(0x12345678) &&
           validation_destination[0x0C] == 0x78u &&
           validation_destination[0x0F] == 0x12u);
    class_table[(uint8_t)'b'] = 0u;
    assert(gomore_primitives_seed_and_test_text_class(
               classified_text, sizeof(classified_text), class_table,
               seed_source, sizeof(seed_source), validation_destination,
               sizeof(validation_destination), adapter_seed) == -1004);

    uint8_t byte_source[9] = {0u, 0u, 0u, 0u, 'a', 'b', 'c', 0u, 3u};
    const uint8_t matching_candidate[3] = {'a', 'b', 'c'};
    const uint8_t rejected_candidate[3] = {'a', 'x', 'c'};
    memset(validation_destination, UINT8_C(0xA5),
           sizeof(validation_destination));
    assert(gomore_primitives_validate_record_bytes(
               matching_candidate, sizeof(matching_candidate),
               byte_source, sizeof(byte_source), validation_destination,
               sizeof(validation_destination)) == 0);
    assert(gomore_primitives_validate_record_bytes(
               rejected_candidate, sizeof(rejected_candidate),
               byte_source, sizeof(byte_source), validation_destination,
               sizeof(validation_destination)) == -1005);
    assert(validation_destination[0x0C] == 0u &&
           validation_destination[0x0F] == 0u);
    const uint8_t su_signature[3] = {'S', 'U', 0u};
    const uint8_t bad_signature[3] = {'S', 'X', 0u};
    assert(gomore_primitives_validate_su_signature(
               su_signature, sizeof(su_signature), validation_destination,
               sizeof(validation_destination)) == 0);
    validation_destination[0x0C] = 0xA5u;
    assert(gomore_primitives_validate_su_signature(
               bad_signature, sizeof(bad_signature), validation_destination,
               sizeof(validation_destination)) == -1007);
    assert(validation_destination[0x0C] == 0u);

    uint8_t sps_engine[0x58];
    memset(sps_engine, UINT8_C(0xA5), sizeof(sps_engine));
    assert(gomore_primitives_sps_engine_initialize(
        sps_engine, sizeof(sps_engine), UINT32_C(0x89ABCDEF),
        adapter_finish_initialize));
    assert(active_adapter_trace.finish_calls == 1u &&
           sps_engine[0] == 0u && sps_engine[0x18] == 0u &&
           sps_engine[0x1B] == 0x3Fu && sps_engine[0x24] == 1u &&
           sps_engine[0x40] == 0xEFu && sps_engine[0x43] == 0x89u &&
           sps_engine[0x50] == 8u && sps_engine[0x51] == 0u &&
           sps_engine[0x57] == 0x77u);

    uint8_t composite_engine[0x3894];
    uint8_t composite_time_configuration[10] = {0u};
    void *active_estimator_state = NULL;
    uint8_t *composite_result = NULL;
    memset(composite_engine, UINT8_C(0xA5), sizeof(composite_engine));
    store_u32_fixture(&composite_engine[0x3890u], UINT32_C(0x10000000));
    memset(&active_closure_trace, 0, sizeof(active_closure_trace));
    memset(&active_adapter_trace, 0, sizeof(active_adapter_trace));
    assert(gomore_primitives_composite_engine_initialize(
        composite_engine, sizeof(composite_engine),
        composite_time_configuration, sizeof(composite_time_configuration),
        &active_estimator_state, &composite_result,
        closure_mode2_initialize, adapter_finish_initialize,
        closure_filter_initialize));
    static const size_t composite_status_offsets[] = {
        0x3800u, 0x3804u, 0x3805u, 0x3806u,
        0x3807u, 0x3808u, 0x380Fu, 0x3811u,
        0x3814u, 0x3820u, 0x3819u, 0x381Bu,
        0x381Du, 0x382Fu, 0x3839u, 0x383Eu
    };
    for (size_t index = 0u;
         index < sizeof(composite_status_offsets) /
                     sizeof(composite_status_offsets[0]);
         ++index) {
        assert(composite_engine[composite_status_offsets[index]] == 0u);
    }
    assert(active_closure_trace.mode2_calls == 1u &&
           active_closure_trace.filter_calls == 1u &&
           active_adapter_trace.finish_calls == 1u);
    assert(composite_engine[0x22Cu] == 0x66u &&
           composite_engine[0x8F4u] == 8u);
    for (size_t index = 0u; index < 5u; ++index) {
        assert(composite_engine[0xB62u + index] == UINT8_C(0xFE));
    }
    assert(composite_engine[0xB62u + 15u] == 1u &&
           composite_engine[0xB62u + 16u] == 1u);
    assert(load_u32_fixture(&composite_engine[0xB74u + 0x40u]) ==
               UINT32_C(0x10000000) &&
           composite_engine[0xB74u + 0x57u] == 0x77u &&
           load_u32_fixture(&composite_engine[0xBD4u + 0x7Cu]) ==
               UINT32_C(0x3C54FDF4) &&
           load_u32_fixture(&composite_engine[0xC58u + 0x58u]) ==
               UINT32_C(0x10000010) &&
           load_u32_fixture(&composite_engine[0xCB4u + 0x338u]) ==
               UINT32_C(0x10000018));
    assert(active_estimator_state == &composite_engine[0xCB4u]);
    assert(composite_time_configuration[0] == 1u &&
           composite_time_configuration[2] == 15u &&
           composite_time_configuration[3] == 0u &&
           composite_time_configuration[4] == 120u &&
           composite_time_configuration[5] == 0u &&
           composite_time_configuration[8] == 20u &&
           composite_time_configuration[9] == 8u);
    assert(load_u32_fixture(&composite_engine[0xFF0u + 0x138u]) ==
               UINT32_C(0x10000290) &&
           load_u32_fixture(&composite_engine[0x12B8u + 0x20F8u]) ==
               UINT32_C(0x1000029A) &&
           load_u32_fixture(&composite_engine[0x33D8u + 0x3F8u]) == 3u &&
           load_u32_fixture(&composite_engine[0x33D8u + 0x3FCu]) ==
               UINT32_C(0x3F000000) &&
           load_u32_fixture(&composite_engine[0x37DCu + 0x10u]) == 5u &&
           load_u32_fixture(&composite_engine[0x37F8u]) ==
               UINT32_C(0x1000029C));
    assert(composite_result == &composite_engine[0x37FDu]);

    static const size_t composite_control_offsets[] = {
        0x3848u, 0x384Cu, 0x384Du, 0x384Eu,
        0x384Fu, 0x3850u, 0x3857u, 0x3859u,
        0x385Cu, 0x3868u, 0x3861u, 0x3863u,
        0x3865u, 0x3877u, 0x3881u, 0x3886u,
    };
    output_orchestrator_trace orchestrator_trace = {0};
    gomore_primitives_output_orchestrator_providers orchestrator_providers = {
        .context = &orchestrator_trace,
    };
    for (size_t index = 0u;
         index < GOMORE_PRIMITIVES_OUTPUT_STAGE_COUNT; ++index) {
        orchestrator_providers.stages[index] = output_orchestrator_stage;
        composite_engine[composite_control_offsets[index]] = 0u;
    }
    uint8_t *orchestrated_result = NULL;
    assert(gomore_primitives_output_orchestrate(
        composite_engine, sizeof(composite_engine), 7u,
        &orchestrator_providers, &orchestrated_result));
    assert(orchestrator_trace.called_mask == UINT32_C(0xFFFF) &&
           orchestrated_result == &composite_engine[0x37FDu]);
    for (size_t index = 0u;
         index < GOMORE_PRIMITIVES_OUTPUT_STAGE_COUNT; ++index) {
        assert(orchestrator_trace.elapsed[index] == 7u &&
               composite_engine[composite_status_offsets[index]] ==
                   (uint8_t)(UINT32_C(0xA0) + (uint32_t)index));
        composite_engine[composite_control_offsets[index]] = 1u;
    }
    memset(&orchestrator_trace, 0, sizeof(orchestrator_trace));
    assert(gomore_primitives_output_orchestrate(
        composite_engine, sizeof(composite_engine), 99u,
        &orchestrator_providers, &orchestrated_result));
    assert(orchestrator_trace.called_mask == UINT32_C(0xFFFF));
    for (size_t index = 0u;
         index < GOMORE_PRIMITIVES_OUTPUT_STAGE_COUNT; ++index) {
        assert(orchestrator_trace.elapsed[index] == 1u &&
               composite_engine[composite_control_offsets[index]] == 0u);
        composite_engine[composite_control_offsets[index]] = 2u;
        composite_engine[composite_status_offsets[index]] = UINT8_C(0xA5);
    }
    memset(&orchestrator_trace, 0, sizeof(orchestrator_trace));
    assert(gomore_primitives_output_orchestrate(
        composite_engine, sizeof(composite_engine), 5u,
        &orchestrator_providers, &orchestrated_result));
    assert(orchestrator_trace.called_mask == 0u);
    for (size_t index = 0u;
         index < GOMORE_PRIMITIVES_OUTPUT_STAGE_COUNT; ++index) {
        assert(composite_engine[composite_control_offsets[index]] == 3u &&
               composite_engine[composite_status_offsets[index]] == 0u);
    }
    orchestrator_providers.stages[5] = NULL;
    orchestrated_result = composite_engine;
    assert(!gomore_primitives_output_orchestrate(
        composite_engine, sizeof(composite_engine), 1u,
        &orchestrator_providers, &orchestrated_result));
    assert(orchestrated_result == composite_engine);

    memset(composite_engine, UINT8_C(0xA5), sizeof(composite_engine));
    active_estimator_state = composite_engine;
    composite_result = composite_engine;
    assert(!gomore_primitives_composite_engine_initialize(
        composite_engine, sizeof(composite_engine) - 1u,
        composite_time_configuration, sizeof(composite_time_configuration),
        &active_estimator_state, &composite_result,
        closure_mode2_initialize, adapter_finish_initialize,
        closure_filter_initialize));
    assert(composite_engine[0] == UINT8_C(0xA5) &&
           composite_engine[0x3800u] == UINT8_C(0xA5) &&
           active_estimator_state == composite_engine &&
           composite_result == composite_engine);

    uint8_t sleep_algorithm_engine[0x39E0];
    uint8_t sleep_algorithm_previous[0x2E0];
    uint8_t sleep_algorithm_time_configuration[10];
    memset(sleep_algorithm_engine, UINT8_C(0xA5),
           sizeof(sleep_algorithm_engine));
    memset(sleep_algorithm_previous, 0,
           sizeof(sleep_algorithm_previous));
    memset(sleep_algorithm_time_configuration, 0,
           sizeof(sleep_algorithm_time_configuration));
    store_u32_fixture(sleep_algorithm_previous, UINT32_MAX);
    store_u32_fixture(&sleep_algorithm_previous[0x2D8u],
                      float_bits(41.0f));
    store_u32_fixture(&sleep_algorithm_previous[0x2DCu],
                      float_bits(42.0f));
    gomore_primitives_sleep_algorithm_configuration
        sleep_algorithm_configuration = {
            .random_seed = UINT32_C(0x76543210),
            .version_validation_enabled = false,
            .configured_runtime_limit = 0u,
            .runtime_present = true,
            .configured_version = 7,
            .runtime_version = 7,
            .time_configuration = sleep_algorithm_time_configuration,
            .time_configuration_length =
                sizeof(sleep_algorithm_time_configuration),
            .seed_random = adapter_seed,
            .random_value = closure_random,
            .initialize_small_filter = closure_mode_lt2_initialize,
            .initialize_large_filter = closure_mode2_initialize,
            .finish_sps_initialize = adapter_finish_initialize,
            .initialize_filter = closure_filter_initialize,
            .logger = NULL,
        };
    gomore_primitives_sleep_algorithm_outputs sleep_algorithm_outputs = {
        .active_estimator_state = NULL,
        .result_pointer = NULL,
    };
    memset(&active_closure_trace, 0, sizeof(active_closure_trace));
    memset(&active_adapter_trace, 0, sizeof(active_adapter_trace));
    assert(gomore_primitives_sleep_algorithm_initialize(
               sleep_algorithm_engine, sizeof(sleep_algorithm_engine),
               UINT32_C(0x688A5000), &default_profile_input,
               sleep_algorithm_previous, sizeof(sleep_algorithm_previous),
               UINT32_C(0x20000000), &sleep_algorithm_configuration,
               &sleep_algorithm_outputs) == 0);
    assert(active_adapter_trace.seed == UINT32_C(0x76543210) &&
           active_adapter_trace.finish_calls == 1u &&
           active_closure_trace.mode_lt2_calls == 3u &&
           active_closure_trace.mode2_calls == 2u &&
           active_closure_trace.filter_calls == 1u);
    assert(sleep_algorithm_engine[0x39D8u] == 0u &&
           sleep_algorithm_engine[0x39DAu] == 100u &&
           sleep_algorithm_engine[0x39DBu] == 0u &&
           load_u32_fixture(&sleep_algorithm_engine[0x39DCu]) ==
               UINT32_C(0x20000000) &&
           load_u32_fixture(&sleep_algorithm_engine[0x190u]) ==
               UINT32_C(0x688A5000) &&
           load_u32_fixture(&sleep_algorithm_engine[0x39D0u]) ==
               UINT32_C(0x20000008));
    assert(sleep_algorithm_engine[0x140u + 0x7Cu] == 28u &&
           sleep_algorithm_engine[0x140u + 0x7Du] == 1u &&
           load_u32_fixture(&sleep_algorithm_engine[0x140u + 0x74u]) ==
               float_bits(175.0f) &&
           load_u32_fixture(&sleep_algorithm_engine[0x140u + 0x20u]) ==
               float_bits(41.0f) &&
           load_u32_fixture(&sleep_algorithm_engine[0x140u + 0x24u]) ==
               float_bits(42.0f));
    assert(load_u32_fixture(sleep_algorithm_previous) == UINT32_MAX &&
           load_u32_fixture(&sleep_algorithm_previous[0x2D8u]) ==
               float_bits(41.0f) &&
           load_u32_fixture(&sleep_algorithm_previous[0x2DCu]) ==
               float_bits(42.0f));
    assert(sleep_algorithm_outputs.active_estimator_state ==
               &sleep_algorithm_engine[0x140u + 0xCB4u] &&
           sleep_algorithm_outputs.result_pointer ==
               &sleep_algorithm_engine[0x140u + 0x37FDu] &&
           sleep_algorithm_time_configuration[0] == 1u &&
           sleep_algorithm_time_configuration[8] == 20u &&
           sleep_algorithm_time_configuration[9] == 8u);

    memset(sleep_algorithm_engine, UINT8_C(0xA5),
           sizeof(sleep_algorithm_engine));
    memset(sleep_algorithm_previous, 0,
           sizeof(sleep_algorithm_previous));
    sleep_algorithm_previous[12] = 1u;
    memset(&active_closure_trace, 0, sizeof(active_closure_trace));
    memset(&active_adapter_trace, 0, sizeof(active_adapter_trace));
    assert(gomore_primitives_sleep_algorithm_initialize(
               sleep_algorithm_engine, sizeof(sleep_algorithm_engine),
               UINT32_C(0x688A5000), &default_profile_input,
               sleep_algorithm_previous, sizeof(sleep_algorithm_previous),
               UINT32_C(0x20000000), &sleep_algorithm_configuration,
               &sleep_algorithm_outputs) == -5);
    assert(sleep_algorithm_engine[0x39D8u] == UINT8_C(0xFB) &&
           active_closure_trace.mode_lt2_calls == 0u &&
           active_closure_trace.mode2_calls == 0u &&
           active_adapter_trace.finish_calls == 0u);

    memset(sleep_algorithm_engine, UINT8_C(0xA5),
           sizeof(sleep_algorithm_engine));
    memset(sleep_algorithm_previous, 0,
           sizeof(sleep_algorithm_previous));
    memset(sleep_algorithm_time_configuration, 0,
           sizeof(sleep_algorithm_time_configuration));
    memset(&active_closure_trace, 0, sizeof(active_closure_trace));
    memset(&active_adapter_trace, 0, sizeof(active_adapter_trace));
    assert(gomore_primitives_sleep_algorithm_initialize(
               sleep_algorithm_engine, sizeof(sleep_algorithm_engine),
               UINT32_C(0x688A5000), &default_profile_input,
               sleep_algorithm_previous, sizeof(sleep_algorithm_previous),
               UINT32_C(0x20000000), &sleep_algorithm_configuration,
               &sleep_algorithm_outputs) == 0);
    assert(load_u32_fixture(sleep_algorithm_previous) ==
               UINT32_C(0x80000000) &&
           sleep_algorithm_engine[0x39D8u] == 0u);

    sleep_algorithm_configuration.configured_version = 6;
    memset(sleep_algorithm_engine, UINT8_C(0xA5),
           sizeof(sleep_algorithm_engine));
    store_u32_fixture(sleep_algorithm_previous, UINT32_MAX);
    memset(&active_closure_trace, 0, sizeof(active_closure_trace));
    assert(gomore_primitives_sleep_algorithm_initialize(
               sleep_algorithm_engine, sizeof(sleep_algorithm_engine),
               UINT32_C(0x688A5000), &default_profile_input,
               sleep_algorithm_previous, sizeof(sleep_algorithm_previous),
               UINT32_C(0x20000000), &sleep_algorithm_configuration,
               &sleep_algorithm_outputs) == -1008);
    assert(sleep_algorithm_engine[0x39D8u] ==
               (uint8_t)(int32_t)-1008 &&
           active_closure_trace.mode_lt2_calls == 0u);
    sleep_algorithm_configuration.configured_version = 7;

    gomore_primitives_profile_input invalid_sleep_profile =
        default_profile_input;
    invalid_sleep_profile.age_years = 200.0f;
    memset(sleep_algorithm_engine, UINT8_C(0xA5),
           sizeof(sleep_algorithm_engine));
    store_u32_fixture(sleep_algorithm_previous, UINT32_MAX);
    memset(&active_closure_trace, 0, sizeof(active_closure_trace));
    memset(&active_adapter_trace, 0, sizeof(active_adapter_trace));
    assert(gomore_primitives_sleep_algorithm_initialize(
               sleep_algorithm_engine, sizeof(sleep_algorithm_engine),
               UINT32_C(0x688A5000), &invalid_sleep_profile,
               sleep_algorithm_previous, sizeof(sleep_algorithm_previous),
               UINT32_C(0x20000000), &sleep_algorithm_configuration,
               &sleep_algorithm_outputs) == -101);
    assert(sleep_algorithm_engine[0x39D8u] == UINT8_C(0x9B) &&
           active_closure_trace.mode_lt2_calls == 3u &&
           active_closure_trace.mode2_calls == 1u &&
           active_adapter_trace.finish_calls == 0u);

    memset(sleep_algorithm_engine, UINT8_C(0xA5),
           sizeof(sleep_algorithm_engine));
    active_adapter_trace.seed = 0u;
    assert(gomore_primitives_sleep_algorithm_initialize(
               sleep_algorithm_engine,
               sizeof(sleep_algorithm_engine) - 1u,
               UINT32_C(0x688A5000), &default_profile_input,
               sleep_algorithm_previous, sizeof(sleep_algorithm_previous),
               UINT32_C(0x20000000), &sleep_algorithm_configuration,
               &sleep_algorithm_outputs) == -1);
    assert(sleep_algorithm_engine[0] == UINT8_C(0xA5) &&
           sleep_algorithm_engine[0x39DFu] == UINT8_C(0xA5) &&
           active_adapter_trace.seed == 0u);

    uint8_t dispatch_state[0x391D];
    memset(dispatch_state, 0, sizeof(dispatch_state));
    active_adapter_trace.state = dispatch_state;
    assert(gomore_primitives_state_mode_dispatch(
               dispatch_state, sizeof(dispatch_state), 0, 0x66u,
               adapter_state_mode0, adapter_state_mode1,
               adapter_state_mode2, adapter_state_mode3) == 0);
    assert(active_adapter_trace.state_value == 0x66u);
    assert(gomore_primitives_state_mode_dispatch(
               dispatch_state, sizeof(dispatch_state), 1, 0x55u,
               adapter_state_mode0, adapter_state_mode1,
               adapter_state_mode2, adapter_state_mode3) == -1);
    assert(gomore_primitives_state_mode_dispatch(
               dispatch_state, sizeof(dispatch_state), 2, 0u,
               adapter_state_mode0, adapter_state_mode1,
               adapter_state_mode2, adapter_state_mode3) == 0);
    assert(gomore_primitives_state_mode_dispatch(
               dispatch_state, sizeof(dispatch_state), 3, 0u,
               adapter_state_mode0, adapter_state_mode1,
               adapter_state_mode2, adapter_state_mode3) == 0);
    assert(gomore_primitives_state_mode_dispatch(
               dispatch_state, sizeof(dispatch_state), 4, 0u,
               adapter_state_mode0, adapter_state_mode1,
               adapter_state_mode2, adapter_state_mode3) == -1);

    uint8_t commit_engine[0x126C];
    uint8_t adapter_destination[10];
    memset(commit_engine, 0, sizeof(commit_engine));
    memset(adapter_destination, 0, sizeof(adapter_destination));
    assert(gomore_primitives_commit_valid_time_record_adapter(
        commit_engine, sizeof(commit_engine), adapter_destination,
        sizeof(adapter_destination), valid_time_record,
        sizeof(valid_time_record)));
    assert(adapter_destination[2] == 20u &&
           adapter_destination[9] == 20u &&
           commit_engine[0x1260] == 20u &&
           commit_engine[0x1267] == 20u);
    assert(gomore_primitives_one_minus(0.25f) == 0.75f);
    const float logistic = gomore_primitives_logistic(
        2.0f, adapter_exponential);
    assert(logistic > 0.111f && logistic < 0.112f);
    const float scaled_product = gomore_primitives_scaled_product(1.0f, 10.0f);
    assert(scaled_product > 0.139f && scaled_product < 0.141f);
    const float linear_coefficients[4] = {1.0f, 1.0f, 1.0f, 1.0f};
    assert(gomore_primitives_linear_sign_classify(
               1.0f, 2.0f, 3.0f, 4, linear_coefficients, -10.0f) == -1);
    assert(gomore_primitives_linear_sign_classify(
               1.0f, 2.0f, 3.0f, 4, linear_coefficients, -11.0f) == 1);

    uint8_t key_configuration[9] = {
        0u, 0u, 0u, 0u, 'a', 'b', 'c', 0u, 3u};
    uint8_t update_state[0x14];
    uint8_t update_status[12];
    memset(update_state, 0, sizeof(update_state));
    memset(update_status, 0, sizeof(update_status));
    update_state[0x10] = 3u;
    assert(gomore_primitives_validate_key_and_update_status(
               matching_candidate, sizeof(matching_candidate),
               key_configuration, sizeof(key_configuration),
               update_state, sizeof(update_state),
               update_status, sizeof(update_status),
               closure_prepare, closure_random) == 0);
    assert(update_state[0x10] == 4u && update_state[4] == 100u);
    memset(update_state, 0, sizeof(update_state));
    memset(update_status, 0, sizeof(update_status));
    assert(gomore_primitives_validate_key_and_update_status(
               rejected_candidate, sizeof(rejected_candidate),
               key_configuration, sizeof(key_configuration),
               update_state, sizeof(update_state),
               update_status, sizeof(update_status),
               closure_prepare, closure_random) == -1005);
    assert(update_status[6] == 0x13u && update_status[7] == 0xFCu &&
           update_state[8] == 0u);

    uint8_t decimal_configuration[0x10];
    memset(decimal_configuration, 0, sizeof(decimal_configuration));
    memset(update_state, 0, sizeof(update_state));
    memset(update_status, 0, sizeof(update_status));
    const uint8_t decimal_text[] = "123";
    assert(gomore_primitives_decimal_config_update(
               decimal_text, decimal_configuration,
               sizeof(decimal_configuration), update_state,
               sizeof(update_state), update_status, sizeof(update_status),
               false, closure_prepare, closure_random) == 0);
    assert(update_state[8] == 123u && update_state[9] == 0u);
    memset(update_state, 0, sizeof(update_state));
    memset(update_status, 0, sizeof(update_status));
    assert(gomore_primitives_decimal_config_update(
               decimal_text, decimal_configuration,
               sizeof(decimal_configuration), update_state,
               sizeof(update_state), update_status, sizeof(update_status),
               true, closure_prepare, closure_random) == -1006);
    assert(update_status[8] == 0x12u && update_status[9] == 0xFCu &&
           update_state[8] == 0u);

    assert(gomore_primitives_runtime_version_validate(
               UINT32_C(0x688A4181), false, true,
               UINT32_C(0x688A4200), true, 7, 7) == 0);
    assert(gomore_primitives_runtime_version_validate(
               UINT32_C(0x688A4180), false, true,
               UINT32_C(0x688A4200), true, 7, 7) == -1006);
    assert(gomore_primitives_runtime_version_validate(
               UINT32_C(0x688A4181), false, false,
               UINT32_C(0x688A4200), false, 7, 7) == -1);
    assert(gomore_primitives_runtime_version_validate(
               UINT32_C(0x688A4181), true, false,
               UINT32_C(0x688A4200), true, 7, 8) == -1008);
    int32_t run_values_i32[5] = {3, 1, 1, 2, 2};
    int32_t dominant_value = 0;
    size_t dominant_count = 0u;
    assert(gomore_primitives_dominant_sorted_i32(
        run_values_i32, 5u, &dominant_value, &dominant_count));
    assert(run_values_i32[0] == 1 && run_values_i32[1] == 1 &&
           run_values_i32[2] == 2 && run_values_i32[3] == 2 &&
           run_values_i32[4] == 3 && dominant_value == 2 &&
           dominant_count == 2u);
    const int16_t circular_primary[5] = {0, 0, 201, 202, 203};
    const int16_t circular_first[5] = {0, 0, 181, 181, 181};
    const int16_t circular_zero[5] = {0, 0, 0, 0, 0};
    assert(gomore_primitives_circular_signal_predicate(
               circular_primary, circular_first, circular_zero,
               circular_zero, 5u, 0, 3u) == 1);
    assert(gomore_primitives_circular_signal_predicate(
               circular_primary, circular_first, circular_zero,
               circular_zero, 5u, 0, 2u) == -1);
    const float crossing_values[6] = {
        1.0f, -1.0f, -1.0f, 1.0f, 1.0f, -1.0f};
    assert(gomore_primitives_average_sign_crossing_spacing(
               crossing_values, 6u) == 2.0f);
    const float one_crossing[3] = {1.0f, 1.0f, -1.0f};
    assert(gomore_primitives_average_sign_crossing_spacing(
               one_crossing, 3u) == -1.0f);
    assert(gomore_primitives_round_decimal_places(
               1.234f, 2.0f, adapter_power10) == 1.23f);
    assert(gomore_primitives_round_decimal_places(
               -1.234f, 2.0f, adapter_power10) == -1.23f);
    assert(gomore_primitives_round_decimal_places(
               bits_float(UINT32_C(0x7FC00000)), 2.0f,
               adapter_power10) == 0.0f);
    assert(gomore_primitives_round_decimal_places(
               bits_float(UINT32_C(0x7F800000)), 2.0f,
               adapter_power10) > 21474834.0f);

    const float baseline_ordinary_half =
        gomore_primitives_speed_dynamics_baseline(
            0.5f, 165.0f, 1.2f, 70.0f, 0u, adapter_power10);
    const float baseline_ordinary_one =
        gomore_primitives_speed_dynamics_baseline(
            1.0f, 165.0f, 1.2f, 70.0f, 0u, adapter_power10);
    const float baseline_flagged_half =
        gomore_primitives_speed_dynamics_baseline(
            0.5f, 165.0f, 1.2f, 70.0f, UINT16_C(0x0440),
            adapter_power10);
    assert(float_bits(baseline_ordinary_half) == UINT32_C(0x42519EBB));
    assert(float_bits(baseline_ordinary_one) == UINT32_C(0x42D19EBB));
    assert(float_bits(baseline_flagged_half) >= UINT32_C(0x427843EA) &&
           float_bits(baseline_flagged_half) <= UINT32_C(0x427843EE));
    assert(gomore_primitives_speed_dynamics_baseline(
               -1.0f, 165.0f, 1.2f, 70.0f, 0u,
               adapter_power10) == 0.0f);
    assert(gomore_primitives_speed_dynamics_baseline(
               bits_float(UINT32_C(0x7FC00000)), 165.0f,
               1.2f, 70.0f, 0u, adapter_power10) == 0.0f);
    const uint32_t baseline_flagged_threshold_bits = float_bits(
        gomore_primitives_speed_dynamics_baseline(
            bits_float(UINT32_C(0x3FA00000)), 165.0f,
            1.2f, 70.0f, UINT16_C(0x0440), adapter_power10));
    const uint32_t baseline_flagged_above_bits = float_bits(
        gomore_primitives_speed_dynamics_baseline(
            bits_float(UINT32_C(0x3FA00001)), 165.0f,
            1.2f, 70.0f, UINT16_C(0x0440), adapter_power10));
    assert(baseline_flagged_threshold_bits >= UINT32_C(0x4280CDE4) &&
           baseline_flagged_threshold_bits <= UINT32_C(0x4280CDE8));
    assert(baseline_flagged_above_bits >= UINT32_C(0x42D7A338) &&
           baseline_flagged_above_bits <= UINT32_C(0x42D7A33C));
    assert(gomore_primitives_speed_dynamics_baseline(
               1.0f, 165.0f, 1.2f, 70.0f, 0u, NULL) == 0.0f);
    uint8_t time_engine[0x13C];
    uint8_t time_configuration[10];
    memset(time_engine, UINT8_C(0xA5), sizeof(time_engine));
    memset(time_configuration, 0, sizeof(time_configuration));
    assert(gomore_primitives_time_engine_initialize(
        time_engine, sizeof(time_engine), time_configuration,
        sizeof(time_configuration), UINT32_C(0x12345678)));
    assert(time_configuration[0] == 1u &&
           time_configuration[2] == 15u &&
           time_configuration[4] == 120u &&
           time_configuration[8] == 20u &&
           time_configuration[9] == 8u &&
           time_engine[0xB0] == 0x58u && time_engine[0xB1] == 0x02u &&
           time_engine[0x130] == 15u && time_engine[0x132] == 120u &&
           time_engine[0x136] == 20u && time_engine[0x137] == 8u &&
           time_engine[0x138] == 0x78u && time_engine[0x13B] == 0x12u);
    const float interval_values[10] = {
        1.0f, 2.0f, 5.0f, 4.0f, 0.0f,
        0.0f, 0.0f, 0.0f, 0.0f, 0.0f};
    const uint8_t interval_boundaries[3] = {0u, 8u, 10u};
    uint8_t interval_output[2] = {0u, 0u};
    size_t interval_output_count = 0u;
    assert(gomore_primitives_interval_nonzero_argmax(
        interval_values, 10u, interval_boundaries, 3u,
        interval_output, 2u, &interval_output_count));
    assert(interval_output_count == 1u && interval_output[0] == 2u);
    uint8_t replay_state[0x54];
    uint8_t replay_record[8];
    memset(replay_state, 0, sizeof(replay_state));
    memset(replay_record, 0, sizeof(replay_record));
    replay_state[0x48] = 10u;
    replay_record[4] = 13u;
    active_adapter_trace.record_steps = 0u;
    assert(gomore_primitives_sequence_replay(
               replay_state, sizeof(replay_state), replay_record,
               sizeof(replay_record), adapter_process_record) == 42);
    assert(active_adapter_trace.record_steps == 3u &&
           active_adapter_trace.record_sequences[0] == 11u &&
           active_adapter_trace.record_sequences[1] == 12u &&
           active_adapter_trace.record_sequences[2] == 13u &&
           replay_record[4] == 14u && replay_state[0x48] == 14u);
    memset(replay_state, 0, sizeof(replay_state));
    memset(replay_record, 0, sizeof(replay_record));
    replay_state[0x48] = 10u;
    replay_record[4] = 26u;
    assert(gomore_primitives_sequence_replay(
               replay_state, sizeof(replay_state), replay_record,
               sizeof(replay_record), adapter_process_record) == -1027);
    assert(replay_state[0x52] == 0xFDu && replay_state[0x53] == 0xFBu);

    uint8_t dormant_state[GOMORE_PRIMITIVES_DORMANT_ESTIMATOR_STATE_BYTES];
    uint8_t dormant_output[GOMORE_PRIMITIVES_DORMANT_ESTIMATOR_OUTPUT_BYTES];
    const uint32_t dormant_time = 1000u;
    const float dormant_heart_rate = 72.9f;
    const float dormant_speed = 10.0f;
    const float dormant_profile[6] = {
        175.0f, 75.0f, -999999.0f, 0.0f, 0.0f, 1.0f,
    };
    const float dormant_auxiliary[3] = {1.0f, 2.0f, 3.0f};
    const float dormant_energy = 0.1f;
    memset(dormant_state, 0, sizeof(dormant_state));
    memset(dormant_output, UINT8_C(0xA5), sizeof(dormant_output));
    assert(gomore_primitives_dormant_estimator_update(
               dormant_state, sizeof(dormant_state), 1u,
               NULL, NULL, NULL, NULL, NULL, NULL,
               NULL, 0u, NULL) == 1);
    assert(load_u32_fixture(&dormant_state[0x32Cu]) == 0u);

    store_u32_fixture(&dormant_state[0x330u], 2u);
    assert(gomore_primitives_dormant_estimator_update(
               dormant_state, sizeof(dormant_state), 7u,
               &dormant_time, &dormant_heart_rate, &dormant_speed,
               dormant_profile, dormant_auxiliary, &dormant_energy,
               NULL, 0u, NULL) == 0);
    assert(load_u32_fixture(&dormant_state[0x328u]) == 0u &&
           load_u32_fixture(&dormant_state[0x32Cu]) == 1u);
    assert(gomore_primitives_dormant_estimator_update(
               dormant_state, sizeof(dormant_state), 7u,
               &dormant_time, &dormant_heart_rate, &dormant_speed,
               dormant_profile, dormant_auxiliary, &dormant_energy,
               NULL, 0u, NULL) == 0);
    assert(load_u32_fixture(&dormant_state[0x328u]) == 7u &&
           load_u32_fixture(&dormant_state[0x32Cu]) == 2u);

    memset(dormant_state, 0, sizeof(dormant_state));
    memset(dormant_output, UINT8_C(0xA5), sizeof(dormant_output));
    memset(&active_dormant_estimator_trace, 0,
           sizeof(active_dormant_estimator_trace));
    store_u32_fixture(&dormant_state[0x48u], UINT32_MAX);
    store_u32_fixture(&dormant_state[0x330u], 1u);
    dormant_state[0x52] = 0x34u;
    dormant_state[0x53] = 0x12u;
    assert(gomore_primitives_dormant_estimator_update(
               dormant_state, sizeof(dormant_state), 1u,
               &dormant_time, &dormant_heart_rate, &dormant_speed,
               dormant_profile, dormant_auxiliary, &dormant_energy,
               dormant_output, sizeof(dormant_output),
               dormant_estimator_process_record) == 0);
    assert(active_dormant_estimator_trace.calls == 1u &&
           active_dormant_estimator_trace.sample_indices[0] == 0u &&
           active_dormant_estimator_trace.heart_rates[0] == 72 &&
           active_dormant_estimator_trace.speeds[0] == 10.0f &&
           active_dormant_estimator_trace.configurations[0] == -999999.0f &&
           active_dormant_estimator_trace.current_time == 1000u &&
           active_dormant_estimator_trace.auxiliaries[0] == 2.0f &&
           active_dormant_estimator_trace.auxiliaries[1] == 1.0f &&
           active_dormant_estimator_trace.auxiliaries[2] == 3.0f &&
           active_dormant_estimator_trace.energy == 0.1f);
    assert(dormant_output[0] == UINT8_C(0xA5) &&
           dormant_output[0x42] == 0x34u &&
           dormant_output[0x43] == 0x12u &&
           load_u32_fixture(&dormant_state[0x32Cu]) == 1u);

    assert(gomore_primitives_dormant_estimator_update(
               dormant_state, sizeof(dormant_state), 5u,
               &dormant_time, &dormant_heart_rate, &dormant_speed,
               dormant_profile, dormant_auxiliary, &dormant_energy,
               dormant_output, sizeof(dormant_output),
               dormant_estimator_process_record) == 0);
    assert(active_dormant_estimator_trace.calls == 6u);
    for (size_t index = 1u; index < 6u; ++index) {
        assert(active_dormant_estimator_trace.sample_indices[index] == index &&
               active_dormant_estimator_trace.heart_rates[index] ==
                   71 + (int32_t)index &&
               active_dormant_estimator_trace.configurations[index] ==
                   -1000000.0f + (float)index);
    }
    assert(load_u32_fixture(&dormant_state[0x328u]) == 5u &&
           load_u32_fixture(&dormant_state[0x32Cu]) == 2u &&
           load_u32_fixture(&dormant_state[0x48u]) == 6u);

    dormant_state[0x334] = 1u;
    assert(gomore_primitives_dormant_estimator_update(
               dormant_state, sizeof(dormant_state), 1u,
               &dormant_time, &dormant_heart_rate, &dormant_speed,
               dormant_profile, dormant_auxiliary, &dormant_energy,
               dormant_output, sizeof(dormant_output),
               dormant_estimator_process_record) == 0);
    assert(active_dormant_estimator_trace.heart_rates[6] == -1 &&
           active_dormant_estimator_trace.speeds[6] == -1.0f);

    memset(dormant_state, 0, sizeof(dormant_state));
    memset(dormant_output, UINT8_C(0xA5), sizeof(dormant_output));
    memset(&active_dormant_estimator_trace, 0,
           sizeof(active_dormant_estimator_trace));
    store_u32_fixture(&dormant_state[0x48u], UINT32_MAX);
    store_u32_fixture(&dormant_state[0x330u], 1u);
    dormant_state[0x54] = 1u;
    const float dormant_nan = bits_float(UINT32_C(0x7FC00000));
    assert(gomore_primitives_dormant_estimator_update(
               dormant_state, sizeof(dormant_state), 1u,
               &dormant_time, &dormant_nan, &dormant_speed,
               dormant_profile, dormant_auxiliary, &dormant_energy,
               dormant_output, sizeof(dormant_output),
               dormant_estimator_process_record) == 0);
    assert(active_dormant_estimator_trace.heart_rates[0] == 0);
    for (size_t index = 0u; index < sizeof(dormant_output); ++index) {
        assert(dormant_output[index] == 0u);
    }
    const float dormant_conversion_inputs[6] = {
        72.9f,
        -72.9f,
        bits_float(UINT32_C(0x7F800000)),
        bits_float(UINT32_C(0xFF800000)),
        bits_float(UINT32_C(0x4EFFFFFF)),
        bits_float(UINT32_C(0x4F000000)),
    };
    const int32_t dormant_conversion_expected[6] = {
        72, -72, INT32_MAX, INT32_MIN, INT32_C(2147483520), INT32_MAX,
    };
    for (size_t index = 0u; index < 6u; ++index) {
        memset(dormant_state, 0, sizeof(dormant_state));
        memset(&active_dormant_estimator_trace, 0,
               sizeof(active_dormant_estimator_trace));
        store_u32_fixture(&dormant_state[0x48u], UINT32_MAX);
        store_u32_fixture(&dormant_state[0x330u], 1u);
        assert(gomore_primitives_dormant_estimator_update(
                   dormant_state, sizeof(dormant_state), 1u,
                   &dormant_time, &dormant_conversion_inputs[index],
                   &dormant_speed, dormant_profile, dormant_auxiliary,
                   &dormant_energy, dormant_output, sizeof(dormant_output),
                   dormant_estimator_process_record) == 0);
        assert(active_dormant_estimator_trace.heart_rates[0] ==
               dormant_conversion_expected[index]);
    }
    assert(gomore_primitives_dormant_estimator_update(
               dormant_state, sizeof(dormant_state) - 1u, 1u,
               &dormant_time, &dormant_heart_rate, &dormant_speed,
               dormant_profile, dormant_auxiliary, &dormant_energy,
               dormant_output, sizeof(dormant_output),
               dormant_estimator_process_record) == -1);

    gomore_primitives_sleep_motion_state sleep_motion_state;
    assert(sizeof(sleep_motion_state) == 128u);
    memset(&sleep_motion_state, UINT8_C(0xA5),
           sizeof(sleep_motion_state));
    sleep_motion_state.magnitude_threshold = 3.0f;
    float sleep_motion_output[2] = {0.0f, 0.0f};
    assert(gomore_primitives_sleep_motion_feature(
               &sleep_motion_state, 0u, NULL, true,
               sleep_motion_output, NULL, NULL) == INT32_C(0x40));
    assert(sleep_motion_output[0] == -1.0f &&
           sleep_motion_output[1] == -1.0f &&
           sleep_motion_state.warmup_count == 0u &&
           sleep_motion_state.magnitude_threshold == 3.0f);
    const float zero_motion_channel[25] = {0.0f};
    const float *zero_motion_channels[3] = {
        zero_motion_channel, zero_motion_channel, zero_motion_channel,
    };
    for (size_t index = 0u; index < 5u; ++index) {
        assert(gomore_primitives_sleep_motion_feature(
                   &sleep_motion_state, 0u, zero_motion_channels, false,
                   sleep_motion_output, positive_floor_fixture,
                   zero_sqrt_fixture) == INT32_C(0x41));
        assert(sleep_motion_output[0] == -1.0f &&
               sleep_motion_output[1] == -1.0f &&
               sleep_motion_state.warmup_count == index + 1u);
    }
    assert(gomore_primitives_sleep_motion_feature(
               &sleep_motion_state, 0u, zero_motion_channels, false,
               sleep_motion_output, positive_floor_fixture,
               zero_sqrt_fixture) == 0);
    assert(sleep_motion_output[0] == 0.0f &&
           sleep_motion_output[1] == 0.0f &&
           sleep_motion_state.warmup_count == 5u);
    assert(gomore_primitives_sleep_motion_feature(
               &sleep_motion_state, 2u, zero_motion_channels, false,
               sleep_motion_output, positive_floor_fixture,
               zero_sqrt_fixture) == INT32_C(0x41));
    assert(sleep_motion_state.warmup_count == 1u &&
           sleep_motion_state.magnitude_threshold == 3.0f);
    assert(gomore_primitives_sleep_motion_feature(
               NULL, 0u, zero_motion_channels, false,
               sleep_motion_output, positive_floor_fixture,
               zero_sqrt_fixture) == -1);

    gomore_primitives_minute_accumulator minute_accumulator;
    assert(sizeof(minute_accumulator) == 72u);
    memset(&minute_accumulator, 0, sizeof(minute_accumulator));
    assert(gomore_primitives_minute_accumulator_update(
        &minute_accumulator, 10u, 100u, 0.0f));
    assert(minute_accumulator.valid_count == 1 &&
           minute_accumulator.zero_count == 1 &&
           minute_accumulator.integer_sum == 0);
    assert(gomore_primitives_minute_accumulator_update(
        &minute_accumulator, 10u, 110u, 5.9f));
    assert(minute_accumulator.valid_count == 2 &&
           minute_accumulator.zero_count == 1 &&
           minute_accumulator.integer_sum == 5);
    assert(gomore_primitives_minute_accumulator_update(
        &minute_accumulator, 20u, 130u, 2.0f));
    assert(minute_accumulator.minute_zero_fraction[1] == 0.5f &&
           minute_accumulator.previous_zero_fraction == 0.5f &&
           minute_accumulator.valid_count == 1 &&
           minute_accumulator.zero_count == 0 &&
           minute_accumulator.integer_sum == 2);

    memset(&minute_accumulator, 0, sizeof(minute_accumulator));
    minute_accumulator.valid_count = 2;
    minute_accumulator.zero_count = 1;
    minute_accumulator.integer_sum = 9;
    minute_accumulator.previous_zero_fraction = 0.25f;
    assert(gomore_primitives_minute_accumulator_update(
        &minute_accumulator, 190u, 500u, -1.0f));
    assert(minute_accumulator.minute_zero_fraction[5] == 0.5f &&
           minute_accumulator.minute_zero_fraction[6] == 0.5f &&
           minute_accumulator.minute_zero_fraction[7] == 0.5f &&
           minute_accumulator.previous_zero_fraction == 0.5f &&
           minute_accumulator.valid_count == 0 &&
           minute_accumulator.zero_count == 0 &&
           minute_accumulator.integer_sum == 0);

    memset(&minute_accumulator, UINT8_C(0xA5),
           sizeof(minute_accumulator));
    minute_accumulator.previous_zero_fraction = 0.75f;
    minute_accumulator.valid_count = 0;
    minute_accumulator.zero_count = 0;
    minute_accumulator.integer_sum = 0;
    assert(gomore_primitives_minute_accumulator_update(
        &minute_accumulator, 61u, 121u, -1.0f));
    assert(minute_accumulator.minute_zero_fraction[1] == 0.75f);

    memset(&minute_accumulator, UINT8_C(0xA5),
           sizeof(minute_accumulator));
    assert(gomore_primitives_minute_accumulator_update(
        &minute_accumulator, 900u, 1000u, -1.0f));
    for (size_t index = 0u; index < 15u; ++index) {
        assert(minute_accumulator.minute_zero_fraction[index] == 0.0f);
    }
    assert(minute_accumulator.previous_zero_fraction == 0.0f &&
           minute_accumulator.valid_count == 0 &&
           minute_accumulator.zero_count == 0 &&
           minute_accumulator.integer_sum == 0);
    const float accumulator_nan = bits_float(UINT32_C(0x7FC00000));
    assert(gomore_primitives_minute_accumulator_update(
        &minute_accumulator, 0u, 1000u, accumulator_nan));
    assert(minute_accumulator.valid_count == 0);
    assert(!gomore_primitives_minute_accumulator_update(
        NULL, 0u, 0u, 0.0f));

    uintptr_t tensor_bank_layout[13];
    uint32_t tensor_bank_bindings[3] = {
        0u, UINT32_C(0x7777), 0u,
    };
    uint8_t tensor_bank_records[16u * 20u];
    memset(tensor_bank_layout, 0, sizeof(tensor_bank_layout));
    memset(tensor_bank_records, 0, sizeof(tensor_bank_records));
    tensor_bank_records[1u * 20u + 10u] = 11u;
    tensor_bank_records[3u * 20u + 10u] = 22u;
    memset(&active_tensor_fill_trace, 0, sizeof(active_tensor_fill_trace));
    assert(gomore_primitives_tensor_bank_initialize(
        tensor_bank_layout, 11u, true, false, 2u,
        tensor_bank_bindings, 2u, tensor_bank_records, 8u,
        (uintptr_t)UINT32_C(0x1234), (uintptr_t)UINT32_C(0x5678),
        create_filled_tensor_fixture));
    assert(tensor_bank_layout[0] == 1u &&
           tensor_bank_layout[1] == 0u &&
           tensor_bank_layout[2] == 2u &&
           tensor_bank_layout[3] == (uintptr_t)&tensor_bank_records[0] &&
           tensor_bank_layout[5] == (uintptr_t)&tensor_bank_records[20] &&
           tensor_bank_layout[4] == (uintptr_t)&tensor_bank_records[40] &&
           tensor_bank_layout[6] == (uintptr_t)&tensor_bank_records[60] &&
           tensor_bank_layout[7] == (uintptr_t)&tensor_bank_records[80] &&
           tensor_bank_layout[9] == (uintptr_t)&tensor_bank_records[100] &&
           tensor_bank_layout[8] == (uintptr_t)&tensor_bank_records[120] &&
           tensor_bank_layout[10] == (uintptr_t)&tensor_bank_records[140]);
    assert(active_tensor_fill_trace.calls == 1u &&
           active_tensor_fill_trace.runtime_binding ==
               (uintptr_t)UINT32_C(0x1234) &&
           active_tensor_fill_trace.pool_binding ==
               (uintptr_t)UINT32_C(0x5678) &&
           active_tensor_fill_trace.dimensions[0] == 11u &&
           tensor_bank_bindings[0] == UINT32_C(0x9000) &&
           tensor_bank_bindings[1] == UINT32_C(0x7777));

    for (size_t index = 0u; index < 13u; ++index) {
        tensor_bank_layout[index] = (uintptr_t)UINT32_C(0xA5A5A5A5);
    }
    assert(!gomore_primitives_tensor_bank_initialize(
        tensor_bank_layout, 10u, true, false, 2u,
        tensor_bank_bindings, 2u, tensor_bank_records, 8u,
        0u, 0u, create_filled_tensor_fixture));
    assert(tensor_bank_layout[0] ==
           (uintptr_t)UINT32_C(0xA5A5A5A5));
    assert(gomore_primitives_tensor_bank_initialize(
        tensor_bank_layout, 3u, false, false, 0u,
        NULL, 0u, NULL, 0u, 0u, 0u, NULL));
    assert(tensor_bank_layout[0] == 0u &&
           tensor_bank_layout[1] == 0u &&
           tensor_bank_layout[2] == 0u);

    float sleep_iir_impulse[8] = {
        1.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f,
    };
    const uint32_t sleep_iir_expected[8] = {
        UINT32_C(0x3DBBA7A8), UINT32_C(0x3E296194),
        UINT32_C(0x3E07503E), UINT32_C(0x3DD3DD6A),
        UINT32_C(0x3DA16F3C), UINT32_C(0x3D6CC726),
        UINT32_C(0x3D23BD7A), UINT32_C(0x3CCC6846),
    };
    assert(gomore_primitives_sleep_iir2_filter(
        sleep_iir_impulse, 8u));
    for (size_t index = 0u; index < 8u; ++index) {
        assert(float_bits(sleep_iir_impulse[index]) ==
               sleep_iir_expected[index]);
    }
    assert(gomore_primitives_sleep_iir2_filter(NULL, 0u));
    assert(!gomore_primitives_sleep_iir2_filter(NULL, 1u));

    gomore_primitives_sleep_step_state sleep_step_state;
    assert(sizeof(sleep_step_state) == 184u &&
           offsetof(gomore_primitives_sleep_step_state,
                    decimated_ring) == 0x48u &&
           offsetof(gomore_primitives_sleep_step_state, active) == 0xA8u &&
           offsetof(gomore_primitives_sleep_step_state, countdown) == 0xB0u &&
           offsetof(gomore_primitives_sleep_step_state,
                    local_time_window) == 0xB6u);
    memset(&sleep_step_state, 0, sizeof(sleep_step_state));
    const uint8_t local_hour_window[8] = {
        0u, 0u, 0u, 0u, 0u, 0u, 18u, 8u,
    };
    const uint8_t sleep_step_control[2] = {0u, 3u};
    gomore_primitives_civil_time sleep_step_civil;
    memset(&sleep_step_civil, 0, sizeof(sleep_step_civil));
    bool sleep_step_civil_updated = false;
    assert(gomore_primitives_sleep_step_update(
        &sleep_step_state, 10u, sleep_step_control,
        UINT32_C(43230), 0, 0.0f, 40.0f, true,
        local_hour_window, &sleep_step_civil,
        &sleep_step_civil_updated));
    assert(sleep_step_civil_updated && sleep_step_civil.hour == 12u &&
           sleep_step_state.local_time_window == 1u &&
           sleep_step_state.active == 0u &&
           sleep_step_state.countdown == 1190u &&
           sleep_step_state.decimated_ring[(43230u / 10u) % 90u] == 40u &&
           sleep_step_state.minute_accumulator.valid_count == 1);

    const uint8_t sleep_step_bypass_civil[2] = {1u, 1u};
    sleep_step_civil.timestamp = UINT32_C(0xA5A5A5A5);
    assert(gomore_primitives_sleep_step_update(
        &sleep_step_state, 10u, sleep_step_bypass_civil,
        UINT32_C(43240), 0, 1.0f, 5.0f, false,
        local_hour_window, &sleep_step_civil,
        &sleep_step_civil_updated));
    assert(!sleep_step_civil_updated &&
           sleep_step_civil.timestamp == UINT32_C(0xA5A5A5A5) &&
           sleep_step_state.active == 1u &&
           sleep_step_state.countdown == 290u);
    sleep_step_state.activity_latch = 1u;
    const uint8_t sleep_step_preserve_countdown[2] = {1u, 0u};
    assert(gomore_primitives_sleep_step_update(
        &sleep_step_state, 300u, sleep_step_preserve_countdown,
        UINT32_C(43540), 0, -1.0f, -1.0f, true,
        local_hour_window, &sleep_step_civil,
        &sleep_step_civil_updated));
    assert(sleep_step_state.active == 1u &&
           sleep_step_state.countdown == 0u);
    assert(!gomore_primitives_sleep_step_update(
        &sleep_step_state, 0u, sleep_step_control, 0u, 0,
        0.0f, 0.0f, false, local_hour_window, NULL,
        &sleep_step_civil_updated));

    uint8_t sleep_stage_state[0xB7];
    memset(sleep_stage_state, 0, sizeof(sleep_stage_state));
    gomore_primitives_sleep_stage_decision sleep_stage_decision;
    memset(&sleep_stage_decision, UINT8_C(0xA5),
           sizeof(sleep_stage_decision));
    sleep_stage_state[0xB4u] = 1u;
    assert(gomore_primitives_sleep_stage_decide(
        sleep_stage_state, sizeof(sleep_stage_state), 1000u, 0u, 0u,
        0u, false, 0.0f, &sleep_stage_decision));
    assert(sleep_stage_decision.stage == 1u &&
           sleep_stage_decision.transition == 4u &&
           sleep_stage_decision.reason == 5u &&
           sleep_stage_decision.adjustment == 0);
    sleep_stage_state[0xB4u] = 0u;
    store_u32_fixture(&sleep_stage_state[0xB0u], 1u);
    assert(gomore_primitives_sleep_stage_decide(
        sleep_stage_state, sizeof(sleep_stage_state), 1000u, 0u, 0u,
        1u, false, 0.0f, &sleep_stage_decision));
    assert(sleep_stage_decision.stage == 1u &&
           sleep_stage_decision.transition == 0u &&
           sleep_stage_decision.reason == 7u);
    store_u32_fixture(&sleep_stage_state[0xB0u], 0u);
    assert(gomore_primitives_sleep_stage_decide(
        sleep_stage_state, sizeof(sleep_stage_state), 1000u, 0u, 0u,
        0u, true, 0.0f, &sleep_stage_decision));
    assert(sleep_stage_decision.stage == 0u &&
           sleep_stage_decision.reason == 6u);
    assert(gomore_primitives_sleep_stage_decide(
        sleep_stage_state, sizeof(sleep_stage_state), 1000u, 601u, 0u,
        0u, false, 0.0f, &sleep_stage_decision));
    assert(sleep_stage_decision.reason == 3u &&
           sleep_stage_decision.adjustment == -10);
    assert(gomore_primitives_sleep_stage_decide(
        sleep_stage_state, sizeof(sleep_stage_state), UINT32_C(0xA8C0),
        0u, 0u, 1u, false, 0.0f, &sleep_stage_decision));
    assert(sleep_stage_decision.stage == 0u &&
           sleep_stage_decision.transition == 1u &&
           sleep_stage_decision.reason == 8u);
    sleep_stage_state[0xA8u] = 1u;
    assert(gomore_primitives_sleep_stage_decide(
        sleep_stage_state, sizeof(sleep_stage_state), 1000u, 0u, 0u,
        0u, false, 0.0f, &sleep_stage_decision));
    assert(sleep_stage_decision.reason == 4u &&
           sleep_stage_decision.adjustment == -15);
    sleep_stage_state[0xA8u] = 0u;
    for (size_t index = 0u; index < 15u; ++index) {
        store_u32_fixture(&sleep_stage_state[index * 4u],
                          UINT32_C(0x3F800000));
        sleep_stage_state[0x48u + index] = 50u;
    }
    store_u32_fixture(&sleep_stage_state[0xACu], 0u);
    assert(gomore_primitives_sleep_stage_decide(
        sleep_stage_state, sizeof(sleep_stage_state), 1000u, 0u, 0u,
        0u, false, 1.0f, &sleep_stage_decision));
    assert(sleep_stage_decision.stage == 1u &&
           sleep_stage_decision.transition == 2u &&
           sleep_stage_decision.reason == 0u);
    memset(&sleep_stage_state[0x48u], 100, 15u);
    assert(gomore_primitives_sleep_stage_decide(
        sleep_stage_state, sizeof(sleep_stage_state), 1000u, 0u, 0u,
        0u, false, 1.0f, &sleep_stage_decision));
    assert(sleep_stage_decision.stage == 0u &&
           sleep_stage_decision.reason == 2u);
    memset(&sleep_stage_state[0x48u], 50, 15u);
    for (size_t index = 0u; index < 15u; ++index) {
        store_u32_fixture(&sleep_stage_state[index * 4u], 0u);
    }
    assert(gomore_primitives_sleep_stage_decide(
        sleep_stage_state, sizeof(sleep_stage_state), 120u, 0u, 0u,
        1u, false, 0.0f, &sleep_stage_decision));
    assert(sleep_stage_decision.stage == 0u &&
           sleep_stage_decision.transition == 1u &&
           sleep_stage_decision.reason == 1u);
    assert(!gomore_primitives_sleep_stage_decide(
        sleep_stage_state, sizeof(sleep_stage_state) - 1u,
        0u, 0u, 0u, 0u, false, 0.0f, &sleep_stage_decision));

    gomore_primitives_sleep_cycle_state sleep_cycle_state;
    gomore_primitives_sleep_cycle_input sleep_cycle_input;
    gomore_primitives_sleep_interval_result sleep_cycle_output;
    assert(sizeof(sleep_cycle_state) == 0x138u &&
           offsetof(gomore_primitives_sleep_cycle_state,
                    last_decision) == 0xB8u &&
           offsetof(gomore_primitives_sleep_cycle_state,
                    current) == 0xC0u &&
           offsetof(gomore_primitives_sleep_cycle_state,
                    previous_descriptor) == 0xE8u &&
           offsetof(gomore_primitives_sleep_cycle_state,
                    previous_interval) == 0x110u &&
           offsetof(gomore_primitives_sleep_cycle_state,
                    policy) == 0x130u);

    initialize_sleep_cycle_fixture(
        &sleep_cycle_state, &sleep_cycle_input, &sleep_cycle_output);
    sleep_cycle_input.elapsed_seconds = 10u;
    sleep_cycle_input.current_time = UINT32_C(36000);
    assert(gomore_primitives_sleep_cycle_update(
        &sleep_cycle_state, &sleep_cycle_input, &sleep_cycle_output));
    const uint8_t *sleep_cycle_step_bytes =
        (const uint8_t *)&sleep_cycle_state.step;
    assert(load_u32_fixture(&sleep_cycle_step_bytes[0xA4u]) == 0u &&
           sleep_cycle_state.step.active == 0u &&
           sleep_cycle_state.step.activity_latch == 0u &&
           sleep_cycle_state.step.countdown == 290u &&
           sleep_cycle_state.step.local_time_window == 1u &&
           sleep_cycle_state.last_decision.stage == 0u &&
           sleep_cycle_state.last_decision.transition == 0u &&
           sleep_cycle_state.last_decision.reason == 7u &&
           sleep_cycle_state.current.statistics.observations == 1u &&
           sleep_cycle_state.current.statistics.lower_count == 9u &&
           sleep_cycle_state.current.statistics.upper_count == 9u &&
           sleep_cycle_output.flags == 0u &&
           sleep_cycle_output.auxiliary == 7u);
    assert(load_u32_fixture(&sleep_cycle_step_bytes[0xACu]) == 36000u);

    initialize_sleep_cycle_fixture(
        &sleep_cycle_state, &sleep_cycle_input, &sleep_cycle_output);
    ((uint8_t *)&sleep_cycle_state.step)[0xB4u] = 1u;
    sleep_cycle_input.current_time = 1000u;
    sleep_cycle_output.flags = 4u;
    assert(gomore_primitives_sleep_cycle_update(
        &sleep_cycle_state, &sleep_cycle_input, &sleep_cycle_output));
    assert(sleep_cycle_state.last_decision.stage == 1u &&
           sleep_cycle_state.last_decision.transition == 4u &&
           sleep_cycle_state.last_decision.reason == 5u &&
           ((const uint8_t *)&sleep_cycle_state.step)[0xB4u] == 0u &&
           sleep_cycle_state.current.descriptor.start == 1000u &&
           sleep_cycle_state.current.statistics.observations == 1u &&
           sleep_cycle_state.current.descriptor.type == 2u &&
           sleep_cycle_state.current.descriptor.profile == 4u &&
           sleep_cycle_state.previous_descriptor.reserved == 1000u &&
           sleep_cycle_output.flags == 3u &&
           sleep_cycle_output.auxiliary == 5u);

    initialize_sleep_cycle_fixture(
        &sleep_cycle_state, &sleep_cycle_input, &sleep_cycle_output);
    for (size_t index = 0u; index < 15u; ++index) {
        sleep_cycle_state.step.minute_accumulator
            .minute_zero_fraction[index] = 1.0f;
        sleep_cycle_state.step.decimated_ring[index] = 50u;
    }
    sleep_cycle_input.current_time = 1000u;
    sleep_cycle_input.minute_sample = 1.0f;
    sleep_cycle_input.ring_sample = 50.0f;
    sleep_cycle_output.flags = 4u;
    assert(gomore_primitives_sleep_cycle_update(
        &sleep_cycle_state, &sleep_cycle_input, &sleep_cycle_output));
    assert(sleep_cycle_state.last_decision.stage == 1u &&
           sleep_cycle_state.last_decision.transition == 2u &&
           sleep_cycle_state.last_decision.reason == 0u &&
           sleep_cycle_state.current.descriptor.start == 1000u &&
           sleep_cycle_state.current.statistics.positive_count == 1u &&
           sleep_cycle_state.current.statistics.mean == 50.0f &&
           sleep_cycle_state.current.statistics.mean_count == 1u &&
           sleep_cycle_state.current.descriptor.type == 2u &&
           sleep_cycle_state.current.descriptor.profile == 2u &&
           sleep_cycle_output.flags == 3u &&
           sleep_cycle_output.auxiliary == 0u);

    initialize_sleep_cycle_fixture(
        &sleep_cycle_state, &sleep_cycle_input, &sleep_cycle_output);
    sleep_cycle_state.last_decision.stage = 1u;
    sleep_cycle_state.current.interval_source.start = 1000u;
    sleep_cycle_state.current.interval_source.count = 10u;
    sleep_cycle_state.current.interval_source.sum = 4;
    sleep_cycle_state.current.interval_source.metric = 50.0f;
    sleep_cycle_state.current.interval_source.type = 2u;
    sleep_cycle_input.current_time = 2000u;
    sleep_cycle_input.ring_sample = 50.0f;
    sleep_cycle_output.flags = 4u;
    assert(gomore_primitives_sleep_cycle_update(
        &sleep_cycle_state, &sleep_cycle_input, &sleep_cycle_output));
    assert(sleep_cycle_state.last_decision.stage == 0u &&
           sleep_cycle_state.last_decision.transition == 1u &&
           sleep_cycle_state.last_decision.reason == 1u &&
           sleep_cycle_output.start == 1000u &&
           sleep_cycle_output.end == 1990u &&
           sleep_cycle_output.source_start == 1000u &&
           sleep_cycle_output.source_end == 2000u &&
           sleep_cycle_output.clamp_start == 1000u &&
           sleep_cycle_output.flags == 12u &&
           sleep_cycle_output.auxiliary == 1u &&
           sleep_cycle_output.status == 2u &&
           memcmp(&sleep_cycle_state.previous_interval,
                  &sleep_cycle_output, sizeof(sleep_cycle_output)) == 0 &&
           sleep_cycle_state.current.interval_descriptor.start == 2000u &&
           sleep_cycle_state.current.statistics.observations == 1u &&
           sleep_cycle_state.current.statistics.mean == 50.0f &&
           sleep_cycle_state.current.statistics.mean_count == 1u &&
           sleep_cycle_state.current.interval_descriptor.type == 3u &&
           sleep_cycle_state.current.interval_descriptor.profile == 1u);

    initialize_sleep_cycle_fixture(
        &sleep_cycle_state, &sleep_cycle_input, &sleep_cycle_output);
    store_u32_fixture(
        &((uint8_t *)&sleep_cycle_state.step)[0xACu], 100u);
    sleep_cycle_input.current_time = 1000u;
    sleep_cycle_input.input_active = true;
    assert(gomore_primitives_sleep_cycle_update(
        &sleep_cycle_state, &sleep_cycle_input, &sleep_cycle_output));
    sleep_cycle_step_bytes = (const uint8_t *)&sleep_cycle_state.step;
    assert(load_u32_fixture(&sleep_cycle_step_bytes[0xA4u]) == 1000u &&
           load_u32_fixture(&sleep_cycle_step_bytes[0xACu]) == 0u &&
           sleep_cycle_state.step.active == 1u &&
           sleep_cycle_state.step.activity_latch == 1u &&
           sleep_cycle_state.last_decision.reason == 4u &&
           sleep_cycle_state.last_decision.adjustment == -5 &&
           sleep_cycle_output.flags == 0u &&
           sleep_cycle_output.auxiliary == 4u);

    const gomore_primitives_sleep_cycle_state sleep_cycle_state_before =
        sleep_cycle_state;
    const gomore_primitives_sleep_interval_result sleep_cycle_output_before =
        sleep_cycle_output;
    assert(!gomore_primitives_sleep_cycle_update(
        &sleep_cycle_state, NULL, &sleep_cycle_output));
    assert(memcmp(&sleep_cycle_state, &sleep_cycle_state_before,
                  sizeof(sleep_cycle_state)) == 0 &&
           memcmp(&sleep_cycle_output, &sleep_cycle_output_before,
                  sizeof(sleep_cycle_output)) == 0);
    assert(!gomore_primitives_sleep_cycle_update(
        NULL, &sleep_cycle_input, &sleep_cycle_output));
    assert(!gomore_primitives_sleep_cycle_update(
        &sleep_cycle_state, &sleep_cycle_input, NULL));

    assert(!gomore_primitives_state_window_predicate(false, 0u, 0u,
                                                     false, false));
    assert(gomore_primitives_state_window_predicate(false, 0u, 0u,
                                                    true, false));
    assert(!gomore_primitives_state_window_predicate(true, 400u, 100u,
                                                     true, false));
    assert(gomore_primitives_state_window_predicate(true, 401u, 100u,
                                                    false, true));

    uint8_t key[64];
    size_t written = 0u;
    assert(gomore_primitives_key_or_cached_copy(
        key, sizeof(key), false, NULL, 0u, UINT32_C(0x01234567),
        UINT32_C(0x89ABCDEF), UINT32_C(0xA1B2C3D4), &written));
    assert(written == 24u);
    assert(memcmp(key, "a1b2c3d40123456789abcdef", 25u) == 0);
    const uint8_t cached[4] = {9u, 8u, 7u, 6u};
    assert(gomore_primitives_key_or_cached_copy(
        key, sizeof(key), true, cached, sizeof(cached), 0u, 0u, 0u,
        &written));
    assert(written == 4u && memcmp(key, cached, 4u) == 0);

    uint8_t slot_state = 4u;
    gomore_primitives_slot_state_transition(&slot_state, 2u, true);
    assert(slot_state == 4u);
    gomore_primitives_slot_state_transition(&slot_state, 5u, true);
    assert(slot_state == 1u);
    slot_state = 3u;
    gomore_primitives_slot_state_transition(&slot_state, 2u, false);
    assert(slot_state == 3u);
    slot_state = 2u;
    gomore_primitives_slot_state_transition(&slot_state, 5u, false);
    assert(slot_state == 5u);

    uint8_t blob[64];
    uint8_t blob_cache[64];
    uint8_t seed = 3u;
    memset(blob_cache, UINT8_C(0x5A), sizeof(blob_cache));
    assert(gomore_primitives_copy_key_blob(
               blob, sizeof(blob), false, NULL, load_blob, &seed) == 0x40);
    assert(blob[0] == 3u && blob[63] == 66u);
    assert(gomore_primitives_copy_key_blob(
               blob, sizeof(blob), true, blob_cache, NULL, NULL) == 0x40);
    assert(blob[63] == UINT8_C(0x5A));

    memset(&g_auth_setup_trace, 0, sizeof(g_auth_setup_trace));
    g_auth_setup_trace.apply_status = -7;
    const uint32_t auth_timestamp = UINT32_C(0x12345678);
    gomore_primitives_auth_setup_configuration auth_setup = {
        .device_id_0 = UINT32_C(0x01234567),
        .device_id_1 = UINT32_C(0x89ABCDEF),
        .address_word = UINT32_C(0xA1B2C3D4),
        .pkey_loader = load_blob,
        .pkey_loader_context = &seed,
        .timestamp = auth_timestamp_fixture,
        .timestamp_context = (void *)&auth_timestamp,
        .apply = auth_apply_fixture,
    };
    int32_t auth_status = 99;
    assert(gomore_primitives_auth_parameters_setup(
        &auth_setup, &auth_status));
    assert(auth_status == -7 && g_auth_setup_trace.timestamp_calls == 1u &&
           g_auth_setup_trace.apply_calls == 1u &&
           g_auth_setup_trace.device_uuid_length == 24u &&
           g_auth_setup_trace.timestamp == auth_timestamp &&
           memcmp(g_auth_setup_trace.device_uuid,
                  "a1b2c3d40123456789abcdef", 25u) == 0 &&
           g_auth_setup_trace.key[0] == 3u &&
           g_auth_setup_trace.key[63] == 66u);
    static const uint8_t cached_uuid[] = "cached-uuid";
    auth_setup.device_uuid_cache_valid = true;
    auth_setup.device_uuid_cache = cached_uuid;
    auth_setup.device_uuid_cache_length = sizeof(cached_uuid) - 1u;
    auth_setup.pkey_cache_valid = true;
    auth_setup.pkey_cache = blob_cache;
    g_auth_setup_trace.apply_status = 0;
    assert(gomore_primitives_auth_parameters_setup(
        &auth_setup, &auth_status));
    assert(auth_status == 0 && g_auth_setup_trace.apply_calls == 2u &&
           g_auth_setup_trace.device_uuid_length == 11u &&
           memcmp(g_auth_setup_trace.device_uuid, cached_uuid,
                  sizeof(cached_uuid)) == 0 &&
           g_auth_setup_trace.key[63] == UINT8_C(0x5A));
    auth_setup.pkey_cache_valid = false;
    auth_setup.pkey_cache = NULL;
    auth_setup.pkey_loader = fail_blob_load;
    g_auth_setup_trace.timestamp_calls = 0u;
    g_auth_setup_trace.apply_calls = 0u;
    auth_status = 77;
    assert(gomore_primitives_auth_parameters_setup(
        &auth_setup, &auth_status));
    assert(auth_status == -1 && g_auth_setup_trace.timestamp_calls == 0u &&
           g_auth_setup_trace.apply_calls == 0u);
    auth_setup.apply = NULL;
    auth_status = 88;
    assert(!gomore_primitives_auth_parameters_setup(
        &auth_setup, &auth_status));
    assert(auth_status == 88);

    uint8_t sdk_auth_key[64];
    for (size_t index = 0u; index < sizeof(sdk_auth_key); index += 4u) {
        memcpy(&sdk_auth_key[index], "QUFB", 4u);
    }
    static const uint8_t sdk_device_uuid[] =
        "a1b2c3d40123456789abcdef";
    const gomore_primitives_auth_parameters sdk_parameters = {
        .key = sdk_auth_key,
        .device_uuid = sdk_device_uuid,
        .device_uuid_length = 24u,
        .timestamp = UINT32_C(0x12345678),
    };
    uint8_t decrypt_keys[2][GOMORE_PRIMITIVES_SDK_AUTH_KEY_BYTES] = {{0u}};
    sdk_auth_trace sdk_trace = {
        .plaintexts = {"one,two,three,four", "unused"},
        .accepted_attempt = 0,
        .parser_results = {10, 11, 12, 13},
        .validator_results = {1, 2, 1},
    };
    gomore_primitives_sdk_auth_configuration sdk_configuration = {
        .decrypt_keys = {decrypt_keys[0], decrypt_keys[1]},
        .decrypt_context = &sdk_trace,
        .decrypt = sdk_auth_decrypt_fixture,
        .match_context = &sdk_trace,
        .message_matches = sdk_auth_match_fixture,
        .dispatch_context = &sdk_trace,
        .parse_fields = {
            sdk_auth_parse_fixture, sdk_auth_parse_fixture,
            sdk_auth_parse_fixture, sdk_auth_parse_fixture,
        },
        .validate_fields = {
            sdk_auth_validate_fixture, sdk_auth_validate_fixture,
            sdk_auth_validate_fixture,
        },
    };
    gomore_primitives_sdk_auth_status sdk_status;
    memset(&sdk_status, UINT8_C(0xA5), sizeof(sdk_status));
    int32_t sdk_result = 99;
    assert(gomore_primitives_sdk_auth_parse(
        &sdk_parameters, &sdk_configuration, &sdk_status, &sdk_result));
    assert(sdk_result == 11 && sdk_status.error == 0 &&
           sdk_trace.decrypt_calls == 1u && sdk_trace.parser_calls == 4u &&
           sdk_trace.validator_calls == 3u &&
           memcmp(sdk_trace.parser_tokens[0], "one", 4u) == 0 &&
           memcmp(sdk_trace.parser_tokens[3], "four", 5u) == 0 &&
           memcmp(sdk_trace.validator_tokens[1], "two", 4u) == 0 &&
           memcmp(sdk_trace.normalized_uuid, "0123456789ABCDEF", 17u) == 0 &&
           sdk_trace.normalized_uuid_length == 16u &&
           sdk_trace.timestamp == UINT32_C(0x12345678));

    memset(&sdk_trace, 0, sizeof(sdk_trace));
    sdk_trace.plaintexts[0] = "bad,data,for,key";
    sdk_trace.plaintexts[1] = "a,b,c,d";
    sdk_trace.accepted_attempt = 1;
    assert(gomore_primitives_sdk_auth_parse(
        &sdk_parameters, &sdk_configuration, &sdk_status, &sdk_result));
    assert(sdk_result == 0 && sdk_status.error == 0 &&
           sdk_trace.decrypt_calls == 2u && sdk_trace.parser_calls == 4u);

    memset(&sdk_trace, 0, sizeof(sdk_trace));
    sdk_trace.plaintexts[0] = "bad,data,for,key";
    sdk_trace.plaintexts[1] = "wrong,field,count";
    sdk_trace.accepted_attempt = -1;
    assert(gomore_primitives_sdk_auth_parse(
        &sdk_parameters, &sdk_configuration, &sdk_status, &sdk_result));
    assert(sdk_result == -1002 && sdk_status.error == -1002 &&
           sdk_trace.decrypt_calls == 2u && sdk_trace.parser_calls == 0u);

    memset(&sdk_trace, 0, sizeof(sdk_trace));
    sdk_trace.plaintexts[0] = "a,b,c,d";
    sdk_trace.plaintexts[1] = "unused";
    sdk_trace.accepted_attempt = 0;
    sdk_trace.parser_results[2] = -7;
    assert(gomore_primitives_sdk_auth_parse(
        &sdk_parameters, &sdk_configuration, &sdk_status, &sdk_result));
    assert(sdk_result == -7 && sdk_trace.parser_calls == 3u &&
           sdk_trace.validator_calls == 2u);

    gomore_primitives_auth_parameters short_uuid_parameters = sdk_parameters;
    short_uuid_parameters.device_uuid_length = 5u;
    memset(&sdk_status, UINT8_C(0xA5), sizeof(sdk_status));
    sdk_result = 99;
    assert(gomore_primitives_sdk_auth_parse(
        &short_uuid_parameters, &sdk_configuration, &sdk_status, &sdk_result));
    assert(sdk_result == -1005 && sdk_status.error == -1);
    sdk_result = 77;
    assert(!gomore_primitives_sdk_auth_parse(
        &sdk_parameters, NULL, &sdk_status, &sdk_result));
    assert(sdk_result == 77);

    tier2_trace tier2 = {0};
    active_tier2_trace = &tier2;
    uint8_t stage_source[32];
    for (size_t index = 0u; index < sizeof(stage_source); ++index) {
        stage_source[index] = (uint8_t)index;
    }
    assert(gomore_primitives_stage_32_and_consume(
        1u, 2u, stage_source, sizeof(stage_source), 4u, 5u,
        consume_stage) == 0);
    assert(tier2.consume_calls == 1u &&
           memcmp(tier2.staged, stage_source, sizeof(stage_source)) == 0);

    const float mean_values[4] = {1.0f, 2.0f, 3.0f, 6.0f};
    assert(gomore_primitives_mean(mean_values, 4u) == 3.0f);
    assert(gomore_primitives_mean(NULL, 0u) == 0.0f);
    const float argmax_values[4] = {5.0f, 2.0f, 5.0f, 1.0f};
    assert(gomore_primitives_argmax_from_zero(argmax_values, 4u) == 2);
    const float negative_values[2] = {-1.0f, -2.0f};
    assert(gomore_primitives_argmax_from_zero(negative_values, 2u) == 1);

    uint8_t provider_state[0x2E0];
    memset(provider_state, UINT8_C(0xA5), sizeof(provider_state));
    assert(gomore_primitives_reset_provider_state(
        provider_state, sizeof(provider_state), true, set_mode,
        release_state, &tier2, initialize_state));
    assert(tier2.mode_calls == 1u && tier2.mode == 4u &&
           tier2.mode_value == 0u && tier2.release_calls == 1u &&
           tier2.init_calls == 1u && tier2.init_mode == 1u);
    for (size_t index = 0u; index < sizeof(provider_state); ++index) {
        assert(provider_state[index] == 0u);
    }

    const uint8_t plausible[4] = {50u, 1u, 150u, 80u};
    assert(gomore_primitives_sample_plausible(plausible));
    const uint8_t implausible[4] = {10u, 1u, 150u, 80u};
    assert(!gomore_primitives_sample_plausible(implausible));
    const uint8_t health_sample[12] = {
        50u, 1u, 150u, 80u, 0x34u, 0x12u,
        0u, 0u, 0x9Cu, 0xFFu, 0u, 0u};
    float health_features[7] = {0.0f};
    assert(gomore_primitives_health_sample_features(
               health_sample, health_features) == 1u);
    assert(health_features[0] == 50.0f && health_features[1] == 1.0f &&
           health_features[2] == 150.0f && health_features[3] == 80.0f &&
           health_features[4] == 4660.0f && health_features[5] == -1.0f &&
           health_features[6] == -100.0f);
    uint8_t invalid_health_sample[12];
    memcpy(invalid_health_sample, health_sample, sizeof(invalid_health_sample));
    invalid_health_sample[1] = 2u;
    assert(gomore_primitives_health_sample_features(
               invalid_health_sample, health_features) == 0u);
    assert(health_features[1] == 0.0f);
    gomore_primitives_scaled_sample_state scaled_sample_state;
    memset(&scaled_sample_state, 0, sizeof(scaled_sample_state));
    scaled_sample_state.recent[0] = 100u;
    scaled_sample_state.recent[1] = 200u;
    scaled_sample_state.recent[2] = 300u;
    scaled_sample_state.recent[3] = 400u;
    scaled_sample_state.recent[4] = 500u;
    scaled_sample_state.recent_count = 5u;
    scaled_sample_state.capture_enabled = true;
    scaled_sample_publish_calls = 0u;
    assert(gomore_primitives_scaled_sample_publish(
        &scaled_sample_state, true, publish_scaled_sample));
    assert(scaled_sample_state.capture_count == 1u &&
           scaled_sample_state.captured[0] == 30u &&
           scaled_sample_publish_calls == 1u && scaled_sample_topic == 9u &&
           scaled_sample_length == 8u && scaled_sample_payload[0] == 3u &&
           scaled_sample_payload[1] == 0u && scaled_sample_payload[7] == 0u);
    scaled_sample_state.recent_count = 4u;
    assert(gomore_primitives_scaled_sample_publish(
        &scaled_sample_state, false, NULL));
    assert(scaled_sample_state.capture_count == 1u &&
           scaled_sample_publish_calls == 1u);

    memset(&scaled_sample_state, UINT8_C(0xA5),
           sizeof(scaled_sample_state));
    scaled_sample_state.capture_enabled = true;
    scaled_sample_state.capture_count = 7u;
    scaled_sample_state.captured[0] = UINT16_C(1234);
    assert(gomore_primitives_temperature_measurement_begin(
        &scaled_sample_state));
    assert(scaled_sample_state.recent_count == 0u &&
           scaled_sample_state.attempt_count == 0u &&
           scaled_sample_state.measurement_active &&
           scaled_sample_state.capture_enabled &&
           scaled_sample_state.capture_count == 7u &&
           scaled_sample_state.captured[0] == UINT16_C(1234));
    assert(gomore_primitives_temperature_measurement_step(
               &scaled_sample_state, UINT16_C(29999)) ==
           GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_CONTINUE);
    assert(scaled_sample_state.attempt_count == 1u &&
           scaled_sample_state.recent_count == 0u);
    assert(gomore_primitives_temperature_measurement_step(
               &scaled_sample_state, UINT16_C(30000)) ==
           GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_CONTINUE);
    assert(gomore_primitives_temperature_measurement_step(
               &scaled_sample_state, UINT16_C(30300)) ==
           GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_CONTINUE);
    assert(scaled_sample_state.recent_count == 2u);
    assert(gomore_primitives_temperature_measurement_step(
               &scaled_sample_state, UINT16_C(30301)) ==
           GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_CONTINUE);
    assert(scaled_sample_state.recent_count == 0u);
    assert(gomore_primitives_temperature_measurement_step(
               &scaled_sample_state, UINT16_C(50000)) ==
           GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_CONTINUE);
    assert(gomore_primitives_temperature_measurement_step(
               &scaled_sample_state, UINT16_C(49900)) ==
           GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_CONTINUE);
    assert(gomore_primitives_temperature_measurement_step(
               &scaled_sample_state, UINT16_C(49800)) ==
           GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_CONTINUE);
    assert(gomore_primitives_temperature_measurement_step(
               &scaled_sample_state, UINT16_C(49750)) ==
           GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_CONTINUE);
    assert(gomore_primitives_temperature_measurement_step(
               &scaled_sample_state, UINT16_C(49700)) ==
           GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_COMPLETE);
    assert(scaled_sample_state.recent_count == 5u &&
           scaled_sample_state.attempt_count == 9u);

    assert(gomore_primitives_temperature_measurement_begin(
        &scaled_sample_state));
    for (uint8_t attempt = 0u; attempt < 30u; ++attempt) {
        assert(gomore_primitives_temperature_measurement_step(
                   &scaled_sample_state, UINT16_C(1000)) ==
               GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_CONTINUE);
    }
    assert(gomore_primitives_temperature_measurement_step(
               &scaled_sample_state, UINT16_C(40000)) ==
           GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_TIMEOUT);
    assert(scaled_sample_state.attempt_count == 31u &&
           scaled_sample_state.recent_count == 0u);
    assert(gomore_primitives_temperature_measurement_step(
               NULL, UINT16_C(40000)) ==
           GOMORE_PRIMITIVES_TEMPERATURE_MEASUREMENT_INVALID);
    const uint16_t stable_samples[12] = {
        1110u, 1000u, 1100u, 1010u, 1090u, 1020u,
        1080u, 1030u, 1070u, 1040u, 1060u, 1050u};
    uint16_t stable_unscaled = UINT16_MAX;
    assert(gomore_primitives_stable_trimmed_median(
               stable_samples, 12u, &stable_unscaled) == 105u);
    assert(stable_unscaled == 1055u);
    const uint16_t unstable_samples[12] = {
        0u, 0u, 0u, 0u, 0u, 0u, 0u, 0u, 0u, 1000u, 1000u, 1000u};
    assert(gomore_primitives_stable_trimmed_median(
               unstable_samples, 12u, &stable_unscaled) == 0u);
    assert(stable_unscaled == 0u);
    stable_unscaled = UINT16_MAX;
    assert(gomore_primitives_stable_trimmed_median(
               stable_samples, 11u, &stable_unscaled) == 0u &&
           stable_unscaled == 0u);

    uint8_t time_record[0x31];
    memset(time_record, 0, sizeof(time_record));
    int32_t sync_state = 0;
    assert(gomore_primitives_stamp_time_record(
        time_record, sizeof(time_record), read_time, read_offset, read_sync,
        &sync_state));
    assert(time_record[0] == UINT8_C(0x78) &&
           time_record[3] == UINT8_C(0x12));
    assert(time_record[4] == UINT8_C(0xCD) &&
           time_record[5] == UINT8_C(0xAB));
    assert(time_record[0x1D] == 1u && time_record[0x30] == 1u);
    sync_state = 1;
    assert(gomore_primitives_stamp_time_record(
        time_record, sizeof(time_record), read_time, read_offset, read_sync,
        &sync_state));
    assert(time_record[0x30] == 0u);

    assert(gomore_primitives_clamp_hysteresis(0u, 100u) == 1u);
    assert(gomore_primitives_clamp_hysteresis(98u, 100u) == 101u);
    assert(gomore_primitives_clamp_hysteresis(80u, 100u) == 80u);
    uint8_t parameter_state[0x20F6];
    memset(parameter_state, 0, sizeof(parameter_state));
    const uint32_t accepted = 7u;
    assert(gomore_primitives_parameter_commit(
               parameter_state, sizeof(parameter_state), 7u,
               validate_parameter, (void *)&accepted) == 0u);
    assert(parameter_state[0x20F5] == 7u);
    assert(gomore_primitives_parameter_commit(
               parameter_state, sizeof(parameter_state), 8u,
               validate_parameter, (void *)&accepted) == UINT32_C(0x40));

    memset(records, 0, sizeof(records));
    records[2u * GOMORE_PRIMITIVES_RECORD_STRIDE] = UINT8_C(0x05);
    assert(gomore_primitives_records_any_bit2(records, sizeof(records)));
    assert(!gomore_primitives_records_any_bit4(records, sizeof(records)));
    records[2u * GOMORE_PRIMITIVES_RECORD_STRIDE] = UINT8_C(0x11);
    assert(gomore_primitives_records_any_bit4(records, sizeof(records)));
    records[2u * GOMORE_PRIMITIVES_RECORD_STRIDE] = UINT8_C(0x09);
    assert(gomore_primitives_records_any_bit3(records, sizeof(records)));
    records[2u * GOMORE_PRIMITIVES_RECORD_STRIDE] = UINT8_C(0x03);
    assert(gomore_primitives_records_any_bit1(records, sizeof(records)));
    records[2u * GOMORE_PRIMITIVES_RECORD_STRIDE] = UINT8_C(0x10);
    assert(!gomore_primitives_records_any_bit4(records, sizeof(records)));

    const float quantized_min_values[4] = {5.9f, 4.2f, 4.8f, 3.1f};
    assert(gomore_primitives_quantized_argmin(
               quantized_min_values, 0u, 4u) == 3);
    assert(gomore_primitives_quantized_argmin(
               quantized_min_values, 3u, 2u) == -1);
    const float differences[5] = {0.0f, 2.0f, 3.0f, 9.0f, 10.0f};
    assert(gomore_primitives_max_difference_index(
               differences, 0u, 4u) == 2u);

    float median_values[4] = {9.0f, 1.0f, 5.0f, 3.0f};
    float statistic = 0.0f;
    assert(gomore_primitives_median(median_values, 4u, sort_values,
                                    compare_float, &statistic));
    assert(statistic == 4.0f);
    float median_odd[3] = {3.0f, 8.0f, 1.0f};
    assert(gomore_primitives_median(median_odd, 3u, sort_values,
                                    compare_float, &statistic));
    assert(statistic == 3.0f);
    const float deviations[2] = {1.0f, 3.0f};
    assert(gomore_primitives_standard_deviation(
        deviations, 2u, square_value, sqrt_passthrough, &statistic));
    assert(statistic == 2.0f);
    assert(gomore_primitives_logistic_score(
        0.5f, 2.0f, 64.0f, 0.25f, exp_one, &statistic));
    assert(statistic == 18.85f);

    uint8_t modulo_record[0x2F];
    memset(modulo_record, 0, sizeof(modulo_record));
    assert(gomore_primitives_modulo5_record(
        modulo_record, sizeof(modulo_record), UINT8_C(0xFF),
        UINT8_C(0xFF)));
    assert(modulo_record[0x29] == 1u && modulo_record[0x2D] == 1u &&
           modulo_record[0x28] == 1u);
    for (unsigned index = 0u; index < 4u; ++index) {
        assert(gomore_primitives_modulo5_record(
            modulo_record, sizeof(modulo_record), 2u, 3u));
    }
    assert(modulo_record[0x28] == 5u);
    assert(gomore_primitives_modulo5_record(
        modulo_record, sizeof(modulo_record), 2u, 3u));
    assert(modulo_record[0x2A] == 3u && modulo_record[0x2E] == 2u);

    uint8_t window_records[3u * 16u];
    memset(window_records, 0, sizeof(window_records));
    window_records[2] = 10u;
    window_records[16u + 0u] = 30u;
    window_records[16u + 2u] = 40u;
    window_records[32u + 0u] = 50u;
    window_records[32u + 2u] = 60u;
    uint8_t window_count = 3u;
    assert(gomore_primitives_compact_25_windows(
        window_records, 3u, &window_count, 21u));
    assert(window_count == 2u);
    assert(window_records[0] == 5u && window_records[2] == 15u);
    assert(window_records[16u] == 25u && window_records[18u] == 35u);

    uint8_t decimated_ring[90];
    memset(decimated_ring, 7, sizeof(decimated_ring));
    assert(gomore_primitives_decimated_ring_write(
        bits_float(UINT32_C(0x42200000)), decimated_ring, 100u, 140u));
    assert(decimated_ring[14] == 40u);
    assert(decimated_ring[5] == 7u && decimated_ring[6] == 7u &&
           decimated_ring[7] == 7u && decimated_ring[8] == 7u &&
           decimated_ring[9] == 7u && decimated_ring[10] == 7u &&
           decimated_ring[11] == 7u && decimated_ring[12] == 7u &&
           decimated_ring[13] == 7u);
    assert(gomore_primitives_decimated_ring_write(
        -1.0f, decimated_ring, 100u, 150u));
    assert(decimated_ring[15] == 0u);

    const uint8_t auth_pattern[] = "1839052049009318";
    const uint8_t auth_record[] = "1839052049009318,alpha,beta,gamma";
    assert(gomore_primitives_csv4_prefix_compare(
               auth_pattern, sizeof(auth_pattern) - 1u,
               auth_record, sizeof(auth_record) - 1u) == 0);
    const uint8_t prefix_record[] = "1839052049009318-extra,a,b,c";
    assert(gomore_primitives_csv4_prefix_compare(
               auth_pattern, sizeof(auth_pattern) - 1u,
               prefix_record, sizeof(prefix_record) - 1u) == 0);
    const uint8_t mismatch_record[] = "1839052049009319,a,b,c";
    assert(gomore_primitives_csv4_prefix_compare(
               auth_pattern, sizeof(auth_pattern) - 1u,
               mismatch_record, sizeof(mismatch_record) - 1u) != 0);
    const uint8_t short_csv_record[] = "1839052049009318,a,b";
    assert(gomore_primitives_csv4_prefix_compare(
               auth_pattern, sizeof(auth_pattern) - 1u,
               short_csv_record, sizeof(short_csv_record) - 1u) == -1);
    const uint8_t leading_delimiter[] = ",abc,x,y";
    const uint8_t abc_pattern[] = "abc";
    assert(gomore_primitives_csv4_prefix_compare(
               abc_pattern, sizeof(abc_pattern) - 1u,
               leading_delimiter, sizeof(leading_delimiter) - 1u) == 0);
    uint8_t overlong_record[64];
    memset(overlong_record, 'x', sizeof(overlong_record));
    overlong_record[50] = ',';
    overlong_record[52] = ',';
    overlong_record[54] = ',';
    assert(gomore_primitives_csv4_prefix_compare(
               abc_pattern, sizeof(abc_pattern) - 1u,
               overlong_record, sizeof(overlong_record)) == -1);

    uint8_t sleep_engine[0x20F0];
    memset(sleep_engine, UINT8_C(0xA5), sizeof(sleep_engine));
    sleep_engine[0x3E8] = 1u;
    memset(&g_sleep_tensor_trace, 0, sizeof(g_sleep_tensor_trace));
    assert(gomore_primitives_sleep_engine_open(
        sleep_engine, sizeof(sleep_engine), construct_sleep_tensor));
    assert(g_sleep_tensor_trace.calls == 1u &&
           g_sleep_tensor_trace.pool == &sleep_engine[0x55C] &&
           g_sleep_tensor_trace.pool_length == 0x1B90u &&
           g_sleep_tensor_trace.rank == 2u &&
           g_sleep_tensor_trace.dimensions[0] == 1u &&
           g_sleep_tensor_trace.dimensions[1] == 90u &&
           g_sleep_tensor_trace.pool_was_clear);
    assert(sleep_engine[0x20EC] == 0x78u &&
           sleep_engine[0x20ED] == 0x56u &&
           sleep_engine[0x20EE] == 0x34u &&
           sleep_engine[0x20EF] == 0x12u);
    assert(sleep_engine[0x3E6] == 0u && sleep_engine[0x3E7] == 0u &&
           sleep_engine[0x3E8] == 1u && sleep_engine[0x3E9] == 0u &&
           sleep_engine[0x3EA] == 0u);
    for (size_t index = 0x2D6u; index < 0x3E6u; ++index) {
        assert(sleep_engine[index] == 0u);
    }
    for (size_t index = 0x554u; index < 0x55Cu; ++index) {
        assert(sleep_engine[index] == 0u);
    }
    assert(!gomore_primitives_sleep_engine_open(
        sleep_engine, sizeof(sleep_engine) - 1u, construct_sleep_tensor));
    assert(!gomore_primitives_sleep_engine_open(
        sleep_engine, sizeof(sleep_engine), NULL));

    uint8_t filter_history_state[0x6C0];
    memset(filter_history_state, 0, sizeof(filter_history_state));
    float *filter_history =
        (float *)(void *)&filter_history_state[0x2D8];
    for (size_t index = 0u; index < 250u; ++index) {
        filter_history[index] = (float)index;
    }
    float negated_input[25];
    for (size_t index = 0u; index < 25u; ++index) {
        negated_input[index] = (float)(index + 1u);
    }
    const unsigned filters_before = g_accelerometer_filter_calls;
    assert(gomore_primitives_shift_negated_filter_history(
        filter_history_state, sizeof(filter_history_state), negated_input,
        false, accelerometer_filter));
    assert(filter_history[0] == 25.0f && filter_history[224] == 249.0f &&
           filter_history[225] == 9.0f && filter_history[249] == -15.0f &&
           g_accelerometer_filter_calls == filters_before + 1u);
    assert(gomore_primitives_shift_negated_filter_history(
        filter_history_state, sizeof(filter_history_state), NULL,
        true, NULL));
    for (size_t index = 225u; index < 250u; ++index) {
        assert(filter_history[index] == 0.0f);
    }

    const gomore_primitives_log_config logger = {
        true, UINT16_C(1) << 2u, UINT32_C(1) << 2u,
        format_log_value, emit_log_message};
    memset(&g_log_trace, 0, sizeof(g_log_trace));
    assert(gomore_primitives_log_u32(
        &logger, 2u, 2u, "value:%u", UINT32_C(32)));
    assert(g_log_trace.format_calls == 1u && g_log_trace.emit_calls == 1u &&
           g_log_trace.value == 32u &&
           strcmp(g_log_trace.wrapper, "%s") == 0 &&
           strcmp(g_log_trace.message, "[GoMoRe]status\r\n") == 0);
    assert(!gomore_primitives_log_u32(
        &logger, 1u, 2u, "value:%u", UINT32_C(32)));

    uint8_t accelerometer_filters[0x140];
    memset(accelerometer_filters, 0, sizeof(accelerometer_filters));
    float axis_sources[3][7] = {
        {1.0f}, {2.0f}, {3.0f}};
    const float *axis_source_pointers[3] = {
        axis_sources[0], axis_sources[1], axis_sources[2]};
    float axis_destinations[3][25];
    float *axis_destination_pointers[3] = {
        axis_destinations[0], axis_destinations[1], axis_destinations[2]};
    uint8_t accelerometer_failed = UINT8_C(0xA5);
    uint32_t accelerometer_status = UINT32_C(0xFFFFFFFF);
    memset(&g_log_trace, 0, sizeof(g_log_trace));
    const unsigned resamples_before = g_accelerometer_resample_calls;
    assert(gomore_primitives_accelerometer_resample25(
        accelerometer_filters, sizeof(accelerometer_filters),
        axis_source_pointers, 3u, 7, axis_destination_pointers, 3u,
        &accelerometer_failed, &accelerometer_status,
        accelerometer_resample, accelerometer_filter, &logger));
    assert(accelerometer_status == 0u && accelerometer_failed == 0u &&
           g_accelerometer_resample_calls == resamples_before + 3u &&
           axis_destinations[0][0] == 11.0f &&
           axis_destinations[1][24] == 36.0f &&
           axis_destinations[2][0] == 13.0f &&
           g_log_trace.value == 0u);
    assert(gomore_primitives_accelerometer_resample25(
        accelerometer_filters, sizeof(accelerometer_filters),
        axis_source_pointers, 3u, 0, axis_destination_pointers, 3u,
        &accelerometer_failed, &accelerometer_status,
        accelerometer_resample, accelerometer_filter, &logger));
    assert(accelerometer_status == UINT32_C(0x20) &&
           accelerometer_failed == 1u && axis_destinations[0][0] == 0.0f &&
           g_log_trace.value == UINT32_C(0x20));
    float ppg_output[25];
    uint8_t ppg_failed = UINT8_C(0xA5);
    uint32_t ppg_status = UINT32_MAX;
    const unsigned ppg_resamples_before = g_accelerometer_resample_calls;
    assert(gomore_primitives_ppg_resample25(
        accelerometer_filters, sizeof(accelerometer_filters),
        axis_source_pointers, 3u, 2, 7, ppg_output,
        &ppg_failed, &ppg_status, accelerometer_resample,
        accelerometer_filter, &logger));
    assert(ppg_status == 0u && ppg_failed == 0u &&
           g_accelerometer_resample_calls == ppg_resamples_before + 1u &&
           ppg_output[0] == 5.5f && ppg_output[24] == 17.5f &&
           g_log_trace.value == 0u);
    assert(gomore_primitives_ppg_resample25(
        accelerometer_filters, sizeof(accelerometer_filters),
        axis_source_pointers, 3u, 2, 0, ppg_output,
        &ppg_failed, &ppg_status, accelerometer_resample,
        accelerometer_filter, &logger));
    assert(ppg_status == UINT32_C(0x40) && ppg_failed == 1u &&
           ppg_output[0] == 0.0f && g_log_trace.value == UINT32_C(0x40));
}
