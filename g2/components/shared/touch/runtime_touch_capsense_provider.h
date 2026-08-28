/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_CAPSENSE_PROVIDER_H
#define OPENCFW_TOUCH_CAPSENSE_PROVIDER_H

#include <stdint.h>

typedef enum {
    OPEN_CFW_TOUCH_CAPSENSE_INITIALIZE = 0,
    OPEN_CFW_TOUCH_CAPSENSE_SCAN = 1,
    OPEN_CFW_TOUCH_CAPSENSE_PROCESS = 2,
    OPEN_CFW_TOUCH_CAPSENSE_CALIBRATE = 3,
    OPEN_CFW_TOUCH_CAPSENSE_INTERRUPT = 4
} open_cfw_touch_capsense_operation;

typedef int (*open_cfw_touch_capsense_provider_fn)(
    open_cfw_touch_capsense_operation operation, const void *request,
    void *state, void *provider_context);

int open_cfw_touch_capsense_provider_route(
    open_cfw_touch_capsense_provider_fn provider,
    open_cfw_touch_capsense_operation operation, const void *request,
    void *state, void *provider_context);

#endif
