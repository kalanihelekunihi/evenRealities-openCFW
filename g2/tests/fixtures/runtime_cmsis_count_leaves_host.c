#include <stdint.h>

static uint32_t open_cfw_test_irq;
static uint32_t open_cfw_test_task_count;
static uint32_t open_cfw_test_isr_count;
static uint32_t open_cfw_test_task_calls;
static uint32_t open_cfw_test_isr_calls;

void open_cfw_test_cmsis_count_reset(
    uint32_t irq,
    uint32_t task_count,
    uint32_t isr_count
)
{
    open_cfw_test_irq = irq;
    open_cfw_test_task_count = task_count;
    open_cfw_test_isr_count = isr_count;
    open_cfw_test_task_calls = 0U;
    open_cfw_test_isr_calls = 0U;
}

uint32_t open_cfw_cmsis_irq_context(void)
{
    return open_cfw_test_irq;
}

uint32_t open_cfw_freertos_queue_messages_waiting(const void *queue)
{
    (void)queue;
    open_cfw_test_task_calls += 1U;
    return open_cfw_test_task_count;
}

uint32_t open_cfw_freertos_queue_messages_waiting_from_isr(const void *queue)
{
    (void)queue;
    open_cfw_test_isr_calls += 1U;
    return open_cfw_test_isr_count;
}

uint32_t open_cfw_test_cmsis_count_task_calls(void)
{
    return open_cfw_test_task_calls;
}

uint32_t open_cfw_test_cmsis_count_isr_calls(void)
{
    return open_cfw_test_isr_calls;
}

#include "../../components/apollo_main/core_overlay/runtime_cmsis_count_leaves.c"
