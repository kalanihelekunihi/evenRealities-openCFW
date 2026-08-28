/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room, software-only boundaries for eight reachable G2 touch-policy
 * helpers. Storage, GPIO/timing, gesture, and CapSense-dependent behavior is
 * available only through explicit providers and fails closed when absent.
 */
#include "runtime_touch_policy_helpers.h"

_Static_assert(sizeof(open_cfw_touch_policy_config) ==
               OPEN_CFW_TOUCH_POLICY_CONFIG_BYTES,
               "touch policy config layout changed");

static void open_cfw_touch_policy_copy(uint8_t *destination,
                                       const uint8_t *source, size_t size)
{
    size_t index;
    for (index = 0U; index < size; ++index) {
        destination[index] = source[index];
    }
}

void open_cfw_touch_policy_defaults(open_cfw_touch_policy_state *state)
{
    if (state == NULL) {
        return;
    }
    state->config.magic = OPEN_CFW_TOUCH_POLICY_CONFIG_MAGIC;
    state->config.proximity_baseline = 0U;
    state->config.long_press_ms = OPEN_CFW_TOUCH_POLICY_DEFAULT_TIMEOUT_MS;
    state->timeout_ms = OPEN_CFW_TOUCH_POLICY_DEFAULT_TIMEOUT_MS;
    state->current_baseline = 0U;
    state->config_valid = 1U;
}

int open_cfw_touch_policy_config_read(
    const open_cfw_touch_policy_provider *provider, uint32_t offset,
    uint8_t *destination, size_t size)
{
    if (destination == NULL) {
        return OPEN_CFW_TOUCH_POLICY_BAD_ARGUMENT;
    }
    if (offset > OPEN_CFW_TOUCH_POLICY_STORAGE_LIMIT ||
        size > (size_t)(OPEN_CFW_TOUCH_POLICY_STORAGE_LIMIT - offset)) {
        return OPEN_CFW_TOUCH_POLICY_OUT_OF_RANGE;
    }
    if (provider == NULL || provider->storage_ready == NULL ||
        provider->storage_read == NULL) {
        return OPEN_CFW_TOUCH_POLICY_UNAVAILABLE;
    }
    if (provider->storage_ready(provider->context) == 0) {
        return OPEN_CFW_TOUCH_POLICY_NOT_READY;
    }
    if (provider->storage_read(provider->context, offset, destination, size) != 0) {
        return OPEN_CFW_TOUCH_POLICY_PROVIDER_ERROR;
    }
    return OPEN_CFW_TOUCH_POLICY_OK;
}

int open_cfw_touch_policy_config_load(
    open_cfw_touch_policy_state *state,
    const open_cfw_touch_policy_provider *provider)
{
    open_cfw_touch_policy_config candidate;
    int status;

    if (state == NULL) {
        return OPEN_CFW_TOUCH_POLICY_BAD_ARGUMENT;
    }
    open_cfw_touch_policy_defaults(state);
    status = open_cfw_touch_policy_config_read(
        provider, 0U, (uint8_t *)&candidate, sizeof(candidate));
    if (status != OPEN_CFW_TOUCH_POLICY_OK) {
        return status;
    }
    if (candidate.magic != OPEN_CFW_TOUCH_POLICY_CONFIG_MAGIC) {
        return OPEN_CFW_TOUCH_POLICY_INVALID_DATA;
    }
    if (candidate.long_press_ms == 0U) {
        candidate.long_press_ms = OPEN_CFW_TOUCH_POLICY_DEFAULT_TIMEOUT_MS;
    }
    open_cfw_touch_policy_copy((uint8_t *)&state->config,
                               (const uint8_t *)&candidate,
                               sizeof(candidate));
    state->timeout_ms = candidate.long_press_ms;
    state->current_baseline = candidate.proximity_baseline;
    state->config_valid = 1U;
    return OPEN_CFW_TOUCH_POLICY_OK;
}

int open_cfw_touch_policy_saved_baseline_read(
    const open_cfw_touch_policy_state *state, uint16_t *baseline)
{
    if (state == NULL || baseline == NULL) {
        return OPEN_CFW_TOUCH_POLICY_BAD_ARGUMENT;
    }
    if (state->config_valid == 0U ||
        state->config.magic != OPEN_CFW_TOUCH_POLICY_CONFIG_MAGIC) {
        return OPEN_CFW_TOUCH_POLICY_NOT_READY;
    }
    *baseline = state->config.proximity_baseline;
    return OPEN_CFW_TOUCH_POLICY_OK;
}

uint16_t open_cfw_touch_policy_timeout_default(uint16_t timeout_ms)
{
    return timeout_ms == 0U
        ? (uint16_t)OPEN_CFW_TOUCH_POLICY_DEFAULT_TIMEOUT_MS
        : timeout_ms;
}

int open_cfw_touch_policy_attention_rearm(
    const open_cfw_touch_policy_provider *provider)
{
    if (provider == NULL || provider->attention_release_timeout_rearm == NULL) {
        return OPEN_CFW_TOUCH_POLICY_UNAVAILABLE;
    }
    if (provider->attention_release_timeout_rearm(
            provider->context, OPEN_CFW_TOUCH_POLICY_ATTENTION_REARM_MS) != 0) {
        return OPEN_CFW_TOUCH_POLICY_PROVIDER_ERROR;
    }
    return OPEN_CFW_TOUCH_POLICY_OK;
}

int open_cfw_touch_policy_gesture_step(
    const open_cfw_touch_policy_provider *provider,
    const open_cfw_touch_policy_gesture_observation *observation,
    open_cfw_touch_policy_gesture *gesture)
{
    open_cfw_touch_policy_gesture candidate;

    if (observation == NULL || gesture == NULL) {
        return OPEN_CFW_TOUCH_POLICY_BAD_ARGUMENT;
    }
    if (provider == NULL || provider->gesture_policy_step == NULL) {
        return OPEN_CFW_TOUCH_POLICY_UNAVAILABLE;
    }
    candidate = OPEN_CFW_TOUCH_POLICY_GESTURE_NONE;
    if (provider->gesture_policy_step(provider->context, observation,
                                      &candidate) != 0) {
        return OPEN_CFW_TOUCH_POLICY_PROVIDER_ERROR;
    }
    if ((unsigned int)candidate >
        (unsigned int)OPEN_CFW_TOUCH_POLICY_GESTURE_FIVE_FAST_CLICKS) {
        return OPEN_CFW_TOUCH_POLICY_INVALID_DATA;
    }
    *gesture = candidate;
    return OPEN_CFW_TOUCH_POLICY_OK;
}

int open_cfw_touch_policy_baseline_update(
    open_cfw_touch_policy_state *state,
    const open_cfw_touch_policy_provider *provider)
{
    uint16_t candidate;

    if (state == NULL) {
        return OPEN_CFW_TOUCH_POLICY_BAD_ARGUMENT;
    }
    if (state->config_valid == 0U ||
        state->config.magic != OPEN_CFW_TOUCH_POLICY_CONFIG_MAGIC) {
        return OPEN_CFW_TOUCH_POLICY_NOT_READY;
    }
    if (provider == NULL || provider->baseline_update == NULL) {
        return OPEN_CFW_TOUCH_POLICY_UNAVAILABLE;
    }
    candidate = state->current_baseline;
    if (provider->baseline_update(provider->context,
                                  state->config.proximity_baseline,
                                  &candidate) != 0) {
        return OPEN_CFW_TOUCH_POLICY_PROVIDER_ERROR;
    }
    state->current_baseline = candidate;
    return OPEN_CFW_TOUCH_POLICY_OK;
}
