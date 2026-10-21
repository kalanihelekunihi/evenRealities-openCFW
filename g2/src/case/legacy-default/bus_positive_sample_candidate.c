/* SPDX-License-Identifier: MIT
 * Stock 0x0800b4e0 positive-channel response bit and timeout. Live GPIO
 * input at 0x50000410 is the external device boundary.
 */
#include <stdint.h>
extern void case_bus_gpio_config(uint32_t,volatile uint32_t *);
extern void case_control_write(uint32_t,uint32_t,uint32_t);
static void configure(volatile uint32_t *state,uint32_t index,uint32_t mode)
{
    if(state[index]!=mode){state[index]=mode;case_bus_gpio_config(0x50000400u,state);}
}
static uint32_t pin(void){return (*(volatile uint32_t *)(uintptr_t)0x50000410u&4u)!=0u;}
uint32_t case_bus_positive_sample(uint32_t *sample)
{
    volatile uint32_t *diag=(volatile uint32_t *)(uintptr_t)0x20000000u;
    volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)0x20000014u;
    diag[2]=0u;diag[3]=0u;
    configure(state,2u,1u);
    case_control_write(0x50000400u,4u,1u);
    configure(state,1u,1u);
    case_control_write(0x50000400u,4u,1u);
    case_control_write(0x50000400u,4u,0u);
    configure(state,1u,0u);
    for(volatile int32_t i=0;i<0x17;++i){}
    *sample=(~pin())&1u;
    for(uint32_t i=1u;;++i){
        if(i>10000u){diag[3]=1u;return 0u;}
        if(pin()!=0u)return 1u;
    }
}
