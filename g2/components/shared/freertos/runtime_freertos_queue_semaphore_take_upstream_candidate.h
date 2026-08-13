/*
 * FreeRTOS Kernel V10.5.1
 * Copyright (C) 2021 Amazon.com, Inc. or its affiliates.
 *
 * SPDX-License-Identifier: MIT
 *
 * Recovered production G2 ABI for xQueueSemaphoreTake().  The historical
 * candidate filename is retained so the qualification fixtures stay stable.
 */

#ifndef OPEN_CFW_FREERTOS_QUEUE_SEMAPHORE_TAKE_UPSTREAM_CANDIDATE_H
#define OPEN_CFW_FREERTOS_QUEUE_SEMAPHORE_TAKE_UPSTREAM_CANDIDATE_H

typedef int open_cfw_semaphore_take_base_type;
typedef unsigned int open_cfw_semaphore_take_ubase_type;
typedef unsigned int open_cfw_semaphore_take_tick_type;
typedef unsigned char open_cfw_semaphore_take_uint8;

struct open_cfw_semaphore_take_list {
    volatile open_cfw_semaphore_take_ubase_type item_count;
    unsigned char remainder[16];
};

struct open_cfw_semaphore_take_timeout {
    open_cfw_semaphore_take_base_type overflow_count;
    open_cfw_semaphore_take_tick_type time_on_entering;
};

struct open_cfw_semaphore_take_queue {
    signed char *head;
    signed char *write_to;
    union {
        struct {
            signed char *tail;
            signed char *read_from;
        } queue;
        struct {
            void *mutex_holder;
            open_cfw_semaphore_take_ubase_type recursive_call_count;
        } semaphore;
    } value;
    struct open_cfw_semaphore_take_list tasks_waiting_to_send;
    struct open_cfw_semaphore_take_list tasks_waiting_to_receive;
    volatile open_cfw_semaphore_take_ubase_type messages_waiting;
    open_cfw_semaphore_take_ubase_type length;
    open_cfw_semaphore_take_ubase_type item_size;
    volatile signed char receive_lock;
    volatile signed char transmit_lock;
    open_cfw_semaphore_take_uint8 statically_allocated;
    open_cfw_semaphore_take_uint8 allocation_padding;
    open_cfw_semaphore_take_ubase_type queue_number;
    open_cfw_semaphore_take_uint8 queue_type;
    open_cfw_semaphore_take_uint8 trace_padding[3];
};

#if defined(__arm__) && \
    !defined(OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_SKIP_ABI_ASSERTS)
_Static_assert(sizeof(void *) == 4U, "Apollo510 requires 32-bit pointers");
_Static_assert(
    sizeof(struct open_cfw_semaphore_take_list) == 20U,
    "FreeRTOS List_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_semaphore_take_timeout) == 8U,
    "FreeRTOS TimeOut_t ABI changed"
);
_Static_assert(
    sizeof(struct open_cfw_semaphore_take_queue) == 0x50U,
    "FreeRTOS Queue_t ABI changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_semaphore_take_queue, head) ==
        0x00U,
    "Queue_t pcHead/uxQueueType offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_semaphore_take_queue,
        value.semaphore.mutex_holder
    ) == 0x08U,
    "Queue_t mutex-holder offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_semaphore_take_queue,
        tasks_waiting_to_send
    ) == 0x10U,
    "Queue_t sender-list offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_semaphore_take_queue,
        tasks_waiting_to_receive
    ) == 0x24U,
    "Queue_t receiver-list offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_semaphore_take_queue,
        messages_waiting
    ) == 0x38U,
    "Queue_t message-count offset changed"
);
_Static_assert(
    __builtin_offsetof(struct open_cfw_semaphore_take_queue, item_size) ==
        0x40U,
    "Queue_t item-size offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_semaphore_take_queue,
        receive_lock
    ) == 0x44U,
    "Queue_t receive-lock offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_semaphore_take_queue,
        transmit_lock
    ) == 0x45U,
    "Queue_t transmit-lock offset changed"
);
#endif

enum {
    OPEN_CFW_SEMAPHORE_TAKE_FALSE = 0,
    OPEN_CFW_SEMAPHORE_TAKE_TRUE = 1,
    OPEN_CFW_SEMAPHORE_TAKE_PASS = 1,
    OPEN_CFW_SEMAPHORE_TAKE_EMPTY = 0,
    OPEN_CFW_SEMAPHORE_TAKE_SCHEDULER_SUSPENDED = 0,
    OPEN_CFW_SEMAPHORE_TAKE_QUEUE_UNLOCKED = -1
};

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_ASSERT
typedef void (*open_cfw_semaphore_take_assert_fail_fn)(void);
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_ASSERT(condition) \
    do { \
        if (!(condition)) { \
            ((open_cfw_semaphore_take_assert_fail_fn) \
                (__UINTPTR_TYPE__)0x005FA0A5U)(); \
            *(volatile unsigned int *)(__UINTPTR_TYPE__)0xFFFFFFFFU = 0U; \
            for (;;) { \
                __asm__ volatile("" ::: "memory"); \
            } \
        } \
    } while (0)
#endif

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_SCHEDULER_STATE
typedef open_cfw_semaphore_take_base_type
(*open_cfw_semaphore_take_scheduler_state_fn)(void);
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_SCHEDULER_STATE() \
    (((open_cfw_semaphore_take_scheduler_state_fn) \
        (__UINTPTR_TYPE__)0x004558A5U)())
#endif

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_ENTER_CRITICAL
typedef void (*open_cfw_semaphore_take_enter_critical_fn)(void);
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_ENTER_CRITICAL() \
    (((open_cfw_semaphore_take_enter_critical_fn) \
        (__UINTPTR_TYPE__)0x004420D1U)())
#endif

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_EXIT_CRITICAL
typedef void (*open_cfw_semaphore_take_exit_critical_fn)(void);
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_EXIT_CRITICAL() \
    (((open_cfw_semaphore_take_exit_critical_fn) \
        (__UINTPTR_TYPE__)0x004420E9U)())
#endif

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_REMOVE_EVENT
typedef open_cfw_semaphore_take_base_type
(*open_cfw_semaphore_take_remove_event_fn)(
    struct open_cfw_semaphore_take_list *list
);
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_REMOVE_EVENT(list) \
    (((open_cfw_semaphore_take_remove_event_fn) \
        (__UINTPTR_TYPE__)0x00455371U)((list)))
#endif

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_YIELD
typedef void (*open_cfw_semaphore_take_yield_fn)(void);
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_YIELD() \
    (((open_cfw_semaphore_take_yield_fn) \
        (__UINTPTR_TYPE__)0x004420BDU)())
#endif

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_SET_TIMEOUT
typedef void (*open_cfw_semaphore_take_set_timeout_fn)(
    struct open_cfw_semaphore_take_timeout *timeout
);
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_SET_TIMEOUT(timeout) \
    (((open_cfw_semaphore_take_set_timeout_fn) \
        (__UINTPTR_TYPE__)0x00455557U)((timeout)))
#endif

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_SUSPEND_ALL
typedef void (*open_cfw_semaphore_take_suspend_all_fn)(void);
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_SUSPEND_ALL() \
    (((open_cfw_semaphore_take_suspend_all_fn) \
        (__UINTPTR_TYPE__)0x00454D7DU)())
#endif

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_CHECK_TIMEOUT
typedef open_cfw_semaphore_take_base_type
(*open_cfw_semaphore_take_check_timeout_fn)(
    struct open_cfw_semaphore_take_timeout *timeout,
    open_cfw_semaphore_take_tick_type *ticks_to_wait
);
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_CHECK_TIMEOUT(timeout, ticks) \
    (((open_cfw_semaphore_take_check_timeout_fn) \
        (__UINTPTR_TYPE__)0x00455567U)((timeout), (ticks)))
#endif

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_IS_EMPTY
typedef open_cfw_semaphore_take_base_type
(*open_cfw_semaphore_take_is_empty_fn)(const void *queue);
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_IS_EMPTY(queue) \
    (((open_cfw_semaphore_take_is_empty_fn) \
        (__UINTPTR_TYPE__)0x00441FF5U)((queue)))
#endif

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_PLACE_ON_EVENT
typedef void (*open_cfw_semaphore_take_place_on_event_fn)(
    struct open_cfw_semaphore_take_list *list,
    open_cfw_semaphore_take_tick_type ticks_to_wait
);
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_PLACE_ON_EVENT(list, ticks) \
    (((open_cfw_semaphore_take_place_on_event_fn) \
        (__UINTPTR_TYPE__)0x00455283U)((list), (ticks)))
#endif

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_UNLOCK
typedef void (*open_cfw_semaphore_take_unlock_fn)(
    struct open_cfw_semaphore_take_queue *queue
);
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_UNLOCK(queue) \
    (((open_cfw_semaphore_take_unlock_fn) \
        (__UINTPTR_TYPE__)0x00441F89U)((queue)))
#endif

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_RESUME_ALL
typedef open_cfw_semaphore_take_base_type
(*open_cfw_semaphore_take_resume_all_fn)(void);
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_RESUME_ALL() \
    (((open_cfw_semaphore_take_resume_all_fn) \
        (__UINTPTR_TYPE__)0x00454DCDU)())
#endif

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_INCREMENT_MUTEX_HELD
typedef void *(*open_cfw_semaphore_take_increment_mutex_held_fn)(void);
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_INCREMENT_MUTEX_HELD() \
    (((open_cfw_semaphore_take_increment_mutex_held_fn) \
        (__UINTPTR_TYPE__)0x00455AE1U)())
#endif

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_PRIORITY_INHERIT
typedef open_cfw_semaphore_take_base_type
(*open_cfw_semaphore_take_priority_inherit_fn)(void *holder);
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_PRIORITY_INHERIT(holder) \
    (((open_cfw_semaphore_take_priority_inherit_fn) \
        (__UINTPTR_TYPE__)0x004558CDU)((holder)))
#endif

open_cfw_semaphore_take_ubase_type
open_cfw_freertos_queue_get_disinherit_priority_after_timeout(
    const void *queue
);

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_DISINHERIT_PRIORITY
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_DISINHERIT_PRIORITY(queue) \
    open_cfw_freertos_queue_get_disinherit_priority_after_timeout((queue))
#endif

#ifndef OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_DISINHERIT_AFTER_TIMEOUT
typedef void (*open_cfw_semaphore_take_disinherit_after_timeout_fn)(
    void *holder,
    open_cfw_semaphore_take_ubase_type priority
);
#define OPEN_CFW_FREERTOS_SEMAPHORE_TAKE_DISINHERIT_AFTER_TIMEOUT( \
    holder, \
    priority \
) \
    (((open_cfw_semaphore_take_disinherit_after_timeout_fn) \
        (__UINTPTR_TYPE__)0x00455A1DU)((holder), (priority)))
#endif

open_cfw_semaphore_take_base_type
open_cfw_freertos_queue_semaphore_take_upstream_candidate(
    struct open_cfw_semaphore_take_queue *queue,
    open_cfw_semaphore_take_tick_type ticks_to_wait
);

#endif
