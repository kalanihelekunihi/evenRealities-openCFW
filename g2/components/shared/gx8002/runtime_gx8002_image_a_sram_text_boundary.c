/* SPDX-License-Identifier: MIT */
/* Exact provider seam; no proprietary C-SKY body or internal ABI is included. */
#include "runtime_gx8002_image_a_sram_text_boundary.h"

int32_t open_cfw_gx8002_image_a_sram_text_load(
    const open_cfw_gx8002_image_a_sram_text_ports *ports,
    uint8_t *destination,
    size_t capacity)
{
    static const uint8_t expected[32] = {
        0x37U, 0x80U, 0xeaU, 0x0bU, 0xd9U, 0xc1U, 0x1bU, 0xb9U,
        0x4cU, 0xd7U, 0x2bU, 0xfcU, 0x6aU, 0x1eU, 0x89U, 0x24U,
        0xf2U, 0xf3U, 0xe7U, 0x2eU, 0x9aU, 0x31U, 0xecU, 0x49U,
        0xa1U, 0x85U, 0xa1U, 0x87U, 0x99U, 0xc9U, 0xa5U, 0xf8U
    };
    return open_cfw_gx8002_authenticated_segment_load(
        ports, destination, capacity, OPEN_CFW_GX8002_IMAGE_A_SRAM_TEXT_SIZE, expected);
}
