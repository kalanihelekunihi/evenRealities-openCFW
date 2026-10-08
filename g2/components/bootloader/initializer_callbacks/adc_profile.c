/* Locked42f020 profile snapshot/restore and42ea68 config; native power/clock dependencies. */
#include "adc_profile.h"
#include "../platform_control/power_domains.h"
#include "../clock_manager/clock_manager.h"
#define R(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
static uint32_t valid(uint32_t context) {(void)R(context+4u);return context&&(R(context)&0x01ffffffu)==0x01afafafu;}
static const uint32_t profile_registers[12]={0x4003800c,0x40038010,0x40038014,0x40038018,0x4003801c,0x40038020,0x40038024,0x40038028,0x40038040,0x4003802c,0x40038030,0x40038200};
__attribute__((noinline))
uint32_t opencfw_bl_adc_profile_transfer(uint32_t context,uint32_t operation,uint32_t save_restore) {
    if(!valid(context))return 2;
    uint32_t op=(uint8_t)operation;uint32_t save=(uint8_t)save_restore;
    if(op==0) {
        if(save&&!B(context+0xcu))return 7;
        (void)opencfw_bl_mspi_mode_enter(15u);
        if(!save)return 0;
        uint32_t status=clock_request(4u,15u);if(status)return status;
        for(uint32_t i=0;i<11;i++)R(profile_registers[i])=R(context+0x14u+4*i);
        R(0x40038200u)=0;
        R(0x40038000u)=R(context+0x10u)&~1u;
        uint32_t enabled=B(context+0x10u)&1u;
        R(0x40038000u)=(R(0x40038000u)&~1u)|enabled;
        R(0x40038200u)=R(context+0x40u);
        B(context+0xcu)=0;return 0;
    }
    if(op==1 || op==2) {
        if(save) {
            for(uint32_t i=0;i<12;i++)R(context+0x14u+4*i)=R(profile_registers[i]);
            R(context+0x10u)=R(0x40038000u);
            B(context+0xcu)=1;
        }
        (void)clock_release(4u,15u);
        (void)opencfw_bl_mspi_mode_leave(15u);return 0;
    }
    return 6;
}
__attribute__((noinline))
uint32_t opencfw_bl_adc_apply_profile(uint32_t context,const void *profile) {
    if(!valid(context))return 2;
    uintptr_t p=(uintptr_t)profile;
    if(B(p)!=2u)return 6;
    uint32_t status=clock_request(4u,15u);if(status)return status;
    uint32_t word=((uint32_t)B(p)<<24)&0x7000000u;
    word|=((uint32_t)B(p+1)<<20)&0x100000u;
    word|=((uint32_t)B(p+2)<<19)&0x80000u;
    word|=((uint32_t)B(p+3)<<16)&0x70000u;
    word|=0x1000u;
    word|=((uint32_t)B(p+4)<<4)&0x10u;
    word|=((uint32_t)B(p+5)<<3)&8u;
    word|=((uint32_t)B(p+6)<<2)&4u;
    R(0x40038000u)=word&~1u;return 0;
}
