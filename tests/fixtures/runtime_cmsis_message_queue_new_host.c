/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Host oracle and dependency recorder for the bounded CMSIS-FreeRTOS
 * osMessageQueueNew source boundary.
 */

#include <stddef.h>
#include <string.h>

static unsigned int open_cfw_cmsis_test_get_ipsr(void);
static unsigned int open_cfw_cmsis_test_get_primask(void);
static unsigned int open_cfw_cmsis_test_get_basepri(void);

#define OPEN_CFW_CMSIS_MESSAGE_QUEUE_HOST_TEST 1
#include "../../components/apollo_main/core_overlay/runtime_cmsis_message_queue_new.c"

static unsigned char open_cfw_test_cmsis_control[0x50];
static unsigned char open_cfw_test_cmsis_storage[256];
static unsigned char open_cfw_test_cmsis_dynamic_handle;
static open_cfw_cmsis_message_queue_attr open_cfw_test_cmsis_attr;

unsigned int open_cfw_test_cmsis_ipsr;
unsigned int open_cfw_test_cmsis_primask;
unsigned int open_cfw_test_cmsis_basepri;
int open_cfw_test_cmsis_scheduler_state;
unsigned int open_cfw_test_cmsis_scheduler_calls;
unsigned int open_cfw_test_cmsis_ipsr_reads;
unsigned int open_cfw_test_cmsis_primask_reads;
unsigned int open_cfw_test_cmsis_basepri_reads;

unsigned int open_cfw_test_cmsis_static_calls;
unsigned int open_cfw_test_cmsis_static_count;
unsigned int open_cfw_test_cmsis_static_size;
unsigned int open_cfw_test_cmsis_static_type;
void *open_cfw_test_cmsis_static_storage;
void *open_cfw_test_cmsis_static_control;
unsigned int open_cfw_test_cmsis_static_success;

unsigned int open_cfw_test_cmsis_dynamic_calls;
unsigned int open_cfw_test_cmsis_dynamic_count;
unsigned int open_cfw_test_cmsis_dynamic_size;
unsigned int open_cfw_test_cmsis_dynamic_type;
unsigned int open_cfw_test_cmsis_dynamic_success;

static unsigned int open_cfw_cmsis_test_get_ipsr(void)
{
    open_cfw_test_cmsis_ipsr_reads++;
    return open_cfw_test_cmsis_ipsr;
}

static unsigned int open_cfw_cmsis_test_get_primask(void)
{
    open_cfw_test_cmsis_primask_reads++;
    return open_cfw_test_cmsis_primask;
}

static unsigned int open_cfw_cmsis_test_get_basepri(void)
{
    open_cfw_test_cmsis_basepri_reads++;
    return open_cfw_test_cmsis_basepri;
}

open_cfw_cmsis_base_type
open_cfw_freertos_task_get_scheduler_state(void)
{
    open_cfw_test_cmsis_scheduler_calls++;
    return open_cfw_test_cmsis_scheduler_state;
}

open_cfw_cmsis_queue_handle
open_cfw_freertos_queue_generic_create_static(
    open_cfw_cmsis_uint32 queue_length,
    open_cfw_cmsis_uint32 item_size,
    unsigned char *queue_storage,
    open_cfw_cmsis_static_queue *static_queue,
    unsigned char queue_type
)
{
    open_cfw_test_cmsis_static_calls++;
    open_cfw_test_cmsis_static_count = queue_length;
    open_cfw_test_cmsis_static_size = item_size;
    open_cfw_test_cmsis_static_storage = queue_storage;
    open_cfw_test_cmsis_static_control = static_queue;
    open_cfw_test_cmsis_static_type = queue_type;
    if (open_cfw_test_cmsis_static_success == 0U) {
        return (void *)0;
    }
    return static_queue;
}

open_cfw_cmsis_queue_handle
open_cfw_freertos_queue_generic_create(
    open_cfw_cmsis_uint32 queue_length,
    open_cfw_cmsis_uint32 item_size,
    unsigned char queue_type
)
{
    open_cfw_test_cmsis_dynamic_calls++;
    open_cfw_test_cmsis_dynamic_count = queue_length;
    open_cfw_test_cmsis_dynamic_size = item_size;
    open_cfw_test_cmsis_dynamic_type = queue_type;
    if (open_cfw_test_cmsis_dynamic_success == 0U) {
        return (void *)0;
    }
    return &open_cfw_test_cmsis_dynamic_handle;
}

void open_cfw_test_cmsis_message_queue_reset(void)
{
    memset(open_cfw_test_cmsis_control, 0, sizeof(open_cfw_test_cmsis_control));
    memset(open_cfw_test_cmsis_storage, 0, sizeof(open_cfw_test_cmsis_storage));
    memset(&open_cfw_test_cmsis_attr, 0, sizeof(open_cfw_test_cmsis_attr));

    open_cfw_test_cmsis_ipsr = 0U;
    open_cfw_test_cmsis_primask = 0U;
    open_cfw_test_cmsis_basepri = 0U;
    open_cfw_test_cmsis_scheduler_state = 1;
    open_cfw_test_cmsis_scheduler_calls = 0U;
    open_cfw_test_cmsis_ipsr_reads = 0U;
    open_cfw_test_cmsis_primask_reads = 0U;
    open_cfw_test_cmsis_basepri_reads = 0U;

    open_cfw_test_cmsis_static_calls = 0U;
    open_cfw_test_cmsis_static_count = 0U;
    open_cfw_test_cmsis_static_size = 0U;
    open_cfw_test_cmsis_static_type = 0xFFU;
    open_cfw_test_cmsis_static_storage = (void *)0;
    open_cfw_test_cmsis_static_control = (void *)0;
    open_cfw_test_cmsis_static_success = 1U;

    open_cfw_test_cmsis_dynamic_calls = 0U;
    open_cfw_test_cmsis_dynamic_count = 0U;
    open_cfw_test_cmsis_dynamic_size = 0U;
    open_cfw_test_cmsis_dynamic_type = 0xFFU;
    open_cfw_test_cmsis_dynamic_success = 1U;
}

void *open_cfw_test_cmsis_message_queue_call(
    unsigned int msg_count,
    unsigned int msg_size,
    int provide_attr,
    int provide_cb,
    unsigned int cb_size,
    int provide_mq,
    unsigned int mq_size,
    unsigned int attr_bits,
    int provide_name
)
{
    open_cfw_test_cmsis_attr.name =
        provide_name != 0 ? "ignored queue name" : (const char *)0;
    open_cfw_test_cmsis_attr.attr_bits = attr_bits;
    open_cfw_test_cmsis_attr.cb_mem =
        provide_cb != 0 ? open_cfw_test_cmsis_control : (void *)0;
    open_cfw_test_cmsis_attr.cb_size = cb_size;
    open_cfw_test_cmsis_attr.mq_mem =
        provide_mq != 0 ? open_cfw_test_cmsis_storage : (void *)0;
    open_cfw_test_cmsis_attr.mq_size = mq_size;

    return open_cfw_cmsis_message_queue_new(
        msg_count,
        msg_size,
        provide_attr != 0 ? &open_cfw_test_cmsis_attr :
            (const open_cfw_cmsis_message_queue_attr *)0
    );
}

void *open_cfw_test_cmsis_control_pointer(void)
{
    return open_cfw_test_cmsis_control;
}

void *open_cfw_test_cmsis_storage_pointer(void)
{
    return open_cfw_test_cmsis_storage;
}

void *open_cfw_test_cmsis_dynamic_pointer(void)
{
    return &open_cfw_test_cmsis_dynamic_handle;
}

unsigned int open_cfw_test_cmsis_static_queue_size(void)
{
    return (unsigned int)sizeof(open_cfw_cmsis_static_queue);
}

unsigned int open_cfw_test_cmsis_attr_size(void)
{
    return (unsigned int)sizeof(open_cfw_cmsis_message_queue_attr);
}

unsigned int open_cfw_test_cmsis_attr_offset_cb_mem(void)
{
    return (unsigned int)__builtin_offsetof(
        open_cfw_cmsis_message_queue_attr,
        cb_mem
    );
}

unsigned int open_cfw_test_cmsis_attr_offset_cb_size(void)
{
    return (unsigned int)__builtin_offsetof(
        open_cfw_cmsis_message_queue_attr,
        cb_size
    );
}

unsigned int open_cfw_test_cmsis_attr_offset_mq_mem(void)
{
    return (unsigned int)__builtin_offsetof(
        open_cfw_cmsis_message_queue_attr,
        mq_mem
    );
}

unsigned int open_cfw_test_cmsis_attr_offset_mq_size(void)
{
    return (unsigned int)__builtin_offsetof(
        open_cfw_cmsis_message_queue_attr,
        mq_size
    );
}

