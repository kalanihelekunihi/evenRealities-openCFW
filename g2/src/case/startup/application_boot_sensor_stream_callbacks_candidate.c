/* SPDX-License-Identifier: MIT
 * CASE 0x08008808 / 0x08008a48: streaming DMA callbacks.
 */
#include <stdint.h>
extern void case_boot_sensor_callback_8758(uint32_t);
extern void case_boot_sensor_callback_8998(uint32_t);
extern void case_boot_sensor_callback_finish(uint32_t); /* 0x08006544 */
/* Native 0x08005f42 is precisely BX LR. */
void case_boot_sensor_callback_status(uint32_t descriptor){(void)descriptor;}
static uint32_t rd32(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr32(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint16_t rd16(uint32_t a){return *(volatile uint16_t *)(uintptr_t)a;}
static void wr16(uint32_t a,uint16_t v){*(volatile uint16_t *)(uintptr_t)a=v;}
static uint32_t mask(void){uint32_t v;__asm volatile("mrs %0, primask":"=r"(v));return v;}
static void setmask(uint32_t v){__asm volatile("msr primask, %0"::"r"(v):"memory");}
static void and_locked(uint32_t a,uint32_t bits)
{uint32_t s=mask();setmask(1u);wr32(a,rd32(a)&bits);setmask(s);}
static void or_locked(uint32_t a,uint32_t bits)
{uint32_t s=mask();setmask(1u);wr32(a,rd32(a)|bits);setmask(s);}
static void stream(uint32_t d,uint32_t width)
{
    uint32_t hw=rd32(d),saved_control=rd32(hw),saved_config=rd32(hw+8u);
    uint32_t half_limit=rd16(d+104u);
    uint32_t flags=rd32(hw+28u);
    if(rd32(d+140u)!=34u){wr32(hw+24u,rd32(hw+24u)|8u);return;}
    for(;;){
        uint16_t remaining=rd16(d+94u);
        if(half_limit!=0u && (flags&32u)!=0u){
            uint32_t output=rd32(d+88u),value=rd32(hw+36u)&rd16(d+96u);
            if(width==2u)wr16(output,(uint16_t)value);
            else *(volatile uint8_t *)(uintptr_t)output=(uint8_t)value;
            wr32(d+88u,output+width);
            remaining=(uint16_t)(remaining-1u);wr16(d+94u,remaining);
            flags=rd32(hw+28u);
            if((flags&7u)!=0u){
                if((flags&1u)!=0u && (saved_control&0x100u)!=0u){
                    wr32(hw+32u,1u);wr32(d+144u,rd32(d+144u)|1u);
                }
                if((flags&2u)!=0u && (saved_config&1u)!=0u){
                    wr32(hw+32u,2u);wr32(d+144u,rd32(d+144u)|4u);
                }
                if((flags&4u)!=0u && (saved_config&1u)!=0u){
                    wr32(hw+32u,4u);wr32(d+144u,rd32(d+144u)|2u);
                }
                if(rd32(d+144u)!=0u){case_boot_sensor_callback_status(d);wr32(d+144u,0u);}
            }
            if(remaining==0u){
                and_locked(hw,~0x100u);
                and_locked(hw+8u,0xffeffeffu);
                wr32(d+140u,32u);wr32(d+116u,0u);wr32(d+112u,0u);
                if(rd32(d+108u)!=1u)case_boot_sensor_callback_finish(d);
                else{
                    wr32(d+108u,0u);and_locked(hw,~16u);
                    if((rd32(hw+28u)&16u)!=0u)wr32(hw+32u,16u);
                }
            }
            continue;
        }
        if(remaining==0u || half_limit<=remaining)return;
        and_locked(hw+8u,~0x10000000u);
        wr32(d+116u,(uint32_t)(uintptr_t)(width==2u?
            case_boot_sensor_callback_8758:case_boot_sensor_callback_8998));
        or_locked(hw,32u);
        return;
    }
}
void case_boot_sensor_callback_8808(uint32_t descriptor){stream(descriptor,2u);}
void case_boot_sensor_callback_8a48(uint32_t descriptor){stream(descriptor,1u);}
