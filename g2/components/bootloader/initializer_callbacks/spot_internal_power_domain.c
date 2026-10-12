/* SPDX-License-Identifier: MIT
 * Native Spot manager leaf at 0x42a19c. Its two selectors are byte-sized;
 * mode 1 and state 2 latch the source-owned state byte at 0x200271b0.
 */
#include <stdint.h>

uint32_t opencfw_boot_spot_internal_power_domain(uint32_t state,
                                                 uint32_t mode)
{
    if ((uint8_t)mode != 1u)
        return state;
    state = (uint8_t)state;
    if (state == 2u) {
        *(volatile uint8_t *)(uintptr_t)UINT32_C(0x200271b0) = 1u;
        return 1u;
    }
    return state;
}
