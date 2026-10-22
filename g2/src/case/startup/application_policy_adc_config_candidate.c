/* SPDX-License-Identifier: MIT
 * Native CASE ADC configuration 0x06d4, 0x0734, 0x07a8.
 */
#include <stdint.h>
extern uint32_t case_policy_adc_ready(uint32_t base); /* 0x678a */
extern uint32_t case_policy_adc_enabled(uint32_t base); /* 0x677a */
extern uint32_t case_policy_adc_tick(void); /* 0x4eac */
extern uint32_t case_policy_sensor_divide(uint32_t,uint32_t); /* 0x0160 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint32_t timeout_error(uint32_t handle)
{wr(handle+0x58u,rd(handle+0x58u)|0x10u);wr(handle+0x5cu,rd(handle+0x5cu)|1u);return 1u;}
/* Stock 0x080006D4 (case_wait_controller_flag2) */
uint32_t case_policy_adc_close_stop(uint32_t handle)
{
    uint32_t base=rd(handle);
    if(case_policy_adc_ready(base)==0u)return 0u;
    if((rd(base+8u)&2u)==0u)wr(base+8u,(rd(base+8u)&0x7fffffe8u)+0x10u);
    uint32_t start=case_policy_adc_tick();
    while(case_policy_adc_ready(base)!=0u){
        if(case_policy_adc_tick()-start>2u && case_policy_adc_ready(base)!=0u)
            return timeout_error(handle);
    }
    return 0u;
}
/* Stock 0x08000734 (case_start_controller_flag0) */
uint32_t case_policy_adc_close_config(uint32_t handle)
{
    uint32_t base=rd(handle);
    uint32_t initial=(rd(base+8u)>>1)&1u;
    if(case_policy_adc_enabled(base)==0u || initial!=0u)return 0u;
    if((rd(base+8u)&5u)!=1u)return timeout_error(handle);
    wr(base+8u,(rd(base+8u)&0x7fffffe8u)+2u);
    wr(base,3u);
    uint32_t start=case_policy_adc_tick();
    while(case_policy_adc_enabled(base)!=0u){
        if(case_policy_adc_tick()-start>2u && case_policy_adc_enabled(base)!=0u)
            return timeout_error(handle);
    }
    return 0u;
}
/* Stock 0x080007A8 (case_start_peripheral) */
uint32_t case_policy_adc_open_config(uint32_t handle)
{
    uint32_t base=rd(handle);
    if((rd(base+8u)&0x80000017u)!=0u)return timeout_error(handle);
    wr(base+8u,(rd(base+8u)&~0x80000017u)+1u);
    if((rd(0x40012708u)&0x00800000u)!=0u){
        uint32_t n=case_policy_sensor_divide(rd(0x20000124u),200000u)+1u;
        do{--n;}while(n!=0u);
    }
    if(*(volatile uint8_t *)(uintptr_t)(handle+0x19u)==1u)return 0u;
    uint32_t start=case_policy_adc_tick();
    while((rd(base)&1u)==0u){
        if(case_policy_adc_enabled(base)==0u)
            wr(base+8u,(rd(base+8u)&~0x80000017u)+1u);
        if(case_policy_adc_tick()-start>2u && (rd(base)&1u)==0u)
            return timeout_error(handle);
    }
    return 0u;
}
