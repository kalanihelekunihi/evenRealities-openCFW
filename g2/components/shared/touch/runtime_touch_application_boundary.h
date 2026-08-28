/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_APPLICATION_BOUNDARY_H
#define OPENCFW_TOUCH_APPLICATION_BOUNDARY_H

#include <stdint.h>

typedef enum {
    OPEN_CFW_TOUCH_PLATFORM_STARTUP_CONFIGURATION = 0,
    OPEN_CFW_TOUCH_APPLICATION_PROCESSING = 1
} open_cfw_touch_application_family;

typedef int (*open_cfw_touch_application_provider_fn)(
    open_cfw_touch_application_family family, uint32_t shipped_entry,
    const void *request, void *state, void *provider_context);

int open_cfw_touch_application_provider_route(
    open_cfw_touch_application_provider_fn provider,
    open_cfw_touch_application_family family, uint32_t shipped_entry,
    const void *request, void *state, void *provider_context);

#endif
