#include <stdint.h>

static uint32_t open_cfw_test_irq;
static uint32_t open_cfw_test_command_result;
static uint32_t open_cfw_test_active;
static void *open_cfw_test_context;
static uint32_t open_cfw_test_command_calls;
static uint32_t open_cfw_test_active_calls;
static uint32_t open_cfw_test_context_calls;
static uint32_t open_cfw_test_free_calls;
static const void *open_cfw_test_timer;
static int open_cfw_test_command_id;
static uint32_t open_cfw_test_optional_value;
static uint32_t open_cfw_test_ticks_to_wait;
static void *open_cfw_test_freed;

uint32_t open_cfw_cmsis_irq_context(void) { return open_cfw_test_irq; }
uint32_t open_cfw_rtos_timer_command(
    const void *timer,
    int command_id,
    uint32_t optional_value,
    uint32_t *higher_priority_task_woken,
    uint32_t ticks_to_wait
)
{
    open_cfw_test_command_calls += 1U;
    open_cfw_test_timer = timer;
    open_cfw_test_command_id = command_id;
    open_cfw_test_optional_value = optional_value;
    open_cfw_test_ticks_to_wait = ticks_to_wait;
    if (higher_priority_task_woken != (uint32_t *)0) {
        *higher_priority_task_woken = 1U;
    }
    return open_cfw_test_command_result;
}
uint32_t open_cfw_rtos_timer_is_active(const void *timer)
{
    open_cfw_test_active_calls += 1U;
    open_cfw_test_timer = timer;
    return open_cfw_test_active;
}
void *open_cfw_rtos_timer_get_context(const void *timer)
{
    open_cfw_test_context_calls += 1U;
    open_cfw_test_timer = timer;
    return open_cfw_test_context;
}
void open_cfw_freertos_heap4_free(void *memory)
{
    open_cfw_test_free_calls += 1U;
    open_cfw_test_freed = memory;
}

#include "../../components/apollo_main/core_overlay/runtime_cmsis_timer_ops.c"

void open_cfw_test_timer_ops_reset(
    uint32_t irq,
    uint32_t command_result,
    uint32_t active,
    uintptr_t context
)
{
    open_cfw_test_irq = irq;
    open_cfw_test_command_result = command_result;
    open_cfw_test_active = active;
    open_cfw_test_context = (void *)context;
    open_cfw_test_command_calls = 0U;
    open_cfw_test_active_calls = 0U;
    open_cfw_test_context_calls = 0U;
    open_cfw_test_free_calls = 0U;
    open_cfw_test_timer = (void *)0;
    open_cfw_test_command_id = -1;
    open_cfw_test_optional_value = 0U;
    open_cfw_test_ticks_to_wait = 0U;
    open_cfw_test_freed = (void *)0;
}
uint32_t open_cfw_test_timer_ops_command_calls(void)
{ return open_cfw_test_command_calls; }
uint32_t open_cfw_test_timer_ops_active_calls(void)
{ return open_cfw_test_active_calls; }
uint32_t open_cfw_test_timer_ops_context_calls(void)
{ return open_cfw_test_context_calls; }
uint32_t open_cfw_test_timer_ops_free_calls(void)
{ return open_cfw_test_free_calls; }
uintptr_t open_cfw_test_timer_ops_timer(void)
{ return (uintptr_t)open_cfw_test_timer; }
int open_cfw_test_timer_ops_command_id(void)
{ return open_cfw_test_command_id; }
uint32_t open_cfw_test_timer_ops_optional_value(void)
{ return open_cfw_test_optional_value; }
uint32_t open_cfw_test_timer_ops_ticks_to_wait(void)
{ return open_cfw_test_ticks_to_wait; }
uintptr_t open_cfw_test_timer_ops_freed(void)
{ return (uintptr_t)open_cfw_test_freed; }
