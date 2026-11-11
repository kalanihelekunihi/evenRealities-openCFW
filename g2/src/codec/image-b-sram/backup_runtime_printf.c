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

/* W15 evidence: stock image-B printf family is out_rev 0x10008a04 (154 B), ntoa_format
 * 0x10008aa0, ntoa_long 0x10008c88, ntoa_long_long 0x10008d48 (calls 0x1001149c/0x100117d0
 * 64-bit div/mod), vsnprintf 0x10008e20. Ghidra corpus open-2026-09-29/image_b_sram
 * functions-000.jsonl: 0x10008a04 is called only by 0x10008aa0 (upstream _ftoa/_etoa also
 * call _out_rev, so they are absent), and no image-B decompile contains a double. Stock was
 * built with float/exponential support disabled; long long stays enabled. */
#define PRINTF_DISABLE_SUPPORT_FLOAT
#define PRINTF_DISABLE_SUPPORT_EXPONENTIAL
#define _putchar gx8002_image_b_putchar_10009924
#define printf_ gx8002_image_b_heap_log_10009934
#include "../../../../third-party/upstream/nationalchip-lvp-kws/utility/libc/printf.c"
#undef printf_
#undef _putchar
