/* SPDX-License-Identifier: MIT */
/* Exact BINH stage-one block provider; no proprietary executable bytes included. */
#include "runtime_gx8002_image_b_stage1_boundary.h"

int32_t open_cfw_gx8002_image_b_stage1_load(
    const open_cfw_gx8002_image_b_stage1_ports *ports,
    uint8_t *destination,
    size_t capacity)
{
    static const uint8_t expected[32] = {
        0xa8U, 0x09U, 0x24U, 0xccU, 0xf7U, 0x82U, 0x05U, 0xefU,
        0x17U, 0x61U, 0xc4U, 0xf5U, 0x68U, 0xd4U, 0xceU, 0x31U,
        0xf9U, 0x09U, 0x63U, 0x5bU, 0xf3U, 0xadU, 0x7eU, 0xecU,
        0xfaU, 0xedU, 0x25U, 0x0aU, 0xd8U, 0x01U, 0x62U, 0x6cU
    };
    return open_cfw_gx8002_authenticated_segment_load(
        ports, destination, capacity, OPEN_CFW_GX8002_IMAGE_B_STAGE1_SIZE, expected);
}
