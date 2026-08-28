/* SPDX-License-Identifier: MIT */
/*
 * Clean-room provider seam for the exact proprietary image-B SRAM text.
 * This file contains no C-SKY firmware bytes and creates no execution route.
 */
#include "runtime_gx8002_backup_runtime_boundary.h"

int32_t open_cfw_gx8002_backup_runtime_load(
    const open_cfw_gx8002_backup_runtime_ports *ports,
    uint8_t *destination,
    size_t capacity)
{
    static const uint8_t expected[32] = {
        0xcdU, 0x2cU, 0xcdU, 0xc2U, 0xbcU, 0xa9U, 0xdeU, 0xcfU,
        0xf0U, 0xccU, 0x51U, 0x4dU, 0x3cU, 0xcaU, 0x63U, 0x17U,
        0xc2U, 0x8eU, 0xbdU, 0xbeU, 0x22U, 0x89U, 0x16U, 0x60U,
        0xf5U, 0xd9U, 0xbaU, 0x00U, 0x27U, 0x6eU, 0xcdU, 0xb3U
    };
    return open_cfw_gx8002_authenticated_segment_load(
        ports, destination, capacity, OPEN_CFW_GX8002_BACKUP_RUNTIME_SIZE, expected);
}
