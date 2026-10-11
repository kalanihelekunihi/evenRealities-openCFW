/* SPDX-License-Identifier: MIT
 * CASE 0x080085b0 configurable sensor register fields.
 */
#include <stdint.h>
static uint32_t rd32(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr32(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint16_t rd16(uint32_t a){return *(volatile uint16_t *)(uintptr_t)a;}
static void field(uint32_t address,uint32_t clear,uint32_t value)
{wr32(address,(rd32(address)&~clear)|value);}
void case_boot_sensor_open_apply(uint32_t d)
{
    uint32_t hw=rd32(d);
    uint32_t flags=rd16(d+40u);
    if((flags&1u)!=0u)field(hw+4u,1u<<17,rd32(d+44u));
    if((flags&2u)!=0u)field(hw+4u,1u<<16,rd32(d+48u));
    if((flags&4u)!=0u)field(hw+4u,1u<<18,rd32(d+52u));
    if((flags&8u)!=0u)field(hw+4u,1u<<15,rd32(d+56u));
    if((flags&16u)!=0u)field(hw+8u,1u<<12,rd32(d+60u));
    if((flags&32u)!=0u)field(hw+8u,1u<<13,rd32(d+64u));
    if((flags&64u)!=0u){
        uint32_t option=rd32(d+68u);
        field(hw+4u,1u<<20,option);
        if(option==(1u<<20))field(hw+4u,3u<<21,rd32(d+72u));
    }
    if((flags&128u)!=0u)field(hw+4u,1u<<19,rd32(d+76u));
}
