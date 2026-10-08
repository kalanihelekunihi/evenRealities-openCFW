/* SPDX-License-Identifier: MIT
 * Source reconstruction of locked 42a4bc and its call-free 42a1bc leaf.
 * The sequence and temperature-transition descendants remain explicit test cuts.
 */
#include <stdbool.h>
#include <stdint.h>

#define R32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define R8(a)  (*(volatile uint8_t *)(uintptr_t)(a))
#define W32(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))

extern void event_a_temperature_transition_separate(uint32_t new_major,
    uint32_t old_major, uint32_t new_minor, uint32_t old_minor);
extern uint32_t event_a_state_transition_sequence(uint32_t from_state,
    uint32_t to_state, uint8_t *selector);

NI void event_a_power_ton_adjust(uint32_t new_minor, uint32_t major)
{
    uint32_t ton, trim;
    if (major == 8U) new_minor = 7U;
    if (new_minor == 0U) {
        const uint32_t v = R32(0x20026bfcU);
        ton = R8(0x20026bfcU) & 0x1fU;
        trim = (v & 0x7fffU) >> 10;
    } else if (new_minor == 2U) {
        ton = R8(0x20026bf4U) & 0x1fU;
        trim = R8(0x20026bf8U) & 0x1fU;
    } else if (new_minor < 2U) {
        ton = (R32(0x20026bfcU) & 0x3ffU) >> 5;
        trim = (R32(0x20026bfcU) & 0xfffffU) >> 15;
    } else if (new_minor == 4U) {
        ton = (R32(0x20026bf4U) & 0x3ffU) >> 5;
        trim = (R32(0x20026bf8U) & 0x3ffU) >> 5;
    } else if (new_minor < 4U) {
        ton = (R32(0x20026bf4U) & 0x7fffU) >> 10;
        trim = (R32(0x20026bf8U) & 0x7fffU) >> 10;
    } else if (new_minor == 6U) {
        ton = R8(0x20026c00U) & 0x1fU;
        trim = (R32(0x20026c00U) & 0x7fffU) >> 10;
    } else if (new_minor < 6U) {
        ton = (R32(0x20026bf4U) & 0xfffffU) >> 15;
        trim = (R32(0x20026bf8U) & 0xfffffU) >> 15;
    } else if (new_minor == 7U) {
        ton = (R32(0x40020344U) & 0xffffU) >> 11;
        trim = (R32(0x40020354U) & 0x3fffffU) >> 17;
    } else {
        ton = (R32(0x20026bf4U) & 0xfffffU) >> 15;
        trim = (R32(0x20026bf8U) & 0xfffffU) >> 15;
    }
    W32(0x40020344U) = (R32(0x40020344U) & 0xc1ffffffU) | (ton << 25);
    W32(0x40020358U) = (R32(0x40020358U) & 0xffffe0ffU) | (trim << 8);
}

NI void event_a_power_trims_update(uint32_t new_major, uint32_t old_major,
                                   uint32_t new_minor, uint32_t old_minor)
{
    uint8_t selector = 0x1aU;
    uint32_t intermediate = old_major;
    uint32_t rc;

    if (new_major == old_major) {
        if (new_minor != old_minor) event_a_power_ton_adjust(new_minor, new_major);
        return;
    }
    if ((new_major >> 2) == (old_major >> 2)) {
        event_a_temperature_transition_separate(new_major, old_major,
                                                 new_minor, old_minor);
        return;
    }
    if ((new_major & 3U) != (old_major & 3U)) {
        intermediate = (new_major & 3U) | (old_major & 0xfffffffcU);
        event_a_temperature_transition_separate(intermediate, old_major,
                                                 new_minor, old_minor);
    }
    rc = event_a_state_transition_sequence(new_major, intermediate, &selector);
    if (rc == 0U) {
        void (**dispatch)(uint32_t, uint32_t, uint32_t, uint32_t) =
            (void (**)(uint32_t, uint32_t, uint32_t, uint32_t))(uintptr_t)0x20000158U;
        dispatch[selector](new_major, intermediate, new_minor, old_minor);
    }
}
