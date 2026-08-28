/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "runtime_touch_application_boundary.h"

static uint32_t captured_entry;

static int capture(
    open_cfw_touch_application_family family, uint32_t shipped_entry,
    const void *request, void *state, void *provider_context)
{
    if (request == 0 || state == 0 || provider_context == 0) {
        return -2;
    }
    captured_entry = shipped_entry;
    return 20 + (int)family;
}

int touch_host_application_route(int available, uint32_t family, uint32_t entry)
{
    captured_entry = 0xFFFFFFFFu;
    return open_cfw_touch_application_provider_route(
        available ? capture : 0, (open_cfw_touch_application_family)family,
        entry, (const void *)(uintptr_t)1u, (void *)(uintptr_t)2u,
        (void *)(uintptr_t)3u);
}

uint32_t touch_host_application_captured_entry(void)
{
    return captured_entry;
}
