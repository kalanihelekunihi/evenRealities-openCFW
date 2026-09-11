/* SPDX-License-Identifier: MIT */
#include <stdint.h>
/* Stock package 0xd1ec: translate the two RAM aliases, preserve other addresses. */
uint32_t open_cfw_gx8002_dma_bus_address(uint32_t address)
{
    if (address-0x10000000u <= 0x1fffffffu)
        address &= 0x0fffffffu;
    return address;
}
