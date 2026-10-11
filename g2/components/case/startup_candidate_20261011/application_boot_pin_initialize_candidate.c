/* SPDX-License-Identifier: MIT
 * CASE native 0x08006a40 GPIO and interrupt initialization sequence.
 */
#include <stdint.h>
extern void case_control_write(uint32_t base,uint32_t mask,uint32_t enable); /* 0x4e9e */
extern void case_bus_gpio_config(uint32_t base,volatile uint32_t *config); /* 0x4d30 */
extern void case_clock_priority_config(uint32_t irq,uint32_t plan,uint32_t unused); /* 0x5024 */
extern void case_boot_sensor_irq_enable(uint32_t irq); /* 0x500c */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static void configure(uint32_t base,uint32_t pins,uint32_t mode,uint32_t alt,uint32_t fourth)
{
    volatile uint32_t config[5]={pins,mode,alt,fourth,0u};
    case_bus_gpio_config(base,config);
}
void case_boot_pin_initialize(void)
{
    uint32_t clock=0x40021000u;
    wr(clock+52u,rd(clock+52u)|2u);(void)(rd(clock+52u)&2u);
    wr(clock+52u,rd(clock+52u)|4u);(void)(rd(clock+52u)&4u);
    wr(clock+52u,rd(clock+52u)|1u);(void)(rd(clock+52u)&1u);
    case_control_write(0x50000000u,0xcau,0u);
    case_control_write(0x50000400u,4u,0u);
    configure(0x50000800u,0xc040u,3u,0u,0u);
    configure(0x50000000u,1u,0x210000u,0u,0u);
    configure(0x50000000u,0xcau,1u,0u,0u);
    configure(0x50000000u,4u,0x310000u,0u,0u);
    configure(0x50000000u,0x9920u,3u,0u,0u);
    configure(0x50000400u,0xc1u,3u,0u,0u);
    configure(0x50000400u,2u,0x110000u,0u,0u);
    configure(0x50000400u,4u,1u,0u,0u);
    configure(0x50000400u,0x20u,0x310000u,0u,0u);
    for(uint32_t irq=5u;irq<=7u;++irq){
        case_clock_priority_config(irq,3u,0u);
        case_boot_sensor_irq_enable(irq);
    }
}
