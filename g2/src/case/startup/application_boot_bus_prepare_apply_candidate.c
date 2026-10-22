/* SPDX-License-Identifier: MIT
 * Native CASE 0x6d72/0x6db8 bus ready wait and mode application.
 */
#include <stdint.h>
extern uint32_t case_policy_adc_tick(void); /* 0x4eac */
uint32_t case_boot_bus_apply_core(uint32_t descriptor); /* 0x5b8c */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
/* Stock 0x08006D72 (case_wait_controller_ready) */
uint32_t case_boot_bus_prepare(uint32_t descriptor)
{
    uint32_t base=rd(descriptor),result=0u;
    if((rd(base+12u)&0x40u)!=0u)return 0u;
    wr(base+12u,rd(base+12u)|0x80u);
    uint32_t start=case_policy_adc_tick();
    while((rd(base+12u)&0x40u)==0u && result!=3u){
        if(case_policy_adc_tick()-start>1000u){
            result=3u;
            *(volatile uint8_t *)(uintptr_t)(descriptor+41u)=3u;
        }
    }
    return result;
}
/* Stock 0x08006DB8 (case_prepare_controller_wait) */
uint32_t case_boot_bus_apply(uint32_t descriptor)
{
    const uint32_t base=0x40002800u;
    wr(base+12u,rd(base+12u)&~0x80u);
    uint32_t was_enabled=rd(base+24u)&0x20u;
    if(was_enabled!=0u)wr(base+24u,rd(base+24u)&~0x20u);
    uint32_t result=case_boot_bus_apply_core(descriptor);
    if(result!=0u){*(volatile uint8_t *)(uintptr_t)(descriptor+41u)=3u;result=3u;}
    if(was_enabled!=0u)wr(base+24u,rd(base+24u)|0x20u);
    return result;
}
/* Stock 0x08005B8C (case_wait_status_bit5) */
uint32_t case_boot_bus_apply_core(uint32_t descriptor) /* 0x5b8c */
{
    uint32_t base=rd(descriptor);
    wr(base+12u,rd(base+12u)&~0xa0u);
    uint32_t start=case_policy_adc_tick();
    while((rd(base+12u)&0x20u)==0u){
        if(case_policy_adc_tick()-start>1000u)return 3u;
    }
    return 0u;
}
