/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_FIRMWARE_IMAGE_H
#define OPENCFW_TOUCH_FIRMWARE_IMAGE_H

#include <stddef.h>
#include <stdint.h>

#include "runtime_touch_i2c_protocol.h"
#include "runtime_touch_sensing.h"

typedef enum open_cfw_touch_image_qualification {
    OPEN_CFW_TOUCH_IMAGE_HARDWARE_BLOCKED = 0,
    OPEN_CFW_TOUCH_IMAGE_HARDWARE_AUTHORIZED = 1
} open_cfw_touch_image_qualification;

typedef struct open_cfw_touch_firmware_state {
    open_cfw_touch_protocol protocol;
    open_cfw_touch_gesture_state gesture;
    open_cfw_touch_power_state power;
    uint16_t samples[2];
    uint8_t last_event[4];
    uint8_t attention_asserted;
    uint8_t dfu_requested;
    uint8_t initialized;
    open_cfw_touch_image_qualification qualification;
} open_cfw_touch_firmware_state;

extern open_cfw_touch_firmware_state open_cfw_touch_firmware;

int open_cfw_touch_firmware_main(void);
int open_cfw_touch_firmware_service_command(
    const uint8_t *request, size_t request_size);
void open_cfw_touch_firmware_publish(
    uint8_t event, const uint8_t payload[3]);
void open_cfw_touch_firmware_set_sample(uint8_t channel, uint16_t value);
const uint8_t *open_cfw_touch_firmware_tx_buffer(void);
void open_cfw_touch_firmware_tx_complete(void);

#endif
