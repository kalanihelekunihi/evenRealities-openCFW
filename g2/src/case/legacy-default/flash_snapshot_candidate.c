/* SPDX-License-Identifier: MIT
 * Stock 0x08004a00 controller snapshot. Constants from fixed-image literal
 * words 0x08004a68 and 0x08003ed0; live registers remain target state.
 */
#include <stdint.h>
void case_flash_mode_registers(uint32_t snapshot[7])
{
    volatile uint32_t *const regs=(volatile uint32_t *)(uintptr_t)0x40022000u;
    uint32_t offset;
    snapshot[0]=7u;
    if(snapshot[1]==1u) offset=0x2cu;
    else if(snapshot[1]==4u) offset=0x4cu;
    else if(snapshot[1]==8u) offset=0x50u;
    else offset=0x30u;
    uint32_t control=regs[offset/4u];
    snapshot[2]=control&0x7fu;
    snapshot[3]=(control&0x7fffffu)>>16;
    uint32_t option=regs[0x20u/4u]&0xffu;
    snapshot[4]=(option==0xaau||option==0xccu)?option:0xbbu;
    snapshot[6]=regs[0x20u/4u]&0x077f6000u;
    snapshot[5]=0x077f6000u;
}
