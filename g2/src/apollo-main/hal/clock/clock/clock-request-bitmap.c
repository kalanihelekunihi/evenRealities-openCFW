/* SPDX-License-Identifier: MIT
 * Main 0x4c37a8/0x4c37fe/0x4c377a: seven clock-class request bitmaps.
 * Each class has two 32-bit words at the locked SRAM table address.
 */
#include <stdint.h>

#define CLOCK_REQUEST_BITMAP_BASE UINT32_C(0x20073324)

static volatile uint32_t *clock_word(uint32_t clock_class, uint32_t id)
{
    return (volatile uint32_t *)(uintptr_t)
        (CLOCK_REQUEST_BITMAP_BASE + ((uint8_t)clock_class * 8u) +
         (((uint8_t)id >> 5) * 4u));
}

uint32_t g2_main_clock_request_test_4c37a8(uint32_t clock_class,
                                             uint32_t id)
{
    const uint8_t bit = (uint8_t)id & 31u;
    return (*clock_word(clock_class, id) >> bit) & 1u;
}

uint32_t g2_main_clock_request_set_4c37fe(uint32_t clock_class,
                                            uint32_t id,
                                            uint32_t enabled)
{
    if ((uint8_t)clock_class >= 7u || (uint8_t)id >= 0x39u)
        return 6u;
    volatile uint32_t *const word = clock_word(clock_class, id);
    const uint32_t bit = UINT32_C(1) << ((uint8_t)id & 31u);
    if ((uint8_t)enabled == 0u)
        *word &= ~bit;
    else
        *word |= bit;
    return 0u;
}

uint32_t g2_main_clock_request_any_4c377a(uint32_t clock_class)
{
    const volatile uint32_t *const words =
        clock_word(clock_class, 0u);
    return words[0] != 0u || words[1] != 0u;
}
