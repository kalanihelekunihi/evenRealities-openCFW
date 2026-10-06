/* SPDX-License-Identifier: MIT
 * Source providers for the three Thumb callbacks in the scatter descriptor at
 * 0x200001e8 (+0x18, +0x1c, +0x20). Address-boundary values are from the
 * locked configuration table; physical MRAM programming remains ROM-owned.
 */
#include "storage_callbacks.h"

#include <stddef.h>

#define LIMIT_CACHE ((volatile uint32_t *)(uintptr_t)0x200270c8u)
#define MODE_REGISTER (*(volatile uint32_t *)(uintptr_t)0x40020014u)
#define RANGE_TABLE ((const volatile uint16_t *)(uintptr_t)0x43401cu)
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
    /* The raw target computes this 32-bit end value before its size check. */
    const uint32_t inclusive_end = address + size - 1u;
    uint32_t limit = *LIMIT_CACHE;
    if (limit == 0u) {
        const uint32_t mode = (MODE_REGISTER >> 2) & 3u;
        limit = (uint32_t)RANGE_TABLE[mode] << 10;
        *LIMIT_CACHE = limit;
    }

    if (size >= 0x4000u)
        return 0u;
    return inclusive_end < limit ? 1u : 0u;
}

/* Stock entry 0x430a9c: (RAM destination, MRAM source, byte count). */
__attribute__((section(".text.storage_read"), noinline))
uint32_t opencfw_boot_storage_read(void *destination, const void *source,
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

/* Stock entry 0x430ac4: (MRAM destination, RAM source, byte count). */
__attribute__((section(".text.storage_program"), noinline))
uint32_t opencfw_boot_storage_program(uint32_t destination,
                                      const void *source, uint32_t size)
{
    if (opencfw_boot_storage_range_valid(destination, size) == 0u)
        return UINT32_MAX;
    (void)program_with_critical_state(destination, source, size);
    return 0u;
}

/* Stock entry 0x430aec: validate a 4-byte span; this callback does no erase. */
__attribute__((section(".text.storage_erase"), noinline))
uint32_t opencfw_boot_storage_erase_validate(uint32_t destination)
{
    return opencfw_boot_storage_range_valid(destination, 4u) != 0u
        ? 0u : UINT32_MAX;
}
