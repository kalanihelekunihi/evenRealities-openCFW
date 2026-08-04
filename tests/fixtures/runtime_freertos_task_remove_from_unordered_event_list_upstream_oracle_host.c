/*
 * SPDX-License-Identifier: MIT
 *
 * Thin adapter over pristine authenticated FreeRTOS-Kernel V10.5.1 tasks.c.
 */

#include "runtime_freertos_task_increment_tick_upstream_oracle_host.c"

void open_cfw_oracle_unordered_reset(
    uint32_t scheduler_suspended,
    uint32_t current_priority,
    uint32_t waiter_priority,
    uint32_t top_ready_priority,
    uint32_t wake_tick,
    uint32_t seed_ready
)
{
    TCB_t *waiter;

    open_cfw_oracle_freertos_task_increment_tick_reset(
        0U, scheduler_suspended, 0U, pdFALSE, 0,
        0xA5A5A5A5U, top_ready_priority, 0U,
        OPEN_CFW_ORACLE_TICK_DELAYED_LIST_1
    );
    open_cfw_oracle_freertos_task_increment_tick_set_task(
        0U, current_priority, 0U
    );
    open_cfw_oracle_freertos_task_increment_tick_set_task(
        1U, waiter_priority, wake_tick
    );
    open_cfw_oracle_freertos_task_increment_tick_insert_delayed(0U, 1U);
    open_cfw_oracle_freertos_task_increment_tick_insert_event(0U, 1U);
    if (seed_ready != 0U) {
        open_cfw_oracle_freertos_task_increment_tick_set_task(
            2U, waiter_priority, 0U
        );
        open_cfw_oracle_freertos_task_increment_tick_insert_ready(
            waiter_priority, 2U
        );
    }
    waiter = open_cfw_oracle_tick_task(1U);
    listSET_LIST_ITEM_VALUE(&waiter->xEventListItem, (TickType_t)17U);
}

void open_cfw_oracle_unordered_set_indexes(
    uint32_t event_uses_waiter,
    uint32_t blocked_uses_waiter,
    uint32_t ready_uses_seed
)
{
    TCB_t *waiter = open_cfw_oracle_tick_task(1U);
    TCB_t *seed = open_cfw_oracle_tick_task(2U);
    List_t *event = open_cfw_oracle_tick_list(
        OPEN_CFW_ORACLE_TICK_EVENT_LIST_BASE
    );
    List_t *blocked = &xDelayedTaskList1;
    List_t *ready = &pxReadyTasksLists[waiter->uxPriority];

    event->pxIndex = event_uses_waiter != 0U ?
        &waiter->xEventListItem : open_cfw_oracle_tick_list_sentinel(event);
    blocked->pxIndex = blocked_uses_waiter != 0U ?
        &waiter->xStateListItem : open_cfw_oracle_tick_list_sentinel(blocked);
    ready->pxIndex = ready_uses_seed != 0U ?
        &seed->xStateListItem : open_cfw_oracle_tick_list_sentinel(ready);
}

int32_t open_cfw_oracle_unordered_execute(uint32_t item_value)
{
    TCB_t *waiter = open_cfw_oracle_tick_task(1U);

    vTaskRemoveFromUnorderedEventList(
        &waiter->xEventListItem,
        (TickType_t)item_value
    );
    return 0;
}

uint32_t open_cfw_oracle_unordered_get_event_value(void)
{
    return (uint32_t)open_cfw_oracle_tick_task(1U)->xEventListItem.xItemValue;
}

uint32_t open_cfw_oracle_unordered_get_event_count(void)
{
    return open_cfw_oracle_freertos_task_increment_tick_get_list_count(
        OPEN_CFW_ORACLE_TICK_EVENT_LIST_BASE
    );
}

uint32_t open_cfw_oracle_unordered_get_blocked_count(void)
{
    return open_cfw_oracle_freertos_task_increment_tick_get_list_count(0U);
}

uint32_t open_cfw_oracle_unordered_get_ready_count(void)
{
    TCB_t *waiter = open_cfw_oracle_tick_task(1U);

    return open_cfw_oracle_freertos_task_increment_tick_get_list_count(
        OPEN_CFW_ORACLE_TICK_READY_LIST_BASE + waiter->uxPriority
    );
}

uint32_t open_cfw_oracle_unordered_get_event_index(void)
{
    return open_cfw_oracle_freertos_task_increment_tick_get_list_index(
        OPEN_CFW_ORACLE_TICK_EVENT_LIST_BASE
    );
}

uint32_t open_cfw_oracle_unordered_get_blocked_index(void)
{
    return open_cfw_oracle_freertos_task_increment_tick_get_list_index(0U);
}

uint32_t open_cfw_oracle_unordered_get_ready_index(void)
{
    TCB_t *waiter = open_cfw_oracle_tick_task(1U);

    return open_cfw_oracle_freertos_task_increment_tick_get_list_index(
        OPEN_CFW_ORACLE_TICK_READY_LIST_BASE + waiter->uxPriority
    );
}

uint32_t open_cfw_oracle_unordered_get_ready_head(void)
{
    TCB_t *waiter = open_cfw_oracle_tick_task(1U);

    return open_cfw_oracle_freertos_task_increment_tick_get_list_owner(
        OPEN_CFW_ORACLE_TICK_READY_LIST_BASE + waiter->uxPriority,
        0U
    );
}

uint32_t open_cfw_oracle_unordered_get_ready_tail(void)
{
    TCB_t *waiter = open_cfw_oracle_tick_task(1U);
    List_t *ready = &pxReadyTasksLists[waiter->uxPriority];

    return open_cfw_oracle_tick_task_identifier(
        ready->xListEnd.pxPrevious->pvOwner
    );
}

uint32_t open_cfw_oracle_unordered_get_state_container(void)
{
    return open_cfw_oracle_freertos_task_increment_tick_get_task_container(1U);
}

uint32_t open_cfw_oracle_unordered_get_event_container(void)
{
    return open_cfw_oracle_freertos_task_increment_tick_get_event_container(1U);
}

uint32_t open_cfw_oracle_unordered_get_top(void)
{
    return open_cfw_oracle_freertos_task_increment_tick_get_top();
}

uint32_t open_cfw_oracle_unordered_get_yield(void)
{
    return (uint32_t)
        open_cfw_oracle_freertos_task_increment_tick_get_yield();
}

uint32_t open_cfw_oracle_unordered_get_next(void)
{
    return open_cfw_oracle_freertos_task_increment_tick_get_next();
}
