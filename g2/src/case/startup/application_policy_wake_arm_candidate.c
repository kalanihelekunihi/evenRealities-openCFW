/* SPDX-License-Identifier: MIT
 * Native CASE 0x50e8 wake configuration and architectural sleep path.
 */
#include <stdint.h>
/* Stock 0x080050E8 (HAL_PWR_EnterSLEEPMode) */
void case_policy_wake_arm(uint32_t a,uint32_t b)
{
    volatile uint32_t *power=(volatile uint32_t *)(uintptr_t)0x40007000u;
    volatile uint32_t *scr=(volatile uint32_t *)(uintptr_t)0xe000ed10u;
    *power=(*power&~7u)|(a!=0u?1u:0u);
    *scr|=4u;
    if(b==1u){
        __asm__ volatile("wfi" ::: "memory");
    }else{
        __asm__ volatile("sev\nwfe\nwfe" ::: "memory");
    }
    *scr&=~4u;
}
