#include <stdint.h>

uint32_t open_cfw_hwcrs_host_token;
uint32_t open_cfw_hwcrs_host_enter_count;
uint32_t open_cfw_hwcrs_host_restore_count;
uint32_t open_cfw_hwcrs_host_restored_token;
uint32_t open_cfw_hwcrs_host_memset_count;
uint32_t open_cfw_hwcrs_host_memset_length;
uint32_t open_cfw_hwcrs_host_memset_value;

uint32_t open_cfw_hwcrs_host_critical_enter(void)
{
    open_cfw_hwcrs_host_enter_count++;
    return open_cfw_hwcrs_host_token;
}

void open_cfw_hwcrs_host_critical_restore(uint32_t token)
{
    open_cfw_hwcrs_host_restore_count++;
    open_cfw_hwcrs_host_restored_token = token;
}

void open_cfw_hwcrs_host_memset(uint8_t *destination, uint32_t length, uint32_t value)
{
    uint32_t index;
    open_cfw_hwcrs_host_memset_count++;
    open_cfw_hwcrs_host_memset_length = length;
    open_cfw_hwcrs_host_memset_value = value;
    for (index = 0; index < length; index++) destination[index] = (uint8_t)value;
}

#include "../../components/bootloader/core_overlay/runtime_hw_config_release_secondary_422fa2.c"
