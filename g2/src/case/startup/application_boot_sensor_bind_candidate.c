/* SPDX-License-Identifier: MIT
 * Native CASE 0x64ec sensor binding validation and IRQ-masked enable.
 */
#include <stdint.h>
extern uint32_t case_boot_sensor_bind_core(uint32_t descriptor,uint32_t channel,uint32_t enabled); /* 0x8d98 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
/* Stock 0x080064EC (case_start_context_transfer) */
uint32_t case_boot_sensor_bind(uint32_t descriptor,uint32_t channel,uint32_t enabled)
{
    if(rd(descriptor+140u)!=32u)return 2u;
    if(channel==0u || enabled==0u)return 1u;
    if(rd(descriptor+8u)==0x1000u && rd(descriptor+16u)==0u && (channel&1u)!=0u)return 1u;
    wr(descriptor+108u,0u);
    uint32_t base=rd(descriptor);
    if((rd(base+4u)&0x800000u)!=0u){
        uint32_t primask;
        __asm__ volatile("mrs %0, primask\ncpsid i":"=r"(primask)::"memory");
        wr(base,rd(base)|(1u<<26));
        __asm__ volatile("msr primask, %0"::"r"(primask):"memory");
    }
    return case_boot_sensor_bind_core(descriptor,channel,enabled);
}
