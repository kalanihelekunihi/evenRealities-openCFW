/* SPDX-License-Identifier: MIT
 * Native CASE 0x080046a4 console GPIO/IRQ one-time peripheral clock setup.
 */
#include <stdint.h>
extern void case_bus_gpio_config(uint32_t,volatile uint32_t *); /* 0x4d30 */
extern void case_clock_priority_config(uint32_t,uint32_t,uint32_t); /* 0x5024 */
extern void case_boot_sensor_irq_enable(uint32_t); /* 0x500c */
/* Stock 0x080046A4 (case_configure_irq_resource) */
void case_boot_console_reset_descriptor(uint32_t descriptor)
{
    volatile uint32_t config[6];
    for(uint32_t i=0u;i<6u;++i)config[i]=0u;
    if(*(volatile const uint32_t *)(uintptr_t)descriptor!=0x40012400u)return;
    volatile uint32_t *clock=(volatile uint32_t *)(uintptr_t)0x40021040u;
    *clock|=0x00100000u;
    config[5]=*clock&0x00100000u;
    volatile uint32_t *apb=(volatile uint32_t *)(uintptr_t)0x40021034u;
    *apb|=1u;config[5]=*apb&1u;
    config[0]=0x10u;config[1]=3u;config[2]=0u;
    case_bus_gpio_config(0x50000000u,config);
    case_clock_priority_config(12u,3u,0u);
    case_boot_sensor_irq_enable(12u);
}
