/* SPDX-License-Identifier: MIT
 * CASE sensor interrupt dispatcher, native 0x08005f50. Descriptor offsets and
 * IRQ mask transitions follow the retained M0 control flow. The nontrivial
 * sensor completion children remain independently typed source obligations.
 */
#include <stdint.h>
extern void case_boot_sensor_irq_error(uint32_t descriptor); /* 0x86f4 */
extern uint32_t case_boot_sensor_irq_restart_ready(uint32_t peripheral); /* 0x48e6 */
extern uint32_t case_boot_sensor_irq_restart(uint32_t peripheral); /* 0x487a */
extern void case_boot_sensor_irq_final(uint32_t descriptor); /* 0x6776 */
extern uint32_t case_boot_sensor_cancel_callback(uint32_t descriptor); /* native 0x86e0 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static uint16_t rh(uint32_t a){return *(volatile uint16_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static void wh(uint32_t a,uint16_t v){*(volatile uint16_t *)(uintptr_t)a=v;}
static uint32_t mask(void){uint32_t x;__asm volatile("mrs %0, primask":"=r"(x));return x;}
static void setmask(uint32_t x){__asm volatile("msr primask, %0"::"r"(x):"memory");}
static void clear_locked(uint32_t a,uint32_t bits)
{uint32_t m=mask();setmask(1u);wr(a,rd(a)&~bits);setmask(m);}
static void invoke(uint32_t callback,uint32_t descriptor)
{((void (*)(uint32_t))(uintptr_t)callback)(descriptor);}
/* DMA cancellation slot differs from the void-returning RxISR slots. */
static void invoke_cancel(uint32_t callback,uint32_t peripheral)
{(void)((uint32_t (*)(uint32_t))(uintptr_t)callback)(peripheral);}
void case_irq_child_5f50(uint32_t descriptor)
{
    uint32_t hw=rd(descriptor),status=rd(hw),control=rd(hw+8u),enable=rd(hw+28u);
    const uint32_t state=descriptor+128u;
    if((enable&0x80fu)!=0u){
        if(((control&0x10000001u)|(status&0x04000120u))==0u)goto ordinary;
        if((enable&1u)!=0u && (status&0x100u)!=0u){
            wr(hw+32u,1u);wr(state+16u,rd(state+16u)|1u);
        }
        if((enable&2u)!=0u && (control&1u)!=0u){
            wr(hw+32u,2u);wr(state+16u,rd(state+16u)|4u);
        }
        if((enable&4u)!=0u && (control&1u)!=0u){
            wr(hw+32u,4u);wr(state+16u,rd(state+16u)|2u);
        }
        if((enable&8u)!=0u && ((status&32u)|(control&0x10000001u))!=0u){
            wr(hw+32u,8u);wr(state+16u,rd(state+16u)|8u);
        }
        if((enable&0x800u)!=0u && (status&0x4000000u)!=0u){
            wr(hw+32u,0x800u);wr(state+16u,rd(state+16u)|32u);
        }
        if(rd(state+16u)!=0u){
            if((enable&32u)!=0u && ((status&32u)|(control&0x10000000u))!=0u && rd(descriptor+116u)!=0u)
                invoke(rd(descriptor+116u),descriptor);
            if((control&64u)!=0u || (rd(state+16u)&0x28u)!=0u){
                case_boot_sensor_irq_error(descriptor);
                hw=rd(descriptor);
                if((rd(hw+8u)&64u)!=0u){
                    clear_locked(hw+8u,64u);
                    uint32_t p=rd(state);
                    if(p==0u)return;
                    wr(p+56u,(uint32_t)(uintptr_t)case_boot_sensor_cancel_callback);
                    if(case_boot_sensor_irq_restart_ready(p)==0u)return;
                    invoke_cancel(rd(rd(state)+56u),rd(state));
                    return;
                }
                return;
            }
            /* Native 0x5f42 is an empty handler, followed by status clear. */
            wr(state+16u,0u);
            return;
        }
        return;
    }
    if((enable&32u)!=0u && ((status&32u)|(control&0x10000000u))!=0u){
        uint32_t cb=rd(descriptor+116u);if(cb!=0u)invoke(cb,descriptor);
        return;
    }
ordinary:
    if(rd(descriptor+108u)==1u && (enable&16u)!=0u && (status&16u)!=0u){
        wr(hw+32u,16u);
        hw=rd(descriptor);
        if((rd(hw+8u)&64u)!=0u){
            uint32_t p=rd(state),span=rd(rd(p)+4u)&0xffffu;
            if(span==0u)return;
            if(rh(descriptor+92u)<=span)return;
            wh(descriptor+94u,(uint16_t)span);
            if((rd(rd(p))&32u)==0u){
                clear_locked(hw,0x100u);
                clear_locked(hw+8u,1u);
                clear_locked(hw+8u,64u);
                wr(state+12u,32u);wr(descriptor+108u,0u);
                clear_locked(hw,16u);
                (void)case_boot_sensor_irq_restart(p);
            }
            wr(descriptor+112u,2u);
            return;
        }
        uint16_t remain=(uint16_t)(rh(descriptor+92u)-rh(descriptor+94u));
        if(rh(descriptor+94u)==0u || remain==0u)return;
        clear_locked(hw,0x120u);
        clear_locked(hw+8u,0x10000001u);
        wr(state+12u,32u);wr(descriptor+108u,0u);
        wr(descriptor+116u,0u);
        clear_locked(hw,16u);
        wr(descriptor+112u,2u);
        return;
    }
    if((enable&0x100000u)!=0u && (control&0x400000u)!=0u){
        wr(hw+32u,0x100000u);return; /* native 0x5efe BX LR */
    }
    if((enable&0x80u)!=0u && ((status&0x80u)|(control&0x40000000u))!=0u){
        uint32_t cb=rd(descriptor+120u);if(cb!=0u)invoke(cb,descriptor);
        return;
    }
    if((enable&64u)!=0u && (status&64u)!=0u){
        clear_locked(hw,64u);wr(state+8u,32u);wr(descriptor+120u,0u);
        case_boot_sensor_irq_final(descriptor);return;
    }
    if((enable&0x800000u)!=0u && (status&0x40000000u)!=0u)return;
    if((enable&0x1000000u)!=0u && (status&0x80000000u)!=0u)return;
}
