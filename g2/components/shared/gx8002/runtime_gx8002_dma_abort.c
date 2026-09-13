/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_dma_state[];
extern void open_cfw_gx8002_dma_clear(uint32_t);
extern void open_cfw_gx8002_dma_deallocate(uint32_t);

/* Recovered package 0xd0cc. Initialized hardware channel domain is 0/1. */
int open_cfw_gx8002_dma_abort(uint32_t channel)
{
    uint32_t base=open_cfw_gx8002_dma_state[0];
    *(volatile uint32_t *)(uintptr_t)(base+0x3a0u)=256u<<channel;
    open_cfw_gx8002_dma_clear(channel);
    open_cfw_gx8002_dma_deallocate(channel);
    return 0;
}
