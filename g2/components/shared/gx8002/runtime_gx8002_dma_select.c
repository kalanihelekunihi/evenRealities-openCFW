/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_dma_state[];
extern uint32_t open_cfw_gx8002_irq_save(void);
extern void open_cfw_gx8002_irq_restore(uint32_t);
extern void open_cfw_gx8002_dma_resource(uint32_t, uint32_t);
int open_cfw_gx8002_dma_select(void)
{
    uint32_t token=open_cfw_gx8002_irq_save();
    uint32_t count=open_cfw_gx8002_dma_state[1];
    volatile uint8_t *allocated=(volatile uint8_t *)open_cfw_gx8002_dma_state+0x370;
    for (uint32_t channel=0; channel!=count; ++channel) {
        if (!allocated[channel]) {
            allocated[channel]=1;
            open_cfw_gx8002_dma_resource(25,1);
            open_cfw_gx8002_irq_restore(token);
            return (int)channel;
        }
    }
    open_cfw_gx8002_irq_restore(token);
    return -1;
}
