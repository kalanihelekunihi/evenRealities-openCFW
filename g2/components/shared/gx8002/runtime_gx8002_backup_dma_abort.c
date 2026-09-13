/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_dma_state[];
extern void open_cfw_gx8002_dma_deallocate(uint32_t);

/* Backup package 0x3d5c4 samples the base once for all six MMIO writes.
 * Keep acknowledgement inline: the primary helper would reload the base.
 * Initialized hardware channels are zero and one. */
int open_cfw_gx8002_backup_dma_abort(uint32_t channel)
{
    uint32_t base = open_cfw_gx8002_dma_state[0];
    uint32_t mask = 1u << channel;
    *(volatile uint32_t *)(uintptr_t)(base + 0x3a0u) = 256u << channel;
    *(volatile uint32_t *)(uintptr_t)(base + 0x338u) = mask;
    *(volatile uint32_t *)(uintptr_t)(base + 0x340u) = mask;
    *(volatile uint32_t *)(uintptr_t)(base + 0x348u) = mask;
    *(volatile uint32_t *)(uintptr_t)(base + 0x350u) = mask;
    *(volatile uint32_t *)(uintptr_t)(base + 0x358u) = mask;
    open_cfw_gx8002_dma_deallocate(channel);
    return 0;
}
