/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 * SPDX-License-Identifier: MIT
 * Bounded eTaskGetState(), prvDeleteTCB(), and vTaskDelete() adaptations from
 * commit def7d2df2b0506d3d249334974f51e427c17a41c; stock G2 bodies
 * [0x00454B88,0x00454C12), [0x00455836,0x00455876), and
 * [0x00454AAE,0x00454B4C).
 */

#include "runtime_freertos_task_delete.h"

extern void open_cfw_freertos_port_enter_critical(void);
extern void open_cfw_freertos_port_exit_critical(void);
extern void open_cfw_freertos_port_yield(void);
extern open_cfw_freertos_queue_next_ubase_type open_cfw_freertos_list_remove(
    struct open_cfw_freertos_queue_next_list_item *item
);
extern void open_cfw_freertos_list_insert_end(
    struct open_cfw_freertos_queue_next_list *list,
    struct open_cfw_freertos_queue_next_list_item *item
);
extern void open_cfw_freertos_task_reset_next_task_unblock_time(void);
extern void open_cfw_freertos_heap4_free(void *memory);

#if defined(OPEN_CFW_BUILD_TASK_GET_STATE)
__attribute__((used, noinline))
enum open_cfw_freertos_task_state open_cfw_freertos_task_get_state(
    const struct open_cfw_freertos_task_delete_tcb *task
)
{
    struct open_cfw_freertos_queue_next_list *state_list;
    struct open_cfw_freertos_queue_next_list *delayed_list;
    struct open_cfw_freertos_queue_next_list *overflow_list;
    enum open_cfw_freertos_task_state state;

    OPEN_CFW_FREERTOS_TASK_DELETE_ASSERT(task != 0);
    if (task == OPEN_CFW_FREERTOS_TASK_DELETE_CURRENT_TCB_LOAD()) {
        return OPEN_CFW_FREERTOS_TASK_RUNNING;
    }
    open_cfw_freertos_port_enter_critical();
    state_list = task->state_list_item.container;
    delayed_list = OPEN_CFW_FREERTOS_TASK_DELETE_DELAYED_LIST_LOAD();
    overflow_list = OPEN_CFW_FREERTOS_TASK_DELETE_OVERFLOW_LIST_LOAD();
    open_cfw_freertos_port_exit_critical();
    if ((state_list == delayed_list) || (state_list == overflow_list)) {
        state = OPEN_CFW_FREERTOS_TASK_BLOCKED;
    } else if (state_list == OPEN_CFW_FREERTOS_TASK_DELETE_SUSPENDED_LIST()) {
        if (task->event_list_item.container != 0) {
            state = OPEN_CFW_FREERTOS_TASK_BLOCKED;
        } else if (task->notify_state == OPEN_CFW_FREERTOS_TASK_DELETE_NOTIFY_WAITING) {
            state = OPEN_CFW_FREERTOS_TASK_BLOCKED;
        } else {
            state = OPEN_CFW_FREERTOS_TASK_SUSPENDED;
        }
    } else if ((state_list == OPEN_CFW_FREERTOS_TASK_DELETE_TERMINATION_LIST()) || (state_list == 0)) {
        state = OPEN_CFW_FREERTOS_TASK_DELETED;
    } else {
        state = OPEN_CFW_FREERTOS_TASK_READY;
    }
    return state;
}
#endif

#if defined(OPEN_CFW_BUILD_TASK_DELETE_TCB)
__attribute__((used, noinline))
void open_cfw_freertos_task_delete_tcb(
    struct open_cfw_freertos_task_delete_tcb *task
)
{
    if (task->statically_allocated == OPEN_CFW_FREERTOS_TASK_DELETE_DYNAMIC_STACK_AND_TCB) {
        open_cfw_freertos_heap4_free(task->stack);
        open_cfw_freertos_heap4_free(task);
    } else if (task->statically_allocated == OPEN_CFW_FREERTOS_TASK_DELETE_STATIC_STACK_ONLY) {
        open_cfw_freertos_heap4_free(task);
    } else {
        OPEN_CFW_FREERTOS_TASK_DELETE_ASSERT(
            task->statically_allocated == OPEN_CFW_FREERTOS_TASK_DELETE_STATIC_STACK_AND_TCB
        );
    }
}
#endif

#if defined(OPEN_CFW_BUILD_TASK_DELETE)
__attribute__((used, noinline))
void open_cfw_freertos_task_delete(
    struct open_cfw_freertos_task_delete_tcb *task
)
{
    struct open_cfw_freertos_task_delete_tcb *current;

    open_cfw_freertos_port_enter_critical();
    current = OPEN_CFW_FREERTOS_TASK_DELETE_CURRENT_TCB_LOAD();
    if (task == 0) task = current;
    (void)open_cfw_freertos_list_remove(&task->state_list_item);
    if (task->event_list_item.container != 0) {
        (void)open_cfw_freertos_list_remove(&task->event_list_item);
    }
    ++OPEN_CFW_FREERTOS_TASK_DELETE_TASK_NUMBER();
    if (task == current) {
        open_cfw_freertos_list_insert_end(
            OPEN_CFW_FREERTOS_TASK_DELETE_TERMINATION_LIST(),
            &task->state_list_item
        );
        ++OPEN_CFW_FREERTOS_TASK_DELETE_CLEANUP_COUNT();
    } else {
        --OPEN_CFW_FREERTOS_TASK_DELETE_CURRENT_COUNT();
        open_cfw_freertos_task_reset_next_task_unblock_time();
    }
    open_cfw_freertos_port_exit_critical();
    if (task != current) open_cfw_freertos_task_delete_tcb(task);
    if ((OPEN_CFW_FREERTOS_TASK_DELETE_SCHEDULER_RUNNING_LOAD() != 0) && (task == current)) {
        OPEN_CFW_FREERTOS_TASK_DELETE_ASSERT(
            OPEN_CFW_FREERTOS_TASK_DELETE_SCHEDULER_SUSPENDED_LOAD() == 0U
        );
        open_cfw_freertos_port_yield();
    }
}
#endif
