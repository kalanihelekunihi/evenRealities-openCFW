/* Recovered class-5 generator ownership, config leaves, and callback path.
 * Register and poll behavior is validated only in synthetic memory. The
 * CLKGEN HF2ADJ/HFRC2 leaves are upstream am_hal_clkgen.c. */
#include "clock_class_provider5.h"
#include <stdbool.h>
#include "am_mcu_apollo.h"
#include "am_hal_clkgen_private.h" /* AmbiqSuite 5.1.0; stock 0x426c24..0x426d2c */

#include "clock_class_provider2.h"
#include "clock_class_provider4.h"
#include "clock_wait_4216b2.h"
#include "clock_class_providers.h"
#include "clock_popcount_421584.h"

enum {
    CLOCK_USER_BITS_BASE = 0x20026e74u,
    CLOCK5_CONFIG_PRESENT = 0x20027034u,
    CLOCK5_CONFIG = 0x20026ff8u,
    CLOCK5_FEATURE_ENABLED = 0x20000551u,
    CLOCK5_CALLBACK_ACTIVE = 0x2002719du,
    CLOCK5_CALLBACK_POINTER = 0x20027048u,
    CLOCK5_INITIALIZE_FLAG = 0x2002719fu
};

static volatile uint32_t *user_word(uint8_t user_id)
{
    const uint32_t word_index = 5u * 2u + ((uint32_t)user_id >> 5);
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

static void callback_finish(uint32_t *timeout)
{
    volatile uint8_t *const active =
        (volatile uint8_t *)(uintptr_t)CLOCK5_CALLBACK_ACTIVE;
    if (*active == 0u)
        return;

    opencfw_bl_clock_wait_active(active, timeout);

    const uint32_t previous = critical_save();
    *active = 0u;
    *(volatile uint32_t *)(uintptr_t)CLOCK5_CALLBACK_POINTER = 0u;
    critical_restore(previous);
}

uint32_t opencfw_bl_clock_request_id5(uint8_t user_id)
{
    uint32_t timeout = 50u;
    uint32_t status = 0u;
    volatile uint8_t *const active =
        (volatile uint8_t *)(uintptr_t)CLOCK5_CALLBACK_ACTIVE;
    volatile uint32_t *const callback_pointer =
        (volatile uint32_t *)(uintptr_t)CLOCK5_CALLBACK_POINTER;

    if (user_present(user_id)) {
        const uint32_t previous = critical_save();
        if (*active != 0u)
            timeout = *(uint32_t *)(uintptr_t)*callback_pointer;
        *callback_pointer = (uint32_t)(uintptr_t)&timeout;
        critical_restore(previous);
        callback_finish(&timeout);
        return 0u;
    }

    uint32_t previous = critical_save();
    uint32_t other_clock_status = 0u;
    if (user_count() == 0u)
        *(volatile uint8_t *)(uintptr_t)CLOCK5_INITIALIZE_FLAG = 1u;
    user_update(user_id, 1u);
    critical_restore(previous);

    if (*(volatile uint8_t *)(uintptr_t)CLOCK5_FEATURE_ENABLED != 0u &&
        *(volatile uint32_t *)(uintptr_t)CLOCK5_CONFIG_PRESENT != 0u) {
        const uint8_t config_mode =
            *(volatile uint8_t *)(uintptr_t)CLOCK5_CONFIG;
        other_clock_status = config_mode == 0u ?
            opencfw_bl_clock_request_id2(0x36u) :
            opencfw_bl_clock_request_id3(0x36u);
        if (other_clock_status != 0u) {
            previous = critical_save();
            user_update(user_id, 0u);
            critical_restore(previous);
        }
    }

    if (other_clock_status == 0u) {
        previous = critical_save();
        if (*active != 0u)
            timeout = *(uint32_t *)(uintptr_t)*callback_pointer;
        if (*(volatile uint8_t *)(uintptr_t)CLOCK5_FEATURE_ENABLED == 0u)
            status = 1u;

        if (status == 0u &&
            *(volatile uint8_t *)(uintptr_t)CLOCK5_INITIALIZE_FLAG != 0u) {
            *(volatile uint8_t *)(uintptr_t)CLOCK5_INITIALIZE_FLAG = 0u;
            (void)am_hal_clkgen_private_hfrc2_force_on(true);
            if (*(volatile uint32_t *)(uintptr_t)CLOCK5_CONFIG_PRESENT != 0u) {
                status = am_hal_clkgen_private_hf2adj_apply((am_hal_clkgen_hfrc2adj_t *)(const uint8_t *)(uintptr_t)CLOCK5_CONFIG);
                if (status == 0u) {
                    if (*active == 0u)
                        *active = 1u;
                } else {
                    (void)am_hal_clkgen_private_hfrc2_force_on(false);
                }
            }
        }

        if (status != 0u)
            user_update(user_id, 0u);
        if (*(volatile uint8_t *)(uintptr_t)CLOCK5_CALLBACK_ACTIVE != 0u)
            *callback_pointer = (uint32_t)(uintptr_t)&timeout;
        critical_restore(previous);
    }

    if (status != 0u &&
        *(volatile uint8_t *)(uintptr_t)CLOCK5_FEATURE_ENABLED != 0u &&
        *(volatile uint32_t *)(uintptr_t)CLOCK5_CONFIG_PRESENT != 0u) {
        if (*(volatile uint8_t *)(uintptr_t)CLOCK5_CONFIG == 0u)
            (void)opencfw_bl_clock_release_id2(0x36u);
        else
            (void)opencfw_bl_clock_release_id3(0x36u);
    }

    callback_finish(&timeout);
    return status;
}

uint32_t opencfw_bl_clock_release_id5(uint8_t user_id)
{
    if (!user_present(user_id))
        return 0u;

    const uint32_t previous = critical_save();
    user_update(user_id, 0u);
    if (user_count() == 0u) {
        if (*(volatile uint32_t *)(uintptr_t)CLOCK5_CONFIG_PRESENT != 0u) {
            *(volatile uint8_t *)(uintptr_t)CLOCK5_INITIALIZE_FLAG = 0u;
            (void)am_hal_clkgen_private_hf2adj_disable();
            (void)opencfw_bl_clock_release_id2(0x36u);
            (void)opencfw_bl_clock_release_id3(0x36u);
            *(volatile uint8_t *)(uintptr_t)CLOCK5_CALLBACK_ACTIVE = 0u;
            *(volatile uint32_t *)(uintptr_t)CLOCK5_CALLBACK_POINTER = 0u;
        }
        (void)am_hal_clkgen_private_hfrc2_force_on(false);
    }
    critical_restore(previous);
    return 0u;
}
