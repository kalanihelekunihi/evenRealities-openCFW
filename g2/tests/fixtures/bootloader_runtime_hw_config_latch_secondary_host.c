#include <stdint.h>

uint32_t open_cfw_hwcls_host_token;
uint32_t open_cfw_hwcls_host_enter_count;
uint32_t open_cfw_hwcls_host_restore_count;
uint32_t open_cfw_hwcls_host_restored_token;

uint32_t open_cfw_hwcls_host_critical_enter(void)
{
    open_cfw_hwcls_host_enter_count++;
    return open_cfw_hwcls_host_token;
}

void open_cfw_hwcls_host_critical_restore(uint32_t token)
{
    open_cfw_hwcls_host_restore_count++;
    open_cfw_hwcls_host_restored_token = token;
}

#include "../../components/bootloader/core_overlay/runtime_hw_config_latch_secondary_422f4c.c"
