/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdint.h>

#include "runtime_touch_deferred_work.h"

void open_cfw_touch_deferred_0780_process(
    open_cfw_touch_deferred_state *state,
    const open_cfw_touch_deferred_provider *provider)
{
    uint32_t token;
    uint8_t notify_pending;
    uint8_t config_pending;
    uint16_t value;

    if (state == NULL || provider == NULL ||
            provider->enter_critical == NULL ||
            provider->exit_critical == NULL) {
        return;
    }
    token = provider->enter_critical(provider->context);
    notify_pending = state->notify_pending;
    config_pending = state->config_pending;
    value = state->captured_value;
    state->notify_pending = 0u;
    state->config_pending = 0u;
    provider->exit_critical(provider->context, token);

    if (notify_pending != 0u && provider->notify_value != NULL) {
        provider->notify_value(provider->context, value);
    }
    if (config_pending != 0u && provider->load_configuration != NULL) {
        (void)provider->load_configuration(provider->context);
    }
}
