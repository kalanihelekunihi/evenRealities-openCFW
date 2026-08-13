#include <stdint.h>

static uint32_t host_irq;
static int32_t host_scheduler_state;
static int32_t host_kernel_state;
static uint32_t host_scheduler_start_calls;
static int32_t host_state_seen_by_scheduler;

#define OPEN_CFW_CMSIS_KERNEL_LIFECYCLE_STATE_WORD host_kernel_state
#include "../../components/apollo_main/core_overlay/runtime_cmsis_kernel_lifecycle.c"

uint32_t open_cfw_cmsis_irq_context(void) { return host_irq; }
int32_t open_cfw_freertos_task_get_scheduler_state(void) {
    return host_scheduler_state;
}
void open_cfw_retained_freertos_task_start_scheduler(void) {
    ++host_scheduler_start_calls;
    host_state_seen_by_scheduler = host_kernel_state;
}

void open_cfw_cmsis_kernel_lifecycle_host_reset(
    uint32_t irq, int32_t scheduler_state, int32_t kernel_state
)
{
    host_irq = irq;
    host_scheduler_state = scheduler_state;
    host_kernel_state = kernel_state;
    host_scheduler_start_calls = 0;
    host_state_seen_by_scheduler = -99;
}

int32_t open_cfw_cmsis_kernel_lifecycle_host_get(uint32_t index)
{
    const int32_t values[] = {
        host_kernel_state,
        (int32_t)host_scheduler_start_calls,
        host_state_seen_by_scheduler
    };
    return index < sizeof(values) / sizeof(values[0]) ? values[index] : -100;
}
