/* SPDX-License-Identifier: Apache-2.0 */
#include <stdint.h>

static uint32_t host_critical;
static int32_t host_put_isr_result;
static int32_t host_put_task_result;
static int32_t host_get_isr_result;
static int32_t host_get_task_result;
static int32_t host_yield;
static uint32_t host_put_isr_calls;
static uint32_t host_put_task_calls;
static uint32_t host_get_isr_calls;
static uint32_t host_get_task_calls;
static uint32_t host_pendsv;
static uintptr_t host_queue;
static uintptr_t host_message;
static uint32_t host_timeout;
static int32_t host_position;

uint32_t open_cfw_bootloader_critical_context(void) { return host_critical; }
int32_t open_cfw_bootloader_runtime_queue_put_isr_41a024(
    void *queue, const void *message, int32_t *woken, int32_t position)
{
    ++host_put_isr_calls; host_queue=(uintptr_t)queue;
    host_message=(uintptr_t)message; host_position=position; *woken=host_yield;
    return host_put_isr_result;
}
int32_t open_cfw_bootloader_runtime_queue_put_task_419ec0(
    void *queue, const void *message, uint32_t timeout, int32_t position)
{
    ++host_put_task_calls; host_queue=(uintptr_t)queue;
    host_message=(uintptr_t)message; host_timeout=timeout; host_position=position;
    return host_put_task_result;
}
int32_t open_cfw_bootloader_runtime_queue_get_isr_41a3b0(
    void *queue, void *message, int32_t *woken)
{
    ++host_get_isr_calls; host_queue=(uintptr_t)queue;
    host_message=(uintptr_t)message; *woken=host_yield;
    return host_get_isr_result;
}
int32_t open_cfw_bootloader_runtime_queue_get_task_41a114(
    void *queue, void *message, uint32_t timeout)
{
    ++host_get_task_calls; host_queue=(uintptr_t)queue;
    host_message=(uintptr_t)message; host_timeout=timeout;
    return host_get_task_result;
}

#define OPEN_CFW_BOOTLOADER_QUEUE_PUT_PENDSV_SET() (++host_pendsv)
#define OPEN_CFW_BOOTLOADER_QUEUE_GET_PENDSV_SET() (++host_pendsv)
#include "../../components/bootloader/core_overlay/runtime_queue_put_4168a2.c"
#include "../../components/bootloader/core_overlay/runtime_queue_get_416920.c"

void open_cfw_test_queue_io_reset(
    uint32_t critical, int32_t put_isr, int32_t put_task,
    int32_t get_isr, int32_t get_task, int32_t yield_value)
{
    host_critical=critical; host_put_isr_result=put_isr;
    host_put_task_result=put_task; host_get_isr_result=get_isr;
    host_get_task_result=get_task; host_yield=yield_value;
    host_put_isr_calls=0U; host_put_task_calls=0U;
    host_get_isr_calls=0U; host_get_task_calls=0U; host_pendsv=0U;
    host_queue=0U; host_message=0U; host_timeout=0U; host_position=-1;
}
int32_t open_cfw_test_queue_put(
    uintptr_t queue, uintptr_t message, uint8_t priority, uint32_t timeout)
{
    return open_cfw_bootloader_runtime_queue_put_4168a2(
        (void *)queue, (const void *)message, priority, timeout);
}
int32_t open_cfw_test_queue_get(
    uintptr_t queue, uintptr_t message, uintptr_t priority, uint32_t timeout)
{
    return open_cfw_bootloader_runtime_queue_get_416920(
        (void *)queue, (void *)message, (uint8_t *)priority, timeout);
}
uintptr_t open_cfw_test_queue_io_observed(uint32_t selector)
{
    switch (selector) {
        case 0: return host_put_isr_calls; case 1: return host_put_task_calls;
        case 2: return host_get_isr_calls; case 3: return host_get_task_calls;
        case 4: return host_pendsv; case 5: return host_queue;
        case 6: return host_message; case 7: return host_timeout;
        case 8: return (uintptr_t)host_position; default: return 0U;
    }
}
