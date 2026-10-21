/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10204f18 AOUT hardware initialization.
 * Direct C-SKY listing fixes the 0xa0b00000 MMIO base, three ordered
 * enable writes, mode-2 branch, and unbounded native status wait.
 */
#include <stdint.h>

extern void gx8002_resident_platform_gate_25080(uint32_t, uint32_t);

static volatile uint32_t *const aout =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0b00000);

uint32_t gx8002_xip_aout_hw_initialize_10204f18(uint32_t mode)
{
    gx8002_resident_platform_gate_25080(11u, 1u);
    gx8002_resident_platform_gate_25080(15u, 1u);
    aout[0x20u / 4u] = aout[0x20u / 4u] | 2u;
    aout[0x20u / 4u] = aout[0x20u / 4u] | 4u;
    aout[0x20u / 4u] = aout[0x20u / 4u] | 8u;
    uint32_t control = aout[4u / 4u] & ~UINT32_C(0x0c00);
    if (mode == 2u) {
        aout[4u / 4u] = control | UINT32_C(0x0400);
        aout[4u / 4u] = aout[4u / 4u] & ~UINT32_C(0x0080);
    } else {
        aout[4u / 4u] = control | ((mode << 10u) & UINT32_C(0x0c00));
    }
    aout[0x0cu / 4u] = aout[0x0cu / 4u] | UINT32_C(0x00400000);
    while ((aout[0x0cu / 4u] & UINT32_C(0x00100000)) == 0u) {}
    aout[0x0cu / 4u] = aout[0x0cu / 4u] & UINT32_C(0x00100000);
    aout[0u] = aout[0u] | UINT32_C(0x80000000);
    return 0u;
}
