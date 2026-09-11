/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_dma_state[];
/* Channel is an allocated hardware channel (initialized domain 0, 1). */
void open_cfw_gx8002_dma_clear(uint32_t channel)
{
    uint32_t base=open_cfw_gx8002_dma_state[0];
    uint32_t mask=1u<<channel;
    *(volatile uint32_t *)(uintptr_t)(base+0x338)=mask;
    *(volatile uint32_t *)(uintptr_t)(base+0x340)=mask;
    *(volatile uint32_t *)(uintptr_t)(base+0x348)=mask;
    *(volatile uint32_t *)(uintptr_t)(base+0x350)=mask;
    *(volatile uint32_t *)(uintptr_t)(base+0x358)=mask;
}
