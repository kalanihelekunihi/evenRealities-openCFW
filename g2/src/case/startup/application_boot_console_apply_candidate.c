/* SPDX-License-Identifier: MIT
 * Native CASE 0x08004100 console pin/control configuration.
 */
#include <stdint.h>
extern uint32_t case_policy_adc_ready(uint32_t); /* 0x678a */
extern uint32_t case_policy_sensor_divide(uint32_t,uint32_t); /* 0x0160 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint8_t rb(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
static void wb(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
static void global_field(uint32_t v){const uint32_t a=0x40012708u;wr(a,(rd(a)&~0x01c00000u)|v);}
static uint32_t pin_code(uint32_t value)
{
    if((value&0x7ffffu)==0u)return (value&0x7fffffffu)>>26;
    if((value&1u)!=0u)return 0u;
    for(uint32_t bit=1u;bit<=18u;++bit)if((value&(1u<<bit))!=0u)return bit;
    return 0u;
}
/* Stock 0x08004100 (case_configure_pin_policy) */
uint32_t case_boot_console_apply(uint32_t d,const uint32_t *config)
{
    if(rb(d+84u)==1u)return 2u;
    wb(d+84u,1u);
    uint32_t base=rd(d);
    if(case_policy_adc_ready(base)!=0u){wr(d+88u,rd(d+88u)|0x20u);wb(d+84u,0u);return 1u;}
    uint32_t value=config[0],selector=config[1];
    uint32_t source=rd(d+16u);
    uint32_t special=(source==0x80000000u || source==0x80000004u);
    if(selector==2u){
        if(special)wr(base+40u,rd(base+40u)&~(value&0x7ffffu));
        if((value&0x80000000u)!=0u){
            uint32_t shift;
            if(value==0xb0001000u)shift=11u;
            else if(value==0xb8004000u)shift=10u;
            else if(value==0xb4002000u)shift=9u;
            else goto done;
            global_field((rd(0x40012708u)&0x01c00000u)&~(value<<shift));
        }
        goto done;
    }
    if(special)wr(base+40u,rd(base+40u)|(value&0x7ffffu));
    else{
        uint32_t shift=selector&31u;
        wr(d+96u,(rd(d+96u)&~(0xfu<<shift))|(pin_code(value)<<shift));
        if((selector>>2)+1u<=rd(d+28u))
            wr(base+40u,(rd(base+40u)&~(0xfu<<shift))|(((value&0x3fffffffu)>>26)<<shift));
    }
    uint32_t set=value<<8;
    wr(base+20u,(rd(base+20u)&~set)|(set&config[2]&0x07ffffffu));
    if((value&0x80000000u)!=0u){
        uint32_t global=rd(0x40012708u)&0x01c00000u;
        if(value==0xb0001000u && (global&0x00800000u)==0u){
            global_field(global|(value<<11));
            uint32_t count=(case_policy_sensor_divide(rd(0x20000124u),200000u)+1u)*12u;
            while(count!=0u)--count;
        }else if(value==0xb8004000u && (global&0x01000000u)==0u){
            global_field(global|(value<<10));
        }else if(value==0xb4002000u && (global&0x00400000u)==0u){
            global_field(global|(value<<9));
        }
    }
done:
    wb(d+84u,0u);
    return 0u;
}
