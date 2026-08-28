/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "runtime_touch_capsense_provider.h"

static uint32_t captured_operation;

static int capture(
    open_cfw_touch_capsense_operation operation, const void *request,
    void *state, void *provider_context)
{
    if (request == 0 || state == 0 || provider_context == 0) {
        return -2;
    }
    captured_operation = (uint32_t)operation;
    return 17;
}

int touch_host_capsense_route(int available, uint32_t operation)
{
    captured_operation = 0xFFFFFFFFu;
    return open_cfw_touch_capsense_provider_route(
        available ? capture : 0, (open_cfw_touch_capsense_operation)operation,
        (const void *)(uintptr_t)1u, (void *)(uintptr_t)2u,
        (void *)(uintptr_t)3u);
}

uint32_t touch_host_capsense_captured_operation(void)
{
    return captured_operation;
}
