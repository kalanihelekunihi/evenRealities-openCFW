#include <stdint.h>

/* Native 0x315e38..0x315e60: run the encryption action and the 3197c8,
 * 324674, 325fb8 and 325dfc children, then start the PHY timer. */
extern uint32_t opencfw_em9305_enc_action_3197d0(uintptr_t record);
extern uint32_t opencfw_em9305_child_3197c8(uintptr_t record);
extern uint32_t opencfw_em9305_child_324674(uintptr_t record);
extern uint32_t opencfw_em9305_child_325fb8(uintptr_t record);
extern uint32_t opencfw_em9305_child_325dfc(uintptr_t record);
extern uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t record);

uint32_t opencfw_em9305_child_315e38(uintptr_t record)
{
    (void)opencfw_em9305_enc_action_3197d0(record);
    (void)opencfw_em9305_child_3197c8(record);
    (void)opencfw_em9305_child_324674(record);
    (void)opencfw_em9305_child_325fb8(record);
    (void)opencfw_em9305_child_325dfc(record);
    return opencfw_em9305_phy_timer_start_32c7e4(record);
}
