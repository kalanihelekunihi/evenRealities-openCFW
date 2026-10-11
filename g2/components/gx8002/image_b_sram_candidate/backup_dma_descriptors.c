/* SPDX-License-Identifier: MIT
 * Image-B DMA descriptor construction at 0x100048d0. Each descriptor is six
 * words; the native halfword stride table is [0xfff, 0xf001, 0, 0].
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_dma_bus_address_100051c4(uint32_t address);

void gx8002_image_b_dma_descriptors_100048d0(
    const uint32_t *parameters, uint32_t *descriptors,
    int32_t count, int32_t bytes, uint8_t scale)
{
    static const uint16_t stride_table[4] = { 0x0fffu, 0xf001u, 0u, 0u };
    uint32_t config = parameters[3];
    uint32_t source_stride = (uint32_t)scale * stride_table[(config >> 9) & 3u];
    uint32_t target_stride = (uint32_t)scale * stride_table[(config >> 7) & 3u];
    uint32_t completed = 0u;
    if (count >= 2) {
        for (int32_t i = 0; i < count - 1; ++i) {
            uint32_t *entry = descriptors + 6u * (uint32_t)i;
            entry[0] = parameters[0] + source_stride * (uint32_t)i;
            entry[1] = parameters[1] + target_stride * (uint32_t)i;
            entry[3] = config;
            entry[4] = 0x0fffu;
            entry[2] = gx8002_image_b_dma_bus_address_100051c4((uint32_t)(uintptr_t)(entry + 6));
            completed = (uint32_t)i + 1u;
        }
    } else {
        source_stride = 0u;
        target_stride = 0u;
    }
    uint32_t *last = descriptors + 6u * completed;
    last[3] = config & ~UINT32_C(0x18000000);
    int32_t remainder = bytes % 0x0fff;
    if (remainder == 0) remainder = 0x0fff;
    last[0] = parameters[0] + source_stride * completed;
    last[1] = parameters[1] + target_stride * completed;
    last[4] = (uint32_t)remainder;
    last[2] = 0u;
}
