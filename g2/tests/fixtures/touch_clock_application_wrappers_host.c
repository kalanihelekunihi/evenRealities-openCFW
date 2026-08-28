/* SPDX-License-Identifier: MIT */
#include <stdint.h>

#include "../../components/shared/touch/runtime_touch_clock_application_wrappers.c"

typedef struct test_context {
    uint32_t log[64];
    uint32_t count;
    uint32_t divider_calls;
    uint32_t divider_failure_call;
    uint32_t measurement;
    uint32_t preflight_result;
    uint32_t status_result;
    uint32_t exists_mask;
} test_context;

static void push(test_context *context, uint32_t value)
{
    if (context->count < 64U) {
        context->log[context->count++] = value;
    }
}

static uint32_t set_divider(void *raw, uint32_t divider)
{
    test_context *context = (test_context *)raw;
    ++context->divider_calls;
    push(context, UINT32_C(0xD1000000) | divider);
    return context->divider_calls == context->divider_failure_call ? 1U : 0U;
}

static void fault(void *raw, uint32_t reason)
{
    push((test_context *)raw, UINT32_C(0xFA000000) | reason);
}

static void power(void *raw, uint32_t mode)
{
    push((test_context *)raw, UINT32_C(0xA0000000) | mode);
}

static void delay_call(void *raw, uint32_t count)
{
    push((test_context *)raw, count);
}

static void select_clock(void *raw, uint32_t selection)
{
    push((test_context *)raw, UINT32_C(0xC1000000) | selection);
}

static uint32_t measure(void *raw)
{
    test_context *context = (test_context *)raw;
    push(context, UINT32_C(0x4D000000));
    return context->measurement;
}

static uint32_t preflight(void *raw, void *object)
{
    test_context *context = (test_context *)raw;
    (void)object;
    push(context, UINT32_C(0x10000000));
    return context->preflight_result;
}

static void reset_object(void *raw, void *object)
{
    (void)object;
    push((test_context *)raw, UINT32_C(0x20000000));
}

static uint32_t status_object(void *raw, void *object)
{
    test_context *context = (test_context *)raw;
    (void)object;
    push(context, UINT32_C(0x30000000));
    return context->status_result;
}

static void finalize_object(void *raw, void *object)
{
    (void)object;
    push((test_context *)raw, UINT32_C(0x40000000));
}

static uint32_t object_exists(void *raw, uint32_t index, void *object)
{
    test_context *context = (test_context *)raw;
    (void)object;
    push(context, UINT32_C(0x50000000) | index);
    return (context->exists_mask >> index) & 1U;
}

static uint32_t process_object(void *raw, uint32_t index, void *object)
{
    (void)object;
    push((test_context *)raw, UINT32_C(0x60000000) | index);
    return UINT32_C(1) << index;
}

static void update_pointer(void *raw, uint32_t index, void *object)
{
    (void)object;
    push((test_context *)raw, UINT32_C(0x70000000) | index);
}

static open_cfw_touch_clock_provider clock_provider(test_context *context)
{
    open_cfw_touch_clock_provider provider = {
        set_divider, fault, power, delay_call, select_clock, measure, context,
    };
    return provider;
}

static open_cfw_touch_application_provider application_provider(
    test_context *context)
{
    open_cfw_touch_application_provider provider = {
        preflight, reset_object, status_object, finalize_object,
        object_exists, process_object, update_pointer, context,
    };
    return provider;
}

uint32_t open_cfw_test_touch_clock_wrappers(void)
{
    test_context context = {{0U}, 0U, 0U, 1U, UINT32_C(2000001), 0U, 0U, 0U};
    open_cfw_touch_clock_provider provider = clock_provider(&context);
    uint32_t divider = UINT32_C(0xFFFFFFFF);
    uint32_t clock_select_control = UINT32_C(0x12345678);
    uint32_t path = 0U;
    open_cfw_touch_clock_register_view registers = {
        &divider, &clock_select_control, &path,
    };
    open_cfw_touch_clock_state state = {0U, 0U, 0U, 0U};
    uint32_t result = 0U;

    open_cfw_touch_clock_12ac_validate(&registers, &provider);
    result |= divider == UINT32_C(0xFFFFFFF3) && context.count == 2U &&
                      context.log[0] == UINT32_C(0xD1000000) &&
                      context.log[1] == UINT32_C(0xFA000006) ? 1U : 0U;

    context.count = 0U;
    context.divider_calls = 0U;
    context.divider_failure_call = 2U;
    divider = UINT32_C(0xFFFFFFFF);
    open_cfw_touch_clock_12d0_transition(&registers, &state, &provider);
    result |= path == UINT32_C(0x80000000) &&
                      clock_select_control == UINT32_C(0x92345678) &&
                      divider == UINT32_C(0xFFFFFF33) ? 2U : 0U;
    result |= state.frequency_hz == UINT32_C(2000001) &&
                      state.megahertz_ceiling == 3U &&
                      state.kilohertz_ceiling == UINT32_C(2001) &&
                      state.scaled_kilohertz == UINT32_C(65568768) ? 4U : 0U;
    result |= context.count == 10U &&
                      context.log[0] == UINT32_C(0xA0000030) &&
                      context.log[1] == UINT32_C(0x016E3600) &&
                      context.log[2] == UINT32_C(0xD1000000) &&
                      context.log[3] == UINT32_C(0x4D000000) &&
                      context.log[4] == UINT32_C(0xC1000000) &&
                      context.log[5] == UINT32_C(0x02DC6C00) &&
                      context.log[6] == UINT32_C(0xD1000000) &&
                      context.log[7] == UINT32_C(0xFA000006) &&
                      context.log[8] == UINT32_C(0xA0000030) &&
                      context.log[9] == UINT32_C(0x4D000000) ? 8U : 0U;
    return result;
}

uint32_t open_cfw_test_touch_application_wrappers(void)
{
    test_context context = {{0U}, 0U, 0U, 0U, 0U, 0U, UINT32_C(0x22), 5U};
    open_cfw_touch_application_provider provider = application_provider(&context);
    uint8_t object = 0U;
    uint8_t initialized = 0U;
    uint8_t records[3U * 144U] = {0U};
    uint32_t result = 0U;

    records[1U * 144U + 0x7BU] = 7U;
    result |= open_cfw_touch_application_17be_preflight(
                  &object, &initialized, &provider) == UINT32_C(0x22) &&
                      initialized == 1U && context.count == 4U ? 1U : 0U;
    context.count = 0U;
    context.preflight_result = 5U;
    result |= open_cfw_touch_application_17be_preflight(
                  &object, &initialized, &provider) == 5U &&
                      context.count == 1U ? 2U : 0U;

    context.count = 0U;
    context.preflight_result = 0U;
    result |= open_cfw_touch_application_1904_process_three(
                  &object, records, 144U, &provider) == 5U &&
                      context.count == 5U &&
                      context.log[0] == UINT32_C(0x50000002) &&
                      context.log[1] == UINT32_C(0x60000002) &&
                      context.log[2] == UINT32_C(0x50000001) &&
                      context.log[3] == UINT32_C(0x50000000) &&
                      context.log[4] == UINT32_C(0x60000000) ? 4U : 0U;

    context.count = 0U;
    open_cfw_touch_application_1c54_update_three(&object, &provider);
    result |= context.count == 3U &&
                      context.log[0] == UINT32_C(0x70000002) &&
                      context.log[1] == UINT32_C(0x70000001) &&
                      context.log[2] == UINT32_C(0x70000000) ? 8U : 0U;
    return result;
}

uint32_t open_cfw_test_touch_clock_application_null_guards(void)
{
    uint32_t value = open_cfw_touch_application_17be_preflight(
        (void *)0, (uint8_t *)0,
        (const open_cfw_touch_application_provider *)0);
    open_cfw_touch_clock_12ac_validate(
        (const open_cfw_touch_clock_register_view *)0,
        (const open_cfw_touch_clock_provider *)0);
    open_cfw_touch_clock_1434_calibrate(
        0U, (open_cfw_touch_clock_state *)0,
        (const open_cfw_touch_clock_provider *)0);
    open_cfw_touch_clock_12d0_transition(
        (const open_cfw_touch_clock_register_view *)0,
        (open_cfw_touch_clock_state *)0,
        (const open_cfw_touch_clock_provider *)0);
    open_cfw_touch_application_1c54_update_three(
        (void *)0, (const open_cfw_touch_application_provider *)0);
    return value == UINT32_C(0xFFFFFFFF) &&
                   open_cfw_touch_application_1904_process_three(
                       (void *)0, (const uint8_t *)0, 0U,
                       (const open_cfw_touch_application_provider *)0) == 0U
               ? 0U : 1U;
}
