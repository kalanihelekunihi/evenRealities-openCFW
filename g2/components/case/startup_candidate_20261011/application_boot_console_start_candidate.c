/* SPDX-License-Identifier: MIT
 * CASE native 0x08003fd0 ADC-backed console start and calibration.
 */
#include <stdint.h>
extern uint32_t case_policy_adc_open_config(uint32_t descriptor); /* 0x0734 */
extern uint32_t case_policy_sensor_divide(uint32_t value,uint32_t divisor); /* 0x0160 */
extern uint32_t case_policy_adc_tick(void); /* 0x4eac */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint8_t rb(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
static void wb(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
static uint32_t ready(uint32_t hw){return rd(hw+8u)&1u;}
uint32_t case_boot_console_start(uint32_t descriptor)
{
    uint32_t hw=rd(descriptor);
    if(rb(descriptor+84u)==1u)return 2u;
    wb(descriptor+84u,1u);
    uint32_t opened=case_policy_adc_open_config(descriptor);
    if(ready(hw)!=0u){
        wr(descriptor+88u,rd(descriptor+88u)|16u);
        wb(descriptor+84u,0u);
        return opened;
    }
    wr(descriptor+88u,(rd(descriptor+88u)&~0x100u)|2u);
    uint32_t previous=rd(hw+12u)&0x8003u;
    wr(hw+12u,rd(hw+12u)&~0x8003u);
    uint32_t count=0u,sum=0u;
    for(uint32_t sample=0u;sample<8u;++sample){
        wr(hw+8u,(rd(hw+8u)&~0x17u)|0x80000000u);
        while((rd(hw+8u)&0x80000000u)!=0u){
            if(++count>=0x2f200u){
                wr(descriptor+88u,(rd(descriptor+88u)&~2u)|16u);
                wb(descriptor+84u,0u);
                return 1u;
            }
        }
        sum+=(rd(hw+0xb4u)&0x7fu);
    }
    uint32_t average=case_policy_sensor_divide(sum,8u);
    wr(hw+8u,(rd(hw+8u)&0x7fffffe8u)+1u);
    wr(hw+0xb4u,(rd(hw+0xb4u)&~0x7fu)|average);
    wr(hw+8u,(rd(hw+8u)&0x7fffffe8u)+2u);
    uint32_t start=case_policy_adc_tick();
    while(ready(hw)!=0u){
        if(case_policy_adc_tick()-start>2u && ready(hw)!=0u){
            wr(descriptor+88u,rd(descriptor+88u)|16u);
            wr(descriptor+92u,rd(descriptor+92u)|1u);
            return 1u;
        }
    }
    wr(hw+12u,rd(hw+12u)|previous);
    wr(descriptor+88u,(rd(descriptor+88u)&~2u)|1u);
    wb(descriptor+84u,0u);
    return opened;
}
