#include <stdint.h>

/* Native 0x32003c..0x320064: extended-init state machine step. Run the
 * action for (state, event) from the ROM table at 0x334e30 if present, then
 * move the state byte to the table entry at 0x334e70 and return it. */
extern void (*const opencfw_em9305_ext_init_actions_334e30[16])(void);
extern const uint8_t opencfw_em9305_ext_init_transitions_334e70[16];

uint32_t opencfw_em9305_child_32003c(uintptr_t machine, uint32_t event)
{
    uint32_t state = *(volatile uint8_t *)machine;
    uintptr_t action = (uintptr_t)opencfw_em9305_ext_init_actions_334e30[state * 4u + event];
    if (action != 0u) {
        ((void (*)(uintptr_t, uintptr_t, uint32_t))action)(machine, action, state);
        state = *(volatile uint8_t *)machine;
    }
    uint32_t next = opencfw_em9305_ext_init_transitions_334e70[state * 4u + event];
    *(volatile uint8_t *)machine = (uint8_t)next;
    return next;
}
