/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800c078 SysTick divider configuration.
 */
#include <stdint.h>
extern uint32_t case_policy_sensor_divide(uint32_t,uint32_t);
void case_boot_systick_start(void)
{
    volatile uint32_t *systick=(volatile uint32_t *)(uintptr_t)0xe000e000u;
    systick[4]=0u;
    systick[6]=0u;
    uint32_t clock=*(volatile uint32_t *)(uintptr_t)0x20000124u;
    systick[5]=case_policy_sensor_divide(clock,1000u)-1u;
    systick[4]=7u;
}
