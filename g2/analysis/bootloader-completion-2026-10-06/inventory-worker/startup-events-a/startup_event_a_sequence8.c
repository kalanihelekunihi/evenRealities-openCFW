/* SPDX-License-Identifier: BSD-3-Clause
 * Bounded port of PCM2.2 transition selector 8, for timer-disabled execution.
 * The timer-enabled branch is intentionally outside this function's contract.
 */
#include <stdint.h>

#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))

extern void event_a_power_ton_adjust(uint32_t new_minor, uint32_t major);

__attribute__((noinline, used))
uint32_t event_a_transition_sequence_8_timer_disabled(
    uint32_t target_state, uint32_t current_state,
    uint32_t target_ton_state, uint32_t current_ton_state)
{
    (void)current_state;
    (void)current_ton_state;
    const uint32_t *const profile = (const uint32_t *)(uintptr_t)0x20026ba0U;
    const uint32_t target = profile[1U + target_state];
    const uint32_t vddclv = profile[0x64U / 4U];

    /* `COMMON_HEADER` and `UPDATE_GLOBALS` from Ambiq PCM2.2, specialized to
     * the branch where TIMER_A is disabled. Selector 8 otherwise waits and
     * invokes the timer ISR before these writes. */
    W32(0x200270c0U) = target_ton_state;
    W32(0x200270c4U) = target_state;
    W32(0x200270b8U) = (target >> 7) & 0x3ffU;
    W32(0x200270bcU) = (target >> 17) & 0x0fU;
    W32(0x200270b0U) = (target >> 21) & 0x7fU;
    W32(0x200270b4U) = target & 0x7fU;
    event_a_power_ton_adjust(target_ton_state, target_state);

    /* The four-byte VDDCLV local overwrites the saved R3 slot; the epilogue
     * returns these four 7-bit trims in R0. */
    return (vddclv & 0x7fU) |
           (((vddclv >> 7) & 0x7fU) << 8) |
           (((vddclv >> 14) & 0x7fU) << 16) |
           (((vddclv >> 21) & 0x7fU) << 24);
}
