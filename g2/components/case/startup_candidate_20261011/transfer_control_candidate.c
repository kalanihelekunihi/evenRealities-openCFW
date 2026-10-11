/* SPDX-License-Identifier: MIT
 * Experimental source reduction of stock peripheral control 0x08005528.
 * Register bases, masks and timeouts come from pinned 2.2.6.10 literals.
 * The clock-plan child at 0x08004f14 remains a typed lower contract.
 */
#include <stdint.h>
extern uint32_t case_tick_word2(void); /* 0x08004eac */
extern uint32_t case_transfer_clock_config(uint32_t plan); /* 0x08004f14 */
static volatile uint32_t *const ctl=(volatile uint32_t *)(uintptr_t)0x40021000u;
static volatile uint32_t *const port=(volatile uint32_t *)(uintptr_t)0x40021040u;
static volatile uint32_t *const wake=(volatile uint32_t *)(uintptr_t)0x40007000u;
static uint32_t rd(const uint8_t *p,uint32_t off)
{return (uint32_t)p[off]|((uint32_t)p[off+1]<<8)|((uint32_t)p[off+2]<<16)|((uint32_t)p[off+3]<<24);}
static uint32_t elapsed(uint32_t start){return case_tick_word2()-start;}
static uint32_t poll_bit(volatile uint32_t *reg,uint32_t mask,uint32_t wanted,uint32_t limit)
{
    uint32_t start=case_tick_word2();
    while(((*reg&mask)!=0u)!=wanted)if(elapsed(start)>limit)return 3u;
    return 0u;
}
uint32_t case_transfer_control_5528(const uint8_t *cfg)
{
    if(cfg==0)return 1u;
    for(;;){
        uint32_t opt=cfg[0],mode=rd(cfg,4u),source=rd(cfg,8u);
        if(opt&1u){
            uint32_t range=ctl[2]&0x38u,selector=ctl[3]&3u;
            if(!((range==0x10u&&selector!=3u)||(range!=0x10u&&range!=8u))){
                if((ctl[0]&0x20000u)!=0u && mode==0u)return 1u;
            }else{
                if(mode==0x10000u)ctl[0]|=0x10000u;
                else if(mode==0x50000u)ctl[0]|=0x50000u;
                else ctl[0]&=~0x50000u;
                if(mode==0u){if(poll_bit(ctl,0x20000u,0u,100u))return 3u;}
                else if(poll_bit(ctl,0x20000u,1u,100u))return 3u;
            }
        }
        if(opt&2u){
            uint32_t range=ctl[2]&0x38u,selector=ctl[3]&3u,enable=rd(cfg,12u);
            if((range==0x10u&&selector==2u)||range==0u){
                if((ctl[0]&0x400u)!=0u && enable==0u)return 1u;
                goto reconfigure;
            }
            if(enable==0u){
                ctl[0]&=~0x100u;
                if(poll_bit(ctl,0x400u,0u,2u))return 3u;
            }else{
                ctl[0]=(ctl[0]&~0x3800u)|rd(cfg,16u)|0x100u;
                if(poll_bit(ctl,0x400u,1u,2u))return 3u;
                ctl[1]=(ctl[1]&0xffff80ffu)|(rd(cfg,20u)<<8);
            }
        }
        if(opt&8u){
            if(((ctl[2]&0x3fu)>>3)!=3u){
                uint32_t enable=rd(cfg,24u);
                if(enable==0u){port[8]&=~1u;if(poll_bit(port+8,2u,0u,2u))return 3u;}
                else{port[8]|=1u;if(poll_bit(port+8,2u,1u,2u))return 3u;}
            }else if((port[8]&2u)!=0u){if(rd(cfg,24u)==0u)return 1u;goto reconfigure;}
        }
        if(opt&4u){
            if(((ctl[2]&0x3fu)>>3)==4u){if((port[7]&2u)!=0u && source==0u)return 1u;}
            else{
                uint32_t previous=(ctl[15]&0x10000000u)==0u;
                if(previous)ctl[15]|=0x10000000u;
                if((wake[0]&0x100u)==0u){wake[0]|=(uint32_t)((uintptr_t)wake>>22);if(poll_bit(wake,0x100u,1u,2u))return 3u;}
                if(source==1u)port[7]|=1u;
                else if(source==5u)port[7]|=5u;
                else port[7]&=~5u;
                if(poll_bit(port+7,2u,source!=0u,0x1388u))return 3u;
                if(previous)ctl[15]&=~0x10000000u;
            }
        }
        uint32_t check=rd(cfg,28u);
        if(check==0u)return 0u;
        if(((ctl[2]&0x3fu)>>3)!=2u){
            ctl[0]&=~0x1000000u;
            if(poll_bit(ctl,0x2000000u,0u,2u))return 3u;
            if(check==2u){
                ctl[3]=rd(cfg,32u)|rd(cfg,36u)|(rd(cfg,40u)<<8)|rd(cfg,44u)|rd(cfg,48u)|rd(cfg,52u)|(ctl[3]&0x11c1808cu);
                ctl[0]|=0x1000000u;ctl[3]|=0x10000000u;
                if(poll_bit(ctl,0x2000000u,1u,2u))return 3u;
            }else ctl[3]&=0xeefefffcu;
            return 0u;
        }
        if(check==1u)return 1u;
        uint32_t value=ctl[3];
        if((value&3u)==rd(cfg,32u) && (value&0x70u)==rd(cfg,36u) &&
           (value&0x7f00u)==rd(cfg,40u)*0x100u &&
           (value&0x3e0000u)==rd(cfg,44u) &&
           (value&0xe000000u)==rd(cfg,48u) &&
           (value&0xe0000000u)==rd(cfg,52u))return 0u;
        return 1u;
reconfigure:
        ctl[1]=(ctl[1]&0xffff80ffu)|(rd(cfg,20u)<<8);
        if((ctl[2]&0x38u)==0u){
            ctl[0]=(ctl[0]&~0x3800u)|rd(cfg,16u);
            uint32_t divider=1u<<((ctl[0]&0x3fffu)>>11);
            *(volatile uint32_t *)(uintptr_t)0x20000124u=0xf42400u/divider;
        }
        if(case_transfer_clock_config(*(volatile uint32_t *)(uintptr_t)0x2000011cu)!=0u)return 1u;
    }
}
