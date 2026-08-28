/*
 * SPDX-License-Identifier: Apache-2.0
 * Bounded adapter for Infineon mtb-pdl-cat2 commit
 * 35f1714623cfea682d5e285af80d50416b4c7bbc. The upstream implementation and
 * notices remain authoritative; this file contains no Infineon-EULA source.
 */
#include "runtime_touch_cat2_adapters.h"

int open_cfw_touch_cat2_delay_us(
    uint16_t microseconds, uint32_t frequency_mhz,
    void (*delay_cycles)(uint32_t cycles))
{
    if (delay_cycles == NULL) {
        return -1;
    }
    delay_cycles((uint32_t)microseconds * frequency_mhz);
    return 0;
}

void open_cfw_touch_cat2_systick_service(open_cfw_touch_cat2_systick *state)
{
    uint32_t index;
    if (state == NULL || (state->ctrl & OPEN_CFW_TOUCH_SYSTICK_COUNTFLAG) == 0u) {
        return;
    }
    for (index = 0u; index < OPEN_CFW_TOUCH_SYSTICK_CALLBACKS; ++index) {
        if (state->callbacks[index] != NULL) {
            state->callbacks[index]();
        }
    }
}

void open_cfw_touch_cat2_systick_enable(open_cfw_touch_cat2_systick *state)
{
    if (state != NULL) {
        state->ctrl |= OPEN_CFW_TOUCH_SYSTICK_TICKINT |
                       OPEN_CFW_TOUCH_SYSTICK_ENABLE;
    }
}

void open_cfw_touch_cat2_systick_set_clock(
    open_cfw_touch_cat2_systick *state, uint32_t source)
{
    if (state != NULL) {
        state->ctrl &= ~OPEN_CFW_TOUCH_SYSTICK_CLKSOURCE;
        if (source != 0u) {
            state->ctrl |= OPEN_CFW_TOUCH_SYSTICK_CLKSOURCE;
        }
    }
}

int open_cfw_touch_cat2_systick_init(
    open_cfw_touch_cat2_systick *state, uint32_t source, uint32_t interval)
{
    uint32_t index;
    if (state == NULL || interval >= 0x01000000u) {
        return -1;
    }
    for (index = 0u; index < OPEN_CFW_TOUCH_SYSTICK_CALLBACKS; ++index) {
        state->callbacks[index] = NULL;
    }
    state->vector = NULL;
    open_cfw_touch_cat2_systick_set_clock(state, source);
    state->load = interval;
    state->val = 0u;
    open_cfw_touch_cat2_systick_enable(state);
    return 0;
}

open_cfw_touch_cat2_void_fn open_cfw_touch_cat2_systick_set_callback(
    open_cfw_touch_cat2_systick *state, uint32_t number,
    open_cfw_touch_cat2_void_fn callback)
{
    open_cfw_touch_cat2_void_fn previous;
    if (state == NULL || number >= OPEN_CFW_TOUCH_SYSTICK_CALLBACKS) {
        return NULL;
    }
    previous = state->callbacks[number];
    state->callbacks[number] = callback;
    return previous;
}

int open_cfw_touch_cat2_syspm_route(
    open_cfw_touch_cat2_syspm_fn provider, uint32_t type, void *context)
{
    return provider == NULL ? -1 : provider(type, context);
}

int open_cfw_touch_cat2_flash_write_row_route(
    open_cfw_touch_cat2_flash_write_fn provider, uint32_t row_address,
    const uint32_t *data, void *context)
{
    return provider == NULL || data == NULL ? -1 :
           provider(row_address, data, context);
}

int open_cfw_touch_cat2_gpio_pin_init_route(
    open_cfw_touch_cat2_gpio_pin_init_fn provider, void *base, uint32_t pin,
    const void *config, void *context)
{
    return provider == NULL || base == NULL || config == NULL ? -1 :
           provider(base, pin, config, context);
}

int open_cfw_touch_cat2_i2c_slave_interrupt_route(
    open_cfw_touch_cat2_i2c_irq_fn provider, void *base, void *i2c_context,
    void *provider_context)
{
    if (provider == NULL || base == NULL || i2c_context == NULL) {
        return -1;
    }
    provider(base, i2c_context, provider_context);
    return 0;
}

uint32_t open_cfw_touch_cat2_scb_read_route(
    open_cfw_touch_cat2_scb_read_fn provider, const void *base, void *buffer,
    uint32_t size, void *context)
{
    if (provider == NULL || base == NULL || (buffer == NULL && size != 0u)) {
        return 0u;
    }
    return provider(base, buffer, size, context);
}

uint32_t open_cfw_touch_cat2_scb_write_route(
    open_cfw_touch_cat2_scb_write_fn provider, void *base, const void *buffer,
    uint32_t data, uint32_t size, void *context)
{
    if (provider == NULL || base == NULL) {
        return 0u;
    }
    return provider(base, buffer, data, size, context);
}

int open_cfw_touch_cat2_scb_set_rx_level_route(
    open_cfw_touch_cat2_scb_level_fn provider, void *base, uint32_t level,
    void *context)
{
    return provider == NULL || base == NULL ? -1 :
           provider(base, level, context);
}

int open_cfw_touch_cat2_gpio_value_route(
    open_cfw_touch_cat2_gpio_value_fn provider, void *base, uint32_t pin,
    uint32_t value, void *context)
{
    return provider == NULL || base == NULL ? -1 :
           provider(base, pin, value, context);
}

int open_cfw_touch_cat2_sysclk_route(
    open_cfw_touch_cat2_sysclk_fn provider, uint32_t operation,
    uint32_t argument0, uint32_t argument1, uint32_t *result, void *context)
{
    return provider == NULL || result == NULL ? -1 :
           provider(operation, argument0, argument1, result, context);
}

int open_cfw_touch_cat2_msclp_route(
    open_cfw_touch_cat2_msclp_fn provider, void *base, const void *config,
    uint32_t key, void *context)
{
    return provider == NULL || base == NULL || config == NULL || context == NULL ?
           -1 : provider(base, config, key, context);
}

int open_cfw_touch_cat2_i2c_helper_route(
    open_cfw_touch_cat2_i2c_helper_fn provider, void *base, uint32_t flag,
    void *i2c_context, void *provider_context)
{
    if (provider == NULL || base == NULL || i2c_context == NULL) {
        return -1;
    }
    provider(base, flag, i2c_context, provider_context);
    return 0;
}

int open_cfw_touch_cat2_register_callback_route(
    open_cfw_touch_cat2_register_callback_fn provider, void *callback_record,
    void *context)
{
    return provider == NULL || callback_record == NULL ? -1 :
           provider(callback_record, context);
}

int open_cfw_touch_cat2_system_halt_route(
    open_cfw_touch_cat2_system_halt_fn provider, void *context)
{
    return provider == NULL ? -1 : provider(context);
}
