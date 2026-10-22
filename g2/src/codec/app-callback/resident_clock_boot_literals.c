/* SPDX-License-Identifier: MIT
 * Image-A clock boot literals at 0x10025cd0 and 0x10025ce0.
 * The clock switch copies two source records; the initializer indexes the
 * signed five-entry PLL adjustment array by start mode.
 */
#include <stdint.h>

struct gx8002_clock_boot_source {
    uint32_t selector;
    uint32_t value;
};
_Static_assert(sizeof(struct gx8002_clock_boot_source) == 8,
               "clock source ABI");

/* Stock 0x10025CD0 (gx8002_clock_switch_1m_rodata) */
const struct gx8002_clock_boot_source gx8002_clock_1m_sources_25cd0[2]
    __attribute__((section(".gx8002.clock_boot.25cd0"), used,
                   aligned(4))) = {{28u, 0u}, {18u, 1u}};

/* Stock 0x10025CE0 (gx8002_clock_init_pointer_rodata) */
const int32_t gx8002_clock_startmode_adjustments_25ce0[5]
    __attribute__((section(".gx8002.clock_boot.25ce0"), used,
                   aligned(4))) = {0, 10, 15, -10, -15};

/* Native 0x10025aee..0x10025af4 copies this separate 16-byte pair from
 * 0x10025cf4 for start mode 1. The pair at 0x10025cd0 belongs to the
 * independent 0x10025a14 low-power switch. */
const struct gx8002_clock_boot_source gx8002_clock_startmode1_sources_25cf4[2]
    __attribute__((section(".gx8002.clock_boot.25cf4"), used,
                   aligned(4))) = {{16u, 0u}, {0u, 1u}};
