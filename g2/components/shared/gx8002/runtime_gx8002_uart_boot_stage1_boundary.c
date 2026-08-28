/* SPDX-License-Identifier: MIT */
/* Exact volatile boot stage-one provider; no proprietary C-SKY bytes included. */
#include "runtime_gx8002_uart_boot_stage1_boundary.h"

int32_t open_cfw_gx8002_uart_boot_stage1_load(
    const open_cfw_gx8002_uart_boot_stage1_ports *ports,
    uint8_t *destination,
    size_t capacity)
{
    static const uint8_t expected[32] = {
        0xcbU, 0xbeU, 0x85U, 0xa2U, 0xd6U, 0x0fU, 0x5bU, 0xb8U,
        0x05U, 0xddU, 0xdbU, 0x45U, 0xfaU, 0x2eU, 0xacU, 0x16U,
        0x32U, 0xbdU, 0xf0U, 0xabU, 0x80U, 0x66U, 0x5cU, 0x04U,
        0x0cU, 0x08U, 0x92U, 0xc6U, 0x40U, 0x74U, 0x13U, 0x3fU
    };
    return open_cfw_gx8002_authenticated_segment_load(
        ports, destination, capacity, OPEN_CFW_GX8002_UART_BOOT_STAGE1_SIZE, expected);
}
