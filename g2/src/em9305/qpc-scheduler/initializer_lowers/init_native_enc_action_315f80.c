#include <stdint.h>

/* Native 0x315f80..0x315fc0: encryption completion action. Run the five
 * completion steps on the record, then report either LL event 12 (flag
 * +515 set) or LL event 11 with status 0, and clear the flag. */
extern uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t);
extern uint32_t opencfw_em9305_child_3197e8(uintptr_t);
extern uint32_t opencfw_em9305_child_326a48(uintptr_t);
extern uint32_t opencfw_em9305_phy_update_complete_32e220(uintptr_t);
extern uint32_t opencfw_em9305_child_32e214(uintptr_t);
extern uint32_t opencfw_em9305_child_322e14(uintptr_t);
extern uint32_t opencfw_em9305_child_322dd8(uintptr_t,uint32_t);

uint32_t opencfw_em9305_enc_action_315f80(uintptr_t record)
{
    uint32_t result;
    (void)opencfw_em9305_phy_complete_32c818(record);
    (void)opencfw_em9305_child_3197e8(record);
    (void)opencfw_em9305_child_326a48(record);
    (void)opencfw_em9305_phy_update_complete_32e220(record);
    (void)opencfw_em9305_child_32e214(record);
    volatile uint8_t *flag = (volatile uint8_t *)(record + 515u);
    if (*flag != 0u)
        result = opencfw_em9305_child_322e14(record);
    else
        result = opencfw_em9305_child_322dd8(record, 0u);
    *flag = 0u;
    return result;
}
