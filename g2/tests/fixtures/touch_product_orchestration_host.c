/* SPDX-License-Identifier: MIT */
#include <stdint.h>

#include "../../components/shared/touch/runtime_touch_product_orchestration.c"

typedef struct test_context {
    uint32_t log[128];
    uint32_t count;
    uint32_t startup_status;
    uint32_t application_status;
    int16_t interrupt_number;
    uint32_t pending_count;
    uint32_t tick_value;
    uint32_t decision_value;
    uint32_t mode_three_value;
} test_context;

static void push(test_context *context, uint32_t value)
{
    if (context->count < 128U) {
        context->log[context->count++] = value;
    }
}

static uint32_t bringup_initialize(void *raw)
{
    test_context *context = (test_context *)raw;
    push(context, UINT32_C(0x01000000));
    return context->startup_status;
}

static void resolve_interrupt(void *raw, int16_t *value)
{
    test_context *context = (test_context *)raw;
    push(context, UINT32_C(0x02000000));
    *value = context->interrupt_number;
}

static uint32_t bringup_run(void *raw)
{
    test_context *context = (test_context *)raw;
    push(context, UINT32_C(0x03000000));
    return context->application_status;
}

static uint32_t startup(void *raw)
{
    test_context *context = (test_context *)raw;
    push(context, UINT32_C(0x10000000));
    return context->startup_status;
}

static void install(void *raw, uint32_t argument)
{
    push((test_context *)raw, UINT32_C(0x11000000) | argument);
}

static void fault(void *raw, uint32_t reason)
{
    push((test_context *)raw, UINT32_C(0x12000000) | reason);
}

static void log_event(void *raw, uint32_t event)
{
    push((test_context *)raw, UINT32_C(0x13000000) | event);
}

#define VOID_CALLBACK(name, code) \
    static void name(void *raw) { push((test_context *)raw, (code)); }

VOID_CALLBACK(enable_interrupts, UINT32_C(0x14000000))
VOID_CALLBACK(bootstrap, UINT32_C(0x15000000))
VOID_CALLBACK(sample_config, UINT32_C(0x16000000))
VOID_CALLBACK(start_power, UINT32_C(0x17000000))
VOID_CALLBACK(initialize_sensing, UINT32_C(0x18000000))
VOID_CALLBACK(prepare_application, UINT32_C(0x1A000000))
VOID_CALLBACK(announce_application, UINT32_C(0x1B000000))
VOID_CALLBACK(sleep_call, UINT32_C(0x1C000000))
VOID_CALLBACK(refresh, UINT32_C(0x1D000000))
VOID_CALLBACK(wait_primary, UINT32_C(0x1E000000))
VOID_CALLBACK(wait_secondary, UINT32_C(0x1F000000))
VOID_CALLBACK(idle, UINT32_C(0x23000000))
VOID_CALLBACK(prepare_mode_three, UINT32_C(0x24000000))

static uint32_t start_application(void *raw)
{
    test_context *context = (test_context *)raw;
    push(context, UINT32_C(0x19000000));
    return context->application_status;
}

static uint32_t tick(void *raw)
{
    test_context *context = (test_context *)raw;
    push(context, UINT32_C(0x20000000));
    return context->tick_value++;
}

static void delay_until(void *raw, uint32_t value)
{
    push((test_context *)raw, UINT32_C(0x21000000) | (value & 0xFFFFU));
}

static uint32_t pending(void *raw)
{
    test_context *context = (test_context *)raw;
    push(context, UINT32_C(0x22000000));
    if (context->pending_count == 0U) {
        return 0U;
    }
    --context->pending_count;
    return 1U;
}

static uint32_t process_objects(void *raw)
{
    push((test_context *)raw, UINT32_C(0x25000000));
    return 0U;
}

static uint32_t decision(void *raw, uint32_t selector)
{
    test_context *context = (test_context *)raw;
    push(context, UINT32_C(0x26000000) | selector);
    return context->decision_value;
}

static uint32_t mode_three_result(void *raw)
{
    test_context *context = (test_context *)raw;
    push(context, UINT32_C(0x27000000));
    return context->mode_three_value;
}

static open_cfw_touch_product_provider product_provider(test_context *context)
{
    open_cfw_touch_product_provider provider = {
        startup, install, fault, log_event, enable_interrupts, bootstrap,
        sample_config, start_power, initialize_sensing, start_application,
        prepare_application, announce_application, sleep_call, refresh, tick,
        delay_until, pending, wait_primary, wait_secondary, process_objects,
        decision, idle, prepare_mode_three, mode_three_result, context,
    };
    return provider;
}

uint32_t open_cfw_test_touch_product_bringup(void)
{
    test_context context = {{0U}, 0U, 0U, UINT32_C(0x55), 37, 0U, 0U, 0U, 0U};
    open_cfw_touch_bringup_provider provider = {
        bringup_initialize, resolve_interrupt, bringup_run, &context,
    };
    uint32_t enable = 0U;
    uint32_t pending_register = 0U;
    uint32_t result = 0U;

    result |= open_cfw_touch_product_05e0_bringup(
                  &provider, &enable, &pending_register) == UINT32_C(0x55) &&
                      enable == UINT32_C(0x20) && pending_register == UINT32_C(0x20) &&
                      context.count == 3U ? 1U : 0U;
    context.count = 0U;
    context.startup_status = 7U;
    enable = 0U;
    result |= open_cfw_touch_product_05e0_bringup(
                  &provider, &enable, &pending_register) == 7U &&
                      enable == 0U && context.count == 1U ? 2U : 0U;
    return result;
}

uint32_t open_cfw_test_touch_product_initialize(void)
{
    test_context context = {0};
    open_cfw_touch_product_provider provider = product_provider(&context);
    open_cfw_touch_product_state state = {0U, 0U};
    uint32_t setup = 0U;
    uint32_t result = 0U;

    result |= open_cfw_touch_product_09b4_initialize(
                  &state, &setup, &provider) == 0U &&
                      state.mode == 1U && state.countdown == 640U &&
                      setup == 2U && context.count == 11U ? 1U : 0U;
    context.count = 0U;
    context.startup_status = 9U;
    result |= open_cfw_touch_product_09b4_initialize(
                  &state, &setup, &provider) == 9U && context.count == 12U &&
                      context.log[2] == UINT32_C(0x12000001) ? 2U : 0U;
    return result;
}

uint32_t open_cfw_test_touch_product_steps(void)
{
    test_context context = {0};
    open_cfw_touch_product_provider provider = product_provider(&context);
    open_cfw_touch_product_state state = {1U, 1U};
    uint8_t scratch[16];
    uint32_t index;
    uint32_t result = 0U;

    for (index = 0U; index < 16U; ++index) scratch[index] = 0xFFU;
    context.pending_count = 1U;
    open_cfw_touch_product_09b4_step(&state, scratch, &provider);
    result |= state.mode == 2U && state.countdown == 160U &&
                      scratch[0] == 0U && scratch[15] == 0U ? 1U : 0U;

    context.decision_value = 1U;
    context.pending_count = 0U;
    open_cfw_touch_product_09b4_step(&state, scratch, &provider);
    result |= state.mode == 1U && state.countdown == 640U ? 2U : 0U;

    state.mode = 2U;
    state.countdown = 0U;
    context.decision_value = 0U;
    open_cfw_touch_product_09b4_step(&state, scratch, &provider);
    result |= state.mode == 3U ? 4U : 0U;

    context.mode_three_value = 0U;
    open_cfw_touch_product_09b4_step(&state, scratch, &provider);
    result |= state.mode == 2U && state.countdown == 160U ? 8U : 0U;

    state.mode = 99U;
    context.count = 0U;
    open_cfw_touch_product_09b4_step(&state, scratch, &provider);
    result |= context.log[context.count - 1U] == UINT32_C(0x12000001)
                  ? 16U : 0U;
    return result;
}

uint32_t open_cfw_test_touch_product_null_guards(void)
{
    return (open_cfw_touch_product_05e0_bringup(
                (const open_cfw_touch_bringup_provider *)0,
                (volatile uint32_t *)0, (volatile uint32_t *)0) ==
                    UINT32_C(0xFFFFFFFF) ? 0U : 1U) |
           (open_cfw_touch_product_09b4_initialize(
                (open_cfw_touch_product_state *)0, (volatile uint32_t *)0,
                (const open_cfw_touch_product_provider *)0) ==
                    UINT32_C(0xFFFFFFFF) ? 0U : 1U);
}
