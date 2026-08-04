/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Host dependency recorder for the bounded CMSIS-FreeRTOS osSemaphoreNew
 * source boundary.
 */

#include <stddef.h>
#include <stdint.h>
#include <string.h>

static unsigned int open_cfw_cmsis_semaphore_test_get_ipsr(void);
static unsigned int open_cfw_cmsis_semaphore_test_get_primask(void);
static unsigned int open_cfw_cmsis_semaphore_test_get_basepri(void);

#define OPEN_CFW_CMSIS_SEMAPHORE_HOST_TEST 1
#include "../../components/apollo_main/core_overlay/runtime_cmsis_semaphore_new.c"

static open_cfw_cmsis_static_semaphore
    open_cfw_test_cmsis_semaphore_control;
static unsigned int open_cfw_test_cmsis_semaphore_dynamic_handle;
static open_cfw_cmsis_semaphore_attr
    open_cfw_test_cmsis_semaphore_attr;

unsigned int open_cfw_test_cmsis_semaphore_ipsr;
unsigned int open_cfw_test_cmsis_semaphore_primask;
unsigned int open_cfw_test_cmsis_semaphore_basepri;
int open_cfw_test_cmsis_semaphore_scheduler_state;
unsigned int open_cfw_test_cmsis_semaphore_scheduler_calls;
unsigned int open_cfw_test_cmsis_semaphore_ipsr_reads;
unsigned int open_cfw_test_cmsis_semaphore_primask_reads;
unsigned int open_cfw_test_cmsis_semaphore_basepri_reads;

unsigned int open_cfw_test_cmsis_semaphore_binary_static_calls;
unsigned int open_cfw_test_cmsis_semaphore_binary_static_length;
unsigned int open_cfw_test_cmsis_semaphore_binary_static_item_size;
unsigned int open_cfw_test_cmsis_semaphore_binary_static_type;
void *open_cfw_test_cmsis_semaphore_binary_static_storage;
void *open_cfw_test_cmsis_semaphore_binary_static_control;
unsigned int open_cfw_test_cmsis_semaphore_binary_static_success;

unsigned int open_cfw_test_cmsis_semaphore_binary_dynamic_calls;
unsigned int open_cfw_test_cmsis_semaphore_binary_dynamic_length;
unsigned int open_cfw_test_cmsis_semaphore_binary_dynamic_item_size;
unsigned int open_cfw_test_cmsis_semaphore_binary_dynamic_type;
unsigned int open_cfw_test_cmsis_semaphore_binary_dynamic_success;

unsigned int open_cfw_test_cmsis_semaphore_give_calls;
void *open_cfw_test_cmsis_semaphore_give_queue;
const void *open_cfw_test_cmsis_semaphore_give_item;
unsigned int open_cfw_test_cmsis_semaphore_give_ticks;
int open_cfw_test_cmsis_semaphore_give_position;
int open_cfw_test_cmsis_semaphore_give_result;

unsigned int open_cfw_test_cmsis_semaphore_delete_calls;
void *open_cfw_test_cmsis_semaphore_delete_queue;

unsigned int open_cfw_test_cmsis_semaphore_counting_static_calls;
unsigned int open_cfw_test_cmsis_semaphore_counting_static_maximum;
unsigned int open_cfw_test_cmsis_semaphore_counting_static_initial;
void *open_cfw_test_cmsis_semaphore_counting_static_control;
unsigned int open_cfw_test_cmsis_semaphore_counting_static_success;

unsigned int open_cfw_test_cmsis_semaphore_counting_dynamic_calls;
unsigned int open_cfw_test_cmsis_semaphore_counting_dynamic_maximum;
unsigned int open_cfw_test_cmsis_semaphore_counting_dynamic_initial;
unsigned int open_cfw_test_cmsis_semaphore_counting_dynamic_success;

static unsigned int open_cfw_cmsis_semaphore_test_get_ipsr(void)
{
    open_cfw_test_cmsis_semaphore_ipsr_reads++;
    return open_cfw_test_cmsis_semaphore_ipsr;
}

static unsigned int open_cfw_cmsis_semaphore_test_get_primask(void)
{
    open_cfw_test_cmsis_semaphore_primask_reads++;
    return open_cfw_test_cmsis_semaphore_primask;
}

static unsigned int open_cfw_cmsis_semaphore_test_get_basepri(void)
{
    open_cfw_test_cmsis_semaphore_basepri_reads++;
    return open_cfw_test_cmsis_semaphore_basepri;
}

open_cfw_cmsis_semaphore_base_type
open_cfw_freertos_task_get_scheduler_state(void)
{
    open_cfw_test_cmsis_semaphore_scheduler_calls++;
    return open_cfw_test_cmsis_semaphore_scheduler_state;
}

open_cfw_cmsis_semaphore_handle
open_cfw_freertos_queue_generic_create_static(
    open_cfw_cmsis_semaphore_uint32 queue_length,
    open_cfw_cmsis_semaphore_uint32 item_size,
    unsigned char *queue_storage,
    open_cfw_cmsis_static_semaphore *static_queue,
    unsigned char queue_type
)
{
    open_cfw_test_cmsis_semaphore_binary_static_calls++;
    open_cfw_test_cmsis_semaphore_binary_static_length = queue_length;
    open_cfw_test_cmsis_semaphore_binary_static_item_size = item_size;
    open_cfw_test_cmsis_semaphore_binary_static_storage = queue_storage;
    open_cfw_test_cmsis_semaphore_binary_static_control = static_queue;
    open_cfw_test_cmsis_semaphore_binary_static_type = queue_type;

    if (open_cfw_test_cmsis_semaphore_binary_static_success == 0U) {
        return (void *)0;
    }
    return static_queue;
}

open_cfw_cmsis_semaphore_handle
open_cfw_freertos_queue_generic_create(
    open_cfw_cmsis_semaphore_uint32 queue_length,
    open_cfw_cmsis_semaphore_uint32 item_size,
    unsigned char queue_type
)
{
    open_cfw_test_cmsis_semaphore_binary_dynamic_calls++;
    open_cfw_test_cmsis_semaphore_binary_dynamic_length = queue_length;
    open_cfw_test_cmsis_semaphore_binary_dynamic_item_size = item_size;
    open_cfw_test_cmsis_semaphore_binary_dynamic_type = queue_type;

    if (open_cfw_test_cmsis_semaphore_binary_dynamic_success == 0U) {
        return (void *)0;
    }
    return &open_cfw_test_cmsis_semaphore_dynamic_handle;
}

open_cfw_cmsis_semaphore_base_type
open_cfw_freertos_queue_generic_send(
    open_cfw_cmsis_semaphore_handle queue,
    const void *item,
    open_cfw_cmsis_semaphore_tick_type ticks_to_wait,
    open_cfw_cmsis_semaphore_base_type copy_position
)
{
    open_cfw_test_cmsis_semaphore_give_calls++;
    open_cfw_test_cmsis_semaphore_give_queue = queue;
    open_cfw_test_cmsis_semaphore_give_item = item;
    open_cfw_test_cmsis_semaphore_give_ticks = ticks_to_wait;
    open_cfw_test_cmsis_semaphore_give_position = copy_position;
    return open_cfw_test_cmsis_semaphore_give_result;
}

void open_cfw_freertos_queue_delete(
    open_cfw_cmsis_semaphore_handle queue
)
{
    open_cfw_test_cmsis_semaphore_delete_calls++;
    open_cfw_test_cmsis_semaphore_delete_queue = queue;
}

open_cfw_cmsis_semaphore_handle
open_cfw_freertos_queue_create_counting_semaphore_static(
    open_cfw_cmsis_semaphore_uint32 maximum_count,
    open_cfw_cmsis_semaphore_uint32 initial_count,
    open_cfw_cmsis_static_semaphore *static_queue
)
{
    open_cfw_test_cmsis_semaphore_counting_static_calls++;
    open_cfw_test_cmsis_semaphore_counting_static_maximum =
        maximum_count;
    open_cfw_test_cmsis_semaphore_counting_static_initial =
        initial_count;
    open_cfw_test_cmsis_semaphore_counting_static_control =
        static_queue;

    if (open_cfw_test_cmsis_semaphore_counting_static_success == 0U) {
        return (void *)0;
    }
    return static_queue;
}

open_cfw_cmsis_semaphore_handle
open_cfw_freertos_queue_create_counting_semaphore(
    open_cfw_cmsis_semaphore_uint32 maximum_count,
    open_cfw_cmsis_semaphore_uint32 initial_count
)
{
    open_cfw_test_cmsis_semaphore_counting_dynamic_calls++;
    open_cfw_test_cmsis_semaphore_counting_dynamic_maximum =
        maximum_count;
    open_cfw_test_cmsis_semaphore_counting_dynamic_initial =
        initial_count;

    if (open_cfw_test_cmsis_semaphore_counting_dynamic_success == 0U) {
        return (void *)0;
    }
    return &open_cfw_test_cmsis_semaphore_dynamic_handle;
}

void open_cfw_test_cmsis_semaphore_reset(void)
{
    memset(
        &open_cfw_test_cmsis_semaphore_control,
        0,
        sizeof(open_cfw_test_cmsis_semaphore_control)
    );
    memset(
        &open_cfw_test_cmsis_semaphore_attr,
        0,
        sizeof(open_cfw_test_cmsis_semaphore_attr)
    );

    open_cfw_test_cmsis_semaphore_ipsr = 0U;
    open_cfw_test_cmsis_semaphore_primask = 0U;
    open_cfw_test_cmsis_semaphore_basepri = 0U;
    open_cfw_test_cmsis_semaphore_scheduler_state = 1;
    open_cfw_test_cmsis_semaphore_scheduler_calls = 0U;
    open_cfw_test_cmsis_semaphore_ipsr_reads = 0U;
    open_cfw_test_cmsis_semaphore_primask_reads = 0U;
    open_cfw_test_cmsis_semaphore_basepri_reads = 0U;

    open_cfw_test_cmsis_semaphore_binary_static_calls = 0U;
    open_cfw_test_cmsis_semaphore_binary_static_length = 0xFFFFFFFFU;
    open_cfw_test_cmsis_semaphore_binary_static_item_size = 0xFFFFFFFFU;
    open_cfw_test_cmsis_semaphore_binary_static_type = 0xFFU;
    open_cfw_test_cmsis_semaphore_binary_static_storage = (void *)0;
    open_cfw_test_cmsis_semaphore_binary_static_control = (void *)0;
    open_cfw_test_cmsis_semaphore_binary_static_success = 1U;

    open_cfw_test_cmsis_semaphore_binary_dynamic_calls = 0U;
    open_cfw_test_cmsis_semaphore_binary_dynamic_length = 0xFFFFFFFFU;
    open_cfw_test_cmsis_semaphore_binary_dynamic_item_size = 0xFFFFFFFFU;
    open_cfw_test_cmsis_semaphore_binary_dynamic_type = 0xFFU;
    open_cfw_test_cmsis_semaphore_binary_dynamic_success = 1U;

    open_cfw_test_cmsis_semaphore_give_calls = 0U;
    open_cfw_test_cmsis_semaphore_give_queue = (void *)0;
    open_cfw_test_cmsis_semaphore_give_item = (const void *)0;
    open_cfw_test_cmsis_semaphore_give_ticks = 0xFFFFFFFFU;
    open_cfw_test_cmsis_semaphore_give_position = -1;
    open_cfw_test_cmsis_semaphore_give_result = 1;

    open_cfw_test_cmsis_semaphore_delete_calls = 0U;
    open_cfw_test_cmsis_semaphore_delete_queue = (void *)0;

    open_cfw_test_cmsis_semaphore_counting_static_calls = 0U;
    open_cfw_test_cmsis_semaphore_counting_static_maximum = 0U;
    open_cfw_test_cmsis_semaphore_counting_static_initial = 0U;
    open_cfw_test_cmsis_semaphore_counting_static_control = (void *)0;
    open_cfw_test_cmsis_semaphore_counting_static_success = 1U;

    open_cfw_test_cmsis_semaphore_counting_dynamic_calls = 0U;
    open_cfw_test_cmsis_semaphore_counting_dynamic_maximum = 0U;
    open_cfw_test_cmsis_semaphore_counting_dynamic_initial = 0U;
    open_cfw_test_cmsis_semaphore_counting_dynamic_success = 1U;
}

uintptr_t open_cfw_test_cmsis_semaphore_call(
    unsigned int maximum_count,
    unsigned int initial_count,
    int provide_attr,
    int provide_cb,
    unsigned int cb_size,
    int provide_name
)
{
    open_cfw_test_cmsis_semaphore_attr.name =
        provide_name != 0 ? "ignored semaphore name" : (const char *)0;
    open_cfw_test_cmsis_semaphore_attr.attr_bits = 0xA5A5A5A5U;
    open_cfw_test_cmsis_semaphore_attr.cb_mem =
        provide_cb != 0 ?
            &open_cfw_test_cmsis_semaphore_control :
            (void *)0;
    open_cfw_test_cmsis_semaphore_attr.cb_size = cb_size;

    return (uintptr_t)open_cfw_cmsis_semaphore_new(
        maximum_count,
        initial_count,
        provide_attr != 0 ?
            &open_cfw_test_cmsis_semaphore_attr :
            (const open_cfw_cmsis_semaphore_attr *)0
    );
}

uintptr_t open_cfw_test_cmsis_semaphore_control_pointer(void)
{
    return (uintptr_t)&open_cfw_test_cmsis_semaphore_control;
}

uintptr_t open_cfw_test_cmsis_semaphore_dynamic_pointer(void)
{
    return (uintptr_t)&open_cfw_test_cmsis_semaphore_dynamic_handle;
}

unsigned int open_cfw_test_cmsis_semaphore_static_size(void)
{
    return (unsigned int)sizeof(open_cfw_cmsis_static_semaphore);
}

unsigned int open_cfw_test_cmsis_semaphore_attr_size(void)
{
    return (unsigned int)sizeof(open_cfw_cmsis_semaphore_attr);
}

unsigned int open_cfw_test_cmsis_semaphore_attr_offset_name(void)
{
    return (unsigned int)__builtin_offsetof(
        open_cfw_cmsis_semaphore_attr,
        name
    );
}

unsigned int open_cfw_test_cmsis_semaphore_attr_offset_attr_bits(void)
{
    return (unsigned int)__builtin_offsetof(
        open_cfw_cmsis_semaphore_attr,
        attr_bits
    );
}

unsigned int open_cfw_test_cmsis_semaphore_attr_offset_cb_mem(void)
{
    return (unsigned int)__builtin_offsetof(
        open_cfw_cmsis_semaphore_attr,
        cb_mem
    );
}

unsigned int open_cfw_test_cmsis_semaphore_attr_offset_cb_size(void)
{
    return (unsigned int)__builtin_offsetof(
        open_cfw_cmsis_semaphore_attr,
        cb_size
    );
}
