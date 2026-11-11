#include <stdint.h>

/* Native 0x31593c..0x315958: set bit 17 of the record flag word at +636,
 * then run the 32ca74 and 3163d8 children on the record. */
extern uint32_t opencfw_em9305_child_32ca74(uintptr_t record);
extern uint32_t opencfw_em9305_child_3163d8(uintptr_t record);

uint32_t opencfw_em9305_child_31593c(uintptr_t record)
{
    volatile uint32_t *flags=(volatile uint32_t *)(record+636u);
    *flags|=1u<<17;
    (void)opencfw_em9305_child_32ca74(record);
    return opencfw_em9305_child_3163d8(record);
}
