/* SPDX-License-Identifier: MIT
 * Image-B DMA channel release 0x10004bc0 and forwarding entry 0x10004c7c.
 * Native 0x10004c7c forwards its live r0, despite Ghidra's void signature.
 */
#include <stdint.h>

#define DMA_STATE_BASE UINT32_C(0x2002d3e8)

extern uint32_t gx8002_image_b_irq_save_1000486c(void);
extern void gx8002_image_b_irq_restore_10004878(uint32_t previous);
extern void gx8002_image_b_platform_gate_10003be8(uint32_t module, uint32_t enabled);

void gx8002_image_b_dma_pair_10004bc0(uint32_t channel)
{
    uint32_t previous = gx8002_image_b_irq_save_1000486c();
    volatile uint8_t *state = (volatile uint8_t *)(uintptr_t)DMA_STATE_BASE;
    state[0x370u + channel] = 0u;
    uint32_t count = *(volatile uint32_t *)(uintptr_t)(DMA_STATE_BASE + 4u);
    if (count == 0u || (state[0x370u] != 1u &&
                        (count < 2u || state[0x371u] != 1u)))
        gx8002_image_b_platform_gate_10003be8(25u, 0u);
    gx8002_image_b_irq_restore_10004878(previous);
}

void gx8002_image_b_dma_release_10004c7c(uint32_t channel)
{
    gx8002_image_b_dma_pair_10004bc0(channel);
}
