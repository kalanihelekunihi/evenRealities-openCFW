#include "openr1/r1_nv_recovery.h"

#include "openr1/r1_crc.h"

enum {
    PRODUCT_BSN_OFFSET = 0,
    PRODUCT_BSN_BYTES = 30,
    PRODUCT_BSN_LENGTH_OFFSET = 30,
    PRODUCT_SN_OFFSET = 31,
    PRODUCT_SN_BYTES = 30,
    PRODUCT_SN_LENGTH_OFFSET = 61,
    TEMPERATURE_CALIBRATION_OFFSET = 62,
    TEMPERATURE_CALIBRATION_BYTES = 6,
    ACCELEROMETER_CALIBRATION_OFFSET = 68,
    ACCELEROMETER_CALIBRATION_BYTES = 6,
    BODY_BATTERY_TYPE_OFFSET = 92,
    BODY_VOLTAGE_COMPENSATION_OFFSET = 94,
    BODY_RING_SIZE_OFFSET = 96,
    POWER_BATTERY_TYPE_OFFSET = 0,
    POWER_VOLTAGE_COMPENSATION_OFFSET = 2
};

static void copy_bytes(uint8_t *destination, const uint8_t *source, size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        destination[index] = source[index];
    }
}

static void clear_bytes(uint8_t *destination, size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        destination[index] = 0u;
    }
}

static int16_t read_i16(const uint8_t *bytes) {
    const uint16_t raw = (uint16_t)bytes[0] | (uint16_t)((uint16_t)bytes[1] << 8u);
    return (int16_t)raw;
}

static bool battery_type_valid(uint8_t value) {
    return value >= 1u && value <= 4u;
}

static bool voltage_report_valid(int16_t value) {
    return value >= -500 && value <= 500 && value != -1;
}

static bool voltage_recovery_valid(int16_t value) {
    return voltage_report_valid(value) && value != 0;
}

static bool ring_size_valid(uint8_t value) {
    return value >= 6u && value <= 15u;
}

static bool identity_length_valid(uint8_t value) {
    return value >= 1u && value <= 30u;
}

bool r1_nv_recovery_build_body(
    const r1_nv_recovery_state *state,
    uint8_t body[R1_NV_RECOVERY_BODY_BYTES]) {
    if (state == NULL || body == NULL) {
        return false;
    }

    clear_bytes(body, R1_NV_RECOVERY_BODY_BYTES);
    copy_bytes(body + PRODUCT_BSN_OFFSET, state->config + PRODUCT_BSN_OFFSET,
               PRODUCT_BSN_BYTES + 1u);
    copy_bytes(body + PRODUCT_SN_OFFSET, state->config + PRODUCT_SN_OFFSET,
               PRODUCT_SN_BYTES + 1u);
    copy_bytes(body + TEMPERATURE_CALIBRATION_OFFSET,
               state->config + TEMPERATURE_CALIBRATION_OFFSET,
               TEMPERATURE_CALIBRATION_BYTES);
    copy_bytes(body + ACCELEROMETER_CALIBRATION_OFFSET,
               state->config + ACCELEROMETER_CALIBRATION_OFFSET,
               ACCELEROMETER_CALIBRATION_BYTES);
    body[BODY_BATTERY_TYPE_OFFSET] = state->power[POWER_BATTERY_TYPE_OFFSET];
    body[BODY_VOLTAGE_COMPENSATION_OFFSET] =
        state->power[POWER_VOLTAGE_COMPENSATION_OFFSET];
    body[BODY_VOLTAGE_COMPENSATION_OFFSET + 1u] =
        state->power[POWER_VOLTAGE_COMPENSATION_OFFSET + 1u];
    body[BODY_RING_SIZE_OFFSET] = state->ring_size;

    return battery_type_valid(body[BODY_BATTERY_TYPE_OFFSET]) &&
           voltage_report_valid(read_i16(body + BODY_VOLTAGE_COMPENSATION_OFFSET)) &&
           ring_size_valid(body[BODY_RING_SIZE_OFFSET]) &&
           identity_length_valid(body[PRODUCT_BSN_LENGTH_OFFSET]);
}

r1_error r1_nv_recovery_merge(
    const r1_nv_recovery_state *current,
    const uint8_t *body,
    size_t body_length,
    uint16_t expected_crc,
    r1_nv_recovery_result *result) {
    if (current == NULL || body == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (body_length != R1_NV_RECOVERY_BODY_BYTES) {
        return R1_ERROR_LENGTH;
    }
    if (r1_crc16_modbus(body, body_length) != expected_crc) {
        return R1_ERROR_CHECKSUM;
    }

    result->state = *current;
    result->changed_records = 0u;

    const uint8_t incoming_battery = body[BODY_BATTERY_TYPE_OFFSET];
    if (!battery_type_valid(result->state.power[POWER_BATTERY_TYPE_OFFSET]) &&
        battery_type_valid(incoming_battery)) {
        result->state.power[POWER_BATTERY_TYPE_OFFSET] = incoming_battery;
        result->changed_records |= R1_NV_RECOVERY_CHANGED_POWER;
    }

    const int16_t local_voltage =
        read_i16(result->state.power + POWER_VOLTAGE_COMPENSATION_OFFSET);
    const int16_t incoming_voltage =
        read_i16(body + BODY_VOLTAGE_COMPENSATION_OFFSET);
    if (!voltage_recovery_valid(local_voltage) &&
        voltage_recovery_valid(incoming_voltage)) {
        result->state.power[POWER_VOLTAGE_COMPENSATION_OFFSET] =
            body[BODY_VOLTAGE_COMPENSATION_OFFSET];
        result->state.power[POWER_VOLTAGE_COMPENSATION_OFFSET + 1u] =
            body[BODY_VOLTAGE_COMPENSATION_OFFSET + 1u];
        result->changed_records |= R1_NV_RECOVERY_CHANGED_POWER;
    }

    const uint8_t incoming_ring_size = body[BODY_RING_SIZE_OFFSET];
    if (!ring_size_valid(result->state.ring_size) &&
        ring_size_valid(incoming_ring_size)) {
        result->state.ring_size = incoming_ring_size;
        result->changed_records |= R1_NV_RECOVERY_CHANGED_RING_SIZE;
    }

    if (result->state.config[PRODUCT_BSN_LENGTH_OFFSET] == UINT8_MAX &&
        identity_length_valid(body[PRODUCT_BSN_LENGTH_OFFSET])) {
        copy_bytes(result->state.config + PRODUCT_BSN_OFFSET,
                   body + PRODUCT_BSN_OFFSET, PRODUCT_BSN_BYTES + 1u);
        result->changed_records |= R1_NV_RECOVERY_CHANGED_CONFIG;
    }
    if (result->state.config[PRODUCT_SN_LENGTH_OFFSET] == UINT8_MAX &&
        identity_length_valid(body[PRODUCT_SN_LENGTH_OFFSET])) {
        copy_bytes(result->state.config + PRODUCT_SN_OFFSET,
                   body + PRODUCT_SN_OFFSET, PRODUCT_SN_BYTES + 1u);
        result->changed_records |= R1_NV_RECOVERY_CHANGED_CONFIG;
    }
    if (result->state.config[TEMPERATURE_CALIBRATION_OFFSET] == UINT8_MAX &&
        body[TEMPERATURE_CALIBRATION_OFFSET] != UINT8_MAX) {
        copy_bytes(result->state.config + TEMPERATURE_CALIBRATION_OFFSET,
                   body + TEMPERATURE_CALIBRATION_OFFSET,
                   TEMPERATURE_CALIBRATION_BYTES);
        result->changed_records |= R1_NV_RECOVERY_CHANGED_CONFIG;
    }
    if (read_i16(result->state.config + ACCELEROMETER_CALIBRATION_OFFSET) == -1 &&
        read_i16(body + ACCELEROMETER_CALIBRATION_OFFSET) != -1) {
        copy_bytes(result->state.config + ACCELEROMETER_CALIBRATION_OFFSET,
                   body + ACCELEROMETER_CALIBRATION_OFFSET,
                   ACCELEROMETER_CALIBRATION_BYTES);
        result->changed_records |= R1_NV_RECOVERY_CHANGED_CONFIG;
    }

    return R1_OK;
}
