/* SPDX-License-Identifier: MIT */
/* Exact initialized-data provider; no proprietary data content included. */
#include "runtime_gx8002_image_b_sram_data_boundary.h"
int32_t open_cfw_gx8002_image_b_sram_data_load(
    const open_cfw_gx8002_image_b_sram_data_ports *ports,uint8_t *destination,size_t capacity)
{
    static const uint8_t expected[32] = {
        0x4bU,0x69U,0x43U,0x44U,0xb5U,0x09U,0x69U,0xd1U,
        0xe2U,0x11U,0x4dU,0x93U,0x24U,0xcbU,0xd5U,0x33U,
        0x74U,0xafU,0x3dU,0xd0U,0x73U,0x75U,0x61U,0x4aU,
        0x52U,0x57U,0xf1U,0x8fU,0x32U,0x13U,0xf8U,0x84U};
    return open_cfw_gx8002_authenticated_segment_load(
        ports,destination,capacity,OPEN_CFW_GX8002_IMAGE_B_SRAM_DATA_SIZE,expected);
}
