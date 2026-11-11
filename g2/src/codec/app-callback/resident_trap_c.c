/* SPDX-License-Identifier: MIT
 * Image-A SRAM 0x100235f0, trap_c from NationalChip lvp_kws 8bf9ee5c
 * arch/soc/grus/trap_c.c with its report disabled (#if 0 upstream): read
 * the exception vector from PSR bits 23:16, then stop. The register frame
 * built by gx8002_resident_trap_235fc arrives in r0 and is not used.
 */
#include <stdint.h>

/* Stock 0x100235F0 (trap_c) */
__attribute__((noreturn)) void gx8002_resident_trap_c_235f0(uint32_t *regs)
{
    uint32_t vec;
    (void)regs;
    __asm__ volatile("mfcr %0, psr" : "=r"(vec));
    const int32_t vector = (int8_t)(vec >> 16);   /* PSR[23:16] */
    (void)vector;
    for (;;) {
    }
}
