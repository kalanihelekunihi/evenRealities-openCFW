/* SPDX-License-Identifier: MIT
 * Stock 0x0800b53c timed one-bit response sample. GPIO at 0x50000010
 * is live external input; timeout and diagnostics are source-owned.
 */
#include <stdint.h>
extern void case_bus_gpio_config(uint32_t base,volatile uint32_t *state);
extern void case_bus_delay(uint32_t cycles);
static uint32_t pin(void)
{
    return (*(volatile uint32_t *)(uintptr_t)0x50000010u&8u)!=0u;
}
void case_bus_input_line_prepare(void)
{
    volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)0x200000a0u;
    if(state[1]!=0u){state[1]=0u;case_bus_gpio_config(0x50000000u,state);}
    if(state[2]!=1u){state[2]=1u;case_bus_gpio_config(0x50000000u,state);}
}
uint32_t case_bus_response_sample(uint32_t *sample)
{
    volatile uint32_t *diag=(volatile uint32_t *)(uintptr_t)0x2000007cu;
    diag[3]=0u;diag[4]=0u;
    uint32_t ok=1u;
    case_bus_input_line_prepare();
    for(uint32_t i=1u;;++i){
        if(i>100000u){diag[3]=1u;ok=0u;break;}
        if(pin()!=1u)break;
    }
    case_bus_delay(50u);
    uint32_t level=pin();
    uint32_t bit=(~level)&1u;
    *sample=bit;
    for(uint32_t i=1u;;++i){
        if(i>100000u){diag[4]=1u;ok=0u;break;}
        if(pin()!=0u)break;
    }
    *sample=bit;
    return ok;
}
