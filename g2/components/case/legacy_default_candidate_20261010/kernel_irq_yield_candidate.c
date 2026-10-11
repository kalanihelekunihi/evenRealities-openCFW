/* SPDX-License-Identifier: MIT
 * Stock 0x080000f4, 0x080000fc and 0x0800c0a0. These are architecture
 * operations and an architected SCB write, with no product configuration.
 */
#include <stdint.h>

uint32_t case_kernel_irq_save(void)
{
    uint32_t primask;
    __asm__ volatile("mrs %0, primask\n\tcpsid i" : "=r"(primask) :: "memory");
    return primask;
}

void case_kernel_irq_restore(uint32_t primask)
{
    __asm__ volatile("msr primask, %0" :: "r"(primask) : "memory");
}

void case_kernel_yield(void)
{
    *(volatile uint32_t *)(uintptr_t)0xe000ed04u=0x10000000u;
    __asm__ volatile("dsb 0xf\n\tisb 0xf" ::: "memory");
}
