/* Recovered private clock classes 1 and 3, with the directly called
 * power-register update helper. Addresses and bit tables are taken from the
 * locked bootloader image; MMIO is only exercised in synthetic tests. */
#include "clock_class_providers.h"

enum {
    CLOCK_USER_BITS_BASE = 0x20026e74u,
    CLOCK1_ENABLED_FLAG = 0x20000088u,
    CLOCK3_ENABLED_FLAG = 0x2000008cu,
    POWER_REGISTER_BASE = 0x40010000u,
    POWER_REGISTER_LATCH = 0x40010400u,
    POWER_REGISTER_COUNT = 0xe0u
};

static const uint32_t register_allowed_mode[] = {
    0x00000000u, 0x00003fe0u, 0x000003ffu, 0x1ffbfe00u,
    0x0007c000u, 0x00000000u, 0x00000000u
};

static const uint32_t register_nonstandard_allowed[] = {
    0x8fc007e6u, 0xe3f3ffffu, 0x81ffffffu, 0xffffffffu,
    0xf00fc07fu, 0x00000001u, 0x00000189u
};

static volatile uint32_t *clock_user_word(uint8_t clock_id,
                                          uint8_t user_id)
{
    const uint32_t word_index = (uint32_t)clock_id * 2u +
                                ((uint32_t)user_id >> 5);
    return (volatile uint32_t *)(uintptr_t)(CLOCK_USER_BITS_BASE +
                                            word_index * 4u);
}

static uint32_t clock_user_has(uint8_t clock_id, uint8_t user_id)
{
    const uint32_t mask = 1u << (user_id & 31u);
    return (*clock_user_word(clock_id, user_id) & mask) != 0u;
}

static uint32_t clock_user_update(uint8_t clock_id, uint8_t user_id,
                                  uint32_t request)
{
    if (clock_id >= 7u || user_id >= 57u)
        return 6u;
    volatile uint32_t *const word = clock_user_word(clock_id, user_id);
    const uint32_t mask = 1u << (user_id & 31u);
    if (request)
        *word |= mask;
    else
        *word &= ~mask;
    return 0u;
}

static uint32_t critical_save_disable(void)
{
    uint32_t previous;
    __asm volatile("mrs %0, primask\n\tcpsid i"
                   : "=r"(previous) :: "memory");
    return previous;
}

static void critical_restore(uint32_t previous)
{
    __asm volatile("msr primask, %0" :: "r"(previous) : "memory");
}

uint32_t opencfw_bl_clock_request_id1(uint8_t user_id)
{
    if (*(volatile uint32_t *)(uintptr_t)CLOCK1_ENABLED_FLAG == 0u)
        return 7u;
    if (clock_user_has(1u, user_id))
        return 0u;

    const uint32_t previous = critical_save_disable();
    (void)clock_user_update(1u, user_id, 1u);
    critical_restore(previous);
    return 0u;
}

uint32_t opencfw_bl_clock_release_id1(uint8_t user_id)
{
    if (!clock_user_has(1u, user_id))
        return 0u;

    const uint32_t previous = critical_save_disable();
    (void)clock_user_update(1u, user_id, 0u);
    critical_restore(previous);
    return 0u;
}

uint32_t opencfw_bl_power_register_update(uint32_t register_id,
                                          uint32_t value)
{
    if (register_id >= POWER_REGISTER_COUNT)
        return 5u;

    const uint32_t word = register_id >> 5;
    const uint32_t mask = 1u << (register_id & 31u);
    const uint32_t standard_modes = register_allowed_mode[word] & mask;
    if (standard_modes == 0u) {
        const uint32_t requested_mode = (value & 0x0fffu) >> 10;
        if (requested_mode > 1u &&
            (register_nonstandard_allowed[word] & mask) == 0u)
            return 7u;
    } else {
        const uint32_t requested_mode = (value & 0xffffu) >> 13;
        if (requested_mode != 0u && requested_mode != 6u &&
            requested_mode != 1u)
            return 7u;
    }

    const uint32_t previous = critical_save_disable();
    *(volatile uint32_t *)(uintptr_t)POWER_REGISTER_LATCH = 0x73u;
    *(volatile uint32_t *)(uintptr_t)(POWER_REGISTER_BASE +
                                      register_id * 4u) = value;
    *(volatile uint32_t *)(uintptr_t)POWER_REGISTER_LATCH = 0u;
    critical_restore(previous);
    return 0u;
}

uint32_t opencfw_bl_clock_request_id3(uint8_t user_id)
{
    const uint32_t request_value = 3u;
    if (*(volatile uint32_t *)(uintptr_t)CLOCK3_ENABLED_FLAG == 0u)
        return 7u;
    if (clock_user_has(3u, user_id))
        return 0u;

    const uint32_t previous = critical_save_disable();
    const uint32_t configured_value = (request_value & 0xfffffff0u) | 10u;
    (void)opencfw_bl_power_register_update(0x0fu, configured_value);
    (void)clock_user_update(3u, user_id, 1u);
    critical_restore(previous);
    return 0u;
}

uint32_t opencfw_bl_clock_release_id3(uint8_t user_id)
{
    if (!clock_user_has(3u, user_id))
        return 0u;

    const uint32_t previous = critical_save_disable();
    (void)clock_user_update(3u, user_id, 0u);
    if (!clock_user_has(3u, user_id)) {
        /* The stock provider scans both words for any remaining class-3
         * users before writing the baseline value to register 15. */
        uint32_t any_user = 0u;
        for (uint32_t word = 0u; word != 2u; ++word)
            any_user |= *(volatile uint32_t *)(uintptr_t)(CLOCK_USER_BITS_BASE +
                          3u * 8u + word * 4u);
        if (any_user == 0u)
            (void)opencfw_bl_power_register_update(0x0fu, 3u);
    }
    critical_restore(previous);
    return 0u;
}
