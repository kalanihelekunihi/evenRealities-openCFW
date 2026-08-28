#include <stdint.h>
#include <string.h>

#include "../../components/bootloader/core_overlay/runtime_hw_register_clear_422d20.c"

open_cfw_hwrc_u32 open_cfw_hwrc_host_registers[4][32];

void open_cfw_hwrc_host_reset(uint32_t value)
{
    uint32_t i, j;
    for (i = 0; i < 4U; ++i) for (j = 0; j < 32U; ++j) open_cfw_hwrc_host_registers[i][j] = value;
}
