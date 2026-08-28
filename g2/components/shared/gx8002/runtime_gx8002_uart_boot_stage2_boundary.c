/* SPDX-License-Identifier: MIT */
/*
 * Exact byte-provider seam for the proprietary volatile UART boot stage two.
 * No C-SKY body, internal ABI, execution route, or redistribution grant is included.
 */
#include "runtime_gx8002_uart_boot_stage2_boundary.h"

int32_t open_cfw_gx8002_uart_boot_stage2_load(
    const open_cfw_gx8002_uart_boot_stage2_ports *ports,
    uint8_t *destination,
    size_t capacity)
{
    static const uint8_t expected[32] = {
        0x4aU, 0xacU, 0xc9U, 0xe5U, 0xbfU, 0x45U, 0x00U, 0x1bU,
        0xefU, 0x99U, 0x78U, 0x5bU, 0x62U, 0x30U, 0x2eU, 0x88U,
        0xbdU, 0x0bU, 0x5eU, 0x6bU, 0xf4U, 0xd6U, 0x18U, 0x6fU,
        0xd7U, 0x03U, 0x3bU, 0x1eU, 0xaeU, 0xb0U, 0x5bU, 0x0dU
    };
    return open_cfw_gx8002_authenticated_segment_load(
        ports, destination, capacity, OPEN_CFW_GX8002_UART_BOOT_STAGE2_SIZE, expected);
}
