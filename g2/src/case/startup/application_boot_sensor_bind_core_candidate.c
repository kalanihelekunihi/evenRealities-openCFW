/* SPDX-License-Identifier: MIT
 * CASE 0x08008d98 sensor DMA bind. Callback bodies at 0x8758, 0x8808,
 * 0x8998, and 0x8a48 remain separate native source contracts.
 */
#include <stdint.h>
extern void case_boot_sensor_callback_8a48(uint32_t);
extern void case_boot_sensor_callback_8808(uint32_t);
extern void case_boot_sensor_callback_8998(uint32_t);
extern void case_boot_sensor_callback_8758(uint32_t);
static uint32_t rd32(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr32(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static void wr16(uint32_t a,uint16_t v){*(volatile uint16_t *)(uintptr_t)a=v;}
static uint32_t primask(void){uint32_t v;__asm volatile("mrs %0, primask":"=r"(v));return v;}
static void setmask(uint32_t v){__asm volatile("msr primask, %0"::"r"(v):"memory");}
static void or_locked(uint32_t address,uint32_t bits)
{
    uint32_t saved=primask();setmask(1u);
    wr32(address,rd32(address)|bits);
    setmask(saved);
}
/* Stock 0x08008D98 (case_begin_receive) */
uint32_t case_boot_sensor_bind_core(uint32_t descriptor,uint32_t channel,uint32_t enabled)
{
    uint32_t mode=rd32(descriptor+8u),linked=rd32(descriptor+16u);
    wr32(descriptor+88u,channel);
    wr16(descriptor+92u,(uint16_t)enabled);
    wr16(descriptor+94u,(uint16_t)enabled);
    wr32(descriptor+116u,0u);
    uint16_t limit;
    if(mode==0x1000u)limit=linked!=0u?255u:511u;
    else if(mode==0u)limit=linked!=0u?127u:255u;
    else if(mode==0x10000000u)limit=linked!=0u?63u:127u;
    else limit=0u;
    wr16(descriptor+96u,limit);
    wr32(descriptor+144u,0u);
    wr32(descriptor+140u,34u);
    uint32_t base=rd32(descriptor);
    or_locked(base+8u,1u);
    if(rd32(descriptor+100u)==0x20000000u &&
       *(volatile uint16_t *)(uintptr_t)(descriptor+104u)<=enabled){
        if(mode==0x1000u && linked==0u)
            wr32(descriptor+116u,(uint32_t)(uintptr_t)case_boot_sensor_callback_8808);
        else
            wr32(descriptor+116u,(uint32_t)(uintptr_t)case_boot_sensor_callback_8a48);
        if(linked!=0u)or_locked(base,0x100u);
        or_locked(base+8u,0x10000000u);
    }else{
        if(mode==0x1000u && linked==0u)
            wr32(descriptor+116u,(uint32_t)(uintptr_t)case_boot_sensor_callback_8758);
        else
            wr32(descriptor+116u,(uint32_t)(uintptr_t)case_boot_sensor_callback_8998);
        or_locked(base,linked!=0u?0x120u:0x20u);
    }
    return 0u;
}
