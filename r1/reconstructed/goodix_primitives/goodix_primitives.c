/*
 * Clean-room implementation correlated to Goodix-candidate functions in
 * the R1 application image.  Recovered behavior comes from Ghidra output and
 * fresh Thumb-2 disassembly of rebuilt-application.bin; this file contains no
 * Goodix binary, absolute firmware pointer, or copied vendor source.
 */

#include "goodix_primitives/goodix_primitives.h"
#include "model_data/r1_model_data.h"

static uint32_t goodix_primitives_float_bits(float value);
static float goodix_primitives_float_from_bits(uint32_t bits);
static int16_t goodix_primitives_u16_bits_to_i16(uint16_t value);

_Static_assert(sizeof(goodix_primitives_nadt_primary_summary) == 4u,
               "NADT primary summary must retain its four-byte ABI");
_Static_assert(sizeof(goodix_primitives_nadt_sample_summary) == 6u,
               "NADT sample summary must retain its six-byte ABI");
_Static_assert(sizeof(goodix_primitives_nadt_difference_summary) == 20u,
               "NADT difference summary must retain its twenty-byte ABI");
_Static_assert(offsetof(goodix_primitives_nadt_difference_summary,
                        mean_difference) == 8u,
               "NADT mean difference must remain at offset eight");
_Static_assert(offsetof(goodix_primitives_nadt_difference_summary,
                        accepted_count) == 16u,
               "NADT accepted count must remain at offset sixteen");
_Static_assert(sizeof(goodix_primitives_nadt_channel_accumulator) == 24u,
               "NADT channel accumulator must retain its 24-byte ABI");
_Static_assert(sizeof(goodix_primitives_hr_extrema_tracker) == 48u,
               "GH_HR extrema tracker must retain its 48-byte ABI");
_Static_assert(sizeof(goodix_primitives_hrv_work_a) == 0x30u,
               "GH_HRV +0x6C work record must remain 0x30 bytes");
_Static_assert(sizeof(goodix_primitives_hrv_work_b) == 0x2B8u,
               "GH_HRV +0x70 work record must remain 0x2B8 bytes");
_Static_assert(offsetof(goodix_primitives_hrv_work_b, records) == 0x08u,
               "GH_HRV decision records begin at +0x08");
_Static_assert(offsetof(goodix_primitives_hrv_work_b, record_count) == 0x288u,
               "GH_HRV decision count remains at +0x288");
_Static_assert(offsetof(goodix_primitives_hrv_work_b, baseline_count) == 0x2A0u,
               "GH_HRV baseline count remains at +0x2A0");
_Static_assert(sizeof(goodix_primitives_spo2_report_analysis) == 36u,
               "GH_SPO2 report analysis must retain its 36-byte ABI");
_Static_assert(offsetof(goodix_primitives_spo2_report_analysis, score) == 12u,
               "GH_SPO2 report score must remain at offset twelve");
_Static_assert(offsetof(goodix_primitives_spo2_report_analysis,
                        acceptance_gate) == 27u,
               "GH_SPO2 acceptance gate must remain at offset 27");
_Static_assert(sizeof(goodix_primitives_spo2_process_output) == 20u,
               "GH_SPO2 processing output must retain five stock words");

_Static_assert(sizeof(goodix_primitives_hrv_configuration) == 0x18u,
               "recovered GH_HRV configuration is 24 bytes");
_Static_assert(sizeof(goodix_primitives_hr_configuration) == 0x24u,
               "recovered GH_HR configuration is 36 bytes");
_Static_assert(sizeof(goodix_primitives_hrv_work_a) == 0x30u,
               "recovered GH_HRV first work record is 48 bytes");
_Static_assert(sizeof(goodix_primitives_hrv_work_b) == 0x2B8u,
               "recovered GH_HRV second work record is 696 bytes");
_Static_assert(sizeof(goodix_primitives_word_pair) == 8u,
               "recovered bit-reversal element is two words");
_Static_assert(sizeof(goodix_primitives_warmup_average_state) == 0x40u,
               "recovered warm-up average state is 64 bytes");
_Static_assert(sizeof(goodix_primitives_extrema_history) == 0x14u,
               "recovered extrema-history state is 20 bytes");
_Static_assert(sizeof(goodix_primitives_running_triplet) == 0x18u,
               "recovered running-triplet state is 24 bytes");
_Static_assert(sizeof(goodix_primitives_hr_decision_record) == 0x20u,
               "recovered GH_HR decision record is 32 bytes");
_Static_assert(offsetof(goodix_primitives_hr_decision_record, center) == 0x14u,
               "GH_HR decision center remains at offset 0x14");
_Static_assert(offsetof(goodix_primitives_hr_decision_record, tag) == 0x18u,
               "GH_HR decision tag remains at offset 0x18");
_Static_assert(offsetof(goodix_primitives_hr_decision_record, flag) == 0x1Cu,
               "GH_HR decision flag remains at offset 0x1C");
_Static_assert(sizeof(goodix_primitives_hr_event_record) == 0x20u,
               "recovered GH_HR event record is 32 bytes");
_Static_assert(offsetof(goodix_primitives_hr_event_record, center) == 0x14u,
               "GH_HR event center must remain at offset 0x14");
_Static_assert(offsetof(goodix_primitives_hr_event_record, eligible) == 0x18u,
               "GH_HR event eligibility must remain at offset 0x18");
_Static_assert(sizeof(goodix_primitives_nadt_initialize_configuration) == 0x3Cu,
               "GH_NADT public initialization configuration is 60 bytes");
_Static_assert(offsetof(goodix_primitives_nadt_initializer_state,
                        allocation_58) == 0x58u,
               "GH_NADT owned allocation remains at logical offset 0x58");
_Static_assert(offsetof(goodix_primitives_nadt_runtime_configuration,
                        doubled_field_58) == 0x58u,
               "GH_NADT runtime doubled field remains at offset 0x58");
_Static_assert(offsetof(goodix_primitives_nadt_runtime_configuration,
                        constant_74) == 0x74u,
               "GH_NADT runtime terminal constant remains at offset 0x74");

#if UINTPTR_MAX == UINT32_MAX
_Static_assert(sizeof(goodix_primitives_hr_primary_context) == 0x150u,
               "recovered GH_HR primary context is 0x150 bytes");
_Static_assert(offsetof(goodix_primitives_hr_primary_context,
                        configuration_selector) == 0x13u,
               "GH_HR configuration selector remains at +0x13");
_Static_assert(offsetof(goodix_primitives_hr_primary_context,
                        graph_selector_0) == 0x6Cu,
               "GH_HR first graph remains at +0x6C");
_Static_assert(offsetof(goodix_primitives_hr_primary_context,
                        short_history_a) == 0xB0u,
               "GH_HR first short history remains at +0xB0");
_Static_assert(offsetof(goodix_primitives_hr_primary_context,
                        terminal_default) == 0x148u,
               "GH_HR terminal default remains at +0x148");
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

bool goodix_primitives_build_hr_version(char *destination,
                                        size_t capacity) {
    if (destination == NULL || capacity == 0u) {
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
    static const char *const parts[] = {
        "GH_HR_exc", "_pv", "_v2.0.3.0", "_", "CONF", "_", "nc",
        "_", "21d2063d", "_", "002271a1", "\n",
    };
    for (size_t index = 0u; index < sizeof(parts) / sizeof(parts[0]);
            ++index) {
        if (!goodix_primitives_append_string(
                destination, capacity, &length, parts[index])) {
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

bool goodix_primitives_build_nadt_version(char *destination,
                                           size_t capacity) {
    if (destination == NULL || capacity == 0u) {
        return false;
    }
    char dsp_version[23];
    if (!goodix_primitives_copy_dsp_version(
            dsp_version, sizeof(dsp_version))) {
        return false;
    }
    destination[0] = '\0';
    size_t length = 0u;
    static const char *const parts[] = {
        "GH_NADT_pre", "_pv", "_v1.0.2.0", "_", "nc", "_",
        "548d894d", "\n",
    };
    for (size_t index = 0u; index < sizeof(parts) / sizeof(parts[0]);
            ++index) {
        if (!goodix_primitives_append_string(
                destination, capacity, &length, parts[index])) {
            destination[0] = '\0';
            return false;
        }
    }
    if (!goodix_primitives_append_string(
            destination, capacity, &length, dsp_version)) {
        destination[0] = '\0';
        return false;
    }
    return true;
}

static bool goodix_primitives_nadt_version_matches(const char *version) {
    static const char expected[] = "pv_v1.0.0";
    if (version == NULL) {
        return false;
    }
    for (size_t index = 0u; index < sizeof(expected); ++index) {
        if (version[index] != expected[index]) {
            return false;
        }
    }
    return true;
}

static int32_t goodix_primitives_nadt_wrapped_i32(uint32_t value) {
    return value <= (uint32_t)INT32_MAX
        ? (int32_t)value
        : INT32_MIN + (int32_t)(value - UINT32_C(0x80000000));
}

static int32_t goodix_primitives_nadt_scaled_i32(
    int32_t value, float multiplier) {
    const float scaled = ((float)value * multiplier) / 1000.0f;
    if (scaled <= -2147483648.0f) {
        return INT32_MIN;
    }
    if (scaled >= 2147483648.0f) {
        return INT32_MAX;
    }
    return (int32_t)scaled;
}

static uint16_t goodix_primitives_nadt_scaled_u16(
    int32_t value, float multiplier) {
    const float scaled = ((float)value * multiplier) / 1000.0f;
    uint32_t converted = 0u;
    if (scaled >= 4294967296.0f) {
        converted = UINT32_MAX;
    } else if (scaled > 0.0f) {
        converted = (uint32_t)scaled;
    }
    return (uint16_t)converted;
}

static bool goodix_primitives_nadt_workspace_valid(
    const goodix_primitives_nadt_initializer_workspace *workspace) {
    return workspace != NULL && workspace->bank_400_a != NULL &&
        workspace->bank_400_a_bytes >= 400u &&
        workspace->bank_400_b != NULL &&
        workspace->bank_400_b_bytes >= 400u &&
        workspace->bank_600 != NULL && workspace->bank_600_bytes >= 600u &&
        workspace->bank_68 != NULL && workspace->bank_68_bytes >= 68u &&
        workspace->counters != NULL && workspace->counter_count >= 16u &&
        workspace->descriptor != NULL &&
        workspace->descriptor_primary != NULL &&
        workspace->descriptor_primary_words >= 4u &&
        workspace->descriptor_secondary != NULL &&
        workspace->descriptor_secondary_words >= 4u;
}

int32_t goodix_primitives_nadt_context_initialize(
    const goodix_primitives_nadt_initialize_configuration *configuration,
    const char *version,
    goodix_primitives_nadt_initializer_state *state,
    goodix_primitives_nadt_runtime_configuration *runtime,
    goodix_primitives_nadt_initializer_workspace *workspace,
    goodix_primitives_allocate_fn allocate, void *allocate_context) {
    if (configuration == NULL || state == NULL || runtime == NULL ||
            allocate == NULL || !goodix_primitives_nadt_version_matches(version) ||
            !goodix_primitives_nadt_workspace_valid(workspace)) {
        return GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID;
    }
    void *const allocation = allocate(allocate_context, 0x34u);
    if (allocation == NULL) {
        return GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID;
    }

    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)state, sizeof(*state));
    state->allocation_58 = allocation;
    state->limit_34 = UINT32_C(0xFF);
    state->threshold_09 = UINT8_C(0x32);
    state->marker = UINT8_C(0xBF);

    (void)goodix_primitives_byte_fill(
        0u, workspace->bank_400_a, 400u);
    (void)goodix_primitives_byte_fill(
        0u, workspace->bank_400_b, 400u);
    (void)goodix_primitives_byte_fill(
        0u, workspace->bank_600, 600u);
    (void)goodix_primitives_byte_fill(
        0u, workspace->bank_68, 68u);
    for (size_t index = 0u; index < 16u; ++index) {
        workspace->counters[index] = 0u;
    }
    if (!goodix_primitives_dual_buffer_descriptor_initialize(
            workspace->descriptor,
            workspace->descriptor_field_00,
            workspace->descriptor_field_04,
            workspace->descriptor_primary,
            workspace->descriptor_primary_words,
            workspace->descriptor_secondary,
            workspace->descriptor_secondary_words,
            3u, workspace->descriptor_field_14)) {
        return GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID;
    }

    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)runtime, sizeof(*runtime));
    int32_t status = GOODIX_PRIMITIVES_NADT_INITIALIZE_OK;
    switch (configuration->sample_rate) {
        case 25u:
        case 50u:
        case 100u:
        case 200u:
            runtime->sample_rate = configuration->sample_rate;
            break;
        default:
            runtime->sample_rate = 25u;
            status = GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID;
            break;
    }
    if (configuration->mode >= 1u && configuration->mode <= 3u) {
        runtime->mode = configuration->mode;
    } else {
        runtime->mode = 1u;
        status = GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID;
    }
    runtime->field_04 = configuration->field_04;
    runtime->enabled_06 = 1u;
    runtime->field_07 = configuration->field_06;
    runtime->field_08 = configuration->field_07;
    runtime->offset_0c = goodix_primitives_nadt_wrapped_i32(
        (uint32_t)configuration->offset_08 - UINT32_C(0x00800000));
    runtime->offset_10 = goodix_primitives_nadt_wrapped_i32(
        (uint32_t)configuration->offset_0c - UINT32_C(0x00800000));
    runtime->field_14 = configuration->field_10;
    runtime->enabled_18 = 1u;
    runtime->minimum_1c = 0x1.47ae14p-7f;
    runtime->maximum_20 = 0x1.47ae14p-6f;
    runtime->field_24 = configuration->field_14;
    runtime->constant_28 = 8u;
    runtime->field_2c = configuration->field_18;
    runtime->timing_30 = goodix_primitives_nadt_scaled_i32(
        configuration->timing_base, 2.0f);
    runtime->constant_34 = 60u;
    runtime->constant_36 = 40u;
    runtime->timing_38 = goodix_primitives_nadt_scaled_i32(
        configuration->timing_base, 6.0f);
    runtime->field_3c = configuration->field_1c;
    runtime->field_3e = configuration->field_1e;
    runtime->field_40 = configuration->field_20;
    runtime->half_field_44 = (int32_t)configuration->field_20 / 2;
    runtime->field_48 = (uint8_t)configuration->field_24;
    runtime->timing_4a = goodix_primitives_nadt_scaled_u16(
        configuration->timing_base, 5.0f);
    runtime->constant_4c = 900u;
    runtime->timing_4e = goodix_primitives_nadt_scaled_u16(
        configuration->timing_base, 3.0f);
    runtime->timing_50 = goodix_primitives_nadt_scaled_u16(
        configuration->timing_base, 7.0f);
    runtime->field_52_enabled = configuration->field_26 == 0u ? 0u : 1u;
    runtime->constant_54 = 10u;
    runtime->field_56 = configuration->field_26;
    runtime->doubled_field_58 = goodix_primitives_nadt_wrapped_i32(
        (uint32_t)configuration->field_28 << 1u);
    runtime->field_5c = configuration->field_28;
    runtime->timing_60 = goodix_primitives_nadt_scaled_u16(
        configuration->timing_base, 15.0f);
    runtime->constant_62 = 900u;
    runtime->timing_64 = goodix_primitives_nadt_scaled_u16(
        configuration->timing_base, 6.0f);
    runtime->constant_66 = 5u;
    runtime->field_67 = configuration->field_30;
    runtime->field_68 = configuration->field_32;
    runtime->field_6a = configuration->field_32;
    runtime->field_6c = configuration->field_34;
    runtime->field_6d = configuration->field_35;
    runtime->field_6e = configuration->field_36;
    runtime->field_70 = configuration->field_38;
    runtime->field_72 = configuration->field_3a;
    runtime->constant_74 = 70u;
    return status;
}

int32_t goodix_primitives_nadt_default_initialize(
    uint16_t sample_rate, uint8_t *result_status,
    goodix_primitives_nadt_initializer_state *state,
    goodix_primitives_nadt_runtime_configuration *runtime,
    goodix_primitives_nadt_initializer_workspace *workspace,
    goodix_primitives_allocate_fn allocate, void *allocate_context) {
    if (result_status == NULL) {
        return GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID;
    }
    *result_status = 0u;
    char identity[120] = {0};
    char version[20] = {0};
    if (!goodix_primitives_build_nadt_version(identity, sizeof(identity)) ||
            !goodix_primitives_copy_process_version_v1_0(
                version, sizeof(version))) {
        return GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID;
    }
    goodix_primitives_nadt_initialize_configuration configuration = {
        .sample_rate = sample_rate,
        .mode = 3u,
        .field_04 = 1200u,
        .field_06 = 4u,
        .field_07 = 2u,
        .offset_08 = INT32_C(0x008890EC),
        .offset_0c = INT32_C(0x00862DF4),
        .field_10 = 25u,
        .field_14 = 1u,
        .field_18 = 300u,
        .field_1c = 50u,
        .field_1e = 140u,
        .field_20 = 8u,
        .field_24 = 50,
        .field_26 = 30u,
        .field_28 = 15,
        .timing_base = 1000,
        .field_30 = 1u,
        .field_32 = 100u,
        .field_34 = 12u,
        .field_35 = 1u,
        .field_36 = 10u,
        .field_38 = 10u,
        .field_3a = 5u,
    };
    return goodix_primitives_nadt_context_initialize(
        &configuration, version, state, runtime, workspace,
        allocate, allocate_context);
}

int32_t goodix_primitives_nadt_context_reset(
    goodix_primitives_nadt_initializer_state *state,
    goodix_primitives_nadt_initializer_workspace *workspace,
    goodix_primitives_release_fn release, void *release_context) {
    if (state == NULL || release == NULL ||
            !goodix_primitives_nadt_workspace_valid(workspace)) {
        return GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID;
    }

    state->word_28 = 0u;
    state->word_2c = 0u;
    state->flag_01 = 0u;
    state->counter_20 = 0u;
    state->flag_0a = 0u;
    state->counter_22 = 0u;
    (void)goodix_primitives_byte_fill(
        0u, workspace->bank_400_a, 400u);
    (void)goodix_primitives_byte_fill(
        0u, workspace->bank_400_b, 400u);
    (void)goodix_primitives_byte_fill(
        0u, workspace->bank_600, 600u);
    (void)goodix_primitives_byte_fill(
        0u, workspace->bank_68, 68u);
    if (!goodix_primitives_dual_buffer_descriptor_initialize(
            workspace->descriptor,
            workspace->descriptor_field_00,
            workspace->descriptor_field_04,
            workspace->descriptor_primary,
            workspace->descriptor_primary_words,
            workspace->descriptor_secondary,
            workspace->descriptor_secondary_words,
            3u, workspace->descriptor_field_14)) {
        return GOODIX_PRIMITIVES_NADT_INITIALIZE_INVALID;
    }

    state->counter_1c = 0u;
    for (size_t index = 0u; index < sizeof(state->flags_04_08); ++index) {
        state->flags_04_08[index] = 0u;
    }
    state->counter_1e = 0u;
    state->threshold_09 = UINT8_C(0x32);
    for (size_t index = 0u; index < sizeof(state->flags_0b_18); ++index) {
        state->flags_0b_18[index] = 0u;
    }
    state->word_38 = 0u;
    state->word_3c = 0u;
    for (size_t index = 0u; index < 16u; ++index) {
        workspace->counters[index] = 0u;
    }
    state->word_40 = 0u;
    state->word_44 = 0u;
    state->counter_24 = 0u;
    state->counter_26 = 0u;
    state->word_48 = 0u;
    state->word_4c = 0u;
    state->flag_03 = 0u;
    if (state->allocation_58 != NULL) {
        release(release_context, state->allocation_58);
        state->allocation_58 = NULL;
    }
    state->marker = UINT8_C(0xBF);
    return GOODIX_PRIMITIVES_NADT_INITIALIZE_OK;
}

bool goodix_primitives_build_hrv_version(char *destination,
                                         size_t capacity) {
    static const char version[] = "GH_HRV_pre_pv_v1.0.1.0_ed953ff3";
    if (destination == NULL || capacity < sizeof(version)) {
        return false;
    }
    for (size_t index = 0u; index < sizeof(version); ++index) {
        destination[index] = version[index];
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

bool goodix_primitives_counted_word_history_push(
    goodix_primitives_counted_word_history *history, uint32_t value) {
    if (history == NULL || history->values == NULL ||
            history->capacity == 0u || history->count > history->capacity ||
            history->capacity > UINT32_MAX / 4u) {
        return false;
    }
    if (history->count < history->capacity) {
        history->values[history->count] = value;
        ++history->count;
    } else {
        for (uint32_t index = 1u; index < history->capacity; ++index) {
            history->values[index - 1u] = history->values[index];
        }
        history->values[history->capacity - 1u] = value;
    }
    ++history->push_count;
    return true;
}

static bool goodix_primitives_counted_history_valid(
    const goodix_primitives_counted_word_history *history) {
    return history != NULL && history->values != NULL &&
           history->capacity != 0u && history->count <= history->capacity &&
           history->capacity <= UINT32_MAX / 4u;
}

static bool goodix_primitives_counted_float_mean(
    const goodix_primitives_counted_word_history *history, float *mean) {
    if (!goodix_primitives_counted_history_valid(history) || mean == NULL ||
            history->count == 0u) {
        return false;
    }
    float sum = 0.0f;
    for (uint32_t index = 0u; index < history->count; ++index) {
        sum += goodix_primitives_float_from_bits(history->values[index]);
    }
    *mean = sum / (float)history->count;
    return true;
}

bool goodix_primitives_hr_interpolate_periodic_sample(
    goodix_primitives_hr_weighted_feature_state *state, bool *emitted) {
    if (state == NULL || emitted == NULL || state->input_rate < INT32_C(25) ||
            state->interpolation_count < 0 ||
            state->interpolation_count == INT32_MAX ||
            !goodix_primitives_counted_history_valid(&state->raw_history) ||
            !goodix_primitives_counted_history_valid(
                &state->periodic_history)) {
        return false;
    }
    *emitted = false;

    const int32_t quotient = state->input_rate / INT32_C(25);
    const int32_t phase_count = state->input_rate / quotient +
        (state->input_rate % quotient == 0 ? 0 : 1);
    const float phase_step =
        (float)((double)phase_count / 25.0);
    float current = 0.0f;
    float current_weight = 0.0f;
    float previous_weight = 0.0f;

    if (state->raw_history.push_count % (uint32_t)state->input_rate == 0u &&
            state->raw_history.push_count != 0u) {
        if (state->raw_history.count == 0u) {
            return false;
        }
        ++state->interpolation_count;
        current = goodix_primitives_float_from_bits(
            state->raw_history.values[state->raw_history.count - 1u]);
        state->raw_history.push_count = 0u;
        current_weight = 1.0f;
    } else {
        if (state->raw_history.push_count % state->raw_history.capacity != 0u) {
            return true;
        }
        if (!goodix_primitives_counted_float_mean(
                &state->raw_history, &current)) {
            return false;
        }
        ++state->interpolation_count;
        const int32_t phase =
            state->interpolation_count % phase_count;
        state->interpolation_phase = 1;
        while (state->interpolation_phase <= INT32_C(25)) {
            const float boundary =
                (float)state->interpolation_phase * phase_step;
            if (boundary <= (float)phase &&
                    boundary > (float)(phase - INT32_C(1))) {
                current_weight = (float)phase - boundary;
                previous_weight = 1.0f - current_weight;
                break;
            }
            ++state->interpolation_phase;
        }
        if (state->interpolation_phase > INT32_C(25)) {
            return true;
        }
    }

    float output =
        state->previous_interpolation_sample * previous_weight;
    output += current * current_weight;
    if (!goodix_primitives_counted_word_history_push(
            &state->periodic_history,
            goodix_primitives_float_bits(output))) {
        return false;
    }
    state->previous_interpolation_sample = current;
    *emitted = true;
    return true;
}

bool goodix_primitives_hr_weighted_feature_update(
    goodix_primitives_hr_weighted_feature_state *state, float sample,
    bool *emitted) {
    if (state == NULL || emitted == NULL ||
            state->input_rate < INT32_C(25) ||
            !goodix_primitives_counted_history_valid(&state->raw_history) ||
            !goodix_primitives_counted_history_valid(
                &state->periodic_history) ||
            !goodix_primitives_counted_history_valid(&state->mean_history) ||
            !goodix_primitives_counted_history_valid(
                &state->centered_history) ||
            !goodix_primitives_counted_history_valid(
                &state->weighted_history) ||
            (state->mode < UINT32_C(4) &&
             (state->mode_coefficients[state->mode] == NULL &&
              state->mode_coefficient_words[state->mode] == NULL)) ||
            (state->mode < UINT32_C(4) &&
              state->mode_coefficient_counts[state->mode] <
                  state->centered_history.capacity)) {
        return false;
    }
    *emitted = false;

    if (state->input_rate % INT32_C(25) == 0) {
        if (!goodix_primitives_counted_word_history_push(
                &state->periodic_history,
                goodix_primitives_float_bits(sample))) {
            return false;
        }
    } else {
        if (!goodix_primitives_counted_word_history_push(
                &state->raw_history, goodix_primitives_float_bits(sample))) {
            return false;
        }
        bool resampled = false;
        if (!goodix_primitives_hr_interpolate_periodic_sample(
                state, &resampled)) {
            return false;
        }
        if (!resampled) {
            return true;
        }
        if (!goodix_primitives_counted_history_valid(
                &state->periodic_history)) {
            return false;
        }
    }

    if (state->periodic_history.push_count %
            state->periodic_history.capacity != 0u) {
        return true;
    }

    float periodic_mean = 0.0f;
    if (!goodix_primitives_counted_float_mean(
            &state->periodic_history, &periodic_mean) ||
            !goodix_primitives_counted_word_history_push(
                &state->mean_history,
                goodix_primitives_float_bits(periodic_mean))) {
        return false;
    }
    if (state->mean_history.count != state->mean_history.capacity) {
        return true;
    }

    float mean_of_means = 0.0f;
    if (!goodix_primitives_counted_float_mean(
            &state->mean_history, &mean_of_means)) {
        return false;
    }
    const union {
        uint32_t unsigned_value;
        int32_t signed_value;
    } wrapped_window = {
        .unsigned_value = (uint32_t)state->midpoint_window - UINT32_C(1),
    };
    const uint32_t midpoint_index =
        (uint32_t)(wrapped_window.signed_value / INT32_C(2));
    float midpoint = 0.0f;
    if (midpoint_index < state->mean_history.capacity) {
        midpoint = goodix_primitives_float_from_bits(
            state->mean_history.values[midpoint_index]);
    }
    const float centered = midpoint - mean_of_means;
    if (!goodix_primitives_counted_word_history_push(
            &state->centered_history,
            goodix_primitives_float_bits(centered))) {
        return false;
    }

    float weighted = 0.0f;
    if (state->mode < UINT32_C(4)) {
        const float *const coefficients =
            state->mode_coefficients[state->mode];
        const uint32_t *const coefficient_words =
            state->mode_coefficient_words[state->mode];
        const uint32_t count = state->centered_history.count;
        for (uint32_t offset = 0u; offset < count; ++offset) {
            const uint32_t value_index = count - UINT32_C(1) - offset;
            const float coefficient = coefficients != NULL
                ? coefficients[offset]
                : goodix_primitives_float_from_bits(
                    coefficient_words[offset]);
            weighted += goodix_primitives_float_from_bits(
                state->centered_history.values[value_index]) *
                coefficient;
        }
    }
    if (!goodix_primitives_counted_word_history_push(
            &state->weighted_history,
            goodix_primitives_float_bits(weighted))) {
        return false;
    }
    *emitted = true;
    return true;
}

bool goodix_primitives_hr_candidate_window_select(
    goodix_primitives_hr_candidate_selection_state *state,
    const goodix_primitives_hr_candidate_record *records,
    size_t record_count, int32_t raw_lower_bound,
    int32_t raw_upper_bound, int32_t warmup_count,
    int32_t warmup_limit, float scale,
    goodix_primitives_hr_candidate_selection *selection) {
    if (state == NULL || records == NULL || selection == NULL ||
            state->position_step < 0) {
        return false;
    }
    ++state->call_count;
    for (size_t index = 0u; index < 4u; ++index) {
        selection->values[index] = 0.0f;
        selection->tags[index] = 0u;
    }
    selection->count = 0u;

    float upper = (float)raw_upper_bound;
    float lower = (float)raw_lower_bound;
    if (warmup_count >= warmup_limit) {
        const float scaled_upper = scale * 3.0f;
        const float scaled_lower = scale * 0.5f;
        if (upper < scaled_upper) {
            upper = scaled_upper;
        }
        if (lower < scaled_lower) {
            lower = scaled_lower;
        }
    }

    const int64_t origin = state->position_origin;
    const int64_t step = state->position_step;
    const float band_lower = (float)(origin - step * INT64_C(3));
    const float band_upper = (float)(origin - step * INT64_C(2));
    const float fallback_limit = (float)(origin - step * INT64_C(4));
    size_t next_slot = 4u;

    for (size_t remaining = record_count; remaining > 0u;) {
        const size_t index = --remaining;
        const goodix_primitives_hr_candidate_record *const record =
            &records[index];
        if (record->position >= band_lower &&
                record->position < band_upper &&
                record->suppressed == 0u) {
            if (next_slot != 0u) {
                --next_slot;
                float value = record->value;
                uint32_t tag = index == 0u || record->tag == 1u
                    ? record->alternate_tag : record->tag;
                if (value > upper) {
                    value = upper;
                    tag = 8u;
                } else if (value < lower) {
                    value = lower;
                    tag = 8u;
                }
                selection->values[next_slot] = value;
                selection->tags[next_slot] = tag;
            }
            continue;
        }
        if (record->position < band_lower) {
            if (next_slot == 4u && record->position < fallback_limit) {
                selection->values[3] = record->value;
                selection->tags[3] = 7u;
            }
            break;
        }
    }

    uint32_t compacted = 0u;
    for (size_t index = 0u; index < 4u; ++index) {
        if (selection->values[index] > 0.0f) {
            selection->values[compacted] = selection->values[index];
            selection->tags[compacted] = selection->tags[index];
            ++compacted;
        }
    }
    for (size_t index = compacted; index < 4u; ++index) {
        selection->values[index] = 0.0f;
        selection->tags[index] = 0u;
    }
    selection->count = compacted;
    return true;
}

static bool goodix_primitives_hr_process_history_valid(
    const goodix_primitives_counted_word_history *history) {
    return history != NULL && history->values != NULL &&
        history->capacity != 0u && history->count <= history->capacity;
}

static bool goodix_primitives_hr_process_history_mean(
    const goodix_primitives_counted_word_history *history, float *result) {
    if (!goodix_primitives_hr_process_history_valid(history) ||
            result == NULL || history->count == 0u) {
        return false;
    }
    float sum = 0.0f;
    for (uint32_t index = 0u; index < history->count; ++index) {
        sum += goodix_primitives_float_from_bits(history->values[index]);
    }
    *result = sum / (float)history->count;
    return true;
}

static bool goodix_primitives_hr_process_present(
    const goodix_primitives_hr_process_input *input, size_t index) {
    return (input->presence_bytes[index / 8u] >>
            (7u - (uint32_t)(index % 8u)) & UINT8_C(1)) != 0u;
}

static int32_t goodix_primitives_hr_process_quality(
    const goodix_primitives_hr_candidate_selection *selection,
    const goodix_primitives_hr_process_state *state) {
    uint32_t primary = 0u;
    uint32_t boundary = 0u;
    uint32_t other = 0u;
    for (uint32_t index = 0u; index < selection->count; ++index) {
        if (selection->tags[index] == 1u) {
            ++primary;
        } else if (selection->tags[index] == 7u ||
                selection->tags[index] == 8u) {
            ++boundary;
        } else {
            ++other;
        }
    }
    const bool first_reached =
        state->quality_reference <= (float)state->quality_threshold_first;
    if (primary == 0u) {
        if (other != 0u) {
            return first_reached ? 20 : 30;
        }
        return boundary != 0u ? (first_reached ? 0 : 10) : 0;
    }
    if (primary < selection->count) {
        if (other != 0u) {
            return first_reached ? 60 : 70;
        }
        return boundary != 0u ? (first_reached ? 40 : 50) : 0;
    }
    const bool second_reached =
        state->quality_reference <= (float)state->quality_threshold_second;
    if (!first_reached && !second_reached) {
        return 100;
    }
    if ((float)state->quality_threshold_first < state->quality_reference &&
            !second_reached) {
        return 90;
    }
    return 80;
}

static bool goodix_primitives_hr_process_quality_median(
    const goodix_primitives_counted_word_history *history,
    goodix_primitives_hr_process_workspace *workspace, float *result) {
    if (!goodix_primitives_hr_process_history_valid(history) ||
            workspace == NULL || workspace->quality_sort_scratch == NULL ||
            workspace->quality_sort_capacity < history->count ||
            result == NULL || history->count == 0u) {
        return false;
    }
    for (uint32_t index = 0u; index < history->count; ++index) {
        workspace->quality_sort_scratch[index] =
            goodix_primitives_float_from_bits(history->values[index]);
    }
    if (!goodix_primitives_sort_floats(
            workspace->quality_sort_scratch, history->count)) {
        return false;
    }
    const uint32_t middle = history->count / UINT32_C(2);
    *result = (history->count & UINT32_C(1)) != 0u
        ? workspace->quality_sort_scratch[middle]
        : (workspace->quality_sort_scratch[middle - UINT32_C(1)] +
           workspace->quality_sort_scratch[middle]) * 0.5f;
    return true;
}

bool goodix_primitives_hrv_process(
    const goodix_primitives_hr_process_input *input,
    const goodix_primitives_hr_process_plan *plan,
    goodix_primitives_hr_process_state *state,
    goodix_primitives_hr_process_workspace *workspace,
    int32_t output[6]) {
    if (input == NULL || plan == NULL || state == NULL || output == NULL ||
            input->channel_values == NULL || input->presence_bytes == NULL ||
            input->channel_count == 0u ||
            input->channel_value_count < input->channel_count ||
            input->presence_byte_count <
                ((size_t)input->channel_count + 7u) / 8u ||
            state->sample_rate == 0u || plan->sample_invalid == NULL ||
            plan->decision_core == NULL || plan->square_root == NULL ||
            plan->candidate_records == NULL ||
            workspace == NULL || workspace->signal_scratch == NULL ||
            workspace->signal_scratch_capacity <
                state->signal_history.capacity ||
            !goodix_primitives_hr_process_history_valid(
                &state->signal_history) ||
            !goodix_primitives_hr_process_history_valid(
                &state->motion_history) ||
            !goodix_primitives_hr_process_history_valid(
                &state->quality_history)) {
        return false;
    }
    const bool invalid = plan->sample_invalid(
        plan->sample_invalid_context, input->channel_values[0]);
    if (invalid) {
        input->channel_values[0] = 0;
    }
    float selected_sample = 0.0f;
    for (size_t index = 0u; index < input->channel_count; ++index) {
        if (goodix_primitives_hr_process_present(input, index)) {
            selected_sample = (float)input->channel_values[index];
            break;
        }
    }

    ++state->process_count;
    const float magnitude_square =
        (float)input->axis_x * (float)input->axis_x +
        (float)input->axis_y * (float)input->axis_y +
        (float)input->axis_z * (float)input->axis_z;
    const float magnitude = plan->square_root(magnitude_square);
    if (!goodix_primitives_counted_word_history_push(
            &state->motion_history,
            goodix_primitives_float_bits(magnitude))) {
        return false;
    }
    if (state->motion_history.push_count %
            state->motion_history.capacity == 0u) {
        float mean = 0.0f;
        if (!goodix_primitives_hr_process_history_mean(
                &state->motion_history, &mean) ||
                !goodix_primitives_counted_word_history_push(
                    &state->signal_history,
                    goodix_primitives_float_bits(mean))) {
            return false;
        }
    }
    bool weighted_emitted = false;
    if (!goodix_primitives_hr_weighted_feature_update(
            &state->weighted_feature, 0.0f, &weighted_emitted)) {
        return false;
    }
    (void)weighted_emitted;
    for (uint32_t index = 0u; index < state->signal_history.count; ++index) {
        workspace->signal_scratch[index] = goodix_primitives_float_from_bits(
            state->signal_history.values[index]);
    }
    const goodix_primitives_float_buffer signal_view = {
        .values = workspace->signal_scratch,
        .count = state->signal_history.count,
        .capacity = state->signal_history.capacity,
    };
    if (!goodix_primitives_hr_extrema_tracker_update(
            &signal_view, state->extrema_signal_mode,
            state->extrema_interpolation_mode,
            state->extrema_position_base, state->extrema_period,
            &state->extrema_tracker, state->trough_curve,
            state->peak_curve, state->extrema_workspace) ||
            !plan->decision_core(plan->decision_context)) {
        return false;
    }

    const uint32_t minimum_process_count =
        state->sample_rate * UINT32_C(5);
    if (state->process_count <= minimum_process_count ||
            state->process_count % state->sample_rate != 0u) {
        for (size_t index = 0u; index < 6u; ++index) {
            output[index] = state->previous_output[index];
        }
        return true;
    }
    state->window_index = state->process_count / state->sample_rate;
    if (!goodix_primitives_hr_count_mean_outliers(
            &signal_view, 125u, plan->outlier_maximum_threshold,
            plan->outlier_minimum_threshold,
            plan->outlier_deviation_multiplier, plan->square_root,
            &state->outlier_count, &state->tail_outlier_count)) {
        return false;
    }

    goodix_primitives_hr_candidate_selection selection;
    if (!goodix_primitives_hr_candidate_window_select(
            &state->candidate_selector, plan->candidate_records,
            plan->candidate_record_count, plan->candidate_lower_bound,
            plan->candidate_upper_bound,
            (int32_t)state->candidate_warmup_count,
            plan->candidate_warmup_limit, plan->candidate_scale,
            &selection)) {
        return false;
    }
    int32_t rates[4] = {0, 0, 0, 0};
    for (size_t index = 0u; index < 4u; ++index) {
        const float rate = selection.values[index] * 1000.0f /
            (float)state->sample_rate;
        rates[index] = (int32_t)
            goodix_primitives_round_float_half_away_from_zero(rate);
    }
    int32_t quality = goodix_primitives_hr_process_quality(
        &selection, state);
    if (rates[0] > 0) {
        if (!goodix_primitives_counted_word_history_push(
                &state->quality_history,
                goodix_primitives_float_bits((float)quality))) {
            return false;
        }
        if (state->quality_history.count ==
                state->quality_history.capacity) {
            float median = 0.0f;
            if (!goodix_primitives_hr_process_quality_median(
                    &state->quality_history, workspace, &median)) {
                return false;
            }
            quality = (int32_t)median;
        }
    }
    if (invalid) {
        quality = 25;
    }
    if (selection.count == 0u) {
        for (size_t index = 0u; index < 6u; ++index) {
            output[index] = state->previous_output[index];
        }
    } else {
        for (size_t index = 0u; index < 4u; ++index) {
            output[index] = rates[index];
        }
        output[4] = quality;
        output[5] = (int32_t)selection.count;
    }

    const float reference =
        state->decision_reference_position * 1000.0f /
        (float)state->sample_rate;
    if (reference != 0.0f && state->candidate_selector.call_count > 5u &&
            state->decision_reference_mode == 1) {
        const float first_ratio = (float)output[0] / reference - 1.0f;
        const float first_difference =
            first_ratio < 0.0f ? -first_ratio : first_ratio;
        if (first_difference >= 0.2f || rates[0] == 0) {
            output[0] = (int32_t)((reference +
                (float)state->previous_rate) * 0.5f);
            rates[0] = output[0];
            if (rates[0] == 0) {
                output[1] = 0;
                output[2] = 0;
                output[3] = 0;
                output[5] = 1;
            }
        }
    }
    for (size_t index = 0u; index < 4u; ++index) {
        state->latest_rates[index] = rates[index];
        if (rates[index] != 0) {
            state->previous_rate = rates[index];
        }
    }
    if (selection.count != 0u) {
        for (size_t index = 0u; index < 6u; ++index) {
            state->previous_output[index] = output[index];
        }
    }
    (void)selected_sample;
    return true;
}

bool goodix_primitives_hr_process(
    const goodix_primitives_hr_process_input *input,
    const goodix_primitives_hr_process_plan *plan,
    goodix_primitives_hr_process_state *state,
    goodix_primitives_hr_process_workspace *workspace,
    int32_t output[6]) {
    return goodix_primitives_hrv_process(
        input, plan, state, workspace, output);
}

bool goodix_primitives_running_triplet_update(
    goodix_primitives_running_triplet *state, float first, float second,
    float third, uint32_t timestamp) {
    if (state == NULL || state->count < 0 || state->capacity <= 0 ||
            state->count > state->capacity) {
        return false;
    }
    if (state->count < state->capacity) {
        ++state->count;
    }
    const float previous = (float)(state->count - 1);
    const float divisor = (float)state->count;
    state->mean[0] = (first + state->mean[0] * previous) / divisor;
    state->mean[1] = (second + state->mean[1] * previous) / divisor;
    state->mean[2] = (third + state->mean[2] * previous) / divisor;
    state->timestamp = timestamp;
    return true;
}

static float goodix_primitives_hr_decision_absolute(float value) {
    return value < 0.0f ? -value : value;
}

static float goodix_primitives_hr_decision_minimum(float first,
                                                    float second) {
    return second < first ? second : first;
}

static float goodix_primitives_hr_decision_maximum(float first,
                                                    float second) {
    return first < second ? second : first;
}

static bool goodix_primitives_hr_decision_history_valid(
    const goodix_primitives_counted_word_history *history) {
    return history != NULL && history->values != NULL &&
        history->capacity == GOODIX_PRIMITIVES_HR_DECISION_HISTORY_VALUES &&
        history->count <= history->capacity;
}

static bool goodix_primitives_hr_decision_append(
    goodix_primitives_hr_decision_state *state,
    const goodix_primitives_hr_decision_record *record) {
    if (state == NULL || record == NULL || state->records == NULL ||
            state->record_capacity == 0u ||
            state->record_count > state->record_capacity) {
        return false;
    }
    if (state->record_count == state->record_capacity) {
        for (uint32_t index = 1u; index < state->record_capacity; ++index) {
            state->records[index - 1u] = state->records[index];
        }
        --state->record_count;
    }
    state->records[state->record_count] = *record;
    ++state->record_count;
    return true;
}

static void goodix_primitives_hr_decision_decrement(
    goodix_primitives_hr_decision_state *state) {
    if (state->record_count != 0u) {
        --state->record_count;
    }
}

static void goodix_primitives_hr_decision_merge(
    goodix_primitives_hr_decision_record *state,
    const goodix_primitives_hr_decision_record *incoming, bool advance) {
    if (!advance) {
        float gap = state->primary_second - incoming->primary_first;
        if (gap < 0.0f) {
            gap = 0.0f;
        }
        state->primary_second = gap + incoming->primary_second;
        state->auxiliary_second +=
            incoming->auxiliary_first + incoming->auxiliary_second;
        return;
    }
    float gap = incoming->primary_first - state->primary_second;
    if (gap < 0.0f) {
        gap = 0.0f;
    }
    state->primary_first += gap;
    state->primary_second = incoming->primary_second;
    state->auxiliary_first +=
        state->auxiliary_second + incoming->auxiliary_first;
    state->auxiliary_second = incoming->auxiliary_second;
    state->center = (state->center + incoming->position) - state->position;
    state->position = incoming->position;
}

static bool goodix_primitives_hr_decision_rebalance(
    goodix_primitives_hr_decision_state *state, float tolerance_scale,
    goodix_primitives_hr_decision_record *first,
    goodix_primitives_hr_decision_record *second) {
    const float baseline = state->baseline.mean[2];
    const float combined = first->center + second->center;
    const float tolerance = tolerance_scale * baseline;
    const float midpoint_delta = goodix_primitives_hr_decision_absolute(
        combined * 0.5f - baseline);
    const float first_delta = goodix_primitives_hr_decision_absolute(
        first->center - baseline);
    const float second_delta = goodix_primitives_hr_decision_absolute(
        second->center - baseline);
    const bool split = midpoint_delta < tolerance &&
        first_delta >= tolerance && second_delta >= tolerance &&
        state->baseline.count >= state->baseline.capacity &&
        first->tag == 1;
    if (!split) {
        goodix_primitives_hr_decision_decrement(state);
    } else {
        first->center = baseline;
        second->center = combined - baseline;
        goodix_primitives_hr_decision_decrement(state);
        goodix_primitives_hr_decision_decrement(state);
        if (!goodix_primitives_hr_decision_append(state, first)) {
            return false;
        }
    }
    return goodix_primitives_hr_decision_append(state, second);
}

static bool goodix_primitives_hr_decision_update_diagnostics(
    goodix_primitives_hr_decision_state *state,
    goodix_primitives_hr_decision_workspace *workspace,
    goodix_primitives_float_unary_fn square_root) {
    float variation_percent = 0.0f;
    float primary_mean = 0.0f;
    float auxiliary_mean = 0.0f;
    float interval_mean = 0.0f;
    if (state->primary_history.count == state->primary_history.capacity) {
        for (size_t index = 0u;
                index < GOODIX_PRIMITIVES_HR_DECISION_HISTORY_VALUES;
                ++index) {
            workspace->compacted[index] = goodix_primitives_float_from_bits(
                state->primary_history.values[index]);
        }
        if (!goodix_primitives_hr_mad_inlier_mask(
                workspace->compacted,
                GOODIX_PRIMITIVES_HR_DECISION_HISTORY_VALUES, 2,
                workspace->mad_scratch,
                GOODIX_PRIMITIVES_HR_DECISION_HISTORY_VALUES,
                workspace->inlier_mask,
                GOODIX_PRIMITIVES_HR_DECISION_HISTORY_VALUES)) {
            return false;
        }
        size_t compacted_count = 0u;
        for (size_t index = 0u;
                index < GOODIX_PRIMITIVES_HR_DECISION_HISTORY_VALUES;
                ++index) {
            if (workspace->inlier_mask[index] == 1u) {
                workspace->compacted[compacted_count++] =
                    goodix_primitives_float_from_bits(
                        state->primary_history.values[index]);
            }
        }
        float standard_deviation = 0.0f;
        if (!goodix_primitives_float_mean(
                workspace->compacted, compacted_count, &primary_mean) ||
                !goodix_primitives_sample_standard_deviation(
                    workspace->compacted, compacted_count, square_root,
                    &standard_deviation) ||
                !goodix_primitives_hr_process_history_mean(
                    &state->auxiliary_history, &auxiliary_mean) ||
                !goodix_primitives_hr_process_history_mean(
                    &state->interval_history, &interval_mean)) {
            return false;
        }
        if (primary_mean == 0.0f) {
            variation_percent = 200.0f;
        } else {
            variation_percent = standard_deviation / primary_mean * 100.0f;
            if (variation_percent < 0.0f) {
                variation_percent = standard_deviation / primary_mean * -100.0f;
            }
        }
    }
    state->diagnostic_variation_percent = variation_percent;
    state->diagnostic_primary_mean = primary_mean;
    state->diagnostic_auxiliary_mean = auxiliary_mean;
    state->diagnostic_interval_mean = interval_mean;
    return true;
}

bool goodix_primitives_hr_decision_update(void *context) {
    goodix_primitives_hr_decision_context *binding =
        (goodix_primitives_hr_decision_context *)context;
    if (binding == NULL || binding->state == NULL ||
            binding->workspace == NULL || binding->square_root == NULL) {
        return false;
    }
    goodix_primitives_hr_decision_state *state = binding->state;
    if (state->records == NULL || state->record_capacity == 0u ||
            state->record_count > state->record_capacity ||
            state->sample_rate == 0u || state->minimum_interval < 0 ||
            state->maximum_interval < 0 || state->baseline.count < 0 ||
            state->baseline.capacity <= 0 ||
            state->baseline.count > state->baseline.capacity ||
            !goodix_primitives_hr_decision_history_valid(
                &state->primary_history) ||
            !goodix_primitives_hr_decision_history_valid(
                &state->auxiliary_history) ||
            !goodix_primitives_hr_decision_history_valid(
                &state->interval_history)) {
        return false;
    }

    const uint32_t original_record_count = state->record_count;
    const uint32_t previous_update_count = state->source.update_count++;
    if (previous_update_count % state->sample_rate == 0u) {
        for (uint32_t index = 0u; index < state->record_count; ++index) {
            state->records[index].primary_second -= (float)state->sample_rate;
        }
    }
    if (state->source.ready != 1u) {
        return true;
    }

    goodix_primitives_hr_decision_record incoming = {
        .position = state->source.position,
        .primary_first = state->source.primary_first,
        .primary_second = state->source.primary_second,
        .auxiliary_first = state->source.auxiliary_first,
        .auxiliary_second = state->source.auxiliary_second,
        .center = state->source.auxiliary_first +
            state->source.auxiliary_second,
        .tag = 2,
        .flag = 0u,
        .reserved = {0u, 0u, 0u},
    };
    state->source.ready = 0u;
    state->source.position = 0.0f;
    state->source.primary_first = 0.0f;
    state->source.primary_second = 0.0f;
    state->source.auxiliary_first = 0.0f;
    state->source.auxiliary_second = 0.0f;
    if (state->record_count < 2u) {
        return goodix_primitives_hr_decision_append(state, &incoming);
    }

    goodix_primitives_hr_decision_record older =
        state->records[state->record_count - 2u];
    goodix_primitives_hr_decision_record current =
        state->records[state->record_count - 1u];
    const float current_primary_ratio =
        current.primary_second / current.primary_first;
    const float older_primary_total =
        older.primary_first + older.primary_second;
    const float current_primary_total =
        current.primary_first + current.primary_second;
    const float incoming_primary_total =
        incoming.primary_first + incoming.primary_second;
    const float older_primary_ratio =
        older.primary_second / older.primary_first;
    const float incoming_primary_ratio =
        incoming.primary_second / incoming.primary_first;
    const float cross_primary_ratio =
        current.primary_first / older.primary_second;
    const float second_cross_primary_ratio =
        current.primary_second / incoming.primary_first;
    const float primary_minimum = goodix_primitives_hr_decision_minimum(
        goodix_primitives_hr_decision_minimum(
            older_primary_total, current_primary_total),
        incoming_primary_total);
    const float primary_maximum = goodix_primitives_hr_decision_maximum(
        goodix_primitives_hr_decision_maximum(
            older_primary_total, current_primary_total),
        incoming_primary_total);
    const float primary_geometry_ratio = primary_minimum / primary_maximum;

    const float older_auxiliary_total =
        older.auxiliary_first + older.auxiliary_second;
    const float current_auxiliary_total =
        current.auxiliary_first + current.auxiliary_second;
    const float incoming_auxiliary_total =
        incoming.auxiliary_first + incoming.auxiliary_second;
    const float previous_interval = current.position - older.position;
    const float incoming_interval = incoming.position - current.position;
    const float combined_interval = incoming.position - older.position;
    const float interval_minimum = goodix_primitives_hr_decision_minimum(
        goodix_primitives_hr_decision_minimum(
            previous_interval, current_auxiliary_total), incoming_interval);
    const float current_previous_ratio =
        goodix_primitives_hr_decision_maximum(
            current_auxiliary_total, previous_interval) /
        goodix_primitives_hr_decision_minimum(
            current_auxiliary_total, previous_interval);
    const float current_incoming_ratio =
        goodix_primitives_hr_decision_maximum(
            current_auxiliary_total, incoming_interval) /
        goodix_primitives_hr_decision_minimum(
            current_auxiliary_total, incoming_interval);
    const float interval_pair_ratio =
        goodix_primitives_hr_decision_minimum(
            previous_interval, incoming_interval) /
        goodix_primitives_hr_decision_maximum(
            previous_interval, incoming_interval);
    const float auxiliary_minimum = goodix_primitives_hr_decision_minimum(
        goodix_primitives_hr_decision_minimum(
            older_auxiliary_total, current_auxiliary_total),
        incoming_auxiliary_total);
    const float auxiliary_maximum = goodix_primitives_hr_decision_maximum(
        goodix_primitives_hr_decision_maximum(
            older_auxiliary_total, current_auxiliary_total),
        incoming_auxiliary_total);
    const float auxiliary_geometry_ratio =
        auxiliary_minimum / auxiliary_maximum;

    if (!goodix_primitives_counted_word_history_push(
            &state->primary_history,
            goodix_primitives_float_bits(incoming_primary_total)) ||
            !goodix_primitives_counted_word_history_push(
                &state->auxiliary_history,
                goodix_primitives_float_bits(incoming_auxiliary_total)) ||
            !goodix_primitives_counted_word_history_push(
                &state->interval_history,
                goodix_primitives_float_bits(incoming_interval)) ||
            !goodix_primitives_hr_decision_update_diagnostics(
                state, binding->workspace, binding->square_root)) {
        return false;
    }

    if (state->mode == 1 &&
            incoming.primary_first / current.primary_first < 0.05f &&
            incoming.primary_second / current.primary_second < 0.05f) {
        incoming.flag = 1u;
        current.tag = 1;
        goodix_primitives_hr_decision_decrement(state);
        return goodix_primitives_hr_decision_append(state, &current) &&
            goodix_primitives_hr_decision_append(state, &incoming);
    }
    if (current.flag == 1u &&
            current.primary_first / incoming.primary_first < 0.05f &&
            current.primary_second / incoming.primary_second < 0.05f) {
        goodix_primitives_hr_decision_decrement(state);
        incoming.center = incoming.position - older.position;
        incoming.tag = 1;
        return goodix_primitives_hr_decision_append(state, &incoming);
    }
    if (state->stale_count > 9) {
        state->stale_count = 0;
    }

    if (state->mode == 0) {
        const float primary_midpoint =
            (primary_minimum + primary_maximum) * 0.5f;
        const float auxiliary_midpoint =
            (auxiliary_minimum + auxiliary_maximum) * 0.5f;
        const float interval_midpoint =
            (previous_interval + incoming_interval) * 0.5f;
        if (primary_geometry_ratio > 0.8f &&
                auxiliary_geometry_ratio > 0.8f &&
                interval_pair_ratio > 0.8f &&
                auxiliary_midpoint > interval_midpoint * 0.6f) {
            goodix_primitives_hr_decision_decrement(state);
            current.tag = 1;
            current.center = previous_interval;
            if (!goodix_primitives_hr_decision_append(state, &current) ||
                    !goodix_primitives_running_triplet_update(
                        &state->baseline, primary_midpoint,
                        auxiliary_midpoint, interval_midpoint,
                        state->timestamp)) {
                return false;
            }
            state->mode = 1;
        } else {
            if (incoming_primary_total <= current_primary_total * 0.5f ||
                    incoming_auxiliary_total <=
                        current_auxiliary_total * 0.5f) {
                if (incoming_interval <= (float)state->maximum_interval) {
                    return true;
                }
                state->record_count = 0u;
                return true;
            }
            return goodix_primitives_hr_decision_append(state, &incoming);
        }
    }

    if (previous_interval > (float)state->maximum_interval ||
            incoming_interval > (float)state->maximum_interval) {
        return goodix_primitives_hr_decision_append(state, &incoming);
    }
    if (state->timestamp - state->baseline.timestamp > UINT32_C(20) &&
            state->diagnostic_variation_percent > 0.0f &&
            state->diagnostic_variation_percent < 30.0f) {
        state->baseline.mean[0] = state->diagnostic_primary_mean;
        state->baseline.mean[1] = state->diagnostic_auxiliary_mean;
        state->baseline.mean[2] = state->diagnostic_interval_mean;
    }

    const int32_t saved_current_tag = current.tag;
    const float tolerance_scale = 0.2f;
    const float primary_rejection_limit = state->baseline.mean[0] * 3.0f;
    const float baseline_interval = state->baseline.mean[2];
    const float primary_acceptance_limit = state->baseline.mean[0] * 0.3f;
    if (older.tag == 1) {
        const float combined_distance =
            goodix_primitives_hr_decision_absolute(
                combined_interval - baseline_interval);
        if (incoming_primary_total >= primary_acceptance_limit &&
                combined_distance <
                    goodix_primitives_hr_decision_absolute(
                        previous_interval - baseline_interval) &&
                combined_distance < baseline_interval * tolerance_scale) {
            goodix_primitives_hr_decision_merge(&current, &incoming, true);
            goodix_primitives_hr_decision_decrement(state);
            return goodix_primitives_hr_decision_append(state, &current);
        }
        if (goodix_primitives_hr_decision_absolute(
                    baseline_interval - older.center) <
                    baseline_interval * tolerance_scale &&
                current_primary_total > primary_rejection_limit &&
                goodix_primitives_hr_decision_absolute(
                    previous_interval - baseline_interval) <
                    baseline_interval * tolerance_scale) {
            current.tag = 1;
            current.center = previous_interval;
            if (!goodix_primitives_hr_decision_rebalance(
                    state, tolerance_scale, &older, &current)) {
                return false;
            }
            incoming.center = incoming.position - current.position;
            incoming.tag = 2;
            if (!goodix_primitives_hr_decision_append(state, &incoming)) {
                return false;
            }
            if (current.tag == 1) {
                return goodix_primitives_running_triplet_update(
                    &state->baseline, current_primary_total,
                    current_auxiliary_total, current.center,
                    state->timestamp);
            }
            return true;
        }
    }

    const bool ratio_rejection =
        (older_primary_ratio > 0.5f && cross_primary_ratio > 2.0f &&
         incoming_primary_ratio < 0.5f) ||
        (older_primary_ratio > 2.0f &&
         second_cross_primary_ratio > 2.0f &&
         incoming_primary_ratio < 2.0f) ||
        (older_primary_ratio > 0.5f && cross_primary_ratio > 2.0f &&
         second_cross_primary_ratio > 2.0f &&
         incoming_primary_ratio < 2.0f) ||
        (older_primary_ratio > 2.0f && current_primary_ratio < 0.5f &&
         incoming_primary_ratio < 2.0f);
    if (incoming_interval < current_primary_total ||
            (current_primary_total >= primary_acceptance_limit &&
             ratio_rejection)) {
        if (state->latch == 0) {
            state->latch = 1;
            if (original_record_count >= 2u &&
                    original_record_count - 2u < state->record_count) {
                state->records[original_record_count - 2u].tag = 5;
            }
        }
        current.tag = 4;
        goodix_primitives_hr_decision_decrement(state);
        if (!goodix_primitives_hr_decision_append(state, &current)) {
            return false;
        }
        incoming.center = incoming.position - current.position;
        incoming.tag = 2;
        if (!goodix_primitives_hr_decision_append(state, &incoming)) {
            return false;
        }
        ++state->stale_count;
        return true;
    }

    const bool geometry_good =
        !(current_previous_ratio > 1.5f && current_incoming_ratio > 1.5f) &&
        interval_minimum > (float)state->minimum_interval;
    const bool energy_good =
        current_primary_total >
            (older_primary_total + incoming_primary_total) * 0.25f &&
        !(current_primary_ratio >= 2.0f && state->latch != 0);
    const bool baseline_good =
        goodix_primitives_hr_decision_absolute(
            current_auxiliary_total - state->baseline.mean[1]) <
            state->baseline.mean[1] * 0.3f &&
        !(previous_interval - current_auxiliary_total >=
              baseline_interval * tolerance_scale &&
          previous_interval - older_auxiliary_total >=
              baseline_interval * tolerance_scale);
    if ((energy_good && geometry_good) || baseline_good) {
        state->stale_count = 0;
        if (state->latch == 1) {
            state->latch = 0;
            current.tag = 5;
        } else {
            current.tag = 1;
        }
        if (!goodix_primitives_hr_decision_rebalance(
                state, tolerance_scale, &older, &current)) {
            return false;
        }
        const float center_tolerance = current.center * tolerance_scale;
        const bool keep_current =
            goodix_primitives_hr_decision_absolute(
                current.center - baseline_interval) >=
                baseline_interval * tolerance_scale &&
            ((older.tag != 1 || saved_current_tag != 2) ||
             (goodix_primitives_hr_decision_absolute(
                  current.center - older_auxiliary_total) >=
                  center_tolerance &&
              goodix_primitives_hr_decision_absolute(
                  current.center - current_auxiliary_total) >=
                  center_tolerance) ||
             cross_primary_ratio > 2.0f || current_primary_ratio > 2.0f ||
             current_primary_ratio < 0.5f);
        if (keep_current) {
            current.tag = 4;
            goodix_primitives_hr_decision_decrement(state);
            if (!goodix_primitives_hr_decision_append(state, &current)) {
                return false;
            }
        }
        incoming.center = incoming.position - current.position;
        incoming.tag = 2;
        if (!goodix_primitives_hr_decision_append(state, &incoming)) {
            return false;
        }
        if (current.tag == 1) {
            return goodix_primitives_running_triplet_update(
                &state->baseline, current_primary_total,
                current_auxiliary_total, current.center,
                state->timestamp);
        }
        return true;
    }

    ++state->stale_count;
    if (state->latch == 1) {
        current.tag = 4;
        goodix_primitives_hr_decision_decrement(state);
        if (!goodix_primitives_hr_decision_append(state, &current)) {
            return false;
        }
        older.position = current.position;
    } else if (current_primary_ratio <= 2.0f &&
            (current_primary_ratio < 0.5f ||
             goodix_primitives_hr_decision_absolute(
                 current_auxiliary_total + incoming_auxiliary_total -
                 baseline_interval) <=
             goodix_primitives_hr_decision_absolute(
                 older_auxiliary_total + current_auxiliary_total -
                 baseline_interval))) {
        const bool continuation =
            incoming_primary_total * 2.0f < current_primary_total ||
            second_cross_primary_ratio > 2.0f ||
            ((goodix_primitives_hr_decision_absolute(
                  current_auxiliary_total + incoming_auxiliary_total -
                  previous_interval) <
                  goodix_primitives_hr_decision_absolute(
                      current_auxiliary_total + incoming_auxiliary_total -
                      combined_interval) ||
              goodix_primitives_hr_decision_absolute(
                  baseline_interval - previous_interval) <
                  goodix_primitives_hr_decision_absolute(
                      baseline_interval - combined_interval)) &&
             goodix_primitives_hr_decision_absolute(
                 baseline_interval - older.center) <
                 baseline_interval * tolerance_scale &&
             incoming_primary_total * 0.5f < current_primary_total &&
             second_cross_primary_ratio > 0.5f);
        goodix_primitives_hr_decision_merge(
            &current, &incoming, !continuation);
        current.tag = 3;
        goodix_primitives_hr_decision_decrement(state);
        return goodix_primitives_hr_decision_append(state, &current);
    } else {
        const bool continuation =
            current_primary_total * 2.0f < older_primary_total ||
            ((goodix_primitives_hr_decision_absolute(
                  older_auxiliary_total + current_auxiliary_total -
                  older.center) <
                  goodix_primitives_hr_decision_absolute(
                      older_auxiliary_total + current_auxiliary_total -
                      (older.center + previous_interval)) ||
              goodix_primitives_hr_decision_absolute(
                  baseline_interval - older.center) <
                  goodix_primitives_hr_decision_absolute(
                      baseline_interval -
                      (older.center + previous_interval))) &&
             goodix_primitives_hr_decision_absolute(
                 baseline_interval - older.center) <
                 baseline_interval * tolerance_scale);
        goodix_primitives_hr_decision_merge(
            &older, &current, !continuation);
        goodix_primitives_hr_decision_decrement(state);
        goodix_primitives_hr_decision_decrement(state);
        if (!goodix_primitives_hr_decision_append(state, &older)) {
            return false;
        }
    }
    incoming.center = incoming.position - older.position;
    incoming.tag = 2;
    return goodix_primitives_hr_decision_append(state, &incoming);
}

bool goodix_primitives_float_window_mean(
    const goodix_primitives_decimated_float_window *window, float *result) {
    if (window == NULL || window->values == NULL || result == NULL ||
            window->count == 0u || window->count > window->capacity) {
        return false;
    }
    float sum = 0.0f;
    for (size_t index = 0u; index < window->count; ++index) {
        sum += window->values[index];
    }
    *result = sum / (float)window->count;
    return true;
}

bool goodix_primitives_float_window_remove(
    goodix_primitives_decimated_float_window *window, size_t index,
    float *removed) {
    if (window == NULL || window->values == NULL || removed == NULL ||
            window->capacity == 0u || window->count == 0u ||
            window->count > window->capacity || index >= window->count ||
            window->cursor >= window->capacity ||
            (window->count < window->capacity && window->cursor == 0u)) {
        return false;
    }
    const float value = window->values[index];
    for (size_t source = index + 1u; source < window->count; ++source) {
        window->values[source - 1u] = window->values[source];
    }
    if (window->count == window->capacity && window->cursor == 0u) {
        window->cursor = (uint16_t)(window->capacity - 1u);
    } else {
        --window->cursor;
    }
    --window->count;
    window->sum -= value;
    *removed = value;
    return true;
}

bool goodix_primitives_i16_window_push(
    goodix_primitives_i16_window *window, int16_t value) {
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

bool goodix_primitives_byte_window_push(
    goodix_primitives_byte_window *window, uint8_t value) {
    if (window == NULL || window->values == NULL || window->capacity == 0u ||
            window->count > window->capacity ||
            window->cursor >= window->capacity) {
        return false;
    }
    if (window->count < window->capacity) {
        window->values[window->count] = value;
        ++window->count;
    } else {
        for (size_t index = 1u; index < window->capacity; ++index) {
            window->values[index - 1u] = window->values[index];
        }
        window->values[window->capacity - 1u] = value;
    }
    ++window->cursor;
    if (window->cursor == window->capacity) {
        window->cursor = 0u;
    }
    return true;
}

bool goodix_primitives_decimated_i16_window_push(
    goodix_primitives_decimated_i16_window *window, int16_t value) {
    if (window == NULL || window->values == NULL || window->capacity == 0u ||
            window->count > window->capacity ||
            window->cursor >= window->capacity || window->period == 0u ||
            window->phase >= window->period) {
        return false;
    }
    if (window->phase == 0u) {
        goodix_primitives_i16_window base = {
            .values = window->values,
            .count = window->count,
            .capacity = window->capacity,
        };
        if (!goodix_primitives_i16_window_push(&base, value)) {
            return false;
        }
        window->count = base.count;
        ++window->cursor;
        if (window->cursor == window->capacity) {
            window->cursor = 0u;
        }
    }
    ++window->phase;
    if (window->phase == window->period) {
        window->phase = 0u;
    }
    return true;
}

bool goodix_primitives_decimated_float_window_push(
    goodix_primitives_decimated_float_window *window, float value) {
    if (window == NULL || window->values == NULL || window->capacity == 0u ||
            window->count > window->capacity ||
            window->cursor >= window->capacity || window->period == 0u ||
            window->phase >= window->period) {
        return false;
    }
    if (window->phase == 0u) {
        if (window->count < window->capacity) {
            window->values[window->count] = value;
            window->sum += value;
            ++window->count;
        } else {
            const float evicted = window->values[0];
            for (size_t index = 1u; index < window->capacity; ++index) {
                window->values[index - 1u] = window->values[index];
            }
            window->values[window->capacity - 1u] = value;
            window->sum = window->sum + value - evicted;
        }
        ++window->cursor;
        if (window->cursor == window->capacity) {
            window->cursor = 0u;
        }
    }
    ++window->phase;
    if (window->phase == window->period) {
        window->phase = 0u;
    }
    return true;
}

bool goodix_primitives_truncate_decimal(float value, uint8_t places,
                                        float *result) {
    if (result == NULL || places > 9u) {
        return false;
    }
    const float scale = goodix_primitives_unsigned_power(10.0f, places);
    const float scaled = value * scale;
    if (scaled != scaled || scaled < -2147483648.0f ||
            scaled >= 2147483648.0f) {
        return false;
    }
    *result = (float)(int32_t)scaled / scale;
    return true;
}

bool goodix_primitives_bit_reverse_permute_pairs(
    goodix_primitives_word_pair *pairs, size_t pair_count,
    uint8_t bit_count) {
    if (pairs == NULL || bit_count >= 31u) {
        return false;
    }
    const size_t required = (size_t)1u << bit_count;
    if (pair_count < required) {
        return false;
    }
    for (size_t index = 0u; index < required; ++index) {
        uint32_t reversed = 0u;
        if (!goodix_primitives_reverse_low_bits(
                (uint32_t)index, bit_count, &reversed)) {
            return false;
        }
        if (index < (size_t)reversed) {
            const goodix_primitives_word_pair saved = pairs[index];
            pairs[index] = pairs[reversed];
            pairs[reversed] = saved;
        }
    }
    return true;
}

/* Exact binary32 rounding of cos(pi * index / 128), index 0..64. The stock
 * image binds the same mathematical quarter-wave table at 0x000BD334. */
static const float goodix_primitives_fft_cosine_quarter[65] = {
    0x1.0000000000000p+0f, 0x1.ffd8860000000p-1f,
    0x1.ff621e0000000p-1f, 0x1.fe9cda0000000p-1f,
    0x1.fd88da0000000p-1f, 0x1.fc26480000000p-1f,
    0x1.fa75580000000p-1f, 0x1.f876500000000p-1f,
    0x1.f6297c0000000p-1f, 0x1.f38f3a0000000p-1f,
    0x1.f0a7f00000000p-1f, 0x1.ed740e0000000p-1f,
    0x1.e9f4160000000p-1f, 0x1.e6288e0000000p-1f,
    0x1.e212100000000p-1f, 0x1.ddb13c0000000p-1f,
    0x1.d906bc0000000p-1f, 0x1.d4134e0000000p-1f,
    0x1.ced7b00000000p-1f, 0x1.c954b20000000p-1f,
    0x1.c38b300000000p-1f, 0x1.bd7c0a0000000p-1f,
    0x1.b728340000000p-1f, 0x1.b090a60000000p-1f,
    0x1.a9b6620000000p-1f, 0x1.a29a7a0000000p-1f,
    0x1.9b3e040000000p-1f, 0x1.93a2240000000p-1f,
    0x1.8bc8060000000p-1f, 0x1.83b0e00000000p-1f,
    0x1.7b5df20000000p-1f, 0x1.72d0840000000p-1f,
    0x1.6a09e60000000p-1f, 0x1.610b760000000p-1f,
    0x1.57d6940000000p-1f, 0x1.4e6cac0000000p-1f,
    0x1.44cf320000000p-1f, 0x1.3affa20000000p-1f,
    0x1.30ff800000000p-1f, 0x1.26d0540000000p-1f,
    0x1.1c73b40000000p-1f, 0x1.11eb360000000p-1f,
    0x1.07387a0000000p-1f, 0x1.f8ba4e0000000p-2f,
    0x1.e2b5d40000000p-2f, 0x1.cc66ea0000000p-2f,
    0x1.b5d1000000000p-2f, 0x1.9ef7940000000p-2f,
    0x1.87de2a0000000p-2f, 0x1.7088540000000p-2f,
    0x1.58f9a80000000p-2f, 0x1.4135ca0000000p-2f,
    0x1.2940620000000p-2f, 0x1.111d260000000p-2f,
    0x1.f19f980000000p-3f, 0x1.c0b8260000000p-3f,
    0x1.8f8b840000000p-3f, 0x1.5e21440000000p-3f,
    0x1.2c81060000000p-3f, 0x1.f564e60000000p-4f,
    0x1.917a6c0000000p-4f, 0x1.2d520a0000000p-4f,
    0x1.91f65e0000000p-5f, 0x1.9215600000000p-6f,
    0x0.0p+0f,
};

static void goodix_primitives_fft_butterfly(
    float *left, float *right, float cosine, float sine) {
    const float right_real = right[0];
    const float right_imaginary = right[1];
    const float real_difference = left[0] - right_real;
    const float imaginary_difference = left[1] - right_imaginary;
    left[0] += right_real;
    left[1] += right_imaginary;
    right[0] = real_difference * cosine + imaginary_difference * sine;
    right[1] = imaginary_difference * cosine - real_difference * sine;
}

static void goodix_primitives_fft_twiddle(
    size_t table_index, float *cosine, float *sine) {
    if (table_index <= 64u) {
        *cosine = goodix_primitives_fft_cosine_quarter[table_index];
        *sine = goodix_primitives_fft_cosine_quarter[64u - table_index];
    } else {
        *cosine = -goodix_primitives_fft_cosine_quarter[128u - table_index];
        *sine = goodix_primitives_fft_cosine_quarter[table_index - 64u];
    }
}

bool goodix_primitives_fft_complex_128_dif(
    float *interleaved, size_t value_count) {
    if (interleaved == NULL ||
            value_count < GOODIX_PRIMITIVES_FFT_COMPLEX_VALUES) {
        return false;
    }
    const size_t complex_count = 128u;
    const size_t initial_half = complex_count / 2u;
    size_t table_index = 0u;
    for (size_t group = 0u; group < initial_half; ++group) {
        float cosine = 0.0f;
        float sine = 0.0f;
        goodix_primitives_fft_twiddle(table_index, &cosine, &sine);
        goodix_primitives_fft_butterfly(
            interleaved + group * 2u,
            interleaved + (group + initial_half) * 2u,
            cosine, sine);
        table_index += 2u;
    }

    size_t width = initial_half;
    size_t twiddle_stride = 2u;
    while (width > 2u) {
        twiddle_stride *= 2u;
        const size_t half = width / 2u;
        table_index = 0u;
        for (size_t group = 0u; group < half; ++group) {
            float cosine = 0.0f;
            float sine = 0.0f;
            goodix_primitives_fft_twiddle(table_index, &cosine, &sine);
            table_index += twiddle_stride;
            for (size_t position = group; position < complex_count;
                    position += width) {
                goodix_primitives_fft_butterfly(
                    interleaved + position * 2u,
                    interleaved + (position + half) * 2u,
                    cosine, sine);
            }
        }
        width = half;
    }
    for (size_t group = 0u; group < complex_count; group += 2u) {
        float *const left = interleaved + group * 2u;
        float *const right = left + 2u;
        const float left_real = left[0];
        const float left_imaginary = left[1];
        left[0] = left_real + right[0];
        left[1] = left_imaginary + right[1];
        right[0] = left_real - right[0];
        right[1] = left_imaginary - right[1];
    }
    return true;
}

bool goodix_primitives_fft_real_magnitude_256(
    float *values, size_t value_capacity, size_t input_count,
    goodix_primitives_float_unary_fn square_root) {
    if (values == NULL || square_root == NULL ||
            value_capacity < GOODIX_PRIMITIVES_FFT_REAL_VALUES ||
            input_count > GOODIX_PRIMITIVES_FFT_REAL_VALUES) {
        return false;
    }
    for (size_t index = input_count;
            index < GOODIX_PRIMITIVES_FFT_REAL_VALUES; ++index) {
        values[index] = 0.0f;
    }
    if (!goodix_primitives_fft_complex_128_dif(
            values, value_capacity)) {
        return false;
    }
    for (size_t index = 0u; index < 128u; ++index) {
        uint32_t reversed = 0u;
        if (!goodix_primitives_reverse_low_bits(
                (uint32_t)index, 7u, &reversed)) {
            return false;
        }
        if (index < (size_t)reversed) {
            const float saved_real = values[index * 2u];
            const float saved_imaginary = values[index * 2u + 1u];
            values[index * 2u] = values[(size_t)reversed * 2u];
            values[index * 2u + 1u] =
                values[(size_t)reversed * 2u + 1u];
            values[(size_t)reversed * 2u] = saved_real;
            values[(size_t)reversed * 2u + 1u] = saved_imaginary;
        }
    }

    const float even_sum = values[0];
    const float odd_sum = values[1];
    for (size_t index = 1u; index <= 64u; ++index) {
        float *const forward = values + index * 2u;
        float *const reverse = values + (128u - index) * 2u;
        const float forward_real = forward[0];
        const float reverse_real = reverse[0];
        const float forward_imaginary = forward[1];
        const float reverse_imaginary = reverse[1];
        const float cosine = goodix_primitives_fft_cosine_quarter[index];
        const float sine =
            goodix_primitives_fft_cosine_quarter[64u - index];
        const float imaginary_sum = forward_imaginary + reverse_imaginary;

        const float first_real = forward_real + reverse_real +
            imaginary_sum * cosine +
            (reverse_real - forward_real) * sine;
        const float first_imaginary =
            (forward_imaginary - reverse_imaginary) +
            (reverse_real - forward_real) * cosine -
            imaginary_sum * sine;
        const float second_real = forward_real + reverse_real -
            imaginary_sum * cosine +
            (forward_real - reverse_real) * sine;
        const float second_imaginary =
            (reverse_imaginary - forward_imaginary) -
            (forward_real - reverse_real) * cosine -
            imaginary_sum * sine;
        forward[0] = square_root(
            first_real * first_real + first_imaginary * first_imaginary);
        reverse[0] = square_root(
            second_real * second_real +
            second_imaginary * second_imaginary);
    }
    for (size_t index = 1u; index < 128u; ++index) {
        values[index] = values[index * 2u] * 0.5f;
    }
    values[0] = 0.0f;
    values[128] = even_sum < odd_sum
        ? odd_sum - even_sum : even_sum - odd_sum;
    return true;
}

static int32_t goodix_primitives_u32_as_i32(uint32_t value) {
    if (value <= (uint32_t)INT32_MAX) {
        return (int32_t)value;
    }
    return INT32_MIN + (int32_t)(value - UINT32_C(0x80000000));
}

bool goodix_primitives_finalize_warmup_average(
    goodix_primitives_warmup_average_state *state) {
    if (state == NULL) {
        return false;
    }
    if (state->phase == 1u) {
        state->second = state->first;
        state->third = state->first;
        state->average = state->first;
    } else if (state->phase == 2u) {
        state->third = state->first;
        state->average = state->second;
    } else if (state->phase == 3u) {
        const uint32_t sum = (uint32_t)state->first +
                             (uint32_t)state->second +
                             (uint32_t)state->third;
        state->average = goodix_primitives_u32_as_i32(sum) / 3;
    }
    state->phase = 4u;
    return true;
}

bool goodix_primitives_normalize_by_max(float *values, size_t count) {
    if (values == NULL || count == 0u) {
        return false;
    }
    float maximum = values[0];
    for (size_t index = 1u; index < count; ++index) {
        if (maximum < values[index]) {
            maximum = values[index];
        }
    }
    if (maximum != maximum) {
        return false;
    }
    const float threshold = 0x1.0c6f7ap-20f;
    const float factor = maximum < threshold ? 1.0f : 1.0f / maximum;
    for (size_t index = 0u; index < count; ++index) {
        values[index] *= factor;
    }
    return true;
}

bool goodix_primitives_nadt_clip_normalize(
    const float *input, size_t count, float *output,
    size_t output_capacity) {
    if (output_capacity < count ||
            (count != 0u && (input == NULL || output == NULL))) {
        return false;
    }
    float scale = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        const float value = input[index];
        const float magnitude = value < 0.0f ? -value : value;
        if (magnitude > scale) {
            scale = magnitude;
        }
    }
    union {
        float value;
        uint32_t bits;
    } encoded = {.value = scale};
    if ((int32_t)encoded.bits >= (int32_t)UINT32_C(0x3CA3D70A)) {
        scale = 0x1.47ae14p-6f;
        encoded.value = scale;
    }
    if ((int32_t)encoded.bits < (int32_t)UINT32_C(0x33D6BF95)) {
        for (size_t index = 0u; index < count; ++index) {
            output[index] = 0.0f;
        }
        return true;
    }
    const float negative_scale = -scale;
    for (size_t index = 0u; index < count; ++index) {
        const float value = input[index];
        float clipped = value <= scale ? value : scale;
        if (!(clipped >= negative_scale)) {
            clipped = negative_scale;
        } else if (!(value <= scale)) {
            /* The stock VFP compare chooses +scale for unordered input. */
            clipped = scale;
        } else {
            clipped = value;
        }
        output[index] = clipped / scale;
    }
    return true;
}

bool goodix_primitives_spo2_smoothed_scale(
    uint32_t sample_count, float sample, uint32_t rate,
    double *accumulator, int32_t *result) {
    if (accumulator == NULL || result == NULL) {
        return false;
    }
    *result = 0;
    if (sample_count <= 60u) {
        *accumulator += (double)sample;
        if (sample_count == 60u) {
            *accumulator /= 60.0;
        }
        return true;
    }
    *accumulator = (*accumulator * 59.0 + (double)sample) / 60.0;
    const float mean = (float)*accumulator;
    if (sample_count % 25u != 0u || !(mean > 0.0f)) {
        return true;
    }
    const float scaled = ((float)rate / 10000.0f) * mean;
    if (scaled != scaled || scaled < -2147483648.0f ||
            scaled >= 2147483648.0f) {
        return false;
    }
    *result = (int32_t)scaled;
    return true;
}

bool goodix_primitives_percentile_lookup(
    const float *values, size_t count, uint32_t percentage, float *result) {
    if (values == NULL || result == NULL || count == 0u ||
            count > (size_t)INT16_MAX || percentage >= 100u) {
        return false;
    }
    const float scaled = ((float)percentage / 100.0f) * (float)count;
    const size_t index = (size_t)(int32_t)scaled;
    if (index >= count) {
        return false;
    }
    *result = values[index];
    return true;
}

bool goodix_primitives_i32_mean(const int32_t *values, size_t count,
                                float *result) {
    if (values == NULL || result == NULL || count == 0u ||
            count > (size_t)INT32_MAX) {
        return false;
    }
    int64_t sum = 0;
    for (size_t index = 0u; index < count; ++index) {
        sum += values[index];
    }
    *result = (float)sum / (float)count;
    return true;
}

bool goodix_primitives_i32_squared_deviation_sum(
    const int32_t *values, size_t count,
    goodix_primitives_float_unary_fn round_provider, uint32_t *result) {
    if (values == NULL || round_provider == NULL || result == NULL ||
            count == 0u) {
        return false;
    }
    float mean = 0.0f;
    if (!goodix_primitives_i32_mean(values, count, &mean)) {
        return false;
    }
    const float rounded = round_provider(mean);
    if (rounded != rounded || rounded < -2147483648.0f ||
            rounded >= 2147483648.0f) {
        return false;
    }
    const int32_t center = (int32_t)rounded;
    uint32_t sum = 0u;
    for (size_t index = 0u; index < count; ++index) {
        int64_t difference = (int64_t)values[index] - (int64_t)center;
        if (difference < 0) {
            difference = -difference;
        }
        const uint64_t square = (uint64_t)difference *
                                (uint64_t)difference;
        if (square > (uint64_t)(UINT32_C(0x3FFFFFFF) - sum)) {
            *result = UINT32_C(0x3FFFFFFF);
            return true;
        }
        sum += (uint32_t)square;
    }
    *result = sum;
    return true;
}

static int16_t goodix_primitives_u16_as_i16(uint16_t value) {
    if (value <= (uint16_t)INT16_MAX) {
        return (int16_t)value;
    }
    return INT16_MIN + (int16_t)(value - UINT16_C(0x8000));
}

bool goodix_primitives_indexed_i16_trimmed_mean(
    const int16_t *values, size_t value_count, const int16_t *indices,
    size_t index_count, int16_t *result) {
    if (values == NULL || indices == NULL || result == NULL ||
            index_count == 0u || index_count > (size_t)INT32_MAX) {
        return false;
    }
    for (size_t index = 0u; index < index_count; ++index) {
        if (indices[index] < 0 || (size_t)indices[index] >= value_count) {
            return false;
        }
    }
    int16_t maximum = values[indices[0]];
    int16_t minimum = maximum;
    uint16_t wrapped_sum = 0u;
    for (size_t index = 0u; index < index_count; ++index) {
        const int16_t value = values[indices[index]];
        if (maximum <= value) {
            maximum = value;
        }
        if (value <= minimum) {
            minimum = value;
        }
        wrapped_sum = (uint16_t)(wrapped_sum + (uint16_t)value);
    }
    int16_t aggregate = goodix_primitives_u16_as_i16(wrapped_sum);
    if (index_count > 2u) {
        uint16_t centered = (uint16_t)aggregate - (uint16_t)maximum;
        centered = (uint16_t)(centered - (uint16_t)minimum);
        aggregate = (int16_t)(goodix_primitives_u16_as_i16(centered) /
                              (int32_t)(index_count - 2u));
    }
    *result = aggregate;
    return true;
}

bool goodix_primitives_mask_columns_any(
    const uint8_t *packed_bits, size_t packed_bytes, size_t columns,
    size_t rows, uint8_t *output, size_t output_count) {
    if (packed_bits == NULL || output == NULL || output_count < columns ||
            (rows != 0u && columns > SIZE_MAX / rows)) {
        return false;
    }
    const size_t bit_count = columns * rows;
    if (bit_count > SIZE_MAX - 7u || packed_bytes < (bit_count + 7u) / 8u) {
        return false;
    }
    for (size_t column = 0u; column < columns; ++column) {
        for (size_t row = 0u; row < rows; ++row) {
            const size_t bit = row * columns + column;
            if (((packed_bits[bit / 8u] >> (bit & 7u)) & 1u) != 0u) {
                output[column] = 1u;
                break;
            }
        }
    }
    return true;
}

bool goodix_primitives_channel_scale_copy(
    const float *source, size_t count, uint32_t mode,
    const float *mode_one_scales, float mode_one_factor,
    float *destination, size_t destination_count, float *factor) {
    if (factor == NULL || destination_count < count ||
            (count != 0u && (source == NULL || destination == NULL)) ||
            (mode == 1u && count != 0u && mode_one_scales == NULL)) {
        return false;
    }
    *factor = mode == 1u ? mode_one_factor : 1.0f;
    for (size_t index = 0u; index < count; ++index) {
        destination[index] = mode == 1u
            ? source[index] * mode_one_scales[index]
            : source[index];
    }
    return true;
}

bool goodix_primitives_float_transform_prefix_copy(
    const float *input, size_t input_count, size_t transform_count,
    float *scratch, size_t scratch_capacity,
    float *output, size_t output_capacity, size_t output_count,
    goodix_primitives_float_transform_fn transform) {
    if (input == NULL || scratch == NULL || output == NULL ||
            transform == NULL || input_count > scratch_capacity ||
            transform_count > scratch_capacity ||
            output_count > transform_count ||
            output_count > output_capacity) {
        return false;
    }
    for (size_t index = 0u; index < input_count; ++index) {
        scratch[index] = input[index];
    }
    transform(scratch, input_count, transform_count);
    for (size_t index = 0u; index < output_count; ++index) {
        output[index] = scratch[index];
    }
    return true;
}

bool goodix_primitives_fft_magnitude_prepare(
    const float *float_input, const uint16_t *packed_input,
    bool use_packed_input, size_t input_count, bool normalize,
    float *scratch, size_t scratch_capacity,
    float *output, size_t output_capacity, size_t output_count,
    goodix_primitives_float_unary_fn square_root) {
    if (scratch == NULL || output == NULL || square_root == NULL ||
            scratch_capacity < GOODIX_PRIMITIVES_FFT_SCRATCH_VALUES ||
            input_count == 0u ||
            input_count > GOODIX_PRIMITIVES_FFT_REAL_VALUES ||
            output_count > GOODIX_PRIMITIVES_FFT_MAGNITUDE_VALUES ||
            output_count > output_capacity ||
            (use_packed_input && packed_input == NULL) ||
            (!use_packed_input && float_input == NULL)) {
        return false;
    }
    for (size_t index = 0u; index < input_count; ++index) {
        if (use_packed_input) {
            const union {
                uint32_t bits;
                float value;
            } converted = {
                .bits = goodix_primitives_packed_5_10_to_f32_bits(
                    packed_input[index]),
            };
            scratch[index] = converted.value;
        } else {
            scratch[index] = float_input[index];
        }
    }
    if (!goodix_primitives_fft_real_magnitude_256(
            scratch, scratch_capacity, input_count, square_root)) {
        return false;
    }
    if (normalize) {
        for (size_t index = 0u;
                index < GOODIX_PRIMITIVES_FFT_MAGNITUDE_VALUES; ++index) {
            scratch[index] = (float)(
                ((double)scratch[index] * 2.0) / (double)input_count);
        }
    }
    for (size_t index = 0u; index < output_count; ++index) {
        output[index] = scratch[index];
    }
    return true;
}

static bool goodix_primitives_spo2_spectrum_prepare(
    const float *input, goodix_primitives_float_unary_fn square_root,
    goodix_primitives_spo2_spectral_workspace *workspace, float *output) {
    return goodix_primitives_fft_magnitude_prepare(
               input, NULL, false,
               GOODIX_PRIMITIVES_SPO2_SPECTRAL_INPUT_VALUES, false,
               workspace->fft_scratch, GOODIX_PRIMITIVES_FFT_SCRATCH_VALUES,
               output, GOODIX_PRIMITIVES_SPO2_SPECTRAL_OUTPUT_VALUES,
               GOODIX_PRIMITIVES_SPO2_SPECTRAL_OUTPUT_VALUES, square_root) &&
           goodix_primitives_normalize_by_max(
               output, GOODIX_PRIMITIVES_SPO2_SPECTRAL_OUTPUT_VALUES);
}

bool goodix_primitives_spo2_normalized_spectra_prepare(
    const goodix_primitives_spo2_spectral_source *source,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_spo2_spectral_workspace *workspace,
    goodix_primitives_spo2_spectral_result *result) {
    if (source == NULL || source->transformed_values == NULL ||
            source->transformed_value_count <
                GOODIX_PRIMITIVES_SPO2_SPECTRAL_FLOAT_CHANNELS *
                GOODIX_PRIMITIVES_SPO2_SPECTRAL_INPUT_VALUES ||
            square_root == NULL || workspace == NULL || result == NULL) {
        return false;
    }
    for (size_t channel = 0u;
            channel < GOODIX_PRIMITIVES_SPO2_SPECTRAL_PACKED_CHANNELS;
            ++channel) {
        if (source->packed_channels[channel] == NULL ||
                source->packed_channel_counts[channel] <
                    GOODIX_PRIMITIVES_SPO2_SPECTRAL_PACKED_VALUES) {
            return false;
        }
    }

    for (size_t channel = 0u;
            channel < GOODIX_PRIMITIVES_SPO2_SPECTRAL_FLOAT_CHANNELS;
            ++channel) {
        const float *const input = source->transformed_values +
            channel * GOODIX_PRIMITIVES_SPO2_SPECTRAL_INPUT_VALUES;
        if (!goodix_primitives_spo2_spectrum_prepare(
                input, square_root, workspace, result->channels[channel])) {
            return false;
        }
    }

    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_SPO2_SPECTRAL_INPUT_VALUES; ++index) {
        const size_t packed_index =
            index * GOODIX_PRIMITIVES_SPO2_SPECTRAL_PACKED_STRIDE;
        float sum = 0.0f;
        for (size_t channel = 0u;
                channel < GOODIX_PRIMITIVES_SPO2_SPECTRAL_PACKED_CHANNELS;
                ++channel) {
            const union {
                uint32_t bits;
                float value;
            } converted = {
                .bits = goodix_primitives_packed_6_9_to_f32_bits(
                    source->packed_channels[channel][packed_index]),
            };
            sum += converted.value;
        }
        workspace->fft_scratch[index] = sum * 0.25f;
    }
    return goodix_primitives_spo2_spectrum_prepare(
        workspace->fft_scratch, square_root, workspace,
        result->channels[GOODIX_PRIMITIVES_SPO2_SPECTRAL_CHANNELS - 1u]);
}

bool goodix_primitives_nadt_spectral_peak_prepare(
    const goodix_primitives_nadt_spectral_source *source,
    goodix_primitives_nadt_harmonic_candidate_fn select_harmonics,
    void *harmonic_context, goodix_primitives_float_unary_fn square_root,
    goodix_primitives_float_unary_fn floor_provider,
    goodix_primitives_nadt_spectral_workspace *workspace,
    goodix_primitives_nadt_spectral_result *result) {
    if (source == NULL || source->spectrum_values == NULL ||
            source->spectrum_count <
                GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES ||
            source->mode_one_scales == NULL ||
            source->scale_count <
                GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES ||
            select_harmonics == NULL || square_root == NULL ||
            floor_provider == NULL || workspace == NULL || result == NULL) {
        return false;
    }
    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)workspace, sizeof(*workspace));
    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)result, sizeof(*result));

    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES; ++index) {
        workspace->accumulated[index] += source->spectrum_values[index];
    }
    const float outlier_multiplier =
        (float)source->outlier_multiplier_tenths / 10.0f;
    if (!goodix_primitives_nadt_quartile_mask(
            workspace->accumulated,
            GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES,
            outlier_multiplier, workspace->quantile_scratch,
            GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES,
            workspace->outlier_mask,
            GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES) ||
            !goodix_primitives_zero_masked_sign_runs(
                workspace->accumulated,
                (const uint8_t *)workspace->outlier_mask,
                GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES,
                workspace->masked)) {
        return false;
    }

    float scale_factor = 1.0f;
    if (!goodix_primitives_channel_scale_copy(
            workspace->masked,
            GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES, 1u,
            source->mode_one_scales, source->mode_one_factor,
            workspace->scaled,
            GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES,
            &scale_factor) ||
            !goodix_primitives_fft_magnitude_prepare(
                workspace->scaled, NULL, false,
                GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES, false,
                workspace->fft_scratch, GOODIX_PRIMITIVES_FFT_SCRATCH_VALUES,
                workspace->fft_bins,
                GOODIX_PRIMITIVES_NADT_SPECTRAL_BIN_VALUES,
                GOODIX_PRIMITIVES_NADT_SPECTRAL_BIN_VALUES, square_root)) {
        return false;
    }

    const float radius_value = floor_provider((float)(
        (((double)scale_factor * 0.8) * 256.0) / 125.0));
    const float begin_value = floor_provider(5.12f);
    if (radius_value != radius_value || begin_value != begin_value ||
            radius_value < 0.0f || radius_value > (float)INT32_MAX ||
            begin_value < 0.0f || begin_value > (float)INT32_MAX) {
        return false;
    }
    const int32_t radius = (int32_t)radius_value;
    const int32_t begin = (int32_t)begin_value;
    int32_t peak_count = 0;
    if (!goodix_primitives_peak_select(
            0.1f, workspace->fft_bins,
            (int32_t)GOODIX_PRIMITIVES_NADT_SPECTRAL_BIN_VALUES,
            begin, (int32_t)GOODIX_PRIMITIVES_NADT_SPECTRAL_BIN_VALUES,
            radius,
            (int32_t)GOODIX_PRIMITIVES_NADT_SPECTRAL_PEAK_CAPACITY,
            workspace->peak_indices, workspace->peak_values, &peak_count)) {
        return false;
    }
    result->spectral_bin_count =
        GOODIX_PRIMITIVES_NADT_SPECTRAL_BIN_VALUES;
    result->peak_begin = begin;
    result->peak_radius = radius;
    result->peak_count = (size_t)peak_count;
    return select_harmonics(
        harmonic_context, 0.09765625f, workspace->peak_indices,
        workspace->peak_values, result->peak_count,
        result->candidate_indices, result->candidate_flags,
        GOODIX_PRIMITIVES_NADT_SPECTRAL_OUTPUT_CAPACITY);
}

bool goodix_primitives_nadt_harmonic_candidates_select(
    void *context, float bin_width, const int32_t *peak_indices,
    const float *peak_values, size_t peak_count,
    int32_t *candidate_indices, uint8_t *candidate_flags,
    size_t candidate_capacity) {
    goodix_primitives_nadt_harmonic_selector_context *const selector =
        context;
    if (selector == NULL || selector->workspace == NULL ||
            selector->square_root == NULL || candidate_indices == NULL ||
            candidate_flags == NULL || candidate_capacity == 0u ||
            candidate_capacity > GOODIX_PRIMITIVES_NADT_HARMONIC_CAPACITY ||
            ((peak_indices == NULL || peak_values == NULL) &&
             peak_count != 0u) || peak_count > (size_t)INT32_MAX ||
            !(bin_width >= 0.0f)) {
        return false;
    }
    goodix_primitives_nadt_harmonic_workspace *const workspace =
        selector->workspace;
    for (size_t lane = 0u;
            lane < GOODIX_PRIMITIVES_NADT_HARMONIC_CAPACITY; ++lane) {
        workspace->selected_indices[lane] = 0;
        workspace->selected_flags[lane] = 0u;
        workspace->candidate_indices[lane] = 0;
        workspace->candidate_values[lane] = 0.0f;
        workspace->candidate_flags[lane] = 0u;
    }

    const float frequency_scale = bin_width * 60.0f;
    float selected_amplitude = 0.0f;
    float selected_score = 0.0f;
    bool selected = false;
    size_t base_limit = peak_count < 2u ? peak_count : 2u;
    for (size_t base = 0u; base < base_limit; ++base) {
        const float base_index = (float)peak_indices[base];
        for (size_t divisor = 1u; divisor <= candidate_capacity; ++divisor) {
            const float fundamental = base_index / (float)divisor;
            for (size_t harmonic = 1u; harmonic <= candidate_capacity;
                    ++harmonic) {
                const float predicted = (float)harmonic * fundamental;
                float closest_error = 10000.0f;
                int32_t closest_index = 0;
                float closest_value = 0.0f;
                for (size_t peak = 0u; peak < peak_count; ++peak) {
                    float error = predicted - (float)peak_indices[peak];
                    if (error < 0.0f) {
                        error = -error;
                    }
                    error *= frequency_scale;
                    if (error < closest_error ||
                            (error == closest_error &&
                             peak_values[peak] > closest_value)) {
                        closest_error = error;
                        closest_index = peak_indices[peak];
                        closest_value = peak_values[peak];
                    }
                }
                float threshold = 10.0f;
                if (harmonic != divisor) {
                    const float ratio =
                        (float)harmonic / (float)divisor;
                    const float scaled = selector->square_root(
                        ratio * ratio + 1.0f) * 5.0f;
                    threshold = scaled < 15.0f ? scaled : 15.0f;
                }
                workspace->candidate_indices[harmonic - 1u] =
                    closest_index;
                workspace->candidate_values[harmonic - 1u] = closest_value;
                workspace->candidate_flags[harmonic - 1u] =
                    closest_error <= threshold ? 1u : 0u;
            }

            uint32_t harmonic_sum = 0u;
            float index_sum = 0.0f;
            size_t selected_count = 0u;
            for (size_t harmonic = 1u; harmonic <= candidate_capacity;
                    ++harmonic) {
                if (workspace->candidate_flags[harmonic - 1u] != 0u) {
                    harmonic_sum += (uint32_t)harmonic;
                    index_sum += (float)workspace->candidate_indices[
                        harmonic - 1u];
                    ++selected_count;
                }
            }
            if (harmonic_sum == 0u || selected_count == 0u) {
                continue;
            }
            const float mean_index = index_sum / (float)harmonic_sum;
            float fit_error = 0.0f;
            float normalization = 0.0f;
            float amplitude_sum = 0.0f;
            for (size_t harmonic = 1u; harmonic <= candidate_capacity;
                    ++harmonic) {
                if (workspace->candidate_flags[harmonic - 1u] == 0u) {
                    continue;
                }
                float difference =
                    (float)workspace->candidate_indices[harmonic - 1u] -
                    (float)harmonic * mean_index;
                if (difference < 0.0f) {
                    difference = -difference;
                }
                fit_error += frequency_scale * difference;
                const uint32_t other_count =
                    (uint32_t)(selected_count - 1u);
                const uint32_t remaining =
                    harmonic_sum - (uint32_t)harmonic;
                const float numerator = (float)(
                    other_count * (uint32_t)harmonic * (uint32_t)harmonic +
                    remaining * remaining);
                const float denominator =
                    (float)harmonic_sum * (float)harmonic_sum;
                normalization += selector->square_root(
                    numerator / denominator);
                amplitude_sum +=
                    workspace->candidate_values[harmonic - 1u];
            }
            if (normalization <= 0.000001f) {
                normalization = 0.000001f;
            }
            const float score = fit_error / normalization;
            if (score >= 5.0f || workspace->candidate_flags[0] == 0u) {
                continue;
            }
            bool distinct_harmonics = true;
            for (size_t right = 1u; right < candidate_capacity; ++right) {
                if (workspace->candidate_flags[right] == 0u) {
                    continue;
                }
                for (size_t left = 0u; left < right; ++left) {
                    if (workspace->candidate_flags[left] != 0u &&
                            workspace->candidate_indices[left] ==
                                workspace->candidate_indices[right]) {
                        distinct_harmonics = false;
                    }
                }
            }
            if (!distinct_harmonics) {
                continue;
            }
            const bool stronger = !selected ||
                amplitude_sum > selected_amplitude * 0.9f;
            const bool comparable_and_cleaner = selected &&
                amplitude_sum >= selected_amplitude * 0.5f &&
                score < selected_score;
            if (stronger || comparable_and_cleaner) {
                for (size_t lane = 0u; lane < candidate_capacity; ++lane) {
                    workspace->selected_indices[lane] =
                        workspace->candidate_indices[lane];
                    workspace->selected_flags[lane] =
                        workspace->candidate_flags[lane];
                }
                selected_amplitude = amplitude_sum;
                selected_score = score;
                selected = true;
            }
        }
        if (workspace->selected_flags[0] != 0u &&
                workspace->selected_flags[1] != 0u &&
                workspace->selected_flags[2] != 0u) {
            base_limit = base + 1u;
        }
    }
    for (size_t lane = 0u; lane < candidate_capacity; ++lane) {
        candidate_indices[lane] = workspace->selected_indices[lane];
        candidate_flags[lane] = workspace->selected_flags[lane];
    }
    return true;
}

bool goodix_primitives_float_quantile_interpolated(
    const float *values, size_t count, float fraction,
    float *scratch, size_t scratch_capacity, float *result) {
    if (values == NULL || count == 0u || scratch == NULL ||
            scratch_capacity < count || result == NULL ||
            fraction != fraction) {
        return false;
    }
    for (size_t index = 0u; index < count; ++index) {
        scratch[index] = values[index];
    }
    if (!goodix_primitives_sort_floats(scratch, count)) {
        return false;
    }
    const float first_position =
        (float)(0.5 / (double)count);
    if (!(fraction > first_position)) {
        *result = scratch[0];
        return true;
    }
    const float last_position =
        (float)(((double)count - 0.5) / (double)count);
    if (fraction > last_position) {
        *result = scratch[count - 1u];
        return true;
    }
    float interpolated = 0.0f;
    for (size_t index = 0u; index + 1u < count; ++index) {
        const float left_position =
            (float)(((double)index + 0.5) / (double)count);
        const float right_position =
            (float)(((double)index + 1.5) / (double)count);
        if (left_position < fraction && fraction <= right_position) {
            const float ratio =
                (fraction - left_position) /
                (right_position - left_position);
            interpolated = scratch[index] +
                ratio * (scratch[index + 1u] - scratch[index]);
        }
    }
    *result = interpolated;
    return true;
}

bool goodix_primitives_nadt_quartile_mask(
    const float *values, size_t count, float multiplier,
    float *sort_scratch, size_t sort_capacity,
    int8_t *mask, size_t mask_capacity) {
    if (values == NULL || mask == NULL || mask_capacity < count) {
        return false;
    }
    float upper_quartile = 0.0f;
    float lower_quartile = 0.0f;
    if (!goodix_primitives_float_quantile_interpolated(
            values, count, 0.75f, sort_scratch, sort_capacity,
            &upper_quartile) ||
            !goodix_primitives_float_quantile_interpolated(
                values, count, 0.25f, sort_scratch, sort_capacity,
                &lower_quartile)) {
        return false;
    }
    const float spread = upper_quartile - lower_quartile;
    const float upper = upper_quartile + spread * multiplier;
    const float lower = lower_quartile - spread * multiplier;
    for (size_t index = 0u; index < count; ++index) {
        int8_t classification = 0;
        if (values[index] > upper || values[index] < lower) {
            classification = 1;
        }
        if (values[index] < lower) {
            classification = -1;
        }
        mask[index] = classification;
    }
    return true;
}

bool goodix_primitives_nadt_nonuniform_mask_count(
    const float *values, size_t count, uint8_t multiplier_tenths,
    float *sort_scratch, size_t sort_capacity,
    int8_t *mask_scratch, size_t mask_capacity, int32_t *result) {
    if (result == NULL || count > (size_t)INT32_MAX ||
            !goodix_primitives_nadt_quartile_mask(
                values, count, (float)multiplier_tenths / 10.0f,
                sort_scratch, sort_capacity, mask_scratch, mask_capacity)) {
        return false;
    }
    int32_t nonzero_count = 0;
    int32_t signed_sum = 0;
    for (size_t index = 0u; index < count; ++index) {
        if (mask_scratch[index] != 0) {
            ++nonzero_count;
        }
        signed_sum += mask_scratch[index];
    }
    if (signed_sum != 0) {
        const int32_t magnitude = signed_sum < 0 ? -signed_sum : signed_sum;
        if (magnitude == nonzero_count) {
            nonzero_count = 0;
        }
    }
    *result = nonzero_count;
    return true;
}

bool goodix_primitives_nadt_positive_difference_statistics(
    const float *values, size_t value_count,
    const int32_t *first_indices, const int32_t *second_indices,
    size_t pair_count, goodix_primitives_nadt_difference_summary *summary) {
    if (values == NULL || first_indices == NULL || second_indices == NULL ||
            summary == NULL || value_count > (size_t)INT32_MAX ||
            pair_count > (size_t)INT32_MAX / 5u) {
        return false;
    }
    for (size_t index = 0u; index < pair_count; ++index) {
        if (first_indices[index] < 0 || second_indices[index] < 0 ||
                (size_t)first_indices[index] >= value_count ||
                (size_t)second_indices[index] >= value_count) {
            return false;
        }
    }
    float sum = 0.0f;
    float squared_sum = 0.0f;
    float previous = 0.0f;
    int32_t accepted = 0;
    for (size_t index = 0u; index < pair_count; ++index) {
        const size_t first = (size_t)first_indices[index];
        const size_t second = (size_t)second_indices[index];
        float difference = values[first] - values[second];
        if (difference == 0.0f && index + 1u == pair_count && accepted > 0) {
            const size_t span = value_count - first;
            float minimum = 0.0f;
            size_t minimum_index = 0u;
            if (span != 0u && goodix_primitives_float_min_index(
                    values + first, span, &minimum, &minimum_index) &&
                    minimum_index < span - 1u) {
                const float candidate = values[first] - minimum;
                if ((double)candidate >= (double)previous * 0.85 &&
                        (double)candidate <= (double)previous * 1.15) {
                    difference = candidate;
                } else {
                    difference = 0.0f;
                }
            }
        }
        if (difference > 0.0f) {
            squared_sum += difference * difference;
            sum += difference;
            previous = difference;
            ++accepted;
        }
    }
    float mean = sum;
    float mean_square = squared_sum;
    if (accepted > 0) {
        mean /= (float)accepted;
        mean_square /= (float)accepted;
    }
    float relative_variance = -1.0f;
    if (accepted > 1 && mean != 0.0f) {
        relative_variance = mean_square - mean * mean;
        relative_variance /= mean * mean;
    }
    summary->mean_difference = mean;
    summary->relative_variance = relative_variance;
    summary->accepted_count = (uint8_t)(uint32_t)accepted;
    summary->sufficient_coverage =
        pair_count != 0u && accepted >= (int32_t)((pair_count * 5u) / 6u)
            ? UINT8_C(1) : UINT8_C(0);
    return true;
}

bool goodix_primitives_nadt_difference_summary_execute(
    const float *values, size_t value_count,
    const int32_t *first_indices, const int32_t *second_indices,
    size_t pair_count, uint8_t multiplier_tenths,
    float *sort_scratch, size_t sort_capacity,
    int8_t *mask_scratch, size_t mask_capacity,
    goodix_primitives_nadt_difference_summary *summary, int32_t *result) {
    if (summary == NULL || result == NULL ||
            !goodix_primitives_nadt_nonuniform_mask_count(
                values, value_count, multiplier_tenths,
                sort_scratch, sort_capacity, mask_scratch, mask_capacity,
                &summary->nonuniform_mask_count) ||
            !goodix_primitives_nadt_positive_difference_statistics(
                values, value_count, first_indices, second_indices,
                pair_count, summary)) {
        return false;
    }
    *result = 0;
    return true;
}

/* The two tables formerly reached through the absolute pointer stored at
 * 0x00036EAC.  Hex-float notation keeps every recovered IEEE-754 bit visible
 * and makes the reconstructed bundle independent of the stock image. */
static const float goodix_primitives_nadt_smoothing_kernel[25] = {
    0x1.dc727cp-6f, 0x1.025772p-5f, 0x1.15a448p-5f,
    0x1.27e5e0p-5f, 0x1.38e498p-5f, 0x1.486bf0p-5f,
    0x1.564b5ep-5f, 0x1.625716p-5f, 0x1.6c68c0p-5f,
    0x1.74601cp-5f, 0x1.7a237cp-5f, 0x1.7da042p-5f,
    0x1.7ecb1cp-5f, 0x1.7da042p-5f, 0x1.7a237cp-5f,
    0x1.74601cp-5f, 0x1.6c68c0p-5f, 0x1.625716p-5f,
    0x1.564b5ep-5f, 0x1.486bf0p-5f, 0x1.38e498p-5f,
    0x1.27e5e0p-5f, 0x1.15a448p-5f, 0x1.025772p-5f,
    0x1.dc727cp-6f,
};

static const float goodix_primitives_nadt_residual_kernel[25] = {
    -0x1.c91882p-9f, -0x1.0e4ce4p-7f, -0x1.a3657cp-9f,
    -0x1.c84004p-10f, -0x1.8144a2p-6f, -0x1.4b53e2p-5f,
    -0x1.cba8a2p-7f, 0x1.2eb9aep-7f, -0x1.9a8060p-5f,
    -0x1.01e27ep-3f, -0x1.ca4706p-6f, 0x1.0ae292p-2f,
    0x1.d15cacp-2f, 0x1.0ae292p-2f, -0x1.ca4706p-6f,
    -0x1.01e27ep-3f, -0x1.9a8060p-5f, 0x1.2eb9aep-7f,
    -0x1.cba8a2p-7f, -0x1.4b53e2p-5f, -0x1.8144a2p-6f,
    -0x1.c84004p-10f, -0x1.a3657cp-9f, -0x1.0e4ce4p-7f,
    -0x1.c91882p-9f,
};

static bool goodix_primitives_nadt_float_window_valid(
    const goodix_primitives_decimated_float_window *window) {
    return window != NULL && window->values != NULL &&
           window->capacity != 0u && window->count <= window->capacity &&
           window->cursor < window->capacity && window->period != 0u &&
           window->phase < window->period;
}

static bool goodix_primitives_nadt_i16_window_valid(
    const goodix_primitives_i16_window *window) {
    return window != NULL && window->values != NULL &&
           window->capacity != 0u && window->count <= window->capacity;
}

static uint32_t goodix_primitives_float_bits(float value) {
    const union {
        float value;
        uint32_t bits;
    } conversion = {.value = value};
    return conversion.bits;
}

static float goodix_primitives_float_from_bits(uint32_t bits) {
    const union {
        uint32_t bits;
        float value;
    } conversion = {.bits = bits};
    return conversion.value;
}

static int32_t goodix_primitives_wrapped_square(int32_t value) {
    const uint32_t product = (uint32_t)value * (uint32_t)value;
    const union {
        uint32_t unsigned_value;
        int32_t signed_value;
    } conversion = {.unsigned_value = product};
    return conversion.signed_value;
}

static int32_t goodix_primitives_wrapped_add_i32(
    int32_t first, int32_t second) {
    const uint32_t sum = (uint32_t)first + (uint32_t)second;
    const union {
        uint32_t unsigned_value;
        int32_t signed_value;
    } conversion = {.unsigned_value = sum};
    return conversion.signed_value;
}

static bool goodix_primitives_float_to_i32(float value, int32_t *result) {
    if (result == NULL || value != value || value < -2147483648.0f ||
            value >= 2147483648.0f) {
        return false;
    }
    *result = (int32_t)value;
    return true;
}

static bool goodix_primitives_nadt_scaled_round_u32(
    float value, float scale, uint32_t *result) {
    if (result == NULL) {
        return false;
    }
    const double rounded = (double)(value * scale) + 0.5;
    if (!(rounded >= 0.0 && rounded < 4294967296.0)) {
        return false;
    }
    *result = (uint32_t)rounded;
    return true;
}

bool goodix_primitives_nadt_rolling_feature_update(
    float value, uint32_t sample_index, uint32_t average_period,
    goodix_primitives_nadt_rolling_feature_state *state) {
    if (average_period == 0u || state == NULL ||
            !goodix_primitives_nadt_float_window_valid(&state->input) ||
            !goodix_primitives_nadt_float_window_valid(&state->smoothed) ||
            !goodix_primitives_nadt_float_window_valid(&state->residual) ||
            !goodix_primitives_nadt_float_window_valid(
                &state->residual_smoothed) ||
            !goodix_primitives_nadt_float_window_valid(
                &state->feature_average) ||
            !goodix_primitives_decimated_float_window_push(
                &state->input, value) || state->input.count == 0u) {
        return false;
    }

    float smoothed = 0.0f;
    if (!goodix_primitives_reverse_clamped_weighted_sum(
            goodix_primitives_nadt_smoothing_kernel, 25u,
            state->input.values, state->input.count, state->input.count,
            &smoothed) ||
            !goodix_primitives_decimated_float_window_push(
                &state->smoothed, smoothed)) {
        return false;
    }
    const size_t delayed_index = state->input.count > 13u
        ? (size_t)state->input.count - 13u : 0u;
    const float residual = state->input.values[delayed_index] - smoothed;
    if (!goodix_primitives_decimated_float_window_push(
            &state->residual, residual)) {
        return false;
    }
    float residual_smoothed = 0.0f;
    if (!goodix_primitives_reverse_clamped_weighted_sum(
            goodix_primitives_nadt_residual_kernel, 25u,
            state->residual.values, state->residual.count,
            state->residual.count, &residual_smoothed) ||
            !goodix_primitives_decimated_float_window_push(
                &state->residual_smoothed, residual_smoothed)) {
        return false;
    }

    if (sample_index % average_period == average_period - 1u) {
        if (state->smoothed.count == 0u) {
            return false;
        }
        float sum = 0.0f;
        for (size_t offset = 0u; offset < average_period; ++offset) {
            const size_t index = state->smoothed.count > 13u + offset
                ? (size_t)state->smoothed.count - 13u - offset : 0u;
            sum += state->smoothed.values[index];
        }
        if (!goodix_primitives_decimated_float_window_push(
                &state->feature_average, sum / (float)average_period)) {
            return false;
        }
    }
    return true;
}

bool goodix_primitives_nadt_feature_pair_update(
    const goodix_primitives_nadt_feature_pair *input,
    uint32_t sample_index,
    const goodix_primitives_nadt_cadence_configuration *configuration,
    goodix_primitives_nadt_feature_pair_state *state) {
    if (input == NULL || configuration == NULL || state == NULL ||
            configuration->feature_average_period == 0u ||
            configuration->pair_average_period == 0u ||
            !goodix_primitives_nadt_float_window_valid(
                &state->pair_average) ||
            !goodix_primitives_nadt_rolling_feature_update(
                input->feature_value, sample_index,
                configuration->feature_average_period, &state->feature)) {
        return false;
    }
    const uint32_t period = configuration->pair_average_period;
    const uint32_t remainder = sample_index % period;
    float accumulator = remainder == 0u ? 0.0f : state->average_accumulator;
    accumulator += input->average_value;
    state->average_accumulator = accumulator;
    if (remainder == period - 1u &&
            !goodix_primitives_decimated_float_window_push(
                &state->pair_average, accumulator / (float)period)) {
        return false;
    }
    return true;
}

bool goodix_primitives_nadt_channel_ratio_update(
    const goodix_primitives_nadt_channel_input *input,
    uint32_t sample_index,
    const goodix_primitives_nadt_cadence_configuration *configuration,
    goodix_primitives_nadt_channel_state *state) {
    if (input == NULL || configuration == NULL || state == NULL ||
            configuration->ratio_period == 0u ||
            !goodix_primitives_nadt_float_window_valid(
                &state->combined_ratio) ||
            !goodix_primitives_nadt_float_window_valid(
                &state->primary_ratio) ||
            !goodix_primitives_nadt_float_window_valid(
                &state->secondary_ratio) ||
            state->half_primary_input.values == NULL ||
            state->half_primary_input.capacity == 0u ||
            state->half_primary_input.count >
                state->half_primary_input.capacity ||
            state->half_primary_input.cursor >=
                state->half_primary_input.capacity ||
            state->half_primary_input.period == 0u ||
            state->half_primary_input.phase >=
                state->half_primary_input.period ||
            !goodix_primitives_nadt_feature_pair_update(
                &input->primary, sample_index, configuration,
                &state->primary) ||
            !goodix_primitives_nadt_feature_pair_update(
                &input->secondary, sample_index, configuration,
                &state->secondary)) {
        return false;
    }

    const uint32_t ratio_period = configuration->ratio_period;
    if (sample_index % ratio_period == ratio_period - 1u) {
        const goodix_primitives_nadt_rolling_feature_state *const primary =
            &state->primary.feature;
        const goodix_primitives_nadt_rolling_feature_state *const secondary =
            &state->secondary.feature;
        if (primary->smoothed.count == 0u ||
                primary->residual_smoothed.count == 0u ||
                secondary->smoothed.count == 0u ||
                secondary->residual_smoothed.count == 0u) {
            return false;
        }
        const size_t primary_index = primary->smoothed.count > 13u
            ? (size_t)primary->smoothed.count - 13u : 0u;
        float primary_denominator = primary->smoothed.values[primary_index];
        if ((int32_t)goodix_primitives_float_bits(primary_denominator) <=
                (int32_t)UINT32_C(0x358637BD)) {
            primary_denominator = 0x1.0c6f7ap-20f;
        }
        const float primary_ratio =
            primary->residual_smoothed.values[
                primary->residual_smoothed.count - 1u] /
            primary_denominator;
        if (!goodix_primitives_decimated_float_window_push(
                &state->primary_ratio, primary_ratio)) {
            return false;
        }

        const size_t secondary_index = secondary->smoothed.count > 13u
            ? (size_t)secondary->smoothed.count - 13u : 0u;
        float secondary_denominator =
            secondary->smoothed.values[secondary_index];
        if ((int32_t)goodix_primitives_float_bits(secondary_denominator) <=
                (int32_t)UINT32_C(0x358637BD)) {
            secondary_denominator = 0x1.0c6f7ap-20f;
        }
        const float secondary_ratio =
            secondary->residual_smoothed.values[
                secondary->residual_smoothed.count - 1u] /
            secondary_denominator;
        if (!goodix_primitives_decimated_float_window_push(
                &state->secondary_ratio, secondary_ratio)) {
            return false;
        }

        float absolute_primary = primary_ratio;
        if (absolute_primary < 0.0f) {
            absolute_primary = -absolute_primary;
        }
        float combined = 0.0f;
        if ((int32_t)goodix_primitives_float_bits(absolute_primary) >=
                (int32_t)UINT32_C(0x33D6BF95)) {
            combined = secondary_ratio / primary_ratio;
        }
        const uint32_t adjusted = goodix_primitives_float_bits(combined) +
            UINT32_C(0xC1B33333);
        if (adjusted >= UINT32_C(0x01B33334)) {
            combined = 0.0f;
        }
        if (!goodix_primitives_decimated_float_window_push(
                &state->combined_ratio, combined)) {
            return false;
        }
    }

    const float half_input = input->primary.feature_value * 0.5f;
    if (half_input != half_input || half_input < 0.0f ||
            half_input >= 4294967296.0f) {
        return false;
    }
    return goodix_primitives_decimated_i16_window_push(
        &state->half_primary_input,
        (int16_t)(uint16_t)(uint32_t)half_input);
}

bool goodix_primitives_nadt_vector_geometry_update(
    const int32_t vector[3], uint32_t sample_index,
    const goodix_primitives_nadt_cadence_configuration *configuration,
    goodix_primitives_nadt_geometry_state *state,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_double_unary_fn arc_tangent) {
    if (vector == NULL || configuration == NULL || state == NULL ||
            square_root == NULL || arc_tangent == NULL ||
            configuration->geometry_period == 0u ||
            !goodix_primitives_nadt_i16_window_valid(
                &state->magnitude_delta) ||
            !goodix_primitives_nadt_i16_window_valid(
                &state->angle_average)) {
        return false;
    }
    const float x = (float)vector[0];
    const float y_square =
        (float)goodix_primitives_wrapped_square(vector[1]);
    const float z_square =
        (float)goodix_primitives_wrapped_square(vector[2]);
    const float magnitude = square_root(y_square + x * x + z_square);
    const float horizontal = square_root(y_square + x * x);
    float angle = 90.0f;
    if (vector[2] != 0) {
        const float ratio = horizontal / (float)vector[2];
        angle = (float)(arc_tangent((double)ratio) * 180.0 /
                        0x1.921ff2e48e8a7p+1);
        if (vector[2] < 0) {
            angle += 180.0f;
        }
    }
    if (sample_index == 0u) {
        state->magnitude = magnitude;
    }
    int32_t converted = 0;
    if (!goodix_primitives_float_to_i32(
            magnitude - state->magnitude, &converted) ||
            !goodix_primitives_i16_window_push(
                &state->magnitude_delta, (int16_t)converted)) {
        return false;
    }
    state->magnitude = magnitude;

    const uint32_t period = configuration->geometry_period;
    const uint32_t remainder = sample_index % period;
    if (remainder == 0u) {
        state->angle_accumulator = 0.0f;
    }
    const float accumulated = state->angle_accumulator + angle;
    state->angle_accumulator = accumulated;
    if (remainder == period - 1u) {
        if (!goodix_primitives_float_to_i32(
                accumulated / (float)period, &converted) ||
                !goodix_primitives_i16_window_push(
                    &state->angle_average, (int16_t)converted)) {
            return false;
        }
    }
    return true;
}

bool goodix_primitives_nadt_accumulation_execute(
    const goodix_primitives_nadt_channel_input *channel,
    const int32_t vector[3], uint32_t sample_index,
    const goodix_primitives_nadt_cadence_configuration *configuration,
    goodix_primitives_nadt_channel_state *channel_state,
    goodix_primitives_nadt_geometry_state *geometry_state,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_double_unary_fn arc_tangent, int32_t *result) {
    if (result == NULL ||
            !goodix_primitives_nadt_channel_ratio_update(
                channel, sample_index, configuration, channel_state) ||
            !goodix_primitives_nadt_vector_geometry_update(
                vector, sample_index, configuration, geometry_state,
                square_root, arc_tangent)) {
        return false;
    }
    *result = sample_index % 25u == 24u && sample_index + 1u >= 125u
        ? 0 : 4;
    return true;
}

bool goodix_primitives_nadt_batch_accumulate(
    const goodix_primitives_nadt_batch_input *input,
    const goodix_primitives_nadt_batch_configuration *configuration,
    goodix_primitives_nadt_batch_state *state, int32_t *result) {
    if (input == NULL || configuration == NULL || state == NULL ||
            result == NULL || input->channels == NULL ||
            state->channels == NULL || configuration->channel_count == 0u ||
            configuration->channel_count > state->channel_capacity ||
            configuration->channel_count > (size_t)UINT32_MAX ||
            configuration->period == 0u ||
            configuration->period > (uint32_t)INT32_MAX) {
        return false;
    }
    const uint32_t period = configuration->period;
    if (input->sample_index % period == 0u) {
        for (size_t channel = 0u;
                channel < configuration->channel_count; ++channel) {
            state->channels[channel] =
                (goodix_primitives_nadt_channel_accumulator) {{0u, 0u},
                                                               {0.0f, 0.0f},
                                                               {0.0f, 0.0f}};
        }
        state->aggregate =
            (goodix_primitives_nadt_channel_accumulator) {{0u, 0u},
                                                           {0.0f, 0.0f},
                                                           {0.0f, 0.0f}};
        state->vector[0] = 0;
        state->vector[1] = 0;
        state->vector[2] = 0;
    }
    for (size_t channel = 0u;
            channel < configuration->channel_count; ++channel) {
        state->channels[channel].primary[0] +=
            input->channels[channel].primary[0];
        state->channels[channel].primary[1] +=
            input->channels[channel].primary[1];
        state->channels[channel].secondary[0] +=
            input->channels[channel].secondary[0];
        state->channels[channel].secondary[1] +=
            input->channels[channel].secondary[1];
    }
    for (size_t axis = 0u; axis < 3u; ++axis) {
        state->vector[axis] = goodix_primitives_wrapped_add_i32(
            state->vector[axis], input->vector[axis]);
    }

    if (input->sample_index % period != period - 1u) {
        *result = 3;
        return true;
    }
    state->selector = (uint8_t)input->selector;
    state->batch_index = input->sample_index / period;
    const float period_float = (float)(int32_t)period;
    for (size_t channel = 0u;
            channel < configuration->channel_count; ++channel) {
        state->channels[channel].primary[0] /= period_float;
        state->channels[channel].primary[1] /= period_float;
        state->channels[channel].secondary[0] /= period_float;
        state->channels[channel].secondary[1] /= period_float;
        state->aggregate.primary[0] +=
            state->channels[channel].primary[0];
        state->aggregate.secondary[0] +=
            state->channels[channel].secondary[0];
    }
    const float channel_count_float =
        (float)(uint32_t)configuration->channel_count;
    state->aggregate.primary[0] /= channel_count_float;
    state->aggregate.secondary[0] /= channel_count_float;
    for (size_t axis = 0u; axis < 3u; ++axis) {
        state->vector[axis] /= (int32_t)period;
    }
    *result = 0;
    return true;
}

bool goodix_primitives_nadt_record_encode(
    const goodix_primitives_nadt_output_record *record,
    uint32_t output[16]) {
    if (record == NULL || output == NULL ||
            !goodix_primitives_nadt_scaled_round_u32(
                record->metric, 10000.0f, &output[0]) ||
            !goodix_primitives_nadt_scaled_round_u32(
                record->reference, 1.0f, &output[4]) ||
            !goodix_primitives_nadt_scaled_round_u32(
                record->scaled_reference, 100.0f, &output[5]) ||
            !goodix_primitives_nadt_scaled_round_u32(
                record->first_score, 100000.0f, &output[7]) ||
            !goodix_primitives_nadt_scaled_round_u32(
                record->second_score, 100000.0f, &output[8]) ||
            !goodix_primitives_nadt_scaled_round_u32(
                record->output_metric, 10000.0f, &output[11])) {
        return false;
    }
    output[1] = (uint32_t)(int32_t)record->direction;
    output[2] = record->category;
    output[3] = 0u;
    output[6] = record->source_flags;
    output[9] = 0u;
    output[10] = 0u;
    output[12] = 0u;
    output[13] = 0u;
    output[14] = 0u;
    output[15] = 0u;
    return true;
}

bool goodix_primitives_nadt_output_record_build(
    bool reference_enabled, float metric, int8_t direction,
    const goodix_primitives_nadt_source_metrics *source,
    const goodix_primitives_nadt_reference_metrics *reference,
    float output_metric, goodix_primitives_nadt_output_record *record,
    uint32_t output[16]) {
    if (source == NULL || record == NULL || output == NULL ||
            (reference_enabled && reference == NULL)) {
        return false;
    }
    record->metric = metric;
    record->direction = direction;
    record->category = source->category;
    record->baseline = 0.0f;
    record->reference = reference_enabled ? reference->reference : 0.0f;
    record->scaled_reference = reference_enabled
        ? reference->scaled_reference : 0.0f;
    record->source_flags = source->source_flags;
    record->first_score = source->first_score;
    record->second_score = source->second_score;
    record->third_score = source->third_score;
    record->fourth_score = source->fourth_score;
    record->output_metric = output_metric;
    if (!goodix_primitives_nadt_record_encode(record, output)) {
        return false;
    }
    output[12] = 1u;
    return true;
}

bool goodix_primitives_nadt_output_record_quality_update(
    const goodix_primitives_nadt_quality_configuration *configuration,
    uint8_t source_flags, float sample,
    goodix_primitives_nadt_output_record *record) {
    if (configuration == NULL || record == NULL ||
            !goodix_primitives_nadt_float_window_valid(&record->history)) {
        return false;
    }
    if (source_flags != 0u) {
        record->primary_count = 0u;
    } else if (record->primary_count != UINT8_MAX) {
        ++record->primary_count;
    }
    if (!goodix_primitives_decimated_float_window_push(
            &record->history, sample) || record->history.count == 0u) {
        return false;
    }
    uint32_t rounded_last = 0u;
    if (!goodix_primitives_nadt_scaled_round_u32(
            record->history.values[record->history.count - 1u],
            1.0f, &rounded_last)) {
        return false;
    }
    int32_t history_length = configuration->default_history_length;
    float tolerance = (float)configuration->default_tolerance;
    if ((uint32_t)configuration->rounded_value_threshold <= rounded_last) {
        history_length = configuration->alternate_history_length;
        tolerance = (float)configuration->alternate_tolerance;
    }
    if (history_length <= 0) {
        return false;
    }

    float maximum = tolerance + 1.0f;
    float minimum = 0x1.156526p+13f;
    if ((uint32_t)record->history.count >= (uint32_t)history_length) {
        const size_t first = (size_t)record->history.count -
            (size_t)history_length;
        maximum = record->history.values[first];
        minimum = maximum;
        for (size_t index = first + 1u;
                index < record->history.count; ++index) {
            if (maximum < record->history.values[index]) {
                maximum = record->history.values[index];
            }
            if (record->history.values[index] < minimum) {
                minimum = record->history.values[index];
            }
        }
    }
    float spread = maximum - minimum;
    if (spread < 0.0f) {
        spread = -spread;
    }
    record->quality_flags =
        (uint8_t)(record->primary_count < (uint32_t)history_length
            ? UINT8_C(0x04) : UINT8_C(0x00));
    if (spread > tolerance) {
        record->quality_flags |= UINT8_C(0x80);
    }

    if ((source_flags & UINT8_C(0x07)) != 0u) {
        record->secondary_count = 0u;
    } else if (record->secondary_count != UINT8_MAX) {
        ++record->secondary_count;
    }
    return true;
}

bool goodix_primitives_nadt_channel_analysis_execute(
    const goodix_primitives_nadt_channel_state *state,
    const goodix_primitives_event_pair_source *events, int32_t mode,
    uint8_t multiplier_tenths,
    int32_t *primary_index_scratch, int32_t *secondary_index_scratch,
    size_t index_scratch_capacity,
    float *sort_scratch, size_t sort_capacity,
    int8_t *mask_scratch, size_t mask_capacity,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_nadt_channel_analysis *analysis) {
    const size_t sample_count = 125u;
    if (state == NULL || events == NULL || square_root == NULL ||
            analysis == NULL || state->primary_ratio.values == NULL ||
            state->secondary_ratio.values == NULL ||
            state->primary_ratio.count < sample_count ||
            state->secondary_ratio.count < sample_count ||
            sort_capacity < sample_count || mask_capacity < sample_count ||
            sort_scratch == NULL || mask_scratch == NULL) {
        return false;
    }
    size_t pair_count = 0u;
    if (!goodix_primitives_align_event_pairs(
            mode, events, primary_index_scratch, secondary_index_scratch,
            index_scratch_capacity, &pair_count)) {
        return false;
    }
    const float *const primary_values = state->primary_ratio.values +
        state->primary_ratio.count - sample_count;
    const float *const secondary_values = state->secondary_ratio.values +
        state->secondary_ratio.count - sample_count;
    int32_t summary_result = 0;
    if (!goodix_primitives_nadt_difference_summary_execute(
            primary_values, sample_count,
            primary_index_scratch, secondary_index_scratch, pair_count,
            multiplier_tenths, sort_scratch, sort_capacity,
            mask_scratch, mask_capacity,
            &analysis->primary_difference, &summary_result) ||
            !goodix_primitives_float_window_mean(
                &state->primary.pair_average,
                &analysis->primary_average) ||
            !goodix_primitives_nadt_difference_summary_execute(
                secondary_values, sample_count,
                primary_index_scratch, secondary_index_scratch, pair_count,
                multiplier_tenths, sort_scratch, sort_capacity,
                mask_scratch, mask_capacity,
                &analysis->secondary_difference, &summary_result) ||
            !goodix_primitives_float_window_mean(
                &state->secondary.pair_average,
                &analysis->secondary_average)) {
        return false;
    }
    float similarity = 0.0f;
    int32_t converted = 0;
    if (!goodix_primitives_positive_cosine_similarity(
            secondary_values, primary_values, sample_count,
            square_root, &similarity) ||
            !goodix_primitives_float_to_i32(
                similarity * 100.0f, &converted)) {
        return false;
    }
    analysis->cosine_percent = (uint8_t)(uint32_t)converted;
    return true;
}

bool goodix_primitives_i16_descriptor_mean(
    const goodix_primitives_buffer_descriptor *descriptor, int16_t *result) {
    if (descriptor == NULL || descriptor->data == NULL || result == NULL ||
            descriptor->count == 0u ||
            descriptor->count > descriptor->capacity) {
        return false;
    }
    return goodix_primitives_i16_mean(
        (const int16_t *)descriptor->data, descriptor->count, result);
}

bool goodix_primitives_nadt_sample_statistics(
    const goodix_primitives_nadt_threshold_configuration *configuration,
    const goodix_primitives_buffer_descriptor *descriptor,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_nadt_primary_summary *summary) {
    if (configuration == NULL || descriptor == NULL ||
            descriptor->data == NULL || descriptor->count == 0u ||
            descriptor->count > descriptor->capacity ||
            square_root == NULL || summary == NULL) {
        return false;
    }
    const uint16_t count = descriptor->count < UINT16_C(125)
        ? descriptor->count : UINT16_C(125);
    const int16_t *const values = (const int16_t *)descriptor->data;
    float sum = 0.0f;
    float squared_sum = 0.0f;
    for (uint16_t index = 0u; index < count; ++index) {
        const float value = (float)values[index];
        squared_sum += value * value;
        sum += value;
    }
    const float count_float = (float)count;
    const float mean_float = sum / count_float;
    float variance = squared_sum / count_float;
    variance -= mean_float * mean_float;
    if (variance < 0.0f) {
        variance = 0.0f;
    }
    const float deviation = square_root(variance);
    const float scaled_threshold =
        (float)configuration->deviation_factor * deviation;
    float threshold_float =
        scaled_threshold < (float)configuration->minimum_threshold
            ? (float)configuration->minimum_threshold
            : scaled_threshold;
    threshold_float = threshold_float <
            (float)configuration->maximum_threshold
        ? threshold_float
        : (float)configuration->maximum_threshold;
    if (!(threshold_float >= 0.0f && threshold_float < 2147483648.0f)) {
        return false;
    }
    const int16_t mean = (int16_t)(int32_t)mean_float;
    const int32_t threshold = (int32_t)threshold_float;
    uint16_t outlier_count = 0u;
    for (uint16_t index = 0u; index < count; ++index) {
        int32_t difference = (int32_t)values[index] - (int32_t)mean;
        if (difference < 0) {
            difference = -difference;
        }
        if (difference > threshold) {
            ++outlier_count;
        }
    }
    summary->mean = mean;
    summary->threshold = (uint8_t)(uint32_t)threshold;
    summary->outlier_count = (uint8_t)outlier_count;
    return true;
}

bool goodix_primitives_nadt_sample_summary_build(
    const goodix_primitives_nadt_summary_context *context,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_nadt_sample_summary *summary, int32_t *result) {
    if (context == NULL || summary == NULL || result == NULL) {
        return false;
    }
    goodix_primitives_nadt_primary_summary primary = {0};
    int16_t secondary_mean = 0;
    if (!goodix_primitives_nadt_sample_statistics(
            context->configuration, context->primary, square_root,
            &primary) ||
            !goodix_primitives_i16_descriptor_mean(
                context->secondary, &secondary_mean)) {
        return false;
    }
    summary->mean = primary.mean;
    summary->threshold = primary.threshold;
    summary->outlier_count = primary.outlier_count;
    summary->secondary_mean = secondary_mean;
    *result = 0;
    return true;
}

bool goodix_primitives_nadt_summary_dispatch(
    uintptr_t source, uintptr_t auxiliary,
    goodix_primitives_nadt_sample_summary *summary,
    const goodix_primitives_nadt_summary_context *context,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_five_word_operation_fn downstream, int32_t *result) {
    int32_t summary_result = 0;
    if (context == NULL || downstream == NULL || result == NULL ||
            !goodix_primitives_nadt_sample_summary_build(
                context, square_root, summary, &summary_result)) {
        return false;
    }
    *result = downstream(
        context->downstream_first, context->downstream_second,
        source, auxiliary, (uintptr_t)summary);
    return true;
}

bool goodix_primitives_reverse_clamped_weighted_sum(
    const float *coefficients, size_t coefficient_count,
    const float *history, size_t history_count, size_t active_count,
    float *result) {
    if (result == NULL || coefficient_count > (size_t)UINT16_MAX ||
            active_count > history_count ||
            (coefficient_count != 0u && coefficients == NULL) ||
            (active_count != 0u && history == NULL)) {
        return false;
    }
    float sum = 0.0f;
    if (active_count != 0u) {
        for (size_t index = 0u; index < coefficient_count; ++index) {
            const size_t reverse_index = index + 1u < active_count
                ? active_count - index - 1u
                : 0u;
            sum += coefficients[index] * history[reverse_index];
        }
    }
    *result = sum;
    return true;
}

bool goodix_primitives_extrema_history_update(
    goodix_primitives_extrema_history *state, int32_t sample,
    int32_t threshold, int32_t *transition) {
    if (state == NULL || transition == NULL) {
        return false;
    }
    int32_t result = 0;
    if (state->descending == 0u) {
        if (state->extremum < sample) {
            state->extremum_count = state->sample_count;
            state->extremum = sample;
        }
        if ((int64_t)sample <
                (int64_t)state->extremum - (int64_t)threshold) {
            if (state->extremum_count > 0) {
                state->emitted_count = state->extremum_count;
                result = 1;
            }
            state->extremum_count = state->sample_count;
            state->extremum = sample;
            state->descending = 1u;
        }
    } else {
        if (sample < state->extremum) {
            state->extremum_count = state->sample_count;
            state->extremum = sample;
        }
        if ((int64_t)sample >
                (int64_t)state->extremum + (int64_t)threshold) {
            state->extremum = sample;
            state->emitted_count = state->extremum_count;
            state->extremum_count = state->sample_count;
            result = -1;
            state->descending = 0u;
        }
    }
    state->sample_count = goodix_primitives_u32_as_i32(
        (uint32_t)state->sample_count + 1u);
    *transition = result;
    return true;
}

bool goodix_primitives_normalize_rows_by_range(
    float *values, size_t row_count, size_t column_count) {
    if (values == NULL || row_count > (size_t)UINT8_MAX ||
            column_count == 0u || column_count > (size_t)UINT16_MAX ||
            row_count > SIZE_MAX / column_count) {
        return false;
    }
    const float threshold = 0x1.0c6f7ap-20f;
    for (size_t row = 0u; row < row_count; ++row) {
        float *const current = &values[row * column_count];
        float maximum = current[0];
        float minimum = current[0];
        for (size_t column = 1u; column < column_count; ++column) {
            if (maximum < current[column]) {
                maximum = current[column];
            }
            if (current[column] < minimum) {
                minimum = current[column];
            }
        }
        const float range = maximum - minimum;
        if (threshold < range) {
            for (size_t column = 0u; column < column_count; ++column) {
                current[column] /= range;
            }
        }
    }
    return true;
}

bool goodix_primitives_record32_history_push(
    goodix_primitives_record32_history *history,
    const uint8_t record[32]) {
    if (history == NULL || history->records == NULL || record == NULL ||
            history->capacity == 0u || history->count > history->capacity ||
        history->capacity > UINT32_MAX / 32u) {
        return false;
    }
    if (history->count == history->capacity) {
        for (size_t index = 1u; index < history->capacity; ++index) {
            for (size_t byte = 0u; byte < 32u; ++byte) {
                history->records[(index - 1u) * 32u + byte] =
                    history->records[index * 32u + byte];
            }
        }
        --history->count;
    }
    for (size_t byte = 0u; byte < 32u; ++byte) {
        history->records[history->count * 32u + byte] = record[byte];
    }
    ++history->count;
    return true;
}

bool goodix_primitives_hr_rebalance_record_pair(
    float tolerance_scale, float baseline, int32_t gate_left,
    int32_t gate_right, goodix_primitives_record32_history *history,
    goodix_primitives_hr_event_record *first,
    goodix_primitives_hr_event_record *second) {
    if (history == NULL || history->records == NULL ||
            history->capacity == 0u || history->count > history->capacity ||
            history->capacity > UINT32_MAX / 32u || first == NULL ||
            second == NULL) {
        return false;
    }

    const float combined = first->center + second->center;
    const float tolerance = tolerance_scale * baseline;
    float midpoint_delta = combined * 0.5f - baseline;
    float first_delta = first->center - baseline;
    float second_delta = second->center - baseline;
    if (midpoint_delta < 0.0f) {
        midpoint_delta = -midpoint_delta;
    }
    if (first_delta < 0.0f) {
        first_delta = -first_delta;
    }
    if (second_delta < 0.0f) {
        second_delta = -second_delta;
    }

    /* The VCMPE/BCS and VCMPE/BLT branches all reject unordered inputs.
     * Expressing the complete acceptance predicate with positive ordered
     * comparisons retains that NaN behavior without a math-library binding. */
    const bool split = midpoint_delta < tolerance &&
        first_delta >= tolerance && second_delta >= tolerance &&
        gate_left >= gate_right && first->eligible == 1;
    if (!split) {
        if (history->count > 0u) {
            --history->count;
        }
    } else {
        first->center = baseline;
        second->center = combined - baseline;
        if (history->count > 0u) {
            --history->count;
        }
        if (history->count > 0u) {
            --history->count;
        }
        if (!goodix_primitives_record32_history_push(
                history, (const uint8_t *)(const void *)first)) {
            return false;
        }
    }
    return goodix_primitives_record32_history_push(
        history, (const uint8_t *)(const void *)second);
}

bool goodix_primitives_select_mask_row(
    const uint8_t *packed_bits, size_t packed_bytes, size_t columns,
    uint16_t first_label, uint16_t last_label, uint16_t *selected_label) {
    if (packed_bits == NULL || selected_label == NULL || columns == 0u ||
            first_label == 0u || last_label < first_label ||
            last_label > (uint16_t)INT16_MAX ||
            columns > SIZE_MAX / last_label) {
        return false;
    }
    const size_t bit_count = columns * last_label;
    if (bit_count > SIZE_MAX - 7u || packed_bytes < (bit_count + 7u) / 8u) {
        return false;
    }
    size_t best_score = 0u;
    uint16_t best_label = first_label;
    for (uint32_t label = first_label; label <= last_label; ++label) {
        const size_t row = (size_t)label - 1u;
        size_t score = 0u;
        for (size_t column = 0u; column < columns; ++column) {
            const size_t bit = row * columns + column;
            score += (packed_bits[bit / 8u] >> (bit & 7u)) & 1u;
        }
        if (best_score < score) {
            best_score = score;
            best_label = (uint16_t)label;
        }
    }
    *selected_label = best_label;
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

bool goodix_primitives_nadt_channel_quality_update(
    const goodix_primitives_nadt_channel_quality_configuration *configuration,
    const goodix_primitives_nadt_channel_quality_summary *summary,
    goodix_primitives_nadt_channel_quality_record *record,
    goodix_primitives_float_unary_fn exp_provider) {
    if (configuration == NULL || summary == NULL || record == NULL ||
            exp_provider == NULL) {
        return false;
    }

    uint8_t flags = 0u;
    if (configuration->primary_level_threshold < summary->primary_level) {
        flags |= UINT8_C(0x01);
    }
    if (configuration->secondary_level_threshold <
            (uint32_t)(int32_t)summary->secondary_level) {
        flags |= UINT8_C(0x02);
    }
    if (record->primary_activity > 0 || record->secondary_activity > 0) {
        flags |= UINT8_C(0x04);
    }
    if (!record->primary_valid || !record->secondary_valid) {
        flags |= UINT8_C(0x08);
    }
    const float metric_limit =
        (float)configuration->metric_limit_percent / 100.0f;
    if (record->secondary_metric > metric_limit ||
            record->secondary_metric == -1.0f ||
            record->primary_metric > metric_limit ||
            record->primary_metric == -1.0f) {
        flags |= UINT8_C(0x10);
    }
    if ((int32_t)record->quality <
            (int32_t)configuration->quality_threshold) {
        flags |= UINT8_C(0x20);
    }
    record->flags = flags & configuration->flag_mask;

    static const float fallback = 0x1.0c6f7ap-20f;
    static const float reciprocal_threshold = 0x1.0aaaacp+4f;
    static const float reciprocal_lower_scale = 0x1.1eb84ep-1f;
    static const float reciprocal_upper_scale = 0x1.7538d2p-8f;
    static const float quality_lower_scale = 0x1.31d5acp-4f;
    static const float quality_upper_scale = 0x1.cac082p-3f;

    const float secondary_metric =
        goodix_primitives_u32_as_i32(
            goodix_primitives_float_bits(record->secondary_metric)) > 0
            ? record->secondary_metric
            : fallback;
    float component = 0.0f;
    if (!goodix_primitives_logistic_score(
            1.0f / secondary_metric, reciprocal_threshold,
            reciprocal_lower_scale, reciprocal_upper_scale,
            exp_provider, &component)) {
        return false;
    }
    float score = (float)((double)component * 0.4);

    const float primary_metric =
        goodix_primitives_u32_as_i32(
            goodix_primitives_float_bits(record->primary_metric)) > 0
            ? record->primary_metric
            : fallback;
    if (!goodix_primitives_logistic_score(
            1.0f / primary_metric, reciprocal_threshold,
            reciprocal_lower_scale, reciprocal_upper_scale,
            exp_provider, &component)) {
        return false;
    }
    score = (float)((double)score + (double)component * 0.4);

    if (!goodix_primitives_logistic_score(
            (float)record->quality, 75.0f,
            quality_lower_scale, quality_upper_scale,
            exp_provider, &component)) {
        return false;
    }
    score = (float)((double)score + (double)component * 0.2);
    if (score > 100.0f) {
        score = 100.0f;
    }
    if (score != score || score < 0.0f) {
        return false;
    }
    record->score = (uint8_t)(uint32_t)score;
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

bool goodix_primitives_spo2_expand_packed_banks(
    const uint16_t *const
        banks[GOODIX_PRIMITIVES_SPO2_PACKED_TOTAL_BANK_COUNT],
    float *workspace, size_t workspace_count) {
    if (banks == NULL || workspace == NULL ||
            workspace_count < GOODIX_PRIMITIVES_SPO2_PACKED_WORKSPACE_VALUES) {
        return false;
    }
    for (size_t bank = 0u;
            bank < GOODIX_PRIMITIVES_SPO2_PACKED_TOTAL_BANK_COUNT; ++bank) {
        if (banks[bank] == NULL) {
            return false;
        }
    }
    for (size_t bank = 0u;
            bank < GOODIX_PRIMITIVES_SPO2_PACKED_TOTAL_BANK_COUNT; ++bank) {
        float *const output =
            workspace + bank * GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES;
        for (size_t index = 0u;
                index < GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES; ++index) {
            const union {
                uint32_t bits;
                float value;
            } converted = {
                .bits = goodix_primitives_packed_6_9_to_f32_bits(
                    banks[bank][index]),
            };
            output[index] = converted.value;
        }
    }
    return true;
}

bool goodix_primitives_spo2_expand_packed_triplicate(
    uint8_t disabled_flag, uint8_t ready_flag,
    const uint16_t *packed_values, size_t packed_count,
    float *workspace, size_t workspace_count) {
    if (disabled_flag != 0u || ready_flag != 1u) {
        return true;
    }
    if (packed_values == NULL || workspace == NULL ||
            packed_count < GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES ||
            workspace_count <
                GOODIX_PRIMITIVES_SPO2_PACKED_WORKSPACE_VALUES) {
        return false;
    }
    for (size_t bank = 0u;
            bank < GOODIX_PRIMITIVES_SPO2_PACKED_BANK_COUNT; ++bank) {
        float *const output = workspace +
            GOODIX_PRIMITIVES_SPO2_PACKED_PREFIX_VALUES +
            bank * GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES;
        for (size_t index = 0u;
                index < GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES; ++index) {
            const union {
                uint32_t bits;
                float value;
            } converted = {
                .bits = goodix_primitives_packed_6_9_to_f32_bits(
                    packed_values[index]),
            };
            output[index] = converted.value;
        }
    }
    return true;
}

static uint16_t goodix_primitives_f32_bits_to_packed(
    uint32_t value, uint32_t exponent_bits) {
    const uint32_t fraction_bits = UINT32_C(15) - exponent_bits;
    const uint32_t fraction_shift = UINT32_C(23) - fraction_bits;
    const uint32_t rounding = UINT32_C(1) << (fraction_shift - 1u);
    const int32_t maximum_unbiased =
        (int32_t)(UINT32_C(1) << (exponent_bits - 1u)) - 1;
    const uint16_t packed_infinity = (uint16_t)(
        ((UINT32_C(1) << exponent_bits) - 1u) << fraction_bits);
    const uint32_t exponent =
        (value & UINT32_C(0x7FFFFFFF)) >> 23u;
    const uint16_t sign = (uint16_t)((value >> 16u) & UINT32_C(0x8000));
    const int32_t unbiased = (int32_t)exponent - 127;
    const uint32_t fraction = value & UINT32_C(0x007FFFFF);
    if (unbiased == 128) {
        return (uint16_t)(sign | packed_infinity |
                          (uint16_t)(fraction >> fraction_shift));
    }
    if (unbiased > maximum_unbiased) {
        return (uint16_t)(sign | packed_infinity);
    }
    if (unbiased > -maximum_unbiased) {
        const uint32_t rounded =
            ((uint32_t)(unbiased + maximum_unbiased) << fraction_bits) +
            ((fraction + rounding) >> fraction_shift);
        return (uint16_t)(sign | (uint16_t)rounded);
    }
    if (unbiased > -(maximum_unbiased + (int32_t)fraction_bits)) {
        const uint32_t shift =
            (uint32_t)(-(unbiased + maximum_unbiased - 1));
        const uint32_t rounded =
            (((fraction | UINT32_C(0x00800000)) >> shift) +
             rounding) >> fraction_shift;
        return (uint16_t)(sign | (uint16_t)rounded);
    }
    return sign;
}

uint16_t goodix_primitives_f32_bits_to_packed_5_10(uint32_t value) {
    return goodix_primitives_f32_bits_to_packed(value, 5u);
}

uint16_t goodix_primitives_f32_bits_to_packed_6_9(uint32_t value) {
    return goodix_primitives_f32_bits_to_packed(value, 6u);
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

bool goodix_primitives_float_buffer_mean(
    const goodix_primitives_float_buffer *buffer, float *result) {
    if (buffer == NULL || result == NULL || buffer->count == 0u) {
        return false;
    }
    return goodix_primitives_float_mean(
        buffer->values, (size_t)buffer->count, result);
}

const uint16_t *goodix_primitives_nadt_result_binding(
    const uint16_t *result_words) {
    return result_words;
}

const void *goodix_primitives_hrv_configuration_binding(
    const void *configuration) {
    return configuration;
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

bool goodix_primitives_three_stage_u8_pipeline(
    const goodix_primitives_tensor_stage_fn stages[3],
    void *const stage_contexts[3],
    const goodix_primitives_tensor_binding *input,
    goodix_primitives_tensor_binding *state,
    const uint8_t dimensions[6], size_t workspace_bytes) {
    if (stages == NULL || stage_contexts == NULL || input == NULL ||
            input->descriptor == NULL || state == NULL ||
            state->descriptor == NULL || state->descriptor->data == NULL ||
            dimensions == NULL || stages[0] == NULL || stages[1] == NULL ||
            stages[2] == NULL) {
        return false;
    }
    const size_t first_bytes =
        (size_t)dimensions[0] * (size_t)dimensions[1];
    const size_t middle_bytes =
        (size_t)dimensions[2] * (size_t)dimensions[3];
    const size_t final_bytes =
        (size_t)dimensions[4] * (size_t)dimensions[5];
    if (first_bytes > workspace_bytes || final_bytes > workspace_bytes ||
            middle_bytes > workspace_bytes ||
            workspace_bytes - middle_bytes < (size_t)0x3E0u) {
        return false;
    }

    uint8_t *const workspace = (uint8_t *)state->descriptor->data;
    goodix_primitives_tensor_descriptor descriptors[3];
    (void)goodix_primitives_tensor_descriptor_initialize(
        &descriptors[0], 1u, (uint32_t)dimensions[0],
        (uint32_t)dimensions[1], 1u, workspace);
    (void)goodix_primitives_tensor_descriptor_initialize(
        &descriptors[1], 1u, (uint32_t)dimensions[2],
        (uint32_t)dimensions[3], 1u, workspace + 0x3E0u);
    (void)goodix_primitives_tensor_descriptor_initialize(
        &descriptors[2], 1u, (uint32_t)dimensions[4],
        (uint32_t)dimensions[5], 1u, workspace);

    goodix_primitives_tensor_binding stage_input = *input;
    goodix_primitives_tensor_binding stage_output = {
        &descriptors[0], state->auxiliary,
    };
    stages[0](stage_contexts[0], &stage_input, &stage_output);
    for (size_t stage = 1u; stage < 3u; ++stage) {
        stage_input.descriptor = &descriptors[stage - 1u];
        stage_input.auxiliary = state->auxiliary;
        stage_output.descriptor = &descriptors[stage];
        stage_output.auxiliary = state->auxiliary;
        stages[stage](stage_contexts[stage], &stage_input, &stage_output);
    }
    *state->descriptor = descriptors[2];
    return true;
}

static bool goodix_primitives_nadt_graph_workspace_span(
    size_t workspace_count, size_t offset, size_t value_count) {
    return offset <= workspace_count &&
           value_count <= workspace_count - offset;
}

static void goodix_primitives_nadt_graph_descriptor(
    goodix_primitives_tensor_descriptor *descriptor, uint32_t values,
    float *data) {
    (void)goodix_primitives_tensor_descriptor_initialize(
        descriptor, 1u, values, 1u, 4u, data);
}

static bool goodix_primitives_nadt_graph_stage(
    const goodix_primitives_nadt_generated_graph *graph, size_t stage,
    const goodix_primitives_tensor_descriptor *const *inputs,
    size_t input_count, goodix_primitives_tensor_descriptor *output) {
    goodix_primitives_tensor_descriptor *outputs[1] = {output};
    return graph->stages[stage](
        graph->stage_contexts[stage], inputs, input_count, outputs, 1u);
}

bool goodix_primitives_nadt_generated_graph_execute(
    const goodix_primitives_nadt_generated_graph *graph,
    const float *input, size_t input_count,
    float *workspace, size_t workspace_count, bool reset_recurrent_state,
    float *output, size_t output_capacity) {
    if (graph == NULL || input == NULL ||
            input_count < GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES ||
            workspace == NULL || output == NULL ||
            graph->first_stage_values == 0u ||
            graph->shared_stage_values <
                GOODIX_PRIMITIVES_NADT_GRAPH_AUXILIARY_VALUES ||
            graph->recurrent_values == 0u ||
            graph->recurrent_state == NULL ||
            graph->recurrent_state_capacity < graph->recurrent_values ||
            graph->penultimate_values == 0u || graph->output_values == 0u ||
            output_capacity < graph->output_values) {
        return false;
    }
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_GRAPH_SUBGRAPH_COUNT; ++index) {
        if (graph->subgraphs[index] == NULL) {
            return false;
        }
    }
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_GRAPH_STAGE_COUNT; ++index) {
        if (graph->stages[index] == NULL) {
            return false;
        }
    }

    const size_t first_values = graph->first_stage_values;
    const size_t shared_values = graph->shared_stage_values;
    const size_t recurrent_values = graph->recurrent_values;
    const size_t penultimate_values = graph->penultimate_values;
    const size_t output_values = graph->output_values;
    if (!goodix_primitives_nadt_graph_workspace_span(
            workspace_count, 0u,
            GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES) ||
            !goodix_primitives_nadt_graph_workspace_span(
                workspace_count, GOODIX_PRIMITIVES_NADT_GRAPH_WORKSPACE_BANK,
                first_values) ||
            !goodix_primitives_nadt_graph_workspace_span(
                workspace_count, GOODIX_PRIMITIVES_NADT_GRAPH_WORKSPACE_BANK,
                shared_values) ||
            !goodix_primitives_nadt_graph_workspace_span(
                workspace_count, GOODIX_PRIMITIVES_NADT_GRAPH_WORKSPACE_BANK,
                GOODIX_PRIMITIVES_NADT_GRAPH_MERGED_VALUES) ||
            !goodix_primitives_nadt_graph_workspace_span(
                workspace_count, GOODIX_PRIMITIVES_NADT_GRAPH_AUXILIARY_BANK,
                shared_values) ||
            !goodix_primitives_nadt_graph_workspace_span(
                workspace_count, GOODIX_PRIMITIVES_NADT_GRAPH_STATE_BANK,
                recurrent_values) ||
            !goodix_primitives_nadt_graph_workspace_span(
                workspace_count, 0u, penultimate_values) ||
            !goodix_primitives_nadt_graph_workspace_span(
                workspace_count, GOODIX_PRIMITIVES_NADT_GRAPH_WORKSPACE_BANK,
                output_values)) {
        return false;
    }

    goodix_primitives_tensor_descriptor primary;
    goodix_primitives_tensor_descriptor secondary;
    goodix_primitives_tensor_descriptor merged;
    const goodix_primitives_tensor_descriptor *stage_inputs[2];

    if (!graph->subgraphs[0](
            graph->subgraph_contexts[0], workspace, workspace_count)) {
        return false;
    }
    goodix_primitives_nadt_graph_descriptor(
        &primary, GOODIX_PRIMITIVES_NADT_GRAPH_PRIMARY_VALUES, workspace);
    goodix_primitives_nadt_graph_descriptor(
        &secondary, graph->first_stage_values,
        workspace + GOODIX_PRIMITIVES_NADT_GRAPH_WORKSPACE_BANK);
    stage_inputs[0] = &primary;
    if (!goodix_primitives_nadt_graph_stage(
            graph, 0u, stage_inputs, 1u, &secondary)) {
        return false;
    }

    primary.rows = graph->shared_stage_values;
    primary.data = workspace;
    stage_inputs[0] = &secondary;
    if (!goodix_primitives_nadt_graph_stage(
            graph, 1u, stage_inputs, 1u, &primary)) {
        return false;
    }
    secondary.rows = graph->shared_stage_values;
    secondary.data = workspace + GOODIX_PRIMITIVES_NADT_GRAPH_WORKSPACE_BANK;
    stage_inputs[0] = &primary;
    if (!goodix_primitives_nadt_graph_stage(
            graph, 2u, stage_inputs, 1u, &secondary)) {
        return false;
    }
    for (size_t index = 0u; index < shared_values; ++index) {
        workspace[GOODIX_PRIMITIVES_NADT_GRAPH_AUXILIARY_BANK + index] =
            workspace[GOODIX_PRIMITIVES_NADT_GRAPH_WORKSPACE_BANK + index];
    }

    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES; ++index) {
        workspace[index] = input[index];
    }
    if (!graph->subgraphs[1](
            graph->subgraph_contexts[1], workspace, workspace_count)) {
        return false;
    }
    goodix_primitives_nadt_graph_descriptor(
        &primary, GOODIX_PRIMITIVES_NADT_GRAPH_PRIMARY_VALUES, workspace);
    goodix_primitives_nadt_graph_descriptor(
        &secondary, GOODIX_PRIMITIVES_NADT_GRAPH_AUXILIARY_VALUES,
        workspace + GOODIX_PRIMITIVES_NADT_GRAPH_AUXILIARY_BANK);
    goodix_primitives_nadt_graph_descriptor(
        &merged, GOODIX_PRIMITIVES_NADT_GRAPH_MERGED_VALUES,
        workspace + GOODIX_PRIMITIVES_NADT_GRAPH_WORKSPACE_BANK);
    stage_inputs[0] = &primary;
    stage_inputs[1] = &secondary;
    if (!goodix_primitives_nadt_graph_stage(
            graph, 3u, stage_inputs, 2u, &merged)) {
        return false;
    }

    if (reset_recurrent_state) {
        for (size_t index = 0u; index < recurrent_values; ++index) {
            graph->recurrent_state[index] = 0.0f;
        }
    }
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_GRAPH_MERGED_VALUES; ++index) {
        workspace[index] =
            workspace[GOODIX_PRIMITIVES_NADT_GRAPH_WORKSPACE_BANK + index];
    }
    goodix_primitives_nadt_graph_descriptor(
        &primary, GOODIX_PRIMITIVES_NADT_GRAPH_MERGED_VALUES, workspace);
    goodix_primitives_nadt_graph_descriptor(
        &secondary, graph->recurrent_values,
        workspace + GOODIX_PRIMITIVES_NADT_GRAPH_STATE_BANK);
    stage_inputs[0] = &primary;
    if (!goodix_primitives_nadt_graph_stage(
            graph, 4u, stage_inputs, 1u, &secondary)) {
        return false;
    }

    goodix_primitives_nadt_graph_descriptor(
        &primary, graph->penultimate_values, workspace);
    stage_inputs[0] = &secondary;
    if (!goodix_primitives_nadt_graph_stage(
            graph, 5u, stage_inputs, 1u, &primary)) {
        return false;
    }
    goodix_primitives_nadt_graph_descriptor(
        &secondary, graph->output_values,
        workspace + GOODIX_PRIMITIVES_NADT_GRAPH_WORKSPACE_BANK);
    stage_inputs[0] = &primary;
    if (!goodix_primitives_nadt_graph_stage(
            graph, 6u, stage_inputs, 1u, &secondary)) {
        return false;
    }
    for (size_t index = 0u; index < output_values; ++index) {
        output[index] =
            workspace[GOODIX_PRIMITIVES_NADT_GRAPH_WORKSPACE_BANK + index];
    }
    return true;
}

enum {
    GOODIX_NADT_SUBGRAPH_QUANTIZE = 0,
    GOODIX_NADT_SUBGRAPH_EXPAND_125,
    GOODIX_NADT_SUBGRAPH_REDUCE_62,
    GOODIX_NADT_SUBGRAPH_PIPE_62_0,
    GOODIX_NADT_SUBGRAPH_PIPE_62_1,
    GOODIX_NADT_SUBGRAPH_PIPE_62_2,
    GOODIX_NADT_SUBGRAPH_MERGE_62,
    GOODIX_NADT_SUBGRAPH_REDUCE_31,
    GOODIX_NADT_SUBGRAPH_PIPE_31_0,
    GOODIX_NADT_SUBGRAPH_PIPE_31_1,
    GOODIX_NADT_SUBGRAPH_PIPE_31_2,
    GOODIX_NADT_SUBGRAPH_MERGE_31,
    GOODIX_NADT_SUBGRAPH_REDUCE_15,
    GOODIX_NADT_SUBGRAPH_FLOAT_CONVERT,
    GOODIX_NADT_SUBGRAPH_PROJECT_0,
    GOODIX_NADT_SUBGRAPH_PROJECT_1,
    GOODIX_NADT_SUBGRAPH_PROJECT_2,
    GOODIX_NADT_SUBGRAPH_BRANCH,
    GOODIX_NADT_SUBGRAPH_FINAL_MERGE
};

static void goodix_primitives_nadt_subgraph_descriptor(
    goodix_primitives_tensor_descriptor *descriptor, uint32_t rows,
    uint32_t columns, uint32_t element_bytes, void *data) {
    (void)goodix_primitives_tensor_descriptor_initialize(
        descriptor, 1u, rows, columns, element_bytes, data);
}

static void goodix_primitives_nadt_subgraph_operator(
    const goodix_primitives_nadt_generated_subgraph *subgraph, size_t stage,
    goodix_primitives_tensor_binding inputs[2],
    goodix_primitives_tensor_binding *output) {
    subgraph->operators[stage](
        subgraph->operator_contexts[stage], inputs, output);
}

static void goodix_primitives_nadt_subgraph_u8_pipeline(
    const goodix_primitives_nadt_generated_subgraph *subgraph,
    size_t first_stage, const uint8_t dimensions[6],
    uint8_t *workspace, goodix_primitives_tensor_descriptor *input,
    goodix_primitives_tensor_descriptor *output,
    goodix_primitives_tensor_descriptor *auxiliary) {
    goodix_primitives_tensor_descriptor stages[2];
    goodix_primitives_tensor_binding inputs[2] = {
        {input, (uintptr_t)auxiliary}, {NULL, 0u},
    };
    goodix_primitives_tensor_binding stage_output = {
        &stages[0], (uintptr_t)auxiliary,
    };
    goodix_primitives_nadt_subgraph_descriptor(
        &stages[0], dimensions[0], dimensions[1], 1u, workspace);
    goodix_primitives_nadt_subgraph_operator(
        subgraph, first_stage, inputs, &stage_output);
    inputs[0].descriptor = &stages[0];
    goodix_primitives_nadt_subgraph_descriptor(
        &stages[1], dimensions[2], dimensions[3], 1u,
        workspace + 0x3E0u);
    stage_output.descriptor = &stages[1];
    goodix_primitives_nadt_subgraph_operator(
        subgraph, first_stage + 1u, inputs, &stage_output);
    inputs[0].descriptor = &stages[1];
    goodix_primitives_nadt_subgraph_descriptor(
        output, dimensions[4], dimensions[5], 1u, workspace);
    stage_output.descriptor = output;
    goodix_primitives_nadt_subgraph_operator(
        subgraph, first_stage + 2u, inputs, &stage_output);
}

static void goodix_primitives_nadt_subgraph_f32_pipeline(
    const goodix_primitives_nadt_generated_subgraph *subgraph,
    uint8_t *workspace, goodix_primitives_tensor_descriptor *input,
    goodix_primitives_tensor_descriptor *output) {
    goodix_primitives_tensor_descriptor stages[2];
    goodix_primitives_tensor_binding inputs[2] = {
        {input, 0u}, {NULL, 0u},
    };
    goodix_primitives_tensor_binding stage_output = {&stages[0], 0u};
    goodix_primitives_nadt_subgraph_descriptor(
        &stages[0], 1u, 15u, 4u, workspace);
    goodix_primitives_nadt_subgraph_operator(
        subgraph, GOODIX_NADT_SUBGRAPH_PROJECT_0, inputs, &stage_output);
    inputs[0].descriptor = &stages[0];
    goodix_primitives_nadt_subgraph_descriptor(
        &stages[1], 1u, 15u, 4u, workspace + 0x1F0u);
    stage_output.descriptor = &stages[1];
    goodix_primitives_nadt_subgraph_operator(
        subgraph, GOODIX_NADT_SUBGRAPH_PROJECT_1, inputs, &stage_output);
    inputs[0].descriptor = &stages[1];
    goodix_primitives_nadt_subgraph_descriptor(
        output, 8u, 15u, 4u, workspace);
    stage_output.descriptor = output;
    goodix_primitives_nadt_subgraph_operator(
        subgraph, GOODIX_NADT_SUBGRAPH_PROJECT_2, inputs, &stage_output);
}

bool goodix_primitives_nadt_generated_subgraph_execute(
    const goodix_primitives_nadt_generated_subgraph *subgraph,
    float *workspace, size_t workspace_count) {
    if (subgraph == NULL || workspace == NULL ||
            workspace_count < GOODIX_PRIMITIVES_NADT_SUBGRAPH_WORKSPACE_FLOATS) {
        return false;
    }
    for (size_t stage = 0u;
            stage < GOODIX_PRIMITIVES_NADT_SUBGRAPH_OPERATOR_COUNT; ++stage) {
        if (subgraph->operators[stage] == NULL) {
            return false;
        }
    }
    uint8_t *const bytes = (uint8_t *)workspace;
    float quantization_range[2] = {0.0f, 0.0f};
    uint32_t scalar = UINT32_C(2000);
    goodix_primitives_tensor_descriptor primary;
    goodix_primitives_tensor_descriptor secondary;
    goodix_primitives_tensor_descriptor auxiliary;
    goodix_primitives_tensor_descriptor branch;
    goodix_primitives_tensor_descriptor scalar_descriptor;
    goodix_primitives_tensor_binding inputs[2] = {
        {&primary, 0u}, {NULL, 0u},
    };
    goodix_primitives_tensor_binding output = {
        &primary, (uintptr_t)&auxiliary,
    };
    goodix_primitives_nadt_subgraph_descriptor(
        &primary, 1u, 125u, 4u, bytes);
    goodix_primitives_nadt_subgraph_descriptor(
        &auxiliary, 0u, 0u, 0u, quantization_range);
    goodix_primitives_nadt_subgraph_operator(
        subgraph, GOODIX_NADT_SUBGRAPH_QUANTIZE, inputs, &output);
    goodix_primitives_nadt_subgraph_descriptor(
        &primary, 1u, 125u, 1u, bytes);
    quantization_range[0] = subgraph->quantization_minimum;
    quantization_range[1] = subgraph->quantization_maximum;

    goodix_primitives_nadt_subgraph_descriptor(
        &secondary, 16u, 125u, 1u, bytes);
    goodix_primitives_nadt_subgraph_descriptor(
        &scalar_descriptor, 1u, 1u, 4u, &scalar);
    inputs[0] = (goodix_primitives_tensor_binding) {
        &primary, (uintptr_t)&auxiliary,
    };
    inputs[1] = (goodix_primitives_tensor_binding) {
        &scalar_descriptor, 0u,
    };
    output = (goodix_primitives_tensor_binding) {
        &secondary, (uintptr_t)&auxiliary,
    };
    goodix_primitives_nadt_subgraph_operator(
        subgraph, GOODIX_NADT_SUBGRAPH_EXPAND_125, inputs, &output);

    goodix_primitives_nadt_subgraph_descriptor(
        &primary, 16u, 62u, 1u, bytes);
    inputs[0].descriptor = &secondary;
    inputs[1].descriptor = NULL;
    output.descriptor = &primary;
    goodix_primitives_nadt_subgraph_operator(
        subgraph, GOODIX_NADT_SUBGRAPH_REDUCE_62, inputs, &output);
    static const uint8_t dimensions_62[6] = {4u, 62u, 4u, 62u, 16u, 62u};
    goodix_primitives_nadt_subgraph_u8_pipeline(
        subgraph, GOODIX_NADT_SUBGRAPH_PIPE_62_0, dimensions_62, bytes,
        &primary, &secondary, &auxiliary);
    inputs[0] = (goodix_primitives_tensor_binding) {
        &secondary, (uintptr_t)&auxiliary,
    };
    inputs[1] = (goodix_primitives_tensor_binding) {
        &primary, (uintptr_t)&auxiliary,
    };
    output = inputs[0];
    goodix_primitives_nadt_subgraph_operator(
        subgraph, GOODIX_NADT_SUBGRAPH_MERGE_62, inputs, &output);

    goodix_primitives_nadt_subgraph_descriptor(
        &primary, 16u, 31u, 1u, bytes);
    inputs[0] = output;
    inputs[1].descriptor = NULL;
    output = (goodix_primitives_tensor_binding) {
        &primary, (uintptr_t)&auxiliary,
    };
    goodix_primitives_nadt_subgraph_operator(
        subgraph, GOODIX_NADT_SUBGRAPH_REDUCE_31, inputs, &output);
    static const uint8_t dimensions_31[6] = {4u, 31u, 4u, 31u, 16u, 31u};
    goodix_primitives_nadt_subgraph_u8_pipeline(
        subgraph, GOODIX_NADT_SUBGRAPH_PIPE_31_0, dimensions_31, bytes,
        &primary, &secondary, &auxiliary);
    inputs[0] = (goodix_primitives_tensor_binding) {
        &secondary, (uintptr_t)&auxiliary,
    };
    inputs[1] = (goodix_primitives_tensor_binding) {
        &primary, (uintptr_t)&auxiliary,
    };
    output = inputs[0];
    goodix_primitives_nadt_subgraph_operator(
        subgraph, GOODIX_NADT_SUBGRAPH_MERGE_31, inputs, &output);

    goodix_primitives_nadt_subgraph_descriptor(
        &primary, 16u, 15u, 1u, bytes);
    inputs[0] = output;
    inputs[1].descriptor = NULL;
    output = (goodix_primitives_tensor_binding) {
        &primary, (uintptr_t)&auxiliary,
    };
    goodix_primitives_nadt_subgraph_operator(
        subgraph, GOODIX_NADT_SUBGRAPH_REDUCE_15, inputs, &output);
    goodix_primitives_nadt_subgraph_descriptor(
        &secondary, 16u, 15u, 4u, bytes + 0x3E0u);
    inputs[0] = output;
    output = (goodix_primitives_tensor_binding) {
        &secondary, (uintptr_t)&auxiliary,
    };
    goodix_primitives_nadt_subgraph_operator(
        subgraph, GOODIX_NADT_SUBGRAPH_FLOAT_CONVERT, inputs, &output);

    goodix_primitives_nadt_subgraph_f32_pipeline(
        subgraph, bytes, &secondary, &primary);
    goodix_primitives_nadt_subgraph_descriptor(
        &branch, 8u, 15u, 4u, bytes + 0x1E0u);
    inputs[0] = (goodix_primitives_tensor_binding) {&secondary, 0u};
    output = (goodix_primitives_tensor_binding) {&branch, 0u};
    goodix_primitives_nadt_subgraph_operator(
        subgraph, GOODIX_NADT_SUBGRAPH_BRANCH, inputs, &output);
    inputs[0] = (goodix_primitives_tensor_binding) {
        &primary, (uintptr_t)&branch,
    };
    output = (goodix_primitives_tensor_binding) {&primary, 0u};
    goodix_primitives_nadt_subgraph_operator(
        subgraph, GOODIX_NADT_SUBGRAPH_FINAL_MERGE, inputs, &output);
    return true;
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

bool goodix_primitives_sample_variance(const float *values, size_t count,
                                       float *result) {
    if (values == NULL || count < 2u || result == NULL) {
        return false;
    }
    float mean = 0.0f;
    if (!goodix_primitives_float_mean(values, count, &mean)) {
        return false;
    }
    float squared_difference_sum = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        const float difference = values[index] - mean;
        squared_difference_sum += difference * difference;
    }
    *result = squared_difference_sum / (float)(count - 1u);
    return true;
}

bool goodix_primitives_sample_standard_deviation(
    const float *values, size_t count,
    goodix_primitives_float_unary_fn square_root, float *result) {
    if (square_root == NULL || result == NULL) {
        return false;
    }
    float variance = 0.0f;
    if (!goodix_primitives_sample_variance(values, count, &variance)) {
        return false;
    }
    *result = square_root(variance);
    return true;
}

static int64_t goodix_primitives_u64_as_i64(uint64_t value) {
    if (value <= (uint64_t)INT64_MAX) {
        return (int64_t)value;
    }
    return INT64_MIN +
           (int64_t)(value - UINT64_C(0x8000000000000000));
}

bool goodix_primitives_i16_sample_standard_deviation(
    const int16_t *values, size_t count,
    goodix_primitives_float_unary_fn square_root, float *result) {
    if (result == NULL) {
        return false;
    }
    if (values == NULL || count <= 1u) {
        *result = 0.0f;
        return true;
    }
    if (square_root == NULL || count > (size_t)INT32_MAX) {
        return false;
    }
    uint32_t wrapped_sum = 0u;
    for (size_t index = 0u; index < count; ++index) {
        wrapped_sum += (uint32_t)(int32_t)values[index];
    }
    const int16_t low_count = (int16_t)(uint16_t)count;
    uint64_t squared_sum = 0u;
    for (size_t index = 0u; index < count; ++index) {
        const int32_t product = (int32_t)values[index] *
                                (int32_t)low_count;
        const uint32_t difference_bits =
            (uint32_t)product - wrapped_sum;
        const int32_t difference =
            goodix_primitives_u32_as_i32(difference_bits);
        const int64_t square = (int64_t)difference * (int64_t)difference;
        squared_sum += (uint64_t)square;
    }
    const float centered_sum =
        (float)goodix_primitives_u64_as_i64(squared_sum);
    const float rooted = square_root(centered_sum / (float)(count - 1u));
    *result = rooted / (float)count;
    return true;
}

bool goodix_primitives_u8_population_standard_deviation(
    const uint8_t *values, size_t count,
    goodix_primitives_float_unary_fn square_root, float *result) {
    if (values == NULL || count == 0u || count > (size_t)UINT16_MAX ||
            square_root == NULL || result == NULL) {
        return false;
    }
    float sum = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        sum += (float)values[index];
    }
    const float mean = sum / (float)count;
    float squared_sum = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        const float difference = (float)values[index] - mean;
        squared_sum += difference * difference;
    }
    *result = square_root(squared_sum / (float)count);
    return true;
}

bool goodix_primitives_positive_cosine_similarity(
    const float *left, const float *right, size_t count,
    goodix_primitives_float_unary_fn square_root, float *result) {
    if (result == NULL || square_root == NULL ||
            count > (size_t)INT32_MAX ||
            ((left == NULL || right == NULL) && count != 0u)) {
        return false;
    }
    const float dot = goodix_primitives_dot_product(left, right, count);
    const float left_squared = goodix_primitives_sum_squares(left, count);
    const float right_squared = goodix_primitives_sum_squares(right, count);
    const float left_norm =
        left_squared < 0.0f ? 0.0f : square_root(left_squared);
    const float right_norm =
        right_squared < 0.0f ? 0.0f : square_root(right_squared);
    float similarity = 0.0f;
    if (left_norm != 0.0f && right_norm != 0.0f) {
        const float candidate = dot / (left_norm * right_norm);
        if (candidate > 0.0f) {
            similarity = candidate;
        }
    }
    *result = similarity;
    return true;
}

bool goodix_primitives_collect_extrema_indices(
    const int32_t *samples, size_t count, int32_t threshold,
    int16_t *rising_indices, size_t rising_capacity,
    int16_t *falling_indices, size_t falling_capacity,
    int16_t *transition_indices, size_t transition_capacity,
    goodix_primitives_extrema_index_counts *counts) {
    if (samples == NULL || counts == NULL || count == 0u ||
            count > (size_t)INT32_MAX) {
        return false;
    }
    const size_t implicit_capacity = count / 2u;
    if ((rising_indices != NULL && rising_capacity < implicit_capacity) ||
            (falling_indices != NULL &&
             falling_capacity < implicit_capacity) ||
            (transition_indices != NULL &&
             transition_capacity < implicit_capacity)) {
        return false;
    }
    goodix_primitives_extrema_history state = {0};
    state.extremum = samples[0];
    size_t rising_count = 0u;
    size_t falling_count = 0u;
    size_t transition_count = 0u;
    for (size_t index = 0u; index < count; ++index) {
        int32_t transition = 0;
        if (!goodix_primitives_extrema_history_update(
                &state, samples[index], threshold, &transition)) {
            return false;
        }
        if (transition == 0) {
            continue;
        }
        const int16_t emitted = goodix_primitives_u16_as_i16(
            (uint16_t)(uint32_t)state.emitted_count);
        if (transition == 1) {
            if (rising_indices != NULL && rising_count < implicit_capacity) {
                rising_indices[rising_count] = emitted;
            }
            ++rising_count;
        } else if (transition == -1) {
            if (falling_indices != NULL &&
                    falling_count < implicit_capacity) {
                falling_indices[falling_count] = emitted;
            }
            ++falling_count;
        }
        if (transition_indices != NULL &&
                transition_count < implicit_capacity) {
            transition_indices[transition_count++] = emitted;
        }
    }
    counts->rising_count = rising_count;
    counts->falling_count = falling_count;
    counts->transition_count = transition_count;
    return true;
}

bool goodix_primitives_copy_fresh_gated_triplet(
    goodix_primitives_timed_triplet_destination *destination,
    const goodix_primitives_timed_triplet_source *source, bool *copied) {
    if (destination == NULL || source == NULL || copied == NULL) {
        return false;
    }
    *copied = false;
    if (source->timestamp - destination->last_timestamp > UINT32_C(20) &&
            source->gate > 0.0f && source->gate < 30.0f) {
        for (size_t index = 0u; index < 3u; ++index) {
            destination->values[index] = source->values[index];
        }
        *copied = true;
    }
    return true;
}

bool goodix_primitives_accumulate_threshold_crossings(
    const int32_t *samples, size_t count, int32_t mode,
    goodix_primitives_threshold_history *history) {
    if (history == NULL || history->window.values == NULL ||
            history->window.capacity == 0u ||
            history->window.count > history->window.capacity ||
            count > (size_t)INT32_MAX ||
            (samples == NULL && count != 0u)) {
        return false;
    }
    const uint32_t offset_bits =
        ((uint32_t)mode - UINT32_C(5)) * UINT32_C(25);
    const int32_t offset = goodix_primitives_u32_as_i32(offset_bits);
    int32_t last = 0;
    if (history->window.count != 0u) {
        last = goodix_primitives_u32_as_i32(
            history->window.values[history->window.count - 1u]);
    }
    uint16_t cursor = history->cursor;
    history->emitted_count = 0u;
    for (size_t index = 0u; index < count; ++index) {
        const uint32_t candidate_bits =
            (uint32_t)samples[index] + offset_bits;
        const int32_t candidate =
            goodix_primitives_u32_as_i32(candidate_bits);
        if (last < candidate) {
            if (cursor != 0u && goodix_primitives_word_window_full(
                    &history->window)) {
                --cursor;
            }
            if (!goodix_primitives_word_window_push(
                    &history->window, candidate_bits)) {
                return false;
            }
            history->emitted_count =
                (uint16_t)(history->emitted_count + UINT16_C(1));
        }
    }
    history->cursor = cursor;
    while (history->cursor < history->window.count &&
            goodix_primitives_u32_as_i32(
                history->window.values[history->cursor]) < offset) {
        ++history->cursor;
    }
    return true;
}

static bool goodix_primitives_nadt_peak_packed_bytes(
    size_t count, size_t row_count, size_t *packed_bytes) {
    if (packed_bytes == NULL || count == 0u || row_count == 0u ||
            count > (size_t)INT32_MAX || row_count > (size_t)INT16_MAX ||
            count > SIZE_MAX / row_count) {
        return false;
    }
    /* The stock allocator asks for floor(bits / 8) + 1 bytes, including
     * one deliberately unused byte when the matrix ends on a byte edge. */
    *packed_bytes = (count * row_count) / 8u + 1u;
    return true;
}

static void goodix_primitives_nadt_peak_bit_set(
    uint8_t *packed, size_t bit) {
    packed[bit / 8u] |= (uint8_t)(UINT8_C(1) << (bit & 7u));
}

static void goodix_primitives_nadt_peak_bit_clear(
    uint8_t *packed, size_t bit) {
    packed[bit / 8u] &= (uint8_t)~(UINT8_C(1) << (bit & 7u));
}

static bool goodix_primitives_nadt_peak_bit_test(
    const uint8_t *packed, size_t bit) {
    return ((packed[bit / 8u] >> (bit & 7u)) & UINT8_C(1)) != 0u;
}

static bool goodix_primitives_nadt_vfp_above(float first, float second) {
    /* VCMPE followed by BHI accepts both greater-than (0010) and unordered
     * (0011). Preserve that condition-code behavior instead of inheriting
     * C's always-false relational comparisons for NaNs. */
    return first > second || first != first || second != second;
}

static bool goodix_primitives_nadt_vfp_below_or_unordered(
    float first, float second) {
    /* VCMPE's unordered flags are 0011, which satisfy ARM's BLT (N != V). */
    return first < second || first != first || second != second;
}

bool goodix_primitives_nadt_extrema_neighborhood_mask(
    const float *values, size_t count, size_t row_count,
    size_t plateau_radius, int32_t selector,
    uint8_t *packed_scratch, size_t packed_capacity) {
    size_t packed_bytes = 0u;
    if (values == NULL || packed_scratch == NULL ||
            !goodix_primitives_nadt_peak_packed_bytes(
                count, row_count, &packed_bytes) ||
            plateau_radius >= row_count || packed_capacity < packed_bytes) {
        return false;
    }
    for (size_t byte = 0u; byte < packed_bytes; ++byte) {
        packed_scratch[byte] = 0u;
    }

    const float direction = selector == 1 ? -1.0f : 1.0f;
    for (size_t row = 0u; row < row_count; ++row) {
        const size_t left_edge = row < count ? row : count - 1u;
        const size_t interior_end = count > row + 1u
            ? count - row - 1u : 0u;
        const size_t row_bit = row * count;
        for (size_t column = 0u; column <= left_edge; ++column) {
            goodix_primitives_nadt_peak_bit_set(
                packed_scratch, row_bit + column);
        }
        for (size_t column = left_edge + 1u;
                column < interior_end; ++column) {
            const float center = values[column] * direction;
            const float left = values[column - row - 1u] * direction;
            const float right = values[column + row + 1u] * direction;
            if (!(goodix_primitives_nadt_vfp_above(center, left) &&
                    goodix_primitives_nadt_vfp_above(center, right))) {
                goodix_primitives_nadt_peak_bit_set(
                    packed_scratch, row_bit + column);
            } else {
                goodix_primitives_nadt_peak_bit_clear(
                    packed_scratch, row_bit + column);
            }
        }
        for (size_t column = interior_end; column < count; ++column) {
            goodix_primitives_nadt_peak_bit_set(
                packed_scratch, row_bit + column);
        }
    }

    for (size_t column = 0u; column < count; ++column) {
        bool matched = false;
        size_t matched_offset = 0u;
        for (size_t offset = 0u; offset < plateau_radius &&
                offset < column && offset < count - column - 1u; ++offset) {
            const float center = values[column] * direction;
            const float left = values[column - offset - 1u] * direction;
            const float right = values[column + offset + 1u] * direction;
            if (left != center ||
                    goodix_primitives_nadt_vfp_below_or_unordered(
                        center, right)) {
                break;
            }
            matched = true;
            matched_offset = offset;
            if (center > right) {
                break;
            }
        }
        if (matched && !goodix_primitives_nadt_peak_bit_test(
                packed_scratch, (matched_offset + 1u) * count + column)) {
            for (size_t row = 0u; row <= matched_offset; ++row) {
                goodix_primitives_nadt_peak_bit_clear(
                    packed_scratch, row * count + column);
            }
        }
    }
    return true;
}

bool goodix_primitives_nadt_peak_mask_columns(
    const float *values, size_t count,
    const goodix_primitives_nadt_peak_mask_configuration *configuration,
    int32_t selector, uint8_t *packed_scratch, size_t packed_capacity,
    uint8_t *column_flags, size_t column_capacity) {
    if (configuration == NULL || column_flags == NULL ||
            column_capacity < count || configuration->first_label == 0u ||
            configuration->first_label > configuration->row_count ||
            !goodix_primitives_nadt_extrema_neighborhood_mask(
                values, count, configuration->row_count,
                configuration->plateau_radius, selector,
                packed_scratch, packed_capacity)) {
        return false;
    }
    for (size_t column = 0u; column < count; ++column) {
        column_flags[column] = 0u;
    }
    uint16_t selected_label = 0u;
    if (!goodix_primitives_select_mask_row(
            packed_scratch, packed_capacity, count,
            configuration->first_label, configuration->row_count,
            &selected_label)) {
        return false;
    }
    return goodix_primitives_mask_columns_any(
        packed_scratch, packed_capacity, count, selected_label,
        column_flags, column_capacity);
}

bool goodix_primitives_nadt_peak_index_collect(
    const float *values, size_t count,
    const goodix_primitives_nadt_peak_mask_configuration *configuration,
    int32_t selector, uint8_t *packed_scratch, size_t packed_capacity,
    uint8_t *column_scratch, size_t column_capacity,
    int32_t *indices, size_t index_capacity, size_t *index_count) {
    if (indices == NULL || index_count == NULL || index_capacity == 0u ||
            index_capacity > (size_t)INT32_MAX ||
            !goodix_primitives_nadt_peak_mask_columns(
                values, count, configuration, selector,
                packed_scratch, packed_capacity,
                column_scratch, column_capacity)) {
        return false;
    }
    *index_count = 0u;
    for (size_t column = 0u; column < count; ++column) {
        if (column_scratch[column] != 0u) {
            continue;
        }
        if (*index_count < index_capacity) {
            indices[*index_count] = (int32_t)column;
            ++*index_count;
        } else {
            for (size_t index = 1u; index < index_capacity; ++index) {
                indices[index - 1u] = indices[index];
            }
            indices[index_capacity - 1u] = (int32_t)column;
        }
    }
    return true;
}

bool goodix_primitives_nadt_peak_histories_update(
    const float *values, size_t count, int32_t mode,
    const goodix_primitives_nadt_peak_mask_configuration *configuration,
    uint8_t *packed_scratch, size_t packed_capacity,
    uint8_t *column_scratch, size_t column_capacity,
    int32_t *index_scratch, size_t index_capacity,
    goodix_primitives_threshold_history histories[2]) {
    if (histories == NULL) {
        return false;
    }
    size_t index_count = 0u;
    if (!goodix_primitives_nadt_peak_index_collect(
            values, count, configuration, 0,
            packed_scratch, packed_capacity, column_scratch, column_capacity,
            index_scratch, index_capacity, &index_count) ||
            !goodix_primitives_accumulate_threshold_crossings(
                index_scratch, index_count, mode, &histories[0])) {
        return false;
    }
    for (size_t index = 0u; index < index_capacity; ++index) {
        index_scratch[index] = 0;
    }
    if (!goodix_primitives_nadt_peak_index_collect(
            values, count, configuration, 1,
            packed_scratch, packed_capacity, column_scratch, column_capacity,
            index_scratch, index_capacity, &index_count)) {
        return false;
    }
    return goodix_primitives_accumulate_threshold_crossings(
        index_scratch, index_count, mode, &histories[1]);
}

bool goodix_primitives_nadt_primary_ratio_peak_update(
    const goodix_primitives_nadt_channel_state *state, int32_t mode,
    uint8_t *packed_scratch, size_t packed_capacity,
    uint8_t *column_scratch, size_t column_capacity,
    int32_t *index_scratch, size_t index_capacity,
    goodix_primitives_threshold_history histories[2]) {
    const size_t sample_count = 125u;
    const size_t stock_index_capacity = 20u;
    static const goodix_primitives_nadt_peak_mask_configuration
        configuration = {36u, 2u, 1u};
    if (state == NULL || state->primary_ratio.values == NULL ||
            state->primary_ratio.count < sample_count ||
            state->primary_ratio.count > state->primary_ratio.capacity ||
            index_capacity < stock_index_capacity) {
        return false;
    }
    const float *const values = state->primary_ratio.values +
        state->primary_ratio.count - sample_count;
    return goodix_primitives_nadt_peak_histories_update(
        values, sample_count, mode, &configuration,
        packed_scratch, packed_capacity, column_scratch, column_capacity,
        index_scratch, stock_index_capacity, histories);
}

bool goodix_primitives_nadt_local_maximum_prefix_counts(
    const float *values, size_t count, size_t row_count,
    uint8_t *packed_scratch, size_t packed_capacity,
    int16_t *row_score_scratch, size_t row_score_capacity,
    int16_t *column_counts, size_t column_capacity) {
    size_t packed_bytes = 0u;
    if (values == NULL || packed_scratch == NULL ||
            row_score_scratch == NULL || column_counts == NULL ||
            row_score_capacity < row_count || column_capacity < count ||
            !goodix_primitives_nadt_peak_packed_bytes(
                count, row_count, &packed_bytes) ||
            count > (size_t)INT16_MAX || packed_capacity < packed_bytes) {
        return false;
    }
    for (size_t byte = 0u; byte < packed_bytes; ++byte) {
        packed_scratch[byte] = 0u;
    }
    for (size_t row = 0u; row < row_count; ++row) {
        row_score_scratch[row] = 0;
    }
    for (size_t column = 0u; column < count; ++column) {
        column_counts[column] = 0;
    }

    for (size_t row = 0u; row < row_count; ++row) {
        const size_t row_bit = row * count;
        const size_t left_edge = row < count ? row : count - 1u;
        const size_t interior_end = count > row + 1u
            ? count - row - 1u : 0u;
        for (size_t column = 0u; column <= left_edge; ++column) {
            goodix_primitives_nadt_peak_bit_set(
                packed_scratch, row_bit + column);
        }
        for (size_t column = left_edge + 1u;
                column < interior_end; ++column) {
            const float center = values[column];
            const float left = values[column - row - 1u];
            const float right = values[column + row + 1u];
            if (!(goodix_primitives_nadt_vfp_above(center, left) &&
                    goodix_primitives_nadt_vfp_above(center, right))) {
                goodix_primitives_nadt_peak_bit_set(
                    packed_scratch, row_bit + column);
            }
        }
        for (size_t column = interior_end; column < count; ++column) {
            goodix_primitives_nadt_peak_bit_set(
                packed_scratch, row_bit + column);
        }
    }

    for (size_t row = 0u; row < row_count; ++row) {
        int16_t score = 0;
        for (size_t column = 0u; column < count; ++column) {
            if (goodix_primitives_nadt_peak_bit_test(
                    packed_scratch, row * count + column)) {
                score = (int16_t)(score + 1);
            }
        }
        row_score_scratch[row] = score;
    }
    size_t selected_row = 0u;
    if (!goodix_primitives_i16_min_index(
            row_score_scratch, row_count, &selected_row)) {
        return false;
    }
    for (size_t column = 0u; column < count; ++column) {
        int16_t aggregate = 0;
        for (size_t row = 0u; row <= selected_row; ++row) {
            if (goodix_primitives_nadt_peak_bit_test(
                    packed_scratch, row * count + column)) {
                aggregate = (int16_t)(aggregate + 1);
            }
        }
        column_counts[column] = aggregate;
    }
    return true;
}

bool goodix_primitives_nadt_local_peak_indices(
    const float *values, size_t count, size_t row_count, size_t warmup,
    uint8_t *packed_scratch, size_t packed_capacity,
    int16_t *row_score_scratch, size_t row_score_capacity,
    int16_t *column_scratch, size_t column_capacity,
    int16_t *indices, size_t index_capacity, size_t *index_count) {
    if (index_count == NULL || warmup == SIZE_MAX ||
            (index_capacity != 0u && indices == NULL) ||
            !goodix_primitives_nadt_local_maximum_prefix_counts(
                values, count, row_count, packed_scratch, packed_capacity,
                row_score_scratch, row_score_capacity,
                column_scratch, column_capacity)) {
        return false;
    }
    size_t found = 0u;
    for (size_t index = 1u; index < count; ++index) {
        bool candidate = column_scratch[index] == 0;
        if (!candidate && column_scratch[index - 1u] == 1 &&
                column_scratch[index] == 1 &&
                values[index - 1u] == values[index]) {
            candidate = true;
        }
        if (candidate && warmup + 1u < index && found < index_capacity) {
            indices[found] = (int16_t)index;
            ++found;
        }
    }
    *index_count = found;
    return true;
}

bool goodix_primitives_centered_cross_correlation(
    const float *first, size_t first_count,
    const float *second, size_t second_count,
    float *output, size_t output_capacity) {
    if (first == NULL || second == NULL || output == NULL ||
            first_count == 0u || second_count == 0u ||
            first_count > (size_t)UINT32_MAX ||
            second_count > (size_t)UINT32_MAX) {
        return false;
    }
    const size_t maximum = first_count > second_count
        ? first_count : second_count;
    if (maximum > SIZE_MAX / 2u + 1u) {
        return false;
    }
    const size_t required = maximum * 2u - 1u;
    if (output_capacity < required) {
        return false;
    }

    const float *large = first;
    const float *small = second;
    size_t large_count = first_count;
    size_t small_count = second_count;
    bool reverse_output = false;
    size_t output_index = first_count - second_count;
    if (first_count < second_count) {
        large = second;
        small = first;
        large_count = second_count;
        small_count = first_count;
        reverse_output = true;
        output_index = first_count + second_count - 2u;
    }

    for (size_t overlap = 1u; overlap < small_count; ++overlap) {
        float sum = 0.0f;
        const size_t small_start = small_count - overlap;
        for (size_t index = 0u; index < overlap; ++index) {
            sum += large[index] * small[small_start + index];
        }
        output[output_index] = sum;
        output_index = reverse_output ? output_index - 1u : output_index + 1u;
    }
    for (size_t shift = 0u; shift <= large_count - small_count; ++shift) {
        float sum = 0.0f;
        for (size_t index = 0u; index < small_count; ++index) {
            sum += large[shift + index] * small[index];
        }
        output[output_index] = sum;
        output_index = reverse_output ? output_index - 1u : output_index + 1u;
    }
    for (size_t trailing = 1u; trailing < small_count; ++trailing) {
        const size_t overlap = small_count - trailing;
        const size_t large_start = large_count - small_count + trailing;
        float sum = 0.0f;
        for (size_t index = 0u; index < overlap; ++index) {
            sum += large[large_start + index] * small[index];
        }
        output[output_index] = sum;
        if (trailing + 1u < small_count) {
            output_index = reverse_output
                ? output_index - 1u : output_index + 1u;
        }
    }
    return true;
}

bool goodix_primitives_nadt_normalized_autocorrelation(
    const float *values, size_t count, float *output, size_t output_capacity,
    float *correlation_scratch, size_t scratch_capacity) {
    if (values == NULL || output == NULL || correlation_scratch == NULL ||
            count == 0u || output_capacity < count ||
            count > SIZE_MAX / 2u + 1u) {
        return false;
    }
    const size_t correlation_count = count * 2u - 1u;
    if (scratch_capacity < correlation_count ||
            !goodix_primitives_centered_cross_correlation(
                values, count, values, count,
                correlation_scratch, scratch_capacity)) {
        return false;
    }
    for (size_t index = 0u; index < count; ++index) {
        output[index] = correlation_scratch[index];
    }
    float maximum = 0.0f;
    size_t maximum_index = 0u;
    if (!goodix_primitives_float_max_index(
            output, count, &maximum, &maximum_index)) {
        return false;
    }
    (void)maximum_index;
    if ((int32_t)goodix_primitives_float_bits(maximum) >=
            (int32_t)UINT32_C(0x358637BD)) {
        const float factor = 1.0f / maximum;
        for (size_t index = 0u; index < count; ++index) {
            output[index] *= factor;
        }
    }
    return true;
}

int32_t goodix_primitives_nadt_inference_bridge(
    const goodix_primitives_nadt_inference_source *source,
    const goodix_primitives_nadt_inference_configuration *configuration,
    uint8_t selector, goodix_primitives_seven_word_operation_fn execute,
    float *primary_scratch, size_t primary_scratch_capacity,
    float *normalized_workspace, size_t normalized_workspace_capacity,
    float *output) {
    if (source == NULL || configuration == NULL || execute == NULL ||
            primary_scratch == NULL || normalized_workspace == NULL ||
            output == NULL) {
        return 5;
    }
    const size_t primary_count =
        (size_t)configuration->primary_rows *
        (size_t)configuration->primary_columns;
    const size_t secondary_count =
        (size_t)configuration->secondary_rows *
        (size_t)configuration->secondary_columns;
    if (source->primary_values == NULL ||
            source->secondary_values == NULL ||
            source->primary_count < primary_count ||
            source->secondary_count < secondary_count ||
            primary_scratch_capacity < primary_count ||
            normalized_workspace_capacity <
                GOODIX_PRIMITIVES_NADT_INFERENCE_WORKSPACE_FLOATS ||
            secondary_count >
                GOODIX_PRIMITIVES_NADT_INFERENCE_WORKSPACE_FLOATS) {
        return 5;
    }
    const size_t primary_start = source->primary_count - primary_count;
    for (size_t index = 0u; index < primary_count; ++index) {
        primary_scratch[index] = source->primary_values[primary_start + index];
    }
    const size_t secondary_start = source->secondary_count - secondary_count;
    if (!goodix_primitives_nadt_clip_normalize(
            &source->secondary_values[secondary_start], secondary_count,
            normalized_workspace, normalized_workspace_capacity)) {
        return 5;
    }

    const uintptr_t workspace_binding[4] = {
        (uintptr_t)primary_scratch,
        (uintptr_t)normalized_workspace,
        (uintptr_t)output,
        (uintptr_t)0,
    };
    const uintptr_t output_binding[2] = {
        (uintptr_t)output,
        (uintptr_t)0,
    };
    const int32_t result = execute(
        configuration->field_1c, configuration->field_14,
        (uintptr_t)workspace_binding, configuration->field_18,
        (uintptr_t)output_binding, (uintptr_t)0, (uintptr_t)selector);
    if (result != 0) {
        return 5;
    }

    float comparison = *output;
    if (*output < 0.0f) {
        comparison = 0.0f;
    }
    if ((int32_t)goodix_primitives_float_bits(comparison) <
            INT32_C(0x40000000)) {
        if (*output < 0.0f) {
            *output = 0.0f;
        }
    } else {
        *output = 2.0f;
    }
    return 0;
}

bool goodix_primitives_nadt_peak_dispersion_quality(
    float *values, size_t value_capacity,
    uint16_t *phase_indices, size_t phase_capacity,
    size_t count, uint32_t period,
    goodix_primitives_float_unary_fn square_root,
    float *dispersion, float *quality) {
    if (values == NULL || phase_indices == NULL || square_root == NULL ||
            dispersion == NULL || quality == NULL || period == 0u ||
            count >= (size_t)UINT32_MAX || value_capacity <= count ||
            phase_capacity <= count) {
        return false;
    }

    values[count] = 1.0f;
    phase_indices[count] = (uint16_t)(period - 1u);
    float squared_sum = 0.0f;
    float absolute_sum = 0.0f;
    uint32_t accepted = 0u;
    const size_t appended_count = count + 1u;
    for (size_t index = 0u; index < appended_count; ++index) {
        const float value = values[index];
        if (!(value > 0.0f)) {
            continue;
        }
        const float expected =
            (float)((uint32_t)phase_indices[index] + 1u) / (float)period;
        const float difference = value - expected;
        squared_sum += difference * difference;
        absolute_sum += difference >= 0.0f ? difference : -difference;
        ++accepted;
    }
    if (accepted == 0u) {
        *dispersion = 0.0f;
        *quality = 0.0f;
        return true;
    }

    const float divisor = (float)accepted;
    *dispersion = square_root(squared_sum / divisor);
    float mean_absolute = absolute_sum / divisor;
    if ((int32_t)goodix_primitives_float_bits(mean_absolute) >
            INT32_C(0x3F000000)) {
        mean_absolute = 0.5f;
    }
    *quality = 100.0f - mean_absolute * 2.0f * 100.0f;
    return true;
}

bool goodix_primitives_nadt_gaussian_interval_probability(
    float lower, float upper, float mean, float deviation, float step,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_double_unary_fn exponential,
    float *probability) {
    if (square_root == NULL || exponential == NULL || probability == NULL ||
            !(step > 0.0f)) {
        return false;
    }

    float accumulated = 0.0f;
    if (deviation != 0.0f) {
        const float root_two_pi = square_root(0x1.921fb6p+2f);
        const float normalization = 1.0f / (root_two_pi * deviation);
        const float first = lower + step;
        float current = first;
        while (first <= current && current <= upper) {
            const float exponent =
                ((mean - current) * (current - mean)) /
                (deviation * deviation * 2.0f);
            const double contribution =
                (double)normalization * exponential((double)exponent) *
                (double)step;
            accumulated = (float)((double)accumulated + contribution);
            const float next = current + step;
            if (!(next > current)) {
                break;
            }
            current = next;
        }
    }
    *probability = accumulated;
    return true;
}

bool goodix_primitives_nadt_symmetric_fir_i32(
    const int32_t *input, size_t count,
    const float *coefficients, size_t coefficient_count,
    int32_t *output, size_t output_capacity,
    int32_t *scratch, size_t scratch_capacity) {
    if (input == NULL || coefficients == NULL || output == NULL ||
            scratch == NULL || coefficient_count == 0u ||
            (coefficient_count & 1u) == 0u || output_capacity < count) {
        return false;
    }
    const size_t half = coefficient_count >> 1u;
    if (count <= half || coefficient_count - 1u > SIZE_MAX - count ||
            scratch_capacity < count + coefficient_count - 1u) {
        return false;
    }

    for (size_t index = 0u; index < half; ++index) {
        scratch[index] = input[half - index];
    }
    for (size_t index = 0u; index < count; ++index) {
        scratch[half + index] = input[index];
    }
    for (size_t index = 0u; index < half; ++index) {
        scratch[half + count + index] = input[count - 2u - index];
    }
    for (size_t output_index = 0u; output_index < count; ++output_index) {
        float accumulated = 0.0f;
        for (size_t kernel_index = 0u;
                kernel_index < coefficient_count; ++kernel_index) {
            accumulated +=
                (float)scratch[output_index + kernel_index] *
                coefficients[kernel_index];
        }
        if (!goodix_primitives_float_to_i32(
                accumulated, &output[output_index])) {
            return false;
        }
    }
    return true;
}

bool goodix_primitives_nadt_window_filter_i32(
    const int32_t *input, size_t count,
    int32_t *output, size_t output_capacity, uint32_t boundary_flags,
    const float *boundary_coefficients, size_t boundary_coefficient_count,
    int32_t *filtered_scratch, size_t filtered_scratch_capacity,
    int32_t *fir_scratch, size_t fir_scratch_capacity) {
    enum {
        HALF_WINDOW = 11,
        WINDOW_COUNT = 23,
        BOUNDARY_ROWS = 11,
        BOUNDARY_COEFFICIENT_COUNT = BOUNDARY_ROWS * WINDOW_COUNT,
    };
    if (input == NULL || output == NULL || boundary_coefficients == NULL ||
            filtered_scratch == NULL || fir_scratch == NULL ||
            count < WINDOW_COUNT || output_capacity < count ||
            boundary_coefficient_count < BOUNDARY_COEFFICIENT_COUNT ||
            filtered_scratch_capacity < count ||
            count > SIZE_MAX - (WINDOW_COUNT - 1u) ||
            fir_scratch_capacity < count + WINDOW_COUNT - 1u) {
        return false;
    }

    if ((boundary_flags & UINT32_C(2)) != 0u) {
        for (size_t row = 0u; row < BOUNDARY_ROWS; ++row) {
            float accumulated = 0.0f;
            for (size_t column = 0u; column < WINDOW_COUNT; ++column) {
                accumulated +=
                    boundary_coefficients[row * WINDOW_COUNT + column] *
                    (float)input[WINDOW_COUNT - 1u - column];
            }
            if (!goodix_primitives_float_to_i32(accumulated, &output[row])) {
                return false;
            }
        }
    }

    float uniform_coefficients[WINDOW_COUNT];
    for (size_t index = 0u; index < WINDOW_COUNT; ++index) {
        uniform_coefficients[index] = 0x1.642c86p-5f;
    }
    if (!goodix_primitives_nadt_symmetric_fir_i32(
            input, count, uniform_coefficients, WINDOW_COUNT,
            filtered_scratch, filtered_scratch_capacity,
            fir_scratch, fir_scratch_capacity)) {
        return false;
    }
    for (size_t index = HALF_WINDOW;
            index < count - HALF_WINDOW; ++index) {
        output[index] = filtered_scratch[index];
    }

    if ((boundary_flags & UINT32_C(1)) != 0u) {
        for (size_t row = 0u; row < BOUNDARY_ROWS; ++row) {
            float accumulated = 0.0f;
            const size_t coefficient_row = BOUNDARY_ROWS - 1u - row;
            for (size_t column = 0u; column < WINDOW_COUNT; ++column) {
                accumulated +=
                    boundary_coefficients[
                        coefficient_row * WINDOW_COUNT +
                        WINDOW_COUNT - 1u - column] *
                    (float)input[count - 1u - column];
            }
            if (!goodix_primitives_float_to_i32(
                    accumulated, &output[count - HALF_WINDOW + row])) {
                return false;
            }
        }
    }
    return true;
}

bool goodix_primitives_nadt_periodic_peak_rate(
    const float *amplitudes, const uint16_t *positions, size_t count,
    int32_t *selected_scratch, size_t selected_scratch_capacity,
    int32_t *difference_scratch, size_t difference_scratch_capacity,
    int32_t *rate) {
    if (amplitudes == NULL || positions == NULL ||
            selected_scratch == NULL || difference_scratch == NULL ||
            rate == NULL || count > (size_t)INT32_MAX ||
            selected_scratch_capacity < count ||
            (count != 0u && difference_scratch_capacity < count - 1u)) {
        return false;
    }

    float amplitude_sum = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        amplitude_sum += amplitudes[index];
    }
    const float mean = amplitude_sum / (float)(count == 0u ? 1u : count);
    int32_t truncated_mean = 0;
    if (!goodix_primitives_float_to_i32(mean, &truncated_mean)) {
        return false;
    }

    size_t selected_count = 0u;
    for (size_t index = 0u; index < count; ++index) {
        if ((int32_t)goodix_primitives_float_bits(amplitudes[index]) >=
                INT32_C(0x3DCCCCCD)) {
            selected_scratch[selected_count++] = (int32_t)positions[index];
        }
    }
    if (selected_count > 6u) {
        size_t retained_count = 0u;
        const float threshold = (float)truncated_mean;
        for (size_t index = 0u; index < selected_count; ++index) {
            if (amplitudes[index] >= threshold) {
                selected_scratch[retained_count++] =
                    selected_scratch[index];
            }
        }
        selected_count = retained_count;
    }

    if (selected_count < 3u || selected_count > 13u) {
        *rate = 0;
        return true;
    }
    for (size_t index = 0u; index + 1u < selected_count; ++index) {
        difference_scratch[index] =
            selected_scratch[index + 1u] - selected_scratch[index];
    }
    for (size_t index = 0u; index + 2u < selected_count; ++index) {
        int32_t change =
            difference_scratch[index + 1u] - difference_scratch[index];
        if (change < 0) {
            change = -change;
        }
        if (change > 3) {
            *rate = 0;
            return true;
        }
    }
    const int32_t span =
        selected_scratch[selected_count - 1u] - selected_scratch[0];
    if (span <= 0) {
        *rate = 0;
        return true;
    }
    const float raw_rate =
        ((float)(selected_count - 1u) * 1500.0f) / (float)span;
    const double rounded = (double)raw_rate + 0.5;
    if (rounded < (double)INT32_MIN || rounded >= 2147483648.0) {
        return false;
    }
    int32_t value = (int32_t)rounded;
    if (value < 40) {
        value = 40;
    } else if (value > 200) {
        value = 200;
    }
    *rate = value;
    return true;
}

static bool goodix_primitives_nadt_dual_window_channel_extract(
    const float *values, goodix_primitives_float_unary_fn square_root,
    goodix_primitives_nadt_dual_window_workspace *workspace,
    float *dispersion, int32_t *rate, float *quality) {
    if (!goodix_primitives_nadt_normalized_autocorrelation(
            values, GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES,
            workspace->autocorrelation,
            GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES,
            workspace->correlation,
            GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_CORRELATION_VALUES)) {
        return false;
    }

    size_t peak_count = 0u;
    if (!goodix_primitives_nadt_local_peak_indices(
            workspace->autocorrelation,
            GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES,
            GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_ROWS, 0u,
            workspace->peak_mask,
            GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_MASK_BYTES,
            workspace->row_scores,
            GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_ROWS,
            workspace->column_counts,
            GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES,
            workspace->peak_index_scratch,
            GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_PEAK_CAPACITY,
            &peak_count)) {
        return false;
    }
    for (size_t index = 0u; index < peak_count; ++index) {
        const uint16_t position =
            (uint16_t)workspace->peak_index_scratch[index];
        workspace->peak_indices[index] = position;
        workspace->peak_values[index] = workspace->autocorrelation[position];
    }
    if (peak_count == 0u) {
        *dispersion = 0.5f;
        return true;
    }
    if (!goodix_primitives_nadt_peak_dispersion_quality(
            workspace->peak_values,
            GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_PEAK_STORAGE,
            workspace->peak_indices,
            GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_PEAK_STORAGE,
            peak_count, GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES,
            square_root, dispersion, quality)) {
        return false;
    }
    return goodix_primitives_nadt_periodic_peak_rate(
        workspace->peak_values, workspace->peak_indices, peak_count,
        workspace->selected_positions,
        GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_PEAK_STORAGE,
        workspace->position_differences,
        GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_PEAK_CAPACITY, rate);
}

bool goodix_primitives_nadt_dual_window_features_extract(
    const goodix_primitives_nadt_dual_window_source *source,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_nadt_dual_window_workspace *workspace,
    goodix_primitives_nadt_dual_window_result *result) {
    if (source == NULL || square_root == NULL || workspace == NULL ||
            result == NULL || source->primary_values == NULL ||
            source->secondary_values == NULL ||
            source->primary_count <
                GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES ||
            source->secondary_count <
                GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES) {
        return false;
    }

    float primary_dispersion = result->primary_dispersion;
    float secondary_dispersion = result->secondary_dispersion;
    int32_t primary_rate = result->primary_rate;
    int32_t secondary_rate = result->secondary_rate;
    float primary_quality = result->primary_quality;
    float secondary_quality = result->secondary_quality;
    const float *const primary = source->primary_values +
        source->primary_count - GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES;
    const float *const secondary = source->secondary_values +
        source->secondary_count - GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES;

    if (!goodix_primitives_nadt_dual_window_channel_extract(
            primary, square_root, workspace, &primary_dispersion,
            &primary_rate, &primary_quality)) {
        return false;
    }
    const float primary_squared = goodix_primitives_sum_squares(
        workspace->autocorrelation,
        GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES);
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES; ++index) {
        workspace->primary_packed[index] =
            goodix_primitives_f32_bits_to_packed_5_10(
                goodix_primitives_float_bits(
                    workspace->autocorrelation[index]));
    }

    if (!goodix_primitives_nadt_dual_window_channel_extract(
            secondary, square_root, workspace, &secondary_dispersion,
            &secondary_rate, &secondary_quality)) {
        return false;
    }
    const float secondary_squared = goodix_primitives_sum_squares(
        workspace->autocorrelation,
        GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES);
    float dot = 0.0f;
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_DUAL_WINDOW_VALUES; ++index) {
        const float primary_value = goodix_primitives_float_from_bits(
            goodix_primitives_packed_5_10_to_f32_bits(
                workspace->primary_packed[index]));
        dot += primary_value * workspace->autocorrelation[index];
    }

    const float primary_norm = primary_squared < 0.0f
        ? 0.0f : square_root(primary_squared);
    const float secondary_norm = secondary_squared < 0.0f
        ? 0.0f : square_root(secondary_squared);
    const float correlation = primary_norm == 0.0f || secondary_norm == 0.0f
        ? 0.0f : dot / (primary_norm * secondary_norm);

    result->primary_dispersion = primary_dispersion;
    result->secondary_dispersion = secondary_dispersion;
    result->correlation = correlation;
    result->primary_rate = primary_rate;
    result->secondary_rate = secondary_rate;
    result->primary_quality = primary_quality;
    result->secondary_quality = secondary_quality;
    return true;
}

static bool goodix_primitives_nadt_signal_history_push(
    goodix_primitives_float_buffer *history, float value) {
    if (history == NULL || history->values == NULL ||
            history->capacity == 0u || history->count > history->capacity) {
        return false;
    }
    if (history->count < history->capacity) {
        history->values[history->count++] = value;
        return true;
    }
    for (size_t index = 1u; index < history->capacity; ++index) {
        history->values[index - 1u] = history->values[index];
    }
    history->values[history->capacity - 1u] = value;
    return true;
}

static bool goodix_primitives_f32_to_nearest_i32(
    float value, int32_t *result) {
    if (result == NULL || value != value || value < -2147483648.0f ||
            value >= 2147483648.0f) {
        return false;
    }
    int32_t rounded = (int32_t)value;
    const float fraction = value - (float)rounded;
    if (fraction > 0.5f ||
            (fraction == 0.5f && (rounded & INT32_C(1)) != 0)) {
        ++rounded;
    } else if (fraction < -0.5f ||
            (fraction == -0.5f && (rounded & INT32_C(1)) != 0)) {
        --rounded;
    }
    *result = rounded;
    return true;
}

bool goodix_primitives_nadt_signal_confidence_update(
    const goodix_primitives_nadt_dual_window_result *features,
    const uint16_t *interval_positions, size_t interval_position_count,
    bool enabled, goodix_primitives_nadt_signal_confidence_state *state,
    goodix_primitives_nadt_signal_confidence_workspace *workspace,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_double_unary_fn exponential,
    goodix_primitives_nadt_signal_confidence_diagnostics *diagnostics) {
    if (features == NULL || state == NULL ||
            state->rate_history.values == NULL ||
            state->rate_history.capacity == 0u ||
            state->rate_history.count > state->rate_history.capacity) {
        return false;
    }

    int32_t selected_rate = features->primary_rate;
    float selected_quality = features->primary_quality;
    int64_t rate_difference =
        (int64_t)features->primary_rate - features->secondary_rate;
    if (rate_difference < 0) {
        rate_difference = -rate_difference;
    }
    if (rate_difference < 10) {
        const double blended = (double)features->secondary_rate * 0.2 +
            (double)features->primary_rate * 0.8;
        if (blended < (double)INT32_MIN || blended >= 2147483648.0) {
            return false;
        }
        selected_rate = (int32_t)blended;
        selected_quality = !(features->primary_quality <
                features->secondary_quality)
            ? features->primary_quality : features->secondary_quality;
    } else if (features->primary_rate == 0 &&
            features->secondary_rate > 0) {
        selected_rate = features->secondary_rate;
        selected_quality = features->secondary_quality;
    }

    if (diagnostics != NULL) {
        diagnostics->selected_rate = selected_rate;
        diagnostics->selected_quality = selected_quality;
        diagnostics->interval_deviation = 0.0f;
        diagnostics->rate_appended = false;
    }
    if (!enabled) {
        return true;
    }
    if (interval_positions == NULL || workspace == NULL ||
            square_root == NULL || exponential == NULL ||
            interval_position_count !=
                GOODIX_PRIMITIVES_NADT_SIGNAL_INTERVAL_VALUES) {
        return false;
    }

    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_SIGNAL_DIFFERENCE_VALUES;
            ++index) {
        workspace->differences[index] = (float)(
            (int32_t)interval_positions[index + 1u] -
            (int32_t)interval_positions[index]);
    }
    float interval_deviation = 0.0f;
    if (!goodix_primitives_strided_sample_standard_deviation(
            workspace->differences,
            GOODIX_PRIMITIVES_NADT_SIGNAL_DIFFERENCE_VALUES, 1u,
            GOODIX_PRIMITIVES_NADT_SIGNAL_DIFFERENCE_VALUES,
            square_root, &interval_deviation)) {
        return false;
    }
    if (diagnostics != NULL) {
        diagnostics->interval_deviation = interval_deviation;
    }

    const int32_t quality_bits =
        (int32_t)goodix_primitives_float_bits(selected_quality);
    const int32_t deviation_bits =
        (int32_t)goodix_primitives_float_bits(interval_deviation);
    if (quality_bits > INT32_C(0x42A00000) &&
            deviation_bits > INT32_C(0x42C80000)) {
        state->high_variation_windows = goodix_primitives_wrapped_add_i32(
            state->high_variation_windows, 1);
    } else {
        state->high_variation_windows = 0;
    }
    if (quality_bits > INT32_C(0x42A00000) &&
            deviation_bits < INT32_C(0x42480000)) {
        state->low_variation_windows = goodix_primitives_wrapped_add_i32(
            state->low_variation_windows, 1);
    } else {
        state->low_variation_windows = 0;
    }
    if (state->high_variation_windows >= 5) {
        state->mode = 1;
    } else if (state->low_variation_windows >= 5) {
        state->mode = 0;
    }

    if (selected_rate <= 0) {
        state->hold_windows = (uint8_t)(state->hold_windows + 1u);
        return true;
    }

    const float latest_value = state->rate_history.count == 0u
        ? 0.0f
        : state->rate_history.values[state->rate_history.count - 1u];
    int32_t latest_rate = 0;
    if (!goodix_primitives_f32_to_nearest_i32(
            latest_value, &latest_rate)) {
        return false;
    }
    int64_t latest_difference = (int64_t)latest_rate - selected_rate;
    if (latest_difference < 0) {
        latest_difference = -latest_difference;
    }
    const int32_t substitution_threshold = state->mode == 0
        ? 200 : (state->mode == 1 || state->mode == 2 ? 2000 : 0);
    const bool central_rate = selected_rate > 50 && selected_rate < 90;
    bool append = false;
    if (latest_difference < 10) {
        const float quality_threshold = latest_rate == 0 && central_rate
            ? 40.0f : 50.0f;
        append = quality_bits >
            (int32_t)goodix_primitives_float_bits(quality_threshold);
    }
    if (!append && latest_difference < 5 && latest_rate != 0) {
        append = true;
    }
    if (!append && latest_rate == 0 &&
            quality_bits > INT32_C(0x428C0000)) {
        append = true;
    }
    if (!append && state->hold_windows >= 10u &&
            (quality_bits > INT32_C(0x428C0000) ||
             (central_rate && quality_bits > INT32_C(0x42200000)))) {
        append = true;
    }
    if (append) {
        if (interval_deviation > (float)substitution_threshold &&
                latest_rate != 0) {
            selected_rate = latest_rate;
        }
        if (!goodix_primitives_nadt_signal_history_push(
                &state->rate_history, (float)selected_rate)) {
            return false;
        }
        state->hold_windows = 0u;
        if (diagnostics != NULL) {
            diagnostics->selected_rate = selected_rate;
            diagnostics->rate_appended = true;
        }
    } else {
        state->hold_windows = (uint8_t)(state->hold_windows + 1u);
    }

    if (!goodix_primitives_float_buffer_mean(
            &state->rate_history, &state->rolling_mean)) {
        state->rolling_mean = 0.0f;
    }
    if (state->rate_history.count < 2u) {
        state->probability = 0.0f;
        return true;
    }
    float history_deviation = 0.0f;
    if (!goodix_primitives_float_buffer_incremental_standard_deviation(
            &state->rate_history, square_root, &history_deviation)) {
        return false;
    }
    const float half_width = state->rolling_mean * 0.05f;
    return goodix_primitives_nadt_gaussian_interval_probability(
        -half_width, half_width, 0.0f, history_deviation, 0.1f,
        square_root, exponential, &state->probability);
}

static int32_t goodix_primitives_nadt_output_clamp(int32_t rate) {
    if (rate < 65) {
        return 65;
    }
    return rate > 100 ? 100 : rate;
}

bool goodix_primitives_nadt_output_state_select(
    const goodix_primitives_nadt_output_selection_configuration *configuration,
    uint32_t sample_index,
    goodix_primitives_nadt_output_selection_state *state,
    float *output_rate, uint8_t *output_kind) {
    if (configuration == NULL || state == NULL || output_rate == NULL ||
            output_kind == NULL || state->rate_history.values == NULL ||
            state->rate_history.count == 0u ||
            state->rate_history.count > state->rate_history.capacity ||
            (state->transition_state != 0u &&
             state->transition_state != 1u &&
             state->transition_state != 2u &&
             state->transition_state != 12u &&
             state->transition_state != 21u)) {
        return false;
    }

    const float latest =
        state->rate_history.values[state->rate_history.count - 1u];
    const double adjusted_rate = (double)latest + 0.5;
    const double adjusted_phase =
        (double)(state->phase_value * 10000.0f) + 0.5;
    if (adjusted_rate < (double)INT32_MIN ||
            adjusted_rate >= 2147483648.0 ||
            adjusted_phase < (double)INT32_MIN ||
            adjusted_phase >= 2147483648.0) {
        return false;
    }
    const int32_t rate = (int32_t)adjusted_rate;
    const int32_t phase = (int32_t)adjusted_phase;
    int32_t rounded_gate = 0;
    if (!goodix_primitives_f32_to_nearest_i32(
            state->gate_value, &rounded_gate)) {
        return false;
    }

    uint8_t retained = state->retained_rate;
    if (((uint32_t)phase & 1u) == 0u) {
        const uint8_t remainder = (uint8_t)(rate % 6);
        if (remainder == 1u) {
            retained = (uint8_t)goodix_primitives_nadt_output_clamp(
                (int32_t)retained + 2);
        } else if (remainder == 2u || remainder == 3u) {
            retained = (uint8_t)goodix_primitives_nadt_output_clamp(
                (int32_t)retained - 1);
        } else if (remainder == 4u || remainder == 5u) {
            retained = (uint8_t)goodix_primitives_nadt_output_clamp(
                (int32_t)retained + 1);
        }
    }

    bool wrote_output = false;
#define GOODIX_NADT_WRITE_RATE() do {                                      \
        *output_rate = (float)goodix_primitives_nadt_output_clamp(rate);   \
        *output_kind = 5u;                                                  \
        wrote_output = true;                                                \
    } while (false)
#define GOODIX_NADT_WRITE_RETAINED() do {                                  \
        *output_rate = (float)retained;                                     \
        *output_kind = 2u;                                                  \
        wrote_output = true;                                                \
    } while (false)

    switch (state->transition_state) {
        case 0u:
            if (sample_index >= configuration->initial_sample &&
                    state->signal_present == 0u) {
                GOODIX_NADT_WRITE_RATE();
                state->transition_state =
                    rate >= (int32_t)configuration->rate_threshold ? 1u : 2u;
            }
            break;
        case 1u:
            if (rate < (int32_t)configuration->rate_threshold) {
                if ((configuration->flags & 1u) != 0u &&
                        state->signal_present != 0u) {
                    GOODIX_NADT_WRITE_RETAINED();
                    state->transition_state = 12u;
                } else {
                    GOODIX_NADT_WRITE_RATE();
                    state->transition_state = 2u;
                }
            } else {
                GOODIX_NADT_WRITE_RATE();
            }
            break;
        case 2u:
            if (rate < (int32_t)configuration->rate_threshold) {
                GOODIX_NADT_WRITE_RATE();
            } else if ((configuration->flags & 2u) != 0u &&
                    state->signal_present != 0u) {
                GOODIX_NADT_WRITE_RETAINED();
                state->transition_state = 21u;
            } else {
                GOODIX_NADT_WRITE_RATE();
                state->transition_state = 1u;
            }
            break;
        case 12u:
            if (rate >= (int32_t)configuration->rate_threshold) {
                GOODIX_NADT_WRITE_RATE();
                state->transition_state = 1u;
            } else if (state->signal_present == 0u) {
                GOODIX_NADT_WRITE_RATE();
                state->transition_state = 2u;
            } else {
                GOODIX_NADT_WRITE_RETAINED();
            }
            break;
        case 21u:
            if (rate < (int32_t)configuration->rate_threshold) {
                GOODIX_NADT_WRITE_RATE();
                state->transition_state = 2u;
            } else if (state->signal_present != 0u) {
                GOODIX_NADT_WRITE_RETAINED();
            } else {
                GOODIX_NADT_WRITE_RATE();
                state->transition_state = 1u;
            }
            break;
        default:
            break;
    }

    if (wrote_output && *output_kind == 5u) {
        state->retained_rate = (uint8_t)*output_rate;
    }
    if (state->transition_state == 0u &&
            (configuration->flags & 4u) != 0u &&
            sample_index >= configuration->override_sample &&
            (state->persistence >= 6u || rounded_gate != 0) &&
            (rate >= (int32_t)configuration->rate_threshold ||
             rate % 3 == 0 || rounded_gate != 0)) {
        *output_rate = (float)goodix_primitives_nadt_output_clamp(
            rate % 4 + 97);
        *output_kind = 1u;
    }

#undef GOODIX_NADT_WRITE_RETAINED
#undef GOODIX_NADT_WRITE_RATE
    return true;
}

static int32_t goodix_primitives_nadt_preprocess_call(
    const goodix_primitives_nadt_preprocess_plan *plan,
    goodix_primitives_nadt_preprocess_stage stage,
    goodix_primitives_nadt_preprocess_frame *frame) {
    return plan->execute(plan->context, stage, frame);
}

static float goodix_primitives_nadt_preprocess_adjust(
    float value, float metric) {
    uint32_t bits = goodix_primitives_float_bits(value);
    if (bits + UINT32_C(0xBD4BFFFF) < UINT32_C(0x000C0000)) {
        value += 1.0f;
    }
    int32_t metric_integer = 0;
    if (!goodix_primitives_f32_to_nearest_i32(metric, &metric_integer)) {
        metric_integer = INT32_MIN;
    }
    bits = goodix_primitives_float_bits(value);
    if (bits + UINT32_C(0xBD41FFFF) < UINT32_C(0x0003FFFF) &&
            metric_integer % 3 == 2) {
        value += 1.0f;
    }
    bits = goodix_primitives_float_bits(value);
    if (bits + UINT32_C(0xBD3E0000) < UINT32_C(0x00040001)) {
        if (metric_integer % 5 == 0) {
            value -= 1.0f;
        } else if (metric_integer % 5 == 1) {
            value += 1.0f;
        }
    }
    return value;
}

int32_t goodix_primitives_spo2_calc(
    const goodix_primitives_nadt_preprocess_plan *plan,
    const goodix_primitives_spo2_calc_input *source,
    goodix_primitives_nadt_preprocess_state *state,
    goodix_primitives_nadt_preprocess_workspace *workspace,
    uint32_t *output_words, size_t output_word_count) {
    if (state == NULL || !state->initialized) {
        return 7;
    }
    if (plan == NULL || plan->execute == NULL || source == NULL ||
            workspace == NULL || output_words == NULL ||
            output_word_count < 16u || state->lane_count == 0u ||
            state->lane_count > UINT32_MAX /
                GOODIX_PRIMITIVES_NADT_PREPROCESS_RECORD_BYTES ||
            state->lane_count > UINT32_MAX /
                GOODIX_PRIMITIVES_NADT_PREPROCESS_SUMMARY_BYTES ||
            workspace->assembled_records == NULL ||
            workspace->assembled_record_bytes <
                (size_t)state->lane_count *
                    GOODIX_PRIMITIVES_NADT_PREPROCESS_RECORD_BYTES ||
            workspace->summaries == NULL ||
            workspace->summary_bytes <
                (size_t)state->lane_count *
                    GOODIX_PRIMITIVES_NADT_PREPROCESS_SUMMARY_BYTES ||
            workspace->inference_values == NULL ||
            workspace->inference_capacity < 1u ||
            workspace->adjusted_values == NULL ||
            workspace->adjusted_capacity < 1u ||
            workspace->selected_rates == NULL ||
            workspace->selected_rate_capacity < 1u ||
            workspace->selected_kinds == NULL ||
            workspace->selected_kind_capacity < 1u ||
            plan->quartic_coefficients == NULL ||
            plan->quartic_coefficient_count < 7u) {
        return 5;
    }

    goodix_primitives_nadt_preprocess_frame frame = {
        .source = source,
        .output_words = output_words,
        .output_word_count = output_word_count,
        .state = state,
        .workspace = workspace,
    };
    state->process_count = (uint32_t)(state->process_count + 1u);
    int32_t status = goodix_primitives_nadt_preprocess_call(
        plan, GOODIX_PRIMITIVES_NADT_PREPROCESS_ASSEMBLE, &frame);
    if (status != 0) {
        (void)goodix_primitives_nadt_preprocess_call(
            plan, GOODIX_PRIMITIVES_NADT_PREPROCESS_FAILURE_ENCODE, &frame);
        return status;
    }
    status = goodix_primitives_nadt_preprocess_call(
        plan, GOODIX_PRIMITIVES_NADT_PREPROCESS_BATCH_ACCUMULATE, &frame);
    if (status != 0) {
        (void)goodix_primitives_nadt_preprocess_call(
            plan, GOODIX_PRIMITIVES_NADT_PREPROCESS_FAILURE_ENCODE, &frame);
        return status;
    }

    state->frame_count = (uint32_t)(state->frame_count + 1u);
    status = goodix_primitives_nadt_preprocess_call(
        plan, GOODIX_PRIMITIVES_NADT_PREPROCESS_ACCUMULATE, &frame);
    if (status != 0) {
        return status;
    }
    state->batch_index = state->frame_count / 25u;
    (void)goodix_primitives_nadt_preprocess_call(
        plan, GOODIX_PRIMITIVES_NADT_PREPROCESS_SPECTRAL_PREPARE, &frame);
    (void)goodix_primitives_nadt_preprocess_call(
        plan, GOODIX_PRIMITIVES_NADT_PREPROCESS_PRIMARY_PEAK_UPDATE, &frame);
    (void)goodix_primitives_nadt_preprocess_call(
        plan, GOODIX_PRIMITIVES_NADT_PREPROCESS_SUMMARY_DISPATCH, &frame);
    (void)goodix_primitives_nadt_preprocess_call(
        plan, GOODIX_PRIMITIVES_NADT_PREPROCESS_QUALITY_UPDATE, &frame);
    (void)goodix_primitives_nadt_preprocess_call(
        plan, GOODIX_PRIMITIVES_NADT_PREPROCESS_TRANSITION_UPDATE, &frame);
    status = goodix_primitives_nadt_preprocess_call(
        plan, GOODIX_PRIMITIVES_NADT_PREPROCESS_INFERENCE, &frame);

    float adjusted = goodix_primitives_quartic_evaluate(
        workspace->inference_values[0], plan->quartic_coefficients);
    if (state->adjustment_enabled &&
            !(workspace->summary_metric >=
              (float)state->summary_metric_threshold)) {
        adjusted = goodix_primitives_nadt_preprocess_adjust(
            adjusted, workspace->summary_metric);
    }
    workspace->adjusted_values[0] = adjusted;
    (void)goodix_primitives_nadt_preprocess_call(
        plan, GOODIX_PRIMITIVES_NADT_PREPROCESS_OUTPUT_QUALITY, &frame);
    (void)goodix_primitives_nadt_preprocess_call(
        plan, GOODIX_PRIMITIVES_NADT_PREPROCESS_OUTPUT_SELECT, &frame);
    (void)goodix_primitives_nadt_preprocess_call(
        plan, GOODIX_PRIMITIVES_NADT_PREPROCESS_SIGNAL_CONFIDENCE, &frame);
    (void)goodix_primitives_nadt_preprocess_call(
        plan, GOODIX_PRIMITIVES_NADT_PREPROCESS_OUTPUT_BUILD, &frame);
    return status;
}

int32_t goodix_primitives_nadt_preprocess_execute(
    const goodix_primitives_nadt_preprocess_plan *plan,
    const void *source, goodix_primitives_nadt_preprocess_state *state,
    goodix_primitives_nadt_preprocess_workspace *workspace,
    uint32_t *output_words, size_t output_word_count) {
    return goodix_primitives_spo2_calc(
        plan, (const goodix_primitives_spo2_calc_input *)source, state,
        workspace, output_words, output_word_count);
}

bool goodix_primitives_nadt_alternate_state_classify(
    const int16_t *samples, size_t count,
    const goodix_primitives_nadt_alternate_configuration *configuration,
    goodix_primitives_nadt_alternate_state *state,
    goodix_primitives_nadt_alternate_workspace *workspace,
    goodix_primitives_nadt_alternate_diagnostics *diagnostics,
    int32_t *result) {
    if (configuration == NULL || state == NULL || result == NULL) {
        return false;
    }
    *result = state->current_result;
    if (!configuration->enabled) {
        return true;
    }
    if (state->processing) {
        return false;
    }

    bool matched = false;
    if (count == GOODIX_PRIMITIVES_NADT_ALTERNATE_SAMPLE_COUNT) {
        if (samples == NULL || workspace == NULL) {
            return false;
        }
        int16_t minimum = samples[0];
        int16_t maximum = samples[0];
        int32_t sum = 0;
        for (size_t index = 0u; index < count; ++index) {
            const int16_t value = samples[index];
            if (value > maximum) {
                maximum = value;
            }
            if (value < minimum) {
                minimum = value;
            }
            sum += value;
        }
        const int16_t range = goodix_primitives_u16_bits_to_i16(
            (uint16_t)((uint16_t)maximum - (uint16_t)minimum));
        if (diagnostics != NULL) {
            diagnostics->range = range;
        }

        if ((state->current_result == 0 || state->current_result == 1) &&
                state->sample_gate <= configuration->sample_gate_limit &&
                range > configuration->minimum_range) {
            goodix_primitives_autocorrelation_state correlation =
                state->autocorrelation;
            const int32_t mean = sum /
                (int32_t)GOODIX_PRIMITIVES_NADT_ALTERNATE_SAMPLE_COUNT;
            if (!goodix_primitives_i16_autocorrelation_transform(
                    samples, workspace->centered, count, mean, 1000,
                    &correlation) ||
                    !goodix_primitives_i16_autocorrelation_transform(
                        workspace->centered, workspace->transformed, count,
                        0, 10000, &correlation)) {
                return false;
            }
            state->autocorrelation = correlation;

            uint8_t maxima_count = 0u;
            uint8_t minima_count = 0u;
            if (!goodix_primitives_i16_local_extrema_indices(
                    workspace->transformed, count,
                    workspace->maxima,
                    GOODIX_PRIMITIVES_NADT_ALTERNATE_EXTREMA_CAPACITY,
                    &maxima_count, workspace->minima,
                    GOODIX_PRIMITIVES_NADT_ALTERNATE_EXTREMA_CAPACITY,
                    &minima_count)) {
                return false;
            }
            uint8_t quality = 0u;
            if (maxima_count != 0u &&
                    !goodix_primitives_peak_quality_update(
                        workspace->transformed, count, workspace->maxima,
                        GOODIX_PRIMITIVES_NADT_ALTERNATE_EXTREMA_CAPACITY,
                        &maxima_count,
                        (int32_t)GOODIX_PRIMITIVES_NADT_ALTERNATE_SAMPLE_COUNT,
                        10000, &quality)) {
                return false;
            }

            size_t retained_maxima = 0u;
            for (size_t index = 0u; index < maxima_count; ++index) {
                const int16_t sample_index = workspace->maxima[index];
                if (workspace->transformed[(size_t)sample_index] >= 800) {
                    workspace->maxima[retained_maxima++] = sample_index;
                }
            }
            size_t retained_minima = 0u;
            for (size_t index = 0u; index < minima_count; ++index) {
                const int16_t sample_index = workspace->minima[index];
                const int32_t value =
                    workspace->transformed[(size_t)sample_index];
                const int32_t magnitude = value < 0 ? -value : value;
                if (magnitude >= 800 && value < 0) {
                    workspace->minima[retained_minima++] = sample_index;
                }
            }
            if (diagnostics != NULL) {
                diagnostics->quality = quality;
                diagnostics->maxima_count = (uint8_t)retained_maxima;
                diagnostics->minima_count = (uint8_t)retained_minima;
            }

            const size_t count_difference = retained_maxima > retained_minima
                ? retained_maxima - retained_minima
                : retained_minima - retained_maxima;
            bool alternating = retained_maxima >= 2u &&
                retained_minima >= 2u && count_difference <= 1u;
            if (alternating && retained_maxima == retained_minima + 1u) {
                alternating = workspace->maxima[0] < workspace->minima[0];
            } else if (alternating &&
                    retained_minima == retained_maxima + 1u) {
                alternating = workspace->maxima[0] > workspace->minima[0];
            }

            if (alternating) {
                const size_t extrema_count = retained_maxima + retained_minima;
                const size_t interval_count = extrema_count - 1u;
                size_t maximum_cursor = 0u;
                size_t minimum_cursor = 0u;
                const bool maximum_first =
                    workspace->maxima[0] < workspace->minima[0];
                for (size_t index = 0u; index < interval_count; ++index) {
                    int32_t difference =
                        (int32_t)workspace->maxima[maximum_cursor] -
                        (int32_t)workspace->minima[minimum_cursor];
                    if (difference < 0) {
                        difference = -difference;
                    }
                    workspace->intervals[index] = (int16_t)difference;
                    if ((index & 1u) == 0u) {
                        if (maximum_first) {
                            ++maximum_cursor;
                        } else {
                            ++minimum_cursor;
                        }
                    } else if (maximum_first) {
                        ++minimum_cursor;
                    } else {
                        ++maximum_cursor;
                    }
                }

                int16_t minimum_interval = workspace->intervals[0];
                int16_t maximum_interval = workspace->intervals[0];
                int16_t interval_sum = 0;
                for (size_t index = 0u; index < interval_count; ++index) {
                    const int16_t value = workspace->intervals[index];
                    if (value > maximum_interval) {
                        maximum_interval = value;
                    }
                    if (value < minimum_interval) {
                        minimum_interval = value;
                    }
                    interval_sum = goodix_primitives_u16_bits_to_i16(
                        (uint16_t)((uint16_t)interval_sum +
                                   (uint16_t)value));
                }
                const int16_t average_interval = (int16_t)(
                    (int32_t)interval_sum / (int32_t)interval_count);
                const int16_t interval_range = (int16_t)(
                    maximum_interval - minimum_interval);
                if (diagnostics != NULL) {
                    diagnostics->minimum_interval = minimum_interval;
                    diagnostics->interval_range = interval_range;
                }
                const int32_t half_spread =
                    (int32_t)(configuration->maximum_interval_spread >> 1u);
                matched = (int32_t)maximum_interval - average_interval <=
                              half_spread &&
                    (int32_t)average_interval - minimum_interval <=
                              half_spread &&
                    (int32_t)maximum_interval - minimum_interval <=
                        (int32_t)configuration->maximum_interval_spread &&
                    minimum_interval >
                        (int32_t)configuration->minimum_interval &&
                    quality > configuration->minimum_quality;
            }
        }
    }

    state->consecutive_matches = matched
        ? (uint8_t)(state->consecutive_matches + 1u) : 0u;
    if (state->consecutive_matches >=
            configuration->required_consecutive_windows) {
        state->mode = 4u;
        state->current_result = 2;
        state->consecutive_matches = 0u;
        *result = 2;
    }
    return true;
}

static int32_t goodix_primitives_nadt_wrapped_difference(
    int32_t first, int32_t second) {
    return goodix_primitives_u32_as_i32(
        (uint32_t)first - (uint32_t)second);
}

static int32_t goodix_primitives_nadt_wrapped_absolute(int32_t value) {
    const uint32_t bits = value < 0
        ? UINT32_C(0) - (uint32_t)value : (uint32_t)value;
    return goodix_primitives_u32_as_i32(bits);
}

static uint8_t goodix_primitives_nadt_increment_u8(uint8_t value) {
    return (uint8_t)(value + UINT8_C(1));
}

static bool goodix_primitives_nadt_rounded_i32(
    float value, goodix_primitives_float_unary_fn round_provider,
    int32_t *result) {
    if (round_provider == NULL || result == NULL) {
        return false;
    }
    const float rounded = round_provider(value);
    if (!(rounded >= -2147483648.0f && rounded < 2147483648.0f)) {
        return false;
    }
    *result = (int32_t)rounded;
    return true;
}

bool goodix_primitives_nadt_primary_signal_classify(
    const int32_t *primary, const int32_t *secondary, size_t count,
    const goodix_primitives_nadt_primary_configuration *configuration,
    goodix_primitives_nadt_window_state *state,
    goodix_primitives_nadt_primary_workspace *workspace,
    goodix_primitives_autocorrelation_state *autocorrelation_state,
    goodix_primitives_float_unary_fn round_provider,
    goodix_primitives_nadt_primary_diagnostics *diagnostics,
    uint8_t *result) {
    enum { NADT_FILTER_WINDOW = 23 };
    if (primary == NULL || secondary == NULL || configuration == NULL ||
            state == NULL || workspace == NULL ||
            autocorrelation_state == NULL || round_provider == NULL ||
            result == NULL || count < NADT_FILTER_WINDOW ||
            count > GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES ||
            configuration->filter_boundary_coefficients == NULL ||
            configuration->filter_boundary_coefficient_count <
                GOODIX_PRIMITIVES_NADT_PRIMARY_BOUNDARY_COEFFICIENTS) {
        return false;
    }
    uint8_t classified = (uint8_t)(uint32_t)state->current_result;
    if (!configuration->enabled) {
        *result = classified;
        return true;
    }

    int32_t primary_range = 0;
    float primary_mean = 0.0f;
    if (!goodix_primitives_i32_range(
            primary, count, NULL, NULL, &primary_range) ||
            !goodix_primitives_i32_mean(primary, count, &primary_mean)) {
        return false;
    }
    int32_t history_threshold = 0;
    if (primary_range > 1000) {
        history_threshold = primary_range / 70;
    } else if (primary_range > 300 ||
            (primary_range > 100 && primary_mean < 10000.0f)) {
        history_threshold = primary_range / 50;
    }
    goodix_primitives_extrema_history history = {0};
    history.extremum = primary[0];
    uint32_t transition_count = 0u;
    for (size_t index = 0u; index < count; ++index) {
        int32_t transition = 0;
        if (!goodix_primitives_extrema_history_update(
                &history, primary[index], history_threshold, &transition)) {
            return false;
        }
        if (transition != 0) {
            ++transition_count;
        }
    }
    const int32_t cadence_offset = primary_range < 9 ? -370 : 30;
    const int32_t cadence_threshold = goodix_primitives_u32_as_i32(
        (uint32_t)configuration->cadence_scale * UINT32_C(8) +
        (uint32_t)cadence_offset) / INT32_C(60);

    int32_t activity_maximum = configuration->activity_maxima[0];
    int32_t activity_minimum = configuration->activity_minima[0];
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_WINDOW_METRIC_COUNT; ++index) {
        if (configuration->activity_maxima[index] > activity_maximum) {
            activity_maximum = configuration->activity_maxima[index];
        }
        if (configuration->activity_minima[index] != 0 &&
                configuration->activity_minima[index] < activity_minimum) {
            activity_minimum = configuration->activity_minima[index];
        }
    }
    const int32_t activity_span = goodix_primitives_nadt_wrapped_difference(
        activity_maximum, activity_minimum) >> 8;
    const bool release_family =
        state->trigger_windows[0] == 25u ||
        state->trigger_windows[1] == 25u ||
        (state->trigger_windows[2] == 25u && state->energy_metric == 0) ||
        (state->trigger_windows[3] == 25u && state->energy_metric == 0);
    if (release_family && state->inactive_windows > 0 &&
            activity_span >= configuration->activity_span_threshold &&
            state->profile == 2u) {
        state->profile_release_streak = goodix_primitives_nadt_increment_u8(
            state->profile_release_streak);
        if (state->profile_release_streak >= 8u) {
            state->profile = 0u;
            state->profile_counter = 0;
        }
    }
    state->long_window_score = goodix_primitives_u32_as_i32(
        transition_count);
    uint8_t quality = state->quality;
    const uint8_t input_quality = quality;

    if (!goodix_primitives_nadt_window_filter_i32(
            secondary, count, workspace->filtered,
            GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES,
            configuration->filter_boundary_flags,
            configuration->filter_boundary_coefficients,
            configuration->filter_boundary_coefficient_count,
            workspace->filter_scratch,
            GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES,
            workspace->fir_scratch,
            GOODIX_PRIMITIVES_NADT_PRIMARY_FIR_SCRATCH_VALUES)) {
        return false;
    }
    int32_t filtered_range = 0;
    if (!goodix_primitives_i32_range(
            workspace->filtered, count, NULL, NULL, &filtered_range)) {
        return false;
    }
    uint16_t positive_differences = 0u;
    uint16_t negative_differences = 0u;
    for (size_t index = 0u; index + 1u < count; ++index) {
        const int32_t difference = goodix_primitives_nadt_wrapped_difference(
            workspace->filtered[index + 1u], workspace->filtered[index]);
        if (difference > 0) {
            positive_differences = (uint16_t)(positive_differences + 1u);
        } else if (difference < 0) {
            negative_differences = (uint16_t)(negative_differences + 1u);
        }
    }
    int16_t positive_percent = 0;
    const uint32_t signed_difference_count =
        (uint32_t)positive_differences + (uint32_t)negative_differences;
    if (signed_difference_count != 0u) {
        positive_percent = (int16_t)(
            ((uint32_t)positive_differences * UINT32_C(100)) /
            signed_difference_count);
    }
    for (size_t index = 0u; index < count; ++index) {
        workspace->residual[index] = goodix_primitives_nadt_wrapped_difference(
            secondary[index], workspace->filtered[index]);
    }

    if (!goodix_primitives_i32_autocorrelation_transform(
            workspace->residual, workspace->autocorrelation, count,
            0, 10000, autocorrelation_state)) {
        return false;
    }
    uint8_t maximum_count = 0u;
    uint8_t minimum_count = 0u;
    if (!goodix_primitives_i16_local_extrema_indices(
            workspace->autocorrelation, count,
            workspace->extrema_indices,
            GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES / 2u,
            &maximum_count,
            workspace->extrema_indices +
                GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES / 2u,
            GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES / 2u,
            &minimum_count)) {
        return false;
    }
    for (size_t index = 0u; index < minimum_count; ++index) {
        workspace->extrema_indices[(size_t)maximum_count + index] =
            workspace->extrema_indices[
                GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES / 2u + index];
    }
    uint8_t extrema_count = (uint8_t)(maximum_count + minimum_count);
    if (extrema_count != 0u &&
            !goodix_primitives_peak_quality_update(
                workspace->autocorrelation, count,
                workspace->extrema_indices,
                GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES,
                &extrema_count, (int32_t)count, 10000, &quality)) {
        return false;
    }

    uint16_t near_zero_samples = 0u;
    uint16_t current_near_zero_run = 0u;
    uint16_t longest_near_zero_run = 0u;
    for (size_t index = 0u; index < count; ++index) {
        const int32_t magnitude = goodix_primitives_nadt_wrapped_absolute(
            workspace->residual[index]);
        if (magnitude <= configuration->residual_near_zero_threshold) {
            near_zero_samples = (uint16_t)(near_zero_samples + 1u);
            current_near_zero_run = (uint16_t)(current_near_zero_run + 1u);
        } else {
            if (current_near_zero_run > longest_near_zero_run) {
                longest_near_zero_run = current_near_zero_run;
            }
            current_near_zero_run = 0u;
        }
    }
    if (current_near_zero_run > longest_near_zero_run) {
        longest_near_zero_run = current_near_zero_run;
    }
    int32_t residual_range = 0;
    if (!goodix_primitives_i32_range(
            workspace->residual, count, NULL, NULL, &residual_range)) {
        return false;
    }
    int32_t quarter_ranges[GOODIX_PRIMITIVES_NADT_WINDOW_METRIC_COUNT] = {
        100, 100, 100, 100,
    };
    if (count == GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES) {
        for (size_t quarter = 0u;
                quarter < GOODIX_PRIMITIVES_NADT_WINDOW_METRIC_COUNT;
                ++quarter) {
            if (!goodix_primitives_i32_range(
                    workspace->residual + quarter * 25u, 25u,
                    NULL, NULL, &quarter_ranges[quarter])) {
                return false;
            }
        }
    }

    goodix_primitives_extrema_index_counts counts = {0};
    if (!goodix_primitives_collect_extrema_indices(
            workspace->residual, count, residual_range / 3,
            NULL, 0u, NULL, 0u,
            workspace->transition_indices,
            GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES / 2u, &counts)) {
        return false;
    }
    bool periodic_candidate = false;
    bool strong_periodic = false;
    int32_t mean_extrema_amplitude = 0;
    int32_t periodic_rate = 0;
    int32_t interval_variation = 0;
    if (counts.transition_count > 2u) {
        const size_t difference_count = counts.transition_count - 1u;
        int64_t amplitude_sum = 0;
        for (size_t index = 0u; index < difference_count; ++index) {
            const size_t left = (size_t)workspace->transition_indices[index];
            const size_t right =
                (size_t)workspace->transition_indices[index + 1u];
            const int32_t difference = goodix_primitives_nadt_wrapped_absolute(
                goodix_primitives_nadt_wrapped_difference(
                    workspace->residual[right], workspace->residual[left]));
            workspace->extrema_amplitudes[index] = difference;
            amplitude_sum += difference;
        }
        if (!goodix_primitives_nadt_rounded_i32(
                (float)amplitude_sum / (float)difference_count,
                round_provider, &mean_extrema_amplitude)) {
            return false;
        }
        if (mean_extrema_amplitude >=
                configuration->minimum_extrema_amplitude ||
                state->classification_mode != 0u) {
            size_t phase_count = 0u;
            for (size_t index = 0u; index + 2u < counts.transition_count;
                    index += 2u) {
                workspace->phase_gaps[phase_count++] =
                    (int32_t)workspace->transition_indices[index + 2u] -
                    (int32_t)workspace->transition_indices[index];
            }
            for (size_t index = 1u; index + 2u < counts.transition_count;
                    index += 2u) {
                workspace->phase_gaps[phase_count++] =
                    (int32_t)workspace->transition_indices[index + 2u] -
                    (int32_t)workspace->transition_indices[index];
            }
            if (phase_count > 1u) {
                int64_t variation_sum = 0;
                int64_t gap_sum = 0;
                for (size_t index = 0u; index < phase_count; ++index) {
                    gap_sum += workspace->phase_gaps[index];
                    if (index + 1u < phase_count) {
                        variation_sum += goodix_primitives_nadt_wrapped_absolute(
                            goodix_primitives_nadt_wrapped_difference(
                                workspace->phase_gaps[index + 1u],
                                workspace->phase_gaps[index]));
                    }
                }
                interval_variation = (int32_t)(
                    variation_sum / (int64_t)(phase_count - 1u));
                const float mean_gap =
                    (float)gap_sum / (float)phase_count;
                if (mean_gap > 0.0f &&
                        !goodix_primitives_nadt_rounded_i32(
                            1500.0f / mean_gap, round_provider,
                            &periodic_rate)) {
                    return false;
                }
                uint16_t maximum_rate = configuration->maximum_periodic_rate;
                if (counts.transition_count == 3u) {
                    maximum_rate = 80u;
                } else if (mean_extrema_amplitude < 16) {
                    maximum_rate = 120u;
                }
                periodic_candidate =
                    interval_variation <=
                        configuration->maximum_interval_variation &&
                    periodic_rate >
                        (int32_t)configuration->minimum_periodic_rate &&
                    periodic_rate < (int32_t)maximum_rate;
                strong_periodic = periodic_candidate &&
                    interval_variation <=
                        configuration->strong_periodic_variation / 2 &&
                    counts.transition_count > 3u;
            }
        }
    }

    uint32_t primary_deviation = 0u;
    uint32_t secondary_deviation = 0u;
    if (!goodix_primitives_i32_squared_deviation_sum(
            primary, count, round_provider, &primary_deviation) ||
            !goodix_primitives_i32_squared_deviation_sum(
                secondary, count, round_provider, &secondary_deviation)) {
        return false;
    }
    size_t maximum_position = 0u;
    size_t minimum_position = 0u;
    int32_t primary_maximum = primary[0];
    int32_t primary_minimum = primary[0];
    for (size_t index = 1u; index < count; ++index) {
        if (primary[index] > primary_maximum) {
            primary_maximum = primary[index];
            maximum_position = index;
        }
        if (primary[index] < primary_minimum) {
            primary_minimum = primary[index];
            minimum_position = index;
        }
    }

    uint8_t *const counters = state->transient_counters;
    if (state->classification_mode == 0u) {
        bool trend_gate = false;
        if (positive_differences >= configuration->trend_count_threshold &&
                negative_differences >= configuration->trend_count_threshold &&
                ((uint16_t)positive_percent >=
                     configuration->trend_percent_threshold ||
                 positive_percent <= (int16_t)(
                     UINT16_C(100) -
                     configuration->trend_percent_threshold)) &&
                filtered_range >
                    configuration->filtered_range_lower_threshold) {
            trend_gate = true;
        }
        if (!configuration->trend_gate_enabled) {
            trend_gate = true;
        }
        const uint32_t secondary_denominator =
            secondary_deviation == 0u ? 1u : secondary_deviation;
        const bool deviation_gate =
            primary_deviation / secondary_denominator > 1u &&
            secondary_deviation > 10u;
        const bool cadence_met =
            transition_count >= (uint32_t)(cadence_threshold < 0
                ? 0 : cadence_threshold);
        const bool counter_zero_evidence =
            cadence_met && !strong_periodic && trend_gate && deviation_gate &&
            residual_range >
                (int32_t)configuration->raw_residual_threshold;
        counters[0] = counter_zero_evidence
            ? goodix_primitives_nadt_increment_u8(counters[0]) : 0u;

        const bool near_zero_evidence =
            near_zero_samples >= configuration->minimum_near_zero_samples &&
            longest_near_zero_run >= configuration->minimum_near_zero_run &&
            !strong_periodic && state->profile == 0u;
        counters[1] = near_zero_evidence
            ? goodix_primitives_nadt_increment_u8(counters[1]) : 0u;

        const bool deviation_ratio_evidence =
            cadence_met &&
            primary_deviation / secondary_denominator >=
                configuration->deviation_ratio_threshold &&
            secondary_deviation >= 101u &&
            filtered_range <=
                configuration->filtered_range_upper_threshold &&
            state->profile == 0u;
        counters[2] = deviation_ratio_evidence
            ? goodix_primitives_nadt_increment_u8(counters[2]) : 0u;
        counters[3] = residual_range <=
                (int32_t)configuration->raw_residual_threshold
            ? goodix_primitives_nadt_increment_u8(counters[3]) : 0u;
    } else {
        uint8_t quiet_quarters = 0u;
        if (state->profile == 0u) {
            for (size_t quarter = 0u;
                    quarter < GOODIX_PRIMITIVES_NADT_WINDOW_METRIC_COUNT;
                    ++quarter) {
                if (quarter_ranges[quarter] <=
                        (int32_t)configuration->quiet_quarter_range_threshold) {
                    quiet_quarters = (uint8_t)(quiet_quarters + 1u);
                }
            }
        }
        uint16_t active_threshold =
            configuration->mode_zero_activity_threshold;
        if (activity_span > configuration->activity_span_threshold &&
                state->profile != 1u) {
            active_threshold = configuration->alternate_residual_threshold;
        }
        const bool trigger_family =
            state->trigger_windows[0] == 25u ||
            state->trigger_windows[1] == 25u ||
            (state->trigger_windows[2] == 25u &&
             state->energy_metric <=
                 configuration->trigger_energy_threshold / 2) ||
            state->trigger_windows[3] == 25u;
        const bool counter_zero_evidence =
            residual_range > (int32_t)active_threshold &&
            !strong_periodic &&
            (trigger_family || state->profile == 0u);
        counters[0] = counter_zero_evidence
            ? goodix_primitives_nadt_increment_u8(counters[0]) : 0u;
        int32_t peak_position_delta = (int32_t)maximum_position -
            (int32_t)minimum_position;
        if (peak_position_delta < 0) {
            peak_position_delta = -peak_position_delta;
        }
        const bool counter_one_evidence =
            near_zero_samples >= configuration->minimum_near_zero_samples &&
            longest_near_zero_run >= configuration->minimum_near_zero_run &&
            !strong_periodic && primary_maximum - primary_minimum >= 201 &&
            peak_position_delta <= 2 && trigger_family &&
            (state->profile == 0u ||
             (state->profile == 2u && state->profile_counter <= 2));
        counters[1] = counter_one_evidence
            ? goodix_primitives_nadt_increment_u8(counters[1]) : 0u;
        counters[3] = residual_range <=
                    (int32_t)configuration->quiet_quarter_range_threshold &&
                !strong_periodic &&
                quality < (uint8_t)(configuration->quality_gate * 3u / 2u) &&
                count > 25u && quiet_quarters >=
                    (uint8_t)configuration->quiet_quarter_range_threshold
            ? goodix_primitives_nadt_increment_u8(counters[3]) : 0u;
    }

    const uint16_t reset_threshold = state->classification_mode == 0u
        ? configuration->mode_zero_residual_threshold
        : configuration->mode_one_residual_threshold;
    if (residual_range > (int32_t)reset_threshold) {
        for (size_t index = 0u; index < 4u; ++index) {
            counters[index] = 0u;
        }
    }
    if (counters[0] != 0u || counters[3] != 0u) {
        quality = (uint8_t)(quality % 10u + 1u);
    }
    if (counters[1] != 0u || counters[2] != 0u) {
        quality = (uint8_t)(quality >> 1u);
    }
    state->quality = quality;

    if (!state->classifier_suppressed && configuration->classifier_level > 1u) {
        uint8_t transition_windows = configuration->base_transition_windows;
        if (state->profile == 2u) {
            transition_windows = (uint8_t)(transition_windows +
                (state->profile_counter < 3 ? 2u : 4u));
        } else if (state->profile == 1u) {
            transition_windows = 15u;
        }
        if (state->classification_mode == 0u &&
                (counters[0] >= transition_windows ||
                 counters[1] >= transition_windows ||
                 counters[2] >= transition_windows)) {
            classified = 3u;
            state->classification_latched = true;
            counters[0] = 0u;
            state->stationary_latch = 0u;
            counters[1] = 0u;
            counters[2] = 0u;
        } else if (state->classification_mode != 0u &&
                counters[3] >= (state->classifier_suppressed
                    ? 20u : configuration->base_transition_windows)) {
            classified = 3u;
            state->classification_latched = true;
            for (size_t index = 0u; index < 4u; ++index) {
                counters[index] = 0u;
            }
            state->stationary_latch = 0u;
        }
    }

    bool periodic_hold = false;
    if (strong_periodic) {
        periodic_hold = periodic_candidate && residual_range > 10 &&
            residual_range < 1000 && quality > configuration->quality_gate;
        if (state->classification_mode == 1u) {
            periodic_hold = quality > configuration->quality_gate &&
                activity_span <= 2;
        }
    }
    state->stationary_latch = periodic_hold
        ? goodix_primitives_nadt_increment_u8(state->stationary_latch) : 0u;
    if (state->stationary_latch >= configuration->stable_hold_windows &&
            count > 50u) {
        classified = 1u;
        counters[0] = 0u;
        counters[1] = 0u;
        state->stationary_latch = 0u;
    }
    const bool strong_quality = strong_periodic && residual_range > 30 &&
        quality > 80u;
    state->rate = quality;
    state->current_result = classified & UINT8_C(3);
    *result = (uint8_t)(classified | (strong_quality ? UINT8_C(4) : 0u));

    if (diagnostics != NULL) {
        diagnostics->transition_count = transition_count;
        diagnostics->normalized_residual_range =
            (residual_range / 15) * 1000;
        diagnostics->positive_difference_percent = positive_percent;
        diagnostics->filtered_range = filtered_range;
        diagnostics->periodic_rate = periodic_rate;
        diagnostics->interval_variation = interval_variation;
        diagnostics->periodic_candidate = periodic_candidate;
        diagnostics->strong_periodic = strong_periodic;
        diagnostics->input_quality = input_quality;
        diagnostics->output_quality = quality;
        diagnostics->near_zero_samples = near_zero_samples;
        diagnostics->longest_near_zero_run = longest_near_zero_run;
        for (size_t index = 0u;
                index < GOODIX_PRIMITIVES_NADT_WINDOW_METRIC_COUNT; ++index) {
            diagnostics->quarter_ranges[index] = quarter_ranges[index];
        }
    }
    return true;
}

static bool goodix_primitives_nadt_energy_metric(
    const goodix_primitives_nadt_window_configuration *configuration,
    goodix_primitives_double_unary_fn square_root,
    int32_t *maximum, int32_t *minimum, int32_t *metric) {
    float sum = 0.0f;
    *maximum = configuration->window_maxima[0];
    *minimum = configuration->window_minima[0];
    for (size_t index = 0u; index < configuration->window_count; ++index) {
        sum += configuration->window_metrics[index];
        if (configuration->window_maxima[index] > *maximum) {
            *maximum = configuration->window_maxima[index];
        }
        if (configuration->window_minima[index] < *minimum) {
            *minimum = configuration->window_minima[index];
        }
    }
    const uint32_t divisor = configuration->window_count == 0u
        ? UINT32_C(1) : configuration->window_count;
    const float normalized = (sum / (float)divisor) / 24.0f;
    const double scaled = square_root((double)normalized) * 64.0;
    if (!(scaled >= 0.0) || scaled >= 2147483647.5) {
        return false;
    }
    /* 0x3AC88 is the stock double round operation; sqrt makes this path
     * non-negative, so adding one half preserves its away-from-zero tie. */
    *metric = (int32_t)(scaled + 0.5);
    return true;
}

static bool goodix_primitives_nadt_trigger_family(
    const goodix_primitives_nadt_window_configuration *configuration,
    const goodix_primitives_nadt_window_state *state,
    bool high_variation) {
    return (state->trigger_windows[0] == 25u ||
            state->trigger_windows[1] == 25u ||
            (state->trigger_windows[2] == 25u &&
             state->energy_metric <= configuration->metric_threshold / 2) ||
            state->trigger_windows[3] == 25u) &&
        !high_variation;
}

static void goodix_primitives_nadt_update_evidence_streak(
    goodix_primitives_nadt_window_state *state, bool trigger_family,
    bool cap_required, int32_t range) {
    bool admitted = trigger_family;
    if (admitted && cap_required) {
        admitted = (uint32_t)(range - INT32_C(31)) <= UINT32_C(968) &&
            state->rate < 75u;
    }
    if (admitted && state->axis_ratio_streak == 0u) {
        state->evidence_streak = (uint8_t)(state->evidence_streak + 1u);
    } else {
        state->evidence_streak = 0u;
    }
}

bool goodix_primitives_nadt_window_classify(
    const goodix_primitives_nadt_window_configuration *configuration,
    const goodix_primitives_nadt_window_input *input,
    const goodix_primitives_nadt_window_plan *plan,
    goodix_primitives_nadt_window_state *state,
    goodix_primitives_nadt_window_diagnostics *diagnostics,
    int32_t *result) {
    if (configuration == NULL || input == NULL || plan == NULL ||
            state == NULL || result == NULL ||
            configuration->window_count >
                GOODIX_PRIMITIVES_NADT_WINDOW_METRIC_COUNT ||
            plan->classify_primary == NULL ||
            plan->classify_auxiliary == NULL ||
            plan->classify_alternate == NULL || plan->square_root == NULL) {
        return false;
    }
    if (input->sample_count == 100 &&
            (input->tail_samples == NULL || input->tail_sample_count < 100u)) {
        return false;
    }
    if (state->range_cursor >= 50) {
        const size_t cursor = (size_t)state->range_cursor;
        if (input->range_samples == NULL ||
                input->range_sample_count < cursor) {
            return false;
        }
    }

    int32_t maximum;
    int32_t minimum;
    int32_t energy_metric;
    if (!goodix_primitives_nadt_energy_metric(
            configuration, plan->square_root,
            &maximum, &minimum, &energy_metric)) {
        return false;
    }
    state->energy_metric = energy_metric;
    int32_t classified = state->current_result;

    if (input->sample_count == 100) {
        uint8_t nonzero_count = 0u;
        for (size_t index = 50u; index < 100u; ++index) {
            if (input->tail_samples[index] != 0) {
                ++nonzero_count;
            }
        }
        if (nonzero_count >= configuration->minimum_nonzero_tail_samples) {
            state->elapsed_windows = 0u;
        }
    }

    const int32_t numerator = goodix_primitives_wrapped_add_i32(
        goodix_primitives_wrapped_square(input->axis_y),
        goodix_primitives_wrapped_square(input->axis_x));
    float axis_ratio = 300.0f;
    if (input->axis_z != 0) {
        const int32_t denominator =
            goodix_primitives_wrapped_square(input->axis_z);
        axis_ratio = (float)numerator / (float)denominator;
    }
    const uint32_t ratio_bits = goodix_primitives_float_bits(axis_ratio);
    if (ratio_bits + UINT32_C(0xC26CF41F) < UINT32_C(0x03CBCD37)) {
        state->axis_ratio_outside_band_windows = 0u;
    } else {
        state->axis_ratio_outside_band_windows = (uint16_t)(
            state->axis_ratio_outside_band_windows + 1u);
    }

    const int32_t spread = goodix_primitives_nadt_wrapped_difference(
        maximum, minimum);
    const bool high_variation =
        configuration->metric_threshold < energy_metric &&
        configuration->spread_threshold < spread;
    if (high_variation) {
        state->inactive_windows = 0;
    } else {
        state->inactive_windows = goodix_primitives_u32_as_i32(
            (uint32_t)state->inactive_windows + UINT32_C(1));
    }

    uint8_t primary = 0u;
    if (input->sample_count > 0) {
        primary = plan->classify_primary(
            plan->primary_context, input->primary_source,
            input->secondary_source, input->sample_count);
    }

    int32_t auxiliary = 0;
    if (high_variation) {
        for (size_t index = 0u; index < 4u; ++index) {
            state->transient_counters[index] = 0u;
        }
        classified = state->current_result;
        if (diagnostics != NULL) {
            diagnostics->high_variation = true;
            diagnostics->primary_classification = 0u;
            diagnostics->auxiliary_classification = 0u;
            diagnostics->alternate_classification = 0u;
        }
    } else {
        primary &= UINT8_C(3);
        auxiliary = plan->classify_auxiliary(
            plan->auxiliary_context,
            state->axis_ratio_outside_band_windows);
        if (state->elapsed_windows > configuration->elapsed_window_limit &&
                state->axis_ratio_outside_band_windows == 0u) {
            const uint8_t base = configuration->base_transition_windows;
            if ((state->transient_counters[3] >= base &&
                    !state->classifier_suppressed) ||
                    (state->transient_counters[3] >=
                         (uint8_t)(base + 4u) &&
                     state->classifier_suppressed)) {
                classified = 3;
                state->transient_counters[3] = 0u;
            }
            state->transient_counters[0] = 0u;
            state->transient_counters[1] = 0u;
            state->transient_counters[2] = 0u;
        } else {
            if (primary == 1u) {
                classified = 1;
            }
            if (auxiliary == 2) {
                classified = 2;
            }
            if (primary == 3u) {
                classified = 3;
            }
            state->elapsed_windows = (uint16_t)(state->elapsed_windows + 1u);
        }
        if (diagnostics != NULL) {
            diagnostics->high_variation = false;
            diagnostics->primary_classification = primary;
            diagnostics->auxiliary_classification = (uint8_t)auxiliary;
        }
    }

    if ((classified == 0 || classified == 1) &&
            !state->classifier_suppressed &&
            configuration->alternate_classifier_level > 2u) {
        if (!high_variation) {
            const int32_t alternate = plan->classify_alternate(
                plan->alternate_context);
            if (alternate == 2) {
                classified = 2;
            }
            if (diagnostics != NULL) {
                diagnostics->alternate_classification = (uint8_t)alternate;
            }
        }
    } else if (state->alternate_probe_enabled) {
        const int32_t alternate = plan->classify_alternate(
            plan->alternate_context);
        if (diagnostics != NULL) {
            diagnostics->alternate_classification = (uint8_t)alternate;
        }
    }

    if (classified == 0 && input->sample_count >= 26 &&
            !state->classifier_suppressed) {
        int32_t range = 0;
        if (state->range_cursor >= 50) {
            const size_t cursor = (size_t)state->range_cursor;
            const int16_t *const values = input->range_samples +
                (cursor - GOODIX_PRIMITIVES_NADT_WINDOW_RANGE_VALUES);
            int16_t range_maximum = values[0];
            int16_t range_minimum = values[0];
            for (size_t index = 0u;
                    index < GOODIX_PRIMITIVES_NADT_WINDOW_RANGE_VALUES;
                    ++index) {
                if (values[index] >= range_maximum) {
                    range_maximum = values[index];
                }
                if (values[index] <= range_minimum) {
                    range_minimum = values[index];
                }
            }
            range = goodix_primitives_u16_bits_to_i16((uint16_t)(
                (uint16_t)range_maximum - (uint16_t)range_minimum));
        }

        const int32_t signed_ratio_bits =
            goodix_primitives_u32_as_i32(ratio_bits);
        const bool ratio_in_motion_band =
            signed_ratio_bits > INT32_C(0x3C23D70A) &&
            signed_ratio_bits < INT32_C(0x43610000);
        const bool ratio_streak = state->rate >= 90u ||
            (state->rate >= 80u && ratio_in_motion_band) ||
            (state->rate >= 70u && ratio_in_motion_band &&
             state->long_window_score >= 20 && state->profile != 1u);
        state->axis_ratio_streak = ratio_streak
            ? (uint8_t)(state->axis_ratio_streak + 1u) : 0u;

        const bool trigger_family = goodix_primitives_nadt_trigger_family(
            configuration, state, high_variation);
        if (state->classification_mode == 0u) {
            const bool cap_required =
                (state->long_window_score < 66 || range < 21 ||
                 state->rate > 14u) &&
                (state->rate > 30u || range < 6 || state->profile == 1u);
            goodix_primitives_nadt_update_evidence_streak(
                state, trigger_family, cap_required, range);
        } else if (state->classification_mode == 1u) {
            const bool cap_required = state->long_window_score < 61 ||
                range < 21 || state->rate > 14u;
            goodix_primitives_nadt_update_evidence_streak(
                state, trigger_family, cap_required, range);
        }

        const int32_t absolute_x =
            goodix_primitives_nadt_wrapped_absolute(input->axis_x);
        const int32_t absolute_y =
            goodix_primitives_nadt_wrapped_absolute(input->axis_y);
        const int32_t absolute_z =
            goodix_primitives_nadt_wrapped_absolute(input->axis_z);
        if ((absolute_z < 2 || (absolute_y < 2 && absolute_x < 2)) &&
                (state->rate < 75u || input->sample_count < 100)) {
            state->stationary_latch = 0u;
        }

        if (state->axis_ratio_streak >=
                configuration->axis_ratio_streak_limit) {
            state->axis_ratio_streak = 0u;
            state->evidence_streak = 0u;
            classified = 1;
            state->fallback_streak = 0u;
        }

        uint8_t mode_zero_threshold = (uint8_t)(
            configuration->base_transition_windows + 2u);
        uint8_t mode_one_threshold = mode_zero_threshold;
        if (state->profile == 2u) {
            if (state->profile_counter < 3) {
                mode_one_threshold = 10u;
                mode_zero_threshold = (uint8_t)(
                    configuration->base_transition_windows + 2u);
            } else {
                mode_one_threshold = 15u;
                mode_zero_threshold = (uint8_t)(
                    configuration->base_transition_windows + 4u);
            }
        } else if (state->profile == 1u) {
            mode_one_threshold = 25u;
            mode_zero_threshold = 15u;
        }

        bool evidence_transition = false;
        if (state->classification_mode == 0u) {
            evidence_transition =
                state->evidence_streak >= mode_zero_threshold ||
                state->fallback_streak >= 10u;
        } else if (state->classification_mode == 1u) {
            evidence_transition =
                state->evidence_streak >= mode_one_threshold ||
                state->fallback_streak >= 10u;
        }
        if (evidence_transition) {
            state->evidence_streak = 0u;
            classified = 2;
            state->fallback_streak = 0u;
        }
    }

    if (diagnostics != NULL) {
        diagnostics->energy_metric = energy_metric;
    }
    *result = classified;
    return true;
}

bool goodix_primitives_spo2_spectral_peak_concentration_db(
    const float *spectrum, size_t count, size_t radius,
    goodix_primitives_float_unary_fn logarithm_base_10,
    float *concentration_db, float *peak_index) {
    if (spectrum == NULL || logarithm_base_10 == NULL ||
            concentration_db == NULL || peak_index == NULL ||
            count < 4u || count > 255u || radius > 127u) {
        return false;
    }

    size_t strongest_index = 0u;
    float strongest_value = 0.0f;
    float interior_energy = 0.0f;
    size_t interior_count = 0u;
    for (size_t index = 1u; index < count - 2u; ++index) {
        const float value = spectrum[index];
        if (value > spectrum[index - 1u] &&
                value > spectrum[index + 1u] &&
                value > strongest_value) {
            strongest_index = index;
            strongest_value = value;
        }
        interior_energy += value * value;
        ++interior_count;
    }
    if (interior_count == 0u) {
        interior_count = 1u;
    }
    const float mean_energy = interior_energy / (float)interior_count;

    const size_t first_start = strongest_index > radius
        ? strongest_index - radius : 0u;
    size_t first_end = strongest_index + radius;
    if (first_end >= count) {
        first_end = count - 1u;
    }
    float local_energy = 0.0f;
    for (size_t index = first_start; index <= first_end; ++index) {
        local_energy += spectrum[index] * spectrum[index];
    }

    const bool include_harmonic =
        strongest_index >= 31u && strongest_index <= 56u;
    if (include_harmonic) {
        const size_t doubled_index = strongest_index * 2u;
        const size_t second_start = doubled_index > radius
            ? doubled_index - radius : 0u;
        size_t second_end = doubled_index + radius;
        if (second_end >= count) {
            second_end = count - 1u;
        }
        for (size_t index = second_start; index <= second_end; ++index) {
            local_energy += spectrum[index] * spectrum[index];
        }
    }

    const float window_width = (float)(radius * 2u + 1u);
    float expected_energy = window_width * mean_energy;
    if (include_harmonic) {
        expected_energy += window_width * mean_energy;
    }
    *concentration_db = 0.0f;
    *peak_index = (float)strongest_index;
    if (goodix_primitives_u32_as_i32(
            goodix_primitives_float_bits(expected_energy)) >
            INT32_C(0x322BCC77)) {
        const float ratio = local_energy / expected_energy;
        if (goodix_primitives_u32_as_i32(
                goodix_primitives_float_bits(ratio)) >=
                INT32_C(0x3DCCCCCD) && strongest_index != 0u) {
            *concentration_db = logarithm_base_10(ratio) * 10.0f;
        }
    }
    return true;
}

static bool goodix_primitives_spo2_analyzer_byte_window_valid(
    const goodix_primitives_byte_window *window) {
    return window != NULL && window->values != NULL &&
           window->capacity != 0u && window->count <= window->capacity &&
           window->cursor < window->capacity;
}

static bool goodix_primitives_spo2_analyzer_float_window_valid(
    const goodix_primitives_decimated_float_window *window) {
    return window != NULL && window->values != NULL &&
           window->capacity != 0u && window->count <= window->capacity &&
           window->cursor < window->capacity && window->period != 0u &&
           window->phase < window->period;
}

static uint8_t goodix_primitives_spo2_candidate_from_bin(uint32_t bin) {
    float scaled = (float)bin * 60.0f;
    scaled *= 25.0f;
    scaled /= 3.0f;
    scaled *= 0x1p-8f;
    return (uint8_t)(uint32_t)scaled;
}

bool goodix_primitives_spo2_report_analyze(
    const goodix_primitives_spo2_report_analyzer_input *input,
    goodix_primitives_spo2_report_analyzer_state *state,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_float_unary_fn logarithm_base_10,
    goodix_primitives_spo2_report_analysis *analysis) {
    if (input == NULL || state == NULL || square_root == NULL ||
            logarithm_base_10 == NULL || analysis == NULL ||
            input->primary_spectrum == NULL ||
            input->primary_spectrum_count < 349u ||
            input->secondary_spectrum == NULL ||
            input->secondary_spectrum_count < 93u ||
            !goodix_primitives_spo2_analyzer_byte_window_valid(
                &state->primary_candidates) ||
            !goodix_primitives_spo2_analyzer_float_window_valid(
                &state->concentrations) ||
            !goodix_primitives_spo2_analyzer_byte_window_valid(
                &state->reference_candidates) ||
            !goodix_primitives_spo2_analyzer_float_window_valid(
                &state->metric_history)) {
        return false;
    }
    const size_t next_primary_count = state->primary_candidates.count <
            state->primary_candidates.capacity
        ? (size_t)state->primary_candidates.count + 1u
        : (size_t)state->primary_candidates.capacity;
    const size_t next_concentration_count =
        state->concentrations.phase == 0u &&
                state->concentrations.count < state->concentrations.capacity
            ? (size_t)state->concentrations.count + 1u
            : (size_t)state->concentrations.count;
    const size_t next_reference_count = state->reference_candidates.count <
            state->reference_candidates.capacity
        ? (size_t)state->reference_candidates.count + 1u
        : (size_t)state->reference_candidates.capacity;
    if (next_primary_count == state->primary_candidates.capacity &&
            (next_concentration_count < next_primary_count ||
             next_reference_count < next_primary_count)) {
        return false;
    }
    uint8_t *analysis_bytes = (uint8_t *)analysis;
    for (size_t index = 0u; index < sizeof(*analysis); ++index) {
        analysis_bytes[index] = 0u;
    }

    float peak = 0.0f;
    uint32_t peak_index = 0u;
    if (!goodix_primitives_strict_local_peak_max(
            input->primary_spectrum + 15u, 78u, &peak, &peak_index)) {
        return false;
    }
    analysis->primary_candidate =
        goodix_primitives_spo2_candidate_from_bin(peak_index + 15u);
    if (!goodix_primitives_strict_local_peak_max(
            input->secondary_spectrum + 15u, 78u, &peak, &peak_index)) {
        return false;
    }
    analysis->secondary_candidate =
        goodix_primitives_spo2_candidate_from_bin(peak_index + 15u);
    if (!goodix_primitives_strict_local_peak_max(
            input->primary_spectrum + 271u, 78u, &peak, &peak_index)) {
        return false;
    }
    analysis->spectral_candidate =
        goodix_primitives_spo2_candidate_from_bin(peak_index + 15u);

    float spectral_peak = 0.0f;
    if (!goodix_primitives_spo2_spectral_peak_concentration_db(
            input->primary_spectrum, 128u, 2u, logarithm_base_10,
            &analysis->spectral_concentration, &spectral_peak) ||
            !goodix_primitives_byte_window_push(
                &state->primary_candidates, analysis->primary_candidate) ||
            !goodix_primitives_decimated_float_window_push(
                &state->concentrations,
                analysis->spectral_concentration) ||
            !goodix_primitives_decimated_float_window_push(
                &state->metric_history, input->metrics[3]) ||
            !goodix_primitives_byte_window_push(
                &state->reference_candidates,
                input->reference_candidate)) {
        return false;
    }
    (void)spectral_peak;

    const bool history_full = state->primary_candidates.count ==
                              state->primary_candidates.capacity;
    if (history_full) {
        if (!goodix_primitives_u8_population_standard_deviation(
                state->primary_candidates.values,
                state->primary_candidates.count, square_root,
                &analysis->score)) {
            return false;
        }
        if (state->concentrations.count != 0u) {
            const goodix_primitives_float_buffer concentration_buffer = {
                .values = state->concentrations.values,
                .count = state->concentrations.count,
                .capacity = state->concentrations.capacity,
            };
            if (!goodix_primitives_float_buffer_incremental_standard_deviation(
                    &concentration_buffer, square_root,
                    &analysis->concentration_deviation)) {
                return false;
            }
        }
        if (state->metric_history.count != 0u) {
            (void)goodix_primitives_float_window_mean(
                &state->metric_history, &analysis->metric_mean);
        }
    }

    const uint32_t primary = analysis->primary_candidate;
    if ((primary - (uint32_t)analysis->spectral_candidate + 8u) < 17u) {
        analysis->primary_spectral_proximity = 1u;
    }
    bool harmonic_consistent = false;
    if (primary < 50u) {
        const uint32_t base_bin =
            (uint32_t)((float)primary / 0x1.f4p+0f);
        const size_t first_start = (size_t)base_bin + 5u;
        const size_t first_count = 93u - first_start;
        if (!goodix_primitives_strict_local_peak_max(
                input->primary_spectrum + first_start, first_count,
                &peak, &peak_index)) {
            return false;
        }
        analysis->first_harmonic_candidate =
            goodix_primitives_spo2_candidate_from_bin(
                peak_index + base_bin + 4u);
        const size_t second_start = (size_t)base_bin * 2u + 5u;
        const size_t second_count = 93u - second_start;
        if (!goodix_primitives_strict_local_peak_max(
                input->primary_spectrum + second_start, second_count,
                &peak, &peak_index)) {
            return false;
        }
        analysis->second_harmonic_candidate =
            goodix_primitives_spo2_candidate_from_bin(
                peak_index + base_bin * 2u + 4u);
        if (((uint32_t)analysis->first_harmonic_candidate - primary * 2u +
                 6u) < 13u) {
            if (((uint32_t)analysis->second_harmonic_candidate - primary * 3u +
                    8u) < 17u) {
                analysis->harmonic_consistency = 1u;
            }
            harmonic_consistent = true;
        }
    }

    if (history_full) {
        const int32_t mean_bits = goodix_primitives_u32_as_i32(
            goodix_primitives_float_bits(analysis->metric_mean));
        if (mean_bits < INT32_C(0x40800000)) {
            analysis->phase_gate = 1u;
        } else {
            const uint32_t adjusted = (uint32_t)mean_bits +
                                      UINT32_C(0xBF7FFFFF);
            if (adjusted < UINT32_C(0x0247FFFF)) {
                analysis->phase_gate = 2u;
            } else if (mean_bits > INT32_C(0x42C80000)) {
                analysis->phase_gate = 3u;
            }
        }
        const size_t count = state->primary_candidates.count;
        for (size_t index = 0u; index < count; ++index) {
            const int32_t concentration_bits = goodix_primitives_u32_as_i32(
                goodix_primitives_float_bits(state->concentrations.values[index]));
            if (concentration_bits >= INT32_C(0x40E00000)) {
                analysis->acceptance_gate =
                    (uint8_t)(analysis->acceptance_gate + 1u);
            }
            if (concentration_bits >= INT32_C(0x40A00000)) {
                analysis->paired_gate_a =
                    (uint8_t)(analysis->paired_gate_a + 1u);
            }
        }
        for (size_t index = 0u; index < count; ++index) {
            const uint32_t difference =
                (uint32_t)state->reference_candidates.values[index] -
                (uint32_t)state->primary_candidates.values[index];
            if (difference + 2u < 5u) {
                analysis->paired_gate_b =
                    (uint8_t)(analysis->paired_gate_b + 1u);
            }
            if (goodix_primitives_u32_as_i32(difference) > 19) {
                analysis->activation_gate =
                    (uint8_t)(analysis->activation_gate + 1u);
            }
            if (difference + 10u < 21u) {
                analysis->hold_gate =
                    (uint8_t)(analysis->hold_gate + 1u);
            }
        }
    }

    state->primary_spectral_streak = analysis->primary_spectral_proximity == 1u
        ? (uint8_t)(state->primary_spectral_streak + 1u) : 0u;
    state->harmonic_streak = harmonic_consistent
        ? (uint8_t)(state->harmonic_streak + 1u) : 0u;
    if (state->previous_primary_candidate != 0u &&
            ((uint32_t)state->previous_primary_candidate - primary + 2u) < 5u &&
            state->reference_limit <= 50u) {
        state->stable_primary_streak =
            (uint8_t)(state->stable_primary_streak + 1u);
    } else {
        state->stable_primary_streak = 0u;
    }
    analysis->metrics_below_four =
        goodix_primitives_u32_as_i32(
            goodix_primitives_float_bits(input->metrics[0])) <
                INT32_C(0x40800000) &&
        goodix_primitives_u32_as_i32(
            goodix_primitives_float_bits(input->metrics[1])) <
                INT32_C(0x40800000) &&
        goodix_primitives_u32_as_i32(
            goodix_primitives_float_bits(input->metrics[2])) <
                INT32_C(0x40800000) &&
        goodix_primitives_u32_as_i32(
            goodix_primitives_float_bits(input->metrics[3])) <
                INT32_C(0x40800000);
    state->previous_primary_candidate = analysis->primary_candidate;

    const uint32_t secondary = analysis->secondary_candidate;
    if (secondary - 31u < 19u &&
            ((primary - secondary + 4u) < 9u ||
             (primary - secondary * 2u + 6u) < 13u ||
             (primary - secondary * 3u + 8u) < 17u)) {
        analysis->secondary_consistency = 1u;
    }
    return true;
}

bool goodix_primitives_spo2_report_state_update(
    goodix_primitives_spo2_report_state *state,
    uint32_t selected_value, int32_t reference_value,
    goodix_primitives_spo2_report_output *output,
    goodix_primitives_spo2_report_analyze_fn analyze, void *analyze_context) {
    enum { HISTORY_COPY_BYTES = 512 };
    if (state == NULL || output == NULL || analyze == NULL) {
        return false;
    }
    uint8_t *analysis_bytes = (uint8_t *)&output->analysis;
    for (size_t index = 0u; index < sizeof(output->analysis); ++index) {
        analysis_bytes[index] = 0u;
    }
    analyze(analyze_context, &output->analysis);

    if (state->history_shift_a && state->history_shift_b) {
        if (state->history_destination == NULL ||
                state->history_source == NULL ||
                state->history_destination_capacity < HISTORY_COPY_BYTES ||
                state->history_source_capacity < HISTORY_COPY_BYTES) {
            return false;
        }
        for (size_t index = 0u; index < HISTORY_COPY_BYTES; ++index) {
            state->history_destination[index] = state->history_source[index];
        }
        state->use_secondary_candidate = true;
    } else {
        state->use_secondary_candidate = false;
    }
    if (state->accepted) {
        return true;
    }

    const goodix_primitives_spo2_report_analysis *analysis =
        &output->analysis;
    const bool acceptance_quality = analysis->acceptance_gate >= 3u ||
        (analysis->paired_gate_b >= 3u && analysis->paired_gate_a >= 3u);
    const bool score_below_five = goodix_primitives_u32_as_i32(
        goodix_primitives_float_bits(analysis->score)) <
        INT32_C(0x40A00000);
    if (acceptance_quality && score_below_five) {
        const uint8_t candidate = state->use_secondary_candidate
            ? analysis->secondary_candidate : analysis->primary_candidate;
        int32_t difference = goodix_primitives_u32_as_i32(
            (uint32_t)reference_value - (uint32_t)candidate);
        if (difference < 0) {
            difference = goodix_primitives_u32_as_i32(
                UINT32_C(0) - (uint32_t)difference);
        }
        if (difference < 6) {
            if (selected_value < state->minimum_selected_value) {
                selected_value = state->minimum_selected_value;
            }
            output->selected_value = (uint8_t)selected_value;
            state->accepted = true;
            state->event = 0u;
            return true;
        }
    }

    bool event = false;
    if (state->phase == 0u) {
        const bool score_below_two = goodix_primitives_u32_as_i32(
            goodix_primitives_float_bits(analysis->score)) <
            INT32_C(0x40000000);
        if (analysis->activation_gate >= 3u && score_below_two &&
                analysis->acceptance_gate >= 3u &&
                analysis->phase_gate == 1u && reference_value <= 100 &&
                analysis->primary_candidate <= 50u) {
            state->phase = 1u;
            event = true;
        }
    } else if (state->phase == 1u) {
        if (analysis->hold_gate < 3u &&
                (analysis->primary_candidate <= 50u ||
                 analysis->phase_gate <= 1u)) {
            event = true;
        } else {
            state->phase = 2u;
        }
    } else if (state->phase == 2u) {
        state->phase = 0u;
    }
    state->event = (uint8_t)event;
    if (event && state->event_seen == 0u) {
        state->event_seen = 1u;
    }
    return true;
}

bool goodix_primitives_spo2_packed_channel_standard_deviations(
    const goodix_primitives_packed_u16_span channels[4],
    float output[4], float *scratch, size_t scratch_capacity,
    goodix_primitives_float_unary_fn square_root) {
    enum { STOCK_SCRATCH_FLOATS = 60 };
    if (channels == NULL || output == NULL || scratch == NULL ||
            square_root == NULL || scratch_capacity < STOCK_SCRATCH_FLOATS) {
        return false;
    }
    for (size_t channel = 0u; channel < 4u; ++channel) {
        const size_t maximum_count = channel < 3u
            ? STOCK_SCRATCH_FLOATS * 3u : STOCK_SCRATCH_FLOATS;
        if (channels[channel].count > maximum_count ||
                (channels[channel].count != 0u &&
                 channels[channel].values == NULL)) {
            return false;
        }
    }

    for (size_t channel = 0u; channel < 4u; ++channel) {
        const size_t step = channel < 3u ? 3u : 1u;
        size_t scratch_count = 0u;
        for (size_t index = 0u; index < channels[channel].count;
                index += step) {
            scratch[scratch_count++] = goodix_primitives_float_from_bits(
                goodix_primitives_packed_6_9_to_f32_bits(
                    channels[channel].values[index]));
        }
        if (!goodix_primitives_population_standard_deviation_or_zero(
                scratch, scratch_count, square_root, &output[channel])) {
            return false;
        }
    }
    return true;
}

static bool goodix_primitives_msb_first_bit(
    const uint8_t *bytes, size_t bit_index) {
    return ((bytes[bit_index / 8u] >> (7u - bit_index % 8u)) & 1u) != 0u;
}

static bool goodix_primitives_spo2_channel_scale_pair(
    const goodix_primitives_spo2_channel_scaling *scaling,
    uint8_t channel, uint16_t group, float destination[2]) {
    if (scaling == NULL || destination == NULL ||
            scaling->encoded_values == NULL || scaling->divisors == NULL ||
            channel >= scaling->channel_count ||
            (size_t)group > SIZE_MAX / (size_t)scaling->channel_count) {
        return false;
    }
    const size_t index = (size_t)group * (size_t)scaling->channel_count +
        (size_t)channel;
    if (index >= scaling->encoded_value_count ||
            index >= scaling->divisor_count) {
        return false;
    }

    float first = 0.0f;
    float second = 0.0f;
    if (scaling->encoding_mode == 1u) {
        first = (float)scaling->encoded_values[index];
        const uint16_t divisor = (uint16_t)scaling->divisors[index];
        if (divisor != 0u) {
            const float scaled = first / 0x1.f4p+9f;
            second = scaled / (float)divisor;
        }
    } else if (scaling->encoding_mode == 0u) {
        if (scaling->bit_width > 32u) {
            return false;
        }
        const uint32_t mask_bits = scaling->bit_width > 17u
            ? (uint32_t)scaling->bit_width - 1u
            : (uint32_t)scaling->bit_width;
        const uint32_t mask = mask_bits == 32u
            ? UINT32_MAX
            : (UINT32_C(1) << mask_bits) - 1u;
        const uint32_t shift = scaling->bit_width > 17u
            ? (uint32_t)scaling->bit_width - 17u : 0u;
        const uint32_t extracted =
            ((uint32_t)scaling->encoded_values[index] & mask) >> shift;
        first = (float)(int32_t)extracted;

        if (scaling->scale_mode <= 2u) {
            if (scaling->scale_codes == NULL ||
                    index >= scaling->scale_code_count) {
                return false;
            }
            const uint8_t code = scaling->scale_codes[index];
            const int32_t *const table =
                scaling->scale_tables[scaling->scale_mode];
            if (table == NULL ||
                    (size_t)code >=
                        scaling->scale_table_counts[scaling->scale_mode]) {
                return false;
            }
            const int32_t table_scale = table[code];
            const int16_t divisor = scaling->divisors[index];
            if (table_scale != 0 && divisor != 0) {
                if (scaling->power == NULL) {
                    return false;
                }
                if (scaling->scale_mode == 0u) {
                    const double power_ten = scaling->power(10.0, 3.0);
                    const double power_two = scaling->power(2.0, 17.0);
                    float numerator = first * 2.0f;
                    numerator *= 0x1.9p+9f;
                    numerator *= 0x1.f4p+9f;
                    double value = (double)numerator;
                    value /= power_two;
                    value *= power_ten;
                    value /= (double)table_scale;
                    value /= (double)divisor;
                    second = (float)value;
                } else {
                    const double power_ten = scaling->power(10.0, 9.0);
                    const double power_two = scaling->power(2.0, 17.0);
                    double value = (double)first;
                    value *= 0x1.ccccccccccccdp+0;
                    value /= power_two;
                    value /= (double)table_scale;
                    value /= (double)divisor;
                    value *= power_ten;
                    second = (float)value;
                }
            }
        }
    } else {
        return false;
    }

    destination[0] = first;
    destination[1] = second;
    return true;
}

void goodix_primitives_spo2_channel_scale_decode(
    void *context, uint8_t channel, uint16_t group, float destination[2]) {
    (void)goodix_primitives_spo2_channel_scale_pair(
        context, channel, group, destination);
}

bool goodix_primitives_spo2_channel_records_assemble(
    const goodix_primitives_spo2_channel_source *source,
    int32_t sequence, uint32_t expected_record_count,
    goodix_primitives_spo2_channel_output *output,
    goodix_primitives_i32_unary_fn integrity_transform,
    goodix_primitives_spo2_channel_decode_fn decode,
    bool *count_mismatch) {
    if (source == NULL || output == NULL || integrity_transform == NULL ||
            decode == NULL || count_mismatch == NULL ||
            (expected_record_count != 0u && output->records == NULL) ||
            output->record_capacity < (size_t)expected_record_count) {
        return false;
    }

    const size_t value_count = (size_t)source->channel_count * 3u;
    const size_t presence_bytes = (value_count + 7u) / 8u;
    if ((value_count != 0u && (source->presence_bytes == NULL ||
                              source->encoded_values == NULL)) ||
            source->presence_byte_count < presence_bytes ||
            source->encoded_value_count < value_count ||
            (source->integrity_presence != NULL &&
             source->integrity_presence_count < value_count)) {
        return false;
    }

    uint8_t differing_count = 0u;
    for (size_t index = 0u; index < value_count; ++index) {
        const bool integrity_enabled = source->integrity_presence != NULL
            ? source->integrity_presence[index] != 0u
            : goodix_primitives_msb_first_bit(
                  source->presence_bytes, index);
        if (integrity_enabled) {
            const bool differs = goodix_primitives_transformed_differs(
                source->encoded_values[index], integrity_transform);
            differing_count = (uint8_t)(differing_count + (uint8_t)differs);
            if (differs) {
                source->encoded_values[index] = INT32_C(0x00800000);
            }
        }
    }
    (void)differing_count;

    output->sequence = goodix_primitives_wrapped_add_i32(sequence, -1);
    output->metadata[0] = source->metadata[0];
    output->metadata[1] = source->metadata[1];
    output->metadata[2] = source->metadata[2];

    uint8_t record_index = 0u;
    const size_t channel_count = source->channel_count;
    for (size_t channel = 0u; channel < channel_count; ++channel) {
        if (goodix_primitives_msb_first_bit(
                source->presence_bytes, channel) &&
                (uint32_t)record_index < expected_record_count) {
            decode(source->decode_context, (uint8_t)channel, UINT16_C(0),
                   output->records[record_index].groups[0]);
        }
        if (goodix_primitives_msb_first_bit(
                source->presence_bytes, channel + channel_count) &&
                (uint32_t)record_index < expected_record_count) {
            decode(source->decode_context, (uint8_t)channel, UINT16_C(1),
                   output->records[record_index].groups[1]);
        }
        if (goodix_primitives_msb_first_bit(
                source->presence_bytes, channel + channel_count * 2u)) {
            if ((uint32_t)record_index < expected_record_count) {
                decode(source->decode_context, (uint8_t)channel, UINT16_C(2),
                       output->records[record_index].groups[2]);
            }
            record_index = (uint8_t)(record_index + 1u);
            output->record_count = (uint8_t)(output->record_count + 1u);
        }
    }
    *count_mismatch = expected_record_count != (uint32_t)record_index;
    return true;
}

bool goodix_primitives_spo2_biquad_cascade_process(
    goodix_primitives_biquad_cascade *cascade, float input,
    bool update_previous, bool limit_discontinuity,
    int32_t discontinuity_limit, bool force_correction,
    float *output) {
    if (cascade == NULL || cascade->states == NULL ||
            cascade->coefficients == NULL || output == NULL ||
            cascade->stage_count == 0u ||
            cascade->state_count < (size_t)cascade->stage_count ||
            cascade->coefficient_count < (size_t)cascade->stage_count) {
        return false;
    }

    if (update_previous) {
        const float difference = input - cascade->previous_input;
        bool correct = force_correction;
        if (!correct && limit_discontinuity) {
            if (difference != 0.0f) {
                const float magnitude = difference >= 0.0f
                    ? difference : -difference;
                correct = magnitude > (float)discontinuity_limit;
            } else {
                correct =
                    (int32_t)goodix_primitives_float_bits(input) >
                        INT32_C(0x477A0000) ||
                    input == 0.0f;
            }
        }
        if (correct) {
            goodix_primitives_biquad_state *const first =
                &cascade->states[0];
            const goodix_primitives_biquad_coefficients *const coefficients =
                &cascade->coefficients[0];
            first->first +=
                (coefficients->delayed_input +
                 coefficients->second_delayed_input) * difference;
            first->second +=
                coefficients->second_delayed_input * difference;
        }
        cascade->previous_input = input;
    }

    float value = input;
    for (size_t stage = 0u; stage < (size_t)cascade->stage_count; ++stage) {
        goodix_primitives_biquad_state *const state =
            &cascade->states[stage];
        const goodix_primitives_biquad_coefficients *const coefficients =
            &cascade->coefficients[stage];
        const float filtered =
            state->first + coefficients->input * value;
        state->first =
            state->second + coefficients->delayed_input * value +
            coefficients->feedback * filtered;
        state->second =
            coefficients->second_delayed_input * value +
            coefficients->second_feedback * filtered;
        value = filtered;
    }
    *output = value;
    return true;
}

bool goodix_primitives_spo2_decimal_residual(
    float value, goodix_primitives_float_unary_fn logarithm_base_10,
    float *output) {
    if (logarithm_base_10 == NULL || output == NULL) {
        return false;
    }
    const float magnitude = value >= 0.0f ? value : -value;
    if ((int32_t)goodix_primitives_float_bits(magnitude) <
            INT32_C(0x358637BD)) {
        return true;
    }
    const float logarithm = logarithm_base_10(magnitude);
    uint32_t exponent = 0u;
    if (logarithm > 0.0f) {
        exponent = logarithm >= 4294967296.0f
            ? UINT32_MAX : (uint32_t)logarithm;
    }
    const float scale = goodix_primitives_unsigned_power(
        10.0f, (uint8_t)(exponent + 1u));
    const float normalized = value / scale;
    float four_places = 0.0f;
    float eight_places = 0.0f;
    if (!goodix_primitives_truncate_decimal(
            normalized, 4u, &four_places) ||
            !goodix_primitives_truncate_decimal(
                normalized, 8u, &eight_places)) {
        return false;
    }
    float residual = (four_places - eight_places) * 10000.0f;
    if (residual < 0.0f) {
        residual = -residual;
    }
    int32_t parity = 0;
    if (!goodix_primitives_float_to_i32(
            residual * 10000.0f, &parity)) {
        return false;
    }
    *output = (parity & 1) != 0 ? -residual : residual;
    return true;
}

bool goodix_primitives_spo2_rolling_percentile_select(
    const float *source, size_t source_count,
    float *sorted, size_t *sorted_count, size_t sorted_capacity,
    float *prior_anchor, int32_t tolerance_scale, float *output) {
    if (source == NULL || sorted == NULL || sorted_count == NULL ||
            prior_anchor == NULL || output == NULL || source_count == 0u ||
            source_count > (size_t)UINT16_MAX ||
            *sorted_count < source_count || *sorted_count > sorted_capacity) {
        return false;
    }
    size_t remove_index = source_count;
    for (size_t index = 0u; index < source_count; ++index) {
        if (sorted[index] == *prior_anchor) {
            remove_index = index;
            break;
        }
    }
    if (remove_index == source_count && *sorted_count == sorted_capacity) {
        return false;
    }
    if (remove_index < source_count) {
        for (size_t index = remove_index; index + 1u < *sorted_count; ++index) {
            sorted[index] = sorted[index + 1u];
        }
        --*sorted_count;
    }
    const float candidate = source[source_count - 1u];
    if (!goodix_primitives_sorted_insert(
            sorted, sorted_count, sorted_capacity, candidate)) {
        return false;
    }
    *prior_anchor = source[0];
    float lower = 0.0f;
    float median = 0.0f;
    float upper = 0.0f;
    if (!goodix_primitives_percentile_lookup(
            sorted, source_count, 25u, &lower) ||
            !goodix_primitives_percentile_lookup(
                sorted, source_count, 50u, &median) ||
            !goodix_primitives_percentile_lookup(
                sorted, source_count, 75u, &upper)) {
        return false;
    }
    float spread = upper - lower;
    if ((int32_t)goodix_primitives_float_bits(spread) <
            INT32_C(0x40A00000)) {
        spread = 5.0f;
    }
    float difference = candidate - median;
    if (difference < 0.0f) {
        difference = -difference;
    }
    *output = difference <= spread * (float)tolerance_scale
        ? candidate : median;
    return true;
}

static bool goodix_primitives_spo2_stream_cascade_valid(
    const goodix_primitives_biquad_cascade *cascade) {
    return cascade != NULL && cascade->states != NULL &&
        cascade->coefficients != NULL && cascade->stage_count != 0u &&
        cascade->state_count >= (size_t)cascade->stage_count &&
        cascade->coefficient_count >= (size_t)cascade->stage_count;
}

static bool goodix_primitives_spo2_stream_i16_window_valid(
    const goodix_primitives_i16_window *window) {
    return window != NULL && window->values != NULL &&
        window->capacity != 0u && window->count <= window->capacity;
}

static bool goodix_primitives_spo2_stream_motion_window_valid(
    const goodix_primitives_decimated_float_window *window,
    size_t required_capacity) {
    return window != NULL && window->values != NULL &&
        window->capacity >= required_capacity &&
        window->count <= window->capacity && window->period == 1u &&
        window->phase == 0u && window->cursor < window->capacity;
}

static bool goodix_primitives_spo2_stream_push_packed(
    goodix_primitives_i16_window *window, float value) {
    const uint16_t packed = goodix_primitives_f32_bits_to_packed_6_9(
        goodix_primitives_float_bits(value));
    return goodix_primitives_i16_window_push(
        window, goodix_primitives_u16_bits_to_i16(packed));
}

static bool goodix_primitives_spo2_stream_motion_values(
    const goodix_primitives_warmup_average_state *sample,
    float residual, const goodix_primitives_spo2_stream_plan *plan,
    float values[4]) {
    values[0] = (float)goodix_primitives_u32_as_i32(sample->reserved[8]) +
        plan->residual_axis_scale * residual;
    values[1] = (float)goodix_primitives_u32_as_i32(sample->reserved[9]) +
        plan->residual_axis_scale * residual;
    values[2] = (float)goodix_primitives_u32_as_i32(sample->reserved[10]) +
        plan->residual_axis_scale * residual;
    const float mean_square =
        (values[0] * values[0] + values[1] * values[1] +
         values[2] * values[2]) / 3.0f;
    values[3] = mean_square < 0.0f
        ? 0.0f : plan->square_root(mean_square);
    return true;
}

static bool goodix_primitives_spo2_stream_filter_motion(
    const float values[4], uint32_t ordinal,
    goodix_primitives_spo2_stream_state *state) {
    float filtered[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    const bool force_correction = ordinal == 1u;
    for (size_t lane = 0u; lane < 4u; ++lane) {
        if (!goodix_primitives_spo2_biquad_cascade_process(
                &state->motion_filters[lane], values[lane], true, false,
                0, force_correction, &filtered[lane])) {
            return false;
        }
    }
    for (size_t lane = 0u; lane < 3u; ++lane) {
        if (!goodix_primitives_spo2_stream_push_packed(
                &state->motion_packed[lane], filtered[lane])) {
            return false;
        }
    }
    return ordinal % 3u != 1u ||
        goodix_primitives_spo2_stream_push_packed(
            &state->motion_packed[3], filtered[3]);
}

bool goodix_primitives_spo2_stream_accumulate(
    goodix_primitives_warmup_average_state *sample,
    uint8_t filtering_mode,
    const goodix_primitives_spo2_stream_plan *plan,
    goodix_primitives_spo2_stream_state *state,
    goodix_primitives_spo2_stream_workspace *workspace) {
    if (sample == NULL || plan == NULL || state == NULL ||
            workspace == NULL || filtering_mode > 1u ||
            plan->motion_window_size == 0u ||
            plan->motion_spread_factor <= 0 ||
            plan->logarithm_base_10 == NULL || plan->square_root == NULL) {
        return false;
    }
    const size_t motion_count = plan->motion_window_size;
    for (size_t lane = 0u; lane < 4u; ++lane) {
        if (!goodix_primitives_spo2_stream_cascade_valid(
                &state->channel_filters[lane]) ||
                !goodix_primitives_spo2_stream_i16_window_valid(
                    &state->channel_packed[lane]) ||
                !goodix_primitives_spo2_stream_motion_window_valid(
                    &state->motion_history[lane], motion_count)) {
            return false;
        }
    }
    if (!goodix_primitives_spo2_stream_cascade_valid(
            &state->residual_filter) ||
            !goodix_primitives_spo2_stream_i16_window_valid(
                &state->residual_packed)) {
        return false;
    }

    const uint32_t next_count = state->sample_count + UINT32_C(1);
    if (next_count >= (uint32_t)plan->motion_window_size) {
        for (size_t lane = 0u; lane < 4u; ++lane) {
            if (!goodix_primitives_spo2_stream_cascade_valid(
                    &state->motion_filters[lane]) ||
                    !goodix_primitives_spo2_stream_i16_window_valid(
                        &state->motion_packed[lane])) {
                return false;
            }
        }
        for (size_t lane = 0u; lane < 3u; ++lane) {
            if (state->motion_sorted[lane] == NULL ||
                    state->motion_sorted_count[lane] >
                        state->motion_sorted_capacity[lane] ||
                    state->motion_sorted_capacity[lane] < motion_count) {
                return false;
            }
        }
        if (workspace->sort_scratch == NULL ||
                workspace->sort_scratch_capacity < motion_count) {
            return false;
        }
    }

    state->sample_count = next_count;
    if (!goodix_primitives_finalize_warmup_average(sample)) {
        return false;
    }
    const int32_t channel_samples[4] = {
        sample->first, sample->second, sample->third, sample->average,
    };
    float filtered_channel[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    const bool force_correction = state->sample_count == 1u;
    for (size_t lane = 0u; lane < 4u; ++lane) {
        const float value = (float)channel_samples[lane];
        if (filtering_mode == 0u) {
            state->channel_discontinuity_limits[lane] =
                value > 1207959552.0f ? INT32_C(0x40000) :
                INT32_C(0x800);
        } else {
            int32_t scale = 0;
            if (!goodix_primitives_spo2_smoothed_scale(
                    state->sample_count, value, plan->scale_rate,
                    &state->scale_accumulators[lane], &scale)) {
                return false;
            }
            if (scale != 0) {
                state->channel_discontinuity_limits[lane] =
                    scale < plan->minimum_scale
                    ? plan->minimum_scale : scale;
            }
        }
        if (!goodix_primitives_spo2_biquad_cascade_process(
                &state->channel_filters[lane], value, true, true,
                state->channel_discontinuity_limits[lane],
                force_correction, &filtered_channel[lane]) ||
                !goodix_primitives_spo2_stream_push_packed(
                    &state->channel_packed[lane],
                    filtered_channel[lane])) {
            return false;
        }
    }

    float residual = 0.0f;
    if (!goodix_primitives_spo2_decimal_residual(
            filtered_channel[3], plan->logarithm_base_10, &residual)) {
        return false;
    }
    float filtered_residual = 0.0f;
    if (!goodix_primitives_spo2_biquad_cascade_process(
            &state->residual_filter, residual, true, false, 0,
            force_correction, &filtered_residual) ||
            !goodix_primitives_spo2_stream_push_packed(
                &state->residual_packed, filtered_residual)) {
        return false;
    }

    float motion[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    if (!goodix_primitives_spo2_stream_motion_values(
            sample, residual, plan, motion)) {
        return false;
    }
    for (size_t lane = 0u; lane < 4u; ++lane) {
        if (!goodix_primitives_decimated_float_window_push(
                &state->motion_history[lane], motion[lane])) {
            return false;
        }
    }

    if (state->sample_count == (uint32_t)plan->motion_window_size) {
        for (size_t lane = 0u; lane < 4u; ++lane) {
            if (state->motion_history[lane].count < motion_count ||
                    !goodix_primitives_replace_far_from_median(
                        state->motion_history[lane].values, motion_count,
                        plan->motion_spread_factor,
                        workspace->sort_scratch,
                        workspace->sort_scratch_capacity)) {
                return false;
            }
        }
        for (size_t lane = 0u; lane < 3u; ++lane) {
            for (size_t index = 0u; index < motion_count; ++index) {
                state->motion_sorted[lane][index] =
                    state->motion_history[lane].values[index];
            }
            if (!goodix_primitives_sort_floats(
                    state->motion_sorted[lane], motion_count)) {
                return false;
            }
            state->motion_sorted_count[lane] = motion_count;
            state->motion_anchor[lane] =
                state->motion_history[lane].values[0];
        }
        for (size_t index = 0u; index < motion_count; ++index) {
            const float replay[4] = {
                state->motion_history[0].values[index],
                state->motion_history[1].values[index],
                state->motion_history[2].values[index],
                state->motion_history[3].values[index],
            };
            if (!goodix_primitives_spo2_stream_filter_motion(
                    replay, (uint32_t)(index + 1u), state)) {
                return false;
            }
        }
    } else if (state->sample_count >
            (uint32_t)plan->motion_window_size) {
        for (size_t lane = 0u; lane < 3u; ++lane) {
            if (state->motion_history[lane].count < motion_count ||
                    !goodix_primitives_spo2_rolling_percentile_select(
                        state->motion_history[lane].values, motion_count,
                        state->motion_sorted[lane],
                        &state->motion_sorted_count[lane],
                        state->motion_sorted_capacity[lane],
                        &state->motion_anchor[lane],
                        plan->motion_spread_factor, &motion[lane])) {
                return false;
            }
        }
        const float mean_square =
            (motion[0] * motion[0] + motion[1] * motion[1] +
             motion[2] * motion[2]) / 3.0f;
        motion[3] = mean_square < 0.0f
            ? 0.0f : plan->square_root(mean_square);
        if (!goodix_primitives_spo2_stream_filter_motion(
                motion, state->sample_count, state)) {
            return false;
        }
    }
    return true;
}

typedef struct {
    const goodix_primitives_spo2_report_analyzer_input *input;
    goodix_primitives_spo2_report_analyzer_state *state;
    goodix_primitives_float_unary_fn square_root;
    goodix_primitives_float_unary_fn logarithm_base_10;
    bool succeeded;
} goodix_primitives_spo2_process_analyzer_context;

static void goodix_primitives_spo2_process_analyze(
    void *context, goodix_primitives_spo2_report_analysis *analysis) {
    goodix_primitives_spo2_process_analyzer_context *const analyzer = context;
    analyzer->succeeded = goodix_primitives_spo2_report_analyze(
        analyzer->input, analyzer->state, analyzer->square_root,
        analyzer->logarithm_base_10, analysis);
}

static bool goodix_primitives_spo2_process_flag(
    const goodix_primitives_spo2_process_input *input, size_t index) {
    return (input->enable_flags[index / 8u] >> (7u - index % 8u) & 1u) != 0u;
}

static void goodix_primitives_hba_cascade_bind(
    goodix_primitives_biquad_cascade *cascade,
    const goodix_primitives_pair_buffer *buffer,
    const goodix_primitives_biquad_coefficients coefficients[4]) {
    *cascade = (goodix_primitives_biquad_cascade){
        .stage_count = buffer->count,
        .states = (goodix_primitives_biquad_state *)buffer->records,
        .state_count = buffer->count,
        .coefficients = coefficients,
        .coefficient_count = 4u,
    };
}

static void goodix_primitives_hba_i16_window_bind(
    goodix_primitives_i16_window *window,
    const goodix_primitives_buffer_descriptor *descriptor) {
    *window = (goodix_primitives_i16_window){
        .values = descriptor->data,
        .count = descriptor->count,
        .capacity = descriptor->capacity,
    };
}

static void goodix_primitives_hba_float_window_bind(
    goodix_primitives_decimated_float_window *window,
    const goodix_primitives_float_descriptor *descriptor) {
    *window = (goodix_primitives_decimated_float_window){
        .values = descriptor->data,
        .count = descriptor->count,
        .capacity = descriptor->capacity,
        .period = 1u,
    };
}

static void goodix_primitives_hba_byte_window_bind(
    goodix_primitives_byte_window *window,
    const goodix_primitives_extended_descriptor *descriptor) {
    *window = (goodix_primitives_byte_window){
        .values = descriptor->data,
        .count = descriptor->count,
        .capacity = descriptor->capacity,
    };
}

static void goodix_primitives_hba_runtime_sync_plan(
    goodix_primitives_hba_runtime *runtime) {
    for (size_t lane = 0u; lane < 3u; ++lane) {
        runtime->plan.deviation_channels[lane].count =
            runtime->stream_state.motion_packed[lane].count;
    }
    runtime->plan.deviation_channels[3].count =
        runtime->stream_state.motion_packed[3].count;
}

/* 0x0005CEA8: the selector-six graph is an in-place workspace transform.
 * Stock copied the input word to the output word before dispatch; the HBA
 * caller aliases both buffers, so the native reconstruction dispatches the
 * same source-owned workspace for both arguments. */
static int32_t goodix_primitives_hba_workspace_process(
    void *context, float *workspace, size_t workspace_count) {
    goodix_primitives_hba_runtime *runtime = context;
    if (runtime == NULL || workspace == NULL || workspace_count == 0u ||
            runtime->context_owner == NULL ||
            runtime->context_owner->primary == NULL ||
            runtime->plan.operations == NULL) {
        return 1;
    }
    goodix_primitives_hr_primary_context *const primary =
        runtime->context_owner->primary;
    int32_t result = 0;
    if (!goodix_primitives_dispatch_indexed_operation(
            (uint32_t *)primary->graph_selector_6,
            runtime->plan.operations, primary->graph_mode,
            (uintptr_t)workspace, primary->graph_enabled,
            (uintptr_t)workspace, (uintptr_t)0, &result)) {
        return 1;
    }
    return result;
}

bool goodix_primitives_hba_runtime_bind(
    goodix_primitives_hr_context_owner *context_owner,
    const goodix_primitives_hba_runtime_bindings *bindings,
    goodix_primitives_hba_runtime *runtime) {
    if (context_owner == NULL || context_owner->primary == NULL ||
            context_owner->secondary == NULL || bindings == NULL ||
            bindings->integrity_transform == NULL ||
            bindings->quantized == NULL || bindings->operations == NULL ||
            bindings->elapsed_state == NULL ||
            bindings->exponential == NULL ||
            bindings->logarithm_base_10 == NULL ||
            bindings->square_root == NULL || runtime == NULL ||
            runtime->bound) {
        return false;
    }
    *runtime = (goodix_primitives_hba_runtime){0};
    runtime->context_owner = context_owner;
    for (size_t stage = 0u; stage < 4u; ++stage) {
        const size_t word = R1_GOODIX_HBA_FILTER_WORD_OFFSET + stage * 5u;
        runtime->filter_coefficients[stage] =
            (goodix_primitives_biquad_coefficients){
                .input = goodix_primitives_float_from_bits(
                    r1_goodix_hba_words[word]),
                .delayed_input = goodix_primitives_float_from_bits(
                    r1_goodix_hba_words[word + 1u]),
                .second_delayed_input = goodix_primitives_float_from_bits(
                    r1_goodix_hba_words[word + 2u]),
                .feedback = goodix_primitives_float_from_bits(
                    r1_goodix_hba_words[word + 3u]),
                .second_feedback = goodix_primitives_float_from_bits(
                    r1_goodix_hba_words[word + 4u]),
            };
    }

    goodix_primitives_hr_primary_context *const primary =
        context_owner->primary;
    goodix_primitives_hr_secondary_context *const secondary =
        context_owner->secondary;
    for (size_t lane = 0u; lane < 4u; ++lane) {
        goodix_primitives_hba_cascade_bind(
            &runtime->stream_state.channel_filters[lane],
            &secondary->pair_buffers[lane], runtime->filter_coefficients);
        goodix_primitives_hba_i16_window_bind(
            &runtime->stream_state.channel_packed[lane],
            &secondary->i16_buffers[lane]);
    }
    /* Stock 0x3113C order: filters 4..6 are XYZ, 7 is the decimal
     * residual, and 8 is the decimated magnitude. */
    for (size_t lane = 0u; lane < 3u; ++lane) {
        goodix_primitives_hba_cascade_bind(
            &runtime->stream_state.motion_filters[lane],
            &secondary->pair_buffers[4u + lane],
            runtime->filter_coefficients);
        goodix_primitives_hba_i16_window_bind(
            &runtime->stream_state.motion_packed[lane],
            &secondary->i16_buffers[4u + lane]);
    }
    goodix_primitives_hba_cascade_bind(
        &runtime->stream_state.residual_filter,
        &secondary->pair_buffers[7], runtime->filter_coefficients);
    goodix_primitives_hba_i16_window_bind(
        &runtime->stream_state.residual_packed,
        &secondary->i16_buffers[8]);
    goodix_primitives_hba_cascade_bind(
        &runtime->stream_state.motion_filters[3],
        &secondary->pair_buffers[8], runtime->filter_coefficients);
    goodix_primitives_hba_i16_window_bind(
        &runtime->stream_state.motion_packed[3],
        &secondary->i16_buffers[7]);

    for (size_t lane = 0u; lane < 4u; ++lane) {
        goodix_primitives_hba_float_window_bind(
            &runtime->stream_state.motion_history[lane],
            &secondary->float_histories[lane]);
    }
    for (size_t lane = 0u; lane < 3u; ++lane) {
        const goodix_primitives_float_descriptor *const descriptor =
            &secondary->float_histories[4u + lane];
        runtime->stream_state.motion_sorted[lane] = descriptor->data;
        runtime->stream_state.motion_sorted_count[lane] = descriptor->count;
        runtime->stream_state.motion_sorted_capacity[lane] =
            descriptor->capacity;
    }
    for (size_t lane = 0u; lane < 4u; ++lane) {
        runtime->stream_state.scale_accumulators[lane] =
            primary->initial_baselines[lane];
        runtime->stream_state.channel_discontinuity_limits[lane] =
            (int32_t)primary->initial_accumulators[lane];
    }
    runtime->stream_workspace = (goodix_primitives_hba_stream_workspace){
        .sort_scratch = runtime->sort_scratch,
        .sort_scratch_capacity = 20u,
    };
    runtime->stream_plan = (goodix_primitives_spo2_stream_plan){
        .scale_rate = (uint32_t)primary->terminal_default,
        .minimum_scale = INT32_C(112500),
        .residual_axis_scale = 0.0001f,
        .motion_window_size = secondary->float_histories[0].capacity,
        .motion_spread_factor = 8,
        .logarithm_base_10 = bindings->logarithm_base_10,
        .square_root = bindings->square_root,
    };
    runtime->configuration = (goodix_primitives_hba_process_configuration){
        .sample_frequency = primary->sample_rate,
        .processing_cadence = primary->samples_per_25hz_phase,
        .expected_valid_channels = primary->minimum_batch,
        .report_selected_value = primary->secondary_window,
        .maximum_selection = (int32_t)primary->primary_window,
        .selection_delay = (int32_t)primary->candidate_limit,
        .score_scale = primary->owner_word,
    };
    if (runtime->configuration.processing_cadence == 0u ||
            runtime->stream_plan.motion_window_size == 0u ||
            primary->graph_selector_0 == (uintptr_t)0 ||
            primary->graph_selector_1 == (uintptr_t)0 ||
            primary->graph_selector_6 == (uintptr_t)0) {
        *runtime = (goodix_primitives_hba_runtime){0};
        return false;
    }

    runtime->timed_dispatch = (goodix_primitives_timed_dispatch_context){
        .elapsed_state = bindings->elapsed_state,
        .mode_buffers = bindings->mode_buffers,
        .mode = primary->terminal_flags[0],
        .dispatch_record = (uint32_t *)primary->graph_selector_0,
        .field_64 = primary->graph_mode,
        .field_68 = primary->graph_enabled,
    };
    runtime->score_dispatch = (goodix_primitives_spo2_score_context){
        .recent_inputs = runtime->recent_score_inputs,
        .recent_input_count = 4u,
        .dispatch = {
            .dispatch_record = (uint32_t *)primary->graph_selector_1,
            .field_64 = primary->graph_mode,
            .field_68 = primary->graph_enabled,
        },
    };

    runtime->plan = (goodix_primitives_hba_process_plan){
        .integrity_transform = bindings->integrity_transform,
        .stream_plan = &runtime->stream_plan,
        .triplicate_disabled = 1u,
        .workspace_process = goodix_primitives_hba_workspace_process,
        .workspace_process_context = runtime,
        .quantized = bindings->quantized,
        .timed_dispatch = &runtime->timed_dispatch,
        .score_dispatch = &runtime->score_dispatch,
        .operations = bindings->operations,
        .exponential = bindings->exponential,
        .logarithm_base_10 = bindings->logarithm_base_10,
    };
    for (size_t bank = 0u; bank < 7u; ++bank) {
        const goodix_primitives_i16_window *const packed = bank < 4u
            ? &runtime->stream_state.channel_packed[bank]
            : &runtime->stream_state.motion_packed[bank - 4u];
        runtime->plan.packed_banks[bank] =
            (const uint16_t *)packed->values;
    }
    for (size_t lane = 0u; lane < 4u; ++lane) {
        runtime->plan.deviation_channels[lane].values =
            (const uint16_t *)runtime->stream_state.motion_packed[lane].values;
        runtime->plan.spectral_packed_channels[lane] =
            (const uint16_t *)runtime->stream_state.channel_packed[lane].values;
        runtime->plan.spectral_packed_channel_counts[lane] =
            runtime->stream_state.channel_packed[lane].capacity;
    }

    runtime->state.invocation_count = primary->periodic_interval;
    runtime->state.sample_count = primary->processed_count;
    runtime->state.elapsed_seconds = primary->pending_count;
    runtime->state.report_selected_candidate =
        primary->primary_window_low_byte;
    runtime->state.stream = &runtime->stream_state;
    goodix_primitives_hba_byte_window_bind(
        &runtime->state.analyzer.primary_candidates,
        &primary->short_history_a);
    goodix_primitives_hba_float_window_bind(
        &runtime->state.analyzer.concentrations,
        &primary->float_history_a);
    goodix_primitives_hba_byte_window_bind(
        &runtime->state.analyzer.reference_candidates,
        &primary->short_history_b);
    goodix_primitives_hba_float_window_bind(
        &runtime->state.analyzer.metric_history,
        &primary->float_history_b);
    runtime->state.analyzer.reference_limit = 50u;
    goodix_primitives_hba_runtime_sync_plan(runtime);
    runtime->bound = true;
    return true;
}

uint32_t goodix_primitives_hba_runtime_process(
    goodix_primitives_hba_runtime *runtime,
    const goodix_primitives_hba_process_input *input,
    goodix_primitives_hba_process_output *output) {
    if (runtime == NULL || !runtime->bound || input == NULL ||
            output == NULL || runtime->context_owner == NULL ||
            runtime->context_owner->primary == NULL) {
        return UINT32_C(1);
    }
    goodix_primitives_hba_runtime_sync_plan(runtime);
    const uint32_t status = goodix_primitives_hba_process(
        &runtime->configuration, input, output, &runtime->plan,
        &runtime->state, &runtime->stream_workspace, &runtime->workspace);
    goodix_primitives_hr_primary_context *const primary =
        runtime->context_owner->primary;
    primary->periodic_interval = runtime->state.invocation_count;
    primary->processed_count = runtime->state.sample_count;
    primary->pending_count = runtime->state.elapsed_seconds;
    return status;
}

bool goodix_primitives_hba_runtime_unbind(
    goodix_primitives_hba_runtime *runtime) {
    if (runtime == NULL || !runtime->bound) {
        return false;
    }
    *runtime = (goodix_primitives_hba_runtime){0};
    return true;
}

static bool goodix_primitives_spo2_process_dispatch_valid(
    const uint32_t *record,
    const goodix_primitives_indexed_operation_fn *operations) {
    return record != NULL && operations != NULL &&
        record[0] < GOODIX_PRIMITIVES_STATE_COUNT &&
        operations[record[0]] != NULL;
}

static bool goodix_primitives_spo2_process_downstream_valid(
    const goodix_primitives_spo2_process_plan *plan) {
    if (plan->workspace_process == NULL || plan->quantized == NULL ||
            plan->timed_dispatch == NULL || plan->score_dispatch == NULL ||
            plan->exponential == NULL || plan->logarithm_base_10 == NULL ||
            !goodix_primitives_spo2_process_dispatch_valid(
                plan->timed_dispatch->dispatch_record, plan->operations) ||
            !goodix_primitives_spo2_process_dispatch_valid(
                plan->score_dispatch->dispatch.dispatch_record,
                plan->operations)) {
        return false;
    }
    for (size_t bank = 0u;
            bank < GOODIX_PRIMITIVES_SPO2_PACKED_TOTAL_BANK_COUNT; ++bank) {
        if (plan->packed_banks[bank] == NULL) {
            return false;
        }
    }
    for (size_t channel = 0u;
            channel < GOODIX_PRIMITIVES_SPO2_SPECTRAL_PACKED_CHANNELS;
            ++channel) {
        if (plan->spectral_packed_channels[channel] == NULL ||
                plan->spectral_packed_channel_counts[channel] <
                    GOODIX_PRIMITIVES_SPO2_SPECTRAL_PACKED_VALUES) {
            return false;
        }
    }
    return true;
}

static void goodix_primitives_spo2_process_assemble_sample(
    const int32_t channels[12], uint32_t valid_count,
    const goodix_primitives_spo2_process_input *input,
    goodix_primitives_spo2_process_workspace *workspace) {
    workspace->stream_sample.first = channels[0];
    workspace->stream_sample.second = channels[1];
    workspace->stream_sample.third = channels[2];
    workspace->stream_sample.average = channels[3];
    for (size_t index = 0u; index < 8u; ++index) {
        workspace->stream_sample.reserved[index] = (uint32_t)channels[index + 4u];
    }
    for (size_t axis = 0u; axis < 3u; ++axis) {
        workspace->stream_sample.reserved[axis + 8u] =
            (uint32_t)input->accelerometer[axis];
    }
    workspace->stream_sample.phase = valid_count;
    workspace->stream_mode = input->mode;
}

uint32_t goodix_primitives_hba_process(
    const goodix_primitives_spo2_process_configuration *configuration,
    const goodix_primitives_spo2_process_input *input,
    goodix_primitives_spo2_process_output *output,
    const goodix_primitives_spo2_process_plan *plan,
    goodix_primitives_spo2_process_state *state,
    goodix_primitives_spo2_stream_workspace *stream_workspace,
    goodix_primitives_spo2_process_workspace *workspace) {
    if (configuration == NULL || input == NULL || output == NULL ||
            plan == NULL || state == NULL || workspace == NULL ||
            input->channel_values == NULL || input->enable_flags == NULL ||
            input->filter_code == NULL || plan->integrity_transform == NULL ||
            configuration->sample_frequency == 0u ||
            configuration->processing_cadence == 0u ||
            configuration->expected_valid_channels >
                GOODIX_PRIMITIVES_SPO2_PROCESS_MAX_CHANNELS ||
            input->channel_count > GOODIX_PRIMITIVES_SPO2_PROCESS_MAX_CHANNELS ||
            input->channel_value_count <
                (size_t)input->channel_count *
                    GOODIX_PRIMITIVES_SPO2_PROCESS_CHANNEL_GROUPS ||
            input->enable_flag_count <
                ((size_t)input->channel_count *
                     GOODIX_PRIMITIVES_SPO2_PROCESS_CHANNEL_GROUPS + 7u) / 8u ||
            input->filter_code_count == 0u) {
        return UINT32_C(1);
    }

    bool invalid = false;
    for (size_t index = 0u; index < input->channel_count; ++index) {
        if (goodix_primitives_transformed_differs(
                input->channel_values[index], plan->integrity_transform)) {
            invalid = true;
        }
    }
    if (invalid) {
        for (size_t index = 0u; index < input->channel_count; ++index) {
            input->channel_values[index] = 0;
        }
    }

    state->elapsed_seconds =
        (state->invocation_count + UINT32_C(1)) /
        (uint32_t)configuration->sample_frequency;
    const uint32_t cadence = configuration->processing_cadence;
    if (state->invocation_count % cadence != cadence - UINT32_C(1)) {
        ++state->invocation_count;
        return UINT32_C(0);
    }
    if (plan->stream_plan == NULL || state->stream == NULL ||
            stream_workspace == NULL) {
        return UINT32_C(1);
    }

    int32_t channels[12] = {0};
    uint32_t valid_count = 0u;
    const size_t channel_count = input->channel_count;
    for (size_t index = 0u; index < channel_count; ++index) {
        if (goodix_primitives_spo2_process_flag(input, index)) {
            if (valid_count >= GOODIX_PRIMITIVES_SPO2_PROCESS_MAX_CHANNELS) {
                return UINT32_C(1);
            }
            channels[valid_count++] = input->channel_values[index];
        }
        if (goodix_primitives_spo2_process_flag(
                input, index + channel_count)) {
            if (valid_count >
                    GOODIX_PRIMITIVES_SPO2_PROCESS_MAX_CHANNELS) {
                return UINT32_C(1);
            }
            channels[valid_count + 3u] =
                input->channel_values[index + channel_count];
        }
        if (goodix_primitives_spo2_process_flag(
                input, index + channel_count * 2u)) {
            if (valid_count >
                    GOODIX_PRIMITIVES_SPO2_PROCESS_MAX_CHANNELS) {
                return UINT32_C(1);
            }
            channels[valid_count + 7u] =
                input->channel_values[index + channel_count * 2u];
        }
    }
    if (valid_count != configuration->expected_valid_channels) {
        return UINT32_C(1);
    }
    goodix_primitives_spo2_process_assemble_sample(
        channels, valid_count, input, workspace);
    if (!goodix_primitives_spo2_stream_accumulate(
            &workspace->stream_sample, 0u, plan->stream_plan,
            state->stream, stream_workspace)) {
        return UINT32_C(1);
    }

    if (state->stream->sample_count <= UINT32_C(50) ||
            state->sample_count <= UINT32_C(150) ||
            state->sample_count % UINT32_C(25) != UINT32_C(24)) {
        ++state->invocation_count;
        ++state->sample_count;
        return UINT32_C(0);
    }
    if (!goodix_primitives_spo2_process_downstream_valid(plan) ||
            !goodix_primitives_spo2_expand_packed_banks(
                plan->packed_banks, workspace->packed,
                GOODIX_PRIMITIVES_SPO2_PACKED_WORKSPACE_VALUES) ||
            !goodix_primitives_spo2_packed_channel_standard_deviations(
                plan->deviation_channels, workspace->deviations,
                workspace->deviation_scratch,
                GOODIX_PRIMITIVES_SPO2_SPECTRAL_INPUT_VALUES,
                plan->stream_plan->square_root) ||
            !goodix_primitives_spo2_expand_packed_triplicate(
                plan->triplicate_disabled, plan->triplicate_ready,
                plan->triplicate_values, plan->triplicate_value_count,
                workspace->packed,
                GOODIX_PRIMITIVES_SPO2_PACKED_WORKSPACE_VALUES) ||
            !goodix_primitives_normalize_rows_by_range(
                workspace->packed,
                GOODIX_PRIMITIVES_SPO2_PACKED_TOTAL_BANK_COUNT,
                GOODIX_PRIMITIVES_SPO2_PACKED_BANK_VALUES) ||
            plan->workspace_process(
                plan->workspace_process_context, workspace->packed,
                GOODIX_PRIMITIVES_SPO2_PACKED_WORKSPACE_VALUES) != 0) {
        return UINT32_C(1);
    }

    const goodix_primitives_spo2_spectral_source spectral_source = {
        .transformed_values = workspace->packed,
        .transformed_value_count =
            GOODIX_PRIMITIVES_SPO2_SPECTRAL_FLOAT_CHANNELS *
            GOODIX_PRIMITIVES_SPO2_SPECTRAL_INPUT_VALUES,
        .packed_channels = {
            plan->spectral_packed_channels[0],
            plan->spectral_packed_channels[1],
            plan->spectral_packed_channels[2],
            plan->spectral_packed_channels[3],
        },
        .packed_channel_counts = {
            plan->spectral_packed_channel_counts[0],
            plan->spectral_packed_channel_counts[1],
            plan->spectral_packed_channel_counts[2],
            plan->spectral_packed_channel_counts[3],
        },
    };
    if (!goodix_primitives_spo2_normalized_spectra_prepare(
            &spectral_source, plan->stream_plan->square_root,
            &workspace->spectral_workspace, &workspace->spectra)) {
        return UINT32_C(1);
    }

    const goodix_primitives_spo2_report_analyzer_input analyzer_input = {
        .primary_spectrum = workspace->spectra.channels[0],
        .primary_spectrum_count =
            GOODIX_PRIMITIVES_SPO2_SPECTRAL_OUTPUT_VALUES * 3u,
        .secondary_spectrum = workspace->spectra.channels[4],
        .secondary_spectrum_count =
            GOODIX_PRIMITIVES_SPO2_SPECTRAL_OUTPUT_VALUES,
        .metrics = {
            workspace->deviations[0], workspace->deviations[1],
            workspace->deviations[2], workspace->deviations[3],
        },
        .reference_candidate = (uint8_t)state->latest_result,
    };
    goodix_primitives_spo2_process_analyzer_context analyzer = {
        .input = &analyzer_input,
        .state = &state->analyzer,
        .square_root = plan->stream_plan->square_root,
        .logarithm_base_10 = plan->logarithm_base_10,
        .succeeded = false,
    };
    state->report.history_destination =
        (uint8_t *)workspace->spectra.channels[0];
    state->report.history_destination_capacity =
        sizeof(workspace->spectra.channels[0]);
    state->report.history_source =
        (const uint8_t *)workspace->spectra.channels[4];
    state->report.history_source_capacity =
        sizeof(workspace->spectra.channels[4]);
    workspace->report_output.selected_value =
        state->report_selected_candidate;
    if (!goodix_primitives_spo2_report_state_update(
            &state->report, configuration->report_selected_value,
            state->latest_result, &workspace->report_output,
            goodix_primitives_spo2_process_analyze, &analyzer) ||
            !analyzer.succeeded) {
        return UINT32_C(1);
    }
    state->report_selected_candidate =
        workspace->report_output.selected_value;

    enum { FIRST_MODEL_BIN = 15 };
    for (size_t row = 0u; row < GOODIX_PRIMITIVES_SPO2_PROCESS_MODEL_ROWS;
            ++row) {
        for (size_t column = 0u;
                column < GOODIX_PRIMITIVES_SPO2_PROCESS_MODEL_COLUMNS;
                ++column) {
            workspace->model_values[
                row * GOODIX_PRIMITIVES_SPO2_PROCESS_MODEL_COLUMNS + column] =
                workspace->spectra.channels[row][FIRST_MODEL_BIN + column];
        }
        if (!goodix_primitives_normalize_by_max(
                &workspace->model_values[
                    row * GOODIX_PRIMITIVES_SPO2_PROCESS_MODEL_COLUMNS],
                GOODIX_PRIMITIVES_SPO2_PROCESS_MODEL_COLUMNS)) {
            return UINT32_C(1);
        }
    }
    const uint32_t model_shape[2] = {
        GOODIX_PRIMITIVES_SPO2_PROCESS_MODEL_ROWS,
        GOODIX_PRIMITIVES_SPO2_PROCESS_MODEL_COLUMNS,
    };
    if (quantized_runtime_goodix_configured_in_place_float_to_int8(
            plan->quantized, UINT32_C(1), model_shape,
            workspace->model_values,
            GOODIX_PRIMITIVES_SPO2_PROCESS_MODEL_VALUES) != UINT32_C(0)) {
        return UINT32_C(1);
    }
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_SPO2_PROCESS_MODEL_COLUMNS; ++index) {
        workspace->saved_model_row[index] = workspace->model_values[index];
    }

    const goodix_primitives_graph_executor_input graph_input = {
        .workspace = workspace->packed,
        .tail_input = workspace->deviations,
        .workspace_count = GOODIX_PRIMITIVES_SPO2_PACKED_WORKSPACE_VALUES,
        .tail_input_count = 4u,
    };
    float scaled_result = 0.0f;
    const size_t dispatch_slot =
        (size_t)goodix_primitives_filter_code(input->filter_code[0]);
    if (goodix_primitives_timed_dispatch_scaled_output(
            (uintptr_t)&graph_input, dispatch_slot, &scaled_result,
            plan->timed_dispatch, plan->operations) != UINT32_C(0)) {
        return UINT32_C(1);
    }
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_SPO2_PROCESS_MODEL_COLUMNS; ++index) {
        workspace->model_values[index] = workspace->saved_model_row[index];
    }

    goodix_primitives_spo2_score_context score = *plan->score_dispatch;
    score.workspace = workspace->model_values;
    score.workspace_count = GOODIX_PRIMITIVES_SPO2_PROCESS_MODEL_VALUES;
    float logistic_score = 0.0f;
    if (goodix_primitives_spo2_dispatch_logistic_score(
            &score, scaled_result, &logistic_score,
            workspace->score_history_scratch, plan->operations,
            plan->exponential)) {
        return UINT32_C(1);
    }

    const float rounded_result =
        goodix_primitives_round_float_half_away_from_zero(scaled_result);
    const double rounded_result_wide = (double)rounded_result;
    if (!(rounded_result_wide >= (double)INT32_MIN &&
          rounded_result_wide <= (double)INT32_MAX)) {
        return UINT32_C(1);
    }
    state->latest_result = (int32_t)rounded_result_wide;
    output->score_at_least_70 = logistic_score >= 70.0f ? 1u : 0u;
    const float scaled_score =
        (float)configuration->score_scale * logistic_score;
    const double rounded_score = (double)
        goodix_primitives_round_float_half_away_from_zero(scaled_score);
    if (!(rounded_score >= 0.0 && rounded_score <= (double)UINT32_MAX)) {
        return UINT32_C(1);
    }
    output->scaled_score = (uint32_t)rounded_score;

    const uint32_t selected = state->report_selected_candidate;
    if (selected * UINT32_C(25) - UINT32_C(1) <= state->sample_count) {
        const uint32_t delayed =
            (selected + (uint32_t)configuration->selection_delay) *
                UINT32_C(25) - UINT32_C(1);
        if (state->report.event_seen == 0u ||
                configuration->maximum_selection < (int32_t)selected ||
                delayed <= state->sample_count) {
            output->selected = (uint32_t)state->latest_result;
        }
        state->last_selected = (int16_t)(uint16_t)output->selected;
        output->valid = output->selected > UINT32_C(20) ? 1u : 0u;
        state->report.accepted = true;
        state->report.event = 0u;
    }
    ++state->invocation_count;
    ++state->sample_count;
    return UINT32_C(0);
}

uint32_t goodix_primitives_spo2_process(
    const goodix_primitives_spo2_process_configuration *configuration,
    const goodix_primitives_spo2_process_input *input,
    goodix_primitives_spo2_process_output *output,
    const goodix_primitives_spo2_process_plan *plan,
    goodix_primitives_spo2_process_state *state,
    goodix_primitives_spo2_stream_workspace *stream_workspace,
    goodix_primitives_spo2_process_workspace *workspace) {
    return goodix_primitives_hba_process(
        configuration, input, output, plan, state, stream_workspace,
        workspace);
}

bool goodix_primitives_strict_local_peak_max(
    const float *values, size_t count, float *peak, uint32_t *index) {
    if (values == NULL || count == 0u || count > (size_t)UINT8_MAX ||
            peak == NULL || index == NULL) {
        return false;
    }
    float selected = 0.0f;
    uint32_t selected_index = 0u;
    for (size_t current = 1u; current + 1u < count; ++current) {
        const float candidate = values[current];
        if (values[current - 1u] < candidate &&
                values[current + 1u] < candidate &&
                selected < candidate) {
            selected = candidate;
            selected_index = (uint32_t)current;
        }
    }
    *peak = selected;
    *index = selected_index;
    return true;
}

bool goodix_primitives_merge_six_float_state(
    float state[6], const float incoming[5], bool advance) {
    if (state == NULL || incoming == NULL) {
        return false;
    }
    if (!advance) {
        float gap = state[2] - incoming[1];
        if (gap < 0.0f) {
            gap = 0.0f;
        }
        state[2] = gap + incoming[2];
        state[4] += incoming[3] + incoming[4];
        return true;
    }
    float gap = incoming[1] - state[2];
    if (gap < 0.0f) {
        gap = 0.0f;
    }
    state[1] += gap;
    state[2] = incoming[2];
    state[3] += state[4] + incoming[3];
    state[4] = incoming[4];
    state[5] = (state[5] + incoming[0]) - state[0];
    state[0] = incoming[0];
    return true;
}

bool goodix_primitives_zero_masked_sign_runs(
    const float *source, const uint8_t *markers, size_t count, float *output) {
    if (count > (size_t)INT32_MAX ||
            ((source == NULL || markers == NULL || output == NULL) &&
             count != 0u)) {
        return false;
    }
    size_t current = 0u;
    while (current < count) {
        if (markers[current] != 1u) {
            output[current] = source[current];
            ++current;
            continue;
        }
        const bool positive = source[current] > 0.0f;
        const bool negative = source[current] < 0.0f;
        if (!positive && !negative) {
            ++current;
            continue;
        }
        size_t first = current;
        while (first != 0u &&
                (positive ? source[first - 1u] > 0.0f
                          : source[first - 1u] < 0.0f)) {
            --first;
        }
        size_t last = current;
        while (last + 1u < count &&
                (positive ? source[last + 1u] > 0.0f
                          : source[last + 1u] < 0.0f)) {
            ++last;
        }
        for (size_t index = first; index <= last; ++index) {
            output[index] = 0.0f;
        }
        current = last + 1u;
    }
    return true;
}

bool goodix_primitives_running_i32_statistics_update(
    goodix_primitives_running_i32_statistics *state,
    int32_t sample, uint32_t ordinal) {
    if (state == NULL || ordinal == 0u) {
        return false;
    }
    if (ordinal == 1u) {
        state->maximum = sample;
        state->minimum = sample;
        state->mean = (float)sample;
        state->squared_deviation_sum = 0.0f;
        return true;
    }
    if (state->maximum < sample) {
        state->maximum = sample;
    }
    if (sample < state->minimum) {
        state->minimum = sample;
    }
    const uint32_t next_ordinal = ordinal + UINT32_C(1);
    const float prior_mean = state->mean;
    const float difference = (float)sample - prior_mean;
    state->squared_deviation_sum +=
        ((float)ordinal / (float)next_ordinal) * difference * difference;
    state->mean = difference / (float)next_ordinal + prior_mean;
    return true;
}

bool goodix_primitives_second_order_difference_output(
    float input, const float numerator[3], const float denominator[3],
    const float input_history[2], const float output_history[2],
    goodix_primitives_double_unary_fn round_provider, float *result) {
    if (numerator == NULL || denominator == NULL || input_history == NULL ||
            output_history == NULL || result == NULL) {
        return false;
    }
    float value = numerator[1] * input_history[0];
    value += numerator[2] * input_history[1];
    value += numerator[0] * input;
    float feedback = denominator[1] * output_history[0];
    feedback += denominator[2] * output_history[1];
    value -= feedback;
    if (denominator[0] != 1.0f) {
        if (round_provider == NULL) {
            return false;
        }
        value = (float)round_provider((double)(value / denominator[0]));
    }
    *result = value;
    return true;
}

bool goodix_primitives_nadt_optical_sample_transform(
    goodix_primitives_nadt_optical_transform *transform, float input,
    goodix_primitives_double_unary_fn round_provider, float *output) {
    enum {
        STAGE_COUNT = 2,
        COEFFICIENTS_PER_STAGE = 3,
        HISTORY_VALUES_PER_STAGE = 2,
    };
    if (transform == NULL || transform->numerators == NULL ||
            transform->denominators == NULL ||
            transform->input_histories == NULL ||
            transform->output_histories == NULL || round_provider == NULL ||
            output == NULL ||
            transform->numerator_count <
                STAGE_COUNT * COEFFICIENTS_PER_STAGE ||
            transform->denominator_count <
                STAGE_COUNT * COEFFICIENTS_PER_STAGE ||
            transform->input_history_count <
                STAGE_COUNT * HISTORY_VALUES_PER_STAGE ||
            transform->output_history_count <
                STAGE_COUNT * HISTORY_VALUES_PER_STAGE) {
        return false;
    }

    const float difference = input - transform->input_histories[0];
    bool correct_history = false;
    if (difference != 0.0f) {
        /* VCVT.S32.F32 produces the target's signed-indefinite INT32_MIN for
         * an invalid conversion. The following unsigned negate reproduces
         * the target-width RSBS absolute value, including wrapped INT32_MIN. */
        int32_t integer_difference = INT32_MIN;
        (void)goodix_primitives_float_to_i32(
            difference, &integer_difference);
        uint32_t magnitude_bits = (uint32_t)integer_difference;
        if (integer_difference < 0) {
            magnitude_bits = UINT32_C(0) - magnitude_bits;
        }
        const union {
            uint32_t unsigned_value;
            int32_t signed_value;
        } target_magnitude = {.unsigned_value = magnitude_bits};
        const float magnitude = (float)target_magnitude.signed_value;
        /* ARM's unordered VCMPE flags make the following BLT take the
         * no-correction path when the threshold is NaN. */
        if (transform->correction_threshold ==
                transform->correction_threshold) {
            correct_history =
                !(magnitude < transform->correction_threshold);
        }
    } else {
        correct_history =
            (int32_t)goodix_primitives_float_bits(input) >
                INT32_C(0x467A0000) ||
            input == 0.0f;
    }
    if (correct_history) {
        transform->input_histories[0] += difference;
        transform->input_histories[1] += difference;
    }

    float value = input;
    for (size_t stage = 0u; stage < STAGE_COUNT; ++stage) {
        const size_t coefficient_offset =
            stage * COEFFICIENTS_PER_STAGE;
        const size_t history_offset = stage * HISTORY_VALUES_PER_STAGE;
        float filtered = 0.0f;
        if (!goodix_primitives_second_order_difference_output(
                value, &transform->numerators[coefficient_offset],
                &transform->denominators[coefficient_offset],
                &transform->input_histories[history_offset],
                &transform->output_histories[history_offset],
                round_provider, &filtered)) {
            return false;
        }
        transform->input_histories[history_offset + 1u] =
            transform->input_histories[history_offset];
        transform->input_histories[history_offset] = value;
        transform->output_histories[history_offset + 1u] =
            transform->output_histories[history_offset];
        transform->output_histories[history_offset] = filtered;
        value = filtered;
    }
    *output = (float)round_provider((double)value);
    return true;
}

static int32_t goodix_primitives_arithmetic_shift_right_7(int32_t value) {
    if (value >= 0) {
        return value / INT32_C(128);
    }
    return (int32_t)(-((-(int64_t)value + INT64_C(127)) / INT64_C(128)));
}

static int32_t goodix_primitives_nadt_calibrated_sample(
    int32_t calibration, uint8_t scale_code) {
    static const int32_t scales[7] = {
        10, 25, 50, 100, 250, 500, 1000,
    };
    float converted = (float)calibration / 1000000.0f;
    converted *= (float)scales[scale_code];
    converted *= 8388608.0f;
    converted /= 900.0f;
    converted += 8388608.0f;
    int32_t result = INT32_MIN;
    (void)goodix_primitives_float_to_i32(converted, &result);
    return result;
}

bool goodix_primitives_nadt_sample_prepare(
    goodix_primitives_nadt_sample_preparation_state *state,
    const goodix_primitives_nadt_sample_preparation_input *input,
    int32_t output[3], uint16_t *configuration_changed) {
    if (state == NULL || input == NULL || output == NULL ||
            configuration_changed == NULL || input->scale_codes == NULL ||
            input->scale_code_count == 0u ||
            input->lane_stride == 0u) {
        return false;
    }
    const size_t second = input->lane_stride;
    if (second > SIZE_MAX / 2u) {
        return false;
    }
    const size_t third = second * 2u;
    const uint32_t current_sequence = input->sequence;
    const uint32_t current_scale_code = input->scale_codes[0];
    const bool sequence_changed =
        current_sequence != state->previous_sequence &&
        state->previous_sequence != 0u;
    const bool scale_changed =
        current_scale_code != state->previous_scale_code &&
        state->previous_scale_code != UINT32_C(0xFF);
    state->previous_sequence = current_sequence;
    state->previous_scale_code = current_scale_code;
    *configuration_changed = sequence_changed || scale_changed ? 1u : 0u;

    if (!input->calibrated || input->conversion_mode < UINT8_C(3)) {
        if (input->direct_values == NULL ||
                third >= input->direct_value_count) {
            return false;
        }
        output[0] = goodix_primitives_arithmetic_shift_right_7(
            input->direct_values[0]);
        output[1] = input->direct_values[second];
        output[2] = input->direct_values[third];
        return true;
    }

    if (input->conversion_mode != UINT8_C(3) ||
            input->calibration_values == NULL ||
            third >= input->calibration_value_count ||
            third >= input->scale_code_count ||
            input->scale_codes[0] > UINT8_C(6) ||
            input->scale_codes[second] > UINT8_C(6) ||
            input->scale_codes[third] > UINT8_C(6)) {
        output[0] = INT32_C(9000000);
        output[1] = INT32_C(9000000);
        output[2] = INT32_C(9000000);
        return false;
    }

    output[0] = goodix_primitives_nadt_calibrated_sample(
        input->calibration_values[0], input->scale_codes[0]);
    output[0] = goodix_primitives_arithmetic_shift_right_7(output[0]);
    output[1] = goodix_primitives_nadt_calibrated_sample(
        input->calibration_values[second], input->scale_codes[second]);
    output[2] = goodix_primitives_nadt_calibrated_sample(
        input->calibration_values[third], input->scale_codes[third]);
    return true;
}

static void goodix_primitives_nadt_stream_reset_batch(
    goodix_primitives_nadt_stream_state *state) {
    state->batch_sample_count = 0u;
    state->low_primary_count = 0u;
    state->primary_average = 0;
    state->secondary_average = 0;
    for (size_t index = 0u; index < 4u; ++index) {
        state->classifier.trigger_windows[index] = 0u;
    }
}

static int32_t goodix_primitives_nadt_stream_mean_update(
    int32_t mean, int32_t sample, uint8_t ordinal) {
    const uint32_t divisor = ordinal == 0u ? UINT32_C(1) : ordinal;
    const int64_t accumulated =
        (int64_t)mean * (int64_t)(divisor - UINT32_C(1)) + sample;
    return (int32_t)(accumulated / (int64_t)divisor);
}

static void goodix_primitives_nadt_stream_compact(
    goodix_primitives_nadt_stream_state *state,
    goodix_primitives_nadt_stream_workspace *workspace) {
    if (state->primary_history_count >=
            GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES) {
        const size_t retained =
            GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES - 25u;
        for (size_t index = 0u; index < retained; ++index) {
            workspace->primary_raw[index] =
                workspace->primary_raw[index + 25u];
            workspace->primary_filtered[index] =
                workspace->primary_filtered[index + 25u];
            workspace->configuration_markers[index] =
                workspace->configuration_markers[index + 25u];
        }
        state->primary_history_count = retained;
    }
    if (state->secondary_history_count >= 200u) {
        const size_t removed =
            ((state->batch_count / 25u) & UINT32_C(1)) == 0u ? 12u : 13u;
        const size_t retained = 200u - removed;
        for (size_t index = 0u; index < retained; ++index) {
            workspace->secondary_history[index] =
                workspace->secondary_history[index + removed];
        }
        state->secondary_history_count = retained;
    }
}

bool goodix_primitives_nadt_stream_process(
    const goodix_primitives_nadt_stream_input *input,
    const goodix_primitives_nadt_stream_plan *plan,
    goodix_primitives_nadt_stream_state *state,
    goodix_primitives_nadt_stream_workspace *workspace,
    goodix_primitives_nadt_window_diagnostics *window_diagnostics,
    goodix_primitives_nadt_stream_output *output) {
    if (input == NULL || input->sample == NULL || plan == NULL ||
            state == NULL || workspace == NULL || output == NULL ||
            plan->sample_rate < 25u || plan->window_configuration == NULL ||
            plan->window_plan == NULL || plan->preparation_state == NULL ||
            plan->optical_transform == NULL || plan->round_provider == NULL ||
            plan->square_root == NULL) {
        return false;
    }
    output->window_ready = false;
    output->configuration_changed = 0u;
    output->classification = (uint8_t)(
        (uint8_t)(uint32_t)state->classifier.current_result |
        (state->result_flag ? UINT8_C(4) : UINT8_C(0)));
    output->quality = state->classifier.quality;
    output->status = state->status;

    if (!state->initialized) {
        goodix_primitives_nadt_stream_reset_batch(state);
        state->status = 2u;
        output->status = 2u;
        return true;
    }
    const uint16_t cadence = (uint16_t)(plan->sample_rate / 25u);
    if (cadence == 0u) {
        return false;
    }
    state->cadence_counter = (uint16_t)(state->cadence_counter + 1u);
    if (state->cadence_counter % cadence != 0u) {
        return true;
    }
    state->cadence_counter = 0u;

    int32_t lanes[3] = {0, 0, 0};
    uint16_t configuration_changed = 0u;
    const bool prepared = goodix_primitives_nadt_sample_prepare(
        plan->preparation_state, input->sample, lanes,
        &configuration_changed);
    output->configuration_changed = configuration_changed;
    state->classifier.profile = input->profile;
    state->classifier.classifier_suppressed = input->classifier_suppressed;

    const int32_t shifted_x = input->axis_x >> 5;
    const int32_t shifted_y = input->axis_y >> 5;
    const int32_t shifted_z = input->axis_z >> 5;
    float yz_ratio = 300.0f;
    const int64_t z_square = (int64_t)shifted_z * shifted_z;
    if (z_square != 0) {
        const int64_t numerator = (int64_t)shifted_x * shifted_x +
            (int64_t)shifted_y * shifted_y;
        yz_ratio = (float)numerator / (float)z_square;
    }
    float xy_ratio = 300.0f;
    const int64_t x_square = (int64_t)shifted_x * shifted_x;
    if (x_square != 0) {
        const int64_t numerator = (int64_t)shifted_y * shifted_y +
            (int64_t)shifted_z * shifted_z;
        xy_ratio = (float)numerator / (float)x_square;
    }
    if (yz_ratio < plan->ratio_threshold) {
        state->classifier.trigger_windows[0] =
            goodix_primitives_nadt_increment_u8(
                state->classifier.trigger_windows[0]);
    }
    if (yz_ratio < plan->strong_ratio_threshold) {
        state->classifier.trigger_windows[2] =
            goodix_primitives_nadt_increment_u8(
                state->classifier.trigger_windows[2]);
    }
    if (xy_ratio < plan->ratio_threshold) {
        state->classifier.trigger_windows[1] =
            goodix_primitives_nadt_increment_u8(
                state->classifier.trigger_windows[1]);
    }
    if (xy_ratio > plan->strong_ratio_threshold) {
        state->classifier.trigger_windows[3] =
            goodix_primitives_nadt_increment_u8(
                state->classifier.trigger_windows[3]);
    }
    if (input->axis_x == 0 && input->axis_y == 0 && input->axis_z == 0) {
        for (size_t index = 0u; index < 4u; ++index) {
            state->classifier.trigger_windows[index] = 0u;
        }
    }

    ++state->batch_count;
    state->batch_sample_count = goodix_primitives_nadt_increment_u8(
        state->batch_sample_count);
    const size_t primary_index = state->primary_history_count <
            GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES
        ? state->primary_history_count
        : GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES - 1u;
    workspace->primary_raw[primary_index] = lanes[0];
    float filtered = 0.0f;
    if (!goodix_primitives_nadt_optical_sample_transform(
            plan->optical_transform, (float)lanes[0],
            plan->round_provider, &filtered) ||
            !(filtered >= -2147483648.0f && filtered < 2147483648.0f)) {
        return false;
    }
    workspace->primary_filtered[primary_index] = (int32_t)filtered;
    workspace->configuration_markers[primary_index] =
        (int16_t)configuration_changed;
    if (state->batch_count > 50u &&
            state->primary_history_count <
                GOODIX_PRIMITIVES_NADT_PRIMARY_MAX_SAMPLES) {
        ++state->primary_history_count;
    }

    const int32_t primary_centered = goodix_primitives_nadt_wrapped_difference(
        lanes[1], plan->primary_baseline);
    state->primary_average = goodix_primitives_nadt_stream_mean_update(
        state->primary_average, primary_centered,
        state->batch_sample_count);
    if (primary_centered < plan->low_primary_threshold) {
        state->low_primary_count = goodix_primitives_nadt_increment_u8(
            state->low_primary_count);
    }
    state->secondary_average = goodix_primitives_nadt_stream_mean_update(
        state->secondary_average, lanes[2], state->batch_sample_count);
    if ((state->batch_count & UINT32_C(1)) == 0u &&
            state->secondary_history_count < 200u) {
        const int32_t centered = goodix_primitives_nadt_wrapped_difference(
            lanes[2], plan->primary_baseline);
        workspace->secondary_history[state->secondary_history_count++] =
            goodix_primitives_u16_bits_to_i16((uint16_t)(
                (uint32_t)centered >> 8u));
    }

    const int64_t magnitude_square =
        (int64_t)shifted_x * shifted_x +
        (int64_t)shifted_y * shifted_y +
        (int64_t)shifted_z * shifted_z;
    const double magnitude_value = plan->square_root(
        (double)magnitude_square);
    if (!(magnitude_value >= 0.0) || magnitude_value > 2147483647.0) {
        return false;
    }
    const int32_t magnitude = (int32_t)(magnitude_value + 0.5);
    const size_t activity_lane = state->activity_lane & UINT8_C(3);
    goodix_primitives_running_i32_statistics activity = {
        .mean = state->activity_mean[activity_lane],
        .squared_deviation_sum =
            state->activity_squared_deviation_sum[activity_lane],
        .maximum = state->activity_maximum[activity_lane],
        .minimum = state->activity_minimum[activity_lane],
    };
    const uint32_t activity_ordinal =
        (uint32_t)((state->batch_count - 1u) % 25u);
    if (activity_ordinal == 0u) {
        activity.mean = (float)magnitude;
        activity.squared_deviation_sum = 0.0f;
        activity.maximum = magnitude;
        activity.minimum = magnitude;
    } else {
        if (!goodix_primitives_running_i32_statistics_update(
                &activity, magnitude, activity_ordinal)) {
            return false;
        }
    }
    state->activity_mean[activity_lane] = activity.mean;
    state->activity_squared_deviation_sum[activity_lane] =
        activity.squared_deviation_sum;
    state->activity_maximum[activity_lane] = activity.maximum;
    state->activity_minimum[activity_lane] = activity.minimum;
    plan->window_configuration->window_metrics[activity_lane] =
        activity.squared_deviation_sum;
    plan->window_configuration->window_maxima[activity_lane] =
        activity.maximum;
    plan->window_configuration->window_minima[activity_lane] =
        activity.minimum;
    if (activity_ordinal == 24u) {
        state->activity_lane = (uint8_t)((activity_lane + 1u) & 3u);
    }

    if (state->batch_count % 25u == 0u) {
        state->classifier.range_cursor =
            (int16_t)state->secondary_history_count;
        const goodix_primitives_nadt_window_input window_input = {
            .primary_source = workspace->primary_raw,
            .secondary_source = workspace->primary_filtered,
            .tail_samples = workspace->configuration_markers,
            .tail_sample_count = state->primary_history_count,
            .range_samples = workspace->secondary_history,
            .range_sample_count = state->secondary_history_count,
            .sample_count = (int32_t)state->primary_history_count,
            .axis_x = shifted_x,
            .axis_y = shifted_y,
            .axis_z = shifted_z,
        };
        int32_t classified = state->classifier.current_result;
        if (!goodix_primitives_nadt_window_classify(
                plan->window_configuration, &window_input,
                plan->window_plan, &state->classifier,
                window_diagnostics, &classified)) {
            return false;
        }
        state->classifier.current_result = classified & INT32_C(3);
        output->window_ready = true;
        output->classification = (uint8_t)(
            (uint8_t)(uint32_t)classified |
            (state->result_flag ? UINT8_C(4) : UINT8_C(0)));
        output->quality = state->classifier.quality;
        goodix_primitives_nadt_stream_reset_batch(state);
        goodix_primitives_nadt_stream_compact(state, workspace);
    }
    if (!prepared || state->status == 1u) {
        output->classification = 0u;
    }
    if (!prepared) {
        output->quality = 50u;
    }
    if (output->classification == 2u || output->classification == 3u) {
        state->classifier.current_result = 0;
    }
    output->status = state->status;
    return true;
}

bool goodix_primitives_command_status_poll(
    const goodix_primitives_command_poll_ops *operations,
    uint32_t flags, int32_t *result) {
    if (operations == NULL || operations->command == NULL ||
            operations->register_read == NULL || operations->clock == NULL ||
            result == NULL) {
        return false;
    }
    if ((flags & UINT32_C(0x2000)) != 0u) {
        *result = operations->command(UINT32_C(0xA6), operations->context);
        return true;
    }
    const int32_t command_result =
        operations->command(UINT32_C(0xAE), operations->context);
    if (command_result != 0) {
        *result = command_result;
        return true;
    }
    const uint32_t started = operations->clock(operations->context);
    for (;;) {
        const int32_t status = operations->register_read(
            UINT32_C(0xAE), UINT32_C(1), operations->context);
        const uint32_t elapsed =
            operations->clock(operations->context) - started;
        if (elapsed >= UINT32_C(0x140)) {
            *result = status == 0 ? 0 : -3;
            return true;
        }
        if (status == 0) {
            *result = 0;
            return true;
        }
    }
}

int32_t goodix_primitives_algorithm_context_destroy(
    goodix_primitives_algorithm_context_ownership *context,
    goodix_primitives_release_fn release, void *release_context) {
    if (context == NULL || release == NULL) {
        return -1;
    }
    (void)goodix_primitives_release_if_present(
        context->owned_260, release, release_context);
    (void)goodix_primitives_release_if_present(
        context->owned_1c0, release, release_context);
    (void)goodix_primitives_release_if_present(
        context->owned_1dc, release, release_context);
    (void)goodix_primitives_release_if_present(
        context->owned_1f4, release, release_context);
    release(release_context, context);
    return 0;
}

int32_t goodix_primitives_record_family_teardown(
    goodix_primitives_record_family_ownership *ownership,
    goodix_primitives_release_fn release, void *release_context) {
    if (ownership == NULL || release == NULL) {
        return -1;
    }
    for (size_t index = 0u; index < 7u; ++index) {
        (void)goodix_primitives_release_if_present(
            ownership->descriptor_allocations[index], release,
            release_context);
    }
    (void)goodix_primitives_release_if_present(
        ownership->descriptor_allocations[8], release, release_context);
    (void)goodix_primitives_release_if_present(
        ownership->descriptor_allocations[7], release, release_context);
    for (size_t index = 0u; index < 9u; ++index) {
        (void)goodix_primitives_release_and_clear(
            &ownership->owned_slots[index], release, release_context);
    }
    for (size_t index = 0u; index < 7u; ++index) {
        (void)goodix_primitives_release_and_clear(
            &ownership->extended_owned_slots[index], release,
            release_context);
    }
    return 0;
}

bool goodix_primitives_float_median(
    const float *values, size_t count, float *scratch,
    size_t scratch_capacity, float *median) {
    if (median == NULL) {
        return false;
    }
    if (count == 0u) {
        *median = 0.0f;
        return true;
    }
    if (values == NULL || scratch == NULL || scratch_capacity < count ||
            !goodix_primitives_top_descending_strided(
                scratch, scratch_capacity, values, count, 1u, count,
                count)) {
        return false;
    }
    const size_t middle = count >> 1u;
    *median = (count & 1u) != 0u
        ? scratch[middle]
        : (scratch[middle - 1u] + scratch[middle]) * 0.5f;
    return true;
}

bool goodix_primitives_hr_mad_inlier_mask(
    const float *values, size_t count, int32_t deviation_multiplier,
    float *scratch, size_t scratch_capacity,
    uint8_t *mask, size_t mask_capacity) {
    if (values == NULL || scratch == NULL || mask == NULL || count == 0u ||
            count > (size_t)UINT8_MAX || scratch_capacity < count ||
            mask_capacity < count) {
        return false;
    }

    float median = 0.0f;
    if (!goodix_primitives_float_median(
            values, count, scratch, scratch_capacity, &median)) {
        return false;
    }
    for (size_t index = 0u; index < count; ++index) {
        const float difference = values[index] - median;
        scratch[index] = difference >= 0.0f ? difference : -difference;
    }
    float mean_absolute_deviation = 0.0f;
    if (!goodix_primitives_float_mean(
            scratch, count, &mean_absolute_deviation)) {
        return false;
    }
    const double threshold =
        (double)mean_absolute_deviation * 1.4826 *
        (double)deviation_multiplier;
    for (size_t index = 0u; index < count; ++index) {
        mask[index] = (double)scratch[index] <= threshold ? 1u : 0u;
    }
    return true;
}

bool goodix_primitives_dispatch_indexed_operation(
    uint32_t *record,
    const goodix_primitives_indexed_operation_fn
        operations[GOODIX_PRIMITIVES_STATE_COUNT],
    uintptr_t first, uintptr_t second, uintptr_t third,
    uintptr_t fourth, uintptr_t fifth, int32_t *result) {
    if (result == NULL) {
        return false;
    }
    if (record == NULL) {
        *result = 0;
        return true;
    }
    if (operations == NULL || record[0] >= GOODIX_PRIMITIVES_STATE_COUNT ||
            operations[record[0]] == NULL) {
        return false;
    }
    *result = operations[record[0]](
        record, first, second, third, fourth, fifth);
    return true;
}

bool goodix_primitives_nadt_graph_execute_veneer(
    goodix_primitives_seven_word_operation_fn execute,
    uintptr_t first, uintptr_t second, uintptr_t third, uintptr_t fourth,
    uintptr_t fifth, uintptr_t sixth, uintptr_t seventh, int32_t *result) {
    if (execute == NULL || result == NULL) {
        return false;
    }
    *result = execute(
        first, second, third, fourth, fifth, sixth, seventh);
    return true;
}

bool goodix_primitives_send_fixed_aa_pair(
    uint8_t selector, uint32_t first, uint32_t second,
    goodix_primitives_payload_send_fn send, void *send_context) {
    if (send == NULL) {
        return false;
    }
    const uint8_t payload[2] = {UINT8_C(0xAA), UINT8_C(0xAA)};
    send(selector, payload, UINT32_C(2), first, second, send_context);
    return true;
}

bool goodix_primitives_peak_quality_update(
    const int16_t *samples, size_t sample_count,
    int16_t *indices, size_t index_capacity, uint8_t *index_count,
    int32_t period, int32_t amplitude_scale, uint8_t *quality) {
    if (samples == NULL || indices == NULL || index_count == NULL ||
            quality == NULL || period <= 0 || period > INT16_MAX + 1 ||
            amplitude_scale <= 0 || *index_count >= index_capacity ||
            (size_t)(period - 1) >= sample_count) {
        return false;
    }
    for (size_t index = 0u; index < *index_count; ++index) {
        if (indices[index] < 0 || (size_t)indices[index] >= sample_count) {
            return false;
        }
    }
    indices[*index_count] = (int16_t)(period - 1);
    *index_count = (uint8_t)(*index_count + 1u);
    const size_t count = *index_count;
    float error_sum = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        const int32_t sample_index = indices[index];
        int32_t magnitude = samples[(size_t)sample_index];
        if (magnitude < 0) {
            magnitude = -magnitude;
        }
        const float position_ratio =
            (float)(sample_index + 1) / (float)period;
        const float amplitude_ratio =
            (float)magnitude / (float)amplitude_scale;
        error_sum += position_ratio <= amplitude_ratio
            ? amplitude_ratio - position_ratio
            : position_ratio - amplitude_ratio;
    }
    float error = count < 2u
        ? 0.5f
        : error_sum / (float)(count - 1u);
    if (!(error <= 0.5f)) {
        error = 0.5f;
    }
    *quality = (uint8_t)(100.0f - error * 100.0f * 2.0f);
    return true;
}

static int32_t goodix_primitives_u32_bits_to_i32(uint32_t value) {
    if (value <= (uint32_t)INT32_MAX) {
        return (int32_t)value;
    }
    return -1 - (int32_t)(UINT32_MAX - value);
}

static int16_t goodix_primitives_u16_bits_to_i16(uint16_t value) {
    if (value <= (uint16_t)INT16_MAX) {
        return (int16_t)value;
    }
    return (int16_t)(-1 - (int32_t)(UINT16_MAX - value));
}

static int32_t goodix_primitives_autocorrelation_sample(
    const void *samples, bool wide, size_t index) {
    return wide ? ((const int32_t *)samples)[index]
                : ((const int16_t *)samples)[index];
}

static bool goodix_primitives_autocorrelation_transform(
    const void *samples, bool wide, int16_t *output, size_t count,
    int32_t mean, int32_t scale,
    goodix_primitives_autocorrelation_state *state) {
    if (count == 0u) {
        return true;
    }
    if (samples == NULL || output == NULL || state == NULL || scale == 0 ||
            count > (size_t)INT32_MAX) {
        return false;
    }
    int32_t baseline = 0;
    for (size_t lag = 0u; lag < count; ++lag) {
        uint32_t correlation_bits = 0u;
        for (size_t index = lag; index < count; ++index) {
            const uint32_t left =
                (uint32_t)goodix_primitives_autocorrelation_sample(
                    samples, wide, index - lag) - (uint32_t)mean;
            const uint32_t right =
                (uint32_t)goodix_primitives_autocorrelation_sample(
                    samples, wide, index) - (uint32_t)mean;
            correlation_bits += left * right;
        }
        const int32_t correlation =
            goodix_primitives_u32_bits_to_i32(correlation_bits);
        if (lag == 0u) {
            baseline = correlation;
        }
        int16_t transformed = 0;
        if (baseline > 0) {
            const float denominator = (float)baseline / (float)scale;
            const float scaled = (float)correlation / denominator;
            if (!(scaled >= -2147483648.0f && scaled < 2147483648.0f)) {
                return false;
            }
            const int32_t converted = (int32_t)scaled;
            transformed = goodix_primitives_u16_bits_to_i16(
                (uint16_t)(uint32_t)converted);
            if (transformed == state->previous_output) {
                const int32_t adjusted = (int32_t)transformed +
                    (correlation < state->previous_correlation ? -1 : 1);
                transformed = goodix_primitives_u16_bits_to_i16(
                    (uint16_t)(uint32_t)adjusted);
            }
        }
        output[lag] = transformed;
        state->previous_correlation = correlation;
        state->previous_output = transformed;
    }
    for (size_t left = 0u; left < count / 2u; ++left) {
        const size_t right = count - left - 1u;
        const int16_t value = output[left];
        output[left] = output[right];
        output[right] = value;
    }
    return true;
}

bool goodix_primitives_i16_autocorrelation_transform(
    const int16_t *samples, int16_t *output, size_t count,
    int32_t mean, int32_t scale,
    goodix_primitives_autocorrelation_state *state) {
    return goodix_primitives_autocorrelation_transform(
        samples, false, output, count, mean, scale, state);
}

bool goodix_primitives_i32_autocorrelation_transform(
    const int32_t *samples, int16_t *output, size_t count,
    int32_t mean, int32_t scale,
    goodix_primitives_autocorrelation_state *state) {
    return goodix_primitives_autocorrelation_transform(
        samples, true, output, count, mean, scale, state);
}

bool goodix_primitives_reset_register_fields(
    const goodix_primitives_register_configuration_ops *operations) {
    if (operations == NULL || operations->write_register == NULL ||
            operations->write_bit_field == NULL) {
        return false;
    }
    operations->write_register(
        UINT16_C(0x0502), UINT16_C(0), operations->context);
    operations->write_bit_field(
        UINT16_C(0), UINT8_C(10), UINT8_C(10), UINT16_C(0),
        operations->context);
    return true;
}

bool goodix_primitives_dispatch_word_copy(
    const uint32_t *input, uint32_t *output,
    const goodix_primitives_word_dispatch_context *context,
    const goodix_primitives_indexed_operation_fn
        operations[GOODIX_PRIMITIVES_STATE_COUNT]) {
    if (input == NULL || output == NULL || context == NULL) {
        return false;
    }
    *output = *input;
    int32_t result = 0;
    if (!goodix_primitives_dispatch_indexed_operation(
            context->dispatch_record, operations, context->field_64,
            (uintptr_t)input, context->field_68, (uintptr_t)output,
            (uintptr_t)0, &result)) {
        return false;
    }
    return result != 0;
}

bool goodix_primitives_spo2_dispatch_logistic_score(
    goodix_primitives_spo2_score_context *context, float input,
    float *output, uint32_t history_scratch[4],
    const goodix_primitives_indexed_operation_fn
        operations[GOODIX_PRIMITIVES_STATE_COUNT],
    goodix_primitives_float_unary_fn exponential) {
    enum {
        HISTORY_COUNT = 4,
        WORKSPACE_BANK_COUNT = 99,
        WORKSPACE_TOTAL_COUNT = 198,
    };
    if (context == NULL || context->workspace == NULL ||
            context->workspace_count < WORKSPACE_TOTAL_COUNT ||
            context->recent_inputs == NULL ||
            context->recent_input_count < HISTORY_COUNT ||
            context->dispatch.dispatch_record == NULL || output == NULL ||
            history_scratch == NULL || operations == NULL ||
            exponential == NULL) {
        return false;
    }

    for (size_t index = 0u; index < HISTORY_COUNT; ++index) {
        history_scratch[index] = context->recent_inputs[index];
    }
    for (size_t index = HISTORY_COUNT - 1u; index != 0u; --index) {
        context->recent_inputs[index] = context->recent_inputs[index - 1u];
    }
    context->recent_inputs[0] = goodix_primitives_float_bits(input);

    /* floor(113.13999938964844) - floor(15.859999656677246) + 1
     * resolves both the stock destination offset and copied element count. */
    for (size_t index = 0u; index < WORKSPACE_BANK_COUNT; ++index) {
        context->workspace[WORKSPACE_BANK_COUNT + index] =
            context->workspace[index];
    }

    const goodix_primitives_graph_executor_input graph_input = {
        .workspace = context->workspace,
        .tail_input = context->recent_inputs,
        .workspace_count = context->workspace_count,
        .tail_input_count = context->recent_input_count,
    };
    float *output_pointer = output;
    int32_t result = 0;
    const bool dispatched = goodix_primitives_dispatch_indexed_operation(
        context->dispatch.dispatch_record, operations,
        context->dispatch.field_64, (uintptr_t)&graph_input,
        context->dispatch.field_68, (uintptr_t)&output_pointer,
        (uintptr_t)0, &result);
    for (size_t index = 0u; index < HISTORY_COUNT; ++index) {
        context->recent_inputs[index] = history_scratch[index];
    }
    if (!dispatched) {
        return false;
    }

    float exponent = -*output;
    if ((int32_t)goodix_primitives_float_bits(exponent) >=
            INT32_C(0x42B00000)) {
        exponent = 88.0f;
    }
    *output = (1.0f / (exponential(exponent) + 1.0f)) * 100.0f;
    if (result != 0) {
        *output = 0.0f;
        return true;
    }
    return false;
}

uint32_t goodix_primitives_timed_dispatch_scaled_output(
    uintptr_t input, size_t slot, float *output,
    const goodix_primitives_timed_dispatch_context *context,
    const goodix_primitives_indexed_operation_fn
        operations[GOODIX_PRIMITIVES_STATE_COUNT]) {
    if (output == NULL || context == NULL ||
            !goodix_primitives_update_elapsed_slot(
                context->elapsed_state, slot) ||
            !goodix_primitives_clear_mode_buffers(
                context->mode_buffers, context->mode)) {
        return UINT32_C(1);
    }

    float *output_pointer = output;
    int32_t result = 0;
    if (!goodix_primitives_dispatch_indexed_operation(
            context->dispatch_record, operations, context->field_64,
            input, context->field_68, (uintptr_t)&output_pointer,
            (uintptr_t)0, &result)) {
        return UINT32_C(1);
    }
    if (result != 0) {
        *output = 0.0f;
        return UINT32_C(1);
    }

    /* The stock floors the binary64 literal 15.859999656677246 and converts
     * the resulting integer 15 back to Float32 before this exact sequence. */
    float scaled = 15.0f + *output;
    scaled *= 60.0f;
    scaled *= 25.0f;
    scaled /= 3.0f;
    scaled *= 0.00390625f;
    *output = scaled;
    return UINT32_C(0);
}

float goodix_primitives_round_float_half_away_from_zero(float value) {
    union {
        float f;
        uint32_t u;
    } converted = {.f = value};
    const uint32_t sign = converted.u & UINT32_C(0x80000000);
    const uint32_t magnitude = converted.u & UINT32_C(0x7FFFFFFF);
    const uint32_t exponent = magnitude >> 23u;

    /* All finite values at or above 2^23 are already integral. Preserve
     * infinities and NaNs just as the stock floor/ceil path does. */
    if (exponent >= UINT32_C(150)) {
        return value;
    }

    if (exponent < UINT32_C(126)) {
        /* The stock nonpositive branch maps both signed zero inputs through
         * ceil(-0.5), whose result is negative zero. */
        converted.u = magnitude == 0u
            ? UINT32_C(0x80000000)
            : sign;
        return converted.f;
    }
    if (exponent == UINT32_C(126)) {
        converted.u = sign | UINT32_C(0x3F800000);
        return converted.f;
    }

    const uint32_t fractional_bits = UINT32_C(150) - exponent;
    const uint32_t fractional_mask =
        (UINT32_C(1) << fractional_bits) - UINT32_C(1);
    if ((magnitude & fractional_mask) == 0u) {
        return value;
    }
    const uint32_t half = UINT32_C(1) << (fractional_bits - 1u);
    converted.u = sign | ((magnitude + half) & ~fractional_mask);
    return converted.f;
}

int32_t goodix_primitives_processing_context_destroy(
    goodix_primitives_record_family_ownership *record_family,
    goodix_primitives_processing_context_ownership *context,
    const goodix_primitives_state_handler_fn
        handlers[GOODIX_PRIMITIVES_STATE_COUNT],
    goodix_primitives_release_fn release, void *release_context) {
    if (record_family == NULL || context == NULL || handlers == NULL ||
            release == NULL) {
        return -1;
    }
    if (goodix_primitives_record_family_teardown(
            record_family, release, release_context) != 0) {
        return -1;
    }
    release(release_context, record_family);
    if (!goodix_primitives_dispatch_state(context->state_6c, handlers) ||
            !goodix_primitives_dispatch_state(context->state_70, handlers) ||
            !goodix_primitives_dispatch_state(context->state_84, handlers)) {
        return -1;
    }
    (void)goodix_primitives_release_and_clear(
        &context->owned_b0, release, release_context);
    (void)goodix_primitives_release_and_clear(
        &context->owned_bc, release, release_context);
    (void)goodix_primitives_release_and_clear(
        &context->owned_cc, release, release_context);
    (void)goodix_primitives_release_and_clear(
        &context->owned_d8, release, release_context);
    release(release_context, context);
    return 0;
}

bool goodix_primitives_strided_sample_standard_deviation(
    const float *values, size_t value_count, size_t stride, size_t count,
    goodix_primitives_float_unary_fn square_root, float *result) {
    if (values == NULL || square_root == NULL || result == NULL ||
            stride == 0u || count < 2u ||
            (count - 1u) > (SIZE_MAX - 1u) / stride ||
            (count - 1u) * stride >= value_count) {
        return false;
    }
    float mean = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        const float ordinal = (float)(index + 1u);
        mean += (values[index * stride] - mean) / ordinal;
    }
    float moment = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        const float difference = values[index * stride] - mean;
        const float ordinal = (float)(index + 1u);
        moment += (difference * difference - moment) / ordinal;
    }
    const float count_float = (float)count;
    const float variance =
        (count_float / (float)(count - 1u)) * moment;
    *result = square_root(variance);
    return true;
}

bool goodix_primitives_float_buffer_incremental_standard_deviation(
    const goodix_primitives_float_buffer *buffer,
    goodix_primitives_float_unary_fn square_root, float *result) {
    if (buffer == NULL || buffer->count == 0u ||
            buffer->count > buffer->capacity) {
        return false;
    }
    return goodix_primitives_strided_sample_standard_deviation(
        buffer->values, (size_t)buffer->capacity, 1u,
        (size_t)buffer->count, square_root, result);
}

bool goodix_primitives_float_buffer_standard_deviation(
    const goodix_primitives_float_buffer *buffer,
    goodix_primitives_float_unary_fn square_root, float *result) {
    if (buffer == NULL) {
        return false;
    }
    return goodix_primitives_sample_standard_deviation(
        buffer->values, (size_t)buffer->count, square_root, result);
}

bool goodix_primitives_hr_count_mean_outliers(
    const goodix_primitives_float_buffer *buffer, size_t scan_count,
    float maximum_threshold, float minimum_threshold,
    float deviation_multiplier,
    goodix_primitives_float_unary_fn square_root,
    uint32_t *outlier_count, uint32_t *tail_outlier_count) {
    if (buffer == NULL || square_root == NULL || outlier_count == NULL ||
            tail_outlier_count == NULL || buffer->count > buffer->capacity ||
            scan_count > (size_t)buffer->capacity ||
            (buffer->capacity != 0u && buffer->values == NULL) ||
            scan_count > (size_t)INT32_MAX) {
        return false;
    }

    float mean = 0.0f;
    float deviation = 0.0f;
    (void)goodix_primitives_float_buffer_mean(buffer, &mean);
    (void)goodix_primitives_float_buffer_standard_deviation(
        buffer, square_root, &deviation);
    const float scaled = deviation_multiplier * deviation;
    const float lower_clamped = scaled < minimum_threshold
        ? minimum_threshold : scaled;
    const float threshold = lower_clamped < maximum_threshold
        ? lower_clamped : maximum_threshold;

    uint8_t total = 0u;
    uint8_t tail = 0u;
    for (size_t index = 0u; index < scan_count; ++index) {
        float distance = buffer->values[index] - mean;
        if (distance < 0.0f) {
            distance = -distance;
        }
        if (distance > threshold) {
            ++total;
            if (index >= 100u) {
                ++tail;
            }
        }
    }
    *outlier_count = (uint32_t)total;
    *tail_outlier_count = (uint32_t)tail;
    return true;
}

static bool variance_or_zero(const float *values, size_t count,
                             size_t divisor, float *result) {
    if (result == NULL || (values == NULL && count != 0u) || divisor == 0u) {
        return false;
    }
    if (count == 0u) {
        *result = 0.0f;
        return true;
    }
    const float mean = goodix_primitives_float_mean_or_zero(values, count);
    float squared_difference_sum = 0.0f;
    for (size_t index = 0u; index < count; ++index) {
        const float difference = values[index] - mean;
        squared_difference_sum += difference * difference;
    }
    *result = squared_difference_sum / (float)divisor;
    return true;
}

bool goodix_primitives_sample_variance_or_zero(
    const float *values, size_t count, float *result) {
    return variance_or_zero(
        values, count, count > 1u ? count - 1u : 1u, result);
}

bool goodix_primitives_population_variance_or_zero(
    const float *values, size_t count, float *result) {
    return variance_or_zero(
        values, count, count == 0u ? 1u : count, result);
}

bool goodix_primitives_sample_standard_deviation_or_zero(
    const float *values, size_t count,
    goodix_primitives_float_unary_fn square_root, float *result) {
    float variance = 0.0f;
    if (square_root == NULL || result == NULL ||
            !goodix_primitives_sample_variance_or_zero(
                values, count, &variance)) {
        return false;
    }
    *result = square_root(variance);
    return true;
}

bool goodix_primitives_population_standard_deviation_or_zero(
    const float *values, size_t count,
    goodix_primitives_float_unary_fn square_root, float *result) {
    float variance = 0.0f;
    if (square_root == NULL || result == NULL ||
            !goodix_primitives_population_variance_or_zero(
                values, count, &variance)) {
        return false;
    }
    *result = square_root(variance);
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

bool goodix_primitives_replace_far_from_median(
    float *values, size_t count, int32_t spread_factor,
    float *sort_scratch, size_t scratch_capacity) {
    if (values == NULL || sort_scratch == NULL || values == sort_scratch ||
            count == 0u || count > (size_t)UINT8_MAX ||
            scratch_capacity < count) {
        return false;
    }
    for (size_t index = 0u; index < count; ++index) {
        sort_scratch[index] = values[index];
    }
    if (!goodix_primitives_sort_floats(sort_scratch, count)) {
        return false;
    }

    float lower_quartile = 0.0f;
    float upper_quartile = 0.0f;
    float median = 0.0f;
    if (!goodix_primitives_percentile_lookup(
            sort_scratch, count, UINT32_C(25), &lower_quartile) ||
            !goodix_primitives_percentile_lookup(
                sort_scratch, count, UINT32_C(75), &upper_quartile) ||
            !goodix_primitives_percentile_lookup(
                sort_scratch, count, UINT32_C(50), &median)) {
        return false;
    }
    float spread = upper_quartile - lower_quartile;
    if ((int32_t)goodix_primitives_float_bits(spread) <
            (int32_t)UINT32_C(0x40A00000)) {
        spread = 5.0f;
    }
    const float threshold = spread * (float)spread_factor;
    for (size_t index = 0u; index < count; ++index) {
        float distance = values[index] - median;
        if (distance < 0.0f) {
            distance = -distance;
        }
        if (distance > threshold) {
            values[index] = median;
        }
    }
    return true;
}

bool goodix_primitives_insertion_sort_floats(float *values, size_t count) {
    if ((values == NULL && count != 0u) || count > (size_t)INT32_MAX) {
        return false;
    }
    for (size_t index = 1u; index < count; ++index) {
        const float value = values[index];
        size_t insertion = index;
        while (insertion != 0u) {
            const float previous = values[insertion - 1u];
            if (previous <= value) {
                break;
            }
            values[insertion] = previous;
            --insertion;
        }
        values[insertion] = value;
    }
    return true;
}

bool goodix_primitives_top_descending_strided(
    float *output, size_t output_capacity, const float *source,
    size_t source_value_count, size_t stride, size_t sample_count,
    size_t selected_count) {
    if (output == NULL || source == NULL || stride == 0u ||
            selected_count == 0u || sample_count == 0u ||
            selected_count > sample_count ||
            output_capacity < selected_count ||
            sample_count > (size_t)UINT32_MAX ||
            (sample_count - 1u) > (SIZE_MAX - 1u) / stride ||
            (sample_count - 1u) * stride >= source_value_count) {
        return false;
    }
    output[0] = source[0];
    size_t populated = 1u;
    float smallest = output[0];
    for (size_t source_index = 1u; source_index < sample_count;
            ++source_index) {
        const float value = source[source_index * stride];
        size_t insertion;
        if (populated < selected_count) {
            ++populated;
            insertion = populated;
        } else if (!(smallest < value)) {
            continue;
        } else {
            insertion = populated;
        }
        while (--insertion != 0u) {
            const float previous = output[insertion - 1u];
            if (value < previous) {
                break;
            }
            output[insertion] = previous;
        }
        output[insertion] = value;
        smallest = output[populated - 1u];
    }
    return true;
}

bool goodix_primitives_i16_local_extrema_indices(
    const int16_t *values, size_t count,
    int16_t *maximum_indices, size_t maximum_capacity,
    uint8_t *maximum_count, int16_t *minimum_indices,
    size_t minimum_capacity, uint8_t *minimum_count) {
    if ((values == NULL && count > 2u) ||
            count > (size_t)INT16_MAX + 2u) {
        return false;
    }
    size_t maxima = 0u;
    size_t minima = 0u;
    if (maximum_indices != NULL) {
        for (size_t index = 1u; index + 1u < count; ++index) {
            if (values[index - 1u] < values[index] &&
                    values[index + 1u] < values[index]) {
                ++maxima;
            }
        }
    }
    if (minimum_indices != NULL) {
        for (size_t index = 1u; index + 1u < count; ++index) {
            if (values[index] < values[index - 1u] &&
                    values[index] < values[index + 1u]) {
                ++minima;
            }
        }
    }
    if (maxima > maximum_capacity || minima > minimum_capacity ||
            maxima > (size_t)UINT8_MAX || minima > (size_t)UINT8_MAX) {
        return false;
    }
    size_t maximum_index = 0u;
    size_t minimum_index = 0u;
    for (size_t index = 1u; index + 1u < count; ++index) {
        if (maximum_indices != NULL &&
                values[index - 1u] < values[index] &&
                values[index + 1u] < values[index]) {
            maximum_indices[maximum_index++] = (int16_t)index;
        }
        if (minimum_indices != NULL &&
                values[index] < values[index - 1u] &&
                values[index] < values[index + 1u]) {
            minimum_indices[minimum_index++] = (int16_t)index;
        }
    }
    if (maximum_count != NULL) {
        *maximum_count = (uint8_t)maxima;
    }
    if (minimum_count != NULL) {
        *minimum_count = (uint8_t)minima;
    }
    return true;
}

static int16_t goodix_primitives_positive_f32_to_nearest_i16(float value) {
    int32_t rounded = (int32_t)value;
    const float fraction = value - (float)rounded;
    if (fraction > 0.5f ||
            (fraction == 0.5f && (rounded & INT32_C(1)) != 0)) {
        ++rounded;
    }
    return goodix_primitives_u16_as_i16((uint16_t)rounded);
}

static bool goodix_primitives_i32_within_ten(int32_t value) {
    return value >= -10 && value <= 10;
}

bool goodix_primitives_nadt_auxiliary_state_classify(
    int16_t *values, size_t count,
    const goodix_primitives_nadt_auxiliary_configuration *configuration,
    bool transition_enabled,
    goodix_primitives_nadt_auxiliary_state *state,
    goodix_primitives_nadt_auxiliary_workspace *workspace,
    goodix_primitives_nadt_auxiliary_diagnostics *diagnostics,
    goodix_primitives_float_unary_fn square_root, uint32_t *result) {
    if (configuration == NULL || state == NULL || result == NULL) {
        return false;
    }
    uint32_t classified = state->current_result;
    if (!configuration->enabled) {
        *result = classified;
        return true;
    }
    if (state->processing) {
        return false;
    }
    if (count < GOODIX_PRIMITIVES_NADT_AUXILIARY_WINDOW_VALUES) {
        *result = classified;
        return true;
    }
    if (values == NULL) {
        return false;
    }
    int16_t *const tail = values +
        (count - GOODIX_PRIMITIVES_NADT_AUXILIARY_WINDOW_VALUES);
    int16_t maximum = tail[0];
    int16_t minimum = maximum;
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_AUXILIARY_WINDOW_VALUES;
            ++index) {
        if (maximum <= tail[index]) {
            maximum = tail[index];
        }
        if (tail[index] <= minimum) {
            minimum = tail[index];
        }
    }
    const int16_t range = goodix_primitives_u16_as_i16(
        (uint16_t)((uint16_t)maximum - (uint16_t)minimum));
    if (range > configuration->range_threshold &&
            (workspace == NULL || square_root == NULL)) {
        return false;
    }
    if (diagnostics != NULL) {
        diagnostics->range = range;
    }
    if (range > configuration->range_threshold) {
        float deviation = 0.0f;
        if (!goodix_primitives_i16_sample_standard_deviation(
                tail, GOODIX_PRIMITIVES_NADT_AUXILIARY_WINDOW_VALUES,
                square_root, &deviation)) {
            return false;
        }
        const int16_t rounded_deviation =
            goodix_primitives_positive_f32_to_nearest_i16(deviation);
        size_t unique_count = 1u;
        for (size_t index = 1u;
                index < GOODIX_PRIMITIVES_NADT_AUXILIARY_WINDOW_VALUES;
                ++index) {
            if (tail[index] != tail[index - 1u]) {
                tail[unique_count++] = tail[index];
            }
        }
        uint8_t maximum_count = 0u;
        uint8_t minimum_count = 0u;
        if (!goodix_primitives_i16_local_extrema_indices(
                tail, unique_count,
                workspace->maximum_indices,
                GOODIX_PRIMITIVES_NADT_AUXILIARY_EXTREMA_CAPACITY,
                &maximum_count, workspace->minimum_indices,
                GOODIX_PRIMITIVES_NADT_AUXILIARY_EXTREMA_CAPACITY,
                &minimum_count)) {
            return false;
        }
        const int32_t half_range = (int32_t)range / 2;
        size_t retained_maxima = 0u;
        for (size_t index = 0u; index < maximum_count; ++index) {
            const int16_t position = workspace->maximum_indices[index];
            if ((int32_t)tail[position] - (int32_t)minimum >=
                    half_range) {
                workspace->maximum_indices[retained_maxima++] = position;
            }
        }
        maximum_count = (uint8_t)retained_maxima;
        size_t retained_minima = 0u;
        for (size_t index = 0u; index < minimum_count; ++index) {
            const int16_t position = workspace->minimum_indices[index];
            if ((int32_t)maximum - (int32_t)tail[position] >=
                    half_range) {
                workspace->minimum_indices[retained_minima++] = position;
            }
        }
        minimum_count = (uint8_t)retained_minima;

        int16_t maximum_mean = 0;
        int16_t minimum_mean = 0;
        if (maximum_count != 0u &&
                !goodix_primitives_indexed_i16_trimmed_mean(
                    tail, unique_count,
                    workspace->maximum_indices, maximum_count,
                    &maximum_mean)) {
            return false;
        }
        if (minimum_count != 0u &&
                !goodix_primitives_indexed_i16_trimmed_mean(
                    tail, unique_count,
                    workspace->minimum_indices, minimum_count,
                    &minimum_mean)) {
            return false;
        }
        const bool separated_means =
            (int32_t)maximum_mean - (int32_t)minimum_mean > 100;
        uint8_t clustered_maxima = 0u;
        for (size_t index = 0u; index < maximum_count; ++index) {
            const int16_t sample = tail[
                workspace->maximum_indices[index]];
            if ((int32_t)maximum - (int32_t)sample < 11 ||
                    (separated_means && goodix_primitives_i32_within_ten(
                        (int32_t)maximum_mean - (int32_t)sample))) {
                ++clustered_maxima;
            }
        }
        uint8_t clustered_minima = 0u;
        for (size_t index = 0u; index < minimum_count; ++index) {
            const int16_t sample = tail[
                workspace->minimum_indices[index]];
            if ((int32_t)sample - (int32_t)minimum < 11 ||
                    (separated_means && goodix_primitives_i32_within_ten(
                        (int32_t)minimum_mean - (int32_t)sample))) {
                ++clustered_minima;
            }
        }
        if (diagnostics != NULL) {
            diagnostics->maximum_count = maximum_count;
        }
        if (configuration->deviation_threshold < rounded_deviation &&
                configuration->required_extrema_count <= maximum_count &&
                configuration->required_extrema_count <= minimum_count &&
                (maximum_count >> 1u) <= clustered_maxima &&
                (minimum_count >> 1u) <= clustered_minima) {
            state->consecutive_matches =
                (uint8_t)(state->consecutive_matches + 1u);
        } else {
            state->consecutive_matches = 0u;
        }
    } else {
        state->consecutive_matches = 0u;
    }
    if (state->consecutive_matches >=
            configuration->required_consecutive_windows &&
            transition_enabled) {
        classified = 2u;
        state->mode = 5u;
        state->consecutive_matches = 0u;
    }
    *result = classified;
    return true;
}

bool goodix_primitives_grouped_row_weighted_sums(
    const float *coefficients, size_t coefficient_value_count,
    size_t group_count, size_t coefficient_count,
    const float *values, size_t value_count, size_t row_count,
    float *output, size_t output_count) {
    if (coefficients == NULL || values == NULL || output == NULL ||
            group_count == 0u || coefficient_count == 0u ||
            row_count == 0u ||
            group_count > SIZE_MAX / coefficient_count ||
            group_count * coefficient_count > coefficient_value_count ||
            coefficient_count > SIZE_MAX / row_count ||
            coefficient_count * row_count > value_count ||
            group_count > SIZE_MAX / row_count ||
            group_count * row_count > output_count ||
            group_count > (size_t)UINT16_MAX ||
            coefficient_count > (size_t)UINT16_MAX ||
            row_count > (size_t)UINT16_MAX) {
        return false;
    }
    for (size_t group = 0u; group < group_count; ++group) {
        for (size_t row = 0u; row < row_count; ++row) {
            float sum = 0.0f;
            for (size_t coefficient = 0u;
                    coefficient < coefficient_count; ++coefficient) {
                sum += coefficients[group * coefficient_count + coefficient] *
                       values[row + coefficient * row_count];
            }
            output[group * row_count + row] = sum;
        }
    }
    return true;
}

bool goodix_primitives_cardinal_spline_point(
    float parameter, const goodix_primitives_point2f control_points[4],
    int32_t shape_parameter, goodix_primitives_point2f *output) {
    if (control_points == NULL || output == NULL) {
        return false;
    }

    /* 0x48018 forms [t^3, t^2, t, 1] and multiplies it by this recovered
     * row-major coefficient matrix before applying the four point rows:
     *
     *   -h,  2h, -h, 0
     *  2-h, h-3,  0, 1
     *  h-2, 3-2h, h, 0
     *     h,  -h,  0, 0
     *
     * where h = (1 - float(shape_parameter)) / 2.  The temporaries retain
     * the stock multiply/add order used by 0x34490. */
    const float shape = (float)shape_parameter;
    const float one_minus_shape = 1.0f - shape;
    const float half = one_minus_shape * 0.5f;
    const float parameter_squared = parameter * parameter;
    const float parameter_cubed = parameter_squared * parameter;
    const float polynomial[4] = {
        parameter_cubed, parameter_squared, parameter, 1.0f,
    };
    const float matrix[16] = {
        -half, 2.0f - half, half - 2.0f, half,
        half * 2.0f, half - 3.0f, 3.0f - half * 2.0f, -half,
        -half, 0.0f, half, 0.0f,
        0.0f, 1.0f, 0.0f, 0.0f,
    };
    float weights[4];
    for (size_t column = 0u; column < 4u; ++column) {
        float sum = 0.0f;
        for (size_t row = 0u; row < 4u; ++row) {
            sum += polynomial[row] * matrix[row * 4u + column];
        }
        weights[column] = sum;
    }

    float x = 0.0f;
    float y = 0.0f;
    for (size_t index = 0u; index < 4u; ++index) {
        x += weights[index] * control_points[index].x;
        y += weights[index] * control_points[index].y;
    }
    output->x = x;
    output->y = y;
    return true;
}

bool goodix_primitives_sample_cardinal_spline(
    const goodix_primitives_point2f control_points[4],
    int32_t shape_parameter, size_t subdivisions,
    goodix_primitives_point2f *output, size_t output_capacity) {
    if (control_points == NULL || output == NULL ||
            subdivisions > (size_t)INT32_MAX ||
            output_capacity < subdivisions + 1u) {
        return false;
    }
    if (!goodix_primitives_cardinal_spline_point(
            0.0f, control_points, shape_parameter, &output[0])) {
        return false;
    }
    if (subdivisions == 0u) {
        return true;
    }
    const float reciprocal = 1.0f / (float)(int32_t)subdivisions;
    for (size_t index = 1u; index <= subdivisions; ++index) {
        const float parameter = (float)(int32_t)index * reciprocal;
        if (!goodix_primitives_cardinal_spline_point(
                parameter, control_points, shape_parameter,
                &output[index])) {
            return false;
        }
    }
    return true;
}

static size_t goodix_primitives_hr_extrema_subdivisions(uint32_t mode) {
    switch (mode) {
        case 0u:
            return 40u;
        case 1u:
            return 20u;
        case 2u:
            return 10u;
        case 3u:
            return 5u;
        default:
            return 0u;
    }
}

static bool goodix_primitives_hr_extrema_refine(
    const goodix_primitives_hr_extrema_curve *curve,
    float fourth, float third, float previous, float latest,
    size_t subdivisions, bool select_minimum,
    goodix_primitives_hr_extrema_workspace *workspace,
    goodix_primitives_point2f *selected) {
    if (curve == NULL || workspace == NULL || selected == NULL ||
            subdivisions >= GOODIX_PRIMITIVES_HR_EXTREMA_SPLINE_POINTS) {
        return false;
    }
    const goodix_primitives_point2f controls[4] = {
        {curve->x[0], fourth},
        {curve->x[1], third},
        {curve->x[2], previous},
        {curve->x[3], latest},
    };
    if (!goodix_primitives_sample_cardinal_spline(
            controls, 0, subdivisions, workspace->spline,
            GOODIX_PRIMITIVES_HR_EXTREMA_SPLINE_POINTS)) {
        return false;
    }
    *selected = workspace->spline[0];
    for (size_t index = 1u; index <= subdivisions; ++index) {
        const goodix_primitives_point2f candidate = workspace->spline[index];
        if ((select_minimum && candidate.y < selected->y) ||
                (!select_minimum && candidate.y > selected->y)) {
            *selected = candidate;
        }
    }
    return true;
}

bool goodix_primitives_hr_extrema_tracker_update(
    const goodix_primitives_float_buffer *history,
    int32_t signal_mode, uint32_t interpolation_mode,
    int32_t position_base, int32_t period,
    goodix_primitives_hr_extrema_tracker *tracker,
    const goodix_primitives_hr_extrema_curve *trough_curve,
    const goodix_primitives_hr_extrema_curve *peak_curve,
    goodix_primitives_hr_extrema_workspace *workspace) {
    if (history == NULL || tracker == NULL || period <= 0 ||
            history->count > history->capacity ||
            (history->count != 0u && history->values == NULL)) {
        return false;
    }
    if (history->count != history->capacity) {
        return true;
    }
    if (history->count < 2u) {
        return false;
    }
    if (signal_mode == 1 &&
            (history->count < 4u || trough_curve == NULL ||
             peak_curve == NULL || workspace == NULL)) {
        return false;
    }

    const int32_t remainder = tracker->sample_index % period;
    if (remainder == 0) {
        const float period_float = (float)period;
        tracker->peak_position -= period_float;
        tracker->trough_position -= period_float;
    }
    const float latest = history->values[history->count - 1u];
    const float previous = history->values[history->count - 2u];

    if (tracker->direction_state == 2) {
        if (latest < previous) {
            tracker->direction_state = 0;
        } else if (latest > previous) {
            tracker->direction_state = 1;
        }
        return true;
    }

    if (tracker->direction_state == 0) {
        if (!(latest > previous)) {
            return true;
        }
        tracker->direction_state = 1;
        tracker->trough_position =
            ((float)position_base - (float)period) +
            (float)remainder - 1.0f;
        tracker->trough_value = previous;
        if (tracker->pair_ready == 1u) {
            if (signal_mode == 1) {
                if (history->count < 3u) {
                    return false;
                }
                const float third = history->values[history->count - 3u];
                if (third < latest) {
                    if (history->count < 4u) {
                        return false;
                    }
                    const float fourth =
                        history->values[history->count - 4u];
                    const size_t subdivisions =
                        goodix_primitives_hr_extrema_subdivisions(
                            interpolation_mode);
                    goodix_primitives_point2f selected;
                    if (!goodix_primitives_hr_extrema_refine(
                            trough_curve, fourth, third, previous, latest,
                            subdivisions, true, workspace, &selected)) {
                        return false;
                    }
                    tracker->trough_position +=
                        selected.x - trough_curve->x[2];
                    tracker->trough_value = selected.y;
                }
            }
            tracker->fall_amplitude =
                tracker->peak_value - tracker->trough_value;
            tracker->fall_span =
                tracker->trough_position - tracker->peak_position;
            tracker->fall_complete = 1u;
        }
        tracker->pair_ready = 1u;
        return true;
    }

    if (tracker->direction_state != 1) {
        return true;
    }
    if (!(latest < previous)) {
        return true;
    }
    tracker->direction_state = 0;
    if (tracker->pair_ready != 1u) {
        return true;
    }
    tracker->peak_position =
        ((float)position_base - (float)period) + (float)remainder;
    tracker->peak_value = previous;
    if (signal_mode == 1) {
        if (history->count < 3u) {
            return false;
        }
        const float third = history->values[history->count - 3u];
        if (latest < third) {
            if (history->count < 4u) {
                return false;
            }
            const float fourth = history->values[history->count - 4u];
            const size_t subdivisions =
                goodix_primitives_hr_extrema_subdivisions(
                    interpolation_mode);
            goodix_primitives_point2f selected;
            if (!goodix_primitives_hr_extrema_refine(
                    peak_curve, fourth, third, previous, latest,
                    subdivisions, false, workspace, &selected)) {
                return false;
            }
            tracker->peak_position += selected.x - peak_curve->x[2];
            tracker->peak_value = selected.y;
        }
    }
    tracker->rise_amplitude = tracker->peak_value - tracker->trough_value;
    tracker->rise_span = tracker->peak_position - tracker->trough_position;
    return true;
}

static void goodix_primitives_spo2_diagnostic_emit(
    const goodix_primitives_spo2_diagnostic_plan *plan,
    const char *format, const int32_t *values, size_t value_count) {
    if (plan->formatted_emit != NULL) {
        plan->formatted_emit(
            plan->formatted_context, format, values, value_count);
    }
    if (plan->direct_emit != NULL) {
        plan->direct_emit(plan->direct_context, format, values, value_count);
    }
}

bool goodix_primitives_spo2_input_diagnostics_emit(
    const goodix_primitives_spo2_diagnostic_configuration *configuration,
    const goodix_primitives_spo2_diagnostic_input *input,
    const goodix_primitives_spo2_diagnostic_plan *plan) {
    if (configuration == NULL || plan == NULL) {
        return false;
    }
    const bool has_sink = plan->formatted_emit != NULL ||
                          plan->direct_emit != NULL;
    size_t enable_count = 0u;
    if (input != NULL) {
        enable_count = ((size_t)input->total_channel_count * 3u + 7u) / 8u;
        if (input->ppg_count < input->total_channel_count ||
                input->enable_flag_count < enable_count ||
                (input->total_channel_count != 0u && input->ppg == NULL) ||
                (enable_count != 0u && input->enable_flags == NULL) ||
                (has_sink && plan->memory_available == NULL)) {
            return false;
        }
    }
    if (!has_sink) {
        return true;
    }

    int32_t values[3];
    if (configuration->timestamp == 0u) {
        values[0] = (int32_t)configuration->mode;
        goodix_primitives_spo2_diagnostic_emit(
            plan, "alg:mode=%d\n", values, 1u);
        values[0] = (int32_t)configuration->sample_frequency;
        goodix_primitives_spo2_diagnostic_emit(
            plan, "alg:fs=%d\n", values, 1u);
        values[0] = (int32_t)configuration->valid_channel_count;
        goodix_primitives_spo2_diagnostic_emit(
            plan, "alg:valid_ch_num=%d\n", values, 1u);
        values[0] = configuration->earliest_output_time;
        goodix_primitives_spo2_diagnostic_emit(
            plan, "alg:earliest_output_time=%d\n", values, 1u);
        values[0] = configuration->latest_output_time;
        goodix_primitives_spo2_diagnostic_emit(
            plan, "alg:latest_output_time=%d\n", values, 1u);
        values[0] = configuration->sigma;
        goodix_primitives_spo2_diagnostic_emit(
            plan, "alg:sigma=%d\n", values, 1u);
        values[0] = configuration->raw_ppg_scale;
        goodix_primitives_spo2_diagnostic_emit(
            plan, "alg:raw_ppg_scale=%d\n", values, 1u);
        values[0] = configuration->delay_time;
        goodix_primitives_spo2_diagnostic_emit(
            plan, "alg:delay_time=%d\n", values, 1u);
        values[0] = configuration->valid_score_scale;
        goodix_primitives_spo2_diagnostic_emit(
            plan, "alg:valid_score_scale=%d\n", values, 1u);
    }
    if (input == NULL) {
        return true;
    }

    values[0] = goodix_primitives_u32_as_i32(configuration->timestamp);
    goodix_primitives_spo2_diagnostic_emit(
        plan, "alg:ts=%d\n", values, 1u);

    /* Stock calls GdMemGetFreeSize independently for each enabled route. */
    if (plan->formatted_emit != NULL) {
        values[0] = goodix_primitives_u32_as_i32(
            plan->memory_available(plan->memory_context));
        plan->formatted_emit(
            plan->formatted_context, "alg:mem=%d\n", values, 1u);
    }
    if (plan->direct_emit != NULL) {
        values[0] = goodix_primitives_u32_as_i32(
            plan->memory_available(plan->memory_context));
        plan->direct_emit(
            plan->direct_context, "alg:mem=%d\n", values, 1u);
    }

    values[0] = configuration->last_heart_rate;
    goodix_primitives_spo2_diagnostic_emit(
        plan, "alg:lhr=%d\n", values, 1u);
    values[0] = (int32_t)input->total_channel_count;
    goodix_primitives_spo2_diagnostic_emit(
        plan, "alg:total_ch_num=%d\n", values, 1u);
    for (size_t index = 0u; index < input->total_channel_count; ++index) {
        values[0] = (int32_t)index;
        values[1] = input->ppg[index];
        goodix_primitives_spo2_diagnostic_emit(
            plan, "alg:%d ppg=%d\n", values, 2u);
    }
    for (size_t index = 0u; index < enable_count; ++index) {
        values[0] = (int32_t)input->enable_flags[index];
        goodix_primitives_spo2_diagnostic_emit(
            plan, "alg:en=%d\n", values, 1u);
    }
    for (size_t index = 0u; index < 3u; ++index) {
        values[index] = input->accelerometer[index];
    }
    goodix_primitives_spo2_diagnostic_emit(
        plan, "alg:c3Xm=%d,y=%d,z=%d\n", values, 3u);
    for (size_t index = 0u; index < 3u; ++index) {
        values[index] = input->gyroscope[index];
    }
    goodix_primitives_spo2_diagnostic_emit(
        plan, "alg:groy_x=%d,groy_y=%d,groy_z=%d\n\n", values, 3u);
    return true;
}

bool goodix_primitives_align_event_pairs(
    int32_t mode, const goodix_primitives_event_pair_source *source,
    int32_t *primary_output, int32_t *secondary_output,
    size_t output_capacity, size_t *produced_count) {
    if (source == NULL || produced_count == NULL ||
            source->primary_start > source->primary_count ||
            source->secondary_start > source->secondary_count ||
            (source->primary_count != 0u && source->primary == NULL) ||
            (source->secondary_count != 0u && source->secondary == NULL)) {
        return false;
    }
    const size_t required =
        (size_t)source->primary_count - (size_t)source->primary_start;
    if (output_capacity < required ||
            (required != 0u &&
             (primary_output == NULL || secondary_output == NULL))) {
        return false;
    }
    const uint32_t offset =
        (UINT32_C(5) - (uint32_t)mode) * UINT32_C(25);
    size_t secondary_index = source->secondary_start;
    size_t produced = 0u;
    for (size_t primary_index = source->primary_start;
            primary_index < source->primary_count; ++primary_index) {
        const int32_t primary = source->primary[primary_index];
        const int32_t adjusted_primary = goodix_primitives_u32_as_i32(
            (uint32_t)primary + offset);
        primary_output[produced] = adjusted_primary;
        while (secondary_index < source->secondary_count &&
                source->secondary[secondary_index] < primary) {
            ++secondary_index;
        }
        if (secondary_index < source->secondary_count &&
                (primary_index + 1u >= source->primary_count ||
                 source->secondary[secondary_index] <
                     source->primary[primary_index + 1u])) {
            secondary_output[produced] = goodix_primitives_u32_as_i32(
                (uint32_t)source->secondary[secondary_index] + offset);
            ++secondary_index;
        } else {
            secondary_output[produced] = adjusted_primary;
        }
        ++produced;
    }
    *produced_count = produced;
    return true;
}

bool goodix_primitives_clear_mode_buffers(
    const goodix_primitives_float_span buffers[3], uint32_t mode) {
    if (mode != 1u) {
        return true;
    }
    if (buffers == NULL) {
        return false;
    }
    for (size_t buffer = 0u; buffer < 3u; ++buffer) {
        if (buffers[buffer].values == NULL && buffers[buffer].count != 0u) {
            return false;
        }
    }
    for (size_t buffer = 0u; buffer < 3u; ++buffer) {
        for (size_t index = 0u; index < buffers[buffer].count; ++index) {
            buffers[buffer].values[index] = 0.0f;
        }
    }
    return true;
}

bool goodix_primitives_update_elapsed_slot(
    goodix_primitives_elapsed_state *state, size_t slot) {
    if (state == NULL || state->slot_timestamps == NULL ||
            slot >= state->slot_count) {
        return false;
    }
    const uint32_t timestamp = state->slot_timestamps[slot];
    if (timestamp == 0u) {
        return false;
    }
    if (slot != 0u) {
        state->elapsed_b = state->elapsed_b - state->baseline + timestamp;
        state->elapsed_a = state->elapsed_a - state->baseline + timestamp;
        state->baseline = timestamp;
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

bool goodix_primitives_hrv_context_destroy(
    goodix_primitives_hrv_context **context,
    goodix_primitives_release_fn release, void *release_context) {
    if (context == NULL || release == NULL) {
        return false;
    }
    if (*context == NULL) {
        return true;
    }
    goodix_primitives_hrv_context *owned = *context;
    for (size_t index = 0u; index < 11u; ++index) {
        (void)goodix_primitives_release_and_clear(
            &owned->subobjects[index], release, release_context);
    }
    if (owned->owned_6c != NULL) {
        release(release_context, owned->owned_6c);
        owned->owned_6c = NULL;
    }
    if (owned->owned_70 != NULL) {
        release(release_context, owned->owned_70);
        owned->owned_70 = NULL;
    }
    release(release_context, owned);
    *context = NULL;
    return true;
}

enum {
    GOODIX_HRV_SUB_94 = 0,
    GOODIX_HRV_SUB_A8,
    GOODIX_HRV_SUB_B8,
    GOODIX_HRV_SUB_C8,
    GOODIX_HRV_SUB_1C,
    GOODIX_HRV_SUB_2C,
    GOODIX_HRV_SUB_3C,
    GOODIX_HRV_SUB_4C,
    GOODIX_HRV_SUB_5C,
    GOODIX_HRV_SUB_74,
    GOODIX_HRV_SUB_84,
};

static void goodix_primitives_hrv_derive_geometry(
    goodix_primitives_hrv_context *context) {
    const uint32_t samples = context->sample_count;
    if (samples <= 975u && samples % 50u == 25u) {
        context->mode = 0u;
        context->divisor = samples / 25u;
        context->window_a = 37u;
        context->window_b = 65u;
        context->group_count = 1u;
    } else if (samples <= 950u && samples % 100u == 50u) {
        context->mode = 1u;
        context->divisor = samples / 50u;
        context->window_a = 75u;
        context->window_b = 65u;
        context->group_count = 1u;
    } else if (samples <= 900u && samples % 200u == 100u) {
        context->mode = 2u;
        context->divisor = samples / 100u;
        context->window_a = 151u;
        context->window_b = 65u;
        context->group_count = 1u;
    } else if (samples >= 200u && samples <= 1000u &&
               samples % 200u == 0u) {
        context->mode = 3u;
        context->divisor = samples / 200u;
        context->window_a = 251u;
        context->window_b = 129u;
        context->group_count = 1u;
    } else {
        context->mode = 0u;
        context->divisor = 1u;
        context->window_a = 151u;
        context->window_b = 65u;
        context->group_count = samples / 25u;
    }
}

static bool goodix_primitives_hrv_abi_matches(const char *abi_tag) {
    static const char expected[10] = "pv_v1.1.0";
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

static bool goodix_primitives_hrv_allocate_subobject(
    goodix_primitives_hrv_context *context, size_t index, size_t capacity,
    goodix_primitives_allocate_fn allocate, void *provider_context) {
    if (index >= GOODIX_PRIMITIVES_HRV_SUBOBJECT_COUNT ||
            capacity > SIZE_MAX / sizeof(float)) {
        return false;
    }
    const size_t bytes = capacity * sizeof(float);
    void *allocation = allocate(provider_context, bytes);
    if (allocation == NULL) {
        return false;
    }
    context->subobjects[index] = allocation;
    context->subobject_capacities[index] = capacity;
    return goodix_primitives_byte_fill(0u, allocation, bytes);
}

uint32_t goodix_primitives_hrv_context_create(
    goodix_primitives_hrv_context **context,
    const goodix_primitives_hrv_configuration *configuration,
    const char *abi_tag, goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context) {
    if (context == NULL || configuration == NULL ||
            configuration->sample_count > INT32_MAX ||
            !goodix_primitives_hrv_abi_matches(abi_tag) ||
            allocate == NULL || release == NULL) {
        return GOODIX_PRIMITIVES_HRV_INVALID;
    }
    if (*context != NULL) {
        return GOODIX_PRIMITIVES_HRV_ALREADY_INITIALIZED;
    }
    goodix_primitives_hrv_context *created =
        allocate(provider_context, sizeof(*created));
    if (created == NULL) {
        return GOODIX_PRIMITIVES_HRV_ALLOCATION_FAILED;
    }
    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)created, sizeof(*created));
    *context = created;
    created->identity = configuration->identity;
    created->sample_count = configuration->sample_count;
    goodix_primitives_hrv_derive_geometry(created);

    created->subobject_capacities[GOODIX_HRV_SUB_94] = 11u;
    created->subobject_capacities[GOODIX_HRV_SUB_A8] = 10u;
    created->subobject_capacities[GOODIX_HRV_SUB_B8] = 10u;
    created->subobject_capacities[GOODIX_HRV_SUB_C8] = 10u;
    created->subobject_capacities[GOODIX_HRV_SUB_1C] =
        created->group_count;
    created->subobject_capacities[GOODIX_HRV_SUB_2C] = created->divisor;
    created->subobject_capacities[GOODIX_HRV_SUB_3C] = created->window_a;
    created->subobject_capacities[GOODIX_HRV_SUB_4C] = created->window_b;
    created->subobject_capacities[GOODIX_HRV_SUB_5C] = 4u;
    created->subobject_capacities[GOODIX_HRV_SUB_74] = 125u;
    created->subobject_capacities[GOODIX_HRV_SUB_84] =
        created->sample_count % 25u == 0u ?
            created->sample_count / 25u : 5u;
    static const size_t allocation_order[11] = {
        GOODIX_HRV_SUB_1C, GOODIX_HRV_SUB_94, GOODIX_HRV_SUB_A8,
        GOODIX_HRV_SUB_B8, GOODIX_HRV_SUB_C8, GOODIX_HRV_SUB_2C,
        GOODIX_HRV_SUB_3C, GOODIX_HRV_SUB_4C, GOODIX_HRV_SUB_5C,
        GOODIX_HRV_SUB_74, GOODIX_HRV_SUB_84,
    };
    for (size_t order = 0u;
            order < sizeof(allocation_order) / sizeof(allocation_order[0]);
            ++order) {
        const size_t index = allocation_order[order];
        const size_t capacity = created->subobject_capacities[index];
        if (!goodix_primitives_hrv_allocate_subobject(
                created, index, capacity, allocate, provider_context)) {
            (void)goodix_primitives_hrv_context_destroy(
                context, release, provider_context);
            return GOODIX_PRIMITIVES_HRV_ALLOCATION_FAILED;
        }
    }

    created->owned_6c = allocate(provider_context,
                                 sizeof(*created->owned_6c));
    if (created->owned_6c != NULL) {
        (void)goodix_primitives_byte_fill(
            0u, (uint8_t *)created->owned_6c, sizeof(*created->owned_6c));
        created->owned_6c->direction_state = 2;
    }
    if (created->owned_6c != NULL) {
        created->owned_70 = allocate(provider_context,
                                     sizeof(*created->owned_70));
    }
    if (created->owned_6c == NULL || created->owned_70 == NULL) {
        (void)goodix_primitives_hrv_context_destroy(
            context, release, provider_context);
        return GOODIX_PRIMITIVES_HRV_ALLOCATION_FAILED;
    }
    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)created->owned_70, sizeof(*created->owned_70));
    created->owned_70->record_capacity = 20u;
    created->owned_70->factor = 7u;
    created->owned_70->minimum_interval =
        (int32_t)(created->sample_count / 4u);
    created->owned_70->maximum_interval =
        (int32_t)(created->sample_count << 1);
    created->owned_70->baseline_capacity = 16;
    created->owned_70->baseline_mean[1] = 1.0f;
    created->owned_70->baseline_mean[2] = 1.0f;
    created->scaled_sample_bytes = created->sample_count << 2;
    created->sample_count_copy = created->sample_count;
    created->calibration_e8 = (float)configuration->calibration[0] / 10000.0f;
    created->calibration_ec = (float)configuration->calibration[1] / 10000.0f;
    created->calibration_f4 = (float)configuration->calibration[2] / 10000.0f;
    created->calibration_f0 = (float)configuration->calibration[3] / 10000.0f;
    return GOODIX_PRIMITIVES_HRV_OK;
}

static bool goodix_primitives_hrv_runtime_sample_invalid(
    void *context, int32_t sample) {
    (void)context;
    return goodix_primitives_integrity_invalid((uint32_t)sample);
}

static void goodix_primitives_hrv_runtime_copy_event_to_decision(
    goodix_primitives_hrv_runtime *runtime) {
    const goodix_primitives_hr_extrema_tracker *const tracker =
        &runtime->state.extrema_tracker;
    runtime->decision_state.source.position = tracker->peak_position;
    runtime->decision_state.source.primary_first = tracker->rise_amplitude;
    runtime->decision_state.source.primary_second = tracker->fall_amplitude;
    runtime->decision_state.source.auxiliary_first = tracker->rise_span;
    runtime->decision_state.source.auxiliary_second = tracker->fall_span;
    runtime->decision_state.source.ready = (uint8_t)tracker->fall_complete;
    runtime->decision_state.source.update_count =
        (uint32_t)tracker->sample_index;
}

static void goodix_primitives_hrv_runtime_copy_event_from_decision(
    goodix_primitives_hrv_runtime *runtime) {
    goodix_primitives_hr_extrema_tracker *const tracker =
        &runtime->state.extrema_tracker;
    tracker->peak_position = runtime->decision_state.source.position;
    tracker->rise_amplitude = runtime->decision_state.source.primary_first;
    tracker->fall_amplitude = runtime->decision_state.source.primary_second;
    tracker->rise_span = runtime->decision_state.source.auxiliary_first;
    tracker->fall_span = runtime->decision_state.source.auxiliary_second;
    tracker->fall_complete = runtime->decision_state.source.ready;
    tracker->sample_index =
        (int32_t)runtime->decision_state.source.update_count;
}

static void goodix_primitives_hrv_runtime_refresh_candidates(
    goodix_primitives_hrv_runtime *runtime) {
    const uint32_t count = runtime->decision_state.record_count;
    for (uint32_t index = 0u; index < count; ++index) {
        const goodix_primitives_hr_decision_record *const current =
            &runtime->decision_state.records[index];
        goodix_primitives_hr_candidate_record *const candidate =
            &runtime->candidate_records[index];
        candidate->tag = index == 0u ? 0u :
            (uint32_t)runtime->decision_state.records[index - 1u].tag;
        candidate->position = current->position;
        candidate->value = current->center;
        candidate->alternate_tag = (uint32_t)current->tag;
        candidate->suppressed = current->flag;
    }
    for (uint32_t index = count; index < 20u; ++index) {
        runtime->candidate_records[index] =
            (goodix_primitives_hr_candidate_record){0};
    }
    runtime->plan.candidate_record_count = count;
    runtime->state.candidate_warmup_count =
        runtime->decision_state.baseline.count < 0 ? 0u :
        (uint32_t)runtime->decision_state.baseline.count;
    runtime->plan.candidate_scale = runtime->decision_state.baseline.mean[2];
    runtime->state.decision_reference_position =
        runtime->decision_state.baseline.mean[2];
    runtime->state.decision_reference_mode = runtime->decision_state.mode;
}

static bool goodix_primitives_hrv_runtime_decision(void *context) {
    goodix_primitives_hrv_runtime *runtime = context;
    if (runtime == NULL || !runtime->bound) {
        return false;
    }
    goodix_primitives_hrv_runtime_copy_event_to_decision(runtime);
    runtime->decision_state.timestamp = runtime->state.window_index;
    if (!goodix_primitives_hr_decision_update(
            &runtime->decision_context)) {
        return false;
    }
    goodix_primitives_hrv_runtime_copy_event_from_decision(runtime);
    goodix_primitives_hrv_runtime_refresh_candidates(runtime);
    return true;
}

static void goodix_primitives_hrv_runtime_commit(
    goodix_primitives_hrv_runtime *runtime) {
    goodix_primitives_hrv_context *const context = runtime->context;
    goodix_primitives_hrv_work_b *const work = context->owned_70;
    *context->owned_6c = runtime->state.extrema_tracker;
    for (uint32_t index = 0u; index < work->record_capacity; ++index) {
        work->records[index] = runtime->decision_state.records[index];
    }
    work->record_count = runtime->decision_state.record_count;
    work->mode = runtime->decision_state.mode;
    work->latch = runtime->decision_state.latch;
    work->minimum_interval = runtime->decision_state.minimum_interval;
    work->maximum_interval = runtime->decision_state.maximum_interval;
    work->stale_count = runtime->decision_state.stale_count;
    work->baseline_count = runtime->decision_state.baseline.count;
    work->baseline_capacity = runtime->decision_state.baseline.capacity;
    for (size_t index = 0u; index < 3u; ++index) {
        work->baseline_mean[index] = runtime->decision_state.baseline.mean[index];
    }
    work->baseline_timestamp = runtime->decision_state.baseline.timestamp;
    context->process_count = runtime->state.process_count;
    context->window_index = runtime->state.window_index;
    context->outlier_count = runtime->state.outlier_count;
    context->tail_outlier_count = runtime->state.tail_outlier_count;
    context->diagnostic_variation_percent =
        runtime->decision_state.diagnostic_variation_percent;
    context->diagnostic_primary_mean =
        runtime->decision_state.diagnostic_primary_mean;
    context->diagnostic_auxiliary_mean =
        runtime->decision_state.diagnostic_auxiliary_mean;
    context->diagnostic_interval_mean =
        runtime->decision_state.diagnostic_interval_mean;
    for (size_t index = 0u; index < 6u; ++index) {
        context->previous_output[index] = runtime->state.previous_output[index];
    }
}

bool goodix_primitives_hrv_runtime_bind(
    goodix_primitives_hrv_context *context,
    goodix_primitives_float_unary_fn square_root,
    goodix_primitives_hrv_runtime *runtime) {
    if (context == NULL || context->sample_count < 25u ||
            context->sample_count > INT32_MAX || context->owned_6c == NULL ||
            context->owned_70 == NULL || square_root == NULL ||
            runtime == NULL || runtime->bound ||
            context->owned_70->record_capacity != 20u ||
            context->owned_70->record_count > 20u) {
        return false;
    }
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_HRV_SUBOBJECT_COUNT; ++index) {
        if (context->subobjects[index] == NULL ||
                context->subobject_capacities[index] == 0u) {
            return false;
        }
    }
    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)runtime, sizeof(*runtime));
    runtime->context = context;
    runtime->state.sample_rate = context->sample_count;
    runtime->state.process_count = context->process_count;
    runtime->state.window_index = context->window_index;
    runtime->state.signal_history = (goodix_primitives_counted_word_history){
        context->subobjects[GOODIX_HRV_SUB_74], 0u,
        (uint32_t)context->subobject_capacities[GOODIX_HRV_SUB_74], 0u,
    };
    runtime->state.motion_history = (goodix_primitives_counted_word_history){
        context->subobjects[GOODIX_HRV_SUB_84], 0u,
        (uint32_t)context->subobject_capacities[GOODIX_HRV_SUB_84], 0u,
    };
    runtime->state.quality_history = (goodix_primitives_counted_word_history){
        context->subobjects[GOODIX_HRV_SUB_94], 0u,
        (uint32_t)context->subobject_capacities[GOODIX_HRV_SUB_94], 0u,
    };
    goodix_primitives_hr_weighted_feature_state *const weighted =
        &runtime->state.weighted_feature;
    weighted->input_rate = (int32_t)context->sample_count;
    weighted->mode = context->mode;
    weighted->midpoint_window = (int32_t)context->window_a;
    weighted->raw_history = (goodix_primitives_counted_word_history){
        context->subobjects[GOODIX_HRV_SUB_1C], 0u,
        (uint32_t)context->subobject_capacities[GOODIX_HRV_SUB_1C], 0u,
    };
    weighted->periodic_history = (goodix_primitives_counted_word_history){
        context->subobjects[GOODIX_HRV_SUB_2C], 0u,
        (uint32_t)context->subobject_capacities[GOODIX_HRV_SUB_2C], 0u,
    };
    weighted->mean_history = (goodix_primitives_counted_word_history){
        context->subobjects[GOODIX_HRV_SUB_3C], 0u,
        (uint32_t)context->subobject_capacities[GOODIX_HRV_SUB_3C], 0u,
    };
    weighted->centered_history = (goodix_primitives_counted_word_history){
        context->subobjects[GOODIX_HRV_SUB_4C], 0u,
        (uint32_t)context->subobject_capacities[GOODIX_HRV_SUB_4C], 0u,
    };
    weighted->weighted_history = (goodix_primitives_counted_word_history){
        context->subobjects[GOODIX_HRV_SUB_5C], 0u,
        (uint32_t)context->subobject_capacities[GOODIX_HRV_SUB_5C], 0u,
    };
    static const size_t coefficient_offsets[4] = {
        R1_GOODIX_HRV_MODE_0_WORD_OFFSET,
        R1_GOODIX_HRV_MODE_1_WORD_OFFSET,
        R1_GOODIX_HRV_MODE_2_WORD_OFFSET,
        R1_GOODIX_HRV_MODE_3_WORD_OFFSET,
    };
    static const size_t coefficient_counts[4] = {
        R1_GOODIX_HRV_MODE_0_WORD_COUNT,
        R1_GOODIX_HRV_MODE_1_WORD_COUNT,
        R1_GOODIX_HRV_MODE_2_WORD_COUNT,
        R1_GOODIX_HRV_MODE_3_WORD_COUNT,
    };
    for (size_t index = 0u; index < 4u; ++index) {
        weighted->mode_coefficient_words[index] =
            &r1_goodix_hrv_weighted_words[coefficient_offsets[index]];
        weighted->mode_coefficient_counts[index] = coefficient_counts[index];
    }
    runtime->state.extrema_tracker = *context->owned_6c;
    runtime->state.extrema_signal_mode = (int32_t)context->identity;
    runtime->state.extrema_interpolation_mode = context->mode;
    runtime->state.extrema_position_base = (int32_t)context->scaled_sample_bytes;
    runtime->state.extrema_period = (int32_t)context->sample_count_copy;
    runtime->state.extrema_workspace = &runtime->extrema_workspace;
    for (size_t index = 0u; index < 4u; ++index) {
        runtime->trough_curve.x[index] = goodix_primitives_float_from_bits(
            r1_goodix_hrv_extrema_curve_words[index]);
        runtime->peak_curve.x[index] = goodix_primitives_float_from_bits(
            r1_goodix_hrv_extrema_curve_words[index + 4u]);
    }
    runtime->state.trough_curve = &runtime->trough_curve;
    runtime->state.peak_curve = &runtime->peak_curve;
    runtime->state.candidate_selector.position_origin =
        (int32_t)context->scaled_sample_bytes;
    runtime->state.candidate_selector.position_step =
        (int32_t)context->sample_count_copy;
    runtime->state.quality_reference = context->calibration_f4;
    runtime->state.quality_threshold_first = (int32_t)context->outlier_count;
    runtime->state.quality_threshold_second =
        (int32_t)context->tail_outlier_count;
    runtime->state.outlier_count = context->outlier_count;
    runtime->state.tail_outlier_count = context->tail_outlier_count;
    for (size_t index = 0u; index < 6u; ++index) {
        runtime->state.previous_output[index] = context->previous_output[index];
    }

    goodix_primitives_hrv_work_b *const work = context->owned_70;
    runtime->decision_state.records = work->records;
    runtime->decision_state.record_count = work->record_count;
    runtime->decision_state.record_capacity = work->record_capacity;
    runtime->decision_state.mode = work->mode;
    runtime->decision_state.latch = work->latch;
    runtime->decision_state.minimum_interval = work->minimum_interval;
    runtime->decision_state.maximum_interval = work->maximum_interval;
    runtime->decision_state.stale_count = work->stale_count;
    runtime->decision_state.baseline.count = work->baseline_count;
    runtime->decision_state.baseline.capacity = work->baseline_capacity;
    for (size_t index = 0u; index < 3u; ++index) {
        runtime->decision_state.baseline.mean[index] = work->baseline_mean[index];
    }
    runtime->decision_state.baseline.timestamp = work->baseline_timestamp;
    runtime->decision_state.primary_history =
        (goodix_primitives_counted_word_history){
            context->subobjects[GOODIX_HRV_SUB_A8], 0u, 10u, 0u,
        };
    runtime->decision_state.auxiliary_history =
        (goodix_primitives_counted_word_history){
            context->subobjects[GOODIX_HRV_SUB_B8], 0u, 10u, 0u,
        };
    runtime->decision_state.interval_history =
        (goodix_primitives_counted_word_history){
            context->subobjects[GOODIX_HRV_SUB_C8], 0u, 10u, 0u,
        };
    runtime->decision_state.sample_rate = context->sample_count_copy;
    runtime->decision_state.diagnostic_variation_percent =
        context->diagnostic_variation_percent;
    runtime->decision_state.diagnostic_primary_mean =
        context->diagnostic_primary_mean;
    runtime->decision_state.diagnostic_auxiliary_mean =
        context->diagnostic_auxiliary_mean;
    runtime->decision_state.diagnostic_interval_mean =
        context->diagnostic_interval_mean;
    runtime->decision_context = (goodix_primitives_hr_decision_context){
        &runtime->decision_state, &runtime->decision_workspace, square_root,
    };
    runtime->workspace.quality_sort_scratch = runtime->quality_sort_scratch;
    runtime->workspace.quality_sort_capacity = 11u;
    runtime->workspace.signal_scratch = runtime->signal_scratch;
    runtime->workspace.signal_scratch_capacity = 125u;
    runtime->plan.sample_invalid =
        goodix_primitives_hrv_runtime_sample_invalid;
    runtime->plan.decision_core = goodix_primitives_hrv_runtime_decision;
    runtime->plan.decision_context = runtime;
    runtime->plan.square_root = square_root;
    runtime->plan.outlier_maximum_threshold = context->calibration_e8;
    runtime->plan.outlier_minimum_threshold = context->calibration_ec;
    runtime->plan.outlier_deviation_multiplier = context->calibration_f0;
    runtime->plan.candidate_records = runtime->candidate_records;
    runtime->plan.candidate_lower_bound = work->minimum_interval;
    runtime->plan.candidate_upper_bound = work->maximum_interval;
    runtime->plan.candidate_warmup_limit = work->baseline_capacity;
    runtime->bound = true;
    goodix_primitives_hrv_runtime_copy_event_to_decision(runtime);
    goodix_primitives_hrv_runtime_refresh_candidates(runtime);
    return true;
}

bool goodix_primitives_hrv_runtime_process(
    goodix_primitives_hrv_runtime *runtime,
    const goodix_primitives_hrv_process_input *input,
    int32_t output[6]) {
    if (runtime == NULL || !runtime->bound || input == NULL ||
            output == NULL || runtime->context == NULL) {
        return false;
    }
    const bool result = goodix_primitives_hrv_process(
        input, &runtime->plan, &runtime->state, &runtime->workspace, output);
    if (result) {
        goodix_primitives_hrv_runtime_commit(runtime);
    }
    return result;
}

uint32_t goodix_primitives_hrv_initialize_for_sample_count(
    goodix_primitives_hrv_context **context,
    const goodix_primitives_hrv_configuration *bound_configuration,
    uint32_t sample_count, goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context) {
    if (bound_configuration == NULL) {
        return GOODIX_PRIMITIVES_HRV_INVALID;
    }
    goodix_primitives_hrv_configuration configuration =
        *bound_configuration;
    configuration.sample_count = sample_count;
    return goodix_primitives_hrv_context_create(
        context, &configuration, "pv_v1.1.0", allocate, release,
        provider_context);
}

int32_t goodix_primitives_hrv_initialize_dispatch(
    goodix_primitives_hrv_context **context,
    const goodix_primitives_hrv_configuration *bound_configuration,
    uint32_t sample_count, uint16_t *result_status,
    uint8_t *provider_active, uint32_t *owner_active,
    goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context) {
    if (result_status == NULL || provider_active == NULL ||
            owner_active == NULL) {
        return -1;
    }
    const uint32_t status = goodix_primitives_hrv_initialize_for_sample_count(
        context, bound_configuration, sample_count, allocate, release,
        provider_context);
    if (status == GOODIX_PRIMITIVES_HRV_OK) {
        *result_status = UINT16_C(0x007F);
    }
    *provider_active = 0u;
    *owner_active = 0u;
    return status == GOODIX_PRIMITIVES_HRV_OK ? 0 : -1;
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

uintptr_t goodix_primitives_quantized_concatenate_vector(void) {
    return (uintptr_t)&quantized_runtime_int8_concatenate_execute;
}

uintptr_t goodix_primitives_release_context_pair_vector(void) {
    return goodix_primitives_quantized_concatenate_vector();
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
    const float *coefficient_record, goodix_primitives_allocate_fn allocate,
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
    buffer->coefficient_record = coefficient_record;
    return true;
}

bool goodix_primitives_hr_secondary_context_release(
    goodix_primitives_hr_secondary_context *context,
    goodix_primitives_release_fn release, void *release_context) {
    if (context == NULL || release == NULL) {
        return false;
    }
    for (size_t index = 0u; index < 9u; ++index) {
        if (context->pair_buffers[index].records != NULL) {
            release(release_context, context->pair_buffers[index].records);
        }
        if (context->i16_buffers[index].data != NULL) {
            release(release_context, context->i16_buffers[index].data);
        }
    }
    for (size_t index = 0u; index < 7u; ++index) {
        if (context->float_histories[index].data != NULL) {
            release(release_context, context->float_histories[index].data);
        }
    }
    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)context, sizeof(*context));
    return true;
}

bool goodix_primitives_hr_secondary_context_initialize(
    goodix_primitives_hr_secondary_context *context,
    const float *coefficient_record,
    goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context) {
    if (context == NULL || coefficient_record == NULL || allocate == NULL ||
            release == NULL) {
        return false;
    }
    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)context, sizeof(*context));

    bool ok = true;
    for (size_t index = 0u; ok && index < 9u; ++index) {
        ok = goodix_primitives_pair_buffer_initialize(
            &context->pair_buffers[index], 8u, coefficient_record,
            allocate, provider_context);
    }
    for (size_t index = 0u; ok && index < 9u; ++index) {
        const uint16_t capacity = index == 7u
            ? UINT16_C(60) : UINT16_C(180);
        ok = goodix_primitives_buffer_descriptor_initialize(
            &context->i16_buffers[index], NULL, capacity,
            sizeof(uint16_t), allocate, provider_context);
    }
    for (size_t index = 0u; ok && index < 7u; ++index) {
        ok = goodix_primitives_float_descriptor_initialize(
            &context->float_histories[index], NULL, UINT16_C(20),
            UINT8_C(1), allocate, provider_context);
    }
    if (!ok) {
        (void)goodix_primitives_hr_secondary_context_release(
            context, release, provider_context);
    }
    return ok;
}

static void goodix_primitives_hr_graph_release(
    const goodix_primitives_hr_graph_binding *binding, uintptr_t *graph) {
    if (binding != NULL && graph != NULL && *graph != (uintptr_t)0) {
        if (binding->release != NULL) {
            binding->release(binding->context, *graph);
        }
        *graph = (uintptr_t)0;
    }
}

bool goodix_primitives_hr_primary_context_release(
    goodix_primitives_hr_context_owner *owner,
    goodix_primitives_release_fn release, void *release_context) {
    if (owner == NULL || release == NULL) {
        return false;
    }
    if (owner->primary != NULL) {
        goodix_primitives_hr_graph_release(
            &owner->graph_bindings.selector_6,
            &owner->primary->graph_selector_6);
        goodix_primitives_hr_graph_release(
            &owner->graph_bindings.selector_1,
            &owner->primary->graph_selector_1);
        goodix_primitives_hr_graph_release(
            &owner->graph_bindings.selector_0,
            &owner->primary->graph_selector_0);
        (void)goodix_primitives_release_and_clear(
            &owner->primary->float_history_b.data, release,
            release_context);
        (void)goodix_primitives_release_and_clear(
            &owner->primary->short_history_b.data, release,
            release_context);
        (void)goodix_primitives_release_and_clear(
            &owner->primary->float_history_a.data, release,
            release_context);
        (void)goodix_primitives_release_and_clear(
            &owner->primary->short_history_a.data, release,
            release_context);
    }
    if (owner->secondary != NULL) {
        (void)goodix_primitives_hr_secondary_context_release(
            owner->secondary, release, release_context);
        release(release_context, owner->secondary);
    }
    if (owner->primary != NULL) {
        release(release_context, owner->primary);
    }
    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)owner, sizeof(*owner));
    return true;
}

uint32_t goodix_primitives_hr_primary_context_create(
    goodix_primitives_hr_context_owner *owner,
    const goodix_primitives_hr_configuration *configuration,
    size_t configuration_bytes, const char *abi_tag,
    const goodix_primitives_tables *tables,
    const float *coefficient_record,
    const goodix_primitives_hr_graph_bindings *graph_bindings,
    goodix_primitives_allocate_fn allocate,
    goodix_primitives_release_fn release, void *provider_context) {
    if (owner == NULL || configuration == NULL ||
            configuration_bytes != sizeof(*configuration) ||
            !goodix_primitives_hrv_abi_matches(abi_tag) || tables == NULL ||
            tables->table_9d640 == NULL || tables->table_a04cc == NULL ||
            tables->table_a50b0 == NULL || tables->table_a692c == NULL ||
            coefficient_record == NULL || graph_bindings == NULL ||
            graph_bindings->selector_0.build == NULL ||
            graph_bindings->selector_1.build == NULL ||
            graph_bindings->selector_6.build == NULL || allocate == NULL ||
            release == NULL || owner->primary != NULL ||
            owner->secondary != NULL) {
        return GOODIX_PRIMITIVES_HR_INVALID;
    }

    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)owner, sizeof(*owner));
    owner->graph_bindings = *graph_bindings;
    owner->primary = allocate(provider_context, sizeof(*owner->primary));
    if (owner->primary == NULL) {
        (void)goodix_primitives_byte_fill(
            0u, (uint8_t *)owner, sizeof(*owner));
        return GOODIX_PRIMITIVES_HR_INVALID;
    }
    (void)goodix_primitives_byte_fill(
        0u, (uint8_t *)owner->primary, sizeof(*owner->primary));

    goodix_primitives_hr_primary_context *const primary = owner->primary;
    uint32_t configured_rate = configuration->sample_rate;
    if (configured_rate == 0u) {
        configured_rate = 25u;
    }
    primary->sample_rate = (uint16_t)configured_rate;
    primary->samples_per_25hz_phase =
        (uint16_t)(primary->sample_rate / UINT16_C(25));
    primary->configuration_selector = configuration->algorithm_mode;
    uint32_t primary_window = 0u;
    if (configuration->algorithm_mode == 0u) {
        primary_window = 20u;
    } else if (configuration->algorithm_mode == 1u) {
        primary_window = 15u;
    } else if (configuration->algorithm_mode == 2u) {
        primary_window = 30u;
    }
    if (configuration->primary_window_override != 0u) {
        primary_window = configuration->primary_window_override;
    }
    primary->primary_window = primary_window;
    primary->secondary_window =
        configuration->secondary_window_override == 0u
            ? UINT32_C(9) : configuration->secondary_window_override;
    const int32_t minimum_batch = configuration->minimum_batch < 1
        ? INT32_C(1) : configuration->minimum_batch;
    primary->minimum_batch = (uint8_t)minimum_batch;
    primary->feature_stride = configuration->feature_stride == 0
        ? INT32_C(1) : configuration->feature_stride;
    primary->candidate_limit = configuration->candidate_limit > 20u
        ? UINT32_C(20) : configuration->candidate_limit;
    primary->owner_word = configuration->owner_word;
    primary->terminal_default = configuration->terminal_default == 0
        ? INT32_C(202) : configuration->terminal_default;
    primary->primary_window_low_byte = (uint8_t)primary_window;

    owner->secondary = allocate(provider_context, sizeof(*owner->secondary));
    if (owner->secondary == NULL) {
        (void)goodix_primitives_hr_primary_context_release(
            owner, release, provider_context);
        return GOODIX_PRIMITIVES_HR_INVALID;
    }
    if (!goodix_primitives_hr_secondary_context_initialize(
            owner->secondary, coefficient_record, allocate, release,
            provider_context)) {
        (void)goodix_primitives_hr_primary_context_release(
            owner, release, provider_context);
        return GOODIX_PRIMITIVES_HR_INVALID;
    }

    primary->graph_control[0] = 1u;
    primary->graph_control[1] = 5u;
    primary->graph_control[2] = UINT8_C(0x80);
    primary->graph_control[3] = 1u;
    primary->graph_control[4] = 4u;
    primary->graph_control[5] = 1u;
    primary->graph_span = UINT32_C(0x164);
    primary->graph_mode = 2u;
    primary->graph_enabled = 1u;

    primary->graph_selector_0 = graph_bindings->selector_0.build(
        graph_bindings->selector_0.context, tables->table_a692c,
        (uintptr_t)(goodix_primitives_library_code() << 2u),
        tables->table_a04cc);
    if (primary->graph_selector_0 != (uintptr_t)0) {
        primary->graph_selector_1 = graph_bindings->selector_1.build(
            graph_bindings->selector_1.context, tables->table_9d640,
            (uintptr_t)0, NULL);
    }
    if (primary->graph_selector_1 != (uintptr_t)0) {
        primary->graph_selector_6 = graph_bindings->selector_6.build(
            graph_bindings->selector_6.context, tables->table_a50b0,
            (uintptr_t)0, NULL);
    }

    const bool initialized = primary->graph_selector_6 != (uintptr_t)0 &&
        goodix_primitives_extended_descriptor_initialize(
            &primary->short_history_a, NULL, UINT16_C(3), 1u, 0u,
            allocate, provider_context) &&
        goodix_primitives_float_descriptor_initialize(
            &primary->float_history_a, NULL, UINT16_C(3), UINT8_C(1),
            allocate, provider_context) &&
        goodix_primitives_extended_descriptor_initialize(
            &primary->short_history_b, NULL, UINT16_C(3), 1u, 0u,
            allocate, provider_context) &&
        goodix_primitives_float_descriptor_initialize(
            &primary->float_history_b, NULL, UINT16_C(3), UINT8_C(1),
            allocate, provider_context);
    if (!initialized) {
        (void)goodix_primitives_hr_primary_context_release(
            owner, release, provider_context);
        return GOODIX_PRIMITIVES_HR_INVALID;
    }

    for (size_t index = 0u; index < 4u; ++index) {
        primary->initial_accumulators[index] = 262144.0f;
        primary->initial_baselines[index] = 0.0;
    }
    return GOODIX_PRIMITIVES_HR_OK;
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

static bool goodix_primitives_spo2_model_stage_configure(
    goodix_primitives_spo2_model_stage *stage,
    const quantized_runtime *quantized, const void *descriptor,
    uint32_t token) {
    if (stage == NULL || quantized == NULL || descriptor == NULL ||
            token == 0u) {
        return false;
    }
    *stage = (goodix_primitives_spo2_model_stage){0};
    stage->stage.descriptor = descriptor;
    stage->stage.execute = quantized_runtime_source_stage_token_resolve(
        NULL, token);
    if (stage->stage.execute != NULL) {
        return true;
    }
    stage->stage.runtime = quantized;
    if (token == (uint32_t)(uintptr_t)
            &quantized_runtime_float_to_int8_quantize) {
        stage->stage.adapter =
            QUANTIZED_RUNTIME_STAGE_QUANTIZE_WITH_RUNTIME;
    } else if (token == (uint32_t)(uintptr_t)
                   &quantized_runtime_int8_add_execute) {
        stage->stage.adapter =
            QUANTIZED_RUNTIME_STAGE_INT8_ADD_WITH_RUNTIME;
    } else if (token == (uint32_t)(uintptr_t)
                   &quantized_runtime_float_softmax_execute) {
        stage->stage.adapter =
            QUANTIZED_RUNTIME_STAGE_SOFTMAX_WITH_RUNTIME;
    } else {
        return false;
    }
    return true;
}

static quantized_runtime_exec_tensor goodix_primitives_spo2_model_tensor(
    const goodix_primitives_tensor_descriptor *source) {
    return (quantized_runtime_exec_tensor){
        .type_flag = source != NULL ? source->element_bytes : 0u,
        .dims = {
            source != NULL ? source->batches : 0u,
            source != NULL ? source->rows : 0u,
            source != NULL ? source->columns : 0u,
        },
        .data = source != NULL ? source->data : NULL,
    };
}

static void goodix_primitives_spo2_model_operator(
    void *context, goodix_primitives_tensor_binding inputs[2],
    goodix_primitives_tensor_binding *output) {
    goodix_primitives_spo2_model_stage *stage = context;
    if (stage == NULL || inputs == NULL || output == NULL ||
            inputs[0].descriptor == NULL || output->descriptor == NULL) {
        if (stage != NULL) {
            stage->last_status = QUANTIZED_RUNTIME_STATUS_BAD_ARGUMENT;
        }
        return;
    }
    quantized_runtime_exec_tensor input_tensors[4];
    quantized_runtime_exec_tensor output_tensors[2];
    quantized_runtime_exec_tensor *input_pointers[4] = {NULL};
    quantized_runtime_exec_tensor *output_pointers[2] = {NULL};
    size_t input_count = 0u;
    for (size_t index = 0u; index < 2u; ++index) {
        if (inputs[index].descriptor != NULL) {
            input_tensors[input_count] =
                goodix_primitives_spo2_model_tensor(inputs[index].descriptor);
            input_pointers[input_count] = &input_tensors[input_count];
            ++input_count;
        }
        if (inputs[index].auxiliary != (uintptr_t)0) {
            input_tensors[input_count] = goodix_primitives_spo2_model_tensor(
                (const goodix_primitives_tensor_descriptor *)
                    inputs[index].auxiliary);
            input_pointers[input_count] = &input_tensors[input_count];
            ++input_count;
        }
    }
    output_tensors[0] =
        goodix_primitives_spo2_model_tensor(output->descriptor);
    output_pointers[0] = &output_tensors[0];
    if (output->auxiliary != (uintptr_t)0) {
        output_tensors[1] = goodix_primitives_spo2_model_tensor(
            (const goodix_primitives_tensor_descriptor *)output->auxiliary);
        output_pointers[1] = &output_tensors[1];
    }
    stage->last_status = quantized_runtime_stage_invoke(
        &stage->stage, input_pointers, output_pointers);
}

static bool goodix_primitives_spo2_model_node(
    void *context,
    const goodix_primitives_tensor_descriptor *const *inputs,
    size_t input_count, goodix_primitives_tensor_descriptor *const *outputs,
    size_t output_count) {
    goodix_primitives_spo2_model_stage *stage = context;
    if (stage == NULL || inputs == NULL || outputs == NULL ||
            input_count == 0u || input_count > 2u || output_count != 1u ||
            outputs[0] == NULL) {
        return false;
    }
    quantized_runtime_exec_tensor input_tensors[2];
    quantized_runtime_exec_tensor output_tensor =
        goodix_primitives_spo2_model_tensor(outputs[0]);
    quantized_runtime_exec_tensor *input_pointers[3] = {NULL};
    quantized_runtime_exec_tensor *output_pointers[2] = {
        &output_tensor, NULL,
    };
    for (size_t index = 0u; index < input_count; ++index) {
        if (inputs[index] == NULL) {
            return false;
        }
        input_tensors[index] =
            goodix_primitives_spo2_model_tensor(inputs[index]);
        input_pointers[index] = &input_tensors[index];
    }
    stage->last_status = quantized_runtime_stage_invoke(
        &stage->stage, input_pointers, output_pointers);
    return stage->last_status == QUANTIZED_RUNTIME_STATUS_OK;
}

static bool goodix_primitives_spo2_model_subgraph(
    void *context, float *workspace, size_t workspace_count) {
    goodix_primitives_nadt_generated_subgraph *subgraph = context;
    if (subgraph == NULL) {
        return false;
    }
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_SUBGRAPH_OPERATOR_COUNT; ++index) {
        goodix_primitives_spo2_model_stage *stage =
            subgraph->operator_contexts[index];
        if (stage == NULL) {
            return false;
        }
        stage->last_status = QUANTIZED_RUNTIME_STATUS_OK;
    }
    if (!goodix_primitives_nadt_generated_subgraph_execute(
            subgraph, workspace, workspace_count)) {
        return false;
    }
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_SUBGRAPH_OPERATOR_COUNT; ++index) {
        const goodix_primitives_spo2_model_stage *stage =
            subgraph->operator_contexts[index];
        if (stage->last_status != QUANTIZED_RUNTIME_STATUS_OK) {
            return false;
        }
    }
    return true;
}

static bool goodix_primitives_spo2_model_plan_bind(
    goodix_primitives_spo2_runtime *runtime) {
    if (runtime == NULL || runtime->bindings.quantized == NULL ||
            runtime->session == NULL || runtime->session->model.instance == NULL) {
        return false;
    }
    quantized_runtime_goodix_model_instance *const instance =
        runtime->session->model.instance;
    static const uint16_t descriptor_offsets[
        GOODIX_PRIMITIVES_NADT_SUBGRAPH_OPERATOR_COUNT] = {
        0x000u, 0x00Cu, 0x024u, 0x02Cu, 0x044u, 0x05Cu, 0x074u,
        0x084u, 0x08Cu, 0x0A4u, 0x0BCu, 0x0D4u, 0x0E4u, 0x0ECu,
        0x0F0u, 0x108u, 0x120u, 0x138u, 0x150u,
    };
    static const uint16_t token_offsets[
        GOODIX_PRIMITIVES_NADT_SUBGRAPH_OPERATOR_COUNT] = {
        0x008u, 0x020u, 0x028u, 0x040u, 0x058u, 0x070u, 0x080u,
        0x088u, 0x0A0u, 0x0B8u, 0x0D0u, 0x0E0u, 0x0E8u, 0x0ECu,
        0x104u, 0x11Cu, 0x134u, 0x14Cu, 0x15Cu,
    };
    quantized_runtime_goodix_graph *graphs[2] = {
        &instance->graph_b, &instance->graph_a,
    };
    for (size_t graph_index = 0u;
            graph_index < GOODIX_PRIMITIVES_NADT_GRAPH_SUBGRAPH_COUNT;
            ++graph_index) {
        goodix_primitives_nadt_generated_subgraph *subgraph =
            &runtime->model_subgraphs[graph_index];
        *subgraph = (goodix_primitives_nadt_generated_subgraph){
            .quantization_minimum = 0.0f,
            .quantization_maximum = 1.0f,
        };
        for (size_t stage_index = 0u;
                stage_index < GOODIX_PRIMITIVES_NADT_SUBGRAPH_OPERATOR_COUNT;
                ++stage_index) {
            uint8_t *const bytes = graphs[graph_index]->bytes;
            goodix_primitives_spo2_model_stage *const stage =
                &runtime->model_subgraph_stages[graph_index][stage_index];
            if (!goodix_primitives_spo2_model_stage_configure(
                    stage, runtime->bindings.quantized,
                    bytes + descriptor_offsets[stage_index],
                    goodix_primitives_load_u32_le(
                        bytes + token_offsets[stage_index]))) {
                return false;
            }
            subgraph->operators[stage_index] =
                goodix_primitives_spo2_model_operator;
            subgraph->operator_contexts[stage_index] = stage;
        }
    }

    const void *outer_descriptors[
        GOODIX_PRIMITIVES_NADT_GRAPH_STAGE_COUNT] = {
        instance->descriptor_a, instance->descriptor_b,
        &instance->softmax_execute, &instance->vector_36dcc,
        &instance->recurrent, instance->descriptor_c,
        instance->descriptor_d,
    };
    const uint32_t outer_tokens[
        GOODIX_PRIMITIVES_NADT_GRAPH_STAGE_COUNT] = {
        goodix_primitives_load_u32_le(instance->descriptor_a + 0x14u),
        goodix_primitives_load_u32_le(instance->descriptor_b + 0x14u),
        (uint32_t)instance->softmax_execute,
        (uint32_t)instance->vector_36dcc,
        (uint32_t)instance->recurrent.execute,
        goodix_primitives_load_u32_le(instance->descriptor_c + 0x14u),
        goodix_primitives_load_u32_le(instance->descriptor_d + 0x14u),
    };
    runtime->model_graph = (goodix_primitives_nadt_generated_graph){
        .first_stage_values = 8u,
        .shared_stage_values = 3u,
        .recurrent_values = 16u,
        .recurrent_state = instance->recurrent.state,
        .recurrent_state_capacity = 16u,
        .penultimate_values = 12u,
        .output_values = 1u,
    };
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_GRAPH_SUBGRAPH_COUNT; ++index) {
        runtime->model_graph.subgraphs[index] =
            goodix_primitives_spo2_model_subgraph;
        runtime->model_graph.subgraph_contexts[index] =
            &runtime->model_subgraphs[index];
    }
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_GRAPH_STAGE_COUNT; ++index) {
        goodix_primitives_spo2_model_stage *const stage =
            &runtime->model_graph_stages[index];
        if (!goodix_primitives_spo2_model_stage_configure(
                stage, runtime->bindings.quantized,
                outer_descriptors[index], outer_tokens[index])) {
            return false;
        }
        runtime->model_graph.stages[index] =
            goodix_primitives_spo2_model_node;
        runtime->model_graph.stage_contexts[index] = stage;
    }
    return true;
}

static goodix_primitives_decimated_float_window
goodix_primitives_spo2_float_window(
    goodix_primitives_float_descriptor *descriptor) {
    return (goodix_primitives_decimated_float_window){
        .values = descriptor != NULL ? descriptor->data : NULL,
        .count = descriptor != NULL ? descriptor->count : 0u,
        .capacity = descriptor != NULL ? descriptor->capacity : 0u,
        .period = 1u,
        .phase = 0u,
        .cursor = descriptor != NULL && descriptor->capacity != 0u
            ? (uint16_t)(descriptor->count % descriptor->capacity) : 0u,
        .sum = 0.0f,
    };
}

static bool goodix_primitives_spo2_source_state_bind(
    goodix_primitives_spo2_runtime *runtime) {
    if (runtime == NULL || runtime->source_state == NULL ||
            runtime->session == NULL ||
            runtime->session->aggregate.session == NULL ||
            runtime->session->aggregate.pair == NULL ||
            runtime->session->record_pair.records == NULL ||
            runtime->session->record_pair.scratch == NULL) {
        return false;
    }
    goodix_primitives_spo2_source_state *const source =
        runtime->source_state;
    *source = (goodix_primitives_spo2_source_state){0};
    source->assembled_output = (goodix_primitives_spo2_channel_output){
        .records = (goodix_primitives_spo2_channel_record *)
            runtime->assembled_records,
        .record_capacity = 1u,
    };
    source->batch_state = (goodix_primitives_nadt_batch_state){
        .channels = (goodix_primitives_nadt_channel_accumulator *)
            runtime->session->record_pair.records,
        .channel_capacity = 1u,
    };

    goodix_primitives_session_state *const session_state =
        runtime->session->aggregate.session;
    goodix_primitives_channel_state *const primary =
        &session_state->primary;
    goodix_primitives_channel_state *const secondary =
        &session_state->secondary;
    source->channel_state = (goodix_primitives_nadt_channel_state){
        .primary = {
            .feature = {
                .input = goodix_primitives_spo2_float_window(
                    &primary->history),
                .smoothed = goodix_primitives_spo2_float_window(
                    &primary->window),
                .residual = goodix_primitives_spo2_float_window(
                    &primary->filtered),
                .residual_smoothed = goodix_primitives_spo2_float_window(
                    &primary->scalar),
                .feature_average = goodix_primitives_spo2_float_window(
                    &primary->primary_buckets),
            },
            .pair_average = goodix_primitives_spo2_float_window(
                &primary->secondary_buckets),
        },
        .secondary = {
            .feature = {
                .input = goodix_primitives_spo2_float_window(
                    &secondary->history),
                .smoothed = goodix_primitives_spo2_float_window(
                    &secondary->window),
                .residual = goodix_primitives_spo2_float_window(
                    &secondary->filtered),
                .residual_smoothed = goodix_primitives_spo2_float_window(
                    &secondary->scalar),
                .feature_average = goodix_primitives_spo2_float_window(
                    &secondary->primary_buckets),
            },
            .pair_average = goodix_primitives_spo2_float_window(
                &secondary->secondary_buckets),
        },
        .combined_ratio = goodix_primitives_spo2_float_window(
            &session_state->tail_a),
        .primary_ratio = goodix_primitives_spo2_float_window(
            &session_state->tail_b),
        .secondary_ratio = goodix_primitives_spo2_float_window(
            &session_state->tail_c),
        .half_primary_input = {
            .values = session_state->tail_d.data,
            .count = session_state->tail_d.count,
            .capacity = session_state->tail_d.capacity,
            .cursor = session_state->tail_d.capacity != 0u
                ? (uint16_t)(session_state->tail_d.count %
                             session_state->tail_d.capacity) : 0u,
            .phase = 0u,
            .period = 1u,
        },
    };
    source->geometry_state = (goodix_primitives_nadt_geometry_state){
        .magnitude_delta = {
            .values = runtime->session->aggregate.auxiliary.full_rate.data,
            .count = runtime->session->aggregate.auxiliary.full_rate.count,
            .capacity =
                runtime->session->aggregate.auxiliary.full_rate.capacity,
        },
        .angle_average = {
            .values = runtime->session->aggregate.auxiliary.reduced_rate.data,
            .count = runtime->session->aggregate.auxiliary.reduced_rate.count,
            .capacity =
                runtime->session->aggregate.auxiliary.reduced_rate.capacity,
        },
    };
    source->output_record.history =
        (goodix_primitives_decimated_float_window){
            .values = source->output_history,
            .capacity = 25u,
            .period = 1u,
        };
    source->harmonic_selector =
        (goodix_primitives_nadt_harmonic_selector_context){
            .workspace = &source->harmonic_workspace,
            .square_root = runtime->bindings.square_root,
        };
    for (size_t index = 0u; index < 2u; ++index) {
        source->peak_histories[index].window =
            (goodix_primitives_word_window){
                .values = source->peak_history_values[index],
                .capacity = 20u,
            };
    }
    source->output_selection.rate_history =
        (goodix_primitives_float_buffer){
            .values = source->output_history,
            .capacity = 25u,
        };
    source->signal_confidence.rate_history =
        (goodix_primitives_float_buffer){
            .values = source->signal_rate_history,
            .capacity = 25u,
        };
    for (size_t index = 0u;
            index < GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES; ++index) {
        runtime->spectral_scales[index] = goodix_primitives_float_from_bits(
            r1_goodix_spo2_spectral_words[
                R1_GOODIX_SPO2_SPECTRAL_SCALE_WORD_OFFSET + index]);
    }
    return true;
}

static int32_t goodix_primitives_spo2_integrity_transform(int32_t value) {
    return (int32_t)goodix_primitives_integrity_encode((uint32_t)value);
}

static int32_t goodix_primitives_spo2_source_stage_execute(
    goodix_primitives_spo2_runtime *runtime,
    goodix_primitives_outer_session *session,
    goodix_primitives_nadt_preprocess_stage stage,
    goodix_primitives_nadt_preprocess_frame *frame) {
    if (runtime == NULL || session == NULL || frame == NULL ||
            frame->source == NULL || frame->workspace == NULL ||
            runtime->source_state == NULL) {
        return 5;
    }
    const goodix_primitives_spo2_calc_input *const input = frame->source;
    goodix_primitives_spo2_source_state *const state =
        runtime->source_state;
    switch (stage) {
        case GOODIX_PRIMITIVES_NADT_PREPROCESS_ASSEMBLE: {
            const size_t channel_count = input->total_channel_count;
            const size_t value_count = channel_count * 3u;
            if (channel_count == 0u || channel_count > UINT8_MAX ||
                    input->enable_flags == NULL ||
                    input->enable_flag_count < (value_count + 7u) / 8u ||
                    input->channel_values == NULL ||
                    input->channel_value_count < value_count ||
                    input->gain_codes == NULL ||
                    input->gain_code_count < value_count ||
                    input->drive_currents == NULL ||
                    input->drive_current_count < value_count) {
                return 5;
            }
            runtime->channel_scaling =
                (goodix_primitives_spo2_channel_scaling){
                    .channel_count = (uint8_t)channel_count,
                    .encoded_values = input->channel_values,
                    .encoded_value_count = input->channel_value_count,
                    .scale_codes = input->gain_codes,
                    .scale_code_count = input->gain_code_count,
                    .divisors = (const int16_t *)(const void *)
                        input->drive_currents,
                    .divisor_count = input->drive_current_count,
                    .bit_width = input->bit_count,
                    .scale_mode = input->chip_type,
                    .encoding_mode = input->data_type,
                    .scale_tables = {
                        r1_goodix_spo2_scale_words +
                            R1_GOODIX_SPO2_SCALE_MODE_0_WORD_OFFSET,
                        r1_goodix_spo2_scale_words +
                            R1_GOODIX_SPO2_SCALE_MODE_1_WORD_OFFSET,
                        r1_goodix_spo2_scale_words +
                            R1_GOODIX_SPO2_SCALE_MODE_2_WORD_OFFSET,
                    },
                    .scale_table_counts = {
                        R1_GOODIX_SPO2_SCALE_MODE_0_WORD_COUNT,
                        R1_GOODIX_SPO2_SCALE_MODE_1_WORD_COUNT,
                        R1_GOODIX_SPO2_SCALE_MODE_2_WORD_COUNT,
                    },
                    .power = runtime->bindings.power,
                };
            const goodix_primitives_spo2_channel_source source = {
                .channel_count = (uint8_t)channel_count,
                .presence_bytes = input->enable_flags,
                .presence_byte_count = input->enable_flag_count,
                .encoded_values = input->channel_values,
                .encoded_value_count = input->channel_value_count,
                .metadata = {
                    (uint32_t)input->acceleration[0],
                    (uint32_t)input->acceleration[1],
                    (uint32_t)input->acceleration[2],
                },
                .decode_context = &runtime->channel_scaling,
            };
            state->assembled_output.record_count = 0u;
            bool mismatch = false;
            if (!goodix_primitives_spo2_channel_records_assemble(
                    &source, (int32_t)frame->state->process_count,
                    frame->state->lane_count, &state->assembled_output,
                    goodix_primitives_spo2_integrity_transform,
                    goodix_primitives_spo2_channel_scale_decode,
                    &mismatch)) {
                return 5;
            }
            return mismatch ? 1 : 0;
        }
        case GOODIX_PRIMITIVES_NADT_PREPROCESS_BATCH_ACCUMULATE: {
            const goodix_primitives_nadt_batch_input batch_input = {
                .sample_index = (uint32_t)state->assembled_output.sequence,
                .selector = state->assembled_output.record_count,
                .channels = (const goodix_primitives_nadt_channel_accumulator *)
                    state->assembled_output.records,
                .vector = {
                    (int32_t)state->assembled_output.metadata[0],
                    (int32_t)state->assembled_output.metadata[1],
                    (int32_t)state->assembled_output.metadata[2],
                },
            };
            const goodix_primitives_nadt_batch_configuration configuration = {
                .channel_count = frame->state->lane_count,
                .period = goodix_primitives_load_u32_le(
                    session->processing_record + 76u),
            };
            int32_t result = 5;
            return goodix_primitives_nadt_batch_accumulate(
                &batch_input, &configuration, &state->batch_state, &result)
                ? result : 5;
        }
        case GOODIX_PRIMITIVES_NADT_PREPROCESS_FAILURE_ENCODE:
            return goodix_primitives_nadt_record_encode(
                &state->output_record, frame->output_words) ? 0 : 5;
        case GOODIX_PRIMITIVES_NADT_PREPROCESS_ACCUMULATE: {
            const goodix_primitives_nadt_channel_input channel = {
                .primary = {
                    state->batch_state.aggregate.primary[0],
                    state->batch_state.aggregate.primary[1],
                },
                .secondary = {
                    state->batch_state.aggregate.secondary[0],
                    state->batch_state.aggregate.secondary[1],
                },
            };
            const goodix_primitives_nadt_cadence_configuration cadence = {
                goodix_primitives_load_u32_le(
                    session->processing_record + 80u),
                goodix_primitives_load_u32_le(
                    session->processing_record + 84u),
                goodix_primitives_load_u32_le(
                    session->processing_record + 88u),
                goodix_primitives_load_u32_le(
                    session->processing_record + 92u),
            };
            int32_t result = 5;
            return goodix_primitives_nadt_accumulation_execute(
                &channel, state->batch_state.vector,
                state->batch_state.batch_index, &cadence,
                &state->channel_state, &state->geometry_state,
                runtime->bindings.square_root,
                runtime->bindings.arc_tangent, &result) ? result : 5;
        }
        case GOODIX_PRIMITIVES_NADT_PREPROCESS_SPECTRAL_PREPARE: {
            const goodix_primitives_decimated_float_window *const spectrum =
                &state->channel_state.combined_ratio;
            if (spectrum->count <
                    GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES) {
                return 5;
            }
            const goodix_primitives_nadt_spectral_source source = {
                .spectrum_values = spectrum->values + spectrum->count -
                    GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES,
                .spectrum_count =
                    GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES,
                .outlier_multiplier_tenths =
                    session->processing_record[0x40u],
                .mode_one_scales = runtime->spectral_scales,
                .scale_count = GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES,
                .mode_one_factor = goodix_primitives_float_from_bits(
                    r1_goodix_spo2_spectral_words[
                        R1_GOODIX_SPO2_SPECTRAL_FACTOR_WORD_OFFSET]),
            };
            return goodix_primitives_nadt_spectral_peak_prepare(
                &source, goodix_primitives_nadt_harmonic_candidates_select,
                &state->harmonic_selector, runtime->bindings.square_root,
                runtime->bindings.floor, &runtime->transient.spectral,
                &state->spectral_result) ? 0 : 5;
        }
        case GOODIX_PRIMITIVES_NADT_PREPROCESS_PRIMARY_PEAK_UPDATE:
            return goodix_primitives_nadt_primary_ratio_peak_update(
                &state->channel_state, (int32_t)frame->state->batch_index,
                runtime->transient.peak.packed,
                sizeof(runtime->transient.peak.packed),
                runtime->transient.peak.columns,
                sizeof(runtime->transient.peak.columns),
                runtime->transient.peak.indices,
                sizeof(runtime->transient.peak.indices) /
                    sizeof(runtime->transient.peak.indices[0]),
                state->peak_histories) ? 0 : 5;
        case GOODIX_PRIMITIVES_NADT_PREPROCESS_SUMMARY_DISPATCH: {
            const goodix_primitives_nadt_threshold_configuration
                configuration = {
                    .maximum_threshold = goodix_primitives_load_u32_le(
                        session->processing_record + 0x24u),
                    .minimum_threshold = goodix_primitives_load_u32_le(
                        session->processing_record + 0x28u),
                    .deviation_factor = goodix_primitives_load_u32_le(
                        session->processing_record + 0x2Cu),
                };
            const goodix_primitives_buffer_descriptor primary = {
                .data = state->geometry_state.magnitude_delta.values,
                .count = state->geometry_state.magnitude_delta.count,
                .capacity = state->geometry_state.magnitude_delta.capacity,
            };
            const goodix_primitives_buffer_descriptor secondary = {
                .data = state->geometry_state.angle_average.values,
                .count = state->geometry_state.angle_average.count,
                .capacity = state->geometry_state.angle_average.capacity,
            };
            const goodix_primitives_nadt_summary_context context = {
                .configuration = &configuration,
                .primary = &primary,
                .secondary = &secondary,
            };
            int32_t summary_result = 5;
            if (!goodix_primitives_nadt_sample_summary_build(
                    &context, runtime->bindings.square_root,
                    &state->sample_summary, &summary_result)) {
                return 5;
            }
            const goodix_primitives_event_pair_source events = {
                .primary = (const int32_t *)(const void *)
                    state->peak_histories[0].window.values,
                .primary_count = state->peak_histories[0].window.count,
                .primary_start = state->peak_histories[0].cursor,
                .secondary = (const int32_t *)(const void *)
                    state->peak_histories[1].window.values,
                .secondary_count = state->peak_histories[1].window.count,
                .secondary_start = state->peak_histories[1].cursor,
            };
            goodix_primitives_spo2_analysis_workspace *const analysis =
                &runtime->transient.analysis;
            if (!goodix_primitives_nadt_channel_analysis_execute(
                    &state->channel_state, &events,
                    (int32_t)frame->state->batch_index,
                    session->processing_record[0x40u],
                    analysis->primary_indices, analysis->secondary_indices,
                    20u, analysis->sort,
                    GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES,
                    analysis->mask,
                    GOODIX_PRIMITIVES_NADT_SPECTRAL_INPUT_VALUES,
                    runtime->bindings.square_root,
                    &state->channel_analysis)) {
                return 5;
            }
            frame->workspace->summary_metric =
                state->channel_analysis.primary_average;
            return summary_result;
        }
        case GOODIX_PRIMITIVES_NADT_PREPROCESS_QUALITY_UPDATE: {
            const goodix_primitives_nadt_channel_quality_configuration
                configuration = {
                    .primary_level_threshold =
                        goodix_primitives_load_u32_le(
                            session->processing_record + 0x30u),
                    .secondary_level_threshold =
                        goodix_primitives_load_u32_le(
                            session->processing_record + 0x34u),
                    .metric_limit_percent =
                        session->processing_record[0x41u],
                    .quality_threshold =
                        session->processing_record[0x42u],
                    .flag_mask = session->processing_record[0x43u],
                };
            const goodix_primitives_nadt_channel_quality_summary summary = {
                .primary_level = state->sample_summary.outlier_count,
                .secondary_level = state->sample_summary.secondary_mean,
            };
            state->quality_record.primary_activity =
                state->channel_analysis.primary_difference.
                    nonuniform_mask_count;
            state->quality_record.secondary_activity =
                state->channel_analysis.secondary_difference.
                    nonuniform_mask_count;
            state->quality_record.primary_metric =
                state->channel_analysis.primary_difference.relative_variance;
            state->quality_record.secondary_metric =
                state->channel_analysis.secondary_difference.relative_variance;
            state->quality_record.primary_valid =
                state->channel_analysis.primary_difference.
                    sufficient_coverage != 0u;
            state->quality_record.secondary_valid =
                state->channel_analysis.secondary_difference.
                    sufficient_coverage != 0u;
            state->quality_record.quality =
                (int8_t)state->channel_analysis.cosine_percent;
            return goodix_primitives_nadt_channel_quality_update(
                &configuration, &summary, &state->quality_record,
                runtime->bindings.exponential) ? 0 : 5;
        }
        case GOODIX_PRIMITIVES_NADT_PREPROCESS_TRANSITION_UPDATE:
            return goodix_primitives_update_transition(
                state->transition_record, sizeof(state->transition_record),
                state->output_selection.transition_state,
                state->quality_record.flags) ? 0 : 5;
        case GOODIX_PRIMITIVES_NADT_PREPROCESS_INFERENCE: {
            const goodix_primitives_decimated_float_window *const primary =
                &state->channel_state.primary_ratio;
            const goodix_primitives_decimated_float_window *const secondary =
                &state->channel_state.secondary_ratio;
            if (primary->count < GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES ||
                    secondary->count <
                        GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES ||
                    !goodix_primitives_nadt_clip_normalize(
                        secondary->values + secondary->count -
                            GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES,
                        GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES,
                        runtime->transient.model,
                        GOODIX_PRIMITIVES_NADT_INFERENCE_WORKSPACE_FLOATS)) {
                return 5;
            }
            const float *const primary_tail = primary->values +
                primary->count - GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES;
            return goodix_primitives_nadt_generated_graph_execute(
                &runtime->model_graph, primary_tail,
                GOODIX_PRIMITIVES_NADT_GRAPH_INPUT_VALUES,
                runtime->transient.model,
                GOODIX_PRIMITIVES_NADT_INFERENCE_WORKSPACE_FLOATS,
                session->buffer_record != NULL &&
                    session->buffer_record->flag_05 == 1u,
                frame->workspace->inference_values,
                frame->workspace->inference_capacity) ? 0 : 5;
        }
        case GOODIX_PRIMITIVES_NADT_PREPROCESS_OUTPUT_QUALITY: {
            const goodix_primitives_nadt_quality_configuration
                configuration = {
                    .rounded_value_threshold =
                        session->processing_record[0x44u],
                    .alternate_history_length =
                        (int8_t)session->processing_record[0x47u],
                    .default_history_length =
                        (int8_t)session->processing_record[0x48u],
                    .alternate_tolerance =
                        session->processing_record[0x49u],
                    .default_tolerance =
                        session->processing_record[0x4Au],
                };
            return goodix_primitives_nadt_output_record_quality_update(
                &configuration, state->quality_record.flags,
                frame->workspace->adjusted_values[0],
                &state->output_record) ? 0 : 5;
        }
        case GOODIX_PRIMITIVES_NADT_PREPROCESS_OUTPUT_SELECT: {
            const goodix_primitives_nadt_output_selection_configuration
                configuration = {
                    .rate_threshold = session->processing_record[0x44u],
                    .initial_sample = session->processing_record[0x45u],
                    .override_sample = session->processing_record[0x46u],
                    .flags = session->processing_record[0x4Bu],
                };
            state->output_selection.rate_history.count =
                state->output_record.history.count;
            state->output_selection.signal_present =
                state->transition_record[5];
            state->output_selection.persistence =
                state->transition_record[6];
            frame->workspace->selected_rates[0] = 0.0f;
            frame->workspace->selected_kinds[0] = 0u;
            return goodix_primitives_nadt_output_state_select(
                &configuration, frame->state->batch_index,
                &state->output_selection,
                frame->workspace->selected_rates,
                frame->workspace->selected_kinds) ? 0 : 5;
        }
        case GOODIX_PRIMITIVES_NADT_PREPROCESS_SIGNAL_CONFIDENCE: {
            const goodix_primitives_decimated_float_window *const primary =
                &state->channel_state.primary_ratio;
            const goodix_primitives_decimated_float_window *const secondary =
                &state->channel_state.secondary_ratio;
            const goodix_primitives_nadt_dual_window_source source = {
                .primary_values = primary->values,
                .primary_count = primary->count,
                .secondary_values = secondary->values,
                .secondary_count = secondary->count,
            };
            if (!goodix_primitives_nadt_dual_window_features_extract(
                    &source, runtime->bindings.square_root,
                    &runtime->transient.dual_window,
                    &state->signal_features)) {
                return 5;
            }
            return goodix_primitives_nadt_signal_confidence_update(
                &state->signal_features,
                (const uint16_t *)(const void *)
                    state->channel_state.half_primary_input.values,
                state->channel_state.half_primary_input.count,
                goodix_primitives_load_u32_le(
                    session->processing_record + 0x1Cu) != 0u,
                &state->signal_confidence,
                &runtime->transient.signal_confidence,
                runtime->bindings.square_root,
                runtime->bindings.double_exponential,
                &state->signal_diagnostics) ? 0 : 5;
        }
        case GOODIX_PRIMITIVES_NADT_PREPROCESS_OUTPUT_BUILD: {
            const goodix_primitives_nadt_source_metrics source_metrics = {
                .second_score = state->quality_record.secondary_metric,
                .fourth_score = state->quality_record.primary_metric,
                .first_score = (float)state->quality_record.score,
                .third_score =
                    (float)state->channel_analysis.cosine_percent,
                .source_flags = state->quality_record.flags,
                .category = frame->workspace->selected_kinds[0],
            };
            const bool reference_enabled = goodix_primitives_load_u32_le(
                session->processing_record + 0x1Cu) == 1u;
            const goodix_primitives_nadt_reference_metrics reference = {
                .reference = state->signal_confidence.rolling_mean,
                .scaled_reference = state->signal_confidence.probability,
            };
            return goodix_primitives_nadt_output_record_build(
                reference_enabled, frame->workspace->selected_rates[0], 0,
                &source_metrics, reference_enabled ? &reference : NULL,
                frame->workspace->inference_values[0],
                &state->output_record, frame->output_words) ? 0 : 5;
        }
        default:
            return 5;
    }
}

static int32_t goodix_primitives_spo2_runtime_stage_adapter(
    void *opaque, goodix_primitives_nadt_preprocess_stage stage,
    goodix_primitives_nadt_preprocess_frame *frame) {
    goodix_primitives_spo2_runtime *runtime = opaque;
    if (runtime == NULL || !runtime->bound || runtime->session == NULL ||
            frame == NULL) {
        return 5;
    }
    if (runtime->bindings.execute == NULL) {
        return goodix_primitives_spo2_source_stage_execute(
            runtime, runtime->session, stage, frame);
    }
    return runtime->bindings.execute(
        runtime->bindings.context, runtime->session, stage, frame);
}

bool goodix_primitives_spo2_runtime_bind(
    const goodix_primitives_spo2_runtime_bindings *bindings,
    goodix_primitives_spo2_runtime *runtime) {
    if (bindings == NULL ||
            (bindings->execute == NULL &&
             (bindings->power == NULL || bindings->square_root == NULL ||
              bindings->floor == NULL || bindings->exponential == NULL ||
              bindings->arc_tangent == NULL ||
              bindings->double_exponential == NULL)) ||
            bindings->quantized == NULL || bindings->allocate == NULL ||
            bindings->release == NULL || runtime == NULL || runtime->bound ||
            runtime->session != NULL) {
        return false;
    }
    *runtime = (goodix_primitives_spo2_runtime){0};
    runtime->bindings = *bindings;
    uint32_t model_base_address =
        r1_goodix_generated_model.stock_base_address;
#if UINTPTR_MAX <= UINT32_MAX
    model_base_address =
        (uint32_t)(uintptr_t)r1_goodix_generated_model.words;
#endif
    if (!goodix_primitives_outer_session_create(
            &runtime->session, r1_goodix_spo2_configuration,
            R1_GOODIX_SPO2_CONFIGURATION_BYTE_COUNT, "pre_pv_v1.1.0",
            bindings->quantized, r1_goodix_generated_model.words,
            r1_goodix_generated_model.word_count,
            model_base_address,
            bindings->allocate, bindings->release,
            bindings->provider_context)) {
        *runtime = (goodix_primitives_spo2_runtime){0};
        return false;
    }
    if (bindings->execute == NULL) {
        runtime->source_state = bindings->allocate(
            bindings->provider_context, sizeof(*runtime->source_state));
        if (runtime->source_state == NULL ||
                !goodix_primitives_spo2_source_state_bind(runtime) ||
                !goodix_primitives_spo2_model_plan_bind(runtime)) {
            if (runtime->source_state != NULL) {
                bindings->release(
                    bindings->provider_context, runtime->source_state);
                runtime->source_state = NULL;
            }
            (void)goodix_primitives_outer_session_destroy(
                &runtime->session, bindings->release,
                bindings->provider_context);
            *runtime = (goodix_primitives_spo2_runtime){0};
            return false;
        }
    }

    /* Stock outer +0x0C is the copied 76-byte record. Root 0x6E838 reads
     * word 0 as lane count, +0x38 as the adjustment flag, and +0x3C as the
     * summary threshold; 0x7412C consumes signed words 2..6 in place. */
    const uint32_t lane_count = goodix_primitives_load_u32_le(
        runtime->session->processing_record);
    if (lane_count != 1u) {
        (void)goodix_primitives_outer_session_destroy(
            &runtime->session, bindings->release,
            bindings->provider_context);
        *runtime = (goodix_primitives_spo2_runtime){0};
        return false;
    }
    runtime->state = (goodix_primitives_nadt_preprocess_state){
        .initialized = true,
        .lane_count = lane_count,
        .adjustment_enabled = goodix_primitives_load_u32_le(
            runtime->session->processing_record + 0x38u) == 1u,
        .summary_metric_threshold = goodix_primitives_load_u32_le(
            runtime->session->processing_record + 0x3Cu),
    };
    runtime->workspace = (goodix_primitives_nadt_preprocess_workspace){
        .assembled_records = runtime->assembled_records,
        .assembled_record_bytes = sizeof(runtime->assembled_records),
        .summaries = runtime->summaries,
        .summary_bytes = sizeof(runtime->summaries),
        .inference_values = &runtime->inference_value,
        .inference_capacity = 1u,
        .adjusted_values = &runtime->adjusted_value,
        .adjusted_capacity = 1u,
        .selected_rates = &runtime->selected_rate,
        .selected_rate_capacity = 1u,
        .selected_kinds = &runtime->selected_kind,
        .selected_kind_capacity = 1u,
    };
    for (size_t index = 0u; index < 7u; ++index) {
        runtime->quartic_coefficients[index] =
            goodix_primitives_u32_as_i32(goodix_primitives_load_u32_le(
                runtime->session->processing_record + index * 4u));
    }
    runtime->plan = (goodix_primitives_nadt_preprocess_plan){
        .execute = goodix_primitives_spo2_runtime_stage_adapter,
        .context = runtime,
        .quartic_coefficients = runtime->quartic_coefficients,
        .quartic_coefficient_count = 7u,
    };
    runtime->bound = true;
    return true;
}

int32_t goodix_primitives_spo2_runtime_process(
    goodix_primitives_spo2_runtime *runtime,
    const goodix_primitives_spo2_calc_input *source,
    uint32_t *output_words, size_t output_word_count) {
    if (runtime == NULL || !runtime->bound || runtime->session == NULL) {
        return 7;
    }
    return goodix_primitives_spo2_calc(
        &runtime->plan, source, &runtime->state, &runtime->workspace,
        output_words, output_word_count);
}

bool goodix_primitives_spo2_runtime_unbind(
    goodix_primitives_spo2_runtime *runtime) {
    if (runtime == NULL || !runtime->bound || runtime->session == NULL ||
            runtime->bindings.release == NULL) {
        return false;
    }
    goodix_primitives_release_fn const release = runtime->bindings.release;
    void *const provider_context = runtime->bindings.provider_context;
    if (runtime->source_state != NULL) {
        release(provider_context, runtime->source_state);
        runtime->source_state = NULL;
    }
    if (!goodix_primitives_outer_session_destroy(
            &runtime->session, release, provider_context)) {
        return false;
    }
    *runtime = (goodix_primitives_spo2_runtime){0};
    return true;
}
