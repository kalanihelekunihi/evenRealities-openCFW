/* SPDX-License-Identifier: MIT
 * Locked PCM2.2 selector-15 transition routine (0x429524).
 */
#include <stdint.h>
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
extern uint32_t opencfw_pcm22_timer_service(void);
extern void opencfw_hal_delay_us(uint32_t);

static void wait_for_timer_and_service(void)
{
    if ((W(0x400083e0u) & 1u) != 0u) {
        for (uint32_t n = 0; n < 60u; ++n) {
            if ((W(0x40008064u) & 0x40000000u) != 0u) break;
            opencfw_hal_delay_us(1u);
        }
        (void)opencfw_pcm22_timer_service();
    }
}

uint64_t opencfw_spot_pcm22_transition15(uint32_t new_power,
                                          uint32_t current_power,
                                          uint32_t new_ton,
                                          uint32_t current_ton)
{
    volatile uint32_t *const profile = (volatile uint32_t *)(uintptr_t)0x20026ba0u;
    volatile uint32_t *const low_voltage = (volatile uint32_t *)(uintptr_t)0x20026c04u;
    uint32_t new_word = profile[new_power + 1u];
    uint32_t current_word = profile[current_power + 1u];
    uint32_t low_word = *low_voltage;
    uint32_t low_trim[4] = {low_word & 0x7fu, (low_word >> 7) & 0x7fu,
                            (low_word >> 14) & 0x7fu, (low_word >> 21) & 0x7fu};
    uint32_t new_low = low_trim[new_power & 3u];
    uint32_t current_low = low_trim[current_power & 3u];
    uint32_t new_vddc = (new_word >> 21) & 0x7fu;
    uint32_t current_vddc = (current_word >> 21) & 0x7fu;
    (void)current_low;
    (void)current_vddc;

    wait_for_timer_and_service();

    W(0x200270c0u) = new_ton;
    W(0x200270c4u) = new_power;
    W(0x200270b8u) = (new_word >> 7) & 0x3ffu;
    W(0x200270bcu) = (new_word >> 17) & 0x0fu;
    W(0x200270b0u) = new_vddc;
    W(0x200270b4u) = new_word & 0x7fu;

    W(0x40020048u) = (W(0x40020048u) & 0xffffff80u) | new_low;
    W(0x40020080u) = (W(0x40020080u) & 0xffffc3ffu) |
                      (((new_word >> 17) & 0x0fu) << 10);
    W(0x40020080u) = (W(0x40020080u) & 0xfffffc00u) |
                      ((new_word >> 7) & 0x3ffu);
    W(0x40020044u) = (W(0x40020044u) & 0xffffff80u) | new_vddc;

    /* Stock's four byte stores overwrite saved r2/r3 and therefore return
       the four unpacked trim bytes in r0/r1. */
    uint32_t packed = (low_trim[0] & 0xffu) | ((low_trim[1] & 0xffu) << 8) |
                      ((low_trim[2] & 0xffu) << 16) | ((low_trim[3] & 0xffu) << 24);
    return ((uint64_t)current_ton << 32) | packed;
}
