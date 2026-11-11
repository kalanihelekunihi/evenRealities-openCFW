#include <stdint.h>

/* Native 0x315e14..0x315e32: encryption action; run the four start-up
 * steps on the record and mark its flag byte +515. */
extern uint32_t opencfw_em9305_child_3197c8(uintptr_t);
extern uint32_t opencfw_em9305_phy_start_324680(uintptr_t);
extern uint32_t opencfw_em9305_child_324674(uintptr_t);
extern uint32_t opencfw_em9305_phy_schedule_318278(uintptr_t);

uint32_t opencfw_em9305_enc_action_315e14(uintptr_t record)
{
    (void)opencfw_em9305_child_3197c8(record);
    (void)opencfw_em9305_phy_start_324680(record);
    (void)opencfw_em9305_child_324674(record);
    uint32_t result = opencfw_em9305_phy_schedule_318278(record);
    *(volatile uint8_t *)(record + 515u) = 1u;
    return result;
}
