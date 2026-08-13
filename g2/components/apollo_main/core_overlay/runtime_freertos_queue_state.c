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
 * Bounded, freestanding port of prvIsQueueEmpty() and prvIsQueueFull() from
 * FreeRTOS-Kernel V10.5.1 queue.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The official G2 image places the private helpers at 0x00441FF6 and
 * 0x00442012.  Both helpers sample Queue_t while holding the task critical
 * section.  Their callers have already validated the queue handle, so these
 * private helpers deliberately do not add a configASSERT.
 */

typedef int open_cfw_queue_state_base_type;
typedef unsigned int open_cfw_queue_state_ubase_type;
typedef unsigned char open_cfw_queue_state_uint8;

struct open_cfw_queue_state_list {
    volatile open_cfw_queue_state_ubase_type item_count;
    unsigned char remainder[16];
};

struct open_cfw_queue_state_control {
    signed char *head;
    signed char *write_to;
    union {
        struct {
            signed char *tail;
            signed char *read_from;
        } queue;
        struct {
            void *mutex_holder;
            open_cfw_queue_state_ubase_type recursive_call_count;
        } semaphore;
    } value;
    struct open_cfw_queue_state_list tasks_waiting_to_send;
    struct open_cfw_queue_state_list tasks_waiting_to_receive;
    volatile open_cfw_queue_state_ubase_type messages_waiting;
    open_cfw_queue_state_ubase_type length;
    open_cfw_queue_state_ubase_type item_size;
    volatile signed char receive_lock;
    volatile signed char transmit_lock;
    open_cfw_queue_state_uint8 statically_allocated;
    open_cfw_queue_state_uint8 allocation_padding;
    open_cfw_queue_state_ubase_type queue_number;
    open_cfw_queue_state_uint8 queue_type;
    open_cfw_queue_state_uint8 trace_padding[3];
};

#if defined(__arm__) && \
    !defined(OPEN_CFW_FREERTOS_QUEUE_STATE_SKIP_ABI_ASSERTS)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(struct open_cfw_queue_state_list) == 20U,
    "FreeRTOS List_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_queue_state_control) == 0x50U,
    "FreeRTOS Queue_t ABI changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_state_control,
        messages_waiting
    ) == 0x38U,
    "Queue_t message-count offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_queue_state_control, length) ==
        0x3CU,
    "Queue_t length offset changed"
);
#endif

enum {
    OPEN_CFW_QUEUE_STATE_FALSE = 0,
    OPEN_CFW_QUEUE_STATE_TRUE = 1
};

#ifndef OPEN_CFW_FREERTOS_QUEUE_STATE_ENTER_CRITICAL
typedef void (*open_cfw_queue_state_enter_critical_fn)(void);
#define OPEN_CFW_FREERTOS_QUEUE_STATE_ENTER_CRITICAL() \
    (((open_cfw_queue_state_enter_critical_fn) \
        (__UINTPTR_TYPE__)0x004420D1U)())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_STATE_EXIT_CRITICAL
typedef void (*open_cfw_queue_state_exit_critical_fn)(void);
#define OPEN_CFW_FREERTOS_QUEUE_STATE_EXIT_CRITICAL() \
    (((open_cfw_queue_state_exit_critical_fn) \
        (__UINTPTR_TYPE__)0x004420E9U)())
#endif

__attribute__((used, noinline))
open_cfw_queue_state_base_type open_cfw_freertos_queue_is_empty(
    const void *queue_handle
)
{
    const struct open_cfw_queue_state_control *queue = queue_handle;
    open_cfw_queue_state_base_type result;

    OPEN_CFW_FREERTOS_QUEUE_STATE_ENTER_CRITICAL();
    if (queue->messages_waiting == 0U) {
        result = OPEN_CFW_QUEUE_STATE_TRUE;
    } else {
        result = OPEN_CFW_QUEUE_STATE_FALSE;
    }
    OPEN_CFW_FREERTOS_QUEUE_STATE_EXIT_CRITICAL();

    return result;
}

__attribute__((used, noinline))
open_cfw_queue_state_base_type open_cfw_freertos_queue_is_full(
    const void *queue_handle
)
{
    const struct open_cfw_queue_state_control *queue = queue_handle;
    open_cfw_queue_state_base_type result;

    OPEN_CFW_FREERTOS_QUEUE_STATE_ENTER_CRITICAL();
    if (queue->messages_waiting == queue->length) {
        result = OPEN_CFW_QUEUE_STATE_TRUE;
    } else {
        result = OPEN_CFW_QUEUE_STATE_FALSE;
    }
    OPEN_CFW_FREERTOS_QUEUE_STATE_EXIT_CRITICAL();

    return result;
}
