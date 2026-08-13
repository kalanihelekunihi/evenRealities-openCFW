/*
 * SPDX-License-Identifier: MIT
 *
 * Recovered G2 FreeRTOS vTaskSwitchContext ABI and fixed-state seams.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_TASK_SWITCH_CONTEXT_H
#define OPEN_CFW_RUNTIME_FREERTOS_TASK_SWITCH_CONTEXT_H

typedef __UINT32_TYPE__ open_cfw_freertos_switch_ubase_type;
typedef __UINT32_TYPE__ open_cfw_freertos_switch_stack_type;
typedef __UINTPTR_TYPE__ open_cfw_freertos_switch_uintptr;

enum {
    OPEN_CFW_FREERTOS_SWITCH_FALSE = 0,
    OPEN_CFW_FREERTOS_SWITCH_TRUE = 1,
    OPEN_CFW_FREERTOS_SWITCH_MAX_PRIORITIES = 56U,
    OPEN_CFW_FREERTOS_SWITCH_TRACE_CAPACITY = 64U,
    OPEN_CFW_FREERTOS_SWITCH_STACK_FILL_WORD = 0xA5A5A5A5U,
    OPEN_CFW_FREERTOS_SWITCH_CURRENT_TCB_ADDRESS = 0x20074A20U,
    OPEN_CFW_FREERTOS_SWITCH_TOP_READY_PRIORITY_ADDRESS = 0x20074A38U,
    OPEN_CFW_FREERTOS_SWITCH_YIELD_PENDING_ADDRESS = 0x20074A44U,
    OPEN_CFW_FREERTOS_SWITCH_SCHEDULER_SUSPENDED_ADDRESS = 0x20074A58U,
    OPEN_CFW_FREERTOS_SWITCH_TRACE_INDEX_ADDRESS = 0x20074A5CU,
    OPEN_CFW_FREERTOS_SWITCH_READY_LISTS_ADDRESS = 0x2006A49CU,
    OPEN_CFW_FREERTOS_SWITCH_TRACE_RECORDS_ADDRESS = 0x2006F348U,
    OPEN_CFW_FREERTOS_SWITCH_LIST_ITEM_SIZE = 0x14U,
    OPEN_CFW_FREERTOS_SWITCH_MINI_LIST_ITEM_SIZE = 0x0CU,
    OPEN_CFW_FREERTOS_SWITCH_LIST_SIZE = 0x14U,
    OPEN_CFW_FREERTOS_SWITCH_TCB_STACK_BASE_OFFSET = 0x30U,
    OPEN_CFW_FREERTOS_SWITCH_TCB_NAME_OFFSET = 0x34U,
    OPEN_CFW_FREERTOS_SWITCH_TCB_NUMBER_OFFSET = 0x58U,
    OPEN_CFW_FREERTOS_SWITCH_TCB_SIZE = 0x70U
};

struct open_cfw_freertos_switch_list;

struct open_cfw_freertos_switch_list_item {
    open_cfw_freertos_switch_ubase_type item_value;
    struct open_cfw_freertos_switch_list_item *next;
    struct open_cfw_freertos_switch_list_item *previous;
    void *owner;
    struct open_cfw_freertos_switch_list *container;
};

struct open_cfw_freertos_switch_mini_list_item {
    open_cfw_freertos_switch_ubase_type item_value;
    struct open_cfw_freertos_switch_list_item *next;
    struct open_cfw_freertos_switch_list_item *previous;
};

struct open_cfw_freertos_switch_list {
    volatile open_cfw_freertos_switch_ubase_type item_count;
    struct open_cfw_freertos_switch_list_item *index;
    struct open_cfw_freertos_switch_mini_list_item end;
};

struct open_cfw_freertos_switch_tcb {
    void *top_of_stack;
    struct open_cfw_freertos_switch_list_item state_list_item;
    struct open_cfw_freertos_switch_list_item event_list_item;
    open_cfw_freertos_switch_ubase_type priority;
    volatile open_cfw_freertos_switch_stack_type *stack_base;
    char task_name[32];
    open_cfw_freertos_switch_ubase_type stack_depth;
    open_cfw_freertos_switch_ubase_type task_number;
    open_cfw_freertos_switch_ubase_type task_number_secondary;
    open_cfw_freertos_switch_ubase_type base_priority;
    open_cfw_freertos_switch_ubase_type mutexes_held;
    open_cfw_freertos_switch_ubase_type notification_value;
    unsigned char notification_state;
    unsigned char reserved[3];
};

struct open_cfw_freertos_switch_trace_record {
    volatile open_cfw_freertos_switch_ubase_type switched_out;
    volatile open_cfw_freertos_switch_ubase_type switched_in;
};

_Static_assert(
    sizeof(open_cfw_freertos_switch_ubase_type) == 4U,
    "G2 FreeRTOS UBaseType_t width changed"
);

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(struct open_cfw_freertos_switch_list_item) ==
        OPEN_CFW_FREERTOS_SWITCH_LIST_ITEM_SIZE,
    "G2 FreeRTOS ListItem_t size changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_switch_mini_list_item) ==
        OPEN_CFW_FREERTOS_SWITCH_MINI_LIST_ITEM_SIZE,
    "G2 FreeRTOS MiniListItem_t size changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_switch_list) ==
        OPEN_CFW_FREERTOS_SWITCH_LIST_SIZE,
    "G2 FreeRTOS List_t size changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_switch_list, index) == 0x04U,
    "G2 FreeRTOS List_t index offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_switch_list, end) == 0x08U,
    "G2 FreeRTOS List_t end offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_switch_tcb, stack_base) ==
        OPEN_CFW_FREERTOS_SWITCH_TCB_STACK_BASE_OFFSET,
    "G2 FreeRTOS TCB stack-base offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_switch_tcb, task_name) ==
        OPEN_CFW_FREERTOS_SWITCH_TCB_NAME_OFFSET,
    "G2 FreeRTOS TCB name offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_switch_tcb, task_number) ==
        OPEN_CFW_FREERTOS_SWITCH_TCB_NUMBER_OFFSET,
    "G2 FreeRTOS TCB number offset changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_switch_tcb) ==
        OPEN_CFW_FREERTOS_SWITCH_TCB_SIZE,
    "G2 FreeRTOS TCB size changed"
);
#endif

extern open_cfw_freertos_switch_ubase_type ulSetInterruptMask(void);
extern void open_cfw_retained_freertos_stack_overflow_hook(
    struct open_cfw_freertos_switch_tcb *tcb,
    const char *task_name
);

#ifndef OPEN_CFW_FREERTOS_SWITCH_CURRENT_TCB_LOAD
#define OPEN_CFW_FREERTOS_SWITCH_CURRENT_TCB_LOAD() \
    (*(struct open_cfw_freertos_switch_tcb * volatile *) \
        (open_cfw_freertos_switch_uintptr) \
        OPEN_CFW_FREERTOS_SWITCH_CURRENT_TCB_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_SWITCH_CURRENT_TCB_STORE
#define OPEN_CFW_FREERTOS_SWITCH_CURRENT_TCB_STORE(value) \
    (*(struct open_cfw_freertos_switch_tcb * volatile *) \
        (open_cfw_freertos_switch_uintptr) \
        OPEN_CFW_FREERTOS_SWITCH_CURRENT_TCB_ADDRESS = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_SWITCH_TOP_READY_PRIORITY_LOAD
#define OPEN_CFW_FREERTOS_SWITCH_TOP_READY_PRIORITY_LOAD() \
    (*(volatile open_cfw_freertos_switch_ubase_type *) \
        (open_cfw_freertos_switch_uintptr) \
        OPEN_CFW_FREERTOS_SWITCH_TOP_READY_PRIORITY_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_SWITCH_TOP_READY_PRIORITY_STORE
#define OPEN_CFW_FREERTOS_SWITCH_TOP_READY_PRIORITY_STORE(value) \
    (*(volatile open_cfw_freertos_switch_ubase_type *) \
        (open_cfw_freertos_switch_uintptr) \
        OPEN_CFW_FREERTOS_SWITCH_TOP_READY_PRIORITY_ADDRESS = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_SWITCH_YIELD_PENDING_STORE
#define OPEN_CFW_FREERTOS_SWITCH_YIELD_PENDING_STORE(value) \
    (*(volatile open_cfw_freertos_switch_ubase_type *) \
        (open_cfw_freertos_switch_uintptr) \
        OPEN_CFW_FREERTOS_SWITCH_YIELD_PENDING_ADDRESS = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_SWITCH_SCHEDULER_SUSPENDED_LOAD
#define OPEN_CFW_FREERTOS_SWITCH_SCHEDULER_SUSPENDED_LOAD() \
    (*(volatile open_cfw_freertos_switch_ubase_type *) \
        (open_cfw_freertos_switch_uintptr) \
        OPEN_CFW_FREERTOS_SWITCH_SCHEDULER_SUSPENDED_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_SWITCH_TRACE_INDEX_LOAD
#define OPEN_CFW_FREERTOS_SWITCH_TRACE_INDEX_LOAD() \
    (*(volatile open_cfw_freertos_switch_ubase_type *) \
        (open_cfw_freertos_switch_uintptr) \
        OPEN_CFW_FREERTOS_SWITCH_TRACE_INDEX_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_SWITCH_TRACE_INDEX_STORE
#define OPEN_CFW_FREERTOS_SWITCH_TRACE_INDEX_STORE(value) \
    (*(volatile open_cfw_freertos_switch_ubase_type *) \
        (open_cfw_freertos_switch_uintptr) \
        OPEN_CFW_FREERTOS_SWITCH_TRACE_INDEX_ADDRESS = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_SWITCH_READY_LIST
#define OPEN_CFW_FREERTOS_SWITCH_READY_LIST(priority) \
    (&((struct open_cfw_freertos_switch_list *) \
        (open_cfw_freertos_switch_uintptr) \
        OPEN_CFW_FREERTOS_SWITCH_READY_LISTS_ADDRESS)[(priority)])
#endif

#ifndef OPEN_CFW_FREERTOS_SWITCH_TRACE_RECORD
#define OPEN_CFW_FREERTOS_SWITCH_TRACE_RECORD(index) \
    (&((struct open_cfw_freertos_switch_trace_record *) \
        (open_cfw_freertos_switch_uintptr) \
        OPEN_CFW_FREERTOS_SWITCH_TRACE_RECORDS_ADDRESS)[(index)])
#endif

#ifndef OPEN_CFW_FREERTOS_SWITCH_STACK_OVERFLOW_HOOK
#define OPEN_CFW_FREERTOS_SWITCH_STACK_OVERFLOW_HOOK(tcb, task_name) \
    open_cfw_retained_freertos_stack_overflow_hook((tcb), (task_name))
#endif

#ifndef OPEN_CFW_FREERTOS_SWITCH_ASSERT
#define OPEN_CFW_FREERTOS_SWITCH_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            (void)ulSetInterruptMask(); \
            *(volatile open_cfw_freertos_switch_ubase_type *) \
                (open_cfw_freertos_switch_uintptr)-1 = 0U; \
            for (;;) { \
            } \
        } \
    } while (0)
#endif

void open_cfw_freertos_task_switch_context(void);

#endif
