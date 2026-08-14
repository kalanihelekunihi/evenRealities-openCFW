#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "openr1/r1_crc.h"
#include "openr1/r1_battery.h"
#include "openr1/r1_clock.h"
#include "openr1/r1_connection_params.h"
#include "openr1/r1_dispatch.h"
#include "openr1/r1_event.h"
#include "openr1/r1_goodix.h"
#include "openr1/r1_health.h"
#include "openr1/r1_health_db.h"
#include "openr1/r1_iqs7211e.h"
#include "openr1/r1_kv_store.h"
#include "openr1/r1_motion.h"
#include "openr1/r1_nv_recovery.h"
#include "openr1/r1_persistence.h"
#include "openr1/r1_peer_target.h"
#include "openr1/r1_power_lease.h"
#include "openr1/r1_protocol.h"
#include "openr1/r1_retained_log.h"
#include "openr1/r1_reset_trace.h"
#include "openr1/r1_reset_reason.h"
#include "openr1/r1_runtime.h"
#include "openr1/r1_sleep_db.h"
#include "openr1/r1_state.h"
#include "openr1/r1_st25dvxxkc.h"
#include "openr1/r1_storage.h"
#include "openr1/r1_twi_sync.h"
#include "openr1/r1_wear.h"

static void test_checksums(void) {
    static const uint8_t check[] = "123456789";
    assert(r1_crc16_modbus(check, 9u) == UINT16_C(0x4b37));
    assert(r1_crc16_ccitt(check, 9u) == UINT16_C(0x29b1));
    assert(r1_crc32_castagnoli(check, 9u) == UINT32_C(0xc052a8c8));
    assert(r1_crc32_castagnoli(NULL, 0u) == 0u);
}

typedef struct {
    size_t first_use_calls;
    size_t write_calls;
    uint8_t written[32];
    size_t written_length;
    r1_error first_use_error;
    r1_error write_error;
} retained_log_trace;

static r1_error retained_log_first_use(void *context) {
    retained_log_trace *trace = context;
    ++trace->first_use_calls;
    return trace->first_use_error;
}

static r1_error retained_log_write(
    void *context, const uint8_t *bytes, size_t length) {
    retained_log_trace *trace = context;
    ++trace->write_calls;
    trace->written_length = length < sizeof(trace->written)
        ? length : sizeof(trace->written);
    memcpy(trace->written, bytes, trace->written_length);
    return trace->write_error;
}

static void test_retained_crash_log(void) {
    r1_retained_log log;
    memset(&log, 0xa5, sizeof(log));
    r1_retained_log_reset(&log);
    assert(!log.initialized && log.length == 0u);
    assert(log.bytes[0] == 0u && log.bytes[R1_RETAINED_LOG_BYTES - 1u] == 0u);

    retained_log_trace trace = {
        .first_use_error = R1_ERROR_STATE,
        .write_error = R1_ERROR_CAPACITY,
    };
    r1_retained_log_result result;
    assert(r1_retained_log_append_rendered(
        &log, NULL, 0u, retained_log_first_use, &trace,
        retained_log_write, &trace, &result) == R1_OK);
    assert(!log.initialized && trace.first_use_calls == 0u);

    static const uint8_t empty[] = "";
    assert(r1_retained_log_append_rendered(
        &log, empty, 0u, retained_log_first_use, &trace,
        retained_log_write, &trace, &result) == R1_OK);
    assert(result.initialized_now && result.first_use_error == R1_ERROR_STATE);
    assert(log.initialized && log.length == 0u && trace.first_use_calls == 1u);

    static const uint8_t alpha[] = "alpha";
    assert(r1_retained_log_append_rendered(
        &log, alpha, 5u, retained_log_first_use, &trace,
        retained_log_write, &trace, &result) == R1_OK);
    assert(!result.initialized_now && result.appended && !result.truncated);
    assert(result.captured_length == 5u);
    assert(result.transport_error == R1_ERROR_CAPACITY);
    assert(log.length == 6u && memcmp(log.bytes, "alpha\n", 6u) == 0);
    assert(trace.first_use_calls == 1u && trace.write_calls == 1u);
    assert(trace.written_length == 6u &&
           memcmp(trace.written, "alpha\n", 6u) == 0);

    uint8_t oversized[R1_RETAINED_LOG_BYTES + 8u];
    memset(oversized, 'x', sizeof(oversized));
    assert(r1_retained_log_append_rendered(
        &log, oversized, sizeof(oversized), NULL, NULL,
        NULL, NULL, &result) == R1_OK);
    assert(result.appended && result.truncated);
    assert(result.captured_length == R1_RETAINED_LOG_PAYLOAD_LIMIT - 6u);
    assert(log.length == R1_RETAINED_LOG_APPEND_LIMIT);
    assert(log.bytes[R1_RETAINED_LOG_APPEND_LIMIT - 1u] == (uint8_t)'\n');
    assert(log.bytes[R1_RETAINED_LOG_BYTES - 1u] == 0u);
    assert(r1_retained_log_append_rendered(
        &log, alpha, 5u, NULL, NULL, NULL, NULL, &result) == R1_OK);
    assert(!result.appended && result.truncated &&
           log.length == R1_RETAINED_LOG_APPEND_LIMIT);

    assert(r1_retained_log_append_rendered(
        NULL, alpha, 5u, NULL, NULL, NULL, NULL, &result) ==
           R1_ERROR_ARGUMENT);
    assert(r1_retained_log_append_rendered(
        &log, NULL, 1u, NULL, NULL, NULL, NULL, &result) ==
           R1_ERROR_ARGUMENT);
    assert(r1_retained_log_append_rendered(
        &log, alpha, 5u, NULL, NULL, NULL, NULL, NULL) ==
           R1_ERROR_ARGUMENT);
    r1_retained_log_reset(NULL);
}

static void test_retained_reset_trace(void) {
    r1_reset_trace_record record;
    memset(&record, 0xa5, sizeof(record));
    assert(!r1_reset_trace_valid(&record));
    r1_reset_trace_initialize(&record);
    assert(r1_reset_trace_valid(&record));
    assert(record.bytes[0] == 0u);
    assert(record.bytes[14] == 0xabu && record.bytes[15] == 0x01u);

    uint8_t byte = 0xffu;
    assert(r1_reset_trace_read_byte(
        &record, R1_RESET_TRACE_PERSIST_TAG_INDEX, &byte));
    assert(byte == 0u);
    assert(!r1_reset_trace_read_byte(
        &record, R1_RESET_TRACE_FIELD_COUNT, &byte));
    assert(!r1_reset_trace_read_byte(&record, 0u, NULL));
    assert(!r1_reset_trace_write_byte(
        &record, R1_RESET_TRACE_FIELD_COUNT, 1u));

    r1_reset_trace_set_return_address(&record, UINT32_C(0x11223344));
    r1_reset_trace_set_program_counter(&record, UINT32_C(0x89abcdef));
    assert(record.bytes[3] == 0x44u && record.bytes[6] == 0x11u);
    assert(record.bytes[7] == 0xefu && record.bytes[10] == 0x89u);
    uint32_t address = 0u;
    assert(r1_reset_trace_read_return_address(&record, &address));
    assert(address == UINT32_C(0x11223344));
    assert(r1_reset_trace_read_program_counter(&record, &address));
    assert(address == UINT32_C(0x89abcdef));

    r1_reset_trace_set_persist_tag(&record, R1_RESET_TRACE_FAULT_TAG);
    r1_reset_trace_snapshot snapshot;
    assert(r1_reset_trace_get_snapshot(&record, &snapshot));
    assert(snapshot.persist_tag == R1_RESET_TRACE_FAULT_TAG);
    assert(snapshot.return_address == UINT32_C(0x11223344));
    assert(snapshot.program_counter == UINT32_C(0x89abcdef));

    r1_reset_trace_set_persist_tag(&record, 4u);
    assert(r1_reset_trace_get_snapshot(&record, &snapshot));
    assert(snapshot.persist_tag == 4u && snapshot.return_address == 0u &&
           snapshot.program_counter == 0u);
    r1_reset_trace_capture_site(
        &record, UINT32_C(0x0007a5e6), UINT32_C(0x000274b9));
    assert(r1_reset_trace_get_snapshot(&record, &snapshot));
    assert(snapshot.program_counter == UINT32_C(0x0007a5e6));
    assert(snapshot.return_address == UINT32_C(0x000274b9));
    r1_reset_trace_capture_site(&record, 0u, 0u);
    assert(r1_reset_trace_get_snapshot(&record, &snapshot));
    assert(snapshot.program_counter == UINT32_C(0x0007a5e6));

    r1_reset_trace_set_reboot_caller(&record, 2u);
    assert(r1_reset_trace_get_snapshot(&record, &snapshot));
    assert(snapshot.persist_tag == 4u && snapshot.reboot_caller == 2u);
    assert(snapshot.return_address == 0u && snapshot.program_counter == 0u);

    record.bytes[5] ^= 0x80u;
    assert(!r1_reset_trace_valid(&record));
    assert(!r1_reset_trace_get_snapshot(&record, &snapshot));
    assert(r1_reset_trace_write_byte(&record, 12u, 0x5au));
    assert(r1_reset_trace_valid(&record));
    assert(r1_reset_trace_read_byte(&record, 12u, &byte) && byte == 0x5au);
    assert(record.bytes[1] == 0u && record.bytes[13] == 0x5au);

    r1_reset_trace_clear(&record);
    assert(r1_reset_trace_valid(&record));
    r1_reset_trace_clear(NULL);
    r1_reset_trace_initialize(NULL);
    r1_reset_trace_clear_addresses(NULL);
    r1_reset_trace_set_return_address(NULL, 1u);
    r1_reset_trace_set_program_counter(NULL, 1u);
    r1_reset_trace_set_reboot_caller(NULL, 1u);
    r1_reset_trace_set_persist_tag(NULL, 1u);
    r1_reset_trace_capture_site(NULL, 1u, 1u);
    assert(!r1_reset_trace_valid(NULL));
    assert(!r1_reset_trace_get_snapshot(&record, NULL));
}

static void test_reset_reason_decode(void) {
    r1_reset_trace_record trace;
    r1_reset_reason_report report;
    r1_reset_trace_clear(&trace);
    r1_reset_trace_set_persist_tag(&trace, 2u);
    r1_reset_trace_set_reboot_caller(&trace, 5u);
    r1_reset_trace_capture_site(
        &trace, UINT32_C(0x12345678), UINT32_C(0x9abcdef0));

    assert(r1_reset_reason_decode(0u, &trace, &report));
    assert(report.raw == 0u);
    assert(report.recognized == 0u);
    assert(report.power_on_or_brownout);
    assert(!report.software_trace_valid);

    const uint32_t known = R1_RESET_REASON_PIN |
        R1_RESET_REASON_WATCHDOG | R1_RESET_REASON_SOFTWARE |
        R1_RESET_REASON_LOCKUP | R1_RESET_REASON_SYSTEM_OFF_GPIO |
        R1_RESET_REASON_SYSTEM_OFF_LPCOMP |
        R1_RESET_REASON_SYSTEM_OFF_DEBUG;
    assert(r1_reset_reason_decode(known | UINT32_C(0x80000000),
                                  &trace, &report));
    assert(report.raw == (known | UINT32_C(0x80000000)));
    assert(report.recognized == known);
    assert(!report.power_on_or_brownout);
    assert(report.software_trace_valid);
    assert(report.reboot_caller_valid);
    assert(report.software_trace.persist_tag == 2u);
    assert(report.software_trace.reboot_caller == 5u);
    assert(report.software_trace.program_counter == UINT32_C(0x12345678));
    assert(report.software_trace.return_address == UINT32_C(0x9abcdef0));

    r1_reset_trace_set_persist_tag(&trace, R1_RESET_TRACE_FAULT_TAG);
    r1_reset_trace_capture_site(
        &trace, UINT32_C(0x01020304), UINT32_C(0x05060708));
    assert(r1_reset_reason_decode(R1_RESET_REASON_SOFTWARE, &trace, &report));
    assert(report.software_trace_valid);
    assert(!report.reboot_caller_valid);
    assert(report.software_trace.persist_tag == R1_RESET_TRACE_FAULT_TAG);

    trace.bytes[3] ^= 0x80u;
    assert(r1_reset_reason_decode(R1_RESET_REASON_SOFTWARE, &trace, &report));
    assert(!report.software_trace_valid);
    assert(!report.reboot_caller_valid);
    assert(report.software_trace.program_counter == 0u);
    assert(report.software_trace.return_address == 0u);

    assert(r1_reset_reason_decode(R1_RESET_REASON_PIN, NULL, &report));
    assert(report.recognized == R1_RESET_REASON_PIN);
    assert(!report.software_trace_valid);
    assert(!r1_reset_reason_decode(0u, &trace, NULL));
}

static void test_clock_production(void) {
    r1_clock clock;
    uint32_t value = 0u;

    r1_clock_initialize(&clock, 1024u);
    assert(!clock.synchronized);
    assert(!r1_clock_now(&clock, 0u, &value));
    assert(!r1_clock_local_now(&clock, 0u, &value));

    /* A zero-frequency clock never reports time. */
    r1_clock_initialize(&clock, 0u);
    assert(r1_clock_synchronize(&clock, 1700000000u, 0, 0u) == R1_OK);
    assert(!r1_clock_now(&clock, 4096u, &value));

    r1_clock_initialize(&clock, 1024u);
    assert(r1_clock_synchronize(NULL, 1u, 0, 0u) == R1_ERROR_ARGUMENT);
    assert(r1_clock_synchronize(&clock, 1u, -721, 0u) == R1_ERROR_ARGUMENT);
    assert(r1_clock_synchronize(&clock, 1u, 841, 0u) == R1_ERROR_ARGUMENT);
    assert(!clock.synchronized);
    assert(r1_clock_synchronize(&clock, 1u, -720, 0u) == R1_OK);
    assert(r1_clock_synchronize(&clock, 1u, 840, 0u) == R1_OK);

    assert(r1_clock_synchronize(&clock, 1700000000u, 60, 1000u) == R1_OK);
    /* Partial seconds do not advance the epoch. */
    assert(r1_clock_now(&clock, 2023u, &value));
    assert(value == 1700000000u);
    /* Exact whole-second advance. */
    assert(r1_clock_now(&clock, 1000u + 3u * 1024u, &value));
    assert(value == 1700000003u);
    /* Tick-counter wraparound is wrap-safe. */
    assert(r1_clock_synchronize(&clock, 100u, 0, UINT32_MAX - 511u) == R1_OK);
    assert(r1_clock_now(&clock, 1536u, &value));
    assert(value == 102u);
    /* Epoch advance saturates instead of wrapping. */
    assert(r1_clock_synchronize(&clock, UINT32_MAX - 1u, 0, 0u) == R1_OK);
    assert(r1_clock_now(&clock, 5u * 1024u, &value));
    assert(value == UINT32_MAX);
    /* Local time applies the signed offset and clamps at zero. */
    assert(r1_clock_synchronize(&clock, 3600u, -120, 0u) == R1_OK);
    assert(r1_clock_local_now(&clock, 0u, &value));
    assert(value == 0u);
    assert(r1_clock_synchronize(&clock, 3600u, 90, 0u) == R1_OK);
    assert(r1_clock_local_now(&clock, 0u, &value));
    assert(value == 3600u + 90u * 60u);
    assert(!r1_clock_now(NULL, 0u, &value));
    assert(!r1_clock_now(&clock, 0u, NULL));
    assert(!r1_clock_local_now(&clock, 0u, NULL));
}

static void test_battery_provider_boundary(void) {
    static const uint16_t battery_samples[] = {4095u, 4000u, 3000u, 2000u, 1000u};
    uint16_t millivolts = 0u;
    assert(r1_battery_base_millivolts(
        battery_samples, R1_BATTERY_SAMPLE_COUNT, &millivolts));
    assert(millivolts == 6468u);
    assert(r1_battery_runtime_millivolts(
        battery_samples, R1_BATTERY_SAMPLE_COUNT, 10,
        R1_CHARGE_NOT_CHARGING, &millivolts));
    assert(millivolts == 6478u);
    assert(r1_battery_runtime_millivolts(
        battery_samples, R1_BATTERY_SAMPLE_COUNT, 300,
        R1_CHARGE_NOT_CHARGING, &millivolts));
    assert(millivolts == 6468u);
    assert(r1_battery_runtime_millivolts(
        battery_samples, R1_BATTERY_SAMPLE_COUNT, 0,
        R1_CHARGE_CHARGING, &millivolts));
    assert(millivolts == 6142u);
    assert(!r1_battery_base_millivolts(battery_samples, 4u, &millivolts));

    static const int16_t rectifier_samples[] = {1000, 1000, 1000};
    assert(r1_nfc_rectifier_millivolts(
        rectifier_samples, R1_NFC_RECTIFIER_SAMPLE_COUNT, &millivolts));
    assert(millivolts == 5704u);
    static const int16_t clamped_samples[] = {-1, 0, 4095};
    assert(r1_nfc_rectifier_millivolts(
        clamped_samples, R1_NFC_RECTIFIER_SAMPLE_COUNT, &millivolts));
    assert(millivolts == 7788u);
    static const int16_t current_samples[] = {-1, 2048, 4095};
    assert(r1_pmic_current_sense_millivolts(
        current_samples, R1_PMIC_CURRENT_SAMPLE_COUNT, &millivolts));
    assert(millivolts == 600u);

    assert(r1_battery_discharge_percent(3350u, 1u, 0u) == 0u);
    assert(r1_battery_discharge_percent(3622u, 1u, 0u) == 5u);
    assert(r1_battery_discharge_percent(4310u, 1u, 0u) == 100u);
    assert(r1_battery_discharge_percent(2399u, 1u, 0u) == 50u);
    assert(r1_battery_discharge_percent(4341u, 1u, 5u) == 100u);
    assert(r1_battery_charging_initial_percent(4310u, 1u) == 82u);
    assert(r1_battery_charging_initial_percent(4350u, 3u) == 100u);
    assert(r1_battery_discharge_percent(3900u, 0u, 0u) ==
           r1_battery_discharge_percent(3900u, 4u, 0u));

    r1_battery_charge_progress progress = {84u, 0u};
    r1_battery_charge_result advanced = r1_battery_advance_charging(
        progress, 37u, 1u, 4000u, 0u);
    assert(advanced.state.percent == 84u);
    assert(advanced.state.accumulated_seconds == 37u);
    advanced = r1_battery_advance_charging(
        advanced.state, 1u, 1u, 4000u, 0u);
    assert(advanced.state.percent == 85u);
    assert(advanced.state.accumulated_seconds == 0u);
    progress = (r1_battery_charge_progress){84u, 0u};
    advanced = r1_battery_advance_charging(
        progress, 1000u, 1u, 4000u, 0u);
    assert(advanced.state.percent == 87u);
    assert(advanced.state.accumulated_seconds == 22u);
    advanced = r1_battery_advance_charging(
        advanced.state, 0u, 1u, 4341u, 5u);
    assert(advanced.reported_percent == 100u);
    assert(r1_battery_updated_charged_refresh_count(4u, R1_CHARGE_FULL) == 5u);
    assert(r1_battery_updated_charged_refresh_count(8u, R1_CHARGE_FULL) == 8u);
    assert(r1_battery_updated_charged_refresh_count(
        8u, R1_CHARGE_CHARGING) == 0u);

    uint8_t replacement = 0u;
    assert(r1_battery_stalled_replacement(
        50u, 50u, 4165u, 4200u, 120u, false, 1u, &replacement));
    assert(replacement == 70u);
    assert(!r1_battery_stalled_replacement(
        50u, 50u, 4166u, 4200u, 120u, false, 1u, &replacement));
    assert(!r1_battery_stalled_replacement(
        50u, 50u, 4165u, 4200u, 119u, false, 1u, &replacement));

    r1_battery_stuck_state stuck = {false, 0u, 0u, false};
    r1_battery_stuck_result recovered = r1_battery_update_stuck_recovery(
        stuck, R1_CHARGE_CHARGING, 50u, 4165u, 0u, 1u);
    assert(recovered.state.has_previous_percent);
    assert(recovered.state.previous_percent == 50u);
    assert(recovered.observation_baseline_updated);
    recovered = r1_battery_update_stuck_recovery(
        recovered.state, R1_CHARGE_CHARGING, 50u, 4200u, 120u, 1u);
    assert(recovered.has_replacement_percent);
    assert(recovered.replacement_progress_percent == 70u);
    assert(recovered.should_reset_charge_progress);
    assert(recovered.state.already_recovered);
    const r1_battery_stuck_result one_shot = r1_battery_update_stuck_recovery(
        recovered.state, R1_CHARGE_CHARGING, 50u, 4300u, 120u, 1u);
    assert(!one_shot.has_replacement_percent);
    const r1_battery_stuck_result changed = r1_battery_update_stuck_recovery(
        recovered.state, R1_CHARGE_CHARGING, 51u, 4205u, 1u, 1u);
    assert(changed.state.previous_percent == 51u);
    assert(!changed.state.already_recovered);
    const r1_battery_stuck_result stopped = r1_battery_update_stuck_recovery(
        changed.state, R1_CHARGE_NOT_CHARGING, 51u, 4200u, 1u, 1u);
    assert(!stopped.state.has_previous_percent);
}

static void test_battery_controller(void) {
    r1_battery_controller controller;
    r1_battery_controller_initialize(
        &controller, 1u, 50u, R1_CHARGE_NOT_CHARGING);
    assert(controller.battery_type == 1u);
    assert(controller.percent == 50u);
    assert(controller.charge == R1_CHARGE_NOT_CHARGING);

    assert(r1_battery_controller_update(
        &controller, R1_CHARGE_NOT_CHARGING, 3622u, 60u));
    assert(controller.percent == 5u);
    assert(controller.millivolts == 3622u);

    assert(r1_battery_controller_update(
        &controller, R1_CHARGE_CHARGING, 3799u, 60u));
    assert(controller.percent == 5u);
    assert(controller.charge_progress.accumulated_seconds == 0u);
    assert(r1_battery_controller_update(
        &controller, R1_CHARGE_CHARGING, 3800u, 38u));
    assert(controller.percent == 6u);
    assert(controller.charge_progress.accumulated_seconds == 0u);

    assert(r1_battery_controller_update(
        &controller, R1_CHARGE_FULL, 4341u, 1u));
    assert(controller.percent == 100u);
    assert(controller.charged_refresh_count == 1u);
    assert(controller.charge_progress.percent == 0u);
    for (uint8_t refresh = 2u; refresh <= 5u; ++refresh) {
        assert(r1_battery_controller_update(
            &controller, R1_CHARGE_FULL, 4341u, 1u));
        assert(controller.charged_refresh_count == refresh);
    }
    assert(r1_battery_controller_update(
        &controller, R1_CHARGE_CHARGING, 4341u, 90u));
    assert(controller.percent == 100u);
    assert(controller.charged_refresh_count == 0u);

    const r1_battery_controller unchanged = controller;
    assert(!r1_battery_controller_update(
        &controller, R1_CHARGE_UNKNOWN, 4000u, 1u));
    assert(memcmp(&controller, &unchanged, sizeof controller) == 0);

    r1_battery_controller_initialize(
        &controller, 1u, 50u, R1_CHARGE_CHARGING);
    assert(r1_battery_controller_update(
        &controller, R1_CHARGE_CHARGING, 4165u, 0u));
    assert(controller.percent == 50u);
    assert(controller.stuck.has_previous_percent);
    assert(r1_battery_controller_update(
        &controller, R1_CHARGE_CHARGING, 4200u, 120u));
    assert(controller.percent == 70u);
    assert(controller.stuck.already_recovered);
    assert(controller.charge_progress.accumulated_seconds == 0u);

    r1_runtime runtime;
    r1_runtime_initialize(&runtime, NULL, NULL);
    r1_runtime_configure_battery(&runtime, 1u);
    assert(r1_runtime_update_battery(
        &runtime, R1_CHARGE_NOT_CHARGING, 3622u, 0u));
    assert(runtime.device.battery_percent == 5u);
    assert(runtime.device.charge == R1_CHARGE_NOT_CHARGING);
    assert(runtime.battery.percent == runtime.device.battery_percent);
    assert(!r1_runtime_update_battery(
        &runtime, R1_CHARGE_UNKNOWN, 4000u, 0u));
    assert(runtime.device.battery_percent == 5u);
}

static void test_pmic_charge_event_policy(void) {
    r1_pmic_charge_observation observation = {
        R1_CHARGE_CHARGING, R1_PMIC_CHARGE_EVENT_SAMPLE, UINT8_C(73),
        UINT16_C(14000), UINT16_C(4210), UINT16_C(5075), UINT8_C(0xa6),
        UINT8_C(1), UINT32_C(0),
    };
    r1_pmic_charge_plan plan;
    assert(r1_pmic_plan_charge_event(&observation, &plan));
    assert(plan.cancel_event_work);
    assert(plan.process_dock_mailbox);
    assert(plan.transition == R1_PMIC_TRANSITION_NONE);
    assert(plan.thermal_action == R1_PMIC_THERMAL_ACTION_SET_TARGET);
    assert(plan.thermal_target_word == R1_PMIC_THERMAL_LOW_TARGET_WORD);
    static const uint8_t expected_status[R1_PMIC_CHARGE_STATUS_BUFFER_SIZE] = {
        0u, 1u, 2u, 73u, 57u, 0x72u, 0x10u, 0xd3u, 0x13u, 0xa6u,
        1u, 0u, 0u, '2', '.', '2', '.', '6', '.', '0', '0', '0', '9', 0u,
    };
    assert(memcmp(plan.dock_status, expected_status,
                  sizeof expected_status) == 0);

    observation.charge = R1_CHARGE_FULL;
    observation.current_thermal_target_word = R1_PMIC_THERMAL_LOW_TARGET_WORD;
    assert(r1_pmic_plan_charge_event(&observation, &plan));
    assert((plan.dock_status[4] & UINT8_C(3)) == UINT8_C(2));
    assert(plan.thermal_action == R1_PMIC_THERMAL_ACTION_NONE);

    observation.charge = R1_CHARGE_NOT_CHARGING;
    observation.event = R1_PMIC_CHARGE_EVENT_PRESERVE_WORK;
    assert(r1_pmic_plan_charge_event(&observation, &plan));
    assert(plan.cancel_event_work);
    assert(!plan.process_dock_mailbox);
    assert(plan.transition == R1_PMIC_TRANSITION_NOT_CHARGING);

    observation.charge = R1_CHARGE_CHARGING;
    assert(r1_pmic_plan_charge_event(&observation, &plan));
    assert(!plan.cancel_event_work);
    assert(!plan.process_dock_mailbox);
    assert(plan.transition == R1_PMIC_TRANSITION_NONE);

    observation.charge = R1_CHARGE_UNKNOWN;
    memset(&plan, 0xa5, sizeof plan);
    const r1_pmic_charge_plan unchanged = plan;
    assert(!r1_pmic_plan_charge_event(&observation, &plan));
    assert(memcmp(&plan, &unchanged, sizeof plan) == 0);
    assert(!r1_pmic_plan_charge_event(NULL, &plan));
    assert(!r1_pmic_plan_charge_event(&observation, NULL));

    observation.charge = R1_CHARGE_CHARGING;
    observation.event = R1_PMIC_CHARGE_EVENT_SAMPLE;
    for (uint32_t raw = 0u; raw <= UINT16_MAX; ++raw) {
        observation.charge_temperature_milliunits = (uint16_t)raw;
        const uint8_t band = (uint8_t)((raw / UINT32_C(1000)) & UINT32_C(0x3f));

        observation.current_thermal_target_word = UINT32_C(0);
        assert(r1_pmic_plan_charge_event(&observation, &plan));
        assert((plan.dock_status[4] >> 2u) == band);
        if (band == 0u) {
            assert(plan.thermal_action == R1_PMIC_THERMAL_ACTION_NONE);
        } else if (band <= 14u) {
            assert(plan.thermal_action == R1_PMIC_THERMAL_ACTION_SET_TARGET);
            assert(plan.thermal_target_word == R1_PMIC_THERMAL_LOW_TARGET_WORD);
        } else if (band <= 44u) {
            assert(plan.thermal_action == R1_PMIC_THERMAL_ACTION_SET_TARGET);
            assert(plan.thermal_target_word == R1_PMIC_THERMAL_MID_TARGET_WORD);
        } else {
            assert(plan.thermal_action ==
                   R1_PMIC_THERMAL_ACTION_WRITE_LIMIT_REGISTER);
            assert(plan.thermal_register == R1_PMIC_THERMAL_LIMIT_REGISTER);
            assert(plan.thermal_register_value == R1_PMIC_THERMAL_LIMIT_VALUE);
        }

        observation.current_thermal_target_word =
            band <= 14u ? R1_PMIC_THERMAL_LOW_TARGET_WORD
                        : R1_PMIC_THERMAL_MID_TARGET_WORD;
        assert(r1_pmic_plan_charge_event(&observation, &plan));
        if (band >= 1u && band <= 44u) {
            assert(plan.thermal_action == R1_PMIC_THERMAL_ACTION_NONE);
        }
    }
}

static void test_pmic_charged_notification_policy(void) {
    r1_pmic_charged_observation observation = {
        UINT8_C(0), R1_CHARGE_CHARGING, UINT16_C(49), UINT16_C(4199),
        R1_CHARGE_CHARGING, true, UINT8_C(0), R1_CHARGE_CHARGING,
        UINT8_C(7), UINT8_C(9),
    };
    r1_pmic_charged_plan plan;

    assert(r1_pmic_plan_charged_notification(&observation, &plan));
    assert(plan.retry_counter == 1u);
    assert(plan.pulse_recovery_pin);
    assert(plan.recovery_pulse_milliseconds ==
           R1_PMIC_CHARGED_RECOVERY_PULSE_MS);
    assert(plan.schedule_retry);
    assert(plan.retry_delay_milliseconds ==
           R1_PMIC_CHARGED_RETRY_DELAY_MS);
    assert(!plan.cancel_retry_work);
    assert(!plan.inspect_interrupt_status);

    observation.retry_counter = R1_PMIC_CHARGED_RETRY_MAX_OLD_COUNT;
    assert(r1_pmic_plan_charged_notification(&observation, &plan));
    assert(plan.retry_counter == 13u);
    assert(plan.schedule_retry);
    observation.retry_counter = 13u;
    assert(r1_pmic_plan_charged_notification(&observation, &plan));
    assert(plan.retry_counter == 0u);
    assert(!plan.schedule_retry);
    assert(plan.inspect_interrupt_status);
    assert(plan.cancel_retry_work);
    assert(plan.read_mailbox_control);
    assert(plan.invoke_charge_event);
    assert(plan.charge_event == 7u);
    assert(plan.schedule_post_charge);
    assert(plan.post_charge_delay_milliseconds ==
           R1_PMIC_CHARGED_POST_DELAY_MS);
    assert(plan.invoke_post_charge_device_callback);

    observation.retry_counter = UINT8_MAX;
    assert(r1_pmic_plan_charged_notification(&observation, &plan));
    assert(plan.retry_counter == 0u);
    assert(!plan.schedule_retry);
    assert(plan.invoke_charge_event);

    observation.retry_counter = R1_PMIC_CHARGED_RETRY_MARKER;
    observation.marker_charge = R1_CHARGE_NOT_CHARGING;
    assert(r1_pmic_plan_charged_notification(&observation, &plan));
    assert(plan.retry_counter == 0u);
    assert(plan.cancel_retry_work);
    assert(plan.thread_flags_to_set == R1_PMIC_CHARGED_THREAD_FLAG);
    assert(!plan.inspect_interrupt_status);
    assert(!plan.invoke_charge_event);

    observation.marker_charge = R1_CHARGE_CHARGING;
    observation.retry_charge = R1_CHARGE_FULL;
    observation.interrupt_status = R1_PMIC_CHARGED_IT_TOUCH_CLOSE_MASK;
    observation.mailbox_control_first_status = 0u;
    observation.mailbox_control_second_status = UINT8_C(11);
    assert(r1_pmic_plan_charged_notification(&observation, &plan));
    assert(plan.retry_counter == 0u);
    assert(plan.close_touch_source_one);
    assert(plan.read_mailbox_control);
    assert(plan.enable_mailbox);
    assert(plan.reread_mailbox_control);
    assert(plan.charge_event == 11u);

    observation.retry_counter = 3u;
    observation.retry_charge = R1_CHARGE_NOT_CHARGING;
    observation.interrupt_status = 0u;
    observation.mailbox_charge = R1_CHARGE_NOT_CHARGING;
    assert(r1_pmic_plan_charged_notification(&observation, &plan));
    /* The recovered low-current not-charging branch retains the increment. */
    assert(plan.retry_counter == 4u);
    assert(plan.cancel_retry_work);
    assert(plan.inspect_interrupt_status);
    assert(plan.invoke_charge_event);
    assert(plan.charge_event == 0u);
    assert(!plan.read_mailbox_control);
    assert(!plan.schedule_post_charge);

    observation.current_sense_millivolts =
        R1_PMIC_CHARGED_CURRENT_THRESHOLD_MV;
    observation.retry_charge = R1_CHARGE_CHARGING;
    observation.mailbox_charge = R1_CHARGE_CHARGING;
    observation.interrupt_status_read_succeeded = false;
    observation.mailbox_control_first_status = 0u;
    observation.mailbox_control_second_status = UINT8_C(12);
    assert(r1_pmic_plan_charged_notification(&observation, &plan));
    assert(plan.retry_counter == 0u);
    assert(!plan.close_touch_source_one);
    assert(plan.enable_mailbox);
    assert(plan.reread_mailbox_control);
    assert(plan.charge_event == 12u);

    observation.current_sense_millivolts = 0u;
    observation.battery_millivolts = R1_PMIC_CHARGED_BATTERY_THRESHOLD_MV;
    assert(r1_pmic_plan_charged_notification(&observation, &plan));
    assert(plan.retry_counter == 0u);
    assert(!plan.schedule_retry);

    memset(&plan, 0xa5, sizeof plan);
    const r1_pmic_charged_plan unchanged = plan;
    assert(!r1_pmic_plan_charged_notification(NULL, &plan));
    assert(memcmp(&plan, &unchanged, sizeof plan) == 0);
    assert(!r1_pmic_plan_charged_notification(&observation, NULL));
}

typedef struct {
    uint8_t buffer[64u];
    size_t requested_bytes;
    size_t sent_bytes;
    uint16_t session;
    unsigned release_count;
    bool allocation_succeeds;
    int send_result;
} protocol_response_trace;

static void *protocol_response_allocate(void *context, size_t bytes) {
    protocol_response_trace *trace = context;
    trace->requested_bytes = bytes;
    return trace->allocation_succeeds && bytes <= sizeof trace->buffer
        ? trace->buffer : NULL;
}

static void protocol_response_release(void *context, void *allocation) {
    protocol_response_trace *trace = context;
    assert(allocation == trace->buffer);
    trace->release_count += 1u;
}

static int protocol_response_send(
    void *context, uint16_t session, const uint8_t *bytes, size_t length) {
    protocol_response_trace *trace = context;
    assert(bytes == trace->buffer);
    trace->session = session;
    trace->sent_bytes = length;
    return trace->send_result;
}

static void test_protocol_response_orchestration(void) {
    static const uint8_t payload[] = {0xaau, 0xbbu, 0xccu};
    const r1_response_header header = {
        .status = 3u,
        .module = 1u,
        .command = 4u,
        .subcommand = 5u,
        .serial = UINT16_C(0x1234),
    };
    protocol_response_trace trace = {.allocation_succeeds = true};
    assert(r1_protocol_send_response(
               UINT16_C(0x0042), true, false, &header, 100u,
               NULL, payload, sizeof payload, protocol_response_allocate,
               protocol_response_release, protocol_response_send, &trace)
           == R1_RESPONSE_SENT);
    assert(trace.requested_bytes == 15u && trace.sent_bytes == 15u);
    assert(trace.session == UINT16_C(0x0042) && trace.release_count == 1u);
    r1_model decoded;
    assert(r1_model_decode(trace.buffer, trace.sent_bytes,
                           R1_CHECKSUM_FIRMWARE_FULL_MODBUS, &decoded) == R1_OK);
    assert(decoded.version == R1_PROTOCOL_VERSION && decoded.module == 1u);
    assert(decoded.module_version == 100u && decoded.status == 3u);
    assert(decoded.command == 4u && decoded.subcommand == 5u);
    assert(decoded.serial == UINT16_C(0x1234));
    assert(decoded.payload_length == sizeof payload);
    assert(memcmp(decoded.payload, payload, sizeof payload) == 0);

    assert(r1_protocol_send_response(
               1u, false, false, &header, 100u, NULL, NULL, 0u,
               protocol_response_allocate, protocol_response_release,
               protocol_response_send, &trace) == R1_RESPONSE_NO_ACTIVE_LINK);
    trace.allocation_succeeds = false;
    assert(r1_protocol_send_response(
               1u, true, false, &header, 100u, NULL, NULL, 0u,
               protocol_response_allocate, protocol_response_release,
               protocol_response_send, &trace) == R1_RESPONSE_ALLOCATION_FAILED);
    trace.allocation_succeeds = true;
    trace.send_result = 7;
    assert(r1_protocol_send_response(
               1u, false, true, &header, 100u, NULL, NULL, 0u,
               protocol_response_allocate, protocol_response_release,
               protocol_response_send, &trace) == R1_RESPONSE_TRANSPORT_FAILED);
    assert(trace.release_count == 2u);
    assert(r1_protocol_send_response(
               1u, true, false, NULL, 100u, NULL, NULL, 0u,
               protocol_response_allocate, protocol_response_release,
               protocol_response_send, &trace) == R1_RESPONSE_INVALID_ARGUMENT);
    r1_response_header invalid = header;
    invalid.module = 4u;
    assert(r1_protocol_send_response(
               1u, true, false, &invalid, 100u, NULL, NULL, 0u,
               protocol_response_allocate, protocol_response_release,
               protocol_response_send, &trace) == R1_RESPONSE_INVALID_ARGUMENT);

    r1_response_header generated = header;
    generated.status = 0u;
    uint16_t next_serial = UINT16_C(0x0040);
    trace.send_result = 0;
    assert(r1_protocol_send_response(
               1u, true, false, &generated, 100u, &next_serial, NULL, 0u,
               protocol_response_allocate, protocol_response_release,
               protocol_response_send, &trace) == R1_RESPONSE_SENT);
    assert(next_serial == UINT16_C(0x0041));
    assert(r1_model_decode(trace.buffer, trace.sent_bytes,
                           R1_CHECKSUM_FIRMWARE_FULL_MODBUS, &decoded) == R1_OK);
    assert(decoded.serial == UINT16_C(0x0040));
    assert(r1_protocol_send_response(
               1u, true, false, &generated, 100u, NULL, NULL, 0u,
               protocol_response_allocate, protocol_response_release,
               protocol_response_send, &trace) == R1_RESPONSE_INVALID_ARGUMENT);
}

static void test_model_round_trip(void) {
    static const uint8_t payload[] = {1u, 2u, 3u, 4u};
    const r1_model source = {100u, 1u, 100u, UINT16_C(0x1234), 2u, 0u, 5u,
                             payload, sizeof payload};
    uint8_t encoded[64u];
    size_t written = 0u;
    assert(r1_model_encode(&source, R1_CHECKSUM_PHONE_COMPACT_CCITT,
                           encoded, sizeof encoded, &written) == R1_OK);
    r1_model decoded;
    assert(r1_model_decode(encoded, written, R1_CHECKSUM_PHONE_COMPACT_CCITT,
                           &decoded) == R1_OK);
    assert(decoded.serial == UINT16_C(0x1234));
    assert(decoded.payload_length == sizeof payload);
    encoded[13] ^= 1u;
    assert(r1_model_decode(encoded, written, R1_CHECKSUM_PHONE_COMPACT_CCITT,
                           &decoded) == R1_ERROR_CHECKSUM);
}

static void test_physical_wire_vectors(void) {
    static const uint8_t query[] = {
        0x00u, 0xc0u, 0xfdu, 0x20u, 0xf6u,
        0x64u, 0x02u, 0x64u, 0x14u, 0x00u, 0x00u, 0x01u, 0x01u,
        0x0cu, 0x00u, 0x0eu, 0x99u,
    };
    static const uint8_t response[] = {
        0x00u, 0x55u, 0x0eu, 0xb7u, 0x64u,
        0x64u, 0x02u, 0x64u, 0x14u, 0x00u, 0x03u, 0x01u, 0x01u,
        0x0cu, 0x00u, 0xafu, 0xdfu,
    };
    static const uint8_t acknowledgement[] = {
        0x00u, 0xa7u, 0x6cu, 0x09u, 0x38u,
        0x64u, 0x01u, 0x64u, 0x16u, 0x00u, 0x01u, 0x00u, 0x7eu,
        0x16u, 0x00u, 0x60u, 0xbbu,
        0x02u, 0x01u, 0x01u, 0x00u, 0x2fu, 0x00u, 0x00u, 0x00u, 0x00u, 0x00u,
    };
    r1_reassembler reassembler;
    r1_model model;

    r1_reassembler_reset(&reassembler);
    assert(r1_reassembler_feed(&reassembler, query, sizeof query, NULL)
           == R1_REASSEMBLY_COMPLETE);
    assert(r1_model_decode(reassembler.bytes, reassembler.length,
                           R1_CHECKSUM_PHONE_COMPACT_CCITT, &model) == R1_OK);
    assert(model.serial == UINT16_C(0x14));
    assert(model.module == 2u && model.command == 1u && model.subcommand == 1u);
    assert(model.payload_length == 0u);

    r1_reassembler_reset(&reassembler);
    assert(r1_reassembler_feed(&reassembler, response, sizeof response, NULL)
           == R1_REASSEMBLY_COMPLETE);
    assert(r1_model_decode(reassembler.bytes, reassembler.length,
                           R1_CHECKSUM_FIRMWARE_FULL_MODBUS, &model) == R1_OK);
    assert(model.serial == UINT16_C(0x14));
    assert(model.status == 3u && model.payload_length == 0u);

    r1_reassembler_reset(&reassembler);
    assert(r1_reassembler_feed(&reassembler, acknowledgement, sizeof acknowledgement, NULL)
           == R1_REASSEMBLY_COMPLETE);
    assert(r1_model_decode(reassembler.bytes, reassembler.length,
                           R1_CHECKSUM_PHONE_COMPACT_CCITT, &model) == R1_OK);
    assert(model.serial == UINT16_C(0x16) && model.subcommand == 0x7eu);
    assert(model.payload_length == 10u && model.payload[4] == 0x2fu);

    r1_fragment_set encoded;
    assert(r1_fragment_message(query + R1_FRAGMENT_HEADER_LENGTH,
                               sizeof query - R1_FRAGMENT_HEADER_LENGTH, &encoded) == R1_OK);
    assert(encoded.count == 1u && encoded.fragments[0].length == sizeof query);
    for (size_t index = 0u; index < sizeof query; ++index) {
        assert(encoded.fragments[0].bytes[index] == query[index]);
    }
}

static void test_fragments(void) {
    uint8_t logical[478u];
    for (size_t index = 0u; index < sizeof logical; ++index) {
        logical[index] = (uint8_t)index;
    }
    r1_fragment_set fragments;
    assert(r1_fragment_message(logical, sizeof logical, &fragments) == R1_OK);
    assert(fragments.count == 3u);
    assert(fragments.fragments[0].bytes[0] == 2u);
    assert(fragments.fragments[2].bytes[0] == 0u);
    assert(fragments.fragments[2].length == R1_FRAGMENT_HEADER_LENGTH);

    r1_reassembler reassembler;
    r1_reassembler_reset(&reassembler);
    r1_error error = R1_OK;
    for (size_t index = 0u; index + 1u < fragments.count; ++index) {
        assert(r1_reassembler_feed(&reassembler, fragments.fragments[index].bytes,
                                   fragments.fragments[index].length, &error)
               == R1_REASSEMBLY_WAITING);
    }
    assert(r1_reassembler_feed(&reassembler, fragments.fragments[2].bytes,
                               fragments.fragments[2].length, &error)
           == R1_REASSEMBLY_COMPLETE);
    assert(reassembler.length == sizeof logical);
    for (size_t index = 0u; index < sizeof logical; ++index) {
        assert(reassembler.bytes[index] == logical[index]);
    }
}

static void test_fragment_boundaries(void) {
    static const size_t lengths[] = {0u, 1u, 238u, 239u, 240u, 4062u};
    uint8_t logical[R1_LOGICAL_SAFE_OUTBOUND_MAX];
    for (size_t index = 0u; index < sizeof logical; ++index) {
        logical[index] = (uint8_t)(index * 29u + 7u);
    }
    for (size_t test = 0u; test < sizeof lengths / sizeof lengths[0]; ++test) {
        r1_fragment_set fragments;
        const uint8_t *source = lengths[test] == 0u ? NULL : logical;
        assert(r1_fragment_message(source, lengths[test], &fragments) == R1_OK);
        r1_reassembler reassembler;
        r1_reassembler_reset(&reassembler);
        for (size_t index = 0u; index < fragments.count; ++index) {
            const r1_reassembly_status expected = index + 1u == fragments.count
                ? R1_REASSEMBLY_COMPLETE : R1_REASSEMBLY_WAITING;
            assert(r1_reassembler_feed(&reassembler, fragments.fragments[index].bytes,
                                       fragments.fragments[index].length, NULL) == expected);
        }
        assert(reassembler.length == lengths[test]);
        for (size_t index = 0u; index < lengths[test]; ++index) {
            assert(reassembler.bytes[index] == logical[index]);
        }
    }
    r1_fragment_set rejected;
    assert(r1_fragment_message(logical, R1_LOGICAL_SAFE_OUTBOUND_MAX + 1u, &rejected)
           == R1_ERROR_LENGTH);

    uint8_t two_fragment_message[240u];
    for (size_t index = 0u; index < sizeof two_fragment_message; ++index) {
        two_fragment_message[index] = (uint8_t)(index * 11u + 3u);
    }
    r1_fragment_set malformed;
    assert(r1_fragment_message(two_fragment_message, sizeof two_fragment_message,
                               &malformed) == R1_OK);
    r1_reassembler hardened;
    r1_reassembler_reset(&hardened);
    r1_error hardening_error = R1_OK;
    assert(r1_reassembler_feed(&hardened, malformed.fragments[0].bytes,
                               malformed.fragments[0].length, &hardening_error)
           == R1_REASSEMBLY_WAITING);
    assert(r1_reassembler_feed(&hardened, malformed.fragments[0].bytes,
                               malformed.fragments[0].length, &hardening_error)
           == R1_REASSEMBLY_REJECTED);
    assert(hardening_error == R1_ERROR_SEQUENCE && !hardened.active);

    r1_reassembler_reset(&hardened);
    assert(r1_reassembler_feed(&hardened, malformed.fragments[0].bytes,
                               malformed.fragments[0].length, &hardening_error)
           == R1_REASSEMBLY_WAITING);
    malformed.fragments[1].bytes[1] ^= UINT8_C(0x01);
    assert(r1_reassembler_feed(&hardened, malformed.fragments[1].bytes,
                               malformed.fragments[1].length, &hardening_error)
           == R1_REASSEMBLY_REJECTED);
    assert(hardening_error == R1_ERROR_SEQUENCE && !hardened.active);
}

static r1_model request(uint8_t status, uint8_t subcommand,
                        const uint8_t *payload, size_t length) {
    const r1_model value = {100u, 1u, 100u, 7u, status, 0u, subcommand,
                            payload, length};
    return value;
}

static void test_dispatch(void) {
    r1_device_state state;
    r1_state_initialize(&state);
    r1_session session = {true, true, true, R1_ROLE_PHONE};
    r1_dispatch_result result;

    r1_model input = request(0u, 1u, NULL, 0u);
    assert(r1_dispatch(&state, &session, &input, &result) == R1_OK);
    assert(result.count == 1u);
    r1_model response;
    assert(r1_model_decode(result.models[0], result.lengths[0],
                           R1_CHECKSUM_FIRMWARE_FULL_MODBUS, &response) == R1_OK);
    assert(response.payload_length == 7u);
    assert(response.payload[0] == 100u);
    assert(response.payload[1] == R1_CHARGE_NOT_CHARGING);
    assert(response.status == 3u);

    static const uint8_t short_time[] = {0u, 0u, 0u, 0u, 0u};
    input = request(2u, 5u, short_time, sizeof short_time);
    assert(r1_dispatch(&state, &session, &input, &result) == R1_OK);
    assert(state.unix_seconds == 0u);
    assert(r1_model_decode(result.models[0], result.lengths[0],
                           R1_CHECKSUM_FIRMWARE_FULL_MODBUS, &response) == R1_OK);
    assert(((response.status >> 2u) & 3u) == 1u);

    static const uint8_t time_payload[] = {0xc4u, 0xffu, 0x78u, 0x56u, 0x34u, 0x12u};
    input = request(2u, 5u, time_payload, sizeof time_payload);
    assert(r1_dispatch(&state, &session, &input, &result) == R1_OK);
    assert(state.timezone_minutes_raw == UINT16_C(0xffc4));
    assert(state.unix_seconds == UINT32_C(0x12345678));

    session.authorized = false;
    input = request(0u, 0x10u, NULL, 0u);
    assert(r1_dispatch(&state, &session, &input, &result) == R1_ERROR_UNAUTHORIZED);

    session = (r1_session){false, false, false, R1_ROLE_UNASSIGNED};
    static const uint8_t phone_role[] = {1u};
    input = request(0u, 0x08u, phone_role, sizeof phone_role);
    assert(r1_dispatch(&state, &session, &input, &result) == R1_OK);
    assert(session.role == R1_ROLE_PHONE);
    assert(r1_model_decode(result.models[0], result.lengths[0],
                           R1_CHECKSUM_FIRMWARE_FULL_MODBUS, &response) == R1_OK);
    assert(response.payload_length == 1u && response.payload[0] == 0u);

    session.role = R1_ROLE_UNASSIGNED;
    static const uint8_t unknown_role[] = {2u};
    input = request(0u, 0x08u, unknown_role, sizeof unknown_role);
    assert(r1_dispatch(&state, &session, &input, &result) == R1_OK);
    assert(session.role == R1_ROLE_UNASSIGNED);
    assert(r1_model_decode(result.models[0], result.lengths[0],
                           R1_CHECKSUM_FIRMWARE_FULL_MODBUS, &response) == R1_OK);
    assert(response.payload_length == 1u && response.payload[0] == 0u);
}

static void test_legacy_command_routing(void) {
    typedef struct {
        uint8_t opcode;
        r1_legacy_command_route route;
    } expected_route;
    static const expected_route routes[] = {
        {0x11u, R1_LEGACY_COMMAND_ROUTE_0X11},
        {0x12u, R1_LEGACY_COMMAND_ROUTE_0X12},
        {0x21u, R1_LEGACY_COMMAND_ROUTE_0X21},
        {0x22u, R1_LEGACY_COMMAND_ROUTE_0X22},
        {0x23u, R1_LEGACY_COMMAND_ROUTE_0X23},
        {0x24u, R1_LEGACY_COMMAND_ROUTE_0X24},
        {0x34u, R1_LEGACY_COMMAND_ROUTE_0X34},
        {0x37u, R1_LEGACY_COMMAND_ROUTE_0X37},
        {0x40u, R1_LEGACY_COMMAND_ROUTE_0X40},
        {0x52u, R1_LEGACY_COMMAND_ROUTE_0X52},
        {0x53u, R1_LEGACY_COMMAND_ROUTE_0X53},
        {0x54u, R1_LEGACY_COMMAND_ROUTE_0X54},
        {0x55u, R1_LEGACY_COMMAND_ROUTE_0X55},
        {0x56u, R1_LEGACY_COMMAND_ROUTE_0X56},
        {0x57u, R1_LEGACY_COMMAND_ROUTE_0X57},
        {0x85u, R1_LEGACY_COMMAND_ROUTE_0X85},
        {0x88u, R1_LEGACY_COMMAND_ROUTE_PAIR_AUTH_0X88},
        {0x89u, R1_LEGACY_COMMAND_ROUTE_0X89},
        {0x8au, R1_LEGACY_COMMAND_ROUTE_0X8A},
        {0x91u, R1_LEGACY_COMMAND_ROUTE_0X91},
        {0x94u, R1_LEGACY_COMMAND_ROUTE_0X94},
        {0x95u, R1_LEGACY_COMMAND_ROUTE_0X95},
        {0xf2u, R1_LEGACY_COMMAND_ROUTE_0XF2},
    };
    uint8_t frame[R1_LEGACY_COMMAND_WORKSPACE_SIZE] = {0xa5u, 0x5au, 0u};
    uint8_t workspace[R1_LEGACY_COMMAND_WORKSPACE_SIZE];
    r1_legacy_command_route route = R1_LEGACY_COMMAND_ROUTE_NONE;

    for (size_t index = 0u; index < sizeof routes / sizeof routes[0]; ++index) {
        frame[R1_LEGACY_COMMAND_OPCODE_OFFSET] = routes[index].opcode;
        memset(workspace, 0xcc, sizeof workspace);
        assert(r1_legacy_command_route_frame(
                   frame, 3u, workspace, sizeof workspace, &route) == R1_OK);
        assert(route == routes[index].route);
        assert(memcmp(workspace, frame, 3u) == 0);
        for (size_t offset = 3u; offset < sizeof workspace; ++offset) {
            assert(workspace[offset] == 0u);
        }
    }

    frame[R1_LEGACY_COMMAND_OPCODE_OFFSET] = 0x00u;
    route = R1_LEGACY_COMMAND_ROUTE_0X11;
    assert(r1_legacy_command_route_frame(
               frame, 3u, workspace, sizeof workspace, &route) ==
           R1_ERROR_UNSUPPORTED);
    assert(route == R1_LEGACY_COMMAND_ROUTE_NONE);

    frame[R1_LEGACY_COMMAND_OPCODE_OFFSET] = 0x11u;
    assert(r1_legacy_command_route_frame(
               frame, sizeof frame, workspace, sizeof workspace, &route) == R1_OK);
    assert(r1_legacy_command_route_frame(
               frame, 2u, workspace, sizeof workspace, &route) == R1_ERROR_LENGTH);
    assert(r1_legacy_command_route_frame(
               frame, sizeof frame + 1u, workspace, sizeof workspace, &route) ==
           R1_ERROR_LENGTH);
    assert(r1_legacy_command_route_frame(
               frame, 3u, workspace, sizeof workspace - 1u, &route) ==
           R1_ERROR_LENGTH);
    assert(r1_legacy_command_route_frame(
               NULL, 3u, workspace, sizeof workspace, &route) == R1_ERROR_ARGUMENT);
    assert(r1_legacy_command_route_frame(
               frame, 3u, NULL, sizeof workspace, &route) == R1_ERROR_ARGUMENT);
    assert(r1_legacy_command_route_frame(
               frame, 3u, workspace, sizeof workspace, NULL) == R1_ERROR_ARGUMENT);
}

static void test_legacy_device_info_builder(void) {
    r1_legacy_device_info_sources sources = {
        .product_bsn_length = 21u,
        .product_sn_length = 15u,
        .configuration_byte_0x70 = 0x70u,
        .configuration_word_0x74 = UINT32_C(0x12345678),
        .configuration_byte_0x78 = 0x78u,
    };
    for (size_t index = 0u; index < R1_LEGACY_PRODUCT_BSN_BYTES; ++index) {
        sources.product_bsn[index] = (uint8_t)(0x20u + index);
        sources.product_sn[index] = (uint8_t)(0x60u + index);
    }
    for (size_t index = 0u; index < 6u; ++index) {
        sources.temperature_calibration[index] = (uint8_t)(0xa0u + index);
        sources.accelerometer_calibration[index] = (uint8_t)(0xb0u + index);
    }
    for (size_t index = 0u; index < 20u; ++index) {
        sources.device_identity[index] = (uint8_t)(0xc0u + index);
    }

    uint8_t prefix[4u] = {0x11u, 0x22u, 0x33u, 0u};
    r1_legacy_device_info_response response;
    assert(r1_legacy_device_info_build(prefix, &sources, &response) == R1_OK);
    assert(response.length == 25u && memcmp(response.bytes, prefix, 4u) == 0);
    assert(memcmp(response.bytes + 4u, sources.product_bsn, 21u) == 0);

    prefix[3] = 1u;
    assert(r1_legacy_device_info_build(prefix, &sources, &response) == R1_OK);
    assert(response.length == 25u);
    assert(memcmp(response.bytes + 4u, sources.product_sn, 15u) == 0);
    for (size_t index = 19u; index < 25u; ++index) {
        assert(response.bytes[index] == 0u);
    }
    sources.product_sn_length = UINT8_MAX;
    assert(r1_legacy_device_info_build(prefix, &sources, &response) == R1_OK);
    for (size_t index = 4u; index < 19u; ++index) {
        assert(response.bytes[index] == UINT8_MAX);
    }

    prefix[3] = 2u;
    assert(r1_legacy_device_info_build(prefix, &sources, &response) == R1_OK);
    assert(response.length == 13u);
    assert(memcmp(response.bytes + 4u, sources.temperature_calibration, 6u) == 0);
    assert(memcmp(response.bytes + 10u, sources.accelerometer_calibration, 6u) == 0);

    prefix[3] = 3u;
    assert(r1_legacy_device_info_build(prefix, &sources, &response) == R1_OK);
    assert(response.length == 43u);
    for (size_t index = 4u; index < 40u; ++index) {
        assert(response.bytes[index] == UINT8_MAX);
    }
    assert(response.bytes[40] == 0x70u && response.bytes[41] == 0x78u &&
           response.bytes[42] == 0x78u);

    prefix[3] = 4u;
    assert(r1_legacy_device_info_build(prefix, &sources, &response) == R1_OK);
    assert(response.length == 24u);
    assert(memcmp(response.bytes + 4u, sources.device_identity, 20u) == 0);

    prefix[3] = 5u;
    assert(r1_legacy_device_info_build(prefix, &sources, &response) ==
           R1_ERROR_UNSUPPORTED);
    assert(response.length == 0u);
    assert(r1_legacy_device_info_build(NULL, &sources, &response) ==
           R1_ERROR_ARGUMENT);
}

static void test_ati_calibration_command(void) {
    const r1_ati_calibration_observation observation = {
        true, 0x12u, 0x34u, 9u
    };
    r1_ati_calibration_plan plan;

    assert(r1_ati_calibration_plan_command(
               0u, 3u, 0u, &observation, &plan) == R1_OK);
    assert(plan.action == R1_ATI_CALIBRATION_ACTION_SET_RAW_PRINT_LEVEL);
    assert(plan.action_argument_0 == 3u && plan.response_status == 5u);

    assert(r1_ati_calibration_plan_command(
               1u, 0u, 0u, &observation, &plan) == R1_OK);
    assert(plan.action == R1_ATI_CALIBRATION_ACTION_NONE &&
           plan.event_flags == UINT32_C(0x40));
    assert(r1_ati_calibration_plan_command(
               2u, 0u, 0u, &observation, &plan) == R1_OK);
    assert(plan.event_flags == UINT32_C(0x80));

    static const uint32_t first_words[] = {1u, 2u, 3u, 4u};
    static const uint32_t second_words[] = {1u, 2u, 1u, 1u};
    for (uint8_t subcommand = 3u; subcommand <= 6u; ++subcommand) {
        assert(r1_ati_calibration_plan_command(
                   subcommand, 0x80u, 0x55u, &observation, &plan) == R1_OK);
        const size_t index = (size_t)(subcommand - 3u);
        assert(plan.action == R1_ATI_CALIBRATION_ACTION_SEND_CONFIGURATION);
        assert(plan.configuration_word_1 == first_words[index]);
        assert(plan.configuration_word_2 == second_words[index]);
        assert(plan.event_flags == (UINT32_C(0x100) << index));
        assert(plan.action_argument_0 == (subcommand == 6u ? 1u : 0x80u));
        assert(plan.action_argument_1 == (subcommand == 4u ? 0x55u : 0u));
    }

    assert(r1_ati_calibration_plan_command(
               7u, 0u, 0u, &observation, &plan) == R1_OK);
    assert(plan.action == R1_ATI_CALIBRATION_ACTION_QUERY_CALIBRATION);
    assert(plan.response_status == R1_ATI_CALIBRATION_RESPONSE_STATUS_QUERY);
    assert(plan.response_update_length == 2u &&
           plan.response_update[0] == 0x12u && plan.response_update[1] == 0x34u);
    r1_ati_calibration_observation unavailable = observation;
    unavailable.calibration_available = false;
    assert(r1_ati_calibration_plan_command(
               7u, 0u, 0u, &unavailable, &plan) == R1_OK);
    assert(plan.response_status == R1_ATI_CALIBRATION_RESPONSE_STATUS_DEFAULT);
    assert(plan.response_update_length == 1u &&
           plan.response_update[0] == UINT8_MAX);

    assert(r1_ati_calibration_plan_command(
               8u, 0u, 0u, &observation, &plan) == R1_OK);
    assert(plan.action == R1_ATI_CALIBRATION_ACTION_OPEN_TOUCH_SOURCE &&
           plan.action_argument_0 == 2u);
    assert(r1_ati_calibration_plan_command(
               9u, 0u, 0u, &observation, &plan) == R1_OK);
    assert(plan.action == R1_ATI_CALIBRATION_ACTION_CLOSE_TOUCH_SOURCE &&
           plan.action_argument_0 == 2u);
    assert(r1_ati_calibration_plan_command(
               10u, 0u, 0u, &observation, &plan) == R1_OK);
    assert(plan.action == R1_ATI_CALIBRATION_ACTION_READ_RING_SIZE);
    assert(plan.response_update_length == 1u && plan.response_update[0] == 9u);

    assert(r1_ati_calibration_plan_command(
               UINT8_MAX, 0u, 0u, &observation, &plan) == R1_OK);
    assert(plan.action == R1_ATI_CALIBRATION_ACTION_NONE &&
           plan.event_flags == 0u && plan.response_update_length == 0u);
    assert(r1_ati_calibration_plan_command(
               0u, 0u, 0u, NULL, &plan) == R1_ERROR_ARGUMENT);
    assert(r1_ati_calibration_plan_command(
               0u, 0u, 0u, &observation, NULL) == R1_ERROR_ARGUMENT);
}

static void test_health_history_routing(void) {
    typedef struct {
        uint8_t command;
        uint8_t subcommand;
        uint8_t metric;
        uint8_t kind;
        uint32_t residue;
        r1_health_history_action action;
    } expected_route;
    static const expected_route routed[] = {
        {0x01u, 0x01u, 0u, 1u, 0u, R1_HEALTH_HISTORY_HEART_RATE_DAILY},
        {0x01u, 0x02u, 0u, 0u, 1u, R1_HEALTH_HISTORY_HEART_RATE_POINT},
        {0x02u, 0x01u, 1u, 1u, 3u, R1_HEALTH_HISTORY_SPO2_DAILY},
        {0x02u, 0x02u, 1u, 0u, 3u, R1_HEALTH_HISTORY_SPO2_POINT},
        {0x04u, 0x01u, 5u, 1u, 0u, R1_HEALTH_HISTORY_HRV_DAILY},
        {0x04u, 0x02u, 5u, 0u, 7u, R1_HEALTH_HISTORY_HRV_POINT},
        {0x05u, 0x01u, 4u, 1u, 9u, R1_HEALTH_HISTORY_ACTIVITY_DAILY},
        {0x05u, 0x02u, 4u, 0u, 7u, R1_HEALTH_HISTORY_ACTIVITY_REFRESH},
        {0x06u, 0x01u, 6u, 1u, 11u, R1_HEALTH_HISTORY_SLEEP_DAILY},
    };
    for (size_t index = 0u; index < sizeof routed / sizeof routed[0]; ++index) {
        r1_health_history_route route;
        assert(r1_health_history_route_command(
                   routed[index].command, routed[index].subcommand,
                   UINT16_C(0x1234), &route) == R1_OK);
        assert(route.action == routed[index].action);
        assert(route.metric == routed[index].metric);
        assert(route.query_kind == routed[index].kind);
        assert(route.request_serial == UINT16_C(0x1234));
        assert(route.dispatcher_residue == routed[index].residue);
        assert(route.immediate_empty_response == (routed[index].kind == 1u));
        uint8_t event[R1_HEALTH_HISTORY_EVENT_BYTES];
        assert(r1_health_history_encode_event14(&route, event) == R1_OK);
        assert(event[0] == routed[index].metric);
        assert(event[1] == routed[index].kind);
        assert(event[2] == 0x34u && event[3] == 0x12u);
        r1_health_history_route decoded;
        assert(r1_health_history_decode_event14(
                   event, sizeof event, &decoded) == R1_OK);
        assert(decoded.action == routed[index].action);
        assert(decoded.request_serial == UINT16_C(0x1234));
        assert(decoded.dispatcher_residue == routed[index].residue);
    }

    static const uint16_t non_event_keys[] = {
        UINT16_C(0x0103), UINT16_C(0x0203), UINT16_C(0x0403),
        UINT16_C(0x0602), UINT16_C(0x7f01), UINT16_C(0x0301),
    };
    r1_health_history_route route;
    for (size_t index = 0u;
         index < sizeof non_event_keys / sizeof non_event_keys[0]; ++index) {
        assert(r1_health_history_route_command(
                   (uint8_t)(non_event_keys[index] >> 8u),
                   (uint8_t)non_event_keys[index], 0u, &route) ==
               R1_ERROR_UNSUPPORTED);
    }
    static const uint8_t temperature_event[] = {2u, 1u, 1u, 0u, 0u, 0u, 0u, 0u};
    static const uint8_t stress_event[] = {3u, 0u, 1u, 0u, 0u, 0u, 0u, 0u};
    assert(r1_health_history_decode_event14(
               temperature_event, sizeof temperature_event, &route) ==
           R1_ERROR_UNSUPPORTED);
    assert(r1_health_history_decode_event14(
               stress_event, sizeof stress_event, &route) ==
           R1_ERROR_UNSUPPORTED);
    assert(r1_health_history_decode_event14(
               temperature_event, sizeof temperature_event - 1u, &route) ==
           R1_ERROR_LENGTH);
}

typedef struct {
    uint32_t timestamps[2];
    uint8_t buckets[2];
    size_t calls;
} activity_bucket_trace;

static r1_error resolve_activity_bucket(
    void *context, uint32_t timestamp, uint8_t *bucket_index) {
    activity_bucket_trace *trace = context;
    if (trace == NULL || bucket_index == NULL || trace->calls >= 2u) {
        return R1_ERROR_ARGUMENT;
    }
    trace->timestamps[trace->calls] = timestamp;
    *bucket_index = trace->buckets[trace->calls];
    ++trace->calls;
    return R1_OK;
}

static void test_activity_cumulative_counter_service(void) {
    r1_activity_accumulator accumulator;
    r1_activity_accumulator_initialize(&accumulator);
    accumulator.window_published = 1u;
    accumulator.reserved = UINT16_C(0xbeef);
    accumulator.baseline = (r1_activity_cumulative_counters){1000u, 100u, 50u};
    accumulator.current = accumulator.baseline;

    r1_activity_accumulator_result result;
    r1_activity_cumulative_counters counters = {1005u, 102u, 51u};
    assert(r1_activity_accumulator_periodic(
        &accumulator, &counters, 1000u, 0u, 0u, 2u, &result) == R1_OK);
    assert(result.action == R1_ACTIVITY_ACCUMULATOR_EARLY_WINDOW);
    assert(!result.event_ready && accumulator.window_published == 0u);
    assert(accumulator.current.steps == 1005u && accumulator.reserved == 0xbeefu);

    counters = (r1_activity_cumulative_counters){1010u, 103u, 52u};
    assert(r1_activity_accumulator_periodic(
        &accumulator, &counters, 1195u, 0u, 0u, 2u, &result) == R1_OK);
    assert(result.event_ready && result.event.all_kilocalories == 3u);
    assert(result.event.active_kilocalories == 2u && result.event.steps == 10u);
    assert(result.event.duration_seconds == 595u && result.event.timestamp == 1195u);
    assert(accumulator.window_published == 1u && accumulator.baseline.steps == 1010u);

    counters = (r1_activity_cumulative_counters){1012u, 104u, 53u};
    assert(r1_activity_accumulator_periodic(
        &accumulator, &counters, 1196u, 0u, 0u, 2u, &result) == R1_OK);
    assert(result.action == R1_ACTIVITY_ACCUMULATOR_WINDOW_ALREADY_PUBLISHED);
    assert(!result.event_ready && accumulator.current.steps == 1012u);
    assert(r1_activity_accumulator_refresh(
        &accumulator, 1301u, 0u, 2u, &result) == R1_OK);
    assert(result.event_ready && result.event.steps == 2u);
    assert(result.event.all_kilocalories == 1u &&
           result.event.active_kilocalories == 1u);
    assert(result.event.duration_seconds == 101u);
    assert(accumulator.window_published == 1u);

    r1_activity_accumulator_initialize(&accumulator);
    accumulator.baseline = (r1_activity_cumulative_counters){100u, 10u, 10u};
    accumulator.current = accumulator.baseline;
    counters = (r1_activity_cumulative_counters){99u, 9u, 9u};
    assert(r1_activity_accumulator_periodic(
        &accumulator, &counters, 1795u, 0u, 0u, 2u, &result) == R1_OK);
    assert(result.action == R1_ACTIVITY_ACCUMULATOR_REBASED_COUNTER_ROLLBACK);
    assert(!result.event_ready && accumulator.baseline.steps == 99u);
    assert(accumulator.window_published == 1u);

    accumulator.window_published = 1u;
    counters = (r1_activity_cumulative_counters){500u, 40u, 20u};
    assert(r1_activity_accumulator_periodic(
        &accumulator, &counters, 86400u, 86400u, 0u, 2u, &result) == R1_OK);
    assert(result.action == R1_ACTIVITY_ACCUMULATOR_REBASED_DAY_START);
    assert(accumulator.window_published == 0u && accumulator.baseline.steps == 500u);

    r1_activity_accumulator_initialize(&accumulator);
    accumulator.reserved = UINT16_C(0x1234);
    accumulator.baseline = (r1_activity_cumulative_counters){10u, 2u, 1u};
    accumulator.current = (r1_activity_cumulative_counters){20u, 4u, 2u};
    assert(r1_activity_accumulator_refresh(
        &accumulator, 2000u, 0u, 1u, &result) == R1_OK);
    assert(result.action == R1_ACTIVITY_ACCUMULATOR_TRANSITION_GRACE);
    assert(accumulator.transition_pending == 1u &&
           accumulator.transition_started == 2000u);
    assert(r1_activity_accumulator_refresh(
        &accumulator, 2900u, 0u, 1u, &result) == R1_OK);
    assert(result.action == R1_ACTIVITY_ACCUMULATOR_TRANSITION_GRACE);
    assert(accumulator.baseline.steps == 10u);
    assert(r1_activity_accumulator_refresh(
        &accumulator, 2901u, 0u, 1u, &result) == R1_OK);
    assert(result.action == R1_ACTIVITY_ACCUMULATOR_REBASED_TRANSITION_TIMEOUT);
    assert(accumulator.baseline.steps == 20u && accumulator.transition_pending == 0u);
    assert(accumulator.reserved == 0x1234u);

    accumulator.transition_pending = 1u;
    accumulator.baseline = (r1_activity_cumulative_counters){10u, 2u, 1u};
    accumulator.current = (r1_activity_cumulative_counters){20u, 4u, 2u};
    assert(r1_activity_accumulator_refresh(
        &accumulator, 200u, 1u, 2u, &result) == R1_OK);
    assert(result.action == R1_ACTIVITY_ACCUMULATOR_REBASED_UNAVAILABLE);
    assert(accumulator.baseline.steps == 20u && accumulator.transition_pending == 0u);

    accumulator.window_published = 7u;
    accumulator.baseline = (r1_activity_cumulative_counters){0u, 10u, 20u};
    accumulator.current = (r1_activity_cumulative_counters){65537u, 13u, 22u};
    assert(r1_activity_accumulator_refresh(
        &accumulator, 1301u, 0u, 2u, &result) == R1_OK);
    assert(result.event_ready && result.event.steps == 1u);
    assert(result.event.all_kilocalories == 3u &&
           result.event.active_kilocalories == 2u);
    assert(accumulator.window_published == 7u);

    r1_activity_delta_event pending;
    accumulator.baseline = (r1_activity_cumulative_counters){1000u, 100u, 50u};
    accumulator.current = (r1_activity_cumulative_counters){1010u, 103u, 52u};
    assert(r1_activity_accumulator_pending_delta(
        &accumulator, 0u, 2u, &pending) == R1_OK);
    assert(pending.steps == 10u && pending.all_kilocalories == 3u &&
           pending.active_kilocalories == 2u && pending.duration_seconds == 0u &&
           pending.timestamp == 0u);
    assert(r1_activity_accumulator_pending_delta(
        &accumulator, 1u, 2u, &pending) == R1_OK);
    assert(memcmp(&pending, &(r1_activity_delta_event){0}, sizeof pending) == 0);

    const r1_activity_delta_event wire_event = {
        3u, 2u, 100u, 601u, UINT32_C(0x12345678),
    };
    uint8_t wire[R1_ACTIVITY_DELTA_EVENT_BYTES];
    assert(r1_activity_delta_event_encode(&wire_event, wire) == R1_OK);
    static const uint8_t expected_wire[] = {
        0x03u,0x00u, 0x02u,0x00u, 0x64u,0x00u, 0x59u,0x02u,
        0x78u,0x56u,0x34u,0x12u,
    };
    assert(memcmp(wire, expected_wire, sizeof wire) == 0);
    r1_activity_delta_event decoded;
    assert(r1_activity_delta_event_decode(wire, sizeof wire, &decoded) == R1_OK);
    assert(memcmp(&decoded, &wire_event, sizeof decoded) == 0);
    assert(r1_activity_delta_event_decode(wire, sizeof wire - 1u, &decoded) ==
           R1_ERROR_LENGTH);

    r1_activity_history history = {0};
    activity_bucket_trace trace = {{0u, 0u}, {5u, 6u}, 0u};
    r1_activity_delta_consume_result consumed;
    assert(r1_activity_consume_delta_event(
        &history, &wire_event, resolve_activity_bucket, &trace, 0u, 0,
        &consumed) == R1_OK);
    assert(trace.calls == 2u);
    assert(trace.timestamps[0] == UINT32_C(0x1234541f));
    assert(trace.timestamps[1] == UINT32_C(0x12345678));
    assert(consumed.start_bucket == 5u && consumed.end_bucket == 6u &&
           consumed.crossed_bucket_boundary);
    assert(history.buckets[5].steps == 100u &&
           history.buckets[5].active_kilocalories == 2u &&
           history.buckets[5].all_kilocalories == 3u);
    assert(!history.buckets[6].valid);

    const r1_activity_delta_event wrapped = {1021u, 1022u, 3996u, 1u, 1u};
    trace = (activity_bucket_trace){{0u, 0u}, {5u, 5u}, 0u};
    assert(r1_activity_consume_delta_event(
        &history, &wrapped, resolve_activity_bucket, &trace, 0u, 0,
        &consumed) == R1_OK);
    assert(consumed.stored_steps == 0u);
    assert(consumed.stored_active_kilocalories == 0u);
    assert(consumed.stored_all_kilocalories == 0u);
    assert(!history.buckets[5].valid);
}

static void test_health_histories_and_dispatch(void) {
    r1_device_state state;
    r1_state_initialize(&state);
    assert(r1_health_record_u8(&state.health.heart_rate, 7u, 70u, 110u, 100u, -300)
           == R1_OK);
    assert(r1_health_record_u8(&state.health.heart_rate, 7u, 80u, 120u, 100u, -300)
           == R1_OK);
    assert(r1_health_record_u8(&state.health.heart_rate, 9u, 90u, 130u, 100u, -300)
           == R1_OK);
    uint8_t daily[R1_HEALTH_DAILY_U8_MAX_BYTES];
    size_t written = 0u;
    assert(r1_health_encode_daily_u8(&state.health.heart_rate,
                                     daily, sizeof daily, &written) == R1_OK);
    static const uint8_t expected[] = {
        2u, 0xd4u, 0xfeu, 100u, 0u, 0u, 0u,
        130u, 0u, 0u, 0u, 90u,
        7u, 75u, 80u, 70u,
        9u, 90u, 90u, 90u,
    };
    assert(written == sizeof expected);
    for (size_t index = 0u; index < sizeof expected; ++index) {
        assert(daily[index] == expected[index]);
    }

    assert(r1_health_record_u16(&state.health.heart_rate_variability,
                                3u, 42u, 140u, 100u, -300) == R1_OK);
    state.health.heart_rate_variability.slots[4].sample_count = UINT16_MAX;
    state.health.heart_rate_variability.slots[4].sum = 1u;
    assert(r1_health_record_u16(&state.health.heart_rate_variability,
                                4u, 1u, 141u, 100u, -300) == R1_OK);
    assert(state.health.heart_rate_variability.slots[4].sample_count == 0u);
    assert(state.health.heart_rate_variability.slots[4].average == UINT16_MAX);
    assert(r1_activity_record(&state.health.activity, 2u, 78u, 90u, 12u,
                              150u, 100u, -300) == R1_OK);
    uint8_t activity[R1_ACTIVITY_DAILY_MAX_BYTES];
    assert(r1_activity_encode_daily(&state.health.activity,
                                    activity, sizeof activity, &written) == R1_OK);
    static const uint8_t expected_activity[] = {
        1u, 0xd4u, 0xfeu, 100u, 0u, 0u, 0u,
        2u, 78u, 0u, 90u, 0u, 12u, 0u,
    };
    assert(written == sizeof expected_activity);
    for (size_t index = 0u; index < sizeof expected_activity; ++index) {
        assert(activity[index] == expected_activity[index]);
    }

    r1_session session = {true, true, true, R1_ROLE_PHONE};
    const r1_model query = {100u, 2u, 100u, 0x14u, 0u, 1u, 1u, NULL, 0u};
    r1_dispatch_result result;
    assert(r1_dispatch(&state, &session, &query, &result) == R1_OK);
    assert(result.count == 2u);
    r1_model response;
    assert(r1_model_decode(result.models[0], result.lengths[0],
                           R1_CHECKSUM_FIRMWARE_FULL_MODBUS, &response) == R1_OK);
    assert(response.serial == 0x14u && response.status == 3u);
    assert(response.payload_length == 0u);
    assert(r1_model_decode(result.models[1], result.lengths[1],
                           R1_CHECKSUM_FIRMWARE_FULL_MODBUS, &response) == R1_OK);
    assert(response.serial == 1u && response.status == 2u);
    assert(response.payload_length == sizeof expected);
    for (size_t index = 0u; index < sizeof expected; ++index) {
        assert(response.payload[index] == expected[index]);
    }

    session.authorized = false;
    assert(r1_dispatch(&state, &session, &query, &result) == R1_ERROR_UNAUTHORIZED);
    assert(result.count == 1u);
}

typedef struct {
    size_t count;
    r1_health_auto_sync_leg legs[25u];
    uint8_t serials[25u];
} health_auto_sync_capture;

static void capture_health_auto_sync(
    void *context, r1_health_auto_sync_leg leg, uint8_t serial) {
    health_auto_sync_capture *capture = context;
    assert(capture->count < 25u);
    capture->legs[capture->count] = leg;
    capture->serials[capture->count] = serial;
    capture->count += 1u;
}

static void test_automatic_health_sync(void) {
    r1_health_state health;
    r1_health_initialize(&health);
    health_auto_sync_capture capture = {0};

    r1_health_auto_sync_result result = r1_health_run_automatic_sync(
        &health, false, 100u, capture_health_auto_sync, &capture);
    assert(result.action == R1_HEALTH_AUTO_SYNC_PHONE_DISCONNECTED);
    assert(!result.batch_started && capture.count == 0u);

    result = r1_health_run_automatic_sync(
        &health, true, 100u, capture_health_auto_sync, &capture);
    assert(result.action == R1_HEALTH_AUTO_SYNC_INITIAL);
    assert(result.batch_started && !result.has_elapsed_seconds);
    assert(health.last_auto_sync_or_query_seconds == 100u);
    assert(capture.count == 5u);
    assert(capture.legs[0] == R1_HEALTH_SYNC_HEART_RATE);
    assert(capture.legs[1] == R1_HEALTH_SYNC_BLOOD_OXYGEN);
    assert(capture.legs[2] == R1_HEALTH_SYNC_HEART_RATE_VARIABILITY);
    assert(capture.legs[3] == R1_HEALTH_SYNC_ACTIVITY);
    assert(capture.legs[4] == R1_HEALTH_SYNC_UNSYNCHRONIZED_SLEEP);
    for (size_t index = 0u; index < capture.count; ++index) {
        assert(capture.serials[index] == R1_HEALTH_AUTO_SYNC_SERIAL);
    }

    result = r1_health_run_automatic_sync(
        &health, true, UINT32_C(10899), capture_health_auto_sync, &capture);
    assert(result.action == R1_HEALTH_AUTO_SYNC_COOLDOWN_ACTIVE);
    assert(result.has_elapsed_seconds && result.elapsed_seconds == 10799u);
    assert(!result.batch_started && capture.count == 5u);
    result = r1_health_run_automatic_sync(
        &health, true, UINT32_C(10900), capture_health_auto_sync, &capture);
    assert(result.action == R1_HEALTH_AUTO_SYNC_COOLDOWN_ELAPSED);
    assert(result.batch_started && capture.count == 10u);

    result = r1_health_run_automatic_sync(
        &health, true, 1000u, capture_health_auto_sync, &capture);
    assert(result.action == R1_HEALTH_AUTO_SYNC_CLOCK_REWIND);
    assert(result.batch_started && capture.count == 15u);

    r1_health_note_explicit_history_query(&health, 5000u);
    assert(health.last_auto_sync_or_query_seconds == 5000u);
    result = r1_health_run_automatic_sync(
        &health, true, UINT32_C(15799), capture_health_auto_sync, &capture);
    assert(result.action == R1_HEALTH_AUTO_SYNC_COOLDOWN_ACTIVE);
    result = r1_health_run_automatic_sync(
        &health, true, UINT32_C(15800), capture_health_auto_sync, &capture);
    assert(result.action == R1_HEALTH_AUTO_SYNC_COOLDOWN_ELAPSED);

    r1_device_state state;
    r1_state_initialize(&state);
    state.unix_seconds = 777u;
    r1_session peer = {true, true, true, R1_ROLE_PHONE};
    const r1_model query = {
        R1_PROTOCOL_VERSION, 2u, R1_MODULE_VERSION, 1u,
        0u, 1u, 2u, NULL, 0u,
    };
    r1_dispatch_result dispatch;
    assert(r1_dispatch(&state, &peer, &query, &dispatch) == R1_OK);
    assert(state.health.last_auto_sync_or_query_seconds == 777u);

    r1_runtime runtime;
    r1_runtime_initialize(&runtime, NULL, NULL);
    capture = (health_auto_sync_capture){0};
    result = r1_runtime_run_automatic_health_sync(
        &runtime, 10u, capture_health_auto_sync, &capture);
    assert(result.action == R1_HEALTH_AUTO_SYNC_PHONE_DISCONNECTED);
    runtime.links[0].active = true;
    runtime.links[0].session.role = R1_ROLE_PHONE;
    result = r1_runtime_run_automatic_health_sync(
        &runtime, 10u, capture_health_auto_sync, &capture);
    assert(result.action == R1_HEALTH_AUTO_SYNC_INITIAL);
    assert(result.batch_started && capture.count == 5u);

    result = r1_health_run_automatic_sync(
        NULL, true, 0u, capture_health_auto_sync, &capture);
    assert(result.action == R1_HEALTH_AUTO_SYNC_INVALID);
    result = r1_health_run_automatic_sync(
        &health, true, 0u, NULL, &capture);
    assert(result.action == R1_HEALTH_AUTO_SYNC_INVALID);
}

static void test_health_time_and_hour_orchestration(void) {
    r1_health_time_transition transition = {
        -300, -300, UINT32_C(1700000000), UINT32_C(1700000030),
    };
    r1_health_time_transition_result result;
    assert(r1_health_plan_time_transition(&transition, &result) == R1_OK);
    assert(result.clock_update_attempted);
    assert(result.absolute_delta_seconds == 30u);
    assert(!result.subscriber_broadcast_requested);
    assert(!result.known_cursor_clamp_pass_requested);

    transition = (r1_health_time_transition){
        0, 0, UINT32_C(1700000000), UINT32_C(1700000031),
    };
    assert(r1_health_plan_time_transition(&transition, &result) == R1_OK);
    assert(result.subscriber_broadcast_requested);
    assert(result.known_cursor_clamp_pass_requested);

    transition.new_timestamp_seconds = UINT32_C(1699999820);
    assert(r1_health_plan_time_transition(&transition, &result) == R1_OK);
    assert(result.backward_delta_seconds == 180u);
    assert(result.gomore_reinitialization_requested);
    assert(!result.health_database_format_requested);
    transition.new_timestamp_seconds = UINT32_C(1699996401);
    assert(r1_health_plan_time_transition(&transition, &result) == R1_OK);
    assert(result.backward_delta_seconds == 3599u);
    assert(!result.health_database_format_requested);

    transition.new_timestamp_seconds = UINT32_C(1699996400);
    r1_health_sync_cursor_state cursors = {
        100u, 200u, UINT32_C(0x11111111),
        300u, 400u, UINT32_C(0x22222222),
    };
    assert(r1_health_reconcile_sync_cursors(
               &cursors, &transition, &result) == R1_OK);
    assert(result.health_database_format_requested);
    assert(result.known_cursor_reset_requested);
    assert(cursors.heart_rate_timestamp == 0u);
    assert(cursors.blood_oxygen_timestamp == 0u);
    assert(cursors.heart_rate_variability_timestamp == 0u);
    assert(cursors.activity_timestamp == 0u);
    assert(cursors.unresolved_offset_8 == UINT32_C(0x11111111));
    assert(cursors.unresolved_offset_20 == UINT32_C(0x22222222));

    const uint32_t floor = R1_HEALTH_LEGACY_CLOCK_CUTOFF;
    transition = (r1_health_time_transition){
        -720, 720, floor + UINT32_C(43200), floor + UINT32_C(43200),
    };
    assert(r1_health_plan_time_transition(&transition, &result) == R1_OK);
    assert(result.subscriber_broadcast_requested);
    assert(result.old_local_day_index != result.new_local_day_index);
    assert(result.daily_cache_reset_requested);
    assert(result.daily_cache_family_count == R1_HEALTH_DAILY_CACHE_FAMILY_COUNT);
    assert(!result.health_database_format_requested);

    transition = (r1_health_time_transition){
        0, 0, floor - 100u, floor,
    };
    assert(r1_health_plan_time_transition(&transition, &result) == R1_OK);
    assert(result.current_day_recovery_requested);
    assert(!result.known_cursor_clamp_pass_requested);

    transition = (r1_health_time_transition){
        0, 0, UINT32_C(1700000000), UINT32_C(1699999000),
    };
    cursors = (r1_health_sync_cursor_state){
        UINT32_C(1699999001), UINT32_C(1699998999), 7u,
        UINT32_MAX, 0u, 9u,
    };
    assert(r1_health_reconcile_sync_cursors(
               &cursors, &transition, &result) == R1_OK);
    assert(cursors.heart_rate_timestamp == transition.new_timestamp_seconds);
    assert(cursors.blood_oxygen_timestamp == UINT32_C(1699998999));
    assert(cursors.heart_rate_variability_timestamp ==
           transition.new_timestamp_seconds);
    assert(cursors.activity_timestamp == 0u);
    assert(cursors.unresolved_offset_8 == 7u && cursors.unresolved_offset_20 == 9u);
    assert(result.known_cursor_clamped_count == 2u);

    r1_health_hour_boundary_result hour;
    assert(r1_health_plan_hour_boundary(0u, &hour) == R1_OK);
    assert(hour.hrv_eligibility_evaluation_requested);
    assert(hour.blood_oxygen_eligibility_evaluation_requested);
    assert(hour.database_writer_accepts_hour);
    assert(hour.has_appended_aggregate_hour && hour.appended_aggregate_hour == 23u);
    assert(hour.daily_cache_reset_requested);
    assert(hour.daily_cache_family_count == R1_HEALTH_DAILY_CACHE_FAMILY_COUNT);
    assert(hour.midnight_followup_requested);
    assert(!hour.midnight_followup_has_subscriber);
    assert(r1_health_plan_hour_boundary(1u, &hour) == R1_OK);
    assert(hour.appended_aggregate_hour == 0u);
    assert(!hour.daily_cache_reset_requested);
    assert(r1_health_plan_hour_boundary(24u, &hour) == R1_OK);
    assert(!hour.database_writer_accepts_hour);
    assert(!hour.has_appended_aggregate_hour);
}

typedef struct {
    size_t count;
    uint8_t payloads[3u][64u];
    size_t lengths[3u];
    uint32_t maximum_timestamps[3u];
    uint16_t serials[3u];
    uint8_t modes[3u];
} activity_offline_capture;

static r1_error capture_activity_offline(
    void *context, const r1_activity_offline_packet *packet) {
    activity_offline_capture *capture = context;
    assert(capture->count < 3u);
    const size_t index = capture->count;
    const r1_error error = r1_activity_encode_daily(
        &packet->history, capture->payloads[index],
        sizeof capture->payloads[index], &capture->lengths[index]);
    if (error == R1_OK) {
        capture->maximum_timestamps[index] = packet->maximum_recorded_timestamp;
        capture->serials[index] = packet->serial;
        capture->modes[index] = packet->mode;
        capture->count += 1u;
    }
    return error;
}

static void test_activity_offline_sync(void) {
    r1_activity_offline_queue queue;
    r1_activity_offline_initialize(&queue);
    assert(r1_activity_offline_is_empty(&queue));
    assert(sizeof(r1_activity_offline_entry) == 16u);

    const uint32_t first = 12u | (34u << 12u) | (56u << 22u);
    const uint32_t second = 78u | (90u << 12u) | (12u << 22u);
    r1_activity_offline_enqueue_result enqueue;
    assert(r1_activity_offline_enqueue(
               &queue, 0u, 0u, 0u, 0, 0u, 0u, &enqueue) == R1_OK);
    assert(enqueue.action == R1_ACTIVITY_OFFLINE_DROPPED_ZERO && queue.count == 0u);
    assert(r1_activity_offline_enqueue(
               &queue, first, 100u, 201u, 0, 2u, 200u, &enqueue) == R1_OK);
    assert(enqueue.action == R1_ACTIVITY_OFFLINE_DROPPED_FUTURE_RECORDED);
    assert(r1_activity_offline_enqueue(
               &queue, first, 201u, 200u, 0, 2u, 200u, &enqueue) == R1_OK);
    assert(enqueue.action == R1_ACTIVITY_OFFLINE_DROPPED_FUTURE_DAY);
    assert(r1_activity_offline_enqueue(
               &queue, first, 0u, 0u, 0, R1_ACTIVITY_BUCKETS, 0u, &enqueue)
           == R1_ERROR_LENGTH);

    queue.entries[0].reserved_tail = 0xa5u;
    assert(r1_activity_offline_enqueue(
               &queue, first, 100u, 101u, -300, 2u, 1000u, &enqueue) == R1_OK);
    assert(enqueue.action == R1_ACTIVITY_OFFLINE_ENQUEUED);
    assert(!enqueue.overwrote_oldest && queue.count == 1u);
    assert(queue.entries[0].reserved_tail == 0xa5u);
    assert(!r1_activity_offline_is_empty(&queue));

    r1_activity_offline_initialize(&queue);
    for (uint16_t value = 1u; value <= 145u; ++value) {
        assert(r1_activity_offline_enqueue(
                   &queue, value, 0u, value, 0,
                   (uint8_t)(value % R1_ACTIVITY_BUCKETS), value, &enqueue) == R1_OK);
        assert(enqueue.action == R1_ACTIVITY_OFFLINE_ENQUEUED);
        assert(enqueue.overwrote_oldest == (value == 145u));
    }
    assert(queue.count == R1_ACTIVITY_OFFLINE_CAPACITY);
    assert(queue.read_index == 1u && queue.write_index == 1u);
    assert(queue.entries[queue.read_index].recorded_timestamp == 2u);
    size_t consumed = 0u;
    assert(r1_activity_offline_consume_through(&queue, 10u, &consumed) == R1_OK);
    assert(consumed == 9u && queue.count == 135u);
    assert(queue.entries[queue.read_index].recorded_timestamp == 11u);

    r1_activity_offline_initialize(&queue);
    assert(r1_activity_offline_enqueue(
               &queue, first, 100u, 101u, -300, 2u, 1000u, &enqueue) == R1_OK);
    assert(r1_activity_offline_enqueue(
               &queue, second, 100u, 102u, -300, 2u, 1000u, &enqueue) == R1_OK);
    assert(r1_activity_offline_enqueue(
               &queue, first, 300u, 999u, 0, 4u, 1000u, &enqueue) == R1_OK);
    activity_offline_capture capture = {0};
    r1_activity_offline_packet workspace;
    r1_activity_offline_merge_result merge;
    assert(r1_activity_offline_merge(
               &queue, 250u, &workspace, capture_activity_offline,
               &capture, &merge) == R1_OK);
    assert(merge.packet_count == 1u && merge.skipped_zero_count == 0u);
    assert(merge.skipped_future_count == 1u && capture.count == 1u);
    assert(capture.maximum_timestamps[0] == 102u);
    static const uint8_t expected[] = {
        1u, 0xd4u, 0xfeu, 100u, 0u, 0u, 0u,
        2u, 78u, 0u, 90u, 0u, 12u, 0u,
    };
    assert(capture.lengths[0] == sizeof expected);
    assert(memcmp(capture.payloads[0], expected, sizeof expected) == 0);

    r1_activity_ack_result ack;
    uint32_t last_sync = 40u;
    assert(r1_activity_offline_acknowledge(
               &queue, R1_ACTIVITY_ACK_OFFLINE_QUEUE, 101u, 50u,
               &last_sync, &ack) == R1_OK);
    assert(ack.firmware_clock_sampled && ack.timestamp_was_future);
    assert(!ack.last_sync_updated && ack.consumed_count == 1u);
    assert(queue.count == 2u && last_sync == 40u);
    assert(r1_activity_offline_acknowledge(
               &queue, R1_ACTIVITY_ACK_CURRENT_RAM, 200u, 250u,
               &last_sync, &ack) == R1_OK);
    assert(ack.last_sync_updated && last_sync == 200u);
    assert(r1_activity_offline_acknowledge(
               &queue, R1_ACTIVITY_ACK_FLASH_HISTORY, 300u, 250u,
               &last_sync, &ack) == R1_OK);
    assert(ack.timestamp_was_future && !ack.last_sync_updated && last_sync == 200u);
    assert(r1_activity_offline_acknowledge(
               &queue, 0xffu, 201u, 250u, &last_sync, &ack) == R1_OK);
    assert(!ack.last_sync_updated && ack.consumed_count == 0u);

    queue.write_index = 9u;
    assert(r1_activity_offline_consume_through(&queue, 0u, &consumed)
           == R1_ERROR_STATE);
    assert(r1_activity_offline_enqueue(
               NULL, first, 0u, 0u, 0, 0u, 0u, &enqueue) == R1_ERROR_ARGUMENT);
}

static void test_activity_daily_cache_callbacks(void) {
    r1_activity_history history = {0};
    history.buckets[0] = (r1_activity_bucket){9u, 8u, 7u, true};
    history.latest_timestamp = 77u;
    history.total_steps = 9;
    history.total_kilocalories = 7;
    r1_activity_cache_refresh_metadata(&history, 50u, -300);
    assert(history.local_day_start == 50u && history.utc_offset_minutes == -300);
    assert(history.buckets[0].valid && history.buckets[0].steps == 9u);
    assert(history.latest_timestamp == 77u && history.total_steps == 9 &&
           history.total_kilocalories == 7);
    r1_activity_cache_refresh_metadata(NULL, 0u, 0);
    history.buckets[0] = (r1_activity_bucket){9u, 8u, 7u, true};
    r1_activity_cache_reset(&history, 100u, 60);
    assert(history.local_day_start == 100u && history.utc_offset_minutes == 60);
    assert(!history.buckets[0].valid && history.total_steps == 0);

    r1_activity_bucket hour[R1_ACTIVITY_BUCKETS_PER_HOUR] = {0};
    hour[0] = (r1_activity_bucket){12u, 34u, 56u, true};
    hour[5] = (r1_activity_bucket){78u, 90u, 12u, true};
    assert(r1_activity_cache_write_hour(&history, 2u, hour) == R1_OK);
    assert(history.buckets[12].steps == 12u && history.buckets[17].steps == 78u);
    assert(history.total_steps == 90 && history.total_kilocalories == 68);
    assert(r1_activity_cache_write_hour(
               &history, R1_HEALTH_HOURLY_SLOTS, hour) == R1_ERROR_LENGTH);

    r1_activity_offline_queue queue;
    r1_activity_offline_initialize(&queue);
    r1_activity_cache_read_result result;
    assert(r1_activity_cache_read_hour(
               &history, 2u, 1u, 10u, 10u, NULL, 0u, &queue,
               &result) == R1_OK);
    assert(result.disposition == R1_ACTIVITY_CACHE_RETURNED_CLOCK_VALID);
    assert(result.returned[0].steps == 12u && queue.count == 0u);
    assert(r1_activity_cache_read_hour(
               &history, 2u, 0u, R1_ACTIVITY_LEGACY_CLOCK_CUTOFF + 1u,
               10u, NULL, 0u, &queue, &result) == R1_OK);
    assert(result.disposition == R1_ACTIVITY_CACHE_RETURNED_ABOVE_LEGACY_CUTOFF);

    static const uint32_t timestamps[] = {100u, 100u};
    assert(r1_activity_cache_read_hour(
               &history, 2u, 0u, 90u, 90u, timestamps, 2u, &queue,
               &result) == R1_OK);
    assert(result.disposition == R1_ACTIVITY_CACHE_QUEUED_AND_REDACTED);
    assert(result.has_unsigned_offset_hours && result.unsigned_offset_hours == 1u);
    assert(result.has_adjusted_hour && result.adjusted_hour == 1u);
    assert(result.enqueue_count == 2u && queue.count == 2u);
    assert(queue.entries[0].bucket_index == 6u);
    assert(queue.entries[1].bucket_index == 11u);
    assert(!result.returned[0].valid && !result.returned[5].valid);

    history.utc_offset_minutes = -60;
    assert(r1_activity_cache_read_hour(
               &history, 2u, 0u, 90u, 90u, NULL, 0u, &queue,
               &result) == R1_OK);
    assert(result.disposition == R1_ACTIVITY_CACHE_REDACTED_OFFSET_BEFORE_HOUR);
    history.utc_offset_minutes = 60;
    assert(r1_activity_cache_read_hour(
               &history, 2u, 0u, 90u, 89u, NULL, 0u, &queue,
               &result) == R1_OK);
    assert(result.disposition == R1_ACTIVITY_CACHE_REDACTED_BACKWARD_CLOCK);
    assert(r1_activity_cache_read_hour(
               &history, 2u, 0u, 90u, 90u, timestamps, 1u, &queue,
               &result) == R1_ERROR_LENGTH);
}

static void test_activity_day_builder_merges(void) {
    assert(r1_activity_clamp_acknowledgement_timestamp(0u, 100u) == 100u);
    assert(r1_activity_clamp_acknowledgement_timestamp(90u, 100u) == 90u);
    assert(r1_activity_clamp_acknowledgement_timestamp(110u, 100u) == 100u);

    r1_activity_offline_packet builder = {0};
    builder.serial = 0x1234u;
    builder.mode = 7u;
    builder.acknowledgement_requested = true;
    builder.history.buckets[0].valid = true;
    r1_activity_day_builder_reset(&builder);
    assert(builder.serial == 0x1234u && builder.mode == 7u);
    assert(builder.acknowledgement_requested);
    assert(!builder.history.buckets[0].valid);

    const uint32_t first = 12u | (34u << 12u) | (56u << 22u);
    const uint32_t replacement = 78u | (90u << 12u) | (12u << 22u);
    r1_activity_flash_record record = {
        .utc_offset_minutes = 0,
        .recorded_timestamp = 90000u,
        .packed_words = {first, 0u, 0u, 0u, 0u, 0u},
    };
    activity_offline_capture capture = {0};
    r1_activity_day_flush_result flush;
    assert(r1_activity_flash_record_merge(
               &builder, &record, 200000u, true, capture_activity_offline,
               &capture, &flush) == R1_OK);
    assert(builder.history.local_day_start == 86400u);
    assert(builder.history.buckets[0].valid);
    assert(builder.history.buckets[0].steps == 12u);
    assert(builder.maximum_recorded_timestamp == 90000u);

    record.packed_words[0] = replacement;
    assert(r1_activity_flash_record_merge(
               &builder, &record, 200000u, true, capture_activity_offline,
               &capture, &flush) == R1_OK);
    assert(builder.history.buckets[0].steps == 12u);
    record.recorded_timestamp = 172800u;
    record.packed_words[0] = 0u;
    record.packed_words[5] = replacement;
    assert(r1_activity_flash_record_merge(
               &builder, &record, 200000u, true, capture_activity_offline,
               &capture, &flush) == R1_OK);
    assert(builder.history.local_day_start == 86400u);
    assert(builder.history.buckets[143].steps == 78u);
    assert(r1_activity_day_builder_flush(
               &builder, 200000u, capture_activity_offline, &capture,
               &flush) == R1_OK);
    assert(flush.emitted && flush.encoded_length == 21u);
    assert(capture.count == 1u && capture.maximum_timestamps[0] == 172800u);
    assert(capture.serials[0] == 0x1234u && capture.modes[0] == 7u);
    assert(builder.serial == 0x1234u && builder.mode == 7u);

    builder.history.buckets[1] = (r1_activity_bucket){1u, 2u, 3u, true};
    builder.maximum_recorded_timestamp = 300u;
    assert(r1_activity_day_builder_flush(
               &builder, 200u, capture_activity_offline, &capture,
               &flush) == R1_OK);
    assert(flush.dropped_future_acknowledgement && !flush.emitted);
    assert(!builder.history.buckets[1].valid && capture.count == 1u);

    r1_activity_history cache = {0};
    cache.buckets[0] = (r1_activity_bucket){1u, 1u, 1u, true};
    cache.buckets[1] = (r1_activity_bucket){2u, 3u, 4u, true};
    cache.buckets[2] = (r1_activity_bucket){5u, 6u, 7u, true};
    assert(r1_activity_ram_cache_merge(
               &builder, &cache, 1000u, 1500u, 2200u, -300,
               10u, 20u, 30u, capture_activity_offline, &capture,
               &flush) == R1_OK);
    assert(flush.emitted && capture.count == 2u);
    assert(capture.modes[1] == R1_ACTIVITY_ACK_CURRENT_RAM);
    assert(capture.maximum_timestamps[1] == 2200u);
    assert(capture.lengths[1] == 21u);
    assert(capture.payloads[1][7] == 1u);
    assert(capture.payloads[1][14] == 2u);
    assert(capture.payloads[1][15] == 15u);
    assert(cache.local_day_start == 1000u && cache.utc_offset_minutes == -300);
    assert(builder.mode == 7u && builder.serial == 0x1234u);

    record.recorded_timestamp = 2300u;
    assert(r1_activity_flash_record_merge(
               &builder, &record, 2200u, false, capture_activity_offline,
               &capture, &flush) == R1_OK);
    assert(!builder.history.buckets[0].valid);
}

typedef struct {
    size_t count;
    uint8_t payloads[3u][64u];
    size_t lengths[3u];
    uint32_t maximum_timestamps[3u];
} health_offline_capture;

static void test_scalar_health_daily_cache_callbacks(void) {
    r1_health_u8_history u8 = {0};
    u8.latest_value = 81u;
    u8.latest_timestamp = 0x12345678u;
    u8.has_latest = true;
    u8.slots[5] = (r1_health_u8_slot){70u, 90u, 60u, 4u, 280u};
    r1_health_u8_cache_reset(&u8, 0x01020304u, -300);
    assert(u8.local_day_start == 0x01020304u);
    assert(u8.utc_offset_minutes == -300);
    assert(u8.slots[5].average == 0u && u8.slots[5].sample_count == 0u);
    assert(u8.has_latest && u8.latest_value == 81u);
    assert(u8.latest_timestamp == 0x12345678u);

    u8.slots[5].sample_count = 7u;
    u8.slots[5].sum = 560u;
    assert(r1_health_u8_cache_write_slot(
               &u8, 5u, 80u, 90u, 70u) == R1_OK);
    assert(u8.slots[5].average == 80u && u8.slots[5].maximum == 90u);
    assert(u8.slots[5].minimum == 70u && u8.slots[5].sample_count == 7u);
    assert(u8.slots[5].sum == 560u);
    assert(r1_health_u8_cache_write_slot(
               &u8, R1_HEALTH_HOURLY_SLOTS, 1u, 1u, 1u) == R1_ERROR_LENGTH);

    r1_health_u8_cache_read_result u8_read;
    assert(r1_health_u8_cache_read_slot(
               &u8, 5u, 1u, 0u, 0u, 0u, NULL, &u8_read) == R1_OK);
    assert(u8_read.disposition == R1_HEALTH_CACHE_RETURNED_CLOCK_VALID);
    assert(u8_read.returned.average == 80u && !u8_read.has_enqueue_result);
    assert(r1_health_u8_cache_read_slot(
               &u8, 5u, 0u, R1_HEALTH_LEGACY_CLOCK_CUTOFF + 1u,
               0u, 0u, NULL, &u8_read) == R1_OK);
    assert(u8_read.disposition ==
           R1_HEALTH_CACHE_RETURNED_ABOVE_LEGACY_CUTOFF);

    r1_health_u8_offline_queue u8_queue;
    r1_health_u8_offline_initialize(&u8_queue);
    assert(r1_health_u8_cache_read_slot(
               &u8, 5u, 0u, 1000u, 1000u, 1000u,
               &u8_queue, &u8_read) == R1_OK);
    assert(u8_read.disposition == R1_HEALTH_CACHE_REDACTED_OFFSET_BEFORE_HOUR);
    assert(u8_read.has_unsigned_offset_hours);
    assert(u8_read.unsigned_offset_hours == 1087u);
    assert(u8_read.returned.average == 0u && u8_queue.count == 0u);

    u8.utc_offset_minutes = 120;
    assert(r1_health_u8_cache_read_slot(
               &u8, 5u, 0u, 1000u, 999u, 1000u,
               &u8_queue, &u8_read) == R1_OK);
    assert(u8_read.disposition == R1_HEALTH_CACHE_REDACTED_BACKWARD_CLOCK);
    assert(u8_read.adjusted_hour == 3u && u8_queue.count == 0u);
    assert(r1_health_u8_cache_read_slot(
               &u8, 5u, 0u, 1000u, 1000u, 999u,
               &u8_queue, &u8_read) == R1_OK);
    assert(u8_read.disposition ==
           R1_HEALTH_CACHE_QUEUE_REJECTED_AND_REDACTED);
    assert(u8_read.has_enqueue_result);
    assert(u8_read.enqueue.action ==
           R1_HEALTH_OFFLINE_DROPPED_FUTURE_RECORDED);
    assert(u8_queue.count == 0u);
    u8_queue.entries[0].reserved_after_aggregate = 0xa4u;
    u8_queue.entries[0].reserved_tail = 0xa5u;
    assert(r1_health_u8_cache_read_slot(
               &u8, 5u, 0u, 1000u, 1000u, 1000u,
               &u8_queue, &u8_read) == R1_OK);
    assert(u8_read.disposition == R1_HEALTH_CACHE_QUEUED_AND_REDACTED);
    assert(u8_queue.count == 1u && u8_queue.entries[0].hour_index == 3u);
    assert(u8_queue.entries[0].local_day_start == 0u);
    assert(u8_queue.entries[0].utc_offset_minutes == 0);
    assert(u8_queue.entries[0].recorded_timestamp == 1000u);
    assert(u8_queue.entries[0].reserved_after_aggregate == 0xa4u);
    assert(u8_queue.entries[0].reserved_tail == 0xa5u);

    assert(r1_health_u8_cache_write_slot(&u8, 6u, 0u, 100u, 40u) == R1_OK);
    assert(r1_health_u8_cache_read_slot(
               &u8, 6u, 0u, 1000u, 0u, 0u, NULL, &u8_read) == R1_OK);
    assert(u8_read.disposition == R1_HEALTH_CACHE_RETURNED_ZERO_AVERAGE);
    assert(u8_read.returned.maximum == 100u && u8_read.returned.minimum == 40u);

    r1_health_u16_history u16 = {0};
    u16.latest_value = 42u;
    u16.latest_timestamp = 77u;
    u16.has_latest = true;
    u16.slots[5] = (r1_health_u16_slot){70u, 82u, 60u, 4u, 280u};
    r1_health_u16_cache_reset(&u16, 0x01020304u, 120);
    assert(u16.slots[5].average == 0u && u16.has_latest);
    assert(u16.latest_value == 42u && u16.latest_timestamp == 77u);
    assert(r1_health_u16_cache_write_slot(
               &u16, 5u, 0x1234u, 0x4567u, 0x1111u) == R1_OK);
    assert(r1_health_u16_cache_write_slot(
               &u16, R1_HEALTH_HOURLY_SLOTS, 1u, 1u, 1u) == R1_ERROR_LENGTH);

    r1_health_u16_offline_queue u16_queue;
    r1_health_u16_offline_initialize(&u16_queue);
    u16_queue.entries[0].reserved_after_aggregate[0] = 0xb1u;
    u16_queue.entries[0].reserved_after_aggregate[1] = 0xb2u;
    u16_queue.entries[0].reserved_tail = 0xb3u;
    r1_health_u16_cache_read_result u16_read;
    assert(r1_health_u16_cache_read_slot(
               &u16, 5u, 0u, 1000u, 1000u, 1000u,
               &u16_queue, &u16_read) == R1_OK);
    assert(u16_read.disposition == R1_HEALTH_CACHE_QUEUED_AND_REDACTED);
    assert(u16_read.has_unsigned_offset_hours &&
           u16_read.unsigned_offset_hours == 2u);
    assert(u16_read.has_adjusted_hour && u16_read.adjusted_hour == 3u);
    assert(u16_read.copied.average == 0x1234u);
    assert(u16_read.returned.average == 0u);
    assert(u16_queue.count == 1u && u16_queue.entries[0].hour_index == 3u);
    assert(u16_queue.entries[0].reserved_after_aggregate[0] == 0xb1u);
    assert(u16_queue.entries[0].reserved_after_aggregate[1] == 0xb2u);
    assert(u16_queue.entries[0].reserved_tail == 0xb3u);
}

static void test_temperature_and_stress_daily_cache_callbacks(void) {
    assert(sizeof(r1_health_u8_accumulator) == 8u);

    r1_health_u8_history temperature = {0};
    r1_health_u8_accumulator temperature_average = {0};
    r1_health_u8_sample_result sample;
    assert(r1_temperature_store_sample(
               &temperature, &temperature_average, 249u, 11u, 1u, 1u,
               &sample) == R1_OK);
    assert(sample.action == R1_HEALTH_U8_SAMPLE_REJECTED_RANGE);
    assert(!sample.timestamp_replaced && !temperature.has_latest);
    assert(temperature_average.sample_count == 0u);
    assert(r1_temperature_store_sample(
               &temperature, &temperature_average, 501u, 12u, 1u, 1u,
               &sample) == R1_OK);
    assert(sample.action == R1_HEALTH_U8_SAMPLE_REJECTED_RANGE);

    assert(r1_temperature_store_sample(
               &temperature, &temperature_average, 365u, 0x12345678u,
               4u, 5u, &sample) == R1_OK);
    assert(sample.action == R1_HEALTH_U8_SAMPLE_STORED);
    assert(sample.published_value == 365u && sample.stored_value == 115u);
    assert(sample.timestamp_replaced);
    assert(temperature.slots[4].average == 115u);
    assert(temperature.slots[4].maximum == 115u);
    assert(temperature.slots[4].minimum == 115u);
    assert(temperature_average.hour == 5u);
    assert(temperature_average.reserved == 0u);
    assert(temperature_average.sample_count == 1u);
    assert(temperature_average.sum == 115u);
    assert(temperature.has_latest && temperature.latest_value == 115u);
    assert(temperature.latest_timestamp == 0x12345678u);

    assert(r1_temperature_store_sample(
               &temperature, &temperature_average, 385u, 20u,
               4u, 5u, &sample) == R1_OK);
    assert(temperature.slots[4].average == 125u);
    assert(temperature.slots[4].maximum == 135u);
    assert(temperature.slots[4].minimum == 115u);
    assert(temperature_average.sample_count == 2u);
    assert(temperature_average.sum == 250u);
    assert(r1_temperature_store_sample(
               &temperature, &temperature_average, 250u, 21u,
               6u, 6u, &sample) == R1_OK);
    assert(temperature.slots[6].average == 0u);
    assert(temperature.slots[6].maximum == 0u);
    assert(temperature.slots[6].minimum == 0u);
    assert(temperature_average.hour == 6u);
    assert(temperature_average.sample_count == 1u);
    assert(temperature_average.sum == 0u);
    assert(r1_temperature_store_sample(
               &temperature, &temperature_average, 500u, 22u,
               7u, 7u, &sample) == R1_OK);
    assert(temperature.slots[7].average == 250u);
    assert(temperature.slots[7].maximum == 250u);
    assert(temperature.slots[7].minimum == 250u);
    assert(r1_temperature_store_sample(
               &temperature, &temperature_average, 365u, 22u,
               R1_HEALTH_HOURLY_SLOTS, 0u, &sample) == R1_ERROR_LENGTH);

    r1_health_u8_cache_reset(&temperature, 0x01020304u, -300);
    assert(temperature.has_latest && temperature.latest_value == 250u);
    assert(temperature.latest_timestamp == 22u);
    assert(r1_health_u8_cache_write_slot(
               &temperature, 5u, 115u, 120u, 110u) == R1_OK);
    r1_health_u8_cache_read_result temperature_read;
    assert(r1_temperature_cache_read_slot(
               &temperature, 5u, 1u, 0u, &temperature_read) == R1_OK);
    assert(temperature_read.disposition == R1_HEALTH_CACHE_RETURNED_CLOCK_VALID);
    assert(temperature_read.returned.average == 115u);
    assert(r1_temperature_cache_read_slot(
               &temperature, 5u, 0u, R1_HEALTH_LEGACY_CLOCK_CUTOFF + 1u,
               &temperature_read) == R1_OK);
    assert(temperature_read.disposition ==
           R1_HEALTH_CACHE_RETURNED_ABOVE_LEGACY_CUTOFF);
    assert(temperature_read.returned.maximum == 120u);
    assert(r1_temperature_cache_read_slot(
               &temperature, 5u, 0u, 1000u, &temperature_read) == R1_OK);
    assert(temperature_read.disposition == R1_HEALTH_CACHE_REDACTED_EARLY_CLOCK);
    assert(temperature_read.copied.average == 115u);
    assert(temperature_read.returned.average == 0u);
    assert(r1_health_u8_cache_write_slot(
               &temperature, 6u, 0u, 120u, 110u) == R1_OK);
    assert(r1_temperature_cache_read_slot(
               &temperature, 6u, 0u, 1000u, &temperature_read) == R1_OK);
    assert(temperature_read.disposition == R1_HEALTH_CACHE_RETURNED_ZERO_AVERAGE);
    assert(temperature_read.returned.maximum == 120u);

    r1_health_u8_history stress = {0};
    r1_health_u8_accumulator stress_average = {0};
    assert(r1_stress_store_sample(
               &stress, &stress_average, 50u, 0x12345678u,
               4u, 5u, &sample) == R1_OK);
    assert(sample.action == R1_HEALTH_U8_SAMPLE_STORED);
    assert(stress.slots[4].average == 50u);
    assert(stress_average.hour == 5u && stress_average.sample_count == 1u);
    assert(stress.latest_value == 50u && stress.latest_timestamp == 0x12345678u);
    assert(r1_stress_store_sample(
               &stress, &stress_average, 0u, 9u, 6u, 6u, &sample) == R1_OK);
    assert(sample.action == R1_HEALTH_U8_SAMPLE_STORED);
    assert(stress.slots[6].average == 0u && stress.has_latest);
    assert(r1_stress_store_sample(
               &stress, &stress_average, 100u, 10u, 7u, 7u, &sample) == R1_OK);
    assert(stress.slots[7].average == 100u);
    assert(r1_stress_store_sample(
               &stress, &stress_average, 101u, 11u, 1u, 1u,
               &sample) == R1_OK);
    assert(sample.action == R1_HEALTH_U8_SAMPLE_REJECTED_RANGE);
    assert(stress.latest_value == 100u && stress.latest_timestamp == 10u);

    r1_health_u8_cache_reset(&stress, 0u, 0);
    assert(r1_health_u8_cache_write_slot(
               &stress, 5u, 50u, 80u, 20u) == R1_OK);
    r1_health_u8_slot stress_read = {0};
    assert(r1_stress_cache_read_slot(&stress, 5u, &stress_read) == R1_OK);
    assert(stress_read.average == 50u && stress_read.maximum == 80u);
    assert(stress_read.minimum == 20u);
    assert(r1_stress_cache_read_slot(
               &stress, R1_HEALTH_HOURLY_SLOTS, &stress_read) ==
           R1_ERROR_LENGTH);

    r1_health_u8_accumulator saturated = {
        3u, 0xa5u, UINT16_MAX, UINT32_C(1234),
    };
    uint8_t average = 0u;
    assert(r1_health_u8_accumulate_average(
               &saturated, 3u, 1u, &average) == R1_ERROR_CAPACITY);
    assert(saturated.sample_count == UINT16_MAX && saturated.sum == 1234u);
}

static void test_scalar_health_sample_consumers(void) {
    r1_health_u8_accumulator lifecycle = {
        .hour = 7u, .reserved = 0xa5u, .sample_count = 3u, .sum = 210u,
    };
    uint32_t snapshot_sum = UINT32_MAX;
    uint16_t snapshot_count = UINT16_MAX;
    r1_health_accumulator_snapshot(
        &lifecycle, 6u, &snapshot_sum, &snapshot_count);
    assert(snapshot_sum == 0u && snapshot_count == 0u);
    r1_health_accumulator_snapshot(
        &lifecycle, 7u, &snapshot_sum, &snapshot_count);
    assert(snapshot_sum == 210u && snapshot_count == 3u);
    r1_health_accumulator_snapshot(NULL, 7u, &snapshot_sum, &snapshot_count);
    assert(snapshot_sum == 0u && snapshot_count == 0u);
    r1_health_accumulator_restore(&lifecycle, 8u, 400u, 0u);
    assert(lifecycle.hour == 7u && lifecycle.sum == 210u);
    r1_health_accumulator_restore(&lifecycle, 8u, 400u, 5u);
    assert(lifecycle.hour == 8u && lifecycle.sample_count == 5u &&
           lifecycle.sum == 400u && lifecycle.reserved == 0xa5u);

    r1_health_u8_history heart_rate = {0};
    r1_health_u8_accumulator heart_rate_average = {0};
    r1_health_u8_sample_result u8_result;

    assert(r1_heart_rate_store_sample(
               &heart_rate, &heart_rate_average, 39u, 0u, 10u,
               1u, 1u, &u8_result) == R1_OK);
    assert(u8_result.action == R1_HEALTH_U8_SAMPLE_REJECTED_RANGE);
    assert(!u8_result.timestamp_replaced && !u8_result.notification_requested);
    assert(!heart_rate.has_latest && heart_rate_average.sample_count == 0u);
    assert(r1_heart_rate_store_sample(
               &heart_rate, &heart_rate_average, 221u, 0u, 10u,
               1u, 1u, &u8_result) == R1_OK);
    assert(u8_result.action == R1_HEALTH_U8_SAMPLE_REJECTED_RANGE);

    assert(r1_heart_rate_store_sample(
               &heart_rate, &heart_rate_average, 40u, 0u, 0x12345678u,
               4u, 5u, &u8_result) == R1_OK);
    assert(u8_result.action == R1_HEALTH_U8_SAMPLE_STORED);
    assert(u8_result.published_value == 40u && u8_result.stored_value == 40u);
    assert(u8_result.timestamp_replaced);
    assert(u8_result.effective_timestamp == 0x12345678u);
    assert(u8_result.notification_requested);
    assert(u8_result.notification_metric == R1_HEALTH_NOTIFICATION_HEART_RATE);
    assert(heart_rate.slots[4].average == 40u);
    assert(heart_rate.slots[4].maximum == 40u);
    assert(heart_rate.slots[4].minimum == 40u);
    assert(heart_rate_average.hour == 5u);
    assert(heart_rate_average.sample_count == 1u);
    assert(heart_rate_average.sum == 40u);

    assert(r1_heart_rate_store_sample(
               &heart_rate, &heart_rate_average, 220u, 9u, 10u,
               6u, 6u, &u8_result) == R1_OK);
    assert(!u8_result.timestamp_replaced && u8_result.effective_timestamp == 9u);
    uint8_t latest_u8 = 0u;
    uint32_t latest_timestamp = 0u;
    assert(r1_health_u8_latest_sample(
        &heart_rate, &latest_u8, &latest_timestamp));
    assert(latest_u8 == 220u && latest_timestamp == 9u);

    r1_health_u8_history spo2 = {0};
    r1_health_u8_accumulator spo2_average = {0};
    assert(r1_spo2_store_sample(
               &spo2, &spo2_average, 69u, 7u, 10u,
               1u, 1u, &u8_result) == R1_OK);
    assert(u8_result.action == R1_HEALTH_U8_SAMPLE_REJECTED_RANGE);
    assert(!u8_result.timestamp_replaced && !u8_result.notification_requested);
    assert(r1_spo2_store_sample(
               &spo2, &spo2_average, 70u, 9u, 0x01020304u,
               5u, 6u, &u8_result) == R1_OK);
    assert(u8_result.action == R1_HEALTH_U8_SAMPLE_STORED);
    assert(u8_result.timestamp_replaced);
    assert(u8_result.effective_timestamp == 0x01020304u);
    assert(u8_result.notification_metric == R1_HEALTH_NOTIFICATION_SPO2);
    assert(spo2.slots[5].average == 70u);
    assert(spo2_average.hour == 6u && spo2_average.sum == 70u);
    assert(r1_spo2_store_sample(
               &spo2, &spo2_average, UINT8_MAX, 1u, 2u,
               7u, 7u, &u8_result) == R1_OK);
    assert(u8_result.stored_value == UINT8_MAX);
    assert(u8_result.effective_timestamp == 2u);

    r1_health_u16_history hrv = {0};
    r1_health_u16_accumulator hrv_average = {0};
    r1_health_u16_sample_result u16_result;
    assert(r1_hrv_store_sample(
               &hrv, &hrv_average, 0u, 0u, 0x12345678u,
               8u, 9u, &u16_result) == R1_OK);
    assert(u16_result.action == R1_HEALTH_U8_SAMPLE_STORED);
    assert(u16_result.timestamp_replaced);
    assert(u16_result.effective_timestamp == 0x12345678u);
    assert(u16_result.notification_requested);
    assert(u16_result.notification_metric == R1_HEALTH_NOTIFICATION_HRV);
    assert(hrv.slots[8].average == 0u && hrv.slots[8].minimum == 0u);
    uint16_t latest_u16 = 0xa5a5u;
    latest_timestamp = 0xa5a5a5a5u;
    assert(!r1_health_u16_latest_sample(
        &hrv, &latest_u16, &latest_timestamp));
    assert(latest_u16 == 0xa5a5u && latest_timestamp == 0xa5a5a5a5u);

    assert(r1_hrv_store_sample(
               &hrv, &hrv_average, 50u, 1u, 2u,
               8u, 9u, &u16_result) == R1_OK);
    assert(!u16_result.timestamp_replaced && u16_result.effective_timestamp == 1u);
    assert(r1_hrv_store_sample(
               &hrv, &hrv_average, 0u, 2u, 3u,
               8u, 9u, &u16_result) == R1_OK);
    assert(r1_hrv_store_sample(
               &hrv, &hrv_average, 40u, 3u, 4u,
               8u, 9u, &u16_result) == R1_OK);
    assert(hrv.slots[8].average == 22u);
    assert(hrv.slots[8].maximum == 50u);
    assert(hrv.slots[8].minimum == 40u);
    assert(hrv_average.hour == 9u && hrv_average.sample_count == 4u);
    assert(hrv_average.sum == 90u);
    assert(r1_health_u16_latest_sample(
        &hrv, &latest_u16, &latest_timestamp));
    assert(latest_u16 == 40u && latest_timestamp == 3u);

    r1_health_u16_accumulator saturated = {
        3u, 0x5au, UINT16_MAX, UINT32_C(1234),
    };
    uint16_t average = 0u;
    assert(r1_health_u16_accumulate_average(
               &saturated, 3u, 1u, &average) == R1_ERROR_CAPACITY);
    assert(saturated.sample_count == UINT16_MAX && saturated.sum == 1234u);
    assert(r1_hrv_store_sample(
               &hrv, &saturated, 1u, 1u, 2u,
               R1_HEALTH_HOURLY_SLOTS, 0u, &u16_result) == R1_ERROR_LENGTH);
}

static void test_health_crash_snapshot(void) {
    assert(sizeof(r1_health_crash_snapshot) == R1_HEALTH_CRASH_SNAPSHOT_BYTES);
    assert(sizeof(r1_health_crash_record) == R1_HEALTH_CRASH_RECORD_BYTES);

    r1_health_crash_snapshot snapshot;
    assert(r1_health_build_crash_snapshot(
               NULL, 0u, 0, NULL, NULL, NULL, NULL, NULL) ==
           R1_ERROR_ARGUMENT);
    assert(r1_health_build_crash_snapshot(
               &snapshot, UINT32_C(46800), -60, NULL, NULL, NULL,
               NULL, NULL) == R1_OK);
    assert(snapshot.local_hour == 12u && snapshot.available_flags == 0u);

    r1_activity_history activity = {0};
    for (size_t index = 0u; index < R1_ACTIVITY_BUCKETS_PER_HOUR; ++index) {
        r1_activity_bucket *bucket =
            &activity.buckets[12u * R1_ACTIVITY_BUCKETS_PER_HOUR + index];
        bucket->steps = (uint16_t)(UINT16_C(0x0ff0) + (uint16_t)index);
        bucket->active_kilocalories = (uint16_t)(UINT16_C(0x03f0) + (uint16_t)index);
        bucket->all_kilocalories = (uint16_t)(UINT16_C(0x0200) + (uint16_t)index);
        bucket->valid = true;
    }
    r1_health_u8_history heart_rate = {
        .latest_timestamp = UINT32_C(0x11223344),
        .latest_value = 77u,
        .has_latest = true,
    };
    heart_rate.slots[12] = (r1_health_u8_slot){70u, 90u, 60u, 3u, 210u};
    r1_health_u8_accumulator heart_rate_accumulator = {
        12u, 0xa5u, 3u, 210u,
    };
    r1_health_u8_history spo2 = {
        .latest_timestamp = UINT32_C(0x55667788),
        .latest_value = 98u,
        .has_latest = true,
    };
    r1_health_u16_history hrv = {
        .latest_timestamp = UINT32_C(0x99aabbcc),
        .latest_value = 1234u,
        .has_latest = true,
    };
    assert(r1_health_build_crash_snapshot(
               &snapshot, UINT32_C(46800), -60, &activity, &heart_rate,
               &heart_rate_accumulator, &spo2, &hrv) == R1_OK);
    assert(snapshot.local_hour == 12u);
    assert(snapshot.available_flags ==
           (R1_HEALTH_CRASH_FLAG_HEART_RATE | R1_HEALTH_CRASH_FLAG_SPO2 |
            R1_HEALTH_CRASH_FLAG_HRV | R1_HEALTH_CRASH_FLAG_ACTIVITY));
    assert(snapshot.heart_rate_latest_timestamp == UINT32_C(0x11223344));
    assert(snapshot.heart_rate_accumulator_sum == 210u);
    assert(snapshot.heart_rate_accumulator_count == 3u);
    assert(snapshot.heart_rate_average == 70u);
    assert(snapshot.heart_rate_maximum == 90u);
    assert(snapshot.heart_rate_minimum == 60u);
    assert(snapshot.heart_rate_latest_value == 77u);
    assert(snapshot.spo2_latest_timestamp == UINT32_C(0x55667788));
    assert(snapshot.spo2_latest_value == 98u);
    assert(snapshot.hrv_latest_timestamp == UINT32_C(0x99aabbcc));
    assert(snapshot.hrv_latest_value == 1234u);
    for (size_t index = 0u; index < R1_ACTIVITY_BUCKETS_PER_HOUR; ++index) {
        const uint32_t expected =
            ((UINT32_C(0x0ff0) + (uint32_t)index) & UINT32_C(0x0fff)) |
            (((UINT32_C(0x03f0) + (uint32_t)index) & UINT32_C(0x03ff)) << 12u) |
            (((UINT32_C(0x0200) + (uint32_t)index) & UINT32_C(0x03ff)) << 22u);
        assert(snapshot.activity_packed_words[index] == expected);
    }

    heart_rate_accumulator.hour = 11u;
    assert(r1_health_build_crash_snapshot(
               &snapshot, UINT32_C(46800), -60, NULL, &heart_rate,
               &heart_rate_accumulator, NULL, NULL) == R1_OK);
    assert(snapshot.available_flags == R1_HEALTH_CRASH_FLAG_HEART_RATE);
    assert(snapshot.heart_rate_accumulator_sum == 0u);
    assert(snapshot.heart_rate_accumulator_count == 0u);
    assert(snapshot.heart_rate_average == 70u);

    /* The recovered path clamps offsets to twelve hours before selecting the
     * local hour. */
    assert(r1_health_build_crash_snapshot(
               &snapshot, UINT32_C(43200), 721, NULL, NULL, NULL,
               NULL, NULL) == R1_OK);
    assert(snapshot.local_hour == 0u);
    assert(r1_health_build_crash_snapshot(
               &snapshot, UINT32_C(43200), -721, NULL, NULL, NULL,
               NULL, NULL) == R1_OK);
    assert(snapshot.local_hour == 0u);

    r1_health_crash_record record;
    memset(&record, 0x5cu, sizeof record);
    bool copied = true;
    assert(r1_health_crash_record_initialize(
               NULL, 0u, false, 0u, 0, NULL, 0u, NULL, NULL, NULL,
               NULL, NULL, &copied) == R1_ERROR_ARGUMENT);
    assert(r1_health_crash_record_initialize(
               &record, UINT16_C(0xa5a4), true, UINT32_C(46800), -60,
               NULL, 0u, &activity, &heart_rate, &heart_rate_accumulator,
               &spo2, &hrv, &copied) == R1_OK);
    assert(!copied);
    assert(record.bytes[0] == 0x5au && record.bytes[1] == 0x5au);
    assert(record.bytes[4] == 0xa5u && record.bytes[5] == 0xa5u);
    assert(record.bytes[12] == 0x5cu);
    assert(r1_health_crash_record_valid(&record));
    assert(!r1_health_crash_record_valid(NULL));

    uint8_t provider_blob[R1_HEALTH_CRASH_BLOB_BYTES];
    for (size_t index = 0u; index < sizeof provider_blob; ++index) {
        provider_blob[index] = (uint8_t)index;
    }
    heart_rate_accumulator.hour = 12u;
    assert(r1_health_crash_record_initialize(
               &record, 2u, false, UINT32_C(46800), -60,
               provider_blob, sizeof provider_blob, &activity, &heart_rate,
               &heart_rate_accumulator, &spo2, &hrv, &copied) == R1_OK);
    assert(copied && record.bytes[12] == 0u && record.bytes[13] == 1u);
    assert(record.bytes[12u + R1_HEALTH_CRASH_BLOB_BYTES] == 0x5au);
    assert(record.bytes[4] == 2u && record.bytes[5] == 0u);
    assert(r1_health_crash_record_valid(&record));

    const uint8_t *returned_blob = NULL;
    size_t returned_blob_length = 0u;
    assert(r1_health_crash_record_has_magic(&record));
    assert(r1_health_crash_record_get_provider_blob(
               &record, &returned_blob, &returned_blob_length));
    assert(returned_blob == record.bytes + R1_HEALTH_CRASH_BLOB_OFFSET);
    assert(returned_blob_length == R1_HEALTH_CRASH_BLOB_BYTES);
    assert(returned_blob[255] == 0xffu);
    assert(r1_health_crash_record_get_snapshot(&record, &snapshot));
    assert(snapshot.local_hour == 12u && snapshot.available_flags == 0x0fu);
    r1_health_crash_time crash_time;
    assert(r1_health_crash_record_get_time(&record, &crash_time));
    assert(crash_time.utc_timestamp == UINT32_C(46800));
    assert(crash_time.utc_offset_minutes == -60 && !crash_time.clock_valid);

    r1_activity_history restored_activity = {0};
    r1_activity_bucket *restored_first =
        &restored_activity.buckets[12u * R1_ACTIVITY_BUCKETS_PER_HOUR];
    *restored_first = (r1_activity_bucket){32u, 32u, 600u, true};
    restored_activity.total_steps = 32;
    restored_activity.total_kilocalories = 600;
    r1_health_u8_history restored_heart_rate = {0};
    restored_heart_rate.slots[12] =
        (r1_health_u8_slot){65u, 100u, 65u, 0u, 0u};
    r1_health_u8_accumulator restored_accumulator = {
        3u, 0xa5u, 1u, 1u,
    };
    r1_health_u8_history restored_spo2 = {0};
    restored_spo2.slots[12] =
        (r1_health_u8_slot){95u, 99u, 90u, 0u, 0u};
    r1_health_u16_history restored_hrv = {0};
    r1_health_crash_restore_result restore;
    assert(r1_health_crash_record_restore(
               &record, &restored_activity, &restored_heart_rate,
               &restored_accumulator, &restored_spo2, &restored_hrv,
               &restore) == R1_OK);
    assert(restore.action == R1_HEALTH_CRASH_RESTORED);
    assert(restore.local_hour == 12u && restore.available_flags == 0x0fu);
    assert(restore.activity_bucket_count == R1_ACTIVITY_BUCKETS_PER_HOUR);
    assert(restore.heart_rate_applied &&
           restore.heart_rate_accumulator_applied);
    assert(restore.spo2_applied && restore.hrv_applied &&
           restore.snapshot_cleared);
    assert(restored_first->steps == 16u);
    assert(restored_first->active_kilocalories == 16u);
    assert(restored_first->all_kilocalories == 88u);
    int32_t restored_steps = 0;
    int16_t restored_kilocalories = 0;
    for (size_t index = 0u; index < R1_ACTIVITY_BUCKETS; ++index) {
        if (restored_activity.buckets[index].valid) {
            restored_steps += restored_activity.buckets[index].steps;
            restored_kilocalories = (int16_t)(
                restored_kilocalories +
                (int16_t)restored_activity.buckets[index].all_kilocalories);
        }
    }
    assert(restored_activity.total_steps == restored_steps);
    assert(restored_activity.total_kilocalories == restored_kilocalories);
    assert(restored_heart_rate.slots[12].average == 70u);
    assert(restored_heart_rate.slots[12].maximum == 100u);
    assert(restored_heart_rate.slots[12].minimum == 60u);
    assert(restored_heart_rate.latest_value == 77u);
    assert(restored_heart_rate.latest_timestamp == UINT32_C(0x11223344));
    assert(restored_accumulator.hour == 12u);
    assert(restored_accumulator.sample_count == 3u);
    assert(restored_accumulator.sum == 210u);
    assert(restored_accumulator.reserved == 0xa5u);
    assert(restored_spo2.slots[12].average == 95u);
    assert(restored_spo2.latest_value == 98u);
    assert(restored_hrv.slots[12].average == 1234u);
    assert(restored_hrv.slots[12].maximum == 1234u);
    assert(restored_hrv.slots[12].minimum == 1234u);
    assert(restored_hrv.latest_value == 1234u);
    assert(r1_health_crash_record_valid(&record));
    assert(!r1_health_crash_record_get_snapshot(&record, &snapshot));
    assert(r1_health_crash_record_restore(
               &record, NULL, NULL, NULL, NULL, NULL, &restore) == R1_OK);
    assert(restore.action == R1_HEALTH_CRASH_INVALID_OR_EMPTY);

    assert(r1_health_crash_record_clear_provider_blob(&record) == R1_OK);
    assert(r1_health_crash_record_valid(&record));
    assert(!r1_health_crash_record_get_provider_blob(
        &record, &returned_blob, &returned_blob_length));
    assert(r1_health_crash_record_clear_time(&record) == R1_OK);
    assert(!r1_health_crash_record_get_time(&record, &crash_time));

    r1_health_crash_record no_magic = {{0}};
    assert(r1_health_crash_record_restore(
               &no_magic, NULL, NULL, NULL, NULL, NULL, &restore) == R1_OK);
    assert(restore.action == R1_HEALTH_CRASH_NO_MAGIC);
    assert(r1_health_crash_record_clear_snapshot(NULL) == R1_ERROR_ARGUMENT);

    record.bytes[100] ^= 1u;
    assert(!r1_health_crash_record_valid(&record));
}

typedef enum {
    HEALTH_DB_EVENT_LOCK = 1,
    HEALTH_DB_EVENT_UNLOCK,
    HEALTH_DB_EVENT_INITIALIZE,
    HEALTH_DB_EVENT_MUTEX,
    HEALTH_DB_EVENT_SUBSCRIBE_1,
    HEALTH_DB_EVENT_SUBSCRIBE_0,
    HEALTH_DB_EVENT_SET_CLOCK,
    HEALTH_DB_EVENT_MARK_CLOCK_VALID,
    HEALTH_DB_EVENT_CURRENT_CLOCK,
    HEALTH_DB_EVENT_LOCAL_DAY_START,
    HEALTH_DB_EVENT_ALLOCATE,
    HEALTH_DB_EVENT_RECOVER,
    HEALTH_DB_EVENT_RELEASE
} health_db_event;

typedef struct {
    health_db_event events[20];
    size_t event_count;
    r1_error initialize_error;
    bool allocation_available;
    bool recovery_workspace_was_zero;
    uint8_t workspace[R1_HEALTH_DB_RECORD_BYTES];
    char initialized_name[16];
    char initialized_path[16];
    size_t initialized_record_bytes;
    uint32_t restored_timestamp;
    int16_t restored_offset_minutes;
    uint32_t current_timestamp;
    int16_t current_offset_minutes;
    uint32_t day_start_timestamp;
    uint32_t day_start_input_timestamp;
    int16_t day_start_input_offset_minutes;
    uint32_t recovery_from_timestamp;
    uint32_t recovery_to_timestamp;
    size_t recovery_workspace_bytes;
} health_db_trace;

static void health_db_trace_event(
    health_db_trace *trace, health_db_event event) {
    assert(trace->event_count <
           sizeof(trace->events) / sizeof(trace->events[0]));
    trace->events[trace->event_count++] = event;
}

static void health_db_control(void *context, r1_health_db_control control) {
    health_db_trace *trace = context;
    health_db_trace_event(
        trace, control == R1_HEALTH_DB_LOCK_CONTROL
            ? HEALTH_DB_EVENT_LOCK : HEALTH_DB_EVENT_UNLOCK);
}

static r1_error health_db_initialize(
    void *context, const char *name, const char *path, size_t record_bytes) {
    health_db_trace *trace = context;
    health_db_trace_event(trace, HEALTH_DB_EVENT_INITIALIZE);
    assert(strlen(name) < sizeof(trace->initialized_name));
    assert(strlen(path) < sizeof(trace->initialized_path));
    strcpy(trace->initialized_name, name);
    strcpy(trace->initialized_path, path);
    trace->initialized_record_bytes = record_bytes;
    return trace->initialize_error;
}

static void health_db_ensure_mutex(void *context) {
    health_db_trace_event(context, HEALTH_DB_EVENT_MUTEX);
}

static void health_db_subscribe_time(void *context, uint8_t event_index) {
    health_db_trace_event(
        context, event_index == 1u
            ? HEALTH_DB_EVENT_SUBSCRIBE_1 : HEALTH_DB_EVENT_SUBSCRIBE_0);
}

static void health_db_set_clock(
    void *context, uint32_t timestamp, int16_t utc_offset_minutes) {
    health_db_trace *trace = context;
    health_db_trace_event(trace, HEALTH_DB_EVENT_SET_CLOCK);
    trace->restored_timestamp = timestamp;
    trace->restored_offset_minutes = utc_offset_minutes;
}

static void health_db_mark_clock_valid(void *context) {
    health_db_trace_event(context, HEALTH_DB_EVENT_MARK_CLOCK_VALID);
}

static void health_db_current_clock(
    void *context, uint32_t *timestamp, int16_t *utc_offset_minutes) {
    health_db_trace *trace = context;
    health_db_trace_event(trace, HEALTH_DB_EVENT_CURRENT_CLOCK);
    *timestamp = trace->current_timestamp;
    *utc_offset_minutes = trace->current_offset_minutes;
}

static uint32_t health_db_local_day_start(
    void *context, uint32_t timestamp, int16_t utc_offset_minutes) {
    health_db_trace *trace = context;
    health_db_trace_event(trace, HEALTH_DB_EVENT_LOCAL_DAY_START);
    trace->day_start_input_timestamp = timestamp;
    trace->day_start_input_offset_minutes = utc_offset_minutes;
    return trace->day_start_timestamp;
}

static void *health_db_allocate(void *context, size_t bytes) {
    health_db_trace *trace = context;
    health_db_trace_event(trace, HEALTH_DB_EVENT_ALLOCATE);
    assert(bytes == R1_HEALTH_DB_RECORD_BYTES);
    memset(trace->workspace, 0xa5, sizeof(trace->workspace));
    return trace->allocation_available ? trace->workspace : NULL;
}

static void health_db_release(void *context, void *allocation) {
    health_db_trace *trace = context;
    health_db_trace_event(trace, HEALTH_DB_EVENT_RELEASE);
    assert(allocation == trace->workspace);
}

static void health_db_recover(
    void *context, uint32_t from_timestamp, uint32_t to_timestamp,
    uint8_t *workspace, size_t workspace_bytes) {
    health_db_trace *trace = context;
    health_db_trace_event(trace, HEALTH_DB_EVENT_RECOVER);
    trace->recovery_from_timestamp = from_timestamp;
    trace->recovery_to_timestamp = to_timestamp;
    trace->recovery_workspace_bytes = workspace_bytes;
    trace->recovery_workspace_was_zero = true;
    assert(workspace == trace->workspace);
    for (size_t index = 0u; index < workspace_bytes; ++index) {
        if (workspace[index] != 0u) {
            trace->recovery_workspace_was_zero = false;
        }
    }
}

static r1_health_db_startup_ops health_db_ops(health_db_trace *trace) {
    return (r1_health_db_startup_ops){
        .context = trace,
        .control = health_db_control,
        .initialize = health_db_initialize,
        .ensure_mutex = health_db_ensure_mutex,
        .subscribe_time = health_db_subscribe_time,
        .set_clock = health_db_set_clock,
        .mark_clock_valid = health_db_mark_clock_valid,
        .current_clock = health_db_current_clock,
        .local_day_start = health_db_local_day_start,
        .allocate = health_db_allocate,
        .release = health_db_release,
        .recover = health_db_recover,
    };
}

static void initialize_health_db_crash_record(
    r1_health_crash_record *record, bool clock_valid, uint32_t timestamp,
    const r1_activity_history *activity) {
    bool provider_blob_copied = true;
    memset(record, 0, sizeof(*record));
    assert(r1_health_crash_record_initialize(
               record, UINT16_C(0xa4), clock_valid, timestamp, -60,
               NULL, 0u, activity, NULL, NULL, NULL, NULL,
               &provider_blob_copied) == R1_OK);
    assert(!provider_blob_copied);
}

static void assert_health_db_events(
    const health_db_trace *trace, const health_db_event *expected,
    size_t expected_count) {
    assert(trace->event_count == expected_count);
    for (size_t index = 0u; index < expected_count; ++index) {
        assert(trace->events[index] == expected[index]);
    }
}

static void test_health_database_startup(void) {
    uint32_t provider_database = UINT32_C(0x12345678);
    assert(r1_health_db_provider_handle(&provider_database) ==
           &provider_database);
    assert(r1_health_db_provider_handle(NULL) == NULL);

    const uint8_t schema_at_limit[R1_HEALTH_DB_SCHEMA_COUNT] = {
        20u, 20u, 20u, 20u, 20u, 20u,
    };
    const uint8_t schema_too_large[R1_HEALTH_DB_SCHEMA_COUNT] = {
        21u, 20u, 20u, 20u, 20u, 20u,
    };
    r1_health_crash_record record = {{0}};
    r1_activity_history activity = {0};
    r1_health_u8_history heart_rate = {0};
    r1_health_u8_accumulator accumulator = {0};
    r1_health_u8_history spo2 = {0};
    r1_health_u16_history hrv = {0};
    r1_health_db_startup_result result;
    health_db_trace trace = {
        .allocation_available = true,
        .current_timestamp = UINT32_C(1700001234),
        .current_offset_minutes = -360,
        .day_start_timestamp = UINT32_C(1699941600),
    };
    r1_health_db_startup_ops ops = health_db_ops(&trace);

    assert(r1_health_db_startup(
               NULL, &ops, &record, &activity, &heart_rate, &accumulator,
               &spo2, &hrv, &result) == R1_ERROR_ARGUMENT);
    r1_health_db_startup_ops incomplete_ops = ops;
    incomplete_ops.mark_clock_valid = NULL;
    assert(r1_health_db_startup(
               schema_at_limit, &incomplete_ops, &record, &activity,
               &heart_rate, &accumulator, &spo2, &hrv, &result) ==
           R1_ERROR_ARGUMENT);

    assert(r1_health_db_startup(
               schema_too_large, &ops, &record, &activity, &heart_rate,
               &accumulator, &spo2, &hrv, &result) == R1_OK);
    assert(result.action == R1_HEALTH_DB_STARTUP_SCHEMA_TOO_LARGE);
    assert(trace.event_count == 0u);

    trace.initialize_error = R1_ERROR_STATE;
    assert(r1_health_db_startup(
               schema_at_limit, &ops, &record, &activity, &heart_rate,
               &accumulator, &spo2, &hrv, &result) == R1_OK);
    const health_db_event init_failure_events[] = {
        HEALTH_DB_EVENT_LOCK,
        HEALTH_DB_EVENT_UNLOCK,
        HEALTH_DB_EVENT_INITIALIZE,
    };
    assert_health_db_events(
        &trace, init_failure_events,
        sizeof(init_failure_events) / sizeof(init_failure_events[0]));
    assert(result.action == R1_HEALTH_DB_STARTUP_DATABASE_INIT_FAILED);
    assert(result.database_error == R1_ERROR_STATE);
    assert(strcmp(trace.initialized_name, "health") == 0);
    assert(strcmp(trace.initialized_path, "health.db") == 0);
    assert(trace.initialized_record_bytes == R1_HEALTH_DB_RECORD_BYTES);

    memset(&trace, 0, sizeof(trace));
    trace.current_timestamp = UINT32_C(1700001234);
    trace.current_offset_minutes = -360;
    trace.day_start_timestamp = UINT32_C(1699941600);
    ops = health_db_ops(&trace);
    r1_activity_history crash_activity = {0};
    crash_activity.buckets[12u * R1_ACTIVITY_BUCKETS_PER_HOUR] =
        (r1_activity_bucket){7u, 3u, 9u, true};
    initialize_health_db_crash_record(
        &record, false, UINT32_C(46800), &crash_activity);
    assert(r1_health_db_startup(
               schema_at_limit, &ops, &record, &activity, &heart_rate,
               &accumulator, &spo2, &hrv, &result) == R1_OK);
    const health_db_event allocation_failure_events[] = {
        HEALTH_DB_EVENT_LOCK,
        HEALTH_DB_EVENT_UNLOCK,
        HEALTH_DB_EVENT_INITIALIZE,
        HEALTH_DB_EVENT_MUTEX,
        HEALTH_DB_EVENT_SUBSCRIBE_1,
        HEALTH_DB_EVENT_SUBSCRIBE_0,
        HEALTH_DB_EVENT_SET_CLOCK,
        HEALTH_DB_EVENT_CURRENT_CLOCK,
        HEALTH_DB_EVENT_LOCAL_DAY_START,
        HEALTH_DB_EVENT_ALLOCATE,
    };
    assert_health_db_events(
        &trace, allocation_failure_events,
        sizeof(allocation_failure_events) /
            sizeof(allocation_failure_events[0]));
    assert(result.action == R1_HEALTH_DB_STARTUP_WORKSPACE_UNAVAILABLE);
    assert(result.crash_time_restored);
    assert(result.crash_time_clear_error == R1_OK);
    assert(trace.restored_timestamp == UINT32_C(46800));
    assert(trace.restored_offset_minutes == -60);
    assert(!result.recovery_attempted);
    assert(r1_health_crash_record_valid(&record));
    r1_health_crash_time crash_time;
    assert(!r1_health_crash_record_get_time(&record, &crash_time));
    r1_health_crash_snapshot crash_snapshot;
    assert(r1_health_crash_record_get_snapshot(&record, &crash_snapshot));

    memset(&trace, 0, sizeof(trace));
    trace.allocation_available = true;
    trace.current_timestamp = UINT32_C(1700001234);
    trace.current_offset_minutes = -360;
    trace.day_start_timestamp = UINT32_C(1699941600);
    ops = health_db_ops(&trace);
    memset(&activity, 0, sizeof(activity));
    initialize_health_db_crash_record(
        &record, true, UINT32_C(46800), &crash_activity);
    assert(r1_health_db_startup(
               schema_at_limit, &ops, &record, &activity, &heart_rate,
               &accumulator, &spo2, &hrv, &result) == R1_OK);
    const health_db_event success_events[] = {
        HEALTH_DB_EVENT_LOCK,
        HEALTH_DB_EVENT_UNLOCK,
        HEALTH_DB_EVENT_INITIALIZE,
        HEALTH_DB_EVENT_MUTEX,
        HEALTH_DB_EVENT_SUBSCRIBE_1,
        HEALTH_DB_EVENT_SUBSCRIBE_0,
        HEALTH_DB_EVENT_SET_CLOCK,
        HEALTH_DB_EVENT_MARK_CLOCK_VALID,
        HEALTH_DB_EVENT_CURRENT_CLOCK,
        HEALTH_DB_EVENT_LOCAL_DAY_START,
        HEALTH_DB_EVENT_ALLOCATE,
        HEALTH_DB_EVENT_RECOVER,
        HEALTH_DB_EVENT_RELEASE,
    };
    assert_health_db_events(
        &trace, success_events,
        sizeof(success_events) / sizeof(success_events[0]));
    assert(result.action == R1_HEALTH_DB_STARTUP_COMPLETED);
    assert(result.database_error == R1_OK);
    assert(result.crash_time_restored && result.recovery_attempted);
    assert(result.current_timestamp == trace.current_timestamp);
    assert(result.utc_offset_minutes == trace.current_offset_minutes);
    assert(result.local_day_start_timestamp == trace.day_start_timestamp);
    assert(trace.day_start_input_timestamp == trace.current_timestamp);
    assert(trace.day_start_input_offset_minutes == trace.current_offset_minutes);
    assert(trace.recovery_from_timestamp == trace.day_start_timestamp);
    assert(trace.recovery_to_timestamp == trace.current_timestamp);
    assert(trace.recovery_workspace_bytes == R1_HEALTH_DB_RECORD_BYTES);
    assert(trace.recovery_workspace_was_zero);
    assert(result.crash_restore.action == R1_HEALTH_CRASH_RESTORED);
    assert(result.crash_restore.snapshot_cleared);
    assert(activity.buckets[12u * R1_ACTIVITY_BUCKETS_PER_HOUR].steps == 7u);
    assert(!r1_health_crash_record_get_snapshot(&record, &crash_snapshot));
    assert(r1_health_crash_record_valid(&record));

    memset(&trace, 0, sizeof(trace));
    trace.allocation_available = true;
    ops = health_db_ops(&trace);
    initialize_health_db_crash_record(&record, true, 0u, NULL);
    assert(r1_health_db_startup(
               schema_at_limit, &ops, &record, &activity, &heart_rate,
               &accumulator, &spo2, &hrv, &result) == R1_OK);
    assert(!result.crash_time_restored);
    assert(result.crash_restore.action == R1_HEALTH_CRASH_INVALID_OR_EMPTY);
    for (size_t index = 0u; index < trace.event_count; ++index) {
        assert(trace.events[index] != HEALTH_DB_EVENT_SET_CLOCK);
        assert(trace.events[index] != HEALTH_DB_EVENT_MARK_CLOCK_VALID);
    }
}

typedef struct {
    uint32_t kernel_state;
    uint32_t tick_frequency;
    int32_t acquire_result;
    size_t kernel_state_calls;
    size_t tick_frequency_calls;
    size_t acquire_calls;
    size_t release_calls;
    size_t delay_calls;
    void *last_semaphore;
    uint32_t last_ticks;
    uint32_t acquired_ticks[8];
    uint32_t last_delay_us;
    r1_twi_sync_state *delayed_state;
    size_t complete_after_delays;
    uint32_t transmit_results[4];
    size_t transmit_result_count;
    size_t transmit_calls;
    size_t receive_calls;
    size_t fatal_calls;
    uint8_t last_address;
    uint8_t last_transmit[81];
    uint32_t last_transmit_length;
    uint32_t last_receive_length;
    bool last_no_stop;
    uint32_t receive_result;
    uint32_t last_fatal_status;
    size_t configure_pin_calls;
    size_t initialize_calls;
    size_t enable_calls;
    size_t disable_calls;
    size_t uninitialize_calls;
    size_t power_cycle_calls;
    uint32_t configured_pins[2];
    uint32_t initialize_result;
    r1_twi_lifecycle_config last_lifecycle_config;
    r1_twi_sync_state *last_transfer_state;
} twi_sync_trace;

static uint32_t twi_sync_kernel_state(void *context) {
    twi_sync_trace *trace = context;
    ++trace->kernel_state_calls;
    return trace->kernel_state;
}

static uint32_t twi_sync_tick_frequency(void *context) {
    twi_sync_trace *trace = context;
    ++trace->tick_frequency_calls;
    return trace->tick_frequency;
}

static int32_t twi_sync_semaphore_acquire(
    void *context, void *semaphore, uint32_t ticks) {
    twi_sync_trace *trace = context;
    ++trace->acquire_calls;
    trace->last_semaphore = semaphore;
    trace->last_ticks = ticks;
    if (trace->acquire_calls <= 8u) {
        trace->acquired_ticks[trace->acquire_calls - 1u] = ticks;
    }
    return trace->acquire_result;
}

static void twi_sync_semaphore_release(void *context, void *semaphore) {
    twi_sync_trace *trace = context;
    ++trace->release_calls;
    trace->last_semaphore = semaphore;
}

static void twi_sync_delay_us(void *context, uint32_t microseconds) {
    twi_sync_trace *trace = context;
    ++trace->delay_calls;
    trace->last_delay_us = microseconds;
    if (trace->delayed_state != NULL && trace->complete_after_delays != 0u &&
        trace->delay_calls == trace->complete_after_delays) {
        trace->delayed_state->completed = true;
    }
}

static r1_twi_sync_ops twi_sync_ops(twi_sync_trace *trace) {
    return (r1_twi_sync_ops){
        .context = trace,
        .kernel_state = twi_sync_kernel_state,
        .tick_frequency = twi_sync_tick_frequency,
        .semaphore_acquire = twi_sync_semaphore_acquire,
        .semaphore_release = twi_sync_semaphore_release,
        .delay_us = twi_sync_delay_us,
    };
}

static uint32_t twi_transfer_transmit(
    void *context, void *bus, uint8_t address, const uint8_t *data,
    uint32_t length, bool no_stop) {
    twi_sync_trace *trace = context;
    assert(bus != NULL && length <= sizeof(trace->last_transmit));
    trace->last_address = address;
    trace->last_transmit_length = length;
    trace->last_no_stop = no_stop;
    memcpy(trace->last_transmit, data, length);
    const size_t index = trace->transmit_calls++;
    return index < trace->transmit_result_count ?
        trace->transmit_results[index] : R1_TWI_SYNC_STATUS_OK;
}

static uint32_t twi_transfer_receive(
    void *context, void *bus, uint8_t address, uint8_t *data,
    uint32_t length) {
    twi_sync_trace *trace = context;
    assert(bus != NULL && data != NULL);
    ++trace->receive_calls;
    trace->last_address = address;
    trace->last_receive_length = length;
    return trace->receive_result;
}

static void twi_transfer_fatal_error(void *context, uint32_t status) {
    twi_sync_trace *trace = context;
    ++trace->fatal_calls;
    trace->last_fatal_status = status;
}

static r1_twi_transfer_ops twi_transfer_ops(
    twi_sync_trace *trace, const r1_twi_sync_ops *sync) {
    return (r1_twi_transfer_ops){
        .context = trace,
        .transmit = twi_transfer_transmit,
        .receive = twi_transfer_receive,
        .fatal_error = twi_transfer_fatal_error,
        .sync = sync,
    };
}

static void twi_lifecycle_configure_pin(void *context, uint32_t pin) {
    twi_sync_trace *trace = context;
    assert(trace->configure_pin_calls < 2u);
    trace->configured_pins[trace->configure_pin_calls++] = pin;
}

static uint32_t twi_lifecycle_initialize(
    void *context, void *bus, const r1_twi_lifecycle_config *config,
    r1_twi_sync_state *transfer_state) {
    twi_sync_trace *trace = context;
    assert(bus != NULL);
    ++trace->initialize_calls;
    trace->last_lifecycle_config = *config;
    trace->last_transfer_state = transfer_state;
    return trace->initialize_result;
}

static void twi_lifecycle_enable(void *context, void *bus) {
    twi_sync_trace *trace = context;
    assert(bus != NULL);
    ++trace->enable_calls;
}

static void twi_lifecycle_disable(void *context, void *bus) {
    twi_sync_trace *trace = context;
    assert(bus != NULL);
    ++trace->disable_calls;
}

static void twi_lifecycle_uninitialize(void *context, void *bus) {
    twi_sync_trace *trace = context;
    assert(bus != NULL);
    ++trace->uninitialize_calls;
}

static void twi_lifecycle_power_cycle(void *context, void *bus) {
    twi_sync_trace *trace = context;
    assert(bus != NULL);
    ++trace->power_cycle_calls;
}

static void twi_software_release_pin(void *context, uint32_t pin) {
    twi_sync_trace *trace = context;
    assert(trace->configure_pin_calls < 2u);
    trace->configured_pins[trace->configure_pin_calls++] = pin;
}

static r1_twi_lifecycle_ops twi_lifecycle_ops(twi_sync_trace *trace) {
    return (r1_twi_lifecycle_ops){
        .context = trace,
        .configure_pin = twi_lifecycle_configure_pin,
        .initialize = twi_lifecycle_initialize,
        .enable = twi_lifecycle_enable,
        .disable = twi_lifecycle_disable,
        .uninitialize = twi_lifecycle_uninitialize,
        .power_cycle = twi_lifecycle_power_cycle,
    };
}

static void test_twi_synchronization_adapter(void) {
    twi_sync_trace trace = {
        .kernel_state = 2u,
        .tick_frequency = 1024u,
    };
    r1_twi_sync_ops ops = twi_sync_ops(&trace);
    r1_twi_sync_state state = {0};
    assert(r1_twi_sync_complete(NULL, 0u, &ops) == R1_ERROR_ARGUMENT);
    assert(r1_twi_sync_wait(NULL, 0u, &ops) ==
           R1_TWI_SYNC_STATUS_ARGUMENT);

    state.failed = true;
    state.status = UINT32_C(0xa5a5a5a5);
    assert(r1_twi_sync_complete(
               &state, R1_TWI_SYNC_EVENT_DONE, &ops) == R1_OK);
    assert(state.completed && state.failed);
    assert(state.status == R1_TWI_SYNC_STATUS_OK);
    assert(trace.release_calls == 0u);

    int semaphore;
    state = (r1_twi_sync_state){
        .semaphore_enabled = true,
        .semaphore = &semaphore,
    };
    assert(r1_twi_sync_complete(
               &state, R1_TWI_SYNC_EVENT_ADDRESS_NACK, &ops) == R1_OK);
    assert(state.completed && state.failed);
    assert(state.status == R1_TWI_SYNC_STATUS_ADDRESS_NACK);
    assert(trace.release_calls == 1u && trace.last_semaphore == &semaphore);

    state.completed = false;
    state.failed = false;
    trace.kernel_state = 3u;
    assert(r1_twi_sync_complete(
               &state, R1_TWI_SYNC_EVENT_DATA_NACK, &ops) == R1_OK);
    assert(state.completed && state.failed);
    assert(state.status == R1_TWI_SYNC_STATUS_DATA_NACK);
    assert(trace.release_calls == 2u);

    state.completed = false;
    state.failed = false;
    state.status = UINT32_C(0x11223344);
    trace.kernel_state = 1u;
    assert(r1_twi_sync_complete(&state, 4u, &ops) == R1_OK);
    assert(state.completed && state.failed);
    assert(state.status == UINT32_C(0x11223344));
    assert(trace.release_calls == 2u);

    memset(&trace, 0, sizeof(trace));
    trace.kernel_state = 2u;
    trace.tick_frequency = 1024u;
    ops = twi_sync_ops(&trace);
    state = (r1_twi_sync_state){
        .semaphore_enabled = true,
        .semaphore = &semaphore,
        .status = R1_TWI_SYNC_STATUS_DATA_NACK,
    };
    assert(r1_twi_sync_wait(&state, 500u, &ops) ==
           R1_TWI_SYNC_STATUS_DATA_NACK);
    assert(trace.acquire_calls == 1u);
    assert(trace.last_semaphore == &semaphore && trace.last_ticks == 512u);
    assert(trace.delay_calls == 0u);

    assert(r1_twi_sync_wait(&state, 0u, &ops) ==
           R1_TWI_SYNC_STATUS_DATA_NACK);
    assert(trace.last_ticks == 1u);
    trace.acquire_result = -1;
    assert(r1_twi_sync_wait(&state, 10u, &ops) ==
           R1_TWI_SYNC_STATUS_TIMEOUT);

    memset(&trace, 0, sizeof(trace));
    trace.kernel_state = 1u;
    ops = twi_sync_ops(&trace);
    state = (r1_twi_sync_state){
        .status = R1_TWI_SYNC_STATUS_ADDRESS_NACK,
    };
    trace.delayed_state = &state;
    trace.complete_after_delays = 3u;
    assert(r1_twi_sync_wait(&state, 10u, &ops) ==
           R1_TWI_SYNC_STATUS_ADDRESS_NACK);
    assert(trace.delay_calls == 3u);
    assert(trace.last_delay_us == R1_TWI_SYNC_DELAY_US);
    assert(trace.acquire_calls == 0u && trace.tick_frequency_calls == 0u);

    state.completed = false;
    trace.delay_calls = 0u;
    trace.complete_after_delays = 0u;
    assert(r1_twi_sync_wait(&state, 0u, &ops) ==
           R1_TWI_SYNC_STATUS_TIMEOUT);
    assert(trace.delay_calls == 0u);

    int bus;
    uint8_t read_buffer[300] = {0};
    const uint8_t write_data[] = {0x11u, 0x22u, 0x33u};
    memset(&trace, 0, sizeof(trace));
    trace.kernel_state = 2u;
    trace.tick_frequency = 1000u;
    ops = twi_sync_ops(&trace);
    r1_twi_transfer_ops transfer_ops = twi_transfer_ops(&trace, &ops);
    state = (r1_twi_sync_state){
        .failed = true,
        .semaphore_enabled = true,
        .semaphore = &semaphore,
    };
    assert(r1_twi_primary_register_read(
               &state, &bus, 0x52u, 0xa0u, read_buffer, 300u,
               &transfer_ops) == R1_TWI_SYNC_STATUS_OK);
    assert(!state.failed);
    assert(trace.transmit_calls == 1u && trace.receive_calls == 1u);
    assert(trace.last_transmit_length == 1u && trace.last_transmit[0] == 0xa0u);
    assert(trace.last_no_stop && trace.last_receive_length == 44u);
    assert(trace.acquire_calls == 2u);
    assert(trace.acquired_ticks[0] == 500u && trace.acquired_ticks[1] == 500u);

    memset(&trace, 0, sizeof(trace));
    trace.kernel_state = 2u;
    trace.tick_frequency = 1000u;
    ops = twi_sync_ops(&trace);
    transfer_ops = twi_transfer_ops(&trace, &ops);
    state = (r1_twi_sync_state){
        .failed = true,
        .semaphore_enabled = true,
        .semaphore = &semaphore,
    };
    assert(r1_twi_secondary_register_read(
               &state, &bus, 0x53u, 0xa1u, read_buffer, 300u,
               &transfer_ops) == R1_TWI_SYNC_STATUS_OK);
    assert(state.failed);
    assert(trace.last_receive_length == 300u);
    assert(trace.acquired_ticks[0] == 100u && trace.acquired_ticks[1] == 500u);

    memset(&trace, 0, sizeof(trace));
    trace.kernel_state = 2u;
    trace.tick_frequency = 1000u;
    trace.transmit_results[0] = 2u;
    trace.transmit_results[1] = 0u;
    trace.transmit_result_count = 2u;
    ops = twi_sync_ops(&trace);
    transfer_ops = twi_transfer_ops(&trace, &ops);
    state = (r1_twi_sync_state){
        .failed = true,
        .semaphore_enabled = true,
        .semaphore = &semaphore,
    };
    assert(r1_twi_primary_register_write(
               &state, &bus, 0x54u, 0xa2u, write_data,
               sizeof(write_data), &transfer_ops) == R1_TWI_SYNC_STATUS_OK);
    assert(!state.failed && trace.transmit_calls == 2u);
    assert(trace.fatal_calls == 1u && trace.last_fatal_status == 2u);
    assert(trace.last_transmit_length == 4u && !trace.last_no_stop);
    assert(memcmp(trace.last_transmit,
                  (const uint8_t[]){0xa2u, 0x11u, 0x22u, 0x33u}, 4u) == 0);
    assert(trace.last_ticks == 500u);

    trace.transmit_calls = 0u;
    trace.transmit_results[0] = R1_TWI_SYNC_STATUS_BUSY;
    trace.transmit_result_count = 1u;
    state.failed = true;
    assert(r1_twi_secondary_register_write(
               &state, &bus, 0x55u, 0xa3u, write_data,
               sizeof(write_data), &transfer_ops) == R1_TWI_SYNC_STATUS_BUSY);
    assert(state.failed && trace.acquire_calls == 1u);
    assert(r1_twi_secondary_register_write(
               &state, &bus, 0x55u, 0xa3u, write_data,
               R1_TWI_WRITE_DATA_MAX + 1u, &transfer_ops) ==
           R1_TWI_SYNC_STATUS_DATA_SIZE);
    assert(r1_twi_primary_register_read(
               NULL, &bus, 0x52u, 0xa0u, read_buffer, 1u,
               &transfer_ops) == R1_TWI_SYNC_STATUS_ARGUMENT);

    memset(&trace, 0, sizeof(trace));
    r1_twi_lifecycle_ops lifecycle_ops = twi_lifecycle_ops(&trace);
    const r1_twi_lifecycle_config lifecycle_config = {
        .scl_pin = 12u,
        .sda_pin = 1u,
        .frequency = UINT32_C(0x06680000),
        .interrupt_priority = 2u,
        .clear_bus_init = false,
        .hold_bus_uninit = true,
        .preconfigure_pins = true,
    };
    r1_twi_sync_state transfer_state = {0};
    r1_twi_lifecycle_state lifecycle_state = {
        .transfer_state = &transfer_state,
    };
    assert(r1_twi_lifecycle_initialize(
               &lifecycle_state, &bus, &lifecycle_config,
               &lifecycle_ops) == R1_TWI_SYNC_STATUS_OK);
    assert(lifecycle_state.initialized);
    assert(trace.configure_pin_calls == 2u);
    assert(trace.configured_pins[0] == 12u && trace.configured_pins[1] == 1u);
    assert(trace.initialize_calls == 1u && trace.enable_calls == 1u);
    assert(trace.last_transfer_state == &transfer_state);
    assert(memcmp(&trace.last_lifecycle_config, &lifecycle_config,
                  sizeof(lifecycle_config)) == 0);
    assert(r1_twi_lifecycle_initialize(
               &lifecycle_state, &bus, &lifecycle_config,
               &lifecycle_ops) == R1_TWI_SYNC_STATUS_OK);
    assert(trace.initialize_calls == 1u && trace.enable_calls == 1u);
    assert(r1_twi_lifecycle_shutdown(
               &lifecycle_state, &bus, &lifecycle_ops) ==
           R1_TWI_SYNC_STATUS_OK);
    assert(!lifecycle_state.initialized);
    assert(trace.disable_calls == 1u && trace.uninitialize_calls == 1u);
    assert(trace.power_cycle_calls == 1u);
    assert(r1_twi_lifecycle_shutdown(
               &lifecycle_state, &bus, &lifecycle_ops) ==
           R1_TWI_SYNC_STATUS_OK);
    assert(trace.disable_calls == 1u && trace.uninitialize_calls == 1u);
    assert(trace.power_cycle_calls == 1u);

    memset(&trace, 0, sizeof(trace));
    lifecycle_ops = twi_lifecycle_ops(&trace);
    lifecycle_state = (r1_twi_lifecycle_state){
        .transfer_state = &transfer_state,
    };
    assert(r1_twi_primary_lifecycle_initialize(
               &lifecycle_state, &bus, 12u, 1u, &lifecycle_ops) ==
           R1_TWI_SYNC_STATUS_OK);
    assert(trace.configure_pin_calls == 2u);
    assert(trace.last_lifecycle_config.frequency == UINT32_C(0x06680000));
    assert(trace.last_lifecycle_config.interrupt_priority == 2u);
    assert(!trace.last_lifecycle_config.clear_bus_init);
    assert(trace.last_lifecycle_config.hold_bus_uninit);
    assert(trace.last_lifecycle_config.preconfigure_pins);

    memset(&trace, 0, sizeof(trace));
    lifecycle_ops = twi_lifecycle_ops(&trace);
    lifecycle_state = (r1_twi_lifecycle_state){
        .transfer_state = &transfer_state,
    };
    assert(r1_twi_secondary_lifecycle_initialize(
               &lifecycle_state, &bus, 4u, 5u, &lifecycle_ops) ==
           R1_TWI_SYNC_STATUS_OK);
    assert(trace.configure_pin_calls == 0u);
    assert(trace.last_lifecycle_config.scl_pin == 4u);
    assert(trace.last_lifecycle_config.sda_pin == 5u);
    assert(trace.last_lifecycle_config.frequency == UINT32_C(0x06680000));
    assert(trace.last_lifecycle_config.interrupt_priority == 2u);
    assert(!trace.last_lifecycle_config.clear_bus_init);
    assert(!trace.last_lifecycle_config.hold_bus_uninit);
    assert(!trace.last_lifecycle_config.preconfigure_pins);

    memset(&trace, 0, sizeof(trace));
    trace.initialize_result = 17u;
    lifecycle_ops = twi_lifecycle_ops(&trace);
    lifecycle_state = (r1_twi_lifecycle_state){
        .transfer_state = &transfer_state,
    };
    assert(r1_twi_lifecycle_initialize(
               &lifecycle_state, &bus, &lifecycle_config,
               &lifecycle_ops) == 17u);
    assert(!lifecycle_state.initialized && trace.enable_calls == 0u);
    assert(r1_twi_lifecycle_initialize(
               NULL, &bus, &lifecycle_config, &lifecycle_ops) ==
           R1_TWI_SYNC_STATUS_ARGUMENT);

    memset(&trace, 0, sizeof(trace));
    r1_twi_software_lifecycle_ops software_lifecycle_ops = {
        .context = &trace,
        .release_pin = twi_software_release_pin,
    };
    r1_twi_software_lifecycle_state software_lifecycle_state = {
        .initialized = true,
        .scl_pin = 28u,
        .sda_pin = 45u,
    };
    assert(r1_twi_software_lifecycle_shutdown(
               &software_lifecycle_state, &software_lifecycle_ops) ==
           R1_TWI_SYNC_STATUS_OK);
    assert(!software_lifecycle_state.initialized);
    assert(trace.configure_pin_calls == 2u);
    assert(trace.configured_pins[0] == 28u &&
           trace.configured_pins[1] == 45u);
    assert(r1_twi_software_lifecycle_shutdown(
               &software_lifecycle_state, &software_lifecycle_ops) ==
           R1_TWI_SYNC_STATUS_OK);
    assert(trace.configure_pin_calls == 2u);
    assert(r1_twi_software_lifecycle_shutdown(NULL, &software_lifecycle_ops) ==
           R1_TWI_SYNC_STATUS_ARGUMENT);
}

static r1_error capture_health_u8_offline(
    void *context, const r1_health_u8_offline_packet *packet) {
    health_offline_capture *capture = context;
    assert(capture->count < 3u);
    const size_t index = capture->count;
    const r1_error error = r1_health_encode_daily_u8(
        &packet->history, capture->payloads[index],
        sizeof capture->payloads[index], &capture->lengths[index]);
    if (error == R1_OK) {
        capture->maximum_timestamps[index] = packet->maximum_recorded_timestamp;
        capture->count += 1u;
    }
    return error;
}

static r1_error capture_health_u16_offline(
    void *context, const r1_health_u16_offline_packet *packet) {
    health_offline_capture *capture = context;
    assert(capture->count < 3u);
    const size_t index = capture->count;
    const r1_error error = r1_health_encode_daily_u16(
        &packet->history, capture->payloads[index],
        sizeof capture->payloads[index], &capture->lengths[index]);
    if (error == R1_OK) {
        capture->maximum_timestamps[index] = packet->maximum_recorded_timestamp;
        capture->count += 1u;
    }
    return error;
}

static r1_error reject_health_u16_offline(
    void *context, const r1_health_u16_offline_packet *packet) {
    (void)context;
    (void)packet;
    return R1_ERROR_STATE;
}

static r1_error reject_health_u8_offline(
    void *context, const r1_health_u8_offline_packet *packet) {
    (void)context;
    (void)packet;
    return R1_ERROR_STATE;
}

static void test_scalar_health_ram_cache_merge(void) {
    r1_health_u8_offline_packet builder = {0};
    r1_health_u8_history cache = {0};
    health_offline_capture capture = {0};
    r1_health_u8_day_flush_result flush;

    cache.slots[0] = (r1_health_u8_slot){0x11u, 0x22u, 0x08u, 7u, 0u};
    cache.slots[1] = (r1_health_u8_slot){0x22u, 0x33u, 0x11u, 8u, 0u};
    cache.slots[2] = (r1_health_u8_slot){0x55u, 0x66u, 0x44u, 9u, 0u};
    cache.slots[3] = (r1_health_u8_slot){0u, 0xffu, 0xffu, 1u, 0u};

    assert(r1_health_u8_ram_cache_merge(
               &builder, &cache, 1000u, 4600u, 10000u, -300,
               capture_health_u8_offline, &capture, &flush) == R1_OK);
    assert(flush.emitted && !flush.dropped_future_acknowledgement);
    assert(flush.encoded_length == 15u && capture.count == 1u);
    assert(capture.maximum_timestamps[0] == 8200u);
    static const uint8_t expected[] = {
        2u, 0xd4u, 0xfeu, 0xe8u, 0x03u, 0u, 0u,
        1u, 0x22u, 0x33u, 0x11u,
        2u, 0x55u, 0x66u, 0x44u,
    };
    assert(capture.lengths[0] == sizeof expected);
    assert(memcmp(capture.payloads[0], expected, sizeof expected) == 0);
    assert(cache.local_day_start == 1000u && cache.utc_offset_minutes == -300);
    assert(builder.maximum_recorded_timestamp == 0u);
    assert(builder.history.local_day_start == 0u);
    assert(builder.history.slots[2].average == 0u);

    /* The current hour remains eligible even before the requested window. */
    cache = (r1_health_u8_history){0};
    cache.slots[2] = (r1_health_u8_slot){5u, 6u, 4u, 1u, 5u};
    assert(r1_health_u8_ram_cache_merge(
               &builder, &cache, 1000u, 9000u, 10000u, 60,
               capture_health_u8_offline, &capture, &flush) == R1_OK);
    assert(flush.emitted && flush.encoded_length == 11u);
    assert(capture.count == 2u && capture.maximum_timestamps[1] == 8200u);
    assert(capture.payloads[1][7] == 2u);

    /* Elapsed days cap the special current-hour index at slot 23. */
    cache = (r1_health_u8_history){0};
    cache.slots[23] = (r1_health_u8_slot){9u, 10u, 8u, 1u, 9u};
    assert(r1_health_u8_ram_cache_merge(
               &builder, &cache, 1000u, 90000u, 100000u, 0,
               capture_health_u8_offline, &capture, &flush) == R1_OK);
    assert(flush.emitted && capture.count == 3u);
    assert(capture.maximum_timestamps[2] == 83800u);
    assert(capture.payloads[2][7] == 23u);

    const r1_health_u8_offline_packet before_skip = builder;
    assert(r1_health_u8_ram_cache_merge(
               &builder, &cache, 0u, 0u, 100000u, 0,
               capture_health_u8_offline, &capture, &flush) == R1_OK);
    assert(memcmp(&builder, &before_skip, sizeof builder) == 0);
    assert(r1_health_u8_ram_cache_merge(
               &builder, &cache, 1000u, 100000u, 100000u, 0,
               capture_health_u8_offline, &capture, &flush) == R1_OK);
    assert(memcmp(&builder, &before_skip, sizeof builder) == 0);
    assert(r1_health_u8_ram_cache_merge(
               &builder, &cache, 100001u, 0u, 100000u, 0,
               capture_health_u8_offline, &capture, &flush) == R1_ERROR_STATE);
    assert(r1_health_u8_ram_cache_merge(
               NULL, &cache, 1000u, 0u, 100000u, 0,
               capture_health_u8_offline, &capture, &flush)
           == R1_ERROR_ARGUMENT);

    cache = (r1_health_u8_history){0};
    cache.slots[0] = (r1_health_u8_slot){1u, 2u, 1u, 1u, 1u};
    assert(r1_health_u8_ram_cache_merge(
               &builder, &cache, 1000u, 1u, 2000u, 0,
               reject_health_u8_offline, NULL, &flush) == R1_ERROR_STATE);
    assert(!flush.emitted && flush.encoded_length == 11u);
    assert(builder.maximum_recorded_timestamp == 0u);
    assert(builder.history.slots[0].average == 0u);
}

static void test_hrv_ram_cache_merge(void) {
    r1_health_u16_offline_packet builder = {0};
    r1_health_u16_history cache = {0};
    health_offline_capture capture = {0};
    r1_health_u16_day_flush_result flush;

    cache.latest_timestamp = 9999u;
    cache.latest_value = 0x4444u;
    cache.has_latest = true;
    cache.slots[0] = (r1_health_u16_slot){0x1111u, 0x2222u, 0x0808u, 7u, 0u};
    cache.slots[1] = (r1_health_u16_slot){0x2222u, 0x3333u, 0x1111u, 8u, 0u};
    cache.slots[2] = (r1_health_u16_slot){0x5555u, 0x6666u, 0x4444u, 9u, 0u};
    cache.slots[3] = (r1_health_u16_slot){0u, 0xffffu, 0xffffu, 1u, 0u};

    assert(r1_health_u16_ram_cache_merge(
               &builder, &cache, 1000u, 4600u, 10000u, -300,
               capture_health_u16_offline, &capture, &flush) == R1_OK);
    assert(flush.emitted && !flush.dropped_future_acknowledgement);
    assert(flush.encoded_length == 27u && capture.count == 1u);
    assert(capture.maximum_timestamps[0] == 8200u);
    static const uint8_t expected[] = {
        2u, 0xd4u, 0xfeu, 0xe8u, 0x03u, 0u, 0u,
        0x0fu, 0x27u, 0u, 0u, 0x44u, 0x44u,
        1u, 0x22u, 0x22u, 0x33u, 0x33u, 0x11u, 0x11u,
        2u, 0x55u, 0x55u, 0x66u, 0x66u, 0x44u, 0x44u,
    };
    assert(capture.lengths[0] == sizeof expected);
    assert(memcmp(capture.payloads[0], expected, sizeof expected) == 0);
    assert(cache.local_day_start == 1000u && cache.utc_offset_minutes == -300);
    assert(builder.maximum_recorded_timestamp == 0u);
    assert(builder.history.local_day_start == 0u);
    assert(builder.history.slots[2].average == 0u);

    /* The current hour remains eligible even before the requested window. */
    cache = (r1_health_u16_history){0};
    cache.slots[2] = (r1_health_u16_slot){5u, 6u, 4u, 1u, 5u};
    assert(r1_health_u16_ram_cache_merge(
               &builder, &cache, 1000u, 9000u, 10000u, 60,
               capture_health_u16_offline, &capture, &flush) == R1_OK);
    assert(flush.emitted && flush.encoded_length == 20u);
    assert(capture.count == 2u && capture.maximum_timestamps[1] == 8200u);
    assert(capture.payloads[1][13] == 2u);

    /* Elapsed days cap the special current-hour index at slot 23. */
    cache = (r1_health_u16_history){0};
    cache.slots[23] = (r1_health_u16_slot){9u, 10u, 8u, 1u, 9u};
    assert(r1_health_u16_ram_cache_merge(
               &builder, &cache, 1000u, 90000u, 100000u, 0,
               capture_health_u16_offline, &capture, &flush) == R1_OK);
    assert(flush.emitted && capture.count == 3u);
    assert(capture.maximum_timestamps[2] == 83800u);
    assert(capture.payloads[2][13] == 23u);

    const r1_health_u16_offline_packet before_skip = builder;
    assert(r1_health_u16_ram_cache_merge(
               &builder, &cache, 0u, 0u, 100000u, 0,
               capture_health_u16_offline, &capture, &flush) == R1_OK);
    assert(memcmp(&builder, &before_skip, sizeof builder) == 0);
    assert(r1_health_u16_ram_cache_merge(
               &builder, &cache, 1000u, 100000u, 100000u, 0,
               capture_health_u16_offline, &capture, &flush) == R1_OK);
    assert(memcmp(&builder, &before_skip, sizeof builder) == 0);
    assert(r1_health_u16_ram_cache_merge(
               &builder, &cache, 100001u, 0u, 100000u, 0,
               capture_health_u16_offline, &capture, &flush) == R1_ERROR_STATE);
    assert(r1_health_u16_ram_cache_merge(
               NULL, &cache, 1000u, 0u, 100000u, 0,
               capture_health_u16_offline, &capture, &flush)
           == R1_ERROR_ARGUMENT);

    cache = (r1_health_u16_history){0};
    cache.slots[0] = (r1_health_u16_slot){1u, 2u, 1u, 1u, 1u};
    assert(r1_health_u16_ram_cache_merge(
               &builder, &cache, 1000u, 1u, 2000u, 0,
               reject_health_u16_offline, NULL, &flush) == R1_ERROR_STATE);
    assert(!flush.emitted && flush.encoded_length == 20u);
    assert(builder.maximum_recorded_timestamp == 0u);
    assert(builder.history.slots[0].average == 0u);
}

static void test_scalar_health_flash_record_merge(void) {
    r1_health_u8_offline_packet builder = {0};
    health_offline_capture capture = {0};
    r1_health_u8_day_flush_result flush;
    r1_health_u8_flash_record record = {
        .utc_offset_minutes = 0,
        .recorded_timestamp = 90000u,
        .local_hour = 1u,
        .local_minute = 0u,
        .local_second = 0u,
        .average = 70u,
        .maximum = 90u,
        .minimum = 60u,
    };

    assert(r1_health_u8_flash_record_merge(
               &builder, &record, 200000u, true, 172800u,
               capture_health_u8_offline, &capture, &flush) == R1_OK);
    assert(builder.history.local_day_start == 86400u);
    assert(builder.history.slots[0].average == 70u);
    assert(builder.maximum_recorded_timestamp == 90000u);
    assert(!flush.emitted);

    /* Flash iteration is oldest-first: a later duplicate advances the ACK
     * cursor but does not replace the first populated hour. */
    record.recorded_timestamp = 90100u;
    record.local_minute = 1u;
    record.local_second = 40u;
    record.average = 80u;
    assert(r1_health_u8_flash_record_merge(
               &builder, &record, 200000u, true, 172800u,
               capture_health_u8_offline, &capture, &flush) == R1_OK);
    assert(builder.history.slots[0].average == 70u);
    assert(builder.maximum_recorded_timestamp == 90100u);

    record.recorded_timestamp = 172800u;
    record.local_hour = 0u;
    record.local_minute = 0u;
    record.local_second = 0u;
    record.average = 75u;
    record.maximum = 95u;
    record.minimum = 65u;
    assert(r1_health_u8_flash_record_merge(
               &builder, &record, 200000u, true, 172800u,
               capture_health_u8_offline, &capture, &flush) == R1_OK);
    assert(builder.history.local_day_start == 86400u);
    assert(builder.history.slots[23].average == 75u);
    assert(builder.maximum_recorded_timestamp == 172800u);

    record.recorded_timestamp = 180000u;
    record.local_hour = 2u;
    record.average = 82u;
    assert(r1_health_u8_flash_record_merge(
               &builder, &record, 250000u, false, 0u,
               capture_health_u8_offline, &capture, &flush) == R1_OK);
    assert(flush.emitted && flush.encoded_length == 15u);
    assert(capture.count == 1u && capture.lengths[0] == 15u);
    assert(builder.history.local_day_start == 172800u);
    assert(builder.history.slots[1].average == 82u);

    const r1_health_u8_offline_packet before_skip = builder;
    record.average = 0u;
    assert(r1_health_u8_flash_record_merge(
               &builder, &record, 250000u, false, 0u,
               capture_health_u8_offline, &capture, &flush) == R1_OK);
    assert(memcmp(&builder, &before_skip, sizeof builder) == 0);
    record.average = 82u;
    assert(r1_health_u8_flash_record_merge(
               &builder, &record, 179999u, false, 0u,
               capture_health_u8_offline, &capture, &flush) == R1_OK);
    assert(memcmp(&builder, &before_skip, sizeof builder) == 0);
    assert(r1_health_u8_flash_record_merge(
               &builder, &record, 250000u, true, 172800u,
               capture_health_u8_offline, &capture, &flush) == R1_OK);
    assert(memcmp(&builder, &before_skip, sizeof builder) == 0);

    record.local_minute = 60u;
    assert(r1_health_u8_flash_record_merge(
               &builder, &record, 250000u, false, 0u,
               capture_health_u8_offline, &capture, &flush) == R1_ERROR_LENGTH);
    record.local_minute = 0u;
    assert(r1_health_u8_flash_record_merge(
               NULL, &record, 250000u, false, 0u,
               capture_health_u8_offline, &capture, &flush) == R1_ERROR_ARGUMENT);

    builder.maximum_recorded_timestamp = 300000u;
    assert(r1_health_u8_day_builder_flush(
               &builder, 250000u, capture_health_u8_offline, &capture,
               &flush) == R1_OK);
    assert(flush.dropped_future_acknowledgement && !flush.emitted);
    assert(builder.maximum_recorded_timestamp == 0u);
    assert(builder.history.slots[1].average == 0u);
}

static void test_scalar_health_offline_sync(void) {
    assert(sizeof(r1_health_u8_offline_entry) == 16u);
    assert(sizeof(r1_health_u16_offline_entry) == 20u);

    r1_health_state state;
    r1_health_initialize(&state);
    assert(r1_health_u8_offline_is_empty(&state.heart_rate_offline));
    assert(r1_health_u8_offline_is_empty(&state.blood_oxygen_offline));
    assert(r1_health_u16_offline_is_empty(
        &state.heart_rate_variability_offline));

    r1_health_u8_offline_queue u8_queue;
    r1_health_u8_offline_initialize(&u8_queue);
    u8_queue.entries[0].reserved_after_aggregate = 0xa4u;
    u8_queue.entries[0].reserved_tail = 0xa5u;
    r1_health_offline_enqueue_result enqueue;
    assert(r1_health_u8_offline_enqueue(
               &u8_queue, 0u, 1u, 1u, 100u, 100u, 0, 2u, 100u,
               &enqueue) == R1_OK);
    assert(enqueue.action == R1_HEALTH_OFFLINE_DROPPED_ZERO);
    assert(r1_health_u8_offline_enqueue(
               &u8_queue, 70u, 90u, 60u, 100u, 201u, 0, 2u, 200u,
               &enqueue) == R1_OK);
    assert(enqueue.action == R1_HEALTH_OFFLINE_DROPPED_FUTURE_RECORDED);
    assert(r1_health_u8_offline_enqueue(
               &u8_queue, 70u, 90u, 60u, 201u, 200u, 0, 2u, 200u,
               &enqueue) == R1_OK);
    assert(enqueue.action == R1_HEALTH_OFFLINE_DROPPED_FUTURE_DAY);
    assert(r1_health_u8_offline_enqueue(
               &u8_queue, 70u, 90u, 60u, 100u, 101u, -300, 2u, 1000u,
               &enqueue) == R1_OK);
    assert(u8_queue.entries[0].reserved_after_aggregate == 0xa4u);
    assert(u8_queue.entries[0].reserved_tail == 0xa5u);
    assert(r1_health_u8_offline_enqueue(
               &u8_queue, 80u, 95u, 65u, 100u, 102u, -300, 2u, 1000u,
               &enqueue) == R1_OK);
    assert(r1_health_u8_offline_enqueue(
               &u8_queue, 88u, 99u, 77u, 300u, 999u, 0, 4u, 1000u,
               &enqueue) == R1_OK);

    health_offline_capture capture = {0};
    r1_health_u8_offline_packet u8_workspace;
    r1_health_offline_merge_result merge;
    assert(r1_health_u8_offline_merge(
               &u8_queue, 250u, &u8_workspace, capture_health_u8_offline,
               &capture, &merge) == R1_OK);
    assert(merge.packet_count == 1u && merge.skipped_zero_count == 0u);
    assert(merge.skipped_future_count == 1u && capture.count == 1u);
    assert(capture.maximum_timestamps[0] == 102u);
    static const uint8_t expected_u8[] = {
        1u, 0xd4u, 0xfeu, 100u, 0u, 0u, 0u, 2u, 80u, 95u, 65u,
    };
    assert(capture.lengths[0] == sizeof expected_u8);
    assert(memcmp(capture.payloads[0], expected_u8, sizeof expected_u8) == 0);

    r1_health_offline_ack_result ack;
    uint32_t last_sync = 40u;
    assert(r1_health_u8_offline_acknowledge(
               &u8_queue, R1_HEALTH_ACK_OFFLINE_QUEUE, 101u, 50u,
               &last_sync, &ack) == R1_OK);
    assert(ack.firmware_clock_sampled && ack.timestamp_was_future);
    assert(ack.consumed_count == 1u && u8_queue.count == 2u);
    assert(r1_health_u8_offline_acknowledge(
               &u8_queue, R1_HEALTH_ACK_CURRENT_RAM, 200u, 250u,
               &last_sync, &ack) == R1_OK);
    assert(ack.last_sync_updated && last_sync == 200u);
    assert(r1_health_u8_offline_acknowledge(
               &u8_queue, R1_HEALTH_ACK_FLASH_HISTORY, 300u, 250u,
               &last_sync, &ack) == R1_OK);
    assert(ack.timestamp_was_future && !ack.last_sync_updated);

    r1_health_u8_offline_initialize(&u8_queue);
    for (uint8_t value = 1u; value <= 25u; ++value) {
        assert(r1_health_u8_offline_enqueue(
                   &u8_queue, value, value, value, 0u, value, 0,
                   (uint8_t)(value % R1_HEALTH_HOURLY_SLOTS), value,
                   &enqueue) == R1_OK);
        assert(enqueue.overwrote_oldest == (value == 25u));
    }
    assert(u8_queue.count == R1_HEALTH_OFFLINE_CAPACITY);
    assert(u8_queue.read_index == 1u && u8_queue.write_index == 1u);
    u8_queue.entries[u8_queue.read_index].hour_index = R1_HEALTH_HOURLY_SLOTS;
    size_t consumed = 0u;
    assert(r1_health_u8_offline_consume_through(&u8_queue, 100u, &consumed)
           == R1_ERROR_STATE);

    r1_health_u16_offline_queue u16_queue;
    r1_health_u16_offline_initialize(&u16_queue);
    u16_queue.entries[0].reserved_after_aggregate[0] = 0xb1u;
    u16_queue.entries[0].reserved_after_aggregate[1] = 0xb2u;
    u16_queue.entries[0].reserved_tail = 0xb3u;
    assert(r1_health_u16_offline_enqueue(
               &u16_queue, 0x1234u, 0x4567u, 0x1111u, 100u, 101u,
               60, 4u, 1000u, &enqueue) == R1_OK);
    assert(u16_queue.entries[0].reserved_after_aggregate[0] == 0xb1u);
    assert(u16_queue.entries[0].reserved_after_aggregate[1] == 0xb2u);
    assert(u16_queue.entries[0].reserved_tail == 0xb3u);
    assert(r1_health_u16_offline_enqueue(
               &u16_queue, 0x2222u, 0x3333u, 0x1111u, 100u, 102u,
               60, 4u, 1000u, &enqueue) == R1_OK);
    capture = (health_offline_capture){0};
    r1_health_u16_offline_packet u16_workspace;
    assert(r1_health_u16_offline_merge(
               &u16_queue, 250u, &u16_workspace, capture_health_u16_offline,
               &capture, &merge) == R1_OK);
    static const uint8_t expected_u16[] = {
        1u, 60u, 0u, 100u, 0u, 0u, 0u,
        4u, 0x22u, 0x22u, 0x33u, 0x33u, 0x11u, 0x11u,
    };
    assert(capture.count == 1u && capture.maximum_timestamps[0] == 102u);
    assert(capture.lengths[0] == sizeof expected_u16);
    assert(memcmp(capture.payloads[0], expected_u16, sizeof expected_u16) == 0);
    last_sync = 40u;
    assert(r1_health_u16_offline_acknowledge(
               &u16_queue, R1_HEALTH_ACK_OFFLINE_QUEUE, 101u, 50u,
               &last_sync, &ack) == R1_OK);
    assert(!ack.firmware_clock_sampled && !ack.timestamp_was_future);
    assert(ack.consumed_count == 1u && last_sync == 40u);
    assert(r1_health_u16_offline_acknowledge(
               &u16_queue, R1_HEALTH_ACK_CURRENT_RAM, 200u, 250u,
               &last_sync, &ack) == R1_OK);
    assert(ack.firmware_clock_sampled && ack.last_sync_updated && last_sync == 200u);
}

static void test_sleep_history_and_dispatch(void) {
    r1_device_state state;
    r1_state_initialize(&state);
    r1_sleep_session sleep = {0};
    sleep.type = 1u;
    sleep.efficiency = 92u;
    sleep.score = 84u;
    sleep.wake_ratio = 10u;
    sleep.rem_ratio = 20u;
    sleep.light_ratio = 50u;
    sleep.deep_ratio = 20u;
    sleep.body_temperature_raw = 365u;
    sleep.utc_offset_minutes = -300;
    sleep.start_timestamp = UINT32_C(1700000000);
    sleep.end_timestamp = UINT32_C(1700028800);
    sleep.total_minutes = 480u;
    sleep.wake_minutes = 48u;
    sleep.rem_minutes = 96u;
    sleep.light_minutes = 240u;
    sleep.deep_minutes = 96u;
    sleep.stage_count = 2u;
    sleep.stages[0].type = 2u;
    sleep.stages[0].half_minutes = 300u;
    sleep.stages[1].type = 3u;
    sleep.stages[1].half_minutes = 120u;
    assert(r1_sleep_store(&state.health.sleep, &sleep) == R1_OK);

    uint8_t payload[R1_SLEEP_PAYLOAD_MAX_BYTES];
    size_t written = 0u;
    assert(r1_sleep_encode(&state.health.sleep.sessions[0],
                           payload, sizeof payload, &written) == R1_OK);
    assert(written == 38u);
    assert(payload[0] == 1u && payload[1] == 92u && payload[2] == 84u);
    assert(payload[4] == 10u && payload[5] == 20u &&
           payload[6] == 50u && payload[7] == 20u);
    assert(payload[32] == 2u && payload[33] == 0x2cu && payload[34] == 0x01u);
    assert(payload[35] == 3u && payload[36] == 120u && payload[37] == 0u);

    r1_session peer = {true, true, true, R1_ROLE_PHONE};
    const r1_model query = {100u, 2u, 100u, 9u, 0u, 6u, 1u, NULL, 0u};
    r1_dispatch_result result;
    assert(r1_dispatch(&state, &peer, &query, &result) == R1_OK);
    assert(result.count == 2u);
    r1_model decoded;
    assert(r1_model_decode(result.models[1], result.lengths[1],
                           R1_CHECKSUM_FIRMWARE_FULL_MODBUS, &decoded) == R1_OK);
    assert(decoded.status == 2u && decoded.payload_length == 38u);
    for (size_t index = 0u; index < written; ++index) {
        assert(decoded.payload[index] == payload[index]);
    }
    assert(!state.health.sleep.sessions[0].synchronized);
    static const uint8_t ack_payload[] = {2u, 6u, 1u, 0u, 1u, 0u};
    const r1_model ack = {100u, 1u, 100u, 10u, 1u, 0u, 0x7eu,
                          ack_payload, sizeof ack_payload};
    assert(r1_dispatch(&state, &peer, &ack, &result) == R1_OK);
    assert(result.count == 0u);
    assert(state.health.sleep.sessions[0].synchronized);

    assert(r1_dispatch(&state, &peer, &query, &result) == R1_OK);
    assert(result.count == 1u);
}

static void test_maximum_health_payloads(void) {
    r1_device_state state;
    r1_state_initialize(&state);
    for (size_t index = 0u; index < R1_ACTIVITY_BUCKETS; ++index) {
        assert(r1_activity_record(&state.health.activity, (uint8_t)index,
                                  (uint16_t)(index + 1u), 2u, 3u,
                                  (uint32_t)(1000u + index), 1000u, 0) == R1_OK);
    }
    r1_session peer = {true, true, true, R1_ROLE_PHONE};
    const r1_model activity_query = {100u, 2u, 100u, 20u, 0u, 5u, 1u, NULL, 0u};
    r1_dispatch_result result;
    assert(r1_dispatch(&state, &peer, &activity_query, &result) == R1_OK);
    assert(result.count == 2u);
    assert(result.lengths[1] == R1_MODEL_HEADER_LENGTH + R1_ACTIVITY_DAILY_MAX_BYTES);
    r1_fragment_set fragments;
    assert(r1_fragment_message(result.models[1], result.lengths[1], &fragments) == R1_OK);
    assert(fragments.count == 5u);

    r1_sleep_session session = {0};
    session.type = 2u;
    session.start_timestamp = 10u;
    session.end_timestamp = 20u;
    session.stage_count = 1u;
    session.stages[0].type = 2u;
    session.stages[0].half_minutes = 1u;
    for (size_t index = 0u; index < R1_SLEEP_SESSION_MAX; ++index) {
        session.start_timestamp += 10u;
        session.end_timestamp += 10u;
        assert(r1_sleep_store(&state.health.sleep, &session) == R1_OK);
    }
    const r1_model sleep_query = {100u, 2u, 100u, 21u, 0u, 6u, 1u, NULL, 0u};
    assert(r1_dispatch(&state, &peer, &sleep_query, &result) == R1_OK);
    assert(result.count == R1_DISPATCH_RESPONSE_MAX);
    r1_health_clear_pending(&state.health);
    for (size_t index = 0u; index < R1_PENDING_ACK_CAPACITY; ++index) {
        assert(!state.health.pending[index].active);
    }
}

static uint32_t float_bits(float value) {
    union {
        float floating;
        uint32_t bits;
    } representation;
    representation.floating = value;
    return representation.bits;
}

static void test_hrv_rmssd(void) {
    r1_hrv_rmssd_result result;
    static const uint16_t one[] = {800u};
    assert(r1_hrv_calculate_rmssd(one, 1u, false, &result) == R1_OK);
    assert(!result.has_result && float_bits(result.rmssd) == UINT32_C(0xbf800000));

    static const uint16_t simple[] = {800u, 810u, 790u, 820u};
    assert(r1_hrv_calculate_rmssd(simple, 4u, false, &result) == R1_OK);
    assert(result.has_result && result.difference_count == 3u);
    assert(result.differences[0] == 10u && result.differences[1] == 20u &&
           result.differences[2] == 30u);
    assert(float_bits(result.rmssd) == UINT32_C(0x41acd1db));

    static const uint16_t boundary[] = {800u, 950u, 800u};
    assert(r1_hrv_calculate_rmssd(boundary, 3u, false, &result) == R1_OK);
    assert(float_bits(result.rmssd) == UINT32_C(0x43160000));
    static const uint16_t rejected[] = {800u, 951u, 800u};
    assert(r1_hrv_calculate_rmssd(rejected, 3u, false, &result) == R1_OK);
    assert(!result.has_result && result.validity[0] == 0u &&
           result.validity[1] == 0u && result.validity[2] == 0u);

    static const uint16_t first_quirk[] = {1101u, 1100u, 1099u};
    assert(r1_hrv_calculate_rmssd(first_quirk, 3u, false, &result) == R1_OK);
    assert(float_bits(result.rmssd) == UINT32_C(0x3f800000));
    static const uint16_t alternate[] = {1400u, 1500u, 1400u};
    assert(r1_hrv_calculate_rmssd(alternate, 3u, true, &result) == R1_OK);
    assert(float_bits(result.rmssd) == UINT32_C(0x42c80000));

    const r1_hrv_publication published = r1_hrv_publish(result.rmssd, true,
                                                        UINT32_C(0x12345678));
    assert(published.published && published.transmitted == 100u);
    static const uint8_t expected[] = {100u, 0u, 0u, 0u, 0x78u, 0x56u, 0x34u, 0x12u};
    for (size_t index = 0u; index < sizeof expected; ++index) {
        assert(published.payload[index] == expected[index]);
    }
    assert(!r1_hrv_publish(0.0f, true, 0u).published);
    assert(!r1_hrv_publish(-1.0f, true, 0u).published);
}

static void test_hrv_producer(void) {
    r1_hrv_producer producer;
    r1_hrv_producer_initialize(&producer);
    r1_hrv_producer_session session = {true, true, 0u};
    r1_hrv_producer_result result;
    static const uint16_t warmup[] = {800u, 810u};
    assert(r1_hrv_producer_ingest(&producer, &session, warmup, 2u, false, true,
                                  1u, &result) == R1_OK);
    assert(result.action == R1_HRV_WARMUP_IGNORED);
    assert(producer.buffered_count == 0u && producer.callback_count == 1u);

    producer.callback_count = 59u;
    producer.buffered_count = 70u;
    producer.nonzero_count = 70u;
    for (size_t index = 0u; index < 70u; ++index) {
        producer.physical_buffer[index] = (index & 1u) == 0u ? 800u : 810u;
    }
    assert(r1_hrv_producer_ingest(&producer, &session, NULL, 0u, false, true,
                                  UINT32_C(0x12345678), &result) == R1_OK);
    assert(result.action == R1_HRV_PUBLISHED_RESET);
    assert(result.eligibility_checked && result.publication.published);
    assert(result.publication.transmitted == 10u);
    assert(producer.callback_count == 0u && producer.buffered_count == 0u);
    assert(!session.subscription_active && !session.timed_window_active);
    assert(session.timed_window_completed == 1u);

    r1_hrv_producer_initialize(&producer);
    producer.callback_count = 59u;
    producer.buffered_count = 70u;
    producer.nonzero_count = 70u;
    for (size_t index = 0u; index < 70u; ++index) {
        producer.physical_buffer[index] = 800u;
    }
    session.subscription_active = true;
    session.timed_window_active = true;
    session.timed_window_completed = 0u;
    assert(r1_hrv_producer_ingest(&producer, &session, NULL, 0u, false, true,
                                  2u, &result) == R1_OK);
    assert(result.action == R1_HRV_FAILED_TIMED_RETRY);
    assert(session.subscription_active && session.timed_window_active);
}

static void test_hrv_timing_start_policy(void) {
    r1_hrv_timing_observation observation = {
        .mode = 1u,
        .health_enabled = true,
        .timing_allowed = true,
        .hourly_request = false,
    };
    r1_hrv_timing_plan plan;
    for (uint32_t phase = 0u; phase < UINT32_C(3600); ++phase) {
        observation.current_timestamp = phase;
        assert(r1_hrv_plan_timing_start(&observation, &plan) == R1_OK);
        if (phase >= UINT32_C(3450)) {
            assert(plan.action == R1_HRV_TIMING_CATCHUP_TOO_CLOSE_TO_HOUR);
            assert(!plan.create_one_shot_timeout);
        } else {
            assert(plan.action == R1_HRV_TIMING_START);
            assert(plan.delay_seconds == 120u);
            assert(plan.timeout_milliseconds == 120000u);
            assert(plan.workspace_clear_bytes == 208u);
            assert(plan.create_one_shot_timeout);
            assert(plan.register_sensor_stream_after_timeout_create);
            assert(plan.delete_timeout_on_registration_failure);
        }
    }
    observation.hourly_request = true;
    observation.current_timestamp = 3599u;
    assert(r1_hrv_plan_timing_start(&observation, &plan) == R1_OK);
    assert(plan.action == R1_HRV_TIMING_START && plan.delay_seconds == 120u);

    observation.mode = 0u;
    assert(r1_hrv_plan_timing_start(&observation, &plan) == R1_OK);
    assert(plan.action == R1_HRV_TIMING_INACTIVE);
    observation.mode = 1u;
    observation.transition_pending = true;
    assert(r1_hrv_plan_timing_start(&observation, &plan) == R1_OK);
    assert(plan.action == R1_HRV_TIMING_TRANSITION_PENDING);
    observation.transition_pending = false;
    observation.health_enabled = false;
    assert(r1_hrv_plan_timing_start(&observation, &plan) == R1_OK);
    assert(plan.action == R1_HRV_TIMING_HEALTH_DISABLED);
    observation.health_enabled = true;
    observation.timing_allowed = false;
    assert(r1_hrv_plan_timing_start(&observation, &plan) == R1_OK);
    assert(plan.action == R1_HRV_TIMING_NOT_ALLOWED);
    observation.timing_allowed = true;
    observation.timeout_exists = true;
    assert(r1_hrv_plan_timing_start(&observation, &plan) == R1_OK);
    assert(plan.action == R1_HRV_TIMING_ALREADY_ACTIVE);
    assert(r1_hrv_plan_timing_start(NULL, &plan) == R1_ERROR_ARGUMENT);
}

static void test_event_plane(void) {
    r1_event_plane plane;
    r1_event_plane_initialize(&plane);
    r1_tx_event event = {
        .connection = 7u,
        .channel = 1u,
        .bytes = {0u},
        .length = 1u,
        .resource_retries = 0u,
    };
    for (size_t index = 0u; index < R1_NORMAL_QUEUE_CAPACITY; ++index) {
        assert(r1_event_enqueue(&plane, false, &event) == R1_OK);
    }
    assert(r1_event_enqueue(&plane, false, &event) == R1_ERROR_CAPACITY);
    for (size_t index = 0u; index < R1_HVN_CREDIT_MAX; ++index) {
        assert(r1_event_consume_credit(&plane));
    }
    assert(!r1_event_consume_credit(&plane));
    r1_event_complete(&plane, 2u);
    assert(plane.hvn_credits == 2u);
    r1_event_disconnect(&plane);
    assert(plane.normal.count == 0u && plane.eus.count == 0u);
    assert(plane.hvn_credits == R1_HVN_CREDIT_MAX);
}

static void test_delayed_event_timer_step(void) {
    r1_delayed_event_state state = {0};
    state.last_timer_delay_milliseconds = 30u;
    state.slots[0] = (r1_delayed_event_slot){1u, 0x1111u, 100u};
    state.slots[1] = (r1_delayed_event_slot){2u, 0x2222u, 50u};
    state.slots[2] = (r1_delayed_event_slot){0u, 0x3333u, 20u};
    r1_delayed_event_step_result result;

    assert(r1_delayed_event_timer_step(&state, 0u, 1024u, &result) == R1_OK);
    assert(!result.elapsed_override_used && result.elapsed_milliseconds == 30u);
    assert(result.due_count == 0u && result.timer_start_requested);
    assert(result.next_delay_milliseconds == 20u);
    assert(state.slots[0].remaining_milliseconds == 70u);
    assert(state.slots[1].remaining_milliseconds == 20u);
    assert(state.last_timer_delay_milliseconds == 20u);
    assert(state.last_timer_start_milliseconds == 1000u);

    assert(r1_delayed_event_timer_step(&state, 0u, 2048u, &result) == R1_OK);
    assert(result.due_count == 1u);
    assert(result.due[0].event == 2u && result.due[0].context == 0x2222u);
    assert(state.slots[1].event == 0u && state.slots[1].context == 0x2222u);
    assert(result.next_delay_milliseconds == 50u);
    assert(state.last_timer_start_milliseconds == 2000u);

    state.slots[3] = (r1_delayed_event_slot){3u, 0x3333u, 10u};
    assert(r1_delayed_event_timer_step(
               &state, R1_DELAYED_EVENT_ELAPSED_TAG | 96u,
               3072u, &result) == R1_OK);
    assert(result.elapsed_override_used && result.elapsed_milliseconds == 96u);
    assert(result.due_count == 2u);
    assert(result.due[0].event == 1u && result.due[1].event == 3u);
    assert(result.stock_empty_reload_quirk);
    assert(result.timer_start_requested);
    assert(result.next_delay_milliseconds == UINT32_MAX);
    assert(state.last_timer_delay_milliseconds == UINT32_MAX);
    assert(state.last_timer_start_milliseconds == 3000u);

    state = (r1_delayed_event_state){0};
    state.last_timer_delay_milliseconds = 7u;
    state.slots[0] =
        (r1_delayed_event_slot){4u, 0x4444u, (uint32_t)INT32_MAX + 7u};
    assert(r1_delayed_event_timer_step(&state, 0u, 4096u, &result) == R1_OK);
    assert(result.next_delay_milliseconds == (uint32_t)INT32_MAX);
    assert(result.stock_int32_max_suppression_quirk);
    assert(!result.timer_start_requested);

    assert(r1_delayed_event_timer_step(NULL, 0u, 0u, &result)
           == R1_ERROR_ARGUMENT);
    assert(r1_delayed_event_timer_step(&state, 0u, 0u, NULL)
           == R1_ERROR_ARGUMENT);
}

typedef struct {
    r1_tx_status next_status;
    r1_tx_event captured;
    size_t calls;
} runtime_tx_capture;

typedef struct {
    size_t calls;
    bool shared_queue;
    uint32_t wait_ticks;
    r1_tx_event captured;
} runtime_enqueue_capture;

static r1_tx_status capture_runtime_tx(void *context, const r1_tx_event *event) {
    runtime_tx_capture *capture = context;
    capture->captured = *event;
    capture->calls += 1u;
    return capture->next_status;
}

static r1_error capture_runtime_enqueue(void *context, bool shared_queue,
                                        const r1_tx_event *event,
                                        uint32_t wait_ticks) {
    runtime_enqueue_capture *capture = context;
    capture->calls += 1u;
    capture->shared_queue = shared_queue;
    capture->wait_ticks = wait_ticks;
    capture->captured = *event;
    return R1_OK;
}

typedef struct {
    size_t calls;
    uint16_t connection;
    r1_peer_role role;
    r1_error result;
} runtime_role_capture;

static r1_error capture_runtime_role(void *context, uint16_t connection,
                                     r1_peer_role role) {
    runtime_role_capture *capture = context;
    capture->calls += 1u;
    capture->connection = connection;
    capture->role = role;
    return capture->result;
}

typedef struct {
    size_t calls;
    bool enabled;
} runtime_touch_capture;

static void capture_runtime_touch(void *context, bool enabled) {
    runtime_touch_capture *capture = context;
    capture->calls += 1u;
    capture->enabled = enabled;
}

static r1_error runtime_feed_model(r1_runtime *runtime, uint16_t connection,
                                   const r1_model *model) {
    uint8_t logical[64u];
    size_t logical_length = 0u;
    assert(r1_model_encode(model, R1_CHECKSUM_PHONE_COMPACT_CCITT,
                           logical, sizeof logical, &logical_length) == R1_OK);
    r1_fragment_set fragments;
    assert(r1_fragment_message(logical, logical_length, &fragments) == R1_OK);
    assert(fragments.count == 1u);
    return r1_runtime_receive_eus(runtime, connection,
                                  fragments.fragments[0].bytes,
                                  fragments.fragments[0].length);
}

static void test_runtime_roles(void) {
    r1_runtime runtime;
    r1_runtime_initialize(&runtime, NULL, NULL);
    runtime_role_capture capture = {.result = R1_OK};
    r1_runtime_set_role_handler(&runtime, capture_runtime_role, &capture);
    assert(r1_runtime_connect(&runtime, 1u) == R1_OK);
    assert(r1_runtime_connect(&runtime, 2u) == R1_OK);

    static const uint8_t phone[] = {1u};
    const r1_model pair = {
        R1_PROTOCOL_VERSION, 1u, R1_MODULE_VERSION, 9u,
        0u, 0u, 0x08u, phone, sizeof phone,
    };
    assert(runtime_feed_model(&runtime, 1u, &pair) == R1_OK);
    assert(capture.calls == 1u && capture.connection == 1u &&
           capture.role == R1_ROLE_PHONE);
    assert(runtime.links[0].session.role == R1_ROLE_PHONE);

    assert(runtime_feed_model(&runtime, 2u, &pair) == R1_ERROR_STATE);
    assert(capture.calls == 1u);
    assert(runtime.links[1].session.role == R1_ROLE_UNASSIGNED);

    r1_runtime_disconnect(&runtime, 1u);
    capture.result = R1_ERROR_STATE;
    assert(runtime_feed_model(&runtime, 2u, &pair) == R1_ERROR_STATE);
    assert(capture.calls == 2u);
    assert(runtime.links[1].session.role == R1_ROLE_UNASSIGNED);
}

static void test_runtime_role_occupancy(void) {
    r1_runtime runtime;
    r1_runtime_initialize(&runtime, NULL, NULL);
    bool phone = true;
    bool glasses = true;
    r1_runtime_role_occupancy(NULL, &phone, &glasses);
    assert(!phone && !glasses);
    r1_runtime_role_occupancy(&runtime, &phone, &glasses);
    assert(!phone && !glasses);
    assert(r1_runtime_connect(&runtime, 1u) == R1_OK);
    assert(r1_runtime_connect(&runtime, 2u) == R1_OK);
    /* Connected but unassigned links occupy no role. */
    r1_runtime_role_occupancy(&runtime, &phone, &glasses);
    assert(!phone && !glasses);

    static const uint8_t phone_selector[] = {1u};
    const r1_model pair = {
        R1_PROTOCOL_VERSION, 1u, R1_MODULE_VERSION, 9u,
        0u, 0u, 0x08u, phone_selector, sizeof phone_selector,
    };
    assert(runtime_feed_model(&runtime, 1u, &pair) == R1_OK);
    r1_runtime_role_occupancy(&runtime, &phone, &glasses);
    assert(phone && !glasses);

    runtime.links[1].session.role = R1_ROLE_GLASSES;
    r1_runtime_role_occupancy(&runtime, &phone, &glasses);
    assert(phone && glasses);

    r1_runtime_disconnect(&runtime, 1u);
    r1_runtime_role_occupancy(&runtime, &phone, &glasses);
    assert(!phone && glasses);

    r1_runtime_role_occupancy(&runtime, NULL, NULL);
}

static void test_runtime_touch_effect(void) {
    r1_runtime runtime;
    r1_runtime_initialize(&runtime, NULL, NULL);
    runtime_touch_capture capture = {0};
    r1_runtime_set_touch_handler(&runtime, capture_runtime_touch, &capture);
    assert(r1_runtime_connect(&runtime, 3u) == R1_OK);
    assert(r1_runtime_set_security(&runtime, 3u, true, true, true) == R1_OK);
    static const uint8_t disabled[] = {0u};
    const r1_model set_disabled = request(2u, 0x07u, disabled, sizeof disabled);
    assert(runtime_feed_model(&runtime, 3u, &set_disabled) == R1_OK);
    assert(capture.calls == 1u && !capture.enabled);
    assert(runtime_feed_model(&runtime, 3u, &set_disabled) == R1_OK);
    assert(capture.calls == 1u);
    static const uint8_t enabled[] = {1u};
    const r1_model set_enabled = request(2u, 0x07u, enabled, sizeof enabled);
    assert(runtime_feed_model(&runtime, 3u, &set_enabled) == R1_OK);
    assert(capture.calls == 2u && capture.enabled);
}

static void test_runtime_eus_bridge(void) {
    runtime_tx_capture capture = {.next_status = R1_TX_RESOURCES};
    r1_runtime runtime;
    r1_runtime_initialize(&runtime, capture_runtime_tx, &capture);
    assert(r1_runtime_connect(&runtime, UINT16_C(0x0042)) == R1_OK);
    assert(r1_runtime_connect(&runtime, UINT16_C(0x0042)) == R1_OK);
    assert(r1_runtime_set_security(&runtime, UINT16_C(0x0042), true, false, true)
           == R1_ERROR_ARGUMENT);

    const r1_model query = {
        R1_PROTOCOL_VERSION, 1u, R1_MODULE_VERSION, UINT16_C(0x1234),
        0u, 0u, 1u, NULL, 0u,
    };
    runtime_enqueue_capture enqueue_capture = {0};
    r1_runtime provider_runtime;
    r1_runtime_initialize(&provider_runtime, NULL, NULL);
    r1_runtime_set_enqueue(
        &provider_runtime, capture_runtime_enqueue, &enqueue_capture);
    assert(r1_runtime_connect(&provider_runtime, UINT16_C(0x0043)) == R1_OK);
    assert(runtime_feed_model(&provider_runtime, UINT16_C(0x0043), &query) == R1_OK);
    assert(enqueue_capture.calls == 1u && enqueue_capture.shared_queue);
    assert(enqueue_capture.wait_ticks == R1_TX_ENQUEUE_WAIT_TICKS);
    assert(enqueue_capture.captured.channel == 2u);
    assert(provider_runtime.events.eus.count == 0u);

    uint8_t logical[32u];
    size_t logical_length = 0u;
    assert(r1_model_encode(&query, R1_CHECKSUM_PHONE_COMPACT_CCITT,
                           logical, sizeof logical, &logical_length) == R1_OK);
    r1_fragment_set inbound;
    assert(r1_fragment_message(logical, logical_length, &inbound) == R1_OK);
    assert(inbound.count == 1u);
    assert(r1_runtime_receive_eus(&runtime, UINT16_C(0x0042),
                                  inbound.fragments[0].bytes,
                                  inbound.fragments[0].length) == R1_OK);
    assert(runtime.events.eus.count == 1u);

    assert(r1_runtime_poll(&runtime, 0u) == R1_EUS_RESOURCE_RETRY_TICKS);
    assert(capture.calls == 1u);
    assert(runtime.events.eus.count == 1u);
    assert(runtime.events.hvn_credits == R1_HVN_CREDIT_MAX);
    capture.next_status = R1_TX_SENT;
    assert(r1_runtime_poll(&runtime, R1_EUS_RESOURCE_RETRY_TICKS - 1u) == 1u);
    assert(capture.calls == 1u);
    assert(r1_runtime_poll(&runtime, R1_EUS_RESOURCE_RETRY_TICKS) ==
           R1_RUNTIME_WAIT_FOREVER);
    assert(capture.calls == 2u);
    assert(runtime.events.eus.count == 0u);
    assert(runtime.events.hvn_credits == R1_HVN_CREDIT_MAX - 1u);
    assert(capture.captured.connection == UINT16_C(0x0042));
    assert(capture.captured.channel == 2u);

    r1_reassembler outbound;
    r1_reassembler_reset(&outbound);
    assert(r1_reassembler_feed(&outbound, capture.captured.bytes,
                               capture.captured.length, NULL)
           == R1_REASSEMBLY_COMPLETE);
    r1_model response;
    assert(r1_model_decode(outbound.bytes, outbound.length,
                           R1_CHECKSUM_FIRMWARE_FULL_MODBUS, &response) == R1_OK);
    assert(response.serial == UINT16_C(0x1234));
    assert(response.payload_length == 7u);
    r1_runtime_hvn_complete(&runtime, 1u);
    assert(runtime.events.hvn_credits == R1_HVN_CREDIT_MAX);

    for (size_t index = 0u; index < R1_HVN_CREDIT_MAX; ++index) {
        assert(r1_event_consume_credit(&runtime.events));
    }
    assert(r1_runtime_receive_eus(&runtime, UINT16_C(0x0042),
                                  inbound.fragments[0].bytes,
                                  inbound.fragments[0].length) == R1_OK);
    assert(r1_runtime_poll(&runtime, 2000u) == R1_EUS_CREDIT_WAIT_TICKS);
    assert(capture.calls == 2u && runtime.events.eus.count == 1u);
    assert(r1_runtime_poll(&runtime, 2199u) == 1u);
    r1_runtime_hvn_complete(&runtime, 1u);
    assert(r1_runtime_poll(&runtime, 2199u) == R1_RUNTIME_WAIT_FOREVER);
    assert(capture.calls == 3u && runtime.events.eus.count == 0u);
    assert(runtime.events.hvn_credits == 0u);

    assert(r1_runtime_receive_eus(&runtime, UINT16_C(0x0042),
                                  inbound.fragments[0].bytes,
                                  inbound.fragments[0].length) == R1_OK);
    assert(r1_runtime_poll(&runtime, 3000u) == R1_EUS_CREDIT_WAIT_TICKS);
    assert(r1_runtime_poll(&runtime, 3200u) == R1_RUNTIME_WAIT_FOREVER);
    assert(capture.calls == 3u && runtime.events.eus.count == 0u);

    r1_runtime_hvn_complete(&runtime, R1_HVN_CREDIT_MAX);
    assert(r1_runtime_receive_eus(&runtime, UINT16_C(0x0042),
                                  inbound.fragments[0].bytes,
                                  inbound.fragments[0].length) == R1_OK);
    capture.next_status = R1_TX_RESOURCES;
    assert(r1_runtime_poll(&runtime, 4000u) == R1_EUS_RESOURCE_RETRY_TICKS);
    assert(capture.calls == 4u && runtime.events.eus.count == 1u);
    assert(r1_runtime_poll(&runtime, 4999u) == 1u);
    assert(capture.calls == 4u);
    assert(r1_runtime_poll(&runtime, 5000u) == R1_RUNTIME_WAIT_FOREVER);
    assert(capture.calls == 5u && runtime.events.eus.count == 0u);
    assert(runtime.events.hvn_credits == R1_HVN_CREDIT_MAX);

    for (size_t index = 0u; index < R1_HVN_CREDIT_MAX; ++index) {
        assert(r1_event_consume_credit(&runtime.events));
    }
    assert(r1_runtime_receive_eus(&runtime, UINT16_C(0x0042),
                                  inbound.fragments[0].bytes,
                                  inbound.fragments[0].length) == R1_OK);
    assert(r1_runtime_poll(&runtime, UINT32_MAX - 50u) ==
           R1_EUS_CREDIT_WAIT_TICKS);
    assert(r1_runtime_poll(&runtime, 148u) == 1u);
    assert(r1_runtime_poll(&runtime, 149u) == R1_RUNTIME_WAIT_FOREVER);
    assert(capture.calls == 5u && runtime.events.eus.count == 0u);
    r1_runtime_hvn_complete(&runtime, R1_HVN_CREDIT_MAX);

    assert(r1_runtime_receive_eus(&runtime, UINT16_C(0x0042),
                                  inbound.fragments[0].bytes,
                                  inbound.fragments[0].length) == R1_OK);
    assert(runtime.events.eus.count == 1u);
    r1_runtime_disconnect(&runtime, UINT16_C(0x0042));
    assert(runtime.events.eus.count == 0u);
    assert(r1_runtime_receive_eus(&runtime, UINT16_C(0x0042),
                                  inbound.fragments[0].bytes,
                                  inbound.fragments[0].length) == R1_ERROR_STATE);
}

static void test_bae8_event_route(void) {
    r1_bae8_event_plan plan = r1_runtime_plan_bae8_event(2u);
    assert(plan.route == R1_BAE8_EVENT_BC_RX);
    assert(!plan.assign_glasses_role && !plan.requires_link_context);
    plan = r1_runtime_plan_bae8_event(3u);
    assert(plan.route == R1_BAE8_EVENT_EUS_RX);
    assert(!plan.assign_glasses_role && !plan.requires_link_context);
    for (uint8_t event = 6u; event <= 7u; ++event) {
        plan = r1_runtime_plan_bae8_event(event);
        assert(plan.route == R1_BAE8_EVENT_LINK_GROUP_A);
        assert(plan.assign_glasses_role && plan.requires_link_context);
    }
    for (uint8_t event = 8u; event <= 9u; ++event) {
        plan = r1_runtime_plan_bae8_event(event);
        assert(plan.route == R1_BAE8_EVENT_LINK_GROUP_B);
        assert(!plan.assign_glasses_role && plan.requires_link_context);
    }
    plan = r1_runtime_plan_bae8_event(0u);
    assert(plan.route == R1_BAE8_EVENT_IGNORE);
    plan = r1_runtime_plan_bae8_event(UINT8_MAX);
    assert(plan.route == R1_BAE8_EVENT_IGNORE);
}

static void test_storage(void) {
    const r1_partition *log = r1_storage_partition("log.bin");
    assert(log != NULL);
    assert(log->offset == UINT32_C(0x18000));
    assert(log->length == UINT32_C(0x0c000));
    for (size_t index = 1u; index < R1_STORAGE_PARTITION_COUNT; ++index) {
        const r1_partition *previous = &r1_storage_partitions[index - 1u];
        const r1_partition *current = &r1_storage_partitions[index];
        assert(previous->offset + previous->length == current->offset);
    }
}

static void test_export_planner(void) {
    r1_export_state state = {0};
    r1_export_plan plan;
    r1_export_observation observation = {
        .command = 0u,
        .result = 1u,
        .metadata_available = true,
        .total_bytes = 9000u,
        .checksum = UINT32_C(0x12345678),
    };
    assert(r1_export_plan_command(&state, &observation, &plan) == R1_OK);
    assert(plan.control_length == R1_EXPORT_CONTROL_BYTES);
    assert(plan.control[0] == 0u && plan.control[1] == 0u);
    static const uint8_t expected_info[] = {
        0x28u, 0x23u, 0u, 0u, 0x78u, 0x56u, 0x34u, 0x12u,
    };
    assert(memcmp(plan.control + 2u, expected_info, sizeof expected_info) == 0);
    assert(plan.start_provider && plan.reset_offset && plan.send_data_marker);
    assert(plan.delay_before_data_ms == R1_EXPORT_INTERFRAME_DELAY_MS);
    assert(plan.read_offset == 0u && plan.read_length == 4096u);
    assert(state.active && state.offset == 4096u && state.total_bytes == 9000u);

    observation = (r1_export_observation){.command = 1u, .result = 0u};
    assert(r1_export_plan_command(&state, &observation, &plan) == R1_OK);
    assert(plan.send_data_marker && plan.read_offset == 4096u);
    assert(plan.read_length == 4096u && state.offset == 8192u);
    assert(r1_export_plan_command(&state, &observation, &plan) == R1_OK);
    assert(plan.read_offset == 8192u && plan.read_length == 808u);
    assert(state.offset == 9000u);
    assert(r1_export_plan_command(&state, &observation, &plan) == R1_OK);
    assert(plan.finalize_provider && !state.active && plan.control_length == 0u);
    assert(r1_export_plan_command(&state, &observation, &plan) == R1_OK);
    assert(plan.finalize_provider && plan.control_length == 1u);
    assert(plan.control[0] == 3u);

    state = (r1_export_state){.total_bytes = 9000u, .offset = 8192u, .active = true};
    observation.result = 2u;
    assert(r1_export_plan_command(&state, &observation, &plan) == R1_OK);
    assert(plan.reset_offset && state.offset == 0u && !plan.send_data_marker);
    observation = (r1_export_observation){.command = 0u, .result = 1u};
    assert(r1_export_plan_command(&state, &observation, &plan) == R1_OK);
    assert(plan.control_length == 10u && plan.control[1] == 1u);
    assert(!plan.start_provider && !plan.send_data_marker);
    observation.result = 7u;
    observation.metadata_available = true;
    assert(r1_export_plan_command(&state, &observation, &plan) == R1_OK);
    assert(plan.control[1] == 1u);
    observation.command = 9u;
    assert(r1_export_plan_command(&state, &observation, &plan) == R1_OK);
    assert(plan.control_length == 0u && !plan.finalize_provider);
    assert(r1_export_plan_command(NULL, &observation, &plan) == R1_ERROR_ARGUMENT);
}

static void test_kv_snapshot_store(void) {
    static uint8_t bytes[R1_KV_PARTITION_BYTES];
    static uint8_t legacy_bytes[R1_KV_PARTITION_BYTES];
    static uint8_t snapshot[R1_KV_PARTITION_BYTES];
    static uint8_t attempt_bytes[R1_KV_PARTITION_BYTES];
    uint8_t health[12u];
    uint8_t actual[R1_KV_CLASS_PAYLOAD_MAX];
    size_t actual_length = 0u;
    r1_memory_flash memory;
    r1_kv_store store;

    assert(r1_kv_class_payload_length(R1_KV_DEV_INFO) == 52u);
    assert(r1_kv_class_payload_length(R1_KV_BLE_MULT) == 90u);
    assert(r1_kv_class_payload_length(R1_KV_HEALTH) == 12u);
    assert(r1_kv_class_payload_length(R1_KV_HSYNC) == 24u);
    assert(r1_kv_class_payload_length(R1_KV_POWER) == 4u);
    assert(r1_kv_class_payload_length(R1_KV_NV_R1) == 124u);
    assert(r1_kv_class_payload_length(R1_KV_RING_SIZE) == 1u);
    assert(strcmp(r1_kv_class_name(R1_KV_DEV_INFO), "dev_info") == 0);

    r1_memory_flash_initialize(&memory, bytes, sizeof bytes);
    assert(r1_kv_store_initialize(&store, r1_memory_flash_interface(&memory)) == R1_OK);
    assert(r1_kv_store_get(&store, R1_KV_HEALTH, health, sizeof health,
                           &actual_length) == R1_OK);
    assert(actual_length == sizeof health);
    assert(health[0] == 20u && health[2] == 175u && health[3] == 65u);
    assert(health[4] == 200u && health[6] == 50u && health[8] == 200u);
    assert(r1_kv_store_get(&store, R1_KV_NV_R1, actual, 123u,
                           &actual_length) == R1_ERROR_CAPACITY);
    assert(actual_length == 124u);

    health[0] = 21u;
    assert(r1_kv_store_set(&store, R1_KV_HEALTH, health, sizeof health) == R1_OK);
    assert(r1_kv_store_commit(&store) == R1_OK);
    assert(bytes[12] == '0' && bytes[13] == '1' && bytes[14] == 'P' && bytes[15] == 'E');
    assert(bytes[7u * R1_KV_CLASS_BLOCK_BYTES + 12u] == '0');

    r1_memory_flash legacy_memory;
    r1_memory_flash_initialize(&legacy_memory, legacy_bytes, sizeof legacy_bytes);
    memcpy(legacy_bytes, bytes, sizeof legacy_bytes);
    memset(legacy_bytes + 7u * R1_KV_CLASS_BLOCK_BYTES, UINT8_MAX,
           R1_KV_CLASS_BLOCK_BYTES);
    assert(r1_kv_store_initialize(&store,
                                  r1_memory_flash_interface(&legacy_memory)) == R1_OK);
    assert(r1_kv_store_get(&store, R1_KV_HEALTH, actual, sizeof actual,
                           &actual_length) == R1_OK);
    assert(actual[0] == 21u);
    actual[0] = 22u;
    assert(r1_kv_store_set(&store, R1_KV_HEALTH, actual, 12u) == R1_OK);
    assert(r1_kv_store_commit(&store) == R1_OK);
    assert(legacy_bytes[2u * R1_KV_SLOT_BYTES +
                        7u * R1_KV_CLASS_BLOCK_BYTES + 12u] == '0');

    assert(r1_kv_store_initialize(&store, r1_memory_flash_interface(&memory)) == R1_OK);
    assert(r1_kv_store_get(&store, R1_KV_HEALTH, actual, sizeof actual,
                           &actual_length) == R1_OK);
    assert(actual_length == sizeof health && actual[0] == 21u);

    for (uint8_t age = 22u; age <= 24u; ++age) {
        health[0] = age;
        assert(r1_kv_store_set(&store, R1_KV_HEALTH, health, sizeof health) == R1_OK);
        assert(r1_kv_store_commit(&store) == R1_OK);
    }
    memcpy(snapshot, bytes, sizeof snapshot);

    bool observed_old = false;
    bool observed_new = false;
    for (uint32_t cut = 0u; cut < 11u; ++cut) {
        r1_memory_flash attempt;
        r1_memory_flash_initialize(&attempt, attempt_bytes, sizeof attempt_bytes);
        memcpy(attempt_bytes, snapshot, sizeof snapshot);
        assert(r1_kv_store_initialize(&store, r1_memory_flash_interface(&attempt)) == R1_OK);
        assert(r1_kv_store_get(&store, R1_KV_HEALTH, health, sizeof health,
                               &actual_length) == R1_OK);
        assert(health[0] == 24u);
        health[0] = 25u;
        assert(r1_kv_store_set(&store, R1_KV_HEALTH, health, sizeof health) == R1_OK);
        r1_memory_flash_fail_after(&attempt, cut);
        r1_error commit_result = r1_kv_store_commit(&store);
        assert(commit_result == R1_OK || commit_result == R1_ERROR_STATE);
        r1_memory_flash_fail_after(&attempt, UINT32_MAX);

        assert(r1_kv_store_initialize(&store, r1_memory_flash_interface(&attempt)) == R1_OK);
        assert(r1_kv_store_get(&store, R1_KV_HEALTH, actual, sizeof actual,
                               &actual_length) == R1_OK);
        assert(actual_length == sizeof health);
        assert(actual[0] == 24u || actual[0] == 25u);
        observed_old = observed_old || actual[0] == 24u;
        observed_new = observed_new || actual[0] == 25u;
        if (commit_result == R1_OK) {
            assert(actual[0] == 25u);
        }
    }
    assert(observed_old && observed_new);
}

static void put_i16(uint8_t *bytes, int16_t value) {
    const uint16_t raw = (uint16_t)value;
    bytes[0] = (uint8_t)raw;
    bytes[1] = (uint8_t)(raw >> 8u);
}

static void test_nv_recovery_merge(void) {
    r1_nv_recovery_state current;
    r1_nv_recovery_result result;
    uint8_t body[R1_NV_RECOVERY_BODY_BYTES];
    memset(&current, UINT8_MAX, sizeof current);
    memset(body, 0, sizeof body);

    for (uint8_t index = 0u; index < 30u; ++index) {
        body[index] = (uint8_t)('A' + index % 26u);
        body[31u + index] = (uint8_t)('a' + index % 26u);
    }
    body[30] = 30u;
    body[61] = 5u;
    for (uint8_t index = 0u; index < 6u; ++index) {
        body[62u + index] = (uint8_t)(index + 1u);
        body[68u + index] = (uint8_t)(index + 11u);
    }
    body[92] = 3u;
    put_i16(body + 94u, -250);
    body[96] = 12u;
    const uint16_t crc = r1_crc16_modbus(body, sizeof body);

    assert(r1_nv_recovery_merge(NULL, body, sizeof body, crc, &result) ==
           R1_ERROR_ARGUMENT);
    assert(r1_nv_recovery_merge(&current, body, sizeof body - 1u, crc, &result) ==
           R1_ERROR_LENGTH);
    assert(r1_nv_recovery_merge(&current, body, sizeof body,
                                (uint16_t)(crc ^ 1u), &result) ==
           R1_ERROR_CHECKSUM);
    assert(r1_nv_recovery_merge(&current, body, sizeof body, crc, &result) == R1_OK);
    assert(result.changed_records ==
           (R1_NV_RECOVERY_CHANGED_CONFIG | R1_NV_RECOVERY_CHANGED_POWER |
            R1_NV_RECOVERY_CHANGED_RING_SIZE));
    assert(result.state.config[30] == 30u && result.state.config[61] == 5u);
    assert(memcmp(result.state.config, body, 31u) == 0);
    assert(memcmp(result.state.config + 31u, body + 31u, 43u) == 0);
    assert(result.state.power[0] == 3u && result.state.power[1] == UINT8_MAX);
    assert(result.state.power[2] == body[94] && result.state.power[3] == body[95]);
    assert(result.state.ring_size == 12u);

    r1_nv_recovery_state valid = result.state;
    uint8_t different[R1_NV_RECOVERY_BODY_BYTES];
    memcpy(different, body, sizeof different);
    different[0] = 'Z';
    different[31] = 'Z';
    different[62] = 99u;
    put_i16(different + 68u, 123);
    different[92] = 4u;
    put_i16(different + 94u, 300);
    different[96] = 6u;
    assert(r1_nv_recovery_merge(&valid, different, sizeof different,
                                r1_crc16_modbus(different, sizeof different),
                                &result) == R1_OK);
    assert(result.changed_records == 0u);
    assert(memcmp(&result.state, &valid, sizeof valid) == 0);

    memset(&current, UINT8_MAX, sizeof current);
    current.power[0] = 0u;
    put_i16(current.power + 2u, 0);
    current.ring_size = 0u;
    memset(body, 0, sizeof body);
    body[30] = 31u;
    body[61] = 0u;
    body[62] = UINT8_MAX;
    put_i16(body + 68u, -1);
    body[92] = 5u;
    put_i16(body + 94u, 0);
    body[96] = 16u;
    assert(r1_nv_recovery_merge(&current, body, sizeof body,
                                r1_crc16_modbus(body, sizeof body),
                                &result) == R1_OK);
    assert(result.changed_records == 0u);
    assert(memcmp(&result.state, &current, sizeof current) == 0);

    memset(&current, 0, sizeof current);
    current.config[30] = 3u;
    current.power[0] = 1u;
    put_i16(current.power + 2u, 0);
    current.ring_size = 6u;
    assert(r1_nv_recovery_build_body(&current, body));
    assert(body[30] == 3u && body[92] == 1u && body[96] == 6u);
    assert(body[74] == 0u && body[115] == 0u);
    current.config[30] = 0u;
    assert(!r1_nv_recovery_build_body(&current, body));
}

typedef struct {
    size_t calls;
    r1_sleep_db_record record;
    uint8_t body[R1_SLEEP_DB_SYNC_READ_MAX];
    size_t length;
} sleep_db_capture;

static bool capture_sleep_record(void *context, const r1_sleep_db_record *record,
                                 const uint8_t *body, size_t length) {
    sleep_db_capture *capture = context;
    capture->calls += 1u;
    capture->record = *record;
    capture->length = length;
    for (size_t index = 0u; index < length; ++index) {
        capture->body[index] = body[index];
    }
    return true;
}

static void sleep_db_body(uint8_t *body, size_t length,
                          uint32_t start, uint32_t end) {
    for (size_t index = 0u; index < length; ++index) {
        body[index] = (uint8_t)(index * 17u + 3u);
    }
    body[0] = UINT8_MAX;
    body[10] = 0xd4u;
    body[11] = 0xfeu;
    body[12] = (uint8_t)start;
    body[13] = (uint8_t)(start >> 8u);
    body[14] = (uint8_t)(start >> 16u);
    body[15] = (uint8_t)(start >> 24u);
    body[16] = (uint8_t)end;
    body[17] = (uint8_t)(end >> 8u);
    body[18] = (uint8_t)(end >> 16u);
    body[19] = (uint8_t)(end >> 24u);
}

static void test_sleep_database(void) {
    uint8_t bytes[R1_SLEEP_DB_BYTES];
    r1_memory_flash memory;
    r1_memory_flash_initialize(&memory, bytes, sizeof bytes);
    r1_sleep_db database;
    assert(r1_sleep_db_initialize(&database, r1_memory_flash_interface(&memory), 0u) == R1_OK);

    uint8_t body[32u];
    sleep_db_body(body, sizeof body, 100u, 200u);
    assert(r1_sleep_db_append(&database, body, sizeof body) == R1_OK);
    assert(memory.program_operations == 2u);
    assert(bytes[16] == sizeof body && bytes[17] == 0u);
    assert(bytes[18] == R1_SLEEP_DB_BODY_START && bytes[19] == 0u);
    assert(bytes[36] == UINT8_MAX && bytes[37] == UINT8_MAX &&
           bytes[38] == UINT8_MAX && bytes[39] == UINT8_MAX);
    for (size_t index = 0u; index < sizeof body; ++index) {
        assert(bytes[R1_SLEEP_DB_BODY_START + index] == body[index]);
    }

    size_t count = 0u;
    assert(r1_sleep_db_count(&database, &count) == R1_OK && count == 1u);
    sleep_db_capture capture = {0};
    size_t visited = 0u;
    assert(r1_sleep_db_iterate(&database, false, capture_sleep_record,
                               &capture, &visited) == R1_OK);
    assert(visited == 1u && capture.calls == 1u && capture.length == sizeof body);
    assert(capture.record.header_offset == 16u);
    assert(capture.record.utc_offset_minutes == -300);
    assert(capture.record.start_timestamp == 100u && capture.record.end_timestamp == 200u);

    assert(r1_sleep_db_mark_synchronized(&database, 16u, 101u, 200u) == R1_ERROR_STATE);
    assert(r1_sleep_db_mark_synchronized(&database, 17u, 100u, 200u) == R1_ERROR_ARGUMENT);
    assert(r1_sleep_db_mark_synchronized(&database, 16u, 100u, 200u) == R1_OK);
    capture = (sleep_db_capture){0};
    assert(r1_sleep_db_iterate(&database, true, capture_sleep_record,
                               &capture, &visited) == R1_OK);
    assert(visited == 0u && capture.calls == 0u);

    bytes[R1_SLEEP_DB_BODY_START] &= UINT8_C(0xfe);
    assert(r1_sleep_db_iterate(&database, false, capture_sleep_record,
                               &capture, &visited) == R1_ERROR_CHECKSUM);

    r1_memory_flash_initialize(&memory, bytes, sizeof bytes);
    assert(r1_sleep_db_initialize(&database, r1_memory_flash_interface(&memory), 0u) == R1_OK);
    r1_memory_flash_fail_after(&memory, 1u);
    assert(r1_sleep_db_append(&database, body, sizeof body) == R1_ERROR_STATE);
    assert(memory.program_operations == 1u);
    assert(r1_sleep_db_count(&database, &count) == R1_OK && count == 0u);

    r1_memory_flash_initialize(&memory, bytes, sizeof bytes);
    r1_flash flash = r1_memory_flash_interface(&memory);
    static const uint8_t zero = 0u;
    static const uint8_t erased = UINT8_MAX;
    assert(r1_flash_program(&flash, 0u, &zero, 1u) == R1_OK);
    assert(r1_flash_program(&flash, 0u, &erased, 1u) == R1_ERROR_STATE);

    r1_memory_flash_initialize(&memory, bytes, sizeof bytes);
    assert(r1_sleep_db_initialize(&database, r1_memory_flash_interface(&memory), 0u) == R1_OK);
    for (uint32_t index = 0u; index < 16u; ++index) {
        sleep_db_body(body, sizeof body, 1000u + index, 2000u + index);
        assert(r1_sleep_db_append(&database, body, sizeof body) == R1_OK);
    }
    assert(r1_sleep_db_count(&database, &count) == R1_OK && count == 16u);
    sleep_db_body(body, sizeof body, 3000u, 4000u);
    assert(r1_sleep_db_append(&database, body, sizeof body) == R1_OK);
    assert(memory.erase_operations == 1u);
    assert(r1_sleep_db_count(&database, &count) == R1_OK && count == 9u);
    assert(r1_sleep_db_mark_synchronized(&database, R1_FLASH_PAGE_BYTES + 16u,
                                         1008u, 2008u) == R1_OK);

    uint8_t oversized[R1_SLEEP_DB_SYNC_READ_MAX + 4u];
    r1_memory_flash_initialize(&memory, bytes, sizeof bytes);
    assert(r1_sleep_db_initialize(&database, r1_memory_flash_interface(&memory), 0u) == R1_OK);
    sleep_db_body(oversized, sizeof oversized, 10u, 20u);
    assert(r1_sleep_db_append(&database, oversized, sizeof oversized) == R1_OK);
    assert(r1_sleep_db_count(&database, &count) == R1_OK && count == 1u);
    capture = (sleep_db_capture){0};
    assert(r1_sleep_db_iterate(&database, false, capture_sleep_record,
                               &capture, &visited) == R1_OK);
    assert(visited == 0u);

    uint8_t maximum[R1_SLEEP_DB_APPEND_MAX];
    r1_memory_flash_initialize(&memory, bytes, sizeof bytes);
    assert(r1_sleep_db_initialize(&database, r1_memory_flash_interface(&memory), 0u) == R1_OK);
    sleep_db_body(maximum, sizeof maximum, 30u, 40u);
    assert(r1_sleep_db_append(&database, maximum, sizeof maximum) == R1_OK);
    assert(r1_sleep_db_append(&database, maximum, sizeof maximum + 1u) == R1_ERROR_LENGTH);
    assert(r1_sleep_db_erase_all(&database) == R1_OK);
    assert(memory.erase_operations == 2u);
    assert(r1_sleep_db_count(&database, &count) == R1_OK && count == 0u);
}

static void test_sleep_persistence_bridge(void) {
    r1_sleep_session source = {0};
    source.type = 1u;
    source.efficiency = 91u;
    source.score = 82u;
    source.utc_offset_minutes = -300;
    source.start_timestamp = 1000u;
    source.end_timestamp = 2000u;
    source.total_minutes = 500u;
    source.stage_count = 3u;
    source.stages[0] = (r1_sleep_stage){2u, 300u};
    source.stages[1] = (r1_sleep_stage){2u, 10u};
    source.stages[2] = (r1_sleep_stage){3u, 120u};

    uint8_t compact[R1_SLEEP_STORED_MAX_BYTES];
    size_t written = 0u;
    assert(r1_sleep_encode_compact(&source, compact, sizeof compact, &written) == R1_OK);
    assert(written == 40u);
    assert(compact[30] == 8u && compact[31] == 0u);
    assert(compact[32] == (uint8_t)((63u << 2u) | 2u));
    uint8_t sync_packet[R1_SLEEP_PAYLOAD_MAX_BYTES];
    size_t sync_written = 0u;
    assert(r1_sleep_build_sync_packet(
               compact, written, 1500u, -360,
               sync_packet, sizeof sync_packet, &sync_written) == R1_OK);
    assert(sync_written == 38u);
    assert(sync_packet[3] == 0u);
    assert(sync_packet[10] == 0u && sync_packet[11] == 0u);
    assert(sync_packet[16] == 0xdcu && sync_packet[17] == 0x05u);
    assert(sync_packet[30] == 2u && sync_packet[31] == 0u);
    assert(sync_packet[32] == 2u);
    assert(sync_packet[33] == 0x36u && sync_packet[34] == 0x01u);
    assert(sync_packet[35] == 3u);
    assert(sync_packet[36] == 120u && sync_packet[37] == 0u);

    source.start_timestamp = R1_HEALTH_LEGACY_CLOCK_CUTOFF;
    source.end_timestamp = source.start_timestamp + 1000u;
    assert(r1_sleep_encode_compact(
               &source, compact, sizeof compact, &written) == R1_OK);
    assert(r1_sleep_build_sync_packet(
               compact, written, source.start_timestamp + 500u, -360,
               sync_packet, sizeof sync_packet, &sync_written) == R1_OK);
    assert(sync_packet[10] == 0x98u && sync_packet[11] == 0xfeu);
    assert(sync_packet[16] == compact[16] && sync_packet[17] == compact[17]);
    compact[32] = 0u;
    assert(r1_sleep_build_sync_packet(
               compact, written, 0u, 0,
               sync_packet, sizeof sync_packet, &sync_written) ==
           R1_ERROR_LENGTH);

    source.start_timestamp = 1000u;
    source.end_timestamp = 2000u;
    assert(r1_sleep_encode_compact(
               &source, compact, sizeof compact, &written) == R1_OK);
    r1_sleep_session decoded;
    assert(r1_sleep_decode_compact(compact, written, true, &decoded) == R1_OK);
    assert(decoded.synchronized);
    assert(decoded.stage_count == 2u);
    assert(decoded.stages[0].type == 2u && decoded.stages[0].half_minutes == 310u);
    assert(decoded.stages[1].type == 3u && decoded.stages[1].half_minutes == 120u);

    uint8_t bytes[R1_SLEEP_DB_BYTES];
    r1_memory_flash memory;
    r1_memory_flash_initialize(&memory, bytes, sizeof bytes);
    r1_sleep_db database;
    assert(r1_sleep_db_initialize(&database, r1_memory_flash_interface(&memory), 0u) == R1_OK);
    assert(r1_sleep_persist(&database, &source) == R1_OK);
    assert(r1_sleep_db_mark_synchronized(&database, 16u, 1000u, 2000u) == R1_OK);
    r1_sleep_history restored;
    assert(r1_sleep_restore(&database, &restored) == R1_OK);
    assert(restored.count == 1u);
    assert(restored.sessions[0].synchronized);
    assert(restored.sessions[0].stage_count == 2u);
    assert(restored.sessions[0].stages[0].half_minutes == 310u);
    assert(restored.sessions[0].has_storage_record);
    assert(restored.sessions[0].storage_header_offset == 16u);

    r1_memory_flash_initialize(&memory, bytes, sizeof bytes);
    assert(r1_sleep_db_initialize(&database, r1_memory_flash_interface(&memory), 0u) == R1_OK);
    source.synchronized = false;
    source.has_storage_record = false;
    source.storage_header_offset = 0u;
    assert(r1_sleep_persist_tracked(&database, &source) == R1_OK);
    assert(source.has_storage_record && source.storage_header_offset == 16u);
    r1_health_state health;
    r1_health_initialize(&health);
    assert(r1_sleep_store(&health.sleep, &source) == R1_OK);
    r1_health_bind_sleep_sync_commit(&health, r1_sleep_commit_synchronized, &database);
    assert(r1_health_register_pending(&health, 2u, 6u, 1u, 77u,
                                      R1_PENDING_SLEEP_SESSION, 0u) == R1_OK);
    r1_memory_flash_fail_after(&memory, 0u);
    assert(!r1_health_acknowledge(&health, 2u, 6u, 1u, 77u));
    assert(health.pending[0].active);
    assert(!health.sleep.sessions[0].synchronized);
    r1_memory_flash_fail_after(&memory, UINT32_MAX);
    assert(r1_health_acknowledge(&health, 2u, 6u, 1u, 77u));
    assert(!health.pending[0].active);
    assert(health.sleep.sessions[0].synchronized);
    assert(bytes[36] == 0x44u && bytes[37] == 0x33u &&
           bytes[38] == 0x22u && bytes[39] == 0x11u);

    source.stage_count = 1u;
    source.stages[0] = (r1_sleep_stage){1u, UINT16_MAX};
    assert(r1_sleep_encode_compact(&source, compact, sizeof compact, &written) == R1_ERROR_LENGTH);
    compact[30] = 1u;
    compact[31] = 0u;
    compact[32] = 0u;
    assert(r1_sleep_decode_compact(compact, 33u, false, &decoded) == R1_ERROR_LENGTH);
}

static void test_validated_sleep_delivery_plans(void) {
    r1_sleep_session session = {0};
    session.start_timestamp = 1000u;
    session.end_timestamp = 4599u;
    session.stage_count = 7u;
    r1_sleep_validated_delivery_plan delivery;
    assert(r1_sleep_plan_validated_delivery(&session, &delivery) == R1_OK);
    assert(delivery.route == R1_SLEEP_VALIDATED_DROP_TOO_SHORT);
    assert(delivery.wrapping_duration_seconds == 3599u);
    assert(!delivery.timestamp_wrapped);
    assert(!delivery.direct_fallback_on_post_failure);

    session.end_timestamp = 4600u;
    assert(r1_sleep_plan_validated_delivery(&session, &delivery) == R1_OK);
    assert(delivery.route == R1_SLEEP_VALIDATED_POST_STORAGE_EVENT);
    assert(delivery.storage_event == R1_SLEEP_STORAGE_EVENT);
    assert(delivery.event_payload_length == 39u);
    assert(delivery.direct_fallback_on_post_failure);

    session.start_timestamp = UINT32_MAX - 99u;
    session.end_timestamp = 4000u;
    assert(r1_sleep_plan_validated_delivery(&session, &delivery) == R1_OK);
    assert(delivery.route == R1_SLEEP_VALIDATED_POST_STORAGE_EVENT);
    assert(delivery.timestamp_wrapped);
    assert(delivery.wrapping_duration_seconds == 4100u);

    session.stage_count = R1_SLEEP_COMPACT_STAGE_MAX + 1u;
    assert(r1_sleep_plan_validated_delivery(&session, &delivery) == R1_ERROR_LENGTH);
    assert(r1_sleep_plan_validated_delivery(NULL, &delivery) == R1_ERROR_ARGUMENT);
    assert(r1_sleep_plan_validated_delivery(&session, NULL) == R1_ERROR_ARGUMENT);

    r1_sleep_storage_consumer_plan storage;
    assert(r1_sleep_plan_storage_consumer(false, false, &storage) == R1_OK);
    assert(!storage.consume_record && !storage.request_automatic_sync);
    assert(r1_sleep_plan_storage_consumer(true, false, &storage) == R1_OK);
    assert(storage.consume_record && !storage.request_automatic_sync);
    assert(r1_sleep_plan_storage_consumer(true, true, &storage) == R1_OK);
    assert(storage.consume_record && storage.request_automatic_sync);
    assert(storage.automatic_sync_argument == R1_SLEEP_AUTOMATIC_SYNC_TRIGGER);
    assert(r1_sleep_plan_storage_consumer(true, true, NULL) == R1_ERROR_ARGUMENT);
}

typedef struct {
    uint32_t calls[16u];
    size_t count;
    int32_t provider_result;
} goodix_trace;

static void goodix_record(goodix_trace *trace, uint32_t value) {
    assert(trace->count < sizeof trace->calls / sizeof trace->calls[0]);
    trace->calls[trace->count++] = value;
}

static bool goodix_prepare(void *context) {
    goodix_record(context, UINT32_C(0x10000000));
    return true;
}

static void goodix_shutdown(void *context) {
    goodix_record(context, UINT32_C(0x20000000));
}

static void goodix_delay(void *context, uint32_t milliseconds) {
    goodix_record(context, UINT32_C(0x30000000) | milliseconds);
}

static int32_t goodix_initialize(void *context) {
    goodix_trace *trace = context;
    goodix_record(trace, UINT32_C(0x40000000));
    return trace->provider_result;
}

static int32_t goodix_switch(void *context, uint8_t configuration) {
    goodix_trace *trace = context;
    goodix_record(trace, UINT32_C(0x50000000) | configuration);
    return trace->provider_result;
}

static int32_t goodix_start(void *context, uint32_t mask) {
    goodix_trace *trace = context;
    goodix_record(trace, UINT32_C(0x60000000) | mask);
    return trace->provider_result;
}

static int32_t goodix_stop(void *context, uint32_t mask) {
    goodix_trace *trace = context;
    goodix_record(trace, UINT32_C(0x70000000) | mask);
    return trace->provider_result;
}

static void test_goodix_provider_boundary(void) {
    static const r1_goodix_provider_ops provider = {
        goodix_initialize, goodix_switch, goodix_start, goodix_stop,
    };
    static const r1_goodix_board_ops board = {
        goodix_prepare, goodix_shutdown, goodix_delay,
    };
    r1_goodix_adapter adapter;
    r1_goodix_adapter_initialize(&adapter);
    assert(!r1_goodix_provider_available(&adapter));
    assert(r1_goodix_start_stock_profile(&adapter, R1_GOODIX_STOCK_PROFILE_2000)
           == R1_ERROR_UNSUPPORTED);

    goodix_trace trace = {0};
    assert(r1_goodix_adapter_bind(&adapter, &provider, &trace, &board, &trace)
           == R1_OK);
    assert(r1_goodix_start_stock_profile(&adapter, R1_GOODIX_STOCK_PROFILE_4000)
           == R1_OK);
    assert(adapter.initialized && adapter.prepared);
    assert(adapter.active_mask == R1_GOODIX_MASK_STOCK_4000);
    assert(trace.count == 4u);
    assert(trace.calls[0] == UINT32_C(0x10000000));
    assert(trace.calls[1] == UINT32_C(0x3000000a));
    assert(trace.calls[2] == UINT32_C(0x40000000));
    assert(trace.calls[3] == (UINT32_C(0x60000000) | R1_GOODIX_MASK_STOCK_4000));

    trace.count = 0u;
    assert(r1_goodix_switch_profile(&adapter, R1_GOODIX_SWITCH_PROFILE_2) == R1_OK);
    assert(trace.count == 5u);
    assert(trace.calls[0] == UINT32_C(0x30000064));
    assert(trace.calls[1] == UINT32_C(0x50000000));
    assert(trace.calls[2] == (UINT32_C(0x70000000) | R1_GOODIX_MASK_SWITCH_CLEAR));
    assert(trace.calls[3] == UINT32_C(0x3000000a));
    assert(trace.calls[4] == (UINT32_C(0x60000000) | R1_GOODIX_MASK_SWITCH_2));

    trace.count = 0u;
    assert(r1_goodix_stop_stock_profiles(&adapter) == R1_OK);
    assert(trace.count == 3u);
    assert(trace.calls[0] == (UINT32_C(0x70000000) | R1_GOODIX_MASK_STOCK_2000));
    assert(trace.calls[1] == (UINT32_C(0x70000000) | R1_GOODIX_MASK_STOCK_4000));
    assert(trace.calls[2] == UINT32_C(0x20000000));
    assert(!adapter.initialized && !adapter.prepared && adapter.active_mask == 0u);

    r1_goodix_adapter_initialize(&adapter);
    trace = (goodix_trace){0};
    trace.provider_result = -1;
    assert(r1_goodix_adapter_bind(&adapter, &provider, &trace, &board, &trace)
           == R1_OK);
    assert(r1_goodix_start_stock_profile(&adapter, R1_GOODIX_STOCK_PROFILE_2000)
           == R1_ERROR_STATE);
    assert(trace.count == 4u && trace.calls[3] == UINT32_C(0x20000000));
    assert(!adapter.initialized && adapter.active_mask == 0u);
}

typedef struct {
    uint32_t recorded_info1;
    size_t record_count;
    size_t halt_count;
    bool halt_after_record;
} goodix_fatal_trace;

static void goodix_fatal_record(void *context, uint32_t info1) {
    goodix_fatal_trace *trace = context;
    trace->recorded_info1 = info1;
    trace->record_count++;
}

static void goodix_fatal_halt(void *context) {
    goodix_fatal_trace *trace = context;
    trace->halt_after_record = trace->record_count == 1u;
    trace->halt_count++;
}

static void test_goodix_mem_integrator_glue(void) {
    uint8_t buffer[8u];
    memset(buffer, 0xa5, sizeof buffer);
    r1_goodix_pool_fill(NULL, 4u);
    r1_goodix_pool_fill(buffer, 0u);
    for (size_t index = 0u; index < sizeof buffer; ++index) {
        assert(buffer[index] == 0xa5u);
    }
    r1_goodix_pool_fill(buffer, 6u);
    for (size_t index = 0u; index < 6u; ++index) {
        assert(buffer[index] == 0u);
    }
    assert(buffer[6u] == 0xa5u && buffer[7u] == 0xa5u);

    r1_goodix_pool_not_enough(NULL, UINT32_C(7));

    goodix_fatal_trace trace = {0};
    const r1_goodix_pool_fatal_ops halt_only = {
        NULL, goodix_fatal_halt, &trace,
    };
    r1_goodix_pool_not_enough(&halt_only, UINT32_C(9));
    assert(trace.halt_count == 1u && trace.record_count == 0u);
    assert(!trace.halt_after_record);

    trace = (goodix_fatal_trace){0};
    const r1_goodix_pool_fatal_ops full = {
        goodix_fatal_record, goodix_fatal_halt, &trace,
    };
    r1_goodix_pool_not_enough(&full, UINT32_C(0xdeadbeef));
    assert(trace.record_count == 1u && trace.halt_count == 1u);
    assert(trace.recorded_info1 == UINT32_C(0xdeadbeef));
    assert(trace.halt_after_record);
}

typedef struct {
    bool read;
    uint8_t reg;
    size_t length;
    uint8_t bytes[40u];
} iqs_operation;

typedef struct {
    iqs_operation operations[128u];
    size_t operation_count;
    uint8_t system_control[2u];
    uint8_t irq_bytes[6u];
    size_t open_count;
    size_t close_count;
    size_t schedule_count;
    uint32_t scheduled_ticks;
} iqs_trace;

static iqs_operation *iqs_record(iqs_trace *trace, bool read, uint8_t reg,
                                 size_t length) {
    assert(trace->operation_count < sizeof trace->operations /
                                    sizeof trace->operations[0]);
    assert(length <= sizeof trace->operations[0].bytes);
    iqs_operation *operation = &trace->operations[trace->operation_count++];
    operation->read = read;
    operation->reg = reg;
    operation->length = length;
    return operation;
}

static int32_t iqs_read(void *context, uint8_t address, uint8_t reg,
                        uint8_t *bytes, size_t length) {
    iqs_trace *trace = context;
    assert(address == R1_IQS7211E_ADDRESS);
    iqs_operation *operation = iqs_record(trace, true, reg, length);
    if (reg == R1_IQS7211E_REGISTER_SYSTEM_CONTROL) {
        assert(length == sizeof trace->system_control);
        memcpy(bytes, trace->system_control, length);
    } else {
        assert(reg == R1_IQS7211E_REGISTER_INFO_FLAGS);
        assert(length == sizeof trace->irq_bytes);
        memcpy(bytes, trace->irq_bytes, length);
    }
    memcpy(operation->bytes, bytes, length);
    return 0;
}

static int32_t iqs_write(void *context, uint8_t address, uint8_t reg,
                         const uint8_t *bytes, size_t length) {
    iqs_trace *trace = context;
    assert(address == R1_IQS7211E_ADDRESS);
    iqs_operation *operation = iqs_record(trace, false, reg, length);
    if (length != 0u) {
        assert(bytes != NULL);
        memcpy(operation->bytes, bytes, length);
    } else {
        assert(bytes == NULL);
    }
    return 0;
}

static bool iqs_open(void *context) {
    iqs_trace *trace = context;
    ++trace->open_count;
    return true;
}

static void iqs_close(void *context) {
    iqs_trace *trace = context;
    ++trace->close_count;
}

static bool iqs_schedule(void *context, uint32_t delay_ticks) {
    iqs_trace *trace = context;
    ++trace->schedule_count;
    trace->scheduled_ticks = delay_ticks;
    return true;
}

static void test_iqs7211e_provider_boundary(void) {
    static const r1_iqs7211e_provider_ops provider = {iqs_read, iqs_write};
    static const r1_iqs7211e_board_ops board = {iqs_open, iqs_close, iqs_schedule};
    r1_iqs7211e_adapter adapter;
    r1_iqs7211e_adapter_initialize(&adapter);
    assert(!r1_iqs7211e_provider_available(&adapter));
    assert(r1_iqs7211e_configure(&adapter, R1_IQS7211E_LAYOUT_EIGHT_TX_THREE_RX,
                                 6u) == R1_ERROR_UNSUPPORTED);
    assert(r1_iqs7211e_calibration_for(R1_IQS7211E_LAYOUT_EIGHT_TX_THREE_RX,
                                       5u) == NULL);
    const r1_iqs7211e_calibration *calibration = r1_iqs7211e_calibration_for(
        R1_IQS7211E_LAYOUT_SEVEN_TX_THREE_RX, 10u);
    assert(calibration != NULL);
    assert(calibration->compensation_divider == 0x0cu);
    assert(calibration->fine_fractional_divider == 0x09u);
    assert(calibration->minimum_trim_index == 1u);
    assert(calibration->maximum_trim_index == 5u);
    assert(calibration->channel_slots[2] == UINT8_MAX);
    assert(calibration->channel_slots[3] == 3u);
    assert(calibration->channel_slots[21] == UINT8_MAX);
    uint8_t recovered_records[600u];
    size_t recovered_offset = 0u;
    for (size_t layout_index = 0u; layout_index < 2u; ++layout_index) {
        for (uint8_t ring_size = R1_IQS7211E_RING_SIZE_MIN;
             ring_size <= R1_IQS7211E_RING_SIZE_MAX; ++ring_size) {
            const r1_iqs7211e_calibration *record = r1_iqs7211e_calibration_for(
                (r1_iqs7211e_layout)layout_index, ring_size);
            assert(record != NULL && recovered_offset + 30u <= sizeof recovered_records);
            recovered_records[recovered_offset] = record->compensation_divider;
            recovered_records[recovered_offset + 1u] = 0u;
            recovered_records[recovered_offset + 2u] = record->fine_fractional_divider;
            recovered_records[recovered_offset + 3u] = record->minimum_trim_index;
            recovered_records[recovered_offset + 4u] = record->maximum_trim_index;
            memcpy(recovered_records + recovered_offset + 5u, record->channel_slots,
                   R1_IQS7211E_CHANNEL_SLOT_COUNT);
            recovered_records[recovered_offset + 29u] = 0u;
            recovered_offset += 30u;
        }
    }
    assert(recovered_offset == sizeof recovered_records);
    assert(r1_crc32_castagnoli(recovered_records, sizeof recovered_records) ==
           UINT32_C(0x7179fa46));

    iqs_trace trace = {0};
    assert(r1_iqs7211e_adapter_bind(&adapter, &provider, &trace, &board, &trace)
           == R1_OK);
    assert(r1_iqs7211e_configure(&adapter, R1_IQS7211E_LAYOUT_SEVEN_TX_THREE_RX,
                                 10u) == R1_OK);
    assert(trace.open_count == 1u && trace.operation_count == 10u);
    assert(trace.operations[0].reg == 0x1fu && trace.operations[0].length == 4u);
    assert(trace.operations[0].bytes[0] == 0x11u &&
           trace.operations[0].bytes[3] == 0x02u);
    assert(trace.operations[1].reg == 0x21u && trace.operations[1].bytes[1] == 0x13u &&
           trace.operations[1].bytes[2] == 0x0cu);
    assert(trace.operations[3].reg == 0x36u && trace.operations[3].bytes[3] == 0x1bu);
    assert(trace.operations[4].reg == 0x41u && trace.operations[4].bytes[2] == 0x08u);
    assert(trace.operations[6].reg == 0x56u && trace.operations[6].bytes[9] == 0x01u &&
           trace.operations[6].bytes[10] == 0x0au);
    assert(trace.operations[7].reg == 0x5du && trace.operations[7].length == 30u);
    assert(trace.operations[8].reg == 0x6cu && trace.operations[8].length == 33u);
    assert(trace.operations[9].reg == 0x33u && trace.operations[9].length == 6u);
    static const uint8_t final_control[] = {0xa0u, 0x00u, 0x6cu, 0x47u, 0x00u, 0x00u};
    assert(memcmp(trace.operations[9].bytes, final_control, sizeof final_control) == 0);

    trace.system_control[0] = 0x20u;
    trace.system_control[1] = 0x01u;
    const size_t before_suspend = trace.operation_count;
    assert(r1_iqs7211e_suspend(&adapter) == R1_OK);
    assert(trace.operation_count == before_suspend + 3u);
    assert(trace.operations[before_suspend].read);
    assert(trace.operations[before_suspend + 1u].reg == 0x33u);
    assert(trace.operations[before_suspend + 1u].bytes[0] == 0x20u);
    assert(trace.operations[before_suspend + 1u].bytes[1] == 0x09u);
    assert(trace.operations[before_suspend + 2u].reg == 0xffu &&
           trace.operations[before_suspend + 2u].length == 0u);

    trace.operation_count = 0u;
    trace.irq_bytes[0] = (uint8_t)R1_IQS7211E_INFO_ATI_ERROR;
    for (size_t index = 0u; index < 4u; ++index) {
        assert(r1_iqs7211e_process_irq(&adapter, 0u) == R1_OK);
        assert(!adapter.restart_pending);
    }
    assert(adapter.consecutive_ati_errors == 4u);
    assert(r1_iqs7211e_process_irq(&adapter, 0u) == R1_OK);
    assert(adapter.restart_pending);
    assert(adapter.hardware_restart_attempts == 1u);
    assert(trace.close_count == 1u && trace.schedule_count == 1u);
    assert(trace.scheduled_ticks == R1_IQS7211E_RESTART_DELAY_TICKS);
    assert(r1_iqs7211e_process_irq(&adapter, 0u) == R1_ERROR_STATE);
    assert(r1_iqs7211e_resume_scheduled_restart(&adapter) == R1_OK);
    assert(adapter.configured && !adapter.restart_pending);
    assert(trace.open_count == 2u);

    trace.operation_count = 0u;
    memset(trace.irq_bytes, 0, sizeof trace.irq_bytes);
    trace.irq_bytes[1] = 0x10u;
    assert(r1_iqs7211e_process_irq(&adapter, 0u) == R1_OK);
    assert(trace.operations[2].reg == 0x33u && trace.operations[2].bytes[0] == 0x08u);
    assert(trace.operations[3].reg == 0xffu);

    trace.operation_count = 0u;
    trace.system_control[0] = 0x20u;
    trace.system_control[1] = 0x01u;
    assert(r1_iqs7211e_deactivate(&adapter) == R1_OK);
    assert(!adapter.configured && !adapter.restart_pending);
    assert(adapter.consecutive_ati_errors == 0u);
    assert(adapter.hardware_restart_attempts == 0u);
    assert(trace.close_count == 2u);
    assert(trace.operation_count == 3u);
    assert(trace.operations[2].reg == R1_IQS7211E_REGISTER_COMMUNICATION_END);
    assert(r1_iqs7211e_deactivate(&adapter) == R1_OK);
    assert(trace.close_count == 3u && trace.operation_count == 3u);
}

static void test_iqs7211e_ati_audit_policy(void) {
    r1_iqs7211e_ati_audit_state state = {0u, UINT32_C(900)};
    r1_iqs7211e_ati_audit_request request;
    assert(r1_iqs7211e_ati_audit_begin(
        state, UINT32_C(1000), R1_IQS7211E_LAYOUT_EIGHT_TX_THREE_RX,
        &request));
    assert(request.state.sequence == 1u);
    assert(request.state.last_tick == 1000u);
    assert(request.audit_due);
    assert(request.device_address == R1_IQS7211E_ADDRESS);
    assert(request.register_address == R1_IQS7211E_REGISTER_ATI_COMPENSATION);
    assert(request.channel_count == 24u && request.read_length_bytes == 48u);

    state = request.state;
    assert(r1_iqs7211e_ati_audit_begin(
        state, UINT32_C(10999), R1_IQS7211E_LAYOUT_SEVEN_TX_THREE_RX,
        &request));
    assert(!request.audit_due);
    assert(request.state.sequence == 2u);
    assert(request.state.last_tick == 1000u);
    assert(request.channel_count == 21u && request.read_length_bytes == 42u);
    state = request.state;
    assert(r1_iqs7211e_ati_audit_begin(
        state, UINT32_C(11000), R1_IQS7211E_LAYOUT_SEVEN_TX_THREE_RX,
        &request));
    assert(request.audit_due && request.state.last_tick == 11000u);

    state.sequence = UINT32_MAX;
    state.last_tick = UINT32_MAX - UINT32_C(10);
    assert(r1_iqs7211e_ati_audit_begin(
        state, UINT32_C(5), R1_IQS7211E_LAYOUT_EIGHT_TX_THREE_RX,
        &request));
    assert(request.state.sequence == 0u);
    assert(!request.audit_due);
    assert(request.state.last_tick == state.last_tick);

    const r1_iqs7211e_ati_audit_request unchanged_request = request;
    assert(!r1_iqs7211e_ati_audit_begin(
        state, 0u, (r1_iqs7211e_layout)2, &request));
    assert(memcmp(&request, &unchanged_request, sizeof request) == 0);
    assert(!r1_iqs7211e_ati_audit_begin(
        state, 0u, R1_IQS7211E_LAYOUT_EIGHT_TX_THREE_RX, NULL));

    uint16_t samples[24u];
    uint8_t map[24u];
    for (size_t index = 0u; index < 24u; ++index) {
        samples[index] = (uint16_t)(100u + index);
        map[index] = (index % 3u) == 0u ? UINT8_MAX : (uint8_t)index;
    }
    samples[1] = 2u;
    samples[23] = 900u;
    r1_iqs7211e_ati_audit_summary summary;
    assert(r1_iqs7211e_ati_audit_summarize(
        samples, 24u, map, &summary));
    assert(summary.active_count == 16u);
    assert(summary.minimum == 2u && summary.maximum == 900u);
    assert(summary.active_values[0] == 2u);
    assert(summary.active_values[15] == 900u);

    memset(map, UINT8_MAX, sizeof map);
    assert(r1_iqs7211e_ati_audit_summarize(samples, 21u, map, &summary));
    assert(summary.active_count == 0u);
    assert(summary.minimum == 0u && summary.maximum == 0u);
    for (size_t index = 0u; index < 24u; ++index) {
        assert(summary.active_values[index] == 0u);
    }
    assert(r1_iqs7211e_ati_audit_summarize(
        samples, 21u, NULL, &summary));
    assert(summary.active_count == 21u);
    assert(!r1_iqs7211e_ati_audit_summarize(NULL, 21u, map, &summary));
    assert(!r1_iqs7211e_ati_audit_summarize(samples, 22u, map, &summary));
    assert(!r1_iqs7211e_ati_audit_summarize(samples, 21u, map, NULL));
}

typedef struct {
    size_t initialize_count;
    size_t initialize_failures;
    size_t deinitialize_count;
    size_t read_id_count;
    size_t security_read_count;
    size_t password_count;
    size_t mailbox_status_count;
    size_t mailbox_enable_count;
    size_t reset_eh_count;
    size_t set_gpo1_count;
    size_t read_gpo2_count;
    size_t set_gpo2_count;
    size_t mailbox_read_count;
    size_t delay_count;
    size_t mailbox_read_length;
    uint32_t password_msb;
    uint32_t password_lsb;
    uint32_t delayed_ticks;
    uint8_t ic_reference;
    uint8_t gpo1;
    uint8_t gpo2;
    uint8_t encoded_length;
    bool security_open;
    bool mailbox_mode;
    r1_st25dvxxkc_mailbox_status mailbox_status;
    uint8_t mailbox[R1_ST25DVXXKC_MAILBOX_CAPACITY];
} st25_trace;

typedef struct {
    size_t calls;
    size_t length;
    uint8_t bytes[R1_ST25DVXXKC_MAILBOX_CAPACITY];
} st25_frame_capture;

static int32_t st25_initialize(void *context) {
    st25_trace *trace = context;
    ++trace->initialize_count;
    return trace->initialize_count <= trace->initialize_failures ? -1 : 0;
}

static void st25_deinitialize(void *context) {
    st25_trace *trace = context;
    ++trace->deinitialize_count;
}

static int32_t st25_read_id(void *context, uint8_t *ic_reference) {
    st25_trace *trace = context;
    ++trace->read_id_count;
    *ic_reference = trace->ic_reference;
    return 0;
}

static int32_t st25_read_security_session(void *context, bool *open) {
    st25_trace *trace = context;
    ++trace->security_read_count;
    *open = trace->security_open;
    return 0;
}

static int32_t st25_present_password(void *context, uint32_t most_significant,
                                     uint32_t least_significant) {
    st25_trace *trace = context;
    ++trace->password_count;
    trace->password_msb = most_significant;
    trace->password_lsb = least_significant;
    if (most_significant == 0u && least_significant == 0u) {
        trace->security_open = true;
        return 0;
    }
    if (most_significant == R1_ST25DVXXKC_SESSION_CLOSE_MSB &&
        least_significant == R1_ST25DVXXKC_SESSION_CLOSE_LSB) {
        trace->security_open = false;
        return 0;
    }
    return -1;
}

static int32_t st25_read_mailbox_mode(void *context, bool *enabled) {
    st25_trace *trace = context;
    *enabled = trace->mailbox_mode;
    return 0;
}

static int32_t st25_read_mailbox_status(
    void *context, r1_st25dvxxkc_mailbox_status *status) {
    st25_trace *trace = context;
    ++trace->mailbox_status_count;
    *status = trace->mailbox_status;
    return 0;
}

static int32_t st25_set_mailbox_enabled(void *context) {
    st25_trace *trace = context;
    ++trace->mailbox_enable_count;
    trace->mailbox_status.mailbox_enabled = true;
    return 0;
}

static int32_t st25_reset_eh(void *context) {
    st25_trace *trace = context;
    ++trace->reset_eh_count;
    return 0;
}

static int32_t st25_set_gpo1(void *context, uint8_t configuration) {
    st25_trace *trace = context;
    ++trace->set_gpo1_count;
    trace->gpo1 = configuration;
    return trace->set_gpo1_count < 3u ? -1 : 0;
}

static int32_t st25_read_gpo2(void *context, uint8_t *configuration) {
    st25_trace *trace = context;
    ++trace->read_gpo2_count;
    *configuration = trace->gpo2;
    return 0;
}

static int32_t st25_set_gpo2(void *context, uint8_t configuration) {
    st25_trace *trace = context;
    ++trace->set_gpo2_count;
    trace->gpo2 = configuration;
    return 0;
}

static int32_t st25_read_mailbox_length(void *context,
                                        uint8_t *encoded_length) {
    st25_trace *trace = context;
    *encoded_length = trace->encoded_length;
    return 0;
}

static int32_t st25_read_mailbox(void *context, uint16_t offset,
                                 uint8_t *bytes, size_t length) {
    st25_trace *trace = context;
    assert(offset == 0u);
    assert(length <= sizeof trace->mailbox);
    ++trace->mailbox_read_count;
    trace->mailbox_read_length = length;
    memcpy(bytes, trace->mailbox, length);
    return 0;
}

static void st25_delay(void *context, uint32_t ticks) {
    st25_trace *trace = context;
    ++trace->delay_count;
    trace->delayed_ticks += ticks;
}

static void capture_st25_frame(void *context, const uint8_t *bytes,
                               size_t length) {
    st25_frame_capture *capture = context;
    assert(length <= sizeof capture->bytes);
    ++capture->calls;
    capture->length = length;
    memcpy(capture->bytes, bytes, length);
}

static void test_st25dvxxkc_provider_boundary(void) {
    static const r1_st25dvxxkc_provider_ops provider = {
        st25_initialize,
        st25_deinitialize,
        st25_read_id,
        st25_read_security_session,
        st25_present_password,
        st25_read_mailbox_mode,
        st25_read_mailbox_status,
        st25_set_mailbox_enabled,
        st25_reset_eh,
        st25_set_gpo1,
        st25_read_gpo2,
        st25_set_gpo2,
        st25_read_mailbox_length,
        st25_read_mailbox,
        st25_delay,
    };
    r1_st25dvxxkc_adapter adapter;
    r1_st25dvxxkc_adapter_initialize(&adapter);
    assert(!r1_st25dvxxkc_provider_available(&adapter));
    assert(r1_st25dvxxkc_activate(&adapter) == R1_ERROR_UNSUPPORTED);
    assert(r1_st25dvxxkc_mailbox_length_allowed(0u));
    assert(r1_st25dvxxkc_mailbox_length_allowed(20u));
    assert(!r1_st25dvxxkc_mailbox_length_allowed(21u));
    assert(!r1_st25dvxxkc_mailbox_length_allowed(255u));
    assert(!r1_st25dvxxkc_mailbox_length_allowed(256u));

    st25_trace trace = {0};
    trace.initialize_failures = 2u;
    trace.ic_reference = R1_ST25DVXXKC_ICREF_04KC;
    trace.gpo2 = UINT8_MAX;
    trace.mailbox_mode = true;
    trace.mailbox_status.rf_put_message = true;
    trace.mailbox_status.current_message = R1_ST25DVXXKC_MESSAGE_RF;
    for (size_t index = 0u; index < sizeof trace.mailbox; ++index) {
        trace.mailbox[index] = (uint8_t)(index + 1u);
    }
    assert(r1_st25dvxxkc_adapter_bind(&adapter, &provider, &trace) == R1_OK);
    assert(r1_st25dvxxkc_provider_available(&adapter));
    assert(r1_st25dvxxkc_activate(&adapter) == R1_OK);
    assert(adapter.initialized);
    assert(adapter.ic_reference == R1_ST25DVXXKC_ICREF_04KC);
    assert(trace.initialize_count == 3u);
    assert(trace.read_id_count == 1u);
    assert(trace.security_read_count == 4u);
    assert(trace.password_count == 2u);
    assert(trace.password_msb == R1_ST25DVXXKC_SESSION_CLOSE_MSB);
    assert(trace.password_lsb == R1_ST25DVXXKC_SESSION_CLOSE_LSB);
    assert(!trace.security_open);
    assert(trace.mailbox_enable_count == 2u);
    assert(trace.reset_eh_count == 1u);
    assert(trace.set_gpo1_count == 3u);
    assert(trace.gpo1 == R1_ST25DVXXKC_GPO1_CONFIGURATION);
    assert(trace.read_gpo2_count == 1u && trace.set_gpo2_count == 1u);
    assert(trace.gpo2 == 0xfcu);
    assert(trace.mailbox_status_count == 3u);
    assert(trace.delay_count == 6u);
    assert(trace.delayed_ticks == 6u * R1_ST25DVXXKC_SETTLE_TICKS);

    st25_frame_capture capture = {0};
    r1_st25dvxxkc_set_frame_callback(&adapter, capture_st25_frame, &capture);
    bool received = false;
    trace.encoded_length = 0u;
    assert(r1_st25dvxxkc_poll(&adapter, &received) == R1_OK && received);
    assert(trace.mailbox_read_length == 1u);
    assert(capture.calls == 1u && capture.length == 1u && capture.bytes[0] == 1u);

    trace.encoded_length = 19u;
    received = false;
    assert(r1_st25dvxxkc_poll(&adapter, &received) == R1_OK && received);
    assert(trace.mailbox_read_length == R1_ST25DVXXKC_MAILBOX_CAPACITY);
    assert(capture.calls == 2u &&
           capture.length == R1_ST25DVXXKC_MAILBOX_CAPACITY);
    const size_t reads_before_rejection = trace.mailbox_read_count;
    trace.encoded_length = 20u;
    received = true;
    assert(r1_st25dvxxkc_poll(&adapter, &received) == R1_ERROR_LENGTH);
    assert(!received && trace.mailbox_read_count == reads_before_rejection);
    trace.encoded_length = UINT8_MAX;
    assert(r1_st25dvxxkc_poll(&adapter, &received) == R1_ERROR_LENGTH);
    assert(trace.mailbox_read_count == reads_before_rejection);
    assert(adapter.accepted_frames == 2u && adapter.rejected_lengths == 2u);

    r1_st25dvxxkc_deactivate(&adapter);
    assert(!adapter.initialized && trace.deinitialize_count == 1u);
}

static void test_st25dvxxkc_dock_policy(void) {
    r1_st25dvxxkc_dock_state state;
    r1_st25dvxxkc_dock_state_initialize(&state);
    assert(!state.field_seen && state.heartbeat_count == 0u);
    assert(state.dock_version[0] == '\0');
    r1_st25dvxxkc_dock_state_initialize(NULL);

    const uint8_t short_identity[] = {1u, 2u, 3u, 4u, 0u, 226u, 0u, 9u};
    const uint8_t identity[] = {1u, 2u, 3u, 4u, 0u, 226u, 0u, 9u, 7u};
    assert(!r1_st25dvxxkc_is_dock_identity_frame(NULL, 0u));
    assert(!r1_st25dvxxkc_is_dock_identity_frame(
        short_identity, sizeof short_identity));
    assert(r1_st25dvxxkc_is_dock_identity_frame(identity, sizeof identity));

    uint8_t packet[R1_ST25DVXXKC_DOCK_CONTROL_PACKET_SIZE] = {0};
    r1_st25dvxxkc_dock_action action =
        R1_ST25DVXXKC_DOCK_ACTION_SEND_CONTROL_PACKET;
    assert(r1_st25dvxxkc_plan_dock_frame(
               NULL, identity, sizeof identity,
               R1_ST25DVXXKC_DOCK_MAILBOX_READY, packet, sizeof packet,
               &action) == R1_ERROR_ARGUMENT);
    assert(r1_st25dvxxkc_plan_dock_frame(
               &state, identity, sizeof identity,
               R1_ST25DVXXKC_DOCK_MAILBOX_READY, packet,
               R1_ST25DVXXKC_DOCK_CONTROL_PACKET_SIZE - 1u,
               &action) == R1_ERROR_LENGTH);
    assert(!state.field_seen && state.heartbeat_count == 0u);

    assert(r1_st25dvxxkc_plan_dock_frame(
               &state, identity, sizeof identity, 0u, packet, sizeof packet,
               &action) == R1_OK);
    assert(action == R1_ST25DVXXKC_DOCK_ACTION_NONE);
    assert(state.field_seen && state.heartbeat_count == 1u);
    assert(state.dock_accessory == 7u);
    assert(strcmp(state.dock_version, "2.2.6.0009") == 0);

    assert(r1_st25dvxxkc_plan_dock_frame(
               &state, identity, sizeof identity,
               R1_ST25DVXXKC_DOCK_MAILBOX_READY, packet, sizeof packet,
               &action) == R1_OK);
    assert(action == R1_ST25DVXXKC_DOCK_ACTION_SEND_CONTROL_PACKET);
    assert(packet[1] == 0x55u && packet[2] == 3u && packet[3] == 0u);
    assert(state.advertisement_marker == R1_ST25DVXXKC_DOCK_ADVERTISED);

    packet[6] = 43u;
    assert(r1_st25dvxxkc_plan_dock_frame(
               &state, identity, sizeof identity,
               R1_ST25DVXXKC_DOCK_MAILBOX_READY, packet, sizeof packet,
               &action) == R1_OK);
    assert(action == R1_ST25DVXXKC_DOCK_ACTION_SEND_CONTROL_PACKET);
    assert(state.cached_field_delay == 43u && packet[6] == 43u);
    packet[6] = R1_ST25DVXXKC_DOCK_DELAY_THRESHOLD;
    assert(r1_st25dvxxkc_plan_dock_frame(
               &state, identity, sizeof identity,
               R1_ST25DVXXKC_DOCK_MAILBOX_READY, packet, sizeof packet,
               &action) == R1_OK);
    assert(packet[6] == 43u);

    state.heartbeat_count = R1_ST25DVXXKC_DOCK_HEARTBEAT_LIMIT;
    state.adc_reference = 9u;
    packet[0] = 0xa5u;
    packet[4] = 40u;
    assert(r1_st25dvxxkc_plan_dock_frame(
               &state, identity, sizeof identity,
               R1_ST25DVXXKC_DOCK_MAILBOX_READY, packet, sizeof packet,
               &action) == R1_OK);
    assert(state.heartbeat_count == 0u);
    assert(packet[0] == 0xa5u && packet[1] == 0x55u && packet[2] == 4u &&
           packet[3] == 0u && packet[4] == R1_ST25DVXXKC_DOCK_DELAY_LONG);

    state.heartbeat_count = R1_ST25DVXXKC_DOCK_HEARTBEAT_LIMIT;
    state.adc_reference = 10u;
    packet[4] = 40u;
    assert(r1_st25dvxxkc_plan_dock_frame(
               &state, identity, sizeof identity,
               R1_ST25DVXXKC_DOCK_MAILBOX_READY, packet, sizeof packet,
               &action) == R1_OK);
    assert(packet[4] == R1_ST25DVXXKC_DOCK_DELAY_SHORT);

    state.heartbeat_count = UINT8_MAX;
    packet[6] = 12u;
    assert(r1_st25dvxxkc_plan_dock_frame(
               &state, identity, sizeof identity,
               R1_ST25DVXXKC_DOCK_MAILBOX_READY, packet, sizeof packet,
               &action) == R1_OK);
    assert(state.heartbeat_count == 0u && state.cached_field_delay == 12u);

    const uint8_t large_build[] =
        {1u, 2u, 3u, 4u, 0x03u, 0xe7u, 0xffu, 0xffu, 8u};
    assert(r1_st25dvxxkc_plan_dock_frame(
               &state, large_build, sizeof large_build, 0u, packet,
               sizeof packet, &action) == R1_OK);
    assert(strcmp(state.dock_version, "9.9.9.6553") == 0);

    const uint8_t adv_control[] = {0x55u, 3u};
    assert(r1_st25dvxxkc_plan_dock_frame(
               &state, adv_control, sizeof adv_control, 0u, NULL, 0u,
               &action) == R1_OK);
    assert(action == R1_ST25DVXXKC_DOCK_ACTION_NONE);
    const uint8_t charge_control[] = {0x55u, 4u};
    assert(r1_st25dvxxkc_plan_dock_frame(
               &state, charge_control, sizeof charge_control, 0u, NULL, 0u,
               &action) == R1_OK);
    assert(action == R1_ST25DVXXKC_DOCK_ACTION_SCHEDULE_CHARGE_FIELD);
    assert(R1_ST25DVXXKC_CHARGE_FIELD_DELAY_TICKS == UINT32_C(0x800));
}

typedef struct {
    size_t enable_calls;
    size_t disable_calls;
    bool enabled;
    bool fail_next;
} power_trace;

static bool set_shared_power_enabled(void *context, bool enabled) {
    power_trace *trace = context;
    if (enabled) {
        ++trace->enable_calls;
    } else {
        ++trace->disable_calls;
    }
    if (trace->fail_next) {
        trace->fail_next = false;
        return false;
    }
    trace->enabled = enabled;
    return true;
}

static void test_shared_power_lease(void) {
    static const r1_power_provider_ops provider = {
        set_shared_power_enabled,
    };
    r1_power_lease lease;
    r1_power_lease_initialize(&lease);
    assert(!r1_power_lease_provider_available(&lease));
    assert(r1_power_lease_active_mask(&lease) == 0u);
    assert(r1_power_lease_acquire(
               &lease, R1_POWER_CLIENT_BATTERY_SAMPLING) ==
           R1_ERROR_UNSUPPORTED);
    assert(r1_power_lease_acquire(
               &lease, (r1_power_client)R1_POWER_LEASE_CLIENT_COUNT) ==
           R1_ERROR_ARGUMENT);

    power_trace trace = {0};
    assert(r1_power_lease_bind(&lease, &provider, &trace) == R1_OK);
    assert(r1_power_lease_provider_available(&lease));
    trace.fail_next = true;
    assert(r1_power_lease_acquire(
               &lease, R1_POWER_CLIENT_BATTERY_SAMPLING) == R1_ERROR_STATE);
    assert(r1_power_lease_active_mask(&lease) == 0u && !trace.enabled);
    assert(trace.enable_calls == 1u);

    assert(r1_power_lease_acquire(
               &lease, R1_POWER_CLIENT_BATTERY_SAMPLING) == R1_OK);
    assert(trace.enabled && trace.enable_calls == 2u);
    assert(r1_power_lease_active_mask(&lease) == UINT8_C(0x01));
    assert(r1_power_lease_acquire(
               &lease, R1_POWER_CLIENT_BATTERY_SAMPLING) == R1_OK);
    assert(trace.enable_calls == 2u);
    assert(r1_power_lease_acquire(
               &lease, R1_POWER_CLIENT_OPTICAL_PPG) == R1_OK);
    assert(r1_power_lease_acquire(&lease, R1_POWER_CLIENT_TOUCH) == R1_OK);
    assert(r1_power_lease_active_mask(&lease) ==
           R1_POWER_LEASE_VALID_MASK);
    assert(trace.enable_calls == 2u);

    assert(r1_power_lease_release(
               &lease, R1_POWER_CLIENT_BATTERY_SAMPLING) == R1_OK);
    assert(r1_power_lease_release(
               &lease, R1_POWER_CLIENT_OPTICAL_PPG) == R1_OK);
    assert(trace.disable_calls == 0u && trace.enabled);
    trace.fail_next = true;
    assert(r1_power_lease_release(
               &lease, R1_POWER_CLIENT_TOUCH) == R1_ERROR_STATE);
    assert(r1_power_lease_is_active(&lease, R1_POWER_CLIENT_TOUCH));
    assert(r1_power_lease_active_mask(&lease) == UINT8_C(0x04));
    assert(trace.enabled && trace.disable_calls == 1u);
    assert(r1_power_lease_release(
               &lease, R1_POWER_CLIENT_TOUCH) == R1_OK);
    assert(r1_power_lease_active_mask(&lease) == 0u);
    assert(!trace.enabled && trace.disable_calls == 2u);
    assert(r1_power_lease_release(
               &lease, R1_POWER_CLIENT_TOUCH) == R1_OK);
    assert(trace.disable_calls == 2u);
}

typedef struct {
    uint8_t chip_id;
    size_t probe_calls;
    size_t configure_calls;
    size_t fifo_calls;
    size_t double_tap_calls;
    uint16_t configured_rate_hz;
    size_t reported_samples;
    uint8_t raw[R1_MOTION_FIFO_SAMPLE_LIMIT * R1_MOTION_SAMPLE_BYTES];
    r1_error probe_error;
    r1_error configure_error;
    r1_error fifo_error;
} motion_trace;

static r1_error motion_probe(void *context, uint8_t *chip_id) {
    motion_trace *trace = context;
    ++trace->probe_calls;
    if (trace->probe_error == R1_OK) {
        *chip_id = trace->chip_id;
    }
    return trace->probe_error;
}

static r1_error motion_configure(void *context, uint16_t rate_hz) {
    motion_trace *trace = context;
    ++trace->configure_calls;
    trace->configured_rate_hz = rate_hz;
    return trace->configure_error;
}

static r1_error motion_read_fifo(void *context, uint8_t *raw_samples,
                                 size_t maximum_samples,
                                 size_t *sample_count) {
    motion_trace *trace = context;
    ++trace->fifo_calls;
    if (trace->fifo_error != R1_OK) {
        return trace->fifo_error;
    }
    const size_t copy_count = trace->reported_samples < maximum_samples
        ? trace->reported_samples : maximum_samples;
    memcpy(raw_samples, trace->raw,
           copy_count * R1_MOTION_SAMPLE_BYTES);
    *sample_count = trace->reported_samples;
    return R1_OK;
}

static r1_error motion_disable_double_tap(void *context) {
    motion_trace *trace = context;
    ++trace->double_tap_calls;
    return R1_OK;
}

static void test_motion_provider_boundary(void) {
    static const r1_motion_provider_ops provider = {
        motion_probe,
        motion_configure,
        motion_read_fifo,
        motion_disable_double_tap,
    };
    r1_motion_adapter adapter;
    r1_motion_adapter_initialize(&adapter);
    assert(r1_motion_adapter_selected(&adapter) == R1_MOTION_VARIANT_NONE);
    assert(r1_motion_adapter_configure(
               &adapter, R1_MOTION_POLICY_DISABLED, 25u) ==
           R1_ERROR_UNSUPPORTED);
    assert(r1_motion_adapter_bind(
               &adapter, R1_MOTION_VARIANT_NONE, &provider, NULL) ==
           R1_ERROR_ARGUMENT);

    motion_trace lis = {.chip_id = R1_MOTION_LIS2DW12_CHIP_ID};
    motion_trace bma = {.chip_id = R1_MOTION_BMA456W_CHIP_ID};
    assert(r1_motion_adapter_bind(
               &adapter, R1_MOTION_VARIANT_LIS2DW12, &provider, &lis) == R1_OK);
    assert(r1_motion_adapter_bind(
               &adapter, R1_MOTION_VARIANT_BMA456W, &provider, &bma) == R1_OK);
    assert(r1_motion_adapter_configure(
               &adapter, R1_MOTION_POLICY_AUTO_LICENSED, 100u) == R1_OK);
    assert(r1_motion_adapter_selected(&adapter) ==
           R1_MOTION_VARIANT_LIS2DW12);
    assert(lis.probe_calls == 1u && lis.configure_calls == 1u);
    assert(lis.configured_rate_hz == 100u && bma.probe_calls == 0u);
    assert(r1_motion_adapter_disable_double_tap(&adapter) == R1_OK);
    assert(lis.double_tap_calls == 1u);

    static const uint8_t raw[] = {
        0x07u,0x00u, 0xf9u,0xffu, 0x00u,0x10u,
        0xffu,0xffu, 0x01u,0x00u, 0x00u,0xf0u,
    };
    memcpy(lis.raw, raw, sizeof raw);
    lis.reported_samples = 2u;
    r1_motion_sample samples[2];
    size_t count = 0u;
    assert(r1_motion_adapter_read_fifo(
               &adapter, samples, 2u, &count) == R1_OK);
    assert(count == 2u && lis.fifo_calls == 1u);
    assert(samples[0].x == 1 && samples[0].y == -2 && samples[0].z == 1024);
    assert(samples[1].x == -1 && samples[1].y == 0 && samples[1].z == -1024);
    assert(r1_motion_normalize_axis(INT16_MIN) == -8192);
    assert(r1_motion_normalize_axis(INT16_MAX) == 8191);
    lis.reported_samples = 3u;
    assert(r1_motion_adapter_read_fifo(
               &adapter, samples, 2u, &count) == R1_ERROR_CAPACITY);
    assert(count == 0u);

    r1_motion_adapter_initialize(&adapter);
    lis = (motion_trace){.chip_id = 0u};
    bma = (motion_trace){.chip_id = R1_MOTION_BMA456W_CHIP_ID};
    assert(r1_motion_adapter_bind(
               &adapter, R1_MOTION_VARIANT_LIS2DW12, &provider, &lis) == R1_OK);
    assert(r1_motion_adapter_bind(
               &adapter, R1_MOTION_VARIANT_BMA456W, &provider, &bma) == R1_OK);
    assert(r1_motion_adapter_configure(
               &adapter, R1_MOTION_POLICY_AUTO_LICENSED, 25u) == R1_OK);
    assert(lis.probe_calls == 1u && bma.probe_calls == 1u);
    assert(r1_motion_adapter_selected(&adapter) ==
           R1_MOTION_VARIANT_BMA456W);

    r1_motion_adapter_initialize(&adapter);
    lis = (motion_trace){.chip_id = 0u};
    assert(r1_motion_adapter_bind(
               &adapter, R1_MOTION_VARIANT_LIS2DW12, &provider, &lis) == R1_OK);
    assert(r1_motion_adapter_configure(
               &adapter, R1_MOTION_POLICY_FORCE_LIS2DW12, 25u) ==
           R1_ERROR_UNSUPPORTED);
    assert(r1_motion_adapter_selected(&adapter) == R1_MOTION_VARIANT_NONE);
}

static void test_wear_fusion(void) {
    r1_motion_sample samples[R1_WEAR_MINIMUM_MOTION_SAMPLES];
    for (size_t index = 0u; index < R1_WEAR_MINIMUM_MOTION_SAMPLES;
         ++index) {
        samples[index].x = (int16_t)index;
        samples[index].y = 1024;
        samples[index].z = -1024;
    }
    r1_wear_motion_statistics statistics;
    assert(r1_wear_motion_statistics_compute(
               samples, R1_WEAR_MINIMUM_MOTION_SAMPLES - 1u,
               &statistics) == R1_ERROR_ARGUMENT);
    assert(r1_wear_motion_statistics_compute(
               samples, R1_WEAR_MINIMUM_MOTION_SAMPLES,
               &statistics) == R1_OK);
    assert(statistics.mean_x == 4.5f);
    assert(statistics.mean_y == 1024.0f);
    assert(statistics.mean_z == -1024.0f);
    assert(statistics.variance_x == 8.25f);
    assert(statistics.variance_y == 0.0f);
    assert(statistics.variance_z == 0.0f);

    const uint32_t history[] = {
        UINT32_C(9000000), UINT32_C(9050000), UINT32_C(9100000),
    };
    uint32_t optical_range = 0u;
    assert(r1_wear_optical_range(history, 3u, false, 0u,
                                 &optical_range) == R1_OK);
    assert(optical_range == UINT32_C(100000));
    assert(r1_wear_optical_range(history, 3u, true, UINT32_C(8800000),
                                 &optical_range) == R1_OK);
    assert(optical_range == UINT32_C(300000));
    assert(r1_wear_optical_range(NULL, 0u, false, 0u,
                                 &optical_range) == R1_ERROR_ARGUMENT);

    r1_wear_fusion fusion;
    r1_wear_fusion_initialize(&fusion);
    r1_wear_motion_statistics motion = {0};
    r1_wear_on_observation on = {
        .optical_history_available = false,
        .motion = &motion,
    };
    motion.variance_x = 2000.0f;
    assert(r1_wear_fusion_observe_on(&fusion, &on) ==
           R1_WEAR_ACTION_NONE);
    motion.variance_x = 2000.01f;
    assert(r1_wear_fusion_observe_on(&fusion, &on) ==
           R1_WEAR_ACTION_STATE_CHANGED);
    assert(fusion.state == R1_WEAR_FUSION_SUSPECTED_WORN);

    r1_wear_fusion_initialize(&fusion);
    on = (r1_wear_on_observation){
        .optical_history_available = true,
        .optical_baseline_available = false,
        .optical_latest = R1_WEAR_IR_THRESHOLD,
    };
    assert(r1_wear_fusion_observe_on(&fusion, &on) ==
           R1_WEAR_ACTION_NONE);
    on.optical_latest = R1_WEAR_IR_THRESHOLD + 1u;
    assert(r1_wear_fusion_observe_on(&fusion, &on) ==
           R1_WEAR_ACTION_STATE_CHANGED);

    r1_wear_fusion_initialize(&fusion);
    on.optical_baseline_available = true;
    on.optical_range = R1_WEAR_IR_RANGE_MINIMUM - 1u;
    assert(r1_wear_fusion_observe_on(&fusion, &on) ==
           R1_WEAR_ACTION_NONE);
    on.optical_range = R1_WEAR_IR_RANGE_MINIMUM;
    assert(r1_wear_fusion_observe_on(&fusion, &on) ==
           R1_WEAR_ACTION_STATE_CHANGED);

    r1_wear_off_observation off = {
        .current_tick = R1_WEAR_LIVING_WINDOW_TICKS,
        .living_tick = 0u,
        .living_status = 1u,
    };
    assert(r1_wear_fusion_observe_off(&fusion, &off) ==
           (R1_WEAR_ACTION_STOP_LIVING_PROBE |
            R1_WEAR_ACTION_STATE_CHANGED));
    assert(fusion.state == R1_WEAR_FUSION_LIVING_CONFIRMED);
    assert(r1_wear_fusion_is_confirmed(&fusion));

    fusion.state = R1_WEAR_FUSION_SUSPECTED_WORN;
    off.living_status = 0u;
    assert(r1_wear_fusion_observe_off(&fusion, &off) ==
           (R1_WEAR_ACTION_STOP_LIVING_PROBE |
            R1_WEAR_ACTION_STATE_CHANGED));
    assert(fusion.state == R1_WEAR_FUSION_NOT_WORN);

    fusion.state = R1_WEAR_FUSION_SUSPECTED_WORN;
    off = (r1_wear_off_observation){
        .current_tick = R1_WEAR_LIVING_WINDOW_TICKS + 1u,
        .living_tick = 0u,
        .optical_history_available = true,
        .optical_latest = R1_WEAR_IR_THRESHOLD - 1u,
    };
    for (uint8_t decision = 1u; decision < R1_WEAR_LOW_IR_DECISIONS;
         ++decision) {
        assert(r1_wear_fusion_observe_off(&fusion, &off) ==
               R1_WEAR_ACTION_START_LIVING_PROBE);
        assert(fusion.state == R1_WEAR_FUSION_SUSPECTED_WORN);
        assert(fusion.low_ir_decisions == decision);
    }
    assert(r1_wear_fusion_observe_off(&fusion, &off) ==
           (R1_WEAR_ACTION_STOP_LIVING_PROBE |
            R1_WEAR_ACTION_STATE_CHANGED));
    assert(fusion.state == R1_WEAR_FUSION_NOT_WORN);

    fusion.state = R1_WEAR_FUSION_SUSPECTED_WORN;
    fusion.low_ir_decisions = R1_WEAR_LOW_IR_DECISIONS - 1u;
    off.sleep_status = 1u;
    assert(r1_wear_fusion_observe_off(&fusion, &off) ==
           R1_WEAR_ACTION_START_LIVING_PROBE);
    assert(fusion.state == R1_WEAR_FUSION_SUSPECTED_WORN);
    assert(fusion.low_ir_decisions == 0u);

    fusion.stationary_decisions = 0u;
    motion = (r1_wear_motion_statistics){.mean_y = 1024.0f};
    off.sleep_status = 0u;
    off.optical_history_available = false;
    off.motion = &motion;
    for (uint8_t decision = 1u; decision < R1_WEAR_STATIONARY_DECISIONS;
         ++decision) {
        assert(r1_wear_fusion_observe_off(&fusion, &off) ==
               R1_WEAR_ACTION_START_LIVING_PROBE);
        assert(fusion.stationary_decisions == decision);
    }
    assert(r1_wear_fusion_observe_off(&fusion, &off) ==
           (R1_WEAR_ACTION_STOP_LIVING_PROBE |
            R1_WEAR_ACTION_STATE_CHANGED));
    assert(fusion.state == R1_WEAR_FUSION_NOT_WORN);

    fusion.state = R1_WEAR_FUSION_SUSPECTED_WORN;
    motion.mean_y = 972.0f;
    assert(r1_wear_fusion_observe_off(&fusion, &off) ==
           R1_WEAR_ACTION_START_LIVING_PROBE);
    assert(fusion.stationary_decisions == 0u);
    motion.mean_y = -1024.0f;
    motion.variance_x = 40.0f;
    assert(r1_wear_fusion_observe_off(&fusion, &off) ==
           R1_WEAR_ACTION_START_LIVING_PROBE);
    assert(fusion.stationary_decisions == 0u);

    assert(r1_wear_notification_state(R1_WEAR_FUSION_NOT_WORN) ==
           R1_WEAR_NOT_WORN);
    assert(r1_wear_notification_state(R1_WEAR_FUSION_SUSPECTED_WORN) ==
           R1_WEAR_WORN);
    assert(r1_wear_notification_state(R1_WEAR_FUSION_LIVING_CONFIRMED) ==
           R1_WEAR_WORN);
    assert(r1_wear_explicit_query_state(R1_WEAR_FUSION_NOT_WORN) ==
           R1_WEAR_NOT_WORN);
    assert(r1_wear_explicit_query_state(R1_WEAR_FUSION_SUSPECTED_WORN) ==
           R1_WEAR_WORN);
    assert(r1_wear_explicit_query_state(
               R1_WEAR_FUSION_LIVING_CONFIRMED) == R1_WEAR_UNKNOWN);
}

static void test_connection_parameter_policy(void) {
    r1_connection_parameter_policy policy;
    r1_connection_parameter_policy_initialize(&policy);
    assert(policy.initial_parameter_status == UINT8_MAX);

    r1_connection_parameters parameters = {
        .minimum_interval = 24u,
        .maximum_interval = R1_CONNECTION_FAST_MAX_INTERVAL,
        .peripheral_latency = 0u,
        .supervision_timeout = 400u,
    };
    assert(r1_connection_parameters_speed(&parameters) ==
           R1_CONNECTION_SPEED_SLOW);
    parameters.maximum_interval = R1_CONNECTION_FAST_MAX_INTERVAL - 1u;
    assert(r1_connection_parameters_speed(&parameters) ==
           R1_CONNECTION_SPEED_FAST);

    r1_connection_parameters_connected(&policy, false, &parameters);
    assert(policy.requested_speed == R1_CONNECTION_SPEED_SLOW);
    parameters.minimum_interval = 39u;
    parameters.maximum_interval = 39u;
    r1_connection_parameters_connected(&policy, true, &parameters);
    assert(policy.requested_speed == R1_CONNECTION_SPEED_FAST);
    assert(policy.phone_speed == R1_CONNECTION_SPEED_FAST);
    assert(policy.glasses_speed == R1_CONNECTION_SPEED_FAST);
    assert(policy.initial_parameter_status == 1u);

    policy.initial_parameter_status = 7u;
    parameters.minimum_interval = 36u;
    parameters.maximum_interval = 36u;
    r1_connection_parameters_connected(&policy, true, &parameters);
    assert(policy.initial_parameter_status == 7u);
    parameters.minimum_interval = 38u;
    parameters.maximum_interval = 38u;
    policy.initial_parameter_status = UINT8_MAX;
    r1_connection_parameters_connected(&policy, true, &parameters);
    assert(policy.initial_parameter_status == UINT8_MAX);

    const uint16_t phone = 3u;
    const uint16_t glasses = 7u;
    policy.requested_speed = R1_CONNECTION_SPEED_FAST;
    policy.phone_speed = R1_CONNECTION_SPEED_SLOW;
    policy.glasses_speed = R1_CONNECTION_SPEED_SLOW;
    parameters.maximum_interval = 49u;
    r1_connection_parameter_action action =
        r1_connection_parameters_updated(
            &policy, glasses, phone, glasses, &parameters);
    assert(action.type == R1_CONNECTION_PARAMETER_ACTION_NONE);
    assert(policy.glasses_speed == R1_CONNECTION_SPEED_FAST);
    assert(policy.phone_speed == R1_CONNECTION_SPEED_SLOW);

    parameters.maximum_interval = 50u;
    action = r1_connection_parameters_updated(
        &policy, phone, phone, glasses, &parameters);
    assert(action.type == R1_CONNECTION_PARAMETER_ACTION_SCHEDULE_RETRY);
    assert(action.requested_speed == R1_CONNECTION_SPEED_FAST);
    assert(action.delay_ms == R1_CONNECTION_RETRY_AFTER_SLOW_MS);
    assert(policy.phone_speed == R1_CONNECTION_SPEED_SLOW);

    policy.requested_speed = R1_CONNECTION_SPEED_SLOW;
    parameters.maximum_interval = 49u;
    action = r1_connection_parameters_updated(
        &policy, phone, phone, glasses, &parameters);
    assert(action.type == R1_CONNECTION_PARAMETER_ACTION_SCHEDULE_RETRY);
    assert(action.requested_speed == R1_CONNECTION_SPEED_SLOW);
    assert(action.delay_ms == R1_CONNECTION_RETRY_AFTER_FAST_MS);

    action = r1_connection_parameters_disconnected();
    assert(action.type == R1_CONNECTION_PARAMETER_ACTION_CANCEL_RETRY);
    assert(action.delay_ms == 0u);
}

static void test_connection_role_assignment(void) {
    r1_connection_role_handles handles = {
        R1_CONNECTION_HANDLE_INVALID, R1_CONNECTION_HANDLE_INVALID,
    };
    r1_connection_role_assign_result result = r1_connection_role_assign(
        &handles, R1_CONNECTION_ROLE_PHONE, 7u);
    assert(result.status == R1_CONNECTION_ROLE_ASSIGN_ASSIGNED);
    assert(result.publish_role && result.published_role == R1_CONNECTION_ROLE_PHONE);
    assert(handles.phone == 7u && handles.glasses == R1_CONNECTION_HANDLE_INVALID);
    result = r1_connection_role_assign(&handles, R1_CONNECTION_ROLE_PHONE, 7u);
    assert(result.status == R1_CONNECTION_ROLE_ASSIGN_ALREADY_SAME);
    result = r1_connection_role_assign(&handles, R1_CONNECTION_ROLE_PHONE, 8u);
    assert(result.status == R1_CONNECTION_ROLE_ASSIGN_OCCUPIED);
    result = r1_connection_role_assign(&handles, R1_CONNECTION_ROLE_GLASSES, 7u);
    assert(result.status == R1_CONNECTION_ROLE_ASSIGN_CROSS_ROLE_CONFLICT);
    result = r1_connection_role_assign(
        &handles, R1_CONNECTION_ROLE_GLASSES, R1_CONNECTION_HANDLE_INVALID);
    assert(result.status == R1_CONNECTION_ROLE_ASSIGN_INVALID);
    result = r1_connection_role_assign(NULL, R1_CONNECTION_ROLE_PHONE, 1u);
    assert(result.status == R1_CONNECTION_ROLE_ASSIGN_INVALID);
}

static void test_peer_target_policy(void) {
    const uint8_t zero[R1_PEER_ADDRESS_SIZE] = {0};
    const uint8_t erased[R1_PEER_ADDRESS_SIZE] = {
        UINT8_MAX, UINT8_MAX, UINT8_MAX, UINT8_MAX, UINT8_MAX, UINT8_MAX,
    };
    const uint8_t right[R1_PEER_ADDRESS_SIZE] = {1u, 2u, 3u, 4u, 5u, 6u};
    const uint8_t left[R1_PEER_ADDRESS_SIZE] = {7u, 8u, 9u, 10u, 11u, 12u};
    const uint8_t other[R1_PEER_ADDRESS_SIZE] = {1u, 1u, 1u, 1u, 1u, 1u};
    assert(!r1_peer_target_address_valid(NULL));
    assert(!r1_peer_target_address_valid(zero));
    assert(!r1_peer_target_address_valid(erased));
    assert(r1_peer_target_address_valid(right));

    uint8_t slots[R1_PEER_SLOT_COUNT * R1_PEER_SLOT_SIZE] = {0};
    slots[0] = 1u;
    memcpy(&slots[1], right, R1_PEER_ADDRESS_SIZE);
    slots[2u * R1_PEER_SLOT_SIZE] = 2u;
    memcpy(&slots[2u * R1_PEER_SLOT_SIZE + 1u], left,
           R1_PEER_ADDRESS_SIZE);
    uint8_t peer[R1_PEER_ADDRESS_SIZE] = {0};
    assert(!r1_peer_address_from_slots(NULL, R1_PEER_SLOT_COUNT, 0u, peer));
    assert(!r1_peer_address_from_slots(slots, R1_PEER_SLOT_COUNT, 0u, NULL));
    assert(r1_peer_address_from_slots(
        slots, R1_PEER_SLOT_COUNT, 0u, peer));
    assert(memcmp(peer, right, R1_PEER_ADDRESS_SIZE) == 0);
    assert(r1_peer_address_from_slots(
        slots, R1_PEER_SLOT_COUNT, 2u, peer));
    assert(memcmp(peer, left, R1_PEER_ADDRESS_SIZE) == 0);
    assert(!r1_peer_address_from_slots(
        slots, R1_PEER_SLOT_COUNT, R1_PEER_SLOT_COUNT, peer));
    assert(!r1_peer_address_from_slots(slots, 1u, 2u, peer));

    assert(r1_peer_is_target_glasses(false, NULL, zero, erased));
    assert(r1_peer_is_target_glasses(false, NULL, right, left));
    assert(r1_peer_is_target_glasses(true, right, right, left));
    assert(r1_peer_is_target_glasses(true, left, right, left));
    assert(!r1_peer_is_target_glasses(true, other, right, left));
    assert(!r1_peer_is_target_glasses(true, other, zero, left));
}

static void test_next_frontier_product_policies(void) {
    static const uint8_t payload[] = {0xaau, 0xbbu, 0xccu, 0xddu, 0xeeu};
    uint8_t envelope[20u];
    size_t allocation_bytes = 0u;
    assert(r1_ble_thread_message_encode(
               UINT32_C(0x11223344), UINT32_C(0x55667788), payload,
               sizeof payload, envelope, sizeof envelope, &allocation_bytes) == R1_OK);
    assert(allocation_bytes == 20u);
    static const uint8_t expected_header[] = {
        0x44u, 0x33u, 0x22u, 0x11u, 0x88u, 0x77u, 0x66u, 0x55u,
        0x05u, 0x00u, 0x00u, 0x00u,
    };
    assert(memcmp(envelope, expected_header, sizeof expected_header) == 0);
    assert(memcmp(envelope + 12u, payload, sizeof payload) == 0);
    assert(envelope[17] == 0u && envelope[18] == 0u && envelope[19] == 0u);
    assert(r1_ble_thread_message_encode(
               0u, 0u, payload, sizeof payload, envelope, 19u,
               &allocation_bytes) == R1_ERROR_CAPACITY);

    const r1_algorithm_user_profile current = {
        30u, 0u, 175u, 70u, -1, -1, -1, 0u,
    };
    r1_algorithm_user_profile next = current;
    r1_user_profile_transition_plan profile_plan;
    assert(r1_user_profile_plan_transition(
               &current, &next, true, &profile_plan) == R1_OK);
    assert(profile_plan.valid && !profile_plan.changed && !profile_plan.persist);
    next.weight_kg = 80u;
    assert(r1_user_profile_plan_transition(
               &current, &next, true, &profile_plan) == R1_OK);
    assert(profile_plan.persist && profile_plan.significant_change &&
           profile_plan.reinitialize_provider);
    next = current;
    next.age_years = 32u;
    assert(r1_user_profile_plan_transition(
               &current, &next, true, &profile_plan) == R1_OK);
    assert(profile_plan.persist && !profile_plan.significant_change);
    next.binary_sex = 2u;
    assert(r1_user_profile_plan_transition(
               &current, &next, true, &profile_plan) == R1_OK);
    assert(!profile_plan.valid && !profile_plan.persist);

    assert(r1_peer_bond_diagnostic_plan(UINT16_MAX, 0) ==
           R1_BOND_DIAGNOSTIC_INVALID_PEER);
    assert(r1_peer_bond_diagnostic_plan(4u, 7) ==
           R1_BOND_DIAGNOSTIC_LOAD_FAILED);
    assert(r1_peer_bond_diagnostic_plan(4u, 0) ==
           R1_BOND_DIAGNOSTIC_REDACTED);

    r1_glasses_status_plan glasses_plan;
    assert(r1_glasses_status_plan_command(
               true, UINT8_C(0x80), false, false, false,
               &glasses_plan) == R1_OK);
    assert(glasses_plan.wear_changed && glasses_plan.open_touch);
    assert(glasses_plan.cancel_slow_event && glasses_plan.cancel_dcdc_event);
    assert(glasses_plan.disable_dcdc_now && !glasses_plan.schedule_slow_event);
    assert(glasses_plan.response_length == 7u);
    assert(r1_glasses_status_plan_command(
               true, 0u, true, true, false, &glasses_plan) == R1_OK);
    assert(glasses_plan.schedule_slow_event && glasses_plan.set_ble_slow_mode);
    assert(glasses_plan.slow_delay_ticks == R1_GLASSES_SLOW_DELAY_TICKS);
    assert(glasses_plan.schedule_dcdc_enable &&
           glasses_plan.dcdc_delay_ticks == R1_GLASSES_DCDC_DELAY_TICKS);
}

static void test_next_frontier_334_342_policies(void) {
    static const uint8_t payload[] = {0x10u, 0x20u, 0x30u};
    uint8_t factory_envelope[16u];
    size_t allocation_bytes = 0u;
    assert(r1_factory_thread_message_encode(
               UINT32_C(0x10203040), 1u, payload, sizeof payload,
               factory_envelope, sizeof factory_envelope,
               &allocation_bytes) == R1_OK);
    assert(allocation_bytes == 16u);
    static const uint8_t expected[] = {
        0x40u, 0x30u, 0x20u, 0x10u, 0x01u, 0x00u, 0x00u, 0x00u,
        0x03u, 0x00u, 0x00u, 0x00u, 0x10u, 0x20u, 0x30u, 0x00u,
    };
    assert(memcmp(factory_envelope, expected, sizeof expected) == 0);

    r1_peripheral_watchdog_plan plan;
    assert(r1_peripheral_watchdog_plan_step(
               0u, 2u, true, true, 0, 0, &plan) == R1_OK);
    assert(plan.next_counter == 1u && plan.report_link_count);
    assert(!plan.connection_invariant_violation &&
           !plan.start_advertising && plan.schedule_next_check);
    assert(plan.next_delay_ticks == R1_PERIPHERAL_WATCHDOG_DELAY_TICKS);

    assert(r1_peripheral_watchdog_plan_step(
               UINT8_C(0xfe), 1u, true, true, 0, 0, &plan) == R1_OK);
    assert(plan.next_counter == 0u && plan.connection_invariant_violation);
    assert(!plan.schedule_next_check && !plan.start_advertising);

    assert(r1_peripheral_watchdog_plan_step(
               59u, 0u, false, false, 0, 7, &plan) == R1_OK);
    assert(plan.next_counter == 60u && !plan.report_link_count);
    assert(plan.cancel_pending_restart && plan.start_advertising);
    assert(plan.report_advertising_start_failure && plan.schedule_next_check);
    assert(plan.advertising_mode == R1_ADVERTISING_MODE_DIRECTED_OR_FAST);

    assert(r1_peripheral_watchdog_plan_step(
               60u, 0u, false, false, 8, 0, &plan) == R1_OK);
    assert(plan.next_counter == 61u && plan.report_link_count);
    assert(!plan.cancel_pending_restart && !plan.start_advertising);
    assert(plan.schedule_next_check);
}

static void test_next_frontier_314_328_policies(void) {
    static const int32_t samples[R1_TEMPERATURE_PAIR_SENSOR_COUNT]
                                [R1_TEMPERATURE_PAIR_SAMPLE_COUNT] = {
        {100, 200, 300, 400, 500, 600, 700, 800, 900, 1000},
        {-1000, -900, -800, -700, -600,
         -500, -400, -300, -200, -100},
    };
    r1_temperature_pair_result temperatures;
    assert(r1_temperature_pair_reduce(samples, NULL, &temperatures) == R1_OK);
    assert(temperatures.sensor_count == R1_TEMPERATURE_PAIR_SENSOR_COUNT);
    assert(temperatures.channels[0] == 550);
    assert(temperatures.channels[1] == -550);

    const r1_temperature_pair_calibration calibration = {
        .channels = {
            {R1_TEMPERATURE_CALIBRATION_SUBTRACT, 25},
            {R1_TEMPERATURE_CALIBRATION_ADD, 50},
        },
    };
    assert(r1_temperature_pair_reduce(
               samples, &calibration, &temperatures) == R1_OK);
    assert(temperatures.channels[0] == 525);
    assert(temperatures.channels[1] == -500);
    assert(r1_temperature_pair_reduce(NULL, NULL, &temperatures) ==
           R1_ERROR_ARGUMENT);

    r1_activity_history activity;
    r1_health_u8_history heart_rate;
    r1_health_u8_history spo2;
    r1_health_u8_history temperature;
    r1_health_u8_history stress;
    r1_health_u16_history hrv;
    memset(&activity, 0xa5, sizeof activity);
    memset(&heart_rate, 0xa5, sizeof heart_rate);
    memset(&spo2, 0xa5, sizeof spo2);
    memset(&temperature, 0xa5, sizeof temperature);
    memset(&stress, 0xa5, sizeof stress);
    memset(&hrv, 0xa5, sizeof hrv);
    r1_health_clear_all_result clear;
    assert(r1_health_clear_all_caches(
               true, UINT32_C(123456), -360, &activity, &heart_rate,
               &spo2, &temperature, &stress, &hrv, &clear) == R1_OK);
    assert(clear.clear_timeseries_database && clear.clear_sleep_history);
    assert(clear.reset_algorithm_aggregate);
    assert(clear.cache_families_reset == R1_HEALTH_DAILY_CACHE_FAMILY_COUNT);
    assert(activity.local_day_start == UINT32_C(123456));
    assert(activity.utc_offset_minutes == -360);
    assert(activity.total_steps == 0 && activity.total_kilocalories == 0);
    assert(heart_rate.local_day_start == UINT32_C(123456));
    assert(heart_rate.utc_offset_minutes == -360);
    assert(hrv.local_day_start == UINT32_C(123456));
    assert(hrv.utc_offset_minutes == -360);
    for (size_t index = 0u; index < R1_HEALTH_HOURLY_SLOTS; ++index) {
        assert(heart_rate.slots[index].sample_count == 0u);
        assert(hrv.slots[index].sample_count == 0u);
    }
    assert(r1_health_clear_all_caches(
               false, 0u, 0, NULL, NULL, NULL, NULL, NULL, NULL,
               &clear) == R1_OK);
    assert(!clear.clear_timeseries_database && clear.clear_sleep_history);
    assert(clear.cache_families_reset == 0u);
}

static void test_next_frontier_280_308_policies(void) {
    uint8_t logical[R1_PB_LOGICAL_MAX];
    for (size_t index = 0u; index < sizeof logical; ++index) {
        logical[index] = (uint8_t)(index * 17u + 3u);
    }
    r1_pb_fragment_set pb;
    assert(r1_pb_fragment_message(2u, NULL, 0u, &pb) == R1_OK);
    assert(pb.count == 1u && pb.fragments[0].length == 6u);
    assert(pb.fragments[0].bytes[0] == 0u && pb.fragments[0].bytes[5] == 2u);
    for (size_t index = 1u; index < 5u; ++index) {
        assert(pb.fragments[0].bytes[index] == 0u);
    }
    assert(r1_pb_fragment_message(0xa5u, logical, 239u, &pb) == R1_OK);
    assert(pb.count == 2u);
    assert(pb.fragments[0].bytes[0] == 1u && pb.fragments[0].length == 244u);
    assert(pb.fragments[1].bytes[0] == 0u && pb.fragments[1].length == 7u);
    assert(pb.fragments[0].bytes[5] == 0xa5u && pb.fragments[1].bytes[5] == 0xa5u);
    for (size_t index = 0u; index < 238u; ++index) {
        assert(pb.fragments[0].bytes[6u + index] == logical[index]);
    }
    assert(pb.fragments[1].bytes[6] == logical[238]);
    assert(r1_pb_fragment_message(7u, logical, sizeof logical, &pb) == R1_OK);
    assert(pb.count == R1_PB_FRAGMENT_COUNT_MAX);
    assert(pb.fragments[0].bytes[0] == 17u);
    assert(pb.fragments[17].bytes[0] == 0u && pb.fragments[17].length == 56u);
    assert(r1_pb_fragment_message(
               0u, logical, R1_PB_LOGICAL_MAX + 1u, &pb) == R1_ERROR_LENGTH);
    assert(r1_pb_fragment_message(0u, NULL, 1u, &pb) == R1_ERROR_ARGUMENT);

    r1_delayed_event_state delayed = {0};
    delayed.last_timer_delay_milliseconds = 100u;
    delayed.last_timer_start_milliseconds = 1000u;
    delayed.slots[0] = (r1_delayed_event_slot){1u, 0x1111u, 100u};
    r1_delayed_event_schedule_result scheduled;
    assert(r1_delayed_event_schedule(
               &delayed, 2u, 0x2222u, 250u, 2048u, &scheduled) == R1_OK);
    assert(scheduled.action == R1_DELAYED_EVENT_SCHEDULED);
    assert(scheduled.slot_index == 1u && scheduled.elapsed_milliseconds == 1000u);
    assert(scheduled.worker_wakeup_requested && !scheduled.immediate_push_requested);
    assert(scheduled.timer_step.due_count == 1u);
    assert(scheduled.timer_step.due[0].event == 1u);
    assert(delayed.slots[1].event == 2u && delayed.slots[1].context == 0x2222u);
    assert(delayed.slots[1].remaining_milliseconds == 250u);
    assert(delayed.last_timer_delay_milliseconds == 250u);
    assert(delayed.last_timer_start_milliseconds == 2000u);
    assert(r1_delayed_event_schedule(
               &delayed, 3u, 0x3333u, 1u, 2048u, &scheduled) == R1_OK);
    assert(scheduled.action == R1_DELAYED_EVENT_IMMEDIATE);
    assert(scheduled.immediate_push_requested && !scheduled.worker_wakeup_requested);
    for (size_t index = 0u; index < R1_DELAYED_EVENT_CAPACITY; ++index) {
        delayed.slots[index].event = (uint32_t)(index + 1u);
    }
    assert(r1_delayed_event_schedule(
               &delayed, 99u, 0u, 10u, 2048u, &scheduled) == R1_ERROR_CAPACITY);
    assert(scheduled.action == R1_DELAYED_EVENT_TABLE_FULL);
    assert(r1_delayed_event_schedule(
               &delayed, 0u, 0u, 10u, 0u, &scheduled) == R1_ERROR_ARGUMENT);

    const r1_health_settings_record stored = {
        .timestamp_seconds = UINT32_C(100),
        .enabled = 0u,
        .reserved = {1u, 2u, 3u, 4u, 5u, 6u, 7u},
    };
    r1_health_settings_command_plan settings;
    assert(r1_health_settings_plan_command(
               false, &stored, NULL, 0u, &settings) == R1_OK);
    assert(!settings.write_command && settings.response_requested);
    assert(settings.response.timestamp_seconds == UINT32_C(100));
    assert(settings.response.enabled == 0u);
    for (size_t index = 0u; index < sizeof settings.response.reserved; ++index) {
        assert(settings.response.reserved[index] == 0u);
    }
    static const uint8_t enable[] = {
        0xc8u, 0x00u, 0x00u, 0x00u, 0x01u,
        0u, 0u, 0u, 0u, 0u, 0u, 0u,
    };
    assert(r1_health_settings_plan_command(
               true, &stored, enable, sizeof enable, &settings) == R1_OK);
    assert(settings.acknowledgement_precedes_effects);
    assert(settings.raw_transition_observed && settings.persistent_update_requested);
    assert(settings.private_event_publish_requested && settings.private_event_value == 1u);
    assert(settings.persistent_record.timestamp_seconds == UINT32_C(200));
    assert(settings.persistent_record.enabled == 1u);

    const r1_health_settings_record enabled = {
        .timestamp_seconds = UINT32_C(200), .enabled = 1u,
    };
    uint8_t noncanonical[12] = {0x2cu, 0x01u, 0u, 0u, 2u};
    assert(r1_health_settings_plan_command(
               true, &enabled, noncanonical, sizeof noncanonical,
               &settings) == R1_OK);
    assert(settings.raw_transition_observed && !settings.persistent_update_requested);
    assert(settings.private_event_publish_requested && settings.private_event_value == 2u);
    assert(settings.persistent_record.timestamp_seconds == UINT32_C(200));
    assert(settings.persistent_record.enabled == 1u);
    assert(r1_health_settings_plan_command(
               true, &enabled, noncanonical, 11u, &settings) == R1_ERROR_LENGTH);
}

static void test_next_frontier_264_274_policies(void) {
    r1_battery_diagnostic_cadence cadence =
        r1_battery_diagnostic_cadence_step(3u);
    assert(cadence.next_counter == 4u);
    assert(!cadence.status_log_requested && !cadence.compensation_log_requested);
    cadence = r1_battery_diagnostic_cadence_step(4u);
    assert(cadence.next_counter == 5u);
    assert(cadence.status_log_requested && !cadence.compensation_log_requested);
    cadence = r1_battery_diagnostic_cadence_step(28u);
    assert(cadence.next_counter == 29u);
    assert(!cadence.status_log_requested && !cadence.compensation_log_requested);
    cadence = r1_battery_diagnostic_cadence_step(29u);
    assert(cadence.next_counter == 0u);
    assert(cadence.status_log_requested && cadence.compensation_log_requested);
    cadence = r1_battery_diagnostic_cadence_step(UINT8_MAX);
    assert(cadence.next_counter == 0u);
    assert(cadence.status_log_requested && !cadence.compensation_log_requested);

    uint8_t records[R1_EP_PARTITION_BYTES];
    memset(records, 0xff, sizeof records);
    r1_ep_scan_result scan;
    assert(r1_ep_scan_cursor(records, sizeof records, &scan) == R1_OK);
    assert(scan.first_free_found && scan.first_free_index == 0u);
    assert(scan.write_cursor == 0u && !scan.all_records_have_magic);
    assert(!scan.latest_nonzero_timestamp_found);

    for (size_t index = 0u; index < R1_EP_RECORD_COUNT; ++index) {
        records[index * R1_EP_RECORD_BYTES] = R1_EP_RECORD_MAGIC;
        memset(records + index * R1_EP_RECORD_BYTES + 1u, 0,
               R1_EP_RECORD_BYTES - 1u);
    }
    assert(r1_ep_scan_cursor(records, sizeof records, &scan) == R1_OK);
    assert(scan.all_records_have_magic && !scan.first_free_found);
    assert(!scan.latest_nonzero_timestamp_found && scan.write_cursor == 1u);

    records[3u * R1_EP_RECORD_BYTES + 4u] = 7u;
    records[9u * R1_EP_RECORD_BYTES + 4u] = 7u;
    assert(r1_ep_scan_cursor(records, sizeof records, &scan) == R1_OK);
    assert(scan.latest_nonzero_timestamp_found && scan.latest_timestamp == 7u);
    assert(scan.latest_timestamp_index == 9u && scan.write_cursor == 10u);

    records[5u * R1_EP_RECORD_BYTES] = 0xffu;
    records[20u * R1_EP_RECORD_BYTES] = 0xffu;
    assert(r1_ep_scan_cursor(records, sizeof records, &scan) == R1_OK);
    assert(scan.first_free_found && scan.first_free_index == 5u);
    assert(scan.write_cursor == 5u && !scan.all_records_have_magic);
    assert(r1_ep_scan_cursor(records, sizeof records - 1u, &scan)
           == R1_ERROR_LENGTH);
    assert(r1_ep_scan_cursor(NULL, sizeof records, &scan) == R1_ERROR_ARGUMENT);
}

static void test_next_frontier_256_262_policies(void) {
    r1_system_settings_command_plan settings;
    assert(r1_system_settings_plan_command(
               false, true, NULL, 0u, &settings) == R1_OK);
    assert(settings.response_requested && settings.response[5] == 1u);
    for (size_t index = 0u; index < R1_SYSTEM_SETTINGS_BYTES; ++index) {
        if (index != 5u) {
            assert(settings.response[index] == 0u);
        }
    }
    uint8_t payload[R1_SYSTEM_SETTINGS_BYTES] = {0};
    payload[5] = 1u;
    assert(r1_system_settings_plan_command(
               true, false, payload, sizeof payload, &settings) == R1_OK);
    assert(settings.acknowledgement_precedes_effects && settings.payload_valid);
    assert(settings.normalized_enabled && settings.persistent_update_requested);
    assert(settings.regulator_update_requested);
    payload[4] = 1u;
    assert(r1_system_settings_plan_command(
               true, false, payload, sizeof payload, &settings) == R1_OK);
    assert(settings.acknowledgement_precedes_effects && !settings.payload_valid);
    assert(!settings.persistent_update_requested &&
           !settings.regulator_update_requested);
    assert(r1_system_settings_plan_command(
               true, false, payload, sizeof payload - 1u, &settings) ==
           R1_ERROR_LENGTH);

    r1_temperature_mode_transition_plan temperature;
    assert(r1_temperature_mode_plan_transition(
               0u, 0u, true, true, &temperature) == R1_OK);
    assert(!temperature.changed && !temperature.unregister_previous_stream);
    assert(r1_temperature_mode_plan_transition(
               0u, 1u, true, false, &temperature) == R1_OK);
    assert(temperature.changed && temperature.unregister_previous_stream);
    assert(temperature.create_timed_mode && !temperature.stop_timed_mode);
    assert(temperature.timed_mode_period == R1_TEMPERATURE_TIMED_MODE_PERIOD);
    assert(r1_temperature_mode_plan_transition(
               1u, 2u, false, true, &temperature) == R1_OK);
    assert(temperature.changed && temperature.stop_timed_mode);
    assert(!temperature.create_timed_mode);
    assert(r1_temperature_mode_plan_transition(
               3u, 0u, false, false, &temperature) == R1_ERROR_ARGUMENT);

    assert(r1_goodix_diagnostic_refresh_due(1u, 0u));
    assert(!r1_goodix_diagnostic_refresh_due(599u, 100u));
    assert(r1_goodix_diagnostic_refresh_due(600u, 100u));
    uint8_t snapshot[R1_GOODIX_DIAGNOSTIC_SNAPSHOT_BYTES] = {0};
    uint8_t output[R1_GOODIX_DIAGNOSTIC_OUTPUT_MAX] = {0};
    size_t written = 99u;
    snapshot[0] = 70u;
    snapshot[4] = 2u;
    snapshot[8] = 3u;
    snapshot[12] = 4u;
    assert(r1_goodix_diagnostic_select(
               snapshot, 1u, output, sizeof output, &written) == R1_OK);
    assert(written == 4u && output[0] == 70u && output[1] == 2u &&
           output[2] == 3u && output[3] == 4u);
    snapshot[40] = 1u;
    for (size_t index = 0u; index < 6u; ++index) {
        snapshot[40u + index * 4u] = (uint8_t)(index + 1u);
    }
    assert(r1_goodix_diagnostic_select(
               snapshot, 2u, output, sizeof output, &written) == R1_OK);
    assert(written == 6u && output[0] == 1u && output[5] == 6u);
    snapshot[188] = 1u;
    snapshot[189] = 0xa5u;
    assert(r1_goodix_diagnostic_select(
               snapshot, 3u, output, sizeof output, &written) == R1_OK);
    assert(written == 2u && output[0] == 0u && output[1] == 0xa5u);
    assert(snapshot[188] == 0u);
    assert(r1_goodix_diagnostic_select(
               snapshot, 3u, output, sizeof output, &written) == R1_OK);
    assert(written == 0u);
    for (size_t index = 0u; index < 124u; ++index) {
        snapshot[64u + index] = (uint8_t)index;
    }
    assert(r1_goodix_diagnostic_select(
               snapshot, 5u, output, sizeof output, &written) == R1_OK);
    assert(written == 124u && output[0] == 0u && output[123] == 123u);
    assert(r1_goodix_diagnostic_select(
               snapshot, 5u, output, 123u, &written) == R1_ERROR_CAPACITY);
}

static void test_next_frontier_230_248_policies(void) {
    r1_ep_initialization_plan plan;
    assert(r1_ep_plan_initialization(
               false, false, false, 0u, &plan) == R1_OK);
    assert(!plan.initialized && !plan.retain_partition && !plan.retain_device);
    assert(plan.reason == R1_EP_INITIALIZATION_PARTITION_NOT_FOUND);
    assert(r1_ep_plan_initialization(
               false, true, false, R1_EP_PARTITION_BYTES, &plan) == R1_OK);
    assert(plan.reason == R1_EP_INITIALIZATION_DEVICE_NOT_FOUND);
    assert(r1_ep_plan_initialization(
               false, true, true, R1_EP_PARTITION_BYTES - 1u, &plan) == R1_OK);
    assert(plan.reason == R1_EP_INITIALIZATION_PARTITION_TOO_SMALL);
    assert(!plan.initialized && !plan.scan_cursor);
    assert(r1_ep_plan_initialization(
               false, true, true, R1_EP_PARTITION_BYTES, &plan) == R1_OK);
    assert(plan.initialized && plan.retain_partition && plan.retain_device);
    assert(plan.scan_cursor && plan.reason == R1_EP_INITIALIZATION_READY);
    assert(r1_ep_plan_initialization(
               true, false, false, 0u, &plan) == R1_OK);
    assert(plan.initialized && plan.retain_partition && plan.retain_device);
    assert(!plan.scan_cursor && plan.reason == R1_EP_INITIALIZATION_READY);
    assert(r1_ep_plan_initialization(
               false, true, true, R1_EP_PARTITION_BYTES, NULL) ==
           R1_ERROR_ARGUMENT);
}

static void test_next_frontier_224_230_policies(void) {
    r1_delayed_event_state delayed = {0};
    delayed.last_timer_start_milliseconds = 1000u;
    delayed.last_timer_delay_milliseconds = 500u;
    delayed.slots[0] = (r1_delayed_event_slot){0x1111u, 0xaaaau, 1500u};
    delayed.slots[1] = (r1_delayed_event_slot){0x2222u, 0xbbbbu, 1800u};
    delayed.slots[2] = (r1_delayed_event_slot){0x1111u, 0xccccu, 1900u};
    r1_delayed_event_cancel_result cancelled;
    assert(r1_delayed_event_cancel(
               &delayed, 0x1111u, 0xaaaau, 2048u, &cancelled) == R1_OK);
    assert(cancelled.removed_count == 1u && cancelled.worker_wakeup_requested);
    assert(cancelled.elapsed_milliseconds == 1000u);
    assert(delayed.slots[0].event == 0u && delayed.slots[1].event == 0x2222u);
    assert(delayed.slots[1].remaining_milliseconds == 800u);
    assert(delayed.slots[2].remaining_milliseconds == 900u);
    assert(cancelled.timer_step.next_delay_milliseconds == 800u);
    assert(r1_delayed_event_cancel(
               &delayed, 0x1111u, 0u, 2048u, &cancelled) == R1_OK);
    assert(cancelled.removed_count == 1u);
    assert(r1_delayed_event_cancel(
               &delayed, 0u, 0u, 0u, &cancelled) == R1_ERROR_ARGUMENT);

    r1_heart_rate_mode_transition_plan heart_rate;
    assert(r1_heart_rate_mode_plan_transition(
               0u, 1u, true, false, false, false, &heart_rate) == R1_OK);
    assert(heart_rate.changed && heart_rate.unregister_previous_stream);
    assert(heart_rate.create_mode_timer &&
           heart_rate.mode_timer_period == R1_HEART_RATE_TIMED_MODE_PERIOD);
    assert(r1_heart_rate_mode_plan_transition(
               1u, 2u, false, true, true, true, &heart_rate) == R1_OK);
    assert(heart_rate.stop_mode_timer && heart_rate.stop_measurement_timer);
    assert(heart_rate.stop_hrv_timer && heart_rate.clear_hrv_timing_state);
    assert(!heart_rate.create_mode_timer);
    assert(r1_heart_rate_mode_plan_transition(
               4u, 0u, false, false, false, false, &heart_rate) ==
           R1_ERROR_ARGUMENT);

    r1_ring_stability_state stability;
    r1_ring_stability_initialize(&stability);
    r1_ring_stability_result stability_result;
    for (size_t index = 0u; index < 7u; ++index) {
        assert(r1_ring_stability_observe(
                   &stability, 0.05f, true, &stability_result) == R1_OK);
        assert(!stability_result.evaluated);
    }
    for (size_t index = 0u; index < 599u; ++index) {
        assert(r1_ring_stability_observe(
                   &stability, 0.05f, true, &stability_result) == R1_OK);
    }
    assert(stability_result.evaluated && !stability_result.detected);
    assert(stability_result.low_motion_count == 599u);
    assert(r1_ring_stability_observe(
               &stability, 0.05f, true, &stability_result) == R1_OK);
    assert(stability_result.detected && stability_result.state_changed);
    assert(stability_result.callback_requested);
    assert(r1_ring_stability_observe(
               &stability, 0.051f, false, &stability_result) == R1_OK);
    assert(!stability_result.detected && stability_result.state_changed);
    assert(!stability_result.callback_requested);

    r1_phy_update_plan phy;
    assert(r1_connection_phy_update_plan(
               7u, true, 1u, 4u, &phy) == R1_OK);
    assert(phy.request_update && phy.connection == 7u);
    assert(phy.transmit_phy == 1u && phy.receive_phy == 4u);
    assert(r1_connection_phy_update_plan(
               R1_CONNECTION_HANDLE_INVALID, true, 1u, 1u, &phy) ==
           R1_ERROR_STATE);
    assert(!phy.request_update);
    assert(r1_connection_phy_update_plan(
               7u, false, 1u, 1u, &phy) == R1_ERROR_STATE);
}

static void test_next_frontier_212_222_policies(void) {
    r1_bae8_hvx_retry_plan hvx;
    assert(r1_bae8_plan_hvx_result(
               false, true, R1_TX_DROP, 0u, &hvx) == R1_OK);
    assert(hvx.release_credit && !hvx.retry_once &&
           hvx.retry_delay_ticks == 0u);
    assert(r1_bae8_plan_hvx_result(
               true, true, R1_TX_RESOURCES, 0u, &hvx) == R1_OK);
    assert(hvx.release_credit && hvx.retry_once &&
           hvx.retry_delay_ticks == R1_EUS_RESOURCE_RETRY_TICKS);
    assert(r1_bae8_plan_hvx_result(
               true, true, R1_TX_RESOURCES, 1u, &hvx) == R1_OK);
    assert(hvx.release_credit && !hvx.retry_once);
    assert(r1_bae8_plan_hvx_result(
               true, false, R1_TX_RESOURCES, 0u, &hvx) == R1_OK);
    assert(!hvx.release_credit && !hvx.retry_once);

    r1_fds_event_plan fds;
    assert(r1_fds_plan_event(
               1u, 0u, UINT16_C(0x25), UINT32_C(0x12345678),
               true, false, &fds) == R1_OK);
    assert(fds.publish_event &&
           fds.persistence_event == R1_FDS_PERSISTENCE_RECORD_SUCCEEDED);
    assert(fds.logical_record_key == UINT16_C(0x4025));
    assert(fds.record_id == UINT32_C(0x12345678));
    assert(r1_fds_plan_event(
               3u, 7u, 2u, 9u, true, false, &fds) == R1_OK);
    assert(fds.publish_event && fds.updated_record &&
           fds.persistence_event == R1_FDS_PERSISTENCE_RECORD_FAILED &&
           fds.provider_result == 7u);
    assert(r1_fds_plan_event(
               4u, 0u, 3u, 0u, true, false, &fds) == R1_OK);
    assert(fds.clear_file_bookkeeping && fds.mark_retry_pending &&
           fds.request_next_queued_operation);
    assert(fds.persistence_event ==
           R1_FDS_PERSISTENCE_FILE_DELETE_SUCCEEDED);
    assert(r1_fds_plan_event(
               5u, 8u, 0u, 0u, false, true, &fds) == R1_OK);
    assert(fds.publish_event && fds.logical_record_key == UINT16_MAX &&
           fds.request_next_queued_operation &&
           fds.persistence_event == R1_FDS_PERSISTENCE_GC_FAILED);
    assert(r1_fds_plan_event(
               2u, 0u, 1u, 1u, false, false, &fds) == R1_OK);
    assert(!fds.publish_event);

    r1_sleep_sync_ack_plan acknowledgement;
    assert(r1_sleep_sync_plan_acknowledgement(
               false, false, &acknowledgement) == R1_OK);
    assert(!acknowledgement.publish_event &&
           !acknowledgement.release_context);
    assert(r1_sleep_sync_plan_acknowledgement(
               true, true, &acknowledgement) == R1_OK);
    assert(acknowledgement.publish_event &&
           acknowledgement.release_context &&
           !acknowledgement.publish_failed);
    assert(acknowledgement.event_identifier == R1_SLEEP_SYNC_MARK_EVENT);
    assert(acknowledgement.event_payload_length ==
           R1_SLEEP_SYNC_ACK_CONTEXT_BYTES);
    assert(r1_sleep_sync_plan_acknowledgement(
               true, false, &acknowledgement) == R1_OK);
    assert(acknowledgement.publish_failed &&
           acknowledgement.release_context);

    r1_system_control_command_37_result control;
    assert(r1_system_control_command_37_plan(
               0u, 59u, 0u, 0u, &control) == R1_OK);
    assert(control.send_reply && control.reply_length == 5u &&
           control.zero_reply_byte4);
    assert(r1_system_control_command_37_plan(
               2u, 0u, UINT8_C(0x54), 0u, &control) == R1_OK);
    assert(control.send_reply && control.reply_length == 5u);
    assert(control.set_configuration_byte &&
           control.configuration_byte == UINT8_C(0x5a));
    assert(control.refresh_configuration && control.delay_requested);
    assert(control.delay_ticks == R1_SYSTEM_CONTROL_DELAY_TICKS);
    assert(control.persist_reset_trace && control.system_reset_requested);
    assert(control.reset_action == R1_SYSTEM_CONTROL_RESET_STANDARD);
    assert(r1_system_control_command_37_plan(
               2u, 0u, UINT8_C(0x55), 0u, &control) == R1_OK);
    assert(!control.persist_reset_trace &&
           control.reset_action == R1_SYSTEM_CONTROL_RESET_ALTERNATE);
    assert(r1_system_control_command_37_plan(
               3u, 1u, 0u, 0u, &control) == R1_OK);
    assert(control.send_reply && control.system_reset_requested &&
           control.reset_action == R1_SYSTEM_CONTROL_RESET_CONFIRMED);
    assert(r1_system_control_command_37_plan(
               4u, 0u, 0u, 60u, &control) == R1_OK);
    assert(control.send_reply && control.reply_length == 64u);
    assert(r1_system_control_command_37_plan(
               4u, 0u, 0u, 61u, &control) == R1_ERROR_CAPACITY);
    assert(r1_system_control_command_37_plan(
               5u, 0u, 0u, 0u, &control) == R1_OK);
    assert(!control.send_reply && control.persist_reset_trace &&
           control.configuration_byte == UINT8_C(0x55));
    assert(r1_system_control_command_37_plan(
               UINT8_C(0xff), 0u, 0u, 0u, &control) == R1_OK);
    assert(!control.send_reply && !control.system_reset_requested);
}

static void test_next_frontier_204_210_policies(void) {
    r1_sensor_stream_registration_plan_result streams;
    assert(r1_sensor_stream_registration_plan(&streams) == R1_OK);
    assert(streams.initialize_goodix && streams.clear_state);
    assert(streams.clear_bytes == R1_SENSOR_STREAM_STATE_BYTES);
    assert(streams.callback_count == R1_SENSOR_STREAM_CALLBACK_COUNT);
    static const char *const names[] = {
        "hr", "spo2", "raw_hr", "wear", "gray", "aging", "hrv", "adt",
    };
    static const uint16_t sizes[] = {4u, 6u, 124u, 2u, 12u, 12u, 10u, 24u};
    static const uint8_t types[] = {1u, 2u, 5u, 3u, 8u, 9u, 4u, 7u};
    for (size_t index = 0u; index < R1_SENSOR_STREAM_REGISTRATION_COUNT;
         ++index) {
        assert(strcmp(streams.registrations[index].name, names[index]) == 0);
        assert(streams.registrations[index].payload_bytes == sizes[index]);
        assert(streams.registrations[index].type == types[index]);
        assert(streams.registrations[index].enabled);
    }
    assert(r1_sensor_stream_registration_plan(NULL) == R1_ERROR_ARGUMENT);

    r1_activity_offline_queue queue;
    r1_activity_offline_initialize(&queue);
    const uint32_t words[6] = {1u, 0u, 2u, 3u, 4u, 5u};
    r1_activity_flash_record_enqueue_result activity;
    assert(r1_activity_flash_record_enqueue_plan(
               &queue, 100u, -60, 2u, words, 150u, 200u, 200u,
               &activity) == R1_OK);
    assert(activity.action == R1_ACTIVITY_FLASH_RECORD_ACCEPTED);
    assert(activity.attempted_count == 6u && activity.enqueued_count == 5u);
    assert(activity.dropped_count == 1u && queue.count == 5u);
    assert(queue.entries[0].bucket_index == 12u);
    assert(queue.entries[4].bucket_index == 17u);
    assert(r1_activity_flash_record_enqueue_plan(
               &queue, 100u, 0, 24u, words, 150u, 200u, 200u,
               &activity) == R1_OK);
    assert(activity.action == R1_ACTIVITY_FLASH_RECORD_IGNORED_HOUR);
    assert(activity.attempted_count == 0u && queue.count == 5u);
    assert(r1_activity_flash_record_enqueue_plan(
               &queue, 100u, 0, 0u, words, 201u, 200u, 300u,
               &activity) == R1_OK);
    assert(activity.action ==
           R1_ACTIVITY_FLASH_RECORD_IGNORED_MAXIMUM_TIMESTAMP);
    assert(r1_activity_flash_record_enqueue_plan(
               &queue, 100u, 0, 0u, words, 250u, 300u, 200u,
               &activity) == R1_OK);
    assert(activity.action == R1_ACTIVITY_FLASH_RECORD_IGNORED_FUTURE_RECORDED);
    assert(r1_activity_flash_record_enqueue_plan(
               &queue, 201u, 0, 0u, words, 150u, 300u, 200u,
               &activity) == R1_OK);
    assert(activity.action == R1_ACTIVITY_FLASH_RECORD_IGNORED_FUTURE_DAY);

    r1_connection_parameter_mode_plan connection;
    assert(r1_connection_parameter_mode_adapter(
               7u, 7u, 8u, 1u, 0u, false, false, &connection) == R1_OK);
    assert(connection.set_preferred && connection.request_update);
    assert(connection.mark_fast_active);
    assert(connection.parameter_set == R1_CONNECTION_PARAMETER_SET_FAST_A);
    assert(r1_connection_parameter_mode_adapter(
               7u, 7u, 8u, 1u, 0u, false, true, &connection) == R1_OK);
    assert(connection.parameter_set == R1_CONNECTION_PARAMETER_SET_FAST_B);
    assert(r1_connection_parameter_mode_adapter(
               8u, 7u, 8u, 2u, 0u, false, false, &connection) == R1_OK);
    assert(connection.parameter_set == R1_CONNECTION_PARAMETER_SET_GLASSES);
    assert(r1_connection_parameter_mode_adapter(
               8u, 7u, 8u, 2u, 0u, true, false, &connection) == R1_OK);
    assert(!connection.set_preferred && !connection.request_update);
    assert(r1_connection_parameter_mode_adapter(
               7u, 7u, 8u, 0u, 1u, false, false, &connection) == R1_OK);
    assert(connection.parameter_set == R1_CONNECTION_PARAMETER_SET_DEFAULT);
    assert(!connection.mark_fast_active);
    assert(r1_connection_parameter_mode_adapter(
               R1_CONNECTION_HANDLE_INVALID, 7u, 8u, 0u, 1u, false, false,
               &connection) == R1_OK);
    assert(!connection.request_update);

    uint8_t flash_bytes[96];
    r1_memory_flash memory;
    r1_memory_flash_initialize(&memory, flash_bytes, sizeof flash_bytes);
    const uint32_t magic = UINT32_C(0x52494e47);
    flash_bytes[2u * 32u + R1_FLASH_SLOT_MAGIC_OFFSET] = (uint8_t)magic;
    flash_bytes[2u * 32u + R1_FLASH_SLOT_MAGIC_OFFSET + 1u] =
        (uint8_t)(magic >> 8u);
    flash_bytes[2u * 32u + R1_FLASH_SLOT_MAGIC_OFFSET + 2u] =
        (uint8_t)(magic >> 16u);
    flash_bytes[2u * 32u + R1_FLASH_SLOT_MAGIC_OFFSET + 3u] =
        (uint8_t)(magic >> 24u);
    const r1_flash flash = r1_memory_flash_interface(&memory);
    r1_latest_valid_flash_slot_scan_result scan;
    assert(r1_latest_valid_flash_slot_scan_adapter(
               &flash, 0u, 32u, 4u, magic, &scan) == R1_OK);
    assert(scan.found && scan.latest_slot == 2u && scan.next_slot == 3u);
    assert(scan.read_count == 2u && scan.provider_read_failed);
    assert(r1_latest_valid_flash_slot_scan_adapter(
               &flash, 0u, 32u, 2u, magic, &scan) == R1_OK);
    assert(!scan.found && scan.next_slot == 0u && scan.read_count == 2u);
}

int main(void) {
    test_checksums();
    test_retained_crash_log();
    test_retained_reset_trace();
    test_reset_reason_decode();
    test_clock_production();
    test_battery_provider_boundary();
    test_battery_controller();
    test_pmic_charge_event_policy();
    test_pmic_charged_notification_policy();
    test_model_round_trip();
    test_protocol_response_orchestration();
    test_physical_wire_vectors();
    test_fragments();
    test_fragment_boundaries();
    test_dispatch();
    test_legacy_command_routing();
    test_legacy_device_info_builder();
    test_ati_calibration_command();
    test_health_history_routing();
    test_activity_cumulative_counter_service();
    test_health_histories_and_dispatch();
    test_automatic_health_sync();
    test_health_time_and_hour_orchestration();
    test_activity_offline_sync();
    test_activity_daily_cache_callbacks();
    test_activity_day_builder_merges();
    test_scalar_health_daily_cache_callbacks();
    test_temperature_and_stress_daily_cache_callbacks();
    test_scalar_health_sample_consumers();
    test_health_crash_snapshot();
    test_health_database_startup();
    test_twi_synchronization_adapter();
    test_scalar_health_ram_cache_merge();
    test_scalar_health_flash_record_merge();
    test_scalar_health_offline_sync();
    test_hrv_ram_cache_merge();
    test_sleep_history_and_dispatch();
    test_maximum_health_payloads();
    test_hrv_rmssd();
    test_hrv_producer();
    test_hrv_timing_start_policy();
    test_event_plane();
    test_delayed_event_timer_step();
    test_runtime_roles();
    test_runtime_role_occupancy();
    test_runtime_touch_effect();
    test_runtime_eus_bridge();
    test_bae8_event_route();
    test_storage();
    test_export_planner();
    test_kv_snapshot_store();
    test_nv_recovery_merge();
    test_sleep_database();
    test_sleep_persistence_bridge();
    test_validated_sleep_delivery_plans();
    test_goodix_provider_boundary();
    test_goodix_mem_integrator_glue();
    test_iqs7211e_provider_boundary();
    test_iqs7211e_ati_audit_policy();
    test_st25dvxxkc_provider_boundary();
    test_st25dvxxkc_dock_policy();
    test_shared_power_lease();
    test_motion_provider_boundary();
    test_wear_fusion();
    test_connection_parameter_policy();
    test_connection_role_assignment();
    test_peer_target_policy();
    test_next_frontier_product_policies();
    test_next_frontier_334_342_policies();
    test_next_frontier_314_328_policies();
    test_next_frontier_280_308_policies();
    test_next_frontier_264_274_policies();
    test_next_frontier_256_262_policies();
    test_next_frontier_230_248_policies();
    test_next_frontier_224_230_policies();
    test_next_frontier_212_222_policies();
    test_next_frontier_204_210_policies();
    puts("openR1: all tests passed");
    return 0;
}
