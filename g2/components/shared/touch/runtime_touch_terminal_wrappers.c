/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdint.h>

#include "runtime_touch_terminal_wrappers.h"

uint32_t open_cfw_touch_terminal_1368_passthrough(uint32_t value)
{
    return value;
}

void open_cfw_touch_terminal_25f8_reset_three(
    open_cfw_touch_terminal_context *context,
    const open_cfw_touch_terminal_provider *provider)
{
    uint32_t index;

    if (context == NULL || context->control == NULL || provider == NULL ||
            provider->reset_object == NULL) {
        return;
    }
    context->control[2] &= UINT32_C(0xFFFFFBFF);
    for (index = 3u; index > 0u; --index) {
        provider->reset_object(provider->context, index - 1u, context);
    }
}

uint32_t open_cfw_touch_terminal_2972_provider_call(
    const open_cfw_touch_terminal_provider *provider,
    uint32_t argument0,
    uint32_t argument1,
    uint32_t argument2)
{
    if (provider == NULL || provider->capsense_call == NULL) {
        return 0u;
    }
    return provider->capsense_call(provider->context, argument0,
                                   argument1, argument2);
}

uint32_t open_cfw_touch_terminal_297a_conditional_call(
    const open_cfw_touch_terminal_provider *provider,
    uint32_t value)
{
    if (value == 0u) {
        return 1u;
    }
    return open_cfw_touch_terminal_2972_provider_call(provider, 0u, 5u, value);
}
