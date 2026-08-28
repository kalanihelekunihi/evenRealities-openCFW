/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_CONFIGURATION_START_PIPELINE_H
#define OPENCFW_TOUCH_CONFIGURATION_START_PIPELINE_H

#include <stdint.h>

typedef uint32_t (*open_cfw_touch_capture_provider)(uint32_t base,
                                                    uint32_t key);
typedef uint32_t (*open_cfw_touch_event_provider)(uint32_t event,
                                                  uint8_t *object);

typedef struct {
    open_cfw_touch_capture_provider capture;
    open_cfw_touch_event_provider event;
} open_cfw_touch_configuration_providers;

uint32_t open_cfw_touch_config_1944_start(
    uint8_t *object, const open_cfw_touch_configuration_providers *providers);
uint32_t open_cfw_touch_config_1972_start_wrapper(
    uint8_t *object, const open_cfw_touch_configuration_providers *providers);
uint32_t open_cfw_touch_config_197c_initialize(
    uint8_t *object, const open_cfw_touch_configuration_providers *providers);

#endif
