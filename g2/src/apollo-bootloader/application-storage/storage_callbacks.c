/* SPDX-License-Identifier: MIT
 * Source providers for the three Thumb callbacks in the scatter descriptor at
 * 0x200001e8 (+0x18, +0x1c, +0x20). Address-boundary values are from the
 * locked configuration table; physical MRAM programming remains ROM-owned.
 */
#include "storage_callbacks.h"
#include "device_info_dispatch.h"

#include <stddef.h>

#define LIMIT_CACHE ((volatile uint32_t *)(uintptr_t)0x200270c8u)
#define PROGRAM_KEY 0x12344321u

__attribute__((section(".boot_storage_range_table"), used))
const uint16_t opencfw_boot_storage_range_limits[4] = {
    0x0400u, 0x0800u, 0x0c00u, 0x1000u,
};

extern uint32_t opencfw_boot_control_critical_save(void);
extern uint32_t opencfw_boot_mram_dispatch(uint32_t key, const void *source,
                                          uint32_t destination,
                                          uint32_t words);

static void source_copy(uint8_t *destination, const uint8_t *source,
                        uint32_t size)
{
    while (size != 0u) {
        *destination++ = *source++;
        --size;
    }
}

uint32_t opencfw_boot_storage_range_valid(uint32_t address, uint32_t size)
{
    /* Stock computes address+size-1 first, but later compares the original
     * address and size separately; the computed end is not consumed. */
    const uint32_t unused_end = address + size - 1u;
    (void)unused_end;
    uint32_t limit = *LIMIT_CACHE;
    if (limit == 0u) {
        volatile uint32_t record[16];
        (void)opencfw_boot_device_info_query(1u, record);
        limit = record[11];
        *LIMIT_CACHE = limit;
    }

    /* `address` is stock r5 and `size` is stock r4. The first comparison
     * rejects addresses below 0x4000; addresses at or above it pass this
     * stage, then the size is compared strictly below the cached limit. */
    if (address < 0x4000u)
        return 0u;
    return size < limit ? 1u : 0u;
}

/* Stock veneer 0x430a9c targets this source body. */
uint32_t opencfw_boot_storage_read_impl(void *destination, const void *source,
                                        uint32_t size)
{
    if (opencfw_boot_storage_range_valid((uint32_t)(uintptr_t)source,
                                         size) == 0u)
        return UINT32_MAX;
    source_copy((uint8_t *)destination, (const uint8_t *)source, size);
    return 0u;
}

static uint32_t program_with_critical_state(uint32_t destination,
                                           const void *source,
                                           uint32_t size)
{
    const uint32_t previous = opencfw_boot_control_critical_save();
    (void)opencfw_boot_mram_dispatch(PROGRAM_KEY, source, destination,
                                     (size + 3u) >> 2);
    __asm__ volatile("msr primask, %0" :: "r"(previous) : "memory");
    return 0u;
}

/* Stock veneer 0x430ac4 targets this source body. */
uint32_t opencfw_boot_storage_program_impl(uint32_t destination,
                                           const void *source,
                                           uint32_t size)
{
    if (opencfw_boot_storage_range_valid(destination, size) == 0u)
        return UINT32_MAX;
    (void)program_with_critical_state(destination, source, size);
    return 0u;
}

/* Stock veneer 0x430aec targets this source body; there is no erase call. */
uint32_t opencfw_boot_storage_erase_validate_impl(uint32_t destination)
{
    return opencfw_boot_storage_range_valid(destination, 4u) != 0u
        ? 0u : UINT32_MAX;
}
