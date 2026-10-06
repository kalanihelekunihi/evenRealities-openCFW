/* SPDX-License-Identifier: MIT */
/* Stock fixed operation2 prefix55c7e8..55ca72; physical dispatch excluded. */
#include "power_prepare.h"
#include "../radio_iom_release/iom_release.h"
#include "../ambiq_mspi/ambiq_cmdq.h"
static volatile uint32_t *field(void *h,uint32_t off)
{ return (volatile uint32_t *)((uint8_t *)h+off); }
static volatile uint32_t *reg(void *h,uint32_t off)
{ return (volatile uint32_t *)(uintptr_t)(0x40050000u+(*field(h,4)<<12)+off); }
uint32_t __attribute__((noinline)) opencfw_iom_cq_pause(void *h)
{ return am_hal_cmdq_disable((void *)(uintptr_t)*field(h,0x828)); }
uint32_t opencfw_iom_powerdown_prepare(void *h,uint32_t retention)
{
    if(!h || ((*field(h,0)&0x01ffffffu)!=0x01123456u))return 2;
    if(*field(h,0)&0x02000000u) {
        if((*reg(h,0x248)&6u)!=4u || *field(h,0x24))return 3;
    }
    if((uint8_t)retention) {
#define SAVE(r,s) *field(h,s)=*reg(h,r)
        SAVE(0x104,0x86c);SAVE(0x118,0x874);SAVE(0x11c,0x878);
        SAVE(0x228,0x87c);SAVE(0x22c,0x880);SAVE(0x234,0x884);
        SAVE(0x23c,0x888);SAVE(0x240,0x88c);SAVE(0x244,0x890);
        SAVE(0x280,0x894);SAVE(0x2c0,0x898);SAVE(0x200,0x89c);
        SAVE(0x210,0x870);
#undef SAVE
        if(*reg(h,0x228)&1u)(void)opencfw_iom_cq_pause(h);
        *(volatile uint8_t *)((uint8_t *)h+0x868)=1;
    }
    *reg(h,0x11c)&=~1u;
    *reg(h,0x11c)&=~0x10u;
    return 0; /* Exact cut before55ca72, not stock full-function success. */
}

uint32_t opencfw_iom_disable_then_prepare(void *h,uint32_t retention)
{
    (void)opencfw_iom_disable(h);
    return opencfw_iom_powerdown_prepare(h,retention);
}
