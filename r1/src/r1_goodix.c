#include "openr1/r1_goodix.h"

#include <stddef.h>

void r1_goodix_pool_fill(void *destination, size_t length) {
    if (destination == NULL) {
        return;
    }
    uint8_t *bytes = destination;
    for (size_t index = 0u; index < length; ++index) {
        bytes[index] = 0u;
    }
}

void r1_goodix_pool_not_enough(const r1_goodix_pool_fatal_ops *ops,
                               uint32_t info1) {
    if (ops == NULL) {
        return;
    }
    if (ops->record != NULL) {
        ops->record(ops->context, info1);
    }
    if (ops->halt != NULL) {
        ops->halt(ops->context);
    }
}

static const r1_sensor_stream_registration sensor_stream_registrations[] = {
    {"hr", 4u, 1u, true},
    {"spo2", 6u, 2u, true},
    {"raw_hr", 124u, 5u, true},
    {"wear", 2u, 3u, true},
    {"gray", 12u, 8u, true},
    {"aging", 12u, 9u, true},
    {"hrv", 10u, 4u, true},
    {"adt", 24u, 7u, true},
};

r1_error r1_sensor_stream_registration_plan(
    r1_sensor_stream_registration_plan_result *plan) {
    if (plan == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *plan = (r1_sensor_stream_registration_plan_result){
        .initialize_goodix = true,
        .clear_state = true,
        .clear_bytes = R1_SENSOR_STREAM_STATE_BYTES,
        .callback_count = R1_SENSOR_STREAM_CALLBACK_COUNT,
    };
    for (size_t index = 0u; index < R1_SENSOR_STREAM_REGISTRATION_COUNT;
         ++index) {
        plan->registrations[index] = sensor_stream_registrations[index];
    }
    return R1_OK;
}

static uint32_t diagnostic_u32(const uint8_t *bytes) {
    return (uint32_t)bytes[0] | ((uint32_t)bytes[1] << 8u) |
        ((uint32_t)bytes[2] << 16u) | ((uint32_t)bytes[3] << 24u);
}

static void diagnostic_write_u32(uint8_t *bytes, uint32_t value) {
    bytes[0] = (uint8_t)value;
    bytes[1] = (uint8_t)(value >> 8u);
    bytes[2] = (uint8_t)(value >> 16u);
    bytes[3] = (uint8_t)(value >> 24u);
}

_Static_assert(R1_GOODIX_RAW_HR_RECORD_BYTES ==
                   4u + R1_GOODIX_RAW_HR_VALUE_CAPACITY * 4u,
               "raw_hr record layout changed");
_Static_assert(R1_GOODIX_ADT_RECORD_BYTES ==
                   4u + R1_GOODIX_ADT_VALUE_CAPACITY * 4u,
               "adt record layout changed");
_Static_assert(R1_GOODIX_WEAR_RECORD_BYTES == 2u,
               "wear record layout changed");

static bool append_bounded_u32(uint8_t *record, uint8_t capacity,
                               uint32_t value) {
    if (record == NULL || record[0] >= capacity) {
        return false;
    }
    const uint8_t count = record[0];
    diagnostic_write_u32(&record[4u + (size_t)count * 4u], value);
    record[0] = (uint8_t)(count + 1u);
    return true;
}

bool r1_goodix_raw_hr_append(
    uint8_t record[R1_GOODIX_RAW_HR_RECORD_BYTES], uint32_t value) {
    return append_bounded_u32(record, R1_GOODIX_RAW_HR_VALUE_CAPACITY,
                              value);
}

bool r1_goodix_adt_append(uint8_t record[R1_GOODIX_ADT_RECORD_BYTES],
                          uint32_t value) {
    return append_bounded_u32(record, R1_GOODIX_ADT_VALUE_CAPACITY, value);
}

void r1_goodix_wear_living_object_update(
    uint8_t record[R1_GOODIX_WEAR_RECORD_BYTES], uint8_t value) {
    if (record == NULL) {
        return;
    }
    record[1] = value;
    record[0] = 1u;
}

static r1_error diagnostic_copy(
    const uint8_t *source, size_t length, uint8_t *output,
    size_t output_capacity, size_t *written) {
    if (output_capacity < length) {
        return R1_ERROR_CAPACITY;
    }
    for (size_t index = 0u; index < length; ++index) {
        output[index] = source[index];
    }
    *written = length;
    return R1_OK;
}

bool r1_goodix_diagnostic_refresh_due(uint32_t now_tick,
                                      uint32_t previous_refresh_tick) {
    return previous_refresh_tick == 0u ||
        previous_refresh_tick + R1_GOODIX_DIAGNOSTIC_REFRESH_TICKS <= now_tick;
}

r1_error r1_goodix_diagnostic_select(
    uint8_t snapshot[R1_GOODIX_DIAGNOSTIC_SNAPSHOT_BYTES], uint8_t selector,
    uint8_t *output, size_t output_capacity, size_t *written) {
    if (snapshot == NULL || output == NULL || written == NULL) {
        return R1_ERROR_ARGUMENT;
    }
    *written = 0u;
    switch (selector) {
        case 1u: {
            const uint32_t primary = diagnostic_u32(snapshot);
            if (primary < 41u || primary > 219u) {
                return R1_OK;
            }
            if (output_capacity < 4u) {
                return R1_ERROR_CAPACITY;
            }
            for (size_t index = 0u; index < 4u; ++index) {
                output[index] = snapshot[index * 4u];
            }
            *written = 4u;
            return R1_OK;
        }
        case 2u:
            if (diagnostic_u32(snapshot + 40u) == 0u) {
                return R1_OK;
            }
            if (output_capacity < 6u) {
                return R1_ERROR_CAPACITY;
            }
            for (size_t index = 0u; index < 6u; ++index) {
                output[index] = snapshot[40u + index * 4u];
            }
            *written = 6u;
            return R1_OK;
        case 3u:
            if (snapshot[188u] != 1u) {
                return R1_OK;
            }
            if (output_capacity < 2u) {
                return R1_ERROR_CAPACITY;
            }
            snapshot[188u] = 0u;
            output[0] = snapshot[188u];
            output[1] = snapshot[189u];
            *written = 2u;
            return R1_OK;
        case 4u:
            if (diagnostic_u32(snapshot + 16u) == 0u) {
                return R1_OK;
            }
            if (output_capacity < 10u) {
                return R1_ERROR_CAPACITY;
            }
            for (size_t index = 0u; index < 4u; ++index) {
                output[index * 2u] = snapshot[16u + index * 4u];
                output[index * 2u + 1u] = snapshot[17u + index * 4u];
            }
            output[8] = snapshot[32u];
            output[9] = snapshot[36u];
            *written = 10u;
            return R1_OK;
        case 5u:
            return diagnostic_copy(snapshot + 64u, 124u, output,
                                   output_capacity, written);
        case 7u:
            return diagnostic_copy(snapshot + 216u, 24u, output,
                                   output_capacity, written);
        case 8u:
            return diagnostic_copy(snapshot + 192u, 12u, output,
                                   output_capacity, written);
        case 9u:
            return diagnostic_copy(snapshot + 204u, 12u, output,
                                   output_capacity, written);
        default:
            return R1_OK;
    }
}

static bool provider_complete(const r1_goodix_provider_ops *provider) {
    return provider != NULL && provider->initialize != NULL &&
           provider->switch_configuration != NULL &&
           provider->start_sampling != NULL && provider->stop_sampling != NULL;
}

static bool board_complete(const r1_goodix_board_ops *board) {
    return board != NULL && board->prepare != NULL && board->shutdown != NULL &&
           board->delay_ms != NULL;
}

void r1_goodix_adapter_initialize(r1_goodix_adapter *adapter) {
    if (adapter == NULL) {
        return;
    }
    adapter->provider = NULL;
    adapter->provider_context = NULL;
    adapter->board = NULL;
    adapter->board_context = NULL;
    adapter->active_mask = 0u;
    adapter->initialized = false;
    adapter->prepared = false;
}

r1_error r1_goodix_adapter_bind(r1_goodix_adapter *adapter,
                                const r1_goodix_provider_ops *provider,
                                void *provider_context,
                                const r1_goodix_board_ops *board,
                                void *board_context) {
    if (adapter == NULL || !provider_complete(provider) || !board_complete(board)) {
        return R1_ERROR_ARGUMENT;
    }
    if (adapter->prepared || adapter->initialized || adapter->active_mask != 0u) {
        return R1_ERROR_STATE;
    }
    adapter->provider = provider;
    adapter->provider_context = provider_context;
    adapter->board = board;
    adapter->board_context = board_context;
    return R1_OK;
}

bool r1_goodix_provider_available(const r1_goodix_adapter *adapter) {
    return adapter != NULL && provider_complete(adapter->provider) &&
           board_complete(adapter->board);
}

static void shutdown_adapter(r1_goodix_adapter *adapter) {
    if (adapter->prepared) {
        adapter->board->shutdown(adapter->board_context);
    }
    adapter->prepared = false;
    adapter->initialized = false;
    adapter->active_mask = 0u;
}

static r1_error prepare_adapter(r1_goodix_adapter *adapter,
                                uint32_t delay_ms) {
    if (!r1_goodix_provider_available(adapter)) {
        return R1_ERROR_UNSUPPORTED;
    }
    if (!adapter->prepared) {
        if (!adapter->board->prepare(adapter->board_context)) {
            return R1_ERROR_STATE;
        }
        adapter->prepared = true;
    }
    adapter->board->delay_ms(adapter->board_context, delay_ms);
    return R1_OK;
}

r1_error r1_goodix_start_stock_profile(r1_goodix_adapter *adapter,
                                       r1_goodix_stock_profile profile) {
    uint32_t mask = 0u;
    if (profile == R1_GOODIX_STOCK_PROFILE_2000) {
        mask = R1_GOODIX_MASK_STOCK_2000;
    } else if (profile == R1_GOODIX_STOCK_PROFILE_4000) {
        mask = R1_GOODIX_MASK_STOCK_4000;
    } else {
        return R1_ERROR_ARGUMENT;
    }
    r1_error error = prepare_adapter(adapter, 10u);
    if (error != R1_OK) {
        return error;
    }
    if (!adapter->initialized) {
        if (adapter->provider->initialize(adapter->provider_context) != 0) {
            shutdown_adapter(adapter);
            return R1_ERROR_STATE;
        }
        adapter->initialized = true;
    }
    if (adapter->provider->start_sampling(adapter->provider_context, mask) != 0) {
        shutdown_adapter(adapter);
        return R1_ERROR_STATE;
    }
    adapter->active_mask |= mask;
    return R1_OK;
}

r1_error r1_goodix_switch_profile(r1_goodix_adapter *adapter,
                                  r1_goodix_switch_selection profile) {
    uint32_t mask = 0u;
    if (profile == R1_GOODIX_SWITCH_PROFILE_2) {
        mask = R1_GOODIX_MASK_SWITCH_2;
    } else if (profile == R1_GOODIX_SWITCH_PROFILE_40) {
        mask = R1_GOODIX_MASK_SWITCH_40;
    } else {
        return R1_ERROR_ARGUMENT;
    }
    if (!r1_goodix_provider_available(adapter)) {
        return R1_ERROR_UNSUPPORTED;
    }
    if (!adapter->initialized) {
        return R1_ERROR_STATE;
    }
    r1_error error = prepare_adapter(adapter, 100u);
    if (error != R1_OK) {
        return error;
    }
    if (adapter->provider->switch_configuration(adapter->provider_context, 0u) != 0 ||
        adapter->provider->stop_sampling(adapter->provider_context,
                                         R1_GOODIX_MASK_SWITCH_CLEAR) != 0) {
        shutdown_adapter(adapter);
        return R1_ERROR_STATE;
    }
    adapter->board->delay_ms(adapter->board_context, 10u);
    if (adapter->provider->start_sampling(adapter->provider_context, mask) != 0) {
        shutdown_adapter(adapter);
        return R1_ERROR_STATE;
    }
    adapter->active_mask = mask;
    return R1_OK;
}

r1_error r1_goodix_stop_stock_profiles(r1_goodix_adapter *adapter) {
    if (!r1_goodix_provider_available(adapter)) {
        return R1_ERROR_UNSUPPORTED;
    }
    if (!adapter->initialized) {
        return R1_ERROR_STATE;
    }
    const int32_t first = adapter->provider->stop_sampling(
        adapter->provider_context, R1_GOODIX_MASK_STOCK_2000);
    const int32_t second = adapter->provider->stop_sampling(
        adapter->provider_context, R1_GOODIX_MASK_STOCK_4000);
    shutdown_adapter(adapter);
    return first == 0 && second == 0 ? R1_OK : R1_ERROR_STATE;
}
