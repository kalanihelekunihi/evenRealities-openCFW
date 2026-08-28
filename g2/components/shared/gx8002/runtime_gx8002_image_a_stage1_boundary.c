/* SPDX-License-Identifier: MIT */
/* Exact BINH stage-one block provider; no proprietary executable bytes included. */
#include "runtime_gx8002_image_a_stage1_boundary.h"

int32_t open_cfw_gx8002_image_a_stage1_load(
    const open_cfw_gx8002_image_a_stage1_ports *ports,
    uint8_t *destination,
    size_t capacity)
{
    static const uint8_t expected[32] = {
        0x95U, 0x46U, 0x16U, 0x4fU, 0x32U, 0x68U, 0x0dU, 0xe4U,
        0x7fU, 0xa9U, 0x9bU, 0xa8U, 0x5bU, 0xa0U, 0x8aU, 0x3cU,
        0x53U, 0x88U, 0x22U, 0x26U, 0x09U, 0x57U, 0xdeU, 0x6cU,
        0x1bU, 0xaeU, 0xe7U, 0x72U, 0x63U, 0x8dU, 0xa4U, 0x64U
    };
    return open_cfw_gx8002_authenticated_segment_load(
        ports, destination, capacity, OPEN_CFW_GX8002_IMAGE_A_STAGE1_SIZE, expected);
}
