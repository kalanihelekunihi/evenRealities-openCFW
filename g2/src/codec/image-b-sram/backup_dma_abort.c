/* SPDX-License-Identifier: MIT
 * Image-B DMA abort 0x10004c84. Native register shift semantics are retained
 * for all channel values, avoiding C's undefined shift count >= word width.
 */
#include <stdint.h>

extern void gx8002_image_b_dma_pair_10004bc0(uint32_t channel);

static uint32_t native_shift(uint32_t value, uint32_t count)
{
    __asm__ volatile ("lsl %0, %1\n" : "+r"(value) : "r"(count));
    return value;
}

uint32_t gx8002_image_b_dma_abort_10004c84(uint32_t channel)
{
    uintptr_t base = *(volatile uint32_t *)(uintptr_t)UINT32_C(0x2002d3e8);
    volatile uint32_t *registers = (volatile uint32_t *)base;
    uint32_t request = native_shift(1u, channel);
    uint32_t control = native_shift(0x100u, channel);
    registers[0x3a0u / 4u] = control;
    registers[0x338u / 4u] = request;
    registers[0x340u / 4u] = request;
    registers[0x348u / 4u] = request;
    registers[0x350u / 4u] = request;
    registers[0x358u / 4u] = request;
    gx8002_image_b_dma_pair_10004bc0(channel);
    return 0u;
}
