#include <stdint.h>

/* Native 0x32ad38..0x32ad64: extended-advertising state machine step. The
 * state byte lives at +2; run the action for (state, event) from the ROM
 * table at 0x334db8 (six events per state) if present, then move the state
 * to the table entry at 0x334e18 and return it. */
extern void (*const opencfw_em9305_ext_adv_actions_334db8[24])(void);
extern const uint8_t opencfw_em9305_ext_adv_transitions_334e18[24];

uint32_t opencfw_em9305_child_32ad38(uintptr_t machine, uint32_t event)
{
    uint32_t state = *(volatile uint8_t *)(machine + 2u);
    uintptr_t action = (uintptr_t)opencfw_em9305_ext_adv_actions_334db8[state * 6u + event];
    if (action != 0u) {
        ((void (*)(uintptr_t, uintptr_t, uint32_t))action)(machine, action, state);
        state = *(volatile uint8_t *)(machine + 2u);
    }
    uint32_t next = opencfw_em9305_ext_adv_transitions_334e18[state * 6u + event];
    *(volatile uint8_t *)(machine + 2u) = (uint8_t)next;
    return next;
}
