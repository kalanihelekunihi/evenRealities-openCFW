/*
 * Copyright (c) 2013-2022 Arm Limited. All rights reserved.
 * SPDX-License-Identifier: Apache-2.0
 *
 * Bounded, freestanding candidates for CMSIS-FreeRTOS v10.5.1
 * osTimerStart(), osTimerStop(), and osTimerDelete() at commit
 * d213f261b5be6bb29a7cce8b84071706b72f4d53.
 */

typedef __UINT32_TYPE__ open_cfw_cmsis_timer_ops_uint32;
typedef __INT32_TYPE__ open_cfw_cmsis_timer_ops_status;
typedef void *open_cfw_cmsis_timer_ops_id;

enum {
    OPEN_CFW_CMSIS_TIMER_OPS_OK = 0,
    OPEN_CFW_CMSIS_TIMER_OPS_ERROR = -1,
    OPEN_CFW_CMSIS_TIMER_OPS_ERROR_RESOURCE = -3,
    OPEN_CFW_CMSIS_TIMER_OPS_ERROR_PARAMETER = -4,
    OPEN_CFW_CMSIS_TIMER_OPS_ERROR_ISR = -6,
    OPEN_CFW_CMSIS_TIMER_OPS_COMMAND_STOP = 3,
    OPEN_CFW_CMSIS_TIMER_OPS_COMMAND_CHANGE_PERIOD = 4,
    OPEN_CFW_CMSIS_TIMER_OPS_COMMAND_DELETE = 5
};

extern open_cfw_cmsis_timer_ops_uint32 open_cfw_cmsis_irq_context(void);
extern open_cfw_cmsis_timer_ops_uint32 open_cfw_rtos_timer_command(
    const void *timer,
    int command_id,
    open_cfw_cmsis_timer_ops_uint32 optional_value,
    open_cfw_cmsis_timer_ops_uint32 *higher_priority_task_woken,
    open_cfw_cmsis_timer_ops_uint32 ticks_to_wait
);
extern open_cfw_cmsis_timer_ops_uint32 open_cfw_rtos_timer_is_active(
    const void *timer
);
extern void *open_cfw_rtos_timer_get_context(const void *timer);
extern void open_cfw_freertos_heap4_free(void *memory);

__attribute__((used, noinline))
open_cfw_cmsis_timer_ops_status open_cfw_cmsis_timer_start(
    open_cfw_cmsis_timer_ops_id timer_id,
    open_cfw_cmsis_timer_ops_uint32 ticks
)
{
    if (open_cfw_cmsis_irq_context() != 0U) {
        return OPEN_CFW_CMSIS_TIMER_OPS_ERROR_ISR;
    }
    if ((timer_id == (open_cfw_cmsis_timer_ops_id)0) || (ticks == 0U)) {
        return OPEN_CFW_CMSIS_TIMER_OPS_ERROR_PARAMETER;
    }
    if (
        open_cfw_rtos_timer_command(
            timer_id,
            OPEN_CFW_CMSIS_TIMER_OPS_COMMAND_CHANGE_PERIOD,
            ticks,
            0,
            0U
        ) == 0U
    ) {
        return OPEN_CFW_CMSIS_TIMER_OPS_ERROR_RESOURCE;
    }
    return OPEN_CFW_CMSIS_TIMER_OPS_OK;
}

__attribute__((used, noinline))
open_cfw_cmsis_timer_ops_status open_cfw_cmsis_timer_stop(
    open_cfw_cmsis_timer_ops_id timer_id
)
{
    if (open_cfw_cmsis_irq_context() != 0U) {
        return OPEN_CFW_CMSIS_TIMER_OPS_ERROR_ISR;
    }
    if (timer_id == (open_cfw_cmsis_timer_ops_id)0) {
        return OPEN_CFW_CMSIS_TIMER_OPS_ERROR_PARAMETER;
    }
    if (open_cfw_rtos_timer_is_active(timer_id) == 0U) {
        return OPEN_CFW_CMSIS_TIMER_OPS_ERROR_RESOURCE;
    }
    if (
        open_cfw_rtos_timer_command(
            timer_id,
            OPEN_CFW_CMSIS_TIMER_OPS_COMMAND_STOP,
            0U,
            0,
            0U
        ) == 0U
    ) {
        return OPEN_CFW_CMSIS_TIMER_OPS_ERROR;
    }
    return OPEN_CFW_CMSIS_TIMER_OPS_OK;
}

__attribute__((used, noinline))
open_cfw_cmsis_timer_ops_status open_cfw_cmsis_timer_delete(
    open_cfw_cmsis_timer_ops_id timer_id
)
{
    void *callback;

    if (open_cfw_cmsis_irq_context() != 0U) {
        return OPEN_CFW_CMSIS_TIMER_OPS_ERROR_ISR;
    }
    if (timer_id == (open_cfw_cmsis_timer_ops_id)0) {
        return OPEN_CFW_CMSIS_TIMER_OPS_ERROR_PARAMETER;
    }

    callback = open_cfw_rtos_timer_get_context(timer_id);
    if (
        open_cfw_rtos_timer_command(
            timer_id,
            OPEN_CFW_CMSIS_TIMER_OPS_COMMAND_DELETE,
            0U,
            0,
            0U
        ) == 0U
    ) {
        return OPEN_CFW_CMSIS_TIMER_OPS_ERROR_RESOURCE;
    }

    if (((__UINTPTR_TYPE__)callback & 1U) != 0U) {
        open_cfw_freertos_heap4_free(
            (void *)((__UINTPTR_TYPE__)callback & ~(__UINTPTR_TYPE__)1U)
        );
    }
    return OPEN_CFW_CMSIS_TIMER_OPS_OK;
}
