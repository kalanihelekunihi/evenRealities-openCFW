/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room Touch product orchestration. Board and resident operations are
 * injected; register writes are limited to caller-authorized volatile views.
 */
#include <stddef.h>
#include <stdint.h>

#include "runtime_touch_product_orchestration.h"

enum {
    OPEN_CFW_TOUCH_MODE_ONE = 1,
    OPEN_CFW_TOUCH_MODE_TWO = 2,
    OPEN_CFW_TOUCH_MODE_THREE = 3,
    OPEN_CFW_TOUCH_LONG_COUNTDOWN = 640,
    OPEN_CFW_TOUCH_SHORT_COUNTDOWN = 160,
};

static void clear_scratch(uint8_t scratch[16])
{
    uint32_t index;

    if (scratch == NULL) {
        return;
    }
    for (index = 0U; index < 16U; ++index) {
        scratch[index] = 0U;
    }
}

static uint32_t required_product_contracts(
    const open_cfw_touch_product_provider *provider)
{
    return provider != NULL && provider->startup != NULL &&
        provider->install_callback != NULL && provider->fault != NULL &&
        provider->log_event != NULL && provider->enable_interrupts != NULL &&
        provider->bootstrap_storage != NULL &&
        provider->sample_configuration != NULL &&
        provider->start_power_callback != NULL &&
        provider->initialize_sensing != NULL &&
        provider->start_application != NULL &&
        provider->prepare_application != NULL &&
        provider->announce_application != NULL && provider->sleep != NULL &&
        provider->refresh != NULL && provider->tick != NULL &&
        provider->delay_until != NULL && provider->pending != NULL &&
        provider->wait_primary != NULL && provider->wait_secondary != NULL &&
        provider->process_objects != NULL && provider->decision != NULL &&
        provider->idle != NULL && provider->prepare_mode_three != NULL &&
        provider->mode_three_result != NULL;
}

static uint32_t settle(
    const open_cfw_touch_product_provider *provider, uint32_t primary)
{
    uint32_t tick = provider->tick(provider->context);

    while (provider->pending(provider->context) != 0U) {
        if (primary != 0U) {
            provider->wait_primary(provider->context);
        } else {
            provider->wait_secondary(provider->context);
        }
        provider->delay_until(provider->context, tick);
        tick = provider->tick(provider->context);
    }
    provider->delay_until(provider->context, tick);
    return tick;
}

uint32_t open_cfw_touch_product_05e0_bringup(
    const open_cfw_touch_bringup_provider *provider,
    volatile uint32_t *enable_register,
    volatile uint32_t *pending_register)
{
    int16_t interrupt_number = -1;
    uint32_t status;

    if (provider == NULL || provider->initialize_configuration == NULL ||
            provider->resolve_interrupt == NULL ||
            provider->run_application == NULL) {
        return UINT32_C(0xFFFFFFFF);
    }
    status = provider->initialize_configuration(provider->context);
    if (status != 0U) {
        return status;
    }
    provider->resolve_interrupt(provider->context, &interrupt_number);
    if (interrupt_number >= 0 && enable_register != NULL &&
            pending_register != NULL) {
        uint32_t bit = UINT32_C(1) << ((uint32_t)interrupt_number & 31U);
        *enable_register = bit;
        *pending_register = bit;
    }
    return provider->run_application(provider->context);
}

uint32_t open_cfw_touch_product_09b4_initialize(
    open_cfw_touch_product_state *state,
    volatile uint32_t *setup_control,
    const open_cfw_touch_product_provider *provider)
{
    uint32_t startup_status;

    if (state == NULL || setup_control == NULL ||
            required_product_contracts(provider) == 0U) {
        return UINT32_C(0xFFFFFFFF);
    }
    startup_status = provider->startup(provider->context);
    provider->install_callback(provider->context, 0U);
    if (startup_status != 0U) {
        provider->fault(provider->context, 1U);
    }
    provider->log_event(provider->context, 0U);
    provider->enable_interrupts(provider->context);
    provider->bootstrap_storage(provider->context);
    provider->sample_configuration(provider->context);
    provider->start_power_callback(provider->context);
    state->mode = OPEN_CFW_TOUCH_MODE_ONE;
    state->countdown = OPEN_CFW_TOUCH_LONG_COUNTDOWN;
    *setup_control = 1U;
    *setup_control = 2U;
    provider->initialize_sensing(provider->context);
    (void)provider->start_application(provider->context);
    provider->prepare_application(provider->context);
    provider->announce_application(provider->context);
    return startup_status;
}

void open_cfw_touch_product_09b4_step(
    open_cfw_touch_product_state *state, uint8_t scratch[16],
    const open_cfw_touch_product_provider *provider)
{
    uint32_t decision;

    if (state == NULL || scratch == NULL ||
            required_product_contracts(provider) == 0U) {
        return;
    }
    provider->sleep(provider->context);
    clear_scratch(scratch);
    switch (state->mode) {
    case OPEN_CFW_TOUCH_MODE_ONE:
        provider->refresh(provider->context);
        (void)settle(provider, 1U);
        (void)provider->process_objects(provider->context);
        decision = provider->decision(provider->context, 1U);
        if (decision != 0U) {
            state->countdown = OPEN_CFW_TOUCH_LONG_COUNTDOWN;
            provider->idle(provider->context);
            return;
        }
        --state->countdown;
        if (state->countdown != 0U) {
            provider->idle(provider->context);
            return;
        }
        state->mode = OPEN_CFW_TOUCH_MODE_TWO;
        state->countdown = OPEN_CFW_TOUCH_SHORT_COUNTDOWN;
        provider->log_event(provider->context, 1U);
        provider->announce_application(provider->context);
        provider->idle(provider->context);
        return;

    case OPEN_CFW_TOUCH_MODE_TWO:
        provider->refresh(provider->context);
        (void)settle(provider, 0U);
        (void)provider->process_objects(provider->context);
        decision = provider->decision(provider->context, 1U);
        if (decision != 0U) {
            state->mode = OPEN_CFW_TOUCH_MODE_ONE;
            state->countdown = OPEN_CFW_TOUCH_LONG_COUNTDOWN;
            provider->log_event(provider->context, 2U);
            provider->announce_application(provider->context);
        } else if (state->countdown == 0U) {
            state->mode = OPEN_CFW_TOUCH_MODE_THREE;
            provider->log_event(provider->context, 3U);
        }
        provider->idle(provider->context);
        return;

    case OPEN_CFW_TOUCH_MODE_THREE:
        provider->prepare_mode_three(provider->context);
        (void)settle(provider, 0U);
        if (provider->mode_three_result(provider->context) != 0U) {
            state->mode = OPEN_CFW_TOUCH_MODE_ONE;
            state->countdown = OPEN_CFW_TOUCH_LONG_COUNTDOWN;
            provider->log_event(provider->context, 4U);
        } else {
            state->mode = OPEN_CFW_TOUCH_MODE_TWO;
            state->countdown = OPEN_CFW_TOUCH_SHORT_COUNTDOWN;
            provider->log_event(provider->context, 5U);
        }
        provider->announce_application(provider->context);
        return;

    default:
        provider->fault(provider->context, 1U);
        return;
    }
}

void open_cfw_touch_product_09b4_run(
    open_cfw_touch_product_state *state, uint8_t scratch[16],
    volatile uint32_t *setup_control,
    const open_cfw_touch_product_provider *provider)
{
    if (open_cfw_touch_product_09b4_initialize(
            state, setup_control, provider) == UINT32_C(0xFFFFFFFF)) {
        return;
    }
    for (;;) {
        open_cfw_touch_product_09b4_step(state, scratch, provider);
    }
}
