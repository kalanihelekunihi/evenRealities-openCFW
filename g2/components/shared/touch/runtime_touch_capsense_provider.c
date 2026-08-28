/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include "runtime_touch_capsense_provider.h"

int open_cfw_touch_capsense_provider_route(
    open_cfw_touch_capsense_provider_fn provider,
    open_cfw_touch_capsense_operation operation, const void *request,
    void *state, void *provider_context)
{
    if (provider == NULL || state == NULL ||
        operation > OPEN_CFW_TOUCH_CAPSENSE_INTERRUPT) {
        return -1;
    }
    return provider(operation, request, state, provider_context);
}
