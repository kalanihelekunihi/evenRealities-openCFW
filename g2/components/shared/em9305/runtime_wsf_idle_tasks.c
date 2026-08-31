/* SPDX-License-Identifier: MIT */
/*
 * Clean-room implementation of the authenticated EM9305
 * wsfOsRunIdleTasks routine at 0x00333d7c.  The callback iteration and
 * one-bit activity reduction also agree with Packetcraft Cordio's
 * Apache-2.0 bare-metal WSF idle loop at pinned commit
 * 3656312d6b73e2a2c1c8b33ee0385bc199dd97e6.
 */

#include "runtime_wsf_idle_tasks.h"

void open_cfw_em9305_wsf_idle_state_init(
    open_cfw_em9305_wsf_idle_state *state)
{
    size_t index;

    if (state == 0) {
        return;
    }
    for (index = 0; index < OPEN_CFW_EM9305_WSF_IDLE_TASK_CAPACITY; ++index) {
        state->callbacks[index] = 0;
    }
    state->callback_count = 0U;
    state->pending = 0U;
}

int32_t open_cfw_em9305_wsf_idle_register(
    open_cfw_em9305_wsf_idle_state *state,
    open_cfw_em9305_wsf_idle_check_fn callback)
{
    if (state == 0 || callback == 0) {
        return OPEN_CFW_EM9305_WSF_IDLE_INVALID_ARGUMENT;
    }
    if (state->callback_count >= OPEN_CFW_EM9305_WSF_IDLE_TASK_CAPACITY) {
        return OPEN_CFW_EM9305_WSF_IDLE_FULL;
    }
    state->callbacks[state->callback_count] = callback;
    ++state->callback_count;
    return OPEN_CFW_EM9305_WSF_IDLE_OK;
}

int32_t open_cfw_em9305_wsf_idle_request(
    open_cfw_em9305_wsf_idle_state *state)
{
    if (state == 0 ||
        state->callback_count > OPEN_CFW_EM9305_WSF_IDLE_TASK_CAPACITY) {
        return OPEN_CFW_EM9305_WSF_IDLE_INVALID_ARGUMENT;
    }
    state->pending = 1U;
    return OPEN_CFW_EM9305_WSF_IDLE_OK;
}

uint32_t open_cfw_em9305_wsf_os_run_idle_tasks(
    open_cfw_em9305_wsf_idle_state *state)
{
    uint32_t active = 0U;
    uint8_t index;

    if (state == 0 || state->pending == 0U ||
        state->callback_count > OPEN_CFW_EM9305_WSF_IDLE_TASK_CAPACITY) {
        return 0U;
    }
    for (index = 0U; index < state->callback_count; ++index) {
        open_cfw_em9305_wsf_idle_check_fn callback = state->callbacks[index];
        if (callback != 0) {
            active |= callback() & 1U;
        }
    }
    state->pending = (uint8_t)(active & 1U);
    return active & 1U;
}
