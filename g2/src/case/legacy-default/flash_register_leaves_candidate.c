/* SPDX-License-Identifier: MIT
 * Stock controller leaves 0x08003e94, 0x08003eec, 0x08003f1c.
 * Register values and flash persistence remain target runtime contracts.
 */
#include <stdint.h>
#define CASE_FLASH_CR (*(volatile uint32_t *)(uintptr_t)0x40022014u)
/* Dedup (0x08003e94): case_flash_erase_mode4 is an alias of case_boot_option_mass_erase (startup/application_boot_option_erase_primitives_candidate.c). */
extern void case_flash_erase_mode4(uint32_t mode);
/* Dedup (0x08003eec): case_flash_erase_page is an alias of case_boot_option_page_erase (startup/application_boot_option_erase_primitives_candidate.c). */
extern void case_flash_erase_page(uint32_t mode,uint32_t page);
/* Stock 0x08003F1C (case_register_pair_commit) */
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
