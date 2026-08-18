#include "openr1/r1_nv_recovery.h"

#include "openr1/r1_crc.h"

enum {
    PRODUCT_BSN_OFFSET = 0,
    PRODUCT_BSN_BYTES = 30,
    PRODUCT_BSN_LENGTH_OFFSET = 30,
    PRODUCT_SN_OFFSET = 31,
    PRODUCT_SN_BYTES = 30,
    PRODUCT_SN_LENGTH_OFFSET = 61,
    PRODUCT_FACTORY_MODE_OFFSET = 112,
    BODY_BATTERY_TYPE_OFFSET = 92,
    BODY_VOLTAGE_COMPENSATION_OFFSET = 94,
    BODY_RING_SIZE_OFFSET = 96
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

static uint16_t read_u16(const uint8_t *bytes) {
    return (uint16_t)bytes[0] |
           (uint16_t)((uint16_t)bytes[1] << 8u);
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

static bool bytes_equal(const uint8_t *left, const uint8_t *right,
                        size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        if (left[index] != right[index]) {
            return false;
        }
    }
    return true;
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
    copy_bytes(body + R1_NV_RECOVERY_TEMPERATURE_CALIBRATION_OFFSET,
               state->config + R1_NV_RECOVERY_TEMPERATURE_CALIBRATION_OFFSET,
               R1_NV_RECOVERY_TEMPERATURE_CALIBRATION_BYTES);
    copy_bytes(body + R1_NV_RECOVERY_ACCELEROMETER_CALIBRATION_OFFSET,
               state->config +
                   R1_NV_RECOVERY_ACCELEROMETER_CALIBRATION_OFFSET,
               R1_NV_RECOVERY_ACCELEROMETER_CALIBRATION_BYTES);
    body[BODY_BATTERY_TYPE_OFFSET] =
        state->power[R1_NV_RECOVERY_POWER_BATTERY_TYPE_OFFSET];
    body[BODY_VOLTAGE_COMPENSATION_OFFSET] =
        state->power[R1_NV_RECOVERY_POWER_VOLTAGE_COMPENSATION_OFFSET];
    body[BODY_VOLTAGE_COMPENSATION_OFFSET + 1u] =
        state->power[R1_NV_RECOVERY_POWER_VOLTAGE_COMPENSATION_OFFSET + 1u];
    body[BODY_RING_SIZE_OFFSET] = state->ring_size;

    return battery_type_valid(body[BODY_BATTERY_TYPE_OFFSET]) &&
           voltage_report_valid(read_i16(body + BODY_VOLTAGE_COMPENSATION_OFFSET)) &&
           ring_size_valid(body[BODY_RING_SIZE_OFFSET]) &&
           identity_length_valid(body[PRODUCT_BSN_LENGTH_OFFSET]);
}

r1_error r1_nv_recovery_command_handler_plan_decode(
    const uint8_t *payload, size_t payload_length,
    r1_nv_recovery_handler_plan *plan) {
    if (payload == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (payload_length < R1_NV_RECOVERY_COMMAND_ENVELOPE_BYTES) {
        return R1_ERROR_LENGTH;
    }

    const uint16_t declared_body_length = read_u16(payload + 1u);
    if (payload_length != R1_NV_RECOVERY_COMMAND_ENVELOPE_BYTES +
                          (size_t)declared_body_length) {
        return R1_ERROR_LENGTH;
    }

    *plan = (r1_nv_recovery_handler_plan){
        .action = R1_NV_RECOVERY_HANDLER_IGNORE,
        .command = payload[0],
        .declared_body_length = declared_body_length,
        .declared_body_crc = read_u16(payload + 3u),
    };
    if (plan->command != 2u) {
        return R1_OK;
    }
    if (plan->declared_body_length != R1_NV_RECOVERY_BODY_BYTES ||
        plan->declared_body_crc == 0u) {
        plan->action = R1_NV_RECOVERY_HANDLER_REQUEST_LOCAL_REPORT;
        return R1_OK;
    }

    plan->action = R1_NV_RECOVERY_HANDLER_DISPATCH_MERGE;
    copy_bytes(plan->body, payload + R1_NV_RECOVERY_COMMAND_ENVELOPE_BYTES,
               R1_NV_RECOVERY_BODY_BYTES);
    return R1_OK;
}

r1_error r1_nv_recovery_outbound_response_plan_build(
    uint16_t current_phone_session, const uint8_t *envelope,
    size_t envelope_length, r1_nv_recovery_outbound_response_plan *plan) {
    if (envelope == NULL || plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (envelope_length < R1_NV_RECOVERY_COMMAND_ENVELOPE_BYTES) {
        return R1_ERROR_LENGTH;
    }
    const uint16_t body_length = read_u16(envelope + 1u);
    if (body_length > R1_NV_RECOVERY_BODY_BYTES) {
        return R1_ERROR_CAPACITY;
    }
    const size_t payload_length =
        R1_NV_RECOVERY_COMMAND_ENVELOPE_BYTES + (size_t)body_length;
    if (envelope_length != payload_length) {
        return R1_ERROR_LENGTH;
    }

    *plan = (r1_nv_recovery_outbound_response_plan){
        .send_response = current_phone_session != UINT16_MAX,
        .session = current_phone_session,
        .identifier = R1_NV_RECOVERY_SYSTEM_IDENTIFIER,
        .response_type = R1_NV_RECOVERY_OUTBOUND_RESPONSE_TYPE,
        .serial = 0u,
        .payload_length = payload_length,
    };
    return R1_OK;
}

r1_error r1_nv_compiled_default_restore_plan_build(
    uint8_t current_battery_type,
    const uint8_t match_key[R1_NV_COMPILED_RESTORE_KEY_BYTES],
    const r1_nv_compiled_restore_record *records, size_t record_count,
    r1_nv_compiled_restore_plan *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_nv_compiled_restore_plan){
        .status = R1_NV_COMPILED_RESTORE_CONFIGURATION_EXISTS,
        .matched_record = SIZE_MAX,
    };
    if (current_battery_type != 0u && current_battery_type != UINT8_MAX) {
        return R1_OK;
    }
    plan->status = R1_NV_COMPILED_RESTORE_NO_MATCH;
    if (match_key == NULL || (record_count != 0u && records == NULL)) {
        return R1_ERROR_ARGUMENT;
    }
    if (record_count > R1_NV_COMPILED_RESTORE_MAX_RECORDS) {
        return R1_ERROR_CAPACITY;
    }

    for (size_t index = 0u; index < record_count; ++index) {
        if (!bytes_equal(match_key, records[index].match_key,
                         R1_NV_COMPILED_RESTORE_KEY_BYTES)) {
            continue;
        }
        const uint8_t packed = records[index].packed_ring_size_battery_type;
        const uint8_t ring_size = packed & UINT8_C(0x0f);
        const uint8_t battery_type = packed >> 4u;
        if (!ring_size_valid(ring_size) || !battery_type_valid(battery_type)) {
            return R1_ERROR_STATE;
        }
        *plan = (r1_nv_compiled_restore_plan){
            .status = R1_NV_COMPILED_RESTORE_APPLY,
            .write_records = true,
            .matched_record = index,
            .ring_size = ring_size,
            .battery_type = battery_type,
            .voltage_compensation_millivolts =
                (int16_t)records[index].voltage_compensation_millivolts,
        };
        return R1_OK;
    }
    return R1_OK;
}

r1_error r1_nv_compiled_default_restore_event_plan(
    uint8_t current_battery_type,
    const uint8_t match_key[R1_NV_COMPILED_RESTORE_KEY_BYTES],
    const r1_nv_compiled_restore_record *records, size_t record_count,
    r1_nv_compiled_restore_plan *plan) {
    return r1_nv_compiled_default_restore_plan_build(
        current_battery_type, match_key, records, record_count, plan);
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
    if (!battery_type_valid(result->state.power[
            R1_NV_RECOVERY_POWER_BATTERY_TYPE_OFFSET]) &&
        battery_type_valid(incoming_battery)) {
        result->state.power[R1_NV_RECOVERY_POWER_BATTERY_TYPE_OFFSET] =
            incoming_battery;
        result->changed_records |= R1_NV_RECOVERY_CHANGED_POWER;
    }

    const int16_t local_voltage =
        read_i16(result->state.power +
                 R1_NV_RECOVERY_POWER_VOLTAGE_COMPENSATION_OFFSET);
    const int16_t incoming_voltage =
        read_i16(body + BODY_VOLTAGE_COMPENSATION_OFFSET);
    if (!voltage_recovery_valid(local_voltage) &&
        voltage_recovery_valid(incoming_voltage)) {
        result->state.power[
            R1_NV_RECOVERY_POWER_VOLTAGE_COMPENSATION_OFFSET] =
            body[BODY_VOLTAGE_COMPENSATION_OFFSET];
        result->state.power[
            R1_NV_RECOVERY_POWER_VOLTAGE_COMPENSATION_OFFSET + 1u] =
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
    if (result->state.config[
            R1_NV_RECOVERY_TEMPERATURE_CALIBRATION_OFFSET] == UINT8_MAX &&
        body[R1_NV_RECOVERY_TEMPERATURE_CALIBRATION_OFFSET] != UINT8_MAX) {
        copy_bytes(
            result->state.config +
                R1_NV_RECOVERY_TEMPERATURE_CALIBRATION_OFFSET,
            body + R1_NV_RECOVERY_TEMPERATURE_CALIBRATION_OFFSET,
            R1_NV_RECOVERY_TEMPERATURE_CALIBRATION_BYTES);
        result->changed_records |= R1_NV_RECOVERY_CHANGED_CONFIG;
    }
    if (read_i16(result->state.config +
                 R1_NV_RECOVERY_ACCELEROMETER_CALIBRATION_OFFSET) == -1 &&
        read_i16(body +
                 R1_NV_RECOVERY_ACCELEROMETER_CALIBRATION_OFFSET) != -1) {
        copy_bytes(
            result->state.config +
                R1_NV_RECOVERY_ACCELEROMETER_CALIBRATION_OFFSET,
            body + R1_NV_RECOVERY_ACCELEROMETER_CALIBRATION_OFFSET,
            R1_NV_RECOVERY_ACCELEROMETER_CALIBRATION_BYTES);
        result->changed_records |= R1_NV_RECOVERY_CHANGED_CONFIG;
    }

    return R1_OK;
}

r1_error r1_nv_recovery_store_load(
    const r1_kv_store *store, r1_nv_recovery_state *state) {
    if (store == NULL || state == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    size_t length = 0u;
    r1_error error = r1_kv_store_get(
        store, R1_KV_NV_R1, state->config, sizeof state->config, &length);
    if (error != R1_OK || length != sizeof state->config) {
        return error == R1_OK ? R1_ERROR_STATE : error;
    }
    error = r1_kv_store_get(
        store, R1_KV_POWER, state->power, sizeof state->power, &length);
    if (error != R1_OK || length != sizeof state->power) {
        return error == R1_OK ? R1_ERROR_STATE : error;
    }
    uint8_t ring_size[R1_NV_RECOVERY_RING_SIZE_BYTES];
    error = r1_kv_store_get(
        store, R1_KV_RING_SIZE, ring_size, sizeof ring_size, &length);
    if (error != R1_OK || length != sizeof ring_size) {
        return error == R1_OK ? R1_ERROR_STATE : error;
    }
    state->ring_size = ring_size[0];
    return R1_OK;
}

r1_error r1_nv_recovery_store_merge_commit(
    r1_kv_store *store, const uint8_t *body, size_t body_length,
    uint16_t expected_crc, r1_nv_recovery_result *result) {
    if (store == NULL || body == NULL || result == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    r1_nv_recovery_state current;
    r1_error error = r1_nv_recovery_store_load(store, &current);
    if (error != R1_OK) {
        return error;
    }
    error = r1_nv_recovery_merge(
        &current, body, body_length, expected_crc, result);
    if (error != R1_OK || result->changed_records == 0u) {
        return error;
    }

    /* A KV commit includes every dirty class. Recovery must remain one
     * isolated, auditable old-or-new snapshot rather than accidentally
     * committing unrelated caller state. */
    for (size_t index = 0u; index < R1_KV_CLASS_COUNT; ++index) {
        if (store->dirty[index]) {
            return R1_ERROR_STATE;
        }
    }

    if ((result->changed_records & R1_NV_RECOVERY_CHANGED_CONFIG) != 0u) {
        error = r1_kv_store_set(
            store, R1_KV_NV_R1, result->state.config,
            sizeof result->state.config);
    }
    if (error == R1_OK &&
        (result->changed_records & R1_NV_RECOVERY_CHANGED_POWER) != 0u) {
        error = r1_kv_store_set(
            store, R1_KV_POWER, result->state.power,
            sizeof result->state.power);
    }
    if (error == R1_OK &&
        (result->changed_records & R1_NV_RECOVERY_CHANGED_RING_SIZE) != 0u) {
        const uint8_t ring_size[R1_NV_RECOVERY_RING_SIZE_BYTES] = {
            result->state.ring_size,
        };
        error = r1_kv_store_set(
            store, R1_KV_RING_SIZE, ring_size, sizeof ring_size);
    }
    if (error == R1_OK) {
        error = r1_kv_store_commit(store);
    }
    if (error != R1_OK) {
        /* r1_kv_store_commit changes generation/latest-slot only after its
         * readback gate succeeds. Restore just the proposed payloads and
         * dirty flags here, avoiding a full-store stack copy on small RTOS
         * service stacks. Partially programmed flash remains uncommitted. */
        if ((result->changed_records & R1_NV_RECOVERY_CHANGED_CONFIG) != 0u) {
            (void)r1_kv_store_set(
                store, R1_KV_NV_R1, current.config, sizeof current.config);
            store->dirty[R1_KV_NV_R1] = false;
        }
        if ((result->changed_records & R1_NV_RECOVERY_CHANGED_POWER) != 0u) {
            (void)r1_kv_store_set(
                store, R1_KV_POWER, current.power, sizeof current.power);
            store->dirty[R1_KV_POWER] = false;
        }
        if ((result->changed_records &
             R1_NV_RECOVERY_CHANGED_RING_SIZE) != 0u) {
            const uint8_t ring_size[R1_NV_RECOVERY_RING_SIZE_BYTES] = {
                current.ring_size,
            };
            (void)r1_kv_store_set(
                store, R1_KV_RING_SIZE, ring_size, sizeof ring_size);
            store->dirty[R1_KV_RING_SIZE] = false;
        }
    }
    return error;
}

r1_error r1_nv_battery_configuration_decode(
    const uint8_t *input, size_t length,
    r1_nv_battery_configuration *configuration) {
    if (input == NULL || configuration == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_NV_RECOVERY_POWER_BYTES) {
        return R1_ERROR_LENGTH;
    }
    const uint16_t raw = (uint16_t)(
        (uint16_t)input[
            R1_NV_RECOVERY_POWER_VOLTAGE_COMPENSATION_OFFSET] |
        (uint16_t)((uint16_t)input[
            R1_NV_RECOVERY_POWER_VOLTAGE_COMPENSATION_OFFSET + 1u] << 8u));
    const int16_t compensation = raw <= (uint16_t)INT16_MAX
        ? (int16_t)raw
        : (int16_t)((int32_t)raw - INT32_C(65536));
    const uint8_t battery_type =
        input[R1_NV_RECOVERY_POWER_BATTERY_TYPE_OFFSET];
    *configuration = (r1_nv_battery_configuration){
        .battery_type = battery_type,
        .voltage_compensation_millivolts = compensation,
        .battery_type_valid = battery_type_valid(battery_type),
        .voltage_compensation_valid = voltage_report_valid(compensation),
    };
    return R1_OK;
}

r1_error r1_nv_product_serial_decode(
    const uint8_t *input, size_t length,
    uint8_t serial[R1_NV_PRODUCT_SERIAL_BYTES], bool *provisioned) {
    if (input == NULL || serial == NULL || provisioned == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_NV_RECOVERY_CONFIG_BYTES) {
        return R1_ERROR_LENGTH;
    }
    *provisioned = input[PRODUCT_SN_LENGTH_OFFSET] != UINT8_MAX;
    for (size_t index = 0u; index < R1_NV_PRODUCT_SERIAL_BYTES; ++index) {
        serial[index] = *provisioned
            ? input[PRODUCT_SN_OFFSET + index] : UINT8_MAX;
    }
    return R1_OK;
}

r1_error r1_nv_factory_mode_decode(
    const uint8_t *input, size_t length, bool *factory_mode) {
    if (input == NULL || factory_mode == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_NV_RECOVERY_CONFIG_BYTES) {
        return R1_ERROR_LENGTH;
    }
    *factory_mode =
        input[PRODUCT_FACTORY_MODE_OFFSET] == R1_NV_FACTORY_MODE_MARKER;
    return R1_OK;
}

r1_error r1_nv_accelerometer_calibration_decode(
    const uint8_t *input, size_t length,
    r1_motion_axis_calibration *calibration, bool *present) {
    if (input == NULL || calibration == NULL || present == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_NV_RECOVERY_ACCELEROMETER_CALIBRATION_BYTES) {
        return R1_ERROR_LENGTH;
    }
    *calibration = (r1_motion_axis_calibration){
        .x = read_i16(input),
        .y = read_i16(input + 2u),
        .z = read_i16(input + 4u),
    };
    *present = !(calibration->x == -1 && calibration->y == -1 &&
                 calibration->z == -1);
    return R1_OK;
}

r1_error r1_nv_ring_size_decode(
    const uint8_t *input, size_t length, uint8_t *ring_size, bool *valid) {
    if (input == NULL || ring_size == NULL || valid == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    if (length != R1_NV_RECOVERY_RING_SIZE_BYTES) {
        return R1_ERROR_LENGTH;
    }
    *ring_size = input[0];
    *valid = ring_size_valid(input[0]);
    return R1_OK;
}
