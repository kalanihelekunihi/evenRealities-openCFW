/*
 * Clean-room implementation correlated to 19 GoMore-candidate functions in
 * the R1 application image.  The implementation contains no model weights,
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

static uint32_t float_bits(float value) {
    union {
        float f;
        uint32_t u;
    } pun;
    pun.f = value;
    return pun.u;
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
