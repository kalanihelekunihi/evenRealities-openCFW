/* SPDX-License-Identifier: MIT
 * Source reconstruction of stock selector/record wrapper 0x41d792.
 */
#include "device_info_dispatch.h"
#include "device_info.h"
#include "device_info_mode0.h"

#define SYSTEM_STATE (*(volatile uint32_t *)(uintptr_t)0x40020014u)

uint32_t opencfw_boot_device_info_query(uint32_t selector,
                                        volatile uint32_t *record)
{
    if (record == 0)
        return 6u;

    switch ((uint8_t)selector) {
    case 0u: {
        const uint32_t mode = SYSTEM_STATE;
        volatile uint8_t *const bytes = (volatile uint8_t *)record;

        bytes[1] = (mode & 3u) >= 2u ? 1u : 0u;
        bytes[0] = (mode & 3u) >= 2u ? 1u : 0u;
        bytes[2] = (mode & 3u) == 3u ? 2u :
                   (mode & 3u) == 0u ? 0u : 1u;
        bytes[3] = (uint8_t)((SYSTEM_STATE >> 2) & 3u);
        bytes[4] = (uint8_t)((SYSTEM_STATE >> 6) & 1u);
        bytes[5] = (uint8_t)((SYSTEM_STATE >> 7) & 1u);
        bytes[6] = (uint8_t)((SYSTEM_STATE >> 8) & 1u);
        bytes[7] = (uint8_t)((SYSTEM_STATE >> 9) & 1u);
        bytes[8] = (uint8_t)((SYSTEM_STATE >> 10) & 1u);
        bytes[9] = (uint8_t)((SYSTEM_STATE >> 19) & 1u);
        bytes[10] = (uint8_t)((SYSTEM_STATE >> 20) & 3u);
        opencfw_boot_device_mode_configure(record);
        return 0u;
    }
    case 1u:
        opencfw_boot_device_info_initialize(record);
        return 0u;
    default:
        return 6u;
    }
}
