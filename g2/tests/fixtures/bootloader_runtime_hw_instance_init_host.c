#include <stdint.h>
#include <string.h>

#include "../../components/bootloader/core_overlay/runtime_hw_instance_init_422ad4.c"

open_cfw_hw_instance open_cfw_hw_host_instances[4];

void open_cfw_hw_host_reset(uint8_t fill)
{
    memset(open_cfw_hw_host_instances, fill, sizeof(open_cfw_hw_host_instances));
}

uint8_t *open_cfw_hw_host_instance_bytes(uint32_t index)
{
    return index < 4U ? open_cfw_hw_host_instances[index].bytes : (uint8_t *)0;
}
