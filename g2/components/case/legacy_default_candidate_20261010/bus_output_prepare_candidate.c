/* SPDX-License-Identifier: MIT
 * Stock 0x0800a2e6 output preamble, including 40 timed cycles.
 * GPIO configuration and writes have source-owned MMIO bodies.
 */
#include <stdint.h>
extern void case_control_write(uint32_t base,uint32_t mask,uint32_t enable);
extern void case_bus_gpio_config(uint32_t base,volatile uint32_t *state);
static void high(void){case_control_write(0x50000400u,4u,1u);}
static void low(void){case_control_write(0x50000400u,4u,0u);}
static void configure(void)
{
    volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)0x20000014u;
    if(state[1]!=1u){state[1]=1u;case_bus_gpio_config(0x50000400u,state);}
}
static void delay(uint32_t cycles){for(volatile int32_t i=0;i<(int32_t)cycles;++i){}}
void case_bus_output_prepare(void)
{
    high();configure();high();low();
    for(uint32_t i=0;i<40u;++i)delay(0x15eu);
    high();
}
