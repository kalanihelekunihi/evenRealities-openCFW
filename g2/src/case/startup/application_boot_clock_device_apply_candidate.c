/* SPDX-License-Identifier: MIT
 * CASE 0x080052e4 system clock switch and flash latency application.
 * Runtime clock and AHB prescaler use source-owned 0x549c and typed ST table.
 */
#include <stdint.h>
extern uint32_t case_policy_adc_tick(void); /* 0x4eac */
extern uint32_t case_boot_sensor_clock_549c(void); /* 0x549c */
extern uint32_t case_transfer_clock_config(uint32_t plan); /* 0x4f14 */
extern const uint32_t case_boot_ahb_shift_table[16]; /* 0xd3a8 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
/* Stock 0x080052E4 (case_configure_clock_path) */
uint32_t case_boot_clock_device_apply(const uint32_t *config,uint32_t latency)
{
    if(config==0)return 1u;
    const uint32_t flash=0x40022000u,rcc=0x40021000u;
    if((rd(flash)&7u)<latency){
        wr(flash,(rd(flash)&~7u)|latency);
        uint32_t start=case_policy_adc_tick();
        while((rd(flash)&7u)!=latency)
            if(case_policy_adc_tick()-start>5000u)return 3u;
    }
    uint32_t fields=config[0];
    if(fields&2u){
        if(fields&4u)wr(rcc+8u,rd(rcc+8u)|0x7000u);
        wr(rcc+8u,(rd(rcc+8u)&~0xf00u)|config[2]);
    }
    if(fields&1u){
        uint32_t source=config[1],ready;
        if(source==0u)ready=rd(rcc)&0x400u;
        else if(source==1u)ready=rd(rcc)&0x20000u;
        else if(source==2u)ready=rd(rcc)&0x2000000u;
        else if(source==3u)ready=rd(rcc+0x60u)&2u;
        else ready=rd(rcc+0x5cu)&2u;
        if(ready==0u)return 1u;
        wr(rcc+8u,(rd(rcc+8u)&~7u)|source);
        uint32_t start=case_policy_adc_tick();
        while((rd(rcc+8u)&0x38u)!=(source<<3u))
            if(case_policy_adc_tick()-start>5000u)return 3u;
    }
    if((rd(flash)&7u)>latency){
        wr(flash,(rd(flash)&~7u)|latency);
        uint32_t start=case_policy_adc_tick();
        while((rd(flash)&7u)!=latency)
            if(case_policy_adc_tick()-start>5000u)return 3u;
    }
    if(fields&4u)wr(rcc+8u,(rd(rcc+8u)&~0x7000u)|config[3]);
    uint32_t clock=case_boot_sensor_clock_549c();
    uint32_t ahb_index=(rd(rcc+8u)>>8u)&15u;
    wr(0x20000124u,clock>>case_boot_ahb_shift_table[ahb_index]);
    return case_transfer_clock_config(rd(0x2000011cu));
}
