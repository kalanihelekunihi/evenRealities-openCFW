/* SPDX-License-Identifier: MIT
 * Main 0x4d3992: apply class 5 clock configuration record to power block.
 */
#include <stdint.h>

uint32_t g2_main_clock_class5_config_4d3992(uint32_t configuration)
{
    if (configuration == 0u)
        return 6u;
    const volatile uint8_t *const bytes =
        (const volatile uint8_t *)(uintptr_t)configuration;
    volatile uint32_t *const enable =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x4000404c);
    volatile uint32_t *const mode =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x40004048);
    volatile uint32_t *const divider =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x40004050);
    *enable |= 7u;
    *mode = (*mode & ~UINT32_C(0x20000000)) |
            (((uint32_t)bytes[0] & 1u) << 29);
    *divider = (*divider & ~3u) | ((uint32_t)bytes[1] & 3u);
    const uint32_t frequency =
        (uint32_t)bytes[4] | ((uint32_t)bytes[5] << 8) |
        ((uint32_t)bytes[6] << 16) | ((uint32_t)bytes[7] << 24);
    *divider = (*divider & UINT32_C(0x80000003)) |
               ((frequency & UINT32_C(0x1fffffff)) << 2);
    *mode |= 1u;
    return 0u;
}
