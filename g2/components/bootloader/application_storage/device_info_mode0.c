/* SPDX-License-Identifier: MIT
 * Source reconstruction of stock mode-0 helper 0x41d69c.
 */
#include "device_info_mode0.h"
#include "device_mode_wait.h"

#define POWER_STATE (*(volatile uint32_t *)(uintptr_t)0x4002000cu)

/* Lower provider corresponds to stock call 0x421548. Its wait/event behavior
 * depends on the boot scheduler and remains separately replaceable. */
void opencfw_boot_device_mode_configure(volatile uint32_t *record)
{
    uint32_t result = 0u;
    const uint32_t wait_status = opencfw_boot_device_mode_wait(
        1u, 0x244u, 1u, &result);
    volatile uint32_t *const mode_word = record + 3;

    *mode_word = 0u;
    if (wait_status == 0u) {
        const uint32_t power_mode = (POWER_STATE >> 4) & 0x0fu;
        if (power_mode == 2u && (POWER_STATE & 0x0fu) >= 2u && result < 255u) {
            if ((POWER_STATE & 0x0fu) != 3u)
                --result;
            *mode_word = ((2u << 8) | (uint8_t)result) | 0x30000u;
        } else {
            *mode_word = (uint8_t)result;
            *mode_word |= 0x10000u;
        }
    } else {
        *mode_word = (uint8_t)result;
    }
}
