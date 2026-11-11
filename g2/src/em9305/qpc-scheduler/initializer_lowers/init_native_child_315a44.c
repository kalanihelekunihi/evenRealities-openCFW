#include <stdint.h>

/* Native 0x315a44..0x315a6c: mark completion (+627), clear bit 0 of the
 * record flags (+13), then run PHY completion, 32ca20 and 325ccc. */
extern uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t);
extern uint32_t opencfw_em9305_child_32ca20(uintptr_t);
extern uint32_t opencfw_em9305_child_325ccc(uintptr_t);

uint32_t opencfw_em9305_child_315a44(uintptr_t record)
{
    uint32_t flags=*(volatile uint8_t *)(record+13u);
    *(volatile uint8_t *)(record+627u)=1u;
    *(volatile uint8_t *)(record+13u)=(uint8_t)(flags&~1u);
    (void)opencfw_em9305_phy_complete_32c818(record);
    (void)opencfw_em9305_child_32ca20(record);
    return opencfw_em9305_child_325ccc(record);
}
