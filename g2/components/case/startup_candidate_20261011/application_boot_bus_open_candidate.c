/* SPDX-License-Identifier: MIT
 * Native CASE 0x5a74 bus driver open and register staging.
 */
#include <stdint.h>
extern void case_boot_bus_reset(uint32_t descriptor); /* 0x5b24 */
extern uint32_t case_boot_bus_prepare(uint32_t descriptor); /* 0x6d72 */
extern uint32_t case_boot_bus_apply(uint32_t descriptor); /* 0x6db8 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
uint32_t case_boot_bus_open(uint32_t descriptor)
{
    if(descriptor==0u)return 1u;
    volatile uint8_t *state=(volatile uint8_t *)(uintptr_t)(descriptor+32u);
    if(state[9]==0u){state[8]=0u;wr(descriptor+4u,0x8800u);case_boot_bus_reset(descriptor);}
    state[9]=2u;
    uint32_t base=rd(descriptor);
    if((rd(base+12u)&16u)==0u){
        wr(base+36u,202u);wr(base+36u,83u);
        uint32_t result=case_boot_bus_prepare(descriptor);
        if(result==0u){
            wr(base+24u,rd(base+24u)&0xfb8fffbfu);
            wr(base+24u,rd(base+24u)|rd(descriptor+8u)|rd(descriptor+28u)|rd(descriptor+20u));
            wr(base+16u,rd(descriptor+16u));
            wr(base+16u,rd(base+16u)|((uint32_t)*(volatile uint16_t *)(uintptr_t)(descriptor+12u)<<16));
            result=case_boot_bus_apply(descriptor);
            if(result==0u){
                wr(base+24u,rd(base+24u)&0x1fffffffu);
                wr(base+24u,rd(base+24u)|rd(descriptor+36u)|rd(descriptor+32u)|rd(descriptor+24u));
            }
        }
        wr(base+36u,255u);
        if(result!=0u)return result;
    }
    state[9]=1u;
    return 0u;
}
