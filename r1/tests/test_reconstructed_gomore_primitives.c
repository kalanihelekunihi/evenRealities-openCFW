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
}
