#include <stdint.h>

unsigned int open_cfw_test_gpu_status_current_mode;
unsigned int open_cfw_test_gpu_status_read_calls;

void open_cfw_test_gpu_status_reset(void)
{
    open_cfw_test_gpu_status_current_mode = 0U;
    open_cfw_test_gpu_status_read_calls = 0U;
}

unsigned int open_cfw_test_gpu_status_current_mode_read(void)
{
    ++open_cfw_test_gpu_status_read_calls;
    return open_cfw_test_gpu_status_current_mode;
}

#define OPEN_CFW_PWRCTRL_GPU_STATUS_CURRENT_MODE_READ() \
    open_cfw_test_gpu_status_current_mode_read()

#include "../../components/apollo_main/core_overlay/pwrctrl_gpu_mode_status.c"
