/* Image-B stage-2 0x10003000 vector shape and 0x10003100 reset entry.
 * Native stage2 SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * Pinned NationalChip arch/cpu/csky/ck804/start.S gives the same control
 * register, stack, system-init, main and terminal-loop sequence.
 * The three child functions are genuine source obligations, not defaults.
 */
#include <stdint.h>

extern void gx8002_image_b_system_init_1000314c(void);
extern void gx8002_image_b_main_10015cfc(void);
extern void gx8002_image_b_default_exception_10003240(void);
extern void gx8002_image_b_generic_irq_10004880(void);

__attribute__((naked, used, section(".text.image_b_reset")))
void gx8002_image_b_reset_10003100(void)
{
    __asm__ volatile (
        "lrw r0, 0x80000200\n\t"
        "mtcr r0, cr<0, 0>\n\t"
        "mfcr r1, cr<31, 0>\n\t"
        "bclri r1, 3\n\t"
        "mtcr r1, cr<31, 0>\n\t"
        "lrw r3, 0x2002fffc\n\t"
        "mov r14, r3\n\t"
        "bsr gx8002_image_b_system_init_1000314c\n\t"
        "bsr gx8002_image_b_main_10015cfc\n"
        "1: br 1b");
}

__attribute__((used, aligned(1024), section(".vectors.image_b")))
const uintptr_t gx8002_image_b_vectors_10003000[64] = {
    (uintptr_t)gx8002_image_b_reset_10003100,
    [1 ... 31] = (uintptr_t)gx8002_image_b_default_exception_10003240,
    [32 ... 63] = (uintptr_t)gx8002_image_b_generic_irq_10004880,
};
