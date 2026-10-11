/* SPDX-License-Identifier: MIT
 * Image-B input route 0x100053e0. Each native INS/ST.W pair remains a
 * separate volatile read-modify-write, including the bit-17 branch.
 */
#include <stdint.h>

#define ROUTE_WORD (*(volatile uint32_t *)(uintptr_t)UINT32_C(0xa0a00004))
#define ROUTE_STATE (*(volatile uint32_t *)(uintptr_t)UINT32_C(0x20017624))

extern void gx8002_image_b_platform_gate_10003be8(uint32_t module, uint32_t enabled);

static void route_field(uint32_t mask, uint32_t value)
{
    ROUTE_WORD = (ROUTE_WORD & ~mask) | (value & mask);
}

void gx8002_image_b_input_route_100053e0(
    uint32_t channel, uint32_t format, uint32_t clock_mode,
    uint32_t sample_mode, uint32_t word_mode, uint32_t route_mode)
{
    gx8002_image_b_platform_gate_10003be8(2u, 1u);
    route_field(15u << 4, (channel & 15u) << 4);
    route_field(7u << 8, (format & 7u) << 8);
    route_field(1u << 16, (clock_mode & 1u) << 16);
    route_field(3u << 18, (sample_mode & 3u) << 18);
    route_field(3u << 21, (word_mode & 3u) << 21);
    route_field(1u << 17, format >= 3u ? 1u << 17 : 0u);
    route_field(1u << 11, (route_mode & 1u) << 11);
    route_field(1u << 20, 0u);
    route_field(1u << 2, 0u);
    route_field(1u << 3, 0u);
    route_field(1u << 30, 1u << 30);
    ROUTE_STATE = ROUTE_STATE | 4u;
}
