/* SPDX-License-Identifier: MIT
 * Image-B architectural IRQ mask primitives at 0x1000486c/0x10004878.
 * Evidence: corpus image_b_sram/functions-000.jsonl gx8002_irq_save
 * @ 0x1000486c (10 B sha 9c1f817c…), gx8002_irq_restore @ 0x10004878
 * (6 B sha 75936780…); native MFCR/PSRCLR/MTCR (headless lost return ABI).
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
