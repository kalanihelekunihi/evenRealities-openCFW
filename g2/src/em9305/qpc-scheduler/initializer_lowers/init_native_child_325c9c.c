#include <stdint.h>

/* Native 0x325c9c..0x325cb2: forward the record's sub-block at +660 to
 * native 0x325c40 with mask 0xf and a width of 8 when the halfword at
 * +662 exceeds 7, otherwise 4. */
extern uint32_t opencfw_em9305_child_325c40(uint32_t,uint32_t,uint32_t,uint32_t);

uint32_t opencfw_em9305_child_325c9c(uintptr_t record)
{
    uintptr_t block = record + 660u;
    uint32_t width = *(volatile uint16_t *)(block + 2u) > 7u ? 8u : 4u;
    return opencfw_em9305_child_325c40((uint32_t)record, 0xfu, (uint32_t)block, width);
}
