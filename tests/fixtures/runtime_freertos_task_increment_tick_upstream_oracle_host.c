/*
 * SPDX-License-Identifier: MIT
 *
 * Differential host oracle for FreeRTOS-Kernel V10.5.1
 * xTaskIncrementTick().  The implementation under test is not copied here:
 * this translation unit includes the authenticated pristine tasks.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c and invokes its public function.
 * list.c is included only to construct and inspect genuine upstream lists.
 *
 * API contract shared with the candidate-host differential test:
 *
 * - task identifiers are in [0, 15]; event-list identifiers are in [0, 3];
 * - delayed selectors 0 and 1 name xDelayedTaskList1 and
 *   xDelayedTaskList2, respectively;
 * - canonical list kinds use 0/1 for those delayed lists,
 *   0x100 + priority for a ready list, and 0x200 + event identifier for an
 *   event list;
 * - canonical node identifier 0xFFFFFFFE denotes a list sentinel and
 *   0xFFFFFFFF denotes NULL, an invalid identifier, or the end of iteration;
 * - reset() initializes globals and empty lists but deliberately does not
 *   insert any task.  Tests call set_task() followed by the desired insert
 *   primitives, including inserting the current task into its ready list;
 * - set_index() accepts the canonical list kind and either a task identifier,
 *   0xFFFFFFFE for that list's sentinel, or 0xFFFFFFFF for NULL;
 * - graph getters return task identifiers rather than host pointers, making
 *   snapshots deterministic across ASLR, architectures, and test processes.
 *
 * Host compilation requires the authenticated kernel include directory, the
 * recovered constructor FreeRTOSConfig/port adapter directory, and the
 * authenticated IAR ARM_CM55_NTZ common-port directory on the include path.
 */

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/*
 * The recovered ARM port uses uint32_t for pointer arithmetic.  The oracle
 * runs in a 64-bit host process, so widen only this compile-time portability
 * seam; it is not consulted by xTaskIncrementTick().  The constructor include
 * adapter intentionally declares only memcpy(), hence the explicit pristine
 * tasks.c dependency below.
 */
#define portPOINTER_SIZE_TYPE uintptr_t
void *memset(void *destination, int value, size_t count);

enum {
    OPEN_CFW_ORACLE_TICK_TASK_COUNT = 16U,
    OPEN_CFW_ORACLE_TICK_EVENT_LIST_COUNT = 4U,
    OPEN_CFW_ORACLE_TICK_DELAYED_LIST_1 = 0U,
    OPEN_CFW_ORACLE_TICK_DELAYED_LIST_2 = 1U,
    OPEN_CFW_ORACLE_TICK_READY_LIST_BASE = 0x100U,
    OPEN_CFW_ORACLE_TICK_EVENT_LIST_BASE = 0x200U,
    OPEN_CFW_ORACLE_TICK_SENTINEL = 0xFFFFFFFEU,
    OPEN_CFW_ORACLE_TICK_NULL = 0xFFFFFFFFU
};

/* Required by the recovered compile-closure FreeRTOSConfig.h. */
uint32_t SystemCoreClock = 96000000U;

static uint32_t open_cfw_oracle_tick_assert_failures;

void open_cfw_cmsis_freertos_assert_fail(void)
{
    ++open_cfw_oracle_tick_assert_failures;
    abort();
}

/* Compile the exact authenticated scheduler source, not an adaptation. */
#include "../../third_party/freertos-kernel/tasks.c"
#include "../../third_party/freertos-kernel/list.c"

static TCB_t open_cfw_oracle_tick_tasks[
    OPEN_CFW_ORACLE_TICK_TASK_COUNT
];
static List_t open_cfw_oracle_tick_event_lists[
    OPEN_CFW_ORACLE_TICK_EVENT_LIST_COUNT
];

static TCB_t *open_cfw_oracle_tick_task(uint32_t identifier)
{
    if (identifier >= OPEN_CFW_ORACLE_TICK_TASK_COUNT) {
        return NULL;
    }
    return &open_cfw_oracle_tick_tasks[identifier];
}

static uint32_t open_cfw_oracle_tick_task_identifier(const void *owner)
{
    uint32_t index;

    if (owner == NULL) {
        return OPEN_CFW_ORACLE_TICK_NULL;
    }
    for (index = 0U; index < OPEN_CFW_ORACLE_TICK_TASK_COUNT; ++index) {
        if (owner == &open_cfw_oracle_tick_tasks[index]) {
            return index;
        }
    }
    return OPEN_CFW_ORACLE_TICK_NULL;
}

static List_t *open_cfw_oracle_tick_list(uint32_t kind)
{
    if (kind == OPEN_CFW_ORACLE_TICK_DELAYED_LIST_1) {
        return &xDelayedTaskList1;
    }
    if (kind == OPEN_CFW_ORACLE_TICK_DELAYED_LIST_2) {
        return &xDelayedTaskList2;
    }
    if (
        kind >= OPEN_CFW_ORACLE_TICK_READY_LIST_BASE &&
        kind < OPEN_CFW_ORACLE_TICK_READY_LIST_BASE + configMAX_PRIORITIES
    ) {
        return &pxReadyTasksLists[
            kind - OPEN_CFW_ORACLE_TICK_READY_LIST_BASE
        ];
    }
    if (
        kind >= OPEN_CFW_ORACLE_TICK_EVENT_LIST_BASE &&
        kind <
            OPEN_CFW_ORACLE_TICK_EVENT_LIST_BASE +
            OPEN_CFW_ORACLE_TICK_EVENT_LIST_COUNT
    ) {
        return &open_cfw_oracle_tick_event_lists[
            kind - OPEN_CFW_ORACLE_TICK_EVENT_LIST_BASE
        ];
    }
    return NULL;
}

static ListItem_t *open_cfw_oracle_tick_list_sentinel(List_t *list)
{
    if (list == NULL) {
        return NULL;
    }
    return (ListItem_t *)(void *)&list->xListEnd;
}

static uint32_t open_cfw_oracle_tick_node_identifier(
    const List_t *list,
    const ListItem_t *item
)
{
    if (item == NULL) {
        return OPEN_CFW_ORACLE_TICK_NULL;
    }
    if (
        list != NULL &&
        item == (const ListItem_t *)(const void *)&list->xListEnd
    ) {
        return OPEN_CFW_ORACLE_TICK_SENTINEL;
    }
    return open_cfw_oracle_tick_task_identifier(item->pvOwner);
}

void open_cfw_oracle_freertos_task_increment_tick_reset(
    uint32_t tick_count,
    uint32_t scheduler_suspended,
    uint32_t pended_ticks,
    int32_t yield_pending,
    int32_t overflow_count,
    uint32_t next_unblock_time,
    uint32_t top_ready_priority,
    uint32_t current_identifier,
    uint32_t delayed_selector
)
{
    uint32_t index;

    memset(
        open_cfw_oracle_tick_tasks,
        0,
        sizeof(open_cfw_oracle_tick_tasks)
    );
    for (index = 0U; index < configMAX_PRIORITIES; ++index) {
        vListInitialise(&pxReadyTasksLists[index]);
    }
    vListInitialise(&xDelayedTaskList1);
    vListInitialise(&xDelayedTaskList2);
    for (
        index = 0U;
        index < OPEN_CFW_ORACLE_TICK_EVENT_LIST_COUNT;
        ++index
    ) {
        vListInitialise(&open_cfw_oracle_tick_event_lists[index]);
    }
    for (index = 0U; index < OPEN_CFW_ORACLE_TICK_TASK_COUNT; ++index) {
        vListInitialiseItem(
            &open_cfw_oracle_tick_tasks[index].xStateListItem
        );
        vListInitialiseItem(
            &open_cfw_oracle_tick_tasks[index].xEventListItem
        );
        listSET_LIST_ITEM_OWNER(
            &open_cfw_oracle_tick_tasks[index].xStateListItem,
            &open_cfw_oracle_tick_tasks[index]
        );
        listSET_LIST_ITEM_OWNER(
            &open_cfw_oracle_tick_tasks[index].xEventListItem,
            &open_cfw_oracle_tick_tasks[index]
        );
    }

    if (delayed_selector == OPEN_CFW_ORACLE_TICK_DELAYED_LIST_2) {
        pxDelayedTaskList = &xDelayedTaskList2;
        pxOverflowDelayedTaskList = &xDelayedTaskList1;
    } else {
        pxDelayedTaskList = &xDelayedTaskList1;
        pxOverflowDelayedTaskList = &xDelayedTaskList2;
    }
    pxCurrentTCB = open_cfw_oracle_tick_task(current_identifier);
    xTickCount = (TickType_t)tick_count;
    uxSchedulerSuspended = (UBaseType_t)scheduler_suspended;
    xPendedTicks = (TickType_t)pended_ticks;
    xYieldPending = (BaseType_t)yield_pending;
    xNumOfOverflows = (BaseType_t)overflow_count;
    xNextTaskUnblockTime = (TickType_t)next_unblock_time;
    uxTopReadyPriority = (UBaseType_t)top_ready_priority;
    open_cfw_oracle_tick_assert_failures = 0U;
}

void open_cfw_oracle_freertos_task_increment_tick_set_task(
    uint32_t identifier,
    uint32_t priority,
    uint32_t wake_tick
)
{
    TCB_t *task = open_cfw_oracle_tick_task(identifier);

    if (task == NULL || priority >= configMAX_PRIORITIES) {
        return;
    }
    task->uxPriority = (UBaseType_t)priority;
    listSET_LIST_ITEM_VALUE(
        &task->xStateListItem,
        (TickType_t)wake_tick
    );
    listSET_LIST_ITEM_VALUE(
        &task->xEventListItem,
        (TickType_t)wake_tick
    );
}

void open_cfw_oracle_freertos_task_increment_tick_insert_delayed(
    uint32_t selector,
    uint32_t identifier
)
{
    TCB_t *task = open_cfw_oracle_tick_task(identifier);
    List_t *list = open_cfw_oracle_tick_list(selector);

    if (task != NULL && list != NULL) {
        vListInsert(list, &task->xStateListItem);
    }
}

void open_cfw_oracle_freertos_task_increment_tick_insert_event(
    uint32_t event_list,
    uint32_t identifier
)
{
    TCB_t *task = open_cfw_oracle_tick_task(identifier);
    List_t *list = open_cfw_oracle_tick_list(
        OPEN_CFW_ORACLE_TICK_EVENT_LIST_BASE + event_list
    );

    if (task != NULL && list != NULL) {
        vListInsertEnd(list, &task->xEventListItem);
    }
}

void open_cfw_oracle_freertos_task_increment_tick_insert_ready(
    uint32_t priority,
    uint32_t identifier
)
{
    TCB_t *task = open_cfw_oracle_tick_task(identifier);

    if (
        task != NULL &&
        priority < configMAX_PRIORITIES &&
        task->uxPriority == (UBaseType_t)priority
    ) {
        vListInsertEnd(
            &pxReadyTasksLists[priority],
            &task->xStateListItem
        );
    }
}

void open_cfw_oracle_freertos_task_increment_tick_set_index(
    uint32_t kind,
    uint32_t identifier
)
{
    List_t *list = open_cfw_oracle_tick_list(kind);
    TCB_t *task;

    if (list == NULL) {
        return;
    }
    if (identifier == OPEN_CFW_ORACLE_TICK_SENTINEL) {
        list->pxIndex = open_cfw_oracle_tick_list_sentinel(list);
        return;
    }
    if (identifier == OPEN_CFW_ORACLE_TICK_NULL) {
        list->pxIndex = NULL;
        return;
    }
    task = open_cfw_oracle_tick_task(identifier);
    if (task == NULL) {
        return;
    }
    if (
        kind >= OPEN_CFW_ORACLE_TICK_EVENT_LIST_BASE &&
        kind <
            OPEN_CFW_ORACLE_TICK_EVENT_LIST_BASE +
            OPEN_CFW_ORACLE_TICK_EVENT_LIST_COUNT
    ) {
        list->pxIndex = &task->xEventListItem;
    } else {
        list->pxIndex = &task->xStateListItem;
    }
}

int32_t open_cfw_oracle_freertos_task_increment_tick_execute(void)
{
    return (int32_t)xTaskIncrementTick();
}

uint32_t open_cfw_oracle_freertos_task_increment_tick_get_tick(void)
{
    return (uint32_t)xTickCount;
}

uint32_t open_cfw_oracle_freertos_task_increment_tick_get_suspended(void)
{
    return (uint32_t)uxSchedulerSuspended;
}

uint32_t open_cfw_oracle_freertos_task_increment_tick_get_pended(void)
{
    return (uint32_t)xPendedTicks;
}

int32_t open_cfw_oracle_freertos_task_increment_tick_get_yield(void)
{
    return (int32_t)xYieldPending;
}

int32_t open_cfw_oracle_freertos_task_increment_tick_get_overflow(void)
{
    return (int32_t)xNumOfOverflows;
}

uint32_t open_cfw_oracle_freertos_task_increment_tick_get_next(void)
{
    return (uint32_t)xNextTaskUnblockTime;
}

uint32_t open_cfw_oracle_freertos_task_increment_tick_get_top(void)
{
    return (uint32_t)uxTopReadyPriority;
}

uint32_t
open_cfw_oracle_freertos_task_increment_tick_get_delayed_selector(void)
{
    return (pxDelayedTaskList == &xDelayedTaskList2) ? 1U : 0U;
}

uint32_t open_cfw_oracle_freertos_task_increment_tick_get_assert_failures(
    void
)
{
    return open_cfw_oracle_tick_assert_failures;
}

uint32_t open_cfw_oracle_freertos_task_increment_tick_get_list_count(
    uint32_t kind
)
{
    List_t *list = open_cfw_oracle_tick_list(kind);

    return (list == NULL) ? OPEN_CFW_ORACLE_TICK_NULL :
        (uint32_t)list->uxNumberOfItems;
}

uint32_t open_cfw_oracle_freertos_task_increment_tick_get_list_index(
    uint32_t kind
)
{
    List_t *list = open_cfw_oracle_tick_list(kind);

    if (list == NULL) {
        return OPEN_CFW_ORACLE_TICK_NULL;
    }
    return open_cfw_oracle_tick_node_identifier(list, list->pxIndex);
}

uint32_t open_cfw_oracle_freertos_task_increment_tick_get_list_owner(
    uint32_t kind,
    uint32_t position
)
{
    List_t *list = open_cfw_oracle_tick_list(kind);
    ListItem_t *sentinel;
    ListItem_t *item;
    uint32_t index;

    if (list == NULL) {
        return OPEN_CFW_ORACLE_TICK_NULL;
    }
    sentinel = open_cfw_oracle_tick_list_sentinel(list);
    item = sentinel->pxNext;
    for (index = 0U; index < position && item != sentinel; ++index) {
        item = item->pxNext;
    }
    if (item == sentinel) {
        return OPEN_CFW_ORACLE_TICK_NULL;
    }
    return open_cfw_oracle_tick_task_identifier(item->pvOwner);
}

uint32_t open_cfw_oracle_freertos_task_increment_tick_get_task_priority(
    uint32_t identifier
)
{
    TCB_t *task = open_cfw_oracle_tick_task(identifier);

    return (task == NULL) ? OPEN_CFW_ORACLE_TICK_NULL :
        (uint32_t)task->uxPriority;
}

uint32_t open_cfw_oracle_freertos_task_increment_tick_get_task_wake(
    uint32_t identifier
)
{
    TCB_t *task = open_cfw_oracle_tick_task(identifier);

    return (task == NULL) ? OPEN_CFW_ORACLE_TICK_NULL :
        (uint32_t)listGET_LIST_ITEM_VALUE(&task->xStateListItem);
}

uint32_t open_cfw_oracle_freertos_task_increment_tick_get_task_container(
    uint32_t identifier
)
{
    TCB_t *task = open_cfw_oracle_tick_task(identifier);
    uint32_t priority;

    if (task == NULL || task->xStateListItem.pxContainer == NULL) {
        return OPEN_CFW_ORACLE_TICK_NULL;
    }
    if (task->xStateListItem.pxContainer == &xDelayedTaskList1) {
        return OPEN_CFW_ORACLE_TICK_DELAYED_LIST_1;
    }
    if (task->xStateListItem.pxContainer == &xDelayedTaskList2) {
        return OPEN_CFW_ORACLE_TICK_DELAYED_LIST_2;
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

uint32_t
open_cfw_oracle_freertos_task_increment_tick_get_event_container(
    uint32_t identifier
)
{
    TCB_t *task = open_cfw_oracle_tick_task(identifier);
    uint32_t event_list;

    if (task == NULL || task->xEventListItem.pxContainer == NULL) {
        return OPEN_CFW_ORACLE_TICK_NULL;
    }
    for (
        event_list = 0U;
        event_list < OPEN_CFW_ORACLE_TICK_EVENT_LIST_COUNT;
        ++event_list
    ) {
        if (
            task->xEventListItem.pxContainer ==
            &open_cfw_oracle_tick_event_lists[event_list]
        ) {
            return OPEN_CFW_ORACLE_TICK_EVENT_LIST_BASE + event_list;
        }
    }
    return OPEN_CFW_ORACLE_TICK_NULL;
}

/*
 * Host-only definitions for port/application seams referenced elsewhere in
 * pristine tasks.c.  xTaskIncrementTick itself reaches none of these except
 * the assertion path's ulSetInterruptMask(), which valid oracle graphs avoid.
 */
BaseType_t xPortIsInsideInterrupt(void)
{
    return pdFALSE;
}

void vPortYield(void)
{
}

void vPortEnterCritical(void)
{
}

void vPortExitCritical(void)
{
}

uint32_t ulSetInterruptMask(void)
{
    return 0U;
}

void vClearInterruptMask(uint32_t mask)
{
    (void)mask;
}

void vPortSuppressTicksAndSleep(TickType_t expected_idle_time)
{
    (void)expected_idle_time;
}

void vApplicationIdleHook(void)
{
}

void vApplicationStackOverflowHook(
    TaskHandle_t task,
    char *task_name
)
{
    (void)task;
    (void)task_name;
}

void *pvPortMalloc(size_t size)
{
    return malloc(size);
}

void vPortFree(void *allocation)
{
    free(allocation);
}

StackType_t *pxPortInitialiseStack(
    StackType_t *top_of_stack,
    StackType_t *end_of_stack,
    TaskFunction_t function,
    void *parameter
)
{
    (void)end_of_stack;
    (void)function;
    (void)parameter;
    return top_of_stack;
}

BaseType_t xPortStartScheduler(void)
{
    return pdFALSE;
}

void vPortEndScheduler(void)
{
}

BaseType_t xTimerCreateTimerTask(void)
{
    return pdPASS;
}

void vApplicationGetIdleTaskMemory(
    StaticTask_t **task_buffer,
    StackType_t **stack_buffer,
    uint32_t *stack_size
)
{
    static StaticTask_t idle_task;
    static StackType_t idle_stack[configMINIMAL_STACK_SIZE];

    *task_buffer = &idle_task;
    *stack_buffer = idle_stack;
    *stack_size = configMINIMAL_STACK_SIZE;
}
