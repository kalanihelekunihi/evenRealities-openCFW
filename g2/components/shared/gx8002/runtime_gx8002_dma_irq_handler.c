/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_dma_state[];
extern volatile uint32_t open_cfw_gx8002_dma_callbacks[];
extern void open_cfw_gx8002_dma_clear(uint32_t);
extern void open_cfw_gx8002_dma_deallocate(uint32_t);
/* The device status is sampled once; callbacks may alter later channel slots.
 * The stock handler visits exactly two channels, independently of state.count. */
int open_cfw_gx8002_dma_irq_handler(int irq, void *argument)
{
    (void)irq;
    (void)argument;
    uint32_t device=open_cfw_gx8002_dma_state[0];
    uint32_t pending=*(volatile uint32_t *)(uintptr_t)(device+0x2e8u);
    for (uint32_t channel=0;channel<2;channel++) {
        if (((pending>>channel)&1u)==0) continue;
        open_cfw_gx8002_dma_clear(channel);
        device=open_cfw_gx8002_dma_state[0];
        *(volatile uint32_t *)(uintptr_t)(device+0x310u)=256u<<channel;
        open_cfw_gx8002_dma_deallocate(channel);
        uint32_t callback=open_cfw_gx8002_dma_callbacks[channel];
        if (callback) {
            uint32_t private_data=open_cfw_gx8002_dma_callbacks[channel+2];
            ((void (*)(void *))(uintptr_t)callback)((void *)(uintptr_t)private_data);
        }
    }
    return 0;
}
