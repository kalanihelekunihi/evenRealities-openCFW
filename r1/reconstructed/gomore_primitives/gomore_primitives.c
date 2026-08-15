/*
 * Clean-room implementation of complete GoMore-candidate functions in the R1
 * application image.  The implementation contains no model weights,
 * original executable bytes, absolute firmware pointers, or vendor source.
 */

#include "gomore_primitives/gomore_primitives.h"

static void clear_bytes(uint8_t *bytes, size_t count) {
    for (size_t index = 0u; index < count; ++index) {
        bytes[index] = 0u;
    }
}

static void store_u32_le(uint8_t *bytes, uint32_t value) {
    bytes[0] = (uint8_t)(value & UINT32_C(0xFF));
    bytes[1] = (uint8_t)((value >> 8) & UINT32_C(0xFF));
    bytes[2] = (uint8_t)((value >> 16) & UINT32_C(0xFF));
    bytes[3] = (uint8_t)((value >> 24) & UINT32_C(0xFF));
}

static uint16_t load_u16_le_early(const uint8_t *bytes) {
    return (uint16_t)((uint16_t)bytes[0] |
                      (uint16_t)((uint16_t)bytes[1] << 8u));
}

static void store_u16_le_early(uint8_t *bytes, uint16_t value) {
    bytes[0] = (uint8_t)(value & UINT16_C(0xFF));
    bytes[1] = (uint8_t)(value >> 8u);
}

static uint32_t load_u32_le(const uint8_t *bytes) {
    return (uint32_t)bytes[0] |
           (uint32_t)bytes[1] << 8u |
           (uint32_t)bytes[2] << 16u |
           (uint32_t)bytes[3] << 24u;
}

static uint32_t float_bits(float value) {
    union {
        float f;
        uint32_t u;
    } pun;
    pun.f = value;
    return pun.u;
}

static float bits_float(uint32_t value) {
    union {
        float f;
        uint32_t u;
    } pun;
    pun.u = value;
    return pun.f;
}

bool gomore_primitives_records_all_clear(const uint8_t *records,
                                         size_t record_bytes) {
    if (records == NULL ||
            record_bytes < GOMORE_PRIMITIVES_RECORD_COUNT *
                               GOMORE_PRIMITIVES_RECORD_STRIDE) {
        return false;
    }
    for (size_t index = 0u; index < GOMORE_PRIMITIVES_RECORD_COUNT; ++index) {
        if ((records[index * GOMORE_PRIMITIVES_RECORD_STRIDE] & 1u) != 0u) {
            return false;
        }
    }
    return true;
}

void gomore_primitives_record5_initialize(uint32_t record[5],
                                          bool add_record_offset,
                                          uint32_t field4,
                                          uint32_t field8,
                                          uint32_t base) {
    if (record == NULL) {
        return;
    }
    record[1] = field4;
    record[2] = field8;
    record[3] = base;
    record[4] = add_record_offset ? base + UINT32_C(0x14) : 0u;
}

void gomore_primitives_span_initialize(uint32_t record[2],
                                       bool add_record_offset,
                                       uint32_t base) {
    if (record == NULL) {
        return;
    }
    record[0] = base;
    record[1] = add_record_offset ? base + UINT32_C(0x14) : 0u;
}

bool gomore_primitives_clear_two_records(void *record, size_t length) {
    if (record == NULL || length < 0x28u) {
        return false;
    }
    clear_bytes(record, 0x14u);
    clear_bytes((uint8_t *)record + 0x14u, 0x14u);
    return true;
}

bool gomore_primitives_fill_missing_pair(float values[2]) {
    if (values == NULL) {
        return false;
    }
    values[0] = -1.0f;
    values[1] = -1.0f;
    return true;
}

bool gomore_primitives_clear_90(void *record, size_t length) {
    if (record == NULL || length < 0x5Au) {
        return false;
    }
    clear_bytes(record, 0x5Au);
    return true;
}

bool gomore_primitives_prepare_and_score(
    const gomore_primitives_score_providers *providers,
    uintptr_t first, uintptr_t second, uintptr_t third, uintptr_t fourth,
    void *workspace, float *output) {
    if (providers == NULL || providers->prepare == NULL ||
            providers->score == NULL || workspace == NULL || output == NULL) {
        return false;
    }
    providers->prepare(first, second, third, fourth, workspace);
    *output = providers->score(workspace);
    return true;
}

bool gomore_primitives_float_in_encoded_range(float value) {
    return float_bits(value) + UINT32_C(0xBDE00000) <=
           UINT32_C(0x01500000);
}

bool gomore_primitives_scale(float factor, const float *source,
                             float *destination, size_t count) {
    if ((source == NULL || destination == NULL) && count != 0u) {
        return false;
    }
    for (size_t index = 0u; index < count; ++index) {
        destination[index] = source[index] * factor;
    }
    return true;
}

bool gomore_primitives_callback_record_initialize(uint8_t *record,
                                                  size_t length,
                                                  uint32_t field_b8,
                                                  uint32_t field_bc) {
    if (record == NULL || length < GOMORE_PRIMITIVES_CALLBACK_RECORD_BYTES) {
        return false;
    }
    record[0xB4u] = 0u;
    store_u32_le(&record[0xB8u], field_b8);
    store_u32_le(&record[0xBCu], field_bc);
    return true;
}

bool gomore_primitives_sort_float_subrange(
    float *values, size_t value_count, size_t first, size_t last,
    gomore_primitives_qsort_fn qsort_provider,
    gomore_primitives_compare_fn compare) {
    if (values == NULL || qsort_provider == NULL || compare == NULL ||
            first > last || last >= value_count) {
        return false;
    }
    qsort_provider(&values[first], (last - first) + 1u, sizeof(*values),
                   compare);
    return true;
}

int32_t gomore_primitives_max_index(const float *values, uint32_t count,
                                    gomore_primitives_max_index_fn provider) {
    if (provider == NULL || (values == NULL && count != 0u)) {
        return -1;
    }
    return provider(values, count);
}

bool gomore_primitives_set_second_word(uint32_t record[2], uint32_t value) {
    if (record == NULL) {
        return false;
    }
    record[1] = value;
    return true;
}

uint32_t gomore_primitives_size_736(void) {
    return UINT32_C(0x2E0);
}

uint32_t gomore_primitives_size_14816(void) {
    return UINT32_C(0x39E0);
}

uint32_t gomore_primitives_return_zero(void) {
    return 0u;
}

void gomore_primitives_noop_76500(void) {
}

void gomore_primitives_noop_578c8(void) {
}

void gomore_primitives_noop_49e58(void) {
}

void gomore_primitives_noop_91080(void) {
}

bool gomore_primitives_clear_72(void *record, size_t length) {
    if (record == NULL || length < 0x48u) {
        return false;
    }
    clear_bytes(record, 0x48u);
    return true;
}

bool gomore_primitives_store_first_word(uint32_t *record, uint32_t value) {
    if (record == NULL) {
        return false;
    }
    *record = value;
    return true;
}

bool gomore_primitives_clear_first_byte(uint8_t *record) {
    if (record == NULL) {
        return false;
    }
    *record = 0u;
    return true;
}

bool gomore_primitives_triplet_initialize(uint32_t record[3],
                                          uint32_t field4,
                                          uint32_t field0,
                                          uint32_t field8) {
    if (record == NULL) {
        return false;
    }
    record[1] = field4;
    record[0] = field0;
    record[2] = field8;
    return true;
}

float gomore_primitives_interpolate(float weight, float first, float second) {
    return second + weight * (first - second);
}

bool gomore_primitives_byte_in_70_100(uint8_t value) {
    return (uint8_t)(value - UINT8_C(70)) <= UINT8_C(30);
}

bool gomore_primitives_clear_flag_1000(uint8_t *state, size_t length) {
    if (state == NULL || length <= 1000u) {
        return false;
    }
    if (state[1000] == 1u) {
        state[1000] = 0u;
    }
    return true;
}

float gomore_primitives_cubic_scale(float value) {
    return value * 0x1.2e09fep-3f * value * value;
}

float gomore_primitives_linear_evaluate(float value, float slope,
                                        float intercept) {
    return intercept + slope * value;
}

bool gomore_primitives_shift_u8_window5(uint8_t values[5], uint8_t value) {
    if (values == NULL) {
        return false;
    }
    for (size_t index = 0u; index < 4u; ++index) {
        values[index] = values[index + 1u];
    }
    values[4] = value;
    return true;
}

size_t gomore_primitives_nullable_strlen(const char *text) {
    if (text == NULL) {
        return 0u;
    }
    size_t length = 0u;
    while (text[length] != '\0') {
        ++length;
    }
    return length;
}

bool gomore_primitives_u16_in_30000_50000(uint16_t value) {
    return (uint16_t)(value - UINT16_C(30000)) <= UINT16_C(20000);
}

bool gomore_primitives_clear_36(void *record, size_t length) {
    if (record == NULL || length < 0x24u) {
        return false;
    }
    clear_bytes(record, 0x24u);
    return true;
}

bool gomore_primitives_step_record_initialize(void *record, size_t length) {
    if (record == NULL || length < 0x1Cu) {
        return false;
    }
    clear_bytes(record, 0x1Cu);
    store_u32_le((uint8_t *)record + 0x10u, 5u);
    return true;
}

bool gomore_primitives_clear_124(void *record, size_t length) {
    if (record == NULL || length < 0x7Cu) {
        return false;
    }
    clear_bytes(record, 0x7Cu);
    return true;
}

bool gomore_primitives_float_state_initialize(void *record, size_t length) {
    if (record == NULL || length < 0x80u ||
            !gomore_primitives_clear_124(record, length)) {
        return false;
    }
    store_u32_le((uint8_t *)record + 0x7Cu, UINT32_C(0x3C54FDF4));
    return true;
}

uint32_t gomore_primitives_half_to_float_bits(uint16_t value) {
    return ((uint32_t)value >> 15u) << 31u |
           ((((uint32_t)value & UINT32_C(0x7FFF)) >> 10u) +
            UINT32_C(0x70)) << 23u |
           ((uint32_t)value & UINT32_C(0x03FF)) << 13u;
}

bool gomore_primitives_store_half_as_float_bits(uint32_t *destination,
                                                uint16_t value) {
    if (destination == NULL) {
        return false;
    }
    *destination = gomore_primitives_half_to_float_bits(value);
    return true;
}

int32_t gomore_primitives_find_next_nonnegative_i16(
    const int16_t *values, size_t count, size_t start) {
    if (values == NULL || count <= 1u || start >= count - 1u) {
        return -1;
    }
    while (start < count - 1u) {
        if (values[start] >= 0) {
            return (int32_t)start;
        }
        ++start;
    }
    return -1;
}

bool gomore_primitives_shift_two_u8_windows5(
    uint8_t first[5], uint8_t second[5],
    uint8_t first_value, uint8_t second_value) {
    return gomore_primitives_shift_u8_window5(first, first_value) &&
           gomore_primitives_shift_u8_window5(second, second_value);
}

float gomore_primitives_normalized_position(float value, float high,
                                            float low) {
    const float span = high - low;
    return span == 0.0f ? 0.0f : (value - low) / span;
}

bool gomore_primitives_packed_2bit_get(const uint8_t *bytes,
                                       size_t length, uint32_t index,
                                       uint8_t *value) {
    const uint32_t wrapped = index % UINT32_C(0xB40);
    const size_t byte_index = (size_t)(wrapped >> 2u);
    if (bytes == NULL || value == NULL || byte_index >= length) {
        return false;
    }
    *value = (uint8_t)((bytes[byte_index] >>
                        ((wrapped & UINT32_C(3)) << 1u)) & UINT8_C(3));
    return true;
}

bool gomore_primitives_energy_state_reset(void *record, size_t length) {
    if (record == NULL || length < 0x58u) {
        return false;
    }
    uint8_t *bytes = record;
    store_u32_le(&bytes[0x4Cu], 0u);
    store_u32_le(&bytes[0x50u], 0u);
    store_u32_le(&bytes[0x54u], 0u);
    store_u32_le(&bytes[0x0Cu], 0u);
    store_u32_le(&bytes[0x14u], UINT32_C(0x3F800000));
    bytes[0x18u] = 0u;
    return true;
}

bool gomore_primitives_large_default_state_initialize(void *record,
                                                      size_t length) {
    if (record == NULL || length < 0x404u) {
        return false;
    }
    uint8_t *bytes = record;
    clear_bytes(bytes, 0x404u);
    store_u32_le(&bytes[0x3F8u], 3u);
    store_u32_le(&bytes[0x3FCu], UINT32_C(0x3F000000));
    return true;
}

bool gomore_primitives_scale_milli(float *values, size_t count) {
    if (values == NULL && count != 0u) {
        return false;
    }
    const float scale = bits_float(UINT32_C(0x3A83126F));
    for (size_t index = 0u; index < count; ++index) {
        values[index] *= scale;
    }
    return true;
}

bool gomore_primitives_sps_state_reset(void *record, size_t length) {
    if (record == NULL || length < 0x58u) {
        return false;
    }
    uint8_t *bytes = record;
    store_u32_le(&bytes[0x54u], 0u);
    store_u32_le(&bytes[0x4Cu], 0u);
    store_u32_le(&bytes[0x2Cu], 0u);
    store_u32_le(&bytes[0x28u], 0u);
    store_u16_le_early(&bytes[0x30u], 0u);
    store_u32_le(&bytes[0x10u], 0u);
    store_u32_le(&bytes[0x0Cu], 0u);
    store_u16_le_early(&bytes[0x14u], 0u);
    return true;
}

bool gomore_primitives_shift_status_windows(uint8_t history[10],
                                            uint8_t output[3]) {
    if (history == NULL || output == NULL ||
            !gomore_primitives_shift_two_u8_windows5(
                &history[5], &history[0], 0u, UINT8_C(0xFE))) {
        return false;
    }
    output[0] = UINT8_C(0xFF);
    output[1] = UINT8_C(0xFE);
    output[2] = 0u;
    return true;
}

size_t gomore_primitives_count_byte_plus_one(const uint8_t *values,
                                             size_t count,
                                             uint8_t target) {
    if (values == NULL && count != 0u) {
        return 0u;
    }
    size_t matches = 0u;
    for (size_t index = 0u; index < count; ++index) {
        matches += values[index] == target ? 1u : 0u;
    }
    return matches + 1u;
}

bool gomore_primitives_accumulate_pair(void *record, size_t length,
                                       float first, float second) {
    if (record == NULL || length < 0x0Eu) {
        return false;
    }
    uint8_t *bytes = record;
    const float accumulated_second =
        bits_float(load_u32_le(&bytes[4])) + second;
    const float accumulated_first =
        bits_float(load_u32_le(&bytes[8])) + first;
    store_u32_le(&bytes[4], float_bits(accumulated_second));
    store_u32_le(&bytes[8], float_bits(accumulated_first));
    store_u16_le_early(
        &bytes[0x0Cu],
        (uint16_t)(load_u16_le_early(&bytes[0x0Cu]) + 1u));
    return true;
}

bool gomore_primitives_selected_state_reset(void *record, size_t length) {
    if (record == NULL || length < 0x64u) {
        return false;
    }
    uint8_t *bytes = record;
    store_u32_le(&bytes[0x10u], 0u);
    store_u32_le(&bytes[0x0Cu], 0u);
    bytes[4] = 0u;
    bytes[1] = 0u;
    for (size_t index = 0u; index < 20u; ++index) {
        store_u32_le(&bytes[0x14u + index * 4u], 0u);
    }
    return true;
}

bool gomore_primitives_pattern17_initialize(void *record, size_t length) {
    if (record == NULL || length < 17u) {
        return false;
    }
    uint8_t *bytes = record;
    for (size_t index = 0u; index < 5u; ++index) {
        bytes[index] = UINT8_C(0xFE);
        bytes[index + 5u] = 0u;
        bytes[index + 10u] = 0u;
    }
    bytes[15] = 1u;
    bytes[16] = 1u;
    return true;
}

bool gomore_primitives_energy_record_initialize(void *record, size_t length,
                                                uint32_t binding) {
    if (record == NULL || length < 0x5Cu) {
        return false;
    }
    uint8_t *bytes = record;
    clear_bytes(bytes, 0x5Cu);
    if (!gomore_primitives_energy_state_reset(record, length)) {
        return false;
    }
    bytes[8] = 0u;
    store_u32_le(&bytes[0], 1u);
    store_u32_le(&bytes[0x58u], binding);
    return true;
}

bool gomore_primitives_large_state_initialize(void *record, size_t length,
                                              uint32_t binding,
                                              void **active_record) {
    if (record == NULL || active_record == NULL || length < 0x33Cu) {
        return false;
    }
    uint8_t *bytes = record;
    clear_bytes(bytes, 0x33Cu);
    *active_record = record;
    store_u32_le(&bytes[0x338u], binding);
    return true;
}

bool gomore_primitives_low24_binding_initialize(
    uint32_t record[2], const uint8_t value[3], uint32_t binding) {
    if (record == NULL || value == NULL) {
        return false;
    }
    record[0] = (uint32_t)value[0] |
                (uint32_t)value[1] << 8u |
                (uint32_t)value[2] << 16u;
    record[1] = binding;
    return true;
}

bool gomore_primitives_pack4_binding_initialize(
    uint32_t record[2], uint8_t byte0, uint8_t byte1,
    uint8_t byte2, uint8_t byte3, uint32_t binding) {
    if (record == NULL) {
        return false;
    }
    record[0] = (uint32_t)byte0 |
                (uint32_t)byte1 << 8u |
                (uint32_t)byte2 << 16u |
                (uint32_t)byte3 << 24u;
    record[1] = binding;
    return true;
}

int16_t gomore_primitives_i16_mean(const int16_t *values, size_t count) {
    if (values == NULL || count == 0u || count > (size_t)INT32_MAX) {
        return 0;
    }
    uint32_t wrapped_sum = 0u;
    for (size_t index = 0u; index < count; ++index) {
        wrapped_sum += (uint32_t)(int32_t)values[index];
    }
    const int32_t signed_sum = (int32_t)wrapped_sum;
    return (int16_t)(signed_sum / (int32_t)count);
}

bool gomore_primitives_float_floor_update(float candidate, float *value) {
    if (value == NULL) {
        return false;
    }
    float difference = 0.0f;
    if (candidate <= *value) {
        difference = *value - candidate;
    }
    *value = difference + candidate;
    return true;
}

bool gomore_primitives_validate_selector(const uint8_t *state,
                                         size_t length, int8_t *selector) {
    if (state == NULL || selector == NULL || length < 17u) {
        return false;
    }
    if ((*selector == 1 && state[15] == 0u) ||
            (*selector == 2 && state[16] == 0u)) {
        *selector = -1;
    }
    return true;
}

int32_t gomore_primitives_nullable_compare(const uint8_t *left,
                                           const uint8_t *right) {
    if (left == NULL || right == NULL) {
        return 0;
    }
    while (*left == *right) {
        if (*left == 0u) {
            return 0;
        }
        ++left;
        ++right;
    }
    return (int32_t)*left - (int32_t)*right;
}

bool gomore_primitives_compact_u32_stride(uint32_t *values,
                                          size_t capacity,
                                          size_t count, size_t stride,
                                          size_t *output_count) {
    if (output_count == NULL || stride == 0u || count > capacity ||
            (values == NULL && count != 0u)) {
        return false;
    }
    size_t destination = 0u;
    for (size_t source = 0u; source < count; source += stride) {
        values[destination++] = values[source];
    }
    *output_count = destination;
    return true;
}

int32_t gomore_primitives_status_record_extract(const void *source,
                                                size_t source_length,
                                                void *destination,
                                                size_t destination_length) {
    if (source == NULL || destination == NULL || source_length < 0x56u ||
            destination_length < 0x44u) {
        return -1;
    }
    const uint8_t *source_bytes = source;
    uint8_t *destination_bytes = destination;
    if (load_u16_le_early(&source_bytes[0x54u]) != 0u) {
        clear_bytes(destination_bytes, 0x44u);
        return -1008;
    }
    store_u16_le_early(&destination_bytes[0x42u],
                       load_u16_le_early(&source_bytes[0x52u]));
    return 0;
}

bool gomore_primitives_half_span_initialize(uint32_t record[5],
                                            uint16_t half_value,
                                            uint32_t base) {
    if (record == NULL) {
        return false;
    }
    record[0] = gomore_primitives_half_to_float_bits(half_value);
    record[1] = base;
    record[2] = base + UINT32_C(0x14);
    record[3] = base + UINT32_C(0x28);
    record[4] = base + UINT32_C(0x3C);
    return true;
}

bool gomore_primitives_parameter_state_initialize(void *record,
                                                  size_t length,
                                                  uint32_t binding) {
    if (record == NULL || length < 0x20FCu) {
        return false;
    }
    uint8_t *bytes = record;
    clear_bytes(bytes, 0x20FCu);
    store_u32_le(&bytes[0x20F8u], binding);
    return true;
}

size_t gomore_primitives_count_encoded_i32(const int32_t *values,
                                           size_t count) {
    if (values == NULL && count != 0u) {
        return 0u;
    }
    size_t matches = 0u;
    for (size_t index = 0u; index < count; ++index) {
        const uint32_t encoded =
            (uint32_t)values[index] + UINT32_C(0xBF200000);
        matches += encoded < UINT32_C(0x00E80001) ? 1u : 0u;
    }
    return matches;
}

float gomore_primitives_scaled_ratio(float numerator, float denominator) {
    const float scaled_denominator =
        denominator * bits_float(UINT32_C(0x40333333));
    if (scaled_denominator == 0.0f) {
        return 0.0f;
    }
    return (numerator * bits_float(UINT32_C(0x43480000))) /
           scaled_denominator;
}

uint8_t gomore_primitives_piecewise_clamp_70_100(int32_t value) {
    int64_t delta = (int64_t)value - INT64_C(96);
    delta *= delta < 0 ? INT64_C(5) : INT64_C(8);
    int64_t transformed = delta / INT64_C(10) + INT64_C(96);
    if (transformed < 70) {
        transformed = 70;
    } else if (transformed > 100) {
        transformed = 100;
    }
    return (uint8_t)transformed;
}

bool gomore_primitives_missing_window_initialize(void *record,
                                                 size_t length) {
    if (record == NULL || length < 0x3Eu) {
        return false;
    }
    uint8_t *bytes = record;
    clear_bytes(bytes, 0x38u);
    for (size_t index = 0u; index < 6u; ++index) {
        bytes[0x38u + index] = UINT8_C(0xFF);
    }
    return true;
}

bool gomore_primitives_modulo_value_get(const uint8_t *bytes,
                                        size_t length, uint32_t index,
                                        bool packed, uint8_t *value) {
    const uint32_t wrapped = index % UINT32_C(0xB40);
    const size_t byte_index = packed ? (size_t)(wrapped >> 2u)
                                     : (size_t)wrapped;
    if (bytes == NULL || value == NULL || byte_index >= length) {
        return false;
    }
    *value = packed
        ? (uint8_t)((bytes[byte_index] >>
                     ((wrapped & UINT32_C(3)) << 1u)) & UINT8_C(3))
        : bytes[byte_index];
    return true;
}

bool gomore_primitives_mode8_state_initialize(void *record, size_t length) {
    if (record == NULL || length < 0x26Eu) {
        return false;
    }
    uint8_t *bytes = record;
    clear_bytes(bytes, 0x26Eu);
    bytes[0] = 8u;
    return true;
}

bool gomore_primitives_vector_pair_transform(float scale, float offset,
                                             const float left[2],
                                             const float right[2],
                                             float output[2]) {
    if (left == NULL || right == NULL || output == NULL) {
        return false;
    }
    output[0] = (left[0] - offset / (scale * 3.0f)) + right[0];
    output[1] = left[1] + right[1];
    return true;
}

bool gomore_primitives_encode_short_record(uint8_t record[17],
                                           const uint8_t *payload,
                                           size_t payload_length) {
    if (record == NULL || payload_length > 16u ||
            (payload == NULL && payload_length != 0u)) {
        return false;
    }
    clear_bytes(record, 17u);
    record[16] = (uint8_t)((payload_length & 0x7Fu) | 0x80u);
    for (size_t index = 0u; index < payload_length; ++index) {
        record[index] = payload[index];
    }
    return true;
}

bool gomore_primitives_accumulate_i8x4_milli(float values[4],
                                             const int8_t increments[4]) {
    if (values == NULL || increments == NULL) {
        return false;
    }
    const float scale = bits_float(UINT32_C(0x3C23D70A));
    for (size_t index = 0u; index < 4u; ++index) {
        values[index] += (float)increments[index] * scale;
    }
    return true;
}

uint32_t gomore_primitives_shift_presence_history(uint8_t *record,
                                                  size_t length,
                                                  uint8_t value) {
    if (record == NULL || length < 0x19u) {
        return 0u;
    }
    for (size_t index = 0u; index < 4u; ++index) {
        record[0x14u + index] = record[0x15u + index];
    }
    record[0x18u] = value;
    if (value != 0u && record[0x17u] == 0u) {
        if (record[0x16u] != 0u) {
            return 1u;
        }
        if (record[0x15u] != 0u) {
            return 2u;
        }
    }
    return 0u;
}

bool gomore_primitives_fill_float_progression(float *values, size_t count,
                                              size_t begin, size_t end,
                                              float first, float step) {
    if (values == NULL || begin > end || end > count) {
        return false;
    }
    size_t offset = 0u;
    for (size_t index = begin; index < end; ++index) {
        values[index] = first + (float)offset * step;
        ++offset;
    }
    return true;
}

bool gomore_primitives_time_record_valid(const void *record, size_t length) {
    if (record == NULL || length < 8u) {
        return false;
    }
    const uint8_t *bytes = record;
    const uint16_t first = load_u16_le_early(&bytes[0]);
    const uint16_t second = load_u16_le_early(&bytes[2]);
    return (uint16_t)(first - UINT16_C(15)) < UINT16_C(46) &&
           second < UINT16_C(241) && bytes[6] <= 23u && bytes[7] <= 23u;
}

size_t gomore_primitives_float_argmax_range(const float *values,
                                            size_t count, size_t begin,
                                            size_t end) {
    if (values == NULL || begin >= end || end > count) {
        return SIZE_MAX;
    }
    size_t result = begin;
    float largest = values[begin];
    for (size_t index = begin; index < end; ++index) {
        if (largest < values[index]) {
            result = index & 0xFFu;
            largest = values[index];
        }
    }
    return result;
}

int32_t gomore_primitives_float_argmax_above_floor(const float *values,
                                                   size_t count) {
    if (values == NULL && count != 0u) {
        return -1;
    }
    int32_t result = -1;
    float largest = bits_float(UINT32_C(0xCE6E6B28));
    for (size_t index = 0u; index < count; ++index) {
        if (largest < values[index]) {
            result = (int32_t)index;
            largest = values[index];
        }
    }
    return result;
}

int32_t gomore_primitives_i16_range(const int16_t *values, size_t count) {
    if (values == NULL || count == 0u) {
        return 32000;
    }
    int32_t minimum = values[0];
    int32_t maximum = values[0];
    for (size_t index = 0u; index < count; ++index) {
        if (values[index] < minimum) {
            minimum = values[index];
        }
        if (values[index] > maximum) {
            maximum = values[index];
        }
    }
    const int32_t range = maximum - minimum;
    return range < 32001 ? (int32_t)(int16_t)range : 32000;
}

bool gomore_primitives_packed_2bit_set(uint8_t *bytes, size_t length,
                                      uint32_t index, uint8_t value) {
    const uint32_t wrapped = index % UINT32_C(0xB40);
    const size_t byte_index = (size_t)(wrapped >> 2u);
    if (bytes == NULL || byte_index >= length) {
        return false;
    }
    const uint32_t shift = (wrapped & UINT32_C(3)) << 1u;
    const uint8_t clear_mask = (uint8_t)~(uint8_t)(UINT8_C(3) << shift);
    bytes[byte_index] = (uint8_t)((bytes[byte_index] & clear_mask) |
                                 (uint8_t)(value << shift));
    return true;
}

float gomore_primitives_rational_transform(float value, float state) {
    const float scaled = value * bits_float(UINT32_C(0x3E16277C)) *
                         state * bits_float(UINT32_C(0x42C80000));
    const float denominator = bits_float(UINT32_C(0x42700000)) -
        value * bits_float(UINT32_C(0x3E20FBA9)) * state *
        bits_float(UINT32_C(0x42C80000));
    return scaled / denominator;
}

int16_t gomore_primitives_i16_mean_absolute_difference(
    const int16_t *values, size_t count) {
    if (values == NULL || count <= 1u) {
        return 0;
    }
    uint32_t sum = 0u;
    for (size_t index = 0u; index + 1u < count; ++index) {
        int32_t difference = (int32_t)values[index + 1u] - values[index];
        if (difference < 0) {
            difference = -difference;
        }
        sum += (uint32_t)difference;
    }
    return (int16_t)(sum / (uint32_t)(count - 1u));
}

bool gomore_primitives_u16_all_within_300(const uint16_t *values,
                                         size_t count, uint16_t target) {
    if (values == NULL && count != 0u) {
        return false;
    }
    for (size_t index = 0u; index < count; ++index) {
        const uint16_t difference = values[index] < target
            ? (uint16_t)(target - values[index])
            : (uint16_t)(values[index] - target);
        if (difference > 300u) {
            return false;
        }
    }
    return true;
}

float gomore_primitives_nonzero_i16_mean8(const int16_t values[8]) {
    if (values == NULL) {
        return 0.0f;
    }
    int32_t sum = 0;
    int32_t count = 0;
    for (size_t index = 0u; index < 8u; ++index) {
        if (values[index] != 0) {
            sum += values[index];
            ++count;
        }
    }
    return count > 0 ? (float)sum / (float)count : 0.0f;
}

float gomore_primitives_circular_u8_dot18(const uint8_t values[18],
                                         uint32_t sample_index,
                                         const float weights[18]) {
    if (values == NULL || weights == NULL) {
        return 0.0f;
    }
    float result = 0.0f;
    const uint32_t start = sample_index / UINT32_C(30);
    for (size_t index = 0u; index < 18u; ++index) {
        const size_t value_index =
            (size_t)((start + (uint32_t)index) % UINT32_C(18));
        result += (float)values[value_index] * weights[index];
    }
    return result;
}

int32_t gomore_primitives_filtered_u8_mean(const uint8_t *values,
                                          size_t count, int32_t center,
                                          int32_t tolerance) {
    if (values == NULL || count > 127u || tolerance < 0) {
        return 0;
    }
    int32_t sum = 0;
    int32_t included = 0;
    for (size_t index = 0u; index < count; ++index) {
        const int32_t value = values[index];
        int32_t difference = value - center;
        if (difference < 0) {
            difference = -difference;
        }
        if (value != 0 && difference <= tolerance) {
            sum += value;
            ++included;
        }
    }
    return included != 0 ? sum / included : 0;
}

bool gomore_primitives_complex_multiply(const float left[2],
                                        const float right[2],
                                        float output[2]) {
    if (left == NULL || right == NULL || output == NULL) {
        return false;
    }
    const float left_real = left[0];
    const float left_imaginary = left[1];
    const float right_real = right[0];
    const float right_imaginary = right[1];
    output[0] = left_real * right_real - left_imaginary * right_imaginary;
    output[1] = left_imaginary * right_real + left_real * right_imaginary;
    return true;
}

uint8_t gomore_primitives_count_hysteresis_crossings(
    const uint16_t *values, size_t count) {
    if (values == NULL && count != 0u) {
        return 0u;
    }
    bool armed = true;
    uint8_t crossings = 0u;
    for (size_t index = 0u; index < count; ++index) {
        if (armed && values[index] > UINT16_C(1200)) {
            armed = false;
            ++crossings;
        } else if (!armed && values[index] < UINT16_C(1000)) {
            armed = true;
        }
    }
    return crossings;
}

int32_t gomore_primitives_nullable_compare_n(const uint8_t *left,
                                             const uint8_t *right,
                                             size_t count) {
    if (left == NULL || right == NULL || count == 0u) {
        return 0xFFFF;
    }
    for (size_t index = 0u; index < count; ++index) {
        if (left[index] < right[index]) {
            return -1;
        }
        if (left[index] > right[index]) {
            return 1;
        }
    }
    return 0;
}

bool gomore_primitives_recent_interval_predicate(const void *record,
                                                 size_t length,
                                                 uint32_t now) {
    if (record == NULL || length < 0x1Bu) {
        return false;
    }
    const uint8_t *bytes = record;
    if ((bytes[0x1Au] & UINT8_C(8)) == 0u) {
        return false;
    }
    const uint32_t begin = load_u32_le(&bytes[0]);
    const uint32_t end = load_u32_le(&bytes[4]);
    const uint32_t duration = end - begin;
    return begin < end && duration <= UINT32_C(86400) &&
           duration >= UINT32_C(900) &&
           begin + UINT32_C(86400) > now && now >= end;
}

int32_t gomore_primitives_record_quality_classify(const void *record,
                                                  size_t length) {
    if (record == NULL || length < 0x3Du) {
        return -1;
    }
    const uint8_t *bytes = record;
    const int8_t flag_39 = (int8_t)bytes[0x39u];
    const int8_t flag_3a = (int8_t)bytes[0x3Au];
    const int8_t flag_3b = (int8_t)bytes[0x3Bu];
    const int8_t flag_3c = (int8_t)bytes[0x3Cu];
    if (flag_3b >= 1 && flag_3c >= 1) {
        return 2;
    }
    const int32_t word_2c = (int32_t)load_u32_le(&bytes[0x2Cu]);
    const int32_t word_30 = (int32_t)load_u32_le(&bytes[0x30u]);
    if ((word_2c <= INT32_C(0x43480000) ||
         word_30 <= INT32_C(0x43340000)) &&
            flag_3a >= 0 && flag_39 >= 0) {
        return 1;
    }
    return -1;
}

int32_t gomore_primitives_seeded_random_offset(
    uint32_t seed, uint32_t *stored_seed,
    gomore_primitives_simple_fn prepare,
    gomore_primitives_random_fn random_value) {
    if (stored_seed == NULL || prepare == NULL || random_value == NULL) {
        return -1;
    }
    *stored_seed = seed;
    prepare();
    return random_value() % 100 + 23;
}

static void *allocate_mode_state(
    size_t length, uint32_t mode, uintptr_t binding,
    gomore_primitives_zero_allocate_fn allocate,
    gomore_primitives_allocated_init_fn initialize) {
    if (allocate == NULL || initialize == NULL) {
        return NULL;
    }
    uint8_t *record = allocate(length);
    if (record == NULL) {
        return NULL;
    }
    store_u32_le(record, mode);
    initialize(record, binding);
    return record;
}

void *gomore_primitives_allocate_mode2_state(
    uintptr_t binding, gomore_primitives_zero_allocate_fn allocate,
    gomore_primitives_allocated_init_fn initialize) {
    return allocate_mode_state(0x23Cu, 2u, binding, allocate, initialize);
}

void *gomore_primitives_allocate_mode1_state(
    uintptr_t binding, gomore_primitives_zero_allocate_fn allocate,
    gomore_primitives_allocated_init_fn initialize) {
    return allocate_mode_state(0x238u, 1u, binding, allocate, initialize);
}

int32_t gomore_primitives_decimal_parse(const uint8_t *text) {
    if (text == NULL) {
        return 0;
    }
    int32_t value = 0;
    for (size_t index = 0u; text[index] != 0u; ++index) {
        value = (int32_t)((uint32_t)value * UINT32_C(10) +
                          (uint32_t)text[index] - UINT32_C(0x30));
    }
    return value;
}

uint32_t gomore_primitives_tensor_call_optional_finish(
    const uint32_t descriptor[3], uintptr_t first, uintptr_t second,
    bool finish, gomore_primitives_tensor_call_fn call,
    gomore_primitives_tensor_finish_fn finish_call) {
    if (descriptor == NULL || call == NULL || (finish && finish_call == NULL)) {
        return UINT32_MAX;
    }
    const uint32_t result = call(first, second, descriptor[0],
                                 descriptor[1], descriptor[2]);
    if (finish) {
        finish_call(first, second);
    }
    return result;
}

int32_t gomore_primitives_all_class_0x20(const uint8_t *bytes,
                                        size_t count,
                                        const uint8_t classes[256]) {
    if ((bytes == NULL && count != 0u) || classes == NULL) {
        return -1;
    }
    for (size_t index = 0u; index < count; ++index) {
        if (classes[bytes[index]] != UINT8_C(0x20)) {
            return -1;
        }
    }
    return 0;
}

bool gomore_primitives_filter_state_initialize(
    void *record, size_t length, gomore_primitives_filter_init_fn initialize) {
    if (record == NULL || length < 0x18Cu || initialize == NULL) {
        return false;
    }
    static const float parameters[2] = {
        0x1.0624dep-6f, 0x1.47ae14p-3f
    };
    clear_bytes(record, 0x18Cu);
    initialize(record, 2u, 2u, parameters);
    return true;
}

bool gomore_primitives_quality_samples_copy(
    void *record, size_t length,
    const gomore_primitives_quality_sample samples[3]) {
    if (record == NULL || length < 0x24u || samples == NULL) {
        return false;
    }
    uint8_t *bytes = record;
    for (size_t index = 0u; index < 3u; ++index) {
        if (samples[index].metadata < INT32_C(0x3727C5AC) &&
                samples[index].value >= 0.0f) {
            store_u32_le(&bytes[0x18u + index * 4u],
                         float_bits(samples[index].value));
        }
    }
    return true;
}

bool gomore_primitives_dual_stage(
    uintptr_t first, uintptr_t second, uintptr_t third, uintptr_t fourth,
    void *output, size_t output_length,
    gomore_primitives_dual_stage_fn first_stage,
    gomore_primitives_dual_stage_fn second_stage) {
    if (output == NULL || output_length < 0x38u || first_stage == NULL ||
            second_stage == NULL) {
        return false;
    }
    first_stage(first, second, third, fourth, output);
    second_stage(first, second, third, fourth, (uint8_t *)output + 0x1Cu);
    return true;
}

bool gomore_primitives_composite_record_initialize(
    void *record, size_t length,
    gomore_primitives_record_init_fn tail_initialize) {
    if (record == NULL || length < 0x30u || tail_initialize == NULL) {
        return false;
    }
    uint8_t *bytes = record;
    tail_initialize(&bytes[0x30u]);
    clear_bytes(&bytes[0x29u], 4u);
    clear_bytes(&bytes[0x2Du], 2u);
    bytes[0x28u] = 0u;
    clear_bytes(bytes, 0x28u);
    return true;
}

bool gomore_primitives_quality_code(const void *record, size_t length,
                                    uint8_t *code) {
    if (record == NULL || length < 0x3Eu || code == NULL) {
        return false;
    }
    const uint8_t *bytes = record;
    uint8_t result = UINT8_C(0xFF);
    if ((int8_t)bytes[0x38u] < 0) {
        result = 0u;
    } else if (bits_float(load_u32_le(&bytes[0x28u])) >= 0.0f &&
               (int8_t)bytes[0x3Du] >= 0) {
        result = (uint8_t)gomore_primitives_record_quality_classify(
            record, length);
    }
    *code = result;
    return true;
}

float gomore_primitives_i16_standard_deviation(
    const int16_t *values, size_t count, int32_t center,
    gomore_primitives_float_unary_fn square_root) {
    if (square_root == NULL || (values == NULL && count != 0u)) {
        return 0.0f;
    }
    uint32_t sum = 0u;
    for (size_t index = 0u; index < count; ++index) {
        const int32_t difference = (int32_t)values[index] - center;
        const int64_t wide_square = (int64_t)difference * difference;
        sum += (uint32_t)wide_square;
    }
    int32_t variance = 0;
    if (count > 1u && count <= (size_t)INT32_MAX) {
        variance = (int32_t)sum / (int32_t)(count - 1u);
    }
    return square_root((float)variance);
}

float gomore_primitives_energy_core(const void *state, size_t length,
                                    float primary, float secondary) {
    if (state == NULL || length < 0x26u) {
        return 0.0f;
    }
    const uint8_t *bytes = state;
    const float state_value = bits_float(load_u32_le(&bytes[0]));
    const uint16_t flags = load_u16_le_early(&bytes[0x24u]);
    if ((flags & UINT16_C(0x0440)) != 0u &&
            (int32_t)float_bits(primary) <= INT32_C(0x3FA00000)) {
        return state_value * bits_float(UINT32_C(0x3CBD230C));
    }
    return ((secondary * bits_float(UINT32_C(0xBAAA3573)) +
             primary * bits_float(UINT32_C(0x3AFD428B)) +
             bits_float(UINT32_C(0x3E91BAD6))) /
            bits_float(UINT32_C(0x3FE6B205))) * state_value;
}

float gomore_primitives_energy_scaled(const void *state, size_t length,
                                      float primary, float scale_input) {
    if (state == NULL || length < 0x26u) {
        return 0.0f;
    }
    const uint8_t *bytes = state;
    const float core = gomore_primitives_energy_core(
        state, length, primary, scale_input);
    const float multiplier = bits_float(load_u32_le(&bytes[4]));
    return (core * multiplier * 2.0f *
            bits_float(UINT32_C(0x411CF5C3)) * scale_input) /
           bits_float(UINT32_C(0x42700000));
}

bool gomore_primitives_state_word_24(const void *state, size_t length,
                                     uint32_t *value) {
    if (state == NULL || length < 0x1Cu || value == NULL) {
        return false;
    }
    *value = load_u32_le((const uint8_t *)state + 0x18u);
    return true;
}

bool gomore_primitives_split_signed_root(
    float value, float output[2],
    gomore_primitives_float_binary_fn power) {
    if (output == NULL || power == NULL) {
        return false;
    }
    if (value < 0.0f) {
        output[0] = 0.0f;
        output[1] = power(-value, 0.5f);
    } else {
        output[0] = power(value, 0.5f);
        output[1] = 0.0f;
    }
    return true;
}

float gomore_primitives_clamped_rational(float value, float state) {
    const float absolute = value < 0.0f ? -value : value;
    const float adjusted = bits_float(UINT32_C(0x3F0A2728)) +
        (absolute - 2.5f) * bits_float(UINT32_C(0x3E20FBA9));
    float result = (value /
        (state * adjusted * bits_float(UINT32_C(0x42C80000)))) *
        bits_float(UINT32_C(0x42700000));
    if ((int32_t)float_bits(result) > INT32_C(0x435C0000)) {
        result = bits_float(UINT32_C(0x435C0000));
    }
    return result;
}

bool gomore_primitives_table_record11(const uint8_t *table,
                                      size_t table_length, int32_t index,
                                      uint8_t output[11]) {
    if (table == NULL || output == NULL || index < 0) {
        return false;
    }
    const size_t offset = index < 100
        ? (size_t)index * 11u
        : (size_t)(index - 100) * 11u + 44u;
    if (offset > table_length || table_length - offset < 11u) {
        return false;
    }
    for (size_t byte = 0u; byte < 11u; ++byte) {
        output[byte] = table[offset + byte];
    }
    return true;
}

int32_t gomore_primitives_status_or_random(
    uint8_t *state, size_t state_length,
    const void *status_record, size_t status_length,
    gomore_primitives_simple_fn prepare,
    gomore_primitives_random_fn random_value) {
    if (state == NULL || state_length < 0x14u || status_record == NULL ||
            status_length < 12u) {
        return -1;
    }
    const uint8_t *status = status_record;
    for (size_t index = 0u; index < 4u; ++index) {
        const int16_t code = (int16_t)load_u16_le_early(
            &status[4u + index * 2u]);
        if (code < 0) {
            return code;
        }
    }
    if (state[0x10u] != 4u) {
        return 0;
    }
    if (prepare == NULL || random_value == NULL) {
        return -1;
    }
    store_u32_le(state, load_u32_le(status));
    prepare();
    return (int16_t)(random_value() % 100 + 23);
}

bool gomore_primitives_mode_state_configure(
    void *record, size_t length, uint32_t mode, uint32_t count,
    const float parameters[2],
    gomore_primitives_mode_lt2_init_fn initialize_lt2,
    gomore_primitives_mode2_init_fn initialize_mode2) {
    if (record == NULL || length < 0x50u || parameters == NULL ||
            (mode < 2u && initialize_lt2 == NULL) ||
            (mode == 2u && initialize_mode2 == NULL)) {
        return false;
    }
    uint8_t *bytes = record;
    if (mode < 2u) {
        initialize_lt2(record, mode, count, parameters[0]);
        store_u32_le(bytes, count);
    } else if (mode == 2u) {
        initialize_mode2(record, count, parameters);
        store_u32_le(bytes, count << 1u);
    }
    clear_bytes(&bytes[0x30u], 16u);
    clear_bytes(&bytes[0x40u], 16u);
    return true;
}

bool gomore_primitives_large_filter_state_initialize(
    void *record, size_t length,
    gomore_primitives_mode2_init_fn initialize_mode2) {
    if (record == NULL || length < 0x6C8u || initialize_mode2 == NULL) {
        return false;
    }
    uint8_t *bytes = record;
    clear_bytes(bytes, 0x6C8u);
    store_u32_le(&bytes[0x6C0u], UINT32_C(0xBF800000));
    store_u32_le(&bytes[0x6C4u], UINT32_C(0xBF800000));
    for (size_t index = 0u; index < 250u; ++index) {
        store_u32_le(&bytes[0x2D8u + index * 4u], 0u);
    }
    const float parameters[2] = {
        bits_float(UINT32_C(0x3D23D70A)),
        bits_float(UINT32_C(0x3EA3D70A))
    };
    return gomore_primitives_mode_state_configure(
        record, length, 2u, 2u, parameters, NULL, initialize_mode2);
}

bool gomore_primitives_engine_state_initialize(
    void *record, size_t length, uint32_t binding,
    gomore_primitives_large_init_fn initialize) {
    if (record == NULL || length < 0x3894u || initialize == NULL) {
        return false;
    }
    uint8_t *bytes = record;
    clear_bytes(bytes, 0x3894u);
    store_u32_le(&bytes[0x3890u], binding);
    initialize(record);
    return true;
}

static bool resample25_and_filter_common(
    void *filter_state, const float *source, int32_t input_count,
    int32_t source_total, float destination[25],
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter) {
    if (filter_state == NULL || source == NULL || destination == NULL ||
            resample == NULL || apply_filter == NULL) {
        return false;
    }
    resample(source, input_count, 25, source_total, destination);
    apply_filter(filter_state, destination, 25u);
    return true;
}

int32_t gomore_primitives_resample25_and_filter(
    void *filter_state, const float *source, int32_t input_count,
    int32_t source_total, float destination[25],
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter) {
    return resample25_and_filter_common(
        filter_state, source, input_count, source_total, destination,
        resample, apply_filter) ? 0 : -1;
}

void gomore_primitives_resample25_and_filter_tail(
    void *filter_state, const float *source, int32_t input_count,
    int32_t source_total, float destination[25],
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter) {
    (void)resample25_and_filter_common(
        filter_state, source, input_count, source_total, destination,
        resample, apply_filter);
}

bool gomore_primitives_prepare_filter_input(
    void *filter_state, size_t filter_length,
    const float *source, bool clear_only, int32_t source_total,
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter) {
    if (filter_state == NULL || filter_length < 0x17Cu) {
        return false;
    }
    float *destination = (float *)((uint8_t *)filter_state + 0x118u);
    if (clear_only) {
        clear_bytes((uint8_t *)destination, 100u);
        return true;
    }
    return resample25_and_filter_common(
        filter_state, source, 25, source_total, destination,
        resample, apply_filter);
}

bool gomore_primitives_commit_valid_time_record(
    void *context, size_t context_length,
    void *destination, size_t destination_length,
    const void *record, size_t record_length) {
    if (context == NULL || context_length < 0x13Cu || destination == NULL ||
            destination_length < 10u || record == NULL || record_length < 8u ||
            !gomore_primitives_time_record_valid(record, record_length)) {
        return false;
    }
    uint8_t *context_bytes = context;
    uint8_t *destination_bytes = destination;
    const uint8_t *record_bytes = record;
    for (size_t index = 0u; index < 8u; ++index) {
        destination_bytes[2u + index] = record_bytes[index];
    }
    if (context_bytes[0xB8u] == 0u && context_bytes[0xB4u] == 0u) {
        for (size_t index = 0u; index < 8u; ++index) {
            context_bytes[0x130u + index] = record_bytes[index];
        }
    }
    return true;
}

bool gomore_primitives_signed_power_third(
    float values[2], gomore_primitives_float_binary_fn power) {
    if (values == NULL || power == NULL) {
        return false;
    }
    const float input = values[0];
    const float magnitude = power(input <= 0.0f ? -input : input,
                                  bits_float(UINT32_C(0x3EAAAAAB)));
    values[0] = input <= 0.0f ? -magnitude : magnitude;
    values[1] = 0.0f;
    return true;
}

bool gomore_primitives_trim_below_reference_tail(
    const uint8_t *reference, size_t reference_count,
    uint8_t *values, size_t capacity, size_t *value_count) {
    if (reference == NULL || values == NULL || value_count == NULL ||
            *value_count > capacity) {
        return false;
    }
    size_t remove = 0u;
    if (reference_count > 0u) {
        const uint8_t threshold = reference[reference_count - 1u];
        for (size_t index = 0u; index < *value_count; ++index) {
            if (values[index] <= threshold) {
                ++remove;
            }
        }
    }
    if (remove == *value_count) {
        *value_count = 0u;
        return true;
    }
    for (size_t index = remove; index < *value_count; ++index) {
        values[index - remove] = values[index];
    }
    *value_count -= remove;
    return true;
}

bool gomore_primitives_selector_transition(const void *record,
                                           size_t length,
                                           int8_t *selector) {
    if (record == NULL || length < 0x3Eu || selector == NULL) {
        return false;
    }
    const uint8_t *bytes = record;
    if (bits_float(load_u32_le(&bytes[0x20u])) > 0.0f &&
            (int8_t)bytes[0x39u] > 0 && *selector == -1) {
        *selector = 1;
    }
    if ((*selector == 1 || *selector == 2) &&
            (bits_float(load_u32_le(&bytes[0x28u])) < 0.0f ||
             (int8_t)bytes[0x3Du] < 0)) {
        *selector = -1;
    }
    return true;
}

bool gomore_primitives_fill_packed_time_gap(void *record, size_t length,
                                            uint32_t now) {
    if (record == NULL || length < 0x2D5u) {
        return false;
    }
    uint8_t *bytes = record;
    const uint32_t previous = load_u32_le(&bytes[0x2D0u]);
    const uint32_t elapsed = now - previous;
    if (elapsed >= UINT32_C(86400)) {
        clear_bytes(bytes, 0x2D0u);
        return true;
    }
    if (elapsed > 1u) {
        uint32_t slot = previous / UINT32_C(30) + 1u;
        const uint32_t end = now / UINT32_C(30);
        while (slot < end) {
            if (!gomore_primitives_packed_2bit_set(
                    bytes, 0x2D0u, slot, bytes[0x2D4u])) {
                return false;
            }
            ++slot;
        }
    }
    return true;
}

float gomore_primitives_centered_ratio(int32_t first, int32_t middle,
                                      int32_t last) {
    const uint32_t wrapped =
        ((uint32_t)first + (uint32_t)last - (uint32_t)middle * 2u) * 2u;
    const int32_t denominator = (int32_t)wrapped;
    const float magnitude = denominator < 0
        ? -(float)denominator : (float)denominator;
    if ((int32_t)float_bits(magnitude) < INT32_C(0x358637BD)) {
        return 0.0f;
    }
    const int32_t numerator = (int32_t)((uint32_t)first - (uint32_t)last);
    return (float)numerator / (float)denominator;
}

bool gomore_primitives_iir_filter_apply(void *state, size_t state_length,
                                       float *values, size_t count) {
    if (state == NULL || (values == NULL && count != 0u) ||
            state_length < 0x44u) {
        return false;
    }
    uint8_t *bytes = state;
    const int32_t order = (int32_t)load_u32_le(bytes);
    const size_t required_length = order > 0
        ? 0x40u + (size_t)order * 4u : 0x44u;
    if (order < 0 || order > 11 || state_length < required_length) {
        return false;
    }
    for (size_t sample = 0u; sample < count; ++sample) {
        float output = bits_float(load_u32_le(&bytes[0x1Cu])) * values[sample];
        for (int32_t index = 1; index <= order; ++index) {
            const size_t input_history = 0x30u + (size_t)(index - 1) * 4u;
            const size_t input_coefficient = 0x1Cu + (size_t)index * 4u;
            const size_t output_history = 0x40u + (size_t)(index - 1) * 4u;
            const size_t output_coefficient = 8u + (size_t)index * 4u;
            output += bits_float(load_u32_le(&bytes[input_history])) *
                      bits_float(load_u32_le(&bytes[input_coefficient]));
            output -= bits_float(load_u32_le(&bytes[output_history])) *
                      bits_float(load_u32_le(&bytes[output_coefficient]));
        }
        for (int32_t index = order - 1; index > 0; --index) {
            store_u32_le(&bytes[0x30u + (size_t)index * 4u],
                         load_u32_le(&bytes[0x30u +
                                            (size_t)(index - 1) * 4u]));
            store_u32_le(&bytes[0x40u + (size_t)index * 4u],
                         load_u32_le(&bytes[0x40u +
                                            (size_t)(index - 1) * 4u]));
        }
        store_u32_le(&bytes[0x30u], float_bits(values[sample]));
        store_u32_le(&bytes[0x40u], float_bits(output));
        values[sample] = output;
    }
    store_u32_le(&bytes[4], 1u);
    return true;
}

float gomore_primitives_thresholded_mean5(float threshold,
                                          const float values[5],
                                          const float comparisons[5]) {
    if (values == NULL || comparisons == NULL) {
        return 0.0f;
    }
    float sum = 0.0f;
    int32_t included = 0;
    for (size_t index = 0u; index < 5u; ++index) {
        if (comparisons[index] >= threshold) {
            sum += values[index];
            ++included;
        }
    }
    return sum / (float)included;
}

float gomore_primitives_magnitude_score10(float threshold,
                                         const float values[10]) {
    if (values == NULL) {
        return 0.0f;
    }
    float score = 0.0f;
    const float limit = bits_float(UINT32_C(0x400851EC));
    const float factor = bits_float(UINT32_C(0x4273E706));
    for (size_t index = 0u; index < 10u; ++index) {
        float magnitude = values[index] < 0.0f ? -values[index] : values[index];
        if ((int32_t)float_bits(magnitude) > INT32_C(0x400851EC)) {
            magnitude = limit;
        } else if (magnitude < threshold) {
            magnitude = 0.0f;
        }
        const float contribution = magnitude * factor;
        if (contribution >= 0.0f) {
            score += contribution;
        }
    }
    return score;
}

int32_t gomore_primitives_circular_count_predicate(
    const int16_t *values, size_t count, int32_t cursor,
    int32_t lookback, int32_t lower, int32_t upper,
    uint8_t comparison, int32_t required) {
    if (values == NULL || count == 0u || count > 127u || cursor < 0 ||
            cursor >= (int32_t)count || lookback < 0) {
        return -1;
    }
    int32_t matches = 0;
    for (int32_t offset = 1; offset <= lookback; ++offset) {
        int32_t index = cursor - offset;
        if (index < 0) {
            index += (int32_t)count;
        }
        const int32_t value = values[index];
        if (value > lower && value < upper) {
            ++matches;
        }
    }
    if (comparison == UINT8_C(0x3E)) {
        return matches >= required ? 1 : -1;
    }
    if (comparison == UINT8_C(0x3C)) {
        return matches < required ? 1 : -1;
    }
    return -1;
}

bool gomore_primitives_run_length_encode_2bit(
    const int8_t *values, size_t count,
    uint8_t *output, size_t capacity, size_t *written) {
    if (output == NULL || written == NULL ||
            (values == NULL && count != 0u)) {
        return false;
    }
    *written = 0u;
    if (count == 0u) {
        return true;
    }
    int8_t current = values[0];
    uint8_t run_minus_one = UINT8_C(0xFF);
    for (size_t index = 0u; index < count; ++index) {
        ++run_minus_one;
        if (values[index] != current || run_minus_one > UINT8_C(0x3E)) {
            if (*written >= capacity) {
                return false;
            }
            output[(*written)++] = (uint8_t)((uint8_t)current & UINT8_C(3)) |
                (uint8_t)((run_minus_one & UINT8_C(0x3F)) << 2u);
            current = values[index];
            run_minus_one = 0u;
        }
        if (index == count - 1u) {
            if (*written >= capacity) {
                return false;
            }
            output[(*written)++] = (uint8_t)((uint8_t)current & UINT8_C(3)) |
                (uint8_t)(((uint8_t)(run_minus_one + 1u) & UINT8_C(0x3F)) << 2u);
        }
    }
    return true;
}

bool gomore_primitives_propagate_packed_status(
    void *state, size_t length, uint8_t *value) {
    if (state == NULL || length < 1001u || value == NULL) {
        return false;
    }
    uint8_t *bytes = state;
    if (bytes[1000] != 0u) {
        const uint32_t slot = load_u32_le(&bytes[0x2D0u]) / UINT32_C(30);
        uint8_t previous = 0u;
        if (!gomore_primitives_packed_2bit_get(
                bytes, 0x2D0u, (slot - 2u) % UINT32_C(0xB40), &previous) ||
            !gomore_primitives_packed_2bit_set(
                bytes, 0x2D0u, (slot - 1u) % UINT32_C(0xB40), previous)) {
            return false;
        }
        *value = previous;
        bytes[1000] = 0u;
    }
    return true;
}

bool gomore_primitives_filter_bank_initialize(
    void *record, size_t length,
    gomore_primitives_mode_lt2_init_fn initialize_lt2,
    gomore_primitives_mode2_init_fn initialize_mode2) {
    if (record == NULL || length < 0x140u || initialize_lt2 == NULL ||
            initialize_mode2 == NULL) {
        return false;
    }
    uint8_t *bytes = record;
    const float first_parameters[2] = {
        bits_float(UINT32_C(0x3C2A64C3)),
        bits_float(UINT32_C(0x3F75C28F))
    };
    if (!gomore_primitives_mode_state_configure(
            bytes, length, 2u, 2u, first_parameters,
            initialize_lt2, initialize_mode2)) {
        return false;
    }
    const float remaining_parameters[2] = {
        bits_float(UINT32_C(0x3F75C28F)), 0.0f
    };
    for (size_t index = 1u; index < 4u; ++index) {
        if (!gomore_primitives_mode_state_configure(
                &bytes[index * 0x50u], length - index * 0x50u,
                0u, 2u, remaining_parameters,
                initialize_lt2, initialize_mode2)) {
            return false;
        }
    }
    return true;
}

bool gomore_primitives_target_runs(
    int8_t target, const int8_t *values, size_t count,
    uint16_t (*runs)[2], size_t run_capacity,
    size_t *run_count, size_t *match_count) {
    if ((values == NULL && count != 0u) || runs == NULL ||
            run_count == NULL || match_count == NULL) {
        return false;
    }
    *run_count = 0u;
    *match_count = 0u;
    int32_t previous = -1;
    const size_t stock_capacity = run_capacity < 40u ? run_capacity : 40u;
    for (size_t index = 0u; index < count; ++index) {
        if (values[index] == target && *run_count < stock_capacity) {
            if (previous == target) {
                runs[*run_count - 1u][1] = (uint16_t)(index + 1u);
            } else {
                runs[*run_count][0] = (uint16_t)index;
                runs[*run_count][1] = (uint16_t)(index + 1u);
                ++*run_count;
            }
            ++*match_count;
        }
        previous = values[index];
    }
    return true;
}

bool gomore_primitives_shift_marked_history(uint8_t *values,
                                            size_t capacity,
                                            size_t *count,
                                            size_t shift) {
    if (values == NULL || count == NULL || *count > capacity ||
            shift > capacity - *count) {
        return false;
    }
    if (shift == 0u) {
        return true;
    }
    for (size_t remaining = *count; remaining != 0u; --remaining) {
        values[remaining - 1u + shift] = values[remaining - 1u];
    }
    clear_bytes(values, shift);
    *count += shift;
    size_t marked = 0u;
    for (size_t index = 0u; index < *count && values[index] != 2u &&
            marked < 21u; ++index) {
        if (values[index] != 0u) {
            values[index] = 2u;
            ++marked;
        }
    }
    return true;
}

bool gomore_primitives_register_mode_topics(
    uintptr_t context, uintptr_t mode4_handler, uintptr_t mode3_handler,
    gomore_primitives_topic_register_fn register_topic) {
    if (register_topic == NULL) {
        return false;
    }
    register_topic(4u, mode4_handler, context);
    register_topic(3u, mode3_handler, context);
    return true;
}

float gomore_primitives_exponential_affine(
    float value, float scale, float center, float offset,
    gomore_primitives_float_unary_fn exponential) {
    if (exponential == NULL) {
        return 0.0f;
    }
    return exponential((value - center) * scale) + offset;
}

int32_t gomore_primitives_seed_and_test_text_class(
    const uint8_t *text, size_t text_length,
    const uint8_t classes[256],
    const void *source_record, size_t source_length,
    void *destination_record, size_t destination_length,
    gomore_primitives_seed_fn seed) {
    if ((text == NULL && text_length != 0u) || classes == NULL ||
            source_record == NULL || source_length < 0x10u ||
            destination_record == NULL || destination_length < 0x10u ||
            seed == NULL) {
        return -1;
    }
    const uint8_t *source = source_record;
    uint8_t *destination = destination_record;
    const uint32_t seed_value = load_u32_le(&source[0x0Cu]);
    store_u32_le(&destination[0x0Cu], seed_value);
    seed(seed_value);
    return gomore_primitives_all_class_0x20(text, text_length, classes) != 0
        ? -1004 : 0;
}

int32_t gomore_primitives_validate_record_bytes(
    const uint8_t *candidate, size_t candidate_length,
    const void *source_record, size_t source_length,
    void *destination_record, size_t destination_length) {
    if (candidate == NULL || source_record == NULL || source_length < 9u ||
            destination_record == NULL || destination_length < 0x10u) {
        return -1;
    }
    const uint8_t *source = source_record;
    const size_t compare_length = source[8];
    if (compare_length > candidate_length ||
            compare_length > source_length - 4u) {
        return -1;
    }
    for (size_t index = 0u; index < compare_length; ++index) {
        if (source[4u + index] != candidate[index]) {
            store_u32_le(&((uint8_t *)destination_record)[0x0Cu], 0u);
            return -1005;
        }
    }
    return 0;
}

int32_t gomore_primitives_validate_su_signature(
    const uint8_t *candidate, size_t candidate_length,
    void *destination_record, size_t destination_length) {
    static const uint8_t signature[3] = {'S', 'U', 0u};
    if (candidate == NULL || candidate_length < sizeof(signature) ||
            destination_record == NULL || destination_length < 0x10u) {
        return -1;
    }
    for (size_t index = 0u; index < sizeof(signature); ++index) {
        if (candidate[index] != signature[index]) {
            store_u32_le(&((uint8_t *)destination_record)[0x0Cu], 0u);
            return -1007;
        }
    }
    return 0;
}

bool gomore_primitives_sps_engine_initialize(
    void *record, size_t length, uint32_t binding,
    gomore_primitives_void_context_fn finish_initialize) {
    if (record == NULL || length < 0x58u || finish_initialize == NULL) {
        return false;
    }
    uint8_t *bytes = record;
    store_u32_le(&bytes[0], 0u);
    store_u32_le(&bytes[4], 0u);
    store_u32_le(&bytes[8], 0u);
    store_u32_le(&bytes[0x24u], 1u);
    store_u32_le(&bytes[0x40u], binding);
    store_u16_le_early(&bytes[0x50u], 8u);
    store_u32_le(&bytes[0x44u], 0u);
    store_u32_le(&bytes[0x48u], 0u);
    store_u32_le(&bytes[0x3Cu], 0u);
    store_u32_le(&bytes[0x34u], UINT32_C(0x3F800000));
    store_u32_le(&bytes[0x38u], 0u);
    store_u32_le(&bytes[0x20u], 0u);
    store_u32_le(&bytes[0x18u], UINT32_C(0x3F800000));
    store_u32_le(&bytes[0x1Cu], 0u);
    if (!gomore_primitives_sps_state_reset(record, length)) {
        return false;
    }
    finish_initialize(record);
    return true;
}

int32_t gomore_primitives_state_mode_dispatch(
    void *state, size_t state_length, int32_t mode, uint8_t value,
    gomore_primitives_state_byte_fn mode0,
    gomore_primitives_state_byte_fn mode1,
    gomore_primitives_state_call_fn mode2,
    gomore_primitives_state_call_fn mode3) {
    if (state == NULL) {
        return -1;
    }
    uint8_t *bytes = state;
    int32_t status = -1;
    if (mode == 0 && state_length >= 0xD15u && mode0 != NULL) {
        status = mode0(&bytes[0xD14u], value);
    } else if (mode == 1 && state_length >= 0x13F9u && mode1 != NULL) {
        status = mode1(&bytes[0x13F8u], value);
    } else if (mode == 2 && state_length >= 0xD99u && mode2 != NULL) {
        status = mode2(&bytes[0xD98u]);
    } else if (mode == 3 && state_length >= 0x391Du && mode3 != NULL) {
        status = mode3(&bytes[0x391Cu]);
    }
    return status == 0 ? 0 : -1;
}

bool gomore_primitives_commit_valid_time_record_adapter(
    void *engine, size_t engine_length,
    void *destination, size_t destination_length,
    const void *record, size_t record_length) {
    if (engine == NULL || engine_length < 0x126Cu) {
        return false;
    }
    return gomore_primitives_commit_valid_time_record(
        &((uint8_t *)engine)[0x1130u], engine_length - 0x1130u,
        destination, destination_length, record, record_length);
}

float gomore_primitives_one_minus(float value) {
    return 1.0f - value;
}

float gomore_primitives_logistic(
    float value, gomore_primitives_float_unary_fn exponential) {
    if (exponential == NULL) {
        return 0.0f;
    }
    return 1.0f / (exponential(-value) + 1.0f);
}

float gomore_primitives_scaled_product(float first, float second) {
    const double scaled = (double)first * 2.8;
    const double product = scaled * (double)second;
    return (float)(product / 200.0);
}

int32_t gomore_primitives_linear_sign_classify(
    float first, float second, float third, int32_t integer,
    const float coefficients[4], float bias) {
    if (coefficients == NULL) {
        return -1;
    }
    float sum = coefficients[0] * (float)integer;
    sum += first * coefficients[1];
    sum += second * coefficients[2];
    sum += third * coefficients[3];
    sum += bias;
    return sum >= 0.0f ? -1 : 1;
}

int32_t gomore_primitives_validate_key_and_update_status(
    const uint8_t *candidate, size_t candidate_length,
    const void *configuration, size_t configuration_length,
    void *state, size_t state_length,
    void *status_record, size_t status_length,
    gomore_primitives_simple_fn prepare,
    gomore_primitives_random_fn random_value) {
    if (candidate == NULL || configuration == NULL ||
            configuration_length < 9u || state == NULL ||
            state_length < 0x14u || status_record == NULL ||
            status_length < 12u) {
        return -1;
    }
    const uint8_t *config = configuration;
    const size_t compare_length = config[8];
    if (compare_length > candidate_length ||
            compare_length > configuration_length - 4u) {
        return -1;
    }
    uint8_t *state_bytes = state;
    uint8_t *status = status_record;
    state_bytes[0x10u] = (uint8_t)(state_bytes[0x10u] + 1u);
    const int32_t comparison = gomore_primitives_nullable_compare_n(
        &config[4], candidate, compare_length);
    if (comparison != 0) {
        store_u16_le_early(&status[6], (uint16_t)(int16_t)-1005);
        const int32_t result = gomore_primitives_status_or_random(
            state_bytes, state_length, status, status_length,
            prepare, random_value);
        store_u16_le_early(&state_bytes[4], (uint16_t)result);
        store_u32_le(&state_bytes[8], 0u);
        return -1005;
    }
    const int32_t result = gomore_primitives_status_or_random(
        state_bytes, state_length, status, status_length,
        prepare, random_value);
    store_u16_le_early(&state_bytes[4], (uint16_t)result);
    return 0;
}

int32_t gomore_primitives_decimal_config_update(
    const uint8_t *text,
    const void *configuration, size_t configuration_length,
    void *state, size_t state_length,
    void *status_record, size_t status_length,
    bool validation_enabled,
    gomore_primitives_simple_fn prepare,
    gomore_primitives_random_fn random_value) {
    if (text == NULL || configuration == NULL ||
            configuration_length < 0x10u || state == NULL ||
            state_length < 0x14u || status_record == NULL ||
            status_length < 12u) {
        return -1;
    }
    const uint32_t parsed = (uint32_t)gomore_primitives_decimal_parse(text);
    uint8_t *state_bytes = state;
    uint8_t *status = status_record;
    state_bytes[0x10u] = (uint8_t)(state_bytes[0x10u] + 1u);
    if (validation_enabled) {
        const uint32_t cap = parsed <= UINT32_C(0x6953F6FF)
            ? parsed : UINT32_C(0x6953F6FF);
        const uint32_t configured =
            load_u32_le(&((const uint8_t *)configuration)[0x0Cu]);
        if (cap < configured || configured < UINT32_C(0x688A4180)) {
            store_u16_le_early(&status[8], (uint16_t)(int16_t)-1006);
            const int32_t result = gomore_primitives_status_or_random(
                state_bytes, state_length, status, status_length,
                prepare, random_value);
            store_u16_le_early(&state_bytes[4], (uint16_t)result);
            store_u32_le(&state_bytes[8], 0u);
            return -1006;
        }
    }
    const int32_t result = gomore_primitives_status_or_random(
        state_bytes, state_length, status, status_length,
        prepare, random_value);
    store_u16_le_early(&state_bytes[4], (uint16_t)result);
    store_u32_le(&state_bytes[8], parsed);
    return 0;
}

int32_t gomore_primitives_runtime_version_validate(
    uint32_t value, bool allow_missing_runtime, bool validation_enabled,
    uint32_t configured_limit, bool runtime_present,
    int16_t configured_version, int16_t runtime_version) {
    int32_t status = 0;
    if (validation_enabled &&
            (configured_limit <= value || value <= UINT32_C(0x688A4180))) {
        status = -1006;
    }
    if (!allow_missing_runtime && !runtime_present) {
        return -1;
    }
    if (configured_version != runtime_version) {
        return -1008;
    }
    return status;
}

bool gomore_primitives_dominant_sorted_i32(
    int32_t *values, size_t count,
    int32_t *dominant_value, size_t *dominant_count) {
    if (values == NULL || count == 0u || dominant_value == NULL ||
            dominant_count == NULL) {
        return false;
    }
    for (size_t index = 1u; index < count; ++index) {
        const int32_t value = values[index];
        size_t position = index;
        while (position != 0u && values[position - 1u] > value) {
            values[position] = values[position - 1u];
            --position;
        }
        values[position] = value;
    }
    int32_t current_value = values[0];
    size_t current_count = 1u;
    *dominant_value = current_value;
    *dominant_count = 1u;
    for (size_t index = 1u; index < count; ++index) {
        const int32_t next_value = values[index];
        if (next_value == current_value) {
            ++current_count;
        }
        if (next_value != current_value || index == count - 1u) {
            if (current_count >= *dominant_count) {
                *dominant_count = current_count;
                *dominant_value = current_value;
            }
            current_value = next_value;
            current_count = 1u;
        }
    }
    return true;
}

int32_t gomore_primitives_circular_signal_predicate(
    const int16_t *primary, const int16_t *first,
    const int16_t *second, const int16_t *third,
    size_t count, int32_t cursor, size_t lookback) {
    if (primary == NULL || first == NULL || second == NULL || third == NULL ||
            count == 0u || count > 127u || lookback > count ||
            cursor < 0 || cursor >= (int32_t)count) {
        return -1;
    }
    int32_t primary_matches = 0;
    int32_t combined_matches = 0;
    for (size_t offset = 1u; offset <= lookback; ++offset) {
        int32_t index = cursor - (int32_t)offset;
        if (index < 0) {
            index += (int32_t)count;
        }
        if (primary[index] > 200) {
            ++primary_matches;
        }
        const int32_t combined = (int32_t)first[index] +
                                 (int32_t)second[index] +
                                 (int32_t)third[index];
        if (combined > 180) {
            ++combined_matches;
        }
    }
    return primary_matches >= 3 && combined_matches >= 3 ? 1 : -1;
}

float gomore_primitives_average_sign_crossing_spacing(
    const float *values, size_t count) {
    if (values == NULL || count < 2u) {
        return -1.0f;
    }
    int32_t first_crossing = -1;
    int32_t last_crossing = -1;
    int32_t crossing_divisor = -1;
    for (size_t index = 0u; index + 1u < count; ++index) {
        if (values[index] * values[index + 1u] < 0.0f) {
            if (first_crossing == -1) {
                first_crossing = (int32_t)index;
            }
            last_crossing = (int32_t)index;
            ++crossing_divisor;
        }
    }
    if (crossing_divisor <= 0) {
        return -1.0f;
    }
    return (float)(last_crossing - first_crossing) /
           (float)crossing_divisor;
}

float gomore_primitives_round_decimal_places(
    float value, float places,
    gomore_primitives_float_binary_fn power) {
    if (power == NULL) {
        return 0.0f;
    }
    const float scale = power(10.0f, places);
    if (scale == 0.0f) {
        return 0.0f;
    }
    const float adjusted = value >= 0.0f
        ? value * scale + 0.5f
        : value * scale - bits_float(UINT32_C(0x3ECCCCCD));
    int32_t converted;
    if (adjusted != adjusted || adjusted >= 2147483648.0f ||
            adjusted < -2147483648.0f) {
        converted = INT32_MIN;
    } else {
        converted = (int32_t)adjusted;
    }
    return (float)converted / scale;
}

bool gomore_primitives_time_engine_initialize(
    void *state, size_t state_length,
    uint8_t *configuration, size_t configuration_length,
    uint32_t configuration_binding) {
    if (state == NULL || state_length < 0x13Cu || configuration == NULL ||
            configuration_length < 10u) {
        return false;
    }
    uint8_t *bytes = state;
    clear_bytes(bytes, 0x13Cu);
    if (configuration[0] == 0u) {
        configuration[0] = 1u;
        store_u16_le_early(&configuration[2], 15u);
        store_u16_le_early(&configuration[4], 120u);
        configuration[6] = 0u;
        configuration[7] = 0u;
        configuration[8] = 20u;
        configuration[9] = 8u;
    }
    store_u32_le(&bytes[0x138u], configuration_binding);
    if (bytes[0xB8u] == 0u) {
        store_u32_le(&bytes[0xB0u], 600u);
    }
    if (!gomore_primitives_clear_90(&bytes[0x48u],
                                    state_length - 0x48u) ||
            !gomore_primitives_clear_72(bytes, state_length)) {
        return false;
    }
    store_u32_le(&bytes[0x130u], load_u32_le(&configuration[2]));
    store_u32_le(&bytes[0x134u], load_u32_le(&configuration[6]));
    return true;
}

bool gomore_primitives_interval_nonzero_argmax(
    const float *values, size_t value_count,
    const uint8_t *boundaries, size_t boundary_count,
    uint8_t *output, size_t output_capacity, size_t *output_count) {
    if (values == NULL || boundaries == NULL || boundary_count == 0u ||
            boundary_count > 256u || output == NULL || output_count == NULL ||
            *output_count > output_capacity) {
        return false;
    }
    for (size_t index = 0u; index + 1u < boundary_count; ++index) {
        const int32_t begin = boundaries[index];
        const int32_t end = boundaries[index + 1u];
        if ((double)(end - begin) >= 7.5) {
            continue;
        }
        if (begin < 0 || end <= begin || (size_t)end > value_count) {
            continue;
        }
        const size_t selected = gomore_primitives_float_argmax_range(
            values, value_count, (size_t)begin, (size_t)end);
        if (selected != SIZE_MAX && values[selected] != 0.0f) {
            if (*output_count >= output_capacity || selected > UINT8_MAX) {
                return false;
            }
            output[(*output_count)++] = (uint8_t)selected;
        }
    }
    return true;
}

int32_t gomore_primitives_sequence_replay(
    void *state, size_t state_length,
    void *record, size_t record_length,
    gomore_primitives_record_step_fn process_record) {
    if (state == NULL || state_length < 0x54u || record == NULL ||
            record_length < 8u || process_record == NULL) {
        return -1;
    }
    uint8_t *state_bytes = state;
    uint8_t *record_bytes = record;
    uint32_t base = load_u32_le(&state_bytes[0x48u]);
    uint32_t sequence = load_u32_le(&record_bytes[4]);
    if (base == UINT32_MAX) {
        base = sequence;
        store_u32_le(&state_bytes[0x48u], base);
    }
    const uint32_t difference = sequence - base;
    uint32_t iterations;
    if (difference - 2u < 14u) {
        iterations = difference;
        store_u32_le(&state_bytes[0x4Cu], iterations);
        sequence = base + 1u;
        store_u32_le(&record_bytes[4], sequence);
    } else if (difference == 1u || sequence == base) {
        iterations = 1u;
        store_u32_le(&state_bytes[0x4Cu], iterations);
    } else {
        store_u16_le_early(&state_bytes[0x52u],
                           (uint16_t)(int16_t)-1027);
        return -1027;
    }
    int32_t status = -1016;
    for (uint32_t index = 0u; index < iterations; ++index) {
        status = process_record(state, record);
        if (iterations != 1u) {
            sequence = load_u32_le(&record_bytes[4]) + 1u;
            store_u32_le(&record_bytes[4], sequence);
        }
    }
    store_u32_le(&state_bytes[0x48u], load_u32_le(&record_bytes[4]));
    return status;
}

bool gomore_primitives_state_window_predicate(bool requested_active,
                                              uint32_t now,
                                              uint32_t last_transition,
                                              bool flag_a8,
                                              bool flag_a9) {
    if (!requested_active) {
        return flag_a8 || flag_a9;
    }
    return (flag_a8 || flag_a9) &&
           now - last_transition > UINT32_C(300);
}

static char hex_digit(uint32_t nibble) {
    return (char)(nibble < 10u ? (uint32_t)'0' + nibble
                              : (uint32_t)'a' + (nibble - 10u));
}

static void store_hex8(uint8_t *destination, uint32_t value) {
    for (size_t index = 0u; index < 8u; ++index) {
        const uint32_t shift = (uint32_t)((7u - index) * 4u);
        destination[index] = (uint8_t)hex_digit((value >> shift) & 0x0Fu);
    }
}

bool gomore_primitives_key_or_cached_copy(
    uint8_t *destination, size_t capacity,
    bool cache_valid, const uint8_t *cache, size_t cache_length,
    uint32_t device_id_0, uint32_t device_id_1, uint32_t address_word,
    size_t *written) {
    if (destination == NULL || written == NULL) {
        return false;
    }
    if (cache_valid) {
        if ((cache == NULL && cache_length != 0u) || cache_length > capacity) {
            return false;
        }
        for (size_t index = 0u; index < cache_length; ++index) {
            destination[index] = cache[index];
        }
        *written = cache_length;
        return true;
    }
    if (capacity < 25u) {
        return false;
    }
    store_hex8(&destination[0], address_word);
    store_hex8(&destination[8], device_id_0);
    store_hex8(&destination[16], device_id_1);
    destination[24] = 0u;
    *written = 24u;
    return true;
}

void gomore_primitives_slot_state_transition(uint8_t *state,
                                             uint8_t requested,
                                             bool guarded_mode) {
    if (state == NULL) {
        return;
    }
    if (guarded_mode) {
        if (*state == 4u) {
            if (requested == 5u) {
                *state = 1u;
            }
        } else {
            *state = requested;
        }
    } else if (*state != 3u && *state != 4u) {
        *state = requested;
    }
}

int32_t gomore_primitives_copy_key_blob(
    uint8_t *destination, size_t capacity,
    bool cache_valid, const uint8_t *cache,
    gomore_primitives_blob_loader_fn loader, void *loader_context) {
    if (destination == NULL || capacity < 0x40u) {
        return -2;
    }
    uint8_t loaded[0x40];
    const uint8_t *source = cache;
    if (!cache_valid) {
        if (loader == NULL || !loader(loader_context, loaded, sizeof(loaded))) {
            return -2;
        }
        source = loaded;
    }
    if (source == NULL) {
        return -2;
    }
    for (size_t index = 0u; index < 0x40u; ++index) {
        destination[index] = source[index];
    }
    return 0x40;
}

bool gomore_primitives_stage_32_and_consume(
    uintptr_t first, uintptr_t second, const uint8_t *source,
    size_t source_length, uintptr_t fourth, uintptr_t fifth,
    gomore_primitives_stage_consumer_fn consumer) {
    if (source == NULL || source_length < 32u || consumer == NULL) {
        return false;
    }
    uint8_t staged[32];
    clear_bytes(staged, sizeof(staged));
    for (size_t index = 0u; index < sizeof(staged); ++index) {
        staged[index] = source[index];
    }
    consumer(first, second, staged, fourth, fifth);
    return true;
}

float gomore_primitives_mean(const float *values, size_t count) {
    if (values == NULL || count == 0u) {
        return 0.0f;
    }
    float sum = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        sum += values[index];
    }
    return sum / (float)count;
}

int32_t gomore_primitives_argmax_from_zero(const float *values, size_t count) {
    if (values == NULL || count == 0u || count > (size_t)INT32_MAX) {
        return -1;
    }
    int32_t result = (int32_t)(count - 1u);
    float largest = 0.0f;
    for (size_t remaining = count; remaining != 0u; --remaining) {
        const size_t index = remaining - 1u;
        if (values[index] > largest) {
            largest = values[index];
            result = (int32_t)index;
        }
    }
    return result;
}

bool gomore_primitives_reset_provider_state(
    uint8_t *state, size_t length, bool active,
    gomore_primitives_mode_fn set_mode,
    gomore_primitives_void_context_fn release,
    void *release_context, gomore_primitives_init_fn initialize) {
    if (state == NULL || length < 0x2E0u || release == NULL ||
            initialize == NULL || (active && set_mode == NULL)) {
        return false;
    }
    if (active) {
        set_mode(4u, 0u);
    }
    release(release_context);
    clear_bytes(state, 0x2E0u);
    initialize(1u);
    return true;
}

bool gomore_primitives_sample_plausible(const uint8_t sample[4]) {
    return sample != NULL && sample[0] > 10u && sample[0] < 100u &&
           sample[1] < 2u && sample[2] > 100u && sample[2] < 0xDCu &&
           sample[3] > 0x1Eu && sample[3] < 0x96u;
}

bool gomore_primitives_stamp_time_record(
    uint8_t *record, size_t length,
    gomore_primitives_time_fn time_provider,
    gomore_primitives_offset_fn offset_provider,
    gomore_primitives_sync_state_fn sync_provider,
    void *provider_context) {
    if (record == NULL || length < 0x31u || time_provider == NULL ||
            offset_provider == NULL || sync_provider == NULL) {
        return false;
    }
    store_u32_le(&record[0], time_provider(provider_context));
    const uint16_t offset = offset_provider(provider_context);
    record[4] = (uint8_t)(offset & UINT16_C(0xFF));
    record[5] = (uint8_t)(offset >> 8);
    record[0x1Du] = 1u;
    record[0x30u] = sync_provider(provider_context) == 0 ? 1u : 0u;
    return true;
}

uint32_t gomore_primitives_clamp_hysteresis(uint32_t value,
                                            uint32_t baseline) {
    if (value == 0u) {
        return 1u;
    }
    if (value <= baseline + 3u && baseline <= value + 3u) {
        return baseline + 1u;
    }
    return value;
}

uint32_t gomore_primitives_parameter_commit(
    uint8_t *state, size_t length, uint32_t value,
    gomore_primitives_parameter_validate_fn validate,
    void *validate_context) {
    if (state == NULL || length <= 0x20F5u || validate == NULL ||
            !validate(validate_context, value)) {
        return UINT32_C(0x40);
    }
    state[0x20F5u] = (uint8_t)value;
    return 0u;
}

static bool records_any_enabled_bit(const uint8_t *records,
                                    size_t record_bytes, uint8_t mask) {
    if (records == NULL ||
            record_bytes < GOMORE_PRIMITIVES_RECORD_COUNT *
                               GOMORE_PRIMITIVES_RECORD_STRIDE) {
        return false;
    }
    for (size_t index = 0u; index < GOMORE_PRIMITIVES_RECORD_COUNT; ++index) {
        const uint8_t flags =
            records[index * GOMORE_PRIMITIVES_RECORD_STRIDE];
        if ((flags & 1u) != 0u && (flags & mask) != 0u) {
            return true;
        }
    }
    return false;
}

bool gomore_primitives_records_any_bit2(const uint8_t *records,
                                        size_t record_bytes) {
    return records_any_enabled_bit(records, record_bytes, UINT8_C(0x04));
}

bool gomore_primitives_records_any_bit4(const uint8_t *records,
                                        size_t record_bytes) {
    return records_any_enabled_bit(records, record_bytes, UINT8_C(0x10));
}

bool gomore_primitives_records_any_bit3(const uint8_t *records,
                                        size_t record_bytes) {
    return records_any_enabled_bit(records, record_bytes, UINT8_C(0x08));
}

bool gomore_primitives_records_any_bit1(const uint8_t *records,
                                        size_t record_bytes) {
    return records_any_enabled_bit(records, record_bytes, UINT8_C(0x02));
}

int32_t gomore_primitives_quantized_argmin(const float *values,
                                           uint32_t begin,
                                           uint32_t end_exclusive) {
    if (values == NULL || end_exclusive < begin ||
            begin > (uint32_t)INT32_MAX) {
        return -1;
    }
    uint32_t result = begin;
    int32_t threshold = (int32_t)values[begin];
    for (uint32_t index = begin; index < end_exclusive; ++index) {
        if (values[index] < (float)threshold) {
            threshold = (int32_t)values[index];
            result = index;
        }
    }
    return (int32_t)result;
}

uint32_t gomore_primitives_max_difference_index(const float *values,
                                                uint32_t begin,
                                                uint32_t end_exclusive) {
    if (values == NULL || begin >= end_exclusive) {
        return UINT32_MAX;
    }
    uint32_t result = begin;
    float largest = values[begin + 1u] - values[begin];
    for (uint32_t index = begin; index < end_exclusive; ++index) {
        const float difference = values[index + 1u] - values[index];
        if (difference > largest) {
            largest = difference;
            result = index & UINT32_C(0xFFFF);
        }
    }
    return result;
}

bool gomore_primitives_median(float *values, size_t count,
                              gomore_primitives_qsort_fn qsort_provider,
                              gomore_primitives_compare_fn compare,
                              float *result) {
    if (values == NULL || count == 0u || qsort_provider == NULL ||
            compare == NULL || result == NULL) {
        return false;
    }
    qsort_provider(values, count, sizeof(*values), compare);
    const size_t middle = count / 2u;
    *result = (count & 1u) != 0u
        ? values[middle]
        : (values[middle - 1u] + values[middle]) * 0.5f;
    return true;
}

bool gomore_primitives_standard_deviation(
    const float *values, size_t count,
    gomore_primitives_float_binary_fn pow_provider,
    gomore_primitives_float_unary_fn sqrt_provider,
    float *result) {
    if (values == NULL || count == 0u || pow_provider == NULL ||
            sqrt_provider == NULL || result == NULL) {
        return false;
    }
    const float mean = gomore_primitives_mean(values, count);
    float sum = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        sum += pow_provider(values[index] - mean, 2.0f);
    }
    const float variance = count == 1u ? 0.0f : sum / (float)(count - 1u);
    *result = sqrt_provider(variance);
    return true;
}

bool gomore_primitives_logistic_score(
    float scale, float bias, float feature, float coefficient,
    gomore_primitives_float_unary_fn exp_provider, float *result) {
    if (exp_provider == NULL || result == NULL) {
        return false;
    }
    const float exponent = exp_provider((feature - 64.0f) * scale);
    float logistic = 0.0f;
    if (exponent + 1.0f != 0.0f) {
        logistic = 0.15000000596046448f / (exponent + 1.0f);
    }
    *result = logistic + 0.7749999761581421f + bias +
              feature * coefficient;
    return true;
}

bool gomore_primitives_modulo5_record(uint8_t *record, size_t length,
                                      uint8_t secondary,
                                      uint8_t primary) {
    if (record == NULL || length < 0x2Fu || record[0x28u] >= 20u) {
        return false;
    }
    const uint8_t counter = record[0x28u];
    if ((counter % 5u) == 0u) {
        const size_t slot = (size_t)(counter / 5u);
        record[0x29u + slot] = primary == UINT8_C(0xFF) ? 1u : primary;
        record[0x2Du + (slot & 1u)] =
            secondary == UINT8_C(0xFF) ? 1u : secondary;
    }
    record[0x28u] = (uint8_t)((counter + 1u) % 20u);
    return true;
}

static uint16_t load_u16_le(const uint8_t *bytes) {
    return (uint16_t)((uint16_t)bytes[0] | ((uint16_t)bytes[1] << 8));
}

static void store_u16_le(uint8_t *bytes, uint16_t value) {
    bytes[0] = (uint8_t)(value & UINT16_C(0xFF));
    bytes[1] = (uint8_t)(value >> 8);
}

bool gomore_primitives_compact_25_windows(uint8_t *records,
                                         size_t record_capacity,
                                         uint8_t *record_count,
                                         uint32_t current_window) {
    if (records == NULL || record_count == NULL ||
            (size_t)*record_count > record_capacity) {
        return false;
    }
    if (*record_count == 0u || current_window <= 20u) {
        return true;
    }
    size_t drop = 0u;
    while (drop < (size_t)*record_count &&
            load_u16_le(&records[drop * 16u + 2u]) < 25u) {
        ++drop;
    }
    const size_t retained = (size_t)*record_count - drop;
    for (size_t index = 0u; index < retained; ++index) {
        uint8_t *destination = &records[index * 16u];
        const uint8_t *source = &records[(index + drop) * 16u];
        for (size_t byte = 0u; byte < 16u; ++byte) {
            destination[byte] = source[byte];
        }
        for (size_t field = 0u; field < 3u; ++field) {
            const uint16_t adjusted = (uint16_t)(
                load_u16_le(&destination[field * 2u]) - UINT16_C(25));
            store_u16_le(&destination[field * 2u], adjusted);
        }
    }
    *record_count = (uint8_t)retained;
    return true;
}

bool gomore_primitives_decimated_ring_write(float value, uint8_t ring[90],
                                            uint32_t begin_tick,
                                            uint32_t end_tick) {
    if (ring == NULL || end_tick < begin_tick) {
        return false;
    }
    uint32_t elapsed = end_tick - begin_tick;
    const uint8_t previous = ring[(elapsed / 10u) % 90u];
    if (!gomore_primitives_float_in_encoded_range(value)) {
        value = 0.0f;
    }
    ring[(end_tick / 10u) % 90u] = (uint8_t)value;
    if (begin_tick > 899u) {
        clear_bytes(ring, 90u);
        return true;
    }
    for (elapsed += 10u; elapsed < end_tick; elapsed += 10u) {
        ring[(elapsed / 10u) % 90u] = previous;
    }
    return true;
}

int32_t gomore_primitives_csv4_prefix_compare(
    const uint8_t *pattern, size_t pattern_length,
    const uint8_t *candidate, size_t candidate_length) {
    if ((pattern == NULL && pattern_length != 0u) ||
            (candidate == NULL && candidate_length != 0u)) {
        return -1;
    }
    uint8_t buffer[48];
    clear_bytes(buffer, sizeof(buffer));
    const size_t copied = candidate_length < 48u ? candidate_length : 47u;
    for (size_t index = 0u; index < copied; ++index) {
        buffer[index] = candidate[index];
    }
    buffer[copied] = 0u;

    /* Stock passed the original length to the comma counter after truncating
     * into this 48-byte local.  Lengths above 48 therefore read beyond the
     * stack object.  Count only admitted bytes while retaining its 4-field
     * result for every defined stock input. */
    size_t fields = 1u;
    for (size_t index = 0u; index < copied; ++index) {
        if (buffer[index] == UINT8_C(0x2C)) {
            ++fields;
        }
    }
    if (fields != 4u) {
        return -1;
    }

    size_t token_begin = 0u;
    while (token_begin < copied &&
            buffer[token_begin] == UINT8_C(0x2C)) {
        ++token_begin;
    }
    if (token_begin >= copied || buffer[token_begin] == 0u) {
        return 0;
    }
    size_t token_end = token_begin;
    while (token_end < copied && buffer[token_end] != 0u &&
            buffer[token_end] != UINT8_C(0x2C)) {
        ++token_end;
    }
    for (size_t index = 0u; index < pattern_length; ++index) {
        const uint8_t left = pattern[index];
        const uint8_t right = token_begin + index < token_end
            ? buffer[token_begin + index] : 0u;
        if (left != right || left == 0u) {
            const int32_t difference = (int32_t)left - (int32_t)right;
            const uint8_t low = (uint8_t)((uint32_t)difference & UINT32_C(0xFF));
            return low < UINT8_C(0x80)
                ? (int32_t)low : (int32_t)low - 256;
        }
    }
    return 0;
}

bool gomore_primitives_sleep_engine_open(
    void *state, size_t state_length,
    gomore_primitives_tensor_construct_binding_fn construct_tensor) {
    if (state == NULL || state_length < 0x20F0u ||
            construct_tensor == NULL) {
        return false;
    }
    uint8_t *bytes = state;
    if (bytes[0x3E8u] == 1u) {
        (void)gomore_primitives_clear_flag_1000(bytes, state_length);
    }
    clear_bytes(&bytes[0x55Cu], 0x1B90u);
    const uint16_t dimensions[2] = {1u, 90u};
    const uint32_t tensor_binding = construct_tensor(
        &bytes[0x55Cu], 0x1B90u, 2u, dimensions, 2u);
    store_u32_le(&bytes[0x20ECu], tensor_binding);
    store_u32_le(&bytes[0x554u], 0u);
    store_u32_le(&bytes[0x558u], 0u);
    bytes[0x3E8u] = 1u;
    bytes[0x3E9u] = 0u;
    store_u16_le_early(&bytes[0x3E6u], 0u);
    bytes[0x3EAu] = 0u;
    clear_bytes(&bytes[0x2D6u], 0x110u);
    return true;
}

bool gomore_primitives_shift_negated_filter_history(
    void *state, size_t state_length,
    const float input[25], bool zero_fill,
    gomore_primitives_filter_apply_fn apply_filter) {
    if (state == NULL || state_length < 0x6C0u ||
            (!zero_fill && (input == NULL || apply_filter == NULL))) {
        return false;
    }
    uint8_t *bytes = state;
    float *history = (float *)(void *)&bytes[0x2D8u];
    for (size_t index = 0u; index < 225u; ++index) {
        history[index] = history[index + 25u];
    }
    for (size_t index = 0u; index < 25u; ++index) {
        history[225u + index] = zero_fill ? 0.0f : -input[index];
    }
    if (!zero_fill) {
        apply_filter(state, &history[225u], 25u);
    }
    return true;
}

bool gomore_primitives_log_u32(
    const gomore_primitives_log_config *configuration,
    uint32_t level, uint32_t category,
    const char *format, uint32_t value) {
    if (configuration == NULL || !configuration->enabled ||
            configuration->emit == NULL || level >= 32u || category >= 32u ||
            (configuration->level_mask & (UINT32_C(1) << level)) == 0u ||
            ((uint32_t)configuration->category_mask &
             (UINT32_C(1) << category)) == 0u) {
        return false;
    }
    if (configuration->format_u32 == NULL || format == NULL) {
        return false;
    }
    char message[256];
    clear_bytes((uint8_t *)message, sizeof(message));
    static const char prefix[8] = {'[', 'G', 'o', 'M', 'o', 'R', 'e', ']'};
    for (size_t index = 0u; index < sizeof(prefix); ++index) {
        message[index] = prefix[index];
    }
    const uint32_t formatted = configuration->format_u32(
        &message[8], 248u, format, value);
    message[255] = '\0';
    /* Stock appended CRLF whenever the formatter reported <248 characters,
     * which overflows its 256-byte aggregate buffer for lengths 246/247.
     * Preserve the suffix for every fitting result and keep the local bound. */
    if (formatted <= 245u) {
        const size_t end = 8u + (size_t)formatted;
        message[end] = '\r';
        message[end + 1u] = '\n';
        message[end + 2u] = '\0';
    }
    configuration->emit("%s", message);
    return true;
}

bool gomore_primitives_accelerometer_resample25(
    void *filter_states, size_t filter_state_length,
    const float *const sources[3], size_t source_count,
    int32_t sample_count,
    float *const destinations[3], size_t destination_count,
    uint8_t *failed, uint32_t *status,
    gomore_primitives_resample_fn resample,
    gomore_primitives_filter_apply_fn apply_filter,
    const gomore_primitives_log_config *logger) {
    if (filter_states == NULL || filter_state_length < 0x140u ||
            sources == NULL || source_count < 3u || destinations == NULL ||
            destination_count < 3u || failed == NULL || status == NULL ||
            resample == NULL || apply_filter == NULL) {
        return false;
    }
    for (size_t axis = 0u; axis < 3u; ++axis) {
        if (destinations[axis] == NULL ||
                (sample_count != 0 && sources[axis] == NULL)) {
            return false;
        }
    }
    for (size_t axis = 0u; axis < 3u; ++axis) {
        clear_bytes((uint8_t *)destinations[axis], 25u * sizeof(float));
    }
    *failed = 0u;
    *status = 0u;
    if (sample_count == 0) {
        *status = UINT32_C(0x20);
        *failed = 1u;
    } else {
        uint8_t *states = filter_states;
        for (size_t axis = 0u; axis < 3u; ++axis) {
            (void)gomore_primitives_resample25_and_filter(
                &states[0x50u + axis * 0x50u], sources[axis], sample_count,
                sample_count, destinations[axis], resample, apply_filter);
        }
    }
    (void)gomore_primitives_log_u32(
        logger, 2u, 2u, "[SnP][ACC]status:%u\r\n", *status);
    return true;
}
