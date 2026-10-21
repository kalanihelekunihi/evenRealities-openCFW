/* SPDX-License-Identifier: MIT
 * CASE 0x08005128 RCC oscillator/bus clock setup. MMIO and timeout behavior
 * follow the native branch graph; clock source and peripheral values are
 * supplied by the caller's real configuration structure.
 */
#include <stdint.h>
extern uint32_t case_policy_adc_tick(void); /* 0x4eac */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
uint32_t case_boot_bus_clock_setup(uint32_t *config)
{
    uint32_t flags=config[0],result=0u,temporary_power=0u;
    const uint32_t rcc=0x40021040u,core=0x40021000u,power=0x40007000u;
    if(flags&0x00020000u){
        if((rd(core+0x3cu)&0x10000000u)==0u){
            wr(core+0x3cu,rd(core+0x3cu)|0x10000000u);
            temporary_power=1u;
        }
        wr(power,rd(power)|0x00000100u);
        uint32_t start=case_policy_adc_tick();
        while((rd(power)&0x00000100u)==0u){
            if(case_policy_adc_tick()-start>2u){result=3u;goto power_done;}
        }
        uint32_t old=rd(rcc+0x1cu)&0x300u;
        if(old!=0u && old!=config[9]){
            uint32_t control=rd(rcc+0x1cu)&~0x300u;
            wr(rcc+0x1cu,rd(rcc+0x1cu)|0x10000u);
            wr(rcc+0x1cu,rd(rcc+0x1cu)&~0x10000u);
            wr(rcc+0x1cu,control);
            if(control&1u){
                start=case_policy_adc_tick();
                while((rd(rcc+0x1cu)&2u)==0u)
                    if(case_policy_adc_tick()-start>5000u){result=3u;goto power_done;}
            }
        }
        wr(rcc+0x1cu,(rd(rcc+0x1cu)&~0x300u)|config[9]);
power_done:
        if(temporary_power)wr(core+0x3cu,rd(core+0x3cu)&~0x10000000u);
    }
    if(flags&1u)wr(rcc+0x14u,(rd(rcc+0x14u)&~3u)|config[1]);
    if(flags&2u)wr(rcc+0x14u,(rd(rcc+0x14u)&~0xcu)|config[2]);
    if(flags&4u)wr(rcc+0x14u,(rd(rcc+0x14u)&~0x30u)|config[3]);
    if(flags&0x20u)wr(rcc+0x14u,(rd(rcc+0x14u)&~0x3000u)|config[4]);
    if(flags&0x40u)wr(rcc+0x14u,(rd(rcc+0x14u)&~0xc000u)|config[5]);
    if(flags&0x4000u){
        wr(rcc+0x14u,(rd(rcc+0x14u)&~0xc0000000u)|config[8]);
        if(config[8]==0x40000000u)wr(core+12u,rd(core+12u)|0x10000u);
    }
    if(flags&0x800u){
        wr(rcc+0x18u,(rd(rcc+0x18u)&~3u)|config[6]);
        if(config[6]==1u)wr(core+12u,rd(core+12u)|0x10000u);
    }
    if(flags&0x2000u){
        wr(rcc+0x18u,(rd(rcc+0x18u)&~0xcu)|config[7]);
        if(config[7]==4u)wr(core+12u,rd(core+12u)|0x10000u);
    }
    if(flags&0x1000000u){
        wr(rcc+0x18u,(rd(rcc+0x18u)&~0x3000u)|config[10]);
        if(config[10]==0x2000u)wr(core+12u,rd(core+12u)|0x1000000u);
    }
    return result;
}
