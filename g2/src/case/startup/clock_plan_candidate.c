/* SPDX-License-Identifier: MIT
 * Source reduction of stock clock planner 0x08004f14 and directly reachable
 * descriptor/device setup 0x08005bda, 0x08005c28, 0x080084c0.
 * The APB prescaler shift follows the retained STM32 HAL table
 * (pre-consolidation:g2/analysis/source-discovery-parallel-2026-10-09/acquisitions/qpc-official/3rd_party/stm32f7-discovery/system_stm32f7xx.c).
 */
#include <stdint.h>
/* Stock 0x08005024 forwards to 0x080091ac, which writes priority lanes. */
/* Stock 0x080091AC (case_configure_two_bit_field) */
void case_clock_priority_config(uint32_t irq,uint32_t plan,uint32_t unused)
{
    (void)unused;
    uint32_t shift=(irq&3u)*8u,mask=0xffu<<shift,value=((plan&3u)<<6)<<shift;
    uintptr_t address;
    if((int32_t)irq>=0)address=0xe000e400u+(irq&~3u);
    else address=0xe000ed00u+((((irq&0xfu)-8u)&~3u)+0x1cu);
    volatile uint32_t *p=(volatile uint32_t *)address;
    *p=(*p&~mask)|value;
}
static volatile uint32_t *const ctl=(volatile uint32_t *)(uintptr_t)0x40021000u;
static volatile uint32_t *const port=(volatile uint32_t *)(uintptr_t)0x40021040u;
static volatile uint8_t *const descriptor=(volatile uint8_t *)(uintptr_t)0x20000f4cu;
static uint32_t word(const volatile uint8_t *p,uint32_t off)
{return (uint32_t)p[off]|((uint32_t)p[off+1]<<8)|((uint32_t)p[off+2]<<16)|((uint32_t)p[off+3]<<24);}
static void putword(volatile uint8_t *p,uint32_t off,uint32_t v)
{for(uint32_t i=0;i<4u;i++)p[off+i]=(uint8_t)(v>>(i*8u));}
static uint32_t divide_u32(uint32_t dividend,uint32_t divisor)
{uint32_t quotient=0u,remainder=0u;for(uint32_t i=0;i<32u;i++){remainder=(remainder<<1)|(dividend>>31);dividend<<=1;quotient<<=1;if(remainder>=divisor){remainder-=divisor;quotient|=1u;}}return quotient;}
static volatile uint32_t *device(uint32_t address){return (volatile uint32_t *)(uintptr_t)address;}
static uint8_t device_a(uint32_t a){return a==0x40012c00u||a==0x40000400u||a==0x40000800u;}
static uint8_t device_b(uint32_t a){return device_a(a)||a==0x40002000u||a==0x40014000u||a==0x40014400u||a==0x40014800u;}
static void case_clock_device_set(uint32_t address,const volatile uint8_t *config)
{
    volatile uint32_t *p=device(address);uint32_t v=p[0];
    if(device_a(address))v=(v&~0x70u)|word(config,4u);
    if(device_b(address))v=(v&~0x300u)|word(config,12u);
    p[0]=(v&~0x80u)|word(config,20u);
    p[11]=word(config,8u);p[10]=word(config,0u);
    if(address==0x40012c00u||address==0x40014000u||address==0x40014400u||address==0x40014800u)p[12]=word(config,16u);
    p[5]=1u;
}
static uint32_t descriptor_prepare(volatile uint8_t *d)
{
    if(d==0)return 1u;
    if(d[0x3d]==0u)d[0x3c]=0u;
    d[0x3d]=2u;
    case_clock_device_set(word(d,0u),d+4u);
    d[0x48]=1u;d[0x3e]=1u;d[0x3f]=1u;d[0x40]=1u;
    d[0x41]=1u;d[0x42]=1u;d[0x43]=1u;d[0x44]=1u;
    d[0x45]=1u;d[0x46]=1u;d[0x47]=1u;d[0x3d]=1u;
    return 0u;
}
static uint32_t descriptor_start(volatile uint8_t *d)
{
    if(d[0x3d]!=1u)return 1u;
    d[0x3d]=2u;uint32_t address=word(d,0u);volatile uint32_t *p=device(address);
    p[3]|=1u;
    if(address==0x40012c00u||address==0x40000400u||address==0x40000800u||address==0x40014000u){
        uint32_t bits=p[2]&0x10007u;
        if(bits==6u||bits==0x10000u)return 0u;
    }
    p[0]|=1u;return 0u;
}
/* Stock 0x08004F14 (case_initialize_interrupt_path) */
uint32_t case_transfer_clock_config(uint32_t plan)
{
    uint32_t prior=port[0];port[0]=prior|0x40000u;
    uint32_t prescale=(ctl[2]&0x7000u)!=0u?2u:1u;
    uint32_t index=(ctl[2]&0x7fffu)>>12;
    uint32_t shift=index<4u?0u:index-3u;
    uint32_t clock=*(volatile uint32_t *)(uintptr_t)0x20000124u;
    uint32_t ticks=divide_u32((clock>>shift)*prescale,0xf4240u);
    putword(descriptor,0u,0x40014800u);
    putword(descriptor,12u,0x3e7u);
    putword(descriptor,4u,ticks-1u);
    putword(descriptor,16u,0u);putword(descriptor,8u,0u);putword(descriptor,24u,0u);
    uint32_t status=descriptor_prepare(descriptor);
    if(status==0u){
        status=descriptor_start(descriptor);
        if(status==0u){
            *(volatile uint32_t *)(uintptr_t)0xe000e100u=1u<<22;
            if(plan<4u){case_clock_priority_config(0x16u,plan,0u);*(volatile uint32_t *)(uintptr_t)0x2000011cu=plan;}
            else status=1u;
        }
    }
    return status;
}
