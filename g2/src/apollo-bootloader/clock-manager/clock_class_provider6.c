/* Recovered class-6 PLL clock ownership (am_hal_clkmgr SYSPLL class). The
 * SYSPLL itself is the upstream AmbiqSuite 5.1.0 am_hal_syspll.c, which the
 * stock bootloader links verbatim (0x426d48..0x4275ea). The synthetic
 * validation makes no physical power/lock claim. */
#include "clock_class_provider6.h"

#include "am_mcu_apollo.h"

#include "clock_class_provider2.h"
#include "clock_class_provider4.h"
#include "clock_class_providers.h"
#include "clock_popcount_421584.h"

enum {
    CLOCK_USER_BITS_BASE = 0x20026e74u,
    CLOCK6_CONFIG = 0x20027004u,
    CLOCK6_FEATURE_ENABLED = 0x2002719au,
    CLOCK6_INITIALIZE_FLAG = 0x200271a0u,
    CLOCK6_HANDLE_POINTER = 0x2002703cu
};

static volatile uint32_t *user_word(uint8_t user_id)
{
    const uint32_t word_index = 6u * 2u + ((uint32_t)user_id >> 5);
    return (volatile uint32_t *)(uintptr_t)(CLOCK_USER_BITS_BASE +
                                            4u * word_index);
}

static uint32_t user_present(uint8_t user_id)
{
    return (*user_word(user_id) & (1u << (user_id & 31u))) != 0u;
}

static void user_update(uint8_t user_id, uint32_t request)
{
    volatile uint32_t *const word = user_word(user_id);
    const uint32_t bit = 1u << (user_id & 31u);
    if (request != 0u)
        *word |= bit;
    else
        *word &= ~bit;
}

static uint32_t user_count(void)
{
    volatile uint32_t *const words = user_word(0u);
    uint32_t count = 0u;
    for (uint32_t i = 0u; i < 2u; ++i) {
        count += opencfw_boot_clock_popcount(words[i]);
    }
    return count;
}

static uint32_t critical_save(void)
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

uint32_t opencfw_bl_clock_request_id6(uint8_t user_id)
{
    if (user_present(user_id))
        return 0u;

    uint32_t previous = critical_save();
    if (user_count() == 0u)
        *(volatile uint8_t *)(uintptr_t)CLOCK6_INITIALIZE_FLAG = 1u;
    user_update(user_id, 1u);
    critical_restore(previous);

    uint32_t status = 0u;
    const uint8_t feature_enabled =
        *(volatile uint8_t *)(uintptr_t)CLOCK6_FEATURE_ENABLED;
    const uint8_t config_mode =
        *(volatile uint8_t *)(uintptr_t)CLOCK6_CONFIG;
    if (feature_enabled != 0u) {
        if (config_mode == 0u) {
            status = opencfw_bl_clock_request_id2(0x35u);
            (void)opencfw_bl_clock_request_id3(0x35u);
        } else {
            status = opencfw_bl_clock_request_id3(0x35u);
            (void)opencfw_bl_clock_request_id2(0x35u);
        }
    }

    uint32_t pll_started = 0u;
    previous = critical_save();
    if (status == 0u) {
        if (*(volatile uint8_t *)(uintptr_t)CLOCK6_FEATURE_ENABLED == 0u)
            status = 1u;

        if (status == 0u &&
            *(volatile uint8_t *)(uintptr_t)CLOCK6_INITIALIZE_FLAG != 0u) {
            *(volatile uint8_t *)(uintptr_t)CLOCK6_INITIALIZE_FLAG = 0u;
            void **const handle_pointer =
                (void **)(uintptr_t)CLOCK6_HANDLE_POINTER;
            if (*handle_pointer == 0)
                status = am_hal_syspll_initialize(0u, handle_pointer);
            if (status == 0u)
                status = am_hal_syspll_configure(*handle_pointer,
                    (am_hal_syspll_config_t *)(uintptr_t)CLOCK6_CONFIG);
            if (status == 0u)
                status = am_hal_syspll_enable(*handle_pointer);
            if (status == 0u) {
                pll_started = 1u;
            } else if (*handle_pointer != 0) {
                (void)am_hal_syspll_deinitialize(*handle_pointer);
                *handle_pointer = 0;
            }
        }
        if (status != 0u)
            user_update(user_id, 0u);
    } else {
        user_update(user_id, 0u);
    }
    critical_restore(previous);

    if (feature_enabled != 0u) {
        if (status == 0u) {
            if (config_mode == 0u)
                (void)opencfw_bl_clock_release_id3(0x35u);
            else
                (void)opencfw_bl_clock_release_id2(0x35u);
        } else {
            (void)opencfw_bl_clock_release_id2(0x35u);
            (void)opencfw_bl_clock_release_id3(0x35u);
        }
    }

    if (pll_started != 0u) {
        void **const handle_pointer =
            (void **)(uintptr_t)CLOCK6_HANDLE_POINTER;
        status = am_hal_syspll_lock_wait(*handle_pointer);
    }
    return status;
}

uint32_t opencfw_bl_clock_release_id6(uint8_t user_id)
{
    if (!user_present(user_id))
        return 0u;

    const uint32_t previous = critical_save();
    user_update(user_id, 0u);
    if (user_count() == 0u) {
        *(volatile uint8_t *)(uintptr_t)CLOCK6_INITIALIZE_FLAG = 0u;
        void **const handle_pointer =
            (void **)(uintptr_t)CLOCK6_HANDLE_POINTER;
        (void)am_hal_syspll_disable(*handle_pointer);
        (void)am_hal_syspll_deinitialize(*handle_pointer);
        *handle_pointer = 0;
        if (*(volatile uint8_t *)(uintptr_t)CLOCK6_CONFIG == 0u)
            (void)opencfw_bl_clock_release_id2(0x35u);
        else
            (void)opencfw_bl_clock_release_id3(0x35u);
    }
    critical_restore(previous);
    return 0u;
}
