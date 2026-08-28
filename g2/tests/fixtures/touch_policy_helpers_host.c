/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include <string.h>

#include "../../components/shared/touch/runtime_touch_policy_helpers.c"

typedef struct test_context {
    uint8_t storage[OPEN_CFW_TOUCH_POLICY_STORAGE_LIMIT];
    int ready;
    int fail;
    uint32_t delay_ms;
    uint16_t saved_baseline;
    uint16_t next_baseline;
    open_cfw_touch_policy_gesture next_gesture;
} test_context;

static int test_ready(void *raw)
{
    return ((test_context *)raw)->ready;
}

static int test_read(void *raw, uint32_t offset, uint8_t *destination,
                     size_t size)
{
    test_context *context = (test_context *)raw;
    if (context->fail != 0) {
        return -1;
    }
    (void)memcpy(destination, &context->storage[offset], size);
    return 0;
}

static int test_attention(void *raw, uint32_t delay_ms)
{
    test_context *context = (test_context *)raw;
    context->delay_ms = delay_ms;
    return context->fail;
}

static int test_gesture(
    void *raw, const open_cfw_touch_policy_gesture_observation *observation,
    open_cfw_touch_policy_gesture *gesture)
{
    test_context *context = (test_context *)raw;
    if (context->fail != 0 || observation->pressed == 0U) {
        return -1;
    }
    *gesture = context->next_gesture;
    return 0;
}

static int test_baseline(void *raw, uint16_t saved, uint16_t *current)
{
    test_context *context = (test_context *)raw;
    context->saved_baseline = saved;
    if (context->fail != 0) {
        return -1;
    }
    *current = context->next_baseline;
    return 0;
}

static open_cfw_touch_policy_provider test_provider(test_context *context)
{
    open_cfw_touch_policy_provider provider;
    provider.storage_ready = test_ready;
    provider.storage_read = test_read;
    provider.attention_release_timeout_rearm = test_attention;
    provider.gesture_policy_step = test_gesture;
    provider.baseline_update = test_baseline;
    provider.context = context;
    return provider;
}

uint32_t open_cfw_test_touch_policy_config(void)
{
    uint32_t bits = 0U;
    test_context context = {0};
    open_cfw_touch_policy_provider provider = test_provider(&context);
    open_cfw_touch_policy_config stored = {
        OPEN_CFW_TOUCH_POLICY_CONFIG_MAGIC, 321U, 777U
    };
    open_cfw_touch_policy_state state;
    uint16_t baseline = 0U;
    uint8_t byte = 0U;

    (void)memcpy(context.storage, &stored, sizeof(stored));
    context.ready = 1;
    if (open_cfw_touch_policy_config_load(&state, &provider) == 0 &&
        state.config.proximity_baseline == 321U &&
        state.timeout_ms == 777U) {
        bits |= 1U;
    }
    if (open_cfw_touch_policy_saved_baseline_read(&state, &baseline) == 0 &&
        baseline == 321U) {
        bits |= 2U;
    }
    if (open_cfw_touch_policy_config_read(&provider, 255U, &byte, 2U) ==
        OPEN_CFW_TOUCH_POLICY_OUT_OF_RANGE) {
        bits |= 4U;
    }
    context.ready = 0;
    if (open_cfw_touch_policy_config_read(&provider, 0U, &byte, 1U) ==
        OPEN_CFW_TOUCH_POLICY_NOT_READY) {
        bits |= 8U;
    }
    stored.magic = 0U;
    (void)memcpy(context.storage, &stored, sizeof(stored));
    context.ready = 1;
    if (open_cfw_touch_policy_config_load(&state, &provider) ==
            OPEN_CFW_TOUCH_POLICY_INVALID_DATA &&
        state.config.magic == OPEN_CFW_TOUCH_POLICY_CONFIG_MAGIC &&
        state.config.long_press_ms == 1000U) {
        bits |= 16U;
    }
    return bits;
}

uint32_t open_cfw_test_touch_policy_provider_boundaries(void)
{
    uint32_t bits = 0U;
    test_context context = {0};
    open_cfw_touch_policy_provider provider = test_provider(&context);
    open_cfw_touch_policy_state state;
    open_cfw_touch_policy_gesture_observation observation = {
        12, 34U, 56U, 1U, 0U
    };
    open_cfw_touch_policy_gesture gesture = OPEN_CFW_TOUCH_POLICY_GESTURE_NONE;

    open_cfw_touch_policy_defaults(&state);
    state.config.proximity_baseline = 400U;
    context.next_baseline = 444U;
    context.next_gesture = OPEN_CFW_TOUCH_POLICY_GESTURE_RIGHT;
    if (open_cfw_touch_policy_attention_rearm(NULL) ==
            OPEN_CFW_TOUCH_POLICY_UNAVAILABLE &&
        open_cfw_touch_policy_gesture_step(NULL, &observation, &gesture) ==
            OPEN_CFW_TOUCH_POLICY_UNAVAILABLE &&
        open_cfw_touch_policy_baseline_update(&state, NULL) ==
            OPEN_CFW_TOUCH_POLICY_UNAVAILABLE) {
        bits |= 1U;
    }
    if (open_cfw_touch_policy_attention_rearm(&provider) == 0 &&
        context.delay_ms == 200U) {
        bits |= 2U;
    }
    if (open_cfw_touch_policy_gesture_step(&provider, &observation, &gesture) == 0 &&
        gesture == OPEN_CFW_TOUCH_POLICY_GESTURE_RIGHT) {
        bits |= 4U;
    }
    if (open_cfw_touch_policy_baseline_update(&state, &provider) == 0 &&
        context.saved_baseline == 400U && state.current_baseline == 444U) {
        bits |= 8U;
    }
    context.fail = 1;
    if (open_cfw_touch_policy_attention_rearm(&provider) ==
            OPEN_CFW_TOUCH_POLICY_PROVIDER_ERROR &&
        open_cfw_touch_policy_baseline_update(&state, &provider) ==
            OPEN_CFW_TOUCH_POLICY_PROVIDER_ERROR &&
        state.current_baseline == 444U) {
        bits |= 16U;
    }
    return bits;
}

uint32_t open_cfw_test_touch_policy_defaults(void)
{
    uint32_t bits = 0U;
    open_cfw_touch_policy_state state;
    uint16_t baseline = 9U;

    open_cfw_touch_policy_defaults(&state);
    if (state.config.magic == OPEN_CFW_TOUCH_POLICY_CONFIG_MAGIC &&
        state.config.long_press_ms == 1000U && state.config_valid == 1U) {
        bits |= 1U;
    }
    if (open_cfw_touch_policy_timeout_default(0U) == 1000U &&
        open_cfw_touch_policy_timeout_default(77U) == 77U) {
        bits |= 2U;
    }
    state.config_valid = 0U;
    if (open_cfw_touch_policy_saved_baseline_read(&state, &baseline) ==
            OPEN_CFW_TOUCH_POLICY_NOT_READY && baseline == 9U) {
        bits |= 4U;
    }
    if (open_cfw_touch_policy_config_load(NULL, NULL) ==
            OPEN_CFW_TOUCH_POLICY_BAD_ARGUMENT) {
        bits |= 8U;
    }
    return bits;
}
