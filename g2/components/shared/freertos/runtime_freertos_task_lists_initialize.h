/*
 * SPDX-License-Identifier: MIT
 *
 * FreeRTOS task-list initialization ABI for the Even
 * Realities G2 Apollo-main image. The fixed addresses and configuration
 * values below are recovered properties of the official V10.5.1 build.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_TASK_LISTS_INITIALIZE_H
#define OPEN_CFW_RUNTIME_FREERTOS_TASK_LISTS_INITIALIZE_H

typedef __UINT32_TYPE__ open_cfw_freertos_task_lists_ubase_type;
typedef __UINT32_TYPE__ open_cfw_freertos_task_lists_tick_type;
typedef __UINT32_TYPE__ open_cfw_freertos_task_lists_target_pointer;
typedef __UINTPTR_TYPE__ open_cfw_freertos_task_lists_uintptr;

enum {
    OPEN_CFW_FREERTOS_TASK_LISTS_MAX_PRIORITIES = 56U,
    OPEN_CFW_FREERTOS_TASK_LISTS_SPECIAL_LIST_COUNT = 5U,
    OPEN_CFW_FREERTOS_TASK_LISTS_READY_LISTS_ADDRESS = 0x2006A49CU,
    OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_1_ADDRESS = 0x20073CFCU,
    OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_2_ADDRESS = 0x20073D10U,
    OPEN_CFW_FREERTOS_TASK_LISTS_PENDING_READY_LIST_ADDRESS = 0x20073D24U,
    OPEN_CFW_FREERTOS_TASK_LISTS_TERMINATION_LIST_ADDRESS = 0x20073D38U,
    OPEN_CFW_FREERTOS_TASK_LISTS_SUSPENDED_LIST_ADDRESS = 0x20073D4CU,
    OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_POINTER_ADDRESS = 0x20074A24U,
    OPEN_CFW_FREERTOS_TASK_LISTS_OVERFLOW_POINTER_ADDRESS = 0x20074A28U
};

/*
 * This is a 32-bit ABI mirror, not a host-native pointer structure. On the
 * target, the three address words have the same representation as the
 * corresponding FreeRTOS pointers. Keeping them as words also makes the
 * target layout fail closed when the source is exercised on a 64-bit host.
 */
struct open_cfw_freertos_task_lists_list {
    volatile open_cfw_freertos_task_lists_ubase_type item_count;
    open_cfw_freertos_task_lists_target_pointer index;
    open_cfw_freertos_task_lists_tick_type end_item_value;
    open_cfw_freertos_task_lists_target_pointer end_next;
    open_cfw_freertos_task_lists_target_pointer end_previous;
};

_Static_assert(
    sizeof(open_cfw_freertos_task_lists_ubase_type) == 4U,
    "G2 FreeRTOS UBaseType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_task_lists_tick_type) == 4U,
    "G2 FreeRTOS TickType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_task_lists_target_pointer) == 4U,
    "G2 FreeRTOS pointer representation changed"
);
_Static_assert(
    OPEN_CFW_FREERTOS_TASK_LISTS_MAX_PRIORITIES == 56U,
    "G2 configMAX_PRIORITIES changed"
);
_Static_assert(
    OPEN_CFW_FREERTOS_TASK_LISTS_SPECIAL_LIST_COUNT == 5U,
    "G2 task special-list selection changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_task_lists_list) == 0x14U,
    "G2 FreeRTOS List_t size changed"
);
_Static_assert(
    _Alignof(struct open_cfw_freertos_task_lists_list) == 4U,
    "G2 FreeRTOS List_t alignment changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_task_lists_list,
        item_count
    ) == 0x00U,
    "G2 FreeRTOS List_t item-count offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_task_lists_list,
        index
    ) == 0x04U,
    "G2 FreeRTOS List_t index offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_task_lists_list,
        end_item_value
    ) == 0x08U,
    "G2 FreeRTOS List_t end-marker offset changed"
);

#ifndef OPEN_CFW_FREERTOS_TASK_LISTS_READY_LISTS
#define OPEN_CFW_FREERTOS_TASK_LISTS_READY_LISTS \
    ((struct open_cfw_freertos_task_lists_list *) \
        (open_cfw_freertos_task_lists_uintptr) \
        OPEN_CFW_FREERTOS_TASK_LISTS_READY_LISTS_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_1
#define OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_1 \
    ((struct open_cfw_freertos_task_lists_list *) \
        (open_cfw_freertos_task_lists_uintptr) \
        OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_1_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_2
#define OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_2 \
    ((struct open_cfw_freertos_task_lists_list *) \
        (open_cfw_freertos_task_lists_uintptr) \
        OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_2_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_TASK_LISTS_PENDING_READY_LIST
#define OPEN_CFW_FREERTOS_TASK_LISTS_PENDING_READY_LIST \
    ((struct open_cfw_freertos_task_lists_list *) \
        (open_cfw_freertos_task_lists_uintptr) \
        OPEN_CFW_FREERTOS_TASK_LISTS_PENDING_READY_LIST_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_TASK_LISTS_TERMINATION_LIST
#define OPEN_CFW_FREERTOS_TASK_LISTS_TERMINATION_LIST \
    ((struct open_cfw_freertos_task_lists_list *) \
        (open_cfw_freertos_task_lists_uintptr) \
        OPEN_CFW_FREERTOS_TASK_LISTS_TERMINATION_LIST_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_TASK_LISTS_SUSPENDED_LIST
#define OPEN_CFW_FREERTOS_TASK_LISTS_SUSPENDED_LIST \
    ((struct open_cfw_freertos_task_lists_list *) \
        (open_cfw_freertos_task_lists_uintptr) \
        OPEN_CFW_FREERTOS_TASK_LISTS_SUSPENDED_LIST_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_POINTER
#define OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_POINTER \
    (*(volatile open_cfw_freertos_task_lists_target_pointer *) \
        (open_cfw_freertos_task_lists_uintptr) \
        OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_POINTER_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_TASK_LISTS_OVERFLOW_POINTER
#define OPEN_CFW_FREERTOS_TASK_LISTS_OVERFLOW_POINTER \
    (*(volatile open_cfw_freertos_task_lists_target_pointer *) \
        (open_cfw_freertos_task_lists_uintptr) \
        OPEN_CFW_FREERTOS_TASK_LISTS_OVERFLOW_POINTER_ADDRESS)
#endif

/* Exact external type and symbol already source-owned by Apollo-main. */
struct open_cfw_freertos_list_initialise_list;

void open_cfw_freertos_list_initialise(
    struct open_cfw_freertos_list_initialise_list *list
);

void open_cfw_freertos_task_lists_initialize(void);

#endif
