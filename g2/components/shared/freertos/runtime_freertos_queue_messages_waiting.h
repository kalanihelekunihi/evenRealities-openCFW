/*
 * SPDX-License-Identifier: MIT
 *
 * Isolated G2 ABI for the FreeRTOS-Kernel V10.5.1
 * uxQueueMessagesWaiting() and uxQueueMessagesWaitingFromISR() source
 * leaves.  Fixed providers are explicit and overridable so the exact target
 * behavior can be exercised by hosted differential fixtures.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_QUEUE_MESSAGES_WAITING_H
#define OPEN_CFW_RUNTIME_FREERTOS_QUEUE_MESSAGES_WAITING_H

typedef __UINT32_TYPE__ open_cfw_freertos_queue_messages_ubase_type;
typedef __UINTPTR_TYPE__ open_cfw_freertos_queue_messages_uintptr;
typedef __INT8_TYPE__ open_cfw_freertos_queue_messages_int8;
typedef __UINT8_TYPE__ open_cfw_freertos_queue_messages_uint8;

enum {
    OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ASSERT_MASK_ADDRESS = 0x005FA0A4U,
    OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ENTER_CRITICAL_ADDRESS = 0x004420D0U,
    OPEN_CFW_FREERTOS_QUEUE_MESSAGES_EXIT_CRITICAL_ADDRESS = 0x004420E8U,
    OPEN_CFW_FREERTOS_QUEUE_MESSAGES_LIST_SIZE = 0x14U,
    OPEN_CFW_FREERTOS_QUEUE_MESSAGES_QUEUE_SIZE = 0x50U
};

struct open_cfw_freertos_queue_messages_list {
    volatile open_cfw_freertos_queue_messages_ubase_type item_count;
    unsigned char remainder[16];
};

struct open_cfw_freertos_queue_messages_control {
    open_cfw_freertos_queue_messages_int8 *head;
    open_cfw_freertos_queue_messages_int8 *write_to;
    union {
        struct {
            open_cfw_freertos_queue_messages_int8 *tail;
            open_cfw_freertos_queue_messages_int8 *read_from;
        } queue;
        struct {
            void *mutex_holder;
            open_cfw_freertos_queue_messages_ubase_type recursive_call_count;
        } semaphore;
    } value;
    struct open_cfw_freertos_queue_messages_list tasks_waiting_to_send;
    struct open_cfw_freertos_queue_messages_list tasks_waiting_to_receive;
    volatile open_cfw_freertos_queue_messages_ubase_type messages_waiting;
    open_cfw_freertos_queue_messages_ubase_type length;
    open_cfw_freertos_queue_messages_ubase_type item_size;
    volatile open_cfw_freertos_queue_messages_int8 receive_lock;
    volatile open_cfw_freertos_queue_messages_int8 transmit_lock;
    open_cfw_freertos_queue_messages_uint8 statically_allocated;
    open_cfw_freertos_queue_messages_uint8 allocation_padding;
    open_cfw_freertos_queue_messages_ubase_type queue_number;
    open_cfw_freertos_queue_messages_uint8 queue_type;
    open_cfw_freertos_queue_messages_uint8 trace_padding[3];
};

_Static_assert(
    sizeof(open_cfw_freertos_queue_messages_ubase_type) == 4U,
    "G2 FreeRTOS UBaseType_t width changed"
);
_Static_assert(
    sizeof(open_cfw_freertos_queue_messages_int8) == 1U,
    "G2 FreeRTOS queue-lock width changed"
);

#if defined(__arm__)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(struct open_cfw_freertos_queue_messages_list) ==
        OPEN_CFW_FREERTOS_QUEUE_MESSAGES_LIST_SIZE,
    "G2 FreeRTOS List_t size changed"
);
_Static_assert(
    sizeof(struct open_cfw_freertos_queue_messages_control) ==
        OPEN_CFW_FREERTOS_QUEUE_MESSAGES_QUEUE_SIZE,
    "G2 FreeRTOS Queue_t size changed"
);
_Static_assert(
    _Alignof(struct open_cfw_freertos_queue_messages_control) == 4U,
    "G2 FreeRTOS Queue_t alignment changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_messages_control,
        tasks_waiting_to_send
    ) == 0x10U,
    "G2 FreeRTOS Queue_t send-list offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_messages_control,
        tasks_waiting_to_receive
    ) == 0x24U,
    "G2 FreeRTOS Queue_t receive-list offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_messages_control,
        messages_waiting
    ) == 0x38U,
    "G2 FreeRTOS Queue_t message-count offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_messages_control,
        length
    ) == 0x3CU,
    "G2 FreeRTOS Queue_t length offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_messages_control,
        item_size
    ) == 0x40U,
    "G2 FreeRTOS Queue_t item-size offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_messages_control,
        receive_lock
    ) == 0x44U,
    "G2 FreeRTOS Queue_t receive-lock offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_messages_control,
        transmit_lock
    ) == 0x45U,
    "G2 FreeRTOS Queue_t transmit-lock offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_messages_control,
        statically_allocated
    ) == 0x46U,
    "G2 FreeRTOS Queue_t allocation-marker offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_messages_control,
        queue_number
    ) == 0x48U,
    "G2 FreeRTOS Queue_t trace-number offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_freertos_queue_messages_control,
        queue_type
    ) == 0x4CU,
    "G2 FreeRTOS Queue_t trace-type offset changed"
);
#endif

typedef open_cfw_freertos_queue_messages_ubase_type
(*open_cfw_freertos_queue_messages_assert_mask_fn)(void);
typedef void (*open_cfw_freertos_queue_messages_critical_fn)(void);

#ifndef OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ASSERT_MASK
#define OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ASSERT_MASK() \
    (((open_cfw_freertos_queue_messages_assert_mask_fn) \
        (open_cfw_freertos_queue_messages_uintptr) \
        (OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ASSERT_MASK_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ASSERT
#define OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            (void)OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ASSERT_MASK(); \
            *(volatile open_cfw_freertos_queue_messages_ubase_type *) \
                (open_cfw_freertos_queue_messages_uintptr)-1 = 0U; \
            for (;;) { \
            } \
        } \
    } while (0)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ENTER_CRITICAL
#define OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ENTER_CRITICAL() \
    (((open_cfw_freertos_queue_messages_critical_fn) \
        (open_cfw_freertos_queue_messages_uintptr) \
        (OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ENTER_CRITICAL_ADDRESS | 1U))())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_MESSAGES_EXIT_CRITICAL
#define OPEN_CFW_FREERTOS_QUEUE_MESSAGES_EXIT_CRITICAL() \
    (((open_cfw_freertos_queue_messages_critical_fn) \
        (open_cfw_freertos_queue_messages_uintptr) \
        (OPEN_CFW_FREERTOS_QUEUE_MESSAGES_EXIT_CRITICAL_ADDRESS | 1U))())
#endif

open_cfw_freertos_queue_messages_ubase_type
open_cfw_freertos_queue_messages_waiting(
    const struct open_cfw_freertos_queue_messages_control *queue
);

open_cfw_freertos_queue_messages_ubase_type
open_cfw_freertos_queue_messages_waiting_from_isr(
    const struct open_cfw_freertos_queue_messages_control *queue
);

#endif
