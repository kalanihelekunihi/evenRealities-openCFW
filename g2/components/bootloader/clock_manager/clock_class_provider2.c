/* Recovered class-2 clock ownership and its bounded radio-mode helpers.
 * Peripheral accesses and callback progress are synthetic in host tests. */
#include "clock_class_provider2.h"
#include "clock_class_provider4.h"
#include "clock_manager.h"

enum {
    CLOCK_USER_BITS_BASE = 0x20026e74u,
    CLOCK2_ENABLED = 0x20000080u,
    CLOCK2_MODE_SELECTOR = 0x2000007cu,
    RADIO_MODE_REGISTER = 0x4002012cu,
    RADIO_CONFIG_REGISTER = 0x40020128u,
    RADIO_CONFIG_MASK = 0xc0007000u,
    RADIO_CONFIG_BASE_REGISTER = 0x40020120u,
    RADIO_CONFIG_LOW_SOURCE = 0x20000090u,
    RADIO_CONFIG_HIGH_SOURCE = 0x20000094u,
    RADIO_CONFIG_FIXED_VALUE = 0x0fff8c00u,
    RADIO_MODE_BUSY = 0x2002719bu,
    RADIO_CALLBACK_POINTER = 0x20027040u,
    RADIO_MODE_CLEAR_MASK = 0xfffffef6u,
    RADIO_MODE_SELECT_MASK = 0xfffffefeu,
    RADIO_MODE_FINAL_MASK = 0xfffffed4u,
    RADIO_MODE_VALUE = 0x03118000u
};

static volatile uint32_t *user_word(uint8_t user_id)
{
    const uint32_t word_index = 2u * 2u + ((uint32_t)user_id >> 5);
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
        uint32_t value = words[i];
        value -= (value >> 1) & 0x55555555u;
        value = (value & 0x33333333u) + ((value >> 2) & 0x33333333u);
        value = (value + (value >> 4)) & 0x0f0f0f0fu;
        count += (value * 0x01010101u) >> 24;
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

uint32_t opencfw_bl_radio_mode_sample(uint8_t *mode)
{
    const uint32_t value = *(volatile uint32_t *)(uintptr_t)RADIO_MODE_REGISTER;
    *mode = (value & (1u << 8)) != 0u ? 2u :
            ((value & 1u) != 0u ? 1u : 0u);
    return 0u;
}

/* Stock returns CONCAT44(local_10, status), so preserve both AAPCS return
 * registers. Class-2 itself ignores the return; selectors 5/6 also call the
 * source dispatcher to acquire/release the nested class-2 user. */
uint64_t opencfw_bl_radio_mode_apply(uint8_t mode, const uint32_t *value,
                                     uint32_t unused, uint32_t value_seed)
{
    (void)unused;
    uint32_t result = value_seed;
    uint32_t status = 0u;
    volatile uint32_t *const base =
        (volatile uint32_t *)(uintptr_t)RADIO_CONFIG_BASE_REGISTER;
    volatile uint32_t *const config =
        (volatile uint32_t *)(uintptr_t)RADIO_CONFIG_REGISTER;
    volatile uint32_t *const radio_mode =
        (volatile uint32_t *)(uintptr_t)RADIO_MODE_REGISTER;
    const uint32_t low =
        *(volatile uint32_t *)(uintptr_t)RADIO_CONFIG_LOW_SOURCE;
    const uint32_t high =
        *(volatile uint32_t *)(uintptr_t)RADIO_CONFIG_HIGH_SOURCE;

    if (mode == 2u) {
        *config = (*config & RADIO_CONFIG_MASK) | (low & 0x3fu) |
                  ((high & 0x0fu) << 6) | RADIO_CONFIG_FIXED_VALUE;
        result = *radio_mode = (*radio_mode & 0xffffffddu) | 2u;
        *radio_mode |= 1u;
        *radio_mode |= 0x10u;
        *radio_mode |= 8u;
        opencfw_bl_delay_us(5u);
        *radio_mode &= ~0x10u;
        if (value != 0 && (*(const volatile uint8_t *)(const void *)value) == 1u)
            result = *radio_mode = (*radio_mode & RADIO_MODE_CLEAR_MASK) | 0x100u;
        goto done;
    }
    if (mode == 0u) {
        result = (*base & 0xffffffe0u) |
                 ((value != 0 &&
                   (*(const volatile uint8_t *)(const void *)value) == 1u) ?
                  5u : 0x19u);
        *base = result;
        goto done;
    }
    if (mode == 1u) {
        result = *base & 0xfffffffcu;
        *base = result;
        goto done;
    }
    if (mode == 3u) {
        *config = (low & 0x3fu) | ((high & 0x0fu) << 6) |
                  RADIO_CONFIG_FIXED_VALUE;
        *radio_mode = (*radio_mode & RADIO_MODE_CLEAR_MASK) | 0x22u;
        *radio_mode |= 1u;
        if (value == 0 || (*(const volatile uint8_t *)(const void *)value) != 1u)
            result = *radio_mode = (*radio_mode & 0xffffffd7u) | 8u;
        else
            result = *radio_mode = (*radio_mode & RADIO_MODE_SELECT_MASK) | 0x100u;
        goto done;
    }
    if (mode == 4u) {
        *config = (*config & RADIO_CONFIG_MASK) | (low & 0x3fu) |
                  ((high & 0x0fu) << 6) | RADIO_MODE_VALUE;
        result = *radio_mode = (*radio_mode & RADIO_MODE_FINAL_MASK) | 2u;
        goto done;
    }
    if (mode == 5u) {
        status = clock_request(2u, 0x34u);
        if (status != 0u)
            goto done;
        if (value == 0) {
            result = *config = (*config & 0xffff8fffu) | 0x4000u;
        } else {
            const uint32_t requested = *value;
            if (requested != 0u && requested - 3u > 4u) {
                status = 6u;
                goto done;
            }
            result = *config = (*config & 0xffff8fffu) |
                                ((requested & 7u) << 12);
        }
        *radio_mode |= 0x80u;
        goto done;
    }
    if (mode == 6u) {
        *config |= 0x7000u;
        *radio_mode &= 0xffffff7fu;
        status = clock_release(2u, 0x34u);
        goto done;
    }
    status = 6u;
done:
    return ((uint64_t)result << 32) | status;
}

void opencfw_bl_radio_callback_finish(uint32_t *timeout)
{
    volatile uint8_t *const active =
        (volatile uint8_t *)(uintptr_t)RADIO_MODE_BUSY;
    if (*active == 0u)
        return;

    while (*timeout != 0u && *active != 0u) {
        opencfw_bl_delay_us(10u);
        --*timeout;
    }

    const uint32_t previous = critical_save();
    *active = 0u;
    *(volatile uint32_t *)(uintptr_t)RADIO_CALLBACK_POINTER = 0u;
    critical_restore(previous);
}

uint32_t opencfw_bl_clock_request_id2(uint8_t user_id)
{
    uint32_t timeout = 150u;
    uint32_t status = 0u;
    volatile uint8_t *const active =
        (volatile uint8_t *)(uintptr_t)RADIO_MODE_BUSY;
    volatile uint32_t *const callback_pointer =
        (volatile uint32_t *)(uintptr_t)RADIO_CALLBACK_POINTER;

    if (*(volatile uint32_t *)(uintptr_t)CLOCK2_ENABLED == 0u)
        return 7u;

    if (user_present(user_id)) {
        const uint32_t previous = critical_save();
        if (*active != 0u)
            timeout = *(uint32_t *)(uintptr_t)*callback_pointer;
        *callback_pointer = (uint32_t)(uintptr_t)&timeout;
        critical_restore(previous);
        opencfw_bl_radio_callback_finish(&timeout);
        return 0u;
    }

    uint32_t previous = critical_save();
    if (*active != 0u)
        timeout = *(uint32_t *)(uintptr_t)*callback_pointer;

    uint8_t current_mode = 0u;
    (void)opencfw_bl_radio_mode_sample(&current_mode);
    const uint8_t selector =
        *(volatile uint8_t *)(uintptr_t)CLOCK2_MODE_SELECTOR;

    if (current_mode == 0u) {
        if (selector == 1u) {
            const uint8_t target = 1u;
            (void)opencfw_bl_radio_mode_apply(3u, (const uint32_t *)(const void *)&target, 0u, 0u);
        } else {
            (void)opencfw_bl_radio_mode_apply(2u, 0, 0u, 0u);
            if (*active == 0u)
                *active = 1u;
        }
    } else if ((current_mode == 2u && selector == 0u) ||
               (current_mode == 1u && selector == 1u)) {
        status = 3u;
    }

    if (status == 0u)
        user_update(user_id, 1u);
    if (*active != 0u)
        *callback_pointer = (uint32_t)(uintptr_t)&timeout;
    critical_restore(previous);
    opencfw_bl_radio_callback_finish(&timeout);
    return status;
}

uint32_t opencfw_bl_clock_release_id2(uint8_t user_id)
{
    if (!user_present(user_id))
        return 0u;

    const uint32_t previous = critical_save();
    user_update(user_id, 0u);
    if (user_count() == 0u) {
        const uint8_t target = 1u;
        (void)opencfw_bl_radio_mode_apply(4u, (const uint32_t *)(const void *)&target, 0u, 0u);
        *(volatile uint8_t *)(uintptr_t)RADIO_MODE_BUSY = 0u;
        *(volatile uint32_t *)(uintptr_t)RADIO_CALLBACK_POINTER = 0u;
    }
    critical_restore(previous);
    return 0u;
}
