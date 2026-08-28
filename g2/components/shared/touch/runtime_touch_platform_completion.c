/*
 * SPDX-License-Identifier: MIT
 *
 * Selected Touch startup/system policy and source-owned generated defaults.
 * Hardware access is injected or restricted to caller-authorized views.
 */
#include <stddef.h>
#include <stdint.h>

#include "runtime_touch_platform_completion.h"

const open_cfw_touch_profile_tables open_cfw_touch_safe_profile_tables = {0};
const uint32_t open_cfw_touch_safe_mapping_words[14] = {
    0U, 1U, 2U, 3U, 4U, 5U, 6U, 7U, 8U, 9U, 10U, 11U, 12U, 13U,
};

static void copy_bytes(uint8_t *destination, const uint8_t *source,
                       size_t size)
{
    size_t index;

    for (index = 0U; index < size; ++index) {
        destination[index] = source[index];
    }
}

static void clear_bytes(uint8_t *start, uint8_t *end)
{
    if (start == NULL || end == NULL || end < start) {
        return;
    }
    while (start != end) {
        *start++ = 0U;
    }
}

uintptr_t open_cfw_touch_runtime_0158_stack_limit(
    open_cfw_touch_runtime_state *state, uintptr_t stack_top)
{
    uintptr_t limit = stack_top >= UINT32_C(0x10000)
        ? stack_top - UINT32_C(0x10000) : 0U;

    if (state != NULL) {
        state->stack_top = stack_top;
        state->stack_limit = limit;
    }
    return limit;
}

uint32_t open_cfw_touch_runtime_0164_reset(
    open_cfw_touch_runtime_state *state,
    uint8_t *bss_start, uint8_t *bss_end,
    const open_cfw_touch_runtime_provider *provider)
{
    uint32_t result;

    if (state == NULL || provider == NULL ||
            provider->application_main == NULL ||
            provider->exit_application == NULL) {
        return UINT32_C(0xFFFFFFFF);
    }
    (void)open_cfw_touch_runtime_0158_stack_limit(state, state->stack_top);
    clear_bytes(bss_start, bss_end);
    if (provider->preinitialize != NULL) {
        provider->preinitialize(provider->context);
    }
    if (provider->initialize != NULL) {
        provider->initialize(provider->context);
    }
    result = provider->application_main(provider->context);
    state->application_result = result;
    provider->exit_application(provider->context, result);
    state->exited = 1U;
    return result;
}

void open_cfw_touch_runtime_0164_reset_entry(
    open_cfw_touch_runtime_state *state,
    uint8_t *bss_start, uint8_t *bss_end,
    const open_cfw_touch_runtime_provider *provider)
{
    (void)open_cfw_touch_runtime_0164_reset(
        state, bss_start, bss_end, provider);
    open_cfw_touch_runtime_7038_halt();
}

void open_cfw_touch_runtime_12a6_fault(
    open_cfw_touch_runtime_state *state, uint32_t reason,
    const open_cfw_touch_runtime_provider *provider)
{
    if (state != NULL) {
        state->fault_reason = reason;
    }
    if (provider != NULL && provider->fault != NULL) {
        provider->fault(provider->context, reason);
    }
}

uint32_t open_cfw_touch_runtime_141c_handoff(
    volatile uint32_t *handoff_register, uint32_t handler_token,
    const open_cfw_touch_runtime_provider *provider)
{
    if (handoff_register == NULL || provider == NULL ||
            provider->disable_interrupts == NULL || provider->handoff == NULL) {
        return UINT32_C(0xFFFFFFFF);
    }
    *handoff_register = handler_token;
    provider->disable_interrupts(provider->context);
    return provider->handoff(provider->context);
}

void open_cfw_touch_runtime_7038_halt(void)
{
    for (;;) {
    }
}

uint32_t open_cfw_touch_config_1de4_load_mapping(
    const open_cfw_touch_mapping_config *config,
    const uint32_t table_words[14],
    open_cfw_touch_mapping_image *image)
{
    uint32_t index;

    if (config == NULL || table_words == NULL || image == NULL) {
        return 1U;
    }
    image->selected_index = UINT8_C(0xFF);
    image->valid_count = 0U;
    for (index = 0U; index < 14U; ++index) {
        image->words[index] = 0U;
    }
    for (index = 0U; index < 14U; ++index) {
        uint8_t destination = config->word_index[index];
        image->word_index[index] = destination;
        if (destination != UINT8_C(0xFF) && destination < 14U) {
            image->words[destination] = table_words[index];
            ++image->valid_count;
        }
    }
    if (config->mode == 1U && config->primary_index < 14U) {
        image->selected_index = config->primary_index;
    } else if (config->mode == 2U && config->secondary_index < 14U) {
        image->selected_index = config->secondary_index;
    } else if (image->valid_count != 0U) {
        for (index = 0U; index < 14U; ++index) {
            if (config->word_index[index] != UINT8_C(0xFF)) {
                image->selected_index = (uint8_t)index;
                break;
            }
        }
    }
    return 0U;
}

void open_cfw_touch_config_1fbc_load_profiles(
    const open_cfw_touch_profile_tables *tables,
    const open_cfw_touch_profile_selectors *selectors,
    uint8_t output[4][28])
{
    if (tables == NULL || selectors == NULL || output == NULL) {
        return;
    }
    copy_bytes(output[0], tables->base[0], 28U);
    copy_bytes(output[1], tables->base[1], 28U);
    copy_bytes(output[2], tables->base[2], 28U);
    copy_bytes(output[3], tables->base[2], 28U);
    if (selectors->mode_a == 1U) {
        copy_bytes(output[0], tables->override_mode_a, 28U);
    }
    if (selectors->mode_b == 1U) {
        copy_bytes(output[1], tables->override_mode_b, 28U);
    }
    if (selectors->mode_c == 1U) {
        copy_bytes(output[3], tables->override_mode_c, 28U);
    }
    if (selectors->option_bits == 5U) {
        output[1][16] |= UINT8_C(0xFD);
    }
}

uint32_t open_cfw_touch_config_2078_build(
    const open_cfw_touch_register_parameters *parameters,
    const open_cfw_touch_profile_tables *tables,
    const uint32_t mapping_words[14],
    open_cfw_touch_register_image *image)
{
    uint32_t index;

    if (parameters == NULL || tables == NULL || mapping_words == NULL ||
            image == NULL) {
        return 1U;
    }
    for (index = 0U; index < 28U; ++index) {
        image->words[index] = 0U;
    }
    image->words[0] = UINT32_C(0x31) |
        (((uint32_t)parameters->channel << 22U) & UINT32_C(0x00C00000));
    image->words[1] = UINT32_C(0x10000000) |
        ((uint32_t)(parameters->polarity & 1U) << 7U) |
        ((uint32_t)(parameters->averaging & 1U) << 8U);
    image->words[2] =
        ((uint32_t)(parameters->threshold_a != 0U
                        ? parameters->threshold_a : 1U) << 8U) |
        (parameters->threshold_b != 0U ? parameters->threshold_b : 1U) |
        ((uint32_t)(parameters->threshold_c & 1U) << 12U);
    image->words[3] = (parameters->resolution_a & UINT16_C(0x0FFF)) |
        ((uint32_t)parameters->resolution_b << 16U);
    image->words[5] = parameters->timing_a |
        ((uint32_t)(parameters->debounce & UINT8_C(0x0F)) << 16U) |
        (((uint32_t)parameters->timing_b << 8U) & UINT32_C(0x0000FF00));
    image->words[7] = parameters->threshold_c;
    image->words[10] = (uint32_t)parameters->threshold_b << 8U;
    image->words[11] = parameters->threshold_a |
        ((uint32_t)parameters->threshold_b << 16U);
    image->words[17] = UINT32_C(6) |
        ((uint32_t)((parameters->debounce == 0U ? 1U : parameters->debounce) - 1U)
         << 16U);
    open_cfw_touch_config_1fbc_load_profiles(
        tables, &parameters->selectors, image->profiles);
    return open_cfw_touch_config_1de4_load_mapping(
        &parameters->mapping, mapping_words, &image->mapping);
}
