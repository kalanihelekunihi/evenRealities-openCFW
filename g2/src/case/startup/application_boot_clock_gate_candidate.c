/* SPDX-License-Identifier: MIT
 * CASE 0x08005048 peripheral clock gate and bounded ready wait.
 */
#include <stdint.h>
extern uint32_t case_policy_sensor_divide(uint32_t,uint32_t); /* 0x08000160 */
/* Stock 0x08005048 (case_configure_mode_wait) */
uint32_t case_boot_clock_gate_enable(uint32_t mask)
{
    volatile uint32_t *const gate=(volatile uint32_t *)(uintptr_t)0x40007000u;
    gate[0]=(gate[0]&~0x600u)|mask;
    if(mask!=0x200u)return 0u;
    uint32_t count=case_policy_sensor_divide(
        (*(volatile uint32_t *)(uintptr_t)0x20000124u)*6u,1000000u)+1u;
    while((gate[5]&0x400u)!=0u){
        if(count==0u)return 3u;
        --count;
    }
    return 0u;
}
