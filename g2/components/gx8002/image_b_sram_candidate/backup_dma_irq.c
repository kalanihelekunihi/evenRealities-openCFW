/* SPDX-License-Identifier: MIT
 * Image-B two-channel DMA IRQ at 0x10004c04. Native order: sample pending
 * once, clear five channel flags, write control, release, then callback.
 */
#include <stdint.h>

extern void gx8002_image_b_dma_pair_10004bc0(uint32_t channel);

typedef void (*dma_callback_t)(uint32_t context);

int32_t gx8002_image_b_dma_irq_10004c04(int32_t line, void *context)
{
    (void)line;
    (void)context;
    volatile uint32_t *dma_state = (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002d3e8);
    volatile uint32_t *registers = (volatile uint32_t *)(uintptr_t)dma_state[0];
    uint32_t pending = registers[0x2e8u / 4u];
    volatile uint32_t *slots = (volatile uint32_t *)(uintptr_t)UINT32_C(0x200174a8);
    for (uint32_t channel = 0u; channel < 2u; ++channel) {
        if (((pending >> channel) & 1u) == 0u) continue;
        registers = (volatile uint32_t *)(uintptr_t)dma_state[0];
        uint32_t flag = 1u << channel;
        registers[0x338u / 4u] = flag;
        registers[0x340u / 4u] = flag;
        registers[0x348u / 4u] = flag;
        registers[0x350u / 4u] = flag;
        registers[0x358u / 4u] = flag;
        registers[0x310u / 4u] = 0x100u << channel;
        gx8002_image_b_dma_pair_10004bc0(channel);
        dma_callback_t callback = (dma_callback_t)(uintptr_t)slots[channel];
        if (callback) callback(slots[channel + 2u]);
    }
    return 0u;
}
