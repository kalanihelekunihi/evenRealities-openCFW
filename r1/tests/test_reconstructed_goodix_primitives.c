#include <assert.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "goodix_primitives/goodix_primitives.h"

static unsigned dispatch_calls;
static unsigned hook_calls;
static unsigned release_calls;

static void state_handler(void *record) {
    uint32_t *words = record;
    ++dispatch_calls;
    words[1] = UINT32_C(0xA55A);
}

static int32_t initialize_device(uint16_t device_id) {
    return device_id == UINT16_C(0x1234) ? 0 : 7;
}

static void hook(void) {
    ++hook_calls;
}

typedef union {
    max_align_t alignment;
    uint8_t bytes[16384];
} aligned_arena;

typedef struct {
    aligned_arena arena;
    size_t used;
    size_t calls;
    size_t fail_after;
} allocation_trace;

static void *allocate_from_trace(void *context, size_t bytes) {
    allocation_trace *trace = context;
    if (trace->fail_after != 0u && trace->calls >= trace->fail_after) {
        return NULL;
    }
    const size_t alignment = sizeof(max_align_t);
    const size_t start = (trace->used + alignment - 1u) / alignment * alignment;
    if (start > sizeof(trace->arena.bytes) ||
            bytes > sizeof(trace->arena.bytes) - start) {
        return NULL;
    }
    trace->used = start + bytes;
    ++trace->calls;
    return &trace->arena.bytes[start];
}

static void release_to_trace(void *context, void *allocation) {
    allocation_trace *trace = context;
    assert(allocation != NULL);
    ++release_calls;
    ++trace->calls;
}

static float exp_fixture(float value) {
    (void)value;
    return 1.0f;
}

static int32_t add_one(int32_t value) {
    return value + 1;
}

static uint16_t low_half(uint32_t value) {
    return (uint16_t)value;
}

static int32_t initialize_ok(void) {
    return 0;
}

void test_reconstructed_goodix_primitives(void) {
    char version[32];
    memset(version, 'x', sizeof(version));
    assert(goodix_primitives_copy_preprocess_version(version,
                                                     sizeof(version)));
    assert(strcmp(version, "pre_pv_v1.1.0") == 0);
    memset(version, 'x', sizeof(version));
    assert(goodix_primitives_copy_preprocess_version(version, 5u));
    assert(memcmp(version, "pre_", 5u) == 0);
    assert(version[4] == '\0');
    assert(!goodix_primitives_copy_preprocess_version(version, 0u));
    assert(goodix_primitives_copy_process_version(version, sizeof(version)));
    assert(strcmp(version, "pv_v1.1.0") == 0);

    char dsp_version[23];
    assert(goodix_primitives_copy_dsp_version(
        dsp_version, sizeof(dsp_version)));
    assert(strcmp(dsp_version, "dsp_pv_v1.3.0_30234f22") == 0);
    char spo2_version[127];
    assert(goodix_primitives_build_spo2_version(
        spo2_version, sizeof(spo2_version), "gh3x2x-v2.23_7ecd2a"));
    static const char expected_spo2_version[] =
        "GH_SPO2_pre_pv_v2.1.10.0(gh3x2x-v2.23_7ecd2a)_nc_277e89de\n"
        "net_1f1cf98b\n"
        "dsp_pv_v1.3.0_30234f22\n"
        "dlCom_pre2exc_pv_v1.3.0_c00c91c9";
    assert(strcmp(spo2_version, expected_spo2_version) == 0);
    assert(!goodix_primitives_build_spo2_version(
        spo2_version, sizeof(spo2_version) - 1u,
        "gh3x2x-v2.23_7ecd2a"));
    assert(spo2_version[0] == '\0');

    const goodix_primitives_state_handler_fn handlers[7] = {
        state_handler, state_handler, state_handler, state_handler,
        state_handler, state_handler, state_handler,
    };
    uint32_t state[2] = {3u, 0u};
    assert(goodix_primitives_dispatch_state(state, handlers));
    assert(dispatch_calls == 1u && state[1] == UINT32_C(0xA55A));
    state[0] = 7u;
    assert(!goodix_primitives_dispatch_state(state, handlers));

    uint8_t record[GOODIX_PRIMITIVES_RECORD_BYTES];
    memset(record, UINT8_C(0x5A), sizeof(record));
    assert(goodix_primitives_record_initialize(record, sizeof(record)));
    assert(record[0] == 0u && record[1] == 0u &&
           record[2] == UINT8_C(0x5A));
    for (size_t index = 3u; index < sizeof(record); ++index) {
        assert(record[index] == UINT8_C(0xFF));
    }
    memset(record, UINT8_C(0xA5), sizeof(record));
    record[0] = 0u;
    assert(goodix_primitives_record_initialize_once(record, sizeof(record)));
    assert(record[1] == 1u && record[0x0B] == 1u && record[0x13] == 0u);
    record[0] = 2u;
    record[1] = 9u;
    assert(goodix_primitives_record_initialize_once(record, sizeof(record)));
    assert(record[1] == 9u);

    assert(goodix_primitives_initialize_device(UINT16_C(0x1234),
                                               initialize_device) == 0);
    assert(goodix_primitives_initialize_device(UINT16_C(1),
                                               initialize_device) == -1);
    assert(goodix_primitives_initialize_device(UINT16_C(1), NULL) == -1);

    uint32_t first = 0u;
    uint32_t second = 0u;
    goodix_primitives_select_fixed_pair(false, &first, &second);
    assert(first == UINT32_C(0x00ECCCCD));
    assert(second == UINT32_C(0x00A66666));
    goodix_primitives_select_fixed_pair(true, &first, &second);
    assert(first == UINT32_C(0x00F33333));
    assert(second == UINT32_C(0x00C00000));

    memset(record, UINT8_C(0xA5), sizeof(record));
    assert(goodix_primitives_reset_state_record(record, sizeof(record)));
    assert(record[0] == UINT8_C(0xFF) && record[1] == 0u);
    assert(record[0x0E] == 0u && record[0x0F] == 0u);
    for (size_t index = 0x14u; index < 0x18u; ++index) {
        assert(record[index] == 0u);
    }
    record[5] = 1u;
    record[6] = 2u;
    record[7] = 3u;
    assert(goodix_primitives_clear_state_flags(record, sizeof(record)));
    assert(record[5] == 0u && record[6] == 0u && record[7] == 0u);

    assert(!goodix_primitives_call_hook(NULL));
    assert(goodix_primitives_call_hook(hook));
    assert(hook_calls == 1u);
    assert(goodix_primitives_library_code() == UINT32_C(0x12F9));
    assert(goodix_primitives_constant_four() == 4u);
    assert(goodix_primitives_constant_one_a() == 1u);
    assert(goodix_primitives_constant_one_b() == 1u);

    static const uint32_t table_values[7] = {1u, 2u, 3u, 4u, 5u, 6u, 7u};
    const goodix_primitives_tables tables = {
        &table_values[0], &table_values[1], &table_values[2],
        &table_values[3], &table_values[4], &table_values[5],
        &table_values[6],
    };
    assert(goodix_primitives_table_9d640(&tables) == &table_values[0]);
    assert(goodix_primitives_table_a04cc(&tables) == &table_values[1]);
    assert(goodix_primitives_table_a50b0(&tables) == &table_values[2]);
    assert(goodix_primitives_table_a692c(&tables) == &table_values[3]);
    assert(goodix_primitives_table_ad1ac(&tables) == &table_values[4]);
    assert(goodix_primitives_table_ad13c(&tables) == &table_values[5]);
    assert(goodix_primitives_table_ad160(&tables) == &table_values[6]);
    assert(goodix_primitives_table_9d640(NULL) == NULL);

    allocation_trace allocation = {0};
    goodix_primitives_buffer_record *buffer_record = NULL;
    assert(goodix_primitives_buffer_record_create(
        &buffer_record, allocate_from_trace, &allocation));
    assert(buffer_record != NULL && buffer_record->buffer != NULL);
    assert(allocation.calls == 2u);
    for (size_t index = 0u; index < 0x40u; ++index) {
        assert(buffer_record->buffer[index] == 0u);
    }
    assert(buffer_record->flag_05 == 0u && buffer_record->flag_06 == 0u);

    const int32_t integers[5] = {-8, 7, 7, 4, 9};
    int32_t maximum = 0;
    size_t maximum_index = 0u;
    assert(goodix_primitives_integer_max_index(
        integers, 5u, &maximum, &maximum_index));
    assert(maximum == 9 && maximum_index == 4u);

    char dlcom_version[40];
    assert(goodix_primitives_copy_dlcom_version(
        dlcom_version, sizeof(dlcom_version)));
    assert(strcmp(dlcom_version,
                  "dlCom_pre2exc_pv_v1.3.0_c00c91c9") == 0);

    uint32_t window_values[3] = {0u, 0u, 0u};
    goodix_primitives_word_window window = {window_values, 0u, 3u};
    assert(goodix_primitives_word_window_push(&window, 1u));
    assert(goodix_primitives_word_window_push(&window, 2u));
    assert(goodix_primitives_word_window_push(&window, 3u));
    assert(goodix_primitives_word_window_push(&window, 4u));
    assert(window.count == 3u && window_values[0] == 2u &&
           window_values[1] == 3u && window_values[2] == 4u);

    float logistic = 0.0f;
    assert(goodix_primitives_logistic_score(
        5.0f, 4.0f, 2.0f, 3.0f, exp_fixture, &logistic));
    assert(logistic == 50.0f);

    goodix_primitives_noop_a();
    goodix_primitives_noop_b();
    assert(goodix_primitives_zero_a() == 0);
    assert(goodix_primitives_zero_b() == 0);
    const uint32_t pair[2] = {7u, 19u};
    assert(goodix_primitives_second_word(pair) == 19u);
    assert(goodix_primitives_transformed_differs(4, add_one));
    static const struct {
        uint32_t input;
        uint32_t encoded;
    } integrity_cases[] = {
        {UINT32_C(0x00000000), UINT32_C(0x00000000)},
        {UINT32_C(0x00000001), UINT32_C(0x00000000)},
        {UINT32_C(0x00000002), UINT32_C(0x00000003)},
        {UINT32_C(0x00000003), UINT32_C(0x00000003)},
        {UINT32_C(0x00000004), UINT32_C(0x00000005)},
        {UINT32_C(0x00000005), UINT32_C(0x00000005)},
        {UINT32_C(0x00000006), UINT32_C(0x00000006)},
        {UINT32_C(0x00000007), UINT32_C(0x00000006)},
        {UINT32_C(0x00123456), UINT32_C(0x00123457)},
        {UINT32_C(0x00ABCDEF), UINT32_C(0x00ABCDEE)},
        {UINT32_C(0x80FFFFFF), UINT32_C(0x80FFFFFF)},
    };
    for (size_t index = 0u;
            index < sizeof(integrity_cases) / sizeof(integrity_cases[0]);
            ++index) {
        assert(goodix_primitives_integrity_encode(
                   integrity_cases[index].input) ==
               integrity_cases[index].encoded);
        assert(goodix_primitives_integrity_invalid(
                   integrity_cases[index].input) ==
               (integrity_cases[index].input !=
                integrity_cases[index].encoded));
    }
    static const struct {
        uint16_t input;
        uint32_t five_ten;
        uint32_t six_nine;
    } packed_cases[] = {
        {UINT16_C(0x0000), UINT32_C(0x00000000), UINT32_C(0x00000000)},
        {UINT16_C(0x8000), UINT32_C(0x80000000), UINT32_C(0x80000000)},
        {UINT16_C(0x0001), UINT32_C(0x33800000), UINT32_C(0x2C000000)},
        {UINT16_C(0x3C00), UINT32_C(0x3F800000), UINT32_C(0x3F000000)},
        {UINT16_C(0x4000), UINT32_C(0x40000000), UINT32_C(0x40000000)},
        {UINT16_C(0xFFFF), UINT32_C(0xC7FFE000), UINT32_C(0xCFFFC000)},
    };
    for (size_t index = 0u;
            index < sizeof(packed_cases) / sizeof(packed_cases[0]); ++index) {
        assert(goodix_primitives_packed_5_10_to_f32_bits(
                   packed_cases[index].input) == packed_cases[index].five_ten);
        assert(goodix_primitives_packed_6_9_to_f32_bits(
                   packed_cases[index].input) == packed_cases[index].six_nine);
    }
    const uint32_t transform_source[3] = {
        UINT32_C(0x12345678), UINT32_C(0xABCDEF01), UINT32_C(0x0000BEEF),
    };
    uint16_t transform_output[3] = {0u, 0u, 0u};
    assert(goodix_primitives_u32_to_u16_transform(
        transform_output, transform_source, 3u, low_half));
    assert(transform_output[0] == UINT16_C(0x5678));
    assert(transform_output[1] == UINT16_C(0xEF01));
    assert(transform_output[2] == UINT16_C(0xBEEF));
    assert(!goodix_primitives_u32_to_u16_transform(
        NULL, transform_source, 3u, low_half));
    int32_t transformed = 8;
    assert(goodix_primitives_transform_in_place(&transformed, add_one));
    assert(transformed == 9);
    assert(goodix_primitives_initialize_status(initialize_ok) == 0);
    assert(goodix_primitives_initialize_status(NULL) == -1);

    float float_values[4] = {1.0f, 2.0f, 3.0f, 4.0f};
    goodix_primitives_float_buffer float_buffer = {
        float_values, 2u, 4u,
    };
    assert(goodix_primitives_is_evenly_divisible(12u, 4u));
    assert(!goodix_primitives_is_evenly_divisible(12u, 0u));
    assert(!goodix_primitives_float_buffer_full(&float_buffer));
    float_buffer.count = 4u;
    assert(goodix_primitives_float_buffer_full(&float_buffer));
    assert(goodix_primitives_float_buffer_get(&float_buffer, 2u, -1.0f) ==
           3.0f);
    assert(goodix_primitives_float_buffer_get(&float_buffer, 4u, -1.0f) ==
           -1.0f);
    assert(goodix_primitives_unsigned_power(2.0f, 5u) == 32.0f);
    assert(goodix_primitives_centered_i8(-1) == INT8_MIN);
    assert(goodix_primitives_centered_i8(128) == 0);
    assert(goodix_primitives_centered_i8(256) == INT8_MAX);
    assert(goodix_primitives_float_sum(float_values, 4u) == 10.0f);

    int32_t counter = 2;
    assert(goodix_primitives_decrement_counter(&counter) && counter == 1);
    goodix_primitives_tensor_descriptor descriptor;
    assert(goodix_primitives_tensor_descriptor_initialize(
               &descriptor, 1u, 2u, 3u, 4u, float_values) == float_values);
    assert(descriptor.element_bytes == 4u && descriptor.batches == 1u &&
           descriptor.rows == 2u && descriptor.columns == 3u);
    assert(goodix_primitives_filter_code(5u) == 5u);
    assert(goodix_primitives_filter_code(2u) == 0u);

    union {
        float value;
        uint32_t word;
    } last_bits = {6.25f};
    uint32_t last_values[2] = {0u, last_bits.word};
    goodix_primitives_word_window last_window = {last_values, 2u, 2u};
    assert(goodix_primitives_word_window_last(&last_window, 0u) ==
           last_bits.word);
    assert(goodix_primitives_word_window_count(&last_window) == 2u);
    uint16_t bound = 0u;
    assert(goodix_primitives_store_version_qualifier(&bound));
    assert(bound == UINT16_C(0x636E));

    assert(goodix_primitives_copy_process_version_v1_1(
        version, sizeof(version)));
    assert(strcmp(version, "pv_v1.1.0") == 0);
    assert(goodix_primitives_copy_process_version_v1_0(
        version, sizeof(version)));
    assert(strcmp(version, "pv_v1.0.0") == 0);
    uint32_t reversed = 0u;
    assert(goodix_primitives_reverse_low_bits(UINT32_C(0x0D), 4u,
                                              &reversed));
    assert(reversed == UINT32_C(0x0B));
    float mean = 0.0f;
    assert(goodix_primitives_float_mean(float_values, 4u, &mean));
    assert(mean == 2.5f);
    assert(goodix_primitives_sum_squares(float_values, 4u) == 30.0f);
    const float other_values[4] = {2.0f, 3.0f, 4.0f, 5.0f};
    assert(goodix_primitives_dot_product(float_values, other_values, 4u) ==
           40.0f);

    uint8_t indexed_records[64];
    for (size_t index = 0u; index < sizeof(indexed_records); ++index) {
        indexed_records[index] = (uint8_t)index;
    }
    uint8_t indexed_copy[32] = {0};
    assert(goodix_primitives_copy_indexed_record(
               indexed_records, 2u, 1, indexed_copy) == 0);
    assert(memcmp(indexed_copy, &indexed_records[32], 32u) == 0);
    assert(goodix_primitives_copy_indexed_record(
               indexed_records, 2u, 2, indexed_copy) ==
           INT32_C(0x10000003));
    assert(goodix_primitives_round_nearest(2.5f) == 3);
    assert(goodix_primitives_round_nearest(-2.5f) == -3);

    uint8_t packed_records[8] = {0u, 0u, 0u, 1u, 0u, 0u, 0u, 2u};
    assert(goodix_primitives_transform_packed24_lsb(
        packed_records, sizeof(packed_records), add_one));
    assert(packed_records[3] == 2u && packed_records[7] == 3u);
    assert(goodix_primitives_visit_packed24(
        packed_records, sizeof(packed_records), add_one));
    uint8_t words[4] = {0x12u, 0x34u, 0xABu, 0xCDu};
    assert(goodix_primitives_swap_u16_bytes(words, sizeof(words)));
    assert(words[0] == 0x34u && words[1] == 0x12u &&
           words[2] == 0xCDu && words[3] == 0xABu);

    const int32_t ranged[4] = {3, -7, 11, 2};
    int32_t high = 0;
    int32_t low = 0;
    int32_t range = 0;
    assert(goodix_primitives_i32_range(
        ranged, 4u, &high, &low, &range));
    assert(high == 11 && low == -7 && range == 18);

    uint8_t processing_source[76] = {0};
    uint8_t processing_record[96] = {0};
    processing_source[4] = 100u;
    assert(goodix_primitives_processing_record_initialize(
        processing_record, sizeof(processing_record), processing_source,
        sizeof(processing_source)));
    assert(processing_record[76] == 4u);
    assert(processing_record[80] == 5u);
    assert(processing_record[84] == 25u);
    assert(processing_record[88] == 1u);
    assert(processing_record[92] == 25u);

    uint8_t transition[7] = {0};
    assert(goodix_primitives_update_transition(
        transition, sizeof(transition), 0u, 1u));
    assert(transition[4] == 0u && transition[5] == 1u);
    transition[6] = 3u;
    assert(goodix_primitives_update_transition(
        transition, sizeof(transition), 1u, 1u));
    assert(transition[5] == 0u && transition[6] == 4u);

    float sorted[6] = {4.0f, 1.0f, 3.0f, 2.0f, 0.0f, 0.0f};
    assert(goodix_primitives_sort_floats(sorted, 4u));
    assert(sorted[0] == 1.0f && sorted[1] == 2.0f &&
           sorted[2] == 3.0f && sorted[3] == 4.0f);
    size_t sorted_count = 4u;
    assert(goodix_primitives_sorted_insert(
        sorted, &sorted_count, 6u, 2.5f));
    assert(sorted_count == 5u && sorted[2] == 2.5f && sorted[3] == 3.0f);
    assert(goodix_primitives_float_mean_or_zero(float_values, 4u) == 2.5f);
    assert(goodix_primitives_float_mean_or_zero(NULL, 0u) == 0.0f);
    assert(goodix_primitives_word_window_full(&last_window));

    const int16_t signed_values[4] = {8, -2, 4, -6};
    int16_t signed_mean = 0;
    size_t signed_minimum_index = 0u;
    assert(goodix_primitives_i16_mean(
        signed_values, 4u, &signed_mean));
    assert(signed_mean == 1);
    assert(goodix_primitives_i16_min_index(
        signed_values, 4u, &signed_minimum_index));
    assert(signed_minimum_index == 3u);
    float extremum = 0.0f;
    size_t extremum_index = 0u;
    assert(goodix_primitives_float_min_index(
        float_values, 4u, &extremum, &extremum_index));
    assert(extremum == 1.0f && extremum_index == 0u);
    assert(goodix_primitives_float_max_index(
        float_values, 4u, &extremum, &extremum_index));
    assert(extremum == 4.0f && extremum_index == 3u);

    void *released = indexed_records;
    assert(goodix_primitives_release_and_clear(
        &released, release_to_trace, &allocation));
    assert(released == NULL && release_calls == 1u);
    assert(goodix_primitives_release_if_present(
               indexed_copy, release_to_trace, &allocation) == 0);
    assert(release_calls == 2u);

    allocation_trace heap = {0};
    void *records_allocation = NULL;
    void *scratch_allocation = NULL;
    assert(goodix_primitives_allocate_record_pair(
        2u, &records_allocation, &scratch_allocation,
        allocate_from_trace, &heap));
    assert(records_allocation != NULL && scratch_allocation != NULL);
    assert(goodix_primitives_release_context_pair_vector() ==
           (uintptr_t)&goodix_primitives_release_context_pair);

    const int32_t quartic_record[] = {0, 0, 1, 2, 3, 4, 5};
    const float quartic_value =
        goodix_primitives_quartic_evaluate(2.0f, quartic_record);
    assert(quartic_value > 0.0056999f && quartic_value < 0.0057001f);
    assert(goodix_primitives_quartic_evaluate(2.0f, NULL) == 0.0f);

    const float peak_values[] = {0.0f, 1.0f, 3.0f, 1.0f, 0.0f,
                                 2.0f, 4.0f, 2.0f, 0.0f};
    int32_t peak_indices[2] = {-1, -1};
    float selected_peaks[2] = {-1.0f, -1.0f};
    int32_t peak_count = -1;
    assert(goodix_primitives_peak_select(
        0.5f, peak_values, 9, 1, 8, 1, 2, peak_indices,
        selected_peaks, &peak_count));
    assert(peak_count == 2);
    assert(peak_indices[0] == 6 && peak_indices[1] == 2);
    assert(selected_peaks[0] == 4.0f && selected_peaks[1] == 3.0f);
    assert(!goodix_primitives_peak_select(
        0.5f, peak_values, 9, 1, 10, 1, 2, peak_indices,
        selected_peaks, &peak_count));

    assert(goodix_primitives_release_context_pair(
               records_allocation, scratch_allocation,
               release_to_trace, &heap) == 0);
    assert(release_calls == 4u);

    allocation_trace descriptors = {0};
    goodix_primitives_buffer_descriptor buffer_descriptor;
    assert(goodix_primitives_buffer_descriptor_initialize(
        &buffer_descriptor, NULL, 4u, sizeof(uint32_t),
        allocate_from_trace, &descriptors));
    assert(buffer_descriptor.data != NULL &&
           buffer_descriptor.count == 0u &&
           buffer_descriptor.capacity == 4u);
    goodix_primitives_extended_descriptor extended_descriptor;
    assert(goodix_primitives_extended_descriptor_initialize(
        &extended_descriptor, NULL, 8u, sizeof(uint16_t), 7u,
        allocate_from_trace, &descriptors));
    assert(extended_descriptor.data != NULL &&
           extended_descriptor.count == 0u &&
           extended_descriptor.capacity == 8u &&
           extended_descriptor.auxiliary == 0u &&
           extended_descriptor.status == 0u &&
           extended_descriptor.flag == 7u);
    goodix_primitives_float_descriptor float_descriptor;
    assert(goodix_primitives_float_descriptor_initialize(
        &float_descriptor, float_values, 4u, 3u,
        allocate_from_trace, &descriptors));
    assert(float_descriptor.data == float_values &&
           float_descriptor.count == 4u &&
           float_descriptor.capacity == 4u &&
           float_descriptor.flag == 3u &&
           float_descriptor.status == 0u &&
           float_descriptor.auxiliary == 0u &&
           float_descriptor.reserved == 0u);

    void *release_first = indexed_records;
    void *release_second = indexed_copy;
    assert(goodix_primitives_release_two_and_clear(
        &release_first, &release_second, release_to_trace, &allocation));
    assert(release_first == NULL && release_second == NULL);
    assert(release_calls == 6u);
    assert(goodix_primitives_release_two(
        indexed_records, indexed_copy, release_to_trace, &allocation));
    assert(release_calls == 8u);
    uint8_t fill[7] = {0};
    assert(goodix_primitives_byte_fill(UINT8_C(0xA6), fill,
                                       sizeof(fill)));
    for (size_t index = 0u; index < sizeof(fill); ++index) {
        assert(fill[index] == UINT8_C(0xA6));
    }

    uint32_t primary[4] = {1u, 2u, 3u, 4u};
    uint32_t secondary[4] = {5u, 6u, 7u, 8u};
    goodix_primitives_dual_buffer_descriptor dual;
    assert(goodix_primitives_dual_buffer_descriptor_initialize(
        &dual, 11u, 12u, primary, 4u, secondary, 4u, 3u, 13u));
    assert(dual.field_00 == 11u && dual.field_04 == 12u &&
           dual.primary == primary && dual.secondary == secondary &&
           dual.count == 3u && dual.field_14 == 13u);
    for (size_t index = 0u; index < 4u; ++index) {
        assert(primary[index] == 0u && secondary[index] == 0u);
    }
    assert(!goodix_primitives_dual_buffer_descriptor_initialize(
        &dual, 11u, 12u, primary, 3u, secondary, 4u, 3u, 13u));

    float supplied_storage[3] = {1.0f, 2.0f, 3.0f};
    goodix_primitives_float_storage float_storage;
    assert(goodix_primitives_float_storage_initialize(
        &float_storage, supplied_storage, 3u, NULL, NULL));
    assert(float_storage.values == supplied_storage &&
           float_storage.count == 3u && float_storage.capacity == 3u &&
           float_storage.limit == 3u && supplied_storage[0] == 1.0f);
    assert(goodix_primitives_float_storage_initialize(
        &float_storage, NULL, 5u, allocate_from_trace, &descriptors));
    assert(float_storage.values != NULL && float_storage.count == 0u &&
           float_storage.capacity == 5u && float_storage.limit == 0u);
    for (size_t index = 0u; index < 5u; ++index) {
        assert(float_storage.values[index] == 0.0f);
    }

    goodix_primitives_pair_buffer pair_buffer;
    assert(goodix_primitives_pair_buffer_initialize(
        &pair_buffer, 6u, UINT32_C(0x12345678),
        allocate_from_trace, &descriptors));
    assert(pair_buffer.count == 3u && pair_buffer.records != NULL &&
           pair_buffer.metadata == UINT32_C(0x12345678));
    const uint8_t *pair_bytes = (const uint8_t *)pair_buffer.records;
    for (size_t index = 0u; index < 24u; ++index) {
        assert(pair_bytes[index] == 0u);
    }

    allocation_trace lifecycle = {0};
    goodix_primitives_channel_state channel_state;
    const unsigned releases_before_channel = release_calls;
    assert(goodix_primitives_channel_state_initialize(
        &channel_state, 5u, 25u, allocate_from_trace,
        release_to_trace, &lifecycle));
    assert(channel_state.history.capacity == 25u &&
           channel_state.window.capacity == 17u &&
           channel_state.filtered.capacity == 25u &&
           channel_state.scalar.capacity == 1u &&
           channel_state.primary_buckets.capacity == 25u &&
           channel_state.secondary_buckets.capacity == 5u);
    assert(goodix_primitives_channel_state_release(
        &channel_state, release_to_trace, &lifecycle));
    assert(release_calls == releases_before_channel + 6u &&
           channel_state.history.data == NULL &&
           channel_state.secondary_buckets.data == NULL);
    assert(!goodix_primitives_channel_state_initialize(
        &channel_state, 0u, 25u, allocate_from_trace,
        release_to_trace, &lifecycle));

    allocation_trace session_lifecycle = {0};
    goodix_primitives_session_state session_state;
    const unsigned releases_before_session = release_calls;
    assert(goodix_primitives_session_state_initialize(
        &session_state, 5u, 25u, allocate_from_trace,
        release_to_trace, &session_lifecycle));
    assert(session_state.primary.window.capacity == 17u &&
           session_state.secondary.secondary_buckets.capacity == 5u &&
           session_state.tail_a.capacity == 125u &&
           session_state.tail_d.capacity == 125u &&
           session_state.tail_d.flag == 1u);
    assert(goodix_primitives_session_state_release(
        &session_state, release_to_trace, &session_lifecycle));
    assert(release_calls == releases_before_session + 16u &&
           session_state.primary.history.data == NULL &&
           session_state.tail_d.data == NULL);

    allocation_trace failing_lifecycle = {0};
    failing_lifecycle.fail_after = 1u;
    const unsigned releases_before_failure = release_calls;
    assert(!goodix_primitives_channel_state_initialize(
        &channel_state, 5u, 25u, allocate_from_trace,
        release_to_trace, &failing_lifecycle));
    assert(release_calls == releases_before_failure + 1u &&
           channel_state.history.data == NULL);

    allocation_trace owned_record_lifecycle = {0};
    goodix_primitives_owned_float_record *owned_record = NULL;
    const unsigned releases_before_owned_record = release_calls;
    assert(goodix_primitives_owned_float_record_create(
        &owned_record, 4u, 7u, allocate_from_trace,
        release_to_trace, &owned_record_lifecycle));
    assert(owned_record != NULL && owned_record->samples.capacity == 7u &&
           owned_record->samples.count == 0u &&
           owned_record->samples.flag == 1u);
    assert(goodix_primitives_owned_float_record_destroy(
        &owned_record, release_to_trace, &owned_record_lifecycle));
    assert(owned_record == NULL &&
           release_calls == releases_before_owned_record + 2u);

    allocation_trace record_array_lifecycle = {0};
    goodix_primitives_channel_record *channel_records = NULL;
    const unsigned releases_before_record_array = release_calls;
    assert(goodix_primitives_channel_record_array_create(
        &channel_records, 3u, true, UINT8_C(0x5A), allocate_from_trace,
        release_to_trace, &record_array_lifecycle));
    for (size_t index = 0u; index < 3u; ++index) {
        assert(channel_records[index].status == 0u &&
               channel_records[index].lower == 0.0f &&
               channel_records[index].upper == 0.0f &&
               channel_records[index].samples.capacity == 15u &&
               channel_records[index].samples.flag == 1u &&
               channel_records[index].tag == UINT8_C(0x5A));
    }
    assert(goodix_primitives_channel_record_array_destroy(
        &channel_records, 3u, true, release_to_trace,
        &record_array_lifecycle));
    assert(channel_records == NULL &&
           release_calls == releases_before_record_array + 4u);

    allocation_trace failing_record_array = {0};
    failing_record_array.fail_after = 2u;
    const unsigned releases_before_record_failure = release_calls;
    assert(!goodix_primitives_channel_record_array_create(
        &channel_records, 3u, true, 1u, allocate_from_trace,
        release_to_trace, &failing_record_array));
    assert(channel_records == NULL &&
           release_calls == releases_before_record_failure + 2u);

    allocation_trace aggregate_lifecycle = {0};
    goodix_primitives_session_aggregate aggregate;
    const unsigned releases_before_aggregate = release_calls;
    assert(goodix_primitives_session_aggregate_create(
        &aggregate, 5u, 25u, 5u, allocate_from_trace,
        release_to_trace, &aggregate_lifecycle));
    assert(aggregate.session != NULL && aggregate.pair != NULL &&
           aggregate.auxiliary.marker == 0u &&
           aggregate.auxiliary.full_rate.capacity == 125u &&
           aggregate.auxiliary.reduced_rate.capacity == 25u &&
           aggregate.pair->first.capacity == 20u &&
           aggregate.pair->second.capacity == 20u);
    assert(goodix_primitives_session_aggregate_destroy(
        &aggregate, release_to_trace, &aggregate_lifecycle));
    assert(aggregate.session == NULL && aggregate.pair == NULL &&
           release_calls == releases_before_aggregate + 22u);

    allocation_trace failing_aggregate = {0};
    failing_aggregate.fail_after = 1u;
    const unsigned releases_before_aggregate_failure = release_calls;
    assert(!goodix_primitives_session_aggregate_create(
        &aggregate, 5u, 25u, 5u, allocate_from_trace,
        release_to_trace, &failing_aggregate));
    assert(aggregate.session == NULL &&
           release_calls == releases_before_aggregate_failure + 1u);

    const unsigned releases_before_buffer_record = release_calls;
    assert(goodix_primitives_buffer_record_destroy(
        &buffer_record, release_to_trace, &allocation));
    assert(buffer_record == NULL &&
           release_calls == releases_before_buffer_record + 2u);

    /* 0x0006EB94 / 0x0006EB30: complete outer session lifecycle. */
    uint8_t outer_source[76] = {0};
    outer_source[0] = 2u;   /* record count */
    outer_source[4] = 125u; /* recovered geometry source */
    outer_source[28] = 1u;  /* channel-record array enabled */
    outer_source[32] = UINT8_C(0x5A);
    outer_source[71] = 4u;
    outer_source[72] = 7u;
    uint32_t outer_model[
        QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS];
    for (size_t index = 0u;
            index < QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS;
            ++index) {
        outer_model[index] = UINT32_C(0xC0000000) + (uint32_t)index;
    }
    quantized_runtime_providers outer_providers = {0};
    outer_providers.vector_36dcc = (uintptr_t)0x00036DCDu;
    outer_providers.run_76bdc = (uintptr_t)0x00076BDDu;
    outer_providers.run_85b9c = (uintptr_t)0x00085B9Du;
    outer_providers.vector_85dc4 = (uintptr_t)0x00085DC5u;
    outer_providers.vector_30534 = (uintptr_t)0x00030535u;
    quantized_runtime outer_runtime;
    quantized_runtime_initialize(&outer_runtime, &outer_providers);
    allocation_trace outer_trace = {0};
    goodix_primitives_outer_session *outer = NULL;
    const unsigned releases_before_outer = release_calls;
    assert(goodix_primitives_outer_session_create(
        &outer, outer_source, sizeof(outer_source), "pre_pv_v1.1.0",
        &outer_runtime, outer_model,
        QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS, 0x10000u,
        allocate_from_trace, release_to_trace, &outer_trace));
    assert(outer != NULL);
    assert(outer->processing_record[0] == 2u);
    assert(outer->processing_record[4] == 125u);
    assert(outer->processing_record[76] == 5u);
    assert(outer->processing_record[80] == 5u);
    assert(outer->processing_record[84] == 25u);
    assert(outer->processing_record[88] == 1u);
    assert(outer->processing_record[92] == 25u);
    assert(outer->record_pair.records != NULL);
    assert(outer->record_pair.scratch != NULL);
    assert(outer->aggregate.session != NULL);
    assert(outer->aggregate.pair != NULL);
    assert(outer->owned_float != NULL);
    assert(outer->owned_float->samples.capacity == 7u);
    assert(outer->buffer_record != NULL);
    assert(outer->model.instance != NULL);
    assert(outer->channel_records != NULL);
    assert(outer->channel_records[0].tag == UINT8_C(0x5A));
    assert(outer->channel_records[1].tag == UINT8_C(0x5A));
    assert(goodix_primitives_outer_session_destroy(
        &outer, release_to_trace, &outer_trace));
    assert(outer == NULL);
    assert(release_calls == releases_before_outer + 34u);

    allocation_trace rejected_outer = {0};
    assert(!goodix_primitives_outer_session_create(
        &outer, outer_source, sizeof(outer_source), "pre_pv_v1.0.0",
        &outer_runtime, outer_model,
        QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS, 0x10000u,
        allocate_from_trace, release_to_trace, &rejected_outer));
    assert(outer == NULL && rejected_outer.calls == 0u);

    allocation_trace failing_outer = {0};
    failing_outer.fail_after = 3u;
    const unsigned releases_before_outer_failure = release_calls;
    assert(!goodix_primitives_outer_session_create(
        &outer, outer_source, sizeof(outer_source), "pre_pv_v1.1.0",
        &outer_runtime, outer_model,
        QUANTIZED_RUNTIME_GOODIX_MODEL_INSTANCE_MODEL_WORDS, 0x10000u,
        allocate_from_trace, release_to_trace, &failing_outer));
    assert(outer == NULL);
    assert(release_calls == releases_before_outer_failure + 3u);
}
