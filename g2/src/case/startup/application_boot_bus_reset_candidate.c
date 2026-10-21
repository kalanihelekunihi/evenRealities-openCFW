/* SPDX-License-Identifier: MIT
 * Native CASE 0x5b24 bus clock/reset, only for the 0x40002800 instance.
 */
#include <stdint.h>
extern uint32_t case_boot_bus_clock_setup(uint32_t *config); /* 0x5128 */
extern void case_boot_init_failure(void); /* 0x3e90 */
extern void case_clock_priority_config(uint32_t irq,uint32_t plan,uint32_t unused); /* 0x5024 */
void case_boot_bus_reset(uint32_t descriptor)
{
    if(*(volatile uint32_t *)(uintptr_t)descriptor!=0x40002800u)return;
    volatile uint32_t config[12];
    for(uint32_t i=0u;i<12u;++i)config[i]=0u;
    config[0]=0x20000u;config[9]=0x200u;
    if(case_boot_bus_clock_setup((uint32_t *)(void *)config)!=0u)case_boot_init_failure();
    volatile uint32_t *enable=(volatile uint32_t *)(uintptr_t)0x4002105cu;
    *enable|=0x8000u;
    volatile uint32_t *clock=(volatile uint32_t *)(uintptr_t)0x4002103cu;
    *clock|=0x400u;
    config[11]=*clock&0x400u;
    case_clock_priority_config(2u,3u,0u);
    *(volatile uint32_t *)(uintptr_t)0xe000e100u=4u;
}
