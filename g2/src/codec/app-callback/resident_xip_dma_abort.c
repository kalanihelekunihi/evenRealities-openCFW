/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10203b40..0x10203b5f. The C-SKY register shift is
 * retained for its full input domain, followed by selected clear/deallocate.
 */
#include <stdint.h>

extern void gx8002_xip_dma_clear_10203804(uint32_t channel);
extern void gx8002_xip_dma_deallocate_10203a98(uint32_t channel);

uint32_t gx8002_xip_dma_abort_10203b40(uint32_t channel)
{
    volatile const uint32_t *const descriptor =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x2002e93c);
    volatile uint8_t *const registers =
        (volatile uint8_t *)(uintptr_t)*descriptor;
    uint32_t mask = UINT32_C(0x100);
    __asm__ volatile("lsl %0, %1" : "+r"(mask) : "r"(channel) : "cc");
    *(volatile uint32_t *)(void *)(registers + 0x3a0u) = mask;
    gx8002_xip_dma_clear_10203804(channel);
    gx8002_xip_dma_deallocate_10203a98(channel);
    return 0u;
}
