/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room Touch clock and application wrappers. Live platform operations
 * are injected and register access is restricted to caller-authorized views.
 */
#include <stddef.h>
#include <stdint.h>

#include "runtime_touch_clock_application_wrappers.h"

static uint32_t divide_u32(uint32_t numerator, uint32_t denominator)
{
    uint32_t quotient = 0U;
    uint32_t remainder = 0U;
    uint32_t bit = 32U;

    while (bit != 0U) {
        --bit;
        remainder = (remainder << 1U) | ((numerator >> bit) & 1U);
        if (remainder >= denominator) {
            remainder -= denominator;
            quotient |= UINT32_C(1) << bit;
        }
    }
    return quotient;
}

void open_cfw_touch_clock_12ac_validate(
    const open_cfw_touch_clock_register_view *registers,
    const open_cfw_touch_clock_provider *provider)
{
    uint32_t result = 0U;

    if (provider != NULL && provider->set_divider != NULL) {
        result = provider->set_divider(provider->context, 0U);
    }
    if (result != 0U && provider != NULL && provider->fault != NULL) {
        provider->fault(provider->context, 6U);
    }
    if (registers != NULL && registers->divider_control != NULL) {
        *registers->divider_control &= ~UINT32_C(0x0000000C);
    }
}

void open_cfw_touch_clock_1434_calibrate(
    uint32_t divider_control,
    open_cfw_touch_clock_state *state,
    const open_cfw_touch_clock_provider *provider)
{
    uint32_t shift = (divider_control >> 6U) & 3U;
    uint32_t measurement;
    uint32_t frequency;
    uint32_t adjusted;

    if (state == NULL || provider == NULL || provider->measure == NULL) {
        return;
    }
    measurement = provider->measure(provider->context);
    frequency = (measurement + ((UINT32_C(1) << shift) >> 1U)) >> shift;
    if (frequency == 0U) {
        return;
    }
    state->frequency_hz = frequency;
    adjusted = frequency - 1U;
    state->megahertz_ceiling =
        (uint8_t)(divide_u32(adjusted, UINT32_C(1000000)) + 1U);
    state->kilohertz_ceiling =
        divide_u32(adjusted, UINT32_C(1000)) + 1U;
    state->scaled_kilohertz = state->kilohertz_ceiling << 15U;
}

void open_cfw_touch_clock_12d0_transition(
    const open_cfw_touch_clock_register_view *registers,
    open_cfw_touch_clock_state *state,
    const open_cfw_touch_clock_provider *provider)
{
    if (registers == NULL || provider == NULL ||
            registers->divider_control == NULL ||
            registers->clock_select_control == NULL ||
            registers->path_control == NULL) {
        return;
    }
    if (provider->set_power_mode != NULL) {
        provider->set_power_mode(provider->context, UINT32_C(0x30));
    }
    *registers->path_control = UINT32_C(0x80000000);
    if (provider->delay != NULL) {
        provider->delay(provider->context, UINT32_C(0x016E3600));
    }
    if (provider->set_divider != NULL) {
        (void)provider->set_divider(provider->context, 0U);
    }
    *registers->divider_control &= ~UINT32_C(0x0000000C);
    *registers->divider_control &= ~UINT32_C(0x000000C0);
    open_cfw_touch_clock_1434_calibrate(
        *registers->divider_control, state, provider);
    if (provider->select_clock != NULL) {
        provider->select_clock(provider->context, 0U);
    }
    *registers->clock_select_control |= UINT32_C(0x80000000);
    if (provider->delay != NULL) {
        provider->delay(provider->context, UINT32_C(0x02DC6C00));
    }
    open_cfw_touch_clock_12ac_validate(registers, provider);
    *registers->divider_control &= ~UINT32_C(0x000000C0);
    if (provider->set_power_mode != NULL) {
        provider->set_power_mode(provider->context, UINT32_C(0x30));
    }
    open_cfw_touch_clock_1434_calibrate(
        *registers->divider_control, state, provider);
}

uint32_t open_cfw_touch_application_17be_preflight(
    void *object, uint8_t *initialized,
    const open_cfw_touch_application_provider *provider)
{
    uint32_t result;

    if (object == NULL || initialized == NULL || provider == NULL ||
            provider->preflight == NULL || provider->reset == NULL ||
            provider->status == NULL || provider->finalize == NULL) {
        return UINT32_C(0xFFFFFFFF);
    }
    result = provider->preflight(provider->context, object);
    if (result != 0U) {
        return result;
    }
    provider->reset(provider->context, object);
    result = provider->status(provider->context, object);
    if (*initialized == 0U) {
        provider->finalize(provider->context, object);
        *initialized = 1U;
    }
    return result;
}

uint32_t open_cfw_touch_application_1904_process_three(
    void *object, const uint8_t *object_records, uint32_t record_stride,
    const open_cfw_touch_application_provider *provider)
{
    uint32_t result = 0U;
    uint32_t index = 3U;

    if (object == NULL || object_records == NULL || record_stride <= 0x7BU ||
            provider == NULL || provider->object_exists == NULL ||
            provider->process_object == NULL) {
        return 0U;
    }
    while (index != 0U) {
        --index;
        if (provider->object_exists(provider->context, index, object) != 0U &&
                object_records[index * record_stride + 0x7BU] != 7U) {
            result |= provider->process_object(
                provider->context, index, object);
        }
    }
    return result;
}

void open_cfw_touch_application_1c54_update_three(
    void *object, const open_cfw_touch_application_provider *provider)
{
    uint32_t index = 3U;

    if (object == NULL || provider == NULL || provider->update_pointer == NULL) {
        return;
    }
    while (index != 0U) {
        --index;
        provider->update_pointer(provider->context, index, object);
    }
}
