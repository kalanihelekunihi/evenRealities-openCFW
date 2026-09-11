/* SPDX-License-Identifier: MIT */
#include <stdint.h>
#include "runtime_gx8002_dma_layout.h"
extern volatile uint32_t open_cfw_gx8002_dma_state[];
extern void open_cfw_gx8002_dma_resource(uint32_t,uint32_t);
extern int open_cfw_gx8002_dma_irq_handler(int, void *);
extern void open_cfw_gx8002_request_irq(int,int (*)(int,void *),void *);
void open_cfw_gx8002_dma_initialize(void)
{
    volatile uint32_t *state=open_cfw_gx8002_dma_state;
    state[0]=0xa1000000u;
    state[1]=2;
    state[218]=((uint32_t)(uintptr_t)state+23u)&~15u;
    volatile uint8_t *bytes=(volatile uint8_t *)state;
    bytes[0x370]=0;
    state[219]=((uint32_t)(uintptr_t)state+455u)&~15u;
    bytes[0x371]=0;
    open_cfw_gx8002_dma_resource(25,1);
    uint32_t base=state[0];
    *(volatile uint32_t *)(uintptr_t)(base+0x398)=0;
    *(volatile uint32_t *)(uintptr_t)(base+0x338)=UINT32_MAX;
    *(volatile uint32_t *)(uintptr_t)(base+0x340)=UINT32_MAX;
    *(volatile uint32_t *)(uintptr_t)(base+0x348)=UINT32_MAX;
    *(volatile uint32_t *)(uintptr_t)(base+0x350)=UINT32_MAX;
    *(volatile uint32_t *)(uintptr_t)(base+0x358)=UINT32_MAX;
    *(volatile uint32_t *)(uintptr_t)(base+0x398)=1;
    open_cfw_gx8002_dma_resource(25,0);
    (void)open_cfw_gx8002_request_irq(10,open_cfw_gx8002_dma_irq_handler,0);
}
