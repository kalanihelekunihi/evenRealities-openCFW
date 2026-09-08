/* SPDX-License-Identifier: MIT */
/* Recovered getinfo/gettype interface. Selector order is identified by the
 * pinned NationalChip gx_flash_info enum; behavior comes from stock code. */
#include <stdint.h>
#include "runtime_gx8002_flash_state.h"
int open_cfw_gx8002_flash_getinfo(unsigned selector)
{
    switch (selector) {
    case 0: case 12: return 0;
    case 1: return *(volatile uint32_t *)(uintptr_t)open_cfw_gx8002_flash_state.selected_device;
    case 2: return *(volatile uint32_t *)((uintptr_t)open_cfw_gx8002_flash_state.selected_device+4);
    case 3: return open_cfw_gx8002_flash_state.usable_bytes;
    case 4: case 6: case 10: return 4096;
    case 5: case 7: case 11: return open_cfw_gx8002_flash_state.usable_bytes>>12;
    case 8: return 256;
    case 13: return 1;
    default: return -1;
    }
}
char *open_cfw_gx8002_flash_gettype(void)
{
    return (char *)(uintptr_t)*(volatile uint32_t *)(uintptr_t)open_cfw_gx8002_flash_state.selected_device;
}
