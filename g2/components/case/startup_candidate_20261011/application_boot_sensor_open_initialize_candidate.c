/* SPDX-License-Identifier: MIT
 * CASE 0x08006308 sensor clock/pin initialization for two hardware bases.
 */
#include <stdint.h>
extern uint32_t case_boot_bus_clock_setup(uint32_t *config); /* 0x5128 */
extern void case_boot_init_failure(void) __attribute__((noreturn)); /* 0x3e90 */
extern void case_bus_gpio_config(uint32_t base,volatile uint32_t *state); /* 0x4d30 */
extern void case_clock_priority_config(uint32_t irq,uint32_t plan,uint32_t unused); /* 0x5024 */
/* Native 0x500c writes the selected NVIC ISER bit for nonnegative IRQs. */
void case_boot_sensor_irq_enable(uint32_t irq)
{
    if((int32_t)irq>=0)
        *(volatile uint32_t *)(uintptr_t)0xe000e100u=1u<<(irq&31u);
}
static uint32_t rd32(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr32(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
void case_boot_sensor_open_initialize(uint32_t descriptor)
{
    volatile uint32_t clock[11],pins[5];
    for(uint32_t i=0;i<11u;++i)clock[i]=0u;
    for(uint32_t i=0;i<5u;++i)pins[i]=0u;
    uint32_t hw=rd32(descriptor);
    if(hw==0x40013800u){
        clock[0]=1u;clock[1]=2u;
        if(case_boot_bus_clock_setup((uint32_t *)(uintptr_t)clock)!=0u)case_boot_init_failure();
        wr32(0x40021040u,rd32(0x40021040u)|(1u<<14));
        wr32(0x40021034u,rd32(0x40021034u)|1u);
        pins[0]=0x600u;pins[1]=2u;pins[2]=0u;pins[3]=0u;pins[4]=1u;
        case_bus_gpio_config(0x50000000u,pins);
        case_clock_priority_config(27u,3u,0u);
        case_boot_sensor_irq_enable(27u);
    }else if(hw==0x40004800u){
        clock[0]=4u;clock[3]=0u;
        if(case_boot_bus_clock_setup((uint32_t *)(uintptr_t)clock)!=0u)case_boot_init_failure();
        wr32(0x4002103cu,rd32(0x4002103cu)|(1u<<18));
        wr32(0x40021034u,rd32(0x40021034u)|2u);
        pins[0]=0x300u;pins[1]=2u;pins[2]=0u;pins[3]=0u;pins[4]=4u;
        case_bus_gpio_config(0x50000400u,pins);
    }
}
