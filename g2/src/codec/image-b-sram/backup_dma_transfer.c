/* SPDX-License-Identifier: MIT
 * Image-B DMA transfer 0x10004ccc. Configuration failure returns -1;
 * success enables the channel, cleans its 0x1a0-byte descriptor area,
 * starts DMA and returns zero.
 */
#include <stdint.h>

extern int32_t gx8002_image_b_dma_configure_100049d4(
    uint32_t source, uint32_t destination, int32_t bytes,
    uint32_t channel, const uint32_t *settings);
extern void gx8002_image_b_dcache_clean_range_10004e74(
    uint32_t address, int32_t length);

static uint32_t native_shift(uint32_t value, uint32_t count)
{
    __asm__ volatile ("lsl %0, %1\n" : "+r"(value) : "r"(count));
    return value;
}

int32_t gx8002_image_b_dma_transfer_10004ccc(
    uint32_t source, uint32_t destination, int32_t bytes,
    uint32_t channel, const uint32_t *settings)
{
    int32_t result = gx8002_image_b_dma_configure_100049d4(
        source, destination, bytes, channel, settings);
    if (result == -1) return result;
    volatile uint32_t *state = (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002d3e8);
    uint32_t channel_bit = native_shift(0x101u, channel);
    volatile uint32_t *registers = (volatile uint32_t *)(uintptr_t)state[0];
    registers[0x310u / 4u] = channel_bit;
    gx8002_image_b_dcache_clean_range_10004e74(state[0xdau + channel], 0x1a0);
    registers = (volatile uint32_t *)(uintptr_t)state[0];
    registers[0x3a0u / 4u] = channel_bit;
    return 0;
}
