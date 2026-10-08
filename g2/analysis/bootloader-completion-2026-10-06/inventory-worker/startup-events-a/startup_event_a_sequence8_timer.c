/* SPDX-License-Identifier: BSD-3-Clause
 * Timer-enabled source port of locked PCM2.2 selector-8 target 0x428bb0.
 * The timer ISR is provided by the separately validated native PCM2.2 module.
 */
#include <stdint.h>

#define R32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))

extern void event_a_power_ton_adjust(uint32_t new_minor, uint32_t major);
extern void opencfw_hal_delay_us(uint32_t microseconds);
extern uint32_t opencfw_pcm22_timer_service(void);

__attribute__((noinline, used))
uint32_t event_a_transition_sequence_8_timer_native(
    uint32_t target_state, uint32_t current_state,
    uint32_t target_ton_state, uint32_t current_ton_state)
{
    const volatile uint32_t *const profile =
        (const volatile uint32_t *)(uintptr_t)0x20026ba0U;
    const uint32_t target = profile[1U + target_state];
    const uint32_t vddclv = profile[0x64U / 4U];
    (void)current_state;
    (void)current_ton_state;

    /* Locked code uses LSL #31 on TIMERCONTROL (source bit 0), samples status
     * bit 30 via LSL #1 before each delay, and invokes the ISR on readiness
     * or after 60 delays. */
    if ((R32(0x400083e0U) & 1U) != 0U) {
        for (uint32_t n = 0; n < 60U; ++n) {
            if ((R32(0x40008064U) & 0x40000000U) != 0U) break;
            opencfw_hal_delay_us(1U);
        }
        (void)opencfw_pcm22_timer_service();
    }

    W32(0x200270c0U) = target_ton_state;
    W32(0x200270c4U) = target_state;
    W32(0x200270b8U) = (target >> 7) & 0x3ffU;
    W32(0x200270bcU) = (target >> 17) & 0x0fU;
    W32(0x200270b0U) = (target >> 21) & 0x7fU;
    W32(0x200270b4U) = target & 0x7fU;
    event_a_power_ton_adjust(target_ton_state, target_state);

    return (vddclv & 0x7fU) |
           (((vddclv >> 7) & 0x7fU) << 8) |
           (((vddclv >> 14) & 0x7fU) << 16) |
           (((vddclv >> 21) & 0x7fU) << 24);
}
