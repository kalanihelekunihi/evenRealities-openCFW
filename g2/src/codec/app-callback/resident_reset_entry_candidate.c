/* SPDX-License-Identifier: MIT
 * Image-A SRAM reset entry at 0x10023500. The naked C definition keeps the
 * architectural PSR, CR31 and stack setup in inline C-SKY instructions: no
 * C stack or calling convention is available until that sequence completes.
 */
#include <stdint.h>

extern void gx8002_resident_system_initialize_2354c(void);
extern void gx8002_resident_main_26314(void);

__attribute__((naked, used, aligned(4),
               section(".text.gx8002_resident_reset_entry_23500")))
void gx8002_resident_reset_entry_23500(void)
{
    __asm__ volatile (
        "lrw r0, 0x80000200\n\t"
        "mtcr r0, cr<0, 0>\n\t"
        "mfcr r1, cr<31, 0>\n\t"
        "bclri r1, 3\n\t"
        "mtcr r1, cr<31, 0>\n\t"
        "lrw r3, 0x2002f7fc\n\t"
        "mov r14, r3\n\t"
        "bsr gx8002_resident_system_initialize_2354c\n\t"
        "bsr gx8002_resident_main_26314\n\t"
        "1: br 1b\n\t"
    );
}
