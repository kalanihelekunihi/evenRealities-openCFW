#include <stdint.h>
#include "native_battery_memory.h"
extern volatile uint8_t r1_battery_runtime_context[];
extern uint32_t r1_stock_dispatch_08(uint32_t);
extern uint32_t r1_stock_dispatch_0c(uint32_t);
extern uint32_t r1_stock_dispatch_10(uint32_t,uint32_t,volatile void *,uint32_t);
extern void nrf_delay_ms(uint32_t);
extern uint32_t osDelay(uint32_t);
/* Native0x91184 seeds its temporary word from incoming r0 and clears only
 * the low half. Keep this register boundary explicit without inventing a
 * semantic argument for callers. Other compilers/LTO require revalidation. */
__attribute__((noinline)) uint32_t r1_battery_five_sample_filter_and_conversion(void)
{
    uint32_t incoming;
    __asm__ volatile("mov %0, r0" : "=r"(incoming));
    volatile uint32_t word=incoming&0xffff0000u;
    uint16_t samples[6]={0};
    uint32_t sum=0;
    (void)r1_stock_dispatch_08(read32(r1_battery_runtime_context+16));
    for (uint32_t i=0;i<5;i++) {
        (void)r1_stock_dispatch_10(read32(r1_battery_runtime_context+16),0,&word,1);
        uint16_t sample=(uint16_t)word;
        samples[i]=sample;sum+=sample;
        word&=0xffff0000u;
        if (r1_battery_runtime_context[1]) (void)osDelay(2);
        else nrf_delay_ms(2);
    }
    (void)r1_stock_dispatch_0c(read32(r1_battery_runtime_context+16));
    uint32_t first=0xffffu,second=0xffffu;
    for (uint32_t i=0;i<5;i++) {
        uint32_t sample=samples[i];
        if (sample<first) { second=first;first=sample; }
        else if (sample<second) second=sample;
    }
    uint32_t average=(uint16_t)((sum-first-second)/3u);
    return (uint16_t)((average*292u*2989u)/0x79d38u);
}
