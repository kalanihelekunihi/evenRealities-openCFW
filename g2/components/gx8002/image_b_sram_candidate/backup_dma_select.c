/* SPDX-License-Identifier: MIT
 * Image-B two-channel DMA allocator 0x10004b6c.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_irq_save_1000486c(void);
extern void gx8002_image_b_irq_restore_10004878(uint32_t previous);
extern void gx8002_image_b_platform_gate_10003be8(uint32_t module, uint32_t enabled);

int32_t gx8002_image_b_dma_select_10004b6c(void)
{
    uint32_t previous = gx8002_image_b_irq_save_1000486c();
    volatile uint8_t *state = (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002d3e8);
    uint32_t count = *(volatile uint32_t *)(void *)(state + 4u);
    if (count != 0u) {
        uint32_t channel = 0u;
        if (state[0x370u] != 0u) {
            channel = 1u;
            if (count <= 1u || state[0x371u] != 0u) goto unavailable;
        }
        state[0x370u + channel] = 1u;
        gx8002_image_b_platform_gate_10003be8(25u, 1u);
        gx8002_image_b_irq_restore_10004878(previous);
        return (int32_t)channel;
    }
unavailable:
    gx8002_image_b_irq_restore_10004878(previous);
    return -1;
}
