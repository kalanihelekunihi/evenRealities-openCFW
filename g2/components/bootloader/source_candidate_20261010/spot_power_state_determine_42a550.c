/* SPDX-License-Identifier: MIT
 * C reconstruction of locked 0x42a550 from decomp/0042a550.c.
 * This is the first SPOT state decoder, distinct from 0x42b6b8:
 * config word 0x434168 and auxiliary byte also controls bit 20.
 * The state truth table is shared in shape, with exact mask literals from
 * locked 0x42acc0..0x42acdc. Source compilation is not oracle admission.
 */
#include <stdint.h>
#define U32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define U8(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern const uint32_t opencfw_boot_spot_config_values[2];

int opencfw_provider_42a550(const uint8_t *input, uint32_t *major,
                             uint32_t *minor)
{
    const uint32_t *word = (const uint32_t *)(const void *)input;
    uint32_t cfg = opencfw_boot_spot_config_values[1];
    uint32_t hw = U32(0x40021000U);
    uint32_t mode = U8(0x2002708cU);
    uint8_t state = input[17];
    uint8_t auxiliary = input[18];
    uint32_t flags = (cfg & 0xfffff0f0U) | ((input[16] & 0xfU) << 8);
    if (state == 1U) flags |= 1U;
    else if (state == 0U) flags &= ~1U;
    else if ((hw & 3U) == 2U) flags |= 1U;
    else flags &= ~1U;

    if (auxiliary == 1U || auxiliary == 2U ||
        (word[0] & 0x3fffffffU) != 0U || (word[1] & 0x4c4U) != 0U)
        flags = (flags & 0xffffff0fU) | 0x10U;
    else flags &= 0xffffff0fU;
    if (auxiliary == 2U) flags = (flags & 0xffff0fffU) | 0x2000U;
    else if (auxiliary == 1U) flags = (flags & 0xffff0fffU) | 0x1000U;
    else flags &= 0xffff0fffU;
    if ((word[0] & 0x3fffffffU) != 0U || (word[1] & 0x4c4U) != 0U)
        flags = (flags & 0xfff0ffffU) | 0x10000U;
    else flags &= 0xfff0ffffU;
    if (auxiliary == 1U || auxiliary == 2U ||
        (word[0] & 0xc00000U) != 0U)
        flags = (flags & 0xff0fffffU) | 0x100000U;
    else flags &= 0xff0fffffU;

    uint32_t code = flags & 0xf00fffU;
    uint32_t m;
    switch (code) {
    case 0x000: m = mode & 1U ? 7U : 3U; break;
    case 0x001: m = mode & 1U ? 15U : 11U; break;
    case 0x010: m = 7U; break;
    case 0x011: m = 15U; break;
    case 0x100: m = mode & 1U ? 6U : 2U; break;
    case 0x101: m = mode & 1U ? 14U : 10U; break;
    case 0x110: m = 6U; break;
    case 0x111: m = 14U; break;
    case 0x200: m = mode & 1U ? 5U : 1U; break;
    case 0x201: m = mode & 1U ? 13U : 9U; break;
    case 0x210: m = 5U; break;
    case 0x211: m = 13U; break;
    case 0x300: m = mode & 1U ? 4U : 0U; break;
    case 0x301: m = mode & 1U ? 12U : 8U; break;
    case 0x310: m = 4U; break;
    case 0x311: m = 12U; break;
    default: {
        uint32_t diff = code - 0x311U;
        if (diff == 0xffcffU) m = 19U;
        else {
            diff -= 0xffcffU;
            if (diff == 1U) m = 15U;
            else if (diff == 0x100U) m = 18U;
            else if (diff == 0x101U) m = 14U;
            else if (diff == 0x200U) m = 17U;
            else if (diff == 0x201U) m = 13U;
            else if (diff == 0x300U) m = 16U;
            else if (diff == 0x301U) m = 12U;
            else return 5;
        }
        break;
    }
    }
    *major = m;

    uint32_t minor_code = flags & 0xff00fU;
    if (minor_code == 0U) *minor = 0U;
    else if (minor_code == 1U) *minor = mode & 1U ? 7U : 1U;
    else if (minor_code == 0x1000U || minor_code == 0x11000U) *minor = 2U;
    else if (minor_code == 0x1001U || minor_code == 0x11001U) *minor = 4U;
    else if (minor_code == 0x2000U || minor_code == 0x12000U) *minor = 3U;
    else if (minor_code == 0x2001U || minor_code == 0x12001U) *minor = 5U;
    else if (minor_code == 0x10000U) *minor = 6U;
    else if (minor_code == 0x10001U) *minor = 7U;
    else return 5;
    return 0;
}

