/*
 * SPDX-License-Identifier: MIT
 *
 * Scriptable host adapter over the authenticated, pristine FreeRTOS-Kernel
 * V10.5.1 queue.c.  xQueueSemaphoreTake() and its private disinherit helper
 * are compiled directly from upstream; only documented task/port seams are
 * supplied here.
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

void *memset(void *destination, int value, size_t count);

#define portPOINTER_SIZE_TYPE uintptr_t

uint32_t SystemCoreClock = 96000000U;

static unsigned int open_cfw_take_assert_failures;

void open_cfw_cmsis_freertos_assert_fail(void)
{
    ++open_cfw_take_assert_failures;
    abort();
}

#include "../../third_party/freertos-kernel/queue.c"

enum {
    OPEN_CFW_TAKE_ENTER = 1,
    OPEN_CFW_TAKE_EXIT = 2,
    OPEN_CFW_TAKE_REMOVE = 3,
    OPEN_CFW_TAKE_YIELD_EVENT = 4,
    OPEN_CFW_TAKE_SET_TIME = 5,
    OPEN_CFW_TAKE_SUSPEND = 6,
    OPEN_CFW_TAKE_CHECK = 7,
    OPEN_CFW_TAKE_PLACE = 8,
    OPEN_CFW_TAKE_UNLOCK_EVENT = 9,
    OPEN_CFW_TAKE_RESUME = 10,
    OPEN_CFW_TAKE_INCREMENT = 11,
    OPEN_CFW_TAKE_INHERIT = 12,
    OPEN_CFW_TAKE_DISINHERIT = 13,
    OPEN_CFW_TAKE_EVENT_CAPACITY = 128
};

static Queue_t open_cfw_take_queue;
static ListItem_t open_cfw_take_receive_head;
static unsigned int open_cfw_take_events[OPEN_CFW_TAKE_EVENT_CAPACITY];
static unsigned int open_cfw_take_event_arguments[
    OPEN_CFW_TAKE_EVENT_CAPACITY
];
static unsigned int open_cfw_take_event_count;
static unsigned int open_cfw_take_scheduler_state_value;
static unsigned int open_cfw_take_remove_result;
static unsigned int open_cfw_take_resume_result;
static unsigned int open_cfw_take_check_first;
static unsigned int open_cfw_take_check_later;
static unsigned int open_cfw_take_mutation_first;
static unsigned int open_cfw_take_mutation_later;
static unsigned int open_cfw_take_check_calls;
static unsigned int open_cfw_take_inherit_result;
static uintptr_t open_cfw_take_increment_holder;
static uintptr_t open_cfw_take_disinherit_holder;
static unsigned int open_cfw_take_disinherit_priority;

static void open_cfw_take_log(unsigned int event, unsigned int argument)
{
    unsigned int index = open_cfw_take_event_count++;

    if (index < OPEN_CFW_TAKE_EVENT_CAPACITY) {
        open_cfw_take_events[index] = event;
        open_cfw_take_event_arguments[index] = argument;
    }
}

static void open_cfw_take_initialise_list(
    List_t *list,
    unsigned int count,
    ListItem_t *head
)
{
    list->uxNumberOfItems = (UBaseType_t)count;
    list->pxIndex = (ListItem_t *)(void *)&list->xListEnd;
    list->xListEnd.xItemValue = portMAX_DELAY;
    if (count == 0U || head == NULL) {
        list->xListEnd.pxNext =
            (ListItem_t *)(void *)&list->xListEnd;
        list->xListEnd.pxPrevious =
            (ListItem_t *)(void *)&list->xListEnd;
        return;
    }
    list->xListEnd.pxNext = head;
    list->xListEnd.pxPrevious = head;
    head->pxNext = (ListItem_t *)(void *)&list->xListEnd;
    head->pxPrevious = (ListItem_t *)(void *)&list->xListEnd;
    head->pxContainer = list;
}

void open_cfw_take_reset(
    unsigned int messages,
    unsigned int mutex,
    unsigned int send_waiters,
    unsigned int receive_waiters,
    unsigned int highest_waiting_priority
)
{
    memset(&open_cfw_take_queue, 0, sizeof(open_cfw_take_queue));
    memset(&open_cfw_take_receive_head, 0, sizeof(open_cfw_take_receive_head));
    memset(open_cfw_take_events, 0, sizeof(open_cfw_take_events));
    memset(
        open_cfw_take_event_arguments,
        0,
        sizeof(open_cfw_take_event_arguments)
    );
    open_cfw_take_queue.pcHead = mutex != 0U ? NULL : (int8_t *)(uintptr_t)1U;
    open_cfw_take_queue.u.xSemaphore.xMutexHolder =
        mutex != 0U ? (void *)(uintptr_t)0x22222222U : NULL;
    open_cfw_take_queue.uxMessagesWaiting = (UBaseType_t)messages;
    open_cfw_take_queue.uxLength = 1U;
    open_cfw_take_queue.uxItemSize = 0U;
    open_cfw_take_queue.cRxLock = queueUNLOCKED;
    open_cfw_take_queue.cTxLock = queueUNLOCKED;
    open_cfw_take_receive_head.xItemValue =
        (TickType_t)(configMAX_PRIORITIES - highest_waiting_priority);
    open_cfw_take_initialise_list(
        &open_cfw_take_queue.xTasksWaitingToSend,
        send_waiters,
        send_waiters != 0U ? &open_cfw_take_receive_head : NULL
    );
    open_cfw_take_initialise_list(
        &open_cfw_take_queue.xTasksWaitingToReceive,
        receive_waiters,
        receive_waiters != 0U ? &open_cfw_take_receive_head : NULL
    );
    open_cfw_take_event_count = 0U;
    open_cfw_take_scheduler_state_value = 1U;
    open_cfw_take_remove_result = 0U;
    open_cfw_take_resume_result = 1U;
    open_cfw_take_check_first = 1U;
    open_cfw_take_check_later = 1U;
    open_cfw_take_mutation_first = messages;
    open_cfw_take_mutation_later = messages;
    open_cfw_take_check_calls = 0U;
    open_cfw_take_inherit_result = 0U;
    open_cfw_take_increment_holder = (uintptr_t)0x33333333U;
    open_cfw_take_disinherit_holder = 0U;
    open_cfw_take_disinherit_priority = 0xFFFFFFFFU;
    open_cfw_take_assert_failures = 0U;
}

void open_cfw_take_configure(
    unsigned int check_first,
    unsigned int mutation_first,
    unsigned int check_later,
    unsigned int mutation_later,
    unsigned int resume_result,
    unsigned int remove_result,
    unsigned int inherit_result
)
{
    open_cfw_take_check_first = check_first;
    open_cfw_take_mutation_first = mutation_first;
    open_cfw_take_check_later = check_later;
    open_cfw_take_mutation_later = mutation_later;
    open_cfw_take_resume_result = resume_result;
    open_cfw_take_remove_result = remove_result;
    open_cfw_take_inherit_result = inherit_result;
}

int open_cfw_take_execute(unsigned int ticks)
{
    return (int)xQueueSemaphoreTake(&open_cfw_take_queue, (TickType_t)ticks);
}

unsigned int open_cfw_take_get_messages(void)
{
    return (unsigned int)open_cfw_take_queue.uxMessagesWaiting;
}

unsigned int open_cfw_take_get_send_waiters(void)
{
    return (unsigned int)
        open_cfw_take_queue.xTasksWaitingToSend.uxNumberOfItems;
}

unsigned int open_cfw_take_get_receive_waiters(void)
{
    return (unsigned int)
        open_cfw_take_queue.xTasksWaitingToReceive.uxNumberOfItems;
}

uintptr_t open_cfw_take_get_holder(void)
{
    return (uintptr_t)open_cfw_take_queue.u.xSemaphore.xMutexHolder;
}

int open_cfw_take_get_receive_lock(void)
{
    return (int)open_cfw_take_queue.cRxLock;
}

int open_cfw_take_get_transmit_lock(void)
{
    return (int)open_cfw_take_queue.cTxLock;
}

unsigned int open_cfw_take_get_check_calls(void)
{
    return open_cfw_take_check_calls;
}

uintptr_t open_cfw_take_get_disinherit_holder(void)
{
    return open_cfw_take_disinherit_holder;
}

unsigned int open_cfw_take_get_disinherit_priority(void)
{
    return open_cfw_take_disinherit_priority;
}

unsigned int open_cfw_take_get_event_count(void)
{
    return open_cfw_take_event_count;
}

unsigned int open_cfw_take_get_event(unsigned int index)
{
    return index < open_cfw_take_event_count ?
        open_cfw_take_events[index] : 0xFFFFFFFFU;
}

unsigned int open_cfw_take_get_event_argument(unsigned int index)
{
    return index < open_cfw_take_event_count ?
        open_cfw_take_event_arguments[index] : 0xFFFFFFFFU;
}

void *pvPortMalloc(size_t size)
{
    return malloc(size);
}

void vPortFree(void *pointer)
{
    free(pointer);
}

void vListInitialise(List_t * const list)
{
    open_cfw_take_initialise_list(list, 0U, NULL);
}

void vPortEnterCritical(void)
{
    open_cfw_take_log(OPEN_CFW_TAKE_ENTER, 0U);
}

void vPortExitCritical(void)
{
    open_cfw_take_log(OPEN_CFW_TAKE_EXIT, 0U);
}

uint32_t ulSetInterruptMask(void)
{
    return 0U;
}

void vClearInterruptMask(uint32_t mask)
{
    (void)mask;
}

void vPortYield(void)
{
    open_cfw_take_log(OPEN_CFW_TAKE_YIELD_EVENT, 0U);
}

void vTaskMissedYield(void)
{
    open_cfw_take_log(OPEN_CFW_TAKE_YIELD_EVENT, 0U);
}

BaseType_t xTaskGetSchedulerState(void)
{
    return (BaseType_t)open_cfw_take_scheduler_state_value;
}

TaskHandle_t xTaskGetCurrentTaskHandle(void)
{
    return (TaskHandle_t)(uintptr_t)0x11111111U;
}

UBaseType_t uxTaskGetNumberOfTasks(void)
{
    return 3U;
}

void vTaskInternalSetTimeOutState(TimeOut_t * const timeout)
{
    timeout->xOverflowCount = 7;
    timeout->xTimeOnEntering = 11U;
    open_cfw_take_log(OPEN_CFW_TAKE_SET_TIME, 0U);
}

void vTaskSuspendAll(void)
{
    open_cfw_take_log(OPEN_CFW_TAKE_SUSPEND, 0U);
}

BaseType_t xTaskCheckForTimeOut(
    TimeOut_t * const timeout,
    TickType_t * const ticks
)
{
    unsigned int result;
    unsigned int mutation;

    (void)timeout;
    open_cfw_take_log(OPEN_CFW_TAKE_CHECK, (unsigned int)*ticks);
    if (open_cfw_take_check_calls++ == 0U) {
        result = open_cfw_take_check_first;
        mutation = open_cfw_take_mutation_first;
    } else {
        result = open_cfw_take_check_later;
        mutation = open_cfw_take_mutation_later;
    }
    open_cfw_take_queue.uxMessagesWaiting = (UBaseType_t)mutation;
    return (BaseType_t)result;
}

void vTaskPlaceOnEventList(
    List_t * const list,
    const TickType_t ticks
)
{
    ++list->uxNumberOfItems;
    open_cfw_take_log(OPEN_CFW_TAKE_PLACE, (unsigned int)ticks);
}

void vTaskPlaceOnEventListRestricted(
    List_t * const list,
    TickType_t ticks,
    const BaseType_t wait_indefinitely
)
{
    (void)wait_indefinitely;
    vTaskPlaceOnEventList(list, ticks);
}

BaseType_t xTaskRemoveFromEventList(const List_t * const list)
{
    List_t *mutable_list = (List_t *)(uintptr_t)list;

    open_cfw_take_log(
        OPEN_CFW_TAKE_REMOVE,
        (unsigned int)mutable_list->uxNumberOfItems
    );
    if (mutable_list->uxNumberOfItems != 0U) {
        --mutable_list->uxNumberOfItems;
    }
    return (BaseType_t)open_cfw_take_remove_result;
}

BaseType_t xTaskResumeAll(void)
{
    open_cfw_take_log(OPEN_CFW_TAKE_RESUME, 0U);
    return (BaseType_t)open_cfw_take_resume_result;
}

TaskHandle_t pvTaskIncrementMutexHeldCount(void)
{
    open_cfw_take_log(OPEN_CFW_TAKE_INCREMENT, 0U);
    return (TaskHandle_t)open_cfw_take_increment_holder;
}

BaseType_t xTaskPriorityInherit(TaskHandle_t const holder)
{
    open_cfw_take_log(
        OPEN_CFW_TAKE_INHERIT,
        holder != NULL ? 1U : 0U
    );
    return (BaseType_t)open_cfw_take_inherit_result;
}

BaseType_t xTaskPriorityDisinherit(TaskHandle_t const holder)
{
    (void)holder;
    return pdFALSE;
}

void vTaskPriorityDisinheritAfterTimeout(
    TaskHandle_t const holder,
    UBaseType_t priority
)
{
    open_cfw_take_disinherit_holder = (uintptr_t)holder;
    open_cfw_take_disinherit_priority = (unsigned int)priority;
    open_cfw_take_log(
        OPEN_CFW_TAKE_DISINHERIT,
        (unsigned int)priority
    );
}
