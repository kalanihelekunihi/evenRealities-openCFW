/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include "runtime_touch_application_boundary.h"

int open_cfw_touch_application_provider_route(
    open_cfw_touch_application_provider_fn provider,
    open_cfw_touch_application_family family, uint32_t shipped_entry,
    const void *request, void *state, void *provider_context)
{
    if (provider == NULL || state == NULL ||
        family > OPEN_CFW_TOUCH_APPLICATION_PROCESSING ||
        (shipped_entry & 1u) != 0u) {
        return -1;
    }
    return provider(family, shipped_entry, request, state, provider_context);
}
