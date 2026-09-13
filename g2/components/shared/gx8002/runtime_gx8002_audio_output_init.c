/* SPDX-License-Identifier: MIT */
#include <stdint.h>
extern void open_cfw_gx8002_platform_gate(uint32_t,uint32_t);
/* Stock e4a4 inlines the SDK _aout_reset sequence. Completion is bit20;
 * preserve the post-poll reread and mask-write acknowledgment. */
int open_cfw_gx8002_aout_init(uint32_t mode)
{
    open_cfw_gx8002_platform_gate(11,1);
    open_cfw_gx8002_platform_gate(15,1);
    volatile uint32_t *hw=(volatile uint32_t *)0xa0b00000u;
    for (uint32_t bit=2;bit<=8;bit<<=1) hw[8]=hw[8]|bit;
    uint32_t word=hw[1]&~0xc00u;
    if (mode==2) {
        hw[1]=word|0x400u;
        hw[1]=hw[1]&~128u;
    } else hw[1]=word|((mode<<10)&0xc00u);
    hw[3]=hw[3]|(1u<<22);
    while (!(hw[3]&(1u<<20))) { }
    hw[3]=hw[3]&(1u<<20);
    hw[0]=hw[0]|(1u<<31);
    return 0;
}
