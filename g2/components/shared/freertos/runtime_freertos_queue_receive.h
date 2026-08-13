/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_FREERTOS_QUEUE_RECEIVE_H
#define OPEN_CFW_RUNTIME_FREERTOS_QUEUE_RECEIVE_H

#include "runtime_freertos_queue_next_closure.h"

struct open_cfw_freertos_queue_receive_timeout {
    open_cfw_freertos_queue_next_base_type overflow_count;
    open_cfw_freertos_queue_next_tick_type time_on_entering;
};

enum {
    OPEN_CFW_FREERTOS_QUEUE_RECEIVE_PORT_MAX_DELAY = 0xFFFFFFFFU,
    OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TICK_COUNT_ADDRESS = 0x20074A34U,
    OPEN_CFW_FREERTOS_QUEUE_RECEIVE_DELAYED_LIST_ADDRESS = 0x20074A24U,
    OPEN_CFW_FREERTOS_QUEUE_RECEIVE_OVERFLOW_LIST_ADDRESS = 0x20074A28U,
    OPEN_CFW_FREERTOS_QUEUE_RECEIVE_SUSPENDED_LIST_ADDRESS = 0x20073D4CU,
    OPEN_CFW_FREERTOS_QUEUE_RECEIVE_NEXT_UNBLOCK_ADDRESS = 0x20074A50U
};

#ifndef OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TICK_COUNT_LOAD
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TICK_COUNT_LOAD() \
    (*(volatile open_cfw_freertos_queue_next_tick_type *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TICK_COUNT_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_RECEIVE_DELAYED_LIST_LOAD
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_DELAYED_LIST_LOAD() \
    (*(struct open_cfw_freertos_queue_next_list * volatile *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_RECEIVE_DELAYED_LIST_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_RECEIVE_OVERFLOW_LIST_LOAD
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_OVERFLOW_LIST_LOAD() \
    (*(struct open_cfw_freertos_queue_next_list * volatile *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_RECEIVE_OVERFLOW_LIST_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_RECEIVE_SUSPENDED_LIST
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_SUSPENDED_LIST() \
    ((struct open_cfw_freertos_queue_next_list *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_RECEIVE_SUSPENDED_LIST_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_RECEIVE_NEXT_UNBLOCK_LOAD
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_NEXT_UNBLOCK_LOAD() \
    (*(volatile open_cfw_freertos_queue_next_tick_type *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_RECEIVE_NEXT_UNBLOCK_ADDRESS)
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_RECEIVE_NEXT_UNBLOCK_STORE
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_NEXT_UNBLOCK_STORE(value) \
    (*(volatile open_cfw_freertos_queue_next_tick_type *) \
        (open_cfw_freertos_queue_next_uintptr) \
        OPEN_CFW_FREERTOS_QUEUE_RECEIVE_NEXT_UNBLOCK_ADDRESS = (value))
#endif

#ifndef OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TRACE
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TRACE(queue) do { (void)(queue); } while (0)
#endif
#ifndef OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TRACE_FAILED
#define OPEN_CFW_FREERTOS_QUEUE_RECEIVE_TRACE_FAILED(queue) do { (void)(queue); } while (0)
#endif

void open_cfw_freertos_list_insert(
    struct open_cfw_freertos_queue_next_list *list,
    struct open_cfw_freertos_queue_next_list_item *item
);
open_cfw_freertos_queue_next_ubase_type open_cfw_freertos_list_remove(
    struct open_cfw_freertos_queue_next_list_item *item
);
void open_cfw_freertos_port_enter_critical(void);
void open_cfw_freertos_port_exit_critical(void);
void open_cfw_freertos_task_missed_yield(void);
void open_cfw_freertos_task_internal_set_timeout_state(
    struct open_cfw_freertos_queue_receive_timeout *timeout
);
void open_cfw_freertos_task_suspend_all(void);
open_cfw_freertos_queue_next_base_type
open_cfw_freertos_task_check_for_timeout(
    struct open_cfw_freertos_queue_receive_timeout *timeout,
    open_cfw_freertos_queue_next_tick_type *ticks_to_wait
);
open_cfw_freertos_queue_next_base_type open_cfw_freertos_queue_is_empty(
    const struct open_cfw_freertos_queue_next_control *queue
);
open_cfw_freertos_queue_next_base_type open_cfw_freertos_task_resume_all(void);
void open_cfw_freertos_port_yield(void);
open_cfw_freertos_queue_next_base_type
open_cfw_freertos_task_get_scheduler_state(void);
void open_cfw_freertos_queue_copy_data_from_queue(
    struct open_cfw_freertos_queue_next_control *queue,
    void *buffer
);

void open_cfw_freertos_task_add_current_to_delayed_list(
    open_cfw_freertos_queue_next_tick_type ticks_to_wait,
    open_cfw_freertos_queue_next_base_type can_block_indefinitely
);
void open_cfw_freertos_task_place_on_event_list(
    struct open_cfw_freertos_queue_next_list *event_list,
    open_cfw_freertos_queue_next_tick_type ticks_to_wait
);
void open_cfw_freertos_queue_unlock(
    struct open_cfw_freertos_queue_next_control *queue
);
open_cfw_freertos_queue_next_base_type open_cfw_freertos_queue_receive(
    struct open_cfw_freertos_queue_next_control *queue,
    void *buffer,
    open_cfw_freertos_queue_next_tick_type ticks_to_wait
);

#endif
