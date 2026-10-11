/* SPDX-License-Identifier: MIT
 * Image-A XIP native suspend/resume registration, 0x102076c0/0x10207718.
 * The 0x2002dfbc registry is runtime BSS; source owns the two scan/update
 * algorithms, not a fabricated initialized registry.
 */
#include <stdint.h>

extern void gx8002_resident_memcpy_25738(void *, const void *, uint32_t);

static uint32_t register_pair(const void *pair, uint32_t slots_offset,
                              uint32_t count_offset)
{
    volatile uint8_t *const registry =
        (volatile uint8_t *)(uintptr_t)UINT32_C(0x2002dfbc);
    const uint32_t key = *(const uint32_t *)pair;
    for (uint32_t index = 0u; index < 8u; ++index) {
        volatile uint32_t *const slot =
            (volatile uint32_t *)(void *)(registry + slots_offset + index * 8u);
        if (*slot == key) {
            gx8002_resident_memcpy_25738((void *)slot, pair, 8u);
            return 0u;
        }
    }
    volatile uint32_t *const count =
        (volatile uint32_t *)(void *)(registry + count_offset);
    uint32_t index = *count;
    if (index >= 8u || key == 0u) return UINT32_MAX;
    gx8002_resident_memcpy_25738(
        (void *)(registry + slots_offset + index * 8u), pair, 8u);
    *count = *count + 1u;
    return 0u;
}

uint32_t gx8002_xip_register_suspend_102076c0(const void *pair)
{
    return register_pair(pair, 0x10u, 0x08u);
}

uint32_t gx8002_xip_register_resume_10207718(const void *pair)
{
    return register_pair(pair, 0x50u, 0x0cu);
}
