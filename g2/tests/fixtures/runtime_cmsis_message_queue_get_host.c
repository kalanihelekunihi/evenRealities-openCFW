/* SPDX-License-Identifier: Apache-2.0 */
#include <stdint.h>

static uint32_t host_irq, host_timeout, host_isr_calls, host_task_calls;
static int32_t host_isr_result, host_task_result, host_yield;
static uint32_t host_pendsv;
static uintptr_t host_queue, host_message;

uint32_t open_cfw_cmsis_irq_context(void) { return host_irq; }
int32_t open_cfw_freertos_queue_receive_from_isr(
    void *queue, void *message, int32_t *woken
)
{
    ++host_isr_calls; host_queue = (uintptr_t)queue;
    host_message = (uintptr_t)message; *woken = host_yield;
    return host_isr_result;
}
int32_t open_cfw_freertos_queue_receive(
    void *queue, void *message, uint32_t timeout
)
{
    ++host_task_calls; host_queue = (uintptr_t)queue;
    host_message = (uintptr_t)message; host_timeout = timeout;
    return host_task_result;
}

#define OPEN_CFW_CMSIS_MQ_GET_PENDSV_SET() (++host_pendsv)
#include "../../components/apollo_main/core_overlay/runtime_cmsis_message_queue_get.c"

void open_cfw_mq_get_host_reset(
    uint32_t irq, int32_t isr_result, int32_t task_result, int32_t yield_value
)
{
    host_irq = irq; host_isr_result = isr_result;
    host_task_result = task_result; host_yield = yield_value;
    host_timeout = host_isr_calls = host_task_calls = host_pendsv = 0U;
    host_queue = host_message = 0U;
}
int32_t open_cfw_mq_get_host_call(
    uintptr_t queue, uintptr_t message, uintptr_t priority, uint32_t timeout
)
{
    return open_cfw_cmsis_message_queue_get(
        (void *)queue, (void *)message, (uint8_t *)priority, timeout
    );
}
uintptr_t open_cfw_mq_get_host_get(uint32_t selector)
{
    switch (selector) {
        case 0: return host_isr_calls; case 1: return host_task_calls;
        case 2: return host_pendsv; case 3: return host_queue;
        case 4: return host_message; case 5: return host_timeout;
        default: return 0U;
    }
}
