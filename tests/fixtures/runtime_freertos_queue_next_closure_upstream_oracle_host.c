/*
 * SPDX-License-Identifier: MIT
 *
 * Thin graph adapter over authenticated pristine FreeRTOS-Kernel V10.5.1
 * tasks.c, queue.c, and list.c.  The included scheduler oracle supplies the
 * recovered G2 configuration and host-only port seams; this file invokes the
 * upstream xQueueGiveFromISR() without copying its implementation.
 */

#include "runtime_freertos_task_increment_tick_upstream_oracle_host.c"
#include "../../third_party/freertos-kernel/queue.c"

enum {
    OPEN_CFW_ORACLE_QUEUE_NEXT_CONTAINER_NONE = 0U,
    OPEN_CFW_ORACLE_QUEUE_NEXT_CONTAINER_BLOCKED = 1U,
    OPEN_CFW_ORACLE_QUEUE_NEXT_CONTAINER_RECEIVE = 2U,
    OPEN_CFW_ORACLE_QUEUE_NEXT_CONTAINER_PENDING = 3U,
    OPEN_CFW_ORACLE_QUEUE_NEXT_CONTAINER_READY_BASE = 0x100U
};

static Queue_t open_cfw_oracle_queue_next_queue;
static BaseType_t open_cfw_oracle_queue_next_flag;

void open_cfw_oracle_queue_next_reset(
    uint32_t scheduler_suspended,
    uint32_t current_priority,
    uint32_t top_ready_priority,
    uint32_t task_count
)
{
    open_cfw_oracle_freertos_task_increment_tick_reset(
        0U,
        scheduler_suspended,
        0U,
        pdFALSE,
        0,
        portMAX_DELAY,
        top_ready_priority,
        0U,
        OPEN_CFW_ORACLE_TICK_DELAYED_LIST_1
    );
    open_cfw_oracle_freertos_task_increment_tick_set_task(
        0U,
        current_priority,
        0U
    );
    memset(
        &open_cfw_oracle_queue_next_queue,
        0,
        sizeof(open_cfw_oracle_queue_next_queue)
    );
    vListInitialise(&open_cfw_oracle_queue_next_queue.xTasksWaitingToSend);
    vListInitialise(
        &open_cfw_oracle_queue_next_queue.xTasksWaitingToReceive
    );
    vListInitialise(&xPendingReadyList);
    uxCurrentNumberOfTasks = (UBaseType_t)task_count;
    open_cfw_oracle_queue_next_flag = pdFALSE;
}

void open_cfw_oracle_queue_next_configure_queue(
    uint32_t length,
    uint32_t messages,
    uint32_t item_size,
    uint32_t mutex_held,
    int32_t transmit_lock
)
{
    open_cfw_oracle_queue_next_queue.pcHead =
        mutex_held != 0U ? NULL : (int8_t *)(uintptr_t)1U;
    open_cfw_oracle_queue_next_queue.u.xSemaphore.xMutexHolder =
        mutex_held != 0U ? open_cfw_oracle_tick_task(2U) : NULL;
    open_cfw_oracle_queue_next_queue.uxLength = (UBaseType_t)length;
    open_cfw_oracle_queue_next_queue.uxMessagesWaiting =
        (UBaseType_t)messages;
    open_cfw_oracle_queue_next_queue.uxItemSize = (UBaseType_t)item_size;
    open_cfw_oracle_queue_next_queue.cRxLock = queueUNLOCKED;
    open_cfw_oracle_queue_next_queue.cTxLock = (int8_t)transmit_lock;
}

void open_cfw_oracle_queue_next_configure_mutex_alias(
    uint32_t head_is_null,
    uint32_t holder_word_is_nonnull
)
{
    open_cfw_oracle_queue_next_queue.pcHead =
        head_is_null != 0U ? NULL : (int8_t *)(uintptr_t)1U;
    open_cfw_oracle_queue_next_queue.u.xSemaphore.xMutexHolder =
        holder_word_is_nonnull != 0U ?
            open_cfw_oracle_tick_task(2U) : NULL;
}

void open_cfw_oracle_queue_next_insert_waiter(uint32_t priority)
{
    TCB_t *task = open_cfw_oracle_tick_task(1U);

    if (task == NULL || priority >= configMAX_PRIORITIES) {
        return;
    }
    open_cfw_oracle_freertos_task_increment_tick_set_task(
        1U,
        priority,
        100U
    );
    listSET_LIST_ITEM_VALUE(
        &task->xEventListItem,
        (TickType_t)(configMAX_PRIORITIES - priority)
    );
    vListInsert(&xDelayedTaskList1, &task->xStateListItem);
    vListInsert(
        &open_cfw_oracle_queue_next_queue.xTasksWaitingToReceive,
        &task->xEventListItem
    );
}

void open_cfw_oracle_queue_next_seed_ready(uint32_t priority)
{
    TCB_t *task = open_cfw_oracle_tick_task(2U);

    if (task == NULL || priority >= configMAX_PRIORITIES) {
        return;
    }
    open_cfw_oracle_freertos_task_increment_tick_set_task(
        2U,
        priority,
        0U
    );
    vListInsertEnd(
        &pxReadyTasksLists[priority],
        &task->xStateListItem
    );
}

void open_cfw_oracle_queue_next_set_ready_index(
    uint32_t priority,
    uint32_t use_seed_task
)
{
    TCB_t *task = open_cfw_oracle_tick_task(2U);

    if (task == NULL || priority >= configMAX_PRIORITIES) {
        return;
    }
    pxReadyTasksLists[priority].pxIndex =
        use_seed_task != 0U ? &task->xStateListItem :
        (ListItem_t *)(void *)&pxReadyTasksLists[priority].xListEnd;
}

int32_t open_cfw_oracle_queue_next_execute(
    uint32_t use_flag,
    int32_t initial_flag
)
{
    open_cfw_oracle_queue_next_flag = (BaseType_t)initial_flag;
    return (int32_t)xQueueGiveFromISR(
        &open_cfw_oracle_queue_next_queue,
        use_flag != 0U ? &open_cfw_oracle_queue_next_flag : NULL
    );
}

uint32_t open_cfw_oracle_queue_next_get_messages(void)
{
    return (uint32_t)open_cfw_oracle_queue_next_queue.uxMessagesWaiting;
}

int32_t open_cfw_oracle_queue_next_get_transmit_lock(void)
{
    return (int32_t)open_cfw_oracle_queue_next_queue.cTxLock;
}

int32_t open_cfw_oracle_queue_next_get_flag(void)
{
    return (int32_t)open_cfw_oracle_queue_next_flag;
}

int32_t open_cfw_oracle_queue_next_get_yield_pending(void)
{
    return (int32_t)xYieldPending;
}

uint32_t open_cfw_oracle_queue_next_get_top_ready_priority(void)
{
    return (uint32_t)uxTopReadyPriority;
}

uint32_t open_cfw_oracle_queue_next_get_receive_count(void)
{
    return (uint32_t)
        open_cfw_oracle_queue_next_queue.xTasksWaitingToReceive
            .uxNumberOfItems;
}

uint32_t open_cfw_oracle_queue_next_get_blocked_count(void)
{
    return (uint32_t)xDelayedTaskList1.uxNumberOfItems;
}

uint32_t open_cfw_oracle_queue_next_get_pending_count(void)
{
    return (uint32_t)xPendingReadyList.uxNumberOfItems;
}

uint32_t open_cfw_oracle_queue_next_get_ready_count(uint32_t priority)
{
    if (priority >= configMAX_PRIORITIES) {
        return 0xFFFFFFFFU;
    }
    return (uint32_t)pxReadyTasksLists[priority].uxNumberOfItems;
}

uint32_t open_cfw_oracle_queue_next_get_ready_head_owner(uint32_t priority)
{
    if (priority >= configMAX_PRIORITIES) {
        return 0xFFFFFFFFU;
    }
    return open_cfw_oracle_tick_task_identifier(
        pxReadyTasksLists[priority].xListEnd.pxNext->pvOwner
    );
}

uint32_t open_cfw_oracle_queue_next_get_ready_tail_owner(uint32_t priority)
{
    if (priority >= configMAX_PRIORITIES) {
        return 0xFFFFFFFFU;
    }
    return open_cfw_oracle_tick_task_identifier(
        pxReadyTasksLists[priority].xListEnd.pxPrevious->pvOwner
    );
}

uint32_t open_cfw_oracle_queue_next_get_ready_index_owner(uint32_t priority)
{
    List_t *list;

    if (priority >= configMAX_PRIORITIES) {
        return 0xFFFFFFFFU;
    }
    list = &pxReadyTasksLists[priority];
    if (list->pxIndex == (ListItem_t *)(void *)&list->xListEnd) {
        return 0xFFFFFFFEU;
    }
    return open_cfw_oracle_tick_task_identifier(list->pxIndex->pvOwner);
}

static uint32_t open_cfw_oracle_queue_next_container(
    const List_t *container
)
{
    uint32_t priority;

    if (container == NULL) {
        return OPEN_CFW_ORACLE_QUEUE_NEXT_CONTAINER_NONE;
    }
    if (container == &xDelayedTaskList1) {
        return OPEN_CFW_ORACLE_QUEUE_NEXT_CONTAINER_BLOCKED;
    }
    if (
        container ==
        &open_cfw_oracle_queue_next_queue.xTasksWaitingToReceive
    ) {
        return OPEN_CFW_ORACLE_QUEUE_NEXT_CONTAINER_RECEIVE;
    }
    if (container == &xPendingReadyList) {
        return OPEN_CFW_ORACLE_QUEUE_NEXT_CONTAINER_PENDING;
    }
    for (priority = 0U; priority < configMAX_PRIORITIES; ++priority) {
        if (container == &pxReadyTasksLists[priority]) {
            return OPEN_CFW_ORACLE_QUEUE_NEXT_CONTAINER_READY_BASE + priority;
        }
    }
    return 0xFFFFFFFFU;
}

uint32_t open_cfw_oracle_queue_next_get_waiter_state_container(void)
{
    TCB_t *task = open_cfw_oracle_tick_task(1U);

    return open_cfw_oracle_queue_next_container(
        task != NULL ? task->xStateListItem.pxContainer : NULL
    );
}

uint32_t open_cfw_oracle_queue_next_get_waiter_event_container(void)
{
    TCB_t *task = open_cfw_oracle_tick_task(1U);

    return open_cfw_oracle_queue_next_container(
        task != NULL ? task->xEventListItem.pxContainer : NULL
    );
}

uint32_t open_cfw_oracle_queue_next_get_next_unblock_time(void)
{
    return (uint32_t)xNextTaskUnblockTime;
}
