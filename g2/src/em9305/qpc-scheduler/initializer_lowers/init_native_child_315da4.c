#include <stdint.h>

/* Native 0x315da4..0x315dd8: PHY update completion: complete the procedure
 * and the PHY update, run 32e214, report the end through 322dd8 (reason
 * 0x1a for opcode 7 at 0x802818, else the reason byte at 0x80281d) and
 * clear the record's busy byte (+515). */
extern uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t);
extern uint32_t opencfw_em9305_phy_update_complete_32e220(uintptr_t);
extern uint32_t opencfw_em9305_child_32e214(uintptr_t);
extern uint32_t opencfw_em9305_child_322dd8(uintptr_t,uint32_t);

uint32_t opencfw_em9305_child_315da4(uintptr_t record)
{
    (void)opencfw_em9305_phy_complete_32c818(record);
    (void)opencfw_em9305_phy_update_complete_32e220(record);
    (void)opencfw_em9305_child_32e214(record);
    uint32_t opcode=*(volatile uint8_t *)(uintptr_t)0x802818u;
    uint32_t reason=*(volatile uint8_t *)(uintptr_t)0x80281du;
    if(opcode==7u) reason=0x1au;
    uint32_t status=opencfw_em9305_child_322dd8(record,reason);
    *(volatile uint8_t *)(record+515u)=0u;
    return status;
}
