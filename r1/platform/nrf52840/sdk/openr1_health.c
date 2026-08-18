#include "openr1/r1_runtime.h"

/*
 * Retained seam for the admitted wall-clock/scheduler producer. The portable
 * controller owns recovered R1 policy; storage and transport stay in their
 * existing typed providers.
 */
typedef struct {
    r1_health_auto_sync_result (*run_automatic_sync)(
        r1_runtime *, uint32_t, r1_health_auto_sync_emit_fn, void *);
    r1_error (*plan_time_transition)(
        const r1_health_time_transition *, r1_health_time_transition_result *);
    r1_error (*reconcile_sync_cursors)(
        r1_health_sync_cursor_state *, const r1_health_time_transition *,
        r1_health_time_transition_result *);
    r1_error (*plan_hour_boundary)(
        uint8_t, r1_health_hour_boundary_result *);
    r1_error (*health_u8_accumulate_average)(
        r1_health_u8_accumulator *, uint8_t, uint8_t, uint8_t *);
    r1_error (*health_u16_accumulate_average)(
        r1_health_u16_accumulator *, uint8_t, uint16_t, uint16_t *);
    void (*health_accumulator_snapshot)(
        const r1_health_u8_accumulator *, uint8_t, uint32_t *, uint16_t *);
    void (*health_accumulator_restore)(
        r1_health_u8_accumulator *, uint8_t, uint32_t, uint16_t);
    r1_error (*health_build_crash_snapshot)(
        r1_health_crash_snapshot *, uint32_t, int16_t,
        const r1_activity_history *, const r1_health_u8_history *,
        const r1_health_u8_accumulator *, const r1_health_u8_history *,
        const r1_health_u16_history *);
    bool (*health_crash_record_valid)(const r1_health_crash_record *);
    bool (*health_crash_record_has_magic)(const r1_health_crash_record *);
    r1_error (*health_crash_record_clear_provider_blob)(
        r1_health_crash_record *);
    r1_error (*health_crash_record_clear_snapshot)(r1_health_crash_record *);
    r1_error (*health_crash_record_clear_time)(r1_health_crash_record *);
    bool (*health_crash_record_get_provider_blob)(
        const r1_health_crash_record *, const uint8_t **, size_t *);
    bool (*health_crash_record_get_snapshot)(
        const r1_health_crash_record *, r1_health_crash_snapshot *);
    bool (*health_crash_record_get_time)(
        const r1_health_crash_record *, r1_health_crash_time *);
    r1_error (*health_crash_record_initialize)(
        r1_health_crash_record *, uint16_t, bool, uint32_t, int16_t,
        const uint8_t *, size_t, const r1_activity_history *,
        const r1_health_u8_history *, const r1_health_u8_accumulator *,
        const r1_health_u8_history *, const r1_health_u16_history *, bool *);
    r1_error (*health_crash_record_restore)(
        r1_health_crash_record *, r1_activity_history *,
        r1_health_u8_history *, r1_health_u8_accumulator *,
        r1_health_u8_history *, r1_health_u16_history *,
        r1_health_crash_restore_result *);
    bool (*health_u8_latest_sample)(
        const r1_health_u8_history *, uint8_t *, uint32_t *);
    bool (*health_u16_latest_sample)(
        const r1_health_u16_history *, uint16_t *, uint32_t *);
    r1_error (*health_history_route_command)(
        uint8_t, uint8_t, uint16_t, r1_health_history_route *);
    r1_error (*health_history_encode_event14)(
        const r1_health_history_route *, uint8_t *);
    r1_error (*health_history_decode_event14)(
        const uint8_t *, size_t, r1_health_history_route *);
    r1_error (*heart_rate_store_sample)(
        r1_health_u8_history *, r1_health_u8_accumulator *, uint8_t,
        uint32_t, uint32_t, uint8_t, uint8_t,
        r1_health_u8_sample_result *);
    r1_error (*spo2_store_sample)(
        r1_health_u8_history *, r1_health_u8_accumulator *, uint8_t,
        uint32_t, uint32_t, uint8_t, uint8_t,
        r1_health_u8_sample_result *);
    r1_error (*hrv_store_sample)(
        r1_health_u16_history *, r1_health_u16_accumulator *, uint16_t,
        uint32_t, uint32_t, uint8_t, uint8_t,
        r1_health_u16_sample_result *);
    r1_error (*hrv_plan_timing_start)(
        const r1_hrv_timing_observation *, r1_hrv_timing_plan *);
    r1_error (*temperature_store_sample)(
        r1_health_u8_history *, r1_health_u8_accumulator *, uint16_t,
        uint32_t, uint8_t, uint8_t, r1_health_u8_sample_result *);
    r1_error (*stress_store_sample)(
        r1_health_u8_history *, r1_health_u8_accumulator *, uint8_t,
        uint32_t, uint8_t, uint8_t, r1_health_u8_sample_result *);
    void (*activity_accumulator_initialize)(r1_activity_accumulator *);
    r1_error (*activity_accumulator_periodic)(
        r1_activity_accumulator *, const r1_activity_cumulative_counters *,
        uint32_t, uint32_t, uint8_t, uint8_t,
        r1_activity_accumulator_result *);
    r1_error (*activity_accumulator_refresh)(
        r1_activity_accumulator *, uint32_t, uint8_t, uint8_t,
        r1_activity_accumulator_result *);
    r1_error (*activity_accumulator_pending_delta)(
        const r1_activity_accumulator *, uint8_t, uint8_t,
        r1_activity_delta_event *);
    r1_error (*activity_delta_event_encode)(
        const r1_activity_delta_event *, uint8_t *);
    r1_error (*activity_delta_event_decode)(
        const uint8_t *, size_t, r1_activity_delta_event *);
    r1_error (*activity_consume_delta_event)(
        r1_activity_history *, const r1_activity_delta_event *,
        r1_activity_bucket_resolver_fn, void *, uint32_t, int16_t,
        r1_activity_delta_consume_result *);
    bool (*activity_offline_is_empty)(const r1_activity_offline_queue *);
    r1_error (*activity_offline_enqueue)(
        r1_activity_offline_queue *, uint32_t, uint32_t, uint32_t, int16_t,
        uint8_t, uint32_t, r1_activity_offline_enqueue_result *);
    r1_error (*activity_offline_consume_through)(
        r1_activity_offline_queue *, uint32_t, size_t *);
    r1_error (*activity_offline_merge)(
        const r1_activity_offline_queue *, uint32_t,
        r1_activity_offline_packet *, r1_activity_offline_emit_fn,
        void *, r1_activity_offline_merge_result *);
    r1_error (*activity_offline_acknowledge)(
        r1_activity_offline_queue *, uint8_t, uint32_t, uint32_t,
        uint32_t *, r1_activity_ack_result *);
    bool (*health_u8_offline_is_empty)(const r1_health_u8_offline_queue *);
    r1_error (*health_u8_offline_enqueue)(
        r1_health_u8_offline_queue *, uint8_t, uint8_t, uint8_t, uint32_t,
        uint32_t, int16_t, uint8_t, uint32_t,
        r1_health_offline_enqueue_result *);
    r1_error (*health_u8_offline_consume_through)(
        r1_health_u8_offline_queue *, uint32_t, size_t *);
    r1_error (*health_u8_offline_merge)(
        const r1_health_u8_offline_queue *, uint32_t,
        r1_health_u8_offline_packet *, r1_health_u8_offline_emit_fn,
        void *, r1_health_offline_merge_result *);
    r1_error (*health_u8_flash_record_merge)(
        r1_health_u8_offline_packet *, const r1_health_u8_flash_record *,
        uint32_t, bool, uint32_t, r1_health_u8_offline_emit_fn, void *,
        r1_health_u8_day_flush_result *);
    r1_error (*health_u8_ram_cache_merge)(
        r1_health_u8_offline_packet *, r1_health_u8_history *, uint32_t,
        uint32_t, uint32_t, int16_t, r1_health_u8_offline_emit_fn, void *,
        r1_health_u8_day_flush_result *);
    r1_error (*health_u8_offline_acknowledge)(
        r1_health_u8_offline_queue *, uint8_t, uint32_t, uint32_t,
        uint32_t *, r1_health_offline_ack_result *);
    bool (*health_u16_offline_is_empty)(const r1_health_u16_offline_queue *);
    r1_error (*health_u16_offline_enqueue)(
        r1_health_u16_offline_queue *, uint16_t, uint16_t, uint16_t, uint32_t,
        uint32_t, int16_t, uint8_t, uint32_t,
        r1_health_offline_enqueue_result *);
    r1_error (*health_u16_offline_consume_through)(
        r1_health_u16_offline_queue *, uint32_t, size_t *);
    r1_error (*health_u16_offline_merge)(
        const r1_health_u16_offline_queue *, uint32_t,
        r1_health_u16_offline_packet *, r1_health_u16_offline_emit_fn,
        void *, r1_health_offline_merge_result *);
    r1_error (*health_u16_flash_record_merge)(
        r1_health_u16_offline_packet *, const r1_health_u16_flash_record *,
        uint32_t, bool, uint32_t, r1_health_u16_offline_emit_fn, void *,
        r1_health_u16_day_flush_result *);
    r1_error (*health_u16_ram_cache_merge)(
        r1_health_u16_offline_packet *, r1_health_u16_history *, uint32_t,
        uint32_t, uint32_t, int16_t, r1_health_u16_offline_emit_fn, void *,
        r1_health_u16_day_flush_result *);
    r1_error (*health_u16_offline_acknowledge)(
        r1_health_u16_offline_queue *, uint8_t, uint32_t, uint32_t,
        uint32_t *, r1_health_offline_ack_result *);
    void (*health_u8_cache_reset)(r1_health_u8_history *, uint32_t, int16_t);
    r1_error (*health_u8_cache_write_slot)(
        r1_health_u8_history *, uint8_t, uint8_t, uint8_t, uint8_t);
    r1_error (*health_u8_cache_read_slot)(
        const r1_health_u8_history *, uint8_t, uint8_t, uint32_t, uint32_t,
        uint32_t, r1_health_u8_offline_queue *,
        r1_health_u8_cache_read_result *);
    r1_error (*temperature_cache_read_slot)(
        const r1_health_u8_history *, uint8_t, uint8_t, uint32_t,
        r1_health_u8_cache_read_result *);
    r1_error (*stress_cache_read_slot)(
        const r1_health_u8_history *, uint8_t, r1_health_u8_slot *);
    void (*health_u16_cache_reset)(r1_health_u16_history *, uint32_t, int16_t);
    r1_error (*health_u16_cache_write_slot)(
        r1_health_u16_history *, uint8_t, uint16_t, uint16_t, uint16_t);
    r1_error (*health_u16_cache_read_slot)(
        const r1_health_u16_history *, uint8_t, uint8_t, uint32_t, uint32_t,
        uint32_t, r1_health_u16_offline_queue *,
        r1_health_u16_cache_read_result *);
    void (*activity_cache_reset)(r1_activity_history *, uint32_t, int16_t);
    void (*activity_cache_refresh_metadata)(
        r1_activity_history *, uint32_t, int16_t);
    r1_error (*activity_cache_write_hour)(
        r1_activity_history *, uint8_t, const r1_activity_bucket *);
    r1_error (*activity_cache_read_hour)(
        const r1_activity_history *, uint8_t, uint8_t, uint32_t, uint32_t,
        const uint32_t *, size_t, r1_activity_offline_queue *,
        r1_activity_cache_read_result *);
    uint32_t (*activity_clamp_acknowledgement_timestamp)(uint32_t, uint32_t);
    void (*activity_day_builder_reset)(r1_activity_offline_packet *);
    r1_error (*activity_day_builder_flush)(
        r1_activity_offline_packet *, uint32_t, r1_activity_offline_emit_fn,
        void *, r1_activity_day_flush_result *);
    r1_error (*activity_ram_cache_merge)(
        r1_activity_offline_packet *, r1_activity_history *, uint32_t,
        uint32_t, uint32_t, int16_t, uint16_t, uint16_t, uint16_t,
        r1_activity_offline_emit_fn, void *, r1_activity_day_flush_result *);
    r1_error (*activity_flash_record_merge)(
        r1_activity_offline_packet *, const r1_activity_flash_record *,
        uint32_t, bool, r1_activity_offline_emit_fn, void *,
        r1_activity_day_flush_result *);
} openr1_health_api;

__attribute__((used, section(".openr1_health_api")))
static const openr1_health_api retained_health_api = {
    r1_runtime_run_automatic_health_sync,
    r1_health_plan_time_transition,
    r1_health_reconcile_sync_cursors,
    r1_health_plan_hour_boundary,
    r1_health_u8_accumulate_average,
    r1_health_u16_accumulate_average,
    r1_health_accumulator_snapshot,
    r1_health_accumulator_restore,
    r1_health_build_crash_snapshot,
    r1_health_crash_record_valid,
    r1_health_crash_record_has_magic,
    r1_health_crash_record_clear_provider_blob,
    r1_health_crash_record_clear_snapshot,
    r1_health_crash_record_clear_time,
    r1_health_crash_record_get_provider_blob,
    r1_health_crash_record_get_snapshot,
    r1_health_crash_record_get_time,
    r1_health_crash_record_initialize,
    r1_health_crash_record_restore,
    r1_health_u8_latest_sample,
    r1_health_u16_latest_sample,
    r1_health_history_route_command,
    r1_health_history_encode_event14,
    r1_health_history_decode_event14,
    r1_heart_rate_store_sample,
    r1_spo2_store_sample,
    r1_hrv_store_sample,
    r1_hrv_plan_timing_start,
    r1_temperature_store_sample,
    r1_stress_store_sample,
    r1_activity_accumulator_initialize,
    r1_activity_accumulator_periodic,
    r1_activity_accumulator_refresh,
    r1_activity_accumulator_pending_delta,
    r1_activity_delta_event_encode,
    r1_activity_delta_event_decode,
    r1_activity_consume_delta_event,
    r1_activity_offline_is_empty,
    r1_activity_offline_enqueue,
    r1_activity_offline_consume_through,
    r1_activity_offline_merge,
    r1_activity_offline_acknowledge,
    r1_health_u8_offline_is_empty,
    r1_health_u8_offline_enqueue,
    r1_health_u8_offline_consume_through,
    r1_health_u8_offline_merge,
    r1_health_u8_flash_record_merge,
    r1_health_u8_ram_cache_merge,
    r1_health_u8_offline_acknowledge,
    r1_health_u16_offline_is_empty,
    r1_health_u16_offline_enqueue,
    r1_health_u16_offline_consume_through,
    r1_health_u16_offline_merge,
    r1_health_u16_flash_record_merge,
    r1_health_u16_ram_cache_merge,
    r1_health_u16_offline_acknowledge,
    r1_health_u8_cache_reset,
    r1_health_u8_cache_write_slot,
    r1_health_u8_cache_read_slot,
    r1_temperature_cache_read_slot,
    r1_stress_cache_read_slot,
    r1_health_u16_cache_reset,
    r1_health_u16_cache_write_slot,
    r1_health_u16_cache_read_slot,
    r1_activity_cache_reset,
    r1_activity_cache_refresh_metadata,
    r1_activity_cache_write_hour,
    r1_activity_cache_read_hour,
    r1_activity_clamp_acknowledgement_timestamp,
    r1_activity_day_builder_reset,
    r1_activity_day_builder_flush,
    r1_activity_ram_cache_merge,
    r1_activity_flash_record_merge,
};
