#ifndef OPENR1_R1_HEALTH_H
#define OPENR1_R1_HEALTH_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"

#define R1_HEALTH_HOURLY_SLOTS 24u
#define R1_ACTIVITY_BUCKETS 144u
#define R1_HEALTH_DAILY_U8_MAX_BYTES 108u
#define R1_HEALTH_DAILY_U16_MAX_BYTES 181u
#define R1_ACTIVITY_DAILY_MAX_BYTES 1015u
#define R1_ACTIVITY_OFFLINE_CAPACITY 144u
#define R1_HEALTH_OFFLINE_CAPACITY 24u
#define R1_SLEEP_SESSION_MAX 16u
#define R1_SLEEP_COMPACT_STAGE_MAX 200u
#define R1_SLEEP_STORED_MAX_BYTES 232u
#define R1_SLEEP_PAYLOAD_MAX_BYTES 632u
#define R1_SLEEP_VALIDATED_MIN_DURATION_SECONDS UINT32_C(3600)
#define R1_SLEEP_STORAGE_EVENT UINT16_C(0x2000)
#define R1_SLEEP_AUTOMATIC_SYNC_TRIGGER UINT8_C(6)
#define R1_PENDING_ACK_CAPACITY 32u
#define R1_HRV_RR_INTERVAL_MAX 100u
#define R1_HEALTH_AUTO_SYNC_INTERVAL_SECONDS UINT32_C(10800)
#define R1_HEALTH_AUTO_SYNC_SERIAL UINT8_C(0)
#define R1_HEALTH_LEGACY_CLOCK_CUTOFF UINT32_C(946080000)
#define R1_ACTIVITY_LEGACY_CLOCK_CUTOFF R1_HEALTH_LEGACY_CLOCK_CUTOFF
#define R1_ACTIVITY_BUCKETS_PER_HOUR 6u
#define R1_HEALTH_TIME_MATERIAL_CHANGE_SECONDS UINT32_C(31)
#define R1_HEALTH_GOMORE_REINITIALIZE_SECONDS UINT32_C(180)
#define R1_HEALTH_DATABASE_FORMAT_SECONDS UINT32_C(3600)
#define R1_HEALTH_SECONDS_PER_DAY UINT32_C(86400)
#define R1_HEALTH_DAILY_CACHE_FAMILY_COUNT 6u
#define R1_TEMPERATURE_PAIR_SAMPLE_COUNT 10u
#define R1_TEMPERATURE_PAIR_SENSOR_COUNT 2u
#define R1_TEMPERATURE_PUBLISHED_MIN UINT16_C(250)
#define R1_TEMPERATURE_PUBLISHED_MAX UINT16_C(500)
#define R1_TEMPERATURE_STORAGE_BASE UINT16_C(250)
#define R1_STRESS_VALUE_MAX UINT8_C(100)
#define R1_HEART_RATE_VALUE_MIN UINT8_C(40)
#define R1_HEART_RATE_VALUE_MAX UINT8_C(220)
#define R1_SPO2_VALUE_MIN UINT8_C(70)
#define R1_HEALTH_NOTIFICATION_HEART_RATE UINT8_C(0)
#define R1_HEALTH_NOTIFICATION_SPO2 UINT8_C(1)
#define R1_HEALTH_NOTIFICATION_HRV UINT8_C(5)
#define R1_HEALTH_HISTORY_EVENT_BYTES 8u
#define R1_ACTIVITY_DELTA_EVENT_BYTES 12u
#define R1_ACTIVITY_WINDOW_SECONDS UINT32_C(600)
#define R1_ACTIVITY_WINDOW_PUBLISH_START_SECONDS UINT32_C(595)
#define R1_ACTIVITY_TRANSITION_GRACE_SECONDS UINT32_C(900)
#define R1_HEALTH_CRASH_MAGIC UINT32_C(0x5a5a5a5a)
#define R1_HEALTH_CRASH_BLOB_BYTES 896u
#define R1_HEALTH_CRASH_SNAPSHOT_BYTES 52u
#define R1_HEALTH_CRASH_BLOB_OFFSET 12u
#define R1_HEALTH_CRASH_BLOB_MAGIC_OFFSET 908u
#define R1_HEALTH_CRASH_SNAPSHOT_OFFSET 912u
#define R1_HEALTH_CRASH_RECORD_CRC_OFFSET 964u
#define R1_HEALTH_CRASH_RECORD_BYTES 966u
#define R1_HEALTH_CRASH_FLAG_HEART_RATE UINT8_C(0x01)
#define R1_HEALTH_CRASH_FLAG_SPO2 UINT8_C(0x02)
#define R1_HEALTH_CRASH_FLAG_HRV UINT8_C(0x04)
#define R1_HEALTH_CRASH_FLAG_ACTIVITY UINT8_C(0x08)

typedef struct {
    uint8_t average;
    uint8_t maximum;
    uint8_t minimum;
    uint16_t sample_count;
    uint32_t sum;
} r1_health_u8_slot;

typedef struct {
    uint16_t average;
    uint16_t maximum;
    uint16_t minimum;
    uint16_t sample_count;
    uint32_t sum;
} r1_health_u16_slot;

typedef struct {
    int16_t utc_offset_minutes;
    uint32_t local_day_start;
    uint32_t latest_timestamp;
    uint8_t latest_value;
    bool has_latest;
    r1_health_u8_slot slots[R1_HEALTH_HOURLY_SLOTS];
} r1_health_u8_history;

typedef struct {
    int16_t utc_offset_minutes;
    uint32_t local_day_start;
    uint32_t latest_timestamp;
    uint16_t latest_value;
    bool has_latest;
    r1_health_u16_slot slots[R1_HEALTH_HOURLY_SLOTS];
} r1_health_u16_history;

/* Exact logical fields of one eight-byte shared hourly-average accumulator.
 * Every metric owns a distinct instance; the caller supplies the instance so
 * this clean model never reaches into private SRAM. */
typedef struct {
    uint8_t hour;
    uint8_t reserved;
    uint16_t sample_count;
    uint32_t sum;
} r1_health_u8_accumulator;

/* The recovered UInt8 and UInt16 metric paths share the same eight-byte
 * accumulator geometry. The aliases keep value-width intent explicit. */
typedef r1_health_u8_accumulator r1_health_u16_accumulator;

typedef enum {
    R1_HEALTH_U8_SAMPLE_STORED = 0,
    R1_HEALTH_U8_SAMPLE_REJECTED_RANGE
} r1_health_u8_sample_action;

typedef struct {
    r1_health_u8_sample_action action;
    uint16_t published_value;
    uint8_t stored_value;
    uint32_t effective_timestamp;
    bool timestamp_replaced;
    bool notification_requested;
    uint8_t notification_metric;
} r1_health_u8_sample_result;

typedef struct {
    r1_health_u8_sample_action action;
    uint16_t stored_value;
    uint32_t effective_timestamp;
    bool timestamp_replaced;
    bool notification_requested;
    uint8_t notification_metric;
} r1_health_u16_sample_result;

typedef enum {
    R1_HEALTH_HISTORY_HEART_RATE_DAILY = 0,
    R1_HEALTH_HISTORY_HEART_RATE_POINT,
    R1_HEALTH_HISTORY_SPO2_DAILY,
    R1_HEALTH_HISTORY_SPO2_POINT,
    R1_HEALTH_HISTORY_HRV_DAILY,
    R1_HEALTH_HISTORY_HRV_POINT,
    R1_HEALTH_HISTORY_ACTIVITY_DAILY,
    R1_HEALTH_HISTORY_ACTIVITY_REFRESH,
    R1_HEALTH_HISTORY_SLEEP_DAILY
} r1_health_history_action;

/* Exact event-14 record. dispatcher_residue is deterministic binary-search
 * residue from the recovered ABI; the consumer does not use it. */
typedef struct {
    r1_health_history_action action;
    uint8_t metric;
    uint8_t query_kind;
    uint16_t request_serial;
    uint32_t dispatcher_residue;
    bool immediate_empty_response;
} r1_health_history_route;

typedef struct {
    uint16_t steps;
    uint16_t active_kilocalories;
    uint16_t all_kilocalories;
    bool valid;
} r1_activity_bucket;

typedef struct {
    int16_t utc_offset_minutes;
    uint32_t local_day_start;
    uint32_t latest_timestamp;
    int32_t total_steps;
    int16_t total_kilocalories;
    r1_activity_bucket buckets[R1_ACTIVITY_BUCKETS];
} r1_activity_history;

typedef enum {
    R1_TEMPERATURE_CALIBRATION_SUBTRACT = 0,
    R1_TEMPERATURE_CALIBRATION_ADD = 1,
    R1_TEMPERATURE_CALIBRATION_DISABLED = 0xff
} r1_temperature_calibration_direction;

typedef struct {
    r1_temperature_calibration_direction direction;
    int16_t offset;
} r1_temperature_channel_calibration;

typedef struct {
    r1_temperature_channel_calibration
        channels[R1_TEMPERATURE_PAIR_SENSOR_COUNT];
} r1_temperature_pair_calibration;

typedef struct {
    uint8_t sensor_count;
    int16_t channels[R1_TEMPERATURE_PAIR_SENSOR_COUNT];
} r1_temperature_pair_result;

/* Provider-facing actions are returned to the platform instead of invoking
 * FlashDB, sleep, or licensed health-algorithm code from the clean model. */
typedef struct {
    bool clear_timeseries_database;
    bool clear_sleep_history;
    bool reset_algorithm_aggregate;
    size_t cache_families_reset;
} r1_health_clear_all_result;

typedef struct {
    uint32_t timestamp_seconds;
    uint8_t enabled;
    uint8_t reserved[7];
} r1_health_settings_record;

typedef struct {
    bool write_command;
    bool response_requested;
    bool acknowledgement_precedes_effects;
    bool raw_transition_observed;
    bool persistent_update_requested;
    bool private_event_publish_requested;
    uint8_t private_event_value;
    r1_health_settings_record response;
    r1_health_settings_record persistent_record;
} r1_health_settings_command_plan;

/* Exact 52-byte product-owned health summary embedded at offset 0x390 in the
 * recovered crash record. Sensor production and wall-clock acquisition remain
 * provider inputs; this structure contains only cache composition. */
typedef struct {
    uint32_t heart_rate_latest_timestamp;
    uint32_t heart_rate_accumulator_sum;
    uint32_t spo2_latest_timestamp;
    uint32_t hrv_latest_timestamp;
    uint32_t activity_packed_words[R1_ACTIVITY_BUCKETS_PER_HOUR];
    uint16_t heart_rate_accumulator_count;
    uint16_t hrv_latest_value;
    uint8_t local_hour;
    uint8_t available_flags;
    uint8_t heart_rate_average;
    uint8_t heart_rate_maximum;
    uint8_t heart_rate_minimum;
    uint8_t heart_rate_latest_value;
    uint8_t spo2_latest_value;
    uint8_t reserved;
} r1_health_crash_snapshot;

/* The complete retained record is 966 bytes and therefore intentionally uses
 * a byte representation rather than acquiring ABI tail padding. */
typedef struct {
    uint8_t bytes[R1_HEALTH_CRASH_RECORD_BYTES];
} r1_health_crash_record;

typedef struct {
    uint32_t utc_timestamp;
    int16_t utc_offset_minutes;
    bool clock_valid;
} r1_health_crash_time;

typedef enum {
    R1_HEALTH_CRASH_RESTORED = 0,
    R1_HEALTH_CRASH_NO_MAGIC,
    R1_HEALTH_CRASH_INVALID_OR_EMPTY
} r1_health_crash_restore_action;

typedef struct {
    r1_health_crash_restore_action action;
    uint8_t local_hour;
    uint8_t available_flags;
    size_t activity_bucket_count;
    bool heart_rate_applied;
    bool heart_rate_accumulator_applied;
    bool spo2_applied;
    bool hrv_applied;
    bool snapshot_cleared;
} r1_health_crash_restore_result;

/* Provider output accepted by the clean-room R1 activity service. The motion
 * classifier and energy/step algorithms remain licensed-provider boundaries. */
typedef struct {
    uint32_t steps;
    uint16_t all_kilocalories;
    uint16_t active_kilocalories;
} r1_activity_cumulative_counters;

/* Exact logical 24-byte state used by the recovered activity-window service. */
typedef struct {
    uint8_t window_published;
    uint8_t transition_pending;
    uint16_t reserved;
    uint32_t transition_started;
    r1_activity_cumulative_counters baseline;
    r1_activity_cumulative_counters current;
} r1_activity_accumulator;

/* Exact event-11 payload before wire encoding. */
typedef struct {
    uint16_t all_kilocalories;
    uint16_t active_kilocalories;
    uint16_t steps;
    uint16_t duration_seconds;
    uint32_t timestamp;
} r1_activity_delta_event;

typedef enum {
    R1_ACTIVITY_ACCUMULATOR_EVENT_READY = 0,
    R1_ACTIVITY_ACCUMULATOR_EARLY_WINDOW,
    R1_ACTIVITY_ACCUMULATOR_WINDOW_ALREADY_PUBLISHED,
    R1_ACTIVITY_ACCUMULATOR_REBASED_DAY_START,
    R1_ACTIVITY_ACCUMULATOR_REBASED_COUNTER_ROLLBACK,
    R1_ACTIVITY_ACCUMULATOR_REBASED_UNAVAILABLE,
    R1_ACTIVITY_ACCUMULATOR_TRANSITION_GRACE,
    R1_ACTIVITY_ACCUMULATOR_REBASED_TRANSITION_TIMEOUT
} r1_activity_accumulator_action;

typedef struct {
    r1_activity_accumulator_action action;
    bool event_ready;
    r1_activity_delta_event event;
} r1_activity_accumulator_result;

typedef r1_error (*r1_activity_bucket_resolver_fn)(
    void *context, uint32_t timestamp, uint8_t *bucket_index);

typedef struct {
    uint8_t start_bucket;
    uint8_t end_bucket;
    bool crossed_bucket_boundary;
    uint16_t stored_steps;
    uint16_t stored_active_kilocalories;
    uint16_t stored_all_kilocalories;
} r1_activity_delta_consume_result;

/* Exact 16-byte activity_unsynced_cache record. The reserved tail is retained
 * on enqueue, matching the recovered ring-buffer storage behavior. */
typedef struct {
    uint32_t packed_word;
    uint32_t local_day_start;
    uint32_t recorded_timestamp;
    int16_t utc_offset_minutes;
    uint8_t bucket_index;
    uint8_t reserved_tail;
} r1_activity_offline_entry;

typedef struct {
    r1_activity_offline_entry entries[R1_ACTIVITY_OFFLINE_CAPACITY];
    uint8_t read_index;
    uint8_t write_index;
    uint8_t count;
} r1_activity_offline_queue;

typedef enum {
    R1_ACTIVITY_OFFLINE_ENQUEUED = 0,
    R1_ACTIVITY_OFFLINE_DROPPED_ZERO,
    R1_ACTIVITY_OFFLINE_DROPPED_FUTURE_RECORDED,
    R1_ACTIVITY_OFFLINE_DROPPED_FUTURE_DAY
} r1_activity_offline_enqueue_action;

typedef struct {
    r1_activity_offline_enqueue_action action;
    bool overwrote_oldest;
} r1_activity_offline_enqueue_result;

typedef enum {
    R1_ACTIVITY_FLASH_RECORD_ACCEPTED = 0,
    R1_ACTIVITY_FLASH_RECORD_IGNORED_HOUR,
    R1_ACTIVITY_FLASH_RECORD_IGNORED_MAXIMUM_TIMESTAMP,
    R1_ACTIVITY_FLASH_RECORD_IGNORED_FUTURE_RECORDED,
    R1_ACTIVITY_FLASH_RECORD_IGNORED_FUTURE_DAY
} r1_activity_flash_record_action;

typedef struct {
    r1_activity_flash_record_action action;
    size_t attempted_count;
    size_t enqueued_count;
    size_t dropped_count;
    size_t overwritten_count;
} r1_activity_flash_record_enqueue_result;

typedef struct {
    r1_activity_history history;
    uint32_t maximum_recorded_timestamp;
    uint16_t serial;
    uint8_t mode;
    bool acknowledgement_requested;
} r1_activity_offline_packet;

typedef struct {
    size_t packet_count;
    size_t skipped_zero_count;
    size_t skipped_future_count;
} r1_activity_offline_merge_result;

typedef r1_error (*r1_activity_offline_emit_fn)(
    void *context, const r1_activity_offline_packet *packet);

typedef struct {
    int16_t utc_offset_minutes;
    uint32_t recorded_timestamp;
    uint32_t packed_words[R1_ACTIVITY_BUCKETS_PER_HOUR];
} r1_activity_flash_record;

typedef struct {
    bool emitted;
    bool dropped_future_acknowledgement;
    size_t encoded_length;
} r1_activity_day_flush_result;

typedef enum {
    R1_ACTIVITY_ACK_FLASH_HISTORY = 0,
    R1_ACTIVITY_ACK_OFFLINE_QUEUE = 1,
    R1_ACTIVITY_ACK_CURRENT_RAM = 2
} r1_activity_ack_mode;

typedef struct {
    uint8_t mode;
    bool firmware_clock_sampled;
    bool timestamp_was_future;
    bool last_sync_updated;
    size_t consumed_count;
} r1_activity_ack_result;

typedef enum {
    R1_ACTIVITY_CACHE_RETURNED_CLOCK_VALID = 0,
    R1_ACTIVITY_CACHE_RETURNED_ABOVE_LEGACY_CUTOFF,
    R1_ACTIVITY_CACHE_RETURNED_ALL_ZERO,
    R1_ACTIVITY_CACHE_REDACTED_OFFSET_BEFORE_HOUR,
    R1_ACTIVITY_CACHE_REDACTED_BACKWARD_CLOCK,
    R1_ACTIVITY_CACHE_QUEUED_AND_REDACTED,
    R1_ACTIVITY_CACHE_QUEUE_REJECTED_AND_REDACTED
} r1_activity_cache_read_disposition;

typedef struct {
    r1_activity_cache_read_disposition disposition;
    r1_activity_bucket returned[R1_ACTIVITY_BUCKETS_PER_HOUR];
    bool has_unsigned_offset_hours;
    uint16_t unsigned_offset_hours;
    bool has_adjusted_hour;
    uint8_t adjusted_hour;
    size_t enqueue_count;
} r1_activity_cache_read_result;

/* Exact 16-byte HR/SpO2 offline record. Bytes 3 and 15 are retained when a
 * physical ring slot is reused because the recovered enqueue paths do not
 * initialize them. */
typedef struct {
    uint8_t average;
    uint8_t maximum;
    uint8_t minimum;
    uint8_t reserved_after_aggregate;
    uint32_t local_day_start;
    uint32_t recorded_timestamp;
    int16_t utc_offset_minutes;
    uint8_t hour_index;
    uint8_t reserved_tail;
} r1_health_u8_offline_entry;

typedef struct {
    r1_health_u8_offline_entry entries[R1_HEALTH_OFFLINE_CAPACITY];
    uint8_t read_index;
    uint8_t write_index;
    uint8_t count;
} r1_health_u8_offline_queue;

/* Exact 20-byte HRV offline record. Bytes 6..7 and 19 are retained on reuse. */
typedef struct {
    uint16_t average;
    uint16_t maximum;
    uint16_t minimum;
    uint8_t reserved_after_aggregate[2];
    uint32_t local_day_start;
    uint32_t recorded_timestamp;
    int16_t utc_offset_minutes;
    uint8_t hour_index;
    uint8_t reserved_tail;
} r1_health_u16_offline_entry;

typedef struct {
    r1_health_u16_offline_entry entries[R1_HEALTH_OFFLINE_CAPACITY];
    uint8_t read_index;
    uint8_t write_index;
    uint8_t count;
} r1_health_u16_offline_queue;

typedef enum {
    R1_HEALTH_OFFLINE_ENQUEUED = 0,
    R1_HEALTH_OFFLINE_DROPPED_ZERO,
    R1_HEALTH_OFFLINE_DROPPED_FUTURE_RECORDED,
    R1_HEALTH_OFFLINE_DROPPED_FUTURE_DAY
} r1_health_offline_enqueue_action;

typedef struct {
    r1_health_offline_enqueue_action action;
    bool overwrote_oldest;
} r1_health_offline_enqueue_result;

typedef enum {
    R1_HEALTH_CACHE_RETURNED_CLOCK_VALID = 0,
    R1_HEALTH_CACHE_RETURNED_ABOVE_LEGACY_CUTOFF,
    R1_HEALTH_CACHE_RETURNED_ZERO_AVERAGE,
    R1_HEALTH_CACHE_REDACTED_OFFSET_BEFORE_HOUR,
    R1_HEALTH_CACHE_REDACTED_BACKWARD_CLOCK,
    R1_HEALTH_CACHE_QUEUED_AND_REDACTED,
    R1_HEALTH_CACHE_QUEUE_REJECTED_AND_REDACTED,
    R1_HEALTH_CACHE_REDACTED_EARLY_CLOCK
} r1_health_cache_read_disposition;

typedef struct {
    r1_health_cache_read_disposition disposition;
    r1_health_u8_slot copied;
    r1_health_u8_slot returned;
    bool has_unsigned_offset_hours;
    uint16_t unsigned_offset_hours;
    bool has_adjusted_hour;
    uint8_t adjusted_hour;
    bool has_enqueue_result;
    r1_health_offline_enqueue_result enqueue;
} r1_health_u8_cache_read_result;

typedef struct {
    r1_health_cache_read_disposition disposition;
    r1_health_u16_slot copied;
    r1_health_u16_slot returned;
    bool has_unsigned_offset_hours;
    uint16_t unsigned_offset_hours;
    bool has_adjusted_hour;
    uint8_t adjusted_hour;
    bool has_enqueue_result;
    r1_health_offline_enqueue_result enqueue;
} r1_health_u16_cache_read_result;

typedef struct {
    r1_health_u8_history history;
    uint32_t maximum_recorded_timestamp;
} r1_health_u8_offline_packet;

/* Normalized fields consumed by the recovered HR/SpO2 FlashDB iterator
 * callbacks. FlashDB owns the 128-byte blob and the time provider owns local
 * calendar conversion; this clean-room record begins at their typed seam. */
typedef struct {
    int16_t utc_offset_minutes;
    uint32_t recorded_timestamp;
    uint8_t local_hour;
    uint8_t local_minute;
    uint8_t local_second;
    uint8_t average;
    uint8_t maximum;
    uint8_t minimum;
} r1_health_u8_flash_record;

typedef struct {
    bool emitted;
    bool dropped_future_acknowledgement;
    size_t encoded_length;
} r1_health_u8_day_flush_result;

/* UInt8 and UInt16 day packets report the same transport-neutral outcome. */
typedef r1_health_u8_day_flush_result r1_health_u16_day_flush_result;

typedef struct {
    r1_health_u16_history history;
    uint32_t maximum_recorded_timestamp;
} r1_health_u16_offline_packet;

typedef struct {
    size_t packet_count;
    size_t skipped_zero_count;
    size_t skipped_future_count;
} r1_health_offline_merge_result;

typedef r1_error (*r1_health_u8_offline_emit_fn)(
    void *context, const r1_health_u8_offline_packet *packet);
typedef r1_error (*r1_health_u16_offline_emit_fn)(
    void *context, const r1_health_u16_offline_packet *packet);

typedef enum {
    R1_HEALTH_ACK_FLASH_HISTORY = 0,
    R1_HEALTH_ACK_OFFLINE_QUEUE = 1,
    R1_HEALTH_ACK_CURRENT_RAM = 2
} r1_health_ack_mode;

typedef struct {
    uint8_t mode;
    bool firmware_clock_sampled;
    bool timestamp_was_future;
    bool last_sync_updated;
    size_t consumed_count;
} r1_health_offline_ack_result;

typedef struct {
    uint8_t type;
    uint16_t half_minutes;
} r1_sleep_stage;

typedef struct {
    uint8_t type;
    uint8_t efficiency;
    uint8_t score;
    uint8_t reserved_header;
    uint8_t wake_ratio;
    uint8_t rem_ratio;
    uint8_t light_ratio;
    uint8_t deep_ratio;
    uint16_t body_temperature_raw;
    int16_t utc_offset_minutes;
    uint32_t start_timestamp;
    uint32_t end_timestamp;
    uint16_t total_minutes;
    uint16_t wake_minutes;
    uint16_t rem_minutes;
    uint16_t light_minutes;
    uint16_t deep_minutes;
    uint16_t stage_count;
    r1_sleep_stage stages[R1_SLEEP_COMPACT_STAGE_MAX];
    bool synchronized;
    bool has_storage_record;
    uint32_t storage_header_offset;
} r1_sleep_session;

typedef enum {
    R1_SLEEP_VALIDATED_DROP_TOO_SHORT = 0,
    R1_SLEEP_VALIDATED_POST_STORAGE_EVENT = 1
} r1_sleep_validated_route;

typedef struct {
    r1_sleep_validated_route route;
    uint32_t wrapping_duration_seconds;
    bool timestamp_wrapped;
    uint16_t storage_event;
    uint16_t event_payload_length;
    bool direct_fallback_on_post_failure;
} r1_sleep_validated_delivery_plan;

typedef struct {
    bool consume_record;
    bool request_automatic_sync;
    uint8_t automatic_sync_argument;
} r1_sleep_storage_consumer_plan;

typedef r1_error (*r1_sleep_sync_commit_fn)(void *context,
                                            const r1_sleep_session *session);

typedef struct {
    r1_sleep_session sessions[R1_SLEEP_SESSION_MAX];
    uint8_t read_index;
    uint8_t count;
} r1_sleep_history;

typedef enum {
    R1_PENDING_GENERIC = 0,
    R1_PENDING_SLEEP_SESSION = 1
} r1_pending_kind;

typedef struct {
    bool active;
    uint8_t module;
    uint8_t command;
    uint8_t subcommand;
    uint16_t serial;
    r1_pending_kind kind;
    uint8_t record_index;
} r1_pending_ack;

typedef struct {
    uint8_t validity[R1_HRV_RR_INTERVAL_MAX];
    uint16_t differences[R1_HRV_RR_INTERVAL_MAX - 1u];
    size_t interval_count;
    size_t difference_count;
    float squared_sum;
    float mean_squared;
    float rmssd;
    bool has_result;
} r1_hrv_rmssd_result;

typedef struct {
    bool published;
    uint32_t converted;
    uint16_t transmitted;
    uint8_t payload[8];
} r1_hrv_publication;

typedef struct {
    uint16_t physical_buffer[R1_HRV_RR_INTERVAL_MAX];
    uint16_t write_index;
    uint16_t buffered_count;
    uint16_t nonzero_count;
    uint16_t callback_count;
} r1_hrv_producer;

typedef struct {
    bool subscription_active;
    bool timed_window_active;
    uint8_t timed_window_completed;
} r1_hrv_producer_session;

typedef enum {
    R1_HRV_WARMUP_IGNORED = 0,
    R1_HRV_ACCUMULATING,
    R1_HRV_BELOW_THRESHOLD,
    R1_HRV_FAILED_RESET,
    R1_HRV_FAILED_TIMED_RETRY,
    R1_HRV_PUBLISHED_RESET
} r1_hrv_producer_action;

typedef struct {
    r1_hrv_producer_action action;
    bool eligibility_checked;
    r1_hrv_rmssd_result calculation;
    r1_hrv_publication publication;
} r1_hrv_producer_result;

typedef struct {
    uint8_t mode;
    bool transition_pending;
    bool timeout_pending;
    bool health_enabled;
    bool timing_allowed;
    bool timeout_exists;
    bool stream_registration_exists;
    bool hourly_request;
    uint32_t current_timestamp;
} r1_hrv_timing_observation;

typedef enum {
    R1_HRV_TIMING_START = 0,
    R1_HRV_TIMING_INACTIVE,
    R1_HRV_TIMING_TRANSITION_PENDING,
    R1_HRV_TIMING_HEALTH_DISABLED,
    R1_HRV_TIMING_NOT_ALLOWED,
    R1_HRV_TIMING_ALREADY_ACTIVE,
    R1_HRV_TIMING_CATCHUP_TOO_CLOSE_TO_HOUR
} r1_hrv_timing_action;

typedef struct {
    r1_hrv_timing_action action;
    uint32_t delay_seconds;
    uint32_t timeout_milliseconds;
    size_t workspace_clear_bytes;
    bool create_one_shot_timeout;
    bool register_sensor_stream_after_timeout_create;
    bool delete_timeout_on_registration_failure;
} r1_hrv_timing_plan;

typedef enum {
    R1_HEALTH_SYNC_HEART_RATE = 0,
    R1_HEALTH_SYNC_BLOOD_OXYGEN,
    R1_HEALTH_SYNC_HEART_RATE_VARIABILITY,
    R1_HEALTH_SYNC_ACTIVITY,
    R1_HEALTH_SYNC_UNSYNCHRONIZED_SLEEP
} r1_health_auto_sync_leg;

typedef enum {
    R1_HEALTH_AUTO_SYNC_INVALID = 0,
    R1_HEALTH_AUTO_SYNC_PHONE_DISCONNECTED,
    R1_HEALTH_AUTO_SYNC_INITIAL,
    R1_HEALTH_AUTO_SYNC_CLOCK_REWIND,
    R1_HEALTH_AUTO_SYNC_COOLDOWN_ACTIVE,
    R1_HEALTH_AUTO_SYNC_COOLDOWN_ELAPSED
} r1_health_auto_sync_action;

typedef void (*r1_health_auto_sync_emit_fn)(
    void *context, r1_health_auto_sync_leg leg, uint8_t serial);

typedef struct {
    r1_health_auto_sync_action action;
    bool batch_started;
    bool has_elapsed_seconds;
    uint32_t elapsed_seconds;
} r1_health_auto_sync_result;

typedef struct {
    int16_t old_utc_offset_minutes;
    int16_t new_utc_offset_minutes;
    uint32_t old_timestamp_seconds;
    uint32_t new_timestamp_seconds;
} r1_health_time_transition;

/* Exact six-word hsync record. Only four fields have recovered metric owners;
 * the two unresolved words are deliberately preserved by reconciliation. */
typedef struct {
    uint32_t heart_rate_timestamp;
    uint32_t blood_oxygen_timestamp;
    uint32_t unresolved_offset_8;
    uint32_t heart_rate_variability_timestamp;
    uint32_t activity_timestamp;
    uint32_t unresolved_offset_20;
} r1_health_sync_cursor_state;

typedef struct {
    bool clock_update_attempted;
    bool subscriber_broadcast_requested;
    bool old_timestamp_valid;
    bool new_timestamp_valid;
    uint32_t absolute_delta_seconds;
    uint32_t backward_delta_seconds;
    int64_t old_local_day_index;
    int64_t new_local_day_index;
    bool gomore_reinitialization_requested;
    bool health_database_format_requested;
    bool current_day_recovery_requested;
    bool daily_cache_reset_requested;
    uint8_t daily_cache_family_count;
    bool known_cursor_reset_requested;
    bool known_cursor_clamp_pass_requested;
    uint8_t known_cursor_clamped_count;
} r1_health_time_transition_result;

typedef struct {
    uint8_t current_local_hour;
    bool hrv_eligibility_evaluation_requested;
    bool blood_oxygen_eligibility_evaluation_requested;
    bool database_writer_accepts_hour;
    bool has_appended_aggregate_hour;
    uint8_t appended_aggregate_hour;
    bool daily_cache_reset_requested;
    uint8_t daily_cache_family_count;
    bool midnight_followup_requested;
    bool midnight_followup_has_subscriber;
} r1_health_hour_boundary_result;

typedef struct {
    r1_health_u8_history heart_rate;
    r1_health_u8_history blood_oxygen;
    r1_health_u16_history heart_rate_variability;
    r1_health_u8_offline_queue heart_rate_offline;
    r1_health_u8_offline_queue blood_oxygen_offline;
    r1_health_u16_offline_queue heart_rate_variability_offline;
    uint32_t heart_rate_last_sync_seconds;
    uint32_t blood_oxygen_last_sync_seconds;
    uint32_t heart_rate_variability_last_sync_seconds;
    r1_activity_accumulator activity_accumulator;
    r1_activity_history activity;
    r1_activity_offline_queue activity_offline;
    uint32_t activity_last_sync_seconds;
    r1_sleep_history sleep;
    uint16_t next_notification_serial;
    uint32_t last_auto_sync_or_query_seconds;
    r1_pending_ack pending[R1_PENDING_ACK_CAPACITY];
    r1_sleep_sync_commit_fn sleep_sync_commit;
    void *sleep_sync_context;
} r1_health_state;

void r1_health_initialize(r1_health_state *state);
r1_error r1_health_record_u8(r1_health_u8_history *history, uint8_t hour,
                             uint8_t value, uint32_t timestamp,
                             uint32_t local_day_start, int16_t utc_offset_minutes);
r1_error r1_health_record_u16(r1_health_u16_history *history, uint8_t hour,
                              uint16_t value, uint32_t timestamp,
                              uint32_t local_day_start, int16_t utc_offset_minutes);
r1_error r1_health_u8_accumulate_average(
    r1_health_u8_accumulator *accumulator, uint8_t hour, uint8_t value,
    uint8_t *average);
r1_error r1_health_u16_accumulate_average(
    r1_health_u16_accumulator *accumulator, uint8_t hour, uint16_t value,
    uint16_t *average);
void r1_health_accumulator_snapshot(
    const r1_health_u8_accumulator *accumulator, uint8_t hour,
    uint32_t *sum, uint16_t *sample_count);
void r1_health_accumulator_restore(
    r1_health_u8_accumulator *accumulator, uint8_t hour,
    uint32_t sum, uint16_t sample_count);
r1_error r1_health_build_crash_snapshot(
    r1_health_crash_snapshot *snapshot, uint32_t utc_timestamp,
    int16_t utc_offset_minutes, const r1_activity_history *activity,
    const r1_health_u8_history *heart_rate,
    const r1_health_u8_accumulator *heart_rate_accumulator,
    const r1_health_u8_history *spo2,
    const r1_health_u16_history *hrv);
bool r1_health_crash_record_valid(const r1_health_crash_record *record);
bool r1_health_crash_record_has_magic(const r1_health_crash_record *record);
r1_error r1_health_crash_record_clear_provider_blob(
    r1_health_crash_record *record);
r1_error r1_health_crash_record_clear_snapshot(
    r1_health_crash_record *record);
r1_error r1_health_crash_record_clear_time(
    r1_health_crash_record *record);
bool r1_health_crash_record_get_provider_blob(
    const r1_health_crash_record *record, const uint8_t **provider_blob,
    size_t *provider_blob_length);
bool r1_health_crash_record_get_snapshot(
    const r1_health_crash_record *record,
    r1_health_crash_snapshot *snapshot);
bool r1_health_crash_record_get_time(
    const r1_health_crash_record *record, r1_health_crash_time *time);
r1_error r1_health_crash_record_initialize(
    r1_health_crash_record *record, uint16_t time_status_flags,
    bool clock_valid, uint32_t utc_timestamp, int16_t utc_offset_minutes,
    const uint8_t *provider_blob, size_t provider_blob_length,
    const r1_activity_history *activity,
    const r1_health_u8_history *heart_rate,
    const r1_health_u8_accumulator *heart_rate_accumulator,
    const r1_health_u8_history *spo2,
    const r1_health_u16_history *hrv, bool *provider_blob_copied);
r1_error r1_health_crash_record_restore(
    r1_health_crash_record *record, r1_activity_history *activity,
    r1_health_u8_history *heart_rate,
    r1_health_u8_accumulator *heart_rate_accumulator,
    r1_health_u8_history *spo2, r1_health_u16_history *hrv,
    r1_health_crash_restore_result *result);
bool r1_health_u8_latest_sample(
    const r1_health_u8_history *history, uint8_t *value,
    uint32_t *timestamp);
bool r1_health_u16_latest_sample(
    const r1_health_u16_history *history, uint16_t *value,
    uint32_t *timestamp);
r1_error r1_heart_rate_store_sample(
    r1_health_u8_history *history, r1_health_u8_accumulator *accumulator,
    uint8_t value, uint32_t event_timestamp, uint32_t firmware_timestamp,
    uint8_t aggregate_hour, uint8_t average_hour,
    r1_health_u8_sample_result *result);
r1_error r1_spo2_store_sample(
    r1_health_u8_history *history, r1_health_u8_accumulator *accumulator,
    uint8_t value, uint32_t event_timestamp, uint32_t firmware_timestamp,
    uint8_t aggregate_hour, uint8_t average_hour,
    r1_health_u8_sample_result *result);
r1_error r1_hrv_store_sample(
    r1_health_u16_history *history, r1_health_u16_accumulator *accumulator,
    uint16_t rmssd, uint32_t event_timestamp, uint32_t firmware_timestamp,
    uint8_t aggregate_hour, uint8_t average_hour,
    r1_health_u16_sample_result *result);
r1_error r1_health_history_route_command(
    uint8_t command, uint8_t subcommand, uint16_t request_serial,
    r1_health_history_route *route);
r1_error r1_health_history_encode_event14(
    const r1_health_history_route *route,
    uint8_t output[R1_HEALTH_HISTORY_EVENT_BYTES]);
r1_error r1_health_history_decode_event14(
    const uint8_t *input, size_t length, r1_health_history_route *route);
r1_error r1_temperature_store_sample(
    r1_health_u8_history *history, r1_health_u8_accumulator *accumulator,
    uint16_t published_value, uint32_t firmware_timestamp,
    uint8_t aggregate_hour, uint8_t average_hour,
    r1_health_u8_sample_result *result);
r1_error r1_stress_store_sample(
    r1_health_u8_history *history, r1_health_u8_accumulator *accumulator,
    uint8_t value, uint32_t firmware_timestamp,
    uint8_t aggregate_hour, uint8_t average_hour,
    r1_health_u8_sample_result *result);
r1_error r1_activity_record(r1_activity_history *history, uint8_t ten_minute_bucket,
                            uint16_t steps, uint16_t active_kilocalories,
                            uint16_t all_kilocalories, uint32_t timestamp,
                            uint32_t local_day_start, int16_t utc_offset_minutes);
void r1_activity_accumulator_initialize(r1_activity_accumulator *accumulator);
r1_error r1_activity_accumulator_periodic(
    r1_activity_accumulator *accumulator,
    const r1_activity_cumulative_counters *current, uint32_t timestamp,
    uint32_t local_day_start, uint8_t sleep_result_status,
    uint8_t wear_fusion_state, r1_activity_accumulator_result *result);
r1_error r1_activity_accumulator_refresh(
    r1_activity_accumulator *accumulator, uint32_t timestamp,
    uint8_t sleep_result_status, uint8_t wear_fusion_state,
    r1_activity_accumulator_result *result);
r1_error r1_activity_accumulator_pending_delta(
    const r1_activity_accumulator *accumulator,
    uint8_t sleep_result_status, uint8_t wear_fusion_state,
    r1_activity_delta_event *event);
r1_error r1_activity_delta_event_encode(
    const r1_activity_delta_event *event,
    uint8_t output[R1_ACTIVITY_DELTA_EVENT_BYTES]);
r1_error r1_activity_delta_event_decode(
    const uint8_t *input, size_t length, r1_activity_delta_event *event);
r1_error r1_activity_consume_delta_event(
    r1_activity_history *history, const r1_activity_delta_event *event,
    r1_activity_bucket_resolver_fn resolve_bucket, void *resolver_context,
    uint32_t local_day_start, int16_t utc_offset_minutes,
    r1_activity_delta_consume_result *result);
r1_error r1_health_encode_daily_u8(const r1_health_u8_history *history,
                                   uint8_t *output, size_t capacity, size_t *written);
r1_error r1_health_encode_daily_u16(const r1_health_u16_history *history,
                                    uint8_t *output, size_t capacity, size_t *written);
r1_error r1_activity_encode_daily(const r1_activity_history *history,
                                  uint8_t *output, size_t capacity, size_t *written);
r1_error r1_activity_encode_all_day(const r1_activity_history *history,
                                    uint8_t *output, size_t capacity, size_t *written);
void r1_activity_offline_initialize(r1_activity_offline_queue *queue);
bool r1_activity_offline_is_empty(const r1_activity_offline_queue *queue);
r1_error r1_activity_offline_enqueue(
    r1_activity_offline_queue *queue, uint32_t packed_word,
    uint32_t local_day_start, uint32_t recorded_timestamp,
    int16_t utc_offset_minutes, uint8_t bucket_index,
    uint32_t firmware_timestamp, r1_activity_offline_enqueue_result *result);
r1_error r1_activity_flash_record_enqueue_plan(
    r1_activity_offline_queue *queue, uint32_t local_day_start,
    int16_t utc_offset_minutes, uint8_t hour,
    const uint32_t packed_words[6], uint32_t recorded_timestamp,
    uint32_t maximum_allowed_timestamp, uint32_t firmware_timestamp,
    r1_activity_flash_record_enqueue_result *result);
r1_error r1_activity_offline_consume_through(
    r1_activity_offline_queue *queue, uint32_t cutoff_timestamp,
    size_t *consumed_count);
r1_error r1_activity_offline_merge(
    const r1_activity_offline_queue *queue, uint32_t firmware_timestamp,
    r1_activity_offline_packet *workspace, r1_activity_offline_emit_fn emit,
    void *emit_context, r1_activity_offline_merge_result *result);
r1_error r1_activity_offline_acknowledge(
    r1_activity_offline_queue *queue, uint8_t mode,
    uint32_t acknowledged_timestamp, uint32_t firmware_timestamp,
    uint32_t *last_sync_timestamp, r1_activity_ack_result *result);
uint32_t r1_activity_clamp_acknowledgement_timestamp(
    uint32_t candidate_timestamp, uint32_t firmware_timestamp);
void r1_activity_day_builder_reset(r1_activity_offline_packet *builder);
r1_error r1_activity_day_builder_flush(
    r1_activity_offline_packet *builder, uint32_t firmware_timestamp,
    r1_activity_offline_emit_fn emit, void *emit_context,
    r1_activity_day_flush_result *result);
r1_error r1_activity_ram_cache_merge(
    r1_activity_offline_packet *builder, r1_activity_history *cache,
    uint32_t requested_day_start, uint32_t window_start,
    uint32_t firmware_timestamp, int16_t current_utc_offset_minutes,
    uint16_t current_steps, uint16_t current_active_kilocalories,
    uint16_t current_all_kilocalories, r1_activity_offline_emit_fn emit,
    void *emit_context, r1_activity_day_flush_result *flush_result);
r1_error r1_activity_flash_record_merge(
    r1_activity_offline_packet *builder,
    const r1_activity_flash_record *record, uint32_t firmware_timestamp,
    bool previous_local_day_only, r1_activity_offline_emit_fn emit,
    void *emit_context, r1_activity_day_flush_result *flush_result);
void r1_activity_cache_reset(r1_activity_history *history,
                             uint32_t local_day_start,
                             int16_t utc_offset_minutes);
/* Recovered service-health clear-all orchestration. Cache pointers may be
 * NULL, matching the stock service's optional cache-provider lookups. */
r1_error r1_health_clear_all_caches(
    bool timeseries_database_available, uint32_t local_day_start,
    int16_t utc_offset_minutes, r1_activity_history *activity,
    r1_health_u8_history *heart_rate, r1_health_u8_history *spo2,
    r1_health_u8_history *temperature, r1_health_u8_history *stress,
    r1_health_u16_history *hrv, r1_health_clear_all_result *result);
r1_error r1_health_settings_plan_command(
    bool write_command, const r1_health_settings_record *stored,
    const uint8_t *payload, size_t payload_length,
    r1_health_settings_command_plan *plan);
/* Product-owned ten-sample reducer around the unavailable GXT310 transport.
 * Sensor acquisition remains an external provider responsibility. */
r1_error r1_temperature_pair_reduce(
    const int32_t samples[R1_TEMPERATURE_PAIR_SENSOR_COUNT]
                         [R1_TEMPERATURE_PAIR_SAMPLE_COUNT],
    const r1_temperature_pair_calibration *calibration,
    r1_temperature_pair_result *result);
void r1_activity_cache_refresh_metadata(
    r1_activity_history *history, uint32_t local_day_start,
    int16_t utc_offset_minutes);
r1_error r1_activity_cache_write_hour(
    r1_activity_history *history, uint8_t hour_index,
    const r1_activity_bucket buckets[R1_ACTIVITY_BUCKETS_PER_HOUR]);
r1_error r1_activity_cache_read_hour(
    const r1_activity_history *history, uint8_t hour_index,
    uint8_t firmware_time_status, uint32_t read_timestamp,
    uint32_t validation_timestamp, const uint32_t *queue_timestamps,
    size_t queue_timestamp_count, r1_activity_offline_queue *queue,
    r1_activity_cache_read_result *result);
void r1_health_u8_cache_reset(r1_health_u8_history *history,
                              uint32_t local_day_start,
                              int16_t utc_offset_minutes);
r1_error r1_health_u8_cache_write_slot(
    r1_health_u8_history *history, uint8_t hour_index,
    uint8_t average, uint8_t maximum, uint8_t minimum);
r1_error r1_health_u8_cache_read_slot(
    const r1_health_u8_history *history, uint8_t hour_index,
    uint8_t firmware_time_status, uint32_t read_timestamp,
    uint32_t validation_timestamp, uint32_t queue_timestamp,
    r1_health_u8_offline_queue *queue,
    r1_health_u8_cache_read_result *result);
r1_error r1_temperature_cache_read_slot(
    const r1_health_u8_history *history, uint8_t hour_index,
    uint8_t firmware_time_status, uint32_t read_timestamp,
    r1_health_u8_cache_read_result *result);
r1_error r1_stress_cache_read_slot(
    const r1_health_u8_history *history, uint8_t hour_index,
    r1_health_u8_slot *returned);
void r1_health_u16_cache_reset(r1_health_u16_history *history,
                               uint32_t local_day_start,
                               int16_t utc_offset_minutes);
r1_error r1_health_u16_cache_write_slot(
    r1_health_u16_history *history, uint8_t hour_index,
    uint16_t average, uint16_t maximum, uint16_t minimum);
r1_error r1_health_u16_cache_read_slot(
    const r1_health_u16_history *history, uint8_t hour_index,
    uint8_t firmware_time_status, uint32_t read_timestamp,
    uint32_t validation_timestamp, uint32_t queue_timestamp,
    r1_health_u16_offline_queue *queue,
    r1_health_u16_cache_read_result *result);
void r1_health_u8_offline_initialize(r1_health_u8_offline_queue *queue);
bool r1_health_u8_offline_is_empty(const r1_health_u8_offline_queue *queue);
r1_error r1_health_u8_offline_enqueue(
    r1_health_u8_offline_queue *queue, uint8_t average, uint8_t maximum,
    uint8_t minimum, uint32_t local_day_start, uint32_t recorded_timestamp,
    int16_t utc_offset_minutes, uint8_t hour_index,
    uint32_t firmware_timestamp, r1_health_offline_enqueue_result *result);
r1_error r1_health_u8_offline_consume_through(
    r1_health_u8_offline_queue *queue, uint32_t cutoff_timestamp,
    size_t *consumed_count);
r1_error r1_health_u8_offline_merge(
    const r1_health_u8_offline_queue *queue, uint32_t firmware_timestamp,
    r1_health_u8_offline_packet *workspace, r1_health_u8_offline_emit_fn emit,
    void *emit_context, r1_health_offline_merge_result *result);
void r1_health_u8_day_builder_reset(r1_health_u8_offline_packet *builder);
r1_error r1_health_u8_day_builder_flush(
    r1_health_u8_offline_packet *builder, uint32_t firmware_timestamp,
    r1_health_u8_offline_emit_fn emit, void *emit_context,
    r1_health_u8_day_flush_result *result);
r1_error r1_health_u8_flash_record_merge(
    r1_health_u8_offline_packet *builder,
    const r1_health_u8_flash_record *record, uint32_t firmware_timestamp,
    bool previous_local_day_only, uint32_t current_local_day_start,
    r1_health_u8_offline_emit_fn emit, void *emit_context,
    r1_health_u8_day_flush_result *flush_result);
r1_error r1_health_u8_ram_cache_merge(
    r1_health_u8_offline_packet *builder, r1_health_u8_history *cache,
    uint32_t requested_day_start, uint32_t window_start,
    uint32_t firmware_timestamp, int16_t current_utc_offset_minutes,
    r1_health_u8_offline_emit_fn emit, void *emit_context,
    r1_health_u8_day_flush_result *flush_result);
r1_error r1_health_u8_offline_acknowledge(
    r1_health_u8_offline_queue *queue, uint8_t mode,
    uint32_t acknowledged_timestamp, uint32_t firmware_timestamp,
    uint32_t *last_sync_timestamp, r1_health_offline_ack_result *result);
void r1_health_u16_offline_initialize(r1_health_u16_offline_queue *queue);
bool r1_health_u16_offline_is_empty(const r1_health_u16_offline_queue *queue);
r1_error r1_health_u16_offline_enqueue(
    r1_health_u16_offline_queue *queue, uint16_t average, uint16_t maximum,
    uint16_t minimum, uint32_t local_day_start, uint32_t recorded_timestamp,
    int16_t utc_offset_minutes, uint8_t hour_index,
    uint32_t firmware_timestamp, r1_health_offline_enqueue_result *result);
r1_error r1_health_u16_offline_consume_through(
    r1_health_u16_offline_queue *queue, uint32_t cutoff_timestamp,
    size_t *consumed_count);
r1_error r1_health_u16_offline_merge(
    const r1_health_u16_offline_queue *queue, uint32_t firmware_timestamp,
    r1_health_u16_offline_packet *workspace, r1_health_u16_offline_emit_fn emit,
    void *emit_context, r1_health_offline_merge_result *result);
r1_error r1_health_u16_ram_cache_merge(
    r1_health_u16_offline_packet *builder, r1_health_u16_history *cache,
    uint32_t requested_day_start, uint32_t window_start,
    uint32_t firmware_timestamp, int16_t current_utc_offset_minutes,
    r1_health_u16_offline_emit_fn emit, void *emit_context,
    r1_health_u16_day_flush_result *flush_result);
r1_error r1_health_u16_offline_acknowledge(
    r1_health_u16_offline_queue *queue, uint8_t mode,
    uint32_t acknowledged_timestamp, uint32_t firmware_timestamp,
    uint32_t *last_sync_timestamp, r1_health_offline_ack_result *result);
r1_error r1_health_encode_point_u8(const r1_health_u8_history *history,
                                   uint8_t state, uint8_t *output,
                                   size_t capacity, size_t *written);
r1_error r1_health_encode_point_u16(const r1_health_u16_history *history,
                                    uint8_t state, uint8_t *output,
                                    size_t capacity, size_t *written);
r1_error r1_sleep_store(r1_sleep_history *history, const r1_sleep_session *session);
r1_error r1_sleep_plan_validated_delivery(
    const r1_sleep_session *session, r1_sleep_validated_delivery_plan *plan);
r1_error r1_sleep_plan_storage_consumer(
    bool record_present, bool append_succeeded,
    r1_sleep_storage_consumer_plan *plan);
r1_error r1_sleep_encode(const r1_sleep_session *session,
                         uint8_t *output, size_t capacity, size_t *written);
r1_error r1_sleep_encode_compact(const r1_sleep_session *session,
                                 uint8_t *output, size_t capacity, size_t *written);
r1_error r1_sleep_decode_compact(const uint8_t *input, size_t length,
                                 bool synchronized, r1_sleep_session *session);
r1_error r1_sleep_build_sync_packet(
    const uint8_t *compact, size_t compact_length,
    uint32_t current_timestamp, int16_t current_utc_offset_minutes,
    uint8_t *output, size_t capacity, size_t *written);
uint16_t r1_health_next_serial(r1_health_state *state);
r1_error r1_health_register_pending(r1_health_state *state,
                                    uint8_t module, uint8_t command, uint8_t subcommand,
                                    uint16_t serial, r1_pending_kind kind,
                                    uint8_t record_index);
bool r1_health_acknowledge(r1_health_state *state,
                           uint8_t module, uint8_t command, uint8_t subcommand,
                           uint16_t serial);
void r1_health_bind_sleep_sync_commit(r1_health_state *state,
                                      r1_sleep_sync_commit_fn commit,
                                      void *context);
void r1_health_clear_pending(r1_health_state *state);
void r1_health_note_explicit_history_query(
    r1_health_state *state, uint32_t now_seconds);
r1_health_auto_sync_result r1_health_run_automatic_sync(
    r1_health_state *state, bool phone_connected, uint32_t now_seconds,
    r1_health_auto_sync_emit_fn emit, void *emit_context);
r1_error r1_health_plan_time_transition(
    const r1_health_time_transition *transition,
    r1_health_time_transition_result *result);
r1_error r1_health_reconcile_sync_cursors(
    r1_health_sync_cursor_state *cursors,
    const r1_health_time_transition *transition,
    r1_health_time_transition_result *result);
r1_error r1_health_plan_hour_boundary(
    uint8_t current_local_hour, r1_health_hour_boundary_result *result);
r1_error r1_hrv_calculate_rmssd(const uint16_t *intervals, size_t count,
                                bool alternate_maximum, r1_hrv_rmssd_result *result);
r1_hrv_publication r1_hrv_publish(float rmssd, bool eligible, uint32_t timestamp);
void r1_hrv_producer_initialize(r1_hrv_producer *producer);
r1_error r1_hrv_producer_ingest(r1_hrv_producer *producer,
                                r1_hrv_producer_session *session,
                                const uint16_t *intervals, size_t count,
                                bool alternate_maximum, bool eligible,
                                uint32_t timestamp, r1_hrv_producer_result *result);
r1_error r1_hrv_plan_timing_start(
    const r1_hrv_timing_observation *observation,
    r1_hrv_timing_plan *plan);

#endif
