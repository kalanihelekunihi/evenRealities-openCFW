#include "openr1_databases_zephyr.h"

#include <errno.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include <fal.h>
#include <flashdb.h>
#include <zephyr/kernel.h>
#include <zephyr/linker/section_tags.h>

#include "openr1/r1_fal_port.h"
#include "openr1/r1_nv_recovery.h"
#include "openr1/r1_persistence.h"
#include "openr1/r1_state.h"
#include "openr1_clock_zephyr.h"
#include "openr1_gomore_zephyr.h"
#include "openr1_power_zephyr.h"
#include "openr1_sensor_stream_zephyr.h"
#include "openr1_storage_zephyr.h"
#include "time_calendar/time_calendar.h"

/* Byte 1 from each recovered 16-byte schema descriptor at 0x00099BF4. */
static const uint8_t health_schema_bytes[R1_HEALTH_DB_SCHEMA_COUNT] = {
    3u, 3u, 3u, 3u, 24u, 6u,
};

static r1_kv_store kv_store;
static r1_sleep_db sleep_database;
static struct fdb_tsdb health_database;
static r1_health_db_startup_result health_startup_result;
static r1_event_bus health_event_bus;
static struct k_mutex health_mutex;
K_MUTEX_DEFINE(kv_mutex);
static r1_health_u8_accumulator heart_rate_accumulator;
static r1_health_u8_accumulator spo2_accumulator;
static r1_health_u16_accumulator hrv_accumulator;
static r1_health_u8_accumulator temperature_accumulator;
static r1_health_u8_history temperature_history;
static r1_health_u8_history stress_history;
static r1_health_sync_cursor_state health_sync_cursors;
static r1_temperature_pair_calibration temperature_calibration;
static bool temperature_calibration_present;
static r1_motion_axis_calibration accelerometer_calibration;
static bool accelerometer_calibration_present;
static r1_nv_battery_configuration battery_configuration;
static uint8_t configured_ring_size;
static bool configured_ring_size_valid;
static r1_health_crash_record retained_health_crash_record __noinit;
static bool health_mutex_ready;
static bool kv_ready;
static bool health_ready;
static bool sleep_ready;
static r1_error health_subscription_error;
static uint32_t health_time_listener_deliveries;
static uint32_t recovery_records_visited;
static uint32_t recovery_records_decoded;
static uint32_t recovery_records_restored;
static uint32_t recovery_records_rejected;
static uint32_t health_records_appended;
static uint32_t health_append_failures;
static uint32_t health_time_recoveries;
static uint32_t health_time_recovery_failures;
static uint32_t health_time_daily_resets;
static uint32_t health_destructive_actions_suppressed;
static uint32_t health_gomore_reinitializations;
static uint32_t health_gomore_reinitialization_failures;
static uint32_t health_settings_updates_persisted;
static uint32_t health_settings_update_failures;
static uint32_t health_cursor_updates_persisted;
static uint32_t health_cursor_update_failures;
static const uint8_t health_listener_indices[R1_HEALTH_DB_TIME_EVENT_COUNT] = {
    0u, 1u,
};

typedef struct {
    r1_runtime *runtime;
} health_database_context;

static health_database_context health_context;

typedef struct {
    bool (*kv_is_ready)(void);
    bool (*health_is_ready)(void);
    bool (*sleep_is_ready)(void);
    r1_kv_store *(*kv)(void);
    r1_event_bus *(*event_bus)(void);
    r1_health_db_startup_result *(*health_startup)(void);
    void *(*health_handle)(void);
    uint32_t (*recovered_record_count)(void);
    uint32_t (*decoded_record_count)(void);
    uint32_t (*restored_record_count)(void);
    uint32_t (*rejected_record_count)(void);
    uint32_t (*appended_record_count)(void);
    uint32_t (*append_failure_count)(void);
    uint32_t (*time_recovery_count)(void);
    uint32_t (*time_recovery_failure_count)(void);
    uint32_t (*time_daily_reset_count)(void);
    uint32_t (*destructive_action_suppressed_count)(void);
    uint32_t (*gomore_reinitialization_count)(void);
    uint32_t (*gomore_reinitialization_failure_count)(void);
    uint32_t (*health_settings_persisted_count)(void);
    uint32_t (*health_settings_failure_count)(void);
    uint32_t (*cursor_update_persisted_count)(void);
    uint32_t (*cursor_update_failure_count)(void);
    const r1_health_sync_cursor_state *(*health_sync_cursor_state)(void);
    bool (*read_temperature_calibration)(
        r1_temperature_pair_calibration *);
    bool (*read_accelerometer_calibration)(r1_motion_axis_calibration *);
    bool (*read_battery_configuration)(r1_nv_battery_configuration *);
    bool (*read_ring_size)(uint8_t *);
    r1_error (*multicast_time_transition)(
        const r1_health_time_transition *);
    r1_error (*multicast_hour)(uint8_t);
    r1_error (*consume_temperature_event)(const void *, size_t);
    r1_error (*consume_heart_rate_event)(const void *, size_t);
    r1_error (*consume_spo2_event)(const void *, size_t);
    r1_error (*consume_hrv_event)(const void *, size_t);
    r1_error (*consume_activity_cumulative)(const uint32_t [2], uint8_t);
    r1_error (*consume_sleep_record)(const uint8_t *, size_t);
    r1_sleep_db *(*sleep)(void);
} openr1_databases_zephyr_api;

static void health_handle_hour_boundary(uint8_t current_local_hour);
static void health_handle_time_transition(
    const r1_health_time_transition *transition);

static void settings_changed(
    void *context, const uint8_t system_settings[R1_SYSTEM_SETTINGS_BYTES]) {
    (void)context;
    if (!kv_ready || k_is_in_isr() ||
        system_settings[4] != R1_SYSTEM_SETTINGS_SWITCH_TYPE_REG1) {
        return;
    }
    const bool enabled = system_settings[5] != 0u;
    uint8_t dev_info[R1_KV_CLASS_PAYLOAD_MAX];
    size_t length = 0u;
    if (k_mutex_lock(&kv_mutex, K_FOREVER) != 0) {
        return;
    }
    const bool persist_failed = r1_kv_store_get(
            &kv_store, R1_KV_DEV_INFO, dev_info, sizeof dev_info,
            &length) != R1_OK ||
        r1_system_settings_store_reg1(
            dev_info, length, enabled) != R1_OK ||
        r1_kv_store_set(
            &kv_store, R1_KV_DEV_INFO, dev_info, length) != R1_OK ||
        r1_kv_store_commit(&kv_store) != R1_OK;
    (void)k_mutex_unlock(&kv_mutex);
    if (!persist_failed) {
        (void)openr1_power_zephyr_set_reg1(enabled);
    }
}

static void health_settings_changed(
    void *context, const r1_health_settings_command_plan *plan) {
    (void)context;
    if (plan == NULL || !plan->write_command) {
        return;
    }
    /* Event 0x100d feeds GoMore authorization slots 0 and 3 in the stock
     * image. The owner-thread poll reconciles those exact source-built slots
     * and the source-built engine independently. */
    if (plan->private_event_publish_requested) {
        openr1_sensor_stream_zephyr_health_policy_request(
            plan->persistent_record.enabled != 0u);
    }
    if (!plan->persistent_update_requested) {
        return;
    }
    if (!kv_ready || k_is_in_isr()) {
        health_settings_update_failures += 1u;
        return;
    }
    uint8_t dev_info[R1_KV_CLASS_PAYLOAD_MAX];
    size_t length = 0u;
    if (k_mutex_lock(&kv_mutex, K_FOREVER) != 0) {
        health_settings_update_failures += 1u;
        return;
    }
    const bool persist_failed = r1_kv_store_get(
            &kv_store, R1_KV_DEV_INFO, dev_info, sizeof dev_info,
            &length) != R1_OK ||
        r1_health_settings_store_dev_info(
            dev_info, length, &plan->persistent_record) != R1_OK ||
        r1_kv_store_set(
            &kv_store, R1_KV_DEV_INFO, dev_info, length) != R1_OK ||
        r1_kv_store_commit(&kv_store) != R1_OK;
    (void)k_mutex_unlock(&kv_mutex);
    if (persist_failed) {
        health_settings_update_failures += 1u;
    } else {
        health_settings_updates_persisted += 1u;
    }
}

static void health_lock(fdb_db_t database) {
    (void)database;
    if (health_mutex_ready && !k_is_in_isr()) {
        (void)k_mutex_lock(&health_mutex, K_FOREVER);
    }
}

static void health_unlock(fdb_db_t database) {
    (void)database;
    if (health_mutex_ready && !k_is_in_isr()) {
        (void)k_mutex_unlock(&health_mutex);
    }
}

static void health_control(void *context, r1_health_db_control control) {
    (void)context;
    fdb_tsdb_control(
        &health_database,
        control == R1_HEALTH_DB_LOCK_CONTROL
            ? FDB_TSDB_CTRL_SET_LOCK : FDB_TSDB_CTRL_SET_UNLOCK,
        control == R1_HEALTH_DB_LOCK_CONTROL
            ? health_lock : health_unlock);
}

static fdb_time_t health_get_time(void) {
    uint32_t epoch = 0u;
    return openr1_clock_zephyr_epoch(&epoch)
        ? (fdb_time_t)epoch : (fdb_time_t)0;
}

static r1_error health_initialize(
    void *context, const char *name, const char *path, size_t record_bytes) {
    (void)context;
    return fdb_tsdb_init(
               &health_database, name, path, health_get_time,
               record_bytes, NULL) == FDB_NO_ERR
        ? R1_OK : R1_ERROR_STATE;
}

static void health_ensure_mutex(void *context) {
    (void)context;
    if (!health_mutex_ready) {
        k_mutex_init(&health_mutex);
        health_mutex_ready = true;
    }
}

static void health_time_listener(
    const uint8_t *payload, size_t length, void *context) {
    health_time_listener_deliveries += 1u;
    const uint8_t event_index = context != NULL
        ? *(const uint8_t *)context : UINT8_MAX;
    if (event_index == 0u && payload != NULL && length == 12u) {
        const uint16_t old_offset_raw = (uint16_t)(
            (uint16_t)payload[0] | (uint16_t)((uint16_t)payload[1] << 8u));
        const uint16_t new_offset_raw = (uint16_t)(
            (uint16_t)payload[2] | (uint16_t)((uint16_t)payload[3] << 8u));
        const r1_health_time_transition transition = {
            .old_utc_offset_minutes = old_offset_raw <= INT16_MAX
                ? (int16_t)old_offset_raw
                : (int16_t)((int32_t)old_offset_raw - INT32_C(65536)),
            .new_utc_offset_minutes = new_offset_raw <= INT16_MAX
                ? (int16_t)new_offset_raw
                : (int16_t)((int32_t)new_offset_raw - INT32_C(65536)),
            .old_timestamp_seconds =
                (uint32_t)payload[4] |
                ((uint32_t)payload[5] << 8u) |
                ((uint32_t)payload[6] << 16u) |
                ((uint32_t)payload[7] << 24u),
            .new_timestamp_seconds =
                (uint32_t)payload[8] |
                ((uint32_t)payload[9] << 8u) |
                ((uint32_t)payload[10] << 16u) |
                ((uint32_t)payload[11] << 24u),
        };
        health_handle_time_transition(&transition);
    } else if (event_index == 1u && payload != NULL && length == 1u) {
        health_handle_hour_boundary(payload[0]);
    }
}

static void health_subscribe_time(void *context, uint8_t event_index) {
    (void)context;
    const r1_error error = r1_event_bus_subscribe(
        &health_event_bus, event_index, health_time_listener,
        event_index < R1_HEALTH_DB_TIME_EVENT_COUNT
            ? (void *)&health_listener_indices[event_index] : NULL);
    if (health_subscription_error == R1_OK && error != R1_OK) {
        health_subscription_error = error;
    }
}

static void health_set_clock(
    void *context, uint32_t timestamp, int16_t utc_offset_minutes) {
    (void)context;
    openr1_clock_zephyr_adopt_phone_time(timestamp, utc_offset_minutes);
}

static void health_mark_clock_valid(void *context) {
    (void)context;
    /* Adoption validates and marks r1_clock synchronized atomically. */
}

static void health_current_clock(
    void *context, uint32_t *timestamp, int16_t *utc_offset_minutes) {
    (void)context;
    uint32_t epoch = 0u;
    int16_t offset = 0;
    if (openr1_clock_zephyr_epoch(&epoch)) {
        (void)openr1_clock_zephyr_utc_offset(&offset);
    }
    *timestamp = epoch;
    *utc_offset_minutes = offset;
}

static uint32_t health_local_day_start(
    void *context, uint32_t timestamp, int16_t utc_offset_minutes) {
    (void)context;
    const int64_t local =
        (int64_t)timestamp + (int64_t)utc_offset_minutes * INT64_C(60);
    if (local <= 0 || local > UINT32_MAX) {
        return 0u;
    }
    time_calendar_broken_down broken;
    if (time_calendar_unix_to_broken_down(
            (uint32_t)local, &broken) != &broken) {
        return 0u;
    }
    const uint32_t within_day =
        broken.hour * UINT32_C(3600) +
        broken.minute * UINT32_C(60) + broken.second;
    const int64_t utc_start = local - (int64_t)within_day -
        (int64_t)utc_offset_minutes * INT64_C(60);
    return utc_start <= 0 || utc_start > UINT32_MAX
        ? 0u : (uint32_t)utc_start;
}

static void health_reset_all_caches(
    uint32_t timestamp, int16_t utc_offset_minutes) {
    if (health_context.runtime == NULL) {
        return;
    }
    const uint32_t day_start = health_local_day_start(
        NULL, timestamp, utc_offset_minutes);
    r1_runtime *runtime = health_context.runtime;
    r1_activity_cache_reset(
        &runtime->device.health.activity, day_start, utc_offset_minutes);
    r1_health_u8_cache_reset(
        &runtime->device.health.heart_rate, day_start, utc_offset_minutes);
    r1_health_u8_cache_reset(
        &runtime->device.health.blood_oxygen, day_start, utc_offset_minutes);
    r1_health_u8_cache_reset(
        &temperature_history, day_start, utc_offset_minutes);
    r1_health_u8_cache_reset(
        &stress_history, day_start, utc_offset_minutes);
    r1_health_u16_cache_reset(
        &runtime->device.health.heart_rate_variability,
        day_start, utc_offset_minutes);
}

static void health_handle_hour_boundary(uint8_t current_local_hour) {
    if (!health_ready || health_context.runtime == NULL ||
        current_local_hour >= R1_HEALTH_HOURLY_SLOTS) {
        return;
    }
    uint32_t timestamp = 0u;
    int16_t utc_offset_minutes = 0;
    if (!openr1_clock_zephyr_epoch(&timestamp) ||
        !openr1_clock_zephyr_utc_offset(&utc_offset_minutes)) {
        health_append_failures += 1u;
        return;
    }

    r1_health_db_record record;
    uint8_t body[R1_HEALTH_DB_RECORD_BYTES];
    r1_runtime *runtime = health_context.runtime;
    r1_error error = r1_health_db_build_record(
        current_local_hour, timestamp, utc_offset_minutes,
        &runtime->device.health.activity,
        &runtime->device.health.heart_rate,
        &runtime->device.health.blood_oxygen,
        &temperature_history, &stress_history,
        &runtime->device.health.heart_rate_variability, &record);
    if (error == R1_OK) {
        error = r1_health_db_encode_record(&record, body);
    }
    if (error == R1_OK) {
        struct fdb_blob blob;
        if (fdb_tsl_append(
                &health_database,
                fdb_blob_make(&blob, body, sizeof body)) == FDB_NO_ERR) {
            health_records_appended += 1u;
        } else {
            health_append_failures += 1u;
        }
    } else {
        health_append_failures += 1u;
    }

    if (current_local_hour == 0u) {
        health_reset_all_caches(timestamp, utc_offset_minutes);
    }
}

static void *health_allocate(void *context, size_t bytes) {
    (void)context;
    return k_malloc(bytes);
}

static void health_release(void *context, void *allocation) {
    (void)context;
    k_free(allocation);
}

typedef struct {
    uint8_t *workspace;
    size_t workspace_bytes;
    uint32_t from_timestamp;
    uint32_t to_timestamp;
    r1_activity_history *activity;
    r1_health_u8_history *heart_rate;
    r1_health_u8_history *spo2;
    r1_health_u16_history *hrv;
} health_recovery_context;

static bool health_recover_record(fdb_tsl_t record, void *opaque) {
    health_recovery_context *recovery = opaque;
    const bool exact_record_length =
        record->log_len == R1_HEALTH_DB_RECORD_BYTES;
    struct fdb_blob blob;
    const size_t bytes = fdb_blob_read(
        (fdb_db_t)&health_database,
        fdb_tsl_to_blob(
            record, fdb_blob_make(
                &blob, recovery->workspace, recovery->workspace_bytes)));
    if (bytes > 0u) {
        recovery_records_visited += 1u;
    }
    if (!exact_record_length || bytes != R1_HEALTH_DB_RECORD_BYTES) {
        recovery_records_rejected += 1u;
        return false;
    }

    r1_health_db_record decoded;
    if (r1_health_db_decode_record(
            recovery->workspace, bytes, &decoded) != R1_OK) {
        recovery_records_rejected += 1u;
        return false;
    }
    recovery_records_decoded += 1u;
    if (record->time < 0 || (uint64_t)record->time > UINT32_MAX) {
        recovery_records_rejected += 1u;
        return false;
    }
    if (decoded.recorded_timestamp < recovery->from_timestamp ||
        decoded.recorded_timestamp > recovery->to_timestamp) {
        recovery_records_rejected += 1u;
        return false;
    }
    r1_health_db_restore_result restored;
    if (r1_health_db_restore_record(
            &decoded, recovery->activity, recovery->heart_rate, recovery->spo2,
            NULL, NULL, recovery->hrv, &restored) != R1_OK ||
        !restored.applied) {
        recovery_records_rejected += 1u;
        return false;
    }
    recovery_records_restored += 1u;
    return false;
}

static void health_recover(
    void *context, uint32_t from_timestamp, uint32_t to_timestamp,
    uint8_t *workspace, size_t workspace_bytes) {
    health_database_context *database = context;
    health_recovery_context recovery = {
        .workspace = workspace,
        .workspace_bytes = workspace_bytes,
        .from_timestamp = from_timestamp,
        .to_timestamp = to_timestamp,
        .activity = &database->runtime->device.health.activity,
        .heart_rate = &database->runtime->device.health.heart_rate,
        .spo2 = &database->runtime->device.health.blood_oxygen,
        .hrv = &database->runtime->device.health.heart_rate_variability,
    };
    fdb_tsl_iter_by_time(
        &health_database, (fdb_time_t)from_timestamp,
        (fdb_time_t)to_timestamp, health_recover_record, &recovery);
}

static bool health_persist_sync_cursors(
    const r1_health_sync_cursor_state *cursors) {
    uint8_t payload[R1_HEALTH_SYNC_CURSOR_BYTES];
    if (!kv_ready || cursors == NULL || k_is_in_isr() ||
        r1_health_sync_cursor_encode(cursors, payload) != R1_OK ||
        k_mutex_lock(&kv_mutex, K_FOREVER) != 0) {
        return false;
    }
    const bool stored = r1_kv_store_set(
        &kv_store, R1_KV_HSYNC, payload, sizeof payload) == R1_OK;
    if (stored) {
        health_sync_cursors = *cursors;
    }
    const bool committed = stored && r1_kv_store_commit(&kv_store) == R1_OK;
    (void)k_mutex_unlock(&kv_mutex);
    return committed;
}

typedef struct {
    r1_health_scalar_history_emit_fn emit;
    void *emit_context;
    uint8_t acknowledgement_mode;
} scalar_history_packet_emitter;

static r1_error scalar_history_emit_packet(
    void *opaque, const r1_health_u8_offline_packet *packet) {
    scalar_history_packet_emitter *emitter = opaque;
    if (emitter == NULL || packet == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    return emitter->emit(
        emitter->emit_context, &packet->history,
        packet->maximum_recorded_timestamp,
        emitter->acknowledgement_mode);
}

typedef struct {
    uint8_t metric;
    uint32_t firmware_timestamp;
    uint32_t current_local_day_start;
    uint8_t workspace[R1_HEALTH_DB_RECORD_BYTES];
    r1_health_u8_offline_packet builder;
    scalar_history_packet_emitter emitter;
    r1_error error;
} scalar_history_flash_query;

static bool scalar_history_flash_record(fdb_tsl_t record, void *opaque) {
    scalar_history_flash_query *query = opaque;
    if (query->error != R1_OK) {
        return true;
    }
    const bool exact_record_length =
        record->log_len == R1_HEALTH_DB_RECORD_BYTES;
    struct fdb_blob blob;
    const size_t bytes = fdb_blob_read(
        (fdb_db_t)&health_database,
        fdb_tsl_to_blob(
            record, fdb_blob_make(
                &blob, query->workspace, sizeof query->workspace)));
    if (!exact_record_length || bytes != R1_HEALTH_DB_RECORD_BYTES) {
        return false;
    }
    r1_health_db_record decoded;
    if (r1_health_db_decode_record(
            query->workspace, bytes, &decoded) != R1_OK ||
        decoded.recorded_timestamp > query->firmware_timestamp) {
        return false;
    }
    const int64_t local = (int64_t)decoded.recorded_timestamp +
        (int64_t)decoded.utc_offset_minutes * INT64_C(60);
    if (local <= 0 || local > UINT32_MAX) {
        return false;
    }
    time_calendar_broken_down broken;
    if (time_calendar_unix_to_broken_down(
            (uint32_t)local, &broken) != &broken) {
        return false;
    }
    const r1_health_db_u8_aggregate *aggregate = query->metric == 0u
        ? &decoded.heart_rate : &decoded.spo2;
    const r1_health_u8_flash_record normalized = {
        .utc_offset_minutes = decoded.utc_offset_minutes,
        .recorded_timestamp = decoded.recorded_timestamp,
        .local_hour = (uint8_t)broken.hour,
        .local_minute = (uint8_t)broken.minute,
        .local_second = (uint8_t)broken.second,
        .average = aggregate->average,
        .maximum = aggregate->maximum,
        .minimum = aggregate->minimum,
    };
    r1_health_u8_day_flush_result flush;
    query->error = r1_health_u8_flash_record_merge(
        &query->builder, &normalized, query->firmware_timestamp,
        true, query->current_local_day_start,
        scalar_history_emit_packet, &query->emitter, &flush);
    return query->error != R1_OK;
}

static r1_error health_query_scalar_history(
    void *context, uint8_t metric, uint32_t firmware_timestamp,
    const r1_health_u8_history *current_history,
    r1_health_scalar_history_emit_fn emit, void *emit_context) {
    (void)context;
    if (metric > 1u || current_history == NULL || emit == NULL ||
        !health_ready || k_is_in_isr()) {
        return R1_ERROR_ARGUMENT;
    }
    int16_t utc_offset_minutes = 0;
    if (!openr1_clock_zephyr_epoch(&firmware_timestamp) ||
        !openr1_clock_zephyr_utc_offset(&utc_offset_minutes)) {
        return R1_OK;
    }
    const uint32_t current_day_start = health_local_day_start(
        NULL, firmware_timestamp, utc_offset_minutes);
    if (current_day_start == 0u) {
        return R1_OK;
    }
    r1_health_u8_history current_snapshot;
    r1_health_u8_offline_queue offline_snapshot;
    if (k_mutex_lock(&health_mutex, K_FOREVER) != 0) {
        return R1_ERROR_STATE;
    }
    current_snapshot = *current_history;
    offline_snapshot = metric == 0u
        ? health_context.runtime->device.health.heart_rate_offline
        : health_context.runtime->device.health.blood_oxygen_offline;
    (void)k_mutex_unlock(&health_mutex);

    const uint32_t last_sync = metric == 0u
        ? health_context.runtime->device.health.heart_rate_last_sync_seconds
        : health_context.runtime->device.health.blood_oxygen_last_sync_seconds;
    const uint32_t window_floor = firmware_timestamp >
            R1_HEALTH_HISTORY_FLASH_WINDOW_SECONDS
        ? firmware_timestamp - R1_HEALTH_HISTORY_FLASH_WINDOW_SECONDS : 0u;
    const uint32_t from_timestamp = last_sync > window_floor
        ? last_sync : window_floor;
    scalar_history_flash_query query = {
        .metric = metric,
        .firmware_timestamp = firmware_timestamp,
        .current_local_day_start = current_day_start,
        .emitter = {
            .emit = emit,
            .emit_context = emit_context,
            .acknowledgement_mode = R1_HEALTH_ACK_FLASH_HISTORY,
        },
        .error = R1_OK,
    };
    r1_health_u8_day_builder_reset(&query.builder);
    fdb_tsl_iter_by_time(
        &health_database, (fdb_time_t)from_timestamp,
        (fdb_time_t)firmware_timestamp,
        scalar_history_flash_record, &query);
    if (query.error != R1_OK) {
        return query.error;
    }
    r1_health_u8_day_flush_result flush;
    query.error = r1_health_u8_day_builder_flush(
        &query.builder, firmware_timestamp, scalar_history_emit_packet,
        &query.emitter, &flush);
    if (query.error != R1_OK) {
        return query.error;
    }
    query.emitter.acknowledgement_mode = R1_HEALTH_ACK_OFFLINE_QUEUE;
    r1_health_offline_merge_result offline_result;
    query.error = r1_health_u8_offline_merge(
        &offline_snapshot, firmware_timestamp, &query.builder,
        scalar_history_emit_packet, &query.emitter, &offline_result);
    if (query.error != R1_OK) {
        return query.error;
    }
    query.emitter.acknowledgement_mode = R1_HEALTH_ACK_CURRENT_RAM;
    return r1_health_u8_ram_cache_merge(
        &query.builder, &current_snapshot, current_day_start, last_sync,
        firmware_timestamp, utc_offset_minutes,
        scalar_history_emit_packet, &query.emitter, &flush);
}

typedef struct {
    r1_health_hrv_history_emit_fn emit;
    void *emit_context;
    uint8_t acknowledgement_mode;
} hrv_history_packet_emitter;

static r1_error hrv_history_emit_packet(
    void *opaque, const r1_health_u16_offline_packet *packet) {
    hrv_history_packet_emitter *emitter = opaque;
    if (emitter == NULL || packet == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    return emitter->emit(
        emitter->emit_context, &packet->history,
        packet->maximum_recorded_timestamp,
        emitter->acknowledgement_mode);
}

typedef struct {
    uint32_t firmware_timestamp;
    uint32_t window_start;
    uint8_t workspace[R1_HEALTH_DB_RECORD_BYTES];
    r1_health_u16_offline_packet builder;
    hrv_history_packet_emitter emitter;
    r1_error error;
} hrv_history_flash_query;

static bool hrv_history_flash_record(fdb_tsl_t record, void *opaque) {
    hrv_history_flash_query *query = opaque;
    if (query->error != R1_OK) {
        return true;
    }
    const bool exact_record_length =
        record->log_len == R1_HEALTH_DB_RECORD_BYTES;
    struct fdb_blob blob;
    const size_t bytes = fdb_blob_read(
        (fdb_db_t)&health_database,
        fdb_tsl_to_blob(
            record, fdb_blob_make(
                &blob, query->workspace, sizeof query->workspace)));
    if (!exact_record_length || bytes != R1_HEALTH_DB_RECORD_BYTES) {
        return false;
    }
    r1_health_db_record decoded;
    if (r1_health_db_decode_record(
            query->workspace, bytes, &decoded) != R1_OK ||
        decoded.recorded_timestamp > query->firmware_timestamp) {
        return false;
    }
    const int64_t local = (int64_t)decoded.recorded_timestamp +
        (int64_t)decoded.utc_offset_minutes * INT64_C(60);
    if (local <= 0 || local > UINT32_MAX) {
        return false;
    }
    time_calendar_broken_down broken;
    if (time_calendar_unix_to_broken_down(
            (uint32_t)local, &broken) != &broken) {
        return false;
    }
    const r1_health_u16_flash_record normalized = {
        .utc_offset_minutes = decoded.utc_offset_minutes,
        .recorded_timestamp = decoded.recorded_timestamp,
        .local_hour = (uint8_t)broken.hour,
        .local_minute = (uint8_t)broken.minute,
        .local_second = (uint8_t)broken.second,
        .average = decoded.hrv.average,
        .maximum = decoded.hrv.maximum,
        .minimum = decoded.hrv.minimum,
    };
    r1_health_u16_day_flush_result flush;
    query->error = r1_health_u16_flash_record_merge(
        &query->builder, &normalized, query->firmware_timestamp,
        true, query->window_start, hrv_history_emit_packet,
        &query->emitter, &flush);
    return query->error != R1_OK;
}

static r1_error health_query_hrv_history(
    void *context, uint32_t firmware_timestamp,
    const r1_health_u16_history *current_history,
    r1_health_hrv_history_emit_fn emit, void *emit_context) {
    (void)context;
    if (current_history == NULL || emit == NULL || !health_ready ||
        k_is_in_isr()) {
        return R1_ERROR_ARGUMENT;
    }
    int16_t utc_offset_minutes = 0;
    if (!openr1_clock_zephyr_epoch(&firmware_timestamp) ||
        !openr1_clock_zephyr_utc_offset(&utc_offset_minutes)) {
        return R1_OK;
    }
    const uint32_t current_day_start = health_local_day_start(
        NULL, firmware_timestamp, utc_offset_minutes);
    if (current_day_start == 0u) {
        return R1_OK;
    }
    r1_health_u16_history current_snapshot;
    r1_health_u16_offline_queue offline_snapshot;
    if (k_mutex_lock(&health_mutex, K_FOREVER) != 0) {
        return R1_ERROR_STATE;
    }
    current_snapshot = *current_history;
    offline_snapshot = health_context.runtime->device.health
        .heart_rate_variability_offline;
    (void)k_mutex_unlock(&health_mutex);

    const uint32_t last_sync = health_context.runtime->device.health
        .heart_rate_variability_last_sync_seconds;
    const uint32_t window_floor = firmware_timestamp >
            R1_HEALTH_HISTORY_FLASH_WINDOW_SECONDS
        ? firmware_timestamp - R1_HEALTH_HISTORY_FLASH_WINDOW_SECONDS : 0u;
    const uint32_t from_timestamp = last_sync > window_floor
        ? last_sync : window_floor;
    hrv_history_flash_query query = {
        .firmware_timestamp = firmware_timestamp,
        .window_start = from_timestamp,
        .emitter = {
            .emit = emit,
            .emit_context = emit_context,
            .acknowledgement_mode = R1_HEALTH_ACK_FLASH_HISTORY,
        },
        .error = R1_OK,
    };
    r1_health_u16_day_builder_reset(&query.builder);
    fdb_tsl_iter_by_time(
        &health_database, (fdb_time_t)from_timestamp,
        (fdb_time_t)firmware_timestamp,
        hrv_history_flash_record, &query);
    if (query.error != R1_OK) {
        return query.error;
    }
    r1_health_u16_day_flush_result flush;
    query.error = r1_health_u16_day_builder_flush(
        &query.builder, firmware_timestamp, hrv_history_emit_packet,
        &query.emitter, &flush);
    if (query.error != R1_OK) {
        return query.error;
    }
    query.emitter.acknowledgement_mode = R1_HEALTH_ACK_OFFLINE_QUEUE;
    r1_health_offline_merge_result offline_result;
    query.error = r1_health_u16_offline_merge(
        &offline_snapshot, firmware_timestamp, &query.builder,
        hrv_history_emit_packet, &query.emitter, &offline_result);
    if (query.error != R1_OK) {
        return query.error;
    }
    query.emitter.acknowledgement_mode = R1_HEALTH_ACK_CURRENT_RAM;
    return r1_health_u16_ram_cache_merge(
        &query.builder, &current_snapshot, current_day_start, last_sync,
        firmware_timestamp, utc_offset_minutes,
        hrv_history_emit_packet, &query.emitter, &flush);
}

typedef struct {
    r1_health_activity_history_emit_fn emit;
    void *emit_context;
} activity_history_packet_emitter;

static r1_error activity_history_emit_packet(
    void *opaque, const r1_activity_offline_packet *packet) {
    activity_history_packet_emitter *emitter = opaque;
    if (emitter == NULL || packet == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    return emitter->emit(
        emitter->emit_context, &packet->history,
        packet->maximum_recorded_timestamp, packet->mode);
}

typedef struct {
    uint32_t firmware_timestamp;
    uint8_t workspace[R1_HEALTH_DB_RECORD_BYTES];
    r1_activity_offline_packet builder;
    activity_history_packet_emitter emitter;
    r1_error error;
} activity_history_flash_query;

static bool activity_history_flash_record(fdb_tsl_t record, void *opaque) {
    activity_history_flash_query *query = opaque;
    if (query->error != R1_OK) {
        return true;
    }
    const bool exact_record_length =
        record->log_len == R1_HEALTH_DB_RECORD_BYTES;
    struct fdb_blob blob;
    const size_t bytes = fdb_blob_read(
        (fdb_db_t)&health_database,
        fdb_tsl_to_blob(
            record, fdb_blob_make(
                &blob, query->workspace, sizeof query->workspace)));
    if (!exact_record_length || bytes != R1_HEALTH_DB_RECORD_BYTES) {
        return false;
    }
    r1_health_db_record decoded;
    if (r1_health_db_decode_record(
            query->workspace, bytes, &decoded) != R1_OK ||
        decoded.recorded_timestamp > query->firmware_timestamp) {
        return false;
    }
    r1_activity_flash_record normalized = {
        .utc_offset_minutes = decoded.utc_offset_minutes,
        .recorded_timestamp = decoded.recorded_timestamp,
        .packed_words = {0u},
    };
    for (size_t index = 0u; index < R1_ACTIVITY_BUCKETS_PER_HOUR; ++index) {
        normalized.packed_words[index] = decoded.activity_packed[index];
    }
    r1_activity_day_flush_result flush;
    query->error = r1_activity_flash_record_merge(
        &query->builder, &normalized, query->firmware_timestamp, true,
        activity_history_emit_packet, &query->emitter, &flush);
    return query->error != R1_OK;
}

static r1_error health_query_activity_history(
    void *context, uint32_t firmware_timestamp,
    const r1_activity_history *current_history,
    r1_health_activity_history_emit_fn emit, void *emit_context) {
    (void)context;
    if (current_history == NULL || emit == NULL || !health_ready ||
        k_is_in_isr()) {
        return R1_ERROR_ARGUMENT;
    }
    int16_t utc_offset_minutes = 0;
    if (!openr1_clock_zephyr_epoch(&firmware_timestamp) ||
        !openr1_clock_zephyr_utc_offset(&utc_offset_minutes)) {
        return R1_OK;
    }
    const uint32_t current_day_start = health_local_day_start(
        NULL, firmware_timestamp, utc_offset_minutes);
    if (current_day_start == 0u) {
        return R1_OK;
    }
    r1_activity_history current_snapshot;
    r1_activity_offline_queue offline_snapshot;
    if (k_mutex_lock(&health_mutex, K_FOREVER) != 0) {
        return R1_ERROR_STATE;
    }
    current_snapshot = *current_history;
    offline_snapshot = health_context.runtime->device.health.activity_offline;
    (void)k_mutex_unlock(&health_mutex);

    const uint32_t last_sync =
        health_context.runtime->device.health.activity_last_sync_seconds;
    const uint32_t window_floor = firmware_timestamp >
            R1_HEALTH_HISTORY_FLASH_WINDOW_SECONDS
        ? firmware_timestamp - R1_HEALTH_HISTORY_FLASH_WINDOW_SECONDS : 0u;
    const uint32_t from_timestamp = last_sync > window_floor
        ? last_sync : window_floor;
    activity_history_flash_query query = {
        .firmware_timestamp = firmware_timestamp,
        .builder = {
            .mode = R1_ACTIVITY_ACK_FLASH_HISTORY,
            .acknowledgement_requested = true,
        },
        .emitter = {
            .emit = emit,
            .emit_context = emit_context,
        },
        .error = R1_OK,
    };
    fdb_tsl_iter_by_time(
        &health_database, (fdb_time_t)from_timestamp,
        (fdb_time_t)firmware_timestamp,
        activity_history_flash_record, &query);
    /* A full activity day occupies five EUS fragments.  The dispatcher
     * enforces the recovered 50-record shared-queue boundary and reports
     * capacity before registering the next packet.  Treat that boundary as
     * a successful page: ACKs advance the exact per-packet cursor/FIFO prefix
     * and a later query resumes from durable state. */
    if (query.error == R1_ERROR_CAPACITY) {
        return R1_OK;
    }
    if (query.error != R1_OK) {
        return query.error;
    }
    r1_activity_day_flush_result flush;
    query.error = r1_activity_day_builder_flush(
        &query.builder, firmware_timestamp, activity_history_emit_packet,
        &query.emitter, &flush);
    if (query.error == R1_ERROR_CAPACITY) {
        return R1_OK;
    }
    if (query.error != R1_OK) {
        return query.error;
    }
    query.builder.mode = R1_ACTIVITY_ACK_OFFLINE_QUEUE;
    r1_activity_offline_merge_result offline_result;
    query.error = r1_activity_offline_merge(
        &offline_snapshot, firmware_timestamp, &query.builder,
        activity_history_emit_packet, &query.emitter, &offline_result);
    if (query.error == R1_ERROR_CAPACITY) {
        return R1_OK;
    }
    if (query.error != R1_OK) {
        return query.error;
    }
    query.builder.mode = R1_ACTIVITY_ACK_CURRENT_RAM;
    query.error = r1_activity_ram_cache_merge(
        &query.builder, &current_snapshot, current_day_start, last_sync,
        firmware_timestamp, utc_offset_minutes, 0u, 0u, 0u,
        activity_history_emit_packet, &query.emitter, &flush);
    return query.error == R1_ERROR_CAPACITY ? R1_OK : query.error;
}

static r1_error health_commit_scalar_sync_cursor(
    void *context, uint8_t metric, uint32_t acknowledged_timestamp) {
    (void)context;
    r1_health_sync_cursor_state updated = health_sync_cursors;
    if (metric == 0u) {
        updated.heart_rate_timestamp = acknowledged_timestamp;
    } else if (metric == 1u) {
        updated.blood_oxygen_timestamp = acknowledged_timestamp;
    } else if (metric == 2u) {
        updated.heart_rate_variability_timestamp = acknowledged_timestamp;
    } else if (metric == 3u) {
        updated.activity_timestamp = acknowledged_timestamp;
    } else {
        return R1_ERROR_ARGUMENT;
    }
    if (health_persist_sync_cursors(&updated)) {
        health_cursor_updates_persisted += 1u;
        return R1_OK;
    }
    health_cursor_update_failures += 1u;
    return R1_ERROR_STATE;
}

static void health_reinitialize_gomore(void *context) {
    (void)context;
    if (openr1_gomore_zephyr_reinitialize(health_context.runtime) == 0) {
        health_gomore_reinitializations += 1u;
    } else {
        health_gomore_reinitialization_failures += 1u;
    }
}

static void health_handle_time_transition(
    const r1_health_time_transition *transition) {
    if (!health_ready || health_context.runtime == NULL ||
        transition == NULL) {
        return;
    }
    r1_health_sync_cursor_state updated_cursors = health_sync_cursors;
    r1_health_time_transition_result plan;
    if (r1_health_reconcile_sync_cursors(
            &updated_cursors, transition, &plan) != R1_OK ||
        !plan.subscriber_broadcast_requested) {
        return;
    }
    (void)r1_gomore_time_transition_adapter(
        transition, health_reinitialize_gomore, NULL);
    if (plan.health_database_format_requested) {
        health_destructive_actions_suppressed += 1u;
    }
    if (plan.current_day_recovery_requested) {
        const uint32_t day_start = health_local_day_start(
            NULL, transition->new_timestamp_seconds,
            transition->new_utc_offset_minutes);
        uint8_t *workspace = day_start != 0u
            ? k_malloc(R1_HEALTH_DB_RECORD_BYTES) : NULL;
        if (workspace != NULL) {
            for (size_t index = 0u; index < R1_HEALTH_DB_RECORD_BYTES;
                 ++index) {
                workspace[index] = 0u;
            }
            health_recover(
                &health_context, day_start,
                transition->new_timestamp_seconds, workspace,
                R1_HEALTH_DB_RECORD_BYTES);
            k_free(workspace);
            health_time_recoveries += 1u;
        } else {
            health_time_recovery_failures += 1u;
        }
    }
    if (plan.daily_cache_reset_requested) {
        health_reset_all_caches(
            transition->new_timestamp_seconds,
            transition->new_utc_offset_minutes);
        health_time_daily_resets += 1u;
    }
    if (plan.known_cursor_reset_requested ||
        plan.known_cursor_clamped_count != 0u) {
        if (health_persist_sync_cursors(&updated_cursors)) {
            health_cursor_updates_persisted += 1u;
        } else {
            health_cursor_update_failures += 1u;
        }
    }
}

static const r1_health_db_startup_ops health_startup_ops = {
    .context = &health_context,
    .control = health_control,
    .initialize = health_initialize,
    .ensure_mutex = health_ensure_mutex,
    .subscribe_time = health_subscribe_time,
    .set_clock = health_set_clock,
    .mark_clock_valid = health_mark_clock_valid,
    .current_clock = health_current_clock,
    .local_day_start = health_local_day_start,
    .allocate = health_allocate,
    .release = health_release,
    .recover = health_recover,
};

static int health_database_startup(r1_runtime *runtime) {
    health_ensure_mutex(NULL);
    health_context.runtime = runtime;
    r1_event_bus_reset(&health_event_bus);
    health_subscription_error = R1_OK;
    recovery_records_visited = 0u;
    recovery_records_decoded = 0u;
    recovery_records_restored = 0u;
    recovery_records_rejected = 0u;
    health_records_appended = 0u;
    health_append_failures = 0u;
    health_time_recoveries = 0u;
    health_time_recovery_failures = 0u;
    health_time_daily_resets = 0u;
    health_destructive_actions_suppressed = 0u;
    health_gomore_reinitializations = 0u;
    health_gomore_reinitialization_failures = 0u;
    health_settings_updates_persisted = 0u;
    health_settings_update_failures = 0u;
    health_cursor_updates_persisted = 0u;
    health_cursor_update_failures = 0u;
    const r1_error error = r1_health_db_startup(
        health_schema_bytes, &health_startup_ops,
        &retained_health_crash_record,
        &runtime->device.health.activity,
        &runtime->device.health.heart_rate,
        &heart_rate_accumulator,
        &runtime->device.health.blood_oxygen,
        &runtime->device.health.heart_rate_variability,
        &health_startup_result);
    if (error != R1_OK || health_subscription_error != R1_OK ||
        health_startup_result.action != R1_HEALTH_DB_STARTUP_COMPLETED) {
        return -EIO;
    }
    health_ready = true;
    return 0;
}

int openr1_databases_zephyr_initialize(r1_runtime *runtime) {
    if (runtime == NULL) {
        return -EINVAL;
    }
    if (kv_ready || health_ready || sleep_ready) {
        return -EALREADY;
    }
    r1_flash *flash = openr1_storage_zephyr_flash();
    if (flash == NULL || flash->size != UINT32_C(0x00024000)) {
        return -ENODEV;
    }
    if (r1_fal_bind(flash) != R1_OK || fal_init() != 7) {
        return -EIO;
    }
    const struct fal_partition *health_partition =
        fal_partition_find("health.db");
    if (health_partition == NULL ||
        health_partition->offset != (long)UINT32_C(0x00002000) ||
        health_partition->len != UINT32_C(0x00006000)) {
        return -EINVAL;
    }
    if (r1_kv_store_initialize(&kv_store, *flash) != R1_OK) {
        return -EIO;
    }
    kv_ready = true;

    uint8_t dev_info[R1_KV_CLASS_PAYLOAD_MAX];
    size_t dev_info_length = 0u;
    uint8_t hsync_payload[R1_HEALTH_SYNC_CURSOR_BYTES];
    size_t hsync_length = 0u;
    uint8_t nv_config[R1_NV_RECOVERY_CONFIG_BYTES];
    size_t nv_config_length = 0u;
    uint8_t power_config[R1_NV_RECOVERY_POWER_BYTES];
    size_t power_config_length = 0u;
    uint8_t ring_size_config[R1_NV_RECOVERY_RING_SIZE_BYTES];
    size_t ring_size_config_length = 0u;
    if (r1_kv_store_get(
            &kv_store, R1_KV_DEV_INFO, dev_info, sizeof dev_info,
            &dev_info_length) != R1_OK ||
        r1_kv_store_get(
            &kv_store, R1_KV_HSYNC, hsync_payload,
            sizeof hsync_payload, &hsync_length) != R1_OK ||
        r1_health_sync_cursor_decode(
            hsync_payload, hsync_length, &health_sync_cursors) != R1_OK ||
        r1_kv_store_get(
            &kv_store, R1_KV_NV_R1, nv_config, sizeof nv_config,
            &nv_config_length) != R1_OK ||
        nv_config_length != R1_NV_RECOVERY_CONFIG_BYTES ||
        r1_temperature_pair_calibration_decode(
            nv_config + R1_NV_RECOVERY_TEMPERATURE_CALIBRATION_OFFSET,
            R1_NV_RECOVERY_TEMPERATURE_CALIBRATION_BYTES,
            &temperature_calibration,
            &temperature_calibration_present) != R1_OK ||
        r1_nv_accelerometer_calibration_decode(
            nv_config + R1_NV_RECOVERY_ACCELEROMETER_CALIBRATION_OFFSET,
            R1_NV_RECOVERY_ACCELEROMETER_CALIBRATION_BYTES,
            &accelerometer_calibration,
            &accelerometer_calibration_present) != R1_OK ||
        r1_kv_store_get(
            &kv_store, R1_KV_POWER, power_config, sizeof power_config,
            &power_config_length) != R1_OK ||
        r1_nv_battery_configuration_decode(
            power_config, power_config_length,
            &battery_configuration) != R1_OK ||
        r1_kv_store_get(
            &kv_store, R1_KV_RING_SIZE, ring_size_config,
            sizeof ring_size_config, &ring_size_config_length) != R1_OK ||
        r1_nv_ring_size_decode(
            ring_size_config, ring_size_config_length,
            &configured_ring_size, &configured_ring_size_valid) != R1_OK) {
        kv_ready = false;
        return -EIO;
    }
    runtime->device.system_settings[5] =
        r1_system_settings_reg1_enabled(dev_info, dev_info_length) ? 1u : 0u;
    runtime->device.health.heart_rate_last_sync_seconds =
        health_sync_cursors.heart_rate_timestamp;
    runtime->device.health.blood_oxygen_last_sync_seconds =
        health_sync_cursors.blood_oxygen_timestamp;
    runtime->device.health.heart_rate_variability_last_sync_seconds =
        health_sync_cursors.heart_rate_variability_timestamp;
    runtime->device.health.activity_last_sync_seconds =
        health_sync_cursors.activity_timestamp;
    if (dev_info_length > R1_DEV_INFO_HEALTH_TIMESTAMP_OFFSET + 3u) {
        runtime->device.health_settings[0] =
            dev_info[R1_DEV_INFO_HEALTH_TIMESTAMP_OFFSET];
        runtime->device.health_settings[1] =
            dev_info[R1_DEV_INFO_HEALTH_TIMESTAMP_OFFSET + 1u];
        runtime->device.health_settings[2] =
            dev_info[R1_DEV_INFO_HEALTH_TIMESTAMP_OFFSET + 2u];
        runtime->device.health_settings[3] =
            dev_info[R1_DEV_INFO_HEALTH_TIMESTAMP_OFFSET + 3u];
        runtime->device.health_settings[4] =
            (dev_info[R1_DEV_INFO_REG1_FLAG_OFFSET] &
             R1_DEV_INFO_HEALTH_FLAG_MASK) != 0u ? 1u : 0u;
    }
    if (battery_configuration.battery_type_valid) {
        r1_runtime_configure_battery(
            runtime, battery_configuration.battery_type);
    }
    r1_runtime_set_settings_handler(runtime, settings_changed, NULL);
    r1_runtime_set_health_settings_handler(
        runtime, health_settings_changed, NULL);
    r1_health_bind_scalar_history_query(
        &runtime->device.health, health_query_scalar_history, NULL);
    r1_health_bind_hrv_history_query(
        &runtime->device.health, health_query_hrv_history, NULL);
    r1_health_bind_activity_history_query(
        &runtime->device.health, health_query_activity_history, NULL);
    r1_health_bind_sync_cursor_commit(
        &runtime->device.health, health_commit_scalar_sync_cursor, NULL);

    /* The recovered startup task initializes health.db before sleep.db. */
    const int health_error = health_database_startup(runtime);
    const r1_partition *sleep = r1_storage_partition("sleep.db");
    if (sleep == NULL || sleep->offset != UINT32_C(0x00008000) ||
        sleep->length != R1_SLEEP_DB_BYTES ||
        r1_sleep_db_initialize(
            &sleep_database, *flash, sleep->offset) != R1_OK) {
        return -EIO;
    }
    if (r1_sleep_restore(
            &sleep_database, &runtime->device.health.sleep) != R1_OK) {
        return -EIO;
    }
    r1_health_bind_sleep_sync_commit(
        &runtime->device.health, r1_sleep_commit_synchronized,
        &sleep_database);
    sleep_ready = true;
    return health_error;
}

bool openr1_databases_zephyr_kv_ready(void) {
    return kv_ready;
}

bool openr1_databases_zephyr_health_ready(void) {
    return health_ready;
}

bool openr1_databases_zephyr_sleep_ready(void) {
    return sleep_ready;
}

r1_kv_store *openr1_databases_zephyr_kv_store(void) {
    return kv_ready ? &kv_store : NULL;
}

r1_event_bus *openr1_databases_zephyr_event_bus(void) {
    return &health_event_bus;
}

r1_health_db_startup_result *openr1_databases_zephyr_health_startup(void) {
    return &health_startup_result;
}

void *openr1_databases_zephyr_health_handle(void) {
    return health_ready
        ? r1_health_db_provider_handle(&health_database) : NULL;
}

uint32_t openr1_databases_zephyr_recovery_records_visited(void) {
    return recovery_records_visited;
}

uint32_t openr1_databases_zephyr_recovery_records_decoded(void) {
    return recovery_records_decoded;
}

uint32_t openr1_databases_zephyr_recovery_records_restored(void) {
    return recovery_records_restored;
}

uint32_t openr1_databases_zephyr_recovery_records_rejected(void) {
    return recovery_records_rejected;
}

uint32_t openr1_databases_zephyr_health_records_appended(void) {
    return health_records_appended;
}

uint32_t openr1_databases_zephyr_health_append_failures(void) {
    return health_append_failures;
}

uint32_t openr1_databases_zephyr_time_recoveries(void) {
    return health_time_recoveries;
}

uint32_t openr1_databases_zephyr_time_recovery_failures(void) {
    return health_time_recovery_failures;
}

uint32_t openr1_databases_zephyr_time_daily_resets(void) {
    return health_time_daily_resets;
}

uint32_t openr1_databases_zephyr_destructive_actions_suppressed(void) {
    return health_destructive_actions_suppressed;
}

uint32_t openr1_databases_zephyr_gomore_reinitializations(void) {
    return health_gomore_reinitializations;
}

uint32_t openr1_databases_zephyr_gomore_reinitialization_failures(void) {
    return health_gomore_reinitialization_failures;
}

uint32_t openr1_databases_zephyr_health_settings_updates_persisted(void) {
    return health_settings_updates_persisted;
}

uint32_t openr1_databases_zephyr_health_settings_update_failures(void) {
    return health_settings_update_failures;
}

uint32_t openr1_databases_zephyr_cursor_updates_persisted(void) {
    return health_cursor_updates_persisted;
}

uint32_t openr1_databases_zephyr_cursor_update_failures(void) {
    return health_cursor_update_failures;
}

const r1_health_sync_cursor_state *
openr1_databases_zephyr_health_sync_cursors(void) {
    return kv_ready ? &health_sync_cursors : NULL;
}

bool openr1_databases_zephyr_temperature_calibration(
    r1_temperature_pair_calibration *calibration) {
    if (!kv_ready || !temperature_calibration_present ||
        calibration == NULL) {
        return false;
    }
    *calibration = temperature_calibration;
    return true;
}

bool openr1_databases_zephyr_accelerometer_calibration(
    r1_motion_axis_calibration *calibration) {
    if (!kv_ready || !accelerometer_calibration_present ||
        calibration == NULL) {
        return false;
    }
    *calibration = accelerometer_calibration;
    return true;
}

bool openr1_databases_zephyr_battery_configuration(
    r1_nv_battery_configuration *configuration) {
    if (!kv_ready || configuration == NULL) {
        return false;
    }
    *configuration = battery_configuration;
    return true;
}

bool openr1_databases_zephyr_ring_size(uint8_t *ring_size) {
    if (!kv_ready || !configured_ring_size_valid || ring_size == NULL) {
        return false;
    }
    *ring_size = configured_ring_size;
    return true;
}

r1_error openr1_databases_zephyr_multicast_time_transition(
    const r1_health_time_transition *transition) {
    if (transition == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    const uint16_t old_offset =
        (uint16_t)transition->old_utc_offset_minutes;
    const uint16_t new_offset =
        (uint16_t)transition->new_utc_offset_minutes;
    const uint32_t old_timestamp = transition->old_timestamp_seconds;
    const uint32_t new_timestamp = transition->new_timestamp_seconds;
    const uint8_t payload[12] = {
        (uint8_t)old_offset,
        (uint8_t)(old_offset >> 8u),
        (uint8_t)new_offset,
        (uint8_t)(new_offset >> 8u),
        (uint8_t)old_timestamp,
        (uint8_t)(old_timestamp >> 8u),
        (uint8_t)(old_timestamp >> 16u),
        (uint8_t)(old_timestamp >> 24u),
        (uint8_t)new_timestamp,
        (uint8_t)(new_timestamp >> 8u),
        (uint8_t)(new_timestamp >> 16u),
        (uint8_t)(new_timestamp >> 24u),
    };
    return r1_event_bus_multicast(
        &health_event_bus, 0u, payload, sizeof payload, NULL);
}

r1_error openr1_databases_zephyr_multicast_hour(uint8_t current_local_hour) {
    if (current_local_hour >= R1_HEALTH_HOURLY_SLOTS) {
        return R1_ERROR_LENGTH;
    }
    const r1_error error = r1_event_bus_multicast(
        &health_event_bus, 1u, &current_local_hour,
        sizeof current_local_hour, NULL);
    if (error == R1_OK && current_local_hour == 0u) {
        return r1_event_bus_multicast(
            &health_event_bus, 2u, &current_local_hour,
            sizeof current_local_hour, NULL);
    }
    return error;
}

r1_error openr1_databases_zephyr_consume_temperature_event(
    const void *payload, size_t length) {
    if (payload == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != 8u) {
        return R1_ERROR_LENGTH;
    }
    if (!health_ready || k_is_in_isr()) {
        return R1_ERROR_STATE;
    }
    const uint8_t *bytes = payload;
    const uint16_t published_value = (uint16_t)(
        (uint16_t)bytes[0] | (uint16_t)((uint16_t)bytes[1] << 8u));
    /* Stock consumer 0x0008A8FC silently ignores out-of-range events before
     * sampling either the firmware clock or local-hour provider. */
    if (published_value < R1_TEMPERATURE_PUBLISHED_MIN ||
        published_value > R1_TEMPERATURE_PUBLISHED_MAX) {
        return R1_OK;
    }
    uint32_t timestamp = 0u;
    struct tm local;
    if (!openr1_clock_zephyr_epoch(&timestamp) ||
        !openr1_clock_zephyr_local_tm(&local) ||
        local.tm_hour < 0 || local.tm_hour >= 24) {
        return R1_ERROR_STATE;
    }
    r1_health_u8_sample_result result;
    return r1_temperature_store_sample(
        &temperature_history, &temperature_accumulator, published_value,
        timestamp, (uint8_t)local.tm_hour, (uint8_t)local.tm_hour, &result);
}

static uint32_t health_event_u32(const uint8_t *bytes) {
    return (uint32_t)bytes[0] | ((uint32_t)bytes[1] << 8u) |
        ((uint32_t)bytes[2] << 16u) | ((uint32_t)bytes[3] << 24u);
}

static r1_error health_event_time(
    uint32_t *timestamp, uint8_t *local_hour) {
    struct tm local;
    if (timestamp == NULL || local_hour == NULL ||
        !openr1_clock_zephyr_epoch(timestamp) ||
        !openr1_clock_zephyr_local_tm(&local) ||
        local.tm_hour < 0 || local.tm_hour >= 24) {
        return R1_ERROR_STATE;
    }
    *local_hour = (uint8_t)local.tm_hour;
    return R1_OK;
}

static void health_execute_storage_notification(
    r1_runtime *runtime, uint32_t firmware_timestamp,
    bool notification_requested) {
    if (runtime == NULL || !notification_requested) {
        return;
    }
    /* Accepted HR, SpO2, and HRV consumers all tail-call 0x0008B138 with
     * their metric ID. That function ignores the ID and runs the common
     * phone/three-hour five-leg gate. Schedule through the already-bounded
     * runtime controller, then opportunistically start its first leg; a busy
     * queue is retried by the normal wall-clock service cadence. */
    const r1_health_auto_sync_result automatic =
        r1_runtime_schedule_automatic_health_sync(
            runtime, firmware_timestamp);
    if (automatic.batch_started) {
        (void)r1_runtime_service_automatic_health_sync(runtime);
    }
}

r1_error openr1_databases_zephyr_consume_heart_rate_event(
    const void *payload, size_t length) {
    if (payload == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_HEALTH_HISTORY_EVENT_BYTES) {
        return R1_ERROR_LENGTH;
    }
    if (!health_ready || health_context.runtime == NULL || k_is_in_isr()) {
        return R1_ERROR_STATE;
    }
    const uint8_t *bytes = payload;
    uint32_t firmware_timestamp = 0u;
    uint8_t local_hour = 0u;
    if (health_event_time(&firmware_timestamp, &local_hour) != R1_OK) {
        return R1_ERROR_STATE;
    }
    r1_health_u8_sample_result result;
    if (k_mutex_lock(&health_mutex, K_FOREVER) != 0) {
        return R1_ERROR_STATE;
    }
    const r1_error error = r1_heart_rate_store_sample(
        &health_context.runtime->device.health.heart_rate,
        &heart_rate_accumulator, bytes[0], health_event_u32(bytes + 4u),
        firmware_timestamp, local_hour, local_hour, &result);
    (void)k_mutex_unlock(&health_mutex);
    if (error == R1_OK) {
        health_execute_storage_notification(
            health_context.runtime, firmware_timestamp,
            result.notification_requested);
    }
    return error;
}

r1_error openr1_databases_zephyr_consume_spo2_event(
    const void *payload, size_t length) {
    if (payload == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_HEALTH_HISTORY_EVENT_BYTES) {
        return R1_ERROR_LENGTH;
    }
    if (!health_ready || health_context.runtime == NULL || k_is_in_isr()) {
        return R1_ERROR_STATE;
    }
    const uint8_t *bytes = payload;
    uint32_t firmware_timestamp = 0u;
    uint8_t local_hour = 0u;
    if (health_event_time(&firmware_timestamp, &local_hour) != R1_OK) {
        return R1_ERROR_STATE;
    }
    r1_health_u8_sample_result result;
    if (k_mutex_lock(&health_mutex, K_FOREVER) != 0) {
        return R1_ERROR_STATE;
    }
    const r1_error error = r1_spo2_store_sample(
        &health_context.runtime->device.health.blood_oxygen,
        &spo2_accumulator, bytes[0], health_event_u32(bytes + 4u),
        firmware_timestamp, local_hour, local_hour, &result);
    (void)k_mutex_unlock(&health_mutex);
    if (error == R1_OK) {
        health_execute_storage_notification(
            health_context.runtime, firmware_timestamp,
            result.notification_requested);
    }
    return error;
}

r1_error openr1_databases_zephyr_consume_hrv_event(
    const void *payload, size_t length) {
    if (payload == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_HEALTH_HISTORY_EVENT_BYTES) {
        return R1_ERROR_LENGTH;
    }
    if (!health_ready || health_context.runtime == NULL || k_is_in_isr()) {
        return R1_ERROR_STATE;
    }
    const uint8_t *bytes = payload;
    const uint16_t rmssd = (uint16_t)(
        (uint16_t)bytes[0] | (uint16_t)((uint16_t)bytes[1] << 8u));
    uint32_t firmware_timestamp = 0u;
    uint8_t local_hour = 0u;
    if (health_event_time(&firmware_timestamp, &local_hour) != R1_OK) {
        return R1_ERROR_STATE;
    }
    r1_health_u16_sample_result result;
    if (k_mutex_lock(&health_mutex, K_FOREVER) != 0) {
        return R1_ERROR_STATE;
    }
    const r1_error error = r1_hrv_store_sample(
        &health_context.runtime->device.health.heart_rate_variability,
        &hrv_accumulator, rmssd, health_event_u32(bytes + 4u),
        firmware_timestamp, local_hour, local_hour, &result);
    (void)k_mutex_unlock(&health_mutex);
    if (error == R1_OK) {
        health_execute_storage_notification(
            health_context.runtime, firmware_timestamp,
            result.notification_requested);
    }
    return error;
}

typedef struct {
    uint32_t local_day_start;
} activity_bucket_context;

static r1_error activity_bucket_resolve(
    void *context, uint32_t timestamp, uint8_t *bucket_index) {
    const activity_bucket_context *const resolver = context;
    if (resolver == NULL || bucket_index == NULL ||
            timestamp < resolver->local_day_start) {
        return R1_ERROR_ARGUMENT;
    }
    const uint32_t bucket =
        (timestamp - resolver->local_day_start) /
        R1_ACTIVITY_WINDOW_SECONDS;
    if (bucket >= R1_ACTIVITY_BUCKETS) {
        return R1_ERROR_LENGTH;
    }
    *bucket_index = (uint8_t)bucket;
    return R1_OK;
}

r1_error openr1_databases_zephyr_consume_activity_cumulative(
    const uint32_t activity[2], uint8_t sleep_result_status) {
    if (activity == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!health_ready || health_context.runtime == NULL || k_is_in_isr()) {
        return R1_ERROR_STATE;
    }
    uint32_t timestamp = 0u;
    int16_t utc_offset_minutes = 0;
    if (!openr1_clock_zephyr_epoch(&timestamp) ||
            !openr1_clock_zephyr_utc_offset(&utc_offset_minutes)) {
        return R1_ERROR_STATE;
    }
    const uint32_t local_day_start = health_local_day_start(
        NULL, timestamp, utc_offset_minutes);
    if (local_day_start == 0u) {
        return R1_ERROR_STATE;
    }
    const r1_activity_cumulative_counters counters = {
        .steps = activity[0],
        .all_kilocalories = (uint16_t)activity[1],
        .active_kilocalories = (uint16_t)(activity[1] >> 16u),
    };
    const r1_wear_state wear = health_context.runtime->device.wear;
    const uint8_t wear_fusion_state = wear == R1_WEAR_WORN ? 2u :
        wear == R1_WEAR_NOT_WORN ? 0u : 1u;
    r1_activity_accumulator_result accumulated;
    if (k_mutex_lock(&health_mutex, K_FOREVER) != 0) {
        return R1_ERROR_STATE;
    }
    r1_error error = r1_activity_accumulator_periodic(
        &health_context.runtime->device.health.activity_accumulator,
        &counters, timestamp, local_day_start, sleep_result_status,
        wear_fusion_state, &accumulated);
    if (error == R1_OK && accumulated.event_ready) {
        const activity_bucket_context resolver = {
            .local_day_start = local_day_start,
        };
        r1_activity_delta_consume_result consumed;
        error = r1_activity_consume_delta_event(
            &health_context.runtime->device.health.activity,
            &accumulated.event, activity_bucket_resolve, (void *)&resolver,
            local_day_start, utc_offset_minutes, &consumed);
    }
    (void)k_mutex_unlock(&health_mutex);
    return error;
}

r1_error openr1_databases_zephyr_consume_sleep_record(
    const uint8_t *payload, size_t length) {
    if (payload == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (!sleep_ready || health_context.runtime == NULL || k_is_in_isr()) {
        return R1_ERROR_STATE;
    }
    r1_sleep_session session;
    r1_error error = r1_sleep_decode_compact(
        payload, length, false, &session);
    if (error != R1_OK) {
        return error;
    }
    int16_t utc_offset_minutes = 0;
    if (openr1_clock_zephyr_utc_offset(&utc_offset_minutes)) {
        session.utc_offset_minutes = utc_offset_minutes;
    }
    r1_sleep_validated_delivery_plan delivery;
    error = r1_sleep_plan_validated_delivery(&session, &delivery);
    if (error != R1_OK ||
            delivery.route == R1_SLEEP_VALIDATED_DROP_TOO_SHORT) {
        return error;
    }
    if (k_mutex_lock(&health_mutex, K_FOREVER) != 0) {
        return R1_ERROR_STATE;
    }
    const r1_error persist_error =
        r1_sleep_persist_tracked(&sleep_database, &session);
    const r1_error store_error = r1_sleep_store(
        &health_context.runtime->device.health.sleep, &session);
    (void)k_mutex_unlock(&health_mutex);
    if (store_error != R1_OK) {
        return store_error;
    }
    if (persist_error != R1_OK) {
        return persist_error;
    }
    uint32_t timestamp = 0u;
    if (openr1_clock_zephyr_epoch(&timestamp)) {
        health_execute_storage_notification(
            health_context.runtime, timestamp, true);
    }
    return R1_OK;
}

r1_sleep_db *openr1_databases_zephyr_sleep_db(void) {
    return sleep_ready ? &sleep_database : NULL;
}

__attribute__((used, section(".openr1_platform_api")))
static const openr1_databases_zephyr_api databases_zephyr_api = {
    openr1_databases_zephyr_kv_ready,
    openr1_databases_zephyr_health_ready,
    openr1_databases_zephyr_sleep_ready,
    openr1_databases_zephyr_kv_store,
    openr1_databases_zephyr_event_bus,
    openr1_databases_zephyr_health_startup,
    openr1_databases_zephyr_health_handle,
    openr1_databases_zephyr_recovery_records_visited,
    openr1_databases_zephyr_recovery_records_decoded,
    openr1_databases_zephyr_recovery_records_restored,
    openr1_databases_zephyr_recovery_records_rejected,
    openr1_databases_zephyr_health_records_appended,
    openr1_databases_zephyr_health_append_failures,
    openr1_databases_zephyr_time_recoveries,
    openr1_databases_zephyr_time_recovery_failures,
    openr1_databases_zephyr_time_daily_resets,
    openr1_databases_zephyr_destructive_actions_suppressed,
    openr1_databases_zephyr_gomore_reinitializations,
    openr1_databases_zephyr_gomore_reinitialization_failures,
    openr1_databases_zephyr_health_settings_updates_persisted,
    openr1_databases_zephyr_health_settings_update_failures,
    openr1_databases_zephyr_cursor_updates_persisted,
    openr1_databases_zephyr_cursor_update_failures,
    openr1_databases_zephyr_health_sync_cursors,
    openr1_databases_zephyr_temperature_calibration,
    openr1_databases_zephyr_accelerometer_calibration,
    openr1_databases_zephyr_battery_configuration,
    openr1_databases_zephyr_ring_size,
    openr1_databases_zephyr_multicast_time_transition,
    openr1_databases_zephyr_multicast_hour,
    openr1_databases_zephyr_consume_temperature_event,
    openr1_databases_zephyr_consume_heart_rate_event,
    openr1_databases_zephyr_consume_spo2_event,
    openr1_databases_zephyr_consume_hrv_event,
    openr1_databases_zephyr_consume_activity_cumulative,
    openr1_databases_zephyr_consume_sleep_record,
    openr1_databases_zephyr_sleep_db,
};
