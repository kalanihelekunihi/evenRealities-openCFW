#include <stdint.h>

/* Native 0x315fc0..0x315ff4: PHY update completion; report the end through
 * 322e14 when the busy byte (+515) is set, otherwise through 322dd8 with
 * reason 0; then clear the busy byte. */
extern uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t);
extern uint32_t opencfw_em9305_phy_update_complete_32e220(uintptr_t);
extern uint32_t opencfw_em9305_child_32e214(uintptr_t);
extern uint32_t opencfw_em9305_child_322e14(uintptr_t);
extern uint32_t opencfw_em9305_child_322dd8(uintptr_t,uint32_t);

uint32_t opencfw_em9305_child_315fc0(uintptr_t record)
{
    uint32_t status;
    (void)opencfw_em9305_phy_complete_32c818(record);
    (void)opencfw_em9305_phy_update_complete_32e220(record);
    (void)opencfw_em9305_child_32e214(record);
    if(*(volatile uint8_t *)(record+515u)!=0u)
        status=opencfw_em9305_child_322e14(record);
    else
        status=opencfw_em9305_child_322dd8(record,0u);
    *(volatile uint8_t *)(record+515u)=0u;
    return status;
}
