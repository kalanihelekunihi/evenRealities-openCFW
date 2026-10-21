/* SPDX-License-Identifier: MIT
 * Image-B architectural IRQ mask primitives at 0x1000486c/0x10004878.
 * Native MFCR/PSRCLR/MTCR semantics are preserved; Ghidra lost the return ABI.
 */
#include <stdint.h>

uint32_t gx8002_image_b_irq_save_1000486c(void)
{
    uint32_t previous;
    __asm__ volatile (
        "mfcr %0, cr<0, 0>\n"
        "psrclr ie\n"
        : "=r"(previous) : : "memory");
    return previous;
}

void gx8002_image_b_irq_restore_10004878(uint32_t previous)
{
    __asm__ volatile ("mtcr %0, cr<0, 0>\n" : : "r"(previous) : "memory");
}
