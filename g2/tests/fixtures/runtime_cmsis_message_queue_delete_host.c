#include <stdint.h>

static uint32_t open_cfw_test_irq_context;
static uint32_t open_cfw_test_delete_calls;
static void *open_cfw_test_deleted_queue;

uint32_t open_cfw_cmsis_irq_context(void)
{
    return open_cfw_test_irq_context;
}

void open_cfw_freertos_queue_delete(void *queue)
{
    open_cfw_test_delete_calls += 1U;
    open_cfw_test_deleted_queue = queue;
}

void open_cfw_test_cmsis_mq_delete_reset(uint32_t irq_context)
{
    open_cfw_test_irq_context = irq_context;
    open_cfw_test_delete_calls = 0U;
    open_cfw_test_deleted_queue = (void *)0;
}

uint32_t open_cfw_test_cmsis_mq_delete_calls(void)
{
    return open_cfw_test_delete_calls;
}

uintptr_t open_cfw_test_cmsis_mq_deleted_queue(void)
{
    return (uintptr_t)open_cfw_test_deleted_queue;
}

#include "../../components/apollo_main/core_overlay/runtime_cmsis_message_queue_delete.c"
