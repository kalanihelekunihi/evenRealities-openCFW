#include "openr1/r1_health_db.h"

void *r1_health_db_provider_handle(void *provider_database) {
    return provider_database;
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
