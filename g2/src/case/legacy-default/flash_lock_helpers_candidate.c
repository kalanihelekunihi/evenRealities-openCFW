/* SPDX-License-Identifier: MIT
 * Stock flash register helpers 0x08004bf4 and 0x08004b20.
 * These express CPU-visible MMIO access; actual controller key/lock behavior
 * requires a physical flash-controller contract.
 */
#include <stdint.h>

uint32_t case_binary_5e_flash_init(void)
{
    volatile uint32_t *regs=(volatile uint32_t *)(uintptr_t)0x40022000u;
    if((int32_t)regs[5]>=0) return 0u;
    regs[2]=0x45670123u;
    regs[2]=0xcdef89abu;
    return (int32_t)regs[5]<0 ? 1u : 0u;
}

uint32_t case_binary_5e_flash_finish(void)
{
    volatile uint32_t *regs=(volatile uint32_t *)(uintptr_t)0x40022000u;
    regs[5]|=0x80000000u;
    return (int32_t)regs[5]>=0 ? 1u : 0u;
}
