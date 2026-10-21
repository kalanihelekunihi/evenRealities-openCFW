/* SPDX-License-Identifier: MIT
 * Native CASE 0x08004fec NVIC disable path.
 */
#include <stdint.h>
void case_boot_irq_disable(uint32_t irq)
{
    if((int32_t)irq<0)return;
    *(volatile uint32_t *)(uintptr_t)0xe000e180u=1u<<(irq&31u);
    __asm__ volatile("dsb sy\nisb sy" ::: "memory");
}
