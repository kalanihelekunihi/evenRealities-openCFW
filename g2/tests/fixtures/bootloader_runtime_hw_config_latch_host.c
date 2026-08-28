#include <stdint.h>

#include "../../components/bootloader/core_overlay/runtime_hw_config_latch_422ee2.c"

uint32_t open_cfw_hwcl_host_token;
uint32_t open_cfw_hwcl_host_enter_count;
uint32_t open_cfw_hwcl_host_restore_count;
uint32_t open_cfw_hwcl_host_restored_token;

open_cfw_hwcl_u32 open_cfw_hwcl_host_critical_enter(void)
{
    open_cfw_hwcl_host_enter_count++;
    return open_cfw_hwcl_host_token;
}

void open_cfw_hwcl_host_critical_restore(open_cfw_hwcl_u32 token)
{
    open_cfw_hwcl_host_restore_count++;
    open_cfw_hwcl_host_restored_token = token;
}
