/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdint.h>

#include "runtime_touch_startup_closed.h"

void open_cfw_touch_startup_0d4c_initialize(
    open_cfw_touch_startup_record *record,
    const uint16_t *initial_timeout)
{
    size_t index;
    uint16_t timeout;

    if (record == NULL || initial_timeout == NULL) {
        return;
    }
    for (index = 0u; index < sizeof(record->bytes); ++index) {
        record->bytes[index] = 0u;
    }
    timeout = *initial_timeout;
    if (timeout == 0u) {
        timeout = 1000u;
    }
    record->bytes[0] = (uint8_t)timeout;
    record->bytes[1] = (uint8_t)(timeout >> 8);
}

void open_cfw_touch_startup_11b4_passthrough_sequence(void)
{
    /* The three authenticated callees return their input and have no effects. */
}

void open_cfw_touch_startup_11d0_configure_dividers(
    const open_cfw_touch_startup_clock_provider *provider)
{
    void *context;

    if (provider == NULL || provider->disable_divider == NULL ||
            provider->set_integer_divider == NULL ||
            provider->set_fractional_divider == NULL ||
            provider->enable_divider == NULL) {
        return;
    }
    context = provider->context;
    provider->disable_divider(context, 1u, 1u);
    provider->set_integer_divider(context, 1u, 1u, 3u);
    provider->enable_divider(context, 1u, 1u);

    provider->disable_divider(context, 2u, 0u);
    provider->set_fractional_divider(context, 2u, 0u, 0x33u, 3u);
    provider->enable_divider(context, 2u, 0u);

    provider->disable_divider(context, 3u, 0u);
    provider->set_fractional_divider(context, 3u, 0u, 0x33u, 3u);
    provider->enable_divider(context, 3u, 0u);
}

void open_cfw_touch_startup_1228_assign_divider(
    const open_cfw_touch_startup_clock_provider *provider)
{
    if (provider == NULL || provider->assign_divider == NULL) {
        return;
    }
    provider->assign_divider(provider->context, 1u, 1u, 1u);
}
