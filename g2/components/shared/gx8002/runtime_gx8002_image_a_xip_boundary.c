/* SPDX-License-Identifier: MIT */
/*
 * Exact byte-provider seam for proprietary image-A C-SKY XIP text.
 * No firmware body, internal ABI, runtime mapping, or production route exists here.
 */
#include "runtime_gx8002_image_a_xip_boundary.h"

int32_t open_cfw_gx8002_image_a_xip_load(
    const open_cfw_gx8002_image_a_xip_ports *ports,
    uint8_t *destination,
    size_t capacity)
{
    static const uint8_t expected[32] = {
        0x49U, 0xc9U, 0xaeU, 0xd0U, 0x12U, 0x64U, 0x93U, 0x22U,
        0x0aU, 0x3eU, 0x48U, 0x82U, 0x7cU, 0x26U, 0x7dU, 0x5eU,
        0x94U, 0xf6U, 0x4dU, 0x51U, 0xd9U, 0xedU, 0xe0U, 0xccU,
        0xc3U, 0xe8U, 0x4bU, 0x89U, 0x46U, 0x74U, 0x45U, 0x84U
    };
    return open_cfw_gx8002_authenticated_segment_load(
        ports, destination, capacity, OPEN_CFW_GX8002_IMAGE_A_XIP_SIZE, expected);
}
