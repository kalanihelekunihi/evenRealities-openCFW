#include <stdint.h>

static volatile int32_t open_cfw_test_scheduler_running;
static volatile uint32_t open_cfw_test_scheduler_suspended;
static volatile uint32_t open_cfw_test_running_reads;
static volatile uint32_t open_cfw_test_suspended_reads;

static int32_t open_cfw_test_read_scheduler_running(void)
{
    ++open_cfw_test_running_reads;
    return open_cfw_test_scheduler_running;
}

static uint32_t open_cfw_test_read_scheduler_suspended(void)
{
    ++open_cfw_test_suspended_reads;
    return open_cfw_test_scheduler_suspended;
}

#define OPEN_CFW_FREERTOS_SCHEDULER_RUNNING \
    open_cfw_test_read_scheduler_running()
#define OPEN_CFW_FREERTOS_SCHEDULER_SUSPENDED \
    open_cfw_test_read_scheduler_suspended()

#include "../../components/apollo_main/core_overlay/runtime_freertos_scheduler_state.c"

void open_cfw_test_freertos_scheduler_state_set(
    int32_t running,
    uint32_t suspended)
{
    open_cfw_test_scheduler_running = running;
    open_cfw_test_scheduler_suspended = suspended;
    open_cfw_test_running_reads = 0U;
    open_cfw_test_suspended_reads = 0U;
}

int32_t open_cfw_test_freertos_scheduler_state_get(void)
{
    return open_cfw_freertos_task_get_scheduler_state();
}

uint32_t open_cfw_test_freertos_scheduler_state_running_reads(void)
{
    return open_cfw_test_running_reads;
}

uint32_t open_cfw_test_freertos_scheduler_state_suspended_reads(void)
{
    return open_cfw_test_suspended_reads;
}
