/* SPDX-License-Identifier: MIT
 * Stock controller leaves 0x08003e94, 0x08003eec, 0x08003f1c.
 * Register values and flash persistence remain target runtime contracts.
 */
#include <stdint.h>
#define CASE_FLASH_CR (*(volatile uint32_t *)(uintptr_t)0x40022014u)
void case_flash_erase_mode4(uint32_t mode)
{
    CASE_FLASH_CR=CASE_FLASH_CR | mode | 0x10000u;
}
void case_flash_erase_page(uint32_t mode,uint32_t page)
{
    uint32_t control=CASE_FLASH_CR & 0xffffe007u;
    if(mode==4u) control&=~0x2000u;
    else control|=0x2000u;
    CASE_FLASH_CR=(page<<3)|control|0x10002u;
}
void case_flash_program_doubleword(uint32_t address,uint32_t retained_r1,
                                   uint32_t low,uint32_t high)
{
    (void)retained_r1;
    volatile uint32_t *destination=(volatile uint32_t *)(uintptr_t)address;
    CASE_FLASH_CR=CASE_FLASH_CR|1u;
    destination[0]=low;
    __asm__ volatile("isb 0xf" ::: "memory");
    destination[1]=high;
}
