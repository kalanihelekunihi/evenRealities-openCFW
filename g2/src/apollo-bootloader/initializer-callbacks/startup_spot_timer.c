/* SPDX-License-Identifier: MIT. Independent locked41cc04..41cc48 leaf. */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
__attribute__((noinline)) void opencfw_boot_spot_timer_initialize(void){
 W(0x400083e0)&=~1u;W(0x400083e0)=0x110;
 W(0x400083f0)=0x100;W(0x400083e8)=0xffffffffu;W(0x400083ec)=0xffffffffu;
 W(0x40008068)=0xc0000000u;W(0x40008060)|=0x40000000u;
}
