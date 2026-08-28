#include <stdint.h>

#include "../../components/bootloader/core_overlay/runtime_bit_run_helpers_41ff60.c"

uint32_t open_cfw_bit_run_fixture_length(uint32_t value)
{
    return open_cfw_bootloader_longest_ones_run_41ff60(&value);
}

uint32_t open_cfw_bit_run_fixture_center(uint32_t value)
{
    return open_cfw_bootloader_longest_ones_center_41ff74(&value);
}
