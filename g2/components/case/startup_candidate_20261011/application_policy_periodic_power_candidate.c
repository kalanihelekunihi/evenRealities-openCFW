/* SPDX-License-Identifier: MIT
 * Native CASE 0x2cb8 -> 0xa270 timed GPIO pulse sequence.
 */
#include <stdint.h>
extern void case_control_write(uint32_t base,uint32_t mask,uint32_t enable); /* 0x4e9e */
extern void case_bus_gpio_config(uint32_t base,volatile uint32_t *state); /* 0x4d30 */
static void delay350(void)
{for(uint32_t n=0u;n<350u;++n)__asm__ volatile("nop");}
static void line_high(void)
{case_control_write(0x50000400u,4u,1u);}
static void line_low(void)
{case_control_write(0x50000400u,4u,0u);}
static void prepare_line(void)
{
    volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)0x20000014u;
    if(state[1]!=1u){state[1]=1u;case_bus_gpio_config(0x50000400u,state);}
}
void case_policy_periodic_power_check(void)
{
    line_high();
    prepare_line();
    line_high();
    delay350();
    line_low();
    for(uint32_t n=0u;n<40u;++n)delay350();
    line_high();
}
