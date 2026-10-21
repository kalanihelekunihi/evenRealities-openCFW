/* SPDX-License-Identifier: MIT
 * Image-B native 0x10009934/0x10008e20 formatter from pinned NationalChip
 * lvp_kws utility/libc/printf.c (commit 8bf9ee5c...).
 * The source remains in the pinned submodule; this adapter renames its public
 * entry and output callback for the distinct loaded image-B candidate.
 */
#include <stdint.h>

extern void gx8002_image_b_runtime_debug_putchar_10009990(uint32_t value);

void gx8002_image_b_putchar_10009924(char character)
{
    if (character != 0)
        gx8002_image_b_runtime_debug_putchar_10009990(
            (uint32_t)(uint8_t)character);
}

#define _putchar gx8002_image_b_putchar_10009924
#define printf_ gx8002_image_b_heap_log_10009934
#include "../../../../third-party/upstream/nationalchip-lvp-kws/utility/libc/printf.c"
#undef printf_
#undef _putchar
