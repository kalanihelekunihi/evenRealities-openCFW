/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_TOUCH_LEAF_PRIMITIVES_H
#define OPENCFW_TOUCH_LEAF_PRIMITIVES_H

#include <stdint.h>

/* Raw AAPCS register-level candidates; the suffix is the shipped entry. */
uint32_t open_cfw_touch_leaf_1226_passthrough(uint32_t r0);
uint32_t open_cfw_touch_leaf_1236_passthrough(uint32_t r0);
uint32_t open_cfw_touch_leaf_12a4_passthrough(uint32_t r0);
uint32_t open_cfw_touch_leaf_1366_passthrough(uint32_t r0);
uint32_t open_cfw_touch_leaf_1370_passthrough(uint32_t r0);
uint32_t open_cfw_touch_leaf_1418_passthrough(uint32_t r0);

uint32_t open_cfw_touch_leaf_1480_constant_1(
    uint32_t r0, uint32_t r1, uint32_t r2, uint32_t r3);
uint32_t open_cfw_touch_leaf_1484_constant_128(
    uint32_t r0, uint32_t r1, uint32_t r2, uint32_t r3);
uint32_t open_cfw_touch_leaf_1488_constant_128(
    uint32_t r0, uint32_t r1, uint32_t r2, uint32_t r3);
uint32_t open_cfw_touch_leaf_148c_constant_0(
    uint32_t r0, uint32_t r1, uint32_t r2, uint32_t r3);
uint32_t open_cfw_touch_leaf_14aa_constant_0(
    uint32_t r0, uint32_t r1, uint32_t r2, uint32_t r3);
uint32_t open_cfw_touch_leaf_1ab4_constant_0(
    uint32_t r0, uint32_t r1, uint32_t r2, uint32_t r3);

uint32_t open_cfw_touch_leaf_1490_bounded_sum(
    uint32_t ignored_r0, uint32_t r1, uint32_t r2);
uint32_t open_cfw_touch_leaf_1ca8_median3(
    uint32_t r0, uint32_t r1, uint32_t r2);
uint32_t open_cfw_touch_leaf_1cde_blend_u8(
    uint32_t r0, uint32_t r1, uint32_t r2);
uint32_t open_cfw_touch_leaf_2228_mode_scale(
    uint32_t r0, uint32_t r1, uint32_t r2);

#endif
