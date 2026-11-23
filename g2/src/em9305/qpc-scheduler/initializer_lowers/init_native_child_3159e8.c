#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x3159e8..0x315a0c: clear bit 0 of the record flags (+13), reject
 * the pending PHY procedure with the reason byte from *((uintptr_t)&em9305_ram_805c5c + 0x10u)+4, then
 * complete it. */
extern uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t);

uint32_t opencfw_em9305_child_3159e8(uintptr_t record)
{
    uintptr_t config=em9305_ram_805c5c.u32_805c6c;
    uint32_t flags=*(volatile uint8_t *)(record+13u);
    *(volatile uint8_t *)(record+13u)=(uint8_t)(flags&~1u);
    (void)opencfw_em9305_phy_reject_32698c(record,*(volatile uint8_t *)(config+4u),1u);
    return opencfw_em9305_phy_complete_32c818(record);
}
