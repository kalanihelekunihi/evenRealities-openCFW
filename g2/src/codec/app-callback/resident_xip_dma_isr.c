/* SPDX-License-Identifier: MIT
 * Native XIP 0x10203adc..0x10203b2d. Two-channel pending-bit walk,
 * clear/deallocate order, completion register and callback forwarding are
 * from direct stock instructions. DMA clear/deallocation are genuine lowers.
 */
#include <stdint.h>

extern void gx8002_xip_dma_clear_10203804(uint32_t channel);
extern void gx8002_xip_dma_deallocate_10203a98(uint32_t channel);

typedef void (*gx8002_dma_callback)(uint32_t argument);

uint32_t gx8002_xip_dma_isr_10203adc(void)
{
    volatile const uint32_t *const dma_state =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x2002e93c);
    volatile uint8_t *const registers =
        (volatile uint8_t *)(uintptr_t)*dma_state;
    uint32_t pending = *(volatile uint32_t *)(void *)(registers + 0x2e8u);
    volatile const uint32_t *const callbacks =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x20027320);
    for (uint32_t channel = 0; channel < 2u; ++channel) {
        if (((pending >> channel) & 1u) == 0u) continue;
        gx8002_xip_dma_clear_10203804(channel);
        volatile uint8_t *const current_registers =
            (volatile uint8_t *)(uintptr_t)*dma_state;
        *(volatile uint32_t *)(void *)(current_registers + 0x310u) =
            0x100u << channel;
        gx8002_xip_dma_deallocate_10203a98(channel);
        uint32_t raw = callbacks[channel];
        if (raw != 0u)
            ((gx8002_dma_callback)(uintptr_t)raw)(callbacks[2u + channel]);
    }
    return 0u;
}
