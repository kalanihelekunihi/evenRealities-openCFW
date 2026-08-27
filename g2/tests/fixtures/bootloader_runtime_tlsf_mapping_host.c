#include <stddef.h>
#include <stdint.h>

uint32_t open_cfw_bootloader_tlsf_align_up_416b4e(
    uint32_t value,
    uint32_t alignment)
{
    return (value + (alignment - 1U)) & ~(alignment - 1U);
}

uint32_t open_cfw_bootloader_runtime_log2_4169f2(uint32_t value)
{
    uint32_t result = UINT32_MAX;
    while (value != 0U) {
        ++result;
        value >>= 1U;
    }
    return result;
}

#include "../../components/bootloader/core_overlay/runtime_tlsf_mapping_416bce.c"
