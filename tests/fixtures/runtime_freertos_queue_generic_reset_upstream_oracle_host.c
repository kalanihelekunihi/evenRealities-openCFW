/*
 * SPDX-License-Identifier: MIT
 *
 * Thin host adapter that invokes pristine authenticated FreeRTOS-Kernel
 * V10.5.1 xQueueGenericReset(); the implementation is not copied here.
 */

#include "runtime_freertos_task_increment_tick_upstream_oracle_host.c"
#include "../../third_party/freertos-kernel/queue.c"

enum {
    OPEN_CFW_ORACLE_QUEUE_RESET_NO_WAITER = 0xFFFFFFFFU
};

static Queue_t open_cfw_oracle_queue_reset_queue;
static int8_t open_cfw_oracle_queue_reset_storage[256];

void open_cfw_oracle_queue_reset_reset(
    uint32_t current_priority,
    uint32_t waiter_priority,
    uint32_t length,
    uint32_t item_size,
    uint32_t messages_waiting,
    uint32_t seed_receive
)
{
    TCB_t *waiter;
    TCB_t *receiver;

    open_cfw_oracle_freertos_task_increment_tick_reset(
        0U, 0U, 0U, pdFALSE, 0, portMAX_DELAY,
        current_priority, 0U, OPEN_CFW_ORACLE_TICK_DELAYED_LIST_1
    );
    open_cfw_oracle_freertos_task_increment_tick_set_task(
        0U, current_priority, 0U
    );
    memset(&open_cfw_oracle_queue_reset_queue, 0xA7,
           sizeof(open_cfw_oracle_queue_reset_queue));
    memset(open_cfw_oracle_queue_reset_storage, 0x5A,
           sizeof(open_cfw_oracle_queue_reset_storage));
    vListInitialise(&open_cfw_oracle_queue_reset_queue.xTasksWaitingToSend);
    vListInitialise(
        &open_cfw_oracle_queue_reset_queue.xTasksWaitingToReceive
    );
    if (waiter_priority != OPEN_CFW_ORACLE_QUEUE_RESET_NO_WAITER) {
        open_cfw_oracle_freertos_task_increment_tick_set_task(
            1U, waiter_priority, 100U
        );
        waiter = open_cfw_oracle_tick_task(1U);
        vListInsert(&xDelayedTaskList1, &waiter->xStateListItem);
        listSET_LIST_ITEM_VALUE(
            &waiter->xEventListItem,
            (TickType_t)(configMAX_PRIORITIES - waiter_priority)
        );
        vListInsert(
            &open_cfw_oracle_queue_reset_queue.xTasksWaitingToSend,
            &waiter->xEventListItem
        );
    }
    if (seed_receive != 0U) {
        open_cfw_oracle_freertos_task_increment_tick_set_task(2U, 1U, 0U);
        receiver = open_cfw_oracle_tick_task(2U);
        vListInsertEnd(
            &open_cfw_oracle_queue_reset_queue.xTasksWaitingToReceive,
            &receiver->xEventListItem
        );
    }
    open_cfw_oracle_queue_reset_queue.pcHead =
        open_cfw_oracle_queue_reset_storage;
    open_cfw_oracle_queue_reset_queue.pcWriteTo =
        open_cfw_oracle_queue_reset_storage + 7;
    open_cfw_oracle_queue_reset_queue.u.xQueue.pcTail =
        open_cfw_oracle_queue_reset_storage + 11;
    open_cfw_oracle_queue_reset_queue.u.xQueue.pcReadFrom =
        open_cfw_oracle_queue_reset_storage + 13;
    open_cfw_oracle_queue_reset_queue.uxLength = (UBaseType_t)length;
    open_cfw_oracle_queue_reset_queue.uxItemSize = (UBaseType_t)item_size;
    open_cfw_oracle_queue_reset_queue.uxMessagesWaiting =
        (UBaseType_t)messages_waiting;
    open_cfw_oracle_queue_reset_queue.cRxLock = 19;
    open_cfw_oracle_queue_reset_queue.cTxLock = 23;
}

int32_t open_cfw_oracle_queue_reset_execute(int32_t new_queue)
{
    return (int32_t)xQueueGenericReset(
        &open_cfw_oracle_queue_reset_queue,
        (BaseType_t)new_queue
    );
}

static uint32_t open_cfw_oracle_queue_reset_offset(const int8_t *pointer)
{
    return (uint32_t)(pointer - open_cfw_oracle_queue_reset_storage);
}

uint32_t open_cfw_oracle_queue_reset_get_tail(void)
{
    return open_cfw_oracle_queue_reset_offset(
        open_cfw_oracle_queue_reset_queue.u.xQueue.pcTail
    );
}

uint32_t open_cfw_oracle_queue_reset_get_write(void)
{
    return open_cfw_oracle_queue_reset_offset(
        open_cfw_oracle_queue_reset_queue.pcWriteTo
    );
}

uint32_t open_cfw_oracle_queue_reset_get_read(void)
{
    return open_cfw_oracle_queue_reset_offset(
        open_cfw_oracle_queue_reset_queue.u.xQueue.pcReadFrom
    );
}

uint32_t open_cfw_oracle_queue_reset_get_messages(void)
{
    return (uint32_t)open_cfw_oracle_queue_reset_queue.uxMessagesWaiting;
}

int32_t open_cfw_oracle_queue_reset_get_receive_lock(void)
{
    return (int32_t)open_cfw_oracle_queue_reset_queue.cRxLock;
}

int32_t open_cfw_oracle_queue_reset_get_transmit_lock(void)
{
    return (int32_t)open_cfw_oracle_queue_reset_queue.cTxLock;
}

uint32_t open_cfw_oracle_queue_reset_get_send_count(void)
{
    return (uint32_t)
        open_cfw_oracle_queue_reset_queue.xTasksWaitingToSend.uxNumberOfItems;
}

uint32_t open_cfw_oracle_queue_reset_get_receive_count(void)
{
    return (uint32_t)
        open_cfw_oracle_queue_reset_queue.xTasksWaitingToReceive.uxNumberOfItems;
}
