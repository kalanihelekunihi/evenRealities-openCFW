/* SPDX-License-Identifier: MIT
 * CASE 0x08004330 serial IRQ fanout. Native callback addresses 0x40f8,
 * 0x40fa, 0x40fc, 0x40fe, 0x4324, 0x4326, and 0x46a0 are BX LR; 0x4328
 * reads base+0x40 with no retained observable result.
 */
#include <stdint.h>
extern uint32_t case_policy_adc_ready(uint32_t base); /* 0x678a */
extern uint32_t case_policy_adc_special(uint32_t base); /* 0x6792 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static uint8_t rd8(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
void case_irq_child_4330(uint32_t state)
{
    uint32_t base=rd(state),control=rd(base),status=rd(base+4u);
    if((control&status&2u)!=0u){
        if((rd(state+88u)&0x10u)==0u)wr(state+88u,rd(state+88u)|0x800u);
        wr(base,2u);
    }
    if(((control&status)&0xcu)!=0u){
        if((rd(state+88u)&0x10u)==0u)wr(state+88u,rd(state+88u)|0x200u);
        if(case_policy_adc_special(base)!=0u && rd8(state+26u)==0u && (rd(base)&8u)!=0u){
            if(case_policy_adc_ready(base)==0u){
                wr(base+4u,rd(base+4u)&~0xcu);
                wr(state+88u,(rd(state+88u)&~0x100u)|1u);
            }else{
                wr(state+88u,rd(state+88u)|0x20u);
                wr(state+92u,rd(state+92u)|1u);
            }
        }
        wr(base,12u);
    }
    if((control&status&0x80u)!=0u){
        wr(state+88u,rd(state+88u)|0x10000u);
        wr(base,0x80u);
    }
    if((control&status&0x100u)!=0u){
        wr(state+88u,rd(state+88u)|0x20000u);
        wr(base,0x100u);
    }
    if((control&status&0x200u)!=0u){
        wr(state+88u,rd(state+88u)|0x40000u);
        wr(base,0x200u);
    }
    if((control&status&0x10u)!=0u){
        if(rd(state+48u)==0u || (rd(base+12u)&3u)!=0u){
            wr(state+88u,rd(state+88u)|0x400u);
            wr(state+92u,rd(state+92u)|2u);
        }
        wr(base,0x10u);
    }
    if((control&status&0x2000u)!=0u)wr(base,0x2000u);
}
