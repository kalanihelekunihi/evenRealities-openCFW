/*
 * SPDX-License-Identifier: MIT
 *
 * Thin xTaskResumeAll() adapter over the authenticated pristine
 * FreeRTOS-Kernel V10.5.1 tasks.c oracle translation unit.  The included
 * fixture supplies the recovered G2 configuration and host-only port seams;
 * this file only exposes pending-ready graph construction and snapshots.
 */

#include "runtime_freertos_task_increment_tick_upstream_oracle_host.c"

enum {
    OPEN_CFW_ORACLE_RESUME_BLOCKED = 0x200U,
    OPEN_CFW_ORACLE_RESUME_PENDING = 0x300U
};

static List_t open_cfw_oracle_resume_blocked;

static List_t *open_cfw_oracle_resume_list(uint32_t kind)
{
    if (
        kind >= OPEN_CFW_ORACLE_TICK_READY_LIST_BASE &&
        kind <
            OPEN_CFW_ORACLE_TICK_READY_LIST_BASE + configMAX_PRIORITIES
    ) {
        return &pxReadyTasksLists[
            kind - OPEN_CFW_ORACLE_TICK_READY_LIST_BASE
        ];
    }
    if (kind == OPEN_CFW_ORACLE_RESUME_BLOCKED) {
        return &open_cfw_oracle_resume_blocked;
    }
    if (kind == OPEN_CFW_ORACLE_RESUME_PENDING) {
        return &xPendingReadyList;
    }
    return NULL;
}

void open_cfw_oracle_freertos_task_resume_all_reset(
    uint32_t suspended,
    uint32_t current_tasks,
    uint32_t pended_ticks,
    int32_t yield_pending,
    uint32_t top_ready_priority,
    uint32_t current_identifier
)
{
    open_cfw_oracle_freertos_task_increment_tick_reset(
        0U,
        suspended,
        pended_ticks,
        yield_pending,
        0,
        portMAX_DELAY,
        top_ready_priority,
        current_identifier,
        0U
    );
    vListInitialise(&xPendingReadyList);
    vListInitialise(&open_cfw_oracle_resume_blocked);
    uxCurrentNumberOfTasks = (UBaseType_t)current_tasks;
}

void open_cfw_oracle_freertos_task_resume_all_set_task(
    uint32_t identifier,
    uint32_t priority
)
{
    open_cfw_oracle_freertos_task_increment_tick_set_task(
        identifier,
        priority,
        0U
    );
}

void open_cfw_oracle_freertos_task_resume_all_insert_ready(
    uint32_t identifier
)
{
    TCB_t *task = open_cfw_oracle_tick_task(identifier);

    if (task != NULL && task->uxPriority < configMAX_PRIORITIES) {
        vListInsertEnd(
            &pxReadyTasksLists[task->uxPriority],
            &task->xStateListItem
        );
    }
}

void open_cfw_oracle_freertos_task_resume_all_insert_pending(
    uint32_t identifier
)
{
    TCB_t *task = open_cfw_oracle_tick_task(identifier);

    if (task != NULL) {
        vListInsertEnd(
            &open_cfw_oracle_resume_blocked,
            &task->xStateListItem
        );
        vListInsertEnd(&xPendingReadyList, &task->xEventListItem);
    }
}

void open_cfw_oracle_freertos_task_resume_all_set_list_index(
    uint32_t kind,
    uint32_t identifier
)
{
    List_t *list = open_cfw_oracle_resume_list(kind);
    TCB_t *task;
    ListItem_t *item;

    if (list == NULL) {
        return;
    }
    if (identifier == OPEN_CFW_ORACLE_TICK_SENTINEL) {
        list->pxIndex = (ListItem_t *)(void *)&list->xListEnd;
        return;
    }
    task = open_cfw_oracle_tick_task(identifier);
    if (task == NULL) {
        return;
    }
    item = (kind == OPEN_CFW_ORACLE_RESUME_PENDING) ?
        &task->xEventListItem : &task->xStateListItem;
    if (item->pxContainer == list) {
        list->pxIndex = item;
    }
}

int32_t open_cfw_oracle_freertos_task_resume_all_execute(void)
{
    return (int32_t)xTaskResumeAll();
}

uint32_t open_cfw_oracle_freertos_task_resume_all_get_suspended(void)
{
    return (uint32_t)uxSchedulerSuspended;
}

uint32_t open_cfw_oracle_freertos_task_resume_all_get_pended(void)
{
    return (uint32_t)xPendedTicks;
}

int32_t open_cfw_oracle_freertos_task_resume_all_get_yield_pending(void)
{
    return (int32_t)xYieldPending;
}

uint32_t open_cfw_oracle_freertos_task_resume_all_get_top(void)
{
    return (uint32_t)uxTopReadyPriority;
}

uint32_t open_cfw_oracle_freertos_task_resume_all_get_pending_count(void)
{
    return (uint32_t)xPendingReadyList.uxNumberOfItems;
}

uint32_t open_cfw_oracle_freertos_task_resume_all_get_blocked_count(void)
{
    return (uint32_t)open_cfw_oracle_resume_blocked.uxNumberOfItems;
}

uint32_t open_cfw_oracle_freertos_task_resume_all_get_ready_count(
    uint32_t priority
)
{
    if (priority >= configMAX_PRIORITIES) {
        return OPEN_CFW_ORACLE_TICK_NULL;
    }
    return (uint32_t)pxReadyTasksLists[priority].uxNumberOfItems;
}

uint32_t open_cfw_oracle_freertos_task_resume_all_get_state_container(
    uint32_t identifier
)
{
    TCB_t *task = open_cfw_oracle_tick_task(identifier);
    uint32_t priority;

    if (task == NULL) {
        return OPEN_CFW_ORACLE_TICK_NULL;
    }
    if (task->xStateListItem.pxContainer == &open_cfw_oracle_resume_blocked) {
        return OPEN_CFW_ORACLE_RESUME_BLOCKED;
    }
    for (priority = 0U; priority < configMAX_PRIORITIES; ++priority) {
        if (
            task->xStateListItem.pxContainer ==
            &pxReadyTasksLists[priority]
        ) {
            return OPEN_CFW_ORACLE_TICK_READY_LIST_BASE + priority;
        }
    }
    return OPEN_CFW_ORACLE_TICK_NULL;
}

uint32_t open_cfw_oracle_freertos_task_resume_all_get_event_container(
    uint32_t identifier
)
{
    TCB_t *task = open_cfw_oracle_tick_task(identifier);

    if (task != NULL &&
        task->xEventListItem.pxContainer == &xPendingReadyList) {
        return OPEN_CFW_ORACLE_RESUME_PENDING;
    }
    return OPEN_CFW_ORACLE_TICK_NULL;
}

uint32_t open_cfw_oracle_freertos_task_resume_all_get_list_index(
    uint32_t kind
)
{
    List_t *list = open_cfw_oracle_resume_list(kind);

    if (list == NULL) {
        return OPEN_CFW_ORACLE_TICK_NULL;
    }
    return open_cfw_oracle_tick_node_identifier(list, list->pxIndex);
}

uint32_t open_cfw_oracle_freertos_task_resume_all_get_list_owner(
    uint32_t kind,
    uint32_t position
)
{
    List_t *list = open_cfw_oracle_resume_list(kind);
    ListItem_t *sentinel;
    ListItem_t *item;
    uint32_t index;

    if (list == NULL) {
        return OPEN_CFW_ORACLE_TICK_NULL;
    }
    sentinel = (ListItem_t *)(void *)&list->xListEnd;
    item = sentinel->pxNext;
    for (index = 0U; index < position && item != sentinel; ++index) {
        item = item->pxNext;
    }
    if (item == sentinel) {
        return OPEN_CFW_ORACLE_TICK_NULL;
    }
    return open_cfw_oracle_tick_task_identifier(item->pvOwner);
}
