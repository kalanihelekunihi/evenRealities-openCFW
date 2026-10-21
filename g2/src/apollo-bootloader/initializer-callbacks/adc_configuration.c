/* Locked ADC context42eb74/channel42eaf6; instruction-derived reconstruction. */
#include "adc_configuration.h"
#define R(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
static uint32_t valid(uint32_t context) {
    (void)R(context+4u); /* Original read precedes NULL/magic check. */
    return context && (R(context)&0x01ffffffu)==0x01afafafu;
}
__attribute__((noinline))
uint32_t opencfw_bl_adc_context_configure(uint32_t context,const void *configuration) {
    if(!valid(context))return 2;
    uintptr_t p=(uintptr_t)configuration;
    uint32_t word=((uint32_t)B(p+1)<<16)&0x70000u;
    word|=R(p+4)&0x3ffu;
    R(0x40038040u)=word;return 0;
}
__attribute__((noinline))
uint32_t opencfw_bl_adc_configure_channel(uint32_t context,uint32_t channel,const void *configuration) {
    if(!valid(context))return 2;
    if(channel>=8u)return 5;
    uintptr_t p=(uintptr_t)configuration;
    if(R(p+4)<0x20u || R(p+4)>=0x40u)return 6;
    uint32_t word=((uint32_t)B(p)<<24)&0x7000000u;
    word|=(R(p+4)<<18)&0xfc0000u;
    word|=((uint32_t)B(p+8)<<16)&0x30000u;
    word|=((uint32_t)B(p+9)<<8)&0xf00u;
    word|=(uint32_t)B(p+10)<<1;
    word|=B(p+11);
    R(0x4003800cu+channel*4u)=word;
    R(0x2002702cu)=R(0x2002702cu)+1u;return 0;
}
