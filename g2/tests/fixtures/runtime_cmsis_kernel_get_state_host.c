#include <stdint.h>

static int32_t open_cfw_test_scheduler_state;
static int32_t open_cfw_test_kernel_state;

int32_t open_cfw_freertos_task_get_scheduler_state(void)
{
    return open_cfw_test_scheduler_state;
}

#define OPEN_CFW_CMSIS_KERNEL_STATE_WORD open_cfw_test_kernel_state
#include "../../components/apollo_main/core_overlay/runtime_cmsis_kernel_get_state.c"

void open_cfw_test_cmsis_kernel_state_reset(int32_t scheduler, int32_t kernel)
{
    open_cfw_test_scheduler_state = scheduler;
    open_cfw_test_kernel_state = kernel;
}
