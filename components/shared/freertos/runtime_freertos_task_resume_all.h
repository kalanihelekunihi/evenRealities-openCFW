/*
 * SPDX-License-Identifier: MIT
 *
 * FreeRTOS xTaskResumeAll ABI for the Even Realities G2 Apollo-main image.
 * This header exposes every recovered RAM and call seam used by the
 * production-integrated source replacement and its host validation fixtures.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_TASK_RESUME_ALL_H
#define OPEN_CFW_RUNTIME_FREERTOS_TASK_RESUME_ALL_H

typedef __INT32_TYPE__ open_cfw_freertos_resume_base_type;
typedef __UINT32_TYPE__ open_cfw_freertos_resume_ubase_type;
typedef __UINT32_TYPE__ open_cfw_freertos_resume_tick_type;
typedef __UINTPTR_TYPE__ open_cfw_freertos_resume_uintptr;

enum {
    OPEN_CFW_FREERTOS_RESUME_FALSE = 0,
    OPEN_CFW_FREERTOS_RESUME_TRUE = 1,
    OPEN_CFW_FREERTOS_RESUME_MAX_PRIORITIES = 56U,
    OPEN_CFW_FREERTOS_RESUME_CURRENT_TCB_ADDRESS = 0x20074A20U,
    OPEN_CFW_FREERTOS_RESUME_CURRENT_TASK_COUNT_ADDRESS = 0x20074A30U,
    OPEN_CFW_FREERTOS_RESUME_TOP_READY_PRIORITY_ADDRESS = 0x20074A38U,
    OPEN_CFW_FREERTOS_RESUME_PENDED_TICKS_ADDRESS = 0x20074A40U,
    OPEN_CFW_FREERTOS_RESUME_YIELD_PENDING_ADDRESS = 0x20074A44U,
    OPEN_CFW_FREERTOS_RESUME_SCHEDULER_SUSPENDED_ADDRESS = 0x20074A58U,
    OPEN_CFW_FREERTOS_RESUME_READY_LISTS_ADDRESS = 0x2006A49CU,
    OPEN_CFW_FREERTOS_RESUME_PENDING_READY_LIST_ADDRESS = 0x20073D24U,
    OPEN_CFW_FREERTOS_RESUME_LIST_ITEM_SIZE = 0x14U,
    OPEN_CFW_FREERTOS_RESUME_MINI_LIST_ITEM_SIZE = 0x0CU,
    OPEN_CFW_FREERTOS_RESUME_LIST_SIZE = 0x14U,
    OPEN_CFW_FREERTOS_RESUME_TCB_STATE_ITEM_OFFSET = 0x04U,
    OPEN_CFW_FREERTOS_RESUME_TCB_EVENT_ITEM_OFFSET = 0x18U,
    OPEN_CFW_FREERTOS_RESUME_TCB_PRIORITY_OFFSET = 0x2CU
};

struct open_cfw_freertos_resume_list;

struct open_cfw_freertos_resume_list_item {
    open_cfw_freertos_resume_tick_type item_value;
    struct open_cfw_freertos_resume_list_item *next;
    struct open_cfw_freertos_resume_list_item *previous;
    void *owner;
    struct open_cfw_freertos_resume_list *container;
};

struct open_cfw_freertos_resume_mini_list_item {
    open_cfw_freertos_resume_tick_type item_value;
    struct open_cfw_freertos_resume_list_item *next;
    struct open_cfw_freertos_resume_list_item *previous;
};

struct open_cfw_freertos_resume_list {
    volatile open_cfw_freertos_resume_ubase_type item_count;
    struct open_cfw_freertos_resume_list_item *index;
    struct open_cfw_freertos_resume_mini_list_item end;
};

struct open_cfw_freertos_resume_tcb {
    void *top_of_stack;
    struct open_cfw_freertos_resume_list_item state_list_item;
    struct open_cfw_freertos_resume_list_item event_list_item;
    open_cfw_freertos_resume_ubase_type priority;
};

_Static_assert(
    sizeof(open_cfw_freertos_resume_base_type) == 4U,
    "G2 FreeRTOS BaseType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_resume_ubase_type) == 4U,
    "G2 FreeRTOS UBaseType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_resume_tick_type) == 4U,
    "G2 FreeRTOS TickType_t width changed"
);

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(struct open_cfw_freertos_resume_list_item) ==
        OPEN_CFW_FREERTOS_RESUME_LIST_ITEM_SIZE,
    "G2 FreeRTOS ListItem_t size changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_resume_mini_list_item) ==
        OPEN_CFW_FREERTOS_RESUME_MINI_LIST_ITEM_SIZE,
    "G2 FreeRTOS MiniListItem_t size changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_resume_list) ==
        OPEN_CFW_FREERTOS_RESUME_LIST_SIZE,
    "G2 FreeRTOS List_t size changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_resume_list, item_count) ==
        0x00U,
    "G2 FreeRTOS List_t item-count offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_resume_list, index) ==
        0x04U,
    "G2 FreeRTOS List_t index offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_resume_list, end) == 0x08U,
    "G2 FreeRTOS List_t end offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_resume_list, end.next) ==
        0x0CU,
    "G2 FreeRTOS List_t head offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_resume_list_item, next) ==
        0x04U,
    "G2 FreeRTOS ListItem_t next offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_resume_list_item, previous) ==
        0x08U,
    "G2 FreeRTOS ListItem_t previous offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_resume_list_item, owner) ==
        0x0CU,
    "G2 FreeRTOS ListItem_t owner offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_resume_list_item, container) ==
        0x10U,
    "G2 FreeRTOS ListItem_t container offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_resume_tcb,
        state_list_item
    ) == OPEN_CFW_FREERTOS_RESUME_TCB_STATE_ITEM_OFFSET,
    "G2 FreeRTOS TCB state-item offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_resume_tcb,
        event_list_item
    ) == OPEN_CFW_FREERTOS_RESUME_TCB_EVENT_ITEM_OFFSET,
    "G2 FreeRTOS TCB event-item offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_resume_tcb, priority) ==
        OPEN_CFW_FREERTOS_RESUME_TCB_PRIORITY_OFFSET,
    "G2 FreeRTOS TCB priority offset changed"
);
#endif

extern open_cfw_freertos_resume_ubase_type ulSetInterruptMask(void);
extern void open_cfw_freertos_port_enter_critical(void);
extern void open_cfw_freertos_port_exit_critical(void);
extern void open_cfw_freertos_port_yield(void);
extern void open_cfw_freertos_task_reset_next_task_unblock_time(void);
extern open_cfw_freertos_resume_base_type
open_cfw_freertos_task_increment_tick(void);

#ifndef OPEN_CFW_FREERTOS_RESUME_CURRENT_TCB_LOAD
#define OPEN_CFW_FREERTOS_RESUME_CURRENT_TCB_LOAD() \
    (*(struct open_cfw_freertos_resume_tcb * volatile *) \
        (open_cfw_freertos_resume_uintptr) \
        OPEN_CFW_FREERTOS_RESUME_CURRENT_TCB_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_CURRENT_TASK_COUNT_LOAD
#define OPEN_CFW_FREERTOS_RESUME_CURRENT_TASK_COUNT_LOAD() \
    (*(volatile open_cfw_freertos_resume_ubase_type *) \
        (open_cfw_freertos_resume_uintptr) \
        OPEN_CFW_FREERTOS_RESUME_CURRENT_TASK_COUNT_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_TOP_READY_PRIORITY_LOAD
#define OPEN_CFW_FREERTOS_RESUME_TOP_READY_PRIORITY_LOAD() \
    (*(volatile open_cfw_freertos_resume_ubase_type *) \
        (open_cfw_freertos_resume_uintptr) \
        OPEN_CFW_FREERTOS_RESUME_TOP_READY_PRIORITY_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_TOP_READY_PRIORITY_STORE
#define OPEN_CFW_FREERTOS_RESUME_TOP_READY_PRIORITY_STORE(value) \
    (*(volatile open_cfw_freertos_resume_ubase_type *) \
        (open_cfw_freertos_resume_uintptr) \
        OPEN_CFW_FREERTOS_RESUME_TOP_READY_PRIORITY_ADDRESS = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_PENDED_TICKS_LOAD
#define OPEN_CFW_FREERTOS_RESUME_PENDED_TICKS_LOAD() \
    (*(volatile open_cfw_freertos_resume_tick_type *) \
        (open_cfw_freertos_resume_uintptr) \
        OPEN_CFW_FREERTOS_RESUME_PENDED_TICKS_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_PENDED_TICKS_STORE
#define OPEN_CFW_FREERTOS_RESUME_PENDED_TICKS_STORE(value) \
    (*(volatile open_cfw_freertos_resume_tick_type *) \
        (open_cfw_freertos_resume_uintptr) \
        OPEN_CFW_FREERTOS_RESUME_PENDED_TICKS_ADDRESS = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_YIELD_PENDING_LOAD
#define OPEN_CFW_FREERTOS_RESUME_YIELD_PENDING_LOAD() \
    (*(volatile open_cfw_freertos_resume_base_type *) \
        (open_cfw_freertos_resume_uintptr) \
        OPEN_CFW_FREERTOS_RESUME_YIELD_PENDING_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_YIELD_PENDING_STORE
#define OPEN_CFW_FREERTOS_RESUME_YIELD_PENDING_STORE(value) \
    (*(volatile open_cfw_freertos_resume_base_type *) \
        (open_cfw_freertos_resume_uintptr) \
        OPEN_CFW_FREERTOS_RESUME_YIELD_PENDING_ADDRESS = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_SCHEDULER_SUSPENDED_LOAD
#define OPEN_CFW_FREERTOS_RESUME_SCHEDULER_SUSPENDED_LOAD() \
    (*(volatile open_cfw_freertos_resume_ubase_type *) \
        (open_cfw_freertos_resume_uintptr) \
        OPEN_CFW_FREERTOS_RESUME_SCHEDULER_SUSPENDED_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_SCHEDULER_SUSPENDED_STORE
#define OPEN_CFW_FREERTOS_RESUME_SCHEDULER_SUSPENDED_STORE(value) \
    (*(volatile open_cfw_freertos_resume_ubase_type *) \
        (open_cfw_freertos_resume_uintptr) \
        OPEN_CFW_FREERTOS_RESUME_SCHEDULER_SUSPENDED_ADDRESS = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_PENDING_READY_LIST
#define OPEN_CFW_FREERTOS_RESUME_PENDING_READY_LIST() \
    ((struct open_cfw_freertos_resume_list *) \
        (open_cfw_freertos_resume_uintptr) \
        OPEN_CFW_FREERTOS_RESUME_PENDING_READY_LIST_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_READY_LIST
#define OPEN_CFW_FREERTOS_RESUME_READY_LIST(priority) \
    (&((struct open_cfw_freertos_resume_list *) \
        (open_cfw_freertos_resume_uintptr) \
        OPEN_CFW_FREERTOS_RESUME_READY_LISTS_ADDRESS)[(priority)])
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_MEMORY_BARRIER
#define OPEN_CFW_FREERTOS_RESUME_MEMORY_BARRIER() \
    __asm volatile("" ::: "memory")
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_ENTER_CRITICAL
#define OPEN_CFW_FREERTOS_RESUME_ENTER_CRITICAL() \
    open_cfw_freertos_port_enter_critical()
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_EXIT_CRITICAL
#define OPEN_CFW_FREERTOS_RESUME_EXIT_CRITICAL() \
    open_cfw_freertos_port_exit_critical()
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_YIELD
#define OPEN_CFW_FREERTOS_RESUME_YIELD() open_cfw_freertos_port_yield()
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_RESET_NEXT_UNBLOCK_TIME
#define OPEN_CFW_FREERTOS_RESUME_RESET_NEXT_UNBLOCK_TIME() \
    open_cfw_freertos_task_reset_next_task_unblock_time()
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_INCREMENT_TICK
#define OPEN_CFW_FREERTOS_RESUME_INCREMENT_TICK() \
    open_cfw_freertos_task_increment_tick()
#endif

#ifndef OPEN_CFW_FREERTOS_RESUME_ASSERT
#define OPEN_CFW_FREERTOS_RESUME_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            (void)ulSetInterruptMask(); \
            *(volatile open_cfw_freertos_resume_ubase_type *) \
                (open_cfw_freertos_resume_uintptr)-1 = 0U; \
            for (;;) { \
            } \
        } \
    } while (0)
#endif

open_cfw_freertos_resume_base_type
open_cfw_freertos_task_resume_all(void);

#endif
