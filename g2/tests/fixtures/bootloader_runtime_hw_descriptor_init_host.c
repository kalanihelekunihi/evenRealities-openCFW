#include <stdint.h>
#include <string.h>

#include "../../components/bootloader/core_overlay/runtime_hw_descriptor_init_422dc6.c"

uint32_t open_cfw_hwdi_host_call_count;
uintptr_t open_cfw_hwdi_host_descriptor[2];
uint32_t open_cfw_hwdi_host_buffer[2];
uint32_t open_cfw_hwdi_host_enabled[2];
uint32_t open_cfw_hwdi_host_value[2];

void open_cfw_hwdi_host_descriptor_init(
    open_cfw_hwdi_u8 *descriptor,
    open_cfw_hwdi_u32 buffer,
    open_cfw_hwdi_u32 enabled,
    open_cfw_hwdi_u32 value)
{
    uint32_t slot = open_cfw_hwdi_host_call_count++;
    uint32_t zero = 0U;
    if (slot < 2U) {
        open_cfw_hwdi_host_descriptor[slot] = (uintptr_t)descriptor;
        open_cfw_hwdi_host_buffer[slot] = buffer;
        open_cfw_hwdi_host_enabled[slot] = enabled;
        open_cfw_hwdi_host_value[slot] = value;
    }
    memcpy(descriptor + 0U, &zero, sizeof(zero));
    memcpy(descriptor + 4U, &zero, sizeof(zero));
    memcpy(descriptor + 8U, &zero, sizeof(zero));
    memcpy(descriptor + 12U, &value, sizeof(value));
    memcpy(descriptor + 16U, &enabled, sizeof(enabled));
    memcpy(descriptor + 20U, &buffer, sizeof(buffer));
}
