/* SPDX-License-Identifier: MIT
 * Source reconstructions of the locked PCM2.2 transition handlers 14 and 18.
 * The fixed-address inputs and write sequence are transcribed from stock
 * instructions; the upstream PCM2.2 unit is used as semantic corroboration.
 */
#include <stdint.h>

#define U32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define U8(a)  (*(volatile uint8_t *)(uintptr_t)(a))

extern uint32_t opencfw_pcm22_timer_service(void);

static void delay_us(uint32_t us)
{
    uint32_t cycles = us * 32u;
    uint32_t threshold = 15u;
    if (((U32(0x40021000u) & 0xf8u) >> 3) == 2u) {
        cycles = (cycles * 250u) / 96u;
        threshold = 24u;
    }
    if (cycles > threshold) {
        typedef void (*rom_wait_fn)(uint32_t);
        ((rom_wait_fn)(uintptr_t)0x41u)(cycles - threshold);
    }
}

static void timer_expire_and_service(void)
{
    if ((U32(0x400083e0u) & 1u) != 0u) {
        uint32_t i;
        for (i = 0; i < 60u; ++i) {
            if ((U32(0x40008064u) & 0x40000000u) != 0u) break;
            delay_us(1u);
        }
        (void)opencfw_pcm22_timer_service();
    }
}

uint32_t opencfw_spot_pcm22_transition14(uint32_t new_power,
                                         uint32_t current_power,
                                         uint32_t new_ton,
                                         uint32_t current_ton)
{
    volatile uint32_t *const profile =
        (volatile uint32_t *)(uintptr_t)0x20026ba0u;
    volatile uint32_t *const low_voltage =
        (volatile uint32_t *)(uintptr_t)0x20026c04u;
    uint32_t new_word = profile[new_power + 1u];
    uint32_t current_word = profile[current_power + 1u];
    uint32_t low_word = *low_voltage;
    uint32_t low_trim[4] = {low_word & 0x7fu, (low_word >> 7) & 0x7fu,
                            (low_word >> 14) & 0x7fu,
                            (low_word >> 21) & 0x7fu};
    uint32_t new_low = low_trim[new_power & 3u];
    uint32_t current_low = low_trim[current_power & 3u];

    /* Stock reads these fields before the timer gate; retain volatile reads. */
    (void)new_low;
    (void)current_low;
    (void)current_word;
    timer_expire_and_service();

    U32(0x200270c0u) = new_ton;
    U32(0x200270c4u) = new_power;
    U32(0x200270b8u) = (new_word >> 7) & 0x3ffu;
    U32(0x200270bcu) = (new_word >> 17) & 0x0fu;
    U32(0x200270b0u) = (new_word >> 21) & 0x7fu;
    U32(0x200270b4u) = new_word & 0x7fu;
    U32(0x4002004cu) = (U32(0x4002004cu) & 0xffffff80u) |
                        (new_word & 0x7fu);
    (void)current_ton;
    return low_trim[0] | (low_trim[1] << 8) | (low_trim[2] << 16) |
           (low_trim[3] << 24);
}

static uint32_t double_boost(uint32_t current, uint32_t target)
{
    uint32_t diff = target > current ? target - current : 0u;
    uint32_t result = current + diff * 2u;
    return result > 0x7fu ? 0x7fu : result;
}

static uint32_t double_boost_wrap(uint32_t current, uint32_t target)
{
    uint32_t result = target + ((current - target) * 2u);
    return result >= 0x80u ? 0x7fu : result;
}

static void replace_low7(uint32_t address, uint32_t value)
{
    U32(address) = (U32(address) & 0xffffff80u) | (value & 0x7fu);
}

uint32_t opencfw_spot_pcm22_transition18(uint32_t new_power,
                                         uint32_t current_power,
                                         uint32_t new_ton,
                                         uint32_t current_ton)
{
    volatile uint32_t *const profile =
        (volatile uint32_t *)(uintptr_t)0x20026ba0u;
    volatile uint32_t *const low_voltage =
        (volatile uint32_t *)(uintptr_t)0x20026c04u;
    uint32_t new_word = profile[new_power + 1u];
    uint32_t current_word = profile[current_power + 1u];
    uint32_t new_vddc = (new_word >> 21) & 0x7fu;
    uint32_t current_vddc = (current_word >> 21) & 0x7fu;
    uint32_t new_vddf = new_word & 0x7fu;
    uint32_t state0_vddf = profile[1u] & 0x7fu;
    uint32_t low_word = *low_voltage;
    uint32_t low_trim[4] = {low_word & 0x7fu, (low_word >> 7) & 0x7fu,
                            (low_word >> 14) & 0x7fu,
                            (low_word >> 21) & 0x7fu};
    uint32_t new_vddclv = low_trim[new_power & 3u];
    uint32_t current_vddclv = low_trim[current_power & 3u];

    /* Stock also reads the current VDDF field into r3 before entering the
       timer gate; it is not used by this handler's observed write sequence. */
    (void)(current_word & 0x7fu);
    timer_expire_and_service();

    U32(0x200270c0u) = new_ton;
    U32(0x200270c4u) = new_power;
    U32(0x200270b8u) = (new_word >> 7) & 0x3ffu;
    U32(0x200270bcu) = (new_word >> 17) & 0x0fu;
    U32(0x200270b0u) = new_vddc;
    U32(0x200270b4u) = new_vddf;

    replace_low7(0x40020048u, double_boost(current_vddclv, new_vddclv));
    replace_low7(0x4002004cu, double_boost_wrap(state0_vddf, new_vddf));
    replace_low7(0x40020044u, double_boost(current_vddc, new_vddc));
    delay_us(50u);
    replace_low7(0x40020044u, new_vddc);
    U32(0x40020080u) = (U32(0x40020080u) & 0xffffc3ffu) |
                        (((new_word >> 17) & 0x0fu) << 10);
    U32(0x40020080u) = (U32(0x40020080u) & 0xfffffc00u) |
                        ((new_word >> 7) & 0x3ffu);
    delay_us(5u);
    replace_low7(0x4002004cu, new_vddf);
    replace_low7(0x40020048u, new_vddclv);
    (void)current_ton;
    return (uint32_t)(uintptr_t)&profile[new_power + 1u];
}
