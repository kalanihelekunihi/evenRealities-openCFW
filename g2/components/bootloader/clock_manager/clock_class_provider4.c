/* Recovered class-4 clock-provider pair and direct HFADJ leaves.
 * Addresses/state are the private bootloader ABI; tests use synthetic SRAM
 * and register memory. The final calibrated wait is the external ROM routine
 * at Thumb address 0x00000041 (raw BL target 0x40). */
#include "clock_class_provider4.h"

enum {
    CLOCK_USER_BITS_BASE = 0x20026e74u,
    CLOCK4_BUSY = 0x2002719cu,
    CLOCK4_CALLBACK_POINTER = 0x20027044u,
    CLOCK4_CONFIG_PRESENT = 0x20027030u,
    CLOCK4_CONFIG_VALUE = 0x20026fecu,
    CLOCK4_REQUEST_ALLOWED = 0x20000550u,
    CLOCK4_DEFERRED_FLAG = 0x2002719eu,
    HFADJ_ENABLE_REGISTER = 0x40004044u,
    HFADJ_CONFIG_REGISTER = 0x40004020u,
    DELAY_CLOCK_MODE_REGISTER = 0x40021000u,
    ROM_CYCLE_WAIT_THUMB = 0x41u
};

static volatile uint32_t *clock_user_word(uint8_t user_id)
{
    const uint32_t word_index = 4u * 2u + ((uint32_t)user_id >> 5);
    return (volatile uint32_t *)(uintptr_t)(CLOCK_USER_BITS_BASE +
                                            word_index * 4u);
}

static uint32_t clock_user_has(uint8_t user_id)
{
    return (*clock_user_word(user_id) & (1u << (user_id & 31u))) != 0u;
}

static void clock_user_update(uint8_t user_id, uint32_t request)
{
    volatile uint32_t *const word = clock_user_word(user_id);
    const uint32_t bit = 1u << (user_id & 31u);
    if (request)
        *word |= bit;
    else
        *word &= ~bit;
}

static uint32_t clock_user_count(void)
{
    uint32_t count = 0u;
    volatile uint32_t *const first = clock_user_word(0u);
    uint32_t value = first[0];
    value = value - ((value >> 1) & 0x55555555u);
    uint32_t folded = ((value >> 2) & 0x33333333u) + (value & 0x33333333u);
    count += (((folded + (folded >> 4)) & 0x0f0f0f0fu) * 0x01010101u) >> 24;
    value = first[1];
    value = value - ((value >> 1) & 0x55555555u);
    folded = ((value >> 2) & 0x33333333u) + (value & 0x33333333u);
    count += (((folded + (folded >> 4)) & 0x0f0f0f0fu) * 0x01010101u) >> 24;
    return count;
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

static uint32_t hfadj_enable(uint32_t enabled)
{
    volatile uint32_t *const reg =
        (volatile uint32_t *)(uintptr_t)HFADJ_ENABLE_REGISTER;
    *reg = (*reg & ~1u) | (enabled != 0u);
    return 0u;
}

static uint32_t hfadj_configure(uint32_t value)
{
    *(volatile uint32_t *)(uintptr_t)HFADJ_CONFIG_REGISTER = value | 1u;
    return 0u;
}

void opencfw_bl_delay_us(uint32_t microseconds)
{
    const float scale32 = (float)microseconds * 32.0f;
    uint32_t waits = (uint32_t)scale32;
    uint32_t threshold = 15u;
    if (((*(volatile uint32_t *)(uintptr_t)DELAY_CLOCK_MODE_REGISTER &
          0x1fu) >> 3) == 2u) {
        const float scaled = ((float)waits * 250.0f) / 96.0f;
        waits = (uint32_t)scaled;
        threshold = 24u;
    }
    if (waits > threshold) {
        typedef void (*rom_cycle_wait_fn)(uint32_t);
        const rom_cycle_wait_fn rom_wait =
            (rom_cycle_wait_fn)(uintptr_t)ROM_CYCLE_WAIT_THUMB;
        rom_wait(waits - threshold);
    }
}

static void callback_finish(uint32_t *timeout)
{
    volatile uint8_t *const active =
        (volatile uint8_t *)(uintptr_t)CLOCK4_BUSY;
    if (*active == 0u)
        return;

    while (*timeout != 0u && *active != 0u) {
        opencfw_bl_delay_us(10u);
        *timeout -= 1u;
    }

    const uint32_t previous = critical_save_disable();
    *(volatile uint8_t *)(uintptr_t)CLOCK4_DEFERRED_FLAG = 1u;
    *active = 0u;
    *(volatile uint32_t *)(uintptr_t)CLOCK4_CALLBACK_POINTER = 0u;
    critical_restore(previous);
}

uint32_t opencfw_bl_clock_request_id4(uint8_t user_id)
{
    uint32_t timeout = 1000u;
    uint32_t status = 0u;
    volatile uint8_t *const active =
        (volatile uint8_t *)(uintptr_t)CLOCK4_BUSY;
    volatile uint32_t *const callback_pointer =
        (volatile uint32_t *)(uintptr_t)CLOCK4_CALLBACK_POINTER;

    if (clock_user_has(user_id)) {
        const uint32_t previous = critical_save_disable();
        if (*active != 0u)
            timeout = *(uint32_t *)(uintptr_t)*callback_pointer;
        *callback_pointer = (uint32_t)(uintptr_t)&timeout;
        critical_restore(previous);
        callback_finish(&timeout);
        return 0u;
    }

    uint32_t previous = critical_save_disable();
    if (*active != 0u)
        timeout = *(uint32_t *)(uintptr_t)*callback_pointer;

    if (*(volatile uint8_t *)(uintptr_t)CLOCK4_REQUEST_ALLOWED == 0u) {
        status = 1u;
    } else {
        if (clock_user_count() == 0u) {
            (void)hfadj_enable(1u);
            if (*(volatile uint32_t *)(uintptr_t)CLOCK4_CONFIG_PRESENT != 0u) {
                status = hfadj_configure(
                    *(volatile uint32_t *)(uintptr_t)CLOCK4_CONFIG_VALUE);
                if (status == 0u && *active == 0u &&
                    *(volatile uint8_t *)(uintptr_t)CLOCK4_DEFERRED_FLAG == 0u) {
                    *active = 1u;
                } else if (status != 0u) {
                    (void)hfadj_enable(0u);
                }
            }
        }
        if (status == 0u)
            clock_user_update(user_id, 1u);
    }

    if (*active != 0u)
        *callback_pointer = (uint32_t)(uintptr_t)&timeout;
    critical_restore(previous);
    callback_finish(&timeout);
    return status;
}

uint32_t opencfw_bl_clock_release_id4(uint8_t user_id)
{
    if (!clock_user_has(user_id))
        return 0u;

    const uint32_t previous = critical_save_disable();
    clock_user_update(user_id, 0u);
    if (clock_user_count() == 0u)
        (void)hfadj_enable(0u);
    critical_restore(previous);
    return 0u;
}
