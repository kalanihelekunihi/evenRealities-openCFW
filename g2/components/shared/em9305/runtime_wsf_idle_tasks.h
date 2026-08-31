/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_EM9305_RUNTIME_WSF_IDLE_TASKS_H
#define OPEN_CFW_EM9305_RUNTIME_WSF_IDLE_TASKS_H

#include <stddef.h>
#include <stdint.h>

enum {
    OPEN_CFW_EM9305_WSF_IDLE_TASK_CAPACITY = 3,
    OPEN_CFW_EM9305_WSF_IDLE_OK = 0,
    OPEN_CFW_EM9305_WSF_IDLE_INVALID_ARGUMENT = 1,
    OPEN_CFW_EM9305_WSF_IDLE_FULL = 2,
};

typedef uint32_t (*open_cfw_em9305_wsf_idle_check_fn)(void);

/*
 * Authenticated stock layout at 0x00806060: three 32-bit callbacks followed
 * by the callback-count byte at +0x0c and the pending byte at +0x0d.
 */
typedef struct open_cfw_em9305_wsf_idle_state {
    open_cfw_em9305_wsf_idle_check_fn callbacks[
        OPEN_CFW_EM9305_WSF_IDLE_TASK_CAPACITY];
    uint8_t callback_count;
    uint8_t pending;
} open_cfw_em9305_wsf_idle_state;

void open_cfw_em9305_wsf_idle_state_init(
    open_cfw_em9305_wsf_idle_state *state);
int32_t open_cfw_em9305_wsf_idle_register(
    open_cfw_em9305_wsf_idle_state *state,
    open_cfw_em9305_wsf_idle_check_fn callback);
int32_t open_cfw_em9305_wsf_idle_request(
    open_cfw_em9305_wsf_idle_state *state);
uint32_t open_cfw_em9305_wsf_os_run_idle_tasks(
    open_cfw_em9305_wsf_idle_state *state);

#endif
