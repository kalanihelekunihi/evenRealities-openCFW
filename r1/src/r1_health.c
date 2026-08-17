#include "openr1/r1_health.h"
#include "openr1/r1_crc.h"
#include "gomore_primitives/gomore_primitives.h"

_Static_assert(sizeof(r1_activity_offline_entry) == 16u,
               "activity offline record layout must remain 16 bytes");
_Static_assert(sizeof(r1_health_u8_offline_entry) == 16u,
               "HR/SpO2 offline record layout must remain 16 bytes");
_Static_assert(sizeof(r1_health_u16_offline_entry) == 20u,
               "HRV offline record layout must remain 20 bytes");
_Static_assert(sizeof(r1_health_sync_cursor_state) ==
                   R1_HEALTH_SYNC_CURSOR_BYTES,
               "health sync cursor record must remain 24 bytes");
_Static_assert(sizeof(r1_health_time_transition) == 12u,
               "time transition record must remain 12 bytes");
_Static_assert(offsetof(r1_health_time_transition, old_timestamp_seconds) == 4u,
               "old timestamp must remain at transition offset 4");
_Static_assert(offsetof(r1_health_time_transition, new_timestamp_seconds) == 8u,
               "new timestamp must remain at transition offset 8");
_Static_assert(sizeof(r1_health_u8_accumulator) == 8u,
               "health hourly-average accumulator must remain 8 bytes");
_Static_assert(sizeof(r1_health_u16_accumulator) == 8u,
               "HRV hourly-average accumulator must remain 8 bytes");
_Static_assert(sizeof(r1_health_settings_record) == 12u,
               "health settings command record must remain 12 bytes");
_Static_assert(sizeof(r1_activity_cumulative_counters) == 8u,
               "activity provider counters must remain 8 bytes");
_Static_assert(sizeof(r1_activity_accumulator) == 24u,
               "activity accumulator state must remain 24 bytes");
_Static_assert(sizeof(r1_activity_delta_event) == 12u,
               "activity event-11 payload must remain 12 bytes");
_Static_assert(sizeof(r1_health_crash_snapshot) == R1_HEALTH_CRASH_SNAPSHOT_BYTES,
               "health crash snapshot must remain 52 bytes");
_Static_assert(sizeof(r1_health_crash_record) == R1_HEALTH_CRASH_RECORD_BYTES,
               "health crash record must remain 966 bytes");
_Static_assert(offsetof(r1_health_crash_snapshot, activity_packed_words) == 16u,
               "activity crash words must remain at offset 0x10");
_Static_assert(offsetof(r1_health_crash_snapshot, heart_rate_accumulator_count) == 40u,
               "heart-rate accumulator count must remain at offset 0x28");
_Static_assert(offsetof(r1_health_crash_snapshot, local_hour) == 44u,
               "health crash local hour must remain at offset 0x2c");

static uint16_t read_u16(const uint8_t *input) {
    return (uint16_t)((uint16_t)input[0] | ((uint16_t)input[1] << 8u));
}

static uint32_t read_u32(const uint8_t *input) {
    return (uint32_t)input[0] | ((uint32_t)input[1] << 8u)
        | ((uint32_t)input[2] << 16u) | ((uint32_t)input[3] << 24u);
}

static void write_u16(uint8_t *output, uint16_t value) {
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8u);
}

static void write_u32(uint8_t *output, uint32_t value) {
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8u);
    output[2] = (uint8_t)(value >> 16u);
    output[3] = (uint8_t)(value >> 24u);
}

static void clear_bytes(uint8_t *bytes, size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        bytes[index] = 0u;
    }
}

void r1_health_initialize(r1_health_state *state) {
    if (state == NULL) {
        return;
    }
    clear_bytes((uint8_t *)state, sizeof *state);
    state->next_notification_serial = 1u;
    state->last_auto_sync_or_query_seconds = 0u;
    r1_health_u8_offline_initialize(&state->heart_rate_offline);
    r1_health_u8_offline_initialize(&state->blood_oxygen_offline);
    r1_health_u16_offline_initialize(&state->heart_rate_variability_offline);
    state->heart_rate_last_sync_seconds = 0u;
    state->blood_oxygen_last_sync_seconds = 0u;
    state->heart_rate_variability_last_sync_seconds = 0u;
    r1_activity_offline_initialize(&state->activity_offline);
    state->activity_last_sync_seconds = 0u;
    state->sleep_sync_commit = NULL;
    state->sleep_sync_context = NULL;
}

void r1_health_note_explicit_history_query(
    r1_health_state *state, uint32_t now_seconds) {
    if (state != NULL) {
        state->last_auto_sync_or_query_seconds = now_seconds;
    }
}

r1_health_auto_sync_result r1_health_run_automatic_sync(
    r1_health_state *state, bool phone_connected, uint32_t now_seconds,
    r1_health_auto_sync_emit_fn emit, void *emit_context) {
    r1_health_auto_sync_result result = {
        R1_HEALTH_AUTO_SYNC_INVALID, false, false, 0u,
    };
    if (state == NULL || emit == NULL) {
        return result;
    }
    if (!phone_connected) {
        result.action = R1_HEALTH_AUTO_SYNC_PHONE_DISCONNECTED;
        return result;
    }

    const uint32_t previous = state->last_auto_sync_or_query_seconds;
    if (previous == 0u) {
        result.action = R1_HEALTH_AUTO_SYNC_INITIAL;
    } else if (now_seconds < previous) {
        result.action = R1_HEALTH_AUTO_SYNC_CLOCK_REWIND;
    } else {
        result.has_elapsed_seconds = true;
        result.elapsed_seconds = now_seconds - previous;
        if (result.elapsed_seconds < R1_HEALTH_AUTO_SYNC_INTERVAL_SECONDS) {
            result.action = R1_HEALTH_AUTO_SYNC_COOLDOWN_ACTIVE;
            return result;
        }
        result.action = R1_HEALTH_AUTO_SYNC_COOLDOWN_ELAPSED;
    }

    static const r1_health_auto_sync_leg legs[] = {
        R1_HEALTH_SYNC_HEART_RATE,
        R1_HEALTH_SYNC_BLOOD_OXYGEN,
        R1_HEALTH_SYNC_HEART_RATE_VARIABILITY,
        R1_HEALTH_SYNC_ACTIVITY,
        R1_HEALTH_SYNC_UNSYNCHRONIZED_SLEEP,
    };
    for (size_t index = 0u; index < sizeof legs / sizeof legs[0]; ++index) {
        emit(emit_context, legs[index], R1_HEALTH_AUTO_SYNC_SERIAL);
    }
    /* Stock updates the shared timestamp after calls without aggregating success. */
    state->last_auto_sync_or_query_seconds = now_seconds;
    result.batch_started = true;
    return result;
}

static int64_t health_local_day_index(
    uint32_t timestamp, int16_t utc_offset_minutes) {
    const int64_t local_seconds = (int64_t)timestamp
        + (int64_t)utc_offset_minutes * INT64_C(60);
    return local_seconds / (int64_t)R1_HEALTH_SECONDS_PER_DAY;
}

bool r1_gomore_time_transition_adapter(
    const r1_health_time_transition *transition,
    r1_gomore_reinitialize_fn reinitialize, void *context) {
    if (transition == NULL ||
        transition->new_timestamp_seconds >= transition->old_timestamp_seconds ||
        transition->old_timestamp_seconds - transition->new_timestamp_seconds <
            R1_HEALTH_GOMORE_REINITIALIZE_SECONDS) {
        return false;
    }
    if (reinitialize != NULL) {
        reinitialize(context);
    }
    return true;
}

r1_error r1_health_plan_time_transition(
    const r1_health_time_transition *transition,
    r1_health_time_transition_result *result) {
    if (transition == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes((uint8_t *)result, sizeof *result);
    result->clock_update_attempted = true;
    result->absolute_delta_seconds =
        transition->old_timestamp_seconds >= transition->new_timestamp_seconds
        ? transition->old_timestamp_seconds - transition->new_timestamp_seconds
        : transition->new_timestamp_seconds - transition->old_timestamp_seconds;
    result->backward_delta_seconds =
        transition->old_timestamp_seconds > transition->new_timestamp_seconds
        ? transition->old_timestamp_seconds - transition->new_timestamp_seconds
        : 0u;
    result->subscriber_broadcast_requested =
        transition->old_utc_offset_minutes != transition->new_utc_offset_minutes
        || result->absolute_delta_seconds
            >= R1_HEALTH_TIME_MATERIAL_CHANGE_SECONDS;
    result->old_timestamp_valid =
        transition->old_timestamp_seconds >= R1_HEALTH_LEGACY_CLOCK_CUTOFF;
    result->new_timestamp_valid =
        transition->new_timestamp_seconds >= R1_HEALTH_LEGACY_CLOCK_CUTOFF;
    result->old_local_day_index = health_local_day_index(
        transition->old_timestamp_seconds,
        transition->old_utc_offset_minutes);
    result->new_local_day_index = health_local_day_index(
        transition->new_timestamp_seconds,
        transition->new_utc_offset_minutes);
    if (!result->subscriber_broadcast_requested) {
        return R1_OK;
    }

    result->gomore_reinitialization_requested =
        r1_gomore_time_transition_adapter(transition, NULL, NULL);
    result->health_database_format_requested =
        result->backward_delta_seconds >= R1_HEALTH_DATABASE_FORMAT_SECONDS;
    result->known_cursor_reset_requested =
        result->health_database_format_requested;
    result->current_day_recovery_requested =
        !result->old_timestamp_valid && result->new_timestamp_valid;
    result->daily_cache_reset_requested = result->old_timestamp_valid
        && result->old_local_day_index != result->new_local_day_index;
    if (result->daily_cache_reset_requested) {
        result->daily_cache_family_count = R1_HEALTH_DAILY_CACHE_FAMILY_COUNT;
    }
    result->known_cursor_clamp_pass_requested = result->old_timestamp_valid
        && transition->new_timestamp_seconds > R1_HEALTH_LEGACY_CLOCK_CUTOFF;
    return R1_OK;
}

r1_error r1_health_sync_cursor_decode(
    const uint8_t *input, size_t length,
    r1_health_sync_cursor_state *cursors) {
    if (input == NULL || cursors == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_HEALTH_SYNC_CURSOR_BYTES) {
        return R1_ERROR_LENGTH;
    }
    cursors->heart_rate_timestamp = read_u32(input);
    cursors->blood_oxygen_timestamp = read_u32(input + 4u);
    cursors->unresolved_offset_8 = read_u32(input + 8u);
    cursors->heart_rate_variability_timestamp = read_u32(input + 12u);
    cursors->activity_timestamp = read_u32(input + 16u);
    cursors->unresolved_offset_20 = read_u32(input + 20u);
    return R1_OK;
}

r1_error r1_health_sync_cursor_encode(
    const r1_health_sync_cursor_state *cursors,
    uint8_t output[R1_HEALTH_SYNC_CURSOR_BYTES]) {
    if (cursors == NULL || output == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    write_u32(output, cursors->heart_rate_timestamp);
    write_u32(output + 4u, cursors->blood_oxygen_timestamp);
    write_u32(output + 8u, cursors->unresolved_offset_8);
    write_u32(output + 12u, cursors->heart_rate_variability_timestamp);
    write_u32(output + 16u, cursors->activity_timestamp);
    write_u32(output + 20u, cursors->unresolved_offset_20);
    return R1_OK;
}

r1_error r1_health_reconcile_sync_cursors(
    r1_health_sync_cursor_state *cursors,
    const r1_health_time_transition *transition,
    r1_health_time_transition_result *result) {
    if (cursors == NULL || transition == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    const r1_error error = r1_health_plan_time_transition(transition, result);
    if (error != R1_OK) {
        return error;
    }
    uint32_t *known[] = {
        &cursors->heart_rate_timestamp,
        &cursors->blood_oxygen_timestamp,
        &cursors->heart_rate_variability_timestamp,
        &cursors->activity_timestamp,
    };
    if (result->known_cursor_reset_requested) {
        for (size_t index = 0u; index < sizeof known / sizeof known[0]; ++index) {
            *known[index] = 0u;
        }
    }
    if (result->known_cursor_clamp_pass_requested) {
        for (size_t index = 0u; index < sizeof known / sizeof known[0]; ++index) {
            if (*known[index] > transition->new_timestamp_seconds) {
                *known[index] = transition->new_timestamp_seconds;
                result->known_cursor_clamped_count = (uint8_t)(
                    result->known_cursor_clamped_count + 1u);
            }
        }
    }
    return R1_OK;
}

r1_error r1_health_plan_hour_boundary(
    uint8_t current_local_hour, r1_health_hour_boundary_result *result) {
    if (result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes((uint8_t *)result, sizeof *result);
    result->current_local_hour = current_local_hour;
    /* These two registered subscribers evaluate their own mode/wear gates for
     * every hour event; this planner does not emulate either provider. */
    result->hrv_eligibility_evaluation_requested = true;
    result->blood_oxygen_eligibility_evaluation_requested = true;
    result->database_writer_accepts_hour =
        current_local_hour < R1_HEALTH_HOURLY_SLOTS;
    if (result->database_writer_accepts_hour) {
        result->has_appended_aggregate_hour = true;
        result->appended_aggregate_hour = current_local_hour == 0u
            ? (uint8_t)(R1_HEALTH_HOURLY_SLOTS - 1u)
            : (uint8_t)(current_local_hour - 1u);
    }
    if (current_local_hour == 0u) {
        result->daily_cache_reset_requested = true;
        result->daily_cache_family_count = R1_HEALTH_DAILY_CACHE_FAMILY_COUNT;
        result->midnight_followup_requested = true;
        result->midnight_followup_has_subscriber = false;
    }
    return R1_OK;
}

static void reset_u8_day(r1_health_u8_history *history, uint32_t local_day_start,
                         int16_t utc_offset_minutes) {
    clear_bytes((uint8_t *)history->slots, sizeof history->slots);
    history->local_day_start = local_day_start;
    history->utc_offset_minutes = utc_offset_minutes;
    history->has_latest = false;
}

static void reset_u16_day(r1_health_u16_history *history, uint32_t local_day_start,
                          int16_t utc_offset_minutes) {
    clear_bytes((uint8_t *)history->slots, sizeof history->slots);
    history->local_day_start = local_day_start;
    history->utc_offset_minutes = utc_offset_minutes;
    history->has_latest = false;
}

r1_error r1_health_record_u8(r1_health_u8_history *history, uint8_t hour,
                             uint8_t value, uint32_t timestamp,
                             uint32_t local_day_start, int16_t utc_offset_minutes) {
    if (history == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (hour >= R1_HEALTH_HOURLY_SLOTS || value == 0u || timestamp < local_day_start) {
        return R1_ERROR_LENGTH;
    }
    if (history->local_day_start != local_day_start ||
        history->utc_offset_minutes != utc_offset_minutes) {
        reset_u8_day(history, local_day_start, utc_offset_minutes);
    }
    r1_health_u8_slot *slot = &history->slots[hour];
    slot->sample_count = (uint16_t)(slot->sample_count + 1u);
    slot->sum += value;
    slot->average = slot->sample_count == 0u
        ? (slot->sum == 0u ? 0u : UINT8_MAX)
        : (uint8_t)(slot->sum / slot->sample_count);
    if (value > slot->maximum) {
        slot->maximum = value;
    }
    if (slot->minimum == 0u || value < slot->minimum) {
        slot->minimum = value;
    }
    history->latest_value = value;
    history->latest_timestamp = timestamp;
    history->has_latest = true;
    return R1_OK;
}

r1_error r1_health_record_u16(r1_health_u16_history *history, uint8_t hour,
                              uint16_t value, uint32_t timestamp,
                              uint32_t local_day_start, int16_t utc_offset_minutes) {
    if (history == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (hour >= R1_HEALTH_HOURLY_SLOTS || value == 0u || timestamp < local_day_start) {
        return R1_ERROR_LENGTH;
    }
    if (history->local_day_start != local_day_start ||
        history->utc_offset_minutes != utc_offset_minutes) {
        reset_u16_day(history, local_day_start, utc_offset_minutes);
    }
    r1_health_u16_slot *slot = &history->slots[hour];
    slot->sample_count = (uint16_t)(slot->sample_count + 1u);
    slot->sum += value;
    const uint32_t average = slot->sample_count == 0u
        ? (slot->sum == 0u ? 0u : UINT16_MAX)
        : slot->sum / slot->sample_count;
    slot->average = average > UINT16_MAX ? UINT16_MAX : (uint16_t)average;
    if (value > slot->maximum) {
        slot->maximum = value;
    }
    if (slot->minimum == 0u || value < slot->minimum) {
        slot->minimum = value;
    }
    history->latest_value = value;
    history->latest_timestamp = timestamp;
    history->has_latest = true;
    return R1_OK;
}

r1_error r1_health_u8_accumulate_average(
    r1_health_u8_accumulator *accumulator, uint8_t hour, uint8_t value,
    uint8_t *average) {
    if (accumulator == NULL || average == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (hour >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }
    if (accumulator->sample_count == 0u || accumulator->hour != hour) {
        clear_bytes((uint8_t *)accumulator, sizeof *accumulator);
        accumulator->hour = hour;
    }
    /* The recovered helper increments a UInt16 count and divides by it. Avoid
     * its wrap-to-zero fault while preserving every reachable normal sample. */
    if (accumulator->sample_count == UINT16_MAX) {
        return R1_ERROR_CAPACITY;
    }
    accumulator->sample_count = (uint16_t)(accumulator->sample_count + 1u);
    accumulator->sum += value;
    *average = (uint8_t)(accumulator->sum / accumulator->sample_count);
    return R1_OK;
}

r1_error r1_health_u16_accumulate_average(
    r1_health_u16_accumulator *accumulator, uint8_t hour, uint16_t value,
    uint16_t *average) {
    if (accumulator == NULL || average == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (hour >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }
    if (accumulator->sample_count == 0u || accumulator->hour != hour) {
        clear_bytes((uint8_t *)accumulator, sizeof *accumulator);
        accumulator->hour = hour;
    }
    /* Stock wraps the UInt16 count and can feed a zero divisor to its
     * floating-point conversion. Preserve normal behavior and fail closed at
     * the otherwise undefined transition. */
    if (accumulator->sample_count == UINT16_MAX) {
        return R1_ERROR_CAPACITY;
    }
    accumulator->sample_count = (uint16_t)(accumulator->sample_count + 1u);
    accumulator->sum += value;
    *average = (uint16_t)(accumulator->sum / accumulator->sample_count);
    return R1_OK;
}

void r1_health_accumulator_snapshot(
    const r1_health_u8_accumulator *accumulator, uint8_t hour,
    uint32_t *sum, uint16_t *sample_count) {
    if (sum == NULL || sample_count == NULL) {
        return;
    }
    *sum = 0u;
    *sample_count = 0u;
    if (accumulator != NULL && accumulator->sample_count != 0u &&
        accumulator->hour == hour) {
        *sum = accumulator->sum;
        *sample_count = accumulator->sample_count;
    }
}

void r1_health_accumulator_restore(
    r1_health_u8_accumulator *accumulator, uint8_t hour,
    uint32_t sum, uint16_t sample_count) {
    if (accumulator == NULL || sample_count == 0u) {
        return;
    }
    accumulator->hour = hour;
    accumulator->sample_count = sample_count;
    accumulator->sum = sum;
}

static uint32_t health_crash_activity_pack(const r1_activity_bucket *bucket) {
    return ((uint32_t)bucket->steps & UINT32_C(0x0fff))
        | (((uint32_t)bucket->active_kilocalories & UINT32_C(0x03ff)) << 12u)
        | (((uint32_t)bucket->all_kilocalories & UINT32_C(0x03ff)) << 22u);
}

r1_error r1_health_build_crash_snapshot(
    r1_health_crash_snapshot *snapshot, uint32_t utc_timestamp,
    int16_t utc_offset_minutes, const r1_activity_history *activity,
    const r1_health_u8_history *heart_rate,
    const r1_health_u8_accumulator *heart_rate_accumulator,
    const r1_health_u8_history *spo2,
    const r1_health_u16_history *hrv) {
    if (snapshot == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes((uint8_t *)snapshot, sizeof *snapshot);

    int16_t clamped_offset = utc_offset_minutes;
    if (clamped_offset > 720) {
        clamped_offset = 720;
    } else if (clamped_offset < -720) {
        clamped_offset = -720;
    }
    const uint32_t adjusted_timestamp = utc_timestamp + (uint32_t)(
        (int32_t)clamped_offset * INT32_C(60));
    const uint8_t hour = (uint8_t)(
        (adjusted_timestamp % R1_HEALTH_SECONDS_PER_DAY) / UINT32_C(3600));
    snapshot->local_hour = hour;

    if (activity != NULL) {
        const size_t start = (size_t)hour * R1_ACTIVITY_BUCKETS_PER_HOUR;
        for (size_t index = 0u; index < R1_ACTIVITY_BUCKETS_PER_HOUR; ++index) {
            snapshot->activity_packed_words[index] =
                health_crash_activity_pack(&activity->buckets[start + index]);
        }
        snapshot->available_flags |= R1_HEALTH_CRASH_FLAG_ACTIVITY;
    }

    if (heart_rate != NULL) {
        uint8_t latest = 0u;
        uint32_t timestamp = 0u;
        if (r1_health_u8_latest_sample(heart_rate, &latest, &timestamp)) {
            snapshot->heart_rate_latest_value = latest;
            snapshot->heart_rate_latest_timestamp = timestamp;
            snapshot->available_flags |= R1_HEALTH_CRASH_FLAG_HEART_RATE;
        }
        const r1_health_u8_slot *slot = &heart_rate->slots[hour];
        if (slot->average != 0u) {
            snapshot->heart_rate_average = slot->average;
            snapshot->heart_rate_maximum = slot->maximum;
            snapshot->heart_rate_minimum = slot->minimum;
            r1_health_accumulator_snapshot(
                heart_rate_accumulator, hour,
                &snapshot->heart_rate_accumulator_sum,
                &snapshot->heart_rate_accumulator_count);
            snapshot->available_flags |= R1_HEALTH_CRASH_FLAG_HEART_RATE;
        }
    }

    if (spo2 != NULL) {
        uint8_t latest = 0u;
        uint32_t timestamp = 0u;
        if (r1_health_u8_latest_sample(spo2, &latest, &timestamp)) {
            snapshot->spo2_latest_value = latest;
            snapshot->spo2_latest_timestamp = timestamp;
            snapshot->available_flags |= R1_HEALTH_CRASH_FLAG_SPO2;
        }
    }

    if (hrv != NULL) {
        uint16_t latest = 0u;
        uint32_t timestamp = 0u;
        if (r1_health_u16_latest_sample(hrv, &latest, &timestamp)) {
            snapshot->hrv_latest_value = latest;
            snapshot->hrv_latest_timestamp = timestamp;
            snapshot->available_flags |= R1_HEALTH_CRASH_FLAG_HRV;
        }
    }
    return R1_OK;
}

bool r1_health_crash_record_valid(const r1_health_crash_record *record) {
    if (record == NULL || read_u32(record->bytes) != R1_HEALTH_CRASH_MAGIC) {
        return false;
    }
    return read_u16(record->bytes + R1_HEALTH_CRASH_RECORD_CRC_OFFSET) ==
        r1_crc16_modbus(record->bytes, R1_HEALTH_CRASH_RECORD_CRC_OFFSET);
}

bool r1_health_crash_record_has_magic(const r1_health_crash_record *record) {
    return record != NULL && read_u32(record->bytes) == R1_HEALTH_CRASH_MAGIC;
}

static void health_crash_record_reseal(r1_health_crash_record *record) {
    write_u16(record->bytes + R1_HEALTH_CRASH_RECORD_CRC_OFFSET,
              r1_crc16_modbus(record->bytes, R1_HEALTH_CRASH_RECORD_CRC_OFFSET));
}

r1_error r1_health_crash_record_clear_provider_blob(
    r1_health_crash_record *record) {
    if (record == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes(record->bytes + R1_HEALTH_CRASH_BLOB_OFFSET,
                R1_HEALTH_CRASH_BLOB_BYTES + 4u);
    health_crash_record_reseal(record);
    return R1_OK;
}

r1_error r1_health_crash_record_clear_snapshot(
    r1_health_crash_record *record) {
    if (record == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes(record->bytes + R1_HEALTH_CRASH_SNAPSHOT_OFFSET,
                R1_HEALTH_CRASH_SNAPSHOT_BYTES);
    health_crash_record_reseal(record);
    return R1_OK;
}

r1_error r1_health_crash_record_clear_time(
    r1_health_crash_record *record) {
    if (record == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes(record->bytes + 4u, 8u);
    health_crash_record_reseal(record);
    return R1_OK;
}

bool r1_health_crash_record_get_provider_blob(
    const r1_health_crash_record *record, const uint8_t **provider_blob,
    size_t *provider_blob_length) {
    if (provider_blob == NULL || provider_blob_length == NULL ||
        !r1_health_crash_record_valid(record) ||
        read_u32(record->bytes + R1_HEALTH_CRASH_BLOB_MAGIC_OFFSET) !=
            R1_HEALTH_CRASH_MAGIC) {
        return false;
    }
    *provider_blob = record->bytes + R1_HEALTH_CRASH_BLOB_OFFSET;
    *provider_blob_length = R1_HEALTH_CRASH_BLOB_BYTES;
    return true;
}

bool r1_health_crash_record_get_snapshot(
    const r1_health_crash_record *record,
    r1_health_crash_snapshot *snapshot) {
    if (snapshot == NULL || !r1_health_crash_record_valid(record)) {
        return false;
    }
    const uint8_t hour = record->bytes[
        R1_HEALTH_CRASH_SNAPSHOT_OFFSET +
        offsetof(r1_health_crash_snapshot, local_hour)];
    const uint8_t flags = record->bytes[
        R1_HEALTH_CRASH_SNAPSHOT_OFFSET +
        offsetof(r1_health_crash_snapshot, available_flags)];
    if (flags == 0u || hour >= R1_HEALTH_HOURLY_SLOTS) {
        return false;
    }
    uint8_t *destination = (uint8_t *)snapshot;
    for (size_t index = 0u; index < sizeof *snapshot; ++index) {
        destination[index] =
            record->bytes[R1_HEALTH_CRASH_SNAPSHOT_OFFSET + index];
    }
    return true;
}

bool r1_health_crash_record_get_time(
    const r1_health_crash_record *record, r1_health_crash_time *time) {
    if (time == NULL || !r1_health_crash_record_valid(record)) {
        return false;
    }
    const uint32_t timestamp = read_u32(record->bytes + 8u);
    if (timestamp == 0u) {
        return false;
    }
    time->utc_timestamp = timestamp;
    time->utc_offset_minutes = (int16_t)read_u16(record->bytes + 6u);
    time->clock_valid = (record->bytes[4] & 1u) != 0u;
    return true;
}

r1_error r1_health_crash_record_initialize(
    r1_health_crash_record *record, uint16_t time_status_flags,
    bool clock_valid, uint32_t utc_timestamp, int16_t utc_offset_minutes,
    const uint8_t *provider_blob, size_t provider_blob_length,
    const r1_activity_history *activity,
    const r1_health_u8_history *heart_rate,
    const r1_health_u8_accumulator *heart_rate_accumulator,
    const r1_health_u8_history *spo2,
    const r1_health_u16_history *hrv, bool *provider_blob_copied) {
    if (record == NULL || provider_blob_copied == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *provider_blob_copied = false;
    write_u32(record->bytes, R1_HEALTH_CRASH_MAGIC);
    write_u16(record->bytes + 4u, (uint16_t)(
        (time_status_flags & UINT16_C(0xfffe)) | (clock_valid ? 1u : 0u)));
    write_u16(record->bytes + 6u, (uint16_t)utc_offset_minutes);
    write_u32(record->bytes + 8u, utc_timestamp);

    if (provider_blob != NULL && provider_blob_length == R1_HEALTH_CRASH_BLOB_BYTES) {
        for (size_t index = 0u; index < R1_HEALTH_CRASH_BLOB_BYTES; ++index) {
            record->bytes[R1_HEALTH_CRASH_BLOB_OFFSET + index] = provider_blob[index];
        }
        write_u32(record->bytes + R1_HEALTH_CRASH_BLOB_MAGIC_OFFSET,
                  R1_HEALTH_CRASH_MAGIC);
        *provider_blob_copied = true;
    }

    r1_health_crash_snapshot snapshot;
    const r1_error error = r1_health_build_crash_snapshot(
        &snapshot, utc_timestamp, utc_offset_minutes, activity, heart_rate,
        heart_rate_accumulator, spo2, hrv);
    if (error != R1_OK) {
        return error;
    }
    const uint8_t *snapshot_bytes = (const uint8_t *)&snapshot;
    for (size_t index = 0u; index < sizeof snapshot; ++index) {
        record->bytes[R1_HEALTH_CRASH_SNAPSHOT_OFFSET + index] = snapshot_bytes[index];
    }
    health_crash_record_reseal(record);
    return R1_OK;
}

r1_error r1_health_crash_record_restore(
    r1_health_crash_record *record, r1_activity_history *activity,
    r1_health_u8_history *heart_rate,
    r1_health_u8_accumulator *heart_rate_accumulator,
    r1_health_u8_history *spo2, r1_health_u16_history *hrv,
    r1_health_crash_restore_result *result) {
    if (record == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes((uint8_t *)result, sizeof *result);
    if (!r1_health_crash_record_has_magic(record)) {
        result->action = R1_HEALTH_CRASH_NO_MAGIC;
        return R1_OK;
    }

    r1_health_crash_snapshot snapshot;
    if (!r1_health_crash_record_get_snapshot(record, &snapshot)) {
        result->action = R1_HEALTH_CRASH_INVALID_OR_EMPTY;
        return R1_OK;
    }
    result->action = R1_HEALTH_CRASH_RESTORED;
    result->local_hour = snapshot.local_hour;
    result->available_flags = snapshot.available_flags;

    if ((snapshot.available_flags & R1_HEALTH_CRASH_FLAG_ACTIVITY) != 0u &&
        activity != NULL) {
        const size_t start =
            (size_t)snapshot.local_hour * R1_ACTIVITY_BUCKETS_PER_HOUR;
        for (size_t index = 0u; index < R1_ACTIVITY_BUCKETS_PER_HOUR; ++index) {
            r1_activity_bucket *bucket = &activity->buckets[start + index];
            if (bucket->valid) {
                activity->total_steps -= bucket->steps;
                activity->total_kilocalories = (int16_t)(
                    activity->total_kilocalories -
                    (int16_t)bucket->all_kilocalories);
            }
            const uint32_t packed = snapshot.activity_packed_words[index];
            bucket->steps = (uint16_t)(
                ((uint32_t)bucket->steps +
                 (packed & UINT32_C(0x0fff))) & UINT32_C(0x0fff));
            bucket->active_kilocalories = (uint16_t)(
                ((uint32_t)bucket->active_kilocalories +
                 ((packed >> 12u) & UINT32_C(0x03ff))) & UINT32_C(0x03ff));
            bucket->all_kilocalories = (uint16_t)(
                ((uint32_t)bucket->all_kilocalories +
                 (packed >> 22u)) & UINT32_C(0x03ff));
            bucket->valid = bucket->steps != 0u ||
                bucket->active_kilocalories != 0u ||
                bucket->all_kilocalories != 0u;
            if (bucket->valid) {
                activity->total_steps += bucket->steps;
                activity->total_kilocalories = (int16_t)(
                    activity->total_kilocalories +
                    (int16_t)bucket->all_kilocalories);
            }
            result->activity_bucket_count += 1u;
        }
    }

    if ((snapshot.available_flags & R1_HEALTH_CRASH_FLAG_HEART_RATE) != 0u &&
        heart_rate != NULL) {
        r1_health_u8_slot *slot = &heart_rate->slots[snapshot.local_hour];
        if (snapshot.heart_rate_average != 0u) {
            slot->average = snapshot.heart_rate_average;
        }
        if (snapshot.heart_rate_maximum > slot->maximum) {
            slot->maximum = snapshot.heart_rate_maximum;
        }
        if (snapshot.heart_rate_minimum != 0u &&
            (slot->minimum == 0u || snapshot.heart_rate_minimum < slot->minimum)) {
            slot->minimum = snapshot.heart_rate_minimum;
        }
        if (snapshot.heart_rate_latest_value != 0u) {
            heart_rate->latest_value = snapshot.heart_rate_latest_value;
            heart_rate->latest_timestamp = snapshot.heart_rate_latest_timestamp;
            heart_rate->has_latest = true;
        }
        if (snapshot.heart_rate_accumulator_count != 0u &&
            heart_rate_accumulator != NULL) {
            r1_health_accumulator_restore(
                heart_rate_accumulator, snapshot.local_hour,
                snapshot.heart_rate_accumulator_sum,
                snapshot.heart_rate_accumulator_count);
            result->heart_rate_accumulator_applied = true;
        }
        result->heart_rate_applied = true;
    }

    if ((snapshot.available_flags & R1_HEALTH_CRASH_FLAG_SPO2) != 0u &&
        spo2 != NULL && snapshot.spo2_latest_value != 0u) {
        r1_health_u8_slot *slot = &spo2->slots[snapshot.local_hour];
        if (slot->average == 0u) {
            slot->average = snapshot.spo2_latest_value;
            slot->maximum = snapshot.spo2_latest_value;
            slot->minimum = snapshot.spo2_latest_value;
        }
        spo2->latest_value = snapshot.spo2_latest_value;
        spo2->latest_timestamp = snapshot.spo2_latest_timestamp;
        spo2->has_latest = true;
        result->spo2_applied = true;
    }

    if ((snapshot.available_flags & R1_HEALTH_CRASH_FLAG_HRV) != 0u &&
        hrv != NULL && snapshot.hrv_latest_value != 0u) {
        r1_health_u16_slot *slot = &hrv->slots[snapshot.local_hour];
        if (slot->average == 0u) {
            slot->average = snapshot.hrv_latest_value;
            slot->maximum = snapshot.hrv_latest_value;
            slot->minimum = snapshot.hrv_latest_value;
        }
        hrv->latest_value = snapshot.hrv_latest_value;
        hrv->latest_timestamp = snapshot.hrv_latest_timestamp;
        hrv->has_latest = true;
        result->hrv_applied = true;
    }

    const r1_error clear_error = r1_health_crash_record_clear_snapshot(record);
    if (clear_error != R1_OK) {
        return clear_error;
    }
    result->snapshot_cleared = true;
    return R1_OK;
}

bool r1_health_u8_latest_sample(
    const r1_health_u8_history *history, uint8_t *value,
    uint32_t *timestamp) {
    if (history == NULL || value == NULL || timestamp == NULL ||
        !history->has_latest || history->latest_value == 0u) {
        return false;
    }
    *value = history->latest_value;
    *timestamp = history->latest_timestamp;
    return true;
}

bool r1_health_u16_latest_sample(
    const r1_health_u16_history *history, uint16_t *value,
    uint32_t *timestamp) {
    if (history == NULL || value == NULL || timestamp == NULL ||
        !history->has_latest || history->latest_value == 0u) {
        return false;
    }
    *value = history->latest_value;
    *timestamp = history->latest_timestamp;
    return true;
}

static r1_error health_store_u8_sample(
    r1_health_u8_history *history, r1_health_u8_accumulator *accumulator,
    uint8_t value, uint32_t effective_timestamp, bool timestamp_replaced,
    uint8_t aggregate_hour, uint8_t average_hour, uint8_t minimum,
    uint8_t maximum, uint8_t notification_metric,
    r1_health_u8_sample_result *result) {
    if (history == NULL || accumulator == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes((uint8_t *)result, sizeof *result);
    result->published_value = value;
    if (value < minimum || value > maximum) {
        result->action = R1_HEALTH_U8_SAMPLE_REJECTED_RANGE;
        return R1_OK;
    }
    if (aggregate_hour >= R1_HEALTH_HOURLY_SLOTS ||
        average_hour >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }

    uint8_t average = 0u;
    const r1_error error = r1_health_u8_accumulate_average(
        accumulator, average_hour, value, &average);
    if (error != R1_OK) {
        return error;
    }
    r1_health_u8_slot *slot = &history->slots[aggregate_hour];
    slot->average = average;
    if (value > slot->maximum) {
        slot->maximum = value;
    }
    if (slot->minimum == 0u || value < slot->minimum) {
        slot->minimum = value;
    }
    history->latest_value = value;
    history->latest_timestamp = effective_timestamp;
    history->has_latest = true;
    result->action = R1_HEALTH_U8_SAMPLE_STORED;
    result->stored_value = value;
    result->effective_timestamp = effective_timestamp;
    result->timestamp_replaced = timestamp_replaced;
    result->notification_requested = true;
    result->notification_metric = notification_metric;
    return R1_OK;
}

r1_error r1_heart_rate_store_sample(
    r1_health_u8_history *history, r1_health_u8_accumulator *accumulator,
    uint8_t value, uint32_t event_timestamp, uint32_t firmware_timestamp,
    uint8_t aggregate_hour, uint8_t average_hour,
    r1_health_u8_sample_result *result) {
    const bool replace_timestamp = event_timestamp == 0u;
    return health_store_u8_sample(
        history, accumulator, value,
        replace_timestamp ? firmware_timestamp : event_timestamp,
        replace_timestamp, aggregate_hour, average_hour,
        R1_HEART_RATE_VALUE_MIN, R1_HEART_RATE_VALUE_MAX,
        R1_HEALTH_NOTIFICATION_HEART_RATE, result);
}

bool r1_hr_value_plausible(uint8_t heart_rate) {
    return heart_rate >= R1_HEART_RATE_VALUE_MIN &&
           heart_rate <= R1_HEART_RATE_VALUE_MAX;
}

static r1_error hr_result_plan_build(
    r1_hr_result_kind kind, const uint8_t *record, size_t record_length,
    bool health_publication_enabled, uint32_t firmware_clock,
    r1_hr_result_plan *plan) {
    if (record == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (record_length != R1_HEART_RATE_RESULT_RECORD_BYTES) {
        return R1_ERROR_LENGTH;
    }

    clear_bytes((uint8_t *)plan, sizeof *plan);
    plan->kind = kind;
    plan->heart_rate = record[0];
    plan->confidence = record[1];
    plan->signal = record[2];
    plan->value_plausible = r1_hr_value_plausible(plan->heart_rate);
    plan->health_publication_enabled = health_publication_enabled;
    plan->unregister_hr_stream = true;
    plan->clear_stream_handle = true;
    plan->release_timing_timer = kind == R1_HR_RESULT_TIMING;
    plan->clear_timing_timer_handle = kind == R1_HR_RESULT_TIMING;

    if (plan->value_plausible && health_publication_enabled) {
        plan->publish_event = true;
        plan->event_id = R1_HEART_RATE_PUBLICATION_EVENT;
        plan->event_payload[0] = plan->heart_rate;
        write_u32(plan->event_payload + 4u, firmware_clock);
        plan->event_payload_length = R1_HEART_RATE_PUBLICATION_BYTES;
    }
    return R1_OK;
}

r1_error r1_hr_once_result_plan(
    const uint8_t *record, size_t record_length,
    bool health_publication_enabled, uint32_t firmware_clock,
    r1_hr_result_plan *plan) {
    return hr_result_plan_build(
        R1_HR_RESULT_ONCE, record, record_length,
        health_publication_enabled, firmware_clock, plan);
}

r1_error r1_hr_timing_result_plan(
    const uint8_t *record, size_t record_length,
    bool health_publication_enabled, uint32_t firmware_clock,
    r1_hr_result_plan *plan) {
    return hr_result_plan_build(
        R1_HR_RESULT_TIMING, record, record_length,
        health_publication_enabled, firmware_clock, plan);
}

static r1_error spo2_result_plan_build(
    r1_spo2_result_kind kind, const uint8_t *record, size_t record_length,
    bool health_publication_enabled, r1_spo2_result_plan *plan) {
    if (record == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (record_length != R1_SPO2_RESULT_RECORD_BYTES) {
        return R1_ERROR_LENGTH;
    }

    clear_bytes((uint8_t *)plan, sizeof *plan);
    plan->kind = kind;
    plan->raw_spo2 = record[0];
    plan->r_value = record[1];
    plan->confidence = record[2];
    plan->level = (int8_t)record[3];
    plan->heart_rate = record[4];
    plan->mark = record[5];
    plan->value_plausible =
        gomore_primitives_byte_in_70_100(plan->raw_spo2);
    plan->health_publication_enabled = health_publication_enabled;
    plan->unregister_spo2_stream = true;
    plan->clear_stream_handle = true;
    plan->release_timing_timer = kind == R1_SPO2_RESULT_TIMING;
    plan->clear_timing_timer_handle = kind == R1_SPO2_RESULT_TIMING;
    if (kind == R1_SPO2_RESULT_TIMING) {
        plan->mark_valid_result_seen = plan->value_plausible;
        plan->mark_invalid_result_seen = !plan->value_plausible;
    }

    if (plan->value_plausible && health_publication_enabled) {
        plan->adjusted_spo2 =
            gomore_primitives_piecewise_clamp_70_100(plan->raw_spo2);
        plan->publish_event = true;
        plan->event_id = R1_SPO2_PUBLICATION_EVENT;
        plan->event_payload[0] = plan->adjusted_spo2;
        plan->event_payload_length = R1_SPO2_PUBLICATION_BYTES;
    }
    return R1_OK;
}

r1_error r1_spo2_once_result_plan(
    const uint8_t *record, size_t record_length,
    bool health_publication_enabled, r1_spo2_result_plan *plan) {
    return spo2_result_plan_build(
        R1_SPO2_RESULT_ONCE, record, record_length,
        health_publication_enabled, plan);
}

r1_error r1_spo2_timing_result_plan(
    const uint8_t *record, size_t record_length,
    bool health_publication_enabled, r1_spo2_result_plan *plan) {
    return spo2_result_plan_build(
        R1_SPO2_RESULT_TIMING, record, record_length,
        health_publication_enabled, plan);
}

r1_error r1_spo2_store_sample(
    r1_health_u8_history *history, r1_health_u8_accumulator *accumulator,
    uint8_t value, uint32_t event_timestamp, uint32_t firmware_timestamp,
    uint8_t aggregate_hour, uint8_t average_hour,
    r1_health_u8_sample_result *result) {
    (void)event_timestamp;
    return health_store_u8_sample(
        history, accumulator, value, firmware_timestamp, true,
        aggregate_hour, average_hour, R1_SPO2_VALUE_MIN, UINT8_MAX,
        R1_HEALTH_NOTIFICATION_SPO2, result);
}

r1_error r1_hrv_store_sample(
    r1_health_u16_history *history, r1_health_u16_accumulator *accumulator,
    uint16_t rmssd, uint32_t event_timestamp, uint32_t firmware_timestamp,
    uint8_t aggregate_hour, uint8_t average_hour,
    r1_health_u16_sample_result *result) {
    if (history == NULL || accumulator == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes((uint8_t *)result, sizeof *result);
    if (aggregate_hour >= R1_HEALTH_HOURLY_SLOTS ||
        average_hour >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }
    uint16_t average = 0u;
    const r1_error error = r1_health_u16_accumulate_average(
        accumulator, average_hour, rmssd, &average);
    if (error != R1_OK) {
        return error;
    }
    r1_health_u16_slot *slot = &history->slots[aggregate_hour];
    slot->average = average;
    if (rmssd > slot->maximum) {
        slot->maximum = rmssd;
    }
    if (slot->minimum == 0u || rmssd < slot->minimum) {
        slot->minimum = rmssd;
    }
    const bool replace_timestamp = event_timestamp == 0u;
    const uint32_t effective_timestamp = replace_timestamp
        ? firmware_timestamp : event_timestamp;
    history->latest_value = rmssd;
    history->latest_timestamp = effective_timestamp;
    history->has_latest = true;
    result->action = R1_HEALTH_U8_SAMPLE_STORED;
    result->stored_value = rmssd;
    result->effective_timestamp = effective_timestamp;
    result->timestamp_replaced = replace_timestamp;
    result->notification_requested = true;
    result->notification_metric = R1_HEALTH_NOTIFICATION_HRV;
    return R1_OK;
}

typedef struct {
    uint16_t packed_command;
    uint8_t residue;
    bool publishes_event14;
    r1_health_history_action action;
    uint8_t metric;
    uint8_t query_kind;
} health_history_registration;

static const health_history_registration health_history_registrations[] = {
    {UINT16_C(0x0101), 0u, true, R1_HEALTH_HISTORY_HEART_RATE_DAILY, 0u, 1u},
    {UINT16_C(0x0102), 1u, true, R1_HEALTH_HISTORY_HEART_RATE_POINT, 0u, 0u},
    {UINT16_C(0x0103), 0u, false, R1_HEALTH_HISTORY_HEART_RATE_POINT, 0u, 0u},
    {UINT16_C(0x0201), 3u, true, R1_HEALTH_HISTORY_SPO2_DAILY, 1u, 1u},
    {UINT16_C(0x0202), 3u, true, R1_HEALTH_HISTORY_SPO2_POINT, 1u, 0u},
    {UINT16_C(0x0203), 5u, false, R1_HEALTH_HISTORY_SPO2_POINT, 1u, 0u},
    {UINT16_C(0x0401), 0u, true, R1_HEALTH_HISTORY_HRV_DAILY, 5u, 1u},
    {UINT16_C(0x0402), 7u, true, R1_HEALTH_HISTORY_HRV_POINT, 5u, 0u},
    {UINT16_C(0x0403), 7u, false, R1_HEALTH_HISTORY_HRV_POINT, 5u, 0u},
    {UINT16_C(0x0501), 9u, true, R1_HEALTH_HISTORY_ACTIVITY_DAILY, 4u, 1u},
    {UINT16_C(0x0502), 7u, true, R1_HEALTH_HISTORY_ACTIVITY_REFRESH, 4u, 0u},
    {UINT16_C(0x0601), 11u, true, R1_HEALTH_HISTORY_SLEEP_DAILY, 6u, 1u},
    {UINT16_C(0x0602), 11u, false, R1_HEALTH_HISTORY_SLEEP_DAILY, 6u, 0u},
    {UINT16_C(0x7f01), 13u, false, R1_HEALTH_HISTORY_SLEEP_DAILY, 0u, 0u},
};

void r1_health_history_noop_handler(void) {
}

bool r1_health_daily_test_event_valid(const uint8_t *payload, size_t length) {
    return payload != NULL && length == 9u;
}

bool r1_health_history_event_valid(const uint8_t *payload, size_t length) {
    return payload != NULL && length == R1_HEALTH_HISTORY_EVENT_BYTES;
}

static bool health_auxiliary_request_accepted(uint8_t request_flags) {
    /* The recovered handlers require bit 1 and reject bit 0. */
    return (request_flags & UINT8_C(0x02)) != 0u
        && (request_flags & UINT8_C(0x01)) == 0u;
}

static r1_error health_auxiliary_plan_initialize(
    r1_health_auxiliary_plan *plan, r1_health_auxiliary_action action,
    uint8_t request_flags) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes((uint8_t *)plan, sizeof *plan);
    plan->action = action;
    plan->accepted = health_auxiliary_request_accepted(request_flags);
    return R1_OK;
}

r1_error r1_sleep_detail_plan(
    uint8_t request_flags, r1_health_auxiliary_plan *plan) {
    const r1_error error = health_auxiliary_plan_initialize(
        plan, R1_HEALTH_AUXILIARY_SLEEP_DETAIL, request_flags);
    if (error != R1_OK || !plan->accepted) {
        return error;
    }
    plan->private_event_requested = true;
    plan->private_event = UINT16_C(0x100e);
    return R1_OK;
}

static r1_error health_measurement_plan(
    uint8_t request_flags, uint16_t request_serial,
    r1_health_auxiliary_action action, uint16_t provider_command,
    uint16_t private_event, r1_health_auxiliary_plan *plan) {
    const r1_error error = health_auxiliary_plan_initialize(
        plan, action, request_flags);
    if (error != R1_OK || !plan->accepted) {
        return error;
    }
    plan->provider_command_requested = true;
    plan->provider_command = provider_command;
    plan->provider_mode = 2u;
    plan->request_serial = request_serial;
    plan->private_event_requested = true;
    plan->private_event = private_event;
    plan->private_event_payload_length = 1u;
    plan->private_event_payload = 1u;
    return R1_OK;
}

r1_error r1_heart_rate_measurement_plan(
    uint8_t request_flags, uint16_t request_serial,
    r1_health_auxiliary_plan *plan) {
    return health_measurement_plan(
        request_flags, request_serial,
        R1_HEALTH_AUXILIARY_HEART_RATE_MEASUREMENT,
        UINT16_C(0x0103), UINT16_C(0x1002), plan);
}

r1_error r1_spo2_measurement_plan(
    uint8_t request_flags, uint16_t request_serial,
    r1_health_auxiliary_plan *plan) {
    return health_measurement_plan(
        request_flags, request_serial, R1_HEALTH_AUXILIARY_SPO2_MEASUREMENT,
        UINT16_C(0x0203), UINT16_C(0x1004), plan);
}

r1_error r1_health_report_setting_plan(
    bool payload_present, uint8_t payload_value,
    r1_health_auxiliary_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes((uint8_t *)plan, sizeof *plan);
    plan->action = R1_HEALTH_AUXILIARY_REPORT_SETTING;
    plan->accepted = true;
    plan->report_setting_update_requested = true;
    /* The stock zero-payload path obtains a false byte from address zero.
     * Model that result directly instead of reproducing a null flash read. */
    plan->report_enabled = payload_present && payload_value != 0u;
    return R1_OK;
}

static r1_error stress_control_plan_initialize(
    r1_stress_control_plan *plan, r1_stress_control_action action,
    uint8_t payload_value, size_t payload_length) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes((uint8_t *)plan, sizeof *plan);
    plan->action = action;
    plan->raw_value = payload_value;
    plan->accepted = payload_length == 1u;
    return R1_OK;
}

r1_error r1_stress_mode_control_plan(
    uint8_t payload_value, size_t payload_length,
    r1_stress_control_plan *plan) {
    const r1_error error = stress_control_plan_initialize(
        plan, R1_STRESS_CONTROL_MODE, payload_value, payload_length);
    if (error != R1_OK || !plan->accepted) {
        return error;
    }
    /* The wrapper forwards every one-byte value. The downstream stock setter
     * performs no transition unless the unsigned value is below two. */
    plan->mode_update_requested = payload_value < 2u;
    plan->mode = payload_value;
    return R1_OK;
}

r1_error r1_stress_measurement_control_plan(
    uint8_t payload_value, size_t payload_length,
    r1_stress_control_plan *plan) {
    const r1_error error = stress_control_plan_initialize(
        plan, R1_STRESS_CONTROL_MEASUREMENT, payload_value, payload_length);
    if (error != R1_OK || !plan->accepted) {
        return error;
    }
    plan->measurement_update_requested = true;
    plan->measurement_enabled = payload_value != 0u;
    return R1_OK;
}

static r1_error factory_optical_plan_initialize(
    const uint8_t *record, size_t record_length, size_t expected_length,
    r1_factory_optical_metric metric,
    r1_factory_optical_diagnostic_plan *plan) {
    if (record == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (record_length != expected_length) {
        return R1_ERROR_LENGTH;
    }
    clear_bytes((uint8_t *)plan, sizeof *plan);
    plan->metric = metric;
    return R1_OK;
}

r1_error r1_factory_heart_rate_diagnostic_plan(
    const uint8_t *record, size_t record_length,
    r1_factory_optical_diagnostic_plan *plan) {
    const r1_error error = factory_optical_plan_initialize(
        record, record_length, 3u, R1_FACTORY_OPTICAL_HEART_RATE, plan);
    if (error != R1_OK) {
        return error;
    }
    /* The stock callback loads all three bytes into variadic argument
     * registers even though its format string consumes only the first. */
    plan->raw_value = record[0];
    plan->normalized_value = record[0];
    plan->text_values[0] = record[0];
    plan->text_values[1] = record[1];
    plan->text_values[2] = record[2];
    plan->text_value_count = 3u;
    return R1_OK;
}

r1_error r1_factory_spo2_diagnostic_plan(
    const uint8_t *record, size_t record_length,
    r1_factory_optical_diagnostic_plan *plan) {
    const r1_error error = factory_optical_plan_initialize(
        record, record_length, 1u, R1_FACTORY_OPTICAL_SPO2, plan);
    if (error != R1_OK) {
        return error;
    }
    plan->raw_value = record[0];
    plan->normalized_value = record[0];
    plan->text_values[0] = record[0];
    plan->text_value_count = 1u;
    return R1_OK;
}

r1_error r1_factory_hrv_diagnostic_plan(
    const uint8_t *record, size_t record_length,
    r1_factory_optical_diagnostic_plan *plan) {
    const r1_error error = factory_optical_plan_initialize(
        record, record_length, 8u, R1_FACTORY_OPTICAL_HRV, plan);
    if (error != R1_OK) {
        return error;
    }
    plan->raw_value = read_u16(record);
    plan->normalized_value = plan->raw_value;
    for (size_t index = 0u; index < 4u; ++index) {
        plan->text_values[index] = read_u16(record + (index * 2u));
    }
    plan->text_value_count = 4u;
    return R1_OK;
}

r1_error r1_factory_temperature_diagnostic_plan(
    const uint8_t *record, size_t record_length,
    r1_factory_optical_diagnostic_plan *plan) {
    const r1_error error = factory_optical_plan_initialize(
        record, record_length, 2u, R1_FACTORY_OPTICAL_TEMPERATURE, plan);
    if (error != R1_OK) {
        return error;
    }
    plan->raw_value = read_u16(record);
    plan->normalized_value = (uint16_t)(plan->raw_value / 100u);
    plan->text_values[0] = (uint8_t)(plan->normalized_value / 10u);
    plan->text_values[1] = (uint8_t)(plan->normalized_value % 10u);
    plan->text_value_count = 2u;
    plan->record_update_requested = true;
    return R1_OK;
}

static r1_error factory_stream_control_plan(
    r1_factory_stream_metric metric, bool register_stream,
    bool handle_present, r1_factory_stream_control_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_factory_stream_control_plan){
        .metric = metric,
        .action = R1_FACTORY_STREAM_NO_ACTION,
        .handle_was_present = handle_present,
    };
    if (register_stream) {
        if (!handle_present) {
            plan->action = R1_FACTORY_STREAM_REGISTER;
        }
    } else if (handle_present) {
        plan->action = R1_FACTORY_STREAM_UNREGISTER;
    }
    return R1_OK;
}

r1_error r1_factory_acc_stream_register_plan(
    bool handle_present, r1_factory_stream_control_plan *plan) {
    return factory_stream_control_plan(
        R1_FACTORY_STREAM_ACC, true, handle_present, plan);
}

r1_error r1_factory_heart_rate_stream_unregister_plan(
    bool handle_present, r1_factory_stream_control_plan *plan) {
    return factory_stream_control_plan(
        R1_FACTORY_STREAM_HEART_RATE, false, handle_present, plan);
}

r1_error r1_factory_heart_rate_stream_register_plan(
    bool handle_present, r1_factory_stream_control_plan *plan) {
    return factory_stream_control_plan(
        R1_FACTORY_STREAM_HEART_RATE, true, handle_present, plan);
}

r1_error r1_factory_hrv_stream_register_plan(
    bool handle_present, r1_factory_stream_control_plan *plan) {
    return factory_stream_control_plan(
        R1_FACTORY_STREAM_HRV, true, handle_present, plan);
}

r1_error r1_factory_spo2_stream_register_plan(
    bool handle_present, r1_factory_stream_control_plan *plan) {
    return factory_stream_control_plan(
        R1_FACTORY_STREAM_SPO2, true, handle_present, plan);
}

r1_error r1_factory_temperature_stream_unregister_plan(
    bool handle_present, r1_factory_stream_control_plan *plan) {
    return factory_stream_control_plan(
        R1_FACTORY_STREAM_TEMPERATURE, false, handle_present, plan);
}

r1_error r1_factory_temperature_stream_register_plan(
    bool handle_present, r1_factory_stream_control_plan *plan) {
    return factory_stream_control_plan(
        R1_FACTORY_STREAM_TEMPERATURE, true, handle_present, plan);
}

r1_error r1_factory_acc_diagnostic_plan_decode(
    const uint8_t *record, size_t record_length,
    r1_factory_acc_diagnostic_plan *plan) {
    if (record == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (record_length != R1_FACTORY_ACC_RESULT_BYTES) {
        return R1_ERROR_LENGTH;
    }
    clear_bytes((uint8_t *)plan, sizeof *plan);
    const uint16_t record_count = read_u16(
        record + (R1_FACTORY_ACC_RECORD_COUNT * R1_FACTORY_ACC_RECORD_STRIDE));
    if (record_count > R1_FACTORY_ACC_RECORD_COUNT) {
        return R1_ERROR_LENGTH;
    }
    plan->record_count = record_count;
    plan->terminator_requested = true;
    for (uint16_t record_index = 0u; record_index < record_count;
         record_index += R1_FACTORY_ACC_DIAGNOSTIC_DECIMATION) {
        const size_t offset =
            (size_t)record_index * R1_FACTORY_ACC_RECORD_STRIDE;
        r1_factory_acc_diagnostic_sample *sample =
            &plan->samples[plan->sample_count++];
        *sample = (r1_factory_acc_diagnostic_sample){
            .record_index = (uint8_t)record_index,
            .x = (int16_t)read_u16(record + offset),
            .y = (int16_t)read_u16(record + offset + 2u),
            .z = (int16_t)read_u16(record + offset + 4u),
        };
    }
    return R1_OK;
}

r1_error r1_factory_battery_diagnostic_plan_build(
    uint16_t battery_millivolts, uint8_t battery_percent,
    uint8_t battery_type, r1_factory_battery_diagnostic_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_factory_battery_diagnostic_plan){
        .battery_millivolts = battery_millivolts,
        .battery_percent = battery_percent,
        .battery_type = battery_type,
        .handler_return_value = 1u,
    };
    return R1_OK;
}

r1_error r1_factory_activity_diagnostic_plan_decode(
    const uint8_t *record, size_t record_length,
    r1_factory_activity_diagnostic_plan *plan) {
    if (record == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (record_length != 8u) {
        return R1_ERROR_LENGTH;
    }
    *plan = (r1_factory_activity_diagnostic_plan){
        .all_kilocalories = read_u32(record),
        .steps = read_u16(record + 4u),
        .active_kilocalories = read_u16(record + 6u),
    };
    return R1_OK;
}

r1_error r1_factory_temperature_pair_diagnostic_plan_decode(
    const uint8_t *record, size_t record_length,
    r1_factory_temperature_pair_diagnostic_plan *plan) {
    if (record == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (record_length != 5u) {
        return R1_ERROR_LENGTH;
    }
    const int16_t temperature_0 = (int16_t)read_u16(record + 1u);
    const int16_t temperature_2 = (int16_t)read_u16(record + 3u);
    const int32_t sum = (int32_t)temperature_0 + (int32_t)temperature_2;
    *plan = (r1_factory_temperature_pair_diagnostic_plan){
        .sensor_count = record[0],
        .temperature_0_millicelsius = temperature_0,
        .temperature_2_millicelsius = temperature_2,
        .average_millicelsius = (int16_t)(sum / 2),
    };
    return R1_OK;
}

r1_error r1_factory_periodic_timer_restart_plan_build(
    r1_factory_periodic_timer_restart_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_factory_periodic_timer_restart_plan){
        .system_task_event_requested = true,
        .system_task_event = 4u,
    };
    return R1_OK;
}

r1_error r1_health_history_route_command(
    uint8_t command, uint8_t subcommand, uint16_t request_serial,
    r1_health_history_route *route) {
    if (route == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes((uint8_t *)route, sizeof *route);
    const uint16_t key = (uint16_t)(((uint16_t)command << 8u) | subcommand);
    size_t lower = 0u;
    size_t upper = sizeof health_history_registrations
        / sizeof health_history_registrations[0];
    while (lower < upper) {
        const size_t middle = lower + (upper - lower) / 2u;
        const health_history_registration *registration =
            &health_history_registrations[middle];
        if (registration->packed_command < key) {
            lower = middle + 1u;
        } else {
            upper = middle;
        }
    }
    if (lower >= sizeof health_history_registrations
            / sizeof health_history_registrations[0] ||
        health_history_registrations[lower].packed_command != key ||
        !health_history_registrations[lower].publishes_event14) {
        return R1_ERROR_UNSUPPORTED;
    }
    const health_history_registration *registration =
        &health_history_registrations[lower];
    route->action = registration->action;
    route->metric = registration->metric;
    route->query_kind = registration->query_kind;
    route->request_serial = request_serial;
    /* Use the recovered residue, not the clean binary-search lower bound. The
     * stock helper returns an ABI register remnant that is semantically inert. */
    route->dispatcher_residue = registration->residue;
    route->immediate_empty_response = registration->query_kind == 1u;
    return R1_OK;
}

r1_error r1_health_history_encode_event14(
    const r1_health_history_route *route,
    uint8_t output[R1_HEALTH_HISTORY_EVENT_BYTES]) {
    if (route == NULL || output == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    output[0] = route->metric;
    output[1] = route->query_kind;
    write_u16(output + 2u, route->request_serial);
    write_u32(output + 4u, route->dispatcher_residue);
    return R1_OK;
}

static r1_error health_history_action_for_event(
    uint8_t metric, uint8_t query_kind, r1_health_history_action *action) {
    if (action == NULL || query_kind > 1u) {
        return R1_ERROR_UNSUPPORTED;
    }
    if (metric == 0u) {
        *action = query_kind == 0u ? R1_HEALTH_HISTORY_HEART_RATE_POINT
                                   : R1_HEALTH_HISTORY_HEART_RATE_DAILY;
    } else if (metric == 1u) {
        *action = query_kind == 0u ? R1_HEALTH_HISTORY_SPO2_POINT
                                   : R1_HEALTH_HISTORY_SPO2_DAILY;
    } else if (metric == 4u) {
        *action = query_kind == 0u ? R1_HEALTH_HISTORY_ACTIVITY_REFRESH
                                   : R1_HEALTH_HISTORY_ACTIVITY_DAILY;
    } else if (metric == 5u) {
        *action = query_kind == 0u ? R1_HEALTH_HISTORY_HRV_POINT
                                   : R1_HEALTH_HISTORY_HRV_DAILY;
    } else if (metric == 6u && query_kind == 1u) {
        *action = R1_HEALTH_HISTORY_SLEEP_DAILY;
    } else {
        return R1_ERROR_UNSUPPORTED;
    }
    return R1_OK;
}

r1_error r1_health_history_decode_event14(
    const uint8_t *input, size_t length, r1_health_history_route *route) {
    if (input == NULL || route == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_HEALTH_HISTORY_EVENT_BYTES) {
        return R1_ERROR_LENGTH;
    }
    clear_bytes((uint8_t *)route, sizeof *route);
    route->metric = input[0];
    route->query_kind = input[1];
    route->request_serial = read_u16(input + 2u);
    route->dispatcher_residue = read_u32(input + 4u);
    route->immediate_empty_response = route->query_kind == 1u;
    return health_history_action_for_event(
        route->metric, route->query_kind, &route->action);
}

static r1_error health_store_bounded_u8(
    r1_health_u8_history *history, r1_health_u8_accumulator *accumulator,
    uint16_t published_value, uint8_t stored_value,
    uint32_t firmware_timestamp, uint8_t aggregate_hour,
    uint8_t average_hour, uint16_t minimum_published,
    uint16_t maximum_published, r1_health_u8_sample_result *result) {
    if (history == NULL || accumulator == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes((uint8_t *)result, sizeof *result);
    result->published_value = published_value;
    if (published_value < minimum_published || published_value > maximum_published) {
        result->action = R1_HEALTH_U8_SAMPLE_REJECTED_RANGE;
        return R1_OK;
    }
    if (aggregate_hour >= R1_HEALTH_HOURLY_SLOTS ||
        average_hour >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }

    uint8_t average = 0u;
    const r1_error error = r1_health_u8_accumulate_average(
        accumulator, average_hour, stored_value, &average);
    if (error != R1_OK) {
        return error;
    }
    r1_health_u8_slot *slot = &history->slots[aggregate_hour];
    if (stored_value > slot->maximum) {
        slot->maximum = stored_value;
    }
    if (slot->minimum == 0u || stored_value < slot->minimum) {
        slot->minimum = stored_value;
    }
    slot->average = average;
    history->latest_value = stored_value;
    history->latest_timestamp = firmware_timestamp;
    history->has_latest = true;
    result->action = R1_HEALTH_U8_SAMPLE_STORED;
    result->stored_value = stored_value;
    result->effective_timestamp = firmware_timestamp;
    result->timestamp_replaced = true;
    return R1_OK;
}

r1_error r1_temperature_store_sample(
    r1_health_u8_history *history, r1_health_u8_accumulator *accumulator,
    uint16_t published_value, uint32_t firmware_timestamp,
    uint8_t aggregate_hour, uint8_t average_hour,
    r1_health_u8_sample_result *result) {
    const uint8_t stored_value = (uint8_t)(
        published_value - R1_TEMPERATURE_STORAGE_BASE);
    return health_store_bounded_u8(
        history, accumulator, published_value, stored_value,
        firmware_timestamp, aggregate_hour, average_hour,
        R1_TEMPERATURE_PUBLISHED_MIN, R1_TEMPERATURE_PUBLISHED_MAX, result);
}

r1_error r1_stress_store_sample(
    r1_health_u8_history *history, r1_health_u8_accumulator *accumulator,
    uint8_t value, uint32_t firmware_timestamp,
    uint8_t aggregate_hour, uint8_t average_hour,
    r1_health_u8_sample_result *result) {
    return health_store_bounded_u8(
        history, accumulator, value, value, firmware_timestamp,
        aggregate_hour, average_hour, 0u, R1_STRESS_VALUE_MAX, result);
}

r1_error r1_activity_record(r1_activity_history *history, uint8_t ten_minute_bucket,
                            uint16_t steps, uint16_t active_kilocalories,
                            uint16_t all_kilocalories, uint32_t timestamp,
                            uint32_t local_day_start, int16_t utc_offset_minutes) {
    if (history == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (ten_minute_bucket >= R1_ACTIVITY_BUCKETS || timestamp < local_day_start) {
        return R1_ERROR_LENGTH;
    }
    if (history->local_day_start != local_day_start ||
        history->utc_offset_minutes != utc_offset_minutes) {
        clear_bytes((uint8_t *)history->buckets, sizeof history->buckets);
        history->total_steps = 0;
        history->total_kilocalories = 0;
        history->local_day_start = local_day_start;
        history->utc_offset_minutes = utc_offset_minutes;
    }
    r1_activity_bucket *bucket = &history->buckets[ten_minute_bucket];
    if (bucket->valid) {
        history->total_steps -= bucket->steps;
        history->total_kilocalories = (int16_t)(history->total_kilocalories
                                               - (int16_t)bucket->all_kilocalories);
    }
    bucket->steps = steps;
    bucket->active_kilocalories = active_kilocalories;
    bucket->all_kilocalories = all_kilocalories;
    bucket->valid = steps != 0u || active_kilocalories != 0u || all_kilocalories != 0u;
    if (bucket->valid) {
        history->total_steps += steps;
        history->total_kilocalories = (int16_t)(history->total_kilocalories
                                               + (int16_t)all_kilocalories);
    }
    history->latest_timestamp = timestamp;
    return R1_OK;
}

void r1_activity_accumulator_initialize(r1_activity_accumulator *accumulator) {
    if (accumulator != NULL) {
        clear_bytes((uint8_t *)accumulator, sizeof *accumulator);
    }
}

static bool activity_counters_rolled_back(
    const r1_activity_cumulative_counters *baseline,
    const r1_activity_cumulative_counters *current) {
    return current->steps < baseline->steps ||
        current->all_kilocalories < baseline->all_kilocalories ||
        current->active_kilocalories < baseline->active_kilocalories;
}

static void activity_accumulator_rebase(r1_activity_accumulator *accumulator) {
    accumulator->baseline = accumulator->current;
}

static void activity_delta_build(
    const r1_activity_accumulator *accumulator, uint32_t timestamp,
    r1_activity_delta_event *event) {
    event->all_kilocalories = (uint16_t)(
        accumulator->current.all_kilocalories -
        accumulator->baseline.all_kilocalories);
    event->active_kilocalories = (uint16_t)(
        accumulator->current.active_kilocalories -
        accumulator->baseline.active_kilocalories);
    event->steps = (uint16_t)(
        accumulator->current.steps - accumulator->baseline.steps);
    event->duration_seconds = (uint16_t)(
        timestamp % R1_ACTIVITY_WINDOW_SECONDS);
    event->timestamp = timestamp;
}

static bool activity_accumulator_available(
    r1_activity_accumulator *accumulator, uint32_t timestamp,
    uint8_t sleep_result_status, uint8_t wear_fusion_state,
    r1_activity_accumulator_result *result) {
    if (sleep_result_status == 1u || wear_fusion_state == 0u) {
        activity_accumulator_rebase(accumulator);
        accumulator->transition_pending = 0u;
        result->action = R1_ACTIVITY_ACCUMULATOR_REBASED_UNAVAILABLE;
        return false;
    }
    if (wear_fusion_state == 2u) {
        accumulator->transition_pending = 0u;
        return true;
    }
    if (accumulator->transition_pending == 0u) {
        accumulator->transition_pending = 1u;
        accumulator->transition_started = timestamp;
    }
    if (timestamp >= accumulator->transition_started &&
        timestamp - accumulator->transition_started <=
            R1_ACTIVITY_TRANSITION_GRACE_SECONDS) {
        result->action = R1_ACTIVITY_ACCUMULATOR_TRANSITION_GRACE;
        return false;
    }
    activity_accumulator_rebase(accumulator);
    accumulator->transition_pending = 0u;
    result->action = R1_ACTIVITY_ACCUMULATOR_REBASED_TRANSITION_TIMEOUT;
    return false;
}

static r1_error activity_accumulator_validate(
    r1_activity_accumulator *accumulator,
    r1_activity_accumulator_result *result) {
    if (accumulator == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes((uint8_t *)result, sizeof *result);
    return R1_OK;
}

r1_error r1_activity_accumulator_periodic(
    r1_activity_accumulator *accumulator,
    const r1_activity_cumulative_counters *current, uint32_t timestamp,
    uint32_t local_day_start, uint8_t sleep_result_status,
    uint8_t wear_fusion_state, r1_activity_accumulator_result *result) {
    if (current == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    const r1_error validation = activity_accumulator_validate(accumulator, result);
    if (validation != R1_OK) {
        return validation;
    }
    accumulator->current = *current;
    if (timestamp == local_day_start) {
        activity_accumulator_rebase(accumulator);
        accumulator->window_published = 0u;
        result->action = R1_ACTIVITY_ACCUMULATOR_REBASED_DAY_START;
        return R1_OK;
    }
    if (activity_counters_rolled_back(&accumulator->baseline, &accumulator->current)) {
        activity_accumulator_rebase(accumulator);
        accumulator->window_published = 1u;
        result->action = R1_ACTIVITY_ACCUMULATOR_REBASED_COUNTER_ROLLBACK;
        return R1_OK;
    }
    if (!activity_accumulator_available(
            accumulator, timestamp, sleep_result_status, wear_fusion_state,
            result)) {
        return R1_OK;
    }
    const uint32_t remainder = timestamp % R1_ACTIVITY_WINDOW_SECONDS;
    if (remainder < R1_ACTIVITY_WINDOW_PUBLISH_START_SECONDS) {
        accumulator->window_published = 0u;
        result->action = R1_ACTIVITY_ACCUMULATOR_EARLY_WINDOW;
        return R1_OK;
    }
    if (accumulator->window_published != 0u) {
        result->action = R1_ACTIVITY_ACCUMULATOR_WINDOW_ALREADY_PUBLISHED;
        return R1_OK;
    }
    activity_delta_build(accumulator, timestamp, &result->event);
    activity_accumulator_rebase(accumulator);
    accumulator->window_published = 1u;
    result->event_ready = true;
    result->action = R1_ACTIVITY_ACCUMULATOR_EVENT_READY;
    return R1_OK;
}

r1_error r1_activity_accumulator_refresh(
    r1_activity_accumulator *accumulator, uint32_t timestamp,
    uint8_t sleep_result_status, uint8_t wear_fusion_state,
    r1_activity_accumulator_result *result) {
    const r1_error validation = activity_accumulator_validate(accumulator, result);
    if (validation != R1_OK) {
        return validation;
    }
    if (activity_counters_rolled_back(&accumulator->baseline, &accumulator->current)) {
        activity_accumulator_rebase(accumulator);
        result->action = R1_ACTIVITY_ACCUMULATOR_REBASED_COUNTER_ROLLBACK;
        return R1_OK;
    }
    if (!activity_accumulator_available(
            accumulator, timestamp, sleep_result_status, wear_fusion_state,
            result)) {
        return R1_OK;
    }
    activity_delta_build(accumulator, timestamp, &result->event);
    activity_accumulator_rebase(accumulator);
    result->event_ready = true;
    result->action = R1_ACTIVITY_ACCUMULATOR_EVENT_READY;
    return R1_OK;
}

r1_error r1_activity_accumulator_pending_delta(
    const r1_activity_accumulator *accumulator,
    uint8_t sleep_result_status, uint8_t wear_fusion_state,
    r1_activity_delta_event *event) {
    if (accumulator == NULL || event == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes((uint8_t *)event, sizeof *event);
    if (sleep_result_status == 1u || wear_fusion_state != 2u ||
        activity_counters_rolled_back(&accumulator->baseline, &accumulator->current)) {
        return R1_OK;
    }
    activity_delta_build(accumulator, 0u, event);
    return R1_OK;
}

r1_error r1_activity_delta_event_encode(
    const r1_activity_delta_event *event,
    uint8_t output[R1_ACTIVITY_DELTA_EVENT_BYTES]) {
    if (event == NULL || output == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    write_u16(output, event->all_kilocalories);
    write_u16(output + 2u, event->active_kilocalories);
    write_u16(output + 4u, event->steps);
    write_u16(output + 6u, event->duration_seconds);
    write_u32(output + 8u, event->timestamp);
    return R1_OK;
}

r1_error r1_activity_delta_event_decode(
    const uint8_t *input, size_t length, r1_activity_delta_event *event) {
    if (input == NULL || event == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_ACTIVITY_DELTA_EVENT_BYTES) {
        return R1_ERROR_LENGTH;
    }
    event->all_kilocalories = read_u16(input);
    event->active_kilocalories = read_u16(input + 2u);
    event->steps = read_u16(input + 4u);
    event->duration_seconds = read_u16(input + 6u);
    event->timestamp = read_u32(input + 8u);
    return R1_OK;
}

r1_error r1_activity_consume_delta_event(
    r1_activity_history *history, const r1_activity_delta_event *event,
    r1_activity_bucket_resolver_fn resolve_bucket, void *resolver_context,
    uint32_t local_day_start, int16_t utc_offset_minutes,
    r1_activity_delta_consume_result *result) {
    if (history == NULL || event == NULL || resolve_bucket == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes((uint8_t *)result, sizeof *result);
    const uint32_t start_timestamp = event->timestamp - event->duration_seconds;
    r1_error error = resolve_bucket(
        resolver_context, start_timestamp, &result->start_bucket);
    if (error != R1_OK) {
        return error;
    }
    error = resolve_bucket(resolver_context, event->timestamp, &result->end_bucket);
    if (error != R1_OK) {
        return error;
    }
    if (result->start_bucket >= R1_ACTIVITY_BUCKETS ||
        result->end_bucket >= R1_ACTIVITY_BUCKETS) {
        return R1_ERROR_LENGTH;
    }
    result->crossed_bucket_boundary =
        result->start_bucket != result->end_bucket;
    const r1_activity_bucket *existing =
        &history->buckets[result->start_bucket];
    result->stored_steps = (uint16_t)(
        ((uint32_t)existing->steps + event->steps) & UINT32_C(0x0fff));
    result->stored_active_kilocalories = (uint16_t)(
        ((uint32_t)existing->active_kilocalories +
         event->active_kilocalories) & UINT32_C(0x03ff));
    result->stored_all_kilocalories = (uint16_t)(
        ((uint32_t)existing->all_kilocalories +
         event->all_kilocalories) & UINT32_C(0x03ff));
    return r1_activity_record(
        history, result->start_bucket, result->stored_steps,
        result->stored_active_kilocalories, result->stored_all_kilocalories,
        event->timestamp, local_day_start, utc_offset_minutes);
}

static size_t count_u8(const r1_health_u8_history *history) {
    size_t count = 0u;
    for (size_t index = 0u; index < R1_HEALTH_HOURLY_SLOTS; ++index) {
        count += history->slots[index].average != 0u ? 1u : 0u;
    }
    return count;
}

static size_t count_u16(const r1_health_u16_history *history) {
    size_t count = 0u;
    for (size_t index = 0u; index < R1_HEALTH_HOURLY_SLOTS; ++index) {
        count += history->slots[index].average != 0u ? 1u : 0u;
    }
    return count;
}

r1_error r1_health_encode_daily_u8(const r1_health_u8_history *history,
                                   uint8_t *output, size_t capacity, size_t *written) {
    if (history == NULL || output == NULL || written == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    const size_t count = count_u8(history);
    const size_t header = history->has_latest ? 12u : 7u;
    const size_t length = header + count * 4u;
    if (capacity < length) {
        return R1_ERROR_CAPACITY;
    }
    output[0] = (uint8_t)count;
    write_u16(output + 1u, (uint16_t)history->utc_offset_minutes);
    write_u32(output + 3u, history->local_day_start);
    size_t offset = 7u;
    if (history->has_latest) {
        write_u32(output + offset, history->latest_timestamp);
        output[offset + 4u] = history->latest_value;
        offset += 5u;
    }
    for (size_t index = 0u; index < R1_HEALTH_HOURLY_SLOTS; ++index) {
        const r1_health_u8_slot *slot = &history->slots[index];
        if (slot->average == 0u) {
            continue;
        }
        output[offset] = (uint8_t)index;
        output[offset + 1u] = slot->average;
        output[offset + 2u] = slot->maximum;
        output[offset + 3u] = slot->minimum;
        offset += 4u;
    }
    *written = offset;
    return R1_OK;
}

r1_error r1_health_encode_daily_u16(const r1_health_u16_history *history,
                                    uint8_t *output, size_t capacity, size_t *written) {
    if (history == NULL || output == NULL || written == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    const size_t count = count_u16(history);
    const size_t header = history->has_latest ? 13u : 7u;
    const size_t length = header + count * 7u;
    if (capacity < length) {
        return R1_ERROR_CAPACITY;
    }
    output[0] = (uint8_t)count;
    write_u16(output + 1u, (uint16_t)history->utc_offset_minutes);
    write_u32(output + 3u, history->local_day_start);
    size_t offset = 7u;
    if (history->has_latest) {
        write_u32(output + offset, history->latest_timestamp);
        write_u16(output + offset + 4u, history->latest_value);
        offset += 6u;
    }
    for (size_t index = 0u; index < R1_HEALTH_HOURLY_SLOTS; ++index) {
        const r1_health_u16_slot *slot = &history->slots[index];
        if (slot->average == 0u) {
            continue;
        }
        output[offset] = (uint8_t)index;
        write_u16(output + offset + 1u, slot->average);
        write_u16(output + offset + 3u, slot->maximum);
        write_u16(output + offset + 5u, slot->minimum);
        offset += 7u;
    }
    *written = offset;
    return R1_OK;
}

r1_error r1_activity_encode_daily(const r1_activity_history *history,
                                  uint8_t *output, size_t capacity, size_t *written) {
    if (history == NULL || output == NULL || written == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    size_t count = 0u;
    for (size_t index = 0u; index < R1_ACTIVITY_BUCKETS; ++index) {
        count += history->buckets[index].valid ? 1u : 0u;
    }
    const size_t length = 7u + count * 7u;
    if (capacity < length) {
        return R1_ERROR_CAPACITY;
    }
    output[0] = (uint8_t)count;
    write_u16(output + 1u, (uint16_t)history->utc_offset_minutes);
    write_u32(output + 3u, history->local_day_start);
    size_t offset = 7u;
    for (size_t index = 0u; index < R1_ACTIVITY_BUCKETS; ++index) {
        const r1_activity_bucket *bucket = &history->buckets[index];
        if (!bucket->valid) {
            continue;
        }
        output[offset] = (uint8_t)index;
        write_u16(output + offset + 1u, bucket->steps);
        write_u16(output + offset + 3u, bucket->active_kilocalories);
        write_u16(output + offset + 5u, bucket->all_kilocalories);
        offset += 7u;
    }
    *written = offset;
    return R1_OK;
}

r1_error r1_activity_encode_all_day(const r1_activity_history *history,
                                    uint8_t *output, size_t capacity, size_t *written) {
    if (history == NULL || output == NULL || written == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (capacity < 14u) {
        return R1_ERROR_CAPACITY;
    }
    write_u16(output, (uint16_t)history->utc_offset_minutes);
    write_u32(output + 2u, history->latest_timestamp);
    write_u32(output + 6u, (uint32_t)history->total_steps);
    write_u16(output + 10u, 0u);
    write_u16(output + 12u, (uint16_t)history->total_kilocalories);
    *written = 14u;
    return R1_OK;
}

void r1_activity_cache_reset(r1_activity_history *history,
                             uint32_t local_day_start,
                             int16_t utc_offset_minutes) {
    if (history == NULL) {
        return;
    }
    clear_bytes((uint8_t *)history->buckets, sizeof history->buckets);
    history->local_day_start = local_day_start;
    history->utc_offset_minutes = utc_offset_minutes;
    history->latest_timestamp = 0u;
    history->total_steps = 0;
    history->total_kilocalories = 0;
}

void r1_activity_cache_refresh_metadata(
    r1_activity_history *history, uint32_t local_day_start,
    int16_t utc_offset_minutes) {
    if (history == NULL) {
        return;
    }
    history->local_day_start = local_day_start;
    history->utc_offset_minutes = utc_offset_minutes;
}

static int16_t health_wrap_i16(int64_t value) {
    const uint16_t bits = (uint16_t)(uint64_t)value;
    if (bits <= (uint16_t)INT16_MAX) {
        return (int16_t)bits;
    }
    return (int16_t)(-((int32_t)UINT16_MAX - (int32_t)bits) - 1);
}

int32_t r1_temperature_gxt310_decode_milliunits(const uint8_t input[2]) {
    if (input == NULL) {
        return 0;
    }
    const uint16_t bits = (uint16_t)(
        ((uint16_t)input[0] << 8u) | (uint16_t)input[1]);
    const int32_t raw = bits <= (uint16_t)INT16_MAX
        ? (int32_t)bits
        : (int32_t)bits - INT32_C(65536);
    /* 0.0078125 C/LSB * 1000 = 125/16 milli-units. C99 signed division
     * truncates toward zero, matching the recovered Float32-to-int result. */
    return raw * INT32_C(125) / INT32_C(16);
}

r1_error r1_temperature_pair_calibration_decode(
    const uint8_t *input, size_t length,
    r1_temperature_pair_calibration *calibration, bool *present) {
    if (input == NULL || calibration == NULL || present == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_TEMPERATURE_PAIR_CALIBRATION_BYTES) {
        return R1_ERROR_LENGTH;
    }
    *present = false;
    for (size_t index = 0u; index < length; ++index) {
        if (input[index] != UINT8_MAX) {
            *present = true;
        }
    }
    for (size_t channel = 0u;
         channel < R1_TEMPERATURE_PAIR_SENSOR_COUNT; ++channel) {
        const size_t offset = channel * 3u;
        const uint8_t direction = input[offset];
        calibration->channels[channel].direction = direction <= 1u
            ? (r1_temperature_calibration_direction)direction
            : R1_TEMPERATURE_CALIBRATION_DISABLED;
        const uint16_t raw = (uint16_t)(
            (uint16_t)input[offset + 1u] |
            (uint16_t)((uint16_t)input[offset + 2u] << 8u));
        calibration->channels[channel].offset = raw <= (uint16_t)INT16_MAX
            ? (int16_t)raw
            : (int16_t)((int32_t)raw - INT32_C(65536));
    }
    return R1_OK;
}

r1_error r1_temperature_pair_stream_value(
    const int32_t channels[R1_TEMPERATURE_PAIR_SENSOR_COUNT],
    const r1_temperature_pair_calibration *calibration, uint16_t *value) {
    if (channels == NULL || value == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    uint32_t adjusted[R1_TEMPERATURE_PAIR_SENSOR_COUNT];
    for (size_t channel = 0u;
         channel < R1_TEMPERATURE_PAIR_SENSOR_COUNT; ++channel) {
        adjusted[channel] = (uint32_t)channels[channel];
        if (calibration == NULL) {
            continue;
        }
        const r1_temperature_channel_calibration *entry =
            &calibration->channels[channel];
        const uint32_t magnitude = (uint16_t)entry->offset;
        if (entry->direction == R1_TEMPERATURE_CALIBRATION_SUBTRACT) {
            adjusted[channel] -= magnitude;
        } else if (entry->direction == R1_TEMPERATURE_CALIBRATION_ADD) {
            adjusted[channel] += magnitude;
        }
    }
    const uint32_t sum = adjusted[0] + adjusted[1];
    const uint32_t toward_zero = sum + (sum >> 31u);
    *value = (uint16_t)(toward_zero >> 1u);
    return R1_OK;
}

static int16_t temperature_trimmed_mean(
    const int32_t samples[R1_TEMPERATURE_PAIR_SAMPLE_COUNT]) {
    int32_t minimum = INT32_MAX;
    int32_t maximum = INT32_MIN;
    int64_t sum = 0;
    for (size_t index = 0u; index < R1_TEMPERATURE_PAIR_SAMPLE_COUNT;
         ++index) {
        const int32_t sample = samples[index];
        sum += sample;
        if (sample < minimum) {
            minimum = sample;
        }
        if (sample > maximum) {
            maximum = sample;
        }
    }
    return health_wrap_i16((sum - minimum - maximum) / 8);
}

r1_error r1_temperature_pair_reduce(
    const int32_t samples[R1_TEMPERATURE_PAIR_SENSOR_COUNT]
                         [R1_TEMPERATURE_PAIR_SAMPLE_COUNT],
    const r1_temperature_pair_calibration *calibration,
    r1_temperature_pair_result *result) {
    if (samples == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *result = (r1_temperature_pair_result){
        .sensor_count = R1_TEMPERATURE_PAIR_SENSOR_COUNT,
    };
    for (size_t channel = 0u; channel < R1_TEMPERATURE_PAIR_SENSOR_COUNT;
         ++channel) {
        int16_t reduced = temperature_trimmed_mean(samples[channel]);
        if (calibration != NULL) {
            const r1_temperature_channel_calibration *entry =
                &calibration->channels[channel];
            if (entry->direction == R1_TEMPERATURE_CALIBRATION_SUBTRACT) {
                reduced = health_wrap_i16(
                    (int32_t)reduced - (int32_t)entry->offset);
            } else if (entry->direction == R1_TEMPERATURE_CALIBRATION_ADD) {
                reduced = health_wrap_i16(
                    (int32_t)reduced + (int32_t)entry->offset);
            }
        }
        result->channels[channel] = reduced;
    }
    return R1_OK;
}

r1_error r1_health_clear_all_caches(
    bool timeseries_database_available, uint32_t local_day_start,
    int16_t utc_offset_minutes, r1_activity_history *activity,
    r1_health_u8_history *heart_rate, r1_health_u8_history *spo2,
    r1_health_u8_history *temperature, r1_health_u8_history *stress,
    r1_health_u16_history *hrv, r1_health_clear_all_result *result) {
    if (result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *result = (r1_health_clear_all_result){
        .clear_timeseries_database = timeseries_database_available,
        .clear_sleep_history = true,
        .reset_algorithm_aggregate = true,
    };
    r1_health_u8_history *const u8_histories[] = {
        heart_rate, spo2, temperature, stress,
    };
    for (size_t index = 0u;
         index < sizeof u8_histories / sizeof u8_histories[0]; ++index) {
        if (u8_histories[index] != NULL) {
            r1_health_u8_cache_reset(
                u8_histories[index], local_day_start, utc_offset_minutes);
            result->cache_families_reset += 1u;
        }
    }
    if (activity != NULL) {
        r1_activity_cache_reset(
            activity, local_day_start, utc_offset_minutes);
        result->cache_families_reset += 1u;
    }
    if (hrv != NULL) {
        r1_health_u16_cache_reset(hrv, local_day_start, utc_offset_minutes);
        result->cache_families_reset += 1u;
    }
    return R1_OK;
}

r1_error r1_health_settings_plan_command(
    bool write_command, const r1_health_settings_record *stored,
    const uint8_t *payload, size_t payload_length,
    r1_health_settings_command_plan *plan) {
    if (stored == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    clear_bytes((uint8_t *)plan, sizeof *plan);
    plan->write_command = write_command;
    plan->response_requested = true;
    plan->persistent_record = *stored;
    clear_bytes((uint8_t *)&plan->response, sizeof plan->response);
    plan->response.timestamp_seconds = stored->timestamp_seconds;
    plan->response.enabled = (uint8_t)(stored->enabled != 0u);
    if (!write_command) {
        if (payload_length != 0u && payload == NULL) {
            return R1_ERROR_ARGUMENT;
        }
        return R1_OK;
    }
    if (payload == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (payload_length != sizeof(r1_health_settings_record)) {
        return R1_ERROR_LENGTH;
    }

    plan->acknowledgement_precedes_effects = true;
    const uint32_t requested_timestamp = read_u32(payload);
    const uint8_t requested_raw = payload[4];
    const uint8_t stored_normalized = (uint8_t)(stored->enabled != 0u);
    const uint8_t requested_normalized = (uint8_t)(requested_raw != 0u);
    plan->raw_transition_observed = requested_raw != stored_normalized;
    plan->private_event_publish_requested = plan->raw_transition_observed;
    plan->private_event_value = requested_raw;
    plan->persistent_update_requested =
        plan->raw_transition_observed
        && requested_normalized != stored_normalized;
    if (plan->persistent_update_requested) {
        plan->persistent_record.timestamp_seconds = requested_timestamp;
        plan->persistent_record.enabled = requested_normalized;
    }
    return R1_OK;
}

static void activity_cache_recompute_totals(r1_activity_history *history) {
    history->total_steps = 0;
    history->total_kilocalories = 0;
    for (size_t index = 0u; index < R1_ACTIVITY_BUCKETS; ++index) {
        const r1_activity_bucket *bucket = &history->buckets[index];
        if (bucket->valid) {
            history->total_steps += bucket->steps;
            history->total_kilocalories = (int16_t)(
                history->total_kilocalories + (int16_t)bucket->all_kilocalories);
        }
    }
}

r1_error r1_activity_cache_write_hour(
    r1_activity_history *history, uint8_t hour_index,
    const r1_activity_bucket buckets[R1_ACTIVITY_BUCKETS_PER_HOUR]) {
    if (history == NULL || buckets == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (hour_index >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }
    const size_t start = (size_t)hour_index * R1_ACTIVITY_BUCKETS_PER_HOUR;
    for (size_t index = 0u; index < R1_ACTIVITY_BUCKETS_PER_HOUR; ++index) {
        history->buckets[start + index] = buckets[index];
    }
    activity_cache_recompute_totals(history);
    return R1_OK;
}

static uint32_t activity_bucket_pack(const r1_activity_bucket *bucket) {
    return ((uint32_t)bucket->steps & UINT32_C(0x0fff))
        | (((uint32_t)bucket->active_kilocalories & UINT32_C(0x03ff)) << 12u)
        | (((uint32_t)bucket->all_kilocalories & UINT32_C(0x03ff)) << 22u);
}

static void activity_cache_copy_hour(
    const r1_activity_history *history, uint8_t hour_index,
    r1_activity_bucket output[R1_ACTIVITY_BUCKETS_PER_HOUR]) {
    const size_t start = (size_t)hour_index * R1_ACTIVITY_BUCKETS_PER_HOUR;
    for (size_t index = 0u; index < R1_ACTIVITY_BUCKETS_PER_HOUR; ++index) {
        output[index] = history->buckets[start + index];
    }
}

r1_error r1_activity_cache_read_hour(
    const r1_activity_history *history, uint8_t hour_index,
    uint8_t firmware_time_status, uint32_t read_timestamp,
    uint32_t validation_timestamp, const uint32_t *queue_timestamps,
    size_t queue_timestamp_count, r1_activity_offline_queue *queue,
    r1_activity_cache_read_result *result) {
    if (history == NULL || queue == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (hour_index >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }
    *result = (r1_activity_cache_read_result){0};
    activity_cache_copy_hour(history, hour_index, result->returned);
    if (firmware_time_status != 0u) {
        result->disposition = R1_ACTIVITY_CACHE_RETURNED_CLOCK_VALID;
        return R1_OK;
    }
    if (read_timestamp > R1_ACTIVITY_LEGACY_CLOCK_CUTOFF) {
        result->disposition = R1_ACTIVITY_CACHE_RETURNED_ABOVE_LEGACY_CUTOFF;
        return R1_OK;
    }
    size_t nonzero_count = 0u;
    for (size_t index = 0u; index < R1_ACTIVITY_BUCKETS_PER_HOUR; ++index) {
        nonzero_count += activity_bucket_pack(&result->returned[index]) != 0u ? 1u : 0u;
    }
    if (nonzero_count == 0u) {
        result->disposition = R1_ACTIVITY_CACHE_RETURNED_ALL_ZERO;
        return R1_OK;
    }
    result->has_unsigned_offset_hours = true;
    result->unsigned_offset_hours = (uint16_t)history->utc_offset_minutes / 60u;
    if (result->unsigned_offset_hours > hour_index) {
        clear_bytes((uint8_t *)result->returned, sizeof result->returned);
        result->disposition = R1_ACTIVITY_CACHE_REDACTED_OFFSET_BEFORE_HOUR;
        return R1_OK;
    }
    result->has_adjusted_hour = true;
    result->adjusted_hour = (uint8_t)(hour_index - result->unsigned_offset_hours);
    if (validation_timestamp < read_timestamp) {
        clear_bytes((uint8_t *)result->returned, sizeof result->returned);
        result->disposition = R1_ACTIVITY_CACHE_REDACTED_BACKWARD_CLOCK;
        return R1_OK;
    }
    if (queue_timestamp_count != nonzero_count ||
        (nonzero_count != 0u && queue_timestamps == NULL)) {
        return R1_ERROR_LENGTH;
    }
    bool all_enqueued = true;
    size_t timestamp_index = 0u;
    const size_t start = (size_t)hour_index * R1_ACTIVITY_BUCKETS_PER_HOUR;
    for (size_t index = 0u; index < R1_ACTIVITY_BUCKETS_PER_HOUR; ++index) {
        const uint32_t packed = activity_bucket_pack(&history->buckets[start + index]);
        if (packed == 0u) {
            continue;
        }
        const uint8_t adjusted_bucket = (uint8_t)(
            (uint16_t)result->adjusted_hour * R1_ACTIVITY_BUCKETS_PER_HOUR + index);
        r1_activity_offline_enqueue_result enqueue;
        const r1_error error = r1_activity_offline_enqueue(
            queue, packed, 0u, read_timestamp, 0, adjusted_bucket,
            queue_timestamps[timestamp_index], &enqueue);
        if (error != R1_OK) {
            return error;
        }
        all_enqueued = all_enqueued
            && enqueue.action == R1_ACTIVITY_OFFLINE_ENQUEUED;
        timestamp_index += 1u;
    }
    result->enqueue_count = timestamp_index;
    clear_bytes((uint8_t *)result->returned, sizeof result->returned);
    result->disposition = all_enqueued
        ? R1_ACTIVITY_CACHE_QUEUED_AND_REDACTED
        : R1_ACTIVITY_CACHE_QUEUE_REJECTED_AND_REDACTED;
    return R1_OK;
}

void r1_health_u8_cache_reset(r1_health_u8_history *history,
                              uint32_t local_day_start,
                              int16_t utc_offset_minutes) {
    if (history == NULL) {
        return;
    }
    /* The stock callback clears aggregate slots while preserving its compact
     * latest-point region. In this normalized representation the latest point
     * lives outside slots, so clearing the complete slot state is equivalent. */
    clear_bytes((uint8_t *)history->slots, sizeof history->slots);
    history->local_day_start = local_day_start;
    history->utc_offset_minutes = utc_offset_minutes;
}

void r1_health_u16_cache_reset(r1_health_u16_history *history,
                               uint32_t local_day_start,
                               int16_t utc_offset_minutes) {
    if (history == NULL) {
        return;
    }
    clear_bytes((uint8_t *)history->slots, sizeof history->slots);
    history->local_day_start = local_day_start;
    history->utc_offset_minutes = utc_offset_minutes;
}

r1_error r1_health_u8_cache_write_slot(
    r1_health_u8_history *history, uint8_t hour_index,
    uint8_t average, uint8_t maximum, uint8_t minimum) {
    if (history == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (hour_index >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }
    r1_health_u8_slot *slot = &history->slots[hour_index];
    slot->average = average;
    slot->maximum = maximum;
    slot->minimum = minimum;
    return R1_OK;
}

r1_error r1_health_u16_cache_write_slot(
    r1_health_u16_history *history, uint8_t hour_index,
    uint16_t average, uint16_t maximum, uint16_t minimum) {
    if (history == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (hour_index >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }
    r1_health_u16_slot *slot = &history->slots[hour_index];
    slot->average = average;
    slot->maximum = maximum;
    slot->minimum = minimum;
    return R1_OK;
}

static void health_u8_cache_redact(r1_health_u8_cache_read_result *result) {
    clear_bytes((uint8_t *)&result->returned, sizeof result->returned);
}

static void health_u16_cache_redact(r1_health_u16_cache_read_result *result) {
    clear_bytes((uint8_t *)&result->returned, sizeof result->returned);
}

r1_error r1_health_u8_cache_read_slot(
    const r1_health_u8_history *history, uint8_t hour_index,
    uint8_t firmware_time_status, uint32_t read_timestamp,
    uint32_t validation_timestamp, uint32_t queue_timestamp,
    r1_health_u8_offline_queue *queue,
    r1_health_u8_cache_read_result *result) {
    if (history == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (hour_index >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }
    clear_bytes((uint8_t *)result, sizeof *result);
    result->copied = history->slots[hour_index];
    result->returned = result->copied;
    if (firmware_time_status != 0u) {
        result->disposition = R1_HEALTH_CACHE_RETURNED_CLOCK_VALID;
        return R1_OK;
    }
    if (read_timestamp > R1_HEALTH_LEGACY_CLOCK_CUTOFF) {
        result->disposition = R1_HEALTH_CACHE_RETURNED_ABOVE_LEGACY_CUTOFF;
        return R1_OK;
    }
    if (result->copied.average == 0u) {
        result->disposition = R1_HEALTH_CACHE_RETURNED_ZERO_AVERAGE;
        return R1_OK;
    }

    result->has_unsigned_offset_hours = true;
    result->unsigned_offset_hours =
        (uint16_t)history->utc_offset_minutes / 60u;
    health_u8_cache_redact(result);
    if (result->unsigned_offset_hours > hour_index) {
        result->disposition = R1_HEALTH_CACHE_REDACTED_OFFSET_BEFORE_HOUR;
        return R1_OK;
    }
    result->has_adjusted_hour = true;
    result->adjusted_hour = (uint8_t)(
        hour_index - result->unsigned_offset_hours);
    if (validation_timestamp < read_timestamp) {
        result->disposition = R1_HEALTH_CACHE_REDACTED_BACKWARD_CLOCK;
        return R1_OK;
    }

    result->has_enqueue_result = true;
    const r1_error error = r1_health_u8_offline_enqueue(
        queue, result->copied.average, result->copied.maximum,
        result->copied.minimum, 0u, read_timestamp, 0,
        result->adjusted_hour, queue_timestamp, &result->enqueue);
    if (error != R1_OK) {
        return error;
    }
    result->disposition = result->enqueue.action == R1_HEALTH_OFFLINE_ENQUEUED
        ? R1_HEALTH_CACHE_QUEUED_AND_REDACTED
        : R1_HEALTH_CACHE_QUEUE_REJECTED_AND_REDACTED;
    return R1_OK;
}

r1_error r1_temperature_cache_read_slot(
    const r1_health_u8_history *history, uint8_t hour_index,
    uint8_t firmware_time_status, uint32_t read_timestamp,
    r1_health_u8_cache_read_result *result) {
    if (history == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (hour_index >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }
    clear_bytes((uint8_t *)result, sizeof *result);
    result->copied = history->slots[hour_index];
    result->returned = result->copied;
    if (firmware_time_status != 0u) {
        result->disposition = R1_HEALTH_CACHE_RETURNED_CLOCK_VALID;
        return R1_OK;
    }
    if (read_timestamp > R1_HEALTH_LEGACY_CLOCK_CUTOFF) {
        result->disposition = R1_HEALTH_CACHE_RETURNED_ABOVE_LEGACY_CUTOFF;
        return R1_OK;
    }
    if (result->copied.average == 0u) {
        result->disposition = R1_HEALTH_CACHE_RETURNED_ZERO_AVERAGE;
        return R1_OK;
    }
    health_u8_cache_redact(result);
    result->disposition = R1_HEALTH_CACHE_REDACTED_EARLY_CLOCK;
    return R1_OK;
}

r1_error r1_stress_cache_read_slot(
    const r1_health_u8_history *history, uint8_t hour_index,
    r1_health_u8_slot *returned) {
    if (history == NULL || returned == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (hour_index >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }
    *returned = history->slots[hour_index];
    return R1_OK;
}

r1_error r1_health_u16_cache_read_slot(
    const r1_health_u16_history *history, uint8_t hour_index,
    uint8_t firmware_time_status, uint32_t read_timestamp,
    uint32_t validation_timestamp, uint32_t queue_timestamp,
    r1_health_u16_offline_queue *queue,
    r1_health_u16_cache_read_result *result) {
    if (history == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (hour_index >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }
    clear_bytes((uint8_t *)result, sizeof *result);
    result->copied = history->slots[hour_index];
    result->returned = result->copied;
    if (firmware_time_status != 0u) {
        result->disposition = R1_HEALTH_CACHE_RETURNED_CLOCK_VALID;
        return R1_OK;
    }
    if (read_timestamp > R1_HEALTH_LEGACY_CLOCK_CUTOFF) {
        result->disposition = R1_HEALTH_CACHE_RETURNED_ABOVE_LEGACY_CUTOFF;
        return R1_OK;
    }
    if (result->copied.average == 0u) {
        result->disposition = R1_HEALTH_CACHE_RETURNED_ZERO_AVERAGE;
        return R1_OK;
    }

    result->has_unsigned_offset_hours = true;
    result->unsigned_offset_hours =
        (uint16_t)history->utc_offset_minutes / 60u;
    health_u16_cache_redact(result);
    if (result->unsigned_offset_hours > hour_index) {
        result->disposition = R1_HEALTH_CACHE_REDACTED_OFFSET_BEFORE_HOUR;
        return R1_OK;
    }
    result->has_adjusted_hour = true;
    result->adjusted_hour = (uint8_t)(
        hour_index - result->unsigned_offset_hours);
    if (validation_timestamp < read_timestamp) {
        result->disposition = R1_HEALTH_CACHE_REDACTED_BACKWARD_CLOCK;
        return R1_OK;
    }

    result->has_enqueue_result = true;
    const r1_error error = r1_health_u16_offline_enqueue(
        queue, result->copied.average, result->copied.maximum,
        result->copied.minimum, 0u, read_timestamp, 0,
        result->adjusted_hour, queue_timestamp, &result->enqueue);
    if (error != R1_OK) {
        return error;
    }
    result->disposition = result->enqueue.action == R1_HEALTH_OFFLINE_ENQUEUED
        ? R1_HEALTH_CACHE_QUEUED_AND_REDACTED
        : R1_HEALTH_CACHE_QUEUE_REJECTED_AND_REDACTED;
    return R1_OK;
}

void r1_activity_offline_initialize(r1_activity_offline_queue *queue) {
    if (queue != NULL) {
        clear_bytes((uint8_t *)queue, sizeof *queue);
    }
}

bool r1_activity_offline_is_empty(const r1_activity_offline_queue *queue) {
    return queue == NULL || queue->count == 0u;
}

static bool activity_offline_queue_valid(const r1_activity_offline_queue *queue) {
    return queue != NULL
        && queue->read_index < R1_ACTIVITY_OFFLINE_CAPACITY
        && queue->write_index < R1_ACTIVITY_OFFLINE_CAPACITY
        && queue->count <= R1_ACTIVITY_OFFLINE_CAPACITY
        && queue->write_index == (uint8_t)(
            ((uint16_t)queue->read_index + (uint16_t)queue->count)
            % R1_ACTIVITY_OFFLINE_CAPACITY);
}

r1_error r1_activity_offline_enqueue(
    r1_activity_offline_queue *queue, uint32_t packed_word,
    uint32_t local_day_start, uint32_t recorded_timestamp,
    int16_t utc_offset_minutes, uint8_t bucket_index,
    uint32_t firmware_timestamp, r1_activity_offline_enqueue_result *result) {
    if (queue == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!activity_offline_queue_valid(queue)) {
        return R1_ERROR_STATE;
    }
    if (bucket_index >= R1_ACTIVITY_BUCKETS) {
        return R1_ERROR_LENGTH;
    }
    *result = (r1_activity_offline_enqueue_result){
        R1_ACTIVITY_OFFLINE_ENQUEUED, false,
    };
    if (packed_word == 0u) {
        result->action = R1_ACTIVITY_OFFLINE_DROPPED_ZERO;
        return R1_OK;
    }
    if (recorded_timestamp > firmware_timestamp) {
        result->action = R1_ACTIVITY_OFFLINE_DROPPED_FUTURE_RECORDED;
        return R1_OK;
    }
    if (local_day_start > firmware_timestamp) {
        result->action = R1_ACTIVITY_OFFLINE_DROPPED_FUTURE_DAY;
        return R1_OK;
    }

    r1_activity_offline_entry *entry = &queue->entries[queue->write_index];
    const uint8_t retained_tail = entry->reserved_tail;
    entry->packed_word = packed_word;
    entry->local_day_start = local_day_start;
    entry->recorded_timestamp = recorded_timestamp;
    entry->utc_offset_minutes = utc_offset_minutes;
    entry->bucket_index = bucket_index;
    entry->reserved_tail = retained_tail;

    queue->write_index = (uint8_t)(
        ((uint16_t)queue->write_index + 1u) % R1_ACTIVITY_OFFLINE_CAPACITY);
    if (queue->count < R1_ACTIVITY_OFFLINE_CAPACITY) {
        queue->count = (uint8_t)(queue->count + 1u);
    } else {
        queue->read_index = (uint8_t)(
            ((uint16_t)queue->read_index + 1u) % R1_ACTIVITY_OFFLINE_CAPACITY);
        result->overwrote_oldest = true;
    }
    return R1_OK;
}

r1_error r1_activity_flash_record_enqueue_plan(
    r1_activity_offline_queue *queue, uint32_t local_day_start,
    int16_t utc_offset_minutes, uint8_t hour,
    const uint32_t packed_words[6], uint32_t recorded_timestamp,
    uint32_t maximum_allowed_timestamp, uint32_t firmware_timestamp,
    r1_activity_flash_record_enqueue_result *result) {
    if (queue == NULL || packed_words == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *result = (r1_activity_flash_record_enqueue_result){
        .action = R1_ACTIVITY_FLASH_RECORD_ACCEPTED,
    };
    if (hour >= 24u) {
        result->action = R1_ACTIVITY_FLASH_RECORD_IGNORED_HOUR;
        return R1_OK;
    }
    if (recorded_timestamp > maximum_allowed_timestamp) {
        result->action = R1_ACTIVITY_FLASH_RECORD_IGNORED_MAXIMUM_TIMESTAMP;
        return R1_OK;
    }
    if (recorded_timestamp > firmware_timestamp) {
        result->action = R1_ACTIVITY_FLASH_RECORD_IGNORED_FUTURE_RECORDED;
        return R1_OK;
    }
    if (local_day_start > firmware_timestamp) {
        result->action = R1_ACTIVITY_FLASH_RECORD_IGNORED_FUTURE_DAY;
        return R1_OK;
    }

    for (size_t index = 0u; index < 6u; ++index) {
        r1_activity_offline_enqueue_result enqueue;
        ++result->attempted_count;
        const r1_error error = r1_activity_offline_enqueue(
            queue, packed_words[index], local_day_start, recorded_timestamp,
            utc_offset_minutes, (uint8_t)((size_t)hour * 6u + index),
            firmware_timestamp, &enqueue);
        if (error != R1_OK) {
            return error;
        }
        if (enqueue.action == R1_ACTIVITY_OFFLINE_ENQUEUED) {
            ++result->enqueued_count;
            if (enqueue.overwrote_oldest) {
                ++result->overwritten_count;
            }
        } else {
            ++result->dropped_count;
        }
    }
    return R1_OK;
}

r1_error r1_activity_offline_consume_through(
    r1_activity_offline_queue *queue, uint32_t cutoff_timestamp,
    size_t *consumed_count) {
    if (queue == NULL || consumed_count == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!activity_offline_queue_valid(queue)) {
        return R1_ERROR_STATE;
    }
    *consumed_count = 0u;
    while (queue->count != 0u) {
        r1_activity_offline_entry *entry = &queue->entries[queue->read_index];
        if (entry->recorded_timestamp > cutoff_timestamp) {
            break;
        }
        clear_bytes((uint8_t *)entry, sizeof *entry);
        queue->read_index = (uint8_t)(
            ((uint16_t)queue->read_index + 1u) % R1_ACTIVITY_OFFLINE_CAPACITY);
        queue->count = (uint8_t)(queue->count - 1u);
        *consumed_count += 1u;
    }
    return R1_OK;
}

static void activity_offline_packet_reset(
    r1_activity_offline_packet *packet, uint32_t local_day_start,
    int16_t utc_offset_minutes) {
    const uint16_t serial = packet->serial;
    const uint8_t mode = packet->mode;
    const bool acknowledgement_requested = packet->acknowledgement_requested;
    clear_bytes((uint8_t *)packet, sizeof *packet);
    packet->serial = serial;
    packet->mode = mode;
    packet->acknowledgement_requested = acknowledgement_requested;
    packet->history.local_day_start = local_day_start;
    packet->history.utc_offset_minutes = utc_offset_minutes;
}

static r1_error activity_offline_packet_emit(
    r1_activity_offline_packet *packet, r1_activity_offline_emit_fn emit,
    void *context, r1_activity_offline_merge_result *result) {
    const r1_error error = emit(context, packet);
    if (error == R1_OK) {
        result->packet_count += 1u;
    }
    return error;
}

r1_error r1_activity_offline_merge(
    const r1_activity_offline_queue *queue, uint32_t firmware_timestamp,
    r1_activity_offline_packet *workspace, r1_activity_offline_emit_fn emit,
    void *emit_context, r1_activity_offline_merge_result *result) {
    if (queue == NULL || workspace == NULL || emit == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!activity_offline_queue_valid(queue)) {
        return R1_ERROR_STATE;
    }
    *result = (r1_activity_offline_merge_result){0u, 0u, 0u};
    bool packet_active = false;
    for (uint16_t position = 0u; position < queue->count; ++position) {
        const uint16_t physical = (uint16_t)(
            ((uint16_t)queue->read_index + position)
            % R1_ACTIVITY_OFFLINE_CAPACITY);
        const r1_activity_offline_entry *entry = &queue->entries[physical];
        if (entry->packed_word == 0u) {
            result->skipped_zero_count += 1u;
            continue;
        }
        if (entry->recorded_timestamp > firmware_timestamp
            || entry->local_day_start > firmware_timestamp) {
            result->skipped_future_count += 1u;
            continue;
        }
        if (entry->bucket_index >= R1_ACTIVITY_BUCKETS) {
            return R1_ERROR_STATE;
        }
        if (!packet_active
            || workspace->history.local_day_start != entry->local_day_start
            || workspace->history.utc_offset_minutes != entry->utc_offset_minutes) {
            if (packet_active) {
                const r1_error error = activity_offline_packet_emit(
                    workspace, emit, emit_context, result);
                if (error != R1_OK) {
                    return error;
                }
            }
            activity_offline_packet_reset(
                workspace, entry->local_day_start, entry->utc_offset_minutes);
            packet_active = true;
        }
        r1_activity_bucket *bucket =
            &workspace->history.buckets[entry->bucket_index];
        bucket->steps = (uint16_t)(entry->packed_word & UINT32_C(0x0fff));
        bucket->active_kilocalories = (uint16_t)(
            (entry->packed_word >> 12u) & UINT32_C(0x03ff));
        bucket->all_kilocalories = (uint16_t)(entry->packed_word >> 22u);
        bucket->valid = true;
        if (entry->recorded_timestamp > workspace->maximum_recorded_timestamp) {
            workspace->maximum_recorded_timestamp = entry->recorded_timestamp;
        }
    }
    if (packet_active) {
        return activity_offline_packet_emit(
            workspace, emit, emit_context, result);
    }
    return R1_OK;
}

r1_error r1_activity_offline_acknowledge(
    r1_activity_offline_queue *queue, uint8_t mode,
    uint32_t acknowledged_timestamp, uint32_t firmware_timestamp,
    uint32_t *last_sync_timestamp, r1_activity_ack_result *result) {
    if (queue == NULL || last_sync_timestamp == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!activity_offline_queue_valid(queue)) {
        return R1_ERROR_STATE;
    }
    *result = (r1_activity_ack_result){
        mode, true, acknowledged_timestamp > firmware_timestamp, false, 0u,
    };
    if (mode == R1_ACTIVITY_ACK_OFFLINE_QUEUE) {
        return r1_activity_offline_consume_through(
            queue, acknowledged_timestamp, &result->consumed_count);
    }
    if ((mode == R1_ACTIVITY_ACK_FLASH_HISTORY
         || mode == R1_ACTIVITY_ACK_CURRENT_RAM)
        && !result->timestamp_was_future
        && acknowledged_timestamp > *last_sync_timestamp) {
        *last_sync_timestamp = acknowledged_timestamp;
        result->last_sync_updated = true;
    }
    return R1_OK;
}

uint32_t r1_activity_clamp_acknowledgement_timestamp(
    uint32_t candidate_timestamp, uint32_t firmware_timestamp) {
    return candidate_timestamp != 0u && candidate_timestamp <= firmware_timestamp
        ? candidate_timestamp : firmware_timestamp;
}

void r1_activity_day_builder_reset(r1_activity_offline_packet *builder) {
    if (builder == NULL) {
        return;
    }
    const uint16_t serial = builder->serial;
    const uint8_t mode = builder->mode;
    const bool acknowledgement_requested = builder->acknowledgement_requested;
    clear_bytes((uint8_t *)builder, sizeof *builder);
    builder->serial = serial;
    builder->mode = mode;
    builder->acknowledgement_requested = acknowledgement_requested;
}

static size_t activity_day_builder_count(
    const r1_activity_offline_packet *builder) {
    size_t count = 0u;
    for (size_t index = 0u; index < R1_ACTIVITY_BUCKETS; ++index) {
        count += builder->history.buckets[index].valid ? 1u : 0u;
    }
    return count;
}

r1_error r1_activity_day_builder_flush(
    r1_activity_offline_packet *builder, uint32_t firmware_timestamp,
    r1_activity_offline_emit_fn emit, void *emit_context,
    r1_activity_day_flush_result *result) {
    if (builder == NULL || emit == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *result = (r1_activity_day_flush_result){false, false, 0u};
    const size_t count = activity_day_builder_count(builder);
    if (count == 0u) {
        return R1_OK;
    }
    if (builder->maximum_recorded_timestamp > firmware_timestamp) {
        result->dropped_future_acknowledgement = true;
        r1_activity_day_builder_reset(builder);
        return R1_OK;
    }
    result->encoded_length = 7u + count * 7u;
    const r1_error error = emit(emit_context, builder);
    result->emitted = error == R1_OK;
    r1_activity_day_builder_reset(builder);
    return error;
}

static void activity_day_builder_set_bucket(
    r1_activity_offline_packet *builder, uint8_t bucket_index,
    uint16_t steps, uint16_t active_kilocalories,
    uint16_t all_kilocalories, bool replace_existing) {
    r1_activity_bucket *bucket = &builder->history.buckets[bucket_index];
    if (bucket->valid && !replace_existing) {
        return;
    }
    bucket->steps = steps;
    bucket->active_kilocalories = active_kilocalories;
    bucket->all_kilocalories = all_kilocalories;
    bucket->valid = true;
}

r1_error r1_activity_ram_cache_merge(
    r1_activity_offline_packet *builder, r1_activity_history *cache,
    uint32_t requested_day_start, uint32_t window_start,
    uint32_t firmware_timestamp, int16_t current_utc_offset_minutes,
    uint16_t current_steps, uint16_t current_active_kilocalories,
    uint16_t current_all_kilocalories, r1_activity_offline_emit_fn emit,
    void *emit_context, r1_activity_day_flush_result *flush_result) {
    if (builder == NULL || cache == NULL || emit == NULL || flush_result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *flush_result = (r1_activity_day_flush_result){false, false, 0u};
    if (requested_day_start == 0u || window_start >= firmware_timestamp) {
        return R1_OK;
    }
    if (requested_day_start > firmware_timestamp) {
        return R1_ERROR_STATE;
    }

    cache->local_day_start = requested_day_start;
    cache->utc_offset_minutes = current_utc_offset_minutes;
    const uint8_t saved_mode = builder->mode;
    builder->mode = R1_ACTIVITY_ACK_CURRENT_RAM;
    r1_activity_day_builder_reset(builder);
    builder->history.local_day_start = requested_day_start;
    builder->history.utc_offset_minutes = current_utc_offset_minutes;

    uint32_t current_index = (firmware_timestamp - requested_day_start) / 600u;
    if (current_index >= R1_ACTIVITY_BUCKETS) {
        current_index = R1_ACTIVITY_BUCKETS - 1u;
    }
    uint32_t maximum_timestamp = 0u;
    for (uint16_t index = 0u; index < R1_ACTIVITY_BUCKETS; ++index) {
        const r1_activity_bucket *source = &cache->buckets[index];
        uint16_t steps = source->steps;
        uint16_t active = source->active_kilocalories;
        uint16_t all = source->all_kilocalories;
        if (index == current_index) {
            steps = (uint16_t)(steps + current_steps);
            active = (uint16_t)(active + current_active_kilocalories);
            all = (uint16_t)(all + current_all_kilocalories);
        }
        if (steps == 0u && active == 0u && all == 0u) {
            continue;
        }
        const uint32_t timestamp = requested_day_start + (uint32_t)index * 600u;
        if (index != current_index
            && (timestamp < window_start || timestamp > firmware_timestamp)) {
            continue;
        }
        activity_day_builder_set_bucket(
            builder, (uint8_t)index, steps, active, all, true);
        if (timestamp > maximum_timestamp) {
            maximum_timestamp = timestamp;
        }
    }
    if (activity_day_builder_count(builder) != 0u) {
        builder->maximum_recorded_timestamp =
            r1_activity_clamp_acknowledgement_timestamp(
                maximum_timestamp, firmware_timestamp);
        const r1_error error = r1_activity_day_builder_flush(
            builder, firmware_timestamp, emit, emit_context, flush_result);
        builder->mode = saved_mode;
        return error;
    }
    builder->mode = saved_mode;
    return R1_OK;
}

static uint32_t activity_local_seconds_of_day(
    uint32_t timestamp, int16_t utc_offset_minutes) {
    int64_t local = (int64_t)timestamp + (int64_t)utc_offset_minutes * 60;
    int64_t seconds = local % INT64_C(86400);
    if (seconds < 0) {
        seconds += INT64_C(86400);
    }
    return (uint32_t)seconds;
}

r1_error r1_activity_flash_record_merge(
    r1_activity_offline_packet *builder,
    const r1_activity_flash_record *record, uint32_t firmware_timestamp,
    bool previous_local_day_only, r1_activity_offline_emit_fn emit,
    void *emit_context, r1_activity_day_flush_result *flush_result) {
    if (builder == NULL || record == NULL || emit == NULL || flush_result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *flush_result = (r1_activity_day_flush_result){false, false, 0u};
    if (record->recorded_timestamp > firmware_timestamp) {
        return R1_OK;
    }
    const uint32_t local_seconds = activity_local_seconds_of_day(
        record->recorded_timestamp, record->utc_offset_minutes);
    const uint8_t local_hour = (uint8_t)(local_seconds / 3600u);
    const uint8_t record_hour = local_hour == 0u ? 23u : (uint8_t)(local_hour - 1u);
    uint32_t record_day_start = record->recorded_timestamp - local_seconds;
    if (local_hour == 0u) {
        record_day_start -= UINT32_C(86400);
    }
    if (previous_local_day_only) {
        const uint32_t current_day_start = firmware_timestamp
            - activity_local_seconds_of_day(
                firmware_timestamp, record->utc_offset_minutes);
        if (current_day_start <= record_day_start) {
            return R1_OK;
        }
    }

    if (activity_day_builder_count(builder) != 0u
        && (builder->history.local_day_start != record_day_start
            || builder->history.utc_offset_minutes
                != record->utc_offset_minutes)) {
        const r1_error error = r1_activity_day_builder_flush(
            builder, firmware_timestamp, emit, emit_context, flush_result);
        if (error != R1_OK) {
            return error;
        }
    }
    if (activity_day_builder_count(builder) == 0u) {
        r1_activity_day_builder_reset(builder);
        builder->history.local_day_start = record_day_start;
        builder->history.utc_offset_minutes = record->utc_offset_minutes;
    }
    for (uint8_t within_hour = 0u;
         within_hour < R1_ACTIVITY_BUCKETS_PER_HOUR; ++within_hour) {
        const uint32_t packed = record->packed_words[within_hour];
        if (packed == 0u) {
            continue;
        }
        const uint8_t bucket_index = (uint8_t)(
            (uint16_t)record_hour * R1_ACTIVITY_BUCKETS_PER_HOUR + within_hour);
        activity_day_builder_set_bucket(
            builder, bucket_index,
            (uint16_t)(packed & UINT32_C(0x0fff)),
            (uint16_t)((packed >> 12u) & UINT32_C(0x03ff)),
            (uint16_t)(packed >> 22u), false);
    }
    if (builder->maximum_recorded_timestamp < record->recorded_timestamp) {
        builder->maximum_recorded_timestamp = record->recorded_timestamp;
    }
    return R1_OK;
}

void r1_health_u8_offline_initialize(r1_health_u8_offline_queue *queue) {
    if (queue != NULL) {
        clear_bytes((uint8_t *)queue, sizeof *queue);
    }
}

void r1_health_u16_offline_initialize(r1_health_u16_offline_queue *queue) {
    if (queue != NULL) {
        clear_bytes((uint8_t *)queue, sizeof *queue);
    }
}

static bool health_u8_offline_queue_valid(
    const r1_health_u8_offline_queue *queue) {
    if (queue == NULL || queue->read_index >= R1_HEALTH_OFFLINE_CAPACITY
        || queue->write_index >= R1_HEALTH_OFFLINE_CAPACITY
        || queue->count > R1_HEALTH_OFFLINE_CAPACITY
        || queue->write_index != (uint8_t)(
            ((uint16_t)queue->read_index + (uint16_t)queue->count)
            % R1_HEALTH_OFFLINE_CAPACITY)) {
        return false;
    }
    for (uint16_t position = 0u; position < queue->count; ++position) {
        const uint16_t physical = (uint16_t)(
            ((uint16_t)queue->read_index + position)
            % R1_HEALTH_OFFLINE_CAPACITY);
        if (queue->entries[physical].hour_index >= R1_HEALTH_HOURLY_SLOTS) {
            return false;
        }
    }
    return true;
}

static bool health_u16_offline_queue_valid(
    const r1_health_u16_offline_queue *queue) {
    if (queue == NULL || queue->read_index >= R1_HEALTH_OFFLINE_CAPACITY
        || queue->write_index >= R1_HEALTH_OFFLINE_CAPACITY
        || queue->count > R1_HEALTH_OFFLINE_CAPACITY
        || queue->write_index != (uint8_t)(
            ((uint16_t)queue->read_index + (uint16_t)queue->count)
            % R1_HEALTH_OFFLINE_CAPACITY)) {
        return false;
    }
    for (uint16_t position = 0u; position < queue->count; ++position) {
        const uint16_t physical = (uint16_t)(
            ((uint16_t)queue->read_index + position)
            % R1_HEALTH_OFFLINE_CAPACITY);
        if (queue->entries[physical].hour_index >= R1_HEALTH_HOURLY_SLOTS) {
            return false;
        }
    }
    return true;
}

bool r1_health_u8_offline_is_empty(const r1_health_u8_offline_queue *queue) {
    return queue == NULL || queue->count == 0u;
}

bool r1_health_u16_offline_is_empty(const r1_health_u16_offline_queue *queue) {
    return queue == NULL || queue->count == 0u;
}

r1_error r1_health_u8_offline_enqueue(
    r1_health_u8_offline_queue *queue, uint8_t average, uint8_t maximum,
    uint8_t minimum, uint32_t local_day_start, uint32_t recorded_timestamp,
    int16_t utc_offset_minutes, uint8_t hour_index,
    uint32_t firmware_timestamp, r1_health_offline_enqueue_result *result) {
    if (queue == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!health_u8_offline_queue_valid(queue)) {
        return R1_ERROR_STATE;
    }
    if (hour_index >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }
    *result = (r1_health_offline_enqueue_result){
        R1_HEALTH_OFFLINE_ENQUEUED, false,
    };
    if (average == 0u) {
        result->action = R1_HEALTH_OFFLINE_DROPPED_ZERO;
        return R1_OK;
    }
    if (recorded_timestamp > firmware_timestamp) {
        result->action = R1_HEALTH_OFFLINE_DROPPED_FUTURE_RECORDED;
        return R1_OK;
    }
    if (local_day_start > firmware_timestamp) {
        result->action = R1_HEALTH_OFFLINE_DROPPED_FUTURE_DAY;
        return R1_OK;
    }

    r1_health_u8_offline_entry *entry = &queue->entries[queue->write_index];
    const uint8_t retained_after = entry->reserved_after_aggregate;
    const uint8_t retained_tail = entry->reserved_tail;
    entry->average = average;
    entry->maximum = maximum;
    entry->minimum = minimum;
    entry->reserved_after_aggregate = retained_after;
    entry->local_day_start = local_day_start;
    entry->recorded_timestamp = recorded_timestamp;
    entry->utc_offset_minutes = utc_offset_minutes;
    entry->hour_index = hour_index;
    entry->reserved_tail = retained_tail;
    queue->write_index = (uint8_t)(
        ((uint16_t)queue->write_index + 1u) % R1_HEALTH_OFFLINE_CAPACITY);
    if (queue->count < R1_HEALTH_OFFLINE_CAPACITY) {
        queue->count = (uint8_t)(queue->count + 1u);
    } else {
        queue->read_index = (uint8_t)(
            ((uint16_t)queue->read_index + 1u) % R1_HEALTH_OFFLINE_CAPACITY);
        result->overwrote_oldest = true;
    }
    return R1_OK;
}

r1_error r1_health_u16_offline_enqueue(
    r1_health_u16_offline_queue *queue, uint16_t average, uint16_t maximum,
    uint16_t minimum, uint32_t local_day_start, uint32_t recorded_timestamp,
    int16_t utc_offset_minutes, uint8_t hour_index,
    uint32_t firmware_timestamp, r1_health_offline_enqueue_result *result) {
    if (queue == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!health_u16_offline_queue_valid(queue)) {
        return R1_ERROR_STATE;
    }
    if (hour_index >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }
    *result = (r1_health_offline_enqueue_result){
        R1_HEALTH_OFFLINE_ENQUEUED, false,
    };
    if (average == 0u) {
        result->action = R1_HEALTH_OFFLINE_DROPPED_ZERO;
        return R1_OK;
    }
    if (recorded_timestamp > firmware_timestamp) {
        result->action = R1_HEALTH_OFFLINE_DROPPED_FUTURE_RECORDED;
        return R1_OK;
    }
    if (local_day_start > firmware_timestamp) {
        result->action = R1_HEALTH_OFFLINE_DROPPED_FUTURE_DAY;
        return R1_OK;
    }

    r1_health_u16_offline_entry *entry = &queue->entries[queue->write_index];
    const uint8_t retained_0 = entry->reserved_after_aggregate[0];
    const uint8_t retained_1 = entry->reserved_after_aggregate[1];
    const uint8_t retained_tail = entry->reserved_tail;
    entry->average = average;
    entry->maximum = maximum;
    entry->minimum = minimum;
    entry->reserved_after_aggregate[0] = retained_0;
    entry->reserved_after_aggregate[1] = retained_1;
    entry->local_day_start = local_day_start;
    entry->recorded_timestamp = recorded_timestamp;
    entry->utc_offset_minutes = utc_offset_minutes;
    entry->hour_index = hour_index;
    entry->reserved_tail = retained_tail;
    queue->write_index = (uint8_t)(
        ((uint16_t)queue->write_index + 1u) % R1_HEALTH_OFFLINE_CAPACITY);
    if (queue->count < R1_HEALTH_OFFLINE_CAPACITY) {
        queue->count = (uint8_t)(queue->count + 1u);
    } else {
        queue->read_index = (uint8_t)(
            ((uint16_t)queue->read_index + 1u) % R1_HEALTH_OFFLINE_CAPACITY);
        result->overwrote_oldest = true;
    }
    return R1_OK;
}

r1_error r1_health_u8_offline_consume_through(
    r1_health_u8_offline_queue *queue, uint32_t cutoff_timestamp,
    size_t *consumed_count) {
    if (queue == NULL || consumed_count == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!health_u8_offline_queue_valid(queue)) {
        return R1_ERROR_STATE;
    }
    *consumed_count = 0u;
    while (queue->count != 0u) {
        r1_health_u8_offline_entry *entry = &queue->entries[queue->read_index];
        if (entry->recorded_timestamp > cutoff_timestamp) {
            break;
        }
        clear_bytes((uint8_t *)entry, sizeof *entry);
        queue->read_index = (uint8_t)(
            ((uint16_t)queue->read_index + 1u) % R1_HEALTH_OFFLINE_CAPACITY);
        queue->count = (uint8_t)(queue->count - 1u);
        *consumed_count += 1u;
    }
    return R1_OK;
}

r1_error r1_health_u16_offline_consume_through(
    r1_health_u16_offline_queue *queue, uint32_t cutoff_timestamp,
    size_t *consumed_count) {
    if (queue == NULL || consumed_count == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!health_u16_offline_queue_valid(queue)) {
        return R1_ERROR_STATE;
    }
    *consumed_count = 0u;
    while (queue->count != 0u) {
        r1_health_u16_offline_entry *entry = &queue->entries[queue->read_index];
        if (entry->recorded_timestamp > cutoff_timestamp) {
            break;
        }
        clear_bytes((uint8_t *)entry, sizeof *entry);
        queue->read_index = (uint8_t)(
            ((uint16_t)queue->read_index + 1u) % R1_HEALTH_OFFLINE_CAPACITY);
        queue->count = (uint8_t)(queue->count - 1u);
        *consumed_count += 1u;
    }
    return R1_OK;
}

static void health_u8_offline_packet_reset(
    r1_health_u8_offline_packet *packet, uint32_t local_day_start,
    int16_t utc_offset_minutes) {
    clear_bytes((uint8_t *)packet, sizeof *packet);
    packet->history.local_day_start = local_day_start;
    packet->history.utc_offset_minutes = utc_offset_minutes;
}

void r1_health_u8_day_builder_reset(r1_health_u8_offline_packet *builder) {
    if (builder != NULL) {
        health_u8_offline_packet_reset(builder, 0u, 0);
    }
}

r1_error r1_health_u8_day_builder_flush(
    r1_health_u8_offline_packet *builder, uint32_t firmware_timestamp,
    r1_health_u8_offline_emit_fn emit, void *emit_context,
    r1_health_u8_day_flush_result *result) {
    if (builder == NULL || emit == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *result = (r1_health_u8_day_flush_result){false, false, 0u};
    const size_t count = count_u8(&builder->history);
    if (count == 0u) {
        return R1_OK;
    }
    if (builder->maximum_recorded_timestamp > firmware_timestamp) {
        result->dropped_future_acknowledgement = true;
        r1_health_u8_day_builder_reset(builder);
        return R1_OK;
    }
    result->encoded_length = 7u + count * 4u;
    const r1_error error = emit(emit_context, builder);
    result->emitted = error == R1_OK;
    r1_health_u8_day_builder_reset(builder);
    return error;
}

r1_error r1_health_u8_flash_record_merge(
    r1_health_u8_offline_packet *builder,
    const r1_health_u8_flash_record *record, uint32_t firmware_timestamp,
    bool previous_local_day_only, uint32_t current_local_day_start,
    r1_health_u8_offline_emit_fn emit, void *emit_context,
    r1_health_u8_day_flush_result *flush_result) {
    if (builder == NULL || record == NULL || emit == NULL
        || flush_result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *flush_result = (r1_health_u8_day_flush_result){false, false, 0u};
    if (record->local_hour >= R1_HEALTH_HOURLY_SLOTS
        || record->local_minute >= 60u || record->local_second >= 60u) {
        return R1_ERROR_LENGTH;
    }
    if (record->recorded_timestamp > firmware_timestamp
        || record->average == 0u) {
        return R1_OK;
    }
    const uint8_t slot = record->local_hour == 0u
        ? 23u : (uint8_t)(record->local_hour - 1u);
    const uint32_t seconds_into_day =
        (uint32_t)record->local_hour * UINT32_C(3600)
        + (uint32_t)record->local_minute * UINT32_C(60)
        + record->local_second;
    uint32_t record_day_start = record->recorded_timestamp - seconds_into_day;
    if (record->local_hour == 0u) {
        record_day_start -= R1_HEALTH_SECONDS_PER_DAY;
    }
    if (previous_local_day_only && current_local_day_start <= record_day_start) {
        return R1_OK;
    }

    if (count_u8(&builder->history) != 0u
        && (builder->history.local_day_start != record_day_start
            || builder->history.utc_offset_minutes
                != record->utc_offset_minutes)) {
        const r1_error error = r1_health_u8_day_builder_flush(
            builder, firmware_timestamp, emit, emit_context, flush_result);
        if (error != R1_OK) {
            return error;
        }
    }
    if (count_u8(&builder->history) == 0u) {
        r1_health_u8_day_builder_reset(builder);
        builder->history.local_day_start = record_day_start;
        builder->history.utc_offset_minutes = record->utc_offset_minutes;
    }
    r1_health_u8_slot *destination = &builder->history.slots[slot];
    if (destination->average == 0u) {
        destination->average = record->average;
        destination->maximum = record->maximum;
        destination->minimum = record->minimum;
    }
    if (builder->maximum_recorded_timestamp < record->recorded_timestamp) {
        builder->maximum_recorded_timestamp = record->recorded_timestamp;
    }
    return R1_OK;
}

static void health_u16_offline_packet_reset(
    r1_health_u16_offline_packet *packet, uint32_t local_day_start,
    int16_t utc_offset_minutes) {
    clear_bytes((uint8_t *)packet, sizeof *packet);
    packet->history.local_day_start = local_day_start;
    packet->history.utc_offset_minutes = utc_offset_minutes;
}

r1_error r1_health_u8_offline_merge(
    const r1_health_u8_offline_queue *queue, uint32_t firmware_timestamp,
    r1_health_u8_offline_packet *workspace, r1_health_u8_offline_emit_fn emit,
    void *emit_context, r1_health_offline_merge_result *result) {
    if (queue == NULL || workspace == NULL || emit == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!health_u8_offline_queue_valid(queue)) {
        return R1_ERROR_STATE;
    }
    *result = (r1_health_offline_merge_result){0u, 0u, 0u};
    bool active = false;
    for (uint16_t position = 0u; position < queue->count; ++position) {
        const uint16_t physical = (uint16_t)(
            ((uint16_t)queue->read_index + position)
            % R1_HEALTH_OFFLINE_CAPACITY);
        const r1_health_u8_offline_entry *entry = &queue->entries[physical];
        if (entry->average == 0u) {
            result->skipped_zero_count += 1u;
            continue;
        }
        if (entry->recorded_timestamp > firmware_timestamp
            || entry->local_day_start > firmware_timestamp) {
            result->skipped_future_count += 1u;
            continue;
        }
        if (!active || workspace->history.local_day_start != entry->local_day_start
            || workspace->history.utc_offset_minutes != entry->utc_offset_minutes) {
            if (active) {
                const r1_error error = emit(emit_context, workspace);
                if (error != R1_OK) {
                    return error;
                }
                result->packet_count += 1u;
            }
            health_u8_offline_packet_reset(
                workspace, entry->local_day_start, entry->utc_offset_minutes);
            active = true;
        }
        r1_health_u8_slot *slot = &workspace->history.slots[entry->hour_index];
        slot->average = entry->average;
        slot->maximum = entry->maximum;
        slot->minimum = entry->minimum;
        if (entry->recorded_timestamp > workspace->maximum_recorded_timestamp) {
            workspace->maximum_recorded_timestamp = entry->recorded_timestamp;
        }
    }
    if (active) {
        const r1_error error = emit(emit_context, workspace);
        if (error != R1_OK) {
            return error;
        }
        result->packet_count += 1u;
    }
    return R1_OK;
}

/* Recovered R1 heart-rate/SpO2 current-RAM history orchestration. Metric
 * production, provider time, storage, encoding, and transport remain seams. */
r1_error r1_health_u8_ram_cache_merge(
    r1_health_u8_offline_packet *builder, r1_health_u8_history *cache,
    uint32_t requested_day_start, uint32_t window_start,
    uint32_t firmware_timestamp, int16_t current_utc_offset_minutes,
    r1_health_u8_offline_emit_fn emit, void *emit_context,
    r1_health_u8_day_flush_result *flush_result) {
    if (builder == NULL || cache == NULL || emit == NULL
        || flush_result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *flush_result = (r1_health_u8_day_flush_result){false, false, 0u};
    if (requested_day_start == 0u || window_start >= firmware_timestamp) {
        return R1_OK;
    }
    /* The stock subtraction assumes a non-future day. Rejecting one avoids
     * unsigned wrap while preserving every observed valid-input behavior. */
    if (requested_day_start > firmware_timestamp) {
        return R1_ERROR_STATE;
    }

    cache->local_day_start = requested_day_start;
    cache->utc_offset_minutes = current_utc_offset_minutes;
    health_u8_offline_packet_reset(
        builder, requested_day_start, current_utc_offset_minutes);

    uint32_t current_index =
        (firmware_timestamp - requested_day_start) / UINT32_C(3600);
    if (current_index >= R1_HEALTH_HOURLY_SLOTS) {
        current_index = R1_HEALTH_HOURLY_SLOTS - 1u;
    }
    uint32_t maximum_timestamp = 0u;
    for (uint8_t index = 0u; index < R1_HEALTH_HOURLY_SLOTS; ++index) {
        const r1_health_u8_slot *source = &cache->slots[index];
        if (source->average == 0u) {
            continue;
        }
        const uint32_t timestamp =
            requested_day_start + (uint32_t)index * UINT32_C(3600);
        if (index != current_index
            && (timestamp < window_start || timestamp > firmware_timestamp)) {
            continue;
        }
        r1_health_u8_slot *destination = &builder->history.slots[index];
        destination->average = source->average;
        destination->maximum = source->maximum;
        destination->minimum = source->minimum;
        if (timestamp > maximum_timestamp) {
            maximum_timestamp = timestamp;
        }
    }

    const size_t count = count_u8(&builder->history);
    if (count == 0u) {
        return R1_OK;
    }
    builder->maximum_recorded_timestamp =
        r1_activity_clamp_acknowledgement_timestamp(
            maximum_timestamp, firmware_timestamp);
    flush_result->encoded_length = 7u + count * 4u;
    const r1_error error = emit(emit_context, builder);
    flush_result->emitted = error == R1_OK;
    health_u8_offline_packet_reset(builder, 0u, 0);
    return error;
}

r1_error r1_health_u16_offline_merge(
    const r1_health_u16_offline_queue *queue, uint32_t firmware_timestamp,
    r1_health_u16_offline_packet *workspace, r1_health_u16_offline_emit_fn emit,
    void *emit_context, r1_health_offline_merge_result *result) {
    if (queue == NULL || workspace == NULL || emit == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!health_u16_offline_queue_valid(queue)) {
        return R1_ERROR_STATE;
    }
    *result = (r1_health_offline_merge_result){0u, 0u, 0u};
    bool active = false;
    for (uint16_t position = 0u; position < queue->count; ++position) {
        const uint16_t physical = (uint16_t)(
            ((uint16_t)queue->read_index + position)
            % R1_HEALTH_OFFLINE_CAPACITY);
        const r1_health_u16_offline_entry *entry = &queue->entries[physical];
        if (entry->average == 0u) {
            result->skipped_zero_count += 1u;
            continue;
        }
        if (entry->recorded_timestamp > firmware_timestamp
            || entry->local_day_start > firmware_timestamp) {
            result->skipped_future_count += 1u;
            continue;
        }
        if (!active || workspace->history.local_day_start != entry->local_day_start
            || workspace->history.utc_offset_minutes != entry->utc_offset_minutes) {
            if (active) {
                const r1_error error = emit(emit_context, workspace);
                if (error != R1_OK) {
                    return error;
                }
                result->packet_count += 1u;
            }
            health_u16_offline_packet_reset(
                workspace, entry->local_day_start, entry->utc_offset_minutes);
            active = true;
        }
        r1_health_u16_slot *slot = &workspace->history.slots[entry->hour_index];
        slot->average = entry->average;
        slot->maximum = entry->maximum;
        slot->minimum = entry->minimum;
        if (entry->recorded_timestamp > workspace->maximum_recorded_timestamp) {
            workspace->maximum_recorded_timestamp = entry->recorded_timestamp;
        }
    }
    if (active) {
        const r1_error error = emit(emit_context, workspace);
        if (error != R1_OK) {
            return error;
        }
        result->packet_count += 1u;
    }
    return R1_OK;
}

/* Recovered R1 HRV current-RAM history orchestration. HRV production,
 * provider time, storage, encoding, and transport remain external seams. */
r1_error r1_health_u16_ram_cache_merge(
    r1_health_u16_offline_packet *builder, r1_health_u16_history *cache,
    uint32_t requested_day_start, uint32_t window_start,
    uint32_t firmware_timestamp, int16_t current_utc_offset_minutes,
    r1_health_u16_offline_emit_fn emit, void *emit_context,
    r1_health_u16_day_flush_result *flush_result) {
    if (builder == NULL || cache == NULL || emit == NULL
        || flush_result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *flush_result = (r1_health_u16_day_flush_result){false, false, 0u};
    if (requested_day_start == 0u || window_start >= firmware_timestamp) {
        return R1_OK;
    }
    /* The stock subtraction assumes a non-future day. Rejecting one avoids
     * unsigned wrap while preserving every observed valid-input behavior. */
    if (requested_day_start > firmware_timestamp) {
        return R1_ERROR_STATE;
    }

    cache->local_day_start = requested_day_start;
    cache->utc_offset_minutes = current_utc_offset_minutes;
    health_u16_offline_packet_reset(
        builder, requested_day_start, current_utc_offset_minutes);
    builder->history.latest_timestamp = cache->latest_timestamp;
    builder->history.latest_value = cache->latest_value;
    /* The recovered flush always reserves its six-byte latest-HRV prefix
     * once the RAM cache accessor succeeds, including an all-zero value. */
    builder->history.has_latest = true;

    uint32_t current_index =
        (firmware_timestamp - requested_day_start) / UINT32_C(3600);
    if (current_index >= R1_HEALTH_HOURLY_SLOTS) {
        current_index = R1_HEALTH_HOURLY_SLOTS - 1u;
    }
    uint32_t maximum_timestamp = 0u;
    for (uint8_t index = 0u; index < R1_HEALTH_HOURLY_SLOTS; ++index) {
        const r1_health_u16_slot *source = &cache->slots[index];
        if (source->average == 0u) {
            continue;
        }
        const uint32_t timestamp =
            requested_day_start + (uint32_t)index * UINT32_C(3600);
        if (index != current_index
            && (timestamp < window_start || timestamp > firmware_timestamp)) {
            continue;
        }
        r1_health_u16_slot *destination = &builder->history.slots[index];
        destination->average = source->average;
        destination->maximum = source->maximum;
        destination->minimum = source->minimum;
        if (timestamp > maximum_timestamp) {
            maximum_timestamp = timestamp;
        }
    }

    const size_t count = count_u16(&builder->history);
    if (count == 0u) {
        return R1_OK;
    }
    builder->maximum_recorded_timestamp =
        r1_activity_clamp_acknowledgement_timestamp(
            maximum_timestamp, firmware_timestamp);
    flush_result->encoded_length =
        (builder->history.has_latest ? 13u : 7u) + count * 7u;
    const r1_error error = emit(emit_context, builder);
    flush_result->emitted = error == R1_OK;
    health_u16_offline_packet_reset(builder, 0u, 0);
    return error;
}

static void health_offline_ack_result_initialize(
    r1_health_offline_ack_result *result, uint8_t mode,
    bool clock_sampled, uint32_t acknowledged_timestamp,
    uint32_t firmware_timestamp) {
    *result = (r1_health_offline_ack_result){
        mode, clock_sampled,
        clock_sampled && acknowledged_timestamp > firmware_timestamp,
        false, 0u,
    };
}

r1_error r1_health_u8_offline_acknowledge(
    r1_health_u8_offline_queue *queue, uint8_t mode,
    uint32_t acknowledged_timestamp, uint32_t firmware_timestamp,
    uint32_t *last_sync_timestamp, r1_health_offline_ack_result *result) {
    if (queue == NULL || last_sync_timestamp == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!health_u8_offline_queue_valid(queue)) {
        return R1_ERROR_STATE;
    }
    health_offline_ack_result_initialize(
        result, mode, true, acknowledged_timestamp, firmware_timestamp);
    if (mode == R1_HEALTH_ACK_OFFLINE_QUEUE) {
        return r1_health_u8_offline_consume_through(
            queue, acknowledged_timestamp, &result->consumed_count);
    }
    if ((mode == R1_HEALTH_ACK_FLASH_HISTORY
         || mode == R1_HEALTH_ACK_CURRENT_RAM)
        && !result->timestamp_was_future
        && acknowledged_timestamp > *last_sync_timestamp) {
        *last_sync_timestamp = acknowledged_timestamp;
        result->last_sync_updated = true;
    }
    return R1_OK;
}

r1_error r1_health_u16_offline_acknowledge(
    r1_health_u16_offline_queue *queue, uint8_t mode,
    uint32_t acknowledged_timestamp, uint32_t firmware_timestamp,
    uint32_t *last_sync_timestamp, r1_health_offline_ack_result *result) {
    if (queue == NULL || last_sync_timestamp == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!health_u16_offline_queue_valid(queue)) {
        return R1_ERROR_STATE;
    }
    const bool clock_sampled = mode == R1_HEALTH_ACK_FLASH_HISTORY
        || mode == R1_HEALTH_ACK_CURRENT_RAM;
    health_offline_ack_result_initialize(
        result, mode, clock_sampled, acknowledged_timestamp, firmware_timestamp);
    if (mode == R1_HEALTH_ACK_OFFLINE_QUEUE) {
        return r1_health_u16_offline_consume_through(
            queue, acknowledged_timestamp, &result->consumed_count);
    }
    if (clock_sampled && !result->timestamp_was_future
        && acknowledged_timestamp > *last_sync_timestamp) {
        *last_sync_timestamp = acknowledged_timestamp;
        result->last_sync_updated = true;
    }
    return R1_OK;
}

r1_error r1_sleep_plan_validated_delivery(
    const r1_sleep_session *session, r1_sleep_validated_delivery_plan *plan) {
    if (session == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_sleep_validated_delivery_plan){0};
    if (session->stage_count > R1_SLEEP_COMPACT_STAGE_MAX) {
        return R1_ERROR_LENGTH;
    }
    plan->wrapping_duration_seconds =
        session->end_timestamp - session->start_timestamp;
    plan->timestamp_wrapped = session->end_timestamp < session->start_timestamp;
    if (plan->wrapping_duration_seconds <
        R1_SLEEP_VALIDATED_MIN_DURATION_SECONDS) {
        plan->route = R1_SLEEP_VALIDATED_DROP_TOO_SHORT;
        return R1_OK;
    }
    plan->route = R1_SLEEP_VALIDATED_POST_STORAGE_EVENT;
    plan->storage_event = R1_SLEEP_STORAGE_EVENT;
    plan->event_payload_length = (uint16_t)(UINT16_C(32) + session->stage_count);
    plan->direct_fallback_on_post_failure = true;
    return R1_OK;
}

r1_error r1_sleep_plan_storage_consumer(
    bool record_present, bool append_succeeded,
    r1_sleep_storage_consumer_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_sleep_storage_consumer_plan){0};
    plan->consume_record = record_present;
    plan->request_automatic_sync = record_present && append_succeeded;
    plan->automatic_sync_argument = plan->request_automatic_sync
        ? R1_SLEEP_AUTOMATIC_SYNC_TRIGGER : 0u;
    return R1_OK;
}

r1_error r1_sleep_store(r1_sleep_history *history, const r1_sleep_session *session) {
    if (history == NULL || session == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if ((session->type != 1u && session->type != 2u) ||
        session->stage_count > R1_SLEEP_COMPACT_STAGE_MAX ||
        session->end_timestamp < session->start_timestamp) {
        return R1_ERROR_LENGTH;
    }
    for (size_t index = 0u; index < session->stage_count; ++index) {
        if (session->stages[index].type > 3u || session->stages[index].half_minutes == 0u) {
            return R1_ERROR_LENGTH;
        }
    }
    size_t write_index = (size_t)(history->read_index + history->count)
        % R1_SLEEP_SESSION_MAX;
    if (history->count == R1_SLEEP_SESSION_MAX) {
        write_index = history->read_index;
        history->read_index = (uint8_t)((history->read_index + 1u)
                                        % R1_SLEEP_SESSION_MAX);
    } else {
        history->count += 1u;
    }
    history->sessions[write_index] = *session;
    history->sessions[write_index].synchronized = false;
    return R1_OK;
}

r1_error r1_sleep_encode(const r1_sleep_session *session,
                         uint8_t *output, size_t capacity, size_t *written) {
    if (session == NULL || output == NULL || written == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (session->stage_count > R1_SLEEP_COMPACT_STAGE_MAX) {
        return R1_ERROR_LENGTH;
    }
    const size_t length = 32u + (size_t)session->stage_count * 3u;
    if (capacity < length) {
        return R1_ERROR_CAPACITY;
    }
    output[0] = session->type;
    output[1] = session->efficiency;
    output[2] = session->score;
    output[3] = session->reserved_header;
    output[4] = session->wake_ratio;
    output[5] = session->rem_ratio;
    output[6] = session->light_ratio;
    output[7] = session->deep_ratio;
    write_u16(output + 8u, session->body_temperature_raw);
    write_u16(output + 10u, (uint16_t)session->utc_offset_minutes);
    write_u32(output + 12u, session->start_timestamp);
    write_u32(output + 16u, session->end_timestamp);
    write_u16(output + 20u, session->total_minutes);
    write_u16(output + 22u, session->wake_minutes);
    write_u16(output + 24u, session->rem_minutes);
    write_u16(output + 26u, session->light_minutes);
    write_u16(output + 28u, session->deep_minutes);
    write_u16(output + 30u, session->stage_count);
    size_t offset = 32u;
    for (size_t index = 0u; index < session->stage_count; ++index) {
        output[offset] = session->stages[index].type;
        write_u16(output + offset + 1u, session->stages[index].half_minutes);
        offset += 3u;
    }
    *written = offset;
    return R1_OK;
}

static r1_error encode_sleep_header(const r1_sleep_session *session,
                                    uint16_t stored_stage_count,
                                    uint8_t *output, size_t capacity) {
    if (capacity < 32u) {
        return R1_ERROR_CAPACITY;
    }
    output[0] = session->type;
    output[1] = session->efficiency;
    output[2] = session->score;
    output[3] = session->reserved_header;
    output[4] = session->wake_ratio;
    output[5] = session->rem_ratio;
    output[6] = session->light_ratio;
    output[7] = session->deep_ratio;
    write_u16(output + 8u, session->body_temperature_raw);
    write_u16(output + 10u, (uint16_t)session->utc_offset_minutes);
    write_u32(output + 12u, session->start_timestamp);
    write_u32(output + 16u, session->end_timestamp);
    write_u16(output + 20u, session->total_minutes);
    write_u16(output + 22u, session->wake_minutes);
    write_u16(output + 24u, session->rem_minutes);
    write_u16(output + 26u, session->light_minutes);
    write_u16(output + 28u, session->deep_minutes);
    write_u16(output + 30u, stored_stage_count);
    return R1_OK;
}

r1_error r1_sleep_encode_compact(const r1_sleep_session *session,
                                 uint8_t *output, size_t capacity, size_t *written) {
    if (session == NULL || output == NULL || written == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (session->stage_count > R1_SLEEP_COMPACT_STAGE_MAX ||
        session->end_timestamp < session->start_timestamp) {
        return R1_ERROR_LENGTH;
    }
    size_t compact_count = 0u;
    for (size_t index = 0u; index < session->stage_count; ++index) {
        const r1_sleep_stage *stage = &session->stages[index];
        if (stage->type > 3u || stage->half_minutes == 0u) {
            return R1_ERROR_LENGTH;
        }
        compact_count += ((size_t)stage->half_minutes + 62u) / 63u;
        if (compact_count > R1_SLEEP_COMPACT_STAGE_MAX) {
            return R1_ERROR_LENGTH;
        }
    }
    const size_t length = 32u + compact_count;
    if (length > R1_SLEEP_STORED_MAX_BYTES) {
        return R1_ERROR_LENGTH;
    }
    if (capacity < length) {
        return R1_ERROR_CAPACITY;
    }
    r1_error error = encode_sleep_header(session, (uint16_t)compact_count,
                                         output, capacity);
    if (error != R1_OK) {
        return error;
    }
    size_t offset = 32u;
    for (size_t index = 0u; index < session->stage_count; ++index) {
        uint16_t remaining = session->stages[index].half_minutes;
        while (remaining > 0u) {
            const uint8_t run = remaining > 63u ? 63u : (uint8_t)remaining;
            output[offset] = (uint8_t)((uint8_t)(run << 2u) |
                                       session->stages[index].type);
            offset += 1u;
            remaining = (uint16_t)(remaining - run);
        }
    }
    *written = offset;
    return R1_OK;
}

r1_error r1_sleep_decode_compact(const uint8_t *input, size_t length,
                                 bool synchronized, r1_sleep_session *session) {
    if (input == NULL || session == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length < 32u || length > R1_SLEEP_STORED_MAX_BYTES) {
        return R1_ERROR_LENGTH;
    }
    const uint16_t compact_count = read_u16(input + 30u);
    if (compact_count > R1_SLEEP_COMPACT_STAGE_MAX ||
        32u + (size_t)compact_count > length) {
        return R1_ERROR_LENGTH;
    }
    *session = (r1_sleep_session){0};
    session->type = input[0];
    session->efficiency = input[1];
    session->score = input[2];
    session->reserved_header = input[3];
    session->wake_ratio = input[4];
    session->rem_ratio = input[5];
    session->light_ratio = input[6];
    session->deep_ratio = input[7];
    session->body_temperature_raw = read_u16(input + 8u);
    session->utc_offset_minutes = (int16_t)read_u16(input + 10u);
    session->start_timestamp = read_u32(input + 12u);
    session->end_timestamp = read_u32(input + 16u);
    session->total_minutes = read_u16(input + 20u);
    session->wake_minutes = read_u16(input + 22u);
    session->rem_minutes = read_u16(input + 24u);
    session->light_minutes = read_u16(input + 26u);
    session->deep_minutes = read_u16(input + 28u);
    session->synchronized = synchronized;
    if ((session->type != 1u && session->type != 2u) ||
        session->end_timestamp < session->start_timestamp) {
        return R1_ERROR_LENGTH;
    }
    for (size_t index = 0u; index < compact_count; ++index) {
        const uint8_t compact = input[32u + index];
        const uint8_t type = compact & 3u;
        const uint16_t run = compact >> 2u;
        if (run == 0u) {
            return R1_ERROR_LENGTH;
        }
        if (session->stage_count > 0u &&
            session->stages[session->stage_count - 1u].type == type) {
            r1_sleep_stage *previous = &session->stages[session->stage_count - 1u];
            if (previous->half_minutes > UINT16_MAX - run) {
                return R1_ERROR_LENGTH;
            }
            previous->half_minutes = (uint16_t)(previous->half_minutes + run);
        } else {
            if (session->stage_count == R1_SLEEP_COMPACT_STAGE_MAX) {
                return R1_ERROR_CAPACITY;
            }
            session->stages[session->stage_count].type = type;
            session->stages[session->stage_count].half_minutes = run;
            session->stage_count += 1u;
        }
    }
    return R1_OK;
}

r1_error r1_sleep_build_sync_packet(
    const uint8_t *compact, size_t compact_length,
    uint32_t current_timestamp, int16_t current_utc_offset_minutes,
    uint8_t *output, size_t capacity, size_t *written) {
    if (compact == NULL || output == NULL || written == NULL ||
        compact_length < 32u) {
        return R1_ERROR_ARGUMENT;
    }
    const size_t encoded_count = compact[30];
    if (encoded_count > R1_SLEEP_COMPACT_STAGE_MAX ||
        32u + encoded_count > compact_length) {
        return R1_ERROR_LENGTH;
    }

    size_t run_count = 0u;
    uint8_t last_type = 0u;
    uint16_t last_duration = 0u;
    for (size_t index = 0u; index < encoded_count; ++index) {
        const uint8_t encoded = compact[32u + index];
        const uint8_t type = encoded & 3u;
        const uint16_t duration = encoded >> 2u;
        if (duration == 0u) {
            return R1_ERROR_LENGTH;
        }
        if (run_count != 0u && type == last_type) {
            if (last_duration > UINT16_MAX - duration) {
                return R1_ERROR_LENGTH;
            }
            last_duration = (uint16_t)(last_duration + duration);
        } else {
            ++run_count;
            last_type = type;
            last_duration = duration;
        }
    }
    const size_t output_length = 32u + run_count * 3u;
    if (capacity < output_length) {
        return R1_ERROR_CAPACITY;
    }

    for (size_t index = 0u; index < output_length; ++index) {
        output[index] = 0u;
    }
    output[0] = compact[0];
    output[1] = compact[1];
    output[2] = compact[2];
    for (size_t index = 4u; index < 10u; ++index) {
        output[index] = compact[index];
    }
    for (size_t index = 12u; index < 30u; ++index) {
        output[index] = compact[index];
    }

    const uint32_t start_timestamp = read_u32(compact + 12u);
    const uint32_t end_timestamp = read_u32(compact + 16u);
    const bool legacy_clock = start_timestamp < R1_HEALTH_LEGACY_CLOCK_CUTOFF;
    write_u16(output + 10u, legacy_clock
        ? 0u : (uint16_t)current_utc_offset_minutes);
    uint32_t adjusted_end = end_timestamp;
    if (legacy_clock && current_timestamp != 0u &&
        current_timestamp >= start_timestamp &&
        current_timestamp < end_timestamp) {
        adjusted_end = current_timestamp;
    }
    write_u32(output + 16u, adjusted_end);
    write_u16(output + 30u, (uint16_t)run_count);

    size_t output_offset = 32u;
    bool have_run = false;
    for (size_t index = 0u; index < encoded_count; ++index) {
        const uint8_t encoded = compact[32u + index];
        const uint8_t type = encoded & 3u;
        const uint16_t duration = encoded >> 2u;
        if (have_run && output[output_offset - 3u] == type) {
            const uint16_t accumulated = read_u16(output + output_offset - 2u);
            write_u16(output + output_offset - 2u,
                      (uint16_t)(accumulated + duration));
        } else {
            output[output_offset] = type;
            write_u16(output + output_offset + 1u, duration);
            output_offset += 3u;
            have_run = true;
        }
    }
    *written = output_offset;
    return R1_OK;
}

r1_error r1_health_encode_point_u8(const r1_health_u8_history *history,
                                   uint8_t state, uint8_t *output,
                                   size_t capacity, size_t *written) {
    if (history == NULL || output == NULL || written == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (capacity < 8u) {
        return R1_ERROR_CAPACITY;
    }
    write_u16(output, (uint16_t)history->utc_offset_minutes);
    write_u32(output + 2u, history->latest_timestamp);
    output[6] = state;
    output[7] = history->has_latest ? history->latest_value : 0u;
    *written = 8u;
    return R1_OK;
}

r1_error r1_health_encode_point_u16(const r1_health_u16_history *history,
                                    uint8_t state, uint8_t *output,
                                    size_t capacity, size_t *written) {
    if (history == NULL || output == NULL || written == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (capacity < 9u) {
        return R1_ERROR_CAPACITY;
    }
    write_u16(output, (uint16_t)history->utc_offset_minutes);
    write_u32(output + 2u, history->latest_timestamp);
    output[6] = state;
    write_u16(output + 7u, history->has_latest ? history->latest_value : 0u);
    *written = 9u;
    return R1_OK;
}

uint16_t r1_health_next_serial(r1_health_state *state) {
    if (state == NULL) {
        return 0u;
    }
    uint16_t serial = state->next_notification_serial;
    state->next_notification_serial += 1u;
    if (state->next_notification_serial == 0u) {
        state->next_notification_serial = 1u;
    }
    if (serial == 0u) {
        serial = state->next_notification_serial;
        state->next_notification_serial += 1u;
    }
    return serial;
}

r1_error r1_health_register_pending(r1_health_state *state,
                                    uint8_t module, uint8_t command, uint8_t subcommand,
                                    uint16_t serial, r1_pending_kind kind,
                                    uint8_t record_index) {
    if (state == NULL || serial == 0u) {
        return R1_ERROR_ARGUMENT;
    }
    for (size_t index = 0u; index < R1_PENDING_ACK_CAPACITY; ++index) {
        r1_pending_ack *pending = &state->pending[index];
        if (!pending->active) {
            pending->active = true;
            pending->module = module;
            pending->command = command;
            pending->subcommand = subcommand;
            pending->serial = serial;
            pending->kind = kind;
            pending->record_index = record_index;
            return R1_OK;
        }
    }
    return R1_ERROR_CAPACITY;
}

bool r1_health_acknowledge(r1_health_state *state,
                           uint8_t module, uint8_t command, uint8_t subcommand,
                           uint16_t serial) {
    if (state == NULL) {
        return false;
    }
    for (size_t index = 0u; index < R1_PENDING_ACK_CAPACITY; ++index) {
        r1_pending_ack *pending = &state->pending[index];
        if (!pending->active || pending->module != module ||
            pending->command != command || pending->subcommand != subcommand ||
            pending->serial != serial) {
            continue;
        }
        if (pending->kind == R1_PENDING_SLEEP_SESSION &&
            pending->record_index < R1_SLEEP_SESSION_MAX) {
            r1_sleep_session *session = &state->sleep.sessions[pending->record_index];
            if (state->sleep_sync_commit != NULL &&
                state->sleep_sync_commit(state->sleep_sync_context, session) != R1_OK) {
                return false;
            }
            session->synchronized = true;
        }
        pending->active = false;
        return true;
    }
    return false;
}

void r1_health_bind_sleep_sync_commit(r1_health_state *state,
                                      r1_sleep_sync_commit_fn commit,
                                      void *context) {
    if (state != NULL) {
        state->sleep_sync_commit = commit;
        state->sleep_sync_context = context;
    }
}

void r1_health_clear_pending(r1_health_state *state) {
    if (state == NULL) {
        return;
    }
    for (size_t index = 0u; index < R1_PENDING_ACK_CAPACITY; ++index) {
        state->pending[index].active = false;
    }
}

r1_error r1_hrv_calculate_rmssd(const uint16_t *intervals, size_t count,
                                bool alternate_maximum, r1_hrv_rmssd_result *result) {
    if (result == NULL || (count > 0u && intervals == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    if (count > R1_HRV_RR_INTERVAL_MAX) {
        return R1_ERROR_LENGTH;
    }
    clear_bytes((uint8_t *)result, sizeof *result);
    result->interval_count = count;
    result->squared_sum = -1.0f;
    result->mean_squared = -1.0f;
    result->rmssd = -1.0f;
    if (count < 2u) {
        return R1_OK;
    }
    for (size_t index = 0u; index < count; ++index) {
        result->validity[index] = 1u;
    }
    const uint16_t maximum = alternate_maximum ? 1500u : 1100u;
    for (size_t index = 1u; index < count; ++index) {
        const int32_t difference = (int32_t)intervals[index]
            - (int32_t)intervals[index - 1u];
        const uint32_t absolute = difference < 0
            ? (uint32_t)(-difference) : (uint32_t)difference;
        if (absolute > 150u || intervals[index] > maximum) {
            result->validity[index] = 0u;
            result->validity[index - 1u] = 0u;
        }
    }
    for (size_t index = 1u; index < count; ++index) {
        if (result->validity[index - 1u] == 0u || result->validity[index] == 0u) {
            continue;
        }
        const int32_t difference = (int32_t)intervals[index]
            - (int32_t)intervals[index - 1u];
        const uint16_t absolute = (uint16_t)(difference < 0 ? -difference : difference);
        result->differences[result->difference_count] = absolute;
        result->difference_count += 1u;
    }
    if (result->difference_count == 0u) {
        return R1_OK;
    }
    float sum = 0.0f;
    for (size_t index = 0u; index < result->difference_count; ++index) {
        const int32_t difference = result->differences[index];
        const int32_t square = difference * difference;
        sum += (float)square;
    }
    result->squared_sum = sum;
    result->mean_squared = sum / (float)(uint32_t)result->difference_count;
    result->rmssd = __builtin_sqrtf(result->mean_squared);
    result->has_result = true;
    return R1_OK;
}

r1_hrv_publication r1_hrv_publish(float rmssd, bool eligible, uint32_t timestamp) {
    r1_hrv_publication result;
    clear_bytes((uint8_t *)&result, sizeof result);
    if (!(rmssd > 0.0f) || !eligible) {
        return result;
    }
    uint32_t converted;
    if (rmssd >= 4294967296.0f || __builtin_isinf(rmssd)) {
        converted = UINT32_MAX;
    } else {
        converted = (uint32_t)rmssd;
    }
    result.published = true;
    result.converted = converted;
    result.transmitted = (uint16_t)converted;
    write_u16(result.payload, result.transmitted);
    write_u16(result.payload + 2u, 0u);
    write_u32(result.payload + 4u, timestamp);
    return result;
}

void r1_hrv_producer_initialize(r1_hrv_producer *producer) {
    if (producer != NULL) {
        clear_bytes((uint8_t *)producer, sizeof *producer);
    }
}

static void producer_insert(r1_hrv_producer *producer, uint16_t interval) {
    if (interval == 0u) {
        return;
    }
    size_t index;
    if (producer->buffered_count < R1_HRV_RR_INTERVAL_MAX) {
        index = ((size_t)producer->write_index + producer->buffered_count)
            % R1_HRV_RR_INTERVAL_MAX;
        producer->buffered_count += 1u;
    } else {
        index = producer->write_index;
        if (producer->physical_buffer[index] != 0u) {
            producer->nonzero_count -= 1u;
        }
        producer->write_index = (uint16_t)((producer->write_index + 1u)
                                           % R1_HRV_RR_INTERVAL_MAX);
    }
    producer->physical_buffer[index] = interval;
    producer->nonzero_count += 1u;
}

r1_error r1_hrv_producer_ingest(r1_hrv_producer *producer,
                                r1_hrv_producer_session *session,
                                const uint16_t *intervals, size_t count,
                                bool alternate_maximum, bool eligible,
                                uint32_t timestamp, r1_hrv_producer_result *result) {
    if (producer == NULL || session == NULL || result == NULL ||
        (count > 0u && intervals == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    if (count > 4u) {
        return R1_ERROR_LENGTH;
    }
    clear_bytes((uint8_t *)result, sizeof *result);
    producer->callback_count = (uint16_t)(producer->callback_count + 1u);
    if (producer->callback_count < 10u) {
        result->action = R1_HRV_WARMUP_IGNORED;
        return R1_OK;
    }
    for (size_t index = 0u; index < count; ++index) {
        producer_insert(producer, intervals[index]);
    }
    if (producer->callback_count < 60u || producer->nonzero_count < 70u) {
        result->action = producer->callback_count >= 60u
            ? R1_HRV_BELOW_THRESHOLD : R1_HRV_ACCUMULATING;
        return R1_OK;
    }
    r1_error error = r1_hrv_calculate_rmssd(
        producer->physical_buffer, producer->buffered_count,
        alternate_maximum, &result->calculation);
    if (error != R1_OK) {
        return error;
    }
    result->eligibility_checked = result->calculation.rmssd > 0.0f;
    result->publication = r1_hrv_publish(
        result->calculation.rmssd,
        result->eligibility_checked ? eligible : false,
        timestamp);
    r1_hrv_producer_initialize(producer);
    if (result->publication.published) {
        session->subscription_active = false;
        if (session->timed_window_active) {
            session->timed_window_active = false;
            session->timed_window_completed = 1u;
        }
        result->action = R1_HRV_PUBLISHED_RESET;
    } else if (session->timed_window_active) {
        result->action = R1_HRV_FAILED_TIMED_RETRY;
    } else {
        session->subscription_active = false;
        result->action = R1_HRV_FAILED_RESET;
    }
    return R1_OK;
}

r1_error r1_hrv_plan_timing_start(
    const r1_hrv_timing_observation *observation,
    r1_hrv_timing_plan *plan) {
    if (observation == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_hrv_timing_plan){
        R1_HRV_TIMING_START, 0u, 0u, 0u, false, false, false,
    };
    if (observation->mode != 1u) {
        plan->action = R1_HRV_TIMING_INACTIVE;
        return R1_OK;
    }
    if (observation->transition_pending || observation->timeout_pending) {
        plan->action = R1_HRV_TIMING_TRANSITION_PENDING;
        return R1_OK;
    }
    if (!observation->health_enabled) {
        plan->action = R1_HRV_TIMING_HEALTH_DISABLED;
        return R1_OK;
    }
    if (!observation->timing_allowed) {
        plan->action = R1_HRV_TIMING_NOT_ALLOWED;
        return R1_OK;
    }
    if (observation->timeout_exists
        || observation->stream_registration_exists) {
        plan->action = R1_HRV_TIMING_ALREADY_ACTIVE;
        return R1_OK;
    }

    uint32_t delay_seconds = UINT32_C(120);
    if (!observation->hourly_request) {
        const uint32_t phase = observation->current_timestamp
            % UINT32_C(3600);
        if (UINT32_C(3600) - phase < UINT32_C(151)) {
            plan->action = R1_HRV_TIMING_CATCHUP_TOO_CLOSE_TO_HOUR;
            return R1_OK;
        }
        const uint32_t catchup = UINT32_C(3570) - phase;
        if (catchup < delay_seconds) {
            delay_seconds = catchup;
            if (delay_seconds == 0u) {
                plan->action = R1_HRV_TIMING_CATCHUP_TOO_CLOSE_TO_HOUR;
                return R1_OK;
            }
        }
    }
    plan->delay_seconds = delay_seconds;
    plan->timeout_milliseconds = delay_seconds * UINT32_C(1000);
    plan->workspace_clear_bytes = 208u;
    plan->create_one_shot_timeout = true;
    plan->register_sensor_stream_after_timeout_create = true;
    plan->delete_timeout_on_registration_failure = true;
    return R1_OK;
}
