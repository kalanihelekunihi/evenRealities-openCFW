/* SPDX-License-Identifier: Apache-2.0 */

#include <stdint.h>

static uint32_t host_irq;
static int32_t host_isr_result;
static int32_t host_task_result;
static int32_t host_yield;
static uint32_t host_isr_calls;
static uint32_t host_task_calls;
static uint32_t host_pendsv;
static uintptr_t host_queue;
static uintptr_t host_message;
static uint32_t host_timeout;
static int32_t host_position;

uint32_t open_cfw_cmsis_irq_context(void)
{
    return host_irq;
}

int32_t open_cfw_freertos_queue_generic_send_from_isr(
    void *queue, const void *message, int32_t *woken, int32_t position
)
{
    ++host_isr_calls;
    host_queue = (uintptr_t)queue;
    host_message = (uintptr_t)message;
    host_position = position;
    if (woken != 0) {
        *woken = host_yield;
    }
    return host_isr_result;
}

int32_t open_cfw_freertos_queue_generic_send(
    void *queue, const void *message, uint32_t timeout, int32_t position
)
{
    ++host_task_calls;
    host_queue = (uintptr_t)queue;
    host_message = (uintptr_t)message;
    host_timeout = timeout;
    host_position = position;
    return host_task_result;
}

#define OPEN_CFW_CMSIS_MQ_PUT_PENDSV_SET() (++host_pendsv)
#include "../../components/apollo_main/core_overlay/runtime_cmsis_message_queue_put.c"

void open_cfw_mq_put_host_reset(
    uint32_t irq, int32_t isr_result, int32_t task_result, int32_t yield_value
)
{
    host_irq = irq;
    host_isr_result = isr_result;
    host_task_result = task_result;
    host_yield = yield_value;
    host_isr_calls = 0U;
    host_task_calls = 0U;
    host_pendsv = 0U;
    host_queue = 0U;
    host_message = 0U;
    host_timeout = 0U;
    host_position = -1;
}

int32_t open_cfw_mq_put_host_call(
    uintptr_t queue, uintptr_t message, uint8_t priority, uint32_t timeout
)
{
    return open_cfw_cmsis_message_queue_put(
        (void *)queue, (const void *)message, priority, timeout
    );
}

uintptr_t open_cfw_mq_put_host_get(uint32_t selector)
{
    switch (selector) {
        case 0: return host_isr_calls;
        case 1: return host_task_calls;
        case 2: return host_pendsv;
        case 3: return host_queue;
        case 4: return host_message;
        case 5: return host_timeout;
        case 6: return (uintptr_t)host_position;
        default: return 0U;
    }
}
