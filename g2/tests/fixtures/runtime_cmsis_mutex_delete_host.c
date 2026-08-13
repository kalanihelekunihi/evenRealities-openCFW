#include <stdint.h>

static uint32_t open_cfw_test_irq;
static uint32_t open_cfw_test_calls;
static void *open_cfw_test_mutex;

uint32_t open_cfw_cmsis_irq_context(void) { return open_cfw_test_irq; }
void open_cfw_freertos_queue_delete(void *mutex)
{
    open_cfw_test_calls += 1U;
    open_cfw_test_mutex = mutex;
}

void open_cfw_test_mutex_delete_reset(uint32_t irq)
{
    open_cfw_test_irq = irq;
    open_cfw_test_calls = 0U;
    open_cfw_test_mutex = (void *)0;
}
uint32_t open_cfw_test_mutex_delete_calls(void) { return open_cfw_test_calls; }
uintptr_t open_cfw_test_mutex_delete_handle(void) { return (uintptr_t)open_cfw_test_mutex; }

#include "../../components/apollo_main/core_overlay/runtime_cmsis_mutex_delete.c"
