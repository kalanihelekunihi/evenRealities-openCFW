#include <stdint.h>

/* Native 0x315d80..0x315da0: mark the record's completion byte (+627), then
 * run PHY completion, the 32c990 step and the 325ccc step on it. */
extern uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t);
extern uint32_t opencfw_em9305_child_32c990(uintptr_t);
extern uint32_t opencfw_em9305_child_325ccc(uintptr_t);

uint32_t opencfw_em9305_child_315d80(uintptr_t record)
{
    *(volatile uint8_t *)(record+627u)=1u;
    (void)opencfw_em9305_phy_complete_32c818(record);
    (void)opencfw_em9305_child_32c990(record);
    return opencfw_em9305_child_325ccc(record);
}
