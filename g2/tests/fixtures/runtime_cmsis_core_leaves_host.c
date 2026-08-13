#include <stdint.h>

static uint32_t test_ipsr;
static uint32_t test_primask;
static uint32_t test_basepri;
static int32_t test_scheduler_state;
static uint32_t test_task_ticks;
static uint32_t test_isr_ticks;
static uintptr_t test_current_task;

uint32_t open_cfw_test_cmsis_get_ipsr(void) { return test_ipsr; }
uint32_t open_cfw_test_cmsis_get_primask(void) { return test_primask; }
uint32_t open_cfw_test_cmsis_get_basepri(void) { return test_basepri; }

int32_t open_cfw_freertos_task_get_scheduler_state(void)
{
    return test_scheduler_state;
}

uint32_t open_cfw_freertos_task_get_tick_count(void)
{
    return test_task_ticks;
}

uint32_t open_cfw_freertos_task_get_tick_count_from_isr(void)
{
    return test_isr_ticks;
}

void *open_cfw_freertos_task_get_current_task_handle(void)
{
    return (void *)test_current_task;
}

#define OPEN_CFW_CMSIS_CORE_HOST_TEST 1
#include "../../components/apollo_main/core_overlay/runtime_cmsis_core_leaves.c"

void open_cfw_test_cmsis_set_context(
    uint32_t ipsr,
    uint32_t primask,
    uint32_t basepri,
    int32_t scheduler_state)
{
    test_ipsr = ipsr;
    test_primask = primask;
    test_basepri = basepri;
    test_scheduler_state = scheduler_state;
}

void open_cfw_test_cmsis_set_ticks(uint32_t task_ticks, uint32_t isr_ticks)
{
    test_task_ticks = task_ticks;
    test_isr_ticks = isr_ticks;
}

void open_cfw_test_cmsis_set_current_task(uintptr_t current_task)
{
    test_current_task = current_task;
}
