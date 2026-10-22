/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x10023528..0x1002353d: native startup BSS clear.
 * Literal bounds are 0x20026d80 and 0x2002ecec, an 0x7f6c-byte span.
 * The final linker must place its source-owned BSS objects within this span.
 */
#include <stdint.h>

/* Stock 0x10023528 (gx8002_clear_bss) */
void gx8002_resident_clear_bss_23528(void)
{
    for (uintptr_t address = UINT32_C(0x20026d80);
         address < UINT32_C(0x2002ecec); address += sizeof(uint32_t))
        *(volatile uint32_t *)address = 0u;
}
