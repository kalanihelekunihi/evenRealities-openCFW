/* SPDX-License-Identifier: MIT
 * Native CASE 0x080062ac sensor-specific peripheral clock and IRQ stop.
 */
#include <stdint.h>
extern void case_boot_pin_config(uint32_t base,uint32_t mask); /* 0x4c1c */
extern void case_boot_irq_disable(uint32_t irq); /* 0x4fec */

void case_policy_sensor_stop(uint32_t descriptor)
{
    volatile const uint32_t *desc=(volatile const uint32_t *)(uintptr_t)descriptor;
    uint32_t base=desc[0u];
    if(base==0x40013800u){
        volatile uint32_t *clock=(volatile uint32_t *)(uintptr_t)0x40021040u;
        *clock &= ~(1u<<14u);
        case_boot_pin_config(0x50000000u,0x600u);
        case_boot_irq_disable(27u);
    }else if(base==0x40004800u){
        volatile uint32_t *clock=(volatile uint32_t *)(uintptr_t)0x40021000u;
        clock[15u] &= ~(1u<<18u);
        case_boot_pin_config(0x50000400u,0x300u);
    }
}
