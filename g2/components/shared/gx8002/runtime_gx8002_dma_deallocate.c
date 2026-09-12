/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern volatile uint32_t open_cfw_gx8002_dma_state[];
extern uint32_t open_cfw_gx8002_irq_save(void);
extern void open_cfw_gx8002_irq_restore(uint32_t);
extern void open_cfw_gx8002_dma_resource(uint32_t,uint32_t);
void open_cfw_gx8002_dma_deallocate(uint32_t channel)
{
    uint32_t token=open_cfw_gx8002_irq_save();
    volatile uint8_t *allocation=(volatile uint8_t *)open_cfw_gx8002_dma_state+0x370;
    allocation[channel]=0;
    uint32_t count=open_cfw_gx8002_dma_state[1];
    for (;count;--count) {
        /* Unlike selection, stock checks exactly one, not any nonzero byte. */
        if (*allocation++==1) {
            open_cfw_gx8002_irq_restore(token);
            return;
        }
    }
    open_cfw_gx8002_dma_resource(25,0);
    open_cfw_gx8002_irq_restore(token);
}
