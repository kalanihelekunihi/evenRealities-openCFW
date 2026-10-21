/* SPDX-License-Identifier: MIT
 * CASE native 0x0800b284 timer tick read and wrap handling.
 */
#include <stdint.h>
extern void case_boot_timer_handle_wrap(void); /* 0xb2b0 */
static uint32_t rd(uint32_t a){return *(volatile uint32_t *)(uintptr_t)a;}
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
uint32_t case_boot_timer_now(uint32_t *overflow)
{
    uint32_t now=rd(0x20000134u);
    uint32_t previous=rd(0x2000016cu);
    if(now<previous){case_boot_timer_handle_wrap();*overflow=1u;}
    else *overflow=0u;
    wr(0x2000016cu,now);
    return now;
}
