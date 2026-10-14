/* SPDX-License-Identifier: MIT
 * Main 0x4809c4: clock mode and source selection, operations 0..6.
 */
#include <stdint.h>

extern void audio_delay_us_selected(uint32_t);
extern uint32_t g2_main_mspi_clock_acquire_4c44bc(uint32_t, uint32_t);
extern uint32_t g2_main_mspi_clock_release_4c4530(uint32_t, uint32_t);

uint64_t g2_main_clock_mode_set_4809c4(uint32_t operation,
                                         const uint32_t *configuration,
                                         uint32_t unused, uint32_t high)
{
    (void)unused;
    const uint8_t mode = (uint8_t)operation;
    volatile uint32_t *const selector =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x40020120);
    volatile uint32_t *const divider =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x40020128);
    volatile uint32_t *const control =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x4002012c);
    const uint32_t mux =
        *(const volatile uint32_t *)(uintptr_t)UINT32_C(0x200001e0);
    const uint32_t divisor =
        *(const volatile uint32_t *)(uintptr_t)UINT32_C(0x200001e4);
    uint32_t status = 0u;

    switch (mode) {
    case 0:
        high = (*selector & UINT32_C(0xffffffe0)) |
               (configuration != 0 && (uint8_t)*configuration == 1u ? 5u : 0x19u);
        *selector = high;
        break;
    case 1:
        high = *selector & UINT32_C(0xfffffffc);
        *selector = high;
        break;
    case 2:
        *divider = (*divider & UINT32_C(0xc0007000)) |
                   (mux & 0x3fu) | ((divisor & 0xfu) << 6) |
                   UINT32_C(0x0fff8c00);
        high = (*control & UINT32_C(0xffffffdd)) | 2u;
        *control = high;
        *control |= 1u;
        *control |= 0x10u;
        *control |= 8u;
        audio_delay_us_selected(5u);
        *control &= UINT32_C(0xffffffef);
        if (configuration != 0 && (uint8_t)*configuration == 1u) {
            high = (*control & UINT32_C(0xfffffef6)) | 0x100u;
            *control = high;
        }
        break;
    case 3:
        *divider = (mux & 0x3fu) | ((divisor & 0xfu) << 6) |
                   UINT32_C(0x0fff8c00);
        *control = (*control & UINT32_C(0xffffffdd)) | 0x22u;
        *control |= 1u;
        if (configuration == 0 || (uint8_t)*configuration != 1u)
            high = (*control & UINT32_C(0xffffffd7)) | 8u;
        else
            high = (*control & UINT32_C(0xfffffefe)) | 0x100u;
        *control = high;
        break;
    case 4:
        *divider = (*divider & UINT32_C(0xc0007000)) |
                   (mux & 0x3fu) | ((divisor & 0xfu) << 6) |
                   UINT32_C(0x03118000);
        high = (*control & UINT32_C(0xfffffed4)) | 2u;
        *control = high;
        break;
    case 5:
        status = g2_main_mspi_clock_acquire_4c44bc(2u, 0x34u);
        if (status != 0u) break;
        if (configuration == 0) {
            high = (*divider & UINT32_C(0xffff8fff)) | 0x4000u;
        } else {
            const uint32_t choice = *configuration;
            if (choice != 0u && (uint32_t)(choice - 3u) > 4u) {
                status = 6u;
                break;
            }
            high = (*divider & UINT32_C(0xffff8fff)) |
                   ((choice & 7u) << 12);
        }
        *divider = high;
        *control |= 0x80u;
        break;
    case 6:
        *divider |= 0x7000u;
        *control &= UINT32_C(0xffffff7f);
        status = g2_main_mspi_clock_release_4c4530(2u, 0x34u);
        break;
    default:
        status = 6u;
        break;
    }
    return ((uint64_t)high << 32) | status;
}
