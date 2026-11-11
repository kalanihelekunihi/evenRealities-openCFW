#include <stdint.h>

/* Native 0x315df0..0x315e12: run the five per-link completion steps on the
 * same record, returning the PHY timer start status. */
extern uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t);
extern uint32_t opencfw_em9305_child_32cfc0(uintptr_t);
extern uint32_t opencfw_em9305_child_317c40(uintptr_t);
extern uint32_t opencfw_em9305_child_324674(uintptr_t);
extern uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t);

uint32_t opencfw_em9305_child_315df0(uintptr_t record)
{
    (void)opencfw_em9305_phy_complete_32c818(record);
    (void)opencfw_em9305_child_32cfc0(record);
    (void)opencfw_em9305_child_317c40(record);
    (void)opencfw_em9305_child_324674(record);
    return opencfw_em9305_phy_timer_start_32c7e4(record);
}
