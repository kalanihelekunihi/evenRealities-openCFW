/*
 * SPDX-License-Identifier: MIT
 *
 * Source-image integration boundary. The complete command/report, gesture,
 * policy, storage, and application source graph is linked into the image.
 * Physical SCB1/MSCLP/flash routing is evidence-locked rather than guessed.
 */
#include "firmware_image.h"

#include "runtime_touch_policy_helpers.h"

open_cfw_touch_firmware_state open_cfw_touch_firmware;

static uint16_t image_sensor_read(void *context, uint8_t channel)
{
    open_cfw_touch_firmware_state *state = context;
    return channel < 2U ? state->samples[channel] : 0U;
}

static int image_config_save(
    void *context, const open_cfw_touch_config *configuration)
{
    open_cfw_touch_firmware_state *state = context;
    if (configuration == 0) {
        return 0;
    }
    state->protocol.config = *configuration;
    return 1;
}

static void image_attention_set(void *context, int asserted_low)
{
    open_cfw_touch_firmware_state *state = context;
    state->attention_asserted = asserted_low != 0 ? 1U : 0U;
}

static void image_dfu_request(void *context, uint8_t mode)
{
    open_cfw_touch_firmware_state *state = context;
    if (mode <= 1U) {
        state->dfu_requested = 1U;
    }
}

static int image_event_dispatch(
    void *context, uint8_t event, const uint8_t payload[3])
{
    open_cfw_touch_firmware_state *state = context;
    state->last_event[0] = event;
    state->last_event[1] = payload[0];
    state->last_event[2] = payload[1];
    state->last_event[3] = payload[2];
    return 1;
}

static open_cfw_touch_port image_port(void)
{
    open_cfw_touch_port port;
    port.sensor_read = image_sensor_read;
    port.config_save = image_config_save;
    port.attention_set = image_attention_set;
    port.enter_dfu_and_reset = image_dfu_request;
    port.event_dispatch = image_event_dispatch;
    port.context = &open_cfw_touch_firmware;
    return port;
}

static void image_initialize(void)
{
    open_cfw_touch_policy_state policy;

    open_cfw_touch_protocol_init(&open_cfw_touch_firmware.protocol, 0);
    open_cfw_touch_policy_defaults(&policy);
    open_cfw_touch_gesture_init(
        &open_cfw_touch_firmware.gesture,
        policy.timeout_ms,
        1U);
    open_cfw_touch_firmware.power = OPEN_CFW_TOUCH_POWER_ACT;
    open_cfw_touch_firmware.qualification =
        OPEN_CFW_TOUCH_IMAGE_HARDWARE_BLOCKED;
    open_cfw_touch_firmware.initialized = 1U;
}

int open_cfw_touch_firmware_main(void)
{
    image_initialize();
    for (;;) {
        if (open_cfw_touch_firmware.protocol.report_timeout != 0U) {
            --open_cfw_touch_firmware.protocol.report_timeout;
        }
        __asm volatile("wfi");
    }
}

int open_cfw_touch_firmware_service_command(
    const uint8_t *request, size_t request_size)
{
    open_cfw_touch_port port = image_port();
    if (open_cfw_touch_firmware.initialized == 0U) {
        image_initialize();
    }
    return open_cfw_touch_handle_command(
        &open_cfw_touch_firmware.protocol, request, request_size, &port);
}

void open_cfw_touch_firmware_publish(
    uint8_t event, const uint8_t payload[3])
{
    open_cfw_touch_port port = image_port();
    open_cfw_touch_build_report(
        &open_cfw_touch_firmware.protocol, event, payload, &port);
}

void open_cfw_touch_firmware_set_sample(uint8_t channel, uint16_t value)
{
    if (channel < 2U) {
        open_cfw_touch_firmware.samples[channel] = value;
    }
}

const uint8_t *open_cfw_touch_firmware_tx_buffer(void)
{
    return open_cfw_touch_firmware.protocol.tx;
}

void open_cfw_touch_firmware_tx_complete(void)
{
    open_cfw_touch_port port = image_port();
    open_cfw_touch_tx_complete(&open_cfw_touch_firmware.protocol, &port);
}
