/* SPDX-License-Identifier: MIT */
/* Host behavior fixture for the clean-room touch-controller protocol. */
#include <stdint.h>

#include "../../components/shared/touch/runtime_touch_i2c_protocol.c"

typedef struct touch_fixture {
    uint32_t sensor_calls;
    uint32_t save_calls;
    uint32_t attention_asserts;
    uint32_t attention_releases;
    uint32_t dfu_calls;
    uint32_t event_calls;
    uint16_t saved_baseline;
    uint8_t last_event;
} touch_fixture;

static uint16_t sensor(void *context, uint8_t channel)
{
    touch_fixture *fixture = context;
    ++fixture->sensor_calls;
    return (uint16_t)(0x1200U + channel);
}

static int save(void *context, const open_cfw_touch_config *config)
{
    touch_fixture *fixture = context;
    ++fixture->save_calls;
    fixture->saved_baseline = config->proximity_baseline;
    return 1;
}

static void attention(void *context, int asserted)
{
    touch_fixture *fixture = context;
    if (asserted != 0) ++fixture->attention_asserts;
    else ++fixture->attention_releases;
}

static void dfu(void *context, uint8_t mode)
{
    touch_fixture *fixture = context;
    if (mode == 0U) ++fixture->dfu_calls;
}

static int event(void *context, uint8_t value, const uint8_t payload[3])
{
    touch_fixture *fixture = context;
    ++fixture->event_calls;
    fixture->last_event = value;
    return payload[0] == 1U && payload[1] == 2U && payload[2] == 3U;
}

static open_cfw_touch_port make_port(touch_fixture *fixture)
{
    open_cfw_touch_port port = {sensor, save, attention, dfu, event, fixture};
    return port;
}

uint32_t open_cfw_test_touch_init_commands(void)
{
    open_cfw_touch_protocol state;
    touch_fixture fixture = {0};
    open_cfw_touch_port port = make_port(&fixture);
    uint8_t rx[16] = {0};
    uint32_t result = 0U;

    open_cfw_touch_protocol_init(&state, 0);
    result |= state.config.magic == OPEN_CFW_TOUCH_CONFIG_MAGIC &&
              state.config.long_press_ms == 1000U ? 1U : 0U;
    result |= state.tx[0] == 0x5AU && state.tx[15] == 0x5AU ? 2U : 0U;
    rx[0] = 0U;
    result |= open_cfw_touch_handle_command(&state, rx, 1U, &port) == 0 &&
              state.tx[0] == 2U && state.tx[7] == 2U ? 4U : 0U;
    state.config.proximity_baseline = 0x3456U;
    rx[0] = 1U;
    result |= open_cfw_touch_handle_command(&state, rx, 1U, &port) == 0 &&
              state.tx[3] == 0x56U && state.tx[4] == 0x34U ? 8U : 0U;
    rx[0] = 4U; rx[1] = 0U; rx[2] = 0U;
    open_cfw_touch_handle_command(&state, rx, 3U, &port);
    result |= state.tx[0] == 7U && state.tx[1] == 0xFFU ? 16U : 0U;
    rx[1] = 0x34U; rx[2] = 0x12U;
    open_cfw_touch_handle_command(&state, rx, 3U, &port);
    result |= state.config.long_press_ms == 0x1234U &&
              state.gesture_dirty_primary == 1U &&
              state.gesture_dirty_secondary == 1U ? 32U : 0U;
    rx[0] = 5U;
    open_cfw_touch_handle_command(&state, rx, 1U, &port);
    result |= fixture.dfu_calls == 1U && state.tx[2] == 0x17U ? 64U : 0U;
    rx[0] = 6U;
    open_cfw_touch_handle_command(&state, rx, 1U, &port);
    result |= fixture.sensor_calls == 2U && state.tx[1] == 0U &&
              state.tx[2] == 0x12U && state.tx[3] == 1U ? 128U : 0U;
    return result;
}

uint32_t open_cfw_test_touch_report_persistence(void)
{
    open_cfw_touch_protocol state;
    touch_fixture fixture = {0};
    open_cfw_touch_port port = make_port(&fixture);
    uint8_t payload[3] = {1U, 2U, 3U};
    uint32_t result = 0U;

    open_cfw_touch_protocol_init(&state, 0);
    state.config.proximity_baseline = 100U;
    state.current_baseline = 149U;
    state.current_channel = 0x2233U;
    state.current_proximity = 0x4455U;
    state.current_gesture = 0x6677U;
    state.save_baseline_pending = 1U;
    open_cfw_touch_build_report(&state, 4U, payload, &port);
    result |= fixture.save_calls == 0U && state.config.proximity_baseline == 100U ? 1U : 0U;
    result |= state.report[0] == 4U && state.report[1] == 1U &&
              state.report[6] == 0x33U && state.report[11] == 0x66U ? 2U : 0U;
    result |= state.report_pending == 1U && state.report_timeout == 0x280U &&
              fixture.attention_asserts == 1U ? 4U : 0U;
    state.current_baseline = 150U;
    state.save_baseline_pending = 1U;
    open_cfw_touch_build_report(&state, 5U, payload, &port);
    result |= fixture.save_calls == 1U && fixture.saved_baseline == 150U &&
              state.config.proximity_baseline == 150U ? 8U : 0U;
    open_cfw_touch_tx_complete(&state, &port);
    result |= state.report_pending == 0U && state.report_timeout == 0U &&
              state.tx[0] == 0x5AU && state.tx[15] == 0x5AU &&
              fixture.attention_releases == 1U ? 16U : 0U;
    return result;
}

uint32_t open_cfw_test_touch_event_fifo_power(void)
{
    touch_fixture fixture = {0};
    open_cfw_touch_port port = make_port(&fixture);
    open_cfw_touch_fifo fifo;
    uint8_t buffer[16];
    uint8_t payload[3] = {1U, 2U, 3U};
    uint32_t result = 0U;
    result |= open_cfw_touch_dispatch_event(&port, 7U, payload) == 1 &&
              fixture.event_calls == 1U && fixture.last_event == 7U ? 1U : 0U;
    result |= open_cfw_touch_dispatch_event(&port, 8U, payload) == 0 ? 2U : 0U;
    open_cfw_touch_fifo_arm(&fifo, buffer, 16U);
    fifo.position = 9U;
    result |= fifo.buffer == buffer && fifo.capacity == 16U &&
              open_cfw_touch_fifo_position(&fifo) == 9U ? 4U : 0U;
    result |= open_cfw_touch_power_mode_valid(0x20U) == 1 &&
              open_cfw_touch_power_mode_valid(0x21U) == 0 ? 8U : 0U;
    return result;
}
