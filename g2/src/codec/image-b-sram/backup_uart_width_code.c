/* SPDX-License-Identifier: MIT
 * Image-B 0x10004078 converts the single-bit UART format mask to the
 * hardware width code. Native callers 0x100040e8/0x10004188 use this body.
 */
#include <stdint.h>

uint32_t gx8002_image_b_uart_width_code_10004078(
    uint32_t mask, const uint32_t *fallback, uint32_t use_mask)
{
    if (use_mask == 0u) mask = *fallback;
    switch (mask) {
    case 4u: return 1u;
    case 8u: return 2u;
    case 16u: return 3u;
    case 32u: return 4u;
    case 64u: return 5u;
    case 128u: return 6u;
    case 256u: return 7u;
    case 512u: return 8u;
    case 1024u: return 9u;
    default: return 0u;
    }
}
