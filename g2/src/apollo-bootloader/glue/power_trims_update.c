/* Source-owned stock 0x42a4bc event-A power trim dispatcher. */
#include <stdint.h>

extern void event_a_power_ton_adjust(uint32_t new_minor, uint32_t major);
extern uint64_t event_a_temperature_transition_separate(uint32_t new_major,
    uint32_t old_major, uint32_t new_minor, uint32_t old_minor);
extern uint32_t event_a_state_transition_sequence(uint32_t from_state,
    uint32_t to_state, uint8_t *selector);

/* Stock 0x42A4BC (spotmgr_power_trims_update_42a4bc) */
void event_a_power_trims_update(uint32_t new_major, uint32_t old_major,
                                uint32_t new_minor, uint32_t old_minor)
{
    uint8_t selector = 0x1au;
    uint32_t intermediate = old_major;

    if (new_major == old_major) {
        if (new_minor != old_minor)
            event_a_power_ton_adjust(new_minor, new_major);
        return;
    }
    if ((new_major >> 2) == (old_major >> 2)) {
        event_a_temperature_transition_separate(new_major, old_major,
                                                 new_minor, old_minor);
        return;
    }
    if ((new_major & 3u) != (old_major & 3u)) {
        intermediate = (new_major & 3u) | (old_major & 0xfffffffcu);
        event_a_temperature_transition_separate(intermediate, old_major,
                                                 new_minor, old_minor);
    }
    const uint32_t status = event_a_state_transition_sequence(new_major,
                                                               intermediate,
                                                               &selector);
    if (status == 0u) {
        void (**dispatch)(uint32_t, uint32_t, uint32_t, uint32_t) =
            (void (**)(uint32_t, uint32_t, uint32_t, uint32_t))(uintptr_t)0x20000158u;
        dispatch[selector](new_major, intermediate, new_minor, old_minor);
    }
}
