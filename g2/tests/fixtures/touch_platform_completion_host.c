/* SPDX-License-Identifier: MIT */
#include <stdint.h>

#include "../../components/shared/touch/runtime_touch_platform_completion.c"

typedef struct test_context {
    uint32_t log[32];
    uint32_t count;
} test_context;

static void push(test_context *context, uint32_t value)
{
    context->log[context->count++] = value;
}

static void preinitialize(void *raw) { push((test_context *)raw, 1U); }
static void initialize(void *raw) { push((test_context *)raw, 2U); }
static uint32_t application_main(void *raw)
{
    push((test_context *)raw, 3U);
    return UINT32_C(0x55AA);
}
static void exit_application(void *raw, uint32_t result)
{
    push((test_context *)raw, UINT32_C(0x10000) | result);
}
static void fault(void *raw, uint32_t reason)
{
    push((test_context *)raw, UINT32_C(0x20000) | reason);
}
static void disable_interrupts(void *raw)
{
    push((test_context *)raw, UINT32_C(0x30000));
}
static uint32_t handoff(void *raw)
{
    push((test_context *)raw, UINT32_C(0x40000));
    return UINT32_C(0x77);
}

static open_cfw_touch_runtime_provider provider_for(test_context *context)
{
    open_cfw_touch_runtime_provider provider = {
        preinitialize, initialize, application_main, exit_application,
        fault, disable_interrupts, handoff, context,
    };
    return provider;
}

uint32_t open_cfw_test_touch_platform_runtime(void)
{
    test_context context = {{0U}, 0U};
    open_cfw_touch_runtime_provider provider = provider_for(&context);
    open_cfw_touch_runtime_state state = {UINT32_C(0x20020000), 0U, 0U, 0U, 0U};
    uint8_t bss[8] = {1U, 2U, 3U, 4U, 5U, 6U, 7U, 8U};
    uint32_t handoff_register = 0U;
    uint32_t result = 0U;

    result |= open_cfw_touch_runtime_0158_stack_limit(
                  &state, UINT32_C(0x20020000)) == UINT32_C(0x20010000) &&
                      state.stack_limit == UINT32_C(0x20010000) ? 1U : 0U;
    result |= open_cfw_touch_runtime_0164_reset(
                  &state, bss, bss + sizeof(bss), &provider) == UINT32_C(0x55AA) &&
                      bss[0] == 0U && bss[7] == 0U && state.exited == 1U &&
                      context.count == 4U ? 2U : 0U;
    open_cfw_touch_runtime_12a6_fault(&state, 6U, &provider);
    result |= state.fault_reason == 6U &&
                      context.log[4] == UINT32_C(0x20006) ? 4U : 0U;
    result |= open_cfw_touch_runtime_141c_handoff(
                  &handoff_register, UINT32_C(0x12345678), &provider) ==
                      UINT32_C(0x77) &&
                      handoff_register == UINT32_C(0x12345678) &&
                      context.log[5] == UINT32_C(0x30000) &&
                      context.log[6] == UINT32_C(0x40000) ? 8U : 0U;
    return result;
}

uint32_t open_cfw_test_touch_platform_mapping_profiles(void)
{
    open_cfw_touch_mapping_config mapping = {0};
    open_cfw_touch_mapping_image image = {{0}, 0U, 0U, {0U}};
    open_cfw_touch_profile_tables tables = {0};
    open_cfw_touch_profile_selectors selectors = {1U, 1U, 1U, 5U};
    uint8_t output[4][28];
    uint32_t words[14];
    uint32_t index;
    uint32_t result = 0U;

    for (index = 0U; index < 14U; ++index) {
        mapping.word_index[index] = UINT8_C(0xFF);
        words[index] = UINT32_C(0x1000) + index;
    }
    mapping.word_index[0] = 2U;
    mapping.word_index[1] = 0U;
    mapping.mode = 1U;
    mapping.primary_index = 1U;
    mapping.secondary_index = 3U;
    result |= open_cfw_touch_config_1de4_load_mapping(
                  &mapping, words, &image) == 0U && image.valid_count == 2U &&
                      image.selected_index == 1U &&
                      image.words[2] == UINT32_C(0x1000) &&
                      image.words[0] == UINT32_C(0x1001) ? 1U : 0U;

    for (index = 0U; index < 28U; ++index) {
        tables.base[0][index] = 1U;
        tables.base[1][index] = 2U;
        tables.base[2][index] = 3U;
        tables.override_mode_a[index] = 4U;
        tables.override_mode_b[index] = 5U;
        tables.override_mode_c[index] = 6U;
    }
    open_cfw_touch_config_1fbc_load_profiles(&tables, &selectors, output);
    result |= output[0][0] == 4U && output[1][0] == 5U &&
                      output[2][0] == 3U && output[3][0] == 6U &&
                      output[1][16] == UINT8_C(0xFD) ? 2U : 0U;
    return result;
}

uint32_t open_cfw_test_touch_platform_register_builder(void)
{
    open_cfw_touch_register_parameters parameters = {0};
    open_cfw_touch_register_image image = {0};
    uint32_t index;

    parameters.channel = 2U;
    parameters.polarity = 1U;
    parameters.averaging = 1U;
    parameters.threshold_a = 0U;
    parameters.threshold_b = 0U;
    parameters.threshold_c = 1U;
    parameters.debounce = 3U;
    parameters.resolution_a = UINT16_C(0x1234);
    parameters.resolution_b = UINT16_C(0x5678);
    parameters.timing_a = UINT16_C(0xABCD);
    parameters.timing_b = UINT16_C(0x22);
    for (index = 0U; index < 14U; ++index) {
        parameters.mapping.word_index[index] = (uint8_t)index;
    }
    return open_cfw_touch_config_2078_build(
               &parameters, &open_cfw_touch_safe_profile_tables,
               open_cfw_touch_safe_mapping_words, &image) == 0U &&
                   image.words[0] == UINT32_C(0x00800031) &&
                   image.words[1] == UINT32_C(0x10000180) &&
                   image.words[2] == UINT32_C(0x1101) &&
                   image.words[3] == UINT32_C(0x56780234) &&
                   image.words[17] == UINT32_C(0x00020006) &&
                   image.mapping.valid_count == 14U
               ? 1U : 0U;
}

uint32_t open_cfw_test_touch_platform_completion_null_guards(void)
{
    return (open_cfw_touch_runtime_0164_reset(
                (open_cfw_touch_runtime_state *)0, (uint8_t *)0, (uint8_t *)0,
                (const open_cfw_touch_runtime_provider *)0) ==
                    UINT32_C(0xFFFFFFFF) ? 0U : 1U) |
           (open_cfw_touch_runtime_141c_handoff(
                (volatile uint32_t *)0, 0U,
                (const open_cfw_touch_runtime_provider *)0) ==
                    UINT32_C(0xFFFFFFFF) ? 0U : 1U) |
           (open_cfw_touch_config_2078_build(
                (const open_cfw_touch_register_parameters *)0,
                (const open_cfw_touch_profile_tables *)0,
                (const uint32_t *)0,
                (open_cfw_touch_register_image *)0) == 1U ? 0U : 1U);
}
