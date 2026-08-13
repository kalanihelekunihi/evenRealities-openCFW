/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 *
 * SPDX-License-Identifier: MIT
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * Bounded, freestanding port of xQueueGenericCreateStatic(),
 * xQueueGenericCreate(), prvInitialiseNewQueue(), and prvInitialiseMutex()
 * from FreeRTOS-Kernel V10.5.1 queue.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * Focused disassembly establishes the exact G2 Queue_t ABI and configuration.
 * The still-opaque reset, heap_4 allocator, and assertion trap remain explicit
 * compatibility seams. The mutex initializer links directly to the existing
 * source-owned xQueueGenericSend() adaptation.
 */

typedef int open_cfw_queue_create_base_type;
typedef unsigned int open_cfw_queue_create_ubase_type;
typedef unsigned int open_cfw_queue_create_size_type;
typedef unsigned char open_cfw_queue_create_uint8;

struct open_cfw_queue_create_list {
    volatile open_cfw_queue_create_ubase_type item_count;
    unsigned char remainder[16];
};

struct open_cfw_queue_create_control {
    signed char *head;
    signed char *write_to;
    union {
        struct {
            signed char *tail;
            signed char *read_from;
        } queue;
        struct {
            void *mutex_holder;
            open_cfw_queue_create_ubase_type recursive_call_count;
        } semaphore;
    } value;
    struct open_cfw_queue_create_list tasks_waiting_to_send;
    struct open_cfw_queue_create_list tasks_waiting_to_receive;
    volatile open_cfw_queue_create_ubase_type messages_waiting;
    open_cfw_queue_create_ubase_type length;
    open_cfw_queue_create_ubase_type item_size;
    volatile signed char receive_lock;
    volatile signed char transmit_lock;
    open_cfw_queue_create_uint8 statically_allocated;
    open_cfw_queue_create_uint8 allocation_padding;
    open_cfw_queue_create_ubase_type queue_number;
    open_cfw_queue_create_uint8 queue_type;
    open_cfw_queue_create_uint8 trace_padding[3];
};

struct open_cfw_queue_control;

#if defined(__arm__) && \
    !defined(OPEN_CFW_FREERTOS_QUEUE_CREATE_SKIP_ABI_ASSERTS)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(open_cfw_queue_create_size_type) == 4U,
    "G2 FreeRTOS size_t view changed"
);
_Static_assert(
    sizeof(struct open_cfw_queue_create_list) == 0x14U,
    "FreeRTOS List_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_queue_create_control) == 0x50U,
    "FreeRTOS Queue_t ABI changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_queue_create_control, head) == 0x00U,
    "Queue_t head offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_create_control,
        value.semaphore.mutex_holder
    ) == 0x08U,
    "Queue_t mutex-holder offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_create_control,
        value.semaphore.recursive_call_count
    ) == 0x0CU,
    "Queue_t recursive-count offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_create_control,
        tasks_waiting_to_send
    ) == 0x10U,
    "Queue_t sender-list offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_create_control,
        tasks_waiting_to_receive
    ) == 0x24U,
    "Queue_t receiver-list offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_create_control,
        messages_waiting
    ) == 0x38U,
    "Queue_t message-count offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_create_control,
        length
    ) == 0x3CU,
    "Queue_t length offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_create_control,
        item_size
    ) == 0x40U,
    "Queue_t item-size offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_create_control,
        statically_allocated
    ) == 0x46U,
    "Queue_t allocation marker offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_create_control,
        queue_type
    ) == 0x4CU,
    "Queue_t trace-type offset changed"
);
#endif

enum {
    OPEN_CFW_QUEUE_CREATE_FALSE = 0,
    OPEN_CFW_QUEUE_CREATE_TRUE = 1,
    OPEN_CFW_QUEUE_CREATE_SEND_TO_BACK = 0
};

#ifndef OPEN_CFW_FREERTOS_QUEUE_CREATE_ASSERT
typedef void (*open_cfw_queue_create_assert_fail_fn)(void);
#define OPEN_CFW_FREERTOS_QUEUE_CREATE_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            ((open_cfw_queue_create_assert_fail_fn) \
                (__UINTPTR_TYPE__)0x005FA0A5U)(); \
            *(volatile unsigned int *)(__UINTPTR_TYPE__)0xFFFFFFFFU = 0U; \
            for (;;) { \
                __asm__ volatile("" ::: "memory"); \
            } \
        } \
    } while (0)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_CREATE_RESET
typedef open_cfw_queue_create_base_type
(*open_cfw_queue_create_reset_fn)(
    struct open_cfw_queue_create_control *queue,
    open_cfw_queue_create_base_type new_queue
);
#define OPEN_CFW_FREERTOS_QUEUE_CREATE_RESET(queue, new_queue) \
    (((open_cfw_queue_create_reset_fn) \
        (__UINTPTR_TYPE__)0x00441517U)((queue), (new_queue)))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_CREATE_MALLOC
typedef void *(*open_cfw_queue_create_malloc_fn)(
    open_cfw_queue_create_size_type size
);
#define OPEN_CFW_FREERTOS_QUEUE_CREATE_MALLOC(size) \
    (((open_cfw_queue_create_malloc_fn) \
        (__UINTPTR_TYPE__)0x00456111U)((size)))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_CREATE_SEND
extern open_cfw_queue_create_base_type
open_cfw_freertos_queue_generic_send(
    struct open_cfw_queue_control *queue,
    const void *item,
    unsigned int ticks_to_wait,
    const int copy_position
);
#define OPEN_CFW_FREERTOS_QUEUE_CREATE_SEND(queue, item, ticks, position) \
    open_cfw_freertos_queue_generic_send( \
        (struct open_cfw_queue_control *)(queue), \
        (item), \
        (ticks), \
        (position) \
    )
#endif

void open_cfw_freertos_queue_initialise_new(
    open_cfw_queue_create_ubase_type length,
    open_cfw_queue_create_ubase_type item_size,
    unsigned char *storage,
    open_cfw_queue_create_uint8 queue_type,
    struct open_cfw_queue_create_control *queue
);

void open_cfw_freertos_queue_initialise_mutex(
    struct open_cfw_queue_create_control *queue
);

__attribute__((used, noinline))
struct open_cfw_queue_create_control *
open_cfw_freertos_queue_generic_create_static(
    open_cfw_queue_create_ubase_type length,
    open_cfw_queue_create_ubase_type item_size,
    unsigned char *storage,
    struct open_cfw_queue_create_control *static_queue,
    open_cfw_queue_create_uint8 queue_type
)
{
    volatile open_cfw_queue_create_size_type static_queue_size =
        (open_cfw_queue_create_size_type)
        sizeof(struct open_cfw_queue_create_control);

    OPEN_CFW_FREERTOS_QUEUE_CREATE_ASSERT(static_queue != 0);
    OPEN_CFW_FREERTOS_QUEUE_CREATE_ASSERT(length > 0U);
    OPEN_CFW_FREERTOS_QUEUE_CREATE_ASSERT(
        !((storage == 0) && (item_size != 0U))
    );
    OPEN_CFW_FREERTOS_QUEUE_CREATE_ASSERT(
        static_queue_size ==
        (open_cfw_queue_create_size_type)
        sizeof(struct open_cfw_queue_create_control)
    );

    static_queue->statically_allocated = 1U;
    open_cfw_freertos_queue_initialise_new(
        length,
        item_size,
        storage,
        queue_type,
        static_queue
    );
    return static_queue;
}

__attribute__((used, noinline))
struct open_cfw_queue_create_control *
open_cfw_freertos_queue_generic_create(
    open_cfw_queue_create_ubase_type length,
    open_cfw_queue_create_ubase_type item_size,
    open_cfw_queue_create_uint8 queue_type
)
{
    struct open_cfw_queue_create_control *queue;
    open_cfw_queue_create_size_type queue_size;
    unsigned char *storage;

    OPEN_CFW_FREERTOS_QUEUE_CREATE_ASSERT(length > 0U);
    OPEN_CFW_FREERTOS_QUEUE_CREATE_ASSERT(
        (((open_cfw_queue_create_size_type)0xFFFFFFFFU / length) >=
         item_size)
    );
    queue_size = length * item_size;
    OPEN_CFW_FREERTOS_QUEUE_CREATE_ASSERT(
        (queue_size +
         (open_cfw_queue_create_size_type)
         sizeof(struct open_cfw_queue_create_control)) > queue_size
    );

    queue = (struct open_cfw_queue_create_control *)
        OPEN_CFW_FREERTOS_QUEUE_CREATE_MALLOC(
            queue_size +
            (open_cfw_queue_create_size_type)
            sizeof(struct open_cfw_queue_create_control)
        );
    if (queue != 0) {
        storage = (unsigned char *)queue +
            sizeof(struct open_cfw_queue_create_control);
        queue->statically_allocated = 0U;
        open_cfw_freertos_queue_initialise_new(
            length,
            item_size,
            storage,
            queue_type,
            queue
        );
    }
    return queue;
}

__attribute__((used, noinline))
void open_cfw_freertos_queue_initialise_new(
    open_cfw_queue_create_ubase_type length,
    open_cfw_queue_create_ubase_type item_size,
    unsigned char *storage,
    open_cfw_queue_create_uint8 queue_type,
    struct open_cfw_queue_create_control *queue
)
{
    if (item_size == 0U) {
        queue->head = (signed char *)queue;
    } else {
        queue->head = (signed char *)storage;
    }
    queue->length = length;
    queue->item_size = item_size;
    (void)OPEN_CFW_FREERTOS_QUEUE_CREATE_RESET(
        queue,
        OPEN_CFW_QUEUE_CREATE_TRUE
    );
    queue->queue_type = queue_type;
}

__attribute__((used, noinline))
void open_cfw_freertos_queue_initialise_mutex(
    struct open_cfw_queue_create_control *queue
)
{
    if (queue != 0) {
        queue->value.semaphore.mutex_holder = 0;
        queue->head = 0;
        queue->value.semaphore.recursive_call_count = 0U;
        (void)OPEN_CFW_FREERTOS_QUEUE_CREATE_SEND(
            queue,
            0,
            0U,
            OPEN_CFW_QUEUE_CREATE_SEND_TO_BACK
        );
    }
}
