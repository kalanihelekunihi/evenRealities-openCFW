/* SPDX-License-Identifier: MIT
 * Main 0x4d391e/0x4d3952/0x4d39e4 clock and power register leaves.
 */
#include <stdint.h>

extern uint32_t g2_main_mspi_status_poll_480826(uint32_t,
                                                  uintptr_t,
                                                  uint32_t,
                                                  uint32_t,
                                                  uint32_t);

uint32_t g2_main_clock_class4_off_4d391e(uint32_t enabled)
{
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x40004044);
    *control = (*control & ~1u) | ((uint8_t)enabled != 0u);
    return 0u;
}

uint32_t g2_main_clock_class5_off_4d3952(uint32_t enabled)
{
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x40004044);
    if ((uint8_t)enabled == 0u) {
        *control &= ~UINT32_C(0x20);
        return 0u;
    }
    if ((*control & UINT32_C(0x20)) != 0u)
        return 0u;
    *control |= UINT32_C(0x20);
    return g2_main_mspi_status_poll_480826(100u,
                                             UINT32_C(0x40004030),
                                             UINT32_C(0x01000000),
                                             UINT32_C(0x01000000), 1u);
}

uint32_t g2_main_clock_class5_prepare_off_4d39e4(void)
{
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x40004048);
    *control &= ~1u;
    return 0u;
}
