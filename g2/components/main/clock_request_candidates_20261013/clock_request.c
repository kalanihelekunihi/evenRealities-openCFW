/* SPDX-License-Identifier: MIT
 * Main 0x480f0c clock request. Validation masks are source-owned copies of
 * the locked Main table at 0x768ba8 and 0x768bc4.
 */
#include <stdint.h>

#define CLOCK_REG_BASE UINT32_C(0x40010000)
#define CLOCK_UNLOCK_REG UINT32_C(0x40010400)

extern uint32_t g2_main_critical_save_473940(void);

__attribute__((used, aligned(4), section(".main_clock_masks")))
const uint32_t g2_main_clock_type_mask[7] = {
    0x00000000u, 0x00003fe0u, 0x000003ffu, 0x1ffbfe00u,
    0x0007c000u, 0x00000000u, 0x00000000u,
};

__attribute__((used, aligned(4), section(".main_clock_masks")))
const uint32_t g2_main_clock_secondary_mask[7] = {
    0x8fc007e6u, 0xe3f3ffffu, 0x81ffffffu, 0xffffffffu,
    0xf00fc07fu, 0x00000001u, 0x00000189u,
};

uint32_t g2_main_clock_request_480f0c(uint32_t clock_id, uint32_t value)
{
    if (clock_id >= 0xe0u)
        return 5u;

    const uint32_t word = clock_id >> 5;
    const uint32_t bit = UINT32_C(1) << (clock_id & 31u);
    if ((g2_main_clock_type_mask[word] & bit) == 0u) {
        if (((value >> 10) & 3u) >= 2u &&
            (g2_main_clock_secondary_mask[word] & bit) == 0u)
            return 7u;
    } else {
        const uint32_t setting = (value >> 13) & 7u;
        if (setting != 0u && setting != 6u && setting != 1u)
            return 7u;
    }

    const uint32_t previous_mask = g2_main_critical_save_473940();
    volatile uint32_t *const unlock =
        (volatile uint32_t *)(uintptr_t)CLOCK_UNLOCK_REG;
    *unlock = 0x73u;
    *(volatile uint32_t *)(uintptr_t)(CLOCK_REG_BASE + clock_id * 4u) = value;
    *unlock = 0u;
    __asm__ volatile("msr primask, %0" :: "r"(previous_mask) : "memory");
    return 0u;
}
