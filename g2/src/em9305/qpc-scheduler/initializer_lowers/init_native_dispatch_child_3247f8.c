#include <stdint.h>

/* Native 0x3247f8..0x32483a: ECU state machine step. Only while the mode
 * byte +620 is 0 or 1 and for events 0..2: run the action for (state, event)
 * from the ROM table at 0x335378 if present, then move the state byte +624
 * to the table entry at 0x335390. */
extern void (*const opencfw_em9305_ecu_callbacks_335378[6])(void);
extern const uint8_t opencfw_em9305_ecu_transitions_335390[6];

void opencfw_em9305_dispatch_child_3247f8(uintptr_t record, uint32_t event)
{
    uint32_t mode = *(volatile uint8_t *)(record + 620u);
    if (mode != 1u && mode != 0u) return;
    if (event >= 3u) return;
    volatile uint8_t *state = (volatile uint8_t *)(record + 624u);
    uintptr_t action = (uintptr_t)opencfw_em9305_ecu_callbacks_335378[*state * 3u + event];
    if (action != 0u)
        ((void (*)(uintptr_t, uintptr_t, uint32_t))action)(record, action, mode);
    *state = opencfw_em9305_ecu_transitions_335390[*state * 3u + event];
}
