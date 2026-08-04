/*
 * SPDX-License-Identifier: MIT
 *
 * Isolated G2 ABI for the FreeRTOS-Kernel V10.5.1 xQueueGenericReset()
 * production source leaf.  Fixed providers are intentionally explicit and
 * overridable by hosted differential fixtures.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_QUEUE_GENERIC_RESET_H
#define OPEN_CFW_RUNTIME_FREERTOS_QUEUE_GENERIC_RESET_H

typedef __INT32_TYPE__ open_cfw_freertos_queue_reset_base_type;
typedef __UINT32_TYPE__ open_cfw_freertos_queue_reset_ubase_type;
typedef __UINT32_TYPE__ open_cfw_freertos_queue_reset_tick_type;
typedef __UINTPTR_TYPE__ open_cfw_freertos_queue_reset_uintptr;
typedef __INT8_TYPE__ open_cfw_freertos_queue_reset_int8;
typedef __UINT8_TYPE__ open_cfw_freertos_queue_reset_uint8;

enum {
    OPEN_CFW_FREERTOS_QUEUE_RESET_FALSE = 0,
    OPEN_CFW_FREERTOS_QUEUE_RESET_PASS = 1,
    OPEN_CFW_FREERTOS_QUEUE_RESET_FAIL = 0,
    OPEN_CFW_FREERTOS_QUEUE_RESET_UNLOCKED = -1,
    OPEN_CFW_FREERTOS_QUEUE_RESET_ASSERT_MASK_ADDRESS = 0x005FA0A4U,
    OPEN_CFW_FREERTOS_QUEUE_RESET_YIELD_ADDRESS = 0x004420BCU,
    OPEN_CFW_FREERTOS_QUEUE_RESET_ENTER_CRITICAL_ADDRESS = 0x004420D0U,
    OPEN_CFW_FREERTOS_QUEUE_RESET_EXIT_CRITICAL_ADDRESS = 0x004420E8U,
    OPEN_CFW_FREERTOS_QUEUE_RESET_REMOVE_EVENT_ADDRESS = 0x00455370U,
    OPEN_CFW_FREERTOS_QUEUE_RESET_LIST_INITIALISE_ADDRESS = 0x0045607CU,
    OPEN_CFW_FREERTOS_QUEUE_RESET_LIST_ITEM_SIZE = 0x14U,
    OPEN_CFW_FREERTOS_QUEUE_RESET_MINI_LIST_ITEM_SIZE = 0x0CU,
    OPEN_CFW_FREERTOS_QUEUE_RESET_LIST_SIZE = 0x14U,
    OPEN_CFW_FREERTOS_QUEUE_RESET_QUEUE_SIZE = 0x50U
};

#define OPEN_CFW_FREERTOS_QUEUE_RESET_SIZE_MAX __UINT32_MAX__

struct open_cfw_freertos_queue_reset_list;

struct open_cfw_freertos_queue_reset_list_item {
    open_cfw_freertos_queue_reset_tick_type item_value;
    struct open_cfw_freertos_queue_reset_list_item *next;
    struct open_cfw_freertos_queue_reset_list_item *previous;
    void *owner;
    struct open_cfw_freertos_queue_reset_list *container;
};

struct open_cfw_freertos_queue_reset_mini_list_item {
    open_cfw_freertos_queue_reset_tick_type item_value;
    struct open_cfw_freertos_queue_reset_list_item *next;
    struct open_cfw_freertos_queue_reset_list_item *previous;
};

struct open_cfw_freertos_queue_reset_list {
    volatile open_cfw_freertos_queue_reset_ubase_type item_count;
    struct open_cfw_freertos_queue_reset_list_item *index;
    struct open_cfw_freertos_queue_reset_mini_list_item end;
};

struct open_cfw_freertos_queue_reset_control {
    open_cfw_freertos_queue_reset_int8 *head;
    open_cfw_freertos_queue_reset_int8 *write_to;
    union {
        struct {
            open_cfw_freertos_queue_reset_int8 *tail;
            open_cfw_freertos_queue_reset_int8 *read_from;
        } queue;
        struct {
            void *mutex_holder;
            open_cfw_freertos_queue_reset_ubase_type recursive_call_count;
        } semaphore;
    } value;
    struct open_cfw_freertos_queue_reset_list tasks_waiting_to_send;
    struct open_cfw_freertos_queue_reset_list tasks_waiting_to_receive;
    volatile open_cfw_freertos_queue_reset_ubase_type messages_waiting;
    open_cfw_freertos_queue_reset_ubase_type length;
    open_cfw_freertos_queue_reset_ubase_type item_size;
    volatile open_cfw_freertos_queue_reset_int8 receive_lock;
    volatile open_cfw_freertos_queue_reset_int8 transmit_lock;
    open_cfw_freertos_queue_reset_uint8 statically_allocated;
    open_cfw_freertos_queue_reset_uint8 allocation_padding;
    open_cfw_freertos_queue_reset_ubase_type queue_number;
    open_cfw_freertos_queue_reset_uint8 queue_type;
    open_cfw_freertos_queue_reset_uint8 trace_padding[3];
};

_Static_assert(
    sizeof(open_cfw_freertos_queue_reset_base_type) == 4U,
    "G2 FreeRTOS BaseType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_queue_reset_ubase_type) == 4U,
    "G2 FreeRTOS UBaseType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_queue_reset_tick_type) == 4U,
    "G2 FreeRTOS TickType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_queue_reset_int8) == 1U,
    "G2 FreeRTOS queue-lock width changed"
);

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(struct open_cfw_freertos_queue_reset_list_item) ==
        OPEN_CFW_FREERTOS_QUEUE_RESET_LIST_ITEM_SIZE,
    "G2 FreeRTOS ListItem_t size changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_queue_reset_mini_list_item) ==
        OPEN_CFW_FREERTOS_QUEUE_RESET_MINI_LIST_ITEM_SIZE,
    "G2 FreeRTOS MiniListItem_t size changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_queue_reset_list) ==
        OPEN_CFW_FREERTOS_QUEUE_RESET_LIST_SIZE,
    "G2 FreeRTOS List_t size changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_queue_reset_control) ==
        OPEN_CFW_FREERTOS_QUEUE_RESET_QUEUE_SIZE,
    "G2 FreeRTOS Queue_t size changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_reset_control,
        value.queue.tail
    ) == 0x08U,
    "G2 FreeRTOS Queue_t tail offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_reset_control,
        value.queue.read_from
    ) == 0x0CU,
    "G2 FreeRTOS Queue_t read offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_reset_control,
        tasks_waiting_to_send
    ) == 0x10U,
    "G2 FreeRTOS Queue_t send-list offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_reset_control,
        tasks_waiting_to_receive
    ) == 0x24U,
    "G2 FreeRTOS Queue_t receive-list offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_reset_control,
        messages_waiting
    ) == 0x38U,
    "G2 FreeRTOS Queue_t message-count offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_freertos_queue_reset_control, length) ==
        0x3CU,
    "G2 FreeRTOS Queue_t length offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_reset_control,
        item_size
    ) == 0x40U,
    "G2 FreeRTOS Queue_t item-size offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_reset_control,
        receive_lock
    ) == 0x44U,
    "G2 FreeRTOS Queue_t receive-lock offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_reset_control,
        transmit_lock
    ) == 0x45U,
    "G2 FreeRTOS Queue_t transmit-lock offset changed"
);
#endif

typedef open_cfw_freertos_queue_reset_ubase_type
(*open_cfw_freertos_queue_reset_assert_mask_fn)(void);
typedef void (*open_cfw_freertos_queue_reset_void_fn)(void);
typedef open_cfw_freertos_queue_reset_base_type
(*open_cfw_freertos_queue_reset_remove_fn)(
    const struct open_cfw_freertos_queue_reset_list *
);
typedef void (*open_cfw_freertos_queue_reset_list_init_fn)(
    struct open_cfw_freertos_queue_reset_list *
);

#ifndef OPEN_CFW_FREERTOS_QUEUE_RESET_ASSERT_MASK
#define OPEN_CFW_FREERTOS_QUEUE_RESET_ASSERT_MASK() \
    (((open_cfw_freertos_queue_reset_assert_mask_fn) \
        (open_cfw_freertos_queue_reset_uintptr) \
        (OPEN_CFW_FREERTOS_QUEUE_RESET_ASSERT_MASK_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_RESET_ASSERT
#define OPEN_CFW_FREERTOS_QUEUE_RESET_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            (void)OPEN_CFW_FREERTOS_QUEUE_RESET_ASSERT_MASK(); \
            *(volatile open_cfw_freertos_queue_reset_ubase_type *) \
                (open_cfw_freertos_queue_reset_uintptr)-1 = 0U; \
            for (;;) { \
            } \
        } \
    } while (0)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_RESET_ENTER_CRITICAL
#define OPEN_CFW_FREERTOS_QUEUE_RESET_ENTER_CRITICAL() \
    (((open_cfw_freertos_queue_reset_void_fn) \
        (open_cfw_freertos_queue_reset_uintptr) \
        (OPEN_CFW_FREERTOS_QUEUE_RESET_ENTER_CRITICAL_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_RESET_EXIT_CRITICAL
#define OPEN_CFW_FREERTOS_QUEUE_RESET_EXIT_CRITICAL() \
    (((open_cfw_freertos_queue_reset_void_fn) \
        (open_cfw_freertos_queue_reset_uintptr) \
        (OPEN_CFW_FREERTOS_QUEUE_RESET_EXIT_CRITICAL_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_RESET_REMOVE_FROM_EVENT_LIST
#define OPEN_CFW_FREERTOS_QUEUE_RESET_REMOVE_FROM_EVENT_LIST(list) \
    (((open_cfw_freertos_queue_reset_remove_fn) \
        (open_cfw_freertos_queue_reset_uintptr) \
        (OPEN_CFW_FREERTOS_QUEUE_RESET_REMOVE_EVENT_ADDRESS | 1U))((list)))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_RESET_LIST_INITIALISE
#define OPEN_CFW_FREERTOS_QUEUE_RESET_LIST_INITIALISE(list) \
    (((open_cfw_freertos_queue_reset_list_init_fn) \
        (open_cfw_freertos_queue_reset_uintptr) \
        (OPEN_CFW_FREERTOS_QUEUE_RESET_LIST_INITIALISE_ADDRESS | 1U))((list)))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_RESET_YIELD
#define OPEN_CFW_FREERTOS_QUEUE_RESET_YIELD() \
    (((open_cfw_freertos_queue_reset_void_fn) \
        (open_cfw_freertos_queue_reset_uintptr) \
        (OPEN_CFW_FREERTOS_QUEUE_RESET_YIELD_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_RESET_COVERAGE_MARKER
#define OPEN_CFW_FREERTOS_QUEUE_RESET_COVERAGE_MARKER() \
    do { \
    } while (0)
#endif

open_cfw_freertos_queue_reset_base_type
open_cfw_freertos_queue_generic_reset(
    struct open_cfw_freertos_queue_reset_control *queue,
    open_cfw_freertos_queue_reset_base_type new_queue
);

#endif
