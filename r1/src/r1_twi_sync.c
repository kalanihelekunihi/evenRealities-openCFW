#include "openr1/r1_twi_sync.h"

void r1_twi_i2c5_delay_noop(uint32_t delay_units) {
    (void)delay_units;
}

static bool operations_valid(const r1_twi_sync_ops *ops) {
    return ops != NULL && ops->kernel_state != NULL &&
        ops->tick_frequency != NULL && ops->semaphore_acquire != NULL &&
        ops->semaphore_release != NULL && ops->delay_us != NULL;
}

static bool kernel_can_block(uint32_t state) {
    return state == 2u || state == 3u;
}

r1_error r1_twi_sync_complete(
    r1_twi_sync_state *state, uint8_t event_type,
    const r1_twi_sync_ops *ops) {
    if (state == NULL || !operations_valid(ops)) {
        return R1_ERROR_ARGUMENT;
    }

    state->completed = true;
    if (event_type == (uint8_t)R1_TWI_SYNC_EVENT_DONE) {
        state->status = R1_TWI_SYNC_STATUS_OK;
    } else {
        state->failed = true;
        if (event_type == (uint8_t)R1_TWI_SYNC_EVENT_ADDRESS_NACK) {
            state->status = R1_TWI_SYNC_STATUS_ADDRESS_NACK;
        } else if (event_type == (uint8_t)R1_TWI_SYNC_EVENT_DATA_NACK) {
            state->status = R1_TWI_SYNC_STATUS_DATA_NACK;
        }
    }

    if (state->semaphore_enabled && state->semaphore != NULL &&
        kernel_can_block(ops->kernel_state(ops->context))) {
        ops->semaphore_release(ops->context, state->semaphore);
    }
    return R1_OK;
}

uint32_t r1_twi_sync_wait(
    r1_twi_sync_state *state, uint32_t timeout_ms,
    const r1_twi_sync_ops *ops) {
    if (state == NULL || !operations_valid(ops)) {
        return R1_TWI_SYNC_STATUS_ARGUMENT;
    }

    if (state->semaphore_enabled && state->semaphore != NULL &&
        kernel_can_block(ops->kernel_state(ops->context))) {
        uint32_t ticks = (timeout_ms * ops->tick_frequency(ops->context)) /
            UINT32_C(1000);
        if (ticks == 0u) {
            ticks = 1u;
        }
        if (ops->semaphore_acquire(
                ops->context, state->semaphore, ticks) != 0) {
            return R1_TWI_SYNC_STATUS_TIMEOUT;
        }
    } else {
        uint32_t iteration = 0u;
        const uint32_t iteration_limit = timeout_ms * UINT32_C(1000);
        while (!state->completed) {
            if (iteration_limit <= iteration) {
                return R1_TWI_SYNC_STATUS_TIMEOUT;
            }
            ops->delay_us(ops->context, R1_TWI_SYNC_DELAY_US);
            iteration += 1u;
        }
    }
    return state->status;
}

static bool transfer_operations_valid(const r1_twi_transfer_ops *ops) {
    return ops != NULL && ops->transmit != NULL && ops->receive != NULL &&
        ops->fatal_error != NULL && operations_valid(ops->sync);
}

static uint32_t register_read(
    r1_twi_sync_state *state, void *bus, uint8_t address, uint8_t reg,
    uint8_t *data, uint32_t length, uint32_t address_timeout_ms,
    bool clear_failed, bool truncate_receive_length,
    const r1_twi_transfer_ops *ops) {
    uint32_t status;
    uint32_t receive_length;
    uint32_t data_timeout_ms;

    if (state == NULL || bus == NULL || data == NULL ||
        !transfer_operations_valid(ops)) {
        return R1_TWI_SYNC_STATUS_ARGUMENT;
    }

    state->completed = false;
    if (clear_failed) {
        state->failed = false;
    }
    status = ops->transmit(
        ops->context, bus, address, &reg, 1u, true);
    if (status != R1_TWI_SYNC_STATUS_OK) {
        return status & UINT32_C(0xff);
    }
    status = r1_twi_sync_wait(state, address_timeout_ms, ops->sync);
    if (status != R1_TWI_SYNC_STATUS_OK) {
        return status & UINT32_C(0xff);
    }

    state->completed = false;
    receive_length = truncate_receive_length ?
        (uint32_t)(uint8_t)length : length;
    status = ops->receive(
        ops->context, bus, address, data, receive_length);
    if (status != R1_TWI_SYNC_STATUS_OK) {
        return status & UINT32_C(0xff);
    }
    data_timeout_ms = length < UINT32_C(50) ? UINT32_C(200) : UINT32_C(500);
    return r1_twi_sync_wait(state, data_timeout_ms, ops->sync) & UINT32_C(0xff);
}

static uint32_t register_write(
    r1_twi_sync_state *state, void *bus, uint8_t address, uint8_t reg,
    const uint8_t *data, uint32_t length, uint32_t timeout_ms,
    bool clear_failed, const r1_twi_transfer_ops *ops) {
    uint8_t frame[R1_TWI_WRITE_DATA_MAX + 1u];
    uint32_t index;

    if (state == NULL || bus == NULL ||
        (data == NULL && length != 0u) || !transfer_operations_valid(ops)) {
        return R1_TWI_SYNC_STATUS_ARGUMENT;
    }
    if (length > R1_TWI_WRITE_DATA_MAX) {
        return R1_TWI_SYNC_STATUS_DATA_SIZE;
    }

    frame[0] = reg;
    for (index = 0u; index < length; ++index) {
        frame[index + 1u] = data[index];
    }
    state->completed = false;
    if (clear_failed) {
        state->failed = false;
    }

    for (;;) {
        const uint32_t status = ops->transmit(
            ops->context, bus, address, frame, length + 1u, false);
        if (status == R1_TWI_SYNC_STATUS_BUSY) {
            return status;
        }
        if (status == R1_TWI_SYNC_STATUS_OK) {
            return r1_twi_sync_wait(state, timeout_ms, ops->sync) &
                UINT32_C(0xff);
        }
        ops->fatal_error(ops->context, status);
    }
}

uint32_t r1_twi_primary_register_read(
    r1_twi_sync_state *state, void *bus, uint8_t address, uint8_t reg,
    uint8_t *data, uint32_t length, const r1_twi_transfer_ops *ops) {
    return register_read(
        state, bus, address, reg, data, length, UINT32_C(500), true, true,
        ops);
}

uint32_t r1_twi_primary_register_write(
    r1_twi_sync_state *state, void *bus, uint8_t address, uint8_t reg,
    const uint8_t *data, uint32_t length, const r1_twi_transfer_ops *ops) {
    return register_write(
        state, bus, address, reg, data, length, UINT32_C(500), true, ops);
}

uint32_t r1_twi_secondary_register_read(
    r1_twi_sync_state *state, void *bus, uint8_t address, uint8_t reg,
    uint8_t *data, uint32_t length, const r1_twi_transfer_ops *ops) {
    return register_read(
        state, bus, address, reg, data, length, UINT32_C(100), false, false,
        ops);
}

uint32_t r1_twi_secondary_register_write(
    r1_twi_sync_state *state, void *bus, uint8_t address, uint8_t reg,
    const uint8_t *data, uint32_t length, const r1_twi_transfer_ops *ops) {
    return register_write(
        state, bus, address, reg, data, length, UINT32_C(200), false, ops);
}

static bool lifecycle_operations_valid(const r1_twi_lifecycle_ops *ops) {
    return ops != NULL && ops->configure_pin != NULL &&
        ops->initialize != NULL && ops->enable != NULL &&
        ops->disable != NULL && ops->uninitialize != NULL &&
        ops->power_cycle != NULL;
}

uint32_t r1_twi_lifecycle_initialize(
    r1_twi_lifecycle_state *state, void *bus,
    const r1_twi_lifecycle_config *config,
    const r1_twi_lifecycle_ops *ops) {
    uint32_t status;

    if (state == NULL || bus == NULL || config == NULL ||
        !lifecycle_operations_valid(ops)) {
        return R1_TWI_SYNC_STATUS_ARGUMENT;
    }
    if (state->initialized) {
        return R1_TWI_SYNC_STATUS_OK;
    }

    if (config->preconfigure_pins) {
        ops->configure_pin(ops->context, config->scl_pin);
        ops->configure_pin(ops->context, config->sda_pin);
    }
    status = ops->initialize(
        ops->context, bus, config, state->transfer_state);
    if (status != R1_TWI_SYNC_STATUS_OK) {
        return status;
    }
    ops->enable(ops->context, bus);
    state->initialized = true;
    return R1_TWI_SYNC_STATUS_OK;
}

uint32_t r1_twi_primary_lifecycle_initialize(
    r1_twi_lifecycle_state *state, void *bus,
    uint32_t scl_pin, uint32_t sda_pin,
    const r1_twi_lifecycle_ops *ops) {
    const r1_twi_lifecycle_config config = {
        .scl_pin = scl_pin,
        .sda_pin = sda_pin,
        .frequency = UINT32_C(0x06680000),
        .interrupt_priority = 2u,
        .clear_bus_init = false,
        .hold_bus_uninit = true,
        .preconfigure_pins = true,
    };
    return r1_twi_lifecycle_initialize(state, bus, &config, ops);
}

uint32_t r1_twi_secondary_lifecycle_initialize(
    r1_twi_lifecycle_state *state, void *bus,
    uint32_t scl_pin, uint32_t sda_pin,
    const r1_twi_lifecycle_ops *ops) {
    const r1_twi_lifecycle_config config = {
        .scl_pin = scl_pin,
        .sda_pin = sda_pin,
        .frequency = UINT32_C(0x06680000),
        .interrupt_priority = 2u,
        .clear_bus_init = false,
        .hold_bus_uninit = false,
        .preconfigure_pins = false,
    };
    return r1_twi_lifecycle_initialize(state, bus, &config, ops);
}

uint32_t r1_twi_lifecycle_shutdown(
    r1_twi_lifecycle_state *state, void *bus,
    const r1_twi_lifecycle_ops *ops) {
    if (state == NULL || bus == NULL || !lifecycle_operations_valid(ops)) {
        return R1_TWI_SYNC_STATUS_ARGUMENT;
    }
    if (state->initialized) {
        ops->disable(ops->context, bus);
        ops->uninitialize(ops->context, bus);
        ops->power_cycle(ops->context, bus);
        state->initialized = false;
    }
    return R1_TWI_SYNC_STATUS_OK;
}

uint32_t r1_twi_software_lifecycle_shutdown(
    r1_twi_software_lifecycle_state *state,
    const r1_twi_software_lifecycle_ops *ops) {
    if (state == NULL || ops == NULL || ops->release_pin == NULL) {
        return R1_TWI_SYNC_STATUS_ARGUMENT;
    }
    if (state->initialized) {
        ops->release_pin(ops->context, state->scl_pin);
        ops->release_pin(ops->context, state->sda_pin);
        state->initialized = false;
    }
    return R1_TWI_SYNC_STATUS_OK;
}
