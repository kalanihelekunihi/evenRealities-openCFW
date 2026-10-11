/* SPDX-License-Identifier: MIT
 * Native CASE 0x5910 start and 0x598c timing configuration.
 */
#include <stdint.h>
extern uint32_t case_policy_adc_tick(void); /* 0x4eac */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static void wr8(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
static uint32_t await_status(uint32_t base,uint32_t start)
{
    while((rd(base+12u)&4u)==0u){
        if(case_policy_adc_tick()-start>1000u)return 3u;
    }
    return 0u;
}
uint32_t case_boot_bus_start(uint32_t descriptor)
{
    uint32_t state=descriptor+32u,base=rd(descriptor);
    if(*(volatile uint8_t *)(uintptr_t)(state+8u)==1u)return 2u;
    wr8(state+8u,1u);wr8(state+9u,2u);
    wr(base+36u,202u);wr(base+36u,83u);
    wr(base+24u,rd(base+24u)&~(1u<<10));
    wr(base+24u,rd(base+24u)&~(1u<<14));
    uint32_t start=case_policy_adc_tick();
    if(await_status(base,start)!=0u){
        wr(base+36u,255u);wr8(state+9u,3u);wr8(state+8u,0u);return 3u;
    }
    wr(base+36u,255u);wr8(state+9u,1u);wr8(state+8u,0u);
    return 0u;
}
uint32_t case_boot_bus_set_frequency(uint32_t descriptor,uint32_t frequency,uint32_t width)
{
    uint32_t state=descriptor+32u,base=rd(descriptor);
    if(*(volatile uint8_t *)(uintptr_t)(state+8u)==1u)return 2u;
    wr8(state+8u,1u);wr8(state+9u,2u);
    wr(base+36u,202u);wr(base+36u,83u);
    wr(base+24u,rd(base+24u)&~(1u<<10));
    wr(base+92u,rd(base+92u)|4u);
    if((rd(0x4000280cu)&0x40u)==0u){
        uint32_t start=case_policy_adc_tick();
        if(await_status(base,start)!=0u){
            wr(base+36u,255u);wr8(state+9u,3u);wr8(state+8u,0u);return 3u;
        }
    }
    wr(base+20u,frequency);
    wr(base+24u,(rd(base+24u)&~7u)|width);
    wr(0x40021880u,rd(0x40021880u)|(1u<<19));
    wr(base+24u,rd(base+24u)|(1u<<14));
    wr(base+24u,rd(base+24u)|(1u<<10));
    wr(base+36u,255u);wr8(state+9u,1u);wr8(state+8u,0u);
    return 0u;
}
