/* SPDX-License-Identifier: MIT
 * Native XIP DMA leaves 0x10203804 and 0x10203a98. Register offsets,
 * descriptor byte flags, and IRQ critical section follow stock C-SKY flow.
 */
#include <stdint.h>

extern uint32_t g2_codec_critical_save(void);
extern void g2_codec_critical_restore(uint32_t state);
extern void gx8002_resident_platform_gate_25080(uint32_t, uint32_t);

void gx8002_xip_dma_clear_10203804(uint32_t channel)
{
    volatile const uint32_t *const descriptor =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x2002e93c);
    volatile uint8_t *const registers =
        (volatile uint8_t *)(uintptr_t)*descriptor;
    uint32_t bit = 1u << (channel & 31u);
    for (uint32_t offset = 0x338u; offset <= 0x358u; offset += 8u)
        *(volatile uint32_t *)(void *)(registers + offset) = bit;
}

void gx8002_xip_dma_deallocate_10203a98(uint32_t channel)
{
    uint32_t saved = g2_codec_critical_save();
    volatile uint8_t *const descriptor =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002e93c);
    descriptor[0x370u + channel] = 0u;
    uint32_t count = *(volatile uint32_t *)(void *)(descriptor + 4u);
    uint32_t index = 0u;
    while (index < count && descriptor[0x370u + index] != 1u) ++index;
    if (index == count) gx8002_resident_platform_gate_25080(25u, 0u);
    g2_codec_critical_restore(saved);
}
