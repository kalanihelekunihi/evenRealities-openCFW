/* SPDX-License-Identifier: MIT
 * BINH A stage-1 vector and reset entry from the locked 0x10000000 boot block.
 * The CPU-register sequence must execute before a C stack exists.
 */
#include <stdint.h>

extern void gx8002_image_a_stage1_boot_setup_10000acc(void);
extern void gx8002_resident_reset_entry_23500(void);

__attribute__((naked, used, section(".spl_a.reset")))
void gx8002_image_a_stage1_reset_10000100(void)
{
    __asm__ volatile (
        "lrw r0, 0x80000200\n\t"
        "mtcr r0, cr<0,0>\n\t"
        "mfcr r1, cr<31,0>\n\t"
        "bclri r1, 3\n\t"
        "mtcr r1, cr<31,0>\n\t"
        "lrw r0, gx8002_image_a_stage1_vectors\n\t"
        "mtcr r0, cr<1,0>\n\t"
        "lrw r0, 0x20002ffc\n\t"
        "mov r14, r0\n\t"
        "jbsr gx8002_image_a_stage1_boot_setup_10000acc\n\t"
        "jbsr gx8002_resident_reset_entry_23500\n\t"
        "bkpt\n\t"
    );
}

__attribute__((noreturn, used, section(".spl_a.default")))
void gx8002_image_a_stage1_default_10000130(void)
{
    for (;;) {}
}

typedef void (*stage1_vector)(void);
__attribute__((used, section(".spl_a.vectors"), aligned(1024)))
stage1_vector const gx8002_image_a_stage1_vectors[64] = {
    gx8002_image_a_stage1_reset_10000100,
    [1 ... 63] = gx8002_image_a_stage1_default_10000130,
};
