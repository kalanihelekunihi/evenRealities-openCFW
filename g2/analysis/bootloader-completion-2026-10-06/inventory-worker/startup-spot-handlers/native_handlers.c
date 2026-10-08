/* SPDX-License-Identifier: BSD-3-Clause
 * Fixed-address ABI hypotheses for isolated comparison with the locked image.
 * Provider functions deliberately expose every intermediate read and commit.
 */
#include <stdint.h>

#define MMIO32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define RAM32(a)  (*(volatile uint32_t *)(uintptr_t)(a))
#define RAM8(a)   (*(volatile uint8_t *)(uintptr_t)(a))

extern int spot_info_read(uint32_t selector, uint32_t word_offset,
                          uint32_t word_count, uint32_t *destination);
extern void spot_timer_init(void);

/* Stock 0x42abbc; profile base 0x20026ba0. */
int spotmgr_init_42abbc_native(void)
{
    uint32_t temporary[5];
    uint32_t *profile = (uint32_t *)(uintptr_t)0x20026ba0U;
    int status;
    if ((MMIO32(0x400201bcU) & 8U) != 0U &&
        (MMIO32(0x40021008U) & 0x08000000U) == 0U) return 7;
    status = spot_info_read(1U, 0x25cU, 20U, profile + 1);
    if (status != 0) return status;
    status = spot_info_read(1U, 0x270U, 5U, temporary);
    if (status != 0) return status;
    for (uint32_t i = 0; i < 5U; ++i) profile[21U + i] = temporary[i];
    status = spot_info_read(1U, 0x278U, 1U, temporary);
    if (status != 0) return status;
    profile[26] = temporary[0];
    profile[0] = 0x1f01600dU;
    spot_timer_init();
    return 0;
}

static uint32_t put_field(uint32_t old, uint32_t value, unsigned shift,
                          uint32_t mask)
{
    return (old & ~(mask << shift)) | ((value & mask) << shift);
}

/* Stock 0x42bdf0; direct global writes preserve provider-visible state. */
int hw_state_compose_42bdf0_native(void)
{
    uint32_t temporary[4];
    uint32_t *p = (uint32_t *)(uintptr_t)0x20026ba0U;
    int status;
    if ((MMIO32(0x400201bcU) & 8U) != 0U &&
        (MMIO32(0x40021008U) & 0x08000000U) == 0U) return 7;
    status = spot_info_read(1U, 0x25cU, 16U, p + 1);
    if (status != 0) return status;
    for (uint32_t i = 0; i < 4U; ++i)
        p[17U+i] = (p[5U+i] & ~0x7fU) | (p[13U+i] & 0x7fU);
    status = spot_info_read(1U, 0x270U, 4U, temporary);
    if (status != 0) return status;
    for (uint32_t i = 0; i < 4U; ++i) p[21U+i] = temporary[i];
    status = spot_info_read(1U, 0x278U, 1U, temporary);
    if (status != 0) return status;
    p[26] = temporary[0];
    p[9] = put_field(p[9], (((p[14] & 0x0fffffffU) >> 21) +
                           ((p[13] & 0x0fffffffU) >> 21)) / 2U, 21, 0x7fU);
    p[10] = put_field(p[10], p[11] >> 21, 21, 0x7fU);
    p[9] = put_field(p[9], p[13] >> 28, 28, 1U);
    p[10] = put_field(p[10], p[11] >> 28, 28, 1U);
    p[13] = put_field(p[13], p[14] >> 21, 21, 0x7fU);
    p[13] = put_field(p[13], p[14] >> 28, 28, 1U);
    p[13] = put_field(p[13], p[14] >> 17, 17, 0xfU);
    p[13] = put_field(p[13], p[14] >> 7, 7, 0x3ffU);
    p[26] = (p[26] & 0xfc0fffffU) | 0x01f00000U;
    p[0] = 0x1f01600dU;
    spot_timer_init();
    return 0;
}

/* Stock 0x42d6c0; the constants below are resolved literals in the image. */
int bl_bl009_dispatch_native(void)
{
    uint32_t revision = MMIO32(0x4002000cU) & 0xffU;
    uint32_t variant = RAM32(0x20000098U);
    uint32_t word = RAM32(0x2002683cU);
    RAM8(0x200271b3U) = (uint8_t)(revision == 0x21U && variant == 2U);
    RAM8(0x200271b4U) = (uint8_t)((revision == 0x21U &&
        (variant == 2U || variant == 3U)) ||
        (revision == 0x22U && variant == 0U));
    if (revision == 0x22U && variant == 1U) {
        RAM8(0x200271b5U) = 1U;
    } else if (revision == 0x23U && variant == 0U) {
        uint32_t special = (word & 0x3fe00000U) == 0x31800000U &&
                           ((word & 0x1fffffU) >> 16) > 0x13U &&
                           (word & 0xffffU) == 0U;
        uint32_t invalid = ((word & 0x3fffffffU) >> 25) < 0x19U ||
                           (word & 0xffffU) != 0U;
        RAM8(0x200271b5U) = (uint8_t)(!special && invalid);
    } else {
        RAM8(0x200271b5U) = 0U;
    }
    return 0;
}

/* Stock 0x42f670. */
int startup_noop_42f670_native(void) { return 0; }
