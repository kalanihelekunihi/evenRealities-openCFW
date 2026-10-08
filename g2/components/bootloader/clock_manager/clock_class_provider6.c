/* Recovered class-6 PLL clock ownership and its local bounded PLL helpers.
 * The synthetic validation makes no physical power/lock claim. */
#include "clock_class_provider6.h"

#include "clock_class_provider2.h"
#include "clock_class_provider4.h"
#include "clock_class_providers.h"

enum {
    CLOCK_USER_BITS_BASE = 0x20026e74u,
    CLOCK6_CONFIG = 0x20027004u,
    CLOCK6_FEATURE_ENABLED = 0x2002719au,
    CLOCK6_INITIALIZE_FLAG = 0x200271a0u,
    CLOCK6_HANDLE_POINTER = 0x2002703cu,
    SYSPLL_CONTEXT = 0x20027010u,
    SYSPLL_CONTEXT_MAGIC = 0x01504c30u,
    SYSPLL_REGISTER_STATUS = 0x40020060u,
    SYSPLL_CONTROL0 = 0x400204d8u,
    SYSPLL_CONTROL1 = 0x400204dcu,
    SYSPLL_CONTROL2 = 0x400204e0u,
    SYSPLL_LOCK_STATUS = 0x400204e4u,
    SYSPLL_REF_CONFIG = 0x40008858u,
    SYSPLL_REVISION = 0x4002000cu,
    SYSPLL_ISOLATION = 0x400201b0u
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

static uint32_t delay_status_check(uint32_t timeout,
                                   volatile uint32_t *address,
                                   uint32_t mask, uint32_t expected)
{
    for (;;) {
        if ((*address & mask) == expected)
            return 0u;
        if (timeout == 0u)
            return 4u;
        opencfw_bl_delay_us(1u);
        --timeout;
    }
}

static void pll_power_initialize(void)
{
    const uint32_t previous = critical_save();
    if ((*(volatile uint32_t *)(uintptr_t)SYSPLL_REVISION & 0xffu) > 0x21u) {
        *(volatile uint32_t *)(uintptr_t)SYSPLL_ISOLATION &= 0xffdfffffu;
        opencfw_bl_delay_us(1u);
    }
    volatile uint32_t *const pll =
        (volatile uint32_t *)(uintptr_t)SYSPLL_CONTROL0;
    *pll &= 0x7fffffffu;
    *pll &= 0xbfffffffu;
    critical_restore(previous);
    opencfw_bl_delay_us(5u);
}

static uint32_t pll_power_down(uint8_t *needs_restore)
{
    volatile uint32_t *const pll =
        (volatile uint32_t *)(uintptr_t)SYSPLL_CONTROL0;
    *needs_restore = (uint8_t)((*pll >> 31) ^ 1u);
    return 0u;
}

static void pll_power_restore(void)
{
    const uint32_t previous = critical_save();
    volatile uint32_t *const pll =
        (volatile uint32_t *)(uintptr_t)SYSPLL_CONTROL0;
    *pll |= 0x80000000u;
    *pll |= 0x40000000u;
    if ((*(volatile uint32_t *)(uintptr_t)SYSPLL_REVISION & 0xffu) > 0x21u) {
        opencfw_bl_delay_us(1u);
        *(volatile uint32_t *)(uintptr_t)SYSPLL_ISOLATION |= 0x00200000u;
    }
    critical_restore(previous);
}

static uint32_t pll_initialize(int mode, uint32_t **handle_out)
{
    volatile uint32_t *const context =
        (volatile uint32_t *)(uintptr_t)SYSPLL_CONTEXT;
    if (mode != 0)
        return 5u;
    if (handle_out == 0)
        return 6u;
    if (((int32_t)(*context << 7)) < 0)
        return 7u;

    *context |= 0x01000000u;
    *context = (*context & 0xff000000u) | 0x00504c30u;
    context[1] = 0u;
    pll_power_initialize();
    *handle_out = (uint32_t *)(uintptr_t)SYSPLL_CONTEXT;
    return 0u;
}

static uint32_t pll_disable(uint32_t *handle)
{
    if (handle == 0 || (handle[0] & 0x01ffffffu) != SYSPLL_CONTEXT_MAGIC)
        return 2u;
    *(volatile uint32_t *)(uintptr_t)SYSPLL_CONTROL0 &= 0xdfffffffu;
    handle[0] &= 0xfdffffffu;
    return 0u;
}

static uint32_t pll_deinitialize(uint32_t *handle)
{
    if (handle == 0 || (handle[0] & 0x01ffffffu) != SYSPLL_CONTEXT_MAGIC)
        return 2u;
    if ((handle[0] & 0x02000000u) != 0u)
        (void)pll_disable(handle);
    uint8_t needs_restore = 0u;
    (void)pll_power_down(&needs_restore);
    if (needs_restore != 0u)
        pll_power_restore();
    handle[0] &= 0xfeffffffu;
    return 0u;
}

static uint32_t pll_configure(uint32_t *handle, const uint8_t *config)
{
    if (handle == 0 || (handle[0] & 0x01ffffffu) != SYSPLL_CONTEXT_MAGIC)
        return 2u;
    if ((handle[0] & 0x02000000u) != 0u)
        return 7u;

    const uint16_t multiplier =
        *(const uint16_t *)(const void *)(config + 6);
    if (config[3] >= 0x40u)
        return 6u;
    if ((config[2] == 1u && (multiplier < 4u || multiplier > 0x3c0u)) ||
        (config[2] != 1u && (multiplier < 10u || multiplier > 0x60u)))
        return 6u;
    if (config[4] >= 8u || config[5] >= 8u || config[5] > config[4])
        return 6u;

    volatile uint32_t *const control0 =
        (volatile uint32_t *)(uintptr_t)SYSPLL_CONTROL0;
    volatile uint32_t *const control1 =
        (volatile uint32_t *)(uintptr_t)SYSPLL_CONTROL1;
    volatile uint32_t *const control2 =
        (volatile uint32_t *)(uintptr_t)SYSPLL_CONTROL2;
    *control0 = (*control0 & 0xfffffdffu) |
                (((uint32_t)config[1] & 1u) << 9);
    *control0 = (*control0 & 0xffffffdfu) |
                (((uint32_t)config[0] & 1u) << 5);
    *control0 = (*control0 & 0xfffffff7u) |
                (((uint32_t)config[2] & 1u) << 3);
    *control1 = (*(const uint32_t *)(const void *)(config + 8) & 0x00ffffffu) |
                (*control1 & 0xff000000u);
    *control2 = (*control2 & 0xf000ffffu) |
                (((uint32_t)multiplier & 0x0fffu) << 16);
    *control2 = ((uint32_t)config[3] & 0x3fu) |
                (*control2 & 0xffffffc0u);
    *control2 = (*control2 & 0xffff8fffu) |
                (((uint32_t)config[4] & 7u) << 12);
    *control2 = (*control2 & 0xfffff8ffu) |
                (((uint32_t)config[5] & 7u) << 8);

    const uint32_t previous = critical_save();
    volatile uint32_t *const ref_config =
        (volatile uint32_t *)(uintptr_t)SYSPLL_REF_CONFIG;
    *ref_config = (*ref_config & 0xffffffbfu) |
                  (((uint32_t)config[0] & 1u) << 6);
    critical_restore(previous);

    *control0 &= 0xffffffefu;
    *control0 |= 1u;
    *control0 &= 0xfffffffdu;
    *control0 &= 0xfffffffbu;
    return 0u;
}

static uint32_t pll_enable(uint32_t *handle)
{
    if (handle == 0 || (handle[0] & 0x01ffffffu) != SYSPLL_CONTEXT_MAGIC)
        return 2u;
    if ((handle[0] & 0x02000000u) != 0u)
        return 0u;

    const uint32_t status =
        *(volatile uint32_t *)(uintptr_t)SYSPLL_REGISTER_STATUS;
    if ((status & 0x000f0000u) != 0x000f0000u)
        return 7u;

    *(volatile uint32_t *)(uintptr_t)SYSPLL_CONTROL0 |= 0x20000000u;
    handle[0] |= 0x02000000u;
    return 0u;
}

static uint32_t pll_lock_wait(uint32_t *handle)
{
    if (handle == 0 || (handle[0] & 0x01ffffffu) != SYSPLL_CONTEXT_MAGIC)
        return 2u;
    volatile uint32_t *const control0 =
        (volatile uint32_t *)(uintptr_t)SYSPLL_CONTROL0;
    if ((*control0 & 0x20000000u) == 0u)
        return 7u;

    const uint32_t scale = ((*control0 >> 9) & 1u) != 0u ? 0x753u : 1000u;
    const uint32_t ref_divider =
        *(volatile uint32_t *)(uintptr_t)SYSPLL_CONTROL2 & 0x3fu;
    const uint32_t timeout = (ref_divider * scale + 0x0bu) / 12u;
    return delay_status_check(timeout,
        (volatile uint32_t *)(uintptr_t)SYSPLL_LOCK_STATUS, 1u, 1u);
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
            uint32_t **const handle_pointer =
                (uint32_t **)(uintptr_t)CLOCK6_HANDLE_POINTER;
            if (*handle_pointer == 0)
                status = pll_initialize(0, handle_pointer);
            if (status == 0u)
                status = pll_configure(*handle_pointer,
                    (const uint8_t *)(uintptr_t)CLOCK6_CONFIG);
            if (status == 0u)
                status = pll_enable(*handle_pointer);
            if (status == 0u) {
                pll_started = 1u;
            } else if (*handle_pointer != 0) {
                (void)pll_deinitialize(*handle_pointer);
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
        uint32_t **const handle_pointer =
            (uint32_t **)(uintptr_t)CLOCK6_HANDLE_POINTER;
        status = pll_lock_wait(*handle_pointer);
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
        uint32_t **const handle_pointer =
            (uint32_t **)(uintptr_t)CLOCK6_HANDLE_POINTER;
        (void)pll_disable(*handle_pointer);
        (void)pll_deinitialize(*handle_pointer);
        *handle_pointer = 0;
        if (*(volatile uint8_t *)(uintptr_t)CLOCK6_CONFIG == 0u)
            (void)opencfw_bl_clock_release_id2(0x35u);
        else
            (void)opencfw_bl_clock_release_id3(0x35u);
    }
    critical_restore(previous);
    return 0u;
}

/* Source accessors for the independently verified clockmux caller. */
void opencfw_boot_syspll_power_initialize_for_clockmux(void)
{
    pll_power_initialize();
}
void opencfw_boot_syspll_power_restore_for_clockmux(void)
{
    pll_power_restore();
}
