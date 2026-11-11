#include <stdint.h>

/* Native 0x315f64..0x315f80: run the 3197e8, 3197d8 and 326a48 steps on the
 * record, then return the PHY timer start status. */
extern uint32_t opencfw_em9305_child_3197e8(uint32_t);
extern uint32_t opencfw_em9305_child_3197d8(uint32_t);
extern uint32_t opencfw_em9305_child_326a48(uint32_t);
extern uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t);

uint32_t opencfw_em9305_child_315f64(uintptr_t record)
{
    (void)opencfw_em9305_child_3197e8(record);
    (void)opencfw_em9305_child_3197d8(record);
    (void)opencfw_em9305_child_326a48(record);
    return opencfw_em9305_phy_timer_start_32c7e4(record);
}
