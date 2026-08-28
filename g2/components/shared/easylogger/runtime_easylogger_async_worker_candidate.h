/*
 * SPDX-License-Identifier: MIT
 *
 * Production-excluded clean-room candidate for the G2 EasyLogger downstream
 * event worker and its CMSIS event/thread initializer.
 */

#ifndef OPEN_CFW_RUNTIME_EASYLOGGER_ASYNC_WORKER_CANDIDATE_H
#define OPEN_CFW_RUNTIME_EASYLOGGER_ASYNC_WORKER_CANDIDATE_H

#include "runtime_easylogger_async_consumer_candidate.h"

typedef void *open_cfw_easylogger_async_cmsis_id;

struct open_cfw_easylogger_async_thread_attributes {
    const char *name;
    open_cfw_easylogger_async_queue_u32 attribute_bits;
    void *control_block_memory;
    open_cfw_easylogger_async_queue_u32 control_block_size;
    void *stack_memory;
    open_cfw_easylogger_async_queue_u32 stack_size;
    open_cfw_easylogger_async_queue_u32 priority;
    open_cfw_easylogger_async_queue_u32 trustzone_module;
    open_cfw_easylogger_async_queue_u32 reserved;
};

extern open_cfw_easylogger_async_cmsis_id
    open_cfw_retained_easylogger_async_event_flags;

extern const char open_cfw_easylogger_async_worker_thread_name[];
extern const char open_cfw_easylogger_async_worker_start_message[];
extern const char open_cfw_easylogger_async_event_create_failure_message[];

void open_cfw_easylogger_async_event_dispatch(
    open_cfw_easylogger_async_queue_u32 flags
);

void open_cfw_easylogger_async_event_worker(void *argument);
void open_cfw_easylogger_async_event_worker_initialize(void);

#endif
