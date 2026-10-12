#include <stdint.h>

/* Native 0x313338..0x313352. The comparison reads the live registered
 * context at 0x805f14; the state byte is read only on a matching context. */
extern uint32_t opencfw_em9305_auxiliary_transition_333a60(void);
uint32_t opencfw_em9305_mode_event_313338(uintptr_t field)
{
    volatile uint8_t *const root=(volatile uint8_t *)(uintptr_t)0x805f04u;
    if (*(volatile uint32_t *)(uintptr_t)0x805f14u != (uint32_t)field)
        return (uint32_t)field;
    uint32_t state=root[0];
    if (state==2u) return state;
    return opencfw_em9305_auxiliary_transition_333a60();
}
