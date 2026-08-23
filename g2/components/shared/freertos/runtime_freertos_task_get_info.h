/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_FREERTOS_TASK_GET_INFO_H
#define OPEN_CFW_RUNTIME_FREERTOS_TASK_GET_INFO_H

typedef __UINT8_TYPE__ open_cfw_freertos_task_get_info_u8;
typedef __UINT16_TYPE__ open_cfw_freertos_task_get_info_u16;
typedef __UINT32_TYPE__ open_cfw_freertos_task_get_info_u32;
typedef __UINTPTR_TYPE__ open_cfw_freertos_task_get_info_uintptr;

enum open_cfw_freertos_task_get_info_state {
    OPEN_CFW_FREERTOS_TASK_GET_INFO_RUNNING = 0,
    OPEN_CFW_FREERTOS_TASK_GET_INFO_READY = 1,
    OPEN_CFW_FREERTOS_TASK_GET_INFO_BLOCKED = 2,
    OPEN_CFW_FREERTOS_TASK_GET_INFO_SUSPENDED = 3,
    OPEN_CFW_FREERTOS_TASK_GET_INFO_DELETED = 4,
    OPEN_CFW_FREERTOS_TASK_GET_INFO_INVALID = 5
};

struct open_cfw_freertos_task_get_info_list_item {
    open_cfw_freertos_task_get_info_u32 value;
    void *next;
    void *previous;
    void *owner;
    void *container;
};

struct open_cfw_freertos_task_get_info_tcb {
    void *top_of_stack;
    struct open_cfw_freertos_task_get_info_list_item state_list_item;
    struct open_cfw_freertos_task_get_info_list_item event_list_item;
    open_cfw_freertos_task_get_info_u32 priority;
    open_cfw_freertos_task_get_info_u8 *stack;
    char name[32];
    void *end_of_stack;
    open_cfw_freertos_task_get_info_u32 tcb_number;
    open_cfw_freertos_task_get_info_u32 task_number;
    open_cfw_freertos_task_get_info_u32 base_priority;
};

/*
 * IAR stores the small eTaskState enum in one byte in this public record.
 * Explicit padding preserves the recovered 36-byte G2 TaskStatus_t ABI.
 */
struct open_cfw_freertos_task_get_info_status {
    struct open_cfw_freertos_task_get_info_tcb *handle;
    const char *name;
    open_cfw_freertos_task_get_info_u32 task_number;
    open_cfw_freertos_task_get_info_u8 current_state;
    open_cfw_freertos_task_get_info_u8 state_padding[3];
    open_cfw_freertos_task_get_info_u32 current_priority;
    open_cfw_freertos_task_get_info_u32 base_priority;
    open_cfw_freertos_task_get_info_u32 run_time_counter;
    open_cfw_freertos_task_get_info_u8 *stack_base;
    open_cfw_freertos_task_get_info_u16 stack_high_water_mark;
    open_cfw_freertos_task_get_info_u16 tail_padding;
};

enum {
    OPEN_CFW_FREERTOS_TASK_GET_INFO_CURRENT_TCB_ADDRESS = 0x20074A20U
};

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(sizeof(struct open_cfw_freertos_task_get_info_list_item) == 0x14U, "G2 ListItem_t ABI changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_task_get_info_tcb, event_list_item.container) == 0x28U, "G2 TCB event-container offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_task_get_info_tcb, priority) == 0x2CU, "G2 TCB priority offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_task_get_info_tcb, stack) == 0x30U, "G2 TCB stack offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_task_get_info_tcb, name) == 0x34U, "G2 TCB name offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_task_get_info_tcb, tcb_number) == 0x58U, "G2 TCB number offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_task_get_info_tcb, base_priority) == 0x60U, "G2 TCB base-priority offset changed");
_Static_assert(sizeof(struct open_cfw_freertos_task_get_info_status) == 0x24U, "G2 TaskStatus_t ABI changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_task_get_info_status, current_state) == 0x0CU, "G2 TaskStatus_t state offset changed");
_Static_assert(__builtin_offsetof(struct open_cfw_freertos_task_get_info_status, stack_high_water_mark) == 0x20U, "G2 TaskStatus_t high-water offset changed");
#endif

#ifndef OPEN_CFW_FREERTOS_TASK_GET_INFO_CURRENT_TCB_LOAD
#define OPEN_CFW_FREERTOS_TASK_GET_INFO_CURRENT_TCB_LOAD() \
    (*(struct open_cfw_freertos_task_get_info_tcb * volatile *) \
        (open_cfw_freertos_task_get_info_uintptr) \
        OPEN_CFW_FREERTOS_TASK_GET_INFO_CURRENT_TCB_ADDRESS)
#endif

void open_cfw_freertos_task_get_info(
    struct open_cfw_freertos_task_get_info_tcb *task,
    struct open_cfw_freertos_task_get_info_status *status,
    open_cfw_freertos_task_get_info_u32 get_free_stack_space,
    enum open_cfw_freertos_task_get_info_state state
);

#endif
