/* SPDX-License-Identifier: MIT
 * Native CASE 0x3f6c option controller wait and error flag clearing.
 */
#include <stdint.h>
extern uint32_t case_policy_adc_tick(void); /* 0x4eac shared timer */
static uint32_t status(void)
{return *(volatile uint32_t *)(uintptr_t)0x40022010u;}
uint32_t case_boot_option_wait(uint32_t ticks)
{
    uint32_t deadline=case_policy_adc_tick()+ticks;
    while((status()&0x30000u)!=0u){
        if(case_policy_adc_tick()>=deadline)return 3u;
    }
    uint32_t errors=status()&0x83fau;
    *(volatile uint32_t *)(uintptr_t)0x40022010u=0x883fbu;
    if(errors!=0u){
        *(volatile uint32_t *)(uintptr_t)0x20000f9cu=errors;
        return 1u;
    }
    deadline=case_policy_adc_tick()+ticks;
    while((status()&0x40000u)!=0u){
        if(case_policy_adc_tick()>=deadline)return 3u;
    }
    return 0u;
}
