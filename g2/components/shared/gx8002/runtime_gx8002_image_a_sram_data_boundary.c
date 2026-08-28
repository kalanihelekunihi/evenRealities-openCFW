/* SPDX-License-Identifier: MIT */
/* Exact initialized-data provider; no proprietary data content included. */
#include "runtime_gx8002_image_a_sram_data_boundary.h"
int32_t open_cfw_gx8002_image_a_sram_data_load(
    const open_cfw_gx8002_image_a_sram_data_ports *ports,uint8_t *destination,size_t capacity)
{
    static const uint8_t expected[32] = {
        0xe0U,0xa8U,0x80U,0x03U,0x90U,0x9bU,0xb4U,0x5aU,
        0xe9U,0x66U,0xbfU,0xedU,0xcbU,0xf6U,0xe2U,0x1aU,
        0x5bU,0xc8U,0x31U,0x37U,0xd2U,0x6bU,0xd3U,0x6cU,
        0x7fU,0x81U,0x11U,0x4fU,0xa0U,0x03U,0x43U,0x84U};
    return open_cfw_gx8002_authenticated_segment_load(
        ports,destination,capacity,OPEN_CFW_GX8002_IMAGE_A_SRAM_DATA_SIZE,expected);
}
