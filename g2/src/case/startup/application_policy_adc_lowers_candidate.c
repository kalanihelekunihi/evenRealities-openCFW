/* SPDX-License-Identifier: MIT
 * Native CASE ADC front-end bodies: 0x4328, 0x4710, 0x47d4, 0x483c.
 */
#include <stdint.h>
extern uint32_t case_policy_adc_ready(uint32_t base); /* 0x678a */
extern uint32_t case_policy_adc_open_config(uint32_t handle); /* 0x07a8 */
extern uint32_t case_policy_adc_close_stop(uint32_t handle); /* 0x06d4 */
extern uint32_t case_policy_adc_close_config(uint32_t handle); /* 0x0734 */
extern uint32_t case_policy_adc_tick(void); /* 0x4eac */
extern uint32_t case_policy_adc_special(uint32_t base); /* 0x6792 */

static uint32_t read32(uint32_t address)
{return *(volatile uint32_t *)(uintptr_t)address;}
static void write32(uint32_t address,uint32_t value)
{*(volatile uint32_t *)(uintptr_t)address=value;}
uint32_t case_policy_adc_read(uint32_t handle)
{return read32(read32(handle)+0x40u);}

uint32_t case_policy_adc_settle(uint32_t handle,uint32_t timeout)
{
    uint32_t base=read32(handle);
    uint32_t required;
    if(read32(handle+0x14u)==8u)required=8u;
    else if((read32(base+0x0cu)&1u)!=0u){
        write32(handle+0x58u,read32(handle+0x58u)|0x20u);
        return 1u;
    }else required=4u;
    uint32_t start=case_policy_adc_tick();
    while((read32(base)&required)==0u){
        if(timeout!=0xffffffffu){
            if((case_policy_adc_tick()-start)>timeout || timeout==0u){
                if((read32(base)&required)==0u){
                    write32(handle+0x58u,read32(handle+0x58u)|4u);
                    *(volatile uint8_t *)(uintptr_t)(handle+0x54u)=0u;
                    return 3u;
                }
            }
        }
    }
    write32(handle+0x58u,read32(handle+0x58u)|0x200u);
    if(case_policy_adc_special(base)!=0u &&
       *(volatile uint8_t *)(uintptr_t)(handle+0x1au)==0u &&
       (read32(base)&8u)!=0u){
        if(case_policy_adc_ready(base)!=0u){
            write32(handle+0x58u,read32(handle+0x58u)|0x20u);
            write32(handle+0x5cu,read32(handle+0x5cu)|1u);
        }else{
            write32(base+4u,read32(base+4u)&~12u);
            write32(handle+0x58u,(read32(handle+0x58u)&~0x100u)|1u);
        }
    }
    if(*(volatile uint8_t *)(uintptr_t)(handle+0x18u)==0u)write32(base,12u);
    return 0u;
}

uint32_t case_policy_adc_open(uint32_t handle)
{
    uint32_t base=read32(handle);
    if(case_policy_adc_ready(base)!=0u)return 2u;
    volatile uint8_t *busy=(volatile uint8_t *)(uintptr_t)(handle+0x54u);
    if(*busy==1u)return 2u;
    *busy=1u;
    uint32_t status=case_policy_adc_open_config(handle);
    if(status!=0u){*busy=0u;return status;}
    write32(handle+0x58u,(read32(handle+0x58u)&0xfffff1feu)|0x100u);
    write32(handle+0x5cu,0u);
    write32(base,0x1cu);
    *busy=0u;
    write32(base+8u,(read32(base+8u)&0x7fffffe8u)+4u);
    return 0u;
}
uint32_t case_policy_adc_close(uint32_t handle)
{
    volatile uint8_t *busy=(volatile uint8_t *)(uintptr_t)(handle+0x54u);
    if(*busy==1u)return 2u;
    *busy=1u;
    uint32_t status=case_policy_adc_close_stop(handle);
    if(status==0u){
        status=case_policy_adc_close_config(handle);
        if(status==0u)write32(handle+0x58u,(read32(handle+0x58u)&~0x100u)|1u);
    }
    *busy=0u;
    return status;
}
