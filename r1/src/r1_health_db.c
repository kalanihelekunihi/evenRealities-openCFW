#include "openr1/r1_health_db.h"

_Static_assert(
    R1_HEALTH_DB_POPULATED_BYTES + R1_HEALTH_DB_RESERVED_TAIL_BYTES ==
        R1_HEALTH_DB_RECORD_BYTES,
    "health.db body geometry must remain exactly 128 bytes");
_Static_assert(
    R1_HEALTH_DB_ACTIVITY_BUCKETS == R1_ACTIVITY_BUCKETS_PER_HOUR,
    "health.db activity body must cover one hour");

static uint16_t health_db_read_u16(const uint8_t *input) {
    return (uint16_t)(
        (uint16_t)input[0] | ((uint16_t)input[1] << 8u));
}

static uint32_t health_db_read_u32(const uint8_t *input) {
    return (uint32_t)input[0]
        | ((uint32_t)input[1] << 8u)
        | ((uint32_t)input[2] << 16u)
        | ((uint32_t)input[3] << 24u);
}

static int16_t health_db_read_i16(const uint8_t *input) {
    const uint16_t bits = health_db_read_u16(input);
    if (bits <= (uint16_t)INT16_MAX) {
        return (int16_t)bits;
    }
    return (int16_t)(-((int32_t)UINT16_MAX - (int32_t)bits) - 1);
}

static void health_db_write_u16(uint8_t *output, uint16_t value) {
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8u);
}

static void health_db_write_u32(uint8_t *output, uint32_t value) {
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8u);
    output[2] = (uint8_t)(value >> 16u);
    output[3] = (uint8_t)(value >> 24u);
}

static void health_db_copy_bytes(
    uint8_t *output, const uint8_t *input, size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        output[index] = input[index];
    }
}

void *r1_health_db_provider_handle(void *provider_database) {
    return provider_database;
}

r1_error r1_health_db_decode_record(
    const uint8_t *input, size_t length, r1_health_db_record *record) {
    if (input == NULL || record == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_HEALTH_DB_RECORD_BYTES) {
        return R1_ERROR_LENGTH;
    }

    *record = (r1_health_db_record){0};
    record->utc_offset_minutes = health_db_read_i16(input);
    record->reserved = health_db_read_u16(input + 2u);
    record->recorded_timestamp = health_db_read_u32(input + 4u);
    record->heart_rate = (r1_health_db_u8_aggregate){
        input[8], input[9], input[10],
    };
    record->spo2 = (r1_health_db_u8_aggregate){
        input[11], input[12], input[13],
    };
    record->temperature = (r1_health_db_u8_aggregate){
        input[14], input[15], input[16],
    };
    record->stress = (r1_health_db_u8_aggregate){
        input[17], input[18], input[19],
    };
    for (size_t index = 0u; index < R1_HEALTH_DB_ACTIVITY_BUCKETS;
         ++index) {
        record->activity_packed[index] =
            health_db_read_u32(input + 20u + index * 4u);
    }
    record->hrv = (r1_health_db_u16_aggregate){
        health_db_read_u16(input + 44u),
        health_db_read_u16(input + 46u),
        health_db_read_u16(input + 48u),
    };
    health_db_copy_bytes(
        record->reserved_tail, input + R1_HEALTH_DB_POPULATED_BYTES,
        R1_HEALTH_DB_RESERVED_TAIL_BYTES);
    return R1_OK;
}

r1_error r1_health_db_encode_record(
    const r1_health_db_record *record,
    uint8_t output[R1_HEALTH_DB_RECORD_BYTES]) {
    if (record == NULL || output == NULL) {
        return R1_ERROR_ARGUMENT;
    }

    health_db_write_u16(output, (uint16_t)record->utc_offset_minutes);
    health_db_write_u16(output + 2u, record->reserved);
    health_db_write_u32(output + 4u, record->recorded_timestamp);
    output[8] = record->heart_rate.average;
    output[9] = record->heart_rate.maximum;
    output[10] = record->heart_rate.minimum;
    output[11] = record->spo2.average;
    output[12] = record->spo2.maximum;
    output[13] = record->spo2.minimum;
    output[14] = record->temperature.average;
    output[15] = record->temperature.maximum;
    output[16] = record->temperature.minimum;
    output[17] = record->stress.average;
    output[18] = record->stress.maximum;
    output[19] = record->stress.minimum;
    for (size_t index = 0u; index < R1_HEALTH_DB_ACTIVITY_BUCKETS;
         ++index) {
        health_db_write_u32(
            output + 20u + index * 4u, record->activity_packed[index]);
    }
    health_db_write_u16(output + 44u, record->hrv.average);
    health_db_write_u16(output + 46u, record->hrv.maximum);
    health_db_write_u16(output + 48u, record->hrv.minimum);
    health_db_copy_bytes(
        output + R1_HEALTH_DB_POPULATED_BYTES, record->reserved_tail,
        R1_HEALTH_DB_RESERVED_TAIL_BYTES);
    return R1_OK;
}

static r1_health_db_u8_aggregate health_db_u8_aggregate_at(
    const r1_health_u8_history *history, uint8_t hour) {
    if (history == NULL) {
        return (r1_health_db_u8_aggregate){0};
    }
    const r1_health_u8_slot *slot = &history->slots[hour];
    return (r1_health_db_u8_aggregate){
        slot->average, slot->maximum, slot->minimum,
    };
}

static uint32_t health_db_pack_activity(
    const r1_activity_bucket *bucket) {
    if (!bucket->valid) {
        return 0u;
    }
    return ((uint32_t)bucket->steps & UINT32_C(0x0fff))
        | (((uint32_t)bucket->active_kilocalories & UINT32_C(0x03ff)) << 12u)
        | (((uint32_t)bucket->all_kilocalories & UINT32_C(0x03ff)) << 22u);
}

r1_error r1_health_db_build_record(
    uint8_t current_local_hour, uint32_t recorded_timestamp,
    int16_t utc_offset_minutes, const r1_activity_history *activity,
    const r1_health_u8_history *heart_rate,
    const r1_health_u8_history *spo2,
    const r1_health_u8_history *temperature,
    const r1_health_u8_history *stress,
    const r1_health_u16_history *hrv, r1_health_db_record *record) {
    if (record == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (current_local_hour >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }
    *record = (r1_health_db_record){
        .utc_offset_minutes = utc_offset_minutes,
        .recorded_timestamp = recorded_timestamp,
    };
    const uint8_t appended_hour = current_local_hour == 0u
        ? 23u : (uint8_t)(current_local_hour - 1u);
    record->heart_rate = health_db_u8_aggregate_at(
        heart_rate, appended_hour);
    record->spo2 = health_db_u8_aggregate_at(spo2, appended_hour);
    record->temperature = health_db_u8_aggregate_at(
        temperature, appended_hour);
    record->stress = health_db_u8_aggregate_at(stress, appended_hour);
    if (activity != NULL) {
        const size_t start =
            (size_t)appended_hour * R1_HEALTH_DB_ACTIVITY_BUCKETS;
        for (size_t index = 0u; index < R1_HEALTH_DB_ACTIVITY_BUCKETS;
             ++index) {
            record->activity_packed[index] =
                health_db_pack_activity(&activity->buckets[start + index]);
        }
    }
    if (hrv != NULL) {
        const r1_health_u16_slot *slot = &hrv->slots[appended_hour];
        record->hrv = (r1_health_db_u16_aggregate){
            slot->average, slot->maximum, slot->minimum,
        };
    }
    return R1_OK;
}

static bool health_db_activity_metadata_differs(
    const r1_activity_history *history, uint32_t local_day_start,
    const r1_health_db_record *record) {
    return history->local_day_start != local_day_start
        || history->utc_offset_minutes != record->utc_offset_minutes;
}

static bool health_db_u8_metadata_differs(
    const r1_health_u8_history *history, uint32_t local_day_start,
    const r1_health_db_record *record) {
    return history->local_day_start != local_day_start
        || history->utc_offset_minutes != record->utc_offset_minutes;
}

static bool health_db_u16_metadata_differs(
    const r1_health_u16_history *history, uint32_t local_day_start,
    const r1_health_db_record *record) {
    return history->local_day_start != local_day_start
        || history->utc_offset_minutes != record->utc_offset_minutes;
}

static r1_error health_db_restore_u8(
    r1_health_u8_history *history, const r1_health_db_record *record,
    const r1_health_db_u8_aggregate *aggregate, uint32_t local_day_start,
    uint8_t hour) {
    if (history == NULL) {
        return R1_OK;
    }
    if (health_db_u8_metadata_differs(history, local_day_start, record)) {
        r1_health_u8_cache_reset(
            history, local_day_start, record->utc_offset_minutes);
    }
    return r1_health_u8_cache_write_slot(
        history, hour, aggregate->average, aggregate->maximum,
        aggregate->minimum);
}

r1_error r1_health_db_restore_record(
    const r1_health_db_record *record, r1_activity_history *activity,
    r1_health_u8_history *heart_rate,
    r1_health_u8_history *spo2, r1_health_u8_history *temperature,
    r1_health_u8_history *stress, r1_health_u16_history *hrv,
    r1_health_db_restore_result *result) {
    if (record == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *result = (r1_health_db_restore_result){0};

    const int64_t local_seconds = (int64_t)record->recorded_timestamp
        + (int64_t)record->utc_offset_minutes * INT64_C(60);
    if (local_seconds < 0) {
        return R1_ERROR_STATE;
    }
    const uint32_t seconds_into_day = (uint32_t)(
        (uint64_t)local_seconds % UINT64_C(86400));
    const uint8_t current_hour = (uint8_t)(
        seconds_into_day / UINT32_C(3600));
    const uint8_t appended_hour = current_hour == 0u
        ? 23u : (uint8_t)(current_hour - 1u);
    int64_t local_day_start =
        (int64_t)record->recorded_timestamp - (int64_t)seconds_into_day;
    if (current_hour == 0u) {
        local_day_start -= INT64_C(86400);
    }
    if (local_day_start < 0 || local_day_start > UINT32_MAX) {
        return R1_ERROR_STATE;
    }
    result->appended_hour = appended_hour;
    result->local_day_start = (uint32_t)local_day_start;

    if (activity != NULL) {
        r1_activity_bucket buckets[R1_HEALTH_DB_ACTIVITY_BUCKETS];
        for (size_t index = 0u; index < R1_HEALTH_DB_ACTIVITY_BUCKETS;
             ++index) {
            const uint32_t packed = record->activity_packed[index];
            buckets[index] = (r1_activity_bucket){
                .steps = (uint16_t)(packed & UINT32_C(0x0fff)),
                .active_kilocalories =
                    (uint16_t)((packed >> 12u) & UINT32_C(0x03ff)),
                .all_kilocalories =
                    (uint16_t)((packed >> 22u) & UINT32_C(0x03ff)),
                .valid = packed != 0u,
            };
        }
        if (health_db_activity_metadata_differs(
                activity, result->local_day_start, record)) {
            r1_activity_cache_reset(
                activity, result->local_day_start,
                record->utc_offset_minutes);
        }
        const r1_error error = r1_activity_cache_write_hour(
            activity, appended_hour, buckets);
        if (error != R1_OK) {
            return error;
        }
        result->activity_bucket_count = R1_HEALTH_DB_ACTIVITY_BUCKETS;
        result->applied = true;
    }

    r1_health_u8_history *u8_targets[] = {
        heart_rate, spo2, temperature, stress,
    };
    const r1_health_db_u8_aggregate *u8_aggregates[] = {
        &record->heart_rate, &record->spo2,
        &record->temperature, &record->stress,
    };
    for (size_t index = 0u;
         index < sizeof u8_targets / sizeof u8_targets[0]; ++index) {
        r1_health_u8_history *target = u8_targets[index];
        const r1_error error = health_db_restore_u8(
            target, record, u8_aggregates[index], result->local_day_start,
            appended_hour);
        if (error != R1_OK) {
            return error;
        }
        if (target != NULL) {
            result->metric_slot_count += 1u;
            result->applied = true;
        }
    }

    if (hrv != NULL) {
        if (health_db_u16_metadata_differs(
                hrv, result->local_day_start, record)) {
            r1_health_u16_cache_reset(
                hrv, result->local_day_start,
                record->utc_offset_minutes);
        }
        const r1_error error = r1_health_u16_cache_write_slot(
            hrv, appended_hour, record->hrv.average,
            record->hrv.maximum, record->hrv.minimum);
        if (error != R1_OK) {
            return error;
        }
        result->metric_slot_count += 1u;
        result->applied = true;
    }
    return R1_OK;
}

static bool startup_arguments_valid(
    const uint8_t *schema_payload_bytes,
    const r1_health_db_startup_ops *ops,
    r1_health_crash_record *crash_record,
    r1_activity_history *activity,
    r1_health_u8_history *heart_rate,
    r1_health_u8_accumulator *heart_rate_accumulator,
    r1_health_u8_history *spo2,
    r1_health_u16_history *hrv,
    r1_health_db_startup_result *result) {
    return schema_payload_bytes != NULL && ops != NULL &&
        ops->control != NULL && ops->initialize != NULL &&
        ops->ensure_mutex != NULL && ops->subscribe_time != NULL &&
        ops->set_clock != NULL && ops->mark_clock_valid != NULL &&
        ops->current_clock != NULL &&
        ops->local_day_start != NULL && ops->allocate != NULL &&
        ops->release != NULL && ops->recover != NULL &&
        crash_record != NULL && activity != NULL && heart_rate != NULL &&
        heart_rate_accumulator != NULL && spo2 != NULL && hrv != NULL &&
        result != NULL;
}

static void clear_workspace(uint8_t *workspace) {
    for (size_t index = 0u; index < R1_HEALTH_DB_RECORD_BYTES; ++index) {
        workspace[index] = 0u;
    }
}

r1_error r1_health_db_startup(
    const uint8_t schema_payload_bytes[R1_HEALTH_DB_SCHEMA_COUNT],
    const r1_health_db_startup_ops *ops,
    r1_health_crash_record *crash_record,
    r1_activity_history *activity,
    r1_health_u8_history *heart_rate,
    r1_health_u8_accumulator *heart_rate_accumulator,
    r1_health_u8_history *spo2,
    r1_health_u16_history *hrv,
    r1_health_db_startup_result *result) {
    if (!startup_arguments_valid(
            schema_payload_bytes, ops, crash_record, activity, heart_rate,
            heart_rate_accumulator, spo2, hrv, result)) {
        return R1_ERROR_ARGUMENT;
    }

    *result = (r1_health_db_startup_result){
        .action = R1_HEALTH_DB_STARTUP_COMPLETED,
        .database_error = R1_OK,
        .crash_time_clear_error = R1_OK,
        .crash_restore = {
            .action = R1_HEALTH_CRASH_INVALID_OR_EMPTY,
        },
    };

    uint16_t schema_bytes = 0u;
    for (size_t index = 0u; index < R1_HEALTH_DB_SCHEMA_COUNT; ++index) {
        schema_bytes = (uint16_t)(
            schema_bytes + (uint16_t)schema_payload_bytes[index]);
    }
    if (schema_bytes > R1_HEALTH_DB_MAX_SCHEMA_BYTES) {
        result->action = R1_HEALTH_DB_STARTUP_SCHEMA_TOO_LARGE;
        return R1_OK;
    }

    ops->control(ops->context, R1_HEALTH_DB_LOCK_CONTROL);
    ops->control(ops->context, R1_HEALTH_DB_UNLOCK_CONTROL);
    result->database_error = ops->initialize(
        ops->context, "health", "health.db", R1_HEALTH_DB_RECORD_BYTES);
    if (result->database_error != R1_OK) {
        result->action = R1_HEALTH_DB_STARTUP_DATABASE_INIT_FAILED;
        return R1_OK;
    }

    ops->ensure_mutex(ops->context);
    ops->subscribe_time(ops->context, 1u);
    ops->subscribe_time(ops->context, 0u);

    r1_health_crash_time crash_time;
    if (r1_health_crash_record_has_magic(crash_record) &&
        r1_health_crash_record_get_time(crash_record, &crash_time)) {
        ops->set_clock(
            ops->context, crash_time.utc_timestamp,
            crash_time.utc_offset_minutes);
        if (crash_time.clock_valid) {
            ops->mark_clock_valid(ops->context);
        }
        result->crash_time_restored = true;
        result->crash_time_clear_error =
            r1_health_crash_record_clear_time(crash_record);
    }

    ops->current_clock(
        ops->context, &result->current_timestamp,
        &result->utc_offset_minutes);
    result->local_day_start_timestamp = ops->local_day_start(
        ops->context, result->current_timestamp,
        result->utc_offset_minutes);

    uint8_t *workspace = ops->allocate(
        ops->context, R1_HEALTH_DB_RECORD_BYTES);
    if (workspace == NULL) {
        result->action = R1_HEALTH_DB_STARTUP_WORKSPACE_UNAVAILABLE;
        return R1_OK;
    }
    clear_workspace(workspace);
    ops->recover(
        ops->context, result->local_day_start_timestamp,
        result->current_timestamp, workspace, R1_HEALTH_DB_RECORD_BYTES);
    result->recovery_attempted = true;
    ops->release(ops->context, workspace);

    return r1_health_crash_record_restore(
        crash_record, activity, heart_rate, heart_rate_accumulator,
        spo2, hrv, &result->crash_restore);
}
