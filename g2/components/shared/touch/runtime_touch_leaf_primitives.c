/* SPDX-License-Identifier: MIT */
#include "runtime_touch_leaf_primitives.h"

#define OPEN_CFW_TOUCH_PASSTHROUGH(entry) \
    uint32_t open_cfw_touch_leaf_##entry##_passthrough(uint32_t r0) \
    { \
        return r0; \
    }

OPEN_CFW_TOUCH_PASSTHROUGH(1226)
OPEN_CFW_TOUCH_PASSTHROUGH(1236)
OPEN_CFW_TOUCH_PASSTHROUGH(12a4)
OPEN_CFW_TOUCH_PASSTHROUGH(1366)
OPEN_CFW_TOUCH_PASSTHROUGH(1370)
OPEN_CFW_TOUCH_PASSTHROUGH(1418)

#define OPEN_CFW_TOUCH_CONSTANT(entry, value) \
    uint32_t open_cfw_touch_leaf_##entry##_constant_##value( \
        uint32_t r0, uint32_t r1, uint32_t r2, uint32_t r3) \
    { \
        (void)r0; \
        (void)r1; \
        (void)r2; \
        (void)r3; \
        return (value); \
    }

OPEN_CFW_TOUCH_CONSTANT(1480, 1)
OPEN_CFW_TOUCH_CONSTANT(1484, 128)
OPEN_CFW_TOUCH_CONSTANT(1488, 128)
OPEN_CFW_TOUCH_CONSTANT(148c, 0)
OPEN_CFW_TOUCH_CONSTANT(14aa, 0)
OPEN_CFW_TOUCH_CONSTANT(1ab4, 0)

uint32_t open_cfw_touch_leaf_1490_bounded_sum(
    uint32_t ignored_r0, uint32_t r1, uint32_t r2)
{
    (void)ignored_r0;
    return (r1 != 0u && (r1 + r2) <= 0x10000u) ? 1u : 0u;
}

uint32_t open_cfw_touch_leaf_1ca8_median3(
    uint32_t r0, uint32_t r1, uint32_t r2)
{
    uint32_t high = r0 > r1 ? r0 : r1;
    uint32_t low = r0 > r1 ? r1 : r0;
    uint32_t upper = high > r2 ? r2 : high;
    return low >= upper ? low : upper;
}

uint32_t open_cfw_touch_leaf_1cde_blend_u8(
    uint32_t r0, uint32_t r1, uint32_t r2)
{
    return ((r0 * r2) + (r1 * (256u - r2))) >> 8u;
}

uint32_t open_cfw_touch_leaf_2228_mode_scale(
    uint32_t r0, uint32_t r1, uint32_t r2)
{
    if ((r1 & 3u) != 2u) {
        return r2;
    }
    return (r0 == 1u || r0 == 10u) ? (r2 >> 2u) : (r2 >> 1u);
}
