/* SPDX-License-Identifier: MIT
 * Native CASE 0x0800a01e elapsed conversion and 0xa074 timer query.
 */
#include <stdint.h>
extern uint32_t case_policy_timer_device_read(uint32_t reg,uint8_t *out,uint32_t count); /* 0x28b4 */
__attribute__((noinline)) int32_t case_policy_timer_bus_read(uint32_t reg,uint8_t *out,uint32_t count)
{
    volatile uint8_t *guard=(volatile uint8_t *)(uintptr_t)0x20000029u;
    if(*guard==0u){
        *guard=1u;
        (void)case_policy_timer_device_read(reg,out,count);
        *guard=0u;
    }
    return 0;
}
__attribute__((noinline)) void case_policy_timer_delay(uint32_t count)
{
    for(uint32_t outer=0u;outer<count;++outer)
        for(uint32_t inner=0u;inner<0x32c8u;++inner)
            __asm__ volatile("nop");
}
__attribute__((noinline)) int32_t case_policy_timer_query(uint32_t reg,uint32_t *out)
{
    uint8_t bytes[4]={0u,0u,0u,0u};
    if(case_policy_timer_bus_read(reg,bytes,2u)!=0)return -1;
    uint32_t first=((uint32_t)bytes[0]<<8)|bytes[1];
    case_policy_timer_delay(5u);
    if(case_policy_timer_bus_read(reg,bytes,2u)!=0)return -1;
    uint32_t second=((uint32_t)bytes[0]<<8)|bytes[1];
    if(first!=second){
        case_policy_timer_delay(5u);
        if(case_policy_timer_bus_read(reg,bytes,2u)!=0)return -1;
        first=((uint32_t)bytes[0]<<8)|bytes[1];
    }
    *out=first;
    return 0;
}
int32_t case_policy_elapsed(uint32_t *out)
{
    uint32_t ticks=0u;
    if(case_policy_timer_query(2u,&ticks)!=0)return -1;
    *out=(ticks+(ticks<<2))>>4;
    return 0;
}
