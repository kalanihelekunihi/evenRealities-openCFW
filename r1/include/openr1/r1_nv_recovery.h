#ifndef OPENR1_R1_NV_RECOVERY_H
#define OPENR1_R1_NV_RECOVERY_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"
#include "openr1/r1_motion.h"

#define R1_NV_RECOVERY_BODY_BYTES 116u
#define R1_NV_RECOVERY_COMMAND_ENVELOPE_BYTES 5u
#define R1_NV_RECOVERY_SYSTEM_IDENTIFIER UINT16_C(0x0011)
#define R1_NV_RECOVERY_OUTBOUND_RESPONSE_TYPE 1u
#define R1_NV_RECOVERY_CONFIG_BYTES 124u
#define R1_NV_RECOVERY_POWER_BYTES 4u
#define R1_NV_RECOVERY_RING_SIZE_BYTES 1u
#define R1_NV_RECOVERY_TEMPERATURE_CALIBRATION_OFFSET 62u
#define R1_NV_RECOVERY_TEMPERATURE_CALIBRATION_BYTES 6u
#define R1_NV_RECOVERY_ACCELEROMETER_CALIBRATION_OFFSET 68u
#define R1_NV_RECOVERY_ACCELEROMETER_CALIBRATION_BYTES 6u
#define R1_NV_RECOVERY_POWER_BATTERY_TYPE_OFFSET 0u
#define R1_NV_RECOVERY_POWER_VOLTAGE_COMPENSATION_OFFSET 2u

#define R1_NV_RECOVERY_CHANGED_CONFIG UINT8_C(0x01)
#define R1_NV_RECOVERY_CHANGED_POWER UINT8_C(0x02)
#define R1_NV_RECOVERY_CHANGED_RING_SIZE UINT8_C(0x04)

#define R1_NV_COMPILED_RESTORE_KEY_BYTES 12u
#define R1_NV_COMPILED_RESTORE_MAX_RECORDS 59u

typedef struct {
    uint8_t match_key[R1_NV_COMPILED_RESTORE_KEY_BYTES];
    uint8_t packed_ring_size_battery_type;
    int8_t voltage_compensation_millivolts;
} r1_nv_compiled_restore_record;

typedef enum {
    R1_NV_COMPILED_RESTORE_APPLY = 0,
    R1_NV_COMPILED_RESTORE_CONFIGURATION_EXISTS = -1,
    R1_NV_COMPILED_RESTORE_NO_MATCH = -2
} r1_nv_compiled_restore_status;

/* Pure, caller-supplied alternative to the identity-bearing stock table. */
typedef struct {
    r1_nv_compiled_restore_status status;
    bool write_records;
    size_t matched_record;
    uint8_t ring_size;
    uint8_t battery_type;
    int16_t voltage_compensation_millivolts;
} r1_nv_compiled_restore_plan;

/*
 * Product-owned state split across the recovered nv_r1, power, and r_size
 * records. This API plans bounded internal recovery only. The normal BLE
 * nvRecover command remains deliberately unavailable.
 */
typedef struct {
    uint8_t config[R1_NV_RECOVERY_CONFIG_BYTES];
    uint8_t power[R1_NV_RECOVERY_POWER_BYTES];
    uint8_t ring_size;
} r1_nv_recovery_state;

typedef struct {
    r1_nv_recovery_state state;
    uint8_t changed_records;
} r1_nv_recovery_result;

typedef struct {
    uint8_t battery_type;
    int16_t voltage_compensation_millivolts;
    bool battery_type_valid;
    bool voltage_compensation_valid;
} r1_nv_battery_configuration;

typedef enum {
    R1_NV_RECOVERY_HANDLER_IGNORE = 0,
    R1_NV_RECOVERY_HANDLER_REQUEST_LOCAL_REPORT,
    R1_NV_RECOVERY_HANDLER_DISPATCH_MERGE
} r1_nv_recovery_handler_action;

/* Strict, non-invoking form of the registered nvRecover handler at
 * 0x00084150 and its command route. The identity-bearing report sender and
 * persistent merge remain unavailable; this structure carries intent only. */
typedef struct {
    r1_nv_recovery_handler_action action;
    uint8_t command;
    uint16_t declared_body_length;
    uint16_t declared_body_crc;
    uint8_t body[R1_NV_RECOVERY_BODY_BYTES];
} r1_nv_recovery_handler_plan;

/* Strict plan for outbound wrapper 0x000839B4. The caller-owned envelope is
 * never sent here; this records only the current-phone-session response
 * parameters passed to the separately gated protocol transport. */
typedef struct {
    bool send_response;
    uint16_t session;
    uint16_t identifier;
    uint8_t response_type;
    uint16_t serial;
    size_t payload_length;
} r1_nv_recovery_outbound_response_plan;

bool r1_nv_recovery_build_body(
    const r1_nv_recovery_state *state,
    uint8_t body[R1_NV_RECOVERY_BODY_BYTES]);

r1_error r1_nv_recovery_merge(
    const r1_nv_recovery_state *current,
    const uint8_t *body,
    size_t body_length,
    uint16_t expected_crc,
    r1_nv_recovery_result *result);

r1_error r1_nv_recovery_command_handler_plan_decode(
    const uint8_t *payload, size_t payload_length,
    r1_nv_recovery_handler_plan *plan);
r1_error r1_nv_recovery_outbound_response_plan_build(
    uint16_t current_phone_session, const uint8_t *envelope,
    size_t envelope_length, r1_nv_recovery_outbound_response_plan *plan);

r1_error r1_nv_compiled_default_restore_plan_build(
    uint8_t current_battery_type,
    const uint8_t match_key[R1_NV_COMPILED_RESTORE_KEY_BYTES],
    const r1_nv_compiled_restore_record *records, size_t record_count,
    r1_nv_compiled_restore_plan *plan);
r1_error r1_nv_compiled_default_restore_event_plan(
    uint8_t current_battery_type,
    const uint8_t match_key[R1_NV_COMPILED_RESTORE_KEY_BYTES],
    const r1_nv_compiled_restore_record *records, size_t record_count,
    r1_nv_compiled_restore_plan *plan);

r1_error r1_nv_battery_configuration_decode(
    const uint8_t *input, size_t length,
    r1_nv_battery_configuration *configuration);
r1_error r1_nv_accelerometer_calibration_decode(
    const uint8_t *input, size_t length,
    r1_motion_axis_calibration *calibration, bool *present);
r1_error r1_nv_ring_size_decode(
    const uint8_t *input, size_t length, uint8_t *ring_size, bool *valid);

#endif
