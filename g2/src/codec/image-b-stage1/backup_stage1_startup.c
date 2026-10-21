/* SPDX-License-Identifier: Apache-2.0
 * Source-shaped BINH-B stage1 reset/vector from pinned CK804 spl_start.S.
 * Native vector0:0x10000100, default vectors:0x10000130, SP:0x20002ffc.
 */
#include <stdint.h>

extern void gx8002_image_b_stage1_boot_setup_10000df0(void);
extern void gx8002_image_b_stage2_reset_10003100(void);

__attribute__((naked, used, section(".spl.reset")))
void gx8002_image_b_stage1_reset_10000100(void)
{
    __asm__ volatile (
        "lrw r0, 0x80000200\n\t"
        "mtcr r0, cr<0,0>\n\t"
        "mfcr r1, cr<31,0>\n\t"
        "bclri r1, 3\n\t"
        "mtcr r1, cr<31,0>\n\t"
        "lrw r0, gx8002_image_b_stage1_vectors\n\t"
        "mtcr r0, cr<1,0>\n\t"
        "lrw r0, 0x20002ffc\n\t"
        "mov r14, r0\n\t"
        "jbsr gx8002_image_b_stage1_boot_setup_10000df0\n\t"
        "jbsr gx8002_image_b_stage2_reset_10003100\n\t"
        "bkpt\n\t"
    );
}

__attribute__((naked, used, section(".spl.default")))
void gx8002_image_b_stage1_default_10000130(void)
{
    __asm__ volatile ("1: br 1b");
}

typedef void (*stage1_vector)(void);
__attribute__((used, section(".spl.vectors"), aligned(1024)))
stage1_vector const gx8002_image_b_stage1_vectors[64] = {
    gx8002_image_b_stage1_reset_10000100,
    [1 ... 63] = gx8002_image_b_stage1_default_10000130,
};
