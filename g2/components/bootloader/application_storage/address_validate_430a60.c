/* SPDX-License-Identifier: MIT
 * Stock 0x430a60..0x430a9c validates a requested span against the cached
 * device-info range. The range cache at 0x200270c8 and device-info record
 * word 11 are native, source-owned contracts. Query mode 1 populates that
 * word; real peripheral reads and delay behavior reside in its selected child.
 */
#include <stdint.h>

#include "device_info_dispatch.h"

#define BOOT_RANGE_CACHE (*(volatile uint32_t *)(uintptr_t)0x200270c8u)

uint32_t opencfw_boot_address_validate(uint32_t address, uint32_t length)
{
    if (BOOT_RANGE_CACHE == 0u) {
        uint32_t record[16];
        (void)opencfw_boot_device_info_query(1u, record);
        BOOT_RANGE_CACHE = record[11];
    }
    if (address < 0x4000u)
        return 0u;
    return length < BOOT_RANGE_CACHE ? 1u : 0u;
}
