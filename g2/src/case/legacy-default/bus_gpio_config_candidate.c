/* SPDX-License-Identifier: MIT
 * Stock 0x08004d30 pin configuration register updates. Configuration words
 * remain runtime RAM data and peripheral effects require target validation.
 */
#include <stdint.h>
static uint32_t lsl32(uint32_t value,uint32_t shift){return shift<32u?value<<shift:0u;}
/* Stock 0x08004D30 (case_bus_gpio_config) */
void case_bus_gpio_config(uint32_t base,volatile uint32_t *state)
{
    volatile uint32_t *port=(volatile uint32_t *)(uintptr_t)base;
    volatile uint32_t *sys=(volatile uint32_t *)(uintptr_t)0x40021800u;
    uint32_t mask=state[0],settings=state[1];
    for(uint32_t bit=0;bit<32u && (mask>>bit)!=0u;++bit){
        uint32_t one=1u<<bit;
        if((mask&one)==0u)continue;
        uint32_t mode=settings&3u;
        uint32_t shift=bit*2u;
        if(mode==1u||mode==2u){
            port[2]=(lsl32(state[3],shift))|(port[2]&~(lsl32(3u,shift)));
            port[1]=lsl32(((settings&0x1fu)>>4),bit)|(port[1]&~one);
        }
        if(((~settings)&3u)!=0u)
            port[3]=(lsl32(state[2],shift))|(port[3]&~(lsl32(3u,shift)));
        if(mode==2u){
            uint32_t afshift=(bit&7u)*4u;
            volatile uint32_t *af=&port[8u+(bit>>3)];
            *af=(lsl32(state[4],afshift))|(*af&~(lsl32(0xfu,afshift)));
        }
        port[0]=(lsl32(mode,shift))|(port[0]&~(lsl32(3u,shift)));
        if((settings&0x30000u)!=0u){
            uint32_t selection;
            if(base==0x50000000u)selection=0u;
            else if(base==0x50000400u)selection=1u;
            else if(base==0x50000800u)selection=2u;
            else if(base==0x50000c00u)selection=3u;
            else if(base==0x50001000u)selection=4u;
            else selection=5u;
            uint32_t sysidx=0x60u/4u+(bit&~3u)/4u;
            uint32_t sysshift=(bit&3u)*8u;
            sys[sysidx]=(lsl32(selection,sysshift))|(sys[sysidx]&~(lsl32(0xfu,sysshift)));
            uint32_t newword=(sys[0]&~one)|((settings&(1u<<20))?one:0u);
            sys[0]=newword;
            newword=(sys[1]&~one)|((settings&(1u<<21))?one:0u);
            sys[1]=newword;
            newword=(sys[0x21]&~one)|((settings&(1u<<17))?one:0u);
            sys[0x21]=newword;
            newword=(sys[0x20]&~one)|((settings&(1u<<16))?one:0u);
            sys[0x20]=newword;
        }
    }
}
