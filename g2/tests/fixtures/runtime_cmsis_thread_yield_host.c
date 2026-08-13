#include <stdint.h>

static uint32_t open_cfw_test_irq_context;
static uint32_t open_cfw_test_yield_calls;

uint32_t open_cfw_cmsis_irq_context(void)
{
    return open_cfw_test_irq_context;
}

void open_cfw_freertos_port_yield(void)
{
    open_cfw_test_yield_calls += 1U;
}

void open_cfw_test_cmsis_yield_reset(uint32_t irq_context)
{
    open_cfw_test_irq_context = irq_context;
    open_cfw_test_yield_calls = 0U;
}

uint32_t open_cfw_test_cmsis_yield_calls(void)
{
    return open_cfw_test_yield_calls;
}

#include "../../components/apollo_main/core_overlay/runtime_cmsis_thread_yield.c"
