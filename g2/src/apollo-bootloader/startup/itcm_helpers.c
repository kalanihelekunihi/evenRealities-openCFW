/* SPDX-License-Identifier: MIT
 * Fixed 24-byte ITCM source image copied to address 0x40. The countdown,
 * word-copy, and two return leaves must retain their exact relative labels:
 * call sites use Thumb addresses 0x41 and 0x49 after the copy. One naked C
 * body keeps the architectural instructions contiguous without C frames.
 */
#include <stdint.h>

__attribute__((naked, used, section(".text.itcm_helpers")))
void opencfw_boot_itcm_countdown(uint32_t count)
{
    __asm__ volatile (
        ".global opencfw_boot_itcm_image_start\n\t"
        "opencfw_boot_itcm_image_start:\n\t"
        "1: subs r0, #1\n\t"
        "bne 1b\n\t"
        "bx lr\n\t"
        ".global opencfw_boot_itcm_noop_46\n\t"
        ".type opencfw_boot_itcm_noop_46, %function\n\t"
        ".thumb_func\n\t"
        "opencfw_boot_itcm_noop_46:\n\t"
        "bx lr\n\t"
        ".global opencfw_boot_itcm_word_copy\n\t"
        ".type opencfw_boot_itcm_word_copy, %function\n\t"
        ".thumb_func\n\t"
        "opencfw_boot_itcm_word_copy:\n\t"
        "2: ldr r3, [r0], #4\n\t"
        "str r3, [r1], #4\n\t"
        "subs r2, #1\n\t"
        "bne 2b\n\t"
        "bx lr\n\t"
        ".global opencfw_boot_itcm_noop_56\n\t"
        ".type opencfw_boot_itcm_noop_56, %function\n\t"
        ".thumb_func\n\t"
        "opencfw_boot_itcm_noop_56:\n\t"
        "bx lr\n\t"
        ".global opencfw_boot_itcm_image_end\n\t"
        "opencfw_boot_itcm_image_end:\n\t"
    );
}
