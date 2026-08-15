#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "gomore_primitives/gomore_primitives.h"

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

static void consume_stage(uintptr_t first, uintptr_t second,
                          const uint8_t staged[32], uintptr_t fourth,
                          uintptr_t fifth) {
    assert(first == 1u && second == 2u && fourth == 4u && fifth == 5u);
    ++active_tier2_trace->consume_calls;
    memcpy(active_tier2_trace->staged, staged,
           sizeof(active_tier2_trace->staged));
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
static uint8_t closure_allocation[0x23C];

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
           source_total == 50 && destination != NULL);
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

static float adapter_power10(float base, float exponent) {
    assert(base == 10.0f && exponent == 2.0f);
    return 100.0f;
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
    const uint8_t filtered_values[5] = {0u, 9u, 10u, 11u, 30u};
    assert(gomore_primitives_filtered_u8_mean(
               filtered_values, 5u, 10, 1) == 10);
    const float complex_left[2] = {2.0f, 3.0f};
    const float complex_right[2] = {4.0f, 5.0f};
    assert(gomore_primitives_complex_multiply(
        complex_left, complex_right, pair_output));
    assert(pair_output[0] == -7.0f && pair_output[1] == 22.0f);
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

    uint8_t mode_state[0x50];
    memset(mode_state, UINT8_C(0xA5), sizeof(mode_state));
    const float mode1_parameters[2] = {0.25f, 0.5f};
    assert(gomore_primitives_mode_state_configure(
        mode_state, sizeof(mode_state), 1u, 3u, mode1_parameters,
        closure_mode_lt2_initialize, NULL));
    assert(mode_state[0] == 3u && mode_state[0x30] == 0u &&
           mode_state[0x4F] == 0u &&
           active_closure_trace.mode_lt2_calls == 1u);
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
    const float mean5_values[5] = {1.0f, 2.0f, 3.0f, 4.0f, 5.0f};
    const float mean5_comparisons[5] = {0.0f, 2.0f, 3.0f, 4.0f, 5.0f};
    assert(gomore_primitives_thresholded_mean5(
               3.0f, mean5_values, mean5_comparisons) == 4.0f);
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
    const uint8_t interval_boundaries[3] = {0u, 4u, 10u};
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

    tier2_trace tier2 = {0};
    active_tier2_trace = &tier2;
    uint8_t stage_source[32];
    for (size_t index = 0u; index < sizeof(stage_source); ++index) {
        stage_source[index] = (uint8_t)index;
    }
    assert(gomore_primitives_stage_32_and_consume(
        1u, 2u, stage_source, sizeof(stage_source), 4u, 5u,
        consume_stage));
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
}
