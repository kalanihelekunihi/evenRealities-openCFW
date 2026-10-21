/* SPDX-License-Identifier: MIT
 * CASE 0x08008ec4 status wait, timeout, and hardware error recovery.
 */
#include <stdint.h>
extern uint32_t case_policy_adc_tick(void); /* 0x4eac */
static uint32_t rd32(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr32(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint32_t mask(void){uint32_t v;__asm volatile("mrs %0, primask":"=r"(v));return v;}
static void setmask(uint32_t v){__asm volatile("msr primask, %0"::"r"(v):"memory");}
static void clear_locked(uint32_t a,uint32_t bits)
{uint32_t s=mask();setmask(1u);wr32(a,rd32(a)&~bits);setmask(s);}
static uint32_t fail(uint32_t descriptor,uint32_t hardware,uint32_t error)
{
    if(error!=0u)wr32(hardware+32u,2048u);
    clear_locked(hardware,0x1a0u);
    clear_locked(hardware+8u,1u);
    wr32(descriptor+136u,32u);wr32(descriptor+140u,32u);
    if(error!=0u)wr32(descriptor+144u,32u);
    *(volatile uint8_t *)(uintptr_t)(descriptor+132u)=0u;
    return 3u;
}
uint32_t case_boot_sensor_open_ready(uint32_t descriptor,uint32_t status_mask,
    uint32_t expected,uint32_t start,uint32_t timeout)
{
    for(;;){
        uint32_t hardware=rd32(descriptor);
        uint32_t actual=(status_mask&~rd32(hardware+28u))==0u?1u:0u;
        if(actual!=expected)return 0u;
        if(timeout==0xffffffffu)continue;
        if(case_policy_adc_tick()-start>timeout||timeout==0u)
            return fail(descriptor,hardware,0u);
        hardware=rd32(descriptor);
        if((rd32(hardware)&4u)!=0u && (rd32(hardware+28u)&0x800u)!=0u)
            return fail(descriptor,hardware,1u);
    }
}
