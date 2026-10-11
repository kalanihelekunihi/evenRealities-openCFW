/* SPDX-License-Identifier: MIT
 * Native CASE 0x08003e94/0x08003eec flash option erase register writes.
 */
#include <stdint.h>
void case_boot_option_mass_erase(uint32_t bank)
{
    volatile uint32_t *cr=(volatile uint32_t *)(uintptr_t)0x40022014u;
    *cr|=bank|0x00010000u;
}
void case_boot_option_page_erase(uint32_t bank,uint32_t page)
{
    volatile uint32_t *cr=(volatile uint32_t *)(uintptr_t)0x40022014u;
    uint32_t value=*cr&0xffffe007u;
    if(bank!=4u)value|=0x2000u;else value&=~0x2000u;
    *cr=value|(page<<3)|0x00010002u;
}
