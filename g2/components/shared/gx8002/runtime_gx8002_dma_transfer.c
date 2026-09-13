/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "gx_dma_ahb.h"
extern volatile uint32_t open_cfw_gx8002_dma_state[];
extern int open_cfw_gx8002_dma_configure(uint32_t, uint32_t, int32_t, uint32_t, volatile GX_DMA_AHB_CH_CONFIG *);
extern void open_cfw_gx8002_dma_descriptor_cache(uint32_t, uint32_t);
/* Channel is an allocated hardware channel; setup failures are exactly -1. */
int open_cfw_gx8002_dma_transfer(uint32_t destination, uint32_t source,
                              uint32_t length, uint32_t channel,
                              GX_DMA_AHB_CH_CONFIG *config)
{
    int result=open_cfw_gx8002_dma_configure(destination,source,(int32_t)length,channel,config);
    if (result==-1) return result;
    volatile uint32_t *state=open_cfw_gx8002_dma_state;
    uint32_t mask=257u<<channel;
    *(volatile uint32_t *)(uintptr_t)(state[0]+0x310)=mask;
    /* Preserve a compact word index instead of expanding byte arithmetic.
     * The empty constraint emits no instructions with the pinned compiler. */
    register uint32_t index __asm__("r5")=channel+218;
    __asm__("" : "+r"(index));
    open_cfw_gx8002_dma_descriptor_cache(state[index],416);
    *(volatile uint32_t *)(uintptr_t)(state[0]+0x3a0)=mask;
    return 0;
}
