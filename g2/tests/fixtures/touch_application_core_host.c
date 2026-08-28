/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include <stdint.h>

#include "../../components/shared/touch/runtime_touch_application_core.c"

typedef struct test_context {
    open_cfw_touch_application_record_view record;
    uint32_t log[128];
    uint32_t count;
    uint32_t exists;
    uint32_t poll_remaining;
    uint32_t preflight_result;
} test_context;

static void push(test_context *context, uint32_t value)
{
    if (context->count < 128U) {
        context->log[context->count++] = value;
    }
}

static open_cfw_touch_application_record_view *record_at(
    void *raw, uint32_t index, void *object)
{
    test_context *context = (test_context *)raw;
    (void)object;
    push(context, UINT32_C(0x10000000) | index);
    return &context->record;
}

static uint32_t object_exists(void *raw, uint32_t index, void *object)
{
    test_context *context = (test_context *)raw;
    (void)object;
    push(context, UINT32_C(0x20000000) | index);
    return context->exists;
}

static void update_pointer(void *raw, uint32_t index, void *object)
{
    (void)object;
    push((test_context *)raw, UINT32_C(0x30000000) | index);
}

static void selection_update(
    void *raw, open_cfw_touch_application_record_view *record, void *object)
{
    (void)record;
    (void)object;
    push((test_context *)raw, UINT32_C(0x40000000));
}

static uint32_t sample_index(test_context *context, uint8_t *sample)
{
    return (uint32_t)(sample - context->record.samples) / 10U;
}

static void prepare_sample(
    void *raw, open_cfw_touch_application_record_view *record,
    uint8_t *sample, uint8_t *coefficients, uint8_t *mode_byte)
{
    test_context *context = (test_context *)raw;
    (void)record;
    (void)coefficients;
    push(context, UINT32_C(0x50000000) | sample_index(context, sample) |
                  (mode_byte != NULL ? UINT32_C(0x100) : 0U));
}

static uint32_t process_sample(
    void *raw, void *algorithm, uint8_t *sample,
    uint16_t *auxiliary, void *object)
{
    test_context *context = (test_context *)raw;
    uint32_t index = sample_index(context, sample);
    (void)algorithm;
    (void)auxiliary;
    (void)object;
    push(context, UINT32_C(0x60000000) | index);
    return UINT32_C(1) << index;
}

static void finish_sample(void *raw, void *algorithm, uint8_t *sample)
{
    test_context *context = (test_context *)raw;
    (void)algorithm;
    push(context, UINT32_C(0x70000000) | sample_index(context, sample));
}

static void apply_four(
    void *raw, open_cfw_touch_application_record_view *record,
    uint8_t *sample, uint8_t *coefficients)
{
    test_context *context = (test_context *)raw;
    (void)record;
    push(context, UINT32_C(0x81000000) | sample_index(context, sample) |
                  ((uint32_t)(coefficients - context->record.coefficients) << 8U));
}

static void apply_two(
    void *raw, open_cfw_touch_application_record_view *record,
    uint8_t *sample, uint8_t *coefficients, uint8_t *mode_byte)
{
    test_context *context = (test_context *)raw;
    (void)record;
    push(context, UINT32_C(0x82000000) | sample_index(context, sample) |
                  ((uint32_t)(coefficients - context->record.coefficients) << 8U) |
                  (mode_byte != NULL ? UINT32_C(0x80) : 0U));
}

static void apply_final(
    void *raw, open_cfw_touch_application_record_view *record,
    uint8_t *sample, uint8_t *coefficients)
{
    test_context *context = (test_context *)raw;
    (void)record;
    push(context, UINT32_C(0x83000000) | sample_index(context, sample) |
                  ((uint32_t)(coefficients - context->record.coefficients) << 8U));
}

static open_cfw_touch_application_core_provider core_provider(
    test_context *context)
{
    open_cfw_touch_application_core_provider provider = {
        record_at, object_exists, update_pointer, selection_update,
        prepare_sample, process_sample, finish_sample,
        apply_four, apply_two, apply_final, context,
    };
    return provider;
}

static void run_notify(void *raw, uint32_t event, void *object)
{
    (void)object;
    push((test_context *)raw, UINT32_C(0x90000000) | event);
}

static uint32_t run_preflight(void *raw, void *object)
{
    test_context *context = (test_context *)raw;
    (void)object;
    push(context, UINT32_C(0x91000000));
    return context->preflight_result;
}

static uint32_t run_stage_a(void *raw, void *object)
{
    (void)object;
    push((test_context *)raw, UINT32_C(0x92000000));
    return 1U;
}

static uint32_t run_stage_b(void *raw, void *object)
{
    (void)object;
    push((test_context *)raw, UINT32_C(0x93000000));
    return 2U;
}

static uint32_t run_stage_c(void *raw, void *object)
{
    (void)object;
    push((test_context *)raw, UINT32_C(0x94000000));
    return 0U;
}

static uint32_t retry_budget(
    void *raw, uint32_t reference_hz, uint32_t timebase_megahertz,
    uint32_t limit)
{
    test_context *context = (test_context *)raw;
    push(context, reference_hz);
    push(context, timebase_megahertz);
    push(context, limit);
    return 2U;
}

static uint32_t run_poll(void *raw, void *object)
{
    test_context *context = (test_context *)raw;
    (void)object;
    push(context, UINT32_C(0x95000000));
    if (context->poll_remaining == 0U) {
        return 0U;
    }
    --context->poll_remaining;
    return 1U;
}

static void run_update(void *raw, uint32_t index, void *object)
{
    (void)object;
    push((test_context *)raw, UINT32_C(0x96000000) | index);
}

static void run_update_all(void *raw, void *object)
{
    (void)object;
    push((test_context *)raw, UINT32_C(0x97000000));
}

static void run_shutdown(void *raw, void *object)
{
    (void)object;
    push((test_context *)raw, UINT32_C(0x98000000));
}

static open_cfw_touch_application_run_provider run_provider(test_context *context)
{
    open_cfw_touch_application_run_provider provider = {
        run_notify, run_preflight, run_stage_a, run_stage_b, run_stage_c,
        retry_budget, run_poll, run_update, run_update_all, run_shutdown,
        context,
    };
    return provider;
}

uint32_t open_cfw_test_touch_application_data_core(void)
{
    uint8_t samples[20] = {0U};
    uint16_t auxiliary[2] = {0U};
    uint8_t coefficients[16] = {0U};
    uint8_t modes[2] = {0U};
    test_context context = {0};
    open_cfw_touch_application_core_provider provider;
    uint8_t object = 0U;
    uint32_t result = 0U;

    context.record.algorithm = &object;
    context.record.samples = samples;
    context.record.auxiliary = auxiliary;
    context.record.coefficients = coefficients;
    context.record.mode_bytes = modes;
    context.record.sample_count = 2U;
    context.record.flags = UINT16_C(0x0692);
    context.record.mode = 1U;
    context.exists = 1U;
    provider = core_provider(&context);

    open_cfw_touch_application_1b6c_update(1U, &object, &provider);
    result |= context.count == 7U &&
                      context.log[0] == UINT32_C(0x10000001) &&
                      context.log[1] == UINT32_C(0x81000000) &&
                      context.log[2] == UINT32_C(0x82000480) &&
                      context.log[3] == UINT32_C(0x83000600) &&
                      context.log[4] == UINT32_C(0x81000401) &&
                      context.log[5] == UINT32_C(0x82000881) &&
                      context.log[6] == UINT32_C(0x83000A01) ? 1U : 0U;

    context.count = 0U;
    result |= open_cfw_touch_application_2638_dispatch(
                  1U, &object, &provider) == 3U && context.count == 7U &&
                      context.log[1] == UINT32_C(0x50000100) &&
                      context.log[2] == UINT32_C(0x60000000) &&
                      context.log[3] == UINT32_C(0x70000000) &&
                      context.log[4] == UINT32_C(0x50000101) &&
                      context.log[5] == UINT32_C(0x60000001) &&
                      context.log[6] == UINT32_C(0x70000001) ? 2U : 0U;

    context.count = 0U;
    result |= open_cfw_touch_application_18a8_process(
                  1U, &object, &provider) == 3U && context.count == 11U &&
                      context.log[0] == UINT32_C(0x10000001) &&
                      context.log[1] == UINT32_C(0x20000001) &&
                      context.log[2] == UINT32_C(0x30000001) &&
                      context.log[10] == UINT32_C(0x40000000) ? 4U : 0U;

    context.count = 0U;
    context.record.lifecycle = 7U;
    result |= open_cfw_touch_application_18a8_process(
                  1U, &object, &provider) == 1U && context.count == 1U
                  ? 8U : 0U;
    return result;
}

uint32_t open_cfw_test_touch_application_run_core(void)
{
    test_context context = {0};
    open_cfw_touch_application_run_provider provider = run_provider(&context);
    uint8_t object = 0U;
    uint8_t busy = 9U;
    uint32_t flags = UINT32_C(0x1234);
    uint32_t result = 0U;

    context.poll_remaining = 3U;
    result |= open_cfw_touch_application_17f4_run(
                  &object, &flags, &busy, UINT32_C(12000000), &provider) == 4U &&
                      flags == UINT32_C(0x1234) && busy == 1U ? 1U : 0U;
    result |= context.count == 17U &&
                      context.log[0] == UINT32_C(0x90000001) &&
                      context.log[1] == UINT32_C(0x91000000) &&
                      context.log[5] == UINT32_C(1000000) &&
                      context.log[6] == 12U && context.log[7] == 5U &&
                      context.log[11] == UINT32_C(0x90000001) &&
                      context.log[12] == UINT32_C(0x96000000) &&
                      context.log[14] == UINT32_C(0x96000002) &&
                      context.log[15] == UINT32_C(0x97000000) &&
                      context.log[16] == UINT32_C(0x98000000) ? 2U : 0U;

    context.count = 0U;
    context.preflight_result = 5U;
    busy = 9U;
    result |= open_cfw_touch_application_17f4_run(
                  &object, &flags, &busy, UINT32_C(12000000), &provider) == 5U &&
                      flags == UINT32_C(0x1234) && busy == 0U &&
                      context.count == 4U &&
                      context.log[2] == UINT32_C(0x97000000) &&
                      context.log[3] == UINT32_C(0x98000000) ? 4U : 0U;
    return result;
}

uint32_t open_cfw_test_touch_application_core_null_guards(void)
{
    open_cfw_touch_application_1b6c_update(
        0U, (void *)0, (const open_cfw_touch_application_core_provider *)0);
    return open_cfw_touch_application_2638_dispatch(
               0U, (void *)0,
               (const open_cfw_touch_application_core_provider *)0) |
           (open_cfw_touch_application_18a8_process(
                4U, (void *)0,
                (const open_cfw_touch_application_core_provider *)0) == 1U
                ? 0U : 1U) |
           (open_cfw_touch_application_17f4_run(
                (void *)0, (volatile uint32_t *)0, (uint8_t *)0, 0U,
                (const open_cfw_touch_application_run_provider *)0) ==
                    UINT32_C(0xFFFFFFFF) ? 0U : 1U);
}
