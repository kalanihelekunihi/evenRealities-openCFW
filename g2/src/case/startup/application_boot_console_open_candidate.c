/* SPDX-License-Identifier: MIT
 * Native CASE 0x08004480 console peripheral open and register plan.
 */
#include <stdint.h>
extern void case_boot_console_reset_descriptor(uint32_t); /* 0x46a4 */
extern uint32_t case_policy_sensor_divide(uint32_t,uint32_t); /* 0x0160 */
extern uint32_t case_policy_adc_ready(uint32_t); /* 0x678a */
extern uint32_t case_policy_adc_enabled(uint32_t); /* 0x677a */
extern void case_boot_console_write_field(uint32_t,uint32_t,uint32_t); /* 0x67b0 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint8_t rb(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
static void wb(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
uint32_t case_boot_console_open(uint32_t d)
{
    if(d==0u)return 1u;
    uint32_t base=rd(d);
    if(rd(d+88u)==0u){case_boot_console_reset_descriptor(d);wr(d+92u,0u);wb(d+84u,0u);}
    base=rd(d);
    uint32_t clock_was_off=(rd(base+8u)&0x10000000u)==0u;
    if(clock_was_off){
        wr(base+8u,(rd(base+8u)&0x7fffffe8u)|0x10000000u);
        uint32_t count=case_policy_sensor_divide(rd(0x20000124u),200000u)*2u+2u;
        while(count!=0u)--count;
    }
    uint32_t status=rd(d+88u),errors=rd(d+92u);
    if((rd(base+8u)&0x10000000u)==0u){status|=0x10u;errors|=1u;wr(d+88u,status);wr(d+92u,errors);}
    uint32_t ready=case_policy_adc_ready(base);
    status=rd(d+88u);
    if((status&0x10u)!=0u || ready!=0u){wr(d+88u,status|0x10u);return 1u;}
    status=(status&~0x100u)|2u;wr(d+88u,status);
    uint32_t source;
    if(case_policy_adc_enabled(base)==0u){
    uint32_t mode=rd(d+8u)|((uint32_t)rb(d+24u)<<14)|((uint32_t)rb(d+25u)<<15)|
                  ((uint32_t)rb(d+26u)<<13)|rd(d+12u);
    if(rd(d+48u)!=0u)mode|=0x1000u;
    source=rd(d+16u);
    mode|=(source&0x80000000u)!=0u?(source&0x7fffffffu):0x200000u;
    mode|=(uint32_t)rb(d+44u)<<1;
    if(rb(d+32u)==1u){
        if(rb(d+26u)==0u)mode|=0x10000u;
        else{wr(d+88u,rd(d+88u)|0x20u);wr(d+92u,rd(d+92u)|1u);}
    }
    if(rd(d+36u)!=0u)mode|=rd(d+40u)|(rd(d+36u)&0x1c0u);
    wr(base+12u,(rd(base+12u)&0xfffe0201u)|mode);
    uint32_t frame=rd(d+76u)|(rd(d+4u)&0xc0000000u);
    if(rb(d+60u)==1u)frame|=rd(d+64u)|rd(d+68u)|rd(d+72u)|((rd(d+4u)&0xc0000000u)+1u);
    wr(base+16u,(rd(base+16u)&0x1ffffc02u)|frame);
    uint32_t selector=rd(d+4u);
    if(selector!=0xc0000000u && selector!=0x40000000u && selector!=0x80000000u){
        wr(0x40012708u,(rd(0x40012708u)&0xffc3ffffu)|(selector&0x3c0000u));
    }
    }
    case_boot_console_write_field(base,0u,rd(d+52u));
    case_boot_console_write_field(base,0x07ffff04u,rd(d+56u));
    source=rd(d+16u);
    if(source==0u)wr(base+40u,rd(base+40u)|0xfffffff0u);
    else if(source==0x200000u){
        uint32_t shift=(rb(d+28u)*4u-4u)&31u;
        wr(base+40u,(0xfffffff0u<<shift)|rd(d+96u));
    }
    if((rd(base+20u)&7u)==rd(d+52u)){
        wr(d+92u,0u);wr(d+88u,(rd(d+88u)&~3u)+1u);return 0u;
    }
    wr(d+88u,(rd(d+88u)&~2u)|0x10u);wr(d+92u,rd(d+92u)|1u);
    return 1u;
}
