#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x315da4..0x315dd8: PHY update completion: complete the procedure
 * and the PHY update, run 32e214, report the end through 322dd8 (reason
 * 0x1a for opcode 7 at ((uintptr_t)&em9305_ram_8027e0 + 0x38u), else the reason byte at ((uintptr_t)&em9305_ram_8027e0 + 0x3du)) and
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
    uint32_t opcode=em9305_ram_8027e0.u8_802818;
    uint32_t reason=em9305_ram_8027e0.u8_80281d;
    if(opcode==7u) reason=0x1au;
    uint32_t status=opencfw_em9305_child_322dd8(record,reason);
    *(volatile uint8_t *)(record+515u)=0u;
    return status;
}
