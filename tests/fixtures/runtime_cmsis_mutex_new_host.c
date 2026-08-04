/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Host dependency recorder for the bounded CMSIS-FreeRTOS osMutexNew source
 * boundary.
 */

#include <stddef.h>
#include <stdint.h>
#include <string.h>

static unsigned int open_cfw_cmsis_mutex_test_get_ipsr(void);
static unsigned int open_cfw_cmsis_mutex_test_get_primask(void);
static unsigned int open_cfw_cmsis_mutex_test_get_basepri(void);

#define OPEN_CFW_CMSIS_MUTEX_HOST_TEST 1
#include "../../components/apollo_main/core_overlay/runtime_cmsis_mutex_new.c"

static open_cfw_cmsis_static_semaphore open_cfw_test_cmsis_mutex_control;
static unsigned int open_cfw_test_cmsis_mutex_dynamic_handle;
static open_cfw_cmsis_mutex_attr open_cfw_test_cmsis_mutex_attr;

unsigned int open_cfw_test_cmsis_mutex_ipsr;
unsigned int open_cfw_test_cmsis_mutex_primask;
unsigned int open_cfw_test_cmsis_mutex_basepri;
int open_cfw_test_cmsis_mutex_scheduler_state;
unsigned int open_cfw_test_cmsis_mutex_scheduler_calls;
unsigned int open_cfw_test_cmsis_mutex_ipsr_reads;
unsigned int open_cfw_test_cmsis_mutex_primask_reads;
unsigned int open_cfw_test_cmsis_mutex_basepri_reads;

unsigned int open_cfw_test_cmsis_mutex_static_calls;
unsigned int open_cfw_test_cmsis_mutex_static_type;
void *open_cfw_test_cmsis_mutex_static_control;
unsigned int open_cfw_test_cmsis_mutex_static_success;

unsigned int open_cfw_test_cmsis_mutex_dynamic_calls;
unsigned int open_cfw_test_cmsis_mutex_dynamic_type;
unsigned int open_cfw_test_cmsis_mutex_dynamic_success;

static unsigned int open_cfw_cmsis_mutex_test_get_ipsr(void)
{
    open_cfw_test_cmsis_mutex_ipsr_reads++;
    return open_cfw_test_cmsis_mutex_ipsr;
}

static unsigned int open_cfw_cmsis_mutex_test_get_primask(void)
{
    open_cfw_test_cmsis_mutex_primask_reads++;
    return open_cfw_test_cmsis_mutex_primask;
}

static unsigned int open_cfw_cmsis_mutex_test_get_basepri(void)
{
    open_cfw_test_cmsis_mutex_basepri_reads++;
    return open_cfw_test_cmsis_mutex_basepri;
}

open_cfw_cmsis_mutex_base_type
open_cfw_freertos_task_get_scheduler_state(void)
{
    open_cfw_test_cmsis_mutex_scheduler_calls++;
    return open_cfw_test_cmsis_mutex_scheduler_state;
}

open_cfw_cmsis_mutex_handle
open_cfw_freertos_queue_create_mutex_static(
    open_cfw_cmsis_mutex_uint32 queue_type,
    open_cfw_cmsis_static_semaphore *static_semaphore
)
{
    open_cfw_test_cmsis_mutex_static_calls++;
    open_cfw_test_cmsis_mutex_static_type = queue_type;
    open_cfw_test_cmsis_mutex_static_control = static_semaphore;
    if (open_cfw_test_cmsis_mutex_static_success == 0U) {
        return (void *)0;
    }
    return static_semaphore;
}

open_cfw_cmsis_mutex_handle
open_cfw_freertos_queue_create_mutex(unsigned char queue_type)
{
    open_cfw_test_cmsis_mutex_dynamic_calls++;
    open_cfw_test_cmsis_mutex_dynamic_type = queue_type;
    if (open_cfw_test_cmsis_mutex_dynamic_success == 0U) {
        return (void *)0;
    }
    return &open_cfw_test_cmsis_mutex_dynamic_handle;
}

void open_cfw_test_cmsis_mutex_reset(void)
{
    memset(
        &open_cfw_test_cmsis_mutex_control,
        0,
        sizeof(open_cfw_test_cmsis_mutex_control)
    );
    memset(
        &open_cfw_test_cmsis_mutex_attr,
        0,
        sizeof(open_cfw_test_cmsis_mutex_attr)
    );

    open_cfw_test_cmsis_mutex_ipsr = 0U;
    open_cfw_test_cmsis_mutex_primask = 0U;
    open_cfw_test_cmsis_mutex_basepri = 0U;
    open_cfw_test_cmsis_mutex_scheduler_state = 1;
    open_cfw_test_cmsis_mutex_scheduler_calls = 0U;
    open_cfw_test_cmsis_mutex_ipsr_reads = 0U;
    open_cfw_test_cmsis_mutex_primask_reads = 0U;
    open_cfw_test_cmsis_mutex_basepri_reads = 0U;

    open_cfw_test_cmsis_mutex_static_calls = 0U;
    open_cfw_test_cmsis_mutex_static_type = 0xFFU;
    open_cfw_test_cmsis_mutex_static_control = (void *)0;
    open_cfw_test_cmsis_mutex_static_success = 1U;

    open_cfw_test_cmsis_mutex_dynamic_calls = 0U;
    open_cfw_test_cmsis_mutex_dynamic_type = 0xFFU;
    open_cfw_test_cmsis_mutex_dynamic_success = 1U;
}

uintptr_t open_cfw_test_cmsis_mutex_call(
    int provide_attr,
    unsigned int attr_bits,
    int provide_cb,
    unsigned int cb_size,
    int provide_name
)
{
    open_cfw_test_cmsis_mutex_attr.name =
        provide_name != 0 ? "ignored mutex name" : (const char *)0;
    open_cfw_test_cmsis_mutex_attr.attr_bits = attr_bits;
    open_cfw_test_cmsis_mutex_attr.cb_mem =
        provide_cb != 0 ? &open_cfw_test_cmsis_mutex_control : (void *)0;
    open_cfw_test_cmsis_mutex_attr.cb_size = cb_size;

    return (uintptr_t)open_cfw_cmsis_mutex_new(
        provide_attr != 0 ? &open_cfw_test_cmsis_mutex_attr :
            (const open_cfw_cmsis_mutex_attr *)0
    );
}

uintptr_t open_cfw_test_cmsis_mutex_control_pointer(void)
{
    return (uintptr_t)&open_cfw_test_cmsis_mutex_control;
}

uintptr_t open_cfw_test_cmsis_mutex_dynamic_pointer(void)
{
    return (uintptr_t)&open_cfw_test_cmsis_mutex_dynamic_handle;
}

unsigned int open_cfw_test_cmsis_mutex_static_semaphore_size(void)
{
    return (unsigned int)sizeof(open_cfw_cmsis_static_semaphore);
}

unsigned int open_cfw_test_cmsis_mutex_attr_size(void)
{
    return (unsigned int)sizeof(open_cfw_cmsis_mutex_attr);
}

unsigned int open_cfw_test_cmsis_mutex_attr_offset_name(void)
{
    return (unsigned int)__builtin_offsetof(
        open_cfw_cmsis_mutex_attr,
        name
    );
}

unsigned int open_cfw_test_cmsis_mutex_attr_offset_attr_bits(void)
{
    return (unsigned int)__builtin_offsetof(
        open_cfw_cmsis_mutex_attr,
        attr_bits
    );
}

unsigned int open_cfw_test_cmsis_mutex_attr_offset_cb_mem(void)
{
    return (unsigned int)__builtin_offsetof(
        open_cfw_cmsis_mutex_attr,
        cb_mem
    );
}

unsigned int open_cfw_test_cmsis_mutex_attr_offset_cb_size(void)
{
    return (unsigned int)__builtin_offsetof(
        open_cfw_cmsis_mutex_attr,
        cb_size
    );
}
