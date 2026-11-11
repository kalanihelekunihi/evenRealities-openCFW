#include <stdint.h>

/* Native 0x324d6c..0x324dd2: connection-update procedure step keyed by the
 * procedure state +622 and an event. Idle (0): events 0/3 start the
 * procedure (native 0x3268cc, PHY timer, state 1), 1 runs native 0x3268e8,
 * 4 reports LL event 17 and runs native 0x32525c. Active (1): event 1 runs
 * native 0x3268e8, 4 reports LL event 17, 2 completes the PHY and returns to
 * idle. Other states and events are ignored. */
extern uint32_t opencfw_em9305_child_3268cc(uintptr_t);
extern uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t);
extern uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t);
extern uint32_t opencfw_em9305_child_3268e8(uintptr_t);
extern uint32_t opencfw_em9305_child_322dac(uintptr_t);
extern uint32_t opencfw_em9305_child_32525c(uintptr_t);

void opencfw_em9305_child_324d6c(uintptr_t record, uint32_t event)
{
    volatile uint8_t *state = (volatile uint8_t *)(record + 622u);
    if (*state == 1u) {
        if (event == 1u) {
            (void)opencfw_em9305_child_3268e8(record);
        } else if (event == 4u) {
            (void)opencfw_em9305_child_322dac(record);
        } else if (event == 2u) {
            (void)opencfw_em9305_phy_complete_32c818(record);
            *state = 0u;
        }
        return;
    }
    if (*state != 0u) return;
    if (event == 0u || event == 3u) {
        (void)opencfw_em9305_child_3268cc(record);
        (void)opencfw_em9305_phy_timer_start_32c7e4(record);
        *state = 1u;
    } else if (event == 1u) {
        (void)opencfw_em9305_child_3268e8(record);
    } else if (event == 4u) {
        (void)opencfw_em9305_child_322dac(record);
        (void)opencfw_em9305_child_32525c(record);
    }
}
