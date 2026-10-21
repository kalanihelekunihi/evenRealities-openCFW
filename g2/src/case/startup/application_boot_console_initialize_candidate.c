/* SPDX-License-Identifier: MIT
 * Native CASE 0x68f0 console peripheral descriptor initialization.
 */
#include <stdint.h>
extern uint32_t case_boot_console_open(uint32_t descriptor); /* 0x4480 */
extern uint32_t case_boot_console_apply(uint32_t descriptor,const uint32_t *config); /* 0x4100 */
extern void case_boot_console_start(uint32_t descriptor); /* 0x3fd0 */
extern void case_boot_init_failure(void); /* 0x3e90 */
static void wr(uint32_t a,uint32_t v){*(volatile uint32_t *)(uintptr_t)a=v;}
static void wr8(uint32_t a,uint8_t v){*(volatile uint8_t *)(uintptr_t)a=v;}
void case_boot_console_initialize(void)
{
    const uint32_t d=0x200008e4u;
    wr(d,0x40012400u);wr(d+8u,0u);wr(d+12u,0u);wr(d+16u,0u);
    wr(d+4u,0x40000000u);wr(d+20u,4u);
    wr8(d+24u,0u);wr8(d+25u,0u);wr8(d+26u,1u);wr(d+28u,1u);
    wr8(d+32u,0u);wr(d+36u,0u);wr(d+40u,0u);wr8(d+44u,0u);
    wr(d+48u,0u);wr(d+52u,5u);wr(d+56u,0u);wr8(d+60u,0u);wr(d+76u,0u);
    if(case_boot_console_open(d)!=0u)case_boot_init_failure();
    uint32_t config[3]={0x10000010u,0u,0u};
    if(case_boot_console_apply(d,config)!=0u)case_boot_init_failure();
    case_boot_console_start(d);
}
