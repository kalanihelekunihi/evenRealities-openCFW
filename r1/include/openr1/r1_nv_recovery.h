#ifndef OPENR1_R1_NV_RECOVERY_H
#define OPENR1_R1_NV_RECOVERY_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"
#include "openr1/r1_motion.h"

#define R1_NV_RECOVERY_BODY_BYTES 116u
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

bool r1_nv_recovery_build_body(
    const r1_nv_recovery_state *state,
    uint8_t body[R1_NV_RECOVERY_BODY_BYTES]);

r1_error r1_nv_recovery_merge(
    const r1_nv_recovery_state *current,
    const uint8_t *body,
    size_t body_length,
    uint16_t expected_crc,
    r1_nv_recovery_result *result);

r1_error r1_nv_battery_configuration_decode(
    const uint8_t *input, size_t length,
    r1_nv_battery_configuration *configuration);
r1_error r1_nv_accelerometer_calibration_decode(
    const uint8_t *input, size_t length,
    r1_motion_axis_calibration *calibration, bool *present);
r1_error r1_nv_ring_size_decode(
    const uint8_t *input, size_t length, uint8_t *ring_size, bool *valid);

#endif
