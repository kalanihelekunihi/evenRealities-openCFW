/*
 * Clean-room implementation correlated to Goodix-candidate functions in
 * the R1 application image.  Recovered behavior comes from Ghidra output and
 * fresh Thumb-2 disassembly of rebuilt-application.bin; this file contains no
 * Goodix binary, absolute firmware pointer, or copied vendor source.
 */

#include "goodix_primitives/goodix_primitives.h"

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(offsetof(goodix_primitives_record_pair_owner, records) == 0x08u,
               "outer record-pair records +0x08");
_Static_assert(offsetof(goodix_primitives_record_pair_owner, scratch) == 0x18u,
               "outer record-pair scratch +0x18");
_Static_assert(sizeof(goodix_primitives_record_pair_owner) == 0x1Cu,
               "outer record-pair owner is 0x1C bytes");
_Static_assert(sizeof(goodix_primitives_outer_session) == 0xD4u,
               "recovered outer Goodix session is 0xD4 bytes");
_Static_assert(offsetof(goodix_primitives_outer_session, processing_record) == 0x0Cu,
               "outer processing record +0x0C");
_Static_assert(offsetof(goodix_primitives_outer_session, record_pair) == 0x6Cu,
               "outer record pair +0x6C");
_Static_assert(offsetof(goodix_primitives_outer_session, aggregate) == 0x88u,
               "outer aggregate +0x88");
_Static_assert(offsetof(goodix_primitives_outer_session, owned_float) == 0xA8u,
               "outer owned float +0xA8");
_Static_assert(offsetof(goodix_primitives_outer_session, buffer_record) == 0xACu,
               "outer buffer record +0xAC");
_Static_assert(offsetof(goodix_primitives_outer_session, model) == 0xB0u,
               "outer model owner +0xB0");
_Static_assert(offsetof(goodix_primitives_outer_session, channel_records) == 0xD0u,
               "outer channel records +0xD0");
#endif

static bool copy_version(char *destination, size_t capacity,
                         const char *version, size_t stock_limit) {
    if (destination == NULL || capacity == 0u || version == NULL) {
        return false;
    }
    size_t count = capacity < stock_limit ? capacity : stock_limit;
    for (size_t index = 0u; index < count; ++index) {
        destination[index] = version[index];
    }
    destination[count - 1u] = '\0';
    return true;
}

bool goodix_primitives_copy_preprocess_version(char *destination,
                                               size_t capacity) {
    static const char version[14] = "pre_pv_v1.1.0";
    return copy_version(destination, capacity, version, sizeof(version));
}

bool goodix_primitives_copy_process_version(char *destination,
                                            size_t capacity) {
    static const char version[10] = "pv_v1.1.0";
    return copy_version(destination, capacity, version, sizeof(version));
}

bool goodix_primitives_dispatch_state(
    uint32_t *record,
    const goodix_primitives_state_handler_fn
        handlers[GOODIX_PRIMITIVES_STATE_COUNT]) {
    if (record == NULL || handlers == NULL ||
            record[0] >= GOODIX_PRIMITIVES_STATE_COUNT ||
            handlers[record[0]] == NULL) {
        return false;
    }
    handlers[record[0]](record);
    return true;
}

bool goodix_primitives_record_initialize(uint8_t *record, size_t length) {
    if (record == NULL || length < GOODIX_PRIMITIVES_RECORD_BYTES) {
        return false;
    }
    record[0] = 0u;
    record[1] = 0u;
    for (size_t index = 0u; index < 32u; ++index) {
        record[index + 3u] = UINT8_C(0xFF);
    }
    return true;
}

bool goodix_primitives_record_initialize_once(uint8_t *record, size_t length) {
    if (record == NULL || length < GOODIX_PRIMITIVES_RECORD_BYTES) {
        return false;
    }
    if (record[0] == 0u) {
        (void)goodix_primitives_record_initialize(record, length);
        record[1] = 1u;
        record[0x0Bu] = 1u;
        record[0x13u] = 0u;
    }
    return true;
}

int32_t goodix_primitives_initialize_device(
    uint16_t device_id, goodix_primitives_device_initialize_fn initialize) {
    if (initialize == NULL) {
        return -1;
    }
    return initialize(device_id) == 0 ? 0 : -1;
}

void goodix_primitives_select_fixed_pair(bool alternate,
                                         uint32_t *first,
                                         uint32_t *second) {
    if (first == NULL || second == NULL) {
        return;
    }
    if (alternate) {
        *first = UINT32_C(0x00F33333);
        *second = UINT32_C(0x00C00000);
    } else {
        *first = UINT32_C(0x00ECCCCD);
        *second = UINT32_C(0x00A66666);
    }
}

bool goodix_primitives_reset_state_record(uint8_t *record, size_t length) {
    if (record == NULL || length < 0x18u) {
        return false;
    }
    record[0] = UINT8_C(0xFF);
    record[1] = 0u;
    record[0x0Eu] = 0u;
    record[0x0Fu] = 0u;
    for (size_t index = 0x14u; index < 0x18u; ++index) {
        record[index] = 0u;
    }
    return true;
}

bool goodix_primitives_clear_state_flags(uint8_t *record, size_t length) {
    if (record == NULL || length < 8u) {
        return false;
    }
    record[5] = 0u;
    record[6] = 0u;
    record[7] = 0u;
    return true;
}

bool goodix_primitives_call_hook(goodix_primitives_hook_fn hook) {
    if (hook == NULL) {
        return false;
    }
    hook();
    return true;
}

uint32_t goodix_primitives_library_code(void) {
    return UINT32_C(0x12F9);
}

uint32_t goodix_primitives_constant_four(void) {
    return 4u;
}

uint32_t goodix_primitives_constant_one_a(void) {
    return 1u;
}

uint32_t goodix_primitives_constant_one_b(void) {
    return 1u;
}

const void *goodix_primitives_table_9d640(
    const goodix_primitives_tables *tables) {
    return tables == NULL ? NULL : tables->table_9d640;
}

const void *goodix_primitives_table_a04cc(
    const goodix_primitives_tables *tables) {
    return tables == NULL ? NULL : tables->table_a04cc;
}

const void *goodix_primitives_table_a50b0(
    const goodix_primitives_tables *tables) {
    return tables == NULL ? NULL : tables->table_a50b0;
}

const void *goodix_primitives_table_a692c(
    const goodix_primitives_tables *tables) {
    return tables == NULL ? NULL : tables->table_a692c;
}

const void *goodix_primitives_table_ad1ac(
    const goodix_primitives_tables *tables) {
    return tables == NULL ? NULL : tables->table_ad1ac;
}

const void *goodix_primitives_table_ad13c(
    const goodix_primitives_tables *tables) {
    return tables == NULL ? NULL : tables->table_ad13c;
}

const void *goodix_primitives_table_ad160(
    const goodix_primitives_tables *tables) {
    return tables == NULL ? NULL : tables->table_ad160;
}

bool goodix_primitives_buffer_record_initialize(
    goodix_primitives_buffer_record *record,
    goodix_primitives_allocate_fn allocate, void *allocate_context) {
    if (record == NULL || allocate == NULL) {
        return false;
    }
    record->buffer = allocate(allocate_context, 0x40u);
    if (record->buffer == NULL) {
        return false;
    }
    for (size_t index = 0u; index < 0x40u; ++index) {
        record->buffer[index] = 0u;
    }
    record->reserved_04 = 0u;
    record->flag_05 = 0u;
    record->flag_06 = 0u;
    record->reserved_07 = 0u;
    return true;
}

bool goodix_primitives_buffer_record_create(
    goodix_primitives_buffer_record **record,
    goodix_primitives_allocate_fn allocate, void *allocate_context) {
    if (record == NULL || allocate == NULL) {
        return false;
    }
    *record = allocate(allocate_context,
                       sizeof(goodix_primitives_buffer_record));
    return *record != NULL && goodix_primitives_buffer_record_initialize(
                                  *record, allocate, allocate_context);
}

bool goodix_primitives_buffer_record_destroy(
    goodix_primitives_buffer_record **record,
    goodix_primitives_release_fn release, void *release_context) {
    if (record == NULL || release == NULL) {
        return false;
    }
    if (*record != NULL) {
        if ((*record)->buffer != NULL) {
            release(release_context, (*record)->buffer);
            (*record)->buffer = NULL;
        }
        release(release_context, *record);
        *record = NULL;
    }
    return true;
}

bool goodix_primitives_integer_max_index(const int32_t *values, size_t count,
                                         int32_t *maximum, size_t *index) {
    if (values == NULL || count == 0u || maximum == NULL || index == NULL) {
        return false;
    }
    int32_t best = values[0];
    size_t best_index = 0u;
    for (size_t current = 1u; current < count; ++current) {
        if (values[current] > best) {
            best = values[current];
            best_index = current;
        }
    }
    *maximum = best;
    *index = best_index;
    return true;
}

bool goodix_primitives_copy_dlcom_version(char *destination,
                                         size_t capacity) {
    static const char version[] = "dlCom_pre2exc_pv_v1.3.0_c00c91c9";
    if (destination == NULL || capacity < sizeof(version)) {
        return false;
    }
    for (size_t index = 0u; index < sizeof(version); ++index) {
        destination[index] = version[index];
    }
    return true;
}

bool goodix_primitives_copy_dsp_version(char *destination,
                                        size_t capacity) {
    static const char version[] = "dsp_pv_v1.3.0_30234f22";
    if (destination == NULL || capacity < sizeof(version)) {
        return false;
    }
    for (size_t index = 0u; index < sizeof(version); ++index) {
        destination[index] = version[index];
    }
    return true;
}

static bool goodix_primitives_append_string(char *destination,
                                            size_t capacity,
                                            size_t *length,
                                            const char *source) {
    if (destination == NULL || length == NULL || source == NULL ||
            *length >= capacity) {
        return false;
    }
    size_t source_length = 0u;
    while (source[source_length] != '\0') {
        ++source_length;
    }
    if (source_length > capacity - *length - 1u) {
        return false;
    }
    for (size_t index = 0u; index < source_length; ++index) {
        destination[*length + index] = source[index];
    }
    *length += source_length;
    destination[*length] = '\0';
    return true;
}

bool goodix_primitives_build_spo2_version(char *destination,
                                          size_t capacity,
                                          const char *weights_version) {
    if (destination == NULL || capacity == 0u || weights_version == NULL) {
        return false;
    }
    char dsp_version[23];
    char dlcom_version[33];
    if (!goodix_primitives_copy_dsp_version(
            dsp_version, sizeof(dsp_version)) ||
            !goodix_primitives_copy_dlcom_version(
                dlcom_version, sizeof(dlcom_version))) {
        return false;
    }
    destination[0] = '\0';
    size_t length = 0u;
    static const char *const parts_before_dsp[] = {
        "GH_SPO2_pre_pv_v2.1.10.0", "(", NULL, ")", "_", "nc", "_",
        "277e89de", "\n", "net_", "1f1cf98b", "\n",
    };
    for (size_t index = 0u;
            index < sizeof(parts_before_dsp) / sizeof(parts_before_dsp[0]);
            ++index) {
        const char *part = parts_before_dsp[index];
        if (part == NULL) {
            part = weights_version;
        }
        if (!goodix_primitives_append_string(
                destination, capacity, &length, part)) {
            destination[0] = '\0';
            return false;
        }
    }
    if (!goodix_primitives_append_string(
            destination, capacity, &length, dsp_version) ||
            !goodix_primitives_append_string(
                destination, capacity, &length, "\n") ||
            !goodix_primitives_append_string(
                destination, capacity, &length, dlcom_version)) {
        destination[0] = '\0';
        return false;
    }
    return true;
}

bool goodix_primitives_word_window_push(goodix_primitives_word_window *window,
                                        uint32_t value) {
    if (window == NULL || window->values == NULL || window->capacity == 0u ||
            window->count > window->capacity) {
        return false;
    }
    if (window->count < window->capacity) {
        window->values[window->count] = value;
        ++window->count;
        return true;
    }
    for (size_t index = 1u; index < window->capacity; ++index) {
        window->values[index - 1u] = window->values[index];
    }
    window->values[window->capacity - 1u] = value;
    return true;
}

bool goodix_primitives_logistic_score(
    float value, float threshold, float lower_scale, float upper_scale,
    goodix_primitives_float_unary_fn exp_provider, float *result) {
    if (exp_provider == NULL || result == NULL) {
        return false;
    }
    const float scale = value >= threshold ? upper_scale : lower_scale;
    *result = 100.0f /
              (exp_provider(-(scale * (value - threshold))) + 1.0f);
    return true;
}

void goodix_primitives_noop_a(void) {}

void goodix_primitives_noop_b(void) {}

int32_t goodix_primitives_zero_a(void) {
    return 0;
}

int32_t goodix_primitives_zero_b(void) {
    return 0;
}

uint32_t goodix_primitives_second_word(const uint32_t *words) {
    return words == NULL ? 0u : words[1];
}

bool goodix_primitives_transformed_differs(
    int32_t value, goodix_primitives_i32_unary_fn transform) {
    return transform != NULL && transform(value) != value;
}

uint32_t goodix_primitives_integrity_encode(uint32_t value) {
    static const uint32_t parity_masks[4] = {
        UINT32_C(0x6B851EB7), UINT32_C(0x4147AE13),
        UINT32_C(0x28F5C28F), UINT32_C(0x15C28F5B),
    };
    uint32_t bits = ((value & UINT32_C(0x00FFFFFF)) >> 1u) ^
        parity_masks[(value & 7u) >> 1u];
    uint32_t parity = 0u;
    while (bits != 0u) {
        bits &= bits - 1u;
        parity = (parity + 1u) & UINT32_C(0xFF);
    }
    return (value & UINT32_C(0xFFFFFFFE)) | (parity & 1u);
}

bool goodix_primitives_integrity_invalid(uint32_t value) {
    return goodix_primitives_integrity_encode(value) != value;
}

static uint32_t packed_to_f32_bits(uint16_t value, uint32_t exponent_bits,
                                   uint32_t fraction_bits,
                                   uint32_t exponent_bias,
                                   uint32_t subnormal_adjust) {
    const uint32_t word = value;
    const uint32_t exponent_mask = (UINT32_C(1) << exponent_bits) - 1u;
    const uint32_t fraction_mask = (UINT32_C(1) << fraction_bits) - 1u;
    const uint32_t exponent = (word >> fraction_bits) & exponent_mask;
    const uint32_t fraction = word & fraction_mask;
    const uint32_t sign = (word & UINT32_C(0x8000)) << 16u;
    if (exponent == 0u) {
        if (fraction == 0u) {
            return sign;
        }
        union {
            float f;
            uint32_t u;
        } converted;
        converted.f = (float)fraction;
        return sign | (converted.u + subnormal_adjust);
    }
    return sign | ((exponent + UINT32_C(127) - exponent_bias) << 23u) |
        (fraction << (23u - fraction_bits));
}

uint32_t goodix_primitives_packed_5_10_to_f32_bits(uint16_t value) {
    return packed_to_f32_bits(value, 5u, 10u, 15u, UINT32_C(0xF4000000));
}

uint32_t goodix_primitives_packed_6_9_to_f32_bits(uint16_t value) {
    return packed_to_f32_bits(value, 6u, 9u, 31u, UINT32_C(0xEC800000));
}

bool goodix_primitives_u32_to_u16_transform(
    uint16_t *destination, const uint32_t *source, size_t count,
    goodix_primitives_u32_to_u16_fn transform) {
    if (destination == NULL || source == NULL || transform == NULL) {
        return false;
    }
    for (size_t index = 0u; index < count; ++index) {
        destination[index] = transform(source[index]);
    }
    return true;
}

bool goodix_primitives_transform_in_place(
    int32_t *value, goodix_primitives_i32_unary_fn transform) {
    if (value == NULL || transform == NULL) {
        return false;
    }
    *value = transform(*value);
    return true;
}

int32_t goodix_primitives_initialize_status(
    goodix_primitives_status_fn initialize) {
    return initialize != NULL && initialize() == 0 ? 0 : -1;
}

bool goodix_primitives_is_evenly_divisible(uint32_t total,
                                            uint32_t divisor) {
    return divisor != 0u && total % divisor == 0u;
}

float goodix_primitives_unsigned_power(float base, uint8_t exponent) {
    float result = 1.0f;
    for (uint32_t index = 0u; index < exponent; ++index) {
        result *= base;
    }
    return result;
}

bool goodix_primitives_float_buffer_full(
    const goodix_primitives_float_buffer *buffer) {
    return buffer != NULL && buffer->count == buffer->capacity;
}

float goodix_primitives_float_buffer_get(
    const goodix_primitives_float_buffer *buffer, size_t index,
    float fallback) {
    if (buffer == NULL || buffer->values == NULL || index >= buffer->capacity) {
        return fallback;
    }
    return buffer->values[index];
}

int8_t goodix_primitives_centered_i8(int32_t value) {
    if (value < 0) {
        return INT8_MIN;
    }
    if (value >= 256) {
        return INT8_MAX;
    }
    return (int8_t)(value - 128);
}

float goodix_primitives_float_sum(const float *values, size_t count) {
    if (values == NULL) {
        return 0.0f;
    }
    float result = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        result += values[index];
    }
    return result;
}

bool goodix_primitives_decrement_counter(int32_t *counter) {
    if (counter == NULL) {
        return false;
    }
    if (*counter > 0) {
        --*counter;
    }
    return true;
}

void *goodix_primitives_tensor_descriptor_initialize(
    goodix_primitives_tensor_descriptor *descriptor, uint32_t batches,
    uint32_t rows, uint32_t columns, uint32_t element_bytes, void *data) {
    if (descriptor == NULL) {
        return NULL;
    }
    descriptor->element_bytes = element_bytes;
    descriptor->batches = batches;
    descriptor->rows = rows;
    descriptor->columns = columns;
    descriptor->data = data;
    return data;
}

uint32_t goodix_primitives_filter_code(uint32_t value) {
    return value == 5u ? value : 0u;
}

uint32_t goodix_primitives_word_window_last(
    const goodix_primitives_word_window *window, uint32_t fallback) {
    if (window == NULL || window->values == NULL || window->count == 0u) {
        return fallback;
    }
    return window->values[window->count - 1u];
}

uint16_t goodix_primitives_word_window_count(
    const goodix_primitives_word_window *window) {
    return window == NULL ? 0u : window->count;
}

bool goodix_primitives_store_version_qualifier(uint16_t *destination) {
    if (destination == NULL) {
        return false;
    }
    *destination = UINT16_C(0x636E);
    return true;
}

bool goodix_primitives_copy_process_version_v1_1(char *destination,
                                                 size_t capacity) {
    static const char version[10] = "pv_v1.1.0";
    return copy_version(destination, capacity, version, sizeof(version));
}

bool goodix_primitives_copy_process_version_v1_0(char *destination,
                                                 size_t capacity) {
    static const char version[10] = "pv_v1.0.0";
    return copy_version(destination, capacity, version, sizeof(version));
}

bool goodix_primitives_reverse_low_bits(uint32_t value, uint8_t bit_count,
                                        uint32_t *result) {
    if (result == NULL || bit_count > 32u) {
        return false;
    }
    uint32_t reversed = 0u;
    for (uint32_t remaining = bit_count; remaining != 0u; --remaining) {
        reversed |= (value & 1u) << (remaining - 1u);
        value >>= 1u;
    }
    *result = reversed;
    return true;
}

bool goodix_primitives_float_mean(const float *values, size_t count,
                                  float *result) {
    if (values == NULL || count == 0u || result == NULL) {
        return false;
    }
    *result = goodix_primitives_float_sum(values, count) / (float)count;
    return true;
}

float goodix_primitives_sum_squares(const float *values, size_t count) {
    if (values == NULL) {
        return 0.0f;
    }
    float result = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        result += values[index] * values[index];
    }
    return result;
}

float goodix_primitives_dot_product(const float *left, const float *right,
                                    size_t count) {
    if (left == NULL || right == NULL) {
        return 0.0f;
    }
    float result = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        result += left[index] * right[index];
    }
    return result;
}

int32_t goodix_primitives_copy_indexed_record(
    const uint8_t *records, size_t record_count, int32_t index,
    uint8_t destination[32]) {
    if (records == NULL || destination == NULL || index < 0 ||
            (size_t)index >= record_count) {
        return INT32_C(0x10000003);
    }
    const size_t offset = (size_t)index * 32u;
    for (size_t byte = 0u; byte < 32u; ++byte) {
        destination[byte] = records[offset + byte];
    }
    return 0;
}

int32_t goodix_primitives_round_nearest(float value) {
    return (int32_t)(value + (value <= 0.0f ? -0.5f : 0.5f));
}

bool goodix_primitives_transform_packed24_lsb(
    uint8_t *records, size_t length, goodix_primitives_i32_unary_fn transform) {
    if (records == NULL || transform == NULL || length % 4u != 0u) {
        return false;
    }
    for (size_t offset = 0u; offset < length; offset += 4u) {
        const uint32_t packed = (uint32_t)records[offset + 1u] << 16u |
                                (uint32_t)records[offset + 2u] << 8u |
                                records[offset + 3u];
        records[offset + 3u] = (uint8_t)transform((int32_t)packed);
    }
    return true;
}

bool goodix_primitives_visit_packed24(
    const uint8_t *records, size_t length,
    goodix_primitives_i32_unary_fn visitor) {
    if (records == NULL || visitor == NULL || length % 4u != 0u) {
        return false;
    }
    for (size_t offset = 0u; offset < length; offset += 4u) {
        const uint32_t packed = (uint32_t)records[offset + 1u] << 16u |
                                (uint32_t)records[offset + 2u] << 8u |
                                records[offset + 3u];
        (void)visitor((int32_t)packed);
    }
    return true;
}

bool goodix_primitives_swap_u16_bytes(uint8_t *bytes, size_t length) {
    if (bytes == NULL || length % 2u != 0u) {
        return false;
    }
    for (size_t offset = 0u; offset < length; offset += 2u) {
        const uint8_t first = bytes[offset];
        bytes[offset] = bytes[offset + 1u];
        bytes[offset + 1u] = first;
    }
    return true;
}

bool goodix_primitives_i32_range(const int32_t *values, size_t count,
                                 int32_t *maximum, int32_t *minimum,
                                 int32_t *range) {
    if (values == NULL || count == 0u || range == NULL) {
        return false;
    }
    int32_t low = values[0];
    int32_t high = values[0];
    for (size_t index = 1u; index < count; ++index) {
        if (values[index] > high) {
            high = values[index];
        }
        if (values[index] < low) {
            low = values[index];
        }
    }
    const int64_t difference = (int64_t)high - (int64_t)low;
    if (difference > INT32_MAX) {
        return false;
    }
    if (maximum != NULL) {
        *maximum = high;
    }
    if (minimum != NULL) {
        *minimum = low;
    }
    *range = (int32_t)difference;
    return true;
}

bool goodix_primitives_processing_record_initialize(
    uint8_t *destination, size_t destination_length,
    const uint8_t *source, size_t source_length) {
    if (destination == NULL || source == NULL || destination_length < 96u ||
            source_length < 76u) {
        return false;
    }
    for (size_t index = 0u; index < 76u; ++index) {
        destination[index] = source[index];
    }
    const uint32_t source_word = (uint32_t)destination[4] |
        (uint32_t)destination[5] << 8u |
        (uint32_t)destination[6] << 16u |
        (uint32_t)destination[7] << 24u;
    const uint32_t tail[5] = {source_word / 25u, 5u, 25u, 1u, 25u};
    for (size_t word = 0u; word < 5u; ++word) {
        for (size_t byte = 0u; byte < 4u; ++byte) {
            destination[76u + word * 4u + byte] =
                (uint8_t)(tail[word] >> (byte * 8u));
        }
    }
    return true;
}

bool goodix_primitives_update_transition(uint8_t *record, size_t length,
                                         uint8_t state,
                                         uint8_t source_flag) {
    if (record == NULL || length < 7u) {
        return false;
    }
    record[4] = state;
    if (state == 0u) {
        record[5] = source_flag != 0u ? 1u : 0u;
    } else if (state == 1u) {
        record[5] = 0u;
        if (source_flag == 0u) {
            record[6] = 0u;
        } else {
            ++record[6];
        }
    }
    return true;
}

bool goodix_primitives_sort_floats(float *values, size_t count) {
    if (values == NULL && count != 0u) {
        return false;
    }
    for (size_t end = count; end > 1u; --end) {
        for (size_t index = 1u; index < end; ++index) {
            if (values[index] < values[index - 1u]) {
                const float temporary = values[index - 1u];
                values[index - 1u] = values[index];
                values[index] = temporary;
            }
        }
    }
    return true;
}

bool goodix_primitives_sorted_insert(float *values, size_t *count,
                                     size_t capacity, float value) {
    if (values == NULL || count == NULL || *count > capacity ||
            *count == capacity) {
        return false;
    }
    size_t index = *count;
    while (index > 0u && values[index - 1u] > value) {
        values[index] = values[index - 1u];
        --index;
    }
    values[index] = value;
    ++*count;
    return true;
}

float goodix_primitives_float_mean_or_zero(const float *values,
                                           size_t count) {
    return goodix_primitives_float_sum(values, count) /
           (float)(count == 0u ? 1u : count);
}

bool goodix_primitives_word_window_full(
    const goodix_primitives_word_window *window) {
    return window != NULL && window->count == window->capacity;
}

bool goodix_primitives_i16_mean(const int16_t *values, size_t count,
                                int16_t *result) {
    if (values == NULL || count == 0u || result == NULL) {
        return false;
    }
    int32_t sum = 0;
    for (size_t index = 0u; index < count; ++index) {
        sum += values[index];
    }
    *result = (int16_t)(sum / (int32_t)count);
    return true;
}

bool goodix_primitives_i16_min_index(const int16_t *values, size_t count,
                                     size_t *index) {
    if (values == NULL || count == 0u || index == NULL) {
        return false;
    }
    int16_t minimum = values[0];
    size_t minimum_index = 0u;
    for (size_t current = 1u; current < count; ++current) {
        if (values[current] < minimum) {
            minimum = values[current];
            minimum_index = current;
        }
    }
    *index = minimum_index;
    return true;
}

bool goodix_primitives_float_min_index(const float *values, size_t count,
                                       float *minimum, size_t *index) {
    if (values == NULL || count == 0u || minimum == NULL || index == NULL) {
        return false;
    }
    float best = values[0];
    size_t best_index = 0u;
    for (size_t current = 1u; current < count; ++current) {
        if (values[current] < best) {
            best = values[current];
            best_index = current;
        }
    }
    *minimum = best;
    *index = best_index;
    return true;
}

bool goodix_primitives_float_max_index(const float *values, size_t count,
                                       float *maximum, size_t *index) {
    if (values == NULL || count == 0u || maximum == NULL || index == NULL) {
        return false;
    }
    float best = values[0];
    size_t best_index = 0u;
    for (size_t current = 1u; current < count; ++current) {
        if (values[current] > best) {
            best = values[current];
            best_index = current;
        }
    }
    *maximum = best;
    *index = best_index;
    return true;
}

bool goodix_primitives_release_and_clear(
    void **allocation, goodix_primitives_release_fn release,
    void *release_context) {
    if (allocation == NULL || release == NULL) {
        return false;
    }
    if (*allocation != NULL) {
        release(release_context, *allocation);
        *allocation = NULL;
    }
    return true;
}

int32_t goodix_primitives_release_if_present(
    void *allocation, goodix_primitives_release_fn release,
    void *release_context) {
    if (allocation != NULL && release != NULL) {
        release(release_context, allocation);
    }
    return 0;
}

bool goodix_primitives_allocate_record_pair(
    size_t count, void **records, void **scratch,
    goodix_primitives_allocate_fn allocate, void *allocate_context) {
    if (records == NULL || scratch == NULL || allocate == NULL ||
            count > SIZE_MAX / 24u) {
        return false;
    }
    *records = allocate(allocate_context, count * 24u);
    *scratch = allocate(allocate_context, 24u);
    return *records != NULL && *scratch != NULL;
}

int32_t goodix_primitives_release_context_pair(
    void *context, void *owned_allocation,
    goodix_primitives_release_fn release, void *release_context) {
    if (context != NULL && release != NULL) {
        if (owned_allocation != NULL) {
            release(release_context, owned_allocation);
        }
        release(release_context, context);
    }
    return 0;
}

uintptr_t goodix_primitives_release_context_pair_vector(void) {
    return (uintptr_t)&goodix_primitives_release_context_pair;
}

float goodix_primitives_quartic_evaluate(
    float value, const int32_t coefficient_record[7]) {
    if (coefficient_record == NULL) {
        return 0.0f;
    }
    float fourth = (float)coefficient_record[2] * value;
    float third = (float)coefficient_record[3] * value;
    fourth *= value;
    third *= value;
    fourth *= value;
    fourth *= value;
    fourth += third * value;
    float second = (float)coefficient_record[4] * value;
    fourth += second * value;
    fourth += (float)coefficient_record[5] * value;
    fourth += (float)coefficient_record[6];
    return fourth / 10000.0f;
}

bool goodix_primitives_peak_select(
    float threshold_ratio, const float *values, int32_t value_count,
    int32_t begin, int32_t end, int32_t radius, int32_t capacity,
    int32_t *selected_indices, float *selected_values,
    int32_t *selected_count) {
    if (values == NULL || selected_indices == NULL || selected_values == NULL ||
            selected_count == NULL || value_count <= 0 || begin < 0 ||
            end < begin || end > value_count || radius < 0 || capacity <= 0) {
        return false;
    }

    float global_maximum = values[0];
    for (int32_t index = 1; index < value_count; ++index) {
        if (global_maximum < values[index]) {
            global_maximum = values[index];
        }
    }
    *selected_count = 0;
    int32_t current = begin;
    while (current < end) {
        int32_t lower = current - radius;
        if (lower < 0) {
            lower = 0;
        }
        const int64_t unbounded_upper64 = (int64_t)current + radius;
        const int32_t unbounded_upper =
            unbounded_upper64 > INT32_MAX ? INT32_MAX :
            (int32_t)unbounded_upper64;
        int32_t upper = unbounded_upper;
        if (upper >= value_count - 1) {
            upper = value_count - 1;
        }

        bool local_peak = true;
        for (int32_t index = lower; index < upper; ++index) {
            if ((index < current && values[index + 1] < values[index]) ||
                    (index >= current && values[index] < values[index + 1])) {
                local_peak = false;
                break;
            }
        }
        if (!local_peak) {
            ++current;
            continue;
        }

        const float candidate = values[current];
        if (candidate >= threshold_ratio * global_maximum) {
            int32_t position = *selected_count;
            while (position > 0 &&
                   values[selected_indices[position - 1]] < candidate) {
                --position;
            }
            if (position >= capacity) {
                position = capacity - 1;
            }
            int32_t move_count = *selected_count - position;
            const int32_t available = capacity - position - 1;
            if (move_count > available) {
                move_count = available;
            }
            for (int32_t offset = move_count; offset > 0; --offset) {
                selected_indices[position + offset] =
                    selected_indices[position + offset - 1];
            }
            selected_indices[position] = current;
            if (*selected_count < capacity) {
                ++*selected_count;
            }
        }
        if (unbounded_upper == INT32_MAX) {
            break;
        }
        current = unbounded_upper + 1;
    }

    for (int32_t index = 0; index < *selected_count; ++index) {
        selected_values[index] = values[selected_indices[index]];
    }
    return true;
}

bool goodix_primitives_buffer_descriptor_initialize(
    goodix_primitives_buffer_descriptor *descriptor, void *data,
    uint16_t capacity, size_t element_bytes,
    goodix_primitives_allocate_fn allocate, void *allocate_context) {
    if (descriptor == NULL || element_bytes == 0u ||
            (data == NULL && allocate == NULL) ||
            (size_t)capacity > SIZE_MAX / element_bytes) {
        return false;
    }
    const bool supplied = data != NULL;
    if (!supplied) {
        data = allocate(allocate_context, (size_t)capacity * element_bytes);
    }
    if (data == NULL && capacity != 0u) {
        return false;
    }
    descriptor->data = data;
    descriptor->count = 0u;
    descriptor->capacity = capacity;
    if (!supplied) {
        (void)goodix_primitives_byte_fill(
            0u, (uint8_t *)data, (size_t)capacity * element_bytes);
    }
    return true;
}

bool goodix_primitives_extended_descriptor_initialize(
    goodix_primitives_extended_descriptor *descriptor, void *data,
    uint16_t capacity, size_t element_bytes, uint8_t flag,
    goodix_primitives_allocate_fn allocate, void *allocate_context) {
    if (descriptor == NULL) {
        return false;
    }
    goodix_primitives_buffer_descriptor base;
    if (!goodix_primitives_buffer_descriptor_initialize(
            &base, data, capacity, element_bytes, allocate,
            allocate_context)) {
        return false;
    }
    descriptor->data = base.data;
    descriptor->count = base.count;
    descriptor->capacity = base.capacity;
    descriptor->auxiliary = 0u;
    descriptor->status = 0u;
    descriptor->flag = flag;
    return true;
}

bool goodix_primitives_float_descriptor_initialize(
    goodix_primitives_float_descriptor *descriptor, void *data,
    uint16_t capacity, uint8_t flag,
    goodix_primitives_allocate_fn allocate, void *allocate_context) {
    if (descriptor == NULL || (data == NULL && allocate == NULL)) {
        return false;
    }
    const bool supplied = data != NULL;
    if (!supplied) {
        data = allocate(allocate_context, (size_t)capacity * sizeof(float));
    }
    if (data == NULL && capacity != 0u) {
        return false;
    }
    if (!supplied) {
        (void)goodix_primitives_byte_fill(
            0u, (uint8_t *)data, (size_t)capacity * sizeof(float));
    }
    descriptor->data = data;
    descriptor->count = supplied ? capacity : 0u;
    descriptor->capacity = capacity;
    descriptor->flag = flag;
    descriptor->status = 0u;
    descriptor->auxiliary = 0u;
    descriptor->reserved = 0u;
    return true;
}

bool goodix_primitives_release_two_and_clear(
    void **first, void **second, goodix_primitives_release_fn release,
    void *release_context) {
    if (first == NULL || second == NULL || release == NULL) {
        return false;
    }
    (void)goodix_primitives_release_and_clear(
        first, release, release_context);
    (void)goodix_primitives_release_and_clear(
        second, release, release_context);
    return true;
}

bool goodix_primitives_release_two(
    void *first, void *second, goodix_primitives_release_fn release,
    void *release_context) {
    if (release == NULL) {
        return false;
    }
    if (first != NULL) {
        release(release_context, first);
    }
    if (second != NULL) {
        release(release_context, second);
    }
    return true;
}

bool goodix_primitives_byte_fill(uint8_t value, uint8_t *destination,
                                 size_t length) {
    if (destination == NULL && length != 0u) {
        return false;
    }
    for (size_t index = 0u; index < length; ++index) {
        destination[index] = value;
    }
    return true;
}

bool goodix_primitives_dual_buffer_descriptor_initialize(
    goodix_primitives_dual_buffer_descriptor *descriptor,
    uint32_t field_00, uint32_t field_04,
    uint32_t *primary, size_t primary_words,
    uint32_t *secondary, size_t secondary_words,
    uint32_t count, uint32_t field_14) {
    if (descriptor == NULL || primary == NULL || secondary == NULL ||
            (size_t)count > (SIZE_MAX - sizeof(uint32_t)) /
                                sizeof(uint32_t)) {
        return false;
    }
    const size_t required_words = (size_t)count + 1u;
    if (primary_words < required_words || secondary_words < required_words) {
        return false;
    }
    descriptor->field_00 = field_00;
    descriptor->field_04 = field_04;
    descriptor->primary = primary;
    descriptor->secondary = secondary;
    descriptor->count = count;
    descriptor->field_14 = field_14;
    const size_t bytes = (size_t)count * sizeof(uint32_t) +
                         sizeof(uint32_t);
    (void)goodix_primitives_byte_fill(0u, (uint8_t *)primary, bytes);
    (void)goodix_primitives_byte_fill(0u, (uint8_t *)secondary, bytes);
    return true;
}

bool goodix_primitives_float_storage_initialize(
    goodix_primitives_float_storage *storage, float *values,
    uint32_t capacity, goodix_primitives_allocate_fn allocate,
    void *allocate_context) {
    if (storage == NULL ||
            (values == NULL && allocate == NULL) ||
            (size_t)capacity > SIZE_MAX / sizeof(float)) {
        return false;
    }
    const bool supplied = values != NULL;
    if (!supplied) {
        values = allocate(allocate_context,
                          (size_t)capacity * sizeof(float));
        if (values == NULL && capacity != 0u) {
            return false;
        }
        (void)goodix_primitives_byte_fill(
            0u, (uint8_t *)values, (size_t)capacity * sizeof(float));
    }
    storage->values = values;
    storage->count = supplied ? capacity : 0u;
    storage->capacity = capacity;
    storage->limit = supplied ? capacity : 0u;
    return true;
}

bool goodix_primitives_pair_buffer_initialize(
    goodix_primitives_pair_buffer *buffer, uint32_t source_count,
    uint32_t metadata, goodix_primitives_allocate_fn allocate,
    void *allocate_context) {
    const uint32_t count = source_count >> 1u;
    if (buffer == NULL || allocate == NULL || count > UINT8_MAX ||
            (size_t)count > SIZE_MAX / 8u) {
        return false;
    }
    void *records = allocate(allocate_context, (size_t)count * 8u);
    if (records == NULL && count != 0u) {
        return false;
    }
    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)records, (size_t)count * 8u);
    buffer->count = (uint8_t)count;
    buffer->records = records;
    buffer->metadata = metadata;
    return true;
}

static void release_float_descriptor(
    goodix_primitives_float_descriptor *descriptor,
    goodix_primitives_release_fn release, void *release_context) {
    if (descriptor != NULL) {
        (void)goodix_primitives_release_and_clear(
            &descriptor->data, release, release_context);
    }
}

bool goodix_primitives_channel_state_release(
    goodix_primitives_channel_state *state,
    goodix_primitives_release_fn release, void *release_context) {
    if (state == NULL || release == NULL) {
        return false;
    }
    release_float_descriptor(&state->history, release, release_context);
    release_float_descriptor(&state->window, release, release_context);
    release_float_descriptor(&state->filtered, release, release_context);
    release_float_descriptor(&state->scalar, release, release_context);
    release_float_descriptor(&state->primary_buckets, release,
                             release_context);
    release_float_descriptor(&state->secondary_buckets, release,
                             release_context);
    return true;
}

bool goodix_primitives_channel_state_initialize(
    goodix_primitives_channel_state *state,
    uint32_t primary_divisor, uint32_t secondary_divisor,
    goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context) {
    if (state == NULL || allocate == NULL || release == NULL ||
            primary_divisor == 0u || secondary_divisor == 0u ||
            primary_divisor > UINT16_MAX - 12u) {
        return false;
    }
    *state = (goodix_primitives_channel_state){0};
    const uint16_t window_capacity =
        (uint16_t)(primary_divisor + 12u);
    const uint16_t primary_buckets =
        (uint16_t)(125u / primary_divisor);
    const uint16_t secondary_buckets =
        (uint16_t)(125u / secondary_divisor);
    const bool ok = goodix_primitives_float_descriptor_initialize(
                        &state->history, NULL, 25u, 1u, allocate,
                        provider_context) &&
                    goodix_primitives_float_descriptor_initialize(
                        &state->window, NULL, window_capacity, 1u, allocate,
                        provider_context) &&
                    goodix_primitives_float_descriptor_initialize(
                        &state->filtered, NULL, 25u, 1u, allocate,
                        provider_context) &&
                    goodix_primitives_float_descriptor_initialize(
                        &state->scalar, NULL, 1u, 1u, allocate,
                        provider_context) &&
                    goodix_primitives_float_descriptor_initialize(
                        &state->primary_buckets, NULL, primary_buckets, 1u,
                        allocate, provider_context) &&
                    goodix_primitives_float_descriptor_initialize(
                        &state->secondary_buckets, NULL, secondary_buckets,
                        1u, allocate, provider_context);
    if (!ok) {
        (void)goodix_primitives_channel_state_release(
            state, release, provider_context);
    }
    return ok;
}

bool goodix_primitives_session_state_release(
    goodix_primitives_session_state *state,
    goodix_primitives_release_fn release, void *release_context) {
    if (state == NULL || release == NULL) {
        return false;
    }
    (void)goodix_primitives_channel_state_release(
        &state->primary, release, release_context);
    (void)goodix_primitives_channel_state_release(
        &state->secondary, release, release_context);
    release_float_descriptor(&state->tail_a, release, release_context);
    release_float_descriptor(&state->tail_b, release, release_context);
    release_float_descriptor(&state->tail_c, release, release_context);
    (void)goodix_primitives_release_and_clear(
        &state->tail_d.data, release, release_context);
    return true;
}

bool goodix_primitives_session_state_initialize(
    goodix_primitives_session_state *state,
    uint32_t primary_divisor, uint32_t secondary_divisor,
    goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context) {
    if (state == NULL || allocate == NULL || release == NULL) {
        return false;
    }
    *state = (goodix_primitives_session_state){0};
    const bool ok = goodix_primitives_channel_state_initialize(
                        &state->primary, primary_divisor, secondary_divisor,
                        allocate, release, provider_context) &&
                    goodix_primitives_channel_state_initialize(
                        &state->secondary, primary_divisor,
                        secondary_divisor, allocate, release,
                        provider_context) &&
                    goodix_primitives_float_descriptor_initialize(
                        &state->tail_a, NULL, 125u, 1u, allocate,
                        provider_context) &&
                    goodix_primitives_float_descriptor_initialize(
                        &state->tail_b, NULL, 125u, 1u, allocate,
                        provider_context) &&
                    goodix_primitives_float_descriptor_initialize(
                        &state->tail_c, NULL, 125u, 1u, allocate,
                        provider_context) &&
                    goodix_primitives_extended_descriptor_initialize(
                        &state->tail_d, NULL, 125u, sizeof(uint16_t), 1u,
                        allocate, provider_context);
    if (!ok) {
        (void)goodix_primitives_session_state_release(
            state, release, provider_context);
    }
    return ok;
}

bool goodix_primitives_owned_float_record_destroy(
    goodix_primitives_owned_float_record **record,
    goodix_primitives_release_fn release, void *release_context) {
    if (record == NULL || release == NULL) {
        return false;
    }
    if (*record != NULL) {
        release_float_descriptor(
            &(*record)->samples, release, release_context);
        release(release_context, *record);
        *record = NULL;
    }
    return true;
}

bool goodix_primitives_owned_float_record_create(
    goodix_primitives_owned_float_record **record,
    uint16_t first_capacity, uint16_t second_capacity,
    goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context) {
    if (record == NULL || allocate == NULL || release == NULL) {
        return false;
    }
    *record = allocate(provider_context, sizeof(**record));
    if (*record == NULL) {
        return false;
    }
    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)*record, sizeof(**record));
    const uint16_t capacity =
        first_capacity < second_capacity ? second_capacity : first_capacity;
    if (!goodix_primitives_float_descriptor_initialize(
            &(*record)->samples, NULL, capacity, 1u, allocate,
            provider_context)) {
        (void)goodix_primitives_owned_float_record_destroy(
            record, release, provider_context);
        return false;
    }
    return true;
}

bool goodix_primitives_channel_record_array_destroy(
    goodix_primitives_channel_record **records, size_t count,
    bool enabled, goodix_primitives_release_fn release,
    void *release_context) {
    if (records == NULL || release == NULL) {
        return false;
    }
    if (!enabled) {
        return true;
    }
    if (*records != NULL) {
        for (size_t index = 0u; index < count; ++index) {
            release_float_descriptor(
                &(*records)[index].samples, release, release_context);
        }
        release(release_context, *records);
        *records = NULL;
    }
    return true;
}

bool goodix_primitives_channel_record_array_create(
    goodix_primitives_channel_record **records, size_t count,
    bool enabled, uint8_t tag, goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context) {
    if (records == NULL || allocate == NULL || release == NULL ||
            count > SIZE_MAX / sizeof(**records)) {
        return false;
    }
    if (!enabled) {
        return true;
    }
    *records = allocate(provider_context, count * sizeof(**records));
    if (*records == NULL && count != 0u) {
        return false;
    }
    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)*records, count * sizeof(**records));
    size_t initialized = 0u;
    while (initialized < count) {
        goodix_primitives_channel_record *record =
            &(*records)[initialized];
        record->status = 0u;
        record->lower = 0.0f;
        record->upper = 0.0f;
        record->tag = tag;
        if (!goodix_primitives_float_descriptor_initialize(
                &record->samples, NULL, 15u, 1u, allocate,
                provider_context)) {
            (void)goodix_primitives_channel_record_array_destroy(
                records, initialized, true, release, provider_context);
            return false;
        }
        ++initialized;
    }
    return true;
}

bool goodix_primitives_dual_i16_storage_initialize(
    goodix_primitives_dual_i16_storage *storage, uint32_t divisor,
    goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context) {
    if (storage == NULL || divisor == 0u || allocate == NULL ||
            release == NULL) {
        return false;
    }
    *storage = (goodix_primitives_dual_i16_storage){0};
    const uint16_t reduced_capacity = (uint16_t)(125u / divisor);
    const bool ok = goodix_primitives_buffer_descriptor_initialize(
                        &storage->full_rate, NULL, 125u, sizeof(uint16_t),
                        allocate, provider_context) &&
                    goodix_primitives_buffer_descriptor_initialize(
                        &storage->reduced_rate, NULL, reduced_capacity,
                        sizeof(uint16_t), allocate, provider_context);
    if (!ok) {
        (void)goodix_primitives_release_and_clear(
            &storage->full_rate.data, release, provider_context);
        (void)goodix_primitives_release_and_clear(
            &storage->reduced_rate.data, release, provider_context);
    }
    return ok;
}

bool goodix_primitives_session_aggregate_destroy(
    goodix_primitives_session_aggregate *aggregate,
    goodix_primitives_release_fn release, void *release_context) {
    if (aggregate == NULL || release == NULL) {
        return false;
    }
    if (aggregate->pair != NULL) {
        (void)goodix_primitives_release_and_clear(
            &aggregate->pair->first.data, release, release_context);
        (void)goodix_primitives_release_and_clear(
            &aggregate->pair->second.data, release, release_context);
        release(release_context, aggregate->pair);
        aggregate->pair = NULL;
    }
    (void)goodix_primitives_release_and_clear(
        &aggregate->auxiliary.full_rate.data, release, release_context);
    (void)goodix_primitives_release_and_clear(
        &aggregate->auxiliary.reduced_rate.data, release, release_context);
    if (aggregate->session != NULL) {
        (void)goodix_primitives_session_state_release(
            aggregate->session, release, release_context);
        release(release_context, aggregate->session);
        aggregate->session = NULL;
    }
    return true;
}

bool goodix_primitives_session_aggregate_create(
    goodix_primitives_session_aggregate *aggregate,
    uint32_t primary_divisor, uint32_t secondary_divisor,
    uint32_t auxiliary_divisor, goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context) {
    if (aggregate == NULL || allocate == NULL || release == NULL ||
            auxiliary_divisor == 0u) {
        return false;
    }
    *aggregate = (goodix_primitives_session_aggregate){0};
    aggregate->session = allocate(provider_context,
                                  sizeof(*aggregate->session));
    if (aggregate->session == NULL) {
        return false;
    }
    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)aggregate->session, sizeof(*aggregate->session));
    const bool session_ok = goodix_primitives_session_state_initialize(
        aggregate->session, primary_divisor, secondary_divisor, allocate,
        release, provider_context);
    const bool auxiliary_ok = session_ok &&
        goodix_primitives_dual_i16_storage_initialize(
            &aggregate->auxiliary, auxiliary_divisor, allocate, release,
            provider_context);
    if (auxiliary_ok) {
        aggregate->pair = allocate(provider_context,
                                   sizeof(*aggregate->pair));
    }
    if (!auxiliary_ok || aggregate->pair == NULL) {
        (void)goodix_primitives_session_aggregate_destroy(
            aggregate, release, provider_context);
        return false;
    }
    *aggregate->pair = (goodix_primitives_descriptor_pair){0};
    const bool pair_ok = goodix_primitives_buffer_descriptor_initialize(
                             &aggregate->pair->first, NULL, 20u,
                             sizeof(uint32_t), allocate, provider_context) &&
                         goodix_primitives_buffer_descriptor_initialize(
                             &aggregate->pair->second, NULL, 20u,
                             sizeof(uint32_t), allocate, provider_context);
    if (!pair_ok) {
        (void)goodix_primitives_session_aggregate_destroy(
            aggregate, release, provider_context);
    }
    return pair_ok;
}

static uint32_t goodix_primitives_load_u32_le(const uint8_t *bytes) {
    return (uint32_t)bytes[0] | ((uint32_t)bytes[1] << 8) |
           ((uint32_t)bytes[2] << 16) | ((uint32_t)bytes[3] << 24);
}

static bool goodix_primitives_preprocess_abi_matches(const char *abi_tag) {
    static const char expected[14] = "pre_pv_v1.1.0";
    if (abi_tag == NULL) {
        return false;
    }
    for (size_t index = 0u; index < sizeof(expected); ++index) {
        if (abi_tag[index] != expected[index]) {
            return false;
        }
    }
    return true;
}

bool goodix_primitives_outer_session_destroy(
    goodix_primitives_outer_session **session,
    goodix_primitives_release_fn release, void *release_context) {
    if (session == NULL || release == NULL) {
        return false;
    }
    goodix_primitives_outer_session *owned = *session;
    if (owned == NULL) {
        return true;
    }
    (void)goodix_primitives_release_two(
        owned->record_pair.records, owned->record_pair.scratch,
        release, release_context);
    owned->record_pair.records = NULL;
    owned->record_pair.scratch = NULL;
    (void)goodix_primitives_session_aggregate_destroy(
        &owned->aggregate, release, release_context);
    (void)goodix_primitives_owned_float_record_destroy(
        &owned->owned_float, release, release_context);
    quantized_runtime_goodix_model_owner_destroy(
        &owned->model, release, release_context);
    const size_t count =
        (size_t)goodix_primitives_load_u32_le(owned->processing_record);
    const bool enabled =
        goodix_primitives_load_u32_le(owned->processing_record + 28u) != 0u;
    (void)goodix_primitives_channel_record_array_destroy(
        &owned->channel_records, count, enabled, release, release_context);
    (void)goodix_primitives_buffer_record_destroy(
        &owned->buffer_record, release, release_context);
    release(release_context, owned);
    *session = NULL;
    return true;
}

bool goodix_primitives_outer_session_create(
    goodix_primitives_outer_session **session,
    const uint8_t *source, size_t source_length, const char *abi_tag,
    const quantized_runtime *runtime, const uint32_t *model_words,
    size_t model_word_count, uint32_t model_base_address,
    goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context) {
    if (session != NULL) {
        *session = NULL;
    }
    if (session == NULL || source == NULL || source_length != 76u ||
            !goodix_primitives_preprocess_abi_matches(abi_tag) ||
            model_words == NULL || allocate == NULL || release == NULL) {
        return false;
    }
    goodix_primitives_outer_session *created =
        allocate(provider_context, sizeof(*created));
    if (created == NULL) {
        return false;
    }
    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)created, sizeof(*created));
    *session = created;
    if (!goodix_primitives_processing_record_initialize(
            created->processing_record, sizeof(created->processing_record),
            source, source_length)) {
        (void)goodix_primitives_outer_session_destroy(
            session, release, provider_context);
        return false;
    }

    const size_t count =
        (size_t)goodix_primitives_load_u32_le(created->processing_record);
    const bool enabled = goodix_primitives_load_u32_le(
                             created->processing_record + 28u) != 0u;
    const uint8_t tag = created->processing_record[32];
    const bool pair_ok = goodix_primitives_allocate_record_pair(
        count, &created->record_pair.records, &created->record_pair.scratch,
        allocate, provider_context);
    const bool aggregate_ok = pair_ok &&
        goodix_primitives_session_aggregate_create(
            &created->aggregate, 5u, 25u, 25u,
            allocate, release, provider_context);
    const bool owned_ok = aggregate_ok &&
        goodix_primitives_owned_float_record_create(
            &created->owned_float, created->processing_record[71],
            created->processing_record[72], allocate, release,
            provider_context);
    const bool buffer_ok = owned_ok &&
        goodix_primitives_buffer_record_create(
            &created->buffer_record, allocate, provider_context);
    const bool model_ok = buffer_ok &&
        quantized_runtime_goodix_model_owner_initialize(
            runtime, &created->model, model_words, model_word_count,
            model_base_address, allocate, release, provider_context);
    const bool records_ok = model_ok &&
        goodix_primitives_channel_record_array_create(
            &created->channel_records, count, enabled, tag,
            allocate, release, provider_context);
    if (!records_ok) {
        (void)goodix_primitives_outer_session_destroy(
            session, release, provider_context);
        return false;
    }
    return true;
}
