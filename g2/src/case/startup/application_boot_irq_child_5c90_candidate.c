/* SPDX-License-Identifier: MIT
 * CASE 0x08005c90 timer IRQ fanout. Event callbacks 0x5c8c, 0x5e14,
 * 0x5e16, 0x5bd4, 0x5bd6, 0x5bd8, and 0x5e2c are native BX LR.
 * The 0x5e18 update child invokes a real RAM tick accumulation only for
 * timer base 0x40014800.
 */
#include <stdint.h>
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static void wr8(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
void case_irq_child_5c90(uint32_t state)
{
    uint32_t base=rd(state);
    for(uint32_t i=0u;i<4u;i++){
        uint32_t bit=1u<<(i+1u);
        if((rd(base+16u)&rd(base+12u)&bit)==0u)continue;
        wr(base+16u,~bit);
        wr8(state+28u,(uint8_t)(1u<<i));
        /* The selected callback is BX LR for both output modes. */
        wr8(state+28u,0u);
    }
    if((rd(base+16u)&rd(base+12u)&1u)!=0u){
        wr(base+16u,~1u);
        if(base==0x40014800u){
            uint32_t accum=0x20000118u;
            wr(accum+8u,rd(accum+8u)+*(volatile uint8_t *)(uintptr_t)accum);
        }
    }
    if((rd(base+16u)&rd(base+12u)&0x80u)!=0u)wr(base+16u,~0x80u);
    if((rd(base+16u)&0x100u)!=0u && (rd(base+12u)&0x80u)!=0u)
        wr(base+16u,~0x100u);
    if((rd(base+16u)&rd(base+12u)&0x40u)!=0u)wr(base+16u,~0x40u);
    if((rd(base+16u)&rd(base+12u)&0x20u)!=0u)wr(base+16u,~0x20u);
}
