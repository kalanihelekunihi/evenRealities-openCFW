/* SPDX-License-Identifier: MIT
 * CASE 0x08008bd8 sensor configuration validation and clock selection.
 * Native prescaler table at 0x0800d380 remains product data.
 */
#include <stdint.h>
extern const uint16_t case_boot_sensor_prescale_table[]; /* 0x0800d380 */
extern uint32_t case_boot_sensor_clock_5474(void);
extern uint32_t case_boot_sensor_clock_549c(void);
extern uint32_t case_policy_sensor_divide(uint32_t,uint32_t); /* 0x0160 */
static uint32_t rd32(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr32(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static void wr16(uint32_t a,uint16_t v){*(volatile uint16_t *)(uintptr_t)a=v;}
static uint32_t source_kind(uint32_t base)
{
    uint32_t clock=rd32(0x40021054u);
    if(base==0x40013800u){
        uint32_t mode=clock&3u;
        return mode==1u?4u:mode==2u?2u:mode==3u?8u:0u;
    }
    if(base==0x40004400u){
        uint32_t mode=clock&12u;
        return mode==4u?4u:mode==8u?2u:mode==12u?8u:0u;
    }
    if(base==0x40004800u){
        uint32_t mode=clock&48u;
        return mode==16u?4u:mode==32u?2u:mode==48u?8u:0u;
    }
    if(base==0x40004c00u||base==0x40005000u||base==0x40013c00u)return 0u;
    return 16u;
}
uint32_t case_boot_sensor_open_validate(uint32_t d)
{
    uint32_t hw=rd32(d);
    wr32(hw,(rd32(hw)&0xcfff69f3u)|rd32(d+8u)|rd32(d+16u)|rd32(d+20u)|rd32(d+28u));
    wr32(hw+4u,(rd32(hw+4u)&~0x3000u)|rd32(d+12u));
    wr32(hw+8u,(rd32(hw+8u)&0x11fff4ffu)|rd32(d+24u)|rd32(d+32u));
    wr32(hw+44u,(rd32(hw+44u)&~15u)|rd32(d+36u));
    uint32_t kind=source_kind(hw),error=0u;
    if(kind==16u)error=1u;
    else{
        uint32_t source;
        if(kind==0u)source=case_boot_sensor_clock_5474();
        else if(kind==4u)source=case_boot_sensor_clock_549c();
        else if(kind==2u)source=0x00f42400u;
        else source=0x8000u;
        if(source!=0u){
            uint32_t index=rd32(d+36u);
            uint32_t scaled=case_policy_sensor_divide(source,case_boot_sensor_prescale_table[index]);
            if(rd32(d+28u)==0x8000u)scaled<<=1;
            uint32_t denominator=rd32(d+4u);
            uint32_t count=case_policy_sensor_divide(scaled+(denominator>>1),denominator);
            if(count-16u>0xffefu)error=1u;
            else if(rd32(d+28u)==0x8000u)
                wr32(hw+12u,(count&0xfff0u)|((count&15u)>>1));
            else wr32(hw+12u,(uint16_t)count);
        }
    }
    wr16(d+106u,1u);wr16(d+104u,1u);
    wr32(d+116u,0u);wr32(d+120u,0u);
    return error;
}
