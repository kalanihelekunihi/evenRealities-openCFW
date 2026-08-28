/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdint.h>

#include "runtime_touch_storage_adapters.h"

static int status_accepted(uint32_t status)
{
    return status == 0u || status == OPEN_CFW_TOUCH_STORAGE_ACCEPTED_STATUS;
}

uint32_t open_cfw_touch_storage_01d8_initialize(
    open_cfw_touch_storage_state *state,
    const open_cfw_touch_storage_provider *provider)
{
    uint32_t status;

    if (state == NULL || provider == NULL || provider->initialize == NULL) {
        return 1u;
    }
    if (state->initialized != 0u) {
        return 0u;
    }
    state->descriptor = 0x0000E400u;
    status = provider->initialize(&state->descriptor, state->provider_context);
    if (!status_accepted(status)) {
        return 1u;
    }
    state->initialized = 1u;
    return 0u;
}

uint32_t open_cfw_touch_storage_0220_read(
    open_cfw_touch_storage_state *state,
    const open_cfw_touch_storage_provider *provider, uint32_t offset,
    uint8_t *destination, uint32_t size)
{
    uint32_t status;

    if (destination == NULL || offset > OPEN_CFW_TOUCH_STORAGE_LIMIT ||
            size > OPEN_CFW_TOUCH_STORAGE_LIMIT - offset) {
        return 4u;
    }
    if (state == NULL || state->initialized == 0u) {
        return 1u;
    }
    if (provider == NULL || provider->read == NULL) {
        return 2u;
    }
    status = provider->read(offset, destination, size, state->provider_context);
    return status_accepted(status) ? 0u : 2u;
}

uint32_t open_cfw_touch_storage_02b0_context_operation(
    open_cfw_touch_storage_state *state,
    const open_cfw_touch_storage_provider *provider)
{
    uint32_t status;

    if (state == NULL || state->initialized == 0u) {
        return 1u;
    }
    if (provider == NULL || provider->context_operation == NULL) {
        return 3u;
    }
    status = provider->context_operation(state->provider_context);
    return status_accepted(status) ? 0u : 3u;
}

void open_cfw_touch_storage_02e4_increment(open_cfw_touch_storage_state *state)
{
    if (state != NULL) {
        ++state->counter;
    }
}
