/* SPDX-License-Identifier: MIT
 * Stock positive-channel 0x0800a1ac/0x0800a1e8 are the two
 * constant-delay forms composed by 0x0800a188. Also 0x0800a224/0x0800a2a2 and
 * response wrapper 0x0800c42c. GPIO state is live; sampler stays imported.
 */
#include <stdint.h>
extern void case_control_write(uint32_t,uint32_t,uint32_t);
extern void case_bus_gpio_config(uint32_t,volatile uint32_t *);
extern uint32_t case_bus_positive_sample(uint32_t *bit); /* 0x0800b4e0 */
static void high(void){case_control_write(0x50000400u,4u,1u);}
static void low(void){case_control_write(0x50000400u,4u,0u);}
static void configure(void)
{
    volatile uint32_t *state=(volatile uint32_t *)(uintptr_t)0x20000014u;
    if(state[1]!=1u){state[1]=1u;case_bus_gpio_config(0x50000400u,state);}
}
static void delay(uint32_t n){for(volatile int32_t i=0;i<(int32_t)n;++i){}}
void case_bus_output_start(uint32_t bit)
{
    high();configure();high();low();delay(bit?0x5au:0x17u);high();
}
void case_bus_output_finish(void)
{
    high();configure();high();delay(0x17u);low();delay(0x15eu);high();
}
void case_bus_output_send(uint32_t value,uint32_t first)
{
    uint32_t bit=first==1u?6u:7u;
    do{case_bus_output_start((value>>bit)&1u);--bit;}while((int32_t)bit>=0);
}
uint32_t case_bus_output_poll(uint32_t *word)
{
    uint32_t bit=0u;
    uint32_t result=case_bus_positive_sample(&bit);
    *word=bit;
    return result;
}
