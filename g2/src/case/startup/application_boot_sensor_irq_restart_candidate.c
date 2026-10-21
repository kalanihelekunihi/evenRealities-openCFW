/* SPDX-License-Identifier: MIT
 * Native CASE 0x487a and 0x48e6 sensor peripheral restart variants.
 */
#include <stdint.h>
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static uint8_t rb(uint32_t a){return *(volatile uint8_t *)(uintptr_t)a;}
static void wb(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
/* The cancellation slot holds uint32_t(uint32_t); native discards its result. */
static void invoke_cancel(uint32_t f,uint32_t a)
{(void)((uint32_t (*)(uint32_t))(uintptr_t)f)(a);}
static void lines(uint32_t p)
{
    wr(rd(p+64u)+4u,1u<<(rd(p+68u)&28u));
    wr(rd(p+76u)+4u,rd(p+80u));
    uint32_t extra=rd(p+84u);
    if(extra!=0u){
        wr(extra,rd(extra)&~0x100u);
        wr(rd(p+88u)+4u,rd(p+92u));
    }
}
uint32_t case_boot_sensor_irq_restart(uint32_t p)
{
    if(p==0u)return 1u;
    if(rb(p+37u)!=2u){wr(p+60u,4u);wb(p+36u,0u);return 1u;}
    uint32_t hw=rd(p);
    wr(hw,rd(hw)&~14u);
    wr(rd(p+72u),rd(rd(p+72u))&~0x100u);
    wr(hw,rd(hw)&~1u);
    lines(p);
    wb(p+37u,1u);wb(p+36u,0u);
    return 0u;
}
uint32_t case_boot_sensor_irq_restart_ready(uint32_t p)
{
    uint32_t state=p+32u;
    if(rb(state+5u)!=2u){wr(p+60u,4u);return 1u;}
    uint32_t hw=rd(p);
    wr(hw,rd(hw)&~14u);
    wr(hw,rd(hw)&~1u);
    wr(rd(p+72u),rd(rd(p+72u))&~0x100u);
    lines(p);
    wb(state+5u,1u);wb(state+4u,0u);
    uint32_t cb=rd(p+56u);if(cb!=0u)invoke_cancel(cb,p);
    return 0u;
}
