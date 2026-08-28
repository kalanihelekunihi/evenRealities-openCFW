/*
 * SPDX-License-Identifier: MIT OR GPL-3.0-only
 *
 * Clean-room device-side G2 touch I2C protocol. The command/report behavior
 * is reconstructed from authenticated PSoC 4000T machine code. Resident HAL,
 * boot, switch-table, and DFU-engine bytes are intentionally represented only
 * by explicit ports.
 */
#include "runtime_touch_i2c_protocol.h"

static void open_cfw_touch_clear(uint8_t *bytes, size_t size, uint8_t value)
{
    size_t index;
    for (index = 0U; index < size; ++index) {
        bytes[index] = value;
    }
}

static void open_cfw_touch_put_u16(uint8_t *bytes, uint16_t value)
{
    bytes[0] = (uint8_t)value;
    bytes[1] = (uint8_t)(value >> 8);
}

static uint16_t open_cfw_touch_get_u16(const uint8_t *bytes)
{
    return (uint16_t)((uint16_t)bytes[0] | ((uint16_t)bytes[1] << 8));
}

static void open_cfw_touch_reply(open_cfw_touch_protocol *state,
                                 uint8_t reply, uint8_t status)
{
    open_cfw_touch_clear(state->tx, sizeof(state->tx), 0U);
    state->tx[0] = reply;
    state->tx[1] = status;
    state->tx[2] = 0x17U;
}

void open_cfw_touch_protocol_init(open_cfw_touch_protocol *state,
                                  const open_cfw_touch_config *stored)
{
    if (state == NULL) {
        return;
    }
    open_cfw_touch_clear((uint8_t *)state, sizeof(*state), 0U);
    open_cfw_touch_clear(state->tx, sizeof(state->tx), 0x5AU);
    if (stored != NULL && stored->magic == OPEN_CFW_TOUCH_CONFIG_MAGIC) {
        state->config = *stored;
    } else {
        state->config.magic = OPEN_CFW_TOUCH_CONFIG_MAGIC;
        state->config.proximity_baseline = 0U;
        state->config.long_press_ms = 1000U;
    }
}

int open_cfw_touch_handle_command(open_cfw_touch_protocol *state,
                                  const uint8_t *rx, size_t rx_length,
                                  const open_cfw_touch_port *port)
{
    uint8_t command;
    uint16_t value;

    if (state == NULL || rx == NULL) {
        return OPEN_CFW_TOUCH_COMMAND_BAD_ARGUMENT;
    }
    if (rx_length < 1U || rx_length > OPEN_CFW_TOUCH_FRAME_SIZE) {
        return OPEN_CFW_TOUCH_COMMAND_BAD_LENGTH;
    }
    command = rx[0];
    if (command > 8U) {
        return OPEN_CFW_TOUCH_COMMAND_IGNORED;
    }
    switch (command) {
    case 0U:
        open_cfw_touch_clear(state->tx, sizeof(state->tx), 0U);
        state->tx[0] = 2U;
        state->tx[1] = 2U;
        state->tx[2] = 0U;
        state->tx[3] = 1U;
        state->tx[4] = 1U;
        state->tx[5] = 0U;
        state->tx[6] = 2U;
        state->tx[7] = 2U;
        break;
    case 1U:
        open_cfw_touch_reply(state, 3U, 0U);
        open_cfw_touch_put_u16(&state->tx[3], state->config.proximity_baseline);
        break;
    case 2U:
        open_cfw_touch_reply(state, 4U, 0U);
        open_cfw_touch_put_u16(&state->tx[3], state->config.long_press_ms);
        break;
    case 3U:
        state->save_baseline_pending = 1U;
        open_cfw_touch_reply(state, 5U, 0U);
        break;
    case 4U:
        if (rx_length < 3U) {
            return OPEN_CFW_TOUCH_COMMAND_BAD_LENGTH;
        }
        value = open_cfw_touch_get_u16(&rx[1]);
        if (value == 0U) {
            open_cfw_touch_reply(state, 7U, 0xFFU);
            break;
        }
        state->config.long_press_ms = value;
        state->gesture_dirty_primary = 1U;
        state->gesture_dirty_secondary = 1U;
        open_cfw_touch_reply(state, 7U, 0U);
        break;
    case 5U:
        open_cfw_touch_reply(state, 2U, 0U);
        if (port != NULL && port->enter_dfu_and_reset != NULL) {
            port->enter_dfu_and_reset(port->context, 0U);
        }
        break;
    case 6U:
        open_cfw_touch_clear(state->tx, sizeof(state->tx), 0U);
        state->tx[0] = 8U;
        if (port != NULL && port->sensor_read != NULL) {
            open_cfw_touch_put_u16(&state->tx[1],
                                   port->sensor_read(port->context, 0U));
            open_cfw_touch_put_u16(&state->tx[3],
                                   port->sensor_read(port->context, 1U));
        }
        break;
    case 7U:
    case 8U:
    default:
        return OPEN_CFW_TOUCH_COMMAND_IGNORED;
    }
    return OPEN_CFW_TOUCH_COMMAND_OK;
}

void open_cfw_touch_build_report(open_cfw_touch_protocol *state,
                                 uint8_t event, const uint8_t payload[3],
                                 const open_cfw_touch_port *port)
{
    uint16_t difference;

    if (state == NULL || payload == NULL) {
        return;
    }
    open_cfw_touch_clear(state->report, sizeof(state->report), 0U);
    state->report[0] = event;
    state->report[1] = payload[0];
    state->report[2] = payload[1];
    state->report[3] = payload[2];
    open_cfw_touch_put_u16(&state->report[4], state->current_baseline);
    open_cfw_touch_put_u16(&state->report[6], state->current_channel);
    open_cfw_touch_put_u16(&state->report[8], state->current_proximity);
    open_cfw_touch_put_u16(&state->report[10], state->current_gesture);

    if (state->save_baseline_pending != 0U) {
        difference = state->current_baseline >= state->config.proximity_baseline
            ? (uint16_t)(state->current_baseline - state->config.proximity_baseline)
            : (uint16_t)(state->config.proximity_baseline - state->current_baseline);
        if (difference > 49U && port != NULL && port->config_save != NULL) {
            open_cfw_touch_config next = state->config;
            next.proximity_baseline = state->current_baseline;
            if (port->config_save(port->context, &next) != 0) {
                state->config = next;
            }
        }
        state->save_baseline_pending = 0U;
    }
    open_cfw_touch_clear(state->tx, sizeof(state->tx), 0U);
    {
        size_t index;
        for (index = 0U; index < sizeof(state->tx); ++index) {
            state->tx[index] = state->report[index];
        }
    }
    state->report_pending = 1U;
    state->report_timeout = OPEN_CFW_TOUCH_REPORT_TIMEOUT;
    if (port != NULL && port->attention_set != NULL) {
        port->attention_set(port->context, 1);
    }
}

void open_cfw_touch_tx_complete(open_cfw_touch_protocol *state,
                                const open_cfw_touch_port *port)
{
    if (state == NULL) {
        return;
    }
    open_cfw_touch_clear(state->tx, sizeof(state->tx), 0x5AU);
    state->report_pending = 0U;
    state->report_timeout = 0U;
    if (port != NULL && port->attention_set != NULL) {
        port->attention_set(port->context, 0);
    }
}

int open_cfw_touch_dispatch_event(const open_cfw_touch_port *port,
                                  uint8_t event, const uint8_t payload[3])
{
    if (port == NULL || port->event_dispatch == NULL || payload == NULL ||
        event > 7U) {
        return 0;
    }
    return port->event_dispatch(port->context, event, payload);
}

void open_cfw_touch_fifo_arm(open_cfw_touch_fifo *fifo, uint8_t *buffer,
                             uint16_t capacity)
{
    if (fifo == NULL) {
        return;
    }
    fifo->buffer = buffer;
    fifo->capacity = capacity;
    fifo->position = 0U;
}

uint16_t open_cfw_touch_fifo_position(const open_cfw_touch_fifo *fifo)
{
    return fifo == NULL ? 0U : fifo->position;
}

int open_cfw_touch_power_mode_valid(uint8_t mode)
{
    return mode <= 0x20U;
}
