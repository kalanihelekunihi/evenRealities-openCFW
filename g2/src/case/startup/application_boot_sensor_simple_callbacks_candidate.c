/* SPDX-License-Identifier: MIT
 * CASE 0x08008758 / 0x08008998: one-sample DMA callbacks, halfword/byte.
 * Native 0x5e6a is a BX LR leaf and has no state effect.
 */
#include <stdint.h>
extern void case_boot_sensor_callback_finish(uint32_t descriptor); /* 0x08006544 */
static uint32_t rd32(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr32(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint16_t rd16(uint32_t a){return *(volatile uint16_t *)(uintptr_t)a;}
static void wr16(uint32_t a,uint16_t v){*(volatile uint16_t *)(uintptr_t)a=v;}
static uint32_t mask(void){uint32_t v;__asm volatile("mrs %0, primask":"=r"(v));return v;}
static void setmask(uint32_t v){__asm volatile("msr primask, %0"::"r"(v):"memory");}
static void and_locked(uint32_t address,uint32_t bits)
{
    uint32_t saved=mask();setmask(1u);wr32(address,rd32(address)&bits);setmask(saved);
}
static void sample(uint32_t descriptor,uint32_t width)
{
    uint32_t hw=rd32(descriptor);
    if(rd32(descriptor+140u)!=34u){wr32(hw+24u,rd32(hw+24u)|8u);return;}
    uint32_t value=rd32(hw+36u)&rd16(descriptor+96u);
    uint32_t output=rd32(descriptor+88u);
    if(width==2u)wr16(output,(uint16_t)value);
    else *(volatile uint8_t *)(uintptr_t)output=(uint8_t)value;
    wr32(descriptor+88u,output+width);
    uint16_t count=(uint16_t)(rd16(descriptor+94u)-1u);
    wr16(descriptor+94u,count);
    if(count!=0u)return;
    and_locked(hw,~0x120u);
    and_locked(hw+8u,~1u);
    wr32(descriptor+140u,32u);
    wr32(descriptor+116u,0u);
    wr32(descriptor+112u,0u);
    if(rd32(descriptor+108u)!=1u){case_boot_sensor_callback_finish(descriptor);return;}
    wr32(descriptor+108u,0u);
    and_locked(hw,~16u);
    if((rd32(hw+28u)&16u)!=0u)wr32(hw+32u,16u);
}
/* Stock 0x08008758 (case_receive_u16) */
void case_boot_sensor_callback_8758(uint32_t descriptor){sample(descriptor,2u);}
/* Stock 0x08008998 (case_receive_u8) */
void case_boot_sensor_callback_8998(uint32_t descriptor){sample(descriptor,1u);}
