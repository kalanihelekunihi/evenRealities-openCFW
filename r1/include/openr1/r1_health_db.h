#ifndef OPENR1_R1_HEALTH_DB_H
#define OPENR1_R1_HEALTH_DB_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_health.h"

#define R1_HEALTH_DB_SCHEMA_COUNT 6u
#define R1_HEALTH_DB_RECORD_BYTES 128u
#define R1_HEALTH_DB_RECORD_OVERHEAD 8u
#define R1_HEALTH_DB_MAX_SCHEMA_BYTES 120u
#define R1_HEALTH_DB_TIME_EVENT_COUNT 2u
#define R1_HEALTH_DB_POPULATED_BYTES 50u
#define R1_HEALTH_DB_ACTIVITY_BUCKETS 6u
#define R1_HEALTH_DB_RESERVED_TAIL_BYTES 78u

typedef struct {
    uint8_t average;
    uint8_t maximum;
    uint8_t minimum;
} r1_health_db_u8_aggregate;

typedef struct {
    uint16_t average;
    uint16_t maximum;
    uint16_t minimum;
} r1_health_db_u16_aggregate;

/* Exact recovered health.db body. The reserved fields are retained so a
 * decoded record can be re-encoded byte-for-byte without treating them as
 * executable or provider-owned content. */
typedef struct {
    int16_t utc_offset_minutes;
    uint16_t reserved;
    uint32_t recorded_timestamp;
    r1_health_db_u8_aggregate heart_rate;
    r1_health_db_u8_aggregate spo2;
    r1_health_db_u8_aggregate temperature;
    r1_health_db_u8_aggregate stress;
    uint32_t activity_packed[R1_HEALTH_DB_ACTIVITY_BUCKETS];
    r1_health_db_u16_aggregate hrv;
    uint8_t reserved_tail[R1_HEALTH_DB_RESERVED_TAIL_BYTES];
} r1_health_db_record;

typedef struct {
    bool applied;
    uint8_t appended_hour;
    uint32_t local_day_start;
    size_t activity_bucket_count;
    size_t metric_slot_count;
} r1_health_db_restore_result;

typedef enum {
    R1_HEALTH_DB_STARTUP_COMPLETED = 0,
    R1_HEALTH_DB_STARTUP_SCHEMA_TOO_LARGE,
    R1_HEALTH_DB_STARTUP_DATABASE_INIT_FAILED,
    R1_HEALTH_DB_STARTUP_WORKSPACE_UNAVAILABLE
} r1_health_db_startup_action;

typedef enum {
    R1_HEALTH_DB_LOCK_CONTROL = 2,
    R1_HEALTH_DB_UNLOCK_CONTROL = 3
} r1_health_db_control;

typedef void (*r1_health_db_control_fn)(void *context,
                                        r1_health_db_control control);
typedef r1_error (*r1_health_db_initialize_fn)(
    void *context, const char *name, const char *path, size_t record_bytes);
typedef void (*r1_health_db_ensure_mutex_fn)(void *context);
typedef void (*r1_health_db_subscribe_time_fn)(void *context,
                                               uint8_t event_index);
typedef void (*r1_health_db_set_clock_fn)(
    void *context, uint32_t timestamp, int16_t utc_offset_minutes);
typedef void (*r1_health_db_mark_clock_valid_fn)(void *context);
typedef void (*r1_health_db_current_clock_fn)(
    void *context, uint32_t *timestamp, int16_t *utc_offset_minutes);
typedef uint32_t (*r1_health_db_local_day_start_fn)(
    void *context, uint32_t timestamp, int16_t utc_offset_minutes);
typedef void *(*r1_health_db_allocate_fn)(void *context, size_t bytes);
typedef void (*r1_health_db_release_fn)(void *context, void *allocation);
typedef void (*r1_health_db_recover_fn)(
    void *context, uint32_t from_timestamp, uint32_t to_timestamp,
    uint8_t *workspace, size_t workspace_bytes);

typedef struct {
    void *context;
    r1_health_db_control_fn control;
    r1_health_db_initialize_fn initialize;
    r1_health_db_ensure_mutex_fn ensure_mutex;
    r1_health_db_subscribe_time_fn subscribe_time;
    r1_health_db_set_clock_fn set_clock;
    r1_health_db_mark_clock_valid_fn mark_clock_valid;
    r1_health_db_current_clock_fn current_clock;
    r1_health_db_local_day_start_fn local_day_start;
    r1_health_db_allocate_fn allocate;
    r1_health_db_release_fn release;
    r1_health_db_recover_fn recover;
} r1_health_db_startup_ops;

typedef struct {
    r1_health_db_startup_action action;
    r1_error database_error;
    bool crash_time_restored;
    r1_error crash_time_clear_error;
    uint32_t current_timestamp;
    int16_t utc_offset_minutes;
    uint32_t local_day_start_timestamp;
    bool recovery_attempted;
    r1_health_crash_restore_result crash_restore;
} r1_health_db_startup_result;

/* The stock accessor returns its statically bound FlashDB object. OpenR1 keeps
 * that object provider-owned and makes the binding explicit. */
void *r1_health_db_provider_handle(void *provider_database);

r1_error r1_health_db_decode_record(
    const uint8_t *input, size_t length, r1_health_db_record *record);
r1_error r1_health_db_encode_record(
    const r1_health_db_record *record,
    uint8_t output[R1_HEALTH_DB_RECORD_BYTES]);
r1_error r1_health_db_build_record(
    uint8_t current_local_hour, uint32_t recorded_timestamp,
    int16_t utc_offset_minutes, const r1_activity_history *activity,
    const r1_health_u8_history *heart_rate,
    const r1_health_u8_history *spo2,
    const r1_health_u8_history *temperature,
    const r1_health_u8_history *stress,
    const r1_health_u16_history *hrv, r1_health_db_record *record);
r1_error r1_health_db_restore_record(
    const r1_health_db_record *record, r1_activity_history *activity,
    r1_health_u8_history *heart_rate,
    r1_health_u8_history *spo2, r1_health_u8_history *temperature,
    r1_health_u8_history *stress, r1_health_u16_history *hrv,
    r1_health_db_restore_result *result);

r1_error r1_health_db_startup(
    const uint8_t schema_payload_bytes[R1_HEALTH_DB_SCHEMA_COUNT],
    const r1_health_db_startup_ops *ops,
    r1_health_crash_record *crash_record,
    r1_activity_history *activity,
    r1_health_u8_history *heart_rate,
    r1_health_u8_accumulator *heart_rate_accumulator,
    r1_health_u8_history *spo2,
    r1_health_u16_history *hrv,
    r1_health_db_startup_result *result);

#endif
