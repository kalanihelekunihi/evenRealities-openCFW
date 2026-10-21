/* SPDX-License-Identifier: MIT
 * Native CASE 0x08005bc0 port-register field update.
 */
#include <stdint.h>
void case_boot_register_mask_5bc0(uint32_t bits)
{
    volatile uint32_t *register_word=(volatile uint32_t *)(uintptr_t)0x40010000u;
    *register_word=(*register_word&~(3u<<9))|bits;
}
