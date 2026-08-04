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
 * Bounded, freestanding port of xQueueCreateMutex(),
 * xQueueGiveMutexRecursive(), xQueueTakeMutexRecursive(),
 * xQueueGenericSend(), and xQueueSemaphoreTake() from FreeRTOS-Kernel
 * V10.5.1 queue.c at commit
 * def7d2df2b0506d3d249334974f51e427c17a41c.
 *
 * The recovered G2 configuration has mutexes, preemption, timers, trace
 * metadata, and both allocation modes enabled; queue sets are disabled. The
 * queue empty/full state helpers are source-owned. The remaining private
 * queue, task, list, and port helpers stay as reviewed stock seams and are
 * named explicitly below.
 */

typedef int open_cfw_queue_base_type;
typedef unsigned int open_cfw_queue_ubase_type;
typedef unsigned int open_cfw_queue_tick_type;
typedef unsigned char open_cfw_queue_uint8;

struct open_cfw_queue_list {
    volatile open_cfw_queue_ubase_type item_count;
    unsigned char remainder[16];
};

struct open_cfw_queue_timeout {
    open_cfw_queue_base_type overflow_count;
    open_cfw_queue_tick_type time_on_entering;
};

struct open_cfw_queue_control {
    signed char *head;
    signed char *write_to;
    union {
        struct {
            signed char *tail;
            signed char *read_from;
        } queue;
        struct {
            void *mutex_holder;
            open_cfw_queue_ubase_type recursive_call_count;
        } semaphore;
    } value;
    struct open_cfw_queue_list tasks_waiting_to_send;
    struct open_cfw_queue_list tasks_waiting_to_receive;
    volatile open_cfw_queue_ubase_type messages_waiting;
    open_cfw_queue_ubase_type length;
    open_cfw_queue_ubase_type item_size;
    volatile signed char receive_lock;
    volatile signed char transmit_lock;
    open_cfw_queue_uint8 statically_allocated;
    open_cfw_queue_uint8 allocation_padding;
    open_cfw_queue_ubase_type queue_number;
    open_cfw_queue_uint8 queue_type;
    open_cfw_queue_uint8 trace_padding[3];
};

#if defined(__arm__) && !defined(OPEN_CFW_FREERTOS_QUEUE_SKIP_ABI_ASSERTS)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(struct open_cfw_queue_list) == 20U,
    "FreeRTOS List_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_queue_timeout) == 8U,
    "FreeRTOS TimeOut_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_queue_control) == 0x50U,
    "FreeRTOS Queue_t ABI changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_queue_control, head) == 0x00U,
    "Queue_t head/type offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_control,
        value.semaphore.mutex_holder
    ) == 0x08U,
    "Queue_t mutex-holder offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_control,
        value.semaphore.recursive_call_count
    ) == 0x0CU,
    "Queue_t recursive-count offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_control,
        tasks_waiting_to_send
    ) == 0x10U,
    "Queue_t sender-list offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_control,
        tasks_waiting_to_receive
    ) == 0x24U,
    "Queue_t receiver-list offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_control,
        messages_waiting
    ) == 0x38U,
    "Queue_t message-count offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_queue_control, length) == 0x3CU,
    "Queue_t length offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_queue_control, item_size) == 0x40U,
    "Queue_t item-size offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_control,
        receive_lock
    ) == 0x44U,
    "Queue_t receive-lock offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_control,
        transmit_lock
    ) == 0x45U,
    "Queue_t transmit-lock offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_control,
        statically_allocated
    ) == 0x46U,
    "Queue_t allocation marker offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_queue_control,
        queue_number
    ) == 0x48U,
    "Queue_t trace-number offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_queue_control, queue_type) == 0x4CU,
    "Queue_t trace-type offset changed"
);
#endif

enum {
    OPEN_CFW_QUEUE_FALSE = 0,
    OPEN_CFW_QUEUE_TRUE = 1,
    OPEN_CFW_QUEUE_PASS = 1,
    OPEN_CFW_QUEUE_FULL = 0,
    OPEN_CFW_QUEUE_EMPTY = 0,
    OPEN_CFW_QUEUE_OVERWRITE = 2,
    OPEN_CFW_QUEUE_SCHEDULER_SUSPENDED = 0
};

#ifndef OPEN_CFW_FREERTOS_QUEUE_ASSERT
typedef void (*open_cfw_queue_assert_fail_fn)(void);
#define OPEN_CFW_FREERTOS_QUEUE_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            ((open_cfw_queue_assert_fail_fn) \
                (__UINTPTR_TYPE__)0x005FA0A5U)(); \
            *(volatile unsigned int *)(__UINTPTR_TYPE__)0xFFFFFFFFU = 0U; \
            for (;;) { \
                __asm__ volatile("" ::: "memory"); \
            } \
        } \
    } while (0)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_GENERIC_CREATE
typedef struct open_cfw_queue_control *
(*open_cfw_queue_generic_create_fn)(
    open_cfw_queue_ubase_type length,
    open_cfw_queue_ubase_type item_size,
    open_cfw_queue_uint8 queue_type
);
#define OPEN_CFW_FREERTOS_QUEUE_GENERIC_CREATE( \
    length, \
    item_size, \
    queue_type \
) \
    (((open_cfw_queue_generic_create_fn) \
        (__UINTPTR_TYPE__)0x00441637U)( \
            (length), \
            (item_size), \
            (queue_type) \
        ))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_INITIALISE_MUTEX
typedef void (*open_cfw_queue_initialise_mutex_fn)(
    struct open_cfw_queue_control *queue
);
#define OPEN_CFW_FREERTOS_QUEUE_INITIALISE_MUTEX(queue) \
    (((open_cfw_queue_initialise_mutex_fn) \
        (__UINTPTR_TYPE__)0x004416B9U)((queue)))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_SCHEDULER_STATE
typedef open_cfw_queue_base_type
(*open_cfw_queue_scheduler_state_fn)(void);
#define OPEN_CFW_FREERTOS_QUEUE_SCHEDULER_STATE() \
    (((open_cfw_queue_scheduler_state_fn) \
        (__UINTPTR_TYPE__)0x004558A5U)())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_CURRENT_TASK
typedef void *(*open_cfw_queue_current_task_fn)(void);
#define OPEN_CFW_FREERTOS_QUEUE_CURRENT_TASK() \
    (((open_cfw_queue_current_task_fn) \
        (__UINTPTR_TYPE__)0x0045589DU)())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_ENTER_CRITICAL
typedef void (*open_cfw_queue_enter_critical_fn)(void);
#define OPEN_CFW_FREERTOS_QUEUE_ENTER_CRITICAL() \
    (((open_cfw_queue_enter_critical_fn) \
        (__UINTPTR_TYPE__)0x004420D1U)())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_EXIT_CRITICAL
typedef void (*open_cfw_queue_exit_critical_fn)(void);
#define OPEN_CFW_FREERTOS_QUEUE_EXIT_CRITICAL() \
    (((open_cfw_queue_exit_critical_fn) \
        (__UINTPTR_TYPE__)0x004420E9U)())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_COPY_DATA
typedef open_cfw_queue_base_type
(*open_cfw_queue_copy_data_fn)(
    struct open_cfw_queue_control *queue,
    const void *item,
    open_cfw_queue_base_type position
);
#define OPEN_CFW_FREERTOS_QUEUE_COPY_DATA(queue, item, position) \
    (((open_cfw_queue_copy_data_fn) \
        (__UINTPTR_TYPE__)0x00441ED9U)((queue), (item), (position)))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_REMOVE_EVENT
typedef open_cfw_queue_base_type
(*open_cfw_queue_remove_event_fn)(struct open_cfw_queue_list *list);
#define OPEN_CFW_FREERTOS_QUEUE_REMOVE_EVENT(list) \
    (((open_cfw_queue_remove_event_fn) \
        (__UINTPTR_TYPE__)0x00455371U)((list)))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_YIELD
typedef void (*open_cfw_queue_yield_fn)(void);
#define OPEN_CFW_FREERTOS_QUEUE_YIELD() \
    (((open_cfw_queue_yield_fn)(__UINTPTR_TYPE__)0x004420BDU)())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_SET_TIMEOUT
typedef void (*open_cfw_queue_set_timeout_fn)(
    struct open_cfw_queue_timeout *timeout
);
#define OPEN_CFW_FREERTOS_QUEUE_SET_TIMEOUT(timeout) \
    (((open_cfw_queue_set_timeout_fn) \
        (__UINTPTR_TYPE__)0x00455557U)((timeout)))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_SUSPEND_ALL
typedef void (*open_cfw_queue_suspend_all_fn)(void);
#define OPEN_CFW_FREERTOS_QUEUE_SUSPEND_ALL() \
    (((open_cfw_queue_suspend_all_fn) \
        (__UINTPTR_TYPE__)0x00454D7DU)())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_CHECK_TIMEOUT
typedef open_cfw_queue_base_type
(*open_cfw_queue_check_timeout_fn)(
    struct open_cfw_queue_timeout *timeout,
    open_cfw_queue_tick_type *ticks_to_wait
);
#define OPEN_CFW_FREERTOS_QUEUE_CHECK_TIMEOUT(timeout, ticks_to_wait) \
    (((open_cfw_queue_check_timeout_fn) \
        (__UINTPTR_TYPE__)0x00455567U)((timeout), (ticks_to_wait)))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_IS_FULL
extern open_cfw_queue_base_type open_cfw_freertos_queue_is_full(
    const void *queue
);
#define OPEN_CFW_FREERTOS_QUEUE_IS_FULL(queue) \
    open_cfw_freertos_queue_is_full((queue))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_PLACE_ON_EVENT
typedef void (*open_cfw_queue_place_on_event_fn)(
    struct open_cfw_queue_list *list,
    open_cfw_queue_tick_type ticks_to_wait
);
#define OPEN_CFW_FREERTOS_QUEUE_PLACE_ON_EVENT(list, ticks_to_wait) \
    (((open_cfw_queue_place_on_event_fn) \
        (__UINTPTR_TYPE__)0x00455283U)((list), (ticks_to_wait)))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_UNLOCK
typedef void (*open_cfw_queue_unlock_fn)(
    struct open_cfw_queue_control *queue
);
#define OPEN_CFW_FREERTOS_QUEUE_UNLOCK(queue) \
    (((open_cfw_queue_unlock_fn) \
        (__UINTPTR_TYPE__)0x00441F89U)((queue)))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_RESUME_ALL
typedef open_cfw_queue_base_type
(*open_cfw_queue_resume_all_fn)(void);
#define OPEN_CFW_FREERTOS_QUEUE_RESUME_ALL() \
    (((open_cfw_queue_resume_all_fn) \
        (__UINTPTR_TYPE__)0x00454DCDU)())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_IS_EMPTY
extern open_cfw_queue_base_type open_cfw_freertos_queue_is_empty(
    const void *queue
);
#define OPEN_CFW_FREERTOS_QUEUE_IS_EMPTY(queue) \
    open_cfw_freertos_queue_is_empty((queue))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_INCREMENT_MUTEX_HELD
typedef void *(*open_cfw_queue_increment_mutex_held_fn)(void);
#define OPEN_CFW_FREERTOS_QUEUE_INCREMENT_MUTEX_HELD() \
    (((open_cfw_queue_increment_mutex_held_fn) \
        (__UINTPTR_TYPE__)0x00455AE1U)())
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_PRIORITY_INHERIT
typedef open_cfw_queue_base_type
(*open_cfw_queue_priority_inherit_fn)(void *mutex_holder);
#define OPEN_CFW_FREERTOS_QUEUE_PRIORITY_INHERIT(mutex_holder) \
    (((open_cfw_queue_priority_inherit_fn) \
        (__UINTPTR_TYPE__)0x004558CDU)((mutex_holder)))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_DISINHERIT_PRIORITY
typedef open_cfw_queue_ubase_type
(*open_cfw_queue_disinherit_priority_fn)(
    const struct open_cfw_queue_control *queue
);
#define OPEN_CFW_FREERTOS_QUEUE_DISINHERIT_PRIORITY(queue) \
    (((open_cfw_queue_disinherit_priority_fn) \
        (__UINTPTR_TYPE__)0x00441EC5U)((queue)))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_DISINHERIT_AFTER_TIMEOUT
typedef void (*open_cfw_queue_disinherit_after_timeout_fn)(
    void *mutex_holder,
    open_cfw_queue_ubase_type highest_waiting_priority
);
#define OPEN_CFW_FREERTOS_QUEUE_DISINHERIT_AFTER_TIMEOUT( \
    mutex_holder, \
    highest_waiting_priority \
) \
    (((open_cfw_queue_disinherit_after_timeout_fn) \
        (__UINTPTR_TYPE__)0x00455A1DU)( \
            (mutex_holder), \
            (highest_waiting_priority) \
        ))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_SEMAPHORE_TAKE
#if defined(OPEN_CFW_FREERTOS_QUEUE_INCLUDE_LEGACY_SEMAPHORE_TAKE)
open_cfw_queue_base_type open_cfw_freertos_queue_semaphore_take(
    struct open_cfw_queue_control *queue,
    open_cfw_queue_tick_type ticks_to_wait
);
#define OPEN_CFW_FREERTOS_QUEUE_SEMAPHORE_TAKE(queue, ticks_to_wait) \
    open_cfw_freertos_queue_semaphore_take((queue), (ticks_to_wait))
#else
typedef open_cfw_queue_base_type
(*open_cfw_queue_semaphore_take_fn)(
    struct open_cfw_queue_control *queue,
    open_cfw_queue_tick_type ticks_to_wait
);
#define OPEN_CFW_FREERTOS_QUEUE_SEMAPHORE_TAKE(queue, ticks_to_wait) \
    (((open_cfw_queue_semaphore_take_fn) \
        (__UINTPTR_TYPE__)0x00441C45U)((queue), (ticks_to_wait)))
#endif
#endif

#define OPEN_CFW_FREERTOS_QUEUE_LIST_IS_EMPTY(list) \
    ((list)->item_count == 0U)

static void open_cfw_freertos_queue_lock(
    struct open_cfw_queue_control *queue
)
{
    OPEN_CFW_FREERTOS_QUEUE_ENTER_CRITICAL();
    if (queue->receive_lock == (signed char)-1) {
        queue->receive_lock = (signed char)0;
    }
    if (queue->transmit_lock == (signed char)-1) {
        queue->transmit_lock = (signed char)0;
    }
    OPEN_CFW_FREERTOS_QUEUE_EXIT_CRITICAL();
}

__attribute__((used, noinline))
struct open_cfw_queue_control *open_cfw_freertos_queue_create_mutex(
    const open_cfw_queue_uint8 queue_type
)
{
    struct open_cfw_queue_control *new_queue;

    new_queue = OPEN_CFW_FREERTOS_QUEUE_GENERIC_CREATE(
        1U,
        0U,
        queue_type
    );
    OPEN_CFW_FREERTOS_QUEUE_INITIALISE_MUTEX(new_queue);
    return new_queue;
}

__attribute__((used, noinline))
open_cfw_queue_base_type open_cfw_freertos_queue_generic_send(
    struct open_cfw_queue_control *queue,
    const void *item,
    open_cfw_queue_tick_type ticks_to_wait,
    const open_cfw_queue_base_type copy_position
)
{
    open_cfw_queue_base_type entry_time_set = OPEN_CFW_QUEUE_FALSE;
    open_cfw_queue_base_type yield_required;
    struct open_cfw_queue_timeout timeout;

    OPEN_CFW_FREERTOS_QUEUE_ASSERT(queue != 0);
    OPEN_CFW_FREERTOS_QUEUE_ASSERT(
        !((item == 0) && (queue->item_size != 0U))
    );
    OPEN_CFW_FREERTOS_QUEUE_ASSERT(
        !((copy_position == OPEN_CFW_QUEUE_OVERWRITE) &&
          (queue->length != 1U))
    );
    OPEN_CFW_FREERTOS_QUEUE_ASSERT(
        !((OPEN_CFW_FREERTOS_QUEUE_SCHEDULER_STATE() ==
           OPEN_CFW_QUEUE_SCHEDULER_SUSPENDED) &&
          (ticks_to_wait != 0U))
    );

    for (;;) {
        OPEN_CFW_FREERTOS_QUEUE_ENTER_CRITICAL();
        if (
            (queue->messages_waiting < queue->length) ||
            (copy_position == OPEN_CFW_QUEUE_OVERWRITE)
        ) {
            yield_required = OPEN_CFW_FREERTOS_QUEUE_COPY_DATA(
                queue,
                item,
                copy_position
            );

            if (
                !OPEN_CFW_FREERTOS_QUEUE_LIST_IS_EMPTY(
                    &queue->tasks_waiting_to_receive
                )
            ) {
                if (
                    OPEN_CFW_FREERTOS_QUEUE_REMOVE_EVENT(
                        &queue->tasks_waiting_to_receive
                    ) != OPEN_CFW_QUEUE_FALSE
                ) {
                    OPEN_CFW_FREERTOS_QUEUE_YIELD();
                }
            } else if (yield_required != OPEN_CFW_QUEUE_FALSE) {
                OPEN_CFW_FREERTOS_QUEUE_YIELD();
            }

            OPEN_CFW_FREERTOS_QUEUE_EXIT_CRITICAL();
            return OPEN_CFW_QUEUE_PASS;
        }

        if (ticks_to_wait == 0U) {
            OPEN_CFW_FREERTOS_QUEUE_EXIT_CRITICAL();
            return OPEN_CFW_QUEUE_FULL;
        }

        if (entry_time_set == OPEN_CFW_QUEUE_FALSE) {
            OPEN_CFW_FREERTOS_QUEUE_SET_TIMEOUT(&timeout);
            entry_time_set = OPEN_CFW_QUEUE_TRUE;
        }
        OPEN_CFW_FREERTOS_QUEUE_EXIT_CRITICAL();

        OPEN_CFW_FREERTOS_QUEUE_SUSPEND_ALL();
        open_cfw_freertos_queue_lock(queue);

        if (
            OPEN_CFW_FREERTOS_QUEUE_CHECK_TIMEOUT(
                &timeout,
                &ticks_to_wait
            ) == OPEN_CFW_QUEUE_FALSE
        ) {
            if (
                OPEN_CFW_FREERTOS_QUEUE_IS_FULL(queue) !=
                OPEN_CFW_QUEUE_FALSE
            ) {
                OPEN_CFW_FREERTOS_QUEUE_PLACE_ON_EVENT(
                    &queue->tasks_waiting_to_send,
                    ticks_to_wait
                );
                OPEN_CFW_FREERTOS_QUEUE_UNLOCK(queue);
                if (
                    OPEN_CFW_FREERTOS_QUEUE_RESUME_ALL() ==
                    OPEN_CFW_QUEUE_FALSE
                ) {
                    OPEN_CFW_FREERTOS_QUEUE_YIELD();
                }
            } else {
                OPEN_CFW_FREERTOS_QUEUE_UNLOCK(queue);
                (void)OPEN_CFW_FREERTOS_QUEUE_RESUME_ALL();
            }
        } else {
            OPEN_CFW_FREERTOS_QUEUE_UNLOCK(queue);
            (void)OPEN_CFW_FREERTOS_QUEUE_RESUME_ALL();
            return OPEN_CFW_QUEUE_FULL;
        }
    }
}

#if defined(OPEN_CFW_FREERTOS_QUEUE_INCLUDE_LEGACY_SEMAPHORE_TAKE)
__attribute__((used, noinline))
open_cfw_queue_base_type open_cfw_freertos_queue_semaphore_take(
    struct open_cfw_queue_control *queue,
    open_cfw_queue_tick_type ticks_to_wait
)
{
    open_cfw_queue_base_type entry_time_set = OPEN_CFW_QUEUE_FALSE;
    open_cfw_queue_base_type inheritance_occurred = OPEN_CFW_QUEUE_FALSE;
    struct open_cfw_queue_timeout timeout;

    OPEN_CFW_FREERTOS_QUEUE_ASSERT(queue != 0);
    OPEN_CFW_FREERTOS_QUEUE_ASSERT(queue->item_size == 0U);
    OPEN_CFW_FREERTOS_QUEUE_ASSERT(
        !((OPEN_CFW_FREERTOS_QUEUE_SCHEDULER_STATE() ==
           OPEN_CFW_QUEUE_SCHEDULER_SUSPENDED) &&
          (ticks_to_wait != 0U))
    );

    for (;;) {
        open_cfw_queue_ubase_type semaphore_count;

        OPEN_CFW_FREERTOS_QUEUE_ENTER_CRITICAL();
        semaphore_count = queue->messages_waiting;
        if (semaphore_count > 0U) {
            queue->messages_waiting = semaphore_count - 1U;
            if (queue->head == 0) {
                queue->value.semaphore.mutex_holder =
                    OPEN_CFW_FREERTOS_QUEUE_INCREMENT_MUTEX_HELD();
            }

            if (
                !OPEN_CFW_FREERTOS_QUEUE_LIST_IS_EMPTY(
                    &queue->tasks_waiting_to_send
                ) &&
                (OPEN_CFW_FREERTOS_QUEUE_REMOVE_EVENT(
                    &queue->tasks_waiting_to_send
                ) != OPEN_CFW_QUEUE_FALSE)
            ) {
                OPEN_CFW_FREERTOS_QUEUE_YIELD();
            }

            OPEN_CFW_FREERTOS_QUEUE_EXIT_CRITICAL();
            return OPEN_CFW_QUEUE_PASS;
        }

        if (ticks_to_wait == 0U) {
            OPEN_CFW_FREERTOS_QUEUE_EXIT_CRITICAL();
            return OPEN_CFW_QUEUE_EMPTY;
        }

        if (entry_time_set == OPEN_CFW_QUEUE_FALSE) {
            OPEN_CFW_FREERTOS_QUEUE_SET_TIMEOUT(&timeout);
            entry_time_set = OPEN_CFW_QUEUE_TRUE;
        }
        OPEN_CFW_FREERTOS_QUEUE_EXIT_CRITICAL();

        OPEN_CFW_FREERTOS_QUEUE_SUSPEND_ALL();
        open_cfw_freertos_queue_lock(queue);

        if (
            OPEN_CFW_FREERTOS_QUEUE_CHECK_TIMEOUT(
                &timeout,
                &ticks_to_wait
            ) == OPEN_CFW_QUEUE_FALSE
        ) {
            if (
                OPEN_CFW_FREERTOS_QUEUE_IS_EMPTY(queue) !=
                OPEN_CFW_QUEUE_FALSE
            ) {
                if (queue->head == 0) {
                    OPEN_CFW_FREERTOS_QUEUE_ENTER_CRITICAL();
                    inheritance_occurred =
                        OPEN_CFW_FREERTOS_QUEUE_PRIORITY_INHERIT(
                            queue->value.semaphore.mutex_holder
                        );
                    OPEN_CFW_FREERTOS_QUEUE_EXIT_CRITICAL();
                }

                OPEN_CFW_FREERTOS_QUEUE_PLACE_ON_EVENT(
                    &queue->tasks_waiting_to_receive,
                    ticks_to_wait
                );
                OPEN_CFW_FREERTOS_QUEUE_UNLOCK(queue);
                if (
                    OPEN_CFW_FREERTOS_QUEUE_RESUME_ALL() ==
                    OPEN_CFW_QUEUE_FALSE
                ) {
                    OPEN_CFW_FREERTOS_QUEUE_YIELD();
                }
            } else {
                OPEN_CFW_FREERTOS_QUEUE_UNLOCK(queue);
                (void)OPEN_CFW_FREERTOS_QUEUE_RESUME_ALL();
            }
        } else {
            OPEN_CFW_FREERTOS_QUEUE_UNLOCK(queue);
            (void)OPEN_CFW_FREERTOS_QUEUE_RESUME_ALL();

            if (
                OPEN_CFW_FREERTOS_QUEUE_IS_EMPTY(queue) !=
                OPEN_CFW_QUEUE_FALSE
            ) {
                if (inheritance_occurred != OPEN_CFW_QUEUE_FALSE) {
                    open_cfw_queue_ubase_type highest_waiting_priority;

                    OPEN_CFW_FREERTOS_QUEUE_ENTER_CRITICAL();
                    highest_waiting_priority =
                        OPEN_CFW_FREERTOS_QUEUE_DISINHERIT_PRIORITY(
                            queue
                        );
                    OPEN_CFW_FREERTOS_QUEUE_DISINHERIT_AFTER_TIMEOUT(
                        queue->value.semaphore.mutex_holder,
                        highest_waiting_priority
                    );
                    OPEN_CFW_FREERTOS_QUEUE_EXIT_CRITICAL();
                }
                return OPEN_CFW_QUEUE_EMPTY;
            }

        }
    }
}
#endif

__attribute__((used, noinline))
open_cfw_queue_base_type open_cfw_freertos_queue_give_mutex_recursive(
    struct open_cfw_queue_control *mutex
)
{
    open_cfw_queue_base_type result;

    OPEN_CFW_FREERTOS_QUEUE_ASSERT(mutex != 0);
    if (
        mutex->value.semaphore.mutex_holder ==
        OPEN_CFW_FREERTOS_QUEUE_CURRENT_TASK()
    ) {
        mutex->value.semaphore.recursive_call_count--;
        if (mutex->value.semaphore.recursive_call_count == 0U) {
            (void)open_cfw_freertos_queue_generic_send(
                mutex,
                0,
                0U,
                0
            );
        }
        result = OPEN_CFW_QUEUE_PASS;
    } else {
        result = OPEN_CFW_QUEUE_FALSE;
    }

    return result;
}

__attribute__((used, noinline))
open_cfw_queue_base_type open_cfw_freertos_queue_take_mutex_recursive(
    struct open_cfw_queue_control *mutex,
    open_cfw_queue_tick_type ticks_to_wait
)
{
    open_cfw_queue_base_type result;

    OPEN_CFW_FREERTOS_QUEUE_ASSERT(mutex != 0);
    if (
        mutex->value.semaphore.mutex_holder ==
        OPEN_CFW_FREERTOS_QUEUE_CURRENT_TASK()
    ) {
        mutex->value.semaphore.recursive_call_count++;
        result = OPEN_CFW_QUEUE_PASS;
    } else {
        result = OPEN_CFW_FREERTOS_QUEUE_SEMAPHORE_TAKE(
            mutex,
            ticks_to_wait
        );
        if (result != OPEN_CFW_QUEUE_FALSE) {
            mutex->value.semaphore.recursive_call_count++;
        }
    }

    return result;
}
