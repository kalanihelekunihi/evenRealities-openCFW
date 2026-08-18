#ifndef OPENR1_DATABASES_ZEPHYR_H
#define OPENR1_DATABASES_ZEPHYR_H

#include <stdbool.h>
#include <stddef.h>

#include "openr1/r1_kv_store.h"
#include "openr1/r1_event_bus.h"
#include "openr1/r1_health_db.h"
#include "openr1/r1_nv_recovery.h"
#include "openr1/r1_runtime.h"
#include "openr1/r1_sleep_db.h"

int openr1_databases_zephyr_initialize(r1_runtime *runtime);
bool openr1_databases_zephyr_kv_ready(void);
bool openr1_databases_zephyr_health_ready(void);
bool openr1_databases_zephyr_sleep_ready(void);
r1_kv_store *openr1_databases_zephyr_kv_store(void);
r1_event_bus *openr1_databases_zephyr_event_bus(void);
r1_health_db_startup_result *openr1_databases_zephyr_health_startup(void);
void *openr1_databases_zephyr_health_handle(void);
uint32_t openr1_databases_zephyr_recovery_records_visited(void);
uint32_t openr1_databases_zephyr_recovery_records_decoded(void);
uint32_t openr1_databases_zephyr_recovery_records_restored(void);
uint32_t openr1_databases_zephyr_recovery_records_rejected(void);
uint32_t openr1_databases_zephyr_health_records_appended(void);
uint32_t openr1_databases_zephyr_health_append_failures(void);
uint32_t openr1_databases_zephyr_time_recoveries(void);
uint32_t openr1_databases_zephyr_time_recovery_failures(void);
uint32_t openr1_databases_zephyr_time_daily_resets(void);
uint32_t openr1_databases_zephyr_destructive_actions_suppressed(void);
uint32_t openr1_databases_zephyr_gomore_reinitializations(void);
uint32_t openr1_databases_zephyr_gomore_reinitialization_failures(void);
uint32_t openr1_databases_zephyr_health_settings_updates_persisted(void);
uint32_t openr1_databases_zephyr_health_settings_update_failures(void);
uint32_t openr1_databases_zephyr_cursor_updates_persisted(void);
uint32_t openr1_databases_zephyr_cursor_update_failures(void);
const r1_health_sync_cursor_state *
openr1_databases_zephyr_health_sync_cursors(void);
bool openr1_databases_zephyr_temperature_calibration(
    r1_temperature_pair_calibration *calibration);
bool openr1_databases_zephyr_accelerometer_calibration(
    r1_motion_axis_calibration *calibration);
bool openr1_databases_zephyr_battery_configuration(
    r1_nv_battery_configuration *configuration);
bool openr1_databases_zephyr_ring_size(uint8_t *ring_size);
bool openr1_databases_zephyr_product_serial(
    uint8_t serial[R1_NV_PRODUCT_SERIAL_BYTES]);
bool openr1_databases_zephyr_factory_mode(void);
r1_error openr1_databases_zephyr_persist_peer_targets(
    const uint8_t first_target[R1_PEER_ADDRESS_SIZE],
    const uint8_t second_target[R1_PEER_ADDRESS_SIZE]);
r1_error openr1_databases_zephyr_remove_ring_metadata(void);
/* Local/service-mode recovery only. The caller must establish physical
 * authorization; this API is intentionally not registered with BLE dispatch.
 * Changed calibration and power fields are cached immediately, while callers
 * should reboot before relying on already-running sensor providers. */
r1_error openr1_databases_zephyr_apply_local_nv_recovery(
    const uint8_t *body, size_t length, uint16_t expected_crc,
    uint8_t *changed_records);
r1_error openr1_databases_zephyr_multicast_time_transition(
    const r1_health_time_transition *transition);
r1_error openr1_databases_zephyr_multicast_hour(uint8_t current_local_hour);
r1_error openr1_databases_zephyr_consume_temperature_event(
    const void *payload, size_t length);
r1_error openr1_databases_zephyr_consume_heart_rate_event(
    const void *payload, size_t length);
r1_error openr1_databases_zephyr_consume_spo2_event(
    const void *payload, size_t length);
r1_error openr1_databases_zephyr_consume_hrv_event(
    const void *payload, size_t length);
r1_error openr1_databases_zephyr_consume_activity_cumulative(
    const uint32_t activity[2], uint8_t sleep_result_status);
r1_error openr1_databases_zephyr_consume_sleep_record(
    const uint8_t *payload, size_t length);
r1_sleep_db *openr1_databases_zephyr_sleep_db(void);

#endif
